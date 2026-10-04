---
layout: default
title: 6. FTL ① 주소 변환
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 6. FTL ① 주소 변환

FTL 의 첫 일은 **"이 LPA 는 지금 어디에 있는가?"** 를 묻는 것이다. 이 질문의 답이 매핑 테이블에 있고, 그 테이블의 일부만 DRAM(CMT)에 있다.


<div style="margin-top: 60px;"></div>

## 1. Translate_lpa_to_ppa_and_dispatch (`:480`)

```cpp
for (각 transaction) {
    if (is_lpa_locked_for_gc(stream, LPA))
        manage_user_transaction_facing_barrier(...);    // GC 가 옮기는 중이면 기다린다
    else
        query_cmt(...);                                  // 정상 경로
}
TSU->Prepare_for_transaction_submit();
for (각 transaction)
    if (Physical_address_determined)                     // 물리 주소가 정해진 것만
        TSU->Submit_transaction(...);
TSU->Schedule();
```

두 가지를 봐 두자.

- **GC 중인 LPA 는 기다린다.** GC 가 어떤 page 를 옮기는 동안 그 LPA 는 잠긴다(`Locked_LPAs`). 이때 같은 LPA 로 사용자 요청이 오면 barrier 에 걸려 대기한다. 옮기는 도중에 매핑이 바뀌면 안 되기 때문이다.
- **물리 주소가 아직 정해지지 않은 transaction 은 TSU 로 가지 않는다.** CMT miss 로 기다리는 것들이 이에 해당한다.


<div style="margin-top: 60px;"></div>

## 2. query_cmt — 매핑이 CMT 에 있는가 (`:510`)

<svg viewBox="0 0 980 400" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="CMT 조회의 갈림길"><defs><marker id="acmt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="acmts" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">query_cmt (Address_Mapping_Unit_Page_Level.cpp:510)</text><rect x="15" y="160" width="150" height="70" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="90.0" y="193.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">transaction</text><text x="90.0" y="212.0" font-size="11" fill="#4d5656" text-anchor="middle">LPA 하나</text><rect x="215" y="150" width="190" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="310.0" y="185.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Mapping_entry_accessible?</text><text x="310.0" y="204.5" font-size="11" fill="#4d5656" text-anchor="middle">CMT 에 이 LPA 의</text><text x="310.0" y="219.5" font-size="11" fill="#4d5656" text-anchor="middle">항목이 있는가</text><rect x="470" y="30" width="220" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="580.0" y="65.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">HIT</text><text x="580.0" y="84.5" font-size="11" fill="#4d5656" text-anchor="middle">translate_lpa_to_ppa()</text><text x="580.0" y="99.5" font-size="11" fill="#4d5656" text-anchor="middle">바로 PPA 확정</text><rect x="470" y="150" width="220" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="580.0" y="185.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">MISS → request_mapping_entry()</text><text x="580.0" y="204.5" font-size="11" fill="#4d5656" text-anchor="middle">매핑 확보 방법을 찾는다 (아래 4가지)</text><text x="580.0" y="219.5" font-size="11" fill="#4d5656" text-anchor="middle">true: 바로 변환 · false: 대기</text><rect x="470" y="290" width="220" height="90" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="580.0" y="325.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">확보 못 함</text><text x="580.0" y="344.5" font-size="11" fill="#4d5656" text-anchor="middle">Waiting_unmapped_*_transactions</text><text x="580.0" y="359.5" font-size="11" fill="#4d5656" text-anchor="middle">에 넣고 기다린다</text><line x1="165" y1="195" x2="215" y2="195" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmt)"/><line x1="405" y1="175" x2="470" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmt)"/><text x="425" y="115" font-size="10.5" fill="#566573" text-anchor="middle">yes</text><line x1="405" y1="205" x2="470" y2="195" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmt)"/><text x="435" y="190" font-size="10.5" fill="#566573" text-anchor="middle">no</text><line x1="580" y1="240" x2="580" y2="290" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmt)"/><text x="610" y="268" font-size="10.5" fill="#566573" text-anchor="middle">false</text><rect x="740" y="20" width="225" height="360" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="852.5" y="96.5" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">request_mapping_entry 의 4가지</text><text x="852.5" y="115.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="852.5" y="129.5" font-size="10.5" fill="#4d5656" text-anchor="middle">① 이 LPA 를 처음 쓴다</text><text x="852.5" y="144.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   → 매핑 page 도 없음</text><text x="852.5" y="158.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   → CMT 에 빈 항목만 만든다</text><text x="852.5" y="173.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   (flash read 없음)</text><text x="852.5" y="187.5" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="852.5" y="202.0" font-size="10.5" fill="#4d5656" text-anchor="middle">② 같은 매핑 page 를 이미</text><text x="852.5" y="216.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   읽는 중 → 슬롯만 예약, 대기</text><text x="852.5" y="231.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="852.5" y="245.5" font-size="10.5" fill="#4d5656" text-anchor="middle">③ 쫓겨나 쓰이는 중인 page</text><text x="852.5" y="260.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   → 메모리에 있다고 보고</text><text x="852.5" y="274.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   GMT 값을 복사</text><text x="852.5" y="289.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="852.5" y="303.5" font-size="10.5" fill="#4d5656" text-anchor="middle">④ 그 외 → translation page 를</text><text x="852.5" y="318.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   flash 에서 읽는다 (매핑 read)</text><line x1="690" y1="195" x2="740" y2="195" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmt)"/></svg>

