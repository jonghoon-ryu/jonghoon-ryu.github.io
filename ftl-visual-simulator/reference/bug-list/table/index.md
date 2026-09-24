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

[버그 목록](/ftl-visual-simulator/reference/bug-list/) 하위 문서들에 흩어져 있는 버그를 한 번에 훑어볼 수 있게 정리한 표. 지금까지 이 프로젝트에서 실제 MQSim 원본 코드에서 찾아낸 버그는 총 **27개** — 전부 수정해서 유지 중이다.

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
<tr>
  <td>11</td>
  <td>GC 마이그레이션 쓰기가 진행-중-쓰기 카운트를 전혀 남기지 않음</td>
  <td><code>ssd/Flash_Block_Manager.cpp</code>, <code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>로직(카운트 누락 → 자기 자신 경쟁 상태)</td>
  <td>"GC 시연" GC 실행 횟수 0 조사 중</td>
  <td>예(WASM 하네스로 확인)</td>
  <td rowspan="2"><a href="/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/">GC 자기 자신 경쟁 상태 버그</a></td>
</tr>
<tr>
  <td>12</td>
  <td>RGA 후보 탐색 루프에 반복 횟수 상한이 없어 무한 루프 가능</td>
  <td><code>ssd/GC_and_WL_Unit_Page_Level.cpp</code></td>
  <td>로직(무한 루프) — 이미 배포된 조합에서 재현 가능했던 라이브 이슈</td>
  <td>버그 11을 고치자 바로 드러남</td>
  <td>예(WASM 하네스로 확인)</td>
</tr>
<tr>
  <td>13</td>
  <td>RGA 후보 선택이 "다 쓴 block인지" 확인을 안 해서 빈 block도 후보에 포함됨</td>
  <td><code>ssd/GC_and_WL_Unit_Page_Level.cpp</code></td>
  <td>로직(후보 필터 누락) — RANDOM_P/RANDOM_PP는 이미 이 확인을 함</td>
  <td>"매핑 기본"에서 GC 임계값/워크로드를 맞춰줘도 GC가 발동 안 하는 이유 조사 중</td>
  <td>예(WASM 하네스로 확인)</td>
  <td><a href="/ftl-visual-simulator/reference/bug-list/rga-incomplete-block-bug/">RGA 후보 선택이 아직 다 안 쓴 block도 포함하던 버그</a></td>
</tr>
<tr>
  <td>14</td>
  <td>서스펜드 switch-case에 break 누락으로 서스펜드가 항상 무력화</td>
  <td><code>ssd/TSU_OutofOrder.cpp</code>, <code>ssd/TSU_Priority_OutOfOrder.cpp</code>(6곳)</td>
  <td>로직(switch fallthrough)</td>
  <td>마모평준화 시연 threshold 인상 조사 중</td>
  <td>예</td>
  <td rowspan="4"><a href="/ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/">명령 서스펜드가 한 번도 작동한 적이 없던 버그</a></td>
</tr>
<tr>
  <td>15</td>
  <td><code>TSU_Base</code> 생성자 호출 시 bool 2개와 time 3개의 인자 순서가 뒤바뀜</td>
  <td><code>ssd/TSU_OutofOrder.cpp</code>, <code>ssd/TSU_Priority_OutOfOrder.cpp</code></td>
  <td>로직(인자 순서 오류)</td>
  <td>버그 14를 고치자 바로 드러남</td>
  <td>예</td>
</tr>
<tr>
  <td>16</td>
  <td>단일 다이 구성에서 서스펜드 시 활성 다이 카운터가 리셋 안 됨</td>
  <td><code>ssd/NVM_PHY_ONFI_NVDDR2.cpp</code></td>
  <td>로직(조건 오류)</td>
  <td>버그 15를 고치자 바로 드러남</td>
  <td>예</td>
