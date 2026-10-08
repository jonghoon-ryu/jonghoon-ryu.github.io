---
layout: default
title: 2. SSD 와 호스트 만들기
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step2-build-ssd/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 2. SSD 와 호스트 만들기

`main()` 가 시나리오마다 두 객체를 만든다 — SSD 쪽 `SSD_Device` 와 호스트 쪽 `Host_System`. 이 단계가 끝나면 모든 부품이 **만들어져 있고 서로 가리킨다.** 그러나 아직 시각은 0 이고 이벤트는 하나도 없다.


<div style="margin-top: 60px;"></div>

## 1. SSD_Device 생성 (`SSD_Device.cpp:22`)

<svg viewBox="0 0 980 470" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="SSD_Device 생성 순서"><defs><marker id="abld" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="ablds" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">SSD_Device 생성자는 아래에서 위로 쌓는다 (exec/SSD_Device.cpp)</text><rect x="100" y="400" width="330" height="36" rx="6" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="118" y="423" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">1</text><text x="150" y="423" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">Flash_Chip × 32</text><text x="445" y="423" font-size="11" fill="#4d5656" text-anchor="start">:38 · 칩마다 AddObject (엔진 등록)</text><rect x="100" y="360" width="330" height="36" rx="6" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="118" y="383" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">2</text><text x="150" y="383" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">ONFI_Channel_NVDDR2 × 8</text><text x="445" y="383" font-size="11" fill="#4d5656" text-anchor="start">:75 · 칩을 묶음. 엔진에는 등록 안 함</text><rect x="100" y="320" width="330" height="36" rx="6" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="118" y="343" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">3</text><text x="150" y="343" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">NVM_PHY_ONFI_NVDDR2</text><text x="445" y="343" font-size="11" fill="#4d5656" text-anchor="start">:101 · 채널 컨트롤러</text><rect x="100" y="280" width="330" height="36" rx="6" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="118" y="303" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">4</text><text x="150" y="303" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">FTL (껍데기)</text><text x="445" y="303" font-size="11" fill="#4d5656" text-anchor="start">:114 · 포인터만 쥔다</text><rect x="100" y="240" width="330" height="36" rx="6" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="118" y="263" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">5</text><text x="150" y="263" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">TSU_Priority_OutOfOrder</text><text x="445" y="263" font-size="11" fill="#4d5656" text-anchor="start">:123 · 설정의 Transaction_Scheduling_Policy 로 선택</text><rect x="100" y="200" width="330" height="36" rx="6" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="118" y="223" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">6</text><text x="150" y="223" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">Flash_Block_Manager</text><text x="445" y="223" font-size="11" fill="#4d5656" text-anchor="start">:183 · plane 별 block 풀</text><rect x="100" y="160" width="330" height="36" rx="6" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="118" y="183" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">7</text><text x="150" y="183" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">Address_Mapping_Unit_Page_Level</text><text x="445" y="183" font-size="11" fill="#4d5656" text-anchor="start">:191 · 직전에 flow 별 주소 범위·자원 분할</text><rect x="100" y="120" width="330" height="36" rx="6" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="118" y="143" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">8</text><text x="150" y="143" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">GC_and_WL_Unit_Page_Level</text><text x="445" y="143" font-size="11" fill="#4d5656" text-anchor="start">:294</text><rect x="100" y="80" width="330" height="36" rx="6" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="118" y="103" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">9</text><text x="150" y="103" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">Data_Cache_Manager_Flash_Advanced</text><text x="445" y="103" font-size="11" fill="#4d5656" text-anchor="start">:316 · flow 별 캐시 모드 전달</text><rect x="100" y="40" width="330" height="36" rx="6" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="118" y="63" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">10</text><text x="150" y="63" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">Host_Interface_NVMe</text><text x="445" y="63" font-size="11" fill="#4d5656" text-anchor="start">:350 · 안에서 입력 스트림 관리자·요청 fetch 유닛 생성</text><line x1="40" y1="440" x2="40" y2="40" stroke="#7f8c8d" stroke-width="2" marker-end="url(#abld)"/><text x="40" y="458" font-size="11" fill="#7f8c8d" text-anchor="start">쌓는 방향 ↑</text></svg>

