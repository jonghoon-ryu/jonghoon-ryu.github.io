---
layout: default
title: MQSim 개요
permalink: /ftl-visual-simulator/mqsim/overview/
---
# MQSim 이란?

이 프로젝트가 그대로 가져다 쓸 엔진, MQSim 을 조사한 기록.

<div style="margin-top: 60px;"></div>

## 한 줄 요약

**MQSim** 은 CMU SAFARI 그룹( Arash Tavakkol 등, ETH Zurich 와 공동 )이 만든 오픈소스 SSD 시뮬레이터로, FAST 2018 학회에서 발표됐다.

> Arash Tavakkol, Juan Gómez-Luna, Mohammad Sadrosadati, Saugata Ghose, Onur Mutlu, *"MQSim: A Framework for Enabling Realistic Studies of Modern Multi-Queue SSD Devices"*, FAST 2018.
> [논문 PDF](https://people.inf.ethz.ch/omutlu/pub/MQSim-SSD-simulation-framework_fast18.pdf) · [GitHub](https://github.com/CMU-SAFARI/MQSim)

기존 SSD 시뮬레이터들이 놓치던 세 가지를 정확히 모델링하는 게 이 논문의 핵심 주장이다.

1. NVMe 같은 최신 multi-queue 호스트 인터페이스 프로토콜
2. SSD 의 steady-state( 어느 정도 채워지고 GC 가 정상적으로 도는 ) 상태
3. I/O 요청의 end-to-end 지연시간( host 부터 flash 까지 전체 경로 )

<div style="margin-top: 60px;"></div>

## 실제로 뭘 하는 프로그램인가

- 입력 : SSD 하드웨어 설정( `ssdconfig.xml` )과 워크로드 정의( `workload.xml`, synthetic 또는 실제 trace 파일 )
- 실행 : 이산 이벤트 시뮬레이션( discrete-event simulation )으로 호스트 요청 → FTL 매핑 → flash 채널 → NAND 동작까지 전부 시간 단위로 시뮬레이션
- 출력 : 요청 처리량/지연시간, FTL 내부 통계( GC 실행 횟수, valid page 이동량, CMT 캐시 hit/miss 등 )가 담긴 결과 XML

9/4 에 직접 clone 해서 `make` 로 빌드하고 샘플 설정으로 실행해봤는데, 외부 의존성 없이( 순수 C++11 + STL ) g++13 에서 코드 수정 없이 바로 빌드됐다.

<div style="margin-top: 60px;"></div>

## 모델링하는 FTL 기능들

우리가 시각화하려는 개념들이 실제로 다 구현되어 있다.

- **주소 매핑** : page-level ( `Address_Mapping_Unit_Page_Level.cpp` )만 실제로 구현되어 있음 — hybrid/log-block( `Address_Mapping_Unit_Hybrid.cpp` )은 클래스 골격만 있고 내부 로직은 빈 스텁( [코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) 정확성 노트 참고 )
- **GC** : victim block 선정( greedy 계열인 RGA 등 ), valid page migration, block erase — `GC_and_WL_Unit_Page_Level.cpp`
- **마모 평준화** : dynamic( 새 write frontier 를 고를 때 erase count 가 가장 낮은 free 블록을 우선 선택 ) / static( plane 내 최대-최소 erase count 차이가 threshold 를 넘으면 강제 순환 ) — `GC_and_WL_Unit_Base.cpp` + `Flash_Block_Manager_Base.cpp`
- **Over-provisioning** : `Address_Mapping_Unit_Base` 의 `overprovisioning_ratio` — 물리 용량 중 호스트에 노출하지 않는 여분 비율
- ⚠️ **Bad block 관리는 실제로 없음** : `Block_PE_Cycles_Limit`(erase 횟수 한계) 값이 존재하긴 하지만, 코드로 확인한 결과 통계용 히스토그램 배열 크기를 정하는 데만 쓰이고, 어떤 블록도 이 한계에 도달했다고 "퇴역(retire)"시키는 로직은 없음( `bad_block`/`badblock` 관련 코드 자체가 전무 )
- **매핑 테이블 캐싱** : CMT(Cached Mapping Table) — DFTL 류의 demand-based 캐싱 개념과 동일한 발상
- **Host interface** : NVMe / SATA — `Host_Interface_NVMe.cpp`, `Host_Interface_SATA.cpp`
- **Flash 물리 계층** : ONFI 채널, NVDDR2 타이밍 모델 — `NVM_PHY_ONFI*.cpp`
- **트랜잭션 스케줄링** : FLIN, out-of-order, priority out-of-order 등 여러 TSU 정책

<div style="margin-top: 60px;"></div>

## 코드 규모

- `src/` 아래 61개 `.cpp` 파일, 헤더 포함 약 19,300 줄
- 모듈 구성 : `exec`( 설정 파싱 ), `host`( 호스트 인터페이스 ), `nvm_chip/flash_memory`( NAND 물리 모델 ), `sim`( 이벤트 엔진 ), `ssd`( FTL 전체 ), `utils`
- 외부 라이브러리 의존성 없음 — 표준 C++11 + STL 만 사용

<div style="margin-top: 60px;"></div>

## ssdconfig.xml 파라미터 구조

실제 `ssdconfig.xml`( 9/4 에 실행한 샘플 설정 )을 열어서 확인한 구조. 크게 `Host_Parameter_Set`( 호스트 쪽 )과 `Device_Parameter_Set`( SSD 쪽 )로 나뉘고, `Device_Parameter_Set` 안에 하드웨어 스펙( `Flash_Parameter_Set` )이 중첩되어 있다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>그룹</th><th>주요 파라미터</th><th>의미</th></tr>
<tr><td><b>Host_Parameter_Set</b></td><td><code>PCIe_Lane_Bandwidth</code>, <code>PCIe_Lane_Count</code>, <code>SATA_Processing_Delay</code></td><td>호스트↔SSD 링크 대역폭/지연 — NVMe 는 PCIe lane, SATA 는 별도 처리 지연값을 씀</td></tr>
<tr><td>Device — 인터페이스/캐시</td><td><code>HostInterface_Type</code>(NVME/SATA), <code>IO_Queue_Depth</code>, <code>Caching_Mechanism</code>(ADVANCED), <code>Data_Cache_Capacity</code></td><td>큐 구조와 SSD 내부 DRAM 캐시 크기 — <code>Data_Cache_Manager</code> 가 쓰는 값</td></tr>
<tr><td>Device — 매핑(FTL)</td><td><code>Address_Mapping</code>(PAGE_LEVEL/HYBRID), <code>CMT_Capacity</code>, <code>Ideal_Mapping_Table</code></td><td><code>Address_Mapping_Unit</code> 이 어떤 서브클래스로 뜨는지, CMT 캐시 규모( demand-based 캐싱 크기 )</td></tr>
<tr><td>Device — GC/마모평준화</td><td><code>Overprovisioning_Ratio</code>, <code>GC_Exec_Threshold</code>, <code>GC_Hard_Threshold</code>, <code>GC_Block_Selection_Policy</code>(RGA 등), <code>Dynamic_Wearleveling_Enabled</code>, <code>Static_Wearleveling_Threshold</code></td><td><code>GC_and_WL_Unit</code> 이 언제(threshold) · 무엇을(policy) 고를지 — 파라미터 패널의 핵심 조절 대상( Session 9 )</td></tr>
<tr><td>Device — 스케줄링</td><td><code>Transaction_Scheduling_Policy</code>(PRIORITY_OUT_OF_ORDER 등), <code>Plane_Allocation_Scheme</code>(CWDP)</td><td>TSU 가 여러 채널/칩에 요청을 어떻게 분배·순서화할지</td></tr>
<tr><td>Device — 채널/타이밍</td><td><code>Flash_Channel_Count</code>, <code>Chip_No_Per_Channel</code>, <code>Channel_Transfer_Rate</code>, <code>Flash_Comm_Protocol</code>(NVDDR2)</td><td><code>ONFI_Channel</code> 물리 계층 구성</td></tr>
<tr><td><b>Flash_Parameter_Set</b>(중첩)</td><td><code>Page_Read/Program_Latency_*</code>, <code>Block_Erase_Latency</code>, <code>Block_PE_Cycles_Limit</code>, <code>Die_No_Per_Chip</code>, <code>Plane_No_Per_Die</code>, <code>Block_No_Per_Plane</code>, <code>Page_No_Per_Block</code>, <code>Page_Capacity</code></td><td>NAND 물리 스펙 — flash grid 의 block/page 개수, 마모 한계( PE cycle )가 여기서 나옴</td></tr>
</table>
</div>

이 중 파라미터 패널( Session 9 )에 그대로 노출할 것 : `Address_Mapping`, `Overprovisioning_Ratio`, `GC_Exec_Threshold`/`GC_Hard_Threshold`, `GC_Block_Selection_Policy`, `Dynamic_Wearleveling_Enabled`, `Block_No_Per_Plane`/`Page_No_Per_Block`( 그리드 크기 ). 나머지( PCIe 대역폭, DRAM 캐시 타이밍, 채널 타이밍 세부값 )는 시뮬레이션 정확도에는 필요하지만 초심자 UI 에는 노출하지 않고 기본값으로 고정한다.

<div style="margin-top: 60px;"></div>

## 다른 오픈소스 SSD/FTL 시뮬레이터들과 비교

FTL 을 시뮬레이션하는 오픈소스 도구는 MQSim 말고도 여럿 있다. 이번 프로젝트에 뭘 쓸지 고르면서 비교해본 것들.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>이름</th><th>특징</th><th>이번 프로젝트 적합성</th></tr>
<tr><td><b>MQSim</b></td><td>Standalone C++ 바이너리. VM/QEMU 불필요. NVMe/SATA, page-level 매핑, GC/WL 모두 구현( ⚠️ hybrid 매핑은 클래스 골격만 있고 실제 로직은 빈 스텁 — 9/5 코드 확인 ). MIT 라이선스. GitHub 385 stars, 2025-08 최근 커밋</td><td>✅ 채택 — 외부 의존성 없어 WASM 컴파일에 유리, 코드 규모도 적당( ~19K 줄 )해서 hook 추가 작업이 감당할 만함</td></tr>
<tr><td>FEMU</td><td>QEMU 기반 FPGA/소프트웨어 에뮬레이터. 실제 VM 위에서 실제 데이터를 읽고 씀. 591 stars, 활발히 유지보수( 최근 커밋 매우 최근 )</td><td>❌ 부적합 — QEMU/KVM 풀 시스템이 전제라서 브라우저 WASM 으로 가져오기 사실상 불가능</td></tr>
<tr><td>SimpleSSD</td><td>gem5 등 full-system 시뮬레이터와 연동하는 고정밀 SSD 스택 모델. GPLv3. 54 stars, 마지막 커밋 2022-11</td><td>❌ 부적합 — 단독 실행 목적이 아니라 다른 시뮬레이터에 붙는 구조라 복잡도가 높고, 최근 유지보수도 뜸함</td></tr>
<tr><td>VSSIM</td><td>QEMU/KVM 기반 virtual machine SSD 시뮬레이터. IDE 인터페이스만 지원. 2013년 전후 연구, 사실상 유지보수 종료</td><td>❌ 부적합 — VM 기반이라 WASM 화 불가능, 기술도 오래됨</td></tr>
<tr><td>Amber</td><td>SSD 리소스를 매우 정밀하게 모델링하는 학술 연구용 full-system 시뮬레이터( arXiv 논문 )</td><td>❌ 부적합 — 공개된 유지보수 오픈소스 저장소로 보기 어렵고, 목적 자체가 이번 프로젝트보다 훨씬 무거움</td></tr>
<tr><td>Dhara</td><td>시뮬레이터가 아니라 실제 MCU 임베디드 기기에 올라가는 <b>진짜 FTL 라이브러리</b>( Daniel Beer, C, ~2,000 줄 ). Perfect wear-levelling, trim, 전원 차단에도 안전한 원자적 쓰기, O(log n) 연산을 제공. ISC 계열 라이선스. 502 stars, 마지막 커밋 2022-03</td><td>❌ 부적합 — 타이밍/큐잉/host 프로토콜을 시뮬레이션하지 않고 GC 정책도 하나로 고정돼 있어 "정책 비교/시각화" 목적에는 안 맞음. 다만 논문 기반 시뮬레이터가 아닌 <i>진짜로 동작하는</i> FTL 코드를 보고 싶을 때 참고하기 좋음</td></tr>
</table>
</div>

<div style="margin-top: 20px;"></div>

### 결론 : 왜 MQSim 인가

1. **VM/QEMU 가 필요 없는 standalone C++ 프로그램** — FEMU, VSSIM 처럼 풀 시스템 에뮬레이션이 전제인 도구들은 애초에 브라우저에서 돌릴 방법이 없음
2. **외부 의존성이 없는 순수 C++11 + STL** — Emscripten 으로 WASM 컴파일할 때 라이브러리 호환성 문제가 최소화됨( 9/4 에 g++13 에서 수정 없이 빌드되는 것으로 이미 확인 )
3. **코드 규모가 적당함( ~19K 줄, 61개 파일 )** — SimpleSSD 처럼 다른 프레임워크에 종속된 복잡한 구조가 아니라, 필요한 지점에 계측(hook) 코드를 추가하는 작업이 현실적으로 가능한 크기
4. **커리큘럼에서 다루려는 FTL 기능이 다 들어있음** — page-level/hybrid 매핑, GC, 마모 평준화, bad block, over-provisioning, CMT 캐싱까지 이 프로젝트가 시각화하려는 개념과 정확히 일치
5. **MIT 라이선스** — 코드를 가져다 수정(hook 추가)하고 재배포하는 데 제약이 없음( SimpleSSD 의 GPLv3 보다 자유로움 )
6. **논문 기반의 검증된 정확도, 활발한 관리** — FAST 2018 발표, 2025년까지 커밋이 이어지고 있어 오래된 프로젝트(VSSIM, Amber)보다 신뢰도가 높음

<div style="margin-top: 60px;"></div>

## 참고

- GitHub : [github.com/CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim)
- 논문(PDF) : [MQSim: A Framework for Enabling Realistic Studies of Modern Multi-Queue SSD Devices](https://people.inf.ethz.ch/omutlu/pub/MQSim-SSD-simulation-framework_fast18.pdf)
- 강의 : [Understanding & Designing Modern Storage Systems - L3: MQSim](https://www.youtube.com/watch?v=9YZGHl6yxBc)
- 비교 대상 중 하나, 실제 임베디드용 FTL 라이브러리 : [github.com/dlbeer/dhara](https://github.com/dlbeer/dhara)
- 관련 프로젝트 : [개발 계획](/ftl-visual-simulator/plan/)