</tr>
<tr>
  <td>17</td>
  <td>리쥼 시 활성 다이 카운터를 복원하지 않아 이후 unsigned 언더플로</td>
  <td><code>ssd/NVM_PHY_ONFI_NVDDR2.h</code></td>
  <td>로직(카운터 언더플로) → 칩 영구 정지</td>
  <td>버그 16과 동시에 발견</td>
  <td>예</td>
</tr>
<tr>
  <td>18</td>
  <td>static WL 대상이 평면 전체 최소 erase count block 으로만 정해져, 한 번도 안 쓰이는 frontier 가 뽑히면 이후 영원히 발동 불가</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>로직(후보 선정)</td>
  <td>threshold 2 이상이 발동 안 하는 이유 재조사 (2026-09-24)</td>
  <td>예</td>
  <td rowspan="10"><a href="/ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/">정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그들</a></td>
</tr>
<tr>
  <td>19</td>
  <td>대기 후 재개된 WL 이 GC 실행으로 집계됨</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>통계 집계</td>
  <td>#18 수정 중 함께 발견</td>
  <td>예</td>
</tr>
<tr>
  <td>20</td>
  <td>WL 페이지 이동이 GC 로 집계돼 <code>Average_Page_Movement_For_WL</code> 이 항상 0</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>통계 집계</td>
  <td>#18 수정 중 함께 발견</td>
  <td>예</td>
</tr>
<tr>
  <td>21</td>
  <td>LPA barrier 에서 풀려난 트랜잭션의 완료가 broadcast 되지 않아 캐시 back-pressure 누수 → 정지</td>
  <td><code>ssd/Address_Mapping_Unit_Page_Level.cpp</code></td>
  <td>로직(완료 신호 누락) → 조용한 정지</td>
  <td>threshold 를 올려 큰 규모로 돌리다 (지난번 "원인 불명 ~9e9 정지")</td>
  <td>예</td>
</tr>
<tr>
  <td>22</td>
  <td>대기했다 재개된 GC/WL 이 erase 트랜잭션을 TSU 에 제출하지 않음</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code></td>
  <td>로직(제출 누락) → 조용한 정지</td>
  <td>#21 수정 후 16 block 구성에서</td>
  <td>예</td>
</tr>
<tr>
  <td>23</td>
  <td>평면 대기열에서 풀려난 write 가 GC/WL LPA barrier 를 확인하지 않음</td>
  <td><code>ssd/Address_Mapping_Unit_Page_Level.cpp</code></td>
  <td>로직(경쟁 상태) → 크래시</td>
  <td>#22 수정 후 멀티 칩/작은 block 구성에서</td>
  <td>예</td>
</tr>
<tr>
  <td>24</td>
  <td>GC 검사가 아무것도 못 했을 때, 평면의 write 가 전부 대기 중이면 다시 검사할 계기가 없음</td>
  <td><code>ssd/GC_and_WL_Unit_Base.cpp</code>, <code>ssd/Address_Mapping_Unit_Page_Level.cpp</code></td>
  <td>로직(재시도 누락) → 조용한 정지</td>
  <td>#23 수정 후 4칩 16 block 구성에서</td>
  <td>예</td>
