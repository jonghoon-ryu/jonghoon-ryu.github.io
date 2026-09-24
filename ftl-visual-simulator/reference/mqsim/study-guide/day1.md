---
layout: default
title: MQSim 학습 가이드 Day 1 — 엔진 · 호스트 · 입구 · DRAM 캐시
permalink: /ftl-visual-simulator/reference/mqsim/study-guide/day1/
---
<style>
table.plan-calendar { width:100% !important; table-layout:fixed !important; border-collapse:collapse; font-size:0.85rem; margin:1rem 0; }
table.plan-calendar th, table.plan-calendar td { border:1px solid #ddd; padding:6px 10px; text-align:left; overflow-wrap:break-word; word-break:break-word; }
table.plan-calendar th { background:#f5f5f5; color:#333; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.fig { font-size:0.85rem; color:#666; text-align:center; margin:-0.4rem 0 1.4rem; }
svg.d1 { width:100%; height:auto; display:block; margin:1rem auto; }
svg.d1 text { font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif; }
svg.d1 .b { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
svg.d1 .h { fill:#fdf2e9; stroke:#ca6f1e; stroke-width:2; }
svg.d1 .g { fill:#e9f7ef; stroke:#1e8449; stroke-width:2; }
svg.d1 .y { fill:#fef9e7; stroke:#b7950b; stroke-width:2; }
svg.d1 .r { fill:#fdedec; stroke:#c0392b; stroke-width:2; }
svg.d1 .w { fill:#ffffff; stroke:#95a5a6; stroke-width:1.5; }
svg.d1 .t { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
svg.d1 .s { fill:#566573; font-size:11.5px; text-anchor:middle; }
svg.d1 .sl { fill:#566573; font-size:11.5px; text-anchor:start; }
svg.d1 .c { fill:#7f8c8d; font-size:11px; text-anchor:middle; font-style:italic; }
svg.d1 .f { stroke:#7f8c8d; stroke-width:2; fill:none; marker-end:url(#d1a); }
svg.d1 .fr { stroke:#c0392b; stroke-width:2; fill:none; marker-end:url(#d1ar); }
svg.d1 .fd { stroke:#7f8c8d; stroke-width:1.5; fill:none; stroke-dasharray:5 4; marker-end:url(#d1a); }
</style>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <marker id="d1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker>
    <marker id="d1ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>
  </defs>
</svg>

# MQSim 학습 가이드 Day 1 — 엔진 · 호스트 · 입구 · DRAM 캐시

[← 학습 가이드 목차](/ftl-visual-simulator/reference/mqsim/study-guide/) · [Day 2 →](/ftl-visual-simulator/reference/mqsim/study-guide/day2/)

오늘은 SSD 의 **바깥쪽 절반**이다: MQSim 이 무엇이고 어떻게 조립되는지, 시간이 어떻게 흐르는지, 호스트가 요청을 어떻게 만들어 SSD 입구로 보내는지, 그리고 SSD 안의 DRAM 캐시가 그 요청을 어떻게 받는지. 내일(Day 2)은 캐시 뒤쪽 — FTL 과 flash 칩이다.

<div style="margin-top: 60px;"></div>

<h2 id="session-1-1">세션 1-1 · 큰 그림 — 입력, 출력, 폴더, 객체 조립 (1시간)</h2>

### MQSim 은 무엇인가

MQSim 은 **SSD 한 대를 통째로 흉내 내는 프로그램**이다. 실제 하드웨어 없이, "이런 SSD 에 이런 요청들을 보내면 몇 마이크로초 걸리고 flash 에 몇 번 쓰는가"를 계산한다. 카네기멜런대(SAFARI 그룹)가 2018년 FAST 학회 논문과 함께 공개했다. 이름의 MQ 는 **Multi-Queue** — 요즘 SSD(NVMe)는 여러 프로그램이 각자의 큐로 동시에 요청을 넣는데, 그걸 제대로 흉내 내는 게 이 시뮬레이터의 핵심 목표였다.

<svg class="d1" viewBox="0 0 900 230" style="max-width:860px">
  <rect class="y" x="20" y="30" width="200" height="70" rx="8"/>
  <text class="t" x="120" y="58">ssdconfig.xml</text>
  <text class="s" x="120" y="80">SSD 의 생김새 (용량, 칩 수, 지연시간, GC 정책…)</text>
  <rect class="y" x="20" y="130" width="200" height="70" rx="8"/>
  <text class="t" x="120" y="158">workload.xml</text>
  <text class="s" x="120" y="180">보낼 요청들 (얼마나, 어떤 주소, 읽기/쓰기 비율…)</text>
  <rect class="b" x="330" y="60" width="240" height="110" rx="10"/>
  <text class="t" x="450" y="100">MQSim</text>
  <text class="s" x="450" y="124">SSD 를 조립하고,</text>
  <text class="s" x="450" y="140">요청을 흘려보내며 시간을 계산</text>
  <rect class="g" x="680" y="60" width="200" height="110" rx="8"/>
  <text class="t" x="780" y="96">workload_scenario_N.xml</text>
  <text class="s" x="780" y="120">flow 별 응답 시간, 처리량</text>
  <text class="s" x="780" y="138">flash 명령 수, GC 횟수 …</text>
  <path class="f" d="M220,65 L328,100"/>
  <path class="f" d="M220,165 L328,130"/>
  <path class="f" d="M570,115 L678,115"/>
  <text class="c" x="450" y="215">workload.xml 에 시나리오가 여러 개면, 시나리오마다 SSD 를 새로 만들어 따로 돌리고 결과 파일도 따로 쓴다</text>
</svg>
<div class="fig">그림 1-1-1. MQSim 의 입력과 출력</div>

### 폴더 지도

원본 `src/` 아래 폴더 6개. 이름만 알아두면 나중에 코드를 열 때 어디를 볼지 바로 안다.

<svg class="d1" viewBox="0 0 900 250" style="max-width:860px">
  <rect class="b" x="20" y="20" width="270" height="60" rx="8"/>
  <text class="t" x="155" y="45">sim/ — 시뮬레이션 엔진</text>
  <text class="s" x="155" y="66">시간, 이벤트 큐, 모든 부품의 부모 클래스</text>
  <rect class="y" x="315" y="20" width="270" height="60" rx="8"/>
  <text class="t" x="450" y="45">exec/ — 조립과 실행</text>
  <text class="s" x="450" y="66">XML 읽기, SSD·호스트 객체 조립</text>
  <rect class="h" x="610" y="20" width="270" height="60" rx="8"/>
  <text class="t" x="745" y="45">host/ — 호스트 쪽</text>
  <text class="s" x="745" y="66">요청 생성기(IO flow), PCIe, NVMe 큐</text>
  <rect class="b" x="20" y="110" width="560" height="60" rx="8"/>
  <text class="t" x="300" y="135">ssd/ — SSD 내부 (코드의 대부분)</text>
  <text class="s" x="300" y="156">Host Interface, DRAM 캐시, FTL(매핑·block 관리·GC/WL·스케줄러), PHY(채널 제어)</text>
  <rect class="g" x="610" y="110" width="270" height="60" rx="8"/>
  <text class="t" x="745" y="135">nvm_chip/ — flash 칩</text>
  <text class="s" x="745" y="156">칩 → 다이 → 플레인 → 블록 → 페이지</text>
  <rect class="w" x="20" y="195" width="860" height="40" rx="8"/>
  <text class="t" x="450" y="220">utils/ — 난수, XML 파서(rapidxml), 주소 분할, 헬퍼</text>
</svg>
<div class="fig">그림 1-1-2. src/ 폴더 6개와 각자의 역할</div>

### SSD 는 어떤 부품으로 조립되나

`exec/SSD_Device.cpp` 의 생성자가 설정값을 보고 부품을 **이 순서로** 만든다. 먼저 물리 계층(칩과 채널), 그다음 FTL 과 그 안의 부품들, 마지막으로 입구(Host Interface)와 캐시. 그림에서 상자 안에 있는 것은 "그 부품이 들고 있다"는 뜻이다.

<svg class="d1" viewBox="0 0 900 420" style="max-width:860px">
  <rect class="w" x="10" y="10" width="880" height="400" rx="12"/>
  <text class="t" x="450" y="34">SSD_Device</text>
  <rect class="b" x="30" y="50" width="260" height="70" rx="8"/>
  <text class="t" x="160" y="76">① Host_Interface_NVMe</text>
  <text class="s" x="160" y="98">입구: NVMe 큐에서 요청을 가져옴</text>
  <rect class="b" x="310" y="50" width="260" height="70" rx="8"/>
  <text class="t" x="440" y="76">② Data_Cache_Manager</text>
  <text class="s" x="440" y="98">DRAM 쓰기 캐시 (기본 256MB)</text>
  <rect class="w" x="30" y="140" width="540" height="160" rx="10"/>
  <text class="t" x="300" y="162">③ FTL (NVM_Firmware)</text>
  <rect class="b" x="45" y="175" width="160" height="55" rx="6"/>
  <text class="t" x="125" y="198">AMU</text>
  <text class="s" x="125" y="217">주소 매핑</text>
  <rect class="b" x="220" y="175" width="160" height="55" rx="6"/>
  <text class="t" x="300" y="198">FBM</text>
  <text class="s" x="300" y="217">block 관리</text>
  <rect class="b" x="395" y="175" width="160" height="55" rx="6"/>
  <text class="t" x="475" y="198">GC_and_WL</text>
  <text class="s" x="475" y="217">GC · 마모평준화</text>
  <rect class="b" x="45" y="240" width="510" height="50" rx="6"/>
  <text class="t" x="300" y="262">TSU — 트랜잭션 스케줄러</text>
  <text class="s" x="300" y="280">칩별 명령 큐에서 다음에 보낼 flash 명령을 고름</text>
  <rect class="g" x="600" y="50" width="270" height="340" rx="10"/>
  <text class="t" x="735" y="74">④ PHY (NVM_PHY_ONFI_NVDDR2)</text>
  <text class="s" x="735" y="94">채널로 명령·데이터를 보내고 칩 상태 관리</text>
  <rect class="w" x="620" y="110" width="230" height="120" rx="6"/>
  <text class="s" x="735" y="130">채널 0 (ONFI_Channel_NVDDR2)</text>
  <rect class="g" x="635" y="142" width="45" height="30" rx="4"/><text class="s" x="657" y="161">칩</text>
  <rect class="g" x="688" y="142" width="45" height="30" rx="4"/><text class="s" x="710" y="161">칩</text>
  <rect class="g" x="741" y="142" width="45" height="30" rx="4"/><text class="s" x="763" y="161">칩</text>
  <rect class="g" x="794" y="142" width="45" height="30" rx="4"/><text class="s" x="816" y="161">칩</text>
  <text class="s" x="735" y="200">× 채널 8개, 채널당 칩 4개 (기본)</text>
  <text class="s" x="735" y="218">칩 = Flash_Chip (nvm_chip/)</text>
  <text class="sl" x="620" y="258">칩 하나 = 다이 2 × 플레인 2</text>
  <text class="sl" x="620" y="278">플레인 하나 = 블록 2048</text>
  <text class="sl" x="620" y="298">블록 하나 = 페이지 256 × 8KB</text>
  <text class="sl" x="620" y="326">= 128 플레인 × 4GB ≈ 512GB</text>
  <text class="sl" x="620" y="352">(용량은 설정 파일 값)</text>
  <path class="f" d="M160,120 L160,138"/>
  <path class="f" d="M440,120 L440,138"/>
  <path class="f" d="M570,265 L598,265"/>
  <text class="c" x="300" y="330">화살표 = 요청이 흘러가는 방향. FTL 의 네 부품은 서로 포인터로 연결돼 있다 (예: GC 가 AMU 에게 "이 LPA 잠가줘")</text>
  <text class="c" x="300" y="350">숫자 ①~④는 흐름 순서. 만드는 순서는 거꾸로다 (④ PHY 먼저, ① 입구 마지막)</text>
</svg>
<div class="fig">그림 1-1-3. SSD_Device 안의 부품과 그 포함 관계</div>

호스트 쪽도 비슷하게 `Host_System` 이 조립된다: 요청을 만드는 **IO flow**(워크로드의 flow 하나당 하나), 호스트 메모리와 SSD 를 잇는 **PCIe** 부품(Root Complex, Link, Switch). 마지막에 `host.Attach_ssd_device(&ssd)` 로 둘을 연결한다.

### 프로그램 전체 흐름 (`main.cpp`)

<svg class="d1" viewBox="0 0 900 190" style="max-width:860px">
  <rect class="y" x="10" y="60" width="140" height="60" rx="8"/><text class="t" x="80" y="86">설정 읽기</text><text class="s" x="80" y="106">ssdconfig.xml</text>
  <rect class="y" x="170" y="60" width="140" height="60" rx="8"/><text class="t" x="240" y="86">워크로드 읽기</text><text class="s" x="240" y="106">시나리오 목록</text>
  <rect class="w" x="330" y="20" width="440" height="150" rx="10"/>
  <text class="t" x="550" y="42">시나리오마다 반복</text>
  <rect class="b" x="345" y="60" width="95" height="60" rx="6"/><text class="t" x="392" y="86">Reset</text><text class="s" x="392" y="106">엔진 초기화</text>
  <rect class="b" x="455" y="60" width="95" height="60" rx="6"/><text class="t" x="502" y="86">조립</text><text class="s" x="502" y="106">SSD + Host</text>
  <rect class="b" x="565" y="60" width="95" height="60" rx="6"/><text class="t" x="612" y="86">실행</text><text class="s" x="612" y="106">이벤트 소진까지</text>
  <rect class="g" x="675" y="60" width="85" height="60" rx="6"/><text class="t" x="717" y="86">결과</text><text class="s" x="717" y="106">XML 저장</text>
  <path class="f" d="M150,90 L168,90"/><path class="f" d="M310,90 L343,90"/>
  <path class="f" d="M440,90 L453,90"/><path class="f" d="M550,90 L563,90"/><path class="f" d="M660,90 L673,90"/>
  <path class="fd" d="M717,122 C717,160 392,160 392,124"/>
  <text class="c" x="550" y="160">다음 시나리오</text>
  <rect class="g" x="790" y="60" width="100" height="60" rx="8"/><text class="t" x="840" y="86">끝</text>
  <path class="f" d="M770,90 L788,90"/>
</svg>
<div class="fig">그림 1-1-4. main() — 시나리오마다 SSD 를 새로 조립해서 끝까지 돌린다</div>

"실행"은 `Simulator->Start_simulation()` 한 줄이다. 이 안에서 무슨 일이 일어나는지가 다음 세션이다.

<div class="check" markdown="1">
**확인 질문**
1. MQSim 에 들어가는 파일 두 개와 나오는 파일은? 각각 무엇을 담나?
2. FTL 안에 있는 부품 네 개의 이름과 한 줄 역할은?
3. 기본 설정의 SSD 는 플레인이 몇 개이고, 플레인 하나는 몇 GB 인가?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-1-2">세션 1-2 · 이산 이벤트 엔진 — 시간은 어떻게 흐르나 (1시간)</h2>

### 핵심 아이디어: 시계를 "다음 일"로 건너뛴다

MQSim 은 1 나노초씩 시계를 돌리지 않는다. 대신 **"미래에 일어날 일" 목록**(이벤트 큐)을 들고 있다가, 가장 이른 일을 꺼내 처리하고, 시계를 그 시각으로 **점프**시킨다. 처리하는 도중에 또 다른 미래의 일을 예약할 수 있다. 목록이 비면 시뮬레이션이 끝난다. 이런 방식을 **이산 이벤트 시뮬레이션(discrete-event simulation)** 이라고 한다.

<svg class="d1" viewBox="0 0 900 250" style="max-width:860px">
  <line x1="40" y1="170" x2="870" y2="170" stroke="#34495e" stroke-width="2" marker-end="url(#d1a)"/>
  <text class="sl" x="840" y="195">시간 (ns)</text>
  <circle cx="100" cy="170" r="7" fill="#1e8449"/><text class="s" x="100" y="195">t=1</text>
  <circle cx="300" cy="170" r="7" fill="#ca6f1e"/><text class="s" x="300" y="195">t=75,000</text>
  <circle cx="520" cy="170" r="7" fill="#ca6f1e"/><text class="s" x="520" y="195">t=750,000</text>
  <circle cx="760" cy="170" r="7" fill="#c0392b"/><text class="s" x="760" y="195">t=3,800,000</text>
  <rect class="g" x="40" y="60" width="120" height="50" rx="6"/><text class="t" x="100" y="82">요청 생성</text><text class="s" x="100" y="100">IO flow</text>
  <rect class="h" x="240" y="60" width="120" height="50" rx="6"/><text class="t" x="300" y="82">읽기 완료</text><text class="s" x="300" y="100">Flash_Chip</text>
  <rect class="h" x="460" y="60" width="120" height="50" rx="6"/><text class="t" x="520" y="82">쓰기 완료</text><text class="s" x="520" y="100">Flash_Chip</text>
  <rect class="r" x="700" y="60" width="120" height="50" rx="6"/><text class="t" x="760" y="82">지우기 완료</text><text class="s" x="760" y="100">Flash_Chip</text>
  <path class="fd" d="M100,110 L100,160"/><path class="fd" d="M300,110 L300,160"/><path class="fd" d="M520,110 L520,160"/><path class="fd" d="M760,110 L760,160"/>
  <text class="c" x="450" y="30">이벤트 큐 = 발생 시각 순으로 정렬된 목록. 엔진은 가장 왼쪽 것만 꺼낸다</text>
  <text class="c" x="450" y="230">그 사이의 시간(예: 75,000 ~ 750,000 ns)은 계산하지 않고 건너뛴다 — 그래서 수 초짜리 SSD 동작도 금방 시뮬레이션된다</text>
</svg>
<div class="fig">그림 1-2-1. 이벤트 큐와 시계 점프</div>

### 이벤트와 부품의 약속

모든 부품(칩, TSU, 캐시, IO flow …)은 `Sim_Object` 를 상속한다. 엔진과 부품 사이의 약속은 단 네 개의 함수다.

<svg class="d1" viewBox="0 0 900 300" style="max-width:860px">
  <rect class="b" x="30" y="30" width="330" height="240" rx="10"/>
  <text class="t" x="195" y="56">Sim_Object (모든 부품의 부모)</text>
  <text class="sl" x="50" y="90">Setup_triggers()</text><text class="sl" x="200" y="90">다른 부품 신호 구독</text>
  <text class="sl" x="50" y="120">Validate_simulation_config()</text><text class="sl" x="50" y="136">                                    설정 검사</text>
  <text class="sl" x="50" y="166">Start_simulation()</text><text class="sl" x="200" y="166">첫 이벤트 예약</text>
  <text class="sl" x="50" y="200">Execute_simulator_event(ev)</text>
  <text class="sl" x="50" y="216">                                    이벤트 처리 ★</text>
  <rect class="y" x="520" y="30" width="350" height="110" rx="10"/>
  <text class="t" x="695" y="56">Sim_Event</text>
  <text class="sl" x="540" y="84">Fire_time — 언제 일어나나</text>
  <text class="sl" x="540" y="104">Target_sim_object — 누가 처리하나</text>
  <text class="sl" x="540" y="124">Parameters, Type — 무엇을</text>
  <rect class="g" x="520" y="170" width="350" height="100" rx="10"/>
  <text class="t" x="695" y="196">Engine (전역 Simulator)</text>
  <text class="sl" x="540" y="222">Register_sim_event(시각, 대상, 인자, 종류)</text>
  <text class="sl" x="540" y="242">Ignore_sim_event(ev) — 예약 취소</text>
  <text class="sl" x="540" y="262">Time() — 지금 시각</text>
  <path class="f" d="M518,220 L362,210"/>
  <text class="c" x="440" y="198">엔진이 호출</text>
</svg>
<div class="fig">그림 1-2-2. 부품이 구현하는 함수 네 개, 이벤트, 엔진</div>

`Start_simulation()` 은 먼저 모든 부품에 대해 위의 앞 세 함수를 차례로 부르고, 그다음 루프를 돈다:

<pre>
while (이벤트 큐가 비지 않음):
    가장 이른 시각의 이벤트 묶음을 꺼낸다      ← EventTree 의 최소 노드
    시계 = 그 시각
    묶음 안의 이벤트마다: 대상->Execute_simulator_event(이벤트)
</pre>

같은 시각에 예약된 이벤트는 한 노드에 묶여 함께 처리된다(**event group**). 이벤트 큐는 시각을 key 로 하는 트리(`EventTree`)다.

### 이벤트가 이벤트를 낳는다 — 한 번의 flash 읽기

이벤트 하나를 처리하면서 다음 이벤트를 예약하는 사슬이 시뮬레이션의 전부다. 칩에 읽기 명령이 들어가는 순간부터 보면:

<svg class="d1" viewBox="0 0 900 230" style="max-width:860px">
  <rect class="b" x="20" y="70" width="170" height="70" rx="8"/><text class="t" x="105" y="98">PHY: 명령 전송</text><text class="s" x="105" y="118">채널로 주소 전송 시간</text>
  <rect class="g" x="230" y="70" width="170" height="70" rx="8"/><text class="t" x="315" y="98">칩: 읽기 시작</text><text class="s" x="315" y="118">완료 이벤트 예약</text>
  <rect class="g" x="440" y="70" width="170" height="70" rx="8"/><text class="t" x="525" y="98">칩: 읽기 완료</text><text class="s" x="525" y="118">+75 µs 후</text>
  <rect class="b" x="650" y="70" width="230" height="70" rx="8"/><text class="t" x="765" y="98">PHY: 데이터 전송 → 완료 알림</text><text class="s" x="765" y="118">채널 데이터 전송 시간 뒤</text>
  <path class="f" d="M190,105 L228,105"/><path class="f" d="M400,105 L438,105"/><path class="f" d="M610,105 L648,105"/>
  <text class="c" x="210" y="60">t0</text><text class="c" x="420" y="60">t0 + 전송</text><text class="c" x="630" y="60">+ 75,000 ns</text>
  <text class="c" x="450" y="185">각 화살표 = "Register_sim_event(지금 + 걸리는 시간, …)". 실제 일(데이터 복사)은 하지 않고 걸리는 시간만 계산한다</text>
  <text class="c" x="450" y="205">완료 알림은 콜백(신호)으로 FTL·캐시·Host Interface 에 퍼진다 — 세션 2-5</text>
</svg>
<div class="fig">그림 1-2-3. 이벤트 사슬: flash 읽기 한 번</div>

**중요한 점**: MQSim 은 데이터를 실제로 저장하지 않는다(내용은 숫자 하나로 흉내만 냄). 계산하는 것은 **언제 끝나는가**와 **몇 번 일어나는가**뿐이다.

<div class="check" markdown="1">
**확인 질문**
1. 이벤트 큐가 비면 무슨 일이 일어나나? 한가운데 시간 75,000~750,000 ns 는 왜 계산하지 않아도 되나?
2. 부품이 이벤트를 받으면 호출되는 함수 이름은? 미래 일을 예약하는 함수는?
3. "event group" 은 무엇인가?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-1-3">세션 1-3 · 호스트 — 워크로드는 요청을 언제 만드나 (1시간)</h2>

### IO flow = 요청을 만드는 프로그램 하나

`workload.xml` 의 시나리오 하나에는 flow 가 여러 개 있을 수 있다. flow 하나는 "SSD 를 쓰는 프로그램 하나"를 흉내 낸다. 종류는 둘:

<svg class="d1" viewBox="0 0 900 200" style="max-width:860px">
  <rect class="h" x="30" y="30" width="390" height="140" rx="10"/>
  <text class="t" x="225" y="56">IO_Flow_Synthetic (합성)</text>
  <text class="sl" x="50" y="84">규칙으로 요청을 만든다:</text>
  <text class="sl" x="50" y="104">• 읽기 비율, 요청 크기 분포</text>
  <text class="sl" x="50" y="124">• 주소 분포 (균일 / 순차 / hot-cold)</text>
  <text class="sl" x="50" y="144">• 언제 멈추나: Stop_Time 또는 총 요청 수</text>
  <rect class="h" x="480" y="30" width="390" height="140" rx="10"/>
  <text class="t" x="675" y="56">IO_Flow_Trace_Based (트레이스)</text>
  <text class="sl" x="500" y="84">실제 기록 파일을 그대로 재생:</text>
  <text class="sl" x="500" y="104">• 한 줄 = 시각, 주소, 크기, 읽기/쓰기</text>
  <text class="sl" x="500" y="124">• 기록된 시각대로 요청을 보냄</text>
  <text class="sl" x="500" y="144">• (이 프로젝트는 합성만 사용)</text>
</svg>
<div class="fig">그림 1-3-1. flow 의 두 종류</div>

### 합성 flow 는 언제 다음 요청을 만드나 — 두 가지 방식

<svg class="d1" viewBox="0 0 900 290" style="max-width:860px">
  <text class="t" x="225" y="24">QUEUE_DEPTH (이 프로젝트가 쓰는 방식)</text>
  <text class="t" x="675" y="24">BANDWIDTH</text>
  <line x1="450" y1="10" x2="450" y2="280" stroke="#ddd" stroke-width="2"/>
  <rect class="w" x="40" y="45" width="370" height="60" rx="8"/>
  <rect class="h" x="55" y="57" width="70" height="36" rx="4"/><text class="s" x="90" y="80">요청</text>
  <rect class="h" x="135" y="57" width="70" height="36" rx="4"/><text class="s" x="170" y="80">요청</text>
  <rect class="h" x="215" y="57" width="70" height="36" rx="4"/><text class="s" x="250" y="80">요청</text>
  <rect class="h" x="295" y="57" width="70" height="36" rx="4"/><text class="s" x="330" y="80">요청</text>
  <text class="s" x="225" y="125">항상 N 개(예: 4)가 SSD 안에 들어가 있게 유지</text>
  <path class="f" d="M330,95 C330,160 225,160 225,178"/>
  <rect class="g" x="120" y="180" width="210" height="44" rx="6"/><text class="t" x="225" y="207">하나가 완료되면</text>
  <path class="f" d="M225,224 L225,248"/>
  <text class="s" x="225" y="266">→ 그 자리에서 즉시 새 요청 하나 생성</text>
  <text class="c" x="225" y="284">SSD 가 느려지면 요청도 느리게 나온다 (수요 기반)</text>
  <line x1="490" y1="140" x2="860" y2="140" stroke="#34495e" stroke-width="2" marker-end="url(#d1a)"/>
  <circle cx="520" cy="140" r="6" fill="#ca6f1e"/><circle cx="560" cy="140" r="6" fill="#ca6f1e"/><circle cx="650" cy="140" r="6" fill="#ca6f1e"/><circle cx="690" cy="140" r="6" fill="#ca6f1e"/><circle cx="800" cy="140" r="6" fill="#ca6f1e"/>
  <text class="s" x="675" y="110">정해진 평균 간격(지수 분포)마다 요청 생성</text>
  <text class="s" x="675" y="175">SSD 가 밀려도 계속 들어온다 (도착률 기반)</text>
  <text class="c" x="675" y="200">목표 대역폭(Bandwidth)에서 간격을 계산</text>
</svg>
<div class="fig">그림 1-3-2. QUEUE_DEPTH 는 "완료되면 다음", BANDWIDTH 는 "시간 되면 다음"</div>

코드에서: QUEUE_DEPTH 는 시작할 때 이벤트 하나(t=1)를 예약해 첫 요청들을 넣고, 이후엔 **완료 통지를 받는 함수**(`NVMe_consume_io_request`) 안에서 `Generate_next_request()` 를 부른다. BANDWIDTH 는 매번 다음 도착 시각을 이벤트로 예약한다.

### 주소는 어떻게 고르나

<svg class="d1" viewBox="0 0 900 230" style="max-width:860px">
  <text class="sl" x="30" y="30">flow 의 주소 범위 (working set = 전체 논리 공간의 몇 %)</text>
  <rect class="w" x="30" y="45" width="840" height="30" rx="4"/>
  <text class="t" x="80" y="112">RANDOM_UNIFORM</text>
  <rect class="w" x="200" y="95" width="670" height="26" rx="4"/>
  <rect x="240" y="99" width="8" height="18" fill="#ca6f1e"/><rect x="420" y="99" width="8" height="18" fill="#ca6f1e"/><rect x="310" y="99" width="8" height="18" fill="#ca6f1e"/><rect x="700" y="99" width="8" height="18" fill="#ca6f1e"/><rect x="560" y="99" width="8" height="18" fill="#ca6f1e"/><rect x="820" y="99" width="8" height="18" fill="#ca6f1e"/>
  <text class="t" x="80" y="152">STREAMING</text>
  <rect class="w" x="200" y="135" width="670" height="26" rx="4"/>
  <rect x="420" y="139" width="8" height="18" fill="#1e8449"/><rect x="430" y="139" width="8" height="18" fill="#1e8449"/><rect x="440" y="139" width="8" height="18" fill="#1e8449"/><rect x="450" y="139" width="8" height="18" fill="#1e8449"/><rect x="460" y="139" width="8" height="18" fill="#1e8449"/>
  <text class="sl" x="480" y="153">→ 무작위 시작점부터 1씩 증가</text>
  <text class="t" x="80" y="192">RANDOM_HOTCOLD</text>
  <rect class="w" x="200" y="175" width="670" height="26" rx="4"/>
  <rect x="200" y="175" width="130" height="26" fill="#fdedec" stroke="#c0392b"/>
  <text class="s" x="265" y="193">hot 영역</text>
  <text class="sl" x="345" y="193">예: 주소의 20% 에 요청의 80% 가 몰림, 나머지는 cold 영역</text>
  <text class="c" x="450" y="222">요청 크기는 FIXED(고정) 또는 NORMAL(정규분포). 크기가 page 보다 크면 다음 세션에서 page 단위로 쪼개진다</text>
</svg>
<div class="fig">그림 1-3-3. 주소 분포 세 가지</div>

<div class="check" markdown="1">
**확인 질문**
1. QUEUE_DEPTH 방식에서 SSD 의 처리 속도가 절반이 되면 요청 생성 속도는 어떻게 되나? BANDWIDTH 방식에서는?
2. STREAMING 은 무엇이 "순차"인가?
3. flow 는 언제 요청 생성을 멈추나?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-1-4">세션 1-4 · Host Interface — NVMe 큐와 요청 분해 (1시간)</h2>

### NVMe 큐 한 쌍 — 제출(SQ)과 완료(CQ)

NVMe 에서는 호스트 메모리에 **큐 두 개**가 있다: 호스트가 명령을 넣는 **Submission Queue(SQ)**, SSD 가 결과를 넣는 **Completion Queue(CQ)**. 둘 다 원형 버퍼(ring)이고, 서로 "여기까지 채웠다"는 위치(tail/head)를 **doorbell** 레지스터에 적어 알린다. MQSim 은 flow 하나마다 SQ/CQ 한 쌍을 만든다 — 이게 "Multi-Queue" 다.

<svg class="d1" viewBox="0 0 900 250" style="max-width:860px">
  <text class="t" x="220" y="24">호스트 메모리</text>
  <text class="t" x="700" y="24">SSD</text>
  <line x1="450" y1="10" x2="450" y2="240" stroke="#ddd" stroke-width="2"/>
  <text class="s" x="450" y="244">PCIe</text>
  <text class="sl" x="30" y="62">SQ</text>
  <rect class="h" x="60" y="45" width="40" height="30"/><rect class="h" x="100" y="45" width="40" height="30"/><rect class="h" x="140" y="45" width="40" height="30"/><rect class="w" x="180" y="45" width="40" height="30"/><rect class="w" x="220" y="45" width="40" height="30"/><rect class="w" x="260" y="45" width="40" height="30"/>
  <text class="s" x="120" y="96">명령 3개 대기</text>
  <text class="sl" x="30" y="152">CQ</text>
  <rect class="g" x="60" y="135" width="40" height="30"/><rect class="w" x="100" y="135" width="40" height="30"/><rect class="w" x="140" y="135" width="40" height="30"/><rect class="w" x="180" y="135" width="40" height="30"/><rect class="w" x="220" y="135" width="40" height="30"/><rect class="w" x="260" y="135" width="40" height="30"/>
  <text class="s" x="80" y="186">완료 1개</text>
  <rect class="b" x="560" y="40" width="280" height="150" rx="10"/>
  <text class="t" x="700" y="64">Host_Interface_NVMe</text>
  <text class="sl" x="575" y="90">Input_Stream_NVMe (flow 당 1개)</text>
  <text class="sl" x="575" y="108">  SQ/CQ 위치, 진행 중 요청 목록</text>
  <text class="sl" x="575" y="132">Request_Fetch_Unit_NVMe</text>
  <text class="sl" x="575" y="150">  SQ 에서 명령을 DMA 로 가져옴</text>
  <text class="sl" x="575" y="174">Input_Stream_Manager — 요청 분해</text>
  <path class="f" d="M300,60 L558,70"/><text class="c" x="430" y="56">① doorbell: SQ tail</text>
  <path class="fd" d="M558,120 L302,70"/><text class="c" x="400" y="104">② 명령 가져오기(DMA)</text>
  <path class="f" d="M558,170 L102,150"/><text class="c" x="330" y="176">③ 결과 쓰기 + 인터럽트</text>
</svg>
<div class="fig">그림 1-4-1. NVMe 의 SQ/CQ 와 doorbell</div>

### 요청 하나의 왕복 — 시간 순서

<svg class="d1" viewBox="0 0 900 380" style="max-width:860px">
  <text class="t" x="110" y="24">IO flow</text><text class="t" x="330" y="24">PCIe</text><text class="t" x="560" y="24">Host Interface</text><text class="t" x="790" y="24">캐시 / FTL</text>
  <line x1="110" y1="34" x2="110" y2="370" stroke="#ccc" stroke-dasharray="4 4"/><line x1="330" y1="34" x2="330" y2="370" stroke="#ccc" stroke-dasharray="4 4"/><line x1="560" y1="34" x2="560" y2="370" stroke="#ccc" stroke-dasharray="4 4"/><line x1="790" y1="34" x2="790" y2="370" stroke="#ccc" stroke-dasharray="4 4"/>
  <path class="f" d="M110,60 L556,60"/><text class="sl" x="120" y="54">1. 요청 생성 → SQ 에 넣고 doorbell 쓰기</text>
  <path class="fd" d="M560,95 L114,95"/><text class="sl" x="300" y="89">2. SQ 항목 읽기 요청(DMA)</text>
  <path class="f" d="M110,125 L556,125"/><text class="sl" x="120" y="119">3. 명령 내용 도착 → User_Request 생성</text>
  <path class="f" d="M560,160 L786,160"/><text class="sl" x="570" y="154">4. page 단위로 쪼개 캐시로</text>
  <path class="fd" d="M560,195 L114,195"/><text class="sl" x="300" y="189">5. (쓰기면) 쓸 데이터 DMA 로 가져오기</text>
  <rect class="y" x="660" y="215" width="260" height="50" rx="6"/><text class="s" x="790" y="237">DRAM 쓰기 / flash 읽기·쓰기 …</text><text class="s" x="790" y="255">(세션 1-5, Day 2)</text>
  <path class="f" d="M786,290 L564,290"/><text class="sl" x="570" y="284">6. 모든 조각 완료</text>
  <path class="f" d="M560,325 L114,325"/><text class="sl" x="300" y="319">7. CQ 에 완료 쓰기 + 인터럽트</text>
  <text class="sl" x="120" y="360">8. 응답 시간 기록 → (QUEUE_DEPTH) 다음 요청 생성</text>
</svg>
<div class="fig">그림 1-4-2. 요청 하나의 왕복. 점선 = SSD 가 호스트 메모리를 읽어오는 방향</div>

응답 시간은 두 가지로 기록된다: **device response time**(SSD 가 명령을 가져온 뒤 끝낼 때까지)과 **end-to-end delay**(호스트가 SQ 에 넣은 뒤 완료를 볼 때까지 — 큐에서 기다린 시간 포함).

### 요청 분해 — 섹터에서 page 로

호스트 요청은 **섹터**(512B) 단위 주소와 길이다. flash 는 **page**(기본 8KB = 16 섹터) 단위로 읽고 쓴다. 그래서 Host Interface 가 요청을 page 경계에서 잘라 **트랜잭션**(`NVM_Transaction_Flash_RD/WR`) 여러 개로 만든다. 각 트랜잭션은 논리 page 번호(**LPA**)와 그 page 안의 어느 섹터인지(**sector bitmap**)를 가진다.

<svg class="d1" viewBox="0 0 900 240" style="max-width:860px">
  <text class="sl" x="30" y="30">요청: 시작 섹터 LSA = 40, 길이 = 20 섹터 (page = 16 섹터)</text>
  <rect class="w" x="30" y="50" width="256" height="36"/><rect class="w" x="286" y="50" width="256" height="36"/><rect class="w" x="542" y="50" width="256" height="36"/>
  <text class="s" x="158" y="100">LPA 2 (섹터 32~47)</text><text class="s" x="414" y="100">LPA 3 (섹터 48~63)</text><text class="s" x="670" y="100">LPA 4 (섹터 64~79)</text>
  <rect x="158" y="54" width="128" height="28" fill="#ca6f1e" opacity="0.8"/>
  <rect x="286" y="54" width="192" height="28" fill="#ca6f1e" opacity="0.8"/>
  <text class="c" x="330" y="45">요청이 걸친 섹터 40~59</text>
  <rect class="h" x="80" y="140" width="330" height="70" rx="8"/>
  <text class="t" x="245" y="166">트랜잭션 1: LPA 2</text>
  <text class="s" x="245" y="188">섹터 8개 (page 의 뒤쪽 절반) → bitmap 에서 8~15번 비트만 1</text>
  <rect class="h" x="480" y="140" width="330" height="70" rx="8"/>
  <text class="t" x="645" y="166">트랜잭션 2: LPA 3</text>
  <text class="s" x="645" y="188">섹터 12개 (page 의 앞쪽 3/4)</text>
  <path class="f" d="M222,86 L245,138"/><path class="f" d="M382,86 L645,138"/>
  <text class="c" x="450" y="232">LPA = (섹터 주소 − flow 시작 섹터) ÷ 16. 각 flow 는 자기 주소를 0 부터 다시 센다 → flow 마다 독립된 논리 공간</text>
</svg>
<div class="fig">그림 1-4-3. 요청 → page 단위 트랜잭션. page 일부만 쓰는 트랜잭션도 생긴다</div>

page 의 **일부만** 쓰는 트랜잭션은 나중에 중요해진다: flash 는 page 를 통째로 써야 하므로, 나머지 섹터를 예전 page 에서 **먼저 읽어와야**(read-modify-write) 한다 — Day 2 세션 2-2.

<div class="check" markdown="1">
**확인 질문**
1. SQ 와 CQ 는 누가 채우고 누가 비우나? doorbell 은 무엇을 알리나?
2. device response time 과 end-to-end delay 의 차이는?
3. 섹터 40 부터 20 섹터짜리 쓰기는 트랜잭션 몇 개가 되나? 각각의 LPA 는?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-1-5">세션 1-5 · DRAM 데이터 캐시 — 쓰기는 어디서 끝나나 (1시간)</h2>

### 캐시의 역할

SSD 안에는 DRAM 이 있다(기본 설정 256MB). flash 쓰기는 느리니까(750µs), 쓰기를 **일단 DRAM 에 받아두고 바로 "완료"라고 답한 뒤**, 나중에 flash 로 내려보낸다(write-back). 기본 캐시는 `Data_Cache_Manager_Flash_Advanced` 이고, 모드는 flow 마다 WRITE_CACHE / READ_CACHE / WRITE_READ_CACHE / TURNED_OFF 중 하나다.

### 쓰기 트랜잭션 하나가 캐시에서 겪는 일

<svg class="d1" viewBox="0 0 900 470" style="max-width:860px">
  <rect class="h" x="330" y="10" width="240" height="44" rx="8"/><text class="t" x="450" y="37">쓰기 트랜잭션 (LPA)</text>
  <path class="f" d="M450,54 L450,78"/>
  <polygon points="450,80 600,115 450,150 300,115" class="y"/>
  <text class="s" x="450" y="112">back-pressure 한도</text><text class="s" x="450" y="128">안인가?</text>
  <path class="f" d="M600,115 L700,115"/><text class="c" x="650" y="108">아니오</text>
  <rect class="r" x="700" y="90" width="190" height="50" rx="6"/><text class="s" x="795" y="111">대기열에 줄 서서</text><text class="s" x="795" y="127">flash 쓰기가 끝나길 기다림</text>
  <path class="f" d="M450,150 L450,172"/><text class="c" x="470" y="166">예</text>
  <polygon points="450,174 590,204 450,234 310,204" class="y"/>
  <text class="s" x="450" y="208">이 LPA 가 이미 캐시에?</text>
  <path class="f" d="M310,204 L200,204"/><text class="c" x="255" y="197">예</text>
  <rect class="b" x="20" y="180" width="180" height="50" rx="6"/><text class="s" x="110" y="201">그 칸의 데이터를 갱신</text><text class="s" x="110" y="217">(덮어쓰기 흡수)</text>
  <path class="f" d="M590,204 L680,204"/><text class="c" x="635" y="197">아니오</text>
  <rect class="b" x="680" y="180" width="210" height="50" rx="6"/><text class="s" x="785" y="201">빈 칸 없으면 LRU 칸을 쫓아냄</text><text class="s" x="785" y="217">→ 새 칸에 넣기</text>
  <path class="fr" d="M785,230 L785,262"/>
  <rect class="r" x="680" y="264" width="210" height="56" rx="6"/><text class="s" x="785" y="286">쫓겨난 칸이 dirty 면</text><text class="s" x="785" y="304">DRAM 에서 읽어 flash 로 (CACHE)</text>
  <path class="f" d="M110,230 L110,350 L330,350"/><path class="f" d="M680,292 L600,292 L600,350 L572,350"/>
  <polygon points="450,322 590,352 450,382 310,352" class="y"/>
  <text class="s" x="450" y="348">이 LPA 에 처음 쓰는가?</text><text class="s" x="450" y="364">(bloom filter)</text>
  <path class="fr" d="M590,352 L680,380"/><text class="c" x="650" y="358">예 (cold)</text>
  <rect class="r" x="680" y="366" width="210" height="50" rx="6"/><text class="s" x="785" y="387">곧바로 flash 로도 씀</text><text class="s" x="785" y="403">(eager write-back)</text>
  <path class="f" d="M450,382 L450,412"/><text class="c" x="470" y="404">(모두)</text>
  <rect class="g" x="300" y="414" width="300" height="46" rx="8"/><text class="t" x="450" y="435">DRAM 쓰기 시간 뒤 → 요청 완료</text><text class="s" x="450" y="452">flash 쓰기를 기다리지 않는다</text>
</svg>
<div class="fig">그림 1-5-1. 캐시의 쓰기 처리. 빨간 경로가 flash 로 내려가는 쓰기</div>

그림의 핵심 세 가지:
- **덮어쓰기 흡수** — 같은 LPA 를 여러 번 쓰면 캐시 칸만 갱신되고 flash 에는 안 간다. (그래서 flash 쓰기 수가 호스트 요청 수보다 훨씬 적을 수 있다.)
- **쫓아내기(eviction)** — 캐시가 차면 가장 오래 안 쓴(LRU) 칸을 내보낸다. 아직 flash 에 안 간(dirty) 데이터면 이때 flash 로 쓴다(출처 표시 `CACHE`).
- **처음 쓰는 LPA 는 바로 flash 로도** — 원본은 bloom filter(여기선 단순한 집합)로 "이 LPA 를 전에 본 적 있나"를 기억해서, 처음 보는 LPA 는 "한 번 쓰고 안 건드릴 cold 데이터일 수 있다"고 보고 즉시 flash 에 써둔다. 두 번째부터는(hot) 캐시에만 남긴다.

### back-pressure — 캐시가 flash 를 기다려야 할 때

flash 로 보낸 쓰기가 아직 안 끝난 양을 `back_pressure_buffer_depth` 로 센다. 이 값이 한도를 넘으면 새 쓰기를 더 받지 않고 **대기열**에 세운다. flash 쓰기가 끝날 때마다 이 값이 줄고, 대기열의 요청이 다시 처리된다. "캐시가 있어도 flash 가 따라오지 못하면 결국 느려진다"를 흉내 내는 장치다.

<svg class="d1" viewBox="0 0 900 190" style="max-width:860px">
  <rect class="h" x="20" y="60" width="160" height="60" rx="8"/><text class="t" x="100" y="86">새 쓰기</text><text class="s" x="100" y="106">(대기열)</text>
  <rect class="y" x="230" y="40" width="200" height="100" rx="10"/><text class="t" x="330" y="66">back-pressure</text>
  <rect class="w" x="255" y="84" width="150" height="22"/><rect x="255" y="84" width="120" height="22" fill="#c0392b" opacity="0.7"/><text class="s" x="330" y="126">flash 로 보낸 뒤 아직 안 끝난 양</text>
  <rect class="g" x="490" y="60" width="160" height="60" rx="8"/><text class="t" x="570" y="86">FTL → flash</text><text class="s" x="570" y="106">쓰기 진행 중</text>
  <rect class="b" x="710" y="60" width="170" height="60" rx="8"/><text class="t" x="795" y="86">쓰기 완료</text><text class="s" x="795" y="106">카운터 감소 → 대기열 재개</text>
  <path class="f" d="M180,90 L228,90"/><path class="f" d="M430,90 L488,90"/><path class="f" d="M650,90 L708,90"/><path class="fd" d="M795,120 C795,170 330,170 330,142"/>
</svg>
<div class="fig">그림 1-5-2. back-pressure: 끝나지 않은 flash 쓰기가 많으면 새 쓰기를 멈춘다</div>

### 읽기

읽기는 더 단순하다: 캐시에 그 LPA 가 있으면(최근에 쓴 데이터) **DRAM 에서 읽고 끝**, 없으면 FTL 로 보내 flash 에서 읽는다. 캐시를 끈(TURNED_OFF) flow 는 읽기·쓰기 모두 바로 FTL 로 간다.

<svg class="d1" viewBox="0 0 900 150" style="max-width:860px">
  <rect class="h" x="20" y="50" width="150" height="50" rx="8"/><text class="t" x="95" y="80">읽기 (LPA)</text>
  <polygon points="300,40 400,75 300,110 200,75" class="y"/><text class="s" x="300" y="80">캐시에 있나?</text>
  <rect class="g" x="470" y="20" width="200" height="44" rx="8"/><text class="s" x="570" y="47">DRAM 에서 읽기 → 완료 (빠름)</text>
  <rect class="b" x="470" y="90" width="200" height="44" rx="8"/><text class="s" x="570" y="117">FTL 로 → flash 읽기 (Day 2)</text>
  <path class="f" d="M170,75 L198,75"/><path class="f" d="M380,62 L468,42"/><text class="c" x="420" y="40">예</text><path class="f" d="M380,88 L468,110"/><text class="c" x="420" y="116">아니오</text>
</svg>
<div class="fig">그림 1-5-3. 읽기 경로</div>

<div class="check" markdown="1">
**확인 질문**
1. 같은 LPA 에 쓰기 100번이 들어오면(모두 캐시에 들어갈 때) flash 쓰기는 대략 몇 번인가? (힌트: 첫 번째 쓰기와 마지막에 쫓겨날 때)
2. 캐시가 가득 찼을 때 새 LPA 쓰기가 오면 무슨 일이 일어나나?
3. back-pressure 한도에 걸리면 호스트 입장에서는 무엇이 달라지나?
</div>

<div style="margin-top: 60px;"></div>

## Day 1 정리

<svg class="d1" viewBox="0 0 900 170" style="max-width:860px">
  <rect class="h" x="10" y="50" width="150" height="70" rx="8"/><text class="t" x="85" y="78">IO flow</text><text class="s" x="85" y="98">QUEUE_DEPTH 로 요청 생성</text>
  <rect class="b" x="190" y="50" width="160" height="70" rx="8"/><text class="t" x="270" y="78">NVMe SQ → 가져오기</text><text class="s" x="270" y="98">PCIe DMA</text>
  <rect class="b" x="380" y="50" width="160" height="70" rx="8"/><text class="t" x="460" y="78">page 로 쪼개기</text><text class="s" x="460" y="98">LPA + sector bitmap</text>
  <rect class="y" x="570" y="50" width="160" height="70" rx="8"/><text class="t" x="650" y="78">DRAM 캐시</text><text class="s" x="650" y="98">흡수 / 쫓아내기 / cold 즉시</text>
  <rect class="g" x="760" y="50" width="130" height="70" rx="8"/><text class="t" x="825" y="78">→ FTL</text><text class="s" x="825" y="98">Day 2</text>
  <path class="f" d="M160,85 L188,85"/><path class="f" d="M350,85 L378,85"/><path class="f" d="M540,85 L568,85"/><path class="f" d="M730,85 L758,85"/>
  <text class="c" x="450" y="150">모든 화살표는 이산 이벤트 엔진의 "지금 + 걸리는 시간"에 예약된 이벤트다</text>
</svg>

[← 목차](/ftl-visual-simulator/reference/mqsim/study-guide/) · [Day 2 — FTL 과 flash 칩 →](/ftl-visual-simulator/reference/mqsim/study-guide/day2/)
