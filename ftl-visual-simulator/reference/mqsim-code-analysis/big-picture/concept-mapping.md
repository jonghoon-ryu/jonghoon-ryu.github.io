---
layout: default
title: FTL 개념 ↔ 파라미터·모듈 대응
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# FTL 개념 ↔ 파라미터·모듈 대응

FTL 책에 나오는 개념 하나하나가 `ssdconfig.xml` 의 어느 항목, 코드의 어느 클래스에 대응하는지를 정리한 표이다. "이 슬라이더를 올리면 어떤 코드가 달라지나?" 에 답하는 용도다. 값은 원본의 기본 `ssdconfig.xml` 이다.

<svg viewBox="0 0 980 300" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="FTL 개념과 코드의 대응"><defs><marker id="acmap" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="acmaps" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">FTL 개념 → 코드</text><rect x="15" y="50" width="185" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="107.5" y="83.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">주소 매핑</text><text x="107.5" y="101.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Address_Mapping_Unit</text><rect x="208" y="50" width="185" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="300.5" y="83.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Over-provisioning</text><text x="300.5" y="101.75" font-size="10.5" fill="#4d5656" text-anchor="middle">논리 용량 계산</text><rect x="401" y="50" width="185" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="493.5" y="83.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC</text><text x="493.5" y="101.75" font-size="10.5" fill="#4d5656" text-anchor="middle">GC_and_WL_Unit</text><rect x="594" y="50" width="185" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="686.5" y="83.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">마모 평준화</text><text x="686.5" y="101.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Block Manager + GC_and_WL</text><rect x="787" y="50" width="185" height="70" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="879.5" y="83.25" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 캐시</text><text x="879.5" y="101.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Data_Cache_Manager</text><rect x="15" y="160" width="945" height="50" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="487.5" y="190.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">자원 배치 · 스케줄링: Plane_Allocation_Scheme (AMU) · Transaction_Scheduling_Policy (TSU)</text><rect x="15" y="230" width="945" height="55" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="487.5" y="262.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">물리 타이밍: Flash_Parameter_Set (read/program/erase 지연) · 채널 수 · Flash_Chip</text><line x1="107" y1="120" x2="107" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/><line x1="300" y1="120" x2="300" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/><line x1="493" y1="120" x2="493" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/><line x1="686" y1="120" x2="686" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/><line x1="879" y1="120" x2="879" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/><line x1="490" y1="210" x2="490" y2="230" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acmap)"/></svg>


<div style="margin-top: 60px;"></div>

## 1. 주소 매핑

| 설정 | 값 | 의미 | 코드 |
|---|---|---|---|
| `Address_Mapping` | PAGE_LEVEL | page 하나하나를 따로 매핑 — 세밀하지만 테이블이 크다 | `Address_Mapping_Unit_Page_Level` |
| `Ideal_Mapping_Table` | false | true 면 테이블 전체가 DRAM 에 있다고 가정 → CMT miss 가 없다 | `ideal_mapping_table` |
| `CMT_Capacity` | 2 MiB | CMT 에 둘 수 있는 항목 수 — 작을수록 miss 가 잦다 | `Cached_Mapping_Table` |
| `CMT_Sharing_Mode` | SHARED | 여러 stream 이 CMT 를 나눠 쓰는 방식 | `AddressMappingDomain` |

CMT miss 는 translation page 읽기라는 **실제 flash read** 를 만든다([FTL 의 부품들](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/)).

## 2. Over-provisioning

| 설정 | 값 | 의미 | 코드 |
|---|---|---|---|
| `Overprovisioning_Ratio` | 0.07 | 물리 용량 중 호스트에 보이지 않는 여분 비율 | AMU 가 논리 주소 공간 크기를 계산할 때 쓴다 |

OP 가 작을수록 GC 가 더 자주, 더 많은 valid page 를 옮긴다 → WAF 가 오른다.

## 3. Garbage Collection

| 설정 | 값 | 의미 | 코드 |
|---|---|---|---|
| `GC_Exec_Threshold` | 0.05 | free block 수가 `threshold × Block_No_Per_Plane` **보다 작아지면** GC | `block_pool_gc_threshold` (최소 1) |
| `GC_Block_Selection_Policy` | RGA | victim 고르는 방법: GREEDY · RGA · RANDOM · RANDOM_P · RANDOM_PP · FIFO | `Check_gc_required()` 의 switch |
| `Use_Copyback_for_GC` | false | valid page 이동을 칩 안에서 바로 복사할지 | `use_copyback` |
| `Preemptible_GC_Enabled` | false | GC 가 사용자 요청에 양보할 수 있는지 | `GC_is_in_urgent_mode()` |
| `GC_Hard_Threshold` | 0.005 | 양보 불가가 되는 문턱 | 아래 참고 |

