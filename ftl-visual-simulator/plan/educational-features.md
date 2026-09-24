---
layout: default
title: 교육용 기능 추가 기록
permalink: /ftl-visual-simulator/plan/educational-features/
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
</style>

# 교육용 기능 추가 기록

마모평준화 시연 연동과 멈춤 버그 수정이 끝난 뒤(2026-09-24), 방향을 **"이 앱은 교육용이다 — 기능 하나가 FTL 개념 하나를 눈에 보이게 해야 한다"** 로 잡고 기능 5개를 추가했다. 이 문서는 각 기능이 어떤 개념을 보여주려는 것인지, 만들면서 실제로 확인한 숫자, 그리고 그 과정에서 틀린 설명을 하나 바로잡은 일을 기록한다.

<div style="margin-top: 60px;"></div>

## 한눈에 보기

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th style="width:24%">기능</th><th style="width:36%">보여주는 개념</th><th style="width:22%">프리셋</th><th style="width:18%">앱 커밋</th></tr>
<tr><td>1. 빈 block 수 변화 차트</td><td>GC 임계값 — 빈 block 이 줄면 GC 가 시작되는 톱니 모양</td><td>GC 시연, 마모평준화 시연</td><td><code>7072833</code></td></tr>
<tr><td>2. "왜 이 block 이 GC victim?"</td><td>victim 선택 규칙과 GC 비용(옮길 valid page 수)</td><td>GC 시연</td><td><code>7072833</code></td></tr>
<tr><td>3. GC 알고리즘 비교</td><td>victim 선택 정책이 WAF 를 좌우한다</td><td>GC 시연</td><td><code>78e6f7d</code></td></tr>
<tr><td>4. 한 쓰기 따라가기</td><td>out-of-place update — 덮어쓰기는 항상 새 page 로 간다</td><td>전부(마모평준화 시연은 목록만)</td><td><code>b45cb2a</code></td></tr>
<tr><td>5. DRAM 쓰기 캐시 켜기/끄기</td><td>DRAM 캐시가 flash 까지 가는 쓰기를 얼마나 흡수하는가</td><td>전부</td><td><code>3cf0e2a</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 1. 빈 block 수 변화 차트

슬라이더의 숫자로만 있던 "GC 임계값"을 그림으로 보여준다. 격자 아래에 **칩별 빈 block 수를 시간에 따라** 그리고:

- GC 임계값을 점선으로,
- GC 가 시작된 순간을 ●, 정적 마모평준화(WL)가 시작된 순간을 ★ 로 표시한다.

빈 block 이 임계값 아래로 내려가면 GC 가 시작되고, block 하나를 지워서 다시 올라가는 **톱니 모양**이 그대로 보인다(GC 시연 기본값: 임계값 6, 빈 block 이 5-6 사이를 오간다). ● 는 GC 가 시작될 때 엔진이 실제로 본 빈 block 수에 찍어서, 화면 갱신(tick) 사이에 지나가 버리는 짧은 dip 도 놓치지 않는다. 마우스를 올리면 그 시점의 빈 block 수와 그때 일어난 GC/WL 설명이 나온다.

칩마다 작은 차트를 따로 그린다(small multiples). 앱의 칩 색들이 색각 이상 기준으로 서로 잘 구분되지 않아서, 한 차트에 선을 겹쳐 색으로만 구분하는 방식은 쓰지 않았다.

<div style="margin-top: 60px;"></div>

## 2. "왜 이 block 을 GC victim 으로 골랐나요?"

마모평준화 시연의 "왜 발동했는지 보기"와 같은 형식으로, GC 시연에서 **가장 최근 GC 가 고른 block 과 그 이유**를 보여준다:

- 빈 block 수 vs 임계값 — 예: "빈 block 3 < 임계값 6 이라서 GC 시작"
- victim 의 valid page 수(옮겨야 할 것) / invalid page 수(지우면 비워질 것) — 예: valid 10 / invalid 6
- 지금 선택된 GC 알고리즘이 victim 을 고르는 규칙 — 예: RGA 는 가득 찬 안전한 block 중 무작위로 log2(block 수)개(block 12개면 3개)를 뽑아 그중 invalid 가 가장 많은 것

valid page 가 많은 victim 일수록 GC 한 번에 옮겨야 할 page 가 많고, 그 복사 쓰기가 곧 WAF 의 증가분이다. 알고리즘 드롭다운을 바꿔가며 victim 의 valid 수를 비교해보면 **victim 선택이 왜 WAF 를 좌우하는지**가 보인다.

엔진 쪽은 `gc_started` 이벤트에 victim 의 valid/invalid page 수, block 당 page 수, 그 순간의 빈 block 수와 임계값을 추가했다(`Simulation_Events` → WASM 바인딩). 차트용 칩별 빈 block 수와 임계값은 `getState().stats` 에 추가.

<div style="margin-top: 60px;"></div>

## 3. GC 알고리즘 비교 — 그리고 틀린 설명 하나

