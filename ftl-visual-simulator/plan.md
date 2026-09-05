---
layout: default
title: 개발 계획
permalink: /ftl-visual-simulator/plan/
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
table.plan-calendar .buffer-mark {
  cursor: pointer;
  user-select: none;
}
</style>

# FTL 시각화 시뮬레이터 — 일정 계획

**1차 완성 목표일 : 2026-10-11**. 9/4(금)를 시작일로 삼아, 이후 주말( 토/일 ) + 공휴일( 10/5, 10/9 ) 기준 하루 5시간씩 총 12세션 커리큘럼. 10/11 에 결과물을 직접 리뷰하고, 필요하면 10/17~10/18, 10/24~10/25 를 이용해 수정한다.

> **9/5(토, 원래 휴무일) 추가 작업 기록** — 쉬는 날이지만 세션 2 마무리 겸 문서 전반을 손봤다.
> - [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/)에 파일별 상세 설명(FTL 코드 라인 수 포함) + 콜 플로우 다이어그램 8개 추가
> - [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/mqsim/concept-mapping/) 문서 신설
> - **개발 계획(이 문서) 검토 및 수정** : Session 6 을 "Hybrid 매핑 구현되어 있음" 전제에서 "실제로는 빈 스텁 → 마모 평준화 중심으로 수정"으로 정정, Session 2 에 MQSim 강의 영상 추가
> - **[MQSim 코드 분석 계획](/ftl-visual-simulator/mqsim/code-analysis-plan/) 수정** : Session 6 정정(위와 동일 이유), Session 7 을 Host 딥다이브에서 "Host 개념만 + FTL 통합 점검"으로 축소( FTL 만 깊이 보고 Host 는 개념만 파악하기로 함 ), Session 4/13 파일 위치 오류 수정
> - 코드 재검증으로 발견한 오류 정정 : GC 트리거는 매 쓰기가 아니라 write frontier 블록이 다 찼을 때만 확인됨, dynamic wear-leveling 은 GC 정책이 아니라 free block pool 배정(erase count 최소 블록 우선)에서 동작, `Preemptible_GC_Enabled=false` 설정에서는 GC 가 항상 긴급 모드, MQSim 에는 bad block 관리가 없음(통계용 카운터만 존재)

<div style="margin-top: 60px;"></div>

## 전제 조건

- 평일 작업은 기대하지 않음. 다만 가능하면 다음 세션 내용을 미리 당기거나, 여유( 버퍼 ) 로 사용
- **9/4(금)를 시작일로 사용** — 세션 1 (FTL 개념)을 짜투리 시간에 미리 시작. **9/5(토)는 계획에서 제외** (쉬는 날)
- 9/12(토), 9/13(일) 은 개인 사정으로 작업 불가 → 계획에서 제외
- 10/5(월), 10/9(금) 은 공휴일이라 평일이지만 주말과 동일하게 5시간 작업일로 포함
- **10/11 이 1차 마감** — 이 날짜 안에 "동작하는 배포본"을 만드는 것이 최우선이고, 그 다음 리뷰 결과에 따라 10/17~10/25 에 수정
- 세션 순서가 날짜보다 중요함. 한 세션이 밀리면 다음 세션도 그만큼 밀린다고 생각하고, 억지로 두 세션을 하루에 몰아넣지 않기
- **구현은 전부 Claude 담당** — Ryu 는 visual simulator 를 만드는 방법을 몰라도 됨. 설계·코딩·빌드·배포 등 구체적인 작업은 모두 Claude 가 하고, 여러 방식 중 선택이 필요한 지점( 예 : 매핑 방식, 색상 스킴, GC 정책 이름 등 )에서만 Claude 가 Ryu 에게 옵션을 제시해 결정을 구함
- **모든 세션에 FTL 개념 공부 + MQSim 코드 이해가 들어감** — Ryu 의 역할은 방향 결정, 코드/결과 리뷰, 브라우저 테스트에 더해 **매 세션 그 단계와 연결된 FTL 개념과 MQSim 실제 소스코드를 함께 이해하는 것**( 각 세션의 "MQSim/FTL 심화" 항목 )
- **( 가능하다면 ) MQSim 에 없는 기능을 직접 구현해보기** — 조사 결과 MQSim 은 GC 정책으로 GREEDY/RGA/RANDOM/RANDOM_P/RANDOM_PP/FIFO 만 지원하고 **Cost-Benefit GC**( LFS/Rosenblum 방식, valid page 비율과 block age 를 함께 고려하는 정책, Session 1/5 에서 배운 "greedy vs cost-benefit" 비교의 그 cost-benefit )는 없음 → 시간이 남으면 13~16번 버퍼 기간에 이 정책을 새로 구현해 RGA 와 비교해보는 것을 확장 목표로 삼음
- **( 시간이 여유로울 때 ) Google Test/Mock 기반 테스트 스위트 추가** — MQSim 은 테스트가 전혀 없지만 `Address_Mapping_Unit_Base`/`Flash_Block_Manager_Base`/`GC_and_WL_Unit_Base`/`TSU_Base` 가 이미 추상 인터페이스라 GMock 으로 단위 테스트가 가능함. **Session 4 가 최적 타이밍** — WASM 임베딩용 라이브러리 분리 리팩터링과 테스트 바이너리에 필요한 리팩터링이 동일하기 때문( 자세한 이유는 [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) 참고 ). 시간이 부족하면 골든/회귀 테스트만 먼저 걸고, 진짜 단위 테스트는 13~16번 버퍼로 미룸
- **초심자 학습 환경이라는 목표를 설계 단계부터 반영** — MQSim 의 raw 파라미터/통계를 그대로 노출하면 초심자에게는 그냥 숫자 나열일 뿐임. Session 3 설계 때부터 "쉬운 용어로 된 툴팁", "개념별 프리셋 시나리오( 매핑 기본 / GC 시연 / 마모평준화 시연 )", "지금 무슨 일이 일어나고 있는지 평범한 말로 알려주는 설명 패널" 을 MVP 범위에 포함시킴 — Session 11(다듬기)의 "툴팁/범례" 는 이 원칙을 마무리하는 단계일 뿐, 처음부터 있어야 하는 요구사항

