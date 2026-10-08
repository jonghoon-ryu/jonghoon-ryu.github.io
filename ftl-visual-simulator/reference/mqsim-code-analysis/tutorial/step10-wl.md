---
layout: default
title: 10. FTL ⑤ 마모평준화
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 10. FTL ⑤ 마모평준화

마모 평준화는 별도의 큰 모듈이 아니라 **블록 매니저의 자료구조와 GC 코드에 얹힌 두 가지 장치**다. block 은 지울 수 있는 횟수에 한계가 있어서, 특정 block 만 계속 지워지지 않게 하는 것이 목적이다.


<div style="margin-top: 60px;"></div>

## 1. dynamic — 새로 쓸 곳을 고를 때 덜 닳은 곳

<svg viewBox="0 0 980 330" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="dynamic 마모평준화"><defs><marker id="adyn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="adyns" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">dynamic: free pool 의 정렬이 곧 마모 평준화</text><text x="20" y="60" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">free pool (multimap&lt; erase 횟수, block &gt;)</text><rect x="20" y="75" width="135" height="62" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="87.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 7</text><text x="87.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 0회</text><rect x="170" y="75" width="135" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="237.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 3</text><text x="237.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 1회</text><rect x="320" y="75" width="135" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="387.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 9</text><text x="387.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 1회</text><rect x="470" y="75" width="135" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="537.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 5</text><text x="537.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 2회</text><rect x="620" y="75" width="135" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="687.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 2</text><text x="687.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 4회</text><rect x="770" y="75" width="135" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="837.5" y="104.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block 11</text><text x="837.5" y="123.0" font-size="11" fill="#4d5656" text-anchor="middle">erase 5회</text><text x="87" y="160" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">← begin(): 새 write frontier 로 뽑힘</text><rect x="20" y="190" width="460" height="120" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="250.0" y="225.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Add_to_free_block_pool(block, consider_dynamic_wl)</text><text x="250.0" y="244.0" font-size="11" fill="#4d5656" text-anchor="middle">Dynamic_Wearleveling_Enabled = true</text><text x="250.0" y="259.0" font-size="11" fill="#4d5656" text-anchor="middle">  → 키 = block 의 erase 횟수 (적을수록 앞)</text><text x="250.0" y="274.0" font-size="11" fill="#4d5656" text-anchor="middle">false</text><text x="250.0" y="289.0" font-size="11" fill="#4d5656" text-anchor="middle">  → 키 = 0 으로 전부 같음 (삽입 순서)</text><rect x="500" y="190" width="465" height="120" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="732.5" y="225.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Get_a_free_block(stream, for_mapping)</text><text x="732.5" y="244.0" font-size="11" fill="#4d5656" text-anchor="middle">block = Free_block_pool.begin()  // 맨 앞</text><text x="732.5" y="259.0" font-size="11" fill="#4d5656" text-anchor="middle">pool 에서 지우고 Stream_id 를 붙여 반환</text><text x="732.5" y="274.0" font-size="11" fill="#4d5656" text-anchor="middle"></text><text x="732.5" y="289.0" font-size="11" fill="#4d5656" text-anchor="middle">→ 가장 덜 닳은 block 부터 쓰이게 된다</text></svg>

별도의 "평준화 로직" 이 없다. free pool 이 **erase 횟수로 정렬된 multimap** 이고, 새 frontier 를 고를 때 맨 앞을 뽑을 뿐이다.

```cpp
void PlaneBookKeepingType::Add_to_free_block_pool(Block_Pool_Slot_Type* block, bool consider_dynamic_wl) {
    if (consider_dynamic_wl) {
        std::pair<unsigned int, Block_Pool_Slot_Type*> entry(block->Erase_count, block);   // 키 = erase 횟수
        Free_block_pool.insert(entry);
    } else {
        std::pair<unsigned int, Block_Pool_Slot_Type*> entry(0, block);                    // 전부 키 0
        Free_block_pool.insert(entry);
    }
}
```

지운 block 이 pool 로 돌아갈 때(`Add_erased_block_to_pool`, `Flash_Block_Manager.cpp:134`) 이 함수가 불린다. 설정 `Dynamic_Wearleveling_Enabled` 가 끄면 키가 모두 0 이라 삽입 순서대로 나온다.

**한계**: dynamic 은 "자주 지워지는 block" 만 걸러 줄 뿐이다. 한 번 쓰고 안 바뀌는 데이터가 있는 block 은 free pool 에 돌아오지 않으므로 이 장치가 닿지 못한다. 그래서 static 이 필요하다.


<div style="margin-top: 60px;"></div>

## 2. static — 덜 닳은 곳에 갇힌 cold 데이터 꺼내기

