---
layout: default
title: GC 와 사용자 I/O 의 경쟁 방지
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concurrency-control/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# GC 와 사용자 I/O 의 경쟁 방지

FTL 코드를 읽다 보면 `barrier`, `Locked_LPAs`, `Ongoing_user_program_count` 같은 이름이 계속 나온다. 이것들은 모두 한 문제를 푼다 — **GC 는 한 page 를 옮기는 데 read → write 로 수십~수백 µs 가 걸리는데, 그 사이 호스트가 같은 데이터를 읽거나 덮어쓰면 어떻게 하나?**


<div style="margin-top: 60px;"></div>

## 1. 문제 장면

<svg viewBox="0 0 980 420" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="GC 와 사용자 I/O 의 경쟁"><defs><marker id="arace" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="araces" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC 가 도는 동안 사용자 I/O 가 같은 데이터를 건드리면</text><line x1="60" y1="120" x2="940" y2="120" stroke="#bbb" stroke-width="1.5"/><text x="60" y="100" font-size="11" fill="#7f8c8d" text-anchor="start">시간 →</text><rect x="70" y="130" width="110" height="30" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="125" y="150" font-size="10.5" fill="#2c3e50" text-anchor="middle">victim 선정</text><rect x="180" y="130" width="110" height="30" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="235" y="150" font-size="10" fill="#2c3e50" text-anchor="middle">유효 LPA 전부 잠금</text><rect x="290" y="130" width="330" height="30" rx="3" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="455" y="150" font-size="10.5" fill="#2c3e50" text-anchor="middle">page 하나씩: read → (LPA 재확인) → write → LPA 잠금 해제</text><rect x="620" y="130" width="150" height="30" rx="3" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="695" y="150" font-size="10.5" fill="#2c3e50" text-anchor="middle">이동 다 끝나면 erase</text><rect x="770" y="130" width="100" height="30" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="820" y="150" font-size="10.5" fill="#2c3e50" text-anchor="middle">free pool 로</text><line x1="390" y1="60" x2="390" y2="128" stroke="#7f8c8d" stroke-width="2" marker-end="url(#arace)"/><text x="520" y="70" font-size="10.5" fill="#566573" text-anchor="middle">사용자 read/write 도착 (LPA 가 잠겨 있음)</text><rect x="130" y="200" width="330" height="85" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="295.0" y="233.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">barrier 에 걸린다</text><text x="295.0" y="252.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Read_/Write_transactions_behind_LPA_barrier 에 보관</text><text x="295.0" y="266.5" font-size="10.5" fill="#4d5656" text-anchor="middle">(매핑·TSU 로 가지 않고 기다린다)</text><rect x="500" y="200" width="460" height="85" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="730.0" y="226.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">잠금이 풀리는 순간</text><text x="730.0" y="244.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Remove_barrier_for_accessing_lpa — 기다리던 read/write 를</text><text x="730.0" y="259.25" font-size="10.5" fill="#4d5656" text-anchor="middle">&quot;GC 가 접근한 실제 page 데이터로 서비스할 수 있다고 가정&quot; 하고</text><text x="730.0" y="273.75" font-size="10.5" fill="#4d5656" text-anchor="middle">즉시 완료 처리한다 (handle_transaction_serviced_signal_from_PHY 직접 호출)</text><line x1="460" y1="242" x2="500" y2="242" stroke="#7f8c8d" stroke-width="2" marker-end="url(#arace)"/><rect x="15" y="310" width="470" height="95" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="250.0" y="341.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">왜 LPA 를 전부 잠그나</text><text x="250.0" y="359.75" font-size="10.5" fill="#4d5656" text-anchor="middle">block 안 page 의 LPA 는 flash 에서 하나씩 읽어야 알 수 있지만</text><text x="250.0" y="374.25" font-size="10.5" fill="#4d5656" text-anchor="middle">구현을 단순하게 하려고 LPA 목록을 DRAM 에 있다고 가정하고</text><text x="250.0" y="388.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Set_barrier_for_accessing_physical_block 이 시작 시점에 한꺼번에 잠근다</text><rect x="495" y="310" width="470" height="95" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="730.0" y="341.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">이 단순화의 결과</text><text x="730.0" y="359.75" font-size="10.5" fill="#4d5656" text-anchor="middle">barrier 뒤의 쓰기는 flash 에 쓰이지 않고 &quot;완료&quot; 로 처리된다</text><text x="730.0" y="374.25" font-size="10.5" fill="#4d5656" text-anchor="middle">(원본 주석에 명시된 가정 — 데모 규모에서는 이것이 캐시로 가는 길을</text><text x="730.0" y="388.75" font-size="10.5" fill="#4d5656" text-anchor="middle">끊어 먹던 버그의 원인이 되기도 했다 → Code Change 참고)</text></svg>