<div style="margin-top: 40px;"></div>

## 날짜표 ( 12 세션 + 리뷰/수정 버퍼 4일 )

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>세션</th><th>날짜</th><th>구분</th><th>단계 ( Claude )</th><th>Ryu 공부 내용</th><th>완료</th></tr>
<tr><td>1</td><td>9/4 (금)</td><td>평일 (시작일)</td><td>Phase 1 — FTL 개념</td><td>FTL 핵심 개념 복습( 매핑/GC/WL/OP ), hybrid·DFTL 은 나중으로 미룸</td><td class="table-mark buffer-mark" data-session="1">☐</td></tr>
<tr><td>2</td><td>9/6 (일)</td><td>주말</td><td>Phase 2 — MQSim 개괄</td><td>MQSim 개요 문서 학습, XML 설정/모듈 구조 리뷰</td><td class="table-mark buffer-mark" data-session="2">☐</td></tr>
<tr><td>-</td><td>9/12 (토)</td><td>주말 (휴업)</td><td>개인 사유로 휴업</td><td>—</td><td>—</td></tr>
<tr><td>-</td><td>9/13 (일)</td><td>주말 (휴업)</td><td>개인 사유로 휴업</td><td>—</td><td>—</td></tr>
<tr><td>3</td><td>9/19 (토)</td><td>주말</td><td>Phase 3 — 설계</td><td>`Address_Mapping_Unit_Page_Level.cpp`, `Flash_Block_Manager.cpp` 읽기</td><td class="table-mark buffer-mark" data-session="3">☐</td></tr>
<tr><td>4</td><td>9/20 (일)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (1)</td><td>`Address_Mapping_Unit_Page_Level.cpp` 의 lookup/allocate 로직 추적</td><td class="table-mark buffer-mark" data-session="4">☐</td></tr>
<tr><td>-</td><td>9/24 (목)</td><td>공휴일 (휴업)</td><td>추석</td><td>—</td><td>—</td></tr>
<tr><td>-</td><td>9/25 (금)</td><td>공휴일 (휴업)</td><td>추석</td><td>—</td><td>—</td></tr>
<tr><td>5</td><td>9/26 (토)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (2)</td><td>GC 이론( greedy vs cost-benefit ) + `GC_and_WL_Unit_Page_Level.cpp` victim selection</td><td class="table-mark buffer-mark" data-session="5">☐</td></tr>
<tr><td>6</td><td>9/27 (일)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (3)</td><td>마모 평준화(dynamic/static WL) 이론 + `GC_and_WL_Unit_Base.cpp`/`Flash_Block_Manager_Base.cpp`( Hybrid 매핑은 빈 스텁이라 확장 목표로 이동, 9/5 확인 )</td><td class="table-mark buffer-mark" data-session="6">☐</td></tr>
<tr><td>7</td><td>10/3 (토)</td><td>주말</td><td>Phase 5 — 시각화 (1)</td><td>시각화 요소와 `Stats.cpp` 통계 항목 대응 관계 확인</td><td class="table-mark buffer-mark" data-session="7">☐</td></tr>
<tr><td>8</td><td>10/4 (일)</td><td>주말</td><td>Phase 5 — 시각화 (2)</td><td>9/4 결과( `workload_scenario_*.xml` )와 대시보드 지표 대조</td><td class="table-mark buffer-mark" data-session="8">☐</td></tr>
<tr><td>9</td><td>10/5 (월)</td><td>공휴일</td><td>Phase 6 — 인터랙션 (1)</td><td>`ssdconfig.xml` 파라미터 범위/의미 재확인</td><td class="table-mark buffer-mark" data-session="9">☐</td></tr>
<tr><td>10</td><td>10/9 (금)</td><td>공휴일</td><td>Phase 6 — 인터랙션 (2)</td><td>`workload.xml` synthetic vs trace-based 비교</td><td class="table-mark buffer-mark" data-session="10">☐</td></tr>
<tr><td>11</td><td>10/10 (토)</td><td>주말</td><td>Phase 7 — 마무리 (1)</td><td>지금까지 추가된 hook 전체 재점검</td><td class="table-mark buffer-mark" data-session="11">☐</td></tr>
<tr><td>12</td><td>10/11 (일)</td><td>주말 · 1차 마감</td><td>Phase 7 — 마무리 (2) · 배포 · 리뷰</td><td>캡스톤 — write 요청 하나를 매핑→GC→flash 까지 전체 설명</td><td class="table-mark buffer-mark" data-session="12">☐</td></tr>
<tr><td>13</td><td>10/17 (토)</td><td>주말</td><td>리뷰 및 수정</td><td>Cost-Benefit GC 이론 복습 + 기존 GC 코드 구조 재설계 지점 파악</td><td class="table-mark buffer-mark" data-session="13">☐</td></tr>
<tr><td>14</td><td>10/18 (일)</td><td>주말</td><td>리뷰 및 수정</td><td>Cost-Benefit GC 코드 리뷰, RGA 대비 비교 검증</td><td class="table-mark buffer-mark" data-session="14">☐</td></tr>
<tr><td>15</td><td>10/24 (토)</td><td>주말</td><td>리뷰 및 수정</td><td>전체 hook 코드 최종 재점검( 매핑/GC/WL, hybrid 는 구현했다면 포함 )</td><td class="table-mark buffer-mark" data-session="15">☐</td></tr>
<tr><td>16</td><td>10/25 (일)</td><td>주말</td><td>리뷰 및 수정</td><td>최종 캡스톤 — 확장 기능까지 포함해 전체 시스템 설명</td><td class="table-mark buffer-mark" data-session="16">☐</td></tr>
</table>
</div>

