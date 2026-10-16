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

<svg viewBox="0 0 980 330" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="이벤트 엔진 루프"><defs><marker id="aloop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aloops" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">이벤트 엔진의 루프 (Engine::Start_simulation, sim/Engine.cpp:81)</text><rect x="15" y="35" width="330" height="280" rx="10" fill="#ebf5fb" fill-opacity="0.35" stroke="#2874a6" stroke-width="1.5" stroke-dasharray="6 4"/><text x="27" y="53" font-size="12" font-weight="700" fill="#2874a6" text-anchor="start">EventTree — 시각 순으로 정렬된 이벤트</text><rect x="35" y="70" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="94.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1 ns   IO_Flow: 첫 요청 생성</text><rect x="35" y="118" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="142.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1.3 µs   PCIe: 메시지 도착</text><rect x="35" y="166" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="190.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 2.0 µs   Cache: 쓰기 완료 처리</text><rect x="35" y="214" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="238.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 750 µs   Flash_Chip: program 끝</text><rect x="35" y="262" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="286.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 3.8 ms   Flash_Chip: erase 끝</text><rect x="400" y="70" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="100.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">1. 가장 이른 이벤트 꺼내기</text><text x="525.0" y="119.5" font-size="11" fill="#4d5656" text-anchor="middle">_sim_time = ev-&gt;Fire_time</text><text x="525.0" y="134.5" font-size="11" fill="#4d5656" text-anchor="middle">(시계가 그 시각으로 점프)</text><rect x="400" y="185" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="215.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">2. 대상 객체에 전달</text><text x="525.0" y="234.5" font-size="11" fill="#4d5656" text-anchor="middle">ev-&gt;Target_sim_object-&gt;</text><text x="525.0" y="249.5" font-size="11" fill="#4d5656" text-anchor="middle">Execute_simulator_event(ev)</text><rect x="710" y="100" width="255" height="130" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="837.5" y="148.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">3. 객체가 일한 뒤</text><text x="837.5" y="167.0" font-size="11" fill="#4d5656" text-anchor="middle">직접 호출 / 신호로 이웃을 부르거나</text><text x="837.5" y="182.0" font-size="11" fill="#4d5656" text-anchor="middle">Register_sim_event(미래 시각, …)</text><text x="837.5" y="197.0" font-size="11" fill="#4d5656" text-anchor="middle">로 다음 이벤트를 예약</text><line x1="325" y1="90" x2="400" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="525" y1="150" x2="525" y2="185" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="650" y1="225" x2="710" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><path d="M837,230 L837,300 L180,300 L180,285" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><text x="500" y="292" font-size="10.5" fill="#566573" text-anchor="middle">예약된 이벤트가 트리에 들어간다</text></svg>

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

<svg viewBox="0 0 980 340" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="신호 연결도"><defs><marker id="asig" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asigs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">신호(콜백) 연결 — Setup_triggers() 가 한 번 연결한다</text><rect x="20" y="140" width="150" height="60" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="95.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Host Interface</text><rect x="230" y="140" width="150" height="60" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="305.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Data Cache</text><rect x="440" y="40" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="75.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Address Mapping</text><rect x="440" y="130" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="165.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC &amp; WL</text><rect x="440" y="220" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="255.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU</text><rect x="680" y="140" width="150" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PHY</text><rect x="860" y="140" width="100" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="910.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Chip</text><line x1="170" y1="160" x2="230" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asig)"/><text x="200" y="150" font-size="10.5" fill="#566573" text-anchor="middle">요청 도착</text><line x1="230" y1="185" x2="170" y2="185" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="200" y="205" font-size="10.5" fill="#566573" text-anchor="middle">요청 완료</text><line x1="830" y1="170" x2="610" y2="70" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="750" y="100" font-size="10.5" fill="#566573" text-anchor="middle">트랜잭션 완료</text><line x1="830" y1="170" x2="610" y2="160" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><line x1="830" y1="180" x2="610" y2="250" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="735" y="230" font-size="10.5" fill="#566573" text-anchor="middle">채널·칩 유휴</text><line x1="860" y1="170" x2="830" y2="170" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="845" y="132" font-size="10.5" fill="#566573" text-anchor="middle">칩 준비됨</text><text x="490" y="318" font-size="11" font-style="italic" fill="#566573" text-anchor="middle">점선 = 아래에서 위로 올라가는 완료 통지, 실선 = 위에서 아래로 내려가는 요청</text></svg>

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