<div style="margin-top: 60px;"></div>

## 2. 보호 장치 다섯 겹

<svg viewBox="0 0 980 400" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="다섯 겹의 보호"><defs><marker id="alayers" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="alayerss" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">충돌을 막는 장치 다섯 겹</text><rect x="15" y="45" width="300" height="62" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="165.0" y="74.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">① block 의 진행 중 I/O 카운트</text><text x="165.0" y="92.0" font-size="10" fill="#4d5656" text-anchor="middle">Ongoing_user_read_count · Ongoing_user_program_count</text><rect x="330" y="45" width="635" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="647.5" y="80.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">둘 다 0 이어야 GC 가 시작될 수 있다 (Can_execute_gc_wl). 아니면 보류했다가 사용자 I/O 가 끝나는 신호에서 재개</text><rect x="15" y="115" width="300" height="62" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="165.0" y="144.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">② GC 중 표시</text><text x="165.0" y="162.0" font-size="10" fill="#4d5656" text-anchor="middle">Has_ongoing_gc_wl · Ongoing_erase_operations</text><rect x="330" y="115" width="635" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="647.5" y="150.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 block 에 GC 가 두 번 걸리지 않게 한다. victim 후보에서 제외 (is_safe_gc_wl_candidate)</text><rect x="15" y="185" width="300" height="62" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="165.0" y="214.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">③ LPA / MVPN barrier</text><text x="165.0" y="232.0" font-size="10" fill="#4d5656" text-anchor="middle">Locked_LPAs · Locked_MVPNs</text><rect x="330" y="185" width="635" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="647.5" y="220.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">옮기는 중인 page 의 논리 주소를 잠가 사용자 요청을 줄 세운다</text><rect x="15" y="255" width="300" height="62" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="165.0" y="284.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">④ GC read 완료 시 재확인</text><text x="165.0" y="302.0" font-size="10" fill="#4d5656" text-anchor="middle">Get_data_mapping_info_for_gc</text><rect x="330" y="255" width="635" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="647.5" y="290.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">읽는 사이 그 LPA 가 덮어쓰이지 않았는지 현재 PPA 와 비교, 다르면 &quot;Inconsistency&quot; 오류</text><rect x="15" y="325" width="300" height="62" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="165.0" y="354.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">⑤ plane 가득 참 보호</text><text x="165.0" y="372.0" font-size="10" fill="#4d5656" text-anchor="middle">Stop_servicing_writes · Write_transactions_for_overfull_planes</text><rect x="330" y="325" width="635" height="62" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="647.5" y="360.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">free block 이 GC 몫만 남으면 사용자 쓰기를 멈추고 대기. erase 후 재개</text></svg>

### ① 진행 중 I/O 카운트로 시작을 늦춘다

사용자 읽기가 transaction 으로 나갈 때(`Read_transaction_issued`)와 쓰기 page 가 할당될 때(`program_transaction_issued`) 그 block 의 카운트가 오르고, flash 가 끝내면(`Read_/Program_transaction_serviced`) 내린다(`Flash_Block_Manager_Base.cpp:183`~). GC 는 victim 을 고른 뒤 `Can_execute_gc_wl()` 로 두 카운트의 합이 0 인지 본다. 아니면 **지금은 시작하지 않고**, 그 block 의 사용자 I/O 가 끝나는 신호(`GC_and_WL_Unit_Base::handle_transaction_serviced_signal_from_PHY` 의 `USERIO` 분기)에서 조건이 풀리면 이동 transaction 을 만들어 시작한다. [튜토리얼 9단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/)의 "사용자 I/O 가 진행 중이면 지금은 시작하지 않는다"가 이것이다.

