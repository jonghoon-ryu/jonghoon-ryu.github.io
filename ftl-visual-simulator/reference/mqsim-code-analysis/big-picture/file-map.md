---
layout: default
title: 파일별 지도
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/file-map/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 파일별 지도

코드를 열기 전에 **어느 파일이 얼마나 크고 무슨 일을 하는지**를 한눈에 보는 표다. 줄 수는 `51f0f2d` 커밋의 `.cpp` 파일이고(헤더 제외), 각 디렉터리의 큰 파일만 골랐다. 전체 규모는 [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) 의 표를 참고.


<div style="margin-top: 60px;"></div>

## 1. ssd/ — FTL 이 사는 곳

<svg viewBox="0 0 980 400" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="ssd/ 의 큰 파일들"><defs><marker id="afbar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="afbars" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">ssd/ 에서 가장 큰 파일들 (.cpp 줄 수)</text><text x="300" y="53" font-size="11" fill="#2c3e50" text-anchor="end">Address_Mapping_Unit_Page_Level</text><rect x="310" y="35" width="560.0" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="878.0" y="51" font-size="10.5" fill="#4d5656" text-anchor="start">1,935</text><text x="300" y="83" font-size="11" fill="#2c3e50" text-anchor="end">FTL</text><rect x="310" y="65" width="262.78036175710594" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="580.780361757106" y="81" font-size="10.5" fill="#4d5656" text-anchor="start">908</text><text x="300" y="113" font-size="11" fill="#2c3e50" text-anchor="end">NVM_PHY_ONFI_NVDDR2</text><rect x="310" y="95" width="204.60981912144703" height="22" rx="3" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="1.2"/><text x="522.609819121447" y="111" font-size="10.5" fill="#4d5656" text-anchor="start">707</text><text x="300" y="143" font-size="11" fill="#2c3e50" text-anchor="end">TSU_FLIN</text><rect x="310" y="125" width="171.03875968992247" height="22" rx="3" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="1.2"/><text x="489.0387596899225" y="141" font-size="10.5" fill="#4d5656" text-anchor="start">591</text><text x="300" y="173" font-size="11" fill="#2c3e50" text-anchor="end">Data_Cache_Manager_Flash_Advanced</text><rect x="310" y="155" width="169.01291989664082" height="22" rx="3" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="1.2"/><text x="487.0129198966408" y="171" font-size="10.5" fill="#4d5656" text-anchor="start">584</text><text x="300" y="203" font-size="11" fill="#2c3e50" text-anchor="end">TSU_Priority_OutOfOrder</text><rect x="310" y="185" width="160.6201550387597" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="478.62015503875966" y="201" font-size="10.5" fill="#4d5656" text-anchor="start">555</text><text x="300" y="233" font-size="11" fill="#2c3e50" text-anchor="end">Host_Interface_NVMe</text><rect x="310" y="215" width="137.75710594315245" height="22" rx="3" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="1.2"/><text x="455.75710594315245" y="231" font-size="10.5" fill="#4d5656" text-anchor="start">476</text><text x="300" y="263" font-size="11" fill="#2c3e50" text-anchor="end">TSU_OutofOrder</text><rect x="310" y="245" width="121.83979328165375" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="439.8397932816538" y="261" font-size="10.5" fill="#4d5656" text-anchor="start">421</text><text x="300" y="293" font-size="11" fill="#2c3e50" text-anchor="end">Host_Interface_SATA</text><rect x="310" y="275" width="104.47545219638243" height="22" rx="3" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="1.2"/><text x="422.47545219638243" y="291" font-size="10.5" fill="#4d5656" text-anchor="start">361</text><text x="300" y="323" font-size="11" fill="#2c3e50" text-anchor="end">Data_Cache_Manager_Flash_Simple</text><rect x="310" y="305" width="95.21447028423772" height="22" rx="3" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="1.2"/><text x="413.21447028423773" y="321" font-size="10.5" fill="#4d5656" text-anchor="start">329</text><text x="300" y="353" font-size="11" fill="#2c3e50" text-anchor="end">GC_and_WL_Unit_Base</text><rect x="310" y="335" width="87.68992248062017" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="405.68992248062017" y="351" font-size="10.5" fill="#4d5656" text-anchor="start">303</text><text x="300" y="383" font-size="11" fill="#2c3e50" text-anchor="end">Flash_Block_Manager_Base</text><rect x="310" y="365" width="70.61498708010335" height="22" rx="3" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="1.2"/><text x="388.61498708010333" y="381" font-size="10.5" fill="#4d5656" text-anchor="start">244</text></svg>

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `Address_Mapping_Unit_Page_Level.cpp` | 1,935 | FTL 의 핵심 — CMT 조회, plane/page 할당, translation page, barrier |
| `FTL.cpp` | 908 | FTL 껍데기와 preconditioning(steady-state 모형) |
| `NVM_PHY_ONFI_NVDDR2.cpp` | 707 | 채널 위 명령 전송 · 데이터 전송 · 서스펜드 · die interleave |
| `TSU_FLIN.cpp` | 591 | (전체가 주석 처리됨) |
| `Data_Cache_Manager_Flash_Advanced.cpp` | 584 | DRAM 캐시: LRU · destage · back-pressure · DRAM 시간 |
| `TSU_Priority_OutOfOrder.cpp` | 555 | 기본 TSU: 우선순위 class 가중 라운드 로빈 |
| `Host_Interface_NVMe.cpp` | 476 | NVMe 입구: 큐 · 명령 fetch · transaction 쪼개기 |
| `TSU_OutofOrder.cpp` | 421 | TSU 단순판 |
| `Host_Interface_SATA.cpp` | 361 | SATA 입구 |
| `Data_Cache_Manager_Flash_Simple.cpp` | 329 | 단순 캐시 (SIMPLE) |
| `GC_and_WL_Unit_Base.cpp` | 303 | GC/WL 공통: 완료 처리 체인, static WL, 안전한 후보 |
| `Flash_Block_Manager_Base.cpp` | 244 | plane 장부, free pool, 카운터 |
| `GC_and_WL_Unit_Page_Level.cpp` | 192 | GC 시작 조건과 victim 정책 switch |
| `Data_Cache_Flash.cpp` | 174 | 캐시 자료구조 (slot, LRU) |
| `Flash_Block_Manager.cpp` | 152 | page 할당, invalidate, erase 반영 |
| `TSU_Base.cpp` | 140 | 신호 연결, 멀티플레인 묶기(issue_command_to_chip) |
| `Stats.cpp` | 106 | 통계 카운터 |
| `ONFI_Channel_NVDDR2.cpp` | 65 | 채널 타이밍 상수 |
| `Host_Interface_Base.cpp` | 188 | 호스트 인터페이스 공통 · 신호 |