<svg viewBox="0 0 980 400" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="EventTree 구조"><defs><marker id="atree" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="atrees" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">EventTree — 같은 시각의 이벤트는 한 노드에 줄 세운다 (sim/EventTree.h)</text><line x1="490" y1="88" x2="260" y2="132" stroke="#aab" stroke-width="1.5"/><line x1="490" y1="88" x2="720" y2="132" stroke="#aab" stroke-width="1.5"/><line x1="260" y1="168" x2="150" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="260" y1="168" x2="370" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="720" y1="168" x2="610" y2="212" stroke="#aab" stroke-width="1.5"/><line x1="720" y1="168" x2="830" y2="212" stroke="#aab" stroke-width="1.5"/><rect x="438" y="52" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="490" y="74" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2,000 ns</text><rect x="208" y="132" width="104" height="36" rx="18" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="260" y="154" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1,300 ns</text><rect x="668" y="132" width="104" height="36" rx="18" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="720" y="154" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">750,000 ns</text><rect x="98" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="150" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1 ns</text><rect x="318" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="370" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1,700 ns</text><rect x="558" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="610" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2,500 ns</text><rect x="778" y="212" width="104" height="36" rx="18" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="830" y="234" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">3,800,000 ns</text><text x="490" y="44" font-size="10.5" fill="#7f8c8d" text-anchor="middle">키 = Fire_time. 노드를 빨강·검정으로 칠해 균형을 유지한다 (Color, RestoreAfterInsert) — 그림의 빨강 = red, 회색 = black</text><rect x="150" y="300" width="170" height="36" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="235.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">FirstSimEvent</text><text x="235.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">Cache: DRAM 쓰기 끝</text><rect x="340" y="300" width="170" height="36" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="425.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">→ Next_event</text><text x="425.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">Host IF: SQ 갱신</text><rect x="530" y="300" width="170" height="36" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="615.0" y="315.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">→ LastSimEvent</text><text x="615.0" y="333.25" font-size="10" fill="#4d5656" text-anchor="middle">PHY: 채널 idle</text><line x1="260" y1="168" x2="235" y2="300" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#atree)"/><text x="720" y="322" font-size="10.5" fill="#566573" text-anchor="start">← 같은 1,300 ns 에 예약된 이벤트 셋 (예시, 예약한 순서)</text><rect x="15" y="350" width="950" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="374.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">Get_min_node 는 가장 왼쪽 노드 · Insert_sim_event 는 같은 key 면 줄 끝에 붙이고, 없으면 Add — 둘 다 O(log N)</text></svg>

이벤트 목록은 `std::priority_queue` 가 아니라 **직접 만든 red-black tree**(`sim/EventTree.cpp`, 503줄)다. 알아 둘 점이 넷 있다.

1. **키는 시각, 노드 하나에 이벤트 줄 하나.** `Insert_sim_event` 는 같은 `Fire_time` 의 노드가 있으면 그 노드의 `LastSimEvent->Next_event` 에 붙인다(도착순 유지). 없으면 새 노드를 `Add` 하고 균형을 복구한다(`RestoreAfterInsert`).
2. **`Count` 는 이벤트 수가 아니라 노드 수** (서로 다른 시각의 수)다. 엔진은 `Count == 0` 일 때 끝난다.
3. **같은 시각에 새로 예약된 이벤트도 같은 순회에서 실행된다.** 엔진은 노드 하나를 꺼내 줄을 끝까지 돌고(`Next_event`) 그다음에 노드를 지운다. 그 도중에 `Fire_time == 지금` 인 이벤트를 예약하면 같은 줄 끝에 붙어서 곧바로 이어서 실행된다.
4. **과거 시각으로는 예약할 수 없다.** `Fire_time < 지금` 이면 `PRINT_ERROR("Illegal request to register a simulation event before Now!")`. 취소는 이벤트를 지우지 않고 `Ignore = true` 로 표시하는 방식이다(`Engine::Ignore_sim_event`) — 서스펜드가 원래의 완료 이벤트를 무시할 때 쓴다.

