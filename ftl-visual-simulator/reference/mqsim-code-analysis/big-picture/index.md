---
layout: default
title: 큰 그림 — MQSim 한눈에
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 큰 그림 — MQSim 한눈에

MQSim 코드 약 1만 9천 줄(헤더 포함 19,309줄, `.cpp` 61개)을 읽기 전에, **어떤 부품이 있고 서로 어떻게 이어지는지**를 먼저 머리에 넣는 곳이다. 코드는 거의 나오지 않고 그림이 대부분이다. 한 줄씩 따라가며 읽는 것은 [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)에서 한다.

기준은 MQSim 원본의 `51f0f2d` 커밋이다. 이 프로젝트가 고친 것은 [Code Change](/ftl-visual-simulator/reference/code-change/)에 따로 있다.


<div style="margin-top: 60px;"></div>

## 전체 구성도

<svg viewBox="0 0 980 470" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="MQSim 전체 구성도"><defs><marker id="asys" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asyss" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><rect x="10" y="10" width="215" height="330" rx="10" fill="#fdf2e9" fill-opacity="0.35" stroke="#ca6f1e" stroke-width="1.5" stroke-dasharray="6 4"/><text x="22" y="28" font-size="12" font-weight="700" fill="#ca6f1e" text-anchor="start">Host (호스트 모델)</text><rect x="30" y="50" width="175" height="70" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="117.5" y="75.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">IO Flow</text><text x="117.5" y="94.5" font-size="11" fill="#4d5656" text-anchor="middle">synthetic 부하 생성기</text><text x="117.5" y="109.5" font-size="11" fill="#4d5656" text-anchor="middle">또는 trace 재생</text><rect x="30" y="150" width="175" height="60" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="117.5" y="170.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NVMe 큐</text><text x="117.5" y="189.5" font-size="11" fill="#4d5656" text-anchor="middle">submission / completion</text><text x="117.5" y="204.5" font-size="11" fill="#4d5656" text-anchor="middle">큐 쌍 (flow 마다 1개)</text><rect x="30" y="240" width="175" height="70" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="117.5" y="265.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PCIe</text><text x="117.5" y="284.5" font-size="11" fill="#4d5656" text-anchor="middle">Root Complex · Switch</text><text x="117.5" y="299.5" font-size="11" fill="#4d5656" text-anchor="middle">· Link (전송 지연)</text><line x1="117" y1="120" x2="117" y2="150" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><line x1="117" y1="210" x2="117" y2="240" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><rect x="245" y="10" width="725" height="330" rx="10" fill="#eef2f7" fill-opacity="0.35" stroke="#34495e" stroke-width="1.5" stroke-dasharray="6 4"/><text x="257" y="28" font-size="12" font-weight="700" fill="#34495e" text-anchor="start">SSD (SSD_Device 가 조립)</text><rect x="265" y="60" width="135" height="90" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="332.5" y="88.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Host Interface</text><text x="332.5" y="107.0" font-size="11" fill="#4d5656" text-anchor="middle">NVMe 큐에서 명령</text><text x="332.5" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">가져와 page 단위</text><text x="332.5" y="137.0" font-size="11" fill="#4d5656" text-anchor="middle">transaction 으로 쪼갬</text><rect x="265" y="190" width="135" height="90" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="332.5" y="225.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Data Cache</text><text x="332.5" y="244.5" font-size="11" fill="#4d5656" text-anchor="middle">DRAM 쓰기 캐시</text><text x="332.5" y="259.5" font-size="11" fill="#4d5656" text-anchor="middle">(적중/치환/destage)</text><rect x="425" y="40" width="330" height="285" rx="10" fill="#f4ecf7" fill-opacity="0.35" stroke="#7d3c98" stroke-width="1.5" stroke-dasharray="6 4"/><text x="437" y="58" font-size="12" font-weight="700" fill="#7d3c98" text-anchor="start">FTL  (NVM_Firmware = FTL 객체가 부품을 묶음)</text><rect x="440" y="70" width="140" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="510.0" y="95.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Address Mapping</text><text x="510.0" y="114.5" font-size="11" fill="#4d5656" text-anchor="middle">LPA → PPA</text><text x="510.0" y="129.5" font-size="11" fill="#4d5656" text-anchor="middle">매핑 · CMT 캐시</text><rect x="600" y="70" width="140" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="670.0" y="95.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block Manager</text><text x="670.0" y="114.5" font-size="11" fill="#4d5656" text-anchor="middle">block/page 상태</text><text x="670.0" y="129.5" font-size="11" fill="#4d5656" text-anchor="middle">free pool · write frontier</text><rect x="440" y="160" width="140" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="510.0" y="185.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC &amp; WL</text><text x="510.0" y="204.5" font-size="11" fill="#4d5656" text-anchor="middle">언제·무엇을 청소</text><text x="510.0" y="219.5" font-size="11" fill="#4d5656" text-anchor="middle">마모 평준화</text><rect x="600" y="160" width="140" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="670.0" y="185.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU</text><text x="670.0" y="204.5" font-size="11" fill="#4d5656" text-anchor="middle">플래시 transaction</text><text x="670.0" y="219.5" font-size="11" fill="#4d5656" text-anchor="middle">스케줄러</text><text x="590" y="262" font-size="11" fill="#566573" text-anchor="middle">AMU 가 주소를 정하면 TSU 로 넘기고,</text><text x="590" y="280" font-size="11" fill="#566573" text-anchor="middle">GC/WL 이 필요하면 스스로 transaction 을 만든다</text><rect x="780" y="60" width="170" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="865.0" y="95.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PHY + Channel</text><text x="865.0" y="114.5" font-size="11" fill="#4d5656" text-anchor="middle">ONFI NVDDR2 타이밍</text><text x="865.0" y="129.5" font-size="11" fill="#4d5656" text-anchor="middle">채널 8개 · 버스 경합</text><rect x="780" y="190" width="170" height="120" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="865.0" y="233.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Flash Chip × 32</text><text x="865.0" y="252.0" font-size="11" fill="#4d5656" text-anchor="middle">Die → Plane → Block → Page</text><text x="865.0" y="267.0" font-size="11" fill="#4d5656" text-anchor="middle">read 75µs · program 750µs</text><text x="865.0" y="282.0" font-size="11" fill="#4d5656" text-anchor="middle">· erase 3.8ms (MLC)</text><path d="M205,275 L235,275 L235,105 L265,105" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><text x="250" y="195" font-size="10.5" fill="#566573" text-anchor="middle">요청</text><line x1="332" y1="150" x2="332" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><line x1="400" y1="235" x2="440" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><line x1="740" y1="195" x2="780" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><line x1="865" y1="150" x2="865" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#asys)"/><line x1="790" y1="225" x2="750" y2="225" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asys)"/><rect x="10" y="365" width="960" height="90" rx="10" fill="#ebf5fb" fill-opacity="0.5" stroke="#2874a6" stroke-width="1.5"/><text x="490" y="392" font-size="14" font-weight="700" fill="#2874a6" text-anchor="middle">이산 이벤트 엔진 (Engine · EventTree · Sim_Object)</text><text x="490" y="414" font-size="11.5" fill="#4d5656" text-anchor="middle">위 모든 상자는 Sim_Object. 엔진이 &quot;가장 이른 이벤트&quot;를 꺼내 그 객체의 Execute_simulator_event() 를 부르고,</text><text x="490" y="432" font-size="11.5" fill="#4d5656" text-anchor="middle">객체들은 서로를 직접 호출하거나 Register_sim_event() 로 미래 이벤트를 예약한다 — 실제 시간은 흐르지 않고 시각만 &quot;점프&quot;한다.</text><line x1="490" y1="365" x2="490" y2="340" stroke="#2874a6" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#asys)"/></svg>

