---
layout: default
title: 명령 서스펜드가 한 번도 작동한 적이 없던 버그 — TSU 스케줄러 4개 결함
permalink: /ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/
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

# 명령 서스펜드가 한 번도 작동한 적이 없던 버그 — TSU 스케줄러 4개 결함

"마모평준화 시연"의 static WL 임계값을 1보다 높여보려다가, 특정 설정에서 시뮬레이션이 에러 한 줄 없이 조용히 멈춰버리는(hang) 문제를 다시 마주쳤다. 사실 이 정지 자체는 이전 세션에서도 한 번 밟았던 것으로, 그때는 "block 개수가 작을 때 TSU_FLIN 스케줄러에서 멈춘다"고 원인을 추정하고 GitHub 이슈로만 남겨둔 채 덮어뒀었다. 이번에 제대로 추적해보니 그 추정 자체가 틀렸다 — `TSU_FLIN` 은 이 프로젝트에서 **인스턴스화조차 되지 않는 완전한 죽은 코드**였고, 실제 원인은 서로 다른 층위에 있는 4개의 독립된 버그가 사슬처럼 얽힌 것이었다. 넷 다 처음 vendoring 된 이후 이 프로젝트가 한 번도 손대지 않은, 원본 그대로의 코드였다.

<div style="margin-top: 60px;"></div>

## 1. 잘못된 단서부터 바로잡기 — TSU_FLIN 은 죽은 코드

`engine/mqsim/src/ssd/TSU_FLIN.cpp` 전체가 `/* ... */` 블록 주석으로 감싸져 있고, `SSD_Device.cpp` 에서 `TSU_FLIN` 을 생성하는 유일한 지점도 `/*case Flash_Scheduling_Type::FLIN: ...*/` 로 통째로 주석 처리돼 있었다. 즉 `Transaction_Scheduling_Policy` 를 아무리 바꿔도 `TSU_FLIN` 이 실행될 방법이 없다. 이 프로젝트가 실제로 쓰는 설정은 `PRIORITY_OUT_OF_ORDER`(`TSU_Priority_OutOfOrder`) — 진짜 범인은 여기, 그리고 그 형제 클래스 `TSU_OutOfOrder` 안에 있었다.

<div style="margin-top: 60px;"></div>

## 2. 버그 (1) — switch-case fallthrough 로 서스펜드가 항상 무력화됨

`service_read_transaction()`/`service_write_transaction()`(두 스케줄러 클래스 모두 동일 패턴)이 칩 상태를 검사하는 마지막 switch 문:

```cpp
switch (cs) {
case ChipStatus::IDLE:
    break;
case ChipStatus::WRITING:
    if (!programSuspensionEnabled || HasSuspendedCommand(chip)) return false;
    if (Expected_finish_time(chip) - Time() < writeReasonableSuspensionTimeForRead) return false;
    suspensionRequired = true;
    // break; 가 없다 — 바로 아래 ERASING 케이스로 그대로 흘러들어감
case ChipStatus::ERASING:
    if (!eraseSuspensionEnabled || HasSuspendedCommand(chip)) return false;
    if (Expected_finish_time(chip) - Time() < eraseReasonableSuspensionTimeForRead) return false;
    suspensionRequired = true;
    // 여기도 break; 없음 — default 로 흘러들어가 무조건 false
default:
    return false;
}
issue_command_to_chip(sourceQueue1, sourceQueue2, Transaction_Type::READ, suspensionRequired);
```

`suspensionRequired = true;` 를 설정한 직후 `break;` 가 없어서, WRITING 케이스는 (엉뚱하게도) ERASING 케이스의 조건까지 다시 통과해야 하고, ERASING 케이스는 그 뒤 `default: return false;` 로 그대로 떨어진다. 결과적으로 **두 케이스 다 `issue_command_to_chip()` 에 도달하는 경로 자체가 없다** — 서스펜드가 조건을 만족해도 절대 실제로 발동하지 않는다. `TSU_OutOfOrder.cpp`(READ 서스펜드) 3곳, `TSU_Priority_OutOfOrder.cpp`(READ 서스펜드) 3곳, 각 파일의 WRITE 서스펜드(ERASING 케이스) 1곳까지 총 6곳이 동일 패턴.

