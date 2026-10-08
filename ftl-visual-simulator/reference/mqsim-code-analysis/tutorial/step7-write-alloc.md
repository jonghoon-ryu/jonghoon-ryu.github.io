---
layout: default
title: 7. FTL ② 쓰기와 page 할당
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 7. FTL ② 쓰기와 page 할당

`translate_lpa_to_ppa()` 의 `else` 분기, 즉 **쓰기**가 FTL 에서 가장 많은 일을 하는 곳이다. 읽기와 달리 물리 주소를 **새로 정한다.**

<svg viewBox="0 0 980 420" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="쓰기의 page 할당"><defs><marker id="aalloc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aallocs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 transaction 의 물리 page 할당 (translate_lpa_to_ppa 의 else 분기)</text><rect x="15" y="40" width="470" height="62" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="250.0" y="61.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">① allocate_plane_for_user_write</text><text x="250.0" y="80.0" font-size="10.5" fill="#4d5656" text-anchor="middle">LPA % 채널수 … 로 plane 결정</text><text x="250.0" y="94.5" font-size="10.5" fill="#4d5656" text-anchor="middle">(CWDP) :987</text><line x1="250" y1="102" x2="250" y2="116" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aalloc)"/><rect x="15" y="116" width="470" height="62" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="250.0" y="137.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">② Stop_servicing_writes?</text><text x="250.0" y="156.0" font-size="10.5" fill="#4d5656" text-anchor="middle">plane 의 free block 이 너무 적으면</text><text x="250.0" y="170.5" font-size="10.5" fill="#4d5656" text-anchor="middle">true → 이 쓰기는 대기 (GC 먼저)</text><line x1="250" y1="178" x2="250" y2="192" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aalloc)"/><rect x="15" y="192" width="470" height="62" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="250.0" y="213.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">③ allocate_page_in_plane_for_user_write</text><text x="250.0" y="232.0" font-size="10.5" fill="#4d5656" text-anchor="middle">옛 PPA 가 있으면 invalid 로 표시</text><text x="250.0" y="246.5" font-size="10.5" fill="#4d5656" text-anchor="middle">:1146</text><line x1="250" y1="254" x2="250" y2="268" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aalloc)"/><rect x="15" y="268" width="470" height="62" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="250.0" y="289.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">④ Allocate_block_and_page_in_plane_for_user_write</text><text x="250.0" y="308.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Data_wf 의 다음 빈 page 를 받는다</text><text x="250.0" y="322.5" font-size="10.5" fill="#4d5656" text-anchor="middle">frontier 가 차면 새 block + GC 검사</text><line x1="250" y1="330" x2="250" y2="344" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aalloc)"/><rect x="15" y="344" width="470" height="62" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="250.0" y="365.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">⑤ Update_mapping_info</text><text x="250.0" y="384.0" font-size="10.5" fill="#4d5656" text-anchor="middle">LPA → 새 PPA 로 매핑 갱신</text><text x="250.0" y="398.5" font-size="10.5" fill="#4d5656" text-anchor="middle">Physical_address_determined = true</text><text x="670" y="62" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 전 (Data_wf block)</text><rect x="540" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="572" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="604" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="636" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="668" y="70" width="30" height="30" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="700" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="732" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="764" y="70" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="540" y="102" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="572" y="102" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="604" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="636" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="668" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="700" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="732" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="764" y="102" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><text x="670" y="182" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 후: 새 page(노랑) 에 씀</text><rect x="540" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="572" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="604" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="636" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="668" y="190" width="30" height="30" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="700" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="732" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="764" y="190" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="540" y="222" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="572" y="222" width="30" height="30" rx="3" fill="#e9f7ef" stroke="#1e8449" stroke-width="2"/><rect x="604" y="222" width="30" height="30" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="636" y="222" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="668" y="222" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="700" y="222" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="732" y="222" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><rect x="764" y="222" width="30" height="30" rx="3" fill="#f4f6f7" stroke="#bbb" stroke-width="2"/><text x="540" y="262" font-size="10.5" fill="#4d5656" text-anchor="start">이번 쓰기가 덮어쓴 LPA 의 옛 page 는 (다른 block 에서) invalid 가 된다</text><rect x="540" y="290" width="425" height="110" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="752.5" y="328.25" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">범례와 요점</text><text x="752.5" y="346.75" font-size="10.5" fill="#4d5656" text-anchor="middle">초록 valid · 빨강 invalid · 노랑 방금 쓴 page · 회색 free</text><text x="752.5" y="361.25" font-size="10.5" fill="#4d5656" text-anchor="middle">덮어쓰기는 같은 자리에 못 쓴다 (out-of-place update)</text><text x="752.5" y="375.75" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 옛 page 가 invalid 로 남아 GC 의 일감이 된다</text></svg>


<div style="margin-top: 60px;"></div>

## 1. plane 을 정한다 (`allocate_plane_for_user_write`, `:987`)

`Plane_Allocation_Scheme` 이 `CWDP` 이면 LPA 를 채널 → 칩 → 다이 → 플레인 순으로 돌려가며 나눈다.

```cpp
targetAddress.ChannelID = domain->Channel_ids[lpn % domain->Channel_no];
targetAddress.ChipID    = domain->Chip_ids[(lpn / domain->Channel_no) % domain->Chip_no];
targetAddress.DieID     = domain->Die_ids[(lpn / (Chip_no * Channel_no)) % Die_no];
targetAddress.PlaneID   = domain->Plane_ids[(lpn / (Die_no * Chip_no * Channel_no)) % Plane_no];
```