같은 시각 이벤트의 순서가 "예약한 순서"라는 점이 시뮬레이션을 **결정적(deterministic)** 으로 만드는 바탕이다. (객체의 `Start_simulation` 호출 순서는 `unordered_map` 이라 보장되지 않지만, 각 객체가 등록한 이벤트끼리의 순서는 이렇게 고정된다.)


<div style="margin-top: 60px;"></div>

## 6. 이벤트 그룹 하나를 자세히 — 시계가 멈춘 동안

엔진이 한 번에 처리하는 단위는 이벤트 **하나**가 아니라 **이벤트 그룹** — 같은 `Fire_time` 을 가진 노드 하나의 줄 전체다. 그룹을 도는 동안 `_sim_time` 은 바뀌지 않는다. 그래서 핸들러 안에서 일어나는 일(직접 호출, 신호, 상태 변경)은 모두 **같은 순간**에 일어난 것으로 친다.

<svg viewBox="0 0 980 360" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="이벤트 그룹 하나와 핸들러가 예약하는 세 가지 시각"><defs><marker id="agrp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
<text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">시각 t 의 이벤트 그룹 — 핸들러가 예약할 수 있는 세 가지 시각</text>
<rect x="20" y="38" width="300" height="236" rx="10" fill="#ebf5fb" fill-opacity="0.35" stroke="#2874a6" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="32" y="58" font-size="12" font-weight="700" fill="#2874a6">노드 t — 시계는 t 에 고정</text>
<rect x="40" y="70" width="260" height="34" rx="7" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="170" y="92" font-size="11" fill="#566573" text-anchor="middle">ev1 — 실행 끝</text>
<rect x="40" y="112" width="260" height="34" rx="7" fill="#ebf5fb" stroke="#2874a6" stroke-width="2.5"/><text x="170" y="134" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">ev2 — 지금 실행 중 (핸들러)</text>
<rect x="40" y="154" width="260" height="34" rx="7" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="170" y="176" font-size="11" fill="#2c3e50" text-anchor="middle">ev3 — 아직</text>
<rect x="40" y="196" width="260" height="34" rx="7" fill="#e9f7ef" stroke="#1e8449" stroke-width="2" stroke-dasharray="5 3"/><text x="170" y="218" font-size="11" font-weight="700" fill="#1e8449" text-anchor="middle">ev4 — ev2 가 방금 붙임</text>
<text x="170" y="256" font-size="10.5" fill="#566573" text-anchor="middle">줄 끝까지 돈 뒤에야 노드를 지운다</text>
<rect x="420" y="70" width="230" height="44" rx="8" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><text x="535" y="89" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">① Register(Time(), …)</text><text x="535" y="105" font-size="10.5" fill="#4d5656" text-anchor="middle">같은 줄 끝 → 이번 그룹에서 실행</text>
<rect x="420" y="140" width="230" height="44" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="535" y="159" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">② Register(Time() + 1, …)</text><text x="535" y="175" font-size="10.5" fill="#4d5656" text-anchor="middle">새 노드 t+1 → 바로 다음 그룹</text>
<rect x="420" y="210" width="230" height="44" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="535" y="229" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">③ Register(Time() + 지연, …)</text><text x="535" y="245" font-size="10.5" fill="#4d5656" text-anchor="middle">먼 미래 노드 → 그 사이 시간은 건너뜀</text>
<path d="M300,129 C360,129 360,92 420,92" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#agrp)"/>
<path d="M300,129 C360,129 360,162 420,162" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#agrp)"/>
<path d="M300,129 C360,129 360,232 420,232" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#agrp)"/>
<path d="M420,98 C380,110 340,190 300,213" fill="none" stroke="#1e8449" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#agrp)"/>
<rect x="700" y="140" width="120" height="44" rx="22" fill="#f4f6f7" stroke="#b7950b" stroke-width="2"/><text x="760" y="166" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">노드 t + 1</text>
<rect x="840" y="210" width="125" height="44" rx="22" fill="#f4f6f7" stroke="#7d3c98" stroke-width="2"/><text x="902" y="230" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">노드 t + 750 µs</text><text x="902" y="245" font-size="9.5" fill="#566573" text-anchor="middle">(예: program 끝)</text>
<line x1="650" y1="162" x2="700" y2="162" stroke="#7f8c8d" stroke-width="2" marker-end="url(#agrp)"/>
<line x1="650" y1="232" x2="840" y2="232" stroke="#7f8c8d" stroke-width="2" marker-end="url(#agrp)"/>
<line x1="40" y1="310" x2="960" y2="310" stroke="#566573" stroke-width="1.5" marker-end="url(#agrp)"/>
<line x1="170" y1="303" x2="170" y2="317" stroke="#566573" stroke-width="2"/><text x="170" y="334" font-size="11" font-weight="700" fill="#2874a6" text-anchor="middle">t</text>
<line x1="760" y1="303" x2="760" y2="317" stroke="#566573" stroke-width="2"/><text x="760" y="334" font-size="11" font-weight="700" fill="#b7950b" text-anchor="middle">t + 1 ns</text>
<line x1="902" y1="303" x2="902" y2="317" stroke="#566573" stroke-width="2"/><text x="902" y="334" font-size="11" font-weight="700" fill="#7d3c98" text-anchor="middle">t + 750 µs</text>
<text x="490" y="352" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">시뮬레이션 시각 (눈금은 비례하지 않음) — 시계는 그룹과 그룹 사이에서만 움직인다</text>
</svg>

