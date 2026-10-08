---
layout: default
title: 이벤트 엔진과 시간
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 이벤트 엔진과 시간


<div style="margin-top: 60px;"></div>

## 1. 시간은 점프한다

<svg viewBox="0 0 980 330" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="이벤트 엔진 루프"><defs><marker id="aloop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aloops" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">이벤트 엔진의 루프 (Engine::Start_simulation, sim/Engine.cpp:81)</text><rect x="15" y="35" width="330" height="280" rx="10" fill="#ebf5fb" fill-opacity="0.35" stroke="#2874a6" stroke-width="1.5" stroke-dasharray="6 4"/><text x="27" y="53" font-size="12" font-weight="700" fill="#2874a6" text-anchor="start">EventTree — 시각 순으로 정렬된 이벤트</text><rect x="35" y="70" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="94.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1 ns   IO_Flow: 첫 요청 생성</text><rect x="35" y="118" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="142.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1.3 µs   PCIe: 메시지 도착</text><rect x="35" y="166" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="190.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 2.0 µs   Cache: 쓰기 완료 처리</text><rect x="35" y="214" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="238.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 750 µs   Flash_Chip: program 끝</text><rect x="35" y="262" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="286.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 3.8 ms   Flash_Chip: erase 끝</text><rect x="400" y="70" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="100.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">1. 가장 이른 이벤트 꺼내기</text><text x="525.0" y="119.5" font-size="11" fill="#4d5656" text-anchor="middle">_sim_time = ev-&gt;Fire_time</text><text x="525.0" y="134.5" font-size="11" fill="#4d5656" text-anchor="middle">(시계가 그 시각으로 점프)</text><rect x="400" y="185" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="215.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">2. 대상 객체에 전달</text><text x="525.0" y="234.5" font-size="11" fill="#4d5656" text-anchor="middle">ev-&gt;Target_sim_object-&gt;</text><text x="525.0" y="249.5" font-size="11" fill="#4d5656" text-anchor="middle">Execute_simulator_event(ev)</text><rect x="710" y="100" width="255" height="130" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="837.5" y="148.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">3. 객체가 일한 뒤</text><text x="837.5" y="167.0" font-size="11" fill="#4d5656" text-anchor="middle">직접 호출 / 신호로 이웃을 부르거나</text><text x="837.5" y="182.0" font-size="11" fill="#4d5656" text-anchor="middle">Register_sim_event(미래 시각, …)</text><text x="837.5" y="197.0" font-size="11" fill="#4d5656" text-anchor="middle">로 다음 이벤트를 예약</text><line x1="325" y1="90" x2="400" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="525" y1="150" x2="525" y2="185" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="650" y1="225" x2="710" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><path d="M837,230 L837,300 L180,300 L180,285" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><text x="500" y="292" font-size="10.5" fill="#566573" text-anchor="middle">예약된 이벤트가 트리에 들어간다</text></svg>

- MQSim 에는 "실제 시간" 이 없다. `_sim_time` 이라는 변수 하나가 있고, 엔진이 이벤트를 꺼낼 때마다 그 이벤트의 시각으로 **뛴다.**
- 객체는 일을 한 뒤 "750 µs 후에 이 칩의 program 이 끝난다" 같은 이벤트를 `Register_sim_event()` 로 미래에 **예약**한다. 아무 이벤트도 남지 않으면 시뮬레이션이 끝난다.
- 그래서 90만 건의 요청도 몇 초에 끝난다. 계산량은 "흐른 시간" 이 아니라 "이벤트 수" 에 비례한다.

모든 구성요소는 `Sim_Object` 를 상속하고 `Execute_simulator_event()` 를 구현한다. 엔진 자체는 `Engine` 싱글턴이고 코드에서는 `Simulator->` 로 부른다(`Engine.h:47`).


<div style="margin-top: 60px;"></div>

## 2. 객체끼리 부르는 방법은 두 가지

| 방법 | 언제 쓰나 | 예 |
|---|---|---|
| **직접 호출 · 신호** | 시간이 걸리지 않는 단계 | 캐시 → `Translate_lpa_to_ppa_and_dispatch()` · AMU → `TSU->Submit_transaction()` |
| **예약된 이벤트** | 시간이 걸리는 곳 | PCIe 전송, DRAM 접근, 플래시 지연 |