연속된 LPA 가 서로 다른 채널로 흩어져 병렬로 쓰인다([플래시 구조와 주소 체계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-and-addresses/)). **같은 LPA 는 항상 같은 plane** 에 간다 — 덮어써도 plane 은 바뀌지 않는다.

## 2. 이 plane 에 쓸 여유가 있나

```cpp
if (ftl->GC_and_WL_Unit->Stop_servicing_writes(transaction->Address))
    return false;       // 이 쓰기는 지금 처리하지 않는다
```

plane 의 free block 이 GC 몫으로만 남았으면 쓰기를 **멈추고** 기다리게 한다(`GC_and_WL_Unit_Base.cpp:216`). 이때 transaction 은 `Write_transactions_for_overfull_planes` 에 들어가고(`mange_unsuccessful_translation`, `:1909`), GC 의 erase 가 끝나 공간이 생기면 `Start_servicing_writes_for_overfull_plane()` (`:1915`) 이 다시 `translate_lpa_to_ppa()` 를 불러 풀어 준다. 장치가 가득 차면 쓰기가 영원히 대기할 수도 있다.


<div style="margin-top: 60px;"></div>

## 3. 옛 page 를 무효로, 새 page 를 받고, 매핑을 바꾼다 (`allocate_page_in_plane_for_user_write`, `:1146`)

```cpp
PPA_type old_ppa = domain->Get_ppa(ideal_mapping_table, stream, LPA);
if (old_ppa != NO_PPA) {                       // 덮어쓰기
    ...
    block_manager->Invalidate_page_in_block(stream, addr(old_ppa));    // 옛 page → invalid
}
// ↓ 반드시 invalidate 뒤에 (아래 주석 참고)
block_manager->Allocate_block_and_page_in_plane_for_user_write(stream, transaction->Address);
transaction->PPA = Convert_address_to_ppa(transaction->Address);
domain->Update_mapping_info(..., LPA, transaction->PPA, bitmap);       // 매핑 갱신
```

핵심 세 줄이 **out-of-place update 의 전부**다.

1. 옛 PPA 가 있으면 그 page 를 **invalid** 로 표시한다. (지우지 않는다 — 지우는 건 block 단위다.)
2. 블록 매니저에게 새 page 를 받는다.
3. 매핑을 새 PPA 로 바꾼다.

원본의 주석이 순서의 이유를 말해 준다. *"invalidate 호출과 순서를 바꾸면 안 된다. 그러면 Allocate_block… 에서 GC 가 시작되어 방금 invalid 처리한 page 를 옮기려 할 수 있다."*

### partial write — "update read"

transaction 의 bitmap 이 옛 page 의 sector 를 **전부 덮지 못하면**(예: page 의 절반만 쓰는 4 KB 쓰기), 안 덮인 sector 를 읽어 새 page 에 합쳐야 한다. 이때 FTL 이 `NVM_Transaction_Flash_RD`(update read)를 하나 더 만들어 `RelatedRead` 에 붙인다. **쓰기 하나가 읽기 하나를 더 낳는 경우**이다. 캐시가 같은 page 의 조각들을 모아 보내면 이 읽기를 피할 수 있다.


<div style="margin-top: 60px;"></div>

## 4. 블록 매니저가 page 를 내준다 (`Flash_Block_Manager.cpp:20`)

```cpp
plane_record->Valid_pages_count++;   plane_record->Free_pages_count--;
page_address.BlockID = plane_record->Data_wf[stream_id]->BlockID;
page_address.PageID  = plane_record->Data_wf[stream_id]->Current_page_write_index++;
program_transaction_issued(page_address);

if (Data_wf[stream_id]->Current_page_write_index == pages_no_per_block) {   // frontier 가 가득 참
    plane_record->Data_wf[stream_id] = plane_record->Get_a_free_block(stream_id, false);
    gc_and_wl_unit->Check_gc_required(plane_record->Get_free_block_pool_size(), page_address);
}
```

- 그 plane 의 **write frontier block**(`Data_wf`)에서 **다음 빈 page** 를 받는다. page 는 항상 block 의 앞에서부터 순서대로 쓰인다.
- frontier block 이 **가득 차는 순간** 새 free block 을 받아 frontier 를 교체하고, **그때만** `Check_gc_required()` 를 부른다. GC 는 매 쓰기마다 검사되지 않는다.
- `Get_a_free_block()` 은 free pool 의 `begin()` — erase 횟수가 가장 적은 block — 을 뽑는다. 이것이 dynamic wear leveling 이다([10단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/)).

write frontier 는 **stream 별로** 있고, 사용자 쓰기(`Data_wf`)와 GC 쓰기(`GC_wf`)가 서로 다른 block 에 쌓인다.

## 확인해 보기

1. 같은 LPA 에 세 번 쓰면 invalid page 는 몇 개 생기나? 어느 block 들에?
2. 쓰기가 계속되는데 `Check_gc_required` 가 한 번도 안 불릴 수 있나? (frontier 가 안 차면?)
3. 4 KB 쓰기가 8 KB page 에 처음 쓰이는 경우(`old_ppa == NO_PPA`)에도 update read 가 생기나?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 6. FTL ① 주소 변환](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)</span><span>[8. FTL ③ 스케줄러와 플래시 칩 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/)</span></div>