GC 시연 패널의 **"지금 설정으로 GC 알고리즘 6개 비교하기"** 버튼: 같은 설정·같은 워크로드로 알고리즘만 바꿔서 6번을 끝까지 돌리고, 결과를 표로 나란히 보여준다. 계산은 자기 WASM 인스턴스를 가진 별도 Web Worker 에서 해서(각 약 2.4초, 전체 약 10초) 화면에서 재생 중인 시뮬레이션에는 영향이 없다.

기본 설정 결과:

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>알고리즘</th><th>GC 실행 횟수</th><th>옮긴 page</th><th>GC 1번에 옮긴 page</th><th>WAF</th></tr>
<tr><td>RGA</td><td>31</td><td>137</td><td>4.4</td><td>1.27x</td></tr>
<tr><td>Greedy</td><td>31</td><td>137</td><td>4.4</td><td>1.27x</td></tr>
<tr><td><b>Random</b></td><td>25</td><td>97</td><td>3.9</td><td><b>1.19x (가장 낮음)</b></td></tr>
<tr><td>Random-p</td><td>33</td><td>196</td><td>5.9</td><td>1.40x</td></tr>
<tr><td>Random-pp</td><td>33</td><td>196</td><td>5.9</td><td>1.40x</td></tr>
<tr><td>FIFO</td><td>34</td><td>171</td><td>5.0</td><td>1.34x</td></tr>
</table>
</div>

WAF = (호스트 쓰기 + GC 가 옮긴 page) / 호스트 쓰기.

**예상과 달리 plain Random 이 가장 쌌다.** 이유는 MQSim 의 Random 구현에 있다: Random 은 "안전한 후보(write frontier 가 아님)"가 나올 때까지만 다시 뽑고, 그 block 에 **invalid page 가 있는지는 확인하지 않는다**. 그래서 아직 덜 찼거나 전부 valid 인 block 을 뽑는 일이 잦은데, 그러면 뒤의 공통 검사("지울 invalid page 없음")에 걸려 **그 GC 기회를 그냥 건너뛴다**. 결과적으로 GC 자체를 덜 하고(25회), 옮기는 page 도 적다. 반면 Random-p 는 "가득 찬 block", Random-pp 는 거기에 "invalid page 가 일정 수 이상"인 block 이 나올 때까지 다시 뽑기 때문에 GC 기회를 거의 놓치지 않고, 가득 찬 block 이면 valid page 가 많아도 그대로 골라서 가장 비싸다.

이 결과 때문에 앱 곳곳에 있던 **"Random 은 RGA/Greedy 보다 훨씬 헛수고한다"** 는 설명(파라미터 힌트, 사용법, 2번의 victim 설명)이 적어도 이 시뮬레이터에서는 틀린 말이었다는 것이 드러났다. 교과서적인 직관("무작위로 고르면 valid 가 많은 block 을 고를 수도 있으니 비효율적")이 틀렸다기보다는, 실제 구현이 "못 고르면 건너뛴다"는 다른 동작을 하고 있었던 것. 그래서 설명은 각 알고리즘이 **어떻게 고르는지**만 말하고, 실제 비용은 비교 표로 직접 확인하도록 바꿨다.

<div style="margin-top: 60px;"></div>

## 4. 한 쓰기 따라가기

로그에서 LPN 이 있는 줄(호스트 쓰기, GC/WL 의 page 이동)을 클릭하면 그 논리 page 하나의 **여정**을 보여준다:

- **"LPN 0x037 의 여정" 패널**: 그 데이터가 거쳐 간 물리 page 를 순서대로 — 처음 쓰기 → (GC 가 옮김) → 덮어쓰기(같은 자리에 못 쓰고 새 page 로) … → 지금 여기. 예전 복사본이 있던 block 이 이미 지워졌으면 몇 개가 사라졌는지도.
- **격자**: 지금 데이터가 있는 page 는 굵은 테두리, 아직 지워지지 않은 예전 복사본(invalid page)은 점선 테두리.
- **로그**: 그 LPN 에 관한 줄 전부 강조.

flash 는 제자리 덮어쓰기가 안 되기 때문에 쓰기마다 새 page 로 가고 예전 page 는 invalid 가 되며, GC 는 살아있는(valid) page 만 옮기고 block 을 지운다 — FTL 의 가장 핵심인 **out-of-place update** 를 LPN 하나로 따라가 보는 기능이다. 브라우저 GC 시연에서 확인한 예: "처음 쓰기(Block 0) → GC 가 옮김(Block 2) → 덮어쓰기(Block 7, 지금 여기)", 격자에 현재 칸 1개 + 점선 칸 1개, 지워진 복사본 1개.

마모평준화 시연은 page 격자가 없는 화면이라 패널의 목록만 나온다.

<div style="margin-top: 60px;"></div>

## 5. DRAM 쓰기 캐시 켜기/끄기

Workload 패널에 **"DRAM 쓰기 캐시"** 체크박스(기본 켜짐)를 추가하고, 통계에 **"호스트 요청 → flash 쓰기"**(호스트가 보낸 요청 수 → 실제로 flash 에 쓴 page 수)를 추가했다. 캐시가 켜져 있으면 SSD 안의 DRAM 이 쓰기를 먼저 받아서 같은 page 에 대한 반복 쓰기를 흡수하고, sector 단위의 작은 쓰기를 page 단위로 모아서 flash 에 내려보낸다. MQSim 설정으로는 `Device_Level_Data_Caching_Mode` 의 `WRITE_CACHE` / `TURNED_OFF`.

