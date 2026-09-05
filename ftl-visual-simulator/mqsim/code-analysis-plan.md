---
layout: default
title: MQSim 코드 분석 계획
permalink: /ftl-visual-simulator/mqsim/code-analysis-plan/
---
<style>
.progress-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  color: #555;
}
.progress-bar-track {
  flex: 1;
  max-width: 280px;
  height: 6px;
  border-radius: 4px;
  background: #e2e2e2;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  width: 0%;
  background: #3a7d44;
  transition: width 0.2s ease;
}
.session.done h3 {
  color: #999;
  text-decoration: line-through;
  text-decoration-color: #bbb;
}
.session.done {
  opacity: 0.6;
}
.session {
  margin-top: 70px;
  padding-top: 32px;
  border-top: 1px solid #ddd;
}
.session:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}
table.plan-calendar {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
table.plan-calendar .row-mark {
  cursor: pointer;
  user-select: none;
}
</style>

# MQSim 코드 분석 계획

시뮬레이터를 만들기 전에, MQSim 소스코드 자체를 처음부터 끝까지 체계적으로 읽는 계획. [개발 계획](/ftl-visual-simulator/plan/) 과 같은 16세션 날짜( 9/4 ~ 10/25 )를 그대로 따라가되, 여기서는 **그 세션에 어떤 MQSim 소스를 읽을 것인가**만 다룬다.

<div style="margin-top: 40px;"></div>

## 왜 이 순서인가

- **하향식( top-down )** : 전체 그림 → 요청이 들어오는 입구 → FTL 핵심(매핑·GC·WL) → 요청이 빠져나가는 출구(스케줄링·물리) → 입출력 주변부(캐시·통계·workload) → 마지막에 전체를 한 번에 관통
- 각 세션은 [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) 문서의 해당 부분을 먼저 훑고, 실제 소스 파일을 열어 문서의 설명과 코드가 정말 일치하는지 확인하는 방식으로 진행
- [개발 계획](/ftl-visual-simulator/plan/) 의 "MQSim/FTL 심화" 항목과 내용이 겹치는 세션도 있음 — 여긴 그걸 하나로 모아 더 깊게 파는 버전

<div style="margin-top: 60px;"></div>

## 세션

<div class="progress-box">
  <span>진행률: <span id="progress-count">0 / 16</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div class="session" data-session="1" markdown="1">

### 1. 전체 그림 잡기 — 디렉터리 구조와 파이프라인

읽을 파일 : `src/` 디렉터리 구조 훑어보기, `src/exec/SSD_Device.h`( 주석의 파이프라인 다이어그램 ), `src/ssd/FTL.h`, `src/exec/Host_System.h`

<div style="overflow-x:auto;">
<svg viewBox="0 0 1200 260" style="width:100%;max-width:900px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-p1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .title { fill:#2c3e50; font-size:15px; font-weight:700; text-anchor:middle; }
    .divider { stroke:#c7d0da; stroke-width:1; }
    .body { fill:#3d4a5a; font-size:11px; text-anchor:middle; }
    .flow { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-p1); fill:none; }
    .endlabel { fill:#2c3e50; font-size:13px; font-weight:700; text-anchor:middle; }
  </style>

  <text x="35" y="140" class="endlabel">Host</text>
  <line x1="5" y1="135" x2="95" y2="135" class="flow"/>

  <rect x="100" y="80" width="160" height="110" rx="8" class="box"/>
  <text x="180" y="102" class="title">Host_Interface</text>
  <line x1="112" y1="112" x2="248" y2="112" class="divider"/>
  <text x="180" y="132" class="body">NVMe / SATA</text>
  <text x="180" y="150" class="body">요청 큐 관리</text>

  <line x1="260" y1="135" x2="300" y2="135" class="flow"/>

  <rect x="300" y="80" width="160" height="110" rx="8" class="box"/>
  <text x="380" y="102" class="title">Data_Cache</text>
  <text x="380" y="118" class="title">_Manager</text>
  <line x1="312" y1="130" x2="448" y2="130" class="divider"/>
  <text x="380" y="150" class="body">SSD 내부 DRAM</text>
  <text x="380" y="166" class="body">쓰기 캐시</text>

  <line x1="460" y1="135" x2="500" y2="135" class="flow"/>

  <rect x="500" y="40" width="230" height="190" rx="8" class="box"/>
  <text x="615" y="62" class="title">FTL</text>
  <line x1="512" y1="72" x2="718" y2="72" class="divider"/>
  <text x="615" y="95" class="body">Address_Mapping_Unit</text>
  <text x="615" y="115" class="body">Flash_Block_Manager</text>
  <text x="615" y="135" class="body">GC_and_WL_Unit</text>
  <text x="615" y="155" class="body">TSU</text>
  <text x="615" y="178" class="body" font-style="italic">(Session 3~6에서 hook 추가)</text>

  <line x1="730" y1="135" x2="770" y2="135" class="flow"/>

  <rect x="770" y="80" width="180" height="110" rx="8" class="box"/>
  <text x="860" y="102" class="title">NVM_PHY_ONFI</text>
  <line x1="782" y1="112" x2="938" y2="112" class="divider"/>
  <text x="860" y="132" class="body">+ ONFI_Channel</text>
  <text x="860" y="150" class="body">타이밍 · 버스 경합</text>

  <line x1="950" y1="135" x2="990" y2="135" class="flow"/>

  <text x="1080" y="128" class="endlabel">Flash_Chip</text>
  <text x="1080" y="146" class="endlabel">(Die→Plane→</text>
  <text x="1080" y="164" class="endlabel">Block→Page)</text>
</svg>
</div>

- `exec/host/nvm_chip/sim/ssd/utils` 6개 디렉터리가 각각 뭘 담당하는지 감 잡기
- `FTL` 클래스가 `Address_Mapping_Unit` / `Flash_Block_Manager` / `GC_and_WL_Unit` / `TSU` 4개를 들고 있다는 구조부터 확인
- `SSD_Device`( 위 그림 전체 조립 )와 `Host_System`( workload 로부터 요청 생성 )이 어떻게 서로를 참조하는지( `host.Attach_ssd_device(&ssd)` )
- 체크포인트 : "SSD_Device 하나가 조립되면 그 안에 뭐가 들어있는지" 를 위 그림 없이 직접 그려볼 수 있으면 통과

</div>

<div class="session" data-session="2" markdown="1">

### 2. 시뮬레이션 엔진 — 이산 이벤트가 어떻게 도는가

읽을 파일 : `src/sim/Sim_Object.h`, `src/sim/Engine.h`, `src/sim/EventTree.h`, `src/main.cpp`

<div style="overflow-x:auto;">
<svg viewBox="0 0 700 320" style="width:100%;max-width:560px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-p2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box2 { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .title2 { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
    .body2 { fill:#3d4a5a; font-size:11px; text-anchor:middle; }
    .flow2 { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-p2); fill:none; }
    .lbl2 { fill:#5a6472; font-size:10.5px; text-anchor:middle; }
  </style>

  <rect x="270" y="20" width="180" height="70" rx="8" class="box2"/>
  <text x="360" y="45" class="title2">EventTree</text>
  <text x="360" y="65" class="body2">시각순 이벤트 보관</text>

  <path d="M 450 60 Q 560 100 500 170" class="flow2"/>
  <text x="560" y="120" class="lbl2">가장 이른</text>
  <text x="560" y="134" class="lbl2">이벤트 pop</text>

  <rect x="270" y="170" width="180" height="80" rx="8" class="box2"/>
  <text x="360" y="195" class="title2">Sim_Object</text>
  <text x="360" y="215" class="body2">Execute_simulator</text>
  <text x="360" y="230" class="body2">_event() 호출</text>

  <path d="M 270 220 Q 150 190 250 90" class="flow2"/>
  <text x="150" y="150" class="lbl2">필요하면 새</text>
  <text x="150" y="164" class="lbl2">이벤트 등록</text>
  <text x="150" y="178" class="lbl2">(Register_sim_event)</text>

  <text x="360" y="295" class="body2" font-style="italic">Engine( = Simulator 매크로 )이 이 루프 전체를 소유하는 싱글턴</text>
</svg>
</div>

- `Sim_Object::Execute_simulator_event()` 가 모든 구성요소의 공통 진입점이라는 것 확인
- `Engine`( `Simulator` 매크로 )이 싱글턴이고 `EventTree` 로 이벤트를 시간순 관리한다는 것 확인 — 위 그림의 루프가 사실상 MQSim 전체의 심장박동
- `main.cpp` 에서 설정 파싱 → 워크로드 파싱 → 시나리오 루프( `Simulator->Reset()` → `SSD_Device` 생성 → `Host_System` 생성 → `Simulator->Start_simulation()` ) 흐름을 코드에서 직접 짚어보기
- 실시간 개념이 없고 "다음 이벤트 시각"만 따라가는 구조라서, 90만 건 요청도 몇 초 만에 끝나는 이유가 여기 있다는 것 확인
- 체크포인트 : "이벤트 하나가 등록되고 실행되는 과정"을 코드 줄 번호로 설명할 수 있으면 통과

</div>

<div class="session" data-session="3" markdown="1">

### 3. 주소 매핑 (1) — 자료구조

읽을 파일 : `src/ssd/Address_Mapping_Unit_Base.h`, `src/ssd/Address_Mapping_Unit_Page_Level.h`, `src/ssd/Flash_Block_Manager_Base.h`

<div style="overflow-x:auto;">
<svg viewBox="0 0 720 260" style="width:100%;max-width:600px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <style>
    .plane3 { fill:#fbfbfb; stroke:#34495e; stroke-width:2; }
    .valid3 { fill:#bfe3c8; stroke:#2f8f4e; }
    .invalid3 { fill:#f3c6c6; stroke:#c0392b; }
    .free3 { fill:#e9ecef; stroke:#9aa4ad; }
    .lbl3 { fill:#2c3e50; font-size:12px; font-weight:700; }
    .small3 { fill:#3d4a5a; font-size:10.5px; }
  </style>

  <rect x="20" y="20" width="330" height="220" rx="8" class="plane3"/>
  <text x="35" y="42" class="lbl3">Plane ( PlaneBookKeepingType )</text>

  <text x="35" y="65" class="small3">Data_wf( 사용자 쓰기 block )</text>
  <rect x="35" y="72" width="24" height="24" class="valid3"/><rect x="61" y="72" width="24" height="24" class="valid3"/>
  <rect x="87" y="72" width="24" height="24" class="invalid3"/><rect x="113" y="72" width="24" height="24" class="free3"/>

  <text x="35" y="120" class="small3">GC_wf( GC 쓰기 block )</text>
  <rect x="35" y="127" width="24" height="24" class="valid3"/><rect x="61" y="127" width="24" height="24" class="free3"/>
  <rect x="87" y="127" width="24" height="24" class="free3"/><rect x="113" y="127" width="24" height="24" class="free3"/>

  <text x="35" y="175" class="small3">Translation_wf( 매핑 테이블용 block )</text>
  <rect x="35" y="182" width="24" height="24" class="invalid3"/><rect x="61" y="182" width="24" height="24" class="valid3"/>

  <text x="35" y="225" class="small3">□ valid  □ invalid  □ free — 각 칸 = Page, 색은 Invalid_page_bitmap 기준</text>

  <rect x="380" y="20" width="320" height="220" rx="8" class="plane3"/>
  <text x="395" y="42" class="lbl3">Block_Pool_Slot_Type ( block 1개 )</text>
  <text x="395" y="70" class="small3">Current_status : IDLE / GC_WL / USER / ...</text>
  <text x="395" y="95" class="small3">Invalid_page_bitmap : 0101...</text>
  <text x="395" y="120" class="small3">Erase_count : N</text>
  <text x="395" y="145" class="small3">Current_page_write_index</text>
  <text x="395" y="180" class="small3" font-style="italic">→ 우리 grid 색상은</text>
  <text x="395" y="198" class="small3" font-style="italic">  결국 이 구조체를 읽으면 됨</text>
</svg>
</div>

- `Block_Pool_Slot_Type`( `Invalid_page_bitmap`, `Erase_count`, `Current_status` 상태 머신 )가 실제 block 상태를 어떻게 들고 있는지 — 위 그림 오른쪽
- `PlaneBookKeepingType` 의 `Data_wf` / `GC_wf` / `Translation_wf`( double write frontier ) 구조 이해 — 사용자 쓰기와 GC 쓰기가 같은 block 을 안 쓰는 이유( hot/cold 분리 ), 위 그림 왼쪽
- CMT( Cached Mapping Table ) 관련 메서드( `Exists`, `Retrieve_ppa`, `Reserve_slot_for_lpn` )가 매핑 테이블 전체를 캐싱하지 않는 이유
- `Free_block_pool`( `std::multimap`, erase count 기준 정렬 )이 마모 평준화와 어떻게 연결되는지 미리 확인( Session 6 예고 )
- 체크포인트 : "매핑 테이블 하나의 엔트리가 무엇을 저장하는지" 정확히 설명

</div>

<div class="session" data-session="4" markdown="1">

### 4. 주소 매핑 (2) — 실제 동작

읽을 파일 : `src/ssd/Address_Mapping_Unit_Page_Level.cpp` ( `Translate_lpa_to_ppa_and_dispatch` 중심 )

<div style="overflow-x:auto;">
<svg viewBox="0 0 780 210" style="width:100%;max-width:640px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-p4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t4{font-size:11.5px;font-weight:700;text-anchor:middle;} .b4{font-size:9.5px;text-anchor:middle;}
    .f4{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-p4);fill:none;}
  </style>
  <rect x="10" y="70" width="150" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="85" y="93" class="t4" fill="#134e4a">query_cmt()</text>
  <text x="85" y="110" class="b4" fill="#134e4a">CMT hit/miss 판정</text>

  <line x1="160" y1="100" x2="200" y2="100" class="f4"/>
  <rect x="200" y="70" width="170" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="285" y="90" class="t4" fill="#134e4a">translate_lpa_to_ppa()</text>
  <text x="285" y="107" class="b4" fill="#134e4a">READ/WRITE 분기</text>

  <line x1="370" y1="100" x2="410" y2="100" class="f4"/>
  <rect x="410" y="10" width="170" height="60" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="495" y="30" class="t4" fill="#78350f">allocate_plane_for</text>
  <text x="495" y="47" class="b4" fill="#78350f">_user_write() (WRITE만)</text>
  <line x1="410" y1="100" x2="410" y2="40" class="f4"/>

  <rect x="410" y="70" width="170" height="60" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="495" y="90" class="t4" fill="#78350f">GC_and_WL_Unit</text>
  <text x="495" y="107" class="b4" fill="#78350f">Stop_servicing_writes()?</text>

  <line x1="580" y1="100" x2="620" y2="100" class="f4"/>
  <rect x="620" y="70" width="150" height="60" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="695" y="90" class="t4" fill="#78350f">allocate_page_in</text>
  <text x="695" y="107" class="b4" fill="#78350f">_plane_for_user_write()</text>

  <text x="390" y="170" class="b4" fill="#475569" font-style="italic">READ 경로는 CMT miss 시 online_create_entry_for_reads() 로 분기 (code-analysis.md 7-2절 참고)</text>
</svg>
</div>

- write 요청이 들어왔을 때 : 기존 매핑 조회( CMT hit/miss ) → 새 PPA 할당( `Flash_Block_Manager` 호출 ) → 매핑 갱신 → 기존 PPA invalidate, 이 순서를 코드에서 그대로 추적
- read 요청 경로도 동일하게 추적
- **주목할 점** : `translate_lpa_to_ppa()` 의 write 분기 안에서 `ftl->GC_and_WL_Unit->Stop_servicing_writes()` 가 true 를 반환하면 이 트랜잭션은 그 자리에서 실패 처리된다 — 정확한 조건은 `block_manager->Get_pool_size() < max_ongoing_gc_reqs_per_plane`(기본값 10), 즉 free 블록이 정말 얼마 안 남았을 때뿐이다( 소스 코드 주석 : "there are too few free pages remaining only for GC" ) — 매핑 코드 안에 GC 압박이 직접 개입하는 지점이라는 걸 놓치기 쉬움
- 체크포인트 : write 요청 하나가 `Translate_lpa_to_ppa_and_dispatch` 안에서 거치는 단계를 순서대로 나열, `Stop_servicing_writes()` 가 어떤 조건에서 write 를 막는지 설명

</div>

<div class="session" data-session="5" markdown="1">

### 5. GC — 트리거부터 erase 까지

읽을 파일 : `src/ssd/GC_and_WL_Unit_Base.h`, `src/ssd/GC_and_WL_Unit_Page_Level.cpp`( `Check_gc_required`, `GC_is_in_urgent_mode`, victim selection 부분 )

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 200" style="width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-p5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box5 { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .diamond5 { fill:#fff6df; stroke:#b8860b; stroke-width:2; }
    .title5 { fill:#2c3e50; font-size:12px; font-weight:700; text-anchor:middle; }
    .body5 { fill:#3d4a5a; font-size:10px; text-anchor:middle; }
    .flow5 { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-p5); fill:none; }
    .lbl5 { fill:#5a6472; font-size:10px; text-anchor:middle; }
  </style>

  <rect x="10" y="70" width="140" height="60" rx="8" class="box5"/>
  <text x="80" y="95" class="title5">Free block pool</text>
  <text x="80" y="112" class="body5">쓰기로 인해 감소</text>

  <line x1="150" y1="100" x2="200" y2="100" class="flow5"/>

  <polygon points="290,60 380,100 290,140 200,100" class="diamond5"/>
  <text x="290" y="95" class="title5">GC_Exec_Threshold</text>
  <text x="290" y="112" class="body5">넘었나?</text>

  <line x1="290" y1="140" x2="290" y2="175" class="flow5"/>
  <text x="290" y="192" class="lbl5">아니오 — 계속 진행</text>

  <line x1="380" y1="100" x2="430" y2="100" class="flow5"/>
  <text x="405" y="88" class="lbl5">예</text>

  <rect x="430" y="70" width="130" height="60" rx="8" class="box5"/>
  <text x="495" y="95" class="title5">Victim 선정</text>
  <text x="495" y="112" class="body5">( GC_Block_Selection</text>
  <text x="495" y="124" class="body5" font-size="9">_Policy = RGA )</text>

  <line x1="560" y1="100" x2="610" y2="100" class="flow5"/>

  <rect x="610" y="70" width="130" height="60" rx="8" class="box5"/>
  <text x="675" y="95" class="title5">Valid page</text>
  <text x="675" y="112" class="body5">migration</text>

  <line x1="740" y1="100" x2="790" y2="100" class="flow5"/>

  <rect x="790" y="70" width="100" height="60" rx="8" class="box5"/>
  <text x="840" y="95" class="title5">Block</text>
  <text x="840" y="112" class="body5">erase</text>
</svg>
</div>

- free block pool 이 줄어들 때 `Check_gc_required()` 가 왜/어떻게 불리는지 — 정확히는 write frontier 블록이 가득 차서 새 free 블록으로 교체되는 순간( 매 쓰기가 아님 )에만 호출된다는 것까지 확인. 위 그림의 첫 판단 지점
- `GC_is_in_urgent_mode()` 의 실제 분기 순서 확인 — `!preemptible_gc_enabled` 이면 `GC_Hard_Threshold` 확인 없이 곧바로 true( 우리 설정 `Preemptible_GC_Enabled=false` 라 항상 이 경로 ). `GC_Hard_Threshold` 가 실제로 쓰이는 건 `Preemptible_GC_Enabled=true` 일 때뿐이라는 것 코드로 확인
- `GC_Block_Selection_Policy`( GREEDY/RGA/RANDOM 계열/FIFO ) 중 실제 설정값( RGA )의 코드 분기 추적
- victim block 선정 → valid page migration → block erase, 3단계를 코드에서 순서대로 확인 — 위 그림의 나머지 3개 박스
- 체크포인트 : "GC 가 왜 지금 시작됐는지" 를 코드 조건문 기준으로 설명

</div>

<div class="session" data-session="6" markdown="1">

### 6. Wear-Leveling 실제 동작, 그리고 Hybrid 매핑의 진실

읽을 파일 : `src/ssd/Address_Mapping_Unit_Hybrid.h/cpp`, `GC_and_WL_Unit_Base.cpp` 의 wear-leveling 관련 부분( `check_static_wl_required`, `run_static_wearleveling`, `Use_dynamic_wearleveling` — ⚠️ Page_Level.cpp 가 아니라 **Base.cpp** 에 있음, 9/5 재확인 ), `Flash_Block_Manager_Base.cpp` 의 `Add_to_free_block_pool`/`Get_a_free_block`/`Get_coldest_block_id`/`Get_min_max_erase_difference`

> ⚠️ **계획 수정 (9/5 코드 재확인)** : `Address_Mapping_Unit_Hybrid.cpp` 를 직접 열어보면 **모든 메서드가 빈 스텁**( `{}` 또는 `return 0`, 파일 전체 53줄 )이다. log-block merge(switch/partial/full) 로직이 코드에 없다 — 애초 계획이 "hybrid 매핑은 이미 있으니 hook 만 추가하면 된다"고 잘못 전제하고 있었다. 그래서 이 세션은 **읽을 코드가 있는 wear-leveling 쪽에 집중**하고, hybrid 매핑은 Cost-Benefit GC 와 같은 성격의 확장 목표( 13~16번 버퍼, 시간이 남을 때 직접 구현 )로 옮긴다. 자세한 근거는 [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/)의 "정확성 노트" 참고.

<div style="overflow-x:auto;">
<svg viewBox="0 0 820 220" style="width:100%;max-width:680px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-p6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t6{font-size:11.5px;font-weight:700;text-anchor:middle;} .b6{font-size:9.5px;text-anchor:middle;}
    .f6{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-p6);fill:none;}
  </style>
  <rect x="10" y="75" width="190" height="60" rx="8" fill="#16a34a" fill-opacity="0.15" stroke="#16a34a" stroke-width="2"/>
  <text x="105" y="98" class="t6" fill="#14532d">GC 실행마다</text>
  <text x="105" y="115" class="b6" fill="#14532d">check_static_wl_required()</text>

  <line x1="200" y1="105" x2="240" y2="105" class="f6"/>
  <polygon points="240,75 340,105 240,135 140,105" fill="#fff6df" stroke="#b8860b" stroke-width="2" transform="translate(100,0)"/>
  <text x="440" y="100" class="t6">max-min</text>
  <text x="440" y="115" class="t6">erase count &gt;</text>
  <text x="440" y="128" class="b6">threshold(100)?</text>

  <line x1="540" y1="105" x2="580" y2="105" class="f6"/>
  <text x="560" y="93" class="b6" fill="#16a34a">예</text>
  <rect x="580" y="75" width="220" height="60" rx="8" fill="#16a34a" fill-opacity="0.15" stroke="#16a34a" stroke-width="2"/>
  <text x="690" y="95" class="t6" fill="#14532d">run_static_wearleveling()</text>
  <text x="690" y="112" class="b6" fill="#14532d">Get_coldest_block_id() 강제 이동</text>

  <line x1="440" y1="135" x2="440" y2="180" class="f6"/>
  <text x="440" y="198" class="b6" fill="#475569">아니오 — 다음 GC까지 대기</text>
</svg>
</div>

- **Static wear-leveling** : GC 로 자연스럽게 마모가 분산되지 않는 "차가운"(거의 안 바뀌는) 데이터가 있는 블록을 강제로 순환시키는 보완 장치. `check_static_wl_required()` 가 plane 내 블록들의 최대-최소 erase count 차이를 `Static_Wearleveling_Threshold`(설정값 100)와 비교하고, 넘으면 `Get_coldest_block_id()`( erase count 가 가장 낮은 블록 — 즉 가장 안 지워진, 정적인 데이터가 오래 눌러앉은 블록 )를 찾아 그 valid page 들을 강제로 다른 곳으로 옮기고 지운다.
- ⚠️ **Dynamic wear-leveling — 9/5 정정** : 예전엔 "GC 의 victim 선정 정책(RGA/RANDOM)에 자연히 녹아 있다"고 적었는데, 실제로는 **완전히 별도의 명시적 메커니즘**이다. erase 가 끝난 블록이 free pool 로 돌아갈 때 `Flash_Block_Manager::Add_erased_block_to_pool()` → `Add_to_free_block_pool(block, consider_dynamic_wl)` 이 호출되는데, `Dynamic_Wearleveling_Enabled`(=`consider_dynamic_wl`) 가 true 면 그 블록을 **실제 erase count 를 key 로** free pool(내부적으로 `erase_count → block` 인 `multimap`)에 넣는다. 다음 write frontier 가 필요할 때 `Get_a_free_block()` 은 **항상 이 multimap 에서 key 가 가장 작은(=erase count 가 가장 낮은) 블록**을 꺼낸다 — "가장 적게 지워진 블록을 다음 쓰기 대상으로 우선 배정"하는 방식. GC 의 victim 선정과는 무관하게, **쓰기 쪽(free pool 배정)에서** 일어나는 로직이라는 게 핵심.
- (참고) Hybrid 매핑을 직접 구현해보고 싶다면 : `Address_Mapping_Unit_Base` 를 상속하는 뼈대는 이미 있으므로, `Address_Mapping_Unit_Page_Level` 을 참고해 log block 개념( 몇 개의 block 을 임시 로그로 쓰고 가득 차면 switch/partial/full merge )을 새로 구현하면 된다 — Cost-Benefit GC(13~14번)와 성격이 같은 "확장 구현" 과제.
- 체크포인트 : static wear-leveling 이 트리거되는 조건과, 그것이 GC 트리거 조건(`Check_gc_required`)과 어떻게 다른 별도 경로인지 설명. `Address_Mapping_Unit_Hybrid.cpp` 를 직접 열어 실제로 빈 스텁인지 확인.

</div>

<div class="session" data-session="7" markdown="1">

### 7. Host 개념 정리( 가볍게 ) + FTL 3종 통합 점검

> ⚠️ **계획 수정( 9/5 )** — 원래 이 세션은 Host Interface 코드를 줄 단위로 읽는 딥다이브였는데, "FTL 만 깊이 보고 Host 는 개념만"이라는 방향에 맞춰 가볍게 바꿨다. Host 는 아래 그림 정도의 개념만 확인하고, 대신 지금까지 세션 3~6 에서 각각 따로 읽은 **FTL 3종( 주소 매핑 / 블록 관리 / GC·WL )을 한 번에 다시 훑어 통합**하는 데 이 세션의 시간을 쓴다.

읽을 파일 : ( Host 개념만, 코드 깊이 안 읽음 ) `Host_Interface_NVMe.h`, `Data_Cache_Manager_Base.h` — ( FTL 통합 점검, 이 세션의 핵심 ) `Address_Mapping_Unit_Page_Level.cpp`, `Flash_Block_Manager.cpp`, `GC_and_WL_Unit_Page_Level.cpp` 를 세션 3~6 노트와 함께 다시 열어보기

<div style="overflow-x:auto;">
<svg viewBox="0 0 760 240" style="width:100%;max-width:620px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-p7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t7{font-size:11.5px;font-weight:700;text-anchor:middle;} .b7{font-size:9.5px;text-anchor:middle;}
    .f7{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-p7);fill:none;}
  </style>
  <rect x="10" y="20" width="220" height="70" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="42" class="t7" fill="#1e3a8a">NVMe : 스트림별 SQ/CQ</text>
  <text x="120" y="60" class="b7" fill="#1e3a8a">Input_Stream_NVMe 링버퍼</text>
  <text x="120" y="75" class="b7" fill="#1e3a8a">(멀티큐 병렬 접수)</text>

  <rect x="10" y="120" width="220" height="60" rx="8" fill="#dbeafe" fill-opacity="0.5" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="142" class="t7" fill="#1e3a8a">SATA : 단일 큐</text>
  <text x="120" y="160" class="b7" fill="#1e3a8a">Host_Interface_SATA</text>

  <line x1="230" y1="55" x2="270" y2="90" class="f7"/>
  <line x1="230" y1="150" x2="270" y2="105" class="f7"/>

  <rect x="270" y="70" width="200" height="60" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="370" y="92" class="t7" fill="#4c1d95">Data_Cache_Manager</text>
  <text x="370" y="110" class="b7" fill="#4c1d95">write cache hit?</text>

  <line x1="470" y1="90" x2="510" y2="60" class="f7"/>
  <text x="530" y="45" class="b7" fill="#7c3aed">hit → 즉시 응답</text>
  <rect x="510" y="20" width="220" height="50" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="620" y="40" class="t7" fill="#4c1d95">캐시에서 바로 서비스</text>
  <text x="620" y="55" class="b7" fill="#4c1d95">FTL 까지 안 내려감</text>

  <line x1="470" y1="110" x2="510" y2="140" class="f7"/>
  <text x="530" y="140" class="b7" fill="#7c3aed">miss → FTL 로</text>
  <rect x="510" y="120" width="220" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="620" y="142" class="t7" fill="#134e4a">FTL.Address_Mapping_Unit</text>
  <text x="620" y="160" class="b7" fill="#134e4a">(Session 3~4 로 이어짐)</text>
</svg>
</div>

**Host 개념( 가볍게, 코드 안 읽어도 됨 )**
- NVMe 의 multi-queue 구조가 SATA 단일 큐와 어떻게 다른지 — 위 그림 왼쪽, "스트림마다 독립된 링버퍼가 있어야 진짜 병렬 접수가 가능하다" 정도만 이해하면 충분
- 캐시 히트 시 FTL 까지 안 내려가는 경로가 있다는 것만 확인 — 위 그림 오른쪽 분기

**FTL 3종 통합 점검( 이 세션의 핵심 )**
- 세션 3~4( 주소 매핑 ), 세션 5( GC ), 세션 6( wear-leveling )에서 각각 따로 읽었던 코드를 이번엔 **하나의 write 요청이 세 클래스를 순서대로 거치는 흐름**으로 다시 추적 — `Address_Mapping_Unit_Page_Level::translate_lpa_to_ppa()` → `Flash_Block_Manager::Allocate_block_and_page_in_plane_for_user_write()` → ( 블록이 다 찼으면 ) `GC_and_WL_Unit::Check_gc_required()`
- 체크포인트 : Host 개념( NVMe vs SATA, 캐시 hit/miss )을 한 문단으로 요약. 그리고 write 요청 하나가 FTL 3종 클래스를 순서대로 거치는 과정을, 이번엔 코드 파일/함수 이름을 직접 대면서( 위 그림 없이 ) 설명

</div>

<div class="session" data-session="8" markdown="1">

### 8. 요청이 빠져나가는 출구 — TSU 와 물리 계층

읽을 파일 : `src/ssd/TSU_Base.h`, `TSU_Priority_OutOfOrder.cpp`( 우리 설정의 실제 정책 ), `NVM_PHY_ONFI.h/cpp`, `ONFI_Channel_Base.h/cpp`, `nvm_chip/flash_memory/Flash_Chip.h`

<div style="overflow-x:auto;">
<svg viewBox="0 0 640 260" style="width:100%;max-width:520px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <style>
    .t8{font-size:12px;font-weight:700;text-anchor:middle;} .b8{font-size:10px;}
  </style>
  <text x="320" y="20" class="t8" fill="#1e293b">ssdconfig.xml 지연시간 파라미터 — 실제 배율(로그 축 아님, 상대 길이)</text>

  <text x="60" y="55" class="b8" fill="#0d9488" text-anchor="end">Read</text>
  <rect x="70" y="40" width="30" height="24" rx="4" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="110" y="57" class="b8" fill="#134e4a">75,000ns (Page_Read_Latency)</text>

  <text x="60" y="105" class="b8" fill="#d97706" text-anchor="end">Program</text>
  <rect x="70" y="90" width="300" height="24" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="380" y="107" class="b8" fill="#78350f">750,000ns (Page_Program_Latency) — read의 10배</text>

  <text x="60" y="155" class="b8" fill="#e11d48" text-anchor="end">Erase</text>
  <rect x="70" y="140" width="560" height="24" rx="4" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="360" y="157" class="b8" fill="#881337">3,800,000ns (Block_Erase_Latency) — read의 50배 이상</text>

  <text x="70" y="200" class="b8" fill="#475569">→ GC 한 번 = program(migration) 여러 번 + erase 한 번 → 매우 비싼 연산</text>
  <text x="70" y="220" class="b8" fill="#475569">→ CMD_Suspension_Support=ERASE 라서, 이 긴 erase 도중 급한 read 가 오면 Suspend()/Resume() 으로 잠깐 끼어들 수 있음</text>
</svg>
</div>

- `TSU.Schedule()` 이 여러 채널/칩 중 무엇을 언제 실행시킬지 정하는 기준 — 실제로는 채널별 라운드로빈 + 칩 하나당 read>write>erase 우선순위( `TSU_Priority_OutOfOrder::Schedule()` 실제 코드로 확인, [코드 분석 7-4절](/ftl-visual-simulator/mqsim/code-analysis/) 참고 )
- ONFI 타이밍 모델( read/program/erase 지연시간 )이 어디서 더해지는지 — 위 그림의 실제 배율을 코드(`Get_command_execution_latency()`)에서 확인
- 채널 하나에 여러 칩이 붙을 때 버스 경합이 어떻게 처리되는지 — `ONFI_Channel_Base::SetStatus()` 가 상태 전이를 어떻게 검증하는지
- 체크포인트 : flash transaction 하나가 큐에 들어가서 실제로 실행되기까지의 대기 이유를 설명, program 이 read 보다 왜 10배 느린지 NAND 물리 원리로 설명

</div>

<div class="session" data-session="9" markdown="1">

### 9. 결과 집계 — Stats 와 XML 출력

읽을 파일 : `src/ssd/Stats.h/cpp`, `src/utils/XMLWriter.h/cpp`, `main.cpp` 의 `collect_results()`

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 220" style="width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-p9" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t9{font-size:11px;font-weight:700;text-anchor:middle;} .b9{font-size:9px;text-anchor:middle;}
    .f9{stroke:#7f8c8d;stroke-width:1.5;marker-end:url(#arrow-p9);fill:none;}
  </style>
  <rect x="10" y="10" width="180" height="50" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="100" y="30" class="t9" fill="#134e4a">query_cmt()</text>
  <text x="100" y="45" class="b9" fill="#134e4a">CMT_hits / CMT_miss++</text>
  <line x1="190" y1="35" x2="620" y2="35" class="f9"/>

  <rect x="10" y="80" width="180" height="50" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="100" y="100" class="t9" fill="#881337">Check_gc_required()</text>
  <text x="100" y="115" class="b9" fill="#881337">Total_gc_executions++</text>
  <line x1="190" y1="105" x2="620" y2="105" class="f9"/>

  <rect x="10" y="150" width="180" height="50" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="100" y="170" class="t9" fill="#78350f">GC 페이지 이동</text>
  <text x="100" y="185" class="b9" fill="#78350f">Total_page_movements_for_gc++</text>
  <line x1="190" y1="175" x2="620" y2="175" class="f9"/>

  <rect x="620" y="70" width="270" height="80" rx="8" fill="#ecfccb" stroke="#65a30d" stroke-width="2"/>
  <text x="755" y="95" class="t9" fill="#365314">Stats:: 전역 정적 카운터</text>
  <text x="755" y="115" class="b9" fill="#365314">시뮬레이션 내내 누적만 됨</text>
  <text x="755" y="130" class="b9" fill="#365314">(중간에 읽지 않음)</text>
</svg>
</div>

- `Total_GC_Executions`( XML 태그명, 코드에서는 `Stats::Total_gc_executions` ), CMT hit/miss, `Total_page_movements_for_gc` 등이 시뮬레이션 도중 어디서 증가되는지 역추적 — 위 그림처럼 여러 파일에 흩어진 지점들이 전부 같은 `Stats` 전역 정적 변수에 모인다는 게 핵심
- `main.cpp` 의 `collect_results()` → `Host_System::Report_results_in_XML()` + `SSD_Device::Report_results_in_XML()` 이 이 정적 카운터들을 XML 로 직렬화하는 지점
- 왜 MQSim 은 중간 상태 없이 "끝나고 나서" 결과를 한 번에 XML 로 쓰는 구조인지( = 우리가 hook 을 심어야 하는 이유 재확인 ) — `Stats` 는 시뮬레이션 도중 계속 누적되기만 하고, 그 값을 "실시간으로" 내보내는 경로가 원래 없다
- 체크포인트 : 9/4 에 봤던 결과 XML 의 특정 숫자 하나를 골라, 그 값이 코드 어디서 만들어지는지 추적

</div>

<div class="session" data-session="10" markdown="1">

### 10. Workload 입력 — Synthetic vs Trace

읽을 파일 : `src/host/IO_Flow_Base.h`, `IO_Flow_Synthetic.cpp`, `IO_Flow_Trace_Based.cpp`

<div style="overflow-x:auto;">
<svg viewBox="0 0 760 220" style="width:100%;max-width:620px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-p10" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t10{font-size:11.5px;font-weight:700;text-anchor:middle;} .b10{font-size:9.5px;text-anchor:middle;}
    .f10{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-p10);fill:none;}
  </style>
  <rect x="10" y="10" width="260" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="140" y="32" class="t10" fill="#1e3a8a">IO_Flow_Synthetic</text>
  <text x="140" y="50" class="b10" fill="#1e3a8a">read 비율, 주소분포(RANDOM_UNIFORM),</text>
  <text x="140" y="65" class="b10" fill="#1e3a8a">hot region 비율, 요청크기 분포</text>
  <text x="140" y="80" class="b10" fill="#1e3a8a">→ RandomGenerator 로 즉석 생성</text>

  <rect x="10" y="120" width="260" height="80" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="140" y="142" class="t10" fill="#4c1d95">IO_Flow_Trace_Based</text>
  <text x="140" y="160" class="b10" fill="#4c1d95">tpcc-small.trace 파일을</text>
  <text x="140" y="175" class="b10" fill="#4c1d95">한 줄씩 파싱(ASCII_Trace_Definition)</text>
  <text x="140" y="190" class="b10" fill="#4c1d95">→ total_replay_no 만큼 반복 재생 가능</text>

  <line x1="270" y1="50" x2="330" y2="105" class="f10"/>
  <line x1="270" y1="160" x2="330" y2="115" class="f10"/>

  <rect x="330" y="90" width="200" height="50" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="430" y="112" class="t10" fill="#1e293b">Generate_next_request()</text>
  <text x="430" y="128" class="b10" fill="#1e293b">→ Host_IO_Request (동일 형태)</text>

  <line x1="530" y1="115" x2="570" y2="115" class="f10"/>
  <rect x="570" y="90" width="180" height="50" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="660" y="112" class="t10" fill="#1e3a8a">Host_Interface</text>
  <text x="660" y="128" class="b10" fill="#1e3a8a">동일 인터페이스로 수렴</text>
</svg>
</div>

- synthetic 워크로드가 파라미터( 분포, hot region 비율 등 )로부터 실제 요청을 어떻게 생성하는지 — `IO_Flow_Synthetic` 이 주소분포/요청크기/도착간격마다 **서로 다른 `RandomGenerator` 시드**를 쓴다는 점 확인( `ssdconfig.xml` 의 `Seed` 하나가 아니라 내부적으로 여러 개 파생 )
- trace 기반 워크로드( `tpcc-small.trace` )가 파일을 어떻게 파싱해서 같은 형태의 요청으로 변환하는지 — `ASCII_Trace_Definition.h`, `percentage_to_be_simulated`( trace 의 일부만 재생하는 옵션 )
- 체크포인트 : 두 방식이 최종적으로 `Host_Interface` 에 요청을 넘기는 지점이 왜 동일한 인터페이스( `Generate_next_request()` → `Host_IO_Request` )로 수렴하는지 설명 — 이 다형성 덕분에 우리 workload 컨트롤 UI(Session 10 원 계획)가 두 방식을 같은 방식으로 다룰 수 있음

</div>

<div class="session" data-session="11" markdown="1">

### 11. 재점검 — hook 지점 다시 훑기

지금까지 hook 을 추가한 파일들( `Address_Mapping_Unit_Page_Level`, `GC_and_WL_Unit_Page_Level`/`GC_and_WL_Unit_Base`( GC + wear-leveling ), `Flash_Block_Manager`/`Flash_Block_Manager_Base`, `Stats` — `Address_Mapping_Unit_Hybrid` 는 빈 스텁이라 hook 대상에서 제외 )을 다시 열어서, 실제로 시뮬레이터에 추가된 hook 코드가 원본 로직의 정확히 어느 지점에 들어갔는지 하나씩 대조

- 체크포인트 : hook 코드 한 줄 한 줄이 "왜 거기 있는지" 설명 가능해야 함

</div>

<div class="session" data-session="12" markdown="1">

### 12. 캡스톤 — 전체 관통

도움 없이, write 요청 하나를 골라 다음을 순서대로 코드 파일/함수 이름을 대며 설명해보기

1. `Host_Interface` 가 요청을 받는다 ( 어느 파일/클래스? )
2. `Data_Cache_Manager` 를 거친다
3. `Address_Mapping_Unit` 에서 매핑을 조회/갱신한다 ( 어느 함수? )
4. `TSU` 가 스케줄링한다
5. `NVM_PHY_ONFI`/`ONFI_Channel` 이 물리 타이밍을 시뮬레이션한다
6. `Flash_Block_Manager` 의 free block pool 이 줄어 `GC_and_WL_Unit.Check_gc_required()` 가 트리거될 수도 있다
7. `Stats` 에 결과가 집계되고 `main.cpp` 의 `collect_results()` 가 XML 로 쓴다

이 7단계가 막힘없이 나오면 MQSim 코드 이해는 끝난 것. 개발 계획의 10/11 1차 마감과 같은 날 — 여기까지가 핵심 커리큘럼이고, 13~16번은 리뷰 이후 버퍼 기간에 진행하는 확장 학습이다.

</div>

<div class="session" data-session="13" markdown="1">

### 13. Cost-Benefit GC 이론 복습과 설계 지점 파악

읽을 파일 : `src/ssd/GC_and_WL_Unit_Page_Level.cpp` 의 `GC_Block_Selection_Policy` switch-case 전체(`Check_gc_required()`), `src/ssd/GC_and_WL_Unit_Base.h` 의 `GC_Block_Selection_Policy_Type` enum( ⚠️ 예전엔 `SSD_Defs.h` 로 적어뒀었는데, 9/5 재확인 결과 실제로는 `GC_and_WL_Unit_Base.h` 에 선언되어 있음 )

<div style="overflow-x:auto;">
<svg viewBox="0 0 780 260" style="width:100%;max-width:640px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <style>
    .t13{font-size:11.5px;font-weight:700;} .b13{font-size:9.5px;}
    .ax13{stroke:#475569;stroke-width:1.5;}
  </style>
  <text x="390" y="20" text-anchor="middle" class="t13" fill="#1e293b">두 블록 후보 비교 — GREEDY 는 B를, Cost-Benefit 은 A를 고를 수 있다</text>

  <line x1="80" y1="220" x2="80" y2="40" class="ax13"/>
  <line x1="80" y1="220" x2="740" y2="220" class="ax13"/>
  <text x="60" y="40" text-anchor="end" class="b13" fill="#475569">age(오래됨)</text>
  <text x="740" y="240" text-anchor="end" class="b13" fill="#475569">invalid page 비율(1-u)</text>

  <circle cx="160" cy="70" r="10" fill="#16a34a" stroke="#14532d" stroke-width="2"/>
  <text x="160" y="55" text-anchor="middle" class="t13" fill="#14532d">A</text>
  <text x="160" y="95" text-anchor="middle" class="b13" fill="#14532d">age 높음(오래 안 지워짐)</text>
  <text x="160" y="108" text-anchor="middle" class="b13" fill="#14532d">invalid 적음(u 큼)</text>
  <text x="160" y="121" text-anchor="middle" class="b13" fill="#14532d" font-weight="700">Cost-Benefit 이 선호</text>

  <circle cx="600" cy="180" r="10" fill="#e11d48" stroke="#881337" stroke-width="2"/>
  <text x="600" y="165" text-anchor="middle" class="t13" fill="#881337">B</text>
  <text x="600" y="205" text-anchor="middle" class="b13" fill="#881337">age 낮음(최근에도 지워짐)</text>
  <text x="600" y="218" text-anchor="middle" class="b13" fill="#881337" font-weight="700">GREEDY/RGA 가 선호</text>

  <text x="390" y="255" text-anchor="middle" class="b13" fill="#475569" font-style="italic">GREEDY/RGA 는 invalid_page_count 하나만 비교 → age 축을 아예 못 봄. Cost-Benefit = age × (1-u)/(1+u) 로 두 축을 함께 반영</text>
</svg>
</div>

- LFS/Rosenblum cost-benefit 공식( `age × (1-u)/(1+u)`, u = valid page 비율 ) 복습 — Session 1/5 에서 배운 이론을 실제 수식으로
- 기존 GREEDY/RGA 케이스가 실제로 비교하는 값은 **오직 `Invalid_page_count`( 그리고 GREEDY 는 `Current_page_write_index == pages_no_per_block` 조건 )뿐**이라는 것을 코드로 재확인( 9/5 코드 확인 결과 — "age" 개념 자체가 지금 코드엔 없음 ). Cost-Benefit 을 구현하려면 블록별로 "마지막으로 valid page 가 갱신된 시각" 같은 age 정보를 `Block_Pool_Slot_Type` 에 새로 추가해야 한다
- enum 에 새 값(`COST_BENEFIT`)을 추가하고 `Check_gc_required()` 의 switch-case 에 새 분기를 넣을 지점을 미리 표시해두기( 실제 구현은 Claude 담당 )
- 체크포인트 : cost-benefit 정책이 greedy 와 다르게 "오래됐지만 invalid page 는 적은 block"(위 그림의 A)을 왜 고르려 하는지 설명, 지금 코드에 age 정보가 없다는 게 무엇을 새로 추가해야 한다는 뜻인지 설명

</div>

<div class="session" data-session="14" markdown="1">

### 14. Cost-Benefit GC 코드 리뷰와 비교 검증

Claude 가 추가한 `COST_BENEFIT` 정책 코드를 리뷰

- 새로 추가된 분기가 13번에서 확인한 지점에 정확히 들어갔는지 확인
- 같은 workload 로 RGA 와 COST_BENEFIT 을 각각 돌려서 `Total_GC_Executions`, WAF, 평균 응답시간을 비교
- 체크포인트 : 두 정책의 결과 차이를 "왜 그런 차이가 나는지" 코드 근거로 설명

</div>

<div class="session" data-session="15" markdown="1">

### 15. 전체 hook 코드 최종 재점검

11번에서 한 번 훑었던 hook 코드 전체( 매핑/GC/WL, hybrid 는 구현했다면 포함 )와, 13~14번에서 추가된 Cost-Benefit 관련 코드까지 포함해서 다시 한 번 통독

- ( 시간이 되면 ) GTest 로 만들어둔 골든/회귀 테스트가 있다면, 그 테스트가 실제로 무엇을 검증하는지 코드로 확인
- 체크포인트 : hook + 확장 코드를 합쳐서 전체 diff 를 설명할 수 있으면 통과

</div>

<div class="session" data-session="16" markdown="1">

### 16. 최종 캡스톤 — 확장 기능까지 포함한 전체 관통

12번의 7단계 설명에 다음을 추가해서 다시 한 번, 이번엔 확장 기능까지 포함해서 설명

8. GC 정책을 RGA 대신 COST_BENEFIT 으로 바꾸면 6번 단계의 victim 선정 결과가 어떻게 달라지는가
9. ( 있다면 ) GTest/GMock 스위트가 이 전체 경로 중 어디를 커버하고 있는가

이번 프로젝트에서 MQSim 코드를 공부한 여정의 종착점.

</div>

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [MQSim 개요](/ftl-visual-simulator/mqsim/overview/) · [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) · [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/mqsim/concept-mapping/) · [개발 계획](/ftl-visual-simulator/plan/)

<script>
(function () {
  var STORAGE_KEY = 'ftl-mqsim-code-analysis-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var sessions = Array.prototype.slice.call(document.querySelectorAll('.session[data-session]'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = sessions.length;
    var state = load();

    function render() {
      var done = 0;
      sessions.forEach(function (wrap) {
        var id = wrap.getAttribute('data-session');
        var isDone = !!state[id];
        wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    sessions.forEach(function (wrap) {
      var h3 = wrap.querySelector('h3');
      if (!h3) return;
      h3.style.cursor = 'pointer';
      h3.title = '클릭해서 완료 표시';
      h3.addEventListener('click', function () {
        var id = wrap.getAttribute('data-session');
        state[id] = !state[id];
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