<div style="margin-top: 20px;"></div>

**13~16번은 계획 외 버퍼** — 10/11 리뷰에서 나온 피드백을 반영하는 용도. 여유가 있으면 확장 목표( Cost-Benefit GC 정책 구현 등 MQSim 에 없는 기능 추가 )에도 사용. 별도 세부 세션 내용 없이 자유롭게 사용.

<div style="margin-top: 60px;"></div>

## 세션

<div class="progress-box">
  <span>진행률: <span id="progress-count">0 / 16</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div class="session" data-session="1" markdown="1">

### 1. (9/4) FTL 개념 — 매핑 · GC · 마모 평준화 · Over-provisioning


- NAND flash 의 물리적 제약 : page / block / plane 구조, "erase-before-write" — 이미 잘 알고 있음 ✅
- 주소 매핑 방식 : page-level, block-level mapping — 이미 잘 알고 있음 ✅
- 마모 평준화( static/dynamic ), bad block 관리, over-provisioning — 이미 잘 알고 있음 ✅
- Hybrid(log-block, FAST) mapping — MQSim 에는 실제로 구현되어 있지 않음(빈 스텁, 9/5 확인) → **직접 구현이 필요한 확장 목표로 13~16번 버퍼에서 다루기로 미룸**
- Garbage Collection ( victim block 선정 알고리즘 등 ) — **Session 5(GC 알고리즘 구현) 때 실습과 함께 깊이 다루기로 미룸**
- DFTL 같은 demand-based 매핑 캐싱 — **확장 기능으로 나중에 실습할 때(DFTL 매핑 캐시 시각화) 같이 다루기로 미룸**
- 결과물 : 개발 계획 수립