코드 안의 `Step 1 … 10` 주석과 번호가 같다. FTL 은 4번에서 만들어지지만 **껍데기**일 뿐이고, 진짜 FTL 기능은 5~8번(TSU · 블록 매니저 · 주소 매핑 · GC/WL)과 9번(캐시)이 나눠 갖는다. 각 부품이 만들어질 때마다 포인터가 `ftl->` 에 꽂힌다.

```
ftl->TSU    ftl->BlockManager    ftl->Address_Mapping_Unit
ftl->GC_and_WL_Unit              ftl->Data_cache_manager
```

**설정이 구현을 고른다.** 예를 들어 5번 TSU 는 `Transaction_Scheduling_Policy` 값에 따라 `TSU_OutOfOrder`(`:142`) 또는 `TSU_Priority_OutOfOrder`(`:150`)가 된다. `FLIN` 을 위한 `case`(`:157`~)도 있지만 **주석 처리**되어 있어 고르면 `default` 의 예외로 떨어진다. 7번 주소 매핑은 `Address_Mapping` 이 `PAGE_LEVEL` 이면 `Address_Mapping_Unit_Page_Level`(`:273`), `HYBRID` 면 `Address_Mapping_Unit_Hybrid`(`:282`)이다 — 후자는 빈 스텁이다([원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/)).

7번 직전에는 `Logical_Address_Partitioning_Unit::Allocate_logical_address_for_flows()` 가 불려, **flow 마다 논리 주소 범위와 쓸 수 있는 채널·칩·다이·플레인을 나눈다.** flow 가 둘이면 논리 주소 공간이 반으로 갈라진다.


<div style="margin-top: 60px;"></div>

## 2. Host_System 생성 (`Host_System.cpp:11`)

1. `PCIe_Link` 를 만든다(대역폭·레인 수는 설정). `PCIe_Root_Complex` 와 `PCIe_Switch` 도 만들어 서로 연결한다.
2. flow 정의마다 `IO_Flow_Synthetic` 또는 `IO_Flow_Trace_Based` 를 `new` 하고 엔진에 등록한다(`:35` 의 루프). 구조체의 값이 생성자 인자로 옮겨지면서 몇 가지가 변환된다.
   - `Working_Set_Percentage` → `/100` 한 비율. 이 비율만큼 flow 가 접근할 주소의 **끝**이 줄어든다.
   - 큐 번호는 `flow_id + 1` (NVMe 0번 큐는 admin 전용).
3. 루트 컴플렉스에 flow 목록을 알려 준다 (완료 메시지를 해당 flow 에 돌려주려고).

## 3. 연결 (`host.Attach_ssd_device(&ssd)`, `Host_System.cpp:102`)

```
ssd.Attach_to_host(PCIe_switch)            // SSD 의 호스트 인터페이스가 스위치를 안다
PCIe_switch->Attach_ssd_device(Host_interface)   // 스위치가 호스트 인터페이스를 안다
```

이제 `PCIe_Link → PCIe_Switch → Host_Interface` 로 메시지가 흐를 수 있다.


<div style="margin-top: 60px;"></div>

## 정리

| 만들어진 것 | 시각 | 이벤트 |
|---|---|---|
| SSD 부품 전부, 호스트 부품 전부, 서로의 포인터 | 0 | **없음** |

다음 단계에서 엔진이 이 객체들을 세 번 훑으며 신호를 연결하고, 각자 초기화하고, 첫 이벤트를 등록한다.

## 확인해 보기

1. `ssdconfig.xml` 에서 `Transaction_Scheduling_Policy` 를 `FLIN` 으로 바꾸면 어느 줄이 실행되나?
2. FTL 객체의 `Start_simulation()` 과 `Execute_simulator_event()` 는 무엇을 하나? (`FTL.cpp:891`, `:895`)
3. 채널 객체는 왜 `Simulator->AddObject()` 를 하지 않을까?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 1. 실행 명령과 main()](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step1-run-and-main/)</span><span>[3. 엔진 시작과 이벤트 루프 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)</span></div>
