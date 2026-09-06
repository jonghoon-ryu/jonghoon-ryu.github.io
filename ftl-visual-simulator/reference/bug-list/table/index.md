---
layout: default
title: 버그 목록표
permalink: /ftl-visual-simulator/reference/bug-list/table/
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

# 버그 목록표

[버그 목록](/ftl-visual-simulator/reference/bug-list/) 하위 문서들에 흩어져 있는 버그를 한 번에 훑어볼 수 있게 정리한 표. 지금까지 이 프로젝트에서 실제 MQSim 원본 코드에서 찾아낸 버그는 총 **10개** — 전부 수정해서 유지 중이다.

<div style="margin-top: 60px;"></div>

## 전체 목록

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr>
  <th>#</th>
  <th>버그</th>
  <th>위치</th>
  <th>종류</th>
  <th>발견 시점</th>
  <th>네이티브에서도 재현되나</th>
  <th>문서</th>
</tr>
<tr>
  <td>1</td>
  <td>RNG 정수 오버플로우</td>
  <td><code>utils/CMRRandomGenerator.h</code></td>
  <td>이식성(UB)</td>
  <td>Session 4</td>
  <td>예(UB 자체는 있음, 결과 차이의 근본 원인은 아니었음)</td>
  <td rowspan="4"><a href="/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/">MQSim 버그 헌트</a></td>
</tr>
<tr>
  <td>2</td>
  <td>6개 클래스의 non-virtual 소멸자로 다형적 delete</td>
  <td>6개 클래스(소멸자)</td>
  <td>이식성(UB)</td>
  <td>Session 4</td>
  <td>예(UB 자체는 있음, WASM 결과엔 영향 없었음)</td>
</tr>
<tr>
  <td>3</td>
  <td><code>IO_Flow_Synthetic</code>의 미초기화 포인터</td>
  <td><code>host/IO_Flow_Synthetic.h</code></td>
  <td>이식성(미초기화 값)</td>
  <td>Session 4</td>
  <td>예(버그 2를 고치자 드러난 크래시)</td>
</tr>
<tr>
  <td>4</td>
  <td><code>std::multimap::find()</code>에 대한 잘못된 가정</td>
  <td><code>ssd/Address_Mapping_Unit_Page_Level.cpp</code></td>
  <td>이식성(근본 원인)</td>
  <td>Session 4</td>
  <td>아니오 — WASM 전용(네이티브/WASM 결과 불일치의 진짜 원인)</td>
</tr>
<tr>
  <td>5</td>
  <td><code>run_static_wearleveling()</code>이 블록 ID를 주소로 착각</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>로직(메모리 안전성)</td>
  <td>Session 6</td>
  <td>예</td>
  <td rowspan="2"><a href="/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/">마모 평준화 버그와 동작 변경</a></td>
</tr>
<tr>
  <td>6</td>
  <td>erase count 차이 대신 블록 번호 차이를 반환</td>
  <td><code>ssd/Flash_Block_Manager_Base.cpp</code>(<code>Get_min_max_erase_difference</code>)</td>
  <td>로직</td>
  <td>Session 6</td>
  <td>예</td>