</tr>
<tr>
  <td>25</td>
  <td>FIFO 가 꺼낸 후보가 거절되면 <code>Block_usage_history</code> 에 다시 안 들어가 영영 후보에서 사라짐</td>
  <td><code>ssd/GC_and_WL_Unit_Page_Level.cpp</code></td>
  <td>로직(큐 누수) → 조용한 정지</td>
  <td>모든 프리셋 × GC 정책 6종 후속 스윕 (#24 의 재시도가 여기서 무한 루프가 됨)</td>
  <td>예</td>
</tr>
<tr>
  <td>26</td>
  <td>RANDOM/RANDOM_P/RANDOM_PP 가 재추첨에 실패하면 검증 안 된 마지막 후보를 그대로 사용</td>
  <td><code>ssd/GC_and_WL_Unit_Page_Level.cpp</code></td>
  <td>로직(후보 검증 누락) → 크래시</td>
  <td>같은 후속 스윕 (block 8 + 칩 4)</td>
  <td>예</td>
</tr>
<tr>
  <td>27</td>
  <td>FIFO 후보 큐에 다른 경로로 지워진 block 의 옛 항목이 남아 큐가 끝없이 커지고 FIFO 순서가 틀어짐</td>
  <td><code>ssd/Flash_Block_Manager_Base.cpp</code>, <code>ssd/GC_and_WL_Unit_Page_Level.cpp</code></td>
  <td>로직(자료구조 누수)</td>
  <td>#25 수정 중 의심 → 4배 길이 실행에서 큐 길이를 찍어 확인</td>
  <td>예</td>
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
<tr><td>로직(경쟁 상태/무한 루프)</td><td>2개(#11-12)</td><td>#12는 이미 배포된 UI 조합(멀티 칩 + 최소 block 수)에서 재현 가능했던 라이브 이슈 - 발견 즉시 함께 수정</td></tr>
<tr><td>로직(후보 필터 누락)</td><td>1개(#13)</td><td>실제 규모에서는 항상 참이라 안 드러남 - 이 프로젝트의 작은 데모 규모에서만 관찰 가능한 확률로 드러남</td></tr>
<tr><td>로직(switch fallthrough/인자 순서/카운터 언더플로)</td><td>4개(#14-17)</td><td>서로 겹겹이 가려져 있던 결함 — #14가 서스펜드 자체를 막고 있어서 #15-17은 몇 년째 실행될 기회조차 없던 코드였음</td></tr>
<tr><td>로직(static WL 후보 선정) + 통계 집계</td><td>3개(#18-20)</td><td>GC 와 WL 이 코드 경로를 공유하면서 WL 쪽 처리를 빠뜨림 — #18 때문에 "WL 은 한 번만 뜬다"를 오랫동안 다른 이유로 잘못 설명해왔음</td></tr>
<tr><td>로직(조용한 정지/크래시 사슬)</td><td>7개(#21-27)</td><td>#14-17 처럼 하나를 고쳐야 다음이 드러나는 사슬 — #22-27은 실제 SSD 규모의 block 수에선 거의 안 드러나고, 이 프로젝트의 작은 데모 규모에서만 확률적으로 나타남</td></tr>
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
- **#11-12**: "GC 시연" GC 실행 횟수가 0인 이유를 조사하다가 크래시(#11)를 발견, 고치는 과정에서 #12(무한 루프)가 바로 드러남
- **#13**: "매핑 기본"에 "GC 시연"과 똑같은 임계값/워크로드를 줘도 GC가 여전히 발동 안 하는 이유를 계속 조사하다가 발견 (Ryu 가 직접 계산으로 반박하면서 진단이 더 정확해짐)
- **#14-17**: "마모평준화 시연" WL 임계값을 올려보려다 시뮬레이션이 조용히 멈추는 문제를 다시 추적 — 이전 세션에 "TSU_FLIN" 으로 잘못 추정했던 바로 그 정지를 제대로 파고들며 연쇄적으로 발견
- **#18-24**: 같은 작업의 두 번째 라운드 — threshold 가 안 올라가는 진짜 이유(#18)를 찾고, 2-flow 워크로드로 규모를 키워 29가지 구성을 돌리며 멈춤/크래시를 하나씩 추적 (#21 이 #14-17 문서에 "남은 문제"로 적어뒀던 정지)
- **#25-26**: 같은 날 세 프리셋 전부와 GC 정책 6종으로 스윕 범위를 넓혀서 발견 — 그 과정에서 #24 수정이 FIFO 와 만나 무한 루프가 되는 이 프로젝트 자신의 회귀도 함께 잡음
- **#27**: #25 를 고치면서 의심한 것을 4배 길이 실행에서 큐 길이를 직접 찍어 확인

<div style="margin-top: 60px;"></div>

## 참고

- [버그 목록](/ftl-visual-simulator/reference/bug-list/)
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