세 가지만 기억하면 된다.

1. **요청은 왼쪽에서 오른쪽으로 흐른다.** 호스트가 만든 요청이 PCIe → Host Interface → 캐시 → FTL → PHY → 칩 순으로 내려가고, 완료 신호가 같은 길을 거슬러 올라온다.
2. **FTL 은 "객체 하나"가 아니라 부품 네 개의 묶음이다.** `FTL` 클래스 자체는 포인터만 쥔 껍데기이고, 일은 주소 매핑(AMU)·블록 매니저·GC/WL·TSU 가 나눠 한다. 데이터 캐시도 FTL 의 문턱에서 같이 움직인다.
3. **시간은 이벤트 엔진이 만든다.** 실제로 기다리지 않고, "다음 이벤트가 일어날 시각"으로 시계를 점프시킨다. 그래서 수십만 건의 I/O 도 몇 초 만에 끝난다.


<div style="margin-top: 60px;"></div>

## 숫자로 보는 MQSim

| 디렉터리 | 역할 | `.cpp` 파일 | 줄 수 (헤더 포함) |
|---|---|--:|--:|
| `ssd/` | SSD 안쪽 전부 — Host Interface, 캐시, FTL 4부품, PHY, 채널 | 33 | 11,591 |
| `exec/` | 설정 파싱, `SSD_Device` · `Host_System` 조립 | 7 | 2,398 |
| `host/` | I/O 생성기, PCIe | 7 | 2,123 |
| `utils/` | XML 파서(rapidxml), 난수, 문자열 | 6 | 1,194 |
| `sim/` | 이벤트 엔진 | 2 | 874 |
| `nvm_chip/` | NAND 칩 물리 모델 | 5 | 817 |
| `main.cpp` (루트) | `main()` — 실행 진입점 | 1 | 312 |
| 합계 | | 61 | 19,309 |

