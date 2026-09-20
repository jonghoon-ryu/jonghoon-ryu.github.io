---
layout: default
title: 쓰기 전에 읽으면 페이지가 소비되는 이유
permalink: /ftl-visual-simulator/reference/mqsim/read-before-write/
---
<style>
table.plan-calendar {
  width: 100% !important;
  table-layout: fixed !important;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: break-word;
  word-break: break-word;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
pre {
  background: #f5f5f5;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>

# 쓰기 전에 읽으면 페이지가 소비되는 이유

**결함은 아니다.** MQSim 이 의도한 대로 동작하는 것이고, 고쳐도 upstream 과 달라지지 않으니 [버그 목록](/ftl-visual-simulator/reference/bug-list/)에는 안 들어간다. 원본 C++ 코드도 건드리지 않았으니 [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/)에도 안 들어간다. 대신 MQSim 내부 동작 자체를 이해해야 왜 이런 선택을 했는지 설명되는 사례라 이 문서에 남긴다.

<div style="margin-top: 60px;"></div>

## 무엇을 발견했나

"매핑 기본" 프리셋에서 Read 비율을 0%에서 60%로 올리고 처음부터 재생했더니, **시뮬레이션의 맨 첫 번째 로그 줄**이 이렇게 나왔다.

```
[0000] 09:52:03  LPN 0x08d -> Chip 1, Block 00, Page 00, Read
```

한 번도 write 가 일어난 적 없는 시점인데 - 즉 이 LPN 은 지금까지 단 한 번도 쓰인 적이 없는데 - 이 Read 하나만으로 Flash Array 화면에서 Chip 1, Block 0, Page 0 이 곧바로 초록색 "valid" 로 바뀌었다.

<div style="margin-top: 60px;"></div>

## 왜 이런 일이 일어나나

### 1. 워크로드 생성기는 write 이력을 전혀 모른다

`IO_Flow_Synthetic::Generate_next_request()`(`host/IO_Flow_Synthetic.cpp`)는 요청마다 매번 동전을 던져 Read 인지 Write 인지 정한다.

```cpp
if (random_request_type_generator->Uniform(0, 1) <= read_ratio) {
    request->Type = Host_IO_Request_Type::READ;
} else {
    request->Type = Host_IO_Request_Type::WRITE;
}
```

이 함수는 그 LPA 에 이미 매핑이 있는지 전혀 확인하지 않는다. 그래서 기기가 완전히 비어 있는 시작 시점에도 Read 가 나올 수 있다.

### 2. 매핑이 없는 주소를 읽으면 - 실패하지 않고, 그 자리에서 페이지를 만들어낸다

`Address_Mapping_Unit_Page_Level::translate_lpa_to_ppa()`의 READ 분기(`ssd/Address_Mapping_Unit_Page_Level.cpp:637-647`):

```cpp
if (transaction->Type == Transaction_Type::READ) {
    if (ppa == NO_PPA) {
        ppa = online_create_entry_for_reads(transaction->LPA, streamID, transaction->Address,
            ((NVM_Transaction_Flash_RD*)transaction)->read_sectors_bitmap);
    }
    transaction->PPA = ppa;
    ...
    return true;
}
```

`ppa == NO_PPA` 는 "이 LPA 는 지금까지 한 번도 매핑된 적이 없다"는 뜻이다. 이 경우 `online_create_entry_for_reads()`(같은 파일, 1276번째 줄)가 대신 처리하는데, 이 함수의 마지막 세 줄이 핵심이다.

```cpp
block_manager->Allocate_block_and_page_in_plane_for_user_write(stream_id, read_address);
PPA_type ppa = Convert_address_to_ppa(read_address);
domain->Update_mapping_info(ideal_mapping_table, stream_id, lpa, ppa, read_sectors_bitmap);
```

`Allocate_block_and_page_in_plane_for_user_write()` 는 **진짜 write 가 페이지를 할당할 때 쓰는 것과 완전히 같은 함수**다 (`Address_Mapping_Unit_Page_Level.cpp:1237`, `allocate_page_in_plane_for_user_write()` 안에서 write 도 똑같이 이 함수를 부른다). 즉 이 "Read" 는:

- 현재 write frontier(`Data_wf`) 에서 다음 페이지를 그대로 가져가고,
- free block pool 을 write 와 똑같이 하나 소비하고,
- 매핑 테이블에 정상적으로 "valid" 항목을 하나 등록한다.

**Program(쓰기) 명령은 실제로는 한 번도 내려가지 않는다.** 순수하게 "이 LPA 는 이제부터 이 물리 페이지에 매핑돼 있다"는 장부상의 예약일 뿐이다. 그 직후에야 진짜 flash Read 명령이 방금 예약한 그 자리에 대해 실행된다.

<div style="margin-top: 60px;"></div>

## 실측 검증

빈 기기에서 Read 비율 80% 워크로드를 네이티브 CLI 로 직접 돌려서 확인했다 (요청 19개, 그중 다수가 첫 접근):

```
Issued_Flash_Read_CMD="16"       Read 는 16번 모두 실제 Read 명령이 나감
Issued_Flash_Program_CMD="3"     Program 은 딱 진짜 write 개수(3개)만큼만
CMT_Misses_For_Read="15"         그 16개 Read 중 15개가 "매핑 없음" 첫 접근이었음
```

Program 명령 수가 정확히 진짜 write 개수와 일치한다 - 매핑 없는 15번의 Read 중 어느 것도 Program 명령을 만들어내지 않았다. 페이지 예약은 순수하게 장부(매핑 테이블 + free pool 카운트) 상의 일이라는 게 이걸로 확인된다.

<div style="margin-top: 60px;"></div>

## 왜 MQSim 은 이렇게 설계됐나

MQSim 은 원래 **실제 애플리케이션을 흉내내는 시뮬레이터가 아니라, SSD 성능(지연시간·처리량)을 측정하는 벤치마크 프레임워크**다. 지연시간을 재려면 Read 명령이 가리킬 **진짜 물리 주소**가 있어야 한다 - "매핑이 없으니 그냥 0을 즉시 반환" 같은 공짜 경로는 없다.

원본이 이 상황을 애초에 안 만나게 막아주는 장치가 따로 있다 - **preconditioning**(`exec/SSD_Device.cpp:429`):

```cpp
void SSD_Device::Perform_preconditioning(std::vector<Utils::Workload_Statistics *> workload_stats)
{
    if (Preconditioning_required) {
        ...
        this->Firmware->Perform_precondition(workload_stats);
        ...
    }
}
```

`Enabled_Preconditioning=true` 면, 실제 측정이 시작되기 **전에** 워크로드 통계를 바탕으로 주소 공간을 미리 채워둔다 - 그래서 측정 구간에서는 Read 가 매핑 없는 주소를 만날 일이 애초에 없다.

이 프로젝트는 데모 속도를 위해 모든 프리셋에서 `Enabled_Preconditioning=false` 로 두고 있다 (전체 기기를 미리 다 채우는 건 짧은 데모에 비해 너무 느리다). `online_create_entry_for_reads()` 는 바로 이 "미리 채워두기"가 생략됐을 때를 위한 **지연(lazy) 버전**이다 - 시작 전에 한꺼번에 치르는 대신, 실제로 그 주소가 처음 건드려지는 순간에 그 자리에서 같은 비용을 치른다.

<div style="margin-top: 60px;"></div>

## GC/마모 평준화와의 관계

이렇게 예약된 페이지는 매핑 테이블 입장에서 진짜로 쓰인 페이지와 **전혀 구별되지 않는다.** 그래서:

- 나중에 같은 LPA 에 진짜 write 가 오면, 이 페이지는 보통의 덮어쓰기와 똑같이 invalidate 되고 새 페이지가 할당된다.
- GC 가 이 페이지가 속한 block 을 victim 으로 고르는 시점에 아직 이 페이지가 유효하다면, 보통의 valid 페이지와 똑같이 다른 곳으로 마이그레이션된다.

즉 한 번 예약되면 이후로는 보통의 valid/invalid/GC 생애주기를 그대로 따라간다 - 회수되기 위해 특별한 처리가 필요하지 않다.

**단, 회수되기 전까지는 free pool 을 write 와 똑같이 소비한다** - 즉 GC 발동 시점(빈 block 개수 기준)에 영향을 줄 수 있다. Read 비율이 높을수록, 특히 시작 직후에는 이런 "가짜 write" 가 상당한 비중을 차지할 수 있다.

<div style="margin-top: 60px;"></div>

## 왜 UI 에서 없앴나

실제 벤치마크 규모(수천 개 block, 수백만 요청)에서는 이런 첫 접근 Read 몇 개는 통계에 묻혀 눈에 띄지 않는다. 하지만 이 프로젝트는 정반대로 - block 8개짜리 기기에서 이벤트 하나하나를 화면에 보여준다. 그 규모에서는 "Read" 라고 적힌 로그 한 줄이 실제로는 페이지 하나를 화면에 새로 초록색으로 칠하는 걸 보게 되는데, 이건 GC/마모 평준화 시연이 원래 보여주려는 것과 무관한 곳에서 혼란만 준다.

그래서 Read 비율 슬라이더 자체를 없애고, `Read_Percentage` 를 항상 `0`으로 고정했다 (`src/data/mqsimConfigs.ts`). 이 값은 애초에 모든 프리셋에서 기본값이 `0`이었으므로, GC/WL 시연 결과에는 아무 영향이 없다.

<div style="margin-top: 60px;"></div>

## 참고

- [MQSim](/ftl-visual-simulator/reference/mqsim/) — 상위 문서
- [MQSim 개요](/ftl-visual-simulator/reference/mqsim/overview/)
- [버그 목록](/ftl-visual-simulator/reference/bug-list/) — 진짜 결함을 모아두는 자매 문서
- [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) — 원본 C++ 코드에 손댄 경우를 모아두는 자매 문서
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