> **죽은 설정** — `Preemptible_GC_Enabled` 가 false 면 `GC_is_in_urgent_mode()` 가 첫 줄에서 곧바로 true 를 돌려준다(`GC_and_WL_Unit_Page_Level.cpp:26`). 그래서 기본 설정에서는 `GC_Hard_Threshold` 가 **읽히지도 않고**, GC 는 항상 "긴급 모드" 로 동작한다.

## 4. 마모 평준화

| 설정 | 값 | 의미 | 코드 |
|---|---|---|---|
| `Dynamic_Wearleveling_Enabled` | true | free pool 에서 **erase 횟수가 가장 적은 block** 을 새 write frontier 로 쓴다 | `Add_to_free_block_pool(…, consider_dynamic_wl)` · `Get_a_free_block` |
| `Static_Wearleveling_Enabled` | true | 거의 안 지워지는 block 의 cold 데이터를 강제로 옮긴다 | `check_static_wl_required()` · `run_static_wearleveling()` |
| `Static_Wearleveling_Threshold` | 100 | plane 안 erase 횟수 최대-최소 차이가 이 이상이면 발동 | `Get_min_max_erase_difference()` |
| `Block_PE_Cycles_Limit` | 10000 | **강제되지 않는다** — 통계 배열 크기를 정하는 데만 쓰이고, 이 횟수에 닿아도 block 을 퇴역시키는 코드는 없다 | `Flash_Chip` · `Flash_Block_Manager` 생성자 |

dynamic 은 "새로 쓸 곳을 고를 때 덜 닳은 곳을 고른다" 이고, static 은 "덜 닳은 곳에 갇힌 cold 데이터를 꺼낸다" 이다. static 의 동작과 이 프로젝트가 고친 부분은 [10단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/)에 있다.

## 5. 두 종류의 캐시 — 헷갈리지 말 것

| | 매핑 캐시 (CMT) | 데이터 캐시 |
|---|---|---|
| 담는 것 | LPA → PPA 매핑 항목 | 사용자 데이터 page |
| 목적 | 매핑 테이블 전체를 DRAM 에 안 두려고 | 호스트 응답을 빨리 주고 반복 쓰기를 흡수하려고 |
| 설정 | `CMT_Capacity` | `Caching_Mechanism` (ADVANCED) · `Data_Cache_Capacity` (256 MiB) |
| 코드 | `Cached_Mapping_Table` | `Data_Cache_Manager_Flash_Advanced` |

## 6. 호스트 인터페이스와 스케줄링

| 설정 | 값 | 의미 | 코드 |
|---|---|---|---|
| `HostInterface_Type` | NVME | stream 마다 SQ/CQ 한 쌍 (multi-queue). SATA 는 단일 큐 | `Host_Interface_NVMe` / `_SATA` |
| `IO_Queue_Depth` · `Queue_Fetch_Size` | 65535 · 512 | 큐 길이, 한 번에 미리 가져올 명령 수 | `Input_Stream_Manager_NVMe` |
| `Transaction_Scheduling_Policy` | PRIORITY_OUT_OF_ORDER | 도착 순서 대신 소스·우선순위로 재정렬 | `TSU_Priority_OutOfOrder` |
| `Plane_Allocation_Scheme` | CWDP | 연속 LPN 을 채널 → 칩 → 다이 → 플레인 순으로 흩뿌림 | `allocate_plane_for_user_write` |
| `CMD_Suspension_Support` | ERASE | 긴 erase 도중 급한 read 가 오면 잠시 멈춤 | `Flash_Chip::Suspend()` |

TSU 의 큐 우선순위는 **매핑 관련 > (GC 긴급 모드면) GC > 사용자** 이다. 기본 설정은 GC 가 항상 긴급 모드이므로 실질적으로 "매핑 > GC > 사용자" 순서가 된다. [8단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/)에서 코드로 본다.

## 7. 물리 타이밍

| 설정 | 값 | 의미 |
|---|---|---|
| `Page_Read_Latency_*` | 75 µs | page read |
| `Page_Program_Latency_*` | 750 µs | program — read 의 10배 |
| `Block_Erase_Latency` | 3.8 ms | erase — program 의 5배 |
| `Flash_Channel_Count` × `Chip_No_Per_Channel` | 8 × 4 | 채널당 칩 4개가 버스를 나눠 쓴다 |


<div style="margin-top: 60px;"></div>

## 관련 문서

- [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) · [Code Change](/ftl-visual-simulator/reference/code-change/) — 이 프로젝트가 원본의 설정 동작을 바꾼 곳 (예: 정적 WL 임계값이 실제로 전달되도록 고친 것)