| 예약 시각 | 결과 | 쓰는 곳 |
|---|---|---|
| ① `Time()` | 지금 도는 줄 끝에 붙어 **이번 그룹 안에서** 실행 | 드물다. 보통은 직접 호출로 충분하다 |
| ② `Time() + 1` | 1 ns 뒤 별도 그룹. 사실상 같은 순간이지만 **지금 호출 스택이 끝난 뒤** 실행 | 이 프로젝트의 수정본에서 GC 검사·GC 시작·static WL·대기 쓰기 풀기를 미룰 때 (아래 참고) |
| ③ `Time() + 지연` | 그 사이 시간은 **계산 없이 건너뛴다** | PCIe 전송, DRAM 접근, 칩 명령 지연, 다음 요청 도착 |

<div class="tip" markdown="1">
**② 는 원본 MQSim 에는 없다.** 이 시뮬레이터가 엔진을 한 단계씩 돌리면서(§10), 원본에서는 "다른 트랜잭션의 완료 처리 도중" 곧바로 실행되던 GC 시작 같은 일이 그 완료와 **한 화면 단계로 뭉치는** 문제가 생겼다. 그래서 vendored 코드는 `Request_gc_check`, `EXECUTE_PARKED_GC_WL`, `RUN_STATIC_WEARLEVELING`(`GC_and_WL_Unit_Base.cpp`), `RELEASE_WAITING_WRITE`(`Address_Mapping_Unit_Page_Level.cpp`) 를 `Time() + 1` 이벤트로 미룬다. µs 단위 지연에 비해 1 ns 는 결과에 영향을 주지 않을 만큼 작다.
</div>


<div style="margin-top: 60px;"></div>

## 7. "바쁘다" = 상태 + 예약된 완료 이벤트 하나

MQSim 에는 폴링이 없다. 자원이 바쁘다는 것은 **상태 변수**와 **미래에 예약된 완료 이벤트 하나**로 표현된다. 플래시 die 가 대표적이다(`Flash_Chip::start_command_execution`).

```cpp
targetDie->Expected_finish_time = Simulator->Time() + Get_command_execution_latency(...);
targetDie->CommandFinishEvent  = Simulator->Register_sim_event(targetDie->Expected_finish_time,
                                     this, command, COMMAND_FINISHED);
targetDie->Status = DieStatus::BUSY;
```

program 이 도는 750 µs 동안 이 die 에 대해 **아무 이벤트도 실행되지 않는다.** 엔진은 그 사이의 다른 이벤트(다른 칩, 호스트 요청 도착 등)를 처리하다가 `COMMAND_FINISHED` 의 시각이 되면 `finish_command_execution()` 을 부르고, die 는 `IDLE` 로 돌아가며 위쪽으로 완료 신호를 보낸다.

이 표현 덕분에 **취소**도 간단하다. program/erase 도중 읽기가 와서 서스펜드할 때, 칩은 예약해 둔 완료 이벤트를 지우지 않고 `Ignore` 로만 표시한다.

