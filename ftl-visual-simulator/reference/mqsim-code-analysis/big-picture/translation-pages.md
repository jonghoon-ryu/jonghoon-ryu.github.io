---
layout: default
title: 매핑 테이블은 어디에 저장되나 — translation page
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/translation-pages/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 매핑 테이블은 어디에 저장되나 — translation page

[FTL 의 부품들](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/)에서 매핑 테이블이 CMT · GMT · GTD 세 겹이라고 했다. 여기서는 **전체 매핑(GMT)을 flash 에 어떻게 두고, CMT 와 어떻게 주고받는지**를 숫자와 함께 본다(`ssd/Address_Mapping_Unit_Page_Level.cpp` 의 `request_mapping_entry` · `generate_flash_*_for_mapping_data` · `handle_transaction_serviced_signal_from_PHY`).


<div style="margin-top: 60px;"></div>

## 1. 크기부터

<svg viewBox="0 0 980 330" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="매핑 테이블 크기"><defs><marker id="asizes" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asizess" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">항목 크기와 개수 (AMU 생성자, Address_Mapping_Unit_Page_Level.cpp:327)</text><rect x="15" y="45" width="300" height="130" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="165.0" y="86.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CMT 항목</text><text x="165.0" y="104.75" font-size="10.5" fill="#4d5656" text-anchor="middle">(LPA, PPA, sector bitmap)</text><text x="165.0" y="119.25" font-size="10.5" fill="#4d5656" text-anchor="middle">= ceil((2·log2(물리 page 수) + sector 수) ÷ 8) byte</text><text x="165.0" y="133.75" font-size="10.5" fill="#4d5656" text-anchor="middle">기본 설정: ceil((2·26 + 16) ÷ 8) = 9 byte</text><text x="165.0" y="148.25" font-size="10.5" fill="#4d5656" text-anchor="middle">CMT 2 MiB → 약 233,016 항목</text><rect x="340" y="45" width="300" height="130" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="86.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">GTD / translation page 항목</text><text x="490.0" y="104.75" font-size="10.5" fill="#4d5656" text-anchor="middle">(PPA, sector bitmap) — LPA 는 위치로 안다</text><text x="490.0" y="119.25" font-size="10.5" fill="#4d5656" text-anchor="middle">= ceil((log2(물리 page 수) + sector 수) ÷ 8) byte</text><text x="490.0" y="133.75" font-size="10.5" fill="#4d5656" text-anchor="middle">기본 설정: ceil((26 + 16) ÷ 8) = 6 byte</text><text x="490.0" y="148.25" font-size="10.5" fill="#4d5656" text-anchor="middle">page(8 KB) 하나에 1,365 항목</text><rect x="665" y="45" width="300" height="130" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="815.0" y="86.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">규모</text><text x="815.0" y="104.75" font-size="10.5" fill="#4d5656" text-anchor="middle">물리 page ≈ 67,108,864 (2²⁶)</text><text x="815.0" y="119.25" font-size="10.5" fill="#4d5656" text-anchor="middle">논리 page ≈ 62,411,243 (OP 7%)</text><text x="815.0" y="133.75" font-size="10.5" fill="#4d5656" text-anchor="middle">translation page ≈ 45,722 개</text><text x="815.0" y="148.25" font-size="10.5" fill="#4d5656" text-anchor="middle">(물리 page 의 약 0.07%)</text><rect x="15" y="195" width="950" height="120" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="231.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">CMT 가 담는 비율</text><text x="490.0" y="249.5" font-size="10.5" fill="#4d5656" text-anchor="middle">CMT 233,016 항목 ÷ 논리 page 62,411,243 ≈ 0.37%</text><text x="490.0" y="264.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 작업 영역이 크고 접근이 무작위이면 거의 매번 CMT miss → 매핑 page 읽기가 데이터 읽기·쓰기만큼 늘어난다</text><text x="490.0" y="278.5" font-size="10.5" fill="#4d5656" text-anchor="middle">(샘플 시나리오 1 의 결과 XML: CMT_Queries 370,966 에 대해 Issued_Flash_Read_CMD_For_Mapping 이 따로 집계됨)</text><text x="490.0" y="293.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Working_Set_Percentage 를 줄이거나 CMT_Capacity 를 키우거나 Ideal_Mapping_Table=true 로 이 효과를 없앨 수 있다</text></svg>