**한 파일이 거의 전부다.** `Address_Mapping_Unit_Page_Level.cpp` 가 FTL 의 핵심 로직 대부분(CMT, plane·page 할당, translation page, barrier)을 담고 있어서, FTL 을 읽는 일은 이 파일을 읽는 일과 같다.


<div style="margin-top: 60px;"></div>

## 2. 나머지 디렉터리

### exec/ — 조립과 설정

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `Device_Parameter_Set.cpp` | 639 | ssdconfig.xml 의 Device 파트 읽기/쓰기 |
| `SSD_Device.cpp` | 463 | SSD 한 대 조립 (10단계) |
| `IO_Flow_Parameter_Set.cpp` | 471 | workload.xml 의 flow 읽기 |
| `Flash_Parameter_Set.cpp` | 215 | NAND 사양 읽기 |
| `Host_System.cpp` | 189 | 호스트 조립 · 시작 |

### host/ — 호스트

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `IO_Flow_Base.cpp` | 608 | flow 공통 — NVMe 큐 · 제출 · 완료 처리 |
| `IO_Flow_Trace_Based.cpp` | 336 | trace 재생 |
| `IO_Flow_Synthetic.cpp` | 262 | 합성 부하 생성 |
| `SATA_HBA.cpp` | 196 | SATA 호스트 쪽 |
| `PCIe_Root_Complex.cpp` | 77 | PCIe 호스트 쪽 |
| `PCIe_Link.cpp` | 79 | 링크 전송 시간 |

### sim/ · nvm_chip/ · utils/

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `EventTree.cpp` | 503 | 시각 순 이벤트 보관 (레드-블랙 트리) |
| `Engine.cpp` | 134 | 엔진: 객체 목록, 이벤트 루프 |

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `flash_memory/Flash_Chip.cpp` | 297 | 칩: 명령 실행 · 서스펜드 · 통계 |

| 파일 | 줄 수 (.cpp) | 역할 |
|---|--:|---|
| `Logical_Address_Partitioning_Unit.cpp` | 264 | flow 별 논리 주소·자원 분할 |
| `RandomGenerator.cpp` | 242 | 난수 분포 |
| `XMLWriter.cpp` | 126 | 결과 XML 쓰기 |


<div style="margin-top: 60px;"></div>

## 3. 읽는 순서 제안

| 목적 | 순서 |
|---|---|
| FTL 만 | `Address_Mapping_Unit_Page_Level.cpp` (query_cmt → translate_lpa_to_ppa → allocate_*) → `Flash_Block_Manager.cpp` → `GC_and_WL_Unit_Page_Level.cpp` → `GC_and_WL_Unit_Base.cpp` |
| 시간이 어떻게 흐르나 | `sim/Engine.cpp` → `ssd/TSU_Base.cpp` → `NVM_PHY_ONFI_NVDDR2.cpp` → `Flash_Chip.cpp` |
| 요청의 입구 | `host/IO_Flow_Base.cpp` → `ssd/Host_Interface_NVMe.cpp` → `Data_Cache_Manager_Flash_Advanced.cpp` |
| 설정이 어떻게 반영되나 | `exec/Device_Parameter_Set.cpp` → `exec/SSD_Device.cpp` |


<div style="margin-top: 60px;"></div>

## 4. 읽다가 마주칠 것

- **주석 처리된 코드**: `TSU_FLIN.*`(전체), `SSD_Device.cpp` 의 FLIN 생성 부분. 구현이 아니라 흔적이다.
- **비어 있는 구현**: `Address_Mapping_Unit_Hybrid.cpp`(53줄 스텁), `FTL::Start_simulation`/`Execute_simulator_event`, `Do_warmup` 의 본문.
- **헤더에 있는 인라인 함수**: 일부 `inline` 함수가 `.cpp` 에 정의되어 있어 다른 파일에서 부르면 링크 오류가 난다 — 이 프로젝트의 유닛 테스트가 처음 밖에서 불러 보고 찾은 버그다([잘못된 inline 선언 버그](/ftl-visual-simulator/reference/code-change/bug-list/inline-linkage-bug/)).


<div style="margin-top: 60px;"></div>

## 관련 문서

- [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)