<svg viewBox="0 0 980 330" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="서스펜드와 재개 때의 완료 이벤트"><defs><marker id="asus" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
<text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">die 하나의 시간표 — program 도중 읽기가 와서 서스펜드 (Flash_Chip::Suspend / Resume)</text>
<text x="20" y="74" font-size="11.5" font-weight="700" fill="#2c3e50">die 상태</text>
<rect x="110" y="56" width="250" height="28" rx="4" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="235" y="75" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">BUSY — program (앞부분)</text>
<rect x="360" y="56" width="170" height="28" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="445" y="75" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">read</text>
<rect x="530" y="56" width="250" height="28" rx="4" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="655" y="75" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">BUSY — program (남은 R)</text>
<text x="20" y="150" font-size="11.5" font-weight="700" fill="#2c3e50">예약된</text><text x="20" y="166" font-size="11.5" font-weight="700" fill="#2c3e50">이벤트</text>
<circle cx="110" cy="150" r="7" fill="#7d3c98"/><text x="110" y="128" font-size="10.5" fill="#2c3e50" text-anchor="middle">t0 시작</text>
<path d="M117,150 L600,150" fill="none" stroke="#7d3c98" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#asus)"/>
<rect x="545" y="164" width="170" height="40" rx="6" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="630" y="181" font-size="10.5" font-weight="700" fill="#c0392b" text-anchor="middle">FINISHED @ t0 + tPROG</text><text x="630" y="196" font-size="10" fill="#c0392b" text-anchor="middle">Ignore = true → 꺼내도 건너뜀</text>
<line x1="600" y1="138" x2="616" y2="162" stroke="#c0392b" stroke-width="2.5"/><line x1="616" y1="138" x2="600" y2="162" stroke="#c0392b" stroke-width="2.5"/>
<circle cx="360" cy="236" r="7" fill="#2874a6"/><text x="360" y="262" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">t1 Suspend</text><text x="360" y="277" font-size="10" fill="#4d5656" text-anchor="middle">R = 예정 끝 − t1 저장</text><text x="360" y="291" font-size="10" fill="#4d5656" text-anchor="middle">기존 완료 이벤트 Ignore</text>
<circle cx="530" cy="236" r="7" fill="#1e8449"/><text x="530" y="262" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">t2 Resume</text><text x="530" y="277" font-size="10" fill="#4d5656" text-anchor="middle">새 완료 이벤트 예약</text>
<path d="M537,236 L775,236" fill="none" stroke="#1e8449" stroke-width="2" marker-end="url(#asus)"/>
<rect x="785" y="216" width="180" height="40" rx="6" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><text x="875" y="233" font-size="10.5" font-weight="700" fill="#1e8449" text-anchor="middle">FINISHED @ t2 + R</text><text x="875" y="248" font-size="10" fill="#1e8449" text-anchor="middle">이것이 실제로 실행된다</text>
<line x1="110" y1="306" x2="960" y2="306" stroke="#566573" stroke-width="1.5" marker-end="url(#asus)"/><text x="490" y="324" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">시뮬레이션 시각 →  (서스펜드 명령 자체에 드는 시간은 PHY 가 읽기 명령 시각에 더한다)</text>
</svg>

- `Suspend` 는 `RemainingSuspendedExecTime = Expected_finish_time − Time()` 를 저장하고 `Ignore_sim_event(CommandFinishEvent)` 를 부른다.
- `Resume` 은 `Time() + RemainingSuspendedExecTime` 에 **새** `COMMAND_FINISHED` 를 예약한다.
- 옛 이벤트는 트리에 남아 있다가 제 시각에 꺼내지지만, 엔진 루프가 `if (!ev->Ignore)` 에서 건너뛰고 지운다.

언제 서스펜드하는지(판단 조건과 시간표)는 [플래시 칩과 PHY 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-chip-and-phy/)에 있다.


<div style="margin-top: 60px;"></div>

## 8. 쓰기 하나를 이벤트로 따라가기

아래 그림은 쓰기 요청 하나가 지나가는 동안 생기는 **예약 이벤트**(●)와 **직접 호출**(시간 0, 점선)을 칸별로 나눈 것이다. 각 단계의 자세한 코드는 [요청 하나가 지나가는 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/)에 있다.