</tr>
<tr>
  <td>7</td>
  <td>DRAM 캐시 대기열의 이중 소유권(use-after-free)</td>
  <td><code>ssd/Data_Cache_Manager_Flash_Advanced.cpp</code></td>
  <td>메모리 안전성(UAF)</td>
  <td>Session 9 (PR #14)</td>
  <td>예(ASan으로 확인) — 단, 재구성(reconfigure) 중간에 멈출 때만 발현</td>
  <td><a href="/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/">재구성 크래시 버그</a></td>
</tr>
<tr>
  <td>8</td>
  <td>초기화되지 않은 <code>Bandwidth</code> 필드</td>
  <td><code>exec/IO_Flow_Parameter_Set.h</code></td>
  <td>미초기화 변수 → 0 나누기</td>
  <td>Session 10</td>
  <td>아니오 — WASM 전용(힙 재사용 패턴 차이로 재현)</td>
  <td><a href="/ftl-visual-simulator/reference/bug-list/bandwidth-divide-by-zero-bug/">초기화되지 않은 Bandwidth 필드 버그</a></td>
</tr>
<tr>
  <td>9</td>
  <td><code>Static_Wearleveling_Threshold</code> 등 3개 설정값이 엔진까지 전달 안 됨</td>
  <td><code>exec/SSD_Device.cpp</code></td>
  <td>설정 누락(파라미터 배선 누락)</td>
  <td>마모평준화 시연 연동 작업 중</td>
  <td>예</td>
  <td><a href="/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/">정적 마모 평준화 설정 누락 버그</a></td>
</tr>
<tr>
  <td>10</td>
  <td>protected 메서드 2개가 <code>.cpp</code>에서 잘못 <code>inline</code> 선언됨</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>빌드/링크(버그라기보단 결함)</td>
  <td>GMock 유닛 테스트 작성 중</td>
  <td>예(네이티브 빌드에서 발견)</td>
  <td><a href="/ftl-visual-simulator/reference/bug-list/inline-linkage-bug/">잘못된 inline 선언 버그</a></td>
</tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 종류별 분류

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>종류</th><th>개수</th><th>공통점</th></tr>
<tr><td>이식성(네이티브/WASM 결과 불일치)</td><td>4개(#1-4)</td><td>고쳐도 upstream 과 다르게 동작하지 않음 — WASM 이 네이티브와 <b>같아지도록</b> 맞추는 수정</td></tr>
<tr><td>로직 오류</td><td>2개(#5-6)</td><td>네이티브에도 그대로 있던 버그 — 고치면 이 프로젝트가 upstream 과 <b>의도적으로 다르게</b> 동작함</td></tr>
<tr><td>메모리 안전성(UAF)</td><td>1개(#7)</td><td>원본 CLI 는 항상 완주 후에만 정리해서 절대 안 겪음 — 이 프로젝트의 일시정지/재구성 UI 가 처음 노출시킴</td></tr>
<tr><td>미초기화 변수</td><td>1개(#8)</td><td>XML 에 없는 필드가 힙 재사용 시 우연한 값으로 남음 — WASM 전용으로 재현</td></tr>
<tr><td>설정 누락</td><td>1개(#9)</td><td>파싱은 맞는데 실제로 쓰는 곳까지 배선이 안 됨 — 기본값과 우연히 같아서 안 드러남</td></tr>
<tr><td>빌드/링크</td><td>1개(#10)</td><td>버그라기보단 아무도 그 코드 경로를 밖에서 불러본 적이 없어서 몇 년째 티가 안 났던 결함</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 발견 계기별 분류

대부분 "새 기능을 실제로 연동하려다" 발견됐다 — 순수하게 코드를 읽다가 찾은 버그는 거의 없다:

- **#1-4**: WASM 빌드 결과가 네이티브와 달라서, 그 차이를 추적하다가 발견( Session 4 )
- **#5-6**: 마모 평준화 hook 을 추가하려다, 트리거 조건 자체가 이상해서 발견( Session 6 )
- **#7**: "GC 시연" 프리셋을 튜닝하려고 워크로드를 키우다가, 재구성 시점에 크래시가 나서 발견( Session 9 )
- **#8**: workload 컨트롤을 추가하고 접근 패턴을 반복 전환하다가, 크래시가 나서 발견( Session 10 )
- **#9**: "마모평준화 시연"을 실제로 연동하려고 threshold 를 낮춰봤는데 반응이 없어서 발견
- **#10**: 유닛 테스트를 작성하며 protected 메서드를 처음 파일 밖에서 불러보다가 발견

<div style="margin-top: 60px;"></div>

## 참고

- [버그 목록](/ftl-visual-simulator/reference/bug-list/)
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