<div style="margin-top: 60px;"></div>

## 2. 시작할 때 이미 채워 둔다

시뮬레이션이 시작되면 `Store_mapping_table_on_flash_at_start()` (`:423`)가 **모든 translation page 의 자리를 정해서 flash 에 "사용 중" 으로 표시**한다. stream 마다 translation page 개수만큼 `allocate_plane_for_translation_write` + `allocate_page_in_plane_for_translation_write` 를 부른다. 그래서 요청이 하나도 오기 전에 flash 의 약 0.07% 가 이미 차 있다.

translation page 는 일반 데이터와 **다른 block**(`Translation_wf`)에 쌓인다. 그 block 들은 `Holds_mapping_data` 가 참이고, GC 가 이들을 옮길 때는 LPA 대신 MVPN 으로 잠그고(`Locked_MVPNs`) 매핑 page 전용 경로(`Get_translation_mapping_info_for_gc`)로 처리한다.


<div style="margin-top: 60px;"></div>

## 3. 읽기 — CMT miss 가 만드는 일

[튜토리얼 6단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)의 네 가지 경우를 기억하자. 마지막 경우, 즉 매핑 page 를 flash 에서 읽을 때:

1. `generate_flash_read_request_for_mapping_data()` (`:1630`)가 GTD 로 그 MVPN 의 MPPN 을 찾아 **소스 `MAPPING` 인 read** 를 TSU 에 낸다 (`Total_flash_reads_for_mapping++`).
2. TSU 는 매핑 read 를 **최우선**으로 서비스한다([TSU 스케줄러 정책](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/tsu-policies/)).
3. read 가 끝나면 AMU 가 `ArrivingMappingEntries` 에서 같은 MVPN 을 기다리던 항목들을 CMT 에 넣는다. 시뮬레이터는 매핑 page 의 **내용**을 따로 저장하지 않으므로, 값은 GMT 배열에서 복사한다(원본 주석의 "Hack").
4. 기다리던 `Waiting_unmapped_read/program_transactions` 를 다시 `translate_lpa_to_ppa()` 로 보낸다. 그 LPA 가 GC 에 잠겨 있으면 barrier 로 간다.


<div style="margin-top: 60px;"></div>

## 4. 쓰기 — 쫓겨남과 translation page 재기록

