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

<svg viewBox="0 0 980 330" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="이벤트 엔진 루프"><defs><marker id="aloop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aloops" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">이벤트 엔진의 루프 (Engine::Start_simulation, sim/Engine.cpp:81)</text><rect x="15" y="35" width="330" height="280" rx="10" fill="#ebf5fb" fill-opacity="0.35" stroke="#2874a6" stroke-width="1.5" stroke-dasharray="6 4"/><text x="27" y="53" font-size="12" font-weight="700" fill="#2874a6" text-anchor="start">EventTree — 시각 순으로 정렬된 이벤트</text><rect x="35" y="70" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="94.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1 ns   IO_Flow: 첫 요청 생성</text><rect x="35" y="118" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="142.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 1.3 µs   PCIe: 메시지 도착</text><rect x="35" y="166" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="190.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 2.0 µs   Cache: 쓰기 완료 처리</text><rect x="35" y="214" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="238.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 750 µs   Flash_Chip: program 끝</text><rect x="35" y="262" width="290" height="40" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="180.0" y="286.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">t = 3.8 ms   Flash_Chip: erase 끝</text><rect x="400" y="70" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="100.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">1. 가장 이른 이벤트 꺼내기</text><text x="525.0" y="119.5" font-size="11" fill="#4d5656" text-anchor="middle">_sim_time = ev-&gt;Fire_time</text><text x="525.0" y="134.5" font-size="11" fill="#4d5656" text-anchor="middle">(시계가 그 시각으로 점프)</text><rect x="400" y="185" width="250" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="525.0" y="215.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">2. 대상 객체에 전달</text><text x="525.0" y="234.5" font-size="11" fill="#4d5656" text-anchor="middle">ev-&gt;Target_sim_object-&gt;</text><text x="525.0" y="249.5" font-size="11" fill="#4d5656" text-anchor="middle">Execute_simulator_event(ev)</text><rect x="710" y="100" width="255" height="130" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="837.5" y="148.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">3. 객체가 일한 뒤</text><text x="837.5" y="167.0" font-size="11" fill="#4d5656" text-anchor="middle">직접 호출 / 신호로 이웃을 부르거나</text><text x="837.5" y="182.0" font-size="11" fill="#4d5656" text-anchor="middle">Register_sim_event(미래 시각, …)</text><text x="837.5" y="197.0" font-size="11" fill="#4d5656" text-anchor="middle">로 다음 이벤트를 예약</text><line x1="325" y1="90" x2="400" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="525" y1="150" x2="525" y2="185" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><line x1="650" y1="225" x2="710" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><path d="M837,230 L837,300 L180,300 L180,285" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aloop)"/><text x="500" y="292" font-size="10.5" fill="#566573" text-anchor="middle">예약된 이벤트가 트리에 들어간다</text></svg>

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

<svg viewBox="0 0 980 340" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="신호 연결도"><defs><marker id="asig" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asigs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">신호(콜백) 연결 — Setup_triggers() 가 한 번 연결한다</text><rect x="20" y="140" width="150" height="60" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="95.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Host Interface</text><rect x="230" y="140" width="150" height="60" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="305.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Data Cache</text><rect x="440" y="40" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="75.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Address Mapping</text><rect x="440" y="130" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="165.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC &amp; WL</text><rect x="440" y="220" width="170" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="525.0" y="255.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU</text><rect x="680" y="140" width="150" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PHY</text><rect x="860" y="140" width="100" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="910.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Chip</text><line x1="170" y1="160" x2="230" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asig)"/><text x="200" y="150" font-size="10.5" fill="#566573" text-anchor="middle">요청 도착</text><line x1="230" y1="185" x2="170" y2="185" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="200" y="205" font-size="10.5" fill="#566573" text-anchor="middle">요청 완료</text><line x1="830" y1="170" x2="610" y2="70" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="750" y="100" font-size="10.5" fill="#566573" text-anchor="middle">트랜잭션 완료</text><line x1="830" y1="170" x2="610" y2="160" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><line x1="830" y1="180" x2="610" y2="250" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="735" y="230" font-size="10.5" fill="#566573" text-anchor="middle">채널·칩 유휴</text><line x1="860" y1="170" x2="830" y2="170" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asig)"/><text x="845" y="132" font-size="10.5" fill="#566573" text-anchor="middle">칩 준비됨</text><text x="490" y="318" font-size="11" font-style="italic" fill="#566573" text-anchor="middle">점선 = 아래에서 위로 올라가는 완료 통지, 실선 = 위에서 아래로 내려가는 요청</text></svg>

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

엔진이 시작하면 등록된 객체 전부에 대해 순서대로 세 번 순회한다. ① `Setup_triggers()` — 신호 연결 ② `Validate_simulation_config()` — 연결이 빠지지 않았는지 검사 ③ `Start_simulation()` — 각자 초기화하고 첫 이벤트 등록. 그다음 위 루프로 들어간다. 객체 목록이 `unordered_map` 이라 ③ 의 호출 **순서는 정해져 있지 않다.** 한 객체의 시작이 다른 객체의 시작 결과를 필요로 하면 안 된다. 코드는 [3단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)에서 본다.


<div style="margin-top: 60px;"></div>

## 관련 문서

- [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · 튜토리얼 [3. 엔진 시작과 이벤트 루프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)