> **코드를 따라갈 때의 요령** — 어떤 함수의 "다음 동작"을 찾을 때는 먼저 "이 함수가 이벤트를 예약하는가?" 를 본다. 예약하면 흐름이 그 함수에서 **끊기고**, 나중에 `Execute_simulator_event()` 에서 이어진다.


<div style="margin-top: 60px;"></div>

## 3. 신호 연결

<svg viewBox="0 0 980 340" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="신호 연결도"><defs><marker id="asig" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asigs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">신호(콜백) 연결 — Setup_triggers() 가 한 번 연결한다</text><rect x="20" y="140" width="150" height="60" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="95.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Host Interface</text><rect x="230" y="140" width="150" height="60" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="305.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Data Cache</text><rect x="440" y="40" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="75.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Address Mapping</text><rect x="440" y="130" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="165.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC &amp; WL</text><rect x="440" y="220" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="255.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU</text><rect x="680" y="140" width="150" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PHY</text><rect x="860" y="140" width="100" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="910.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Chip</text><line x1="170" y1="160" x2="230" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asig)"/><text x="200" y="150" font-size="10.5" fill="#566573" text-anchor="middle">요청 도착</text><line x1="230" y1="185" x2="170" y2="185" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="200" y="205" font-size="10.5" fill="#566573" text-anchor="middle">요청 완료</text><line x1="830" y1="170" x2="610" y2="70" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="750" y="100" font-size="10.5" fill="#566573" text-anchor="middle">트랜잭션 완료</text><line x1="830" y1="170" x2="610" y2="160" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><line x1="830" y1="180" x2="610" y2="250" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="735" y="230" font-size="10.5" fill="#566573" text-anchor="middle">채널·칩 유휴</text><line x1="860" y1="170" x2="830" y2="170" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="845" y="132" font-size="10.5" fill="#566573" text-anchor="middle">칩 준비됨</text><text x="490" y="318" font-size="11" font-style="italic" fill="#566573" text-anchor="middle">점선 = 아래에서 위로 올라가는 완료 통지, 실선 = 위에서 아래로 내려가는 요청</text></svg>

| 알림을 내는 쪽 | 알림 | 받는 쪽 |
|---|---|---|
| Host Interface | 사용자 요청 도착 | Data Cache |
| Data Cache | 사용자 요청 완료 | Host Interface |
| PHY | 트랜잭션 완료 | **AMU · GC/WL · Cache · TSU** 모두 |
| PHY | 채널 유휴 / 칩 유휴 | TSU |
| Flash Chip | 칩 준비됨 | PHY |

특히 **PHY 의 "트랜잭션 완료" 신호를 AMU · GC/WL · 캐시 · TSU 가 모두 받는다**는 점이 중요하다. 같은 완료 신호를 받고 각자 자기 일을 한다 — AMU 는 매핑 항목을 CMT 에 채우고, GC/WL 은 block 의 진행 중 카운트를 줄이고 다음 단계(이동한 page 쓰기, erase)를 시작한다.


<div style="margin-top: 60px;"></div>

## 4. 시작은 세 번의 순회

엔진이 시작하면 등록된 객체 전부에 대해 순서대로 세 번 순회한다. ① `Setup_triggers()` — 신호 연결(이미 연결된 객체는 건너뜀) ② `Validate_simulation_config()` — 필수 부품(포인터)이 설정됐는지 검사. 신호 구독자가 하나라도 있는지는 **검사하지 않는다** ③ `Start_simulation()` — 각자 초기화하고 첫 이벤트 등록. 그다음 위 루프로 들어간다. 객체 목록이 `unordered_map` 이라 ③ 의 호출 **순서는 정해져 있지 않다.** 한 객체의 시작이 다른 객체의 시작 결과를 필요로 하면 안 된다. 코드는 [3단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)에서 본다.


<div style="margin-top: 60px;"></div>

## 5. 이벤트 저장소: EventTree