### ② GC 중임을 표시한다

`GC_WL_started()` 가 `Has_ongoing_gc_wl = true` 를 세우고 `Ongoing_erase_operations` 집합에 block 번호를 넣는다. 한 plane 의 동시 GC 개수는 `max_ongoing_gc_reqs_per_plane` 이 제한한다(이 프로젝트의 [튜닝된 코드](/ftl-visual-simulator/reference/code-change/tweaked-code/)가 이 상수다).

> **선언만 있고 쓰이지 않는 상태 기계.** `Block_Pool_Slot_Type::Current_status` 와 `enum Block_Service_Status {IDLE, GC_WL, USER, GC_USER, GC_UWAIT, GC_USER_UWAIT}` 는 헤더에 있지만 초기화 이후 **갱신되지 않는다**. 실제 방지는 위 카운트와 `Has_ongoing_gc_wl` 플래그가 한다.

### ③ 논리 주소를 잠근다 (barrier)

`Set_barrier_for_accessing_physical_block()` 이 victim 의 **유효 page 전부**의 LPA(매핑 page 라면 MVPN)를 `Locked_LPAs` 에 넣는다. 이후 `Translate_lpa_to_ppa_and_dispatch()` 가 잠긴 LPA 의 transaction 을 보면 `manage_user_transaction_facing_barrier()` 로 보관한다. 그 LPA 의 이동 쓰기가 끝나면 `Remove_barrier_for_accessing_lpa()` 가 잠금을 풀고, 기다리던 transaction 들을 **flash 에 가지 않고 곧바로 완료 처리**한다(원본 주석: "MQSim assumes they can be serviced with the actual page data that is accessed during GC execution").

### ④ 이동 직전에 다시 확인한다

GC 의 read 가 끝나면 FTL 은 그 LPA 의 **현재 PPA** 를 조회해 방금 읽은 PPA 와 같은지 본다. 같으면(그 사이 덮어쓰이지 않았으면) write 의 목적지를 `Allocate_new_page_for_gc()` 로 정하고 제출한다. 다르면 `PRINT_ERROR("Inconsistency found when moving a page for GC/WL!")` — 잠금이 제대로 작동했다면 일어나지 않아야 하는 일이다.

### ⑤ 공간이 모자라면 쓰기를 멈춘다

`Stop_servicing_writes()` 는 plane 의 free block 수가 `max_ongoing_gc_reqs_per_plane` 보다 적으면 true 를 돌려준다. 이때 사용자 쓰기는 `Write_transactions_for_overfull_planes` 에서 기다리고, GC 의 erase 가 끝나면 `Start_servicing_writes_for_overfull_plane()` 이 풀어 준다. GC 가 이동할 자리가 없어서 교착하는 것을 막는 안전장치다.


<div style="margin-top: 60px;"></div>

## 3. 이 프로젝트에서의 의미

- 이 장치들 사이의 **틈**이 이 프로젝트가 찾은 버그의 상당수였다: GC 가 자기가 방금 채운(아직 program 이 안 끝난) page 를 victim 으로 다시 고르는 경쟁 상태, barrier 에서 풀려난 쓰기가 캐시 매니저에 닿지 않던 문제, 대기 중이던 GC 가 erase 를 제출하지 않던 문제 등이다([버그 목록표](/ftl-visual-simulator/reference/code-change/bug-list/table/)).
- 시뮬레이터에서 GC 가 돌 때 격자의 "노랑(이동 중)" 과 "victim" 표시는 이 보호가 걸려 있는 구간이다.


<div style="margin-top: 60px;"></div>

## 관련 문서

- [튜토리얼 9단계 — 가비지 컬렉션](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/) · [FTL 의 부품들과 자료구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/)
- [GC 자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/code-change/bug-list/gc-self-victim-race-bug/)