<div style="margin-top: 60px;"></div>

## 3. 버그 (2) — 생성자 인자 순서가 뒤바뀜

`TSU_Base` 의 생성자 시그니처는:

```cpp
TSU_Base(..., PlaneNoPerDie,
         bool EraseSuspensionEnabled, bool ProgramSuspensionEnabled,
         sim_time_type WriteReasonableSuspensionTimeForRead,
         sim_time_type EraseReasonableSuspensionTimeForRead,
         sim_time_type EraseReasonableSuspensionTimeForWrite);
```

그런데 `TSU_OutOfOrder`/`TSU_Priority_OutOfOrder` 두 파생 클래스 모두 이걸 호출할 때 시간 3개를 먼저, bool 2개를 나중에 넘긴다:

```cpp
: TSU_Base(..., PlaneNoPerDie,
           WriteReasonableSuspensionTimeForRead, EraseReasonableSuspensionTimeForRead, EraseReasonableSuspensionTimeForWrite,
           EraseSuspensionEnabled, ProgramSuspensionEnabled)
```

C++ 는 타입만 맞으면(둘 다 정수 계열이라 암묵적 변환이 가능) 컴파일 에러를 내지 않는다. 그 결과 `programSuspensionEnabled` 은 실제로는 `WriteReasonableSuspensionTimeForRead` 의 나노초 값(0 이 아닌 큰 수)을 bool 로 받아 **항상 true** 가 되고, 반대로 `eraseReasonableSuspensionTimeForRead`/`Write` 자리에는 원래 bool 이었던 0/1이 들어가 사실상 "즉시 만료" 취급된다. 이 때문에 `CMD_Suspension_Support` 를 `ERASE` 로만 설정해도(`ProgramSuspensionEnabled` 는 false 여야 정상) 런타임에는 항상 true 로 읽혔다 — 직접 로그를 찍어 `progSusp=1` 로 확인.

<div style="margin-top: 60px;"></div>

## 4. 버그 (3), (4) — 서스펜드/리쥼 시 활성 다이 카운터가 어긋남

버그 (1)·(2)를 고치고 나서야 서스펜드가 처음으로 실제 실행됐는데, 그러자 곧바로 진짜 교착 상태(hang)가 드러났다. 원인은 `ChipBookKeepingEntry`:

```cpp
void PrepareSuspend() { HasSuspend = true; No_of_active_dies = 0; }
void PrepareResume()  { HasSuspend = false; }  // 카운터를 복원하지 않음
```

`Send_command_to_chip()` 에서 `PrepareSuspend()` 호출이 `if (chipBKE->OngoingDieCMDTransfers.size()) { ... }` 뒤에 숨어 있었다 — 이 조건은 멀티 다이 명령 인터리빙 전용이라, 이 프로젝트가 쓰는 `die_no_per_chip = 1` 구성에서는 사실상 항상 false. 그래서 서스펜드해도 `No_of_active_dies` 가 리셋되지 않고 "여전히 활성" 상태로 남는다. 설령 이걸 고쳐도, 그 짝인 `PrepareResume()` 이 카운터를 다시 올려주지 않으니 나중에 리쥼된 명령이 완료될 때 `No_of_active_dies--` 가 0에서 한 번 더 빠지면서 `unsigned int` 언더플로 — 이후 모든 `== 0` 체크(IDLE/WAIT_FOR_DATA_OUT 전이 조건)가 영원히 실패해 칩이 그 자리에서 영구 정지한다.

<div style="margin-top: 60px;"></div>

## 5. 왜 지금까지 아무도 못 봤나 — 버그 (1)이 나머지 셋을 전부 가리고 있었다