기본 설정으로 끝까지 돌린 결과:

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>프리셋</th><th>캐시 켜짐</th><th>캐시 꺼짐</th></tr>
<tr><td>GC 시연</td><td>요청 2,176,929 → flash 쓰기 504, GC 31회, WAF 1.27</td><td>요청 3,900 → flash 쓰기 3,809, GC 370회, WAF 1.59</td></tr>
<tr><td>마모평준화 시연</td><td>GC 58회, WL 7회</td><td>GC 257회, WL 44회, WAF 1.92</td></tr>
</table>
</div>

두 가지를 읽을 수 있다:

- **캐시를 끄면 요청이 거의 1:1 로 flash 쓰기가 된다.** 그만큼 block 이 빨리 차서 GC 가 10배 이상 자주 일어나고, WAF 도 올라간다.
- **캐시를 켰을 때 요청 수가 수백 배 많은 것은 같은 일을 더 많이 해서가 아니다.** 이 워크로드 생성기(`QUEUE_DEPTH` 방식)는 요청 하나가 끝나야 다음 요청을 만드는데, 캐시는 요청을 DRAM 에서 바로 끝내주므로 같은 시뮬레이션 시간 동안 훨씬 많은 요청이 만들어진다. 그런데도 flash 까지 내려간 것은 504 page 뿐 — 작은 working set 을 계속 덮어쓰는 이 워크로드에서는 캐시가 거의 전부를 흡수한다.

이 두 번째 점은 같은 날 "매핑 기본" 재생이 1분 넘게 멈춘 것처럼 보였던 문제([3a9d283](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/commit/3a9d283) — 캐시가 쓰기를 흡수하는 동안 flash 쪽 이벤트가 하나도 없어서 화면이 안 바뀌던 것)의 원인이기도 하다. 이제 학습자가 체크박스 하나로 그 차이를 직접 볼 수 있다.

구현 메모:

- 캐시를 끄면 한 실행의 이벤트 묶음(event-group) 수가 350-500배 적어져서, 기존 재생 속도로는 1-2 tick 만에 끝나버렸다. 캐시 꺼짐 전용 배수(GC 시연 35, 마모평준화 시연 28)를 둬서 켜짐과 비슷한 약 180 tick 길이를 유지한다.
- 마모평준화 시연의 cold flow 는 이 체크박스와 상관없이 **항상 캐시 끔** — 켜두면 캐시가 "한 번만 쓰는" 데이터까지 흡수해서 flash 에 cold block 이 생기지 않는다([마모평준화 시연 연동 기록 9.2](/ftl-visual-simulator/plan/wear-leveling-integration/#section-9)).
- 엔진: `MQSim_Interface::Get_host_requests_serviced()`(모든 IO flow 의 완료 요청 수 합) → WASM `stats.hostRequestsServiced`.

<div style="margin-top: 60px;"></div>

## 검증

다섯 기능 모두 같은 방식으로 확인했다:

- **엔진 회귀 테스트**: golden 3/3, 유닛(GTest/GMock) 14/14 — 이벤트 필드 추가가 시뮬레이션 결과를 바꾸지 않았음을 확인.
- **Node 에서 WASM 직접 실행**: 화면에 나올 숫자(GC 이벤트의 valid/invalid 값, 6개 알고리즘 비교값, 캐시 켜짐/꺼짐 결과)를 브라우저 없이 먼저 뽑아두고,
- **브라우저**에서 같은 값이 나오는지 비교(예: 비교 표가 Node 결과와 정확히 일치, GC ● 11개 전부 임계값 선 아래).

<div style="margin-top: 60px;"></div>

## Ryu 가 공부할 거리

- **GC victim 선택 코드**: `ssd/GC_and_WL_Unit_Page_Level.cpp` 의 victim 선택 `switch` — RGA/Greedy/Random/Random-p/Random-pp/FIFO 가 각각 후보를 어떻게 뽑고, 못 뽑았을 때 어떻게 하는지(3번의 Random 결과가 여기서 나온다).
- **GC 임계값**: `GC_and_WL_Unit_Base` 생성자에서 GC 시작 기준(빈 block 수)이 어떻게 계산되는지 — 1번 차트의 점선이 이 값이다.
- **DRAM 캐시**: `ssd/Data_Cache_Manager_Flash_Advanced.cpp` — 쓰기 요청이 캐시에 들어갔을 때 언제 호스트에 "완료"를 돌려주고, 언제 flash 로 내려보내는지(5번의 요청 수 차이가 여기서 나온다).

<div style="margin-top: 60px;"></div>

## 참고

- [시뮬레이터 열기](https://jonghoon-ryu.github.io/ftl-visual-simulator-app/)
- [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/), [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/)
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 각 커밋 메시지에 구현 상세