<svg viewBox="0 0 980 400" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="쓰기 하나의 이벤트 시간표"><defs><marker id="awr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
<text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 요청 하나 — 칸 = 객체, ● = 예약된 이벤트가 실행되는 시각 (캐시가 write-back 일 때)</text>
<g font-size="11.5" font-weight="700" fill="#2c3e50">
<rect x="15" y="40" width="950" height="52" fill="#eef2f7" fill-opacity="0.5"/><text x="25" y="70">IO_Flow</text>
<rect x="15" y="92" width="950" height="52" fill="#ffffff"/><text x="25" y="122">PCIe_Link</text>
<rect x="15" y="144" width="950" height="52" fill="#fef9e7" fill-opacity="0.5"/><text x="25" y="174">Data Cache</text>
<rect x="15" y="196" width="950" height="52" fill="#ffffff"/><text x="25" y="220">AMU → TSU</text><text x="25" y="236" font-weight="400" font-size="10.5">→ PHY (전송)</text>
<rect x="15" y="248" width="950" height="52" fill="#e9f7ef" fill-opacity="0.5"/><text x="25" y="278">Flash_Chip</text>
</g>
<circle cx="150" cy="66" r="8" fill="#34495e"/><text x="150" y="52" font-size="10" fill="#2c3e50" text-anchor="middle">① 요청 생성</text>
<path d="M158,66 L300,66" stroke="#34495e" stroke-width="1.5" stroke-dasharray="4 3" fill="none" marker-end="url(#awr)"/><text x="232" y="84" font-size="9.5" fill="#566573" text-anchor="middle">다음 도착 예약 (Exponential)</text>
<line x1="150" y1="74" x2="225" y2="110" stroke="#7f8c8d" stroke-width="1.5" marker-end="url(#awr)"/>
<circle cx="235" cy="118" r="8" fill="#566573"/><text x="250" y="110" font-size="10" fill="#2c3e50">② 전송 끝 → SSD 에 도착</text>
<line x1="242" y1="123" x2="370" y2="165" stroke="#7f8c8d" stroke-width="1.5" marker-end="url(#awr)"/>
<circle cx="380" cy="170" r="8" fill="#b7950b"/><text x="368" y="190" font-size="10" fill="#2c3e50" text-anchor="end">③ DRAM 쓰기 끝</text>
<line x1="387" y1="165" x2="470" y2="126" stroke="#7f8c8d" stroke-width="1.5" marker-end="url(#awr)"/><text x="478" y="124" font-size="9.5" fill="#566573">호스트에 완료 (다시 PCIe 전송 이벤트 → IO_Flow)</text>
<path d="M380,178 L380,219 L483,219" fill="none" stroke="#7f8c8d" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#awr)"/><text x="390" y="212" font-size="9.5" fill="#566573">나중에 flush</text>
<rect x="485" y="206" width="150" height="26" rx="5" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="560" y="223" font-size="10" fill="#2c3e50" text-anchor="middle">PPA 배정 → 큐 → 스케줄</text>
<circle cx="680" cy="222" r="8" fill="#1e8449"/><text x="680" y="209" font-size="10" fill="#2c3e50" text-anchor="middle">④ 명령·데이터 전송 끝</text>
<line x1="635" y1="219" x2="670" y2="221" stroke="#7f8c8d" stroke-width="1.5" marker-end="url(#awr)"/>
<line x1="686" y1="229" x2="700" y2="266" stroke="#7f8c8d" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#awr)"/>
<rect x="700" y="262" width="170" height="22" rx="4" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="785" y="277" font-size="10" fill="#2c3e50" text-anchor="middle">die BUSY (tPROG)</text>
<circle cx="890" cy="274" r="8" fill="#7d3c98"/><text x="890" y="296" font-size="10" fill="#2c3e50" text-anchor="middle">⑤ FINISHED</text>
<line x1="890" y1="265" x2="890" y2="204" stroke="#7f8c8d" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#awr)"/><text x="880" y="232" font-size="9.5" fill="#566573" text-anchor="end">완료 신호 → AMU · GC/WL · Cache · TSU</text>
<line x1="110" y1="322" x2="960" y2="322" stroke="#566573" stroke-width="1.5" marker-end="url(#awr)"/><text x="490" y="340" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">시뮬레이션 시각 → (눈금은 비례하지 않음: ①~③ 은 µs, ⑤ 는 수백 µs)</text>
<rect x="15" y="352" width="950" height="40" rx="8" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="490" y="368" font-size="10.5" fill="#2c3e50" text-anchor="middle">실선 화살표 = 예약 (시간이 흐른다) · 점선 = 직접 호출/신호 (같은 순간)</text><text x="490" y="384" font-size="10.5" fill="#2c3e50" text-anchor="middle">⑤ 의 같은 그룹 안에서 매핑 확정 · page VALID · 빈 block 수 확인 → 필요하면 GC 가 다시 이벤트를 예약한다</text>
</svg>