버그 (1)이 **서스펜드 자체가 시도조차 안 되게** 막고 있었기 때문에, 버그 (2)·(3)·(4)는 처음부터 실행될 기회가 없는 죽은 경로였다. 버그 (1)을 고쳐야 버그 (2)가 드러나고(그래도 여전히 서스펜드는 됨 — 다만 정책과 무관하게 항상 "가능"으로 오판), 버그 (2)까지 고쳐서 `programSuspensionEnabled` 이 비로소 정확히 false 로 읽히게 되자 — 이번엔 (여전히 활성화된) erase 서스펜드가 실제 발동하면서 버그 (3)·(4)가 드러났다. 네 겹으로 겹친 우연이 아니라, 뒤엣것들이 전부 앞엣것 뒤에 숨어서 몇 년째 아무도 밟아본 적 없는 코드였던 셈이다.

<div style="margin-top: 60px;"></div>

## 6. 수정

- `TSU_OutOfOrder.cpp`, `TSU_Priority_OutOfOrder.cpp`: `suspensionRequired = true;` 뒤에 각각 `break;` 추가(총 6곳).
- 두 파일의 `TSU_Base(...)` 호출 인자 순서를 시그니처와 일치하도록 재배열.
- `NVM_PHY_ONFI_NVDDR2.cpp`: `chipBKE->PrepareSuspend()` 호출을 `OngoingDieCMDTransfers` 조건 밖으로 꺼내 무조건 호출.
- `NVM_PHY_ONFI_NVDDR2.h`: `PrepareResume()` 이 `No_of_active_dies` 를 다시 증가시키도록 수정.

<div style="margin-top: 60px;"></div>

## 7. 검증

- `test:engine`(골든 리그레션 3/3), `test:engine:unit`(GMock 12/12) 모두 수정 전과 완전히 동일하게 통과 — 골든 시나리오는 이 서스펜드 경로 근처에 가지 않는 규모라 무관.
- "마모평준화 시연" 기본값(threshold=1)으로 네이티브 CLI 완주 확인: 100% 진행, `Total_WL_Executions="1"`(기존에 검증된 불변식) 그대로 유지.
- 같은 설정에서 threshold 를 2/5/10/20/50 으로 올려도 전부 100% 완주(이전에는 threshold 2부터 이미 응답 없음).
- WASM 재빌드 후 브라우저에서 라이브 확인: WL 발동 → 자동 정지 → 설명 버튼 → 재생 재개까지 프리징 없이 정상 동작, 콘솔 에러 없음.

<div style="margin-top: 60px;"></div>

## 8. 남은 문제

이 넷을 고친 뒤에도, 원래보다 훨씬 큰 스케일(같은 설정에서 이벤트 900만 개 이상, GC 사이클 여러 번을 정상적으로 거친 뒤)에서 한 번 더 비슷한 정지를 관찰했다. 이번엔 `No_of_active_dies` 이상은 아니었고(직접 계측해서 확인), 어느 GC 후보 block 의 마이그레이션이 끝까지 완료되지 못하고 이벤트 큐가 조용히 비어버리는 패턴이었다. 근본 원인은 아직 못 찾았다 — 이 프로젝트가 실제로 쓰는 규모(threshold=1, 기본 Stop_Time)에는 전혀 영향이 없어서 후순위로 남겨뒀다.

> **해결됨 (2026-09-24)**: 이 정지는 LPA barrier 에서 풀려난 트랜잭션의 완료가 data cache manager 에 전달되지 않아 back-pressure 카운터가 새던 upstream 버그였다(#21). 고치고 나니 그 뒤에 숨어 있던 정지·크래시 버그 3개가 더 드러났다 — [정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그 4개](/ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/) 참고.

<div style="margin-top: 60px;"></div>

## 참고

- [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/)
- [GC 자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/) — 마찬가지로 "몇 년째 아무도 밟아본 적 없던 코드 경로" 유형
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
- [GitHub 이슈 #41](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/issues/41) — 이 버그를 처음 밟았을 때(원인을 TSU_FLIN 으로 잘못 추정) 남긴 기록