CMT hit 이면 `translate_lpa_to_ppa()` 로 곧바로 간다. miss 이면 `request_mapping_entry()` (`:1457`) 가 **매핑을 확보할 방법**을 네 가지 중에서 고른다.

1. **이 LPA 를 처음 쓰는 경우** — 매핑 page 조차 없으므로 CMT 에 빈 항목(`PPA = NO_PPA`)만 만든다. **flash read 가 없다.** CMT 가 가득 차 있으면 먼저 하나 쫓아내고, 쫓겨난 항목이 dirty 면 translation page 쓰기를 만든다.
2. **같은 매핑 page 를 읽는 중인 경우**(`ArrivingMappingEntries`) — 그 읽기가 끝나기를 기다린다. 읽기를 중복해서 만들지 않는다.
3. **방금 쫓겨나 flash 에 쓰는 중인 page**(`DepartingMappingEntries`) — 아직 메모리에 있다고 보고 GMT 값을 복사한다.
4. **그 외** — `generate_flash_read_request_for_mapping_data()` (`:1630`) 가 GTD 로 translation page 의 위치(MPPN)를 찾아 **소스 `MAPPING` 인 flash read** 를 만든다.

4번이 "CMT miss 는 실제 flash 접근" 의 정체다. 이 read 가 끝나면 `handle_transaction_serviced_signal_from_PHY()` (`:1665`)가 불려 항목을 CMT 에 채우고, 기다리던 transaction 들을 다시 `translate_lpa_to_ppa()` 로 보낸다.


<div style="margin-top: 60px;"></div>

## 3. translate_lpa_to_ppa — 읽기는 여기서 끝난다 (`:584`)

```cpp
PPA_type ppa = domains[streamID]->Get_ppa(ideal_mapping_table, streamID, transaction->LPA);

if (transaction->Type == Transaction_Type::READ) {
    if (ppa == NO_PPA)                                   // 한 번도 쓴 적 없는 LPA
        ppa = online_create_entry_for_reads(...);        // (원본) 그 자리에서 page 예약
    transaction->PPA = ppa;
    Convert_ppa_to_address(transaction->PPA, transaction->Address);   // 숫자 → 채널·칩·…
    block_manager->Read_transaction_issued(transaction->Address);
    transaction->Physical_address_determined = true;
    return true;
} else { ... }   // 쓰기 → 7단계
```

읽기는 **매핑이 알려 준 PPA 를 물리 좌표로 바꾸기만** 하면 끝이다. `Read_transaction_issued()` 는 그 block 에 "읽기가 진행 중" 이라고 장부에 적어, 그 block 이 지금 GC 로 지워지지 않게 한다. 쓰기는 같은 함수의 `else` 쪽으로 가서 새 page 를 정한다.

> 쓴 적 없는 LPA 를 읽을 때 `online_create_entry_for_reads` 가 물리 page 를 예약하는 이유와 이 프로젝트의 대응은 [쓰기 전에 읽으면 페이지가 소비되는 이유](/ftl-visual-simulator/reference/mqsim-code-analysis/read-before-write/)에 있다.

## 확인해 보기

1. CMT 용량을 아주 작게 하면 어떤 통계가 늘어나나? (`Stats::CMT_miss`, `Total_flash_reads_for_mapping`)
2. 읽기 transaction 이 `Waiting_unmapped_read_transactions` 에서 풀려나는 곳은 어디인가? (`:1665`)
3. `Ideal_Mapping_Table` 을 true 로 하면 `query_cmt` 의 어느 분기가 사라지나?

<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 5. 데이터 캐시 — FTL 의 문턱](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step5-cache/)</span><span>[7. FTL ② 쓰기와 page 할당 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/)</span></div>