눈여겨볼 점 셋:

1. **요청은 미리 다 만들어 두지 않는다.** `IO_Flow_Synthetic::Execute_simulator_event` 는 요청 하나를 만들어 보낸 뒤 **다음 도착 하나만** `Time() + Exponential(평균 간격)` 에 예약한다(BANDWIDTH 모드 — 결과적으로 포아송 도착). QUEUE_DEPTH 모드는 t = 1 ns 에 큐 깊이만큼 한꺼번에 넣고, 이후로는 요청이 끝날 때마다(`NVMe_consume_io_request`) 하나씩 새로 만든다.
2. **write-back 캐시면 호스트는 ③ 에서 완료를 받는다.** 플래시 쓰기(④⑤)는 그 뒤에, 호스트와 상관없이 일어난다.
3. **⑤ 의 그룹이 가장 바쁘다.** die 의 완료 이벤트 하나가 신호를 통해 여러 객체를 깨우고, 그 안에서 다음 트랜잭션 시작, GC 판단 같은 일이 연쇄로 일어난다. 하지만 **시계는 여전히 ⑤ 의 시각**이다.


<div style="margin-top: 60px;"></div>

## 9. 시뮬레이션은 언제 끝나나

엔진 루프는 `_EventList->Count == 0`(트리가 비었을 때) 또는 `stop` 일 때 멈춘다. 이벤트 생산이 멈추는 과정은 다음과 같다.

1. IO flow 의 `Generate_next_request()` 가 `NULL` 을 돌려준다 — `stop_time` 이 지났거나, 만든 요청 수가 `total_requests_to_be_generated` 에 닿았을 때(`IO_Flow_Synthetic.cpp:76`). 그러면 **다음 도착 이벤트를 예약하지 않는다.**
2. 이미 떠난 요청들은 남은 이벤트(전송, 칩 완료, 그에 이어지는 GC 등)를 다 소비하며 끝난다.
3. 더 예약하는 객체가 없으면 트리가 비고 `Count == 0` → 루프 종료.

즉 "끝" 은 정해진 시각이 아니라 **할 일이 바닥난 순간**이다. 시뮬레이터 앱에서 ▶ 가 회색으로 바뀌는 것도 이 순간이다.


<div style="margin-top: 60px;"></div>

## 10. 시뮬레이터 앱은 엔진을 어떻게 한 걸음씩 돌리나

원본 MQSim 의 루프는 `Start_simulation()` 안의 `while (true)` 로, 끝날 때까지 돌아 버린다. 브라우저에서 한 단계씩 보여 주려고 이 프로젝트는 루프 몸체를 `Engine::Run_next_event_group()` 으로 떼어 냈다(이벤트 그룹 **하나**를 처리하고 남은 이벤트가 있는지 돌려준다). `Start_simulation()` 은 이제 `Setup_simulation()` 뒤에 이 함수를 반복 호출할 뿐이라 결과는 원본과 같다. WASM 쪽 함수(`engine/mqsim/src/wasm/bindings.cpp`)는 이 한 걸음을 서로 다른 "보폭" 으로 묶는다.