<svg viewBox="0 0 980 400" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="EventTree 구조"><defs><marker id="atree" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="atrees" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">EventTree — 같은 시각의 이벤트는 한 노드에 줄 세운다 (sim/EventTree.h)</text><line x1="490" y1="88" x2="260" y2="132" stroke="#aab" stroke-width="1.5"/><line x1="490" y1="88" x2="720" y2="132" stroke="#aab" stroke-width="1.5"/><line x1="260" y1="168" x2="150" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="260" y1="168" x2="370" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="720" y1="168" x2="610" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="720" y1="168" x2="830" y2="212" stroke="#aab" stroke-width="1.5"/><rect x="438" y="52" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="490" y="74" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2,000 ns</text><rect x="208" y="132" width="104" height="36" rx="18" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="260" y="154" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1,300 ns</text><rect x="668" y="132" width="104" height="36" rx="18" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="720" y="154" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">750,000 ns</text><rect x="98" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="150" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1 ns</text><rect x="318" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="370" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1,700 ns</text><rect x="558" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="610" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2,500 ns</text><rect x="778" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="830" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">3,800,000 ns</text><text x="490" y="44" font-size="10.5" fill="#7f8c8d" text-anchor="middle">키 = Fire_time. 노드를 빨강·검정으로 칠해 균형을 유지한다 (Color, RestoreAfterInsert) — 그림의 빨강 = red, 회색 = black</text><rect x="150" y="300" width="170" height="36" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="235.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">FirstSimEvent</text><text x="235.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">Cache: DRAM 쓰기 끝</text><rect x="340" y="300" width="170" height="36" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="425.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">→ Next_event</text><text x="425.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">Host IF: SQ 갱신</text><rect x="530" y="300" width="170" height="36" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="615.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">→ LastSimEvent</text><text x="615.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">PHY: 채널 idle</text><line x1="260" y1="168" x2="235" y2="300" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#atree)"/><text x="720" y="322" font-size="10.5" fill="#566573" text-anchor="start">← 같은 1,300 ns 에 예약된 이벤트 셋 (예시, 예약한 순서)</text><rect x="15" y="350" width="950" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="374.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">Get_min_node 는 가장 왼쪽 노드 · Insert_sim_event 는 같은 key 면 줄 끝에 붙이고, 없으면 Add — 둘 다 O(log N)</text></svg>

이벤트 목록은 `std::priority_queue` 가 아니라 **직접 만든 red-black tree**(`sim/EventTree.cpp`, 503줄)다. 알아 둘 점이 넷 있다.

1. **키는 시각, 노드 하나에 이벤트 줄 하나.** `Insert_sim_event` 는 같은 `Fire_time` 의 노드가 있으면 그 노드의 `LastSimEvent->Next_event` 에 붙인다(도착순 유지). 없으면 새 노드를 `Add` 하고 균형을 복구한다(`RestoreAfterInsert`).
2. **`Count` 는 이벤트 수가 아니라 노드 수** (서로 다른 시각의 수)다. 엔진은 `Count == 0` 일 때 끝난다.
3. **같은 시각에 새로 예약된 이벤트도 같은 순회에서 실행된다.** 엔진은 노드 하나를 꺼내 줄을 끝까지 돌고(`Next_event`) 그다음에 노드를 지운다. 그 도중에 `Fire_time == 지금` 인 이벤트를 예약하면 같은 줄 끝에 붙어서 곧바로 이어서 실행된다.
4. **과거 시각으로는 예약할 수 없다.** `Fire_time < 지금` 이면 `PRINT_ERROR("Illegal request to register a simulation event before Now!")`. 취소는 이벤트를 지우지 않고 `Ignore = true` 로 표시하는 방식이다(`Engine::Ignore_sim_event`) — 서스펜드가 원래의 완료 이벤트를 무시할 때 쓴다.

같은 시각 이벤트의 순서가 "예약한 순서"라는 점이 시뮬레이션을 **결정적(deterministic)** 으로 만드는 바탕이다. (객체의 `Start_simulation` 호출 순서는 `unordered_map` 이라 보장되지 않지만, 각 객체가 등록한 이벤트끼리의 순서는 이렇게 고정된다.)


<div style="margin-top: 60px;"></div>

## 관련 문서

- [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · 튜토리얼 [3. 엔진 시작과 이벤트 루프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)