</div>

<div class="session" data-session="2" markdown="1">

### 2. (9/6) MQSim 개괄 학습


**Ryu 가 할 일**
- **MQSim/FTL 심화** : [MQSim 문서](/ftl-visual-simulator/mqsim/) 를 읽으며 MQSim 이 뭘 모델링하는지, 어떤 기능이 있는지, 다른 오픈소스 시뮬레이터와 비교했을 때 왜 이걸 골랐는지 개괄적으로 이해
- Claude 가 정리한 XML 설정 항목·모듈 구조·파이프라인 다이어그램( [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/mqsim/concept-mapping/) )을 리뷰하며, 각 파라미터·모듈이 FTL 개념상 무엇을 의미하는지 실제로 이해
- **강의 시청** : [Understanding & Designing Modern Storage Systems - L3: MQSim](https://www.youtube.com/watch?v=9YZGHl6yxBc) — 제목상 "스토리지 시스템 설계" 강의 시리즈의 MQSim 전용 회차(L3). 위 문서들로 정리한 내용을 강의 설명으로 한 번 더 교차 확인하는 용도( 영상 자체를 열어보지 못했으니 실제 내용은 시청하면서 직접 확인 필요 )

**Claude 가 할 일**
- [CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim) clone, 빌드, 샘플 설정으로 실행 ✅ ( 9/4 에 미리 진행 — g++13 에서 수정 없이 바로 빌드/실행 됨, `/home/ryuj/Ryu/MQSim` )
  - 샘플 `ssdconfig.xml` + `workload.xml` 로 3개 시나리오(synthetic 2개 + trace 기반 tpcc-small) 모두 정상 실행, 결과는 `workload_scenario_*.xml` 로 출력
  - 주목할 점 : 기본 설정(75% occupancy, 짧은 워크로드)으로는 `Total_GC_Executions="0"` — GC 가 한 번도 안 일어남. Session 5 에서 GC 를 실제로 보려면 occupancy 를 높이거나 워크로드를 늘려야 함
- XML 설정 구조( Flash parameter, FTL parameter, GC 정책, cache ) 조사·정리
- 주요 모듈 조사 : Host_Interface, IO_Flow, Address_Mapping_Unit, Flash_Block_Manager, GC_and_WL_Unit, NVM_PHY_ONFI
- 결과물 : Host request → FTL 매핑 → Flash controller → NAND 로 이어지는 파이프라인 다이어그램, "시각화에 그대로 가져갈 부분 / 단순화할 부분" 정리

</div>

<div class="session" data-session="3" markdown="1">

### 3. (9/19) 시뮬레이터 설계 — 범위 · 스택 · 데이터 모델


**Ryu 가 할 일**
- MVP 범위, 사용자 조절 파라미터 방향 결정 및 Claude 초안 검토·조정
- **MQSim/FTL 심화** : `Address_Mapping_Unit_Page_Level.cpp`, `Flash_Block_Manager.cpp` 를 더 자세히 읽고, 설계할 데이터 모델이 MQSim 구조와 어디서 같고 어디서 단순화되는지 정리

**Claude 가 할 일**
- MVP 범위 초안 : flash block/page grid ( free / valid / invalid / erasing 상태 ), 매핑 테이블, GC 이벤트, 통계( WAF, valid page 비율 )
- **엔진 아키텍처 확정** : 자체 TS 엔진을 새로 짜지 않고, **MQSim C++ 코드를 Emscripten 으로 WASM 컴파일해서 그대로 사용**. UI 는 React + Vite, WASM 모듈과는 얇은 JS/TS 바인딩 레이어로 연결, GitHub Pages 정적 배포
- **계측(instrumentation) 지점 설계** : MQSim 은 XML → 실행 → 결과 XML 이라는 일괄 실행 구조라 중간 상태를 못 봄. 시각화를 위해 어디에 hook 을 심어야 하는지 설계 —
  - `Address_Mapping_Unit_Page_Level.cpp` : 매핑 갱신 시점( `Address_Mapping_Unit_Hybrid.cpp` 는 빈 스텁이라 제외 — hybrid 를 확장 구현하게 되면 그때 같이 hook 추가 )
  - `GC_and_WL_Unit_Page_Level.cpp`, `GC_and_WL_Unit_Base.cpp` : GC 시작/victim 선정/migration/erase 시점 + dynamic/static wear-leveling 시점
  - `Flash_Block_Manager.cpp`/`Flash_Block_Manager_Base.cpp` : block/page 상태(free/valid/invalid) 변경 시점
  - 이 지점들에서 이벤트를 JS 로 넘기는 방식 결정 ( Emscripten `EM_ASM`/exported 콜백으로 즉시 통지 vs. 주기적 상태 스냅샷 )
- 파라미터/워크로드 입력 방식 설계 : 파라미터 패널에서 만든 값을 실제 `ssdconfig.xml`/`workload.xml` 형식 텍스트로 만들어 Emscripten 가상 파일시스템(MEMFS)에 써넣고, MQSim 기존 XML 파싱 코드를 그대로 재사용
- **초심자 학습 요소를 MVP 범위에 포함** :
  - 개념별 프리셋 시나리오 설계( 예 : "매핑 기본" — 쓰기 몇 번으로 페이지 매핑만 보여주기, "GC 시연" — occupancy 를 높여 GC 가 빨리 일어나게, "마모평준화 시연" — 특정 block 에 쓰기를 몰아서 WL 개입을 보여주기 )
  - hook 이벤트를 "지금 무슨 일이 일어나는지" 쉬운 말로 바꿔주는 설명 문구 초안( 예 : "block 12 의 유효한 페이지들을 새 block 으로 옮기는 중이에요(GC)" )
  - 용어 툴팁에 들어갈 쉬운 설명 초안( 매핑, GC, 마모 평준화, over-provisioning 등 )
- 화면 와이어프레임( flash grid, 매핑 테이블 패널, 파라미터 패널, 이벤트 로그, 통계 대시보드, 설명 패널, 프리셋 선택 UI )
- 결과물 : 설계 문서 + 와이어프레임, 프로젝트 뼈대(scaffold) 커밋

</div>

<div class="session" data-session="4" markdown="1">

### 4. (9/20) 시뮬레이션 엔진 (1) — MQSim WASM 빌드 · 매핑 상태 노출


**Ryu 가 할 일**
- 빌드 결과·테스트 확인 ( WASM 모듈이 실제로 브라우저에서 로드/실행되는지 )
- **MQSim/FTL 심화** : `Address_Mapping_Unit_Page_Level.cpp` 의 실제 lookup/allocate 로직을 다시 읽고, Claude 가 추가한 hook 이 정확히 그 지점을 포착하는지 확인
- **코드 스터디** : Claude 가 `Address_Mapping_Unit_Page_Level.cpp` 에 추가한 계측 코드(hook)를 원본 로직과 나란히 읽으며, FTL 매핑 갱신이 코드 상 어느 시점인지 이해

**Claude 가 할 일**
- 프로젝트 scaffold ( Vite + React + TS )
- Emscripten 툴체인 셋업, MQSim 을 WASM 으로 빌드 ( CLI 진입점(`main.cpp`) 을 라이브러리 형태로 호출 가능하게 최소 리팩터링 )
- `Address_Mapping_Unit_Page_Level.cpp` 에 매핑 갱신 hook 추가, 매핑 테이블 상태를 JS 에서 읽을 수 있는 export 함수 작성
- host write/read 요청을 WASM 모듈에 넣고 매핑 테이블 변화를 JS 로 받아오는 최소 동작 확인
- ( 시간이 여유로울 때 ) 위에서 만든 라이브러리 분리 구조에 **GTest 프레임워크를 바로 연결** — main.cpp 리팩터링을 두 번 하지 않으려면 지금이 최적의 타이밍( 자세한 이유는 [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) 참고 )

</div>

<div class="session" data-session="5" markdown="1">

### 5. (9/26) 시뮬레이션 엔진 (2) — GC 이벤트 노출


GC 알고리즘 자체는 MQSim 에 이미 구현되어 있음( `GC_and_WL_Unit_Page_Level.cpp` ) — 새로 짜는 게 아니라, 그 기존 로직이 실행되는 시점을 JS 로 노출하는 hook 을 추가하는 세션.

**Ryu 가 할 일**
- **GC 이론 학습** ( Session 1 에서 미뤄둔 부분 ) : victim block 선정 알고리즘( greedy vs cost-benefit ), GC 트리거 정책과 WAF 관계
- 테스트 결과(WAF, GC 발생 횟수 등)로 hook 이 실제 GC 실행과 정확히 맞아떨어지는지 검증
- **MQSim/FTL 심화** : `GC_and_WL_Unit_Page_Level.cpp` 에서 실제 victim selection( `GC_Block_Selection_Policy=RGA` 등 ) 코드를 읽고, 방금 배운 이론과 대조
- **코드 스터디** : Claude 가 추가한 GC hook 코드를 원본 victim selection 로직과 나란히 읽으며, 방금 배운 GC 이론이 실제 코드 어디에 해당하는지 확인

**Claude 가 할 일**
- `GC_and_WL_Unit_Page_Level.cpp` 에 hook 추가 : GC 시작 / victim block 선정 / valid page migration / block erase 각 시점에서 JS 로 이벤트 통지
- WASM 모듈만 따로 단위 테스트 ( 샘플 write 시퀀스를 흘려보내 WAF, GC 발생 횟수 등이 hook 을 통해 정확히 잡히는지 검증 )

</div>

<div class="session" data-session="6" markdown="1">

### 6. (9/27) 시뮬레이션 엔진 (3) — 마모평준화 노출과 바인딩 마무리

> ⚠️ **계획 수정( 9/5 코드 재확인)** : `Address_Mapping_Unit_Hybrid.cpp` 를 직접 열어보니 **모든 메서드가 빈 스텁**( 53줄, log-block merge 로직 없음 )이었다. "hybrid 매핑도 이미 구현되어 있어서 hook 만 추가하면 된다"는 원래 전제가 틀렸음 — 자세한 근거는 [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/)의 "정확성 노트" 참고. 그래서 이 세션은 **실제로 구현되어 있는 마모 평준화(dynamic/static WL)에 집중**하고, hybrid 매핑은 직접 구현이 필요한 확장 목표( Cost-Benefit GC 와 같은 성격, 13~16번 버퍼 )로 옮긴다.

마모 평준화는 MQSim 에 실제로 구현되어 있음( `GC_and_WL_Unit_Base.cpp` 의 dynamic/static WL 로직 — [코드 분석 7-3절](/ftl-visual-simulator/mqsim/code-analysis/) 참고 ) — hook 추가와 WASM 바인딩 API 마무리가 중심.

**Ryu 가 할 일**
- **마모 평준화(dynamic/static WL) 이론 재확인** ( Session 5 GC 이론에 이어서, Session 1 에서 미뤄둔 부분 )
- 리뷰·테스트
- **MQSim/FTL 심화** : `GC_and_WL_Unit_Base.cpp`( `check_static_wl_required`/`run_static_wearleveling` )와 `Flash_Block_Manager_Base.cpp`( `Add_to_free_block_pool`/`Get_a_free_block` — dynamic WL 이 실제로 여기서 "erase count 가 가장 낮은 free 블록 우선 배정"으로 동작 )를 읽고 실제로 어떻게 도는지 확인
- **코드 스터디** : Claude 가 추가한 마모 평준화 hook 코드를 원본 로직과 나란히 읽으며, 방금 확인한 메커니즘이 코드 어디에 해당하는지 확인

**Claude 가 할 일**
- dynamic wear-leveling( `Add_to_free_block_pool`/`Get_a_free_block` ), static wear-leveling( `run_static_wearleveling` ) 코드에 상태 변경 hook 추가
- ( Hybrid 매핑은 빈 스텁이라 이 세션에서는 hook 추가 대상에서 제외 — 확장 목표로 이동 )
- WASM 바인딩 API 확정 ( init(config), step()/run(n), getState(), configure() )
- 결과물 : UI 없이도 동작·테스트가 끝난 WASM 엔진 + 바인딩

</div>

<div class="session" data-session="7" markdown="1">

### 7. (10/3) 시각화 (1) — flash grid · 매핑 테이블 뷰


**Ryu 가 할 일**
- 브라우저에서 직접 조작해보며 리뷰·피드백
- **MQSim/FTL 심화** : 지금 만든 시각화 요소가 MQSim 의 `Stats.cpp` 에서 어떤 통계 항목에 대응하는지 매핑해보기

**Claude 가 할 일**
- flash array grid 시각화 ( block/page 상태별 색상 구분 ), WASM 모듈이 보내는 hook 이벤트를 구독해 write/GC 실시간 애니메이션으로 연결
- 매핑 테이블 뷰어 패널 ( WASM 의 `getState()` 로 매핑 테이블 스냅샷을 읽어와 표시 )
- **범례(legend) + 색상/상태 툴팁을 처음부터 붙여서 구현** ( "나중에 다듬기"가 아니라 초심자 학습 환경의 기본 요구사항 )

</div>

<div class="session" data-session="8" markdown="1">

### 8. (10/4) 시각화 (2) — 로그 · 통계 · 재생 컨트롤


**Ryu 가 할 일**
- 브라우저에서 직접 조작해보며 리뷰·피드백
- **MQSim/FTL 심화** : 9/4 에 실행했던 MQSim 결과( `workload_scenario_*.xml` 의 `Total_GC_Executions`, WAF 관련 카운터 )와 우리 대시보드 지표를 1:1로 대조

**Claude 가 할 일**
- 이벤트 로그 / 타임라인 — hook 이벤트를 그대로 나열하지 않고, Session 3 에서 만든 쉬운 말 설명 문구로 바꿔서 표시( 예 : "block 12 GC 시작" 이 아니라 "block 12 가 꽉 차서 정리를 시작해요" )
- 통계 대시보드 ( WAF, valid page 비율, GC 발생 횟수, erase 횟수 ) — 숫자만 나열하지 않고 각 지표 옆에 "이게 왜 중요한지" 한 줄 설명 추가
- step / play·pause / 속도 조절 슬라이더 — WASM 실행을 Web Worker 로 돌리고 진행 속도를 조절하는 방식으로 구현, write/invalidate/erase/migrate 애니메이션 다듬기
- 결과물 : 고정 기본 파라미터로 브라우저에서 처음부터 끝까지 동작하는 시각화 시뮬레이터, 초심자가 설명만 보고도 따라올 수 있는 수준

</div>

<div class="session" data-session="9" markdown="1">

### 9. (10/5, 공휴일) 인터랙션 (1) — 파라미터 컨트롤 패널


**Ryu 가 할 일**
- UI 를 직접 조작해보며 리뷰·피드백
- **MQSim/FTL 심화** : `ssdconfig.xml` 의 실제 파라미터 범위/의미( `Overprovisioning_Ratio`, `GC_Exec_Threshold`, `GC_Hard_Threshold` 등 )를 다시 확인하고 우리 UI 파라미터와 1:1 대응시키기

**Claude 가 할 일**
- page 크기, block/page 개수, OP 비율, GC 임계값, 매핑 방식 선택 UI — 각 항목에 Session 3 에서 만든 쉬운 설명 툴팁 연결
- 파라미터 변경 시 값들을 `ssdconfig.xml` 형식 텍스트로 만들어 MEMFS 에 다시 써넣고 WASM 모듈을 재시작(reset/reconfigure)하도록 연동
- **개념별 프리셋 버튼 구현** ( "매핑 기본" / "GC 시연" / "마모평준화 시연" ) — 클릭 한 번으로 해당 개념이 잘 보이는 파라미터 조합으로 바로 전환. 초심자는 파라미터를 직접 안 만져도 프리셋만으로 각 개념을 볼 수 있게 함

</div>

<div class="session" data-session="10" markdown="1">

### 10. (10/9, 공휴일) 인터랙션 (2) — workload 컨트롤


**Ryu 가 할 일**
- UI 를 직접 조작해보며 리뷰·피드백
- **MQSim/FTL 심화** : `workload.xml` 의 synthetic vs trace-based 워크로드 정의 방식을 비교하고, `tpcc-small.trace` 포맷을 다시 훑어보기

**Claude 가 할 일**
- workload 생성기 컨트롤 ( sequential/random, read/write 비율, burst 크기 ) — 값을 `workload.xml` 형식으로 만들어 MEMFS 에 전달
- Session 9 의 개념별 프리셋에 맞는 workload 도 함께 세팅( 예 : "GC 시연" 프리셋은 파라미터뿐 아니라 occupancy 를 빠르게 채우는 workload 도 자동으로 같이 걸리게 )
- ( 선택 ) 커스텀 trace 파일 업로드 → MEMFS 에 그대로 마운트해서 MQSim 의 기존 trace 파싱 코드로 실행
- 입력값 검증 및 파라미터 범위 제한
- 결과물 : 프리셋으로 개념을 빠르게 보거나, 파라미터/workload 를 직접 바꿔가며 동작 차이를 관찰할 수 있는 완전한 인터랙티브 시뮬레이터

</div>

<div class="session" data-session="11" markdown="1">

### 11. (10/10) 마무리 (1) — 다듬기


**Ryu 가 할 일**
- 브라우저에서 직접 확인하며 리뷰·피드백
- **MQSim/FTL 심화** : 지금까지 추가된 hook 들( 매핑, GC, 마모평준화 )이 실제 FTL 동작을 빠짐없이 반영하는지 처음부터 끝까지 전체적으로 재점검

**Claude 가 할 일**
- UI 다듬기 ( 범례, 툴팁, 반응형 레이아웃, 색상 접근성 )
- 버그 수정, 크로스 브라우저 확인
- README / 동작 원리 문서 작성

</div>

<div class="session" data-session="12" markdown="1">

### 12. (10/11) 마무리 (2) — 최종 테스트 · 배포 · 리뷰


**Ryu 가 할 일**
- 배포된 사이트를 직접 리뷰 — 1차 완성본 리뷰, 여기서 나온 피드백은 10/17 이후 버퍼 기간에 반영
- **MQSim/FTL 심화(캡스톤)** : host write 요청 하나를 골라, 매핑 조회 → GC 트리거 여부 → flash 물리 동작까지 전체 경로를 도움 없이 처음부터 끝까지 설명해보기 — 설명이 막힘없이 이어지면 이번 1차 완성 목표가 제대로 달성된 것

**Claude 가 할 일**
- 최종 테스트, GitHub Pages 배포

</div>

<div style="margin-top: 100px;"></div>

## 페이싱 & 리스크 노트

- 12세션( 9/4 ~ 10/11 ) 을 다 채우면 정확히 1차 마감일에 맞음 → 여유가 거의 없는 일정
- 가장 위험한 세션은 **Phase 4 (시뮬레이션 엔진, 세션 4~6)**. 여기서 밀리면 Phase 5(시각화) 범위를 줄여서 흡수하고( 예 : 이벤트 로그 생략, grid+매핑테이블+통계만 유지 ), 엔진 정확성과 세션 11~12( 다듬기·배포 ) 는 타협하지 않기
- **엔진을 MQSim C++ 원본을 WASM 으로 컴파일해서 그대로 쓰기로 결정** — TS 로 새로 짜는 것보다 훨씬 정확하지만( MQSim 논문/코드와 100% 동일한 동작 ), Emscripten 빌드 자체가 가능한지, CLI 진입점을 라이브러리 형태로 바꿀 수 있는지가 세션 4의 첫 번째 관문. 만약 WASM 빌드가 예상보다 오래 걸리면 세션 4 안에서 "빌드만 되는 것"을 최소 목표로 잡고, hook 추가는 세션 5~6 으로 늦추기
- 세션 11~12( 마무리·배포 ) 는 일부러 축소하지 않음 — 10/11 에 "리뷰할 수 있는 배포된 결과물" 이 있는 것이 이번 계획의 핵심 목표이기 때문
- 평일에 시간이 나면 : 다음 세션 내용을 미리 당기거나, 확장 기능( DFTL 매핑 캐시 시각화, 실제 SSD trace 재생 ) 에 투자하거나, 그냥 버퍼로 저축
- 세션이 통째로 날아가면 억지로 다음 세션에 두 개를 몰아넣지 말고, 세션 11~12 버퍼로 흡수하는 쪽을 우선. 그래도 안 되면 10/11 리뷰 범위를 줄이고 10/17 이후로 일부 항목을 미루기

<script>
(function () {
  var STORAGE_KEY = 'ftl-visual-simulator-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var marks = Array.prototype.slice.call(document.querySelectorAll('.buffer-mark'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = marks.length;
    var state = load();

    function render() {
      var done = 0;
      marks.forEach(function (mark) {
        var id = mark.getAttribute('data-session');
        var isDone = !!state[id];
        mark.textContent = isDone ? '✅' : '☐';
        var wrap = document.querySelector('.session[data-session="' + id + '"]');
        if (wrap) wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    marks.forEach(function (mark) {
      mark.addEventListener('click', function () {
        var id = mark.getAttribute('data-session');
        state[id] = !state[id];
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