<svg viewBox="0 0 980 300" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="static 마모평준화"><defs><marker id="asta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="astas" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">static: 안 지워지는 block 의 cold 데이터를 꺼낸다</text><rect x="40" y="72.6" width="48" height="127.4" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="1.5"/><text x="64" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 0</text><text x="64" y="67.6" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">98</text><rect x="110" y="67.4" width="48" height="132.6" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="1.5"/><text x="134" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 1</text><text x="134" y="62.400000000000006" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">102</text><rect x="180" y="76.5" width="48" height="123.5" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="1.5"/><text x="204" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 2</text><text x="204" y="71.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">95</text><rect x="250" y="198.7" width="48" height="1.3" rx="3" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="1.5"/><text x="274" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 3</text><text x="274" y="193.7" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">1</text><rect x="320" y="71.29999999999998" width="48" height="128.70000000000002" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="1.5"/><text x="344" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 4</text><text x="344" y="66.29999999999998" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">99</text><rect x="390" y="68.69999999999999" width="48" height="131.3" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="1.5"/><text x="414" y="218" font-size="10.5" fill="#2c3e50" text-anchor="middle">Block 5</text><text x="414" y="63.69999999999999" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">101</text><text x="20" y="245" font-size="10.5" fill="#7f8c8d" text-anchor="start">erase 횟수</text><rect x="500" y="40" width="465" height="90" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="732.5" y="75.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">cold 데이터</text><text x="732.5" y="94.0" font-size="11" fill="#4d5656" text-anchor="middle">Block 3 에 한 번 쓰고 다시는 안 바뀌는 데이터가 있다</text><text x="732.5" y="109.0" font-size="11" fill="#4d5656" text-anchor="middle">→ 이 block 은 GC victim 으로 뽑힐 일이 없어 erase 횟수가 1 에 머문다</text><rect x="500" y="150" width="465" height="130" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="732.5" y="190.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">static WL 이 하는 일</text><text x="732.5" y="209.0" font-size="11" fill="#4d5656" text-anchor="middle">① erase 가 끝날 때마다 &quot;차이가 임계값 이상인가?&quot; 검사</text><text x="732.5" y="224.0" font-size="11" fill="#4d5656" text-anchor="middle">② 그렇다면 가장 덜 닳은(coldest) block 을 victim 으로</text><text x="732.5" y="239.0" font-size="11" fill="#4d5656" text-anchor="middle">③ GC 와 같은 절차로 valid page 를 옮기고 지운다</text><text x="732.5" y="254.0" font-size="11" fill="#4d5656" text-anchor="middle">→ Block 3 이 free pool 로 돌아와 다시 쓰이게 된다</text></svg>

GC 의 erase 가 끝날 때마다(`GC_and_WL_Unit_Base.cpp:` ERASE 분기) 이 검사가 돈다.

```cpp
inline bool check_static_wl_required(const Physical_Page_Address plane_address) {              // :245
    return static_wearleveling_enabled
        && (block_manager->Get_min_max_erase_difference(plane_address) >= static_wearleveling_threshold);
}

void run_static_wearleveling(const Physical_Page_Address plane_address) {                      // :250
    flash_block_ID_type wl_candidate_block_id = block_manager->Get_coldest_block_id(plane_address);
    if (!is_safe_gc_wl_candidate(pbke, wl_candidate_block_id))
        return;                                  // 안전하지 않으면 조용히 포기
    ...                                           // 이후는 GC 와 같은 절차 (Total_wl_executions++)
}
```

`Static_Wearleveling_Threshold` 의 기본값은 100 이다. 발동하면 **plane 에서 erase 횟수가 가장 적은 block**(`Get_coldest_block_id`)을 victim 으로 삼아 valid page 를 옮기고 지운다. 그 block 이 free pool 로 돌아오면 이제 다시 쓰인다.

> **원본의 함정 두 가지** — 이 프로젝트가 직접 부딪쳐 고친 곳이다.
>
> 1. `Get_min_max_erase_difference()` (`Flash_Block_Manager_Base.cpp:146`) 는 이름과 달리 **erase 횟수의 차이가 아니라 block 번호(인덱스)의 차이**(`max_erased_block - min_erased_block`)를 돌려준다. 그래서 발동 여부가 실제 마모와 무관하다.
> 2. `Get_coldest_block_id()` 는 plane 전체에서 가장 덜 닳은 block 을 고르는데, 그것은 대개 **데이터가 한 번도 안 쓰인 frontier block** 이다. `is_safe_gc_wl_candidate()` 가 frontier 를 거절하므로 `run_static_wearleveling()` 이 매번 조용히 포기한다.
>
> 자세한 조사와 수정은 [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/code-change/bug-list/wl-bug-deviation/) · [정적 마모 평준화 대상 선정 버그와 멈춤 버그들](/ftl-visual-simulator/reference/code-change/bug-list/wl-target-and-stall-bugs/) · [정적 마모 평준화 설정이 전달되지 않던 버그](/ftl-visual-simulator/reference/code-change/bug-list/wl-threshold-not-wired-bug/) 에 있다.


<div style="margin-top: 60px;"></div>

## 3. 둘의 역할 분담

| | dynamic | static |
|---|---|---|
| 하는 일 | 새로 쓸 block 을 고를 때 덜 닳은 것 우선 | 덜 닳은 block 안의 cold 데이터를 옮겨 그 block 을 되살림 |
| 언제 | 새 write frontier 가 필요할 때마다 | 매 GC erase 직후 검사, 차이가 임계값 이상일 때만 |
| 비용 | 공짜 (정렬된 자료구조) | page 이동 쓰기 + erase 한 번 — WAF 가 오른다 |
| 못 하는 것 | cold 데이터가 점유한 block | 임계값 미만의 작은 불균형 |

## 확인해 보기

1. `Dynamic_Wearleveling_Enabled` 를 끄면 어느 줄에서 free pool 키가 달라지나?
2. static WL 이 이동시키는 page 는 WAF 계산에서 어디에 해당하나? ([9단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/)의 표를 보자)
3. 모든 block 이 거의 같은 횟수로 지워지고 있다면 static WL 이 발동하지 않는 것이 맞나?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 9. FTL ④ 가비지 컬렉션](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/)</span><span>[11. 마무리 — 전체 콜 그래프 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step11-wrapup/)</span></div>