<svg viewBox="0 0 980 440" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="CMT 쫓아내기"><defs><marker id="aevict" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aevicts" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">CMT 에서 쫓겨난 dirty 항목은 translation page 전체를 다시 쓴다</text><rect x="15" y="45" width="330" height="55" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="180.0" y="70.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">① CMT 가 가득 찼다</text><text x="180.0" y="88.25" font-size="10" fill="#4d5656" text-anchor="middle">Evict_one_slot (LRU)</text><line x1="180" y1="100" x2="180" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aevict)"/><rect x="15" y="110" width="330" height="55" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="180.0" y="135.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">② 쫓겨난 항목이 dirty</text><text x="180.0" y="153.25" font-size="10" fill="#4d5656" text-anchor="middle">→ GMT 에 즉시 반영 (경쟁 방지)</text><line x1="180" y1="165" x2="180" y2="175" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aevict)"/><rect x="15" y="175" width="330" height="55" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="180.0" y="200.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">③ 같은 MVPN 의 CMT 항목을 훑는다</text><text x="180.0" y="218.25" font-size="10" fill="#4d5656" text-anchor="middle">dirty 는 clean 으로, 안 바뀐 항목은 &quot;읽어야 할 sector&quot; 로 표시</text><line x1="180" y1="230" x2="180" y2="240" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aevict)"/><rect x="15" y="240" width="330" height="55" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="180.0" y="265.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">④ 안 바뀐 부분을 flash 에서 읽는다</text><text x="180.0" y="283.25" font-size="10" fill="#4d5656" text-anchor="middle">update read (소스 MAPPING)</text><line x1="180" y1="295" x2="180" y2="305" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aevict)"/><rect x="15" y="305" width="330" height="55" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="180.0" y="330.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">⑤ 합친 page 를 새 자리에 쓴다</text><text x="180.0" y="348.25" font-size="10" fill="#4d5656" text-anchor="middle">Translation_wf block, MPPN 갱신</text><line x1="180" y1="360" x2="180" y2="370" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aevict)"/><rect x="15" y="370" width="330" height="55" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="180.0" y="395.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">⑥ 옛 translation page 는 invalid</text><text x="180.0" y="413.25" font-size="10" fill="#4d5656" text-anchor="middle">→ 일반 page 와 똑같이 GC 대상</text><rect x="380" y="45" width="585" height="190" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="672.5" y="101.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">그동안 같은 MVPN 을 다시 찾는 요청은</text><text x="672.5" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">DepartingMappingEntries(쓰는 중) 에 MVPN 을 올려 둔다</text><text x="672.5" y="134.5" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 다른 요청이 그 항목이 필요하면 flash 를 읽지 않고</text><text x="672.5" y="149.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   GMT 값을 복사해서 CMT 에 넣는다 (&quot;메모리에 있다고 가정&quot; — 원본 주석)</text><text x="672.5" y="163.5" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="672.5" y="178.0" font-size="10.5" fill="#4d5656" text-anchor="middle">ArrivingMappingEntries(읽는 중) 는 같은 매핑 page 읽기를 중복해서</text><text x="672.5" y="192.5" font-size="10.5" fill="#4d5656" text-anchor="middle">만들지 않게 한다. 읽기가 끝나면 기다리던 항목들이 한꺼번에 CMT 로</text><rect x="380" y="255" width="585" height="180" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="672.5" y="306.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">비용을 보면</text><text x="672.5" y="325.0" font-size="10.5" fill="#4d5656" text-anchor="middle">쓰기 하나가 CMT miss 를 만들면 최악의 경우</text><text x="672.5" y="339.5" font-size="10.5" fill="#4d5656" text-anchor="middle">  · 매핑 page read (miss 해결)</text><text x="672.5" y="354.0" font-size="10.5" fill="#4d5656" text-anchor="middle">  · 쫓겨난 항목의 translation page read + write (evict)</text><text x="672.5" y="368.5" font-size="10.5" fill="#4d5656" text-anchor="middle">  · 그리고 데이터 page 의 program</text><text x="672.5" y="383.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 매핑 때문에 flash 접근이 데이터 접근의 몇 배가 될 수 있다</text><text x="672.5" y="397.5" font-size="10.5" fill="#4d5656" text-anchor="middle">이 쓰기·읽기 횟수는 Stats 의 Total_flash_{reads,writes}_for_mapping 에 집계된다</text></svg>


<div style="margin-top: 60px;"></div>

## 5. 매핑이 만든 flash 쓰기는 WAF 에 안 들어간다

호스트 쓰기 대비 flash 쓰기(WAF)를 셀 때 translation page 쓰기는 별도로 `Total_flash_writes_for_mapping` 에 집계된다. **이 프로젝트의 시뮬레이터는 매핑 쓰기를 세지 않는다** — SSD 가 작아서(논리 page 가 수백 개) 기본 CMT(2 MiB, 약 23만 항목)에 매핑 테이블 전체가 들어가므로 쫓겨나는 항목이 없고, 그래서 매핑 page 쓰기가 0 이기 때문이다(`Issued_Flash_Program_CMD_For_Mapping` = 0).


<div style="margin-top: 60px;"></div>

## 관련 문서

- [FTL 의 부품들과 자료구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) · [튜토리얼 6단계 — 주소 변환](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)
- [GC 와 사용자 I/O 의 경쟁 방지](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concurrency-control/) · [결과 파일과 통계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/statistics/)