<svg viewBox="0 0 980 280" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="step, step_io, step_event 의 보폭 비교"><defs><marker id="astep" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
<text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">이벤트 그룹의 줄 — 각 함수가 한 번에 얼마나 나아가나</text>
<g stroke="#566573" stroke-width="1">
<rect x="40" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="78" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="116" y="60" width="34" height="34" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><rect x="154" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="192" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="230" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="268" y="60" width="34" height="34" rx="4" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="306" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="344" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="382" y="60" width="34" height="34" rx="4" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="420" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="458" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="496" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="534" y="60" width="34" height="34" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><rect x="572" y="60" width="34" height="34" rx="4" fill="#ffffff"/><rect x="610" y="60" width="34" height="34" rx="4" fill="#ffffff"/>
</g>
<text x="680" y="58" font-size="10.5" fill="#566573">선의 모양이 바뀌는 곳 = 호출 한 번이 끝난 곳</text><text x="680" y="74" font-size="10.5" fill="#2c3e50">□ 화면에 안 보이는 그룹 (버스 타이밍 · DRAM 등)</text>
<text x="680" y="90" font-size="10.5" fill="#2874a6" font-weight="700">■ 읽기/쓰기 확정 (매핑 갱신)</text>
<text x="680" y="106" font-size="10.5" fill="#c0392b" font-weight="700">■ GC/WL 단계 (시작 · page 이동 · erase 끝)</text>
<path d="M40,112 L74,112" stroke="#34495e" stroke-width="3"/><text x="40" y="128" font-size="10.5" font-weight="700" fill="#34495e">step()</text>
<path d="M40,150 L150,150" stroke="#2874a6" stroke-width="3"/><path d="M154,150 L568,150" stroke="#2874a6" stroke-width="3" stroke-dasharray="7 4"/><text x="40" y="166" font-size="10.5" font-weight="700" fill="#2874a6">step_io() — ■ 파랑까지 (그 사이 GC 단계는 한꺼번에 지나감)</text>
<path d="M40,190 L150,190" stroke="#7d3c98" stroke-width="3"/><path d="M154,190 L302,190" stroke="#7d3c98" stroke-width="3" stroke-dasharray="7 4"/><path d="M306,190 L416,190" stroke="#7d3c98" stroke-width="3"/><text x="40" y="206" font-size="10.5" font-weight="700" fill="#7d3c98">step_event() — 로그가 한 줄 생기는 그룹까지, 종류 무관 (→ "1 step" 버튼)</text>
<rect x="15" y="226" width="950" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="490" y="244" font-size="10.5" fill="#2c3e50" text-anchor="middle">run(n) = step() n 번 · ▶ 는 프레임마다 run(n) 또는 step_event() 여러 번 — 보이는 이벤트가 드문 프리셋에서 run(n) 만 쓰면</text><text x="490" y="260" font-size="10.5" fill="#2c3e50" text-anchor="middle">DRAM 캐시가 쓰기를 흡수하는 동안 화면이 멈춘 것처럼 보이기 때문 (bindings.cpp 의 주석)</text>
</svg>

| 함수 | 멈추는 조건 | 쓰는 곳 |
|---|---|---|
| `step()` | 그룹 1개 | 디버깅용 최소 단위 |
| `run(n)` | 그룹 n 개 또는 트리가 빌 때 | 한꺼번에 진행 |
| `step_io()` | 플래시 읽기/쓰기 하나가 확정될 때 (`Mapping_Updated_Event`) | "I/O 하나씩" 진행 |
| `step_event()` | 로그 한 줄이 될 이벤트 하나 (읽기/쓰기 확정, GC/WL 의 시작·page 이동·erase 끝) | **1 step** 버튼, 일부 프리셋의 ▶ |

세 함수 모두 안에서는 `Run_next_event_group()` 을 부를 뿐이다. 조건은 이벤트 콜백(`Simulation_Events`)이 세우는 플래그로 판단한다. 그래서 **어떤 보폭으로 돌려도 이벤트가 실행되는 순서와 시각은 똑같다** — 달라지는 것은 화면을 다시 그리는 지점뿐이다. 그룹과 그룹 사이에서는 SSD 전체가 멈춘 스냅숏이라, 각 걸음 뒤에 `getState()` 로 읽은 격자·통계는 항상 일관된 상태다.


<div style="margin-top: 60px;"></div>

## 11. 머릿속 모델 — 다섯 줄 요약

1. 시계는 **이벤트를 꺼낼 때만** 움직인다. 계산량은 흐른 시간이 아니라 이벤트 수에 비례한다.
2. 한 걸음 = 같은 시각의 **이벤트 그룹** 전체. 그 안에서는 시계가 멈춰 있다.
3. 같은 시각의 이벤트는 **예약한 순서대로** 실행된다 → 결정적.
4. 바쁜 자원 = **상태 + 예약된 완료 이벤트 하나.** 취소는 `Ignore` 표시.
5. 끝 = **트리가 빈 순간.** 요청 생성이 멈추고 남은 일이 다 소비되면 온다.


<div style="margin-top: 60px;"></div>

## 관련 문서

- [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · 튜토리얼 [3. 엔진 시작과 이벤트 루프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)
- [요청 하나가 지나가는 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/) · [플래시 칩과 PHY 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-chip-and-phy/)