표준 C++11 과 STL 만 쓰고 외부 라이브러리가 없다. FTL 이 사는 `ssd/` 가 전체의 60% 이다.


<div style="margin-top: 60px;"></div>

## 이 섹션의 읽는 순서

| 페이지 | 답하는 질문 |
|---|---|
| [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) | 어떤 클래스가 있고 누가 누구를 소유하는가? |
| [호스트와 stream](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/host-and-streams/) | 호스트의 flow 와 SSD 의 stream 은 어떻게 대응하고, NVMe 큐는 어떻게 도나? |
| [요청 하나가 지나가는 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/) | 쓰기·읽기 요청 하나가 어떤 단계를 거치는가? |
| [플래시 구조와 주소 체계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-and-addresses/) | 채널·칩·다이·플레인·block·page 와 LHA/LPA/PPA 는? |
| [플래시 칩과 PHY 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-chip-and-phy/) | 칩 안에서 명령은 어떻게 실행되고 채널은 어떻게 나눠 쓰나? |
| [FTL 의 부품들과 자료구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) | 매핑 테이블, block 상태, write frontier 는 어떤 모양인가? |
| [매핑 테이블은 어디에 저장되나 — translation page](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/translation-pages/) | 매핑 테이블 자체는 flash 어디에 어떻게 저장되나? |
| [데이터 캐시 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/data-cache/) | DRAM 데이터 캐시는 요청을 어떻게 흡수하나? |
| [GC 와 사용자 I/O 의 경쟁 방지](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concurrency-control/) | GC 와 사용자 I/O 가 같은 데이터를 건드리면? |
| [TSU 스케줄러 정책](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/tsu-policies/) | 스케줄러는 큐를 어떤 순서로 비우나? |
| [Preconditioning — 오래 쓴 SSD 로 시작하기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/preconditioning/) | "오래 쓴 SSD" 로 시작하려면? |
| [이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/) | 시간은 어떻게 흐르고 객체들은 어떻게 연결되는가? |
| [통계와 결과 파일](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/statistics/) | 결과 XML 은 어떻게 읽나? |
| [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/) | OP · GC · 마모평준화 같은 개념은 어느 설정, 어느 코드인가? |
| [파일별 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/file-map/) | 어느 파일에 무엇이 있고 어떤 순서로 읽을까? |
| [원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/) | 원본에 없는 것, 믿으면 안 되는 것은? |
| [용어집](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/glossary/) | 이 말이 무슨 뜻이지? |


<div style="margin-top: 60px;"></div>

## 관련 문서

- [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim-code-analysis/) · [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)
- [MQSim](/ftl-visual-simulator/reference/mqsim/) — 왜 MQSim 을 골랐는가
