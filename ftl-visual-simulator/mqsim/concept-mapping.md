---
layout: default
title: FTL 개념 ↔ 파라미터·모듈 대응
permalink: /ftl-visual-simulator/mqsim/concept-mapping/
---
<style>
table.plan-calendar th, table.plan-calendar td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
table.plan-calendar { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 1rem 0; }
table.plan-calendar th { background: #f5f5f5; color: #333; }
</style>

# FTL 개념 ↔ 파라미터·모듈 대응

[개발 계획](/ftl-visual-simulator/plan/) Session 2 의 "Claude 가 정리한 XML 설정 항목·모듈 구조·파이프라인 다이어그램을 리뷰하며, 각 파라미터·모듈이 FTL 개념상 무엇을 의미하는지 실제로 이해" 항목을 위한 문서. [MQSim 개요](/ftl-visual-simulator/mqsim/overview/)가 "MQSim이 뭔가"를, [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/)이 "코드가 어떻게 짜여 있나"를 다룬다면, 이 문서는 **"FTL 개념 하나하나가 `ssdconfig.xml` 의 어느 파라미터, 코드의 어느 클래스에 대응하는가"**를 개념 중심으로 다시 엮은 것.

<div style="margin-top: 40px;"></div>

## 전체 파이프라인 — 개념으로 다시 그린 그림

<div style="overflow-x:auto;">
<svg viewBox="0 0 1180 260" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-cm0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t0{font-size:13px;font-weight:700;text-anchor:middle;} .b0{font-size:10px;text-anchor:middle;}
    .f0{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-cm0);fill:none;}
  </style>
  <rect x="10" y="90" width="170" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="95" y="112" class="t0" fill="#1e3a8a">① 요청 접수</text>
  <text x="95" y="130" class="b0" fill="#1e3a8a">multi-queue (NVMe)</text>
  <text x="95" y="145" class="b0" fill="#1e3a8a">vs 단일 큐 (SATA)</text>
  <text x="95" y="160" class="b0" fill="#1e3a8a">개념</text>

  <line x1="180" y1="130" x2="215" y2="130" class="f0"/>
  <rect x="215" y="90" width="170" height="80" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="300" y="112" class="t0" fill="#4c1d95">② 쓰기 캐싱</text>
  <text x="300" y="130" class="b0" fill="#4c1d95">DRAM write-back</text>
  <text x="300" y="145" class="b0" fill="#4c1d95">(선택적, 없어도 됨)</text>

  <line x1="385" y1="130" x2="420" y2="130" class="f0"/>
  <rect x="420" y="70" width="220" height="120" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="530" y="92" class="t0" fill="#134e4a">③ 주소 변환</text>
  <text x="530" y="110" class="b0" fill="#134e4a">LPA→PPA 매핑</text>
  <text x="530" y="125" class="b0" fill="#134e4a">demand-based 캐싱(DFTL)</text>
  <text x="530" y="140" class="b0" fill="#134e4a">= "필요한 매핑만 메모리에"</text>
  <text x="530" y="155" class="b0" fill="#134e4a">라는 개념 그 자체</text>
  <text x="530" y="175" class="b0" fill="#134e4a" font-style="italic">Over-provisioning 은 여기서</text>

  <line x1="640" y1="130" x2="675" y2="130" class="f0"/>
  <rect x="675" y="10" width="230" height="70" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="790" y="32" class="t0" fill="#881337">GC 개념</text>
  <text x="790" y="50" class="b0" fill="#881337">"공간 회수" — invalid page</text>
  <text x="790" y="65" class="b0" fill="#881337">쌓인 블록을 지워서 되돌림</text>
  <line x1="790" y1="130" x2="790" y2="80" class="f0"/>

  <rect x="675" y="90" width="230" height="80" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="790" y="112" class="t0" fill="#78350f">④ 공간 관리</text>
  <text x="790" y="130" class="b0" fill="#78350f">block/page 상태</text>
  <text x="790" y="145" class="b0" fill="#78350f">(free/valid/invalid)</text>

  <rect x="675" y="190" width="230" height="60" rx="8" fill="#16a34a" fill-opacity="0.15" stroke="#16a34a" stroke-width="2"/>
  <text x="790" y="210" class="t0" fill="#14532d">마모 평준화 개념</text>
  <text x="790" y="228" class="b0" fill="#14532d">"골고루 지워지게"</text>
  <line x1="790" y1="170" x2="790" y2="195" class="f0"/>

  <line x1="905" y1="130" x2="940" y2="130" class="f0"/>
  <rect x="940" y="90" width="120" height="80" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="1000" y="112" class="t0" fill="#312e81">⑤ 스케줄링</text>
  <text x="1000" y="130" class="b0" fill="#312e81">"언제, 어느</text>
  <text x="1000" y="145" class="b0" fill="#312e81">채널/칩에" 개념</text>

  <line x1="1060" y1="130" x2="1080" y2="130" class="f0"/>
  <text x="1120" y="105" class="b0" fill="#1e293b">⑥ 물리 실행</text>
  <text x="1120" y="120" class="b0" fill="#1e293b">(타이밍 모델,</text>
  <text x="1120" y="135" class="b0" fill="#1e293b">버스 경합)</text>
</svg>
</div>

아래 표는 이 그림의 각 번호가 실제로 어떤 `ssdconfig.xml` 파라미터, 어떤 MQSim 클래스에 대응하는지를 FTL 개념 단위로 풀어쓴 것.

<div style="margin-top: 60px;"></div>

## 1. 주소 매핑 (Address Mapping)

**FTL 개념** : 호스트가 쓰는 논리 주소(LPA)와 실제 flash 물리 주소(PPA)를 분리해서, "쓰기는 항상 새 위치에"(erase-before-write 회피) 하면서도 호스트 입장에서는 같은 주소를 계속 쓰는 것처럼 보이게 하는 간접 계층. 매핑 테이블을 전부 DRAM 에 두면 비싸므로, 일부만 캐싱하고 나머지는 flash 에 두는 **demand-based 캐싱(DFTL, Gupta et al., ASPLOS 2009)** 이 현실적인 절충안.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>ssdconfig.xml 파라미터</th><th>FTL 개념상 의미</th><th>담당 코드</th></tr>
<tr><td><code>Address_Mapping</code> = PAGE_LEVEL</td><td>매핑 단위가 페이지 하나하나 — 세밀하지만 매핑 테이블이 큼(그래서 캐싱이 필요)</td><td><code>Address_Mapping_Unit_Page_Level</code></td></tr>
<tr><td><code>Ideal_Mapping_Table</code> = false</td><td>true 면 "매핑 테이블이 무한히 커서 항상 DRAM 에 다 있다"는 이상적 가정 — 우리는 false 라서 실제 DFTL 캐싱 동작(hit/miss)을 볼 수 있음</td><td><code>Address_Mapping_Unit_Base::ideal_mapping_table</code></td></tr>
<tr><td><code>CMT_Capacity</code> = 2097152 (바이트)</td><td>DRAM 에 얼마나 많은 매핑 항목을 캐싱해둘지 — 작을수록 CMT miss(=매핑 자체를 flash 에서 다시 읽어와야 함)가 잦아짐</td><td><code>Cached_Mapping_Table</code>(LRU 캐시)</td></tr>
<tr><td><code>CMT_Sharing_Mode</code> = SHARED</td><td>여러 I/O 스트림이 캐시 공간을 나눠 쓸지(EQUAL_SIZE_PARTITIONING), 통째로 공유할지</td><td><code>AddressMappingDomain</code></td></tr>
</table>
</div>

**실제로 관찰되는 현상** : CMT 에 없는 LPA 를 요청하면(miss) MQSim 은 "매핑 테이블이 저장된 flash 페이지를 읽어오는" 별도의 flash read 트랜잭션을 만든다( [코드 분석 7-2절](/ftl-visual-simulator/mqsim/code-analysis/) 참고 ) — 이게 바로 "매핑 테이블도 결국 flash 공간을 차지하고, 매핑 miss 도 실제 I/O 지연을 유발한다"는 DFTL 개념이 코드로 구현된 부분.

<div style="margin-top: 60px;"></div>

## 2. Over-Provisioning (OP)

**FTL 개념** : 호스트에게 보여주는 논리 용량보다 실제 물리 flash 용량을 더 크게 만들어두는 것. 여분 공간이 있어야 GC 가 "일단 새 블록에 옮겨 쓰고 나서 예전 블록을 지우는" 여유를 가질 수 있다 — OP 가 낮을수록 GC 가 더 자주, 더 급하게 일어난다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>Overprovisioning_Ratio</code> = 0.07 (7%)</td><td>물리 용량 중 호스트에 노출하지 않고 여분으로 남겨두는 비율</td><td><code>Address_Mapping_Unit_Base::overprovisioning_ratio</code> — 논리 주소 공간 크기를 물리 공간보다 작게 계산할 때 사용</td></tr>
</table>
</div>

**실제로 관찰되는 현상** : OP 를 낮추면(예: 0.01) 같은 워크로드에서도 `Total_gc_executions` 가 급증한다 — "GC 시연" 프리셋(Session 9)이 바로 이 값을 낮춰서 GC 를 빨리 보이게 만드는 원리.

<div style="margin-top: 60px;"></div>

## 3. Garbage Collection (GC)

**FTL 개념** : 데이터를 지우려면(erase) 블록 전체를 한 번에 지워야 하는데(NAND 의 물리적 제약), 새 쓰기는 계속 새 위치에 일어나므로 예전 블록에는 "이제 안 쓰는(invalid) 페이지"가 쌓인다. GC 는 이런 블록에서 아직 유효한(valid) 페이지만 골라 다른 곳에 옮기고, 그 블록을 통째로 지워서 free 공간으로 되돌리는 과정.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>FTL 개념상 의미</th><th>담당 코드</th></tr>
<tr><td><code>GC_Exec_Threshold</code> = 0.05</td><td>free page 비율이 이 아래로 떨어지면 GC 시작 — "얼마나 급해야 청소를 시작하나"</td><td><code>GC_and_WL_Unit_Base::gc_threshold</code>, <code>Check_gc_required()</code></td></tr>
<tr><td><code>GC_Hard_Threshold</code> = 0.005</td><td>이보다 더 급하면 "긴급 모드" — 우선순위 없이 무조건 GC 먼저</td><td><code>GC_is_in_urgent_mode()</code></td></tr>
<tr><td><code>Preemptible_GC_Enabled</code> = false</td><td>GC 도중 사용자 요청이 끼어들 수 있게 할지(false=끼어들기 불가, 매 GC 를 방해 없이 완주)</td><td><code>preemptible_gc_enabled</code></td></tr>
<tr><td><code>GC_Block_Selection_Policy</code> = RGA</td><td>"어떤 블록을 청소 대상(victim)으로 고를까" 정책 — invalid page 가 많은 블록을 고르는 게 이득이지만, 전수 조사(GREEDY)는 비쌈</td><td><code>Check_gc_required()</code> 의 policy별 switch-case(6가지, [코드 분석 7-3절](/ftl-visual-simulator/mqsim/code-analysis/) 표 참고)</td></tr>
<tr><td><code>Use_Copyback_for_GC</code> = false</td><td>valid page 이동 시 데이터를 컨트롤러 밖으로 꺼내지 않고 칩 내부에서 바로 복사(copyback)할지 — 속도상 이점이지만 오류 검출이 약해짐</td><td><code>NVM_PHY_ONFI</code> 의 COPYBACK 커맨드 계열</td></tr>
</table>
</div>

**실제로 관찰되는 현상** : GC 한 번이 일으키는 "추가 쓰기"(valid page 이동)가 바로 Write Amplification 의 원인 — 우리 대시보드의 WAF 지표가 이 GC 빈도·이동량과 직접 연결된다.

<div style="margin-top: 60px;"></div>

## 4. 마모 평준화 (Wear Leveling)

**FTL 개념** : 블록은 지울 수 있는 횟수(P/E cycle)에 물리적 한계가 있다. 특정 블록만 계속 지워지면 그 블록만 먼저 죽는다 — 그래서 "지워지는 빈도를 여러 블록에 고르게 분산"시키는 게 마모 평준화. GC 의 victim 선정이 확률적이면(RGA/RANDOM) 자연히 어느 정도 분산되지만(dynamic WL), 아예 안 바뀌는 "차가운" 데이터가 있는 블록은 GC 대상이 될 기회 자체가 없어서 별도 보정(static WL)이 필요하다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>Dynamic_Wearleveling_Enabled</code> = true</td><td>GC victim 선정이 마모 분산도 함께 고려하는지( 사실상 RGA/RANDOM 계열 정책 자체가 이 역할 )</td><td><code>Check_gc_required()</code> 의 확률적 정책들</td></tr>
<tr><td><code>Static_Wearleveling_Enabled</code> = true, <code>Static_Wearleveling_Threshold</code> = 100</td><td>GC 로 커버 안 되는 차가운 블록을 강제로 순환시키는 문턱값( plane 내 최대-최소 erase count 차이 )</td><td><code>check_static_wl_required()</code>, <code>run_static_wearleveling()</code>, <code>Get_coldest_block_id()</code></td></tr>
<tr><td><code>Block_PE_Cycles_Limit</code> = 10000</td><td>블록 하나가 버틸 수 있는 최대 erase 횟수 — 마모 평준화의 목표가 "이 한계에 도달하는 시점을 블록들 사이에 최대한 늦고 고르게" 만드는 것</td><td><code>max_allowed_block_erase_count</code>(FTL 생성자 인자)</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 5. 캐싱 — SSD 내부 DRAM 쓰기 캐시 (매핑 캐시와는 다른 개념!)

**FTL 개념** : 여기서 "캐시"는 두 가지가 있어서 헷갈리기 쉽다 — (1) 위 1번의 CMT 는 **매핑 테이블용** 캐시, (2) 이번 항목은 **사용자 데이터 자체**를 SSD 내부 DRAM 에 잠깐 쌓아뒀다가 flash 에 쓰는 **쓰기 캐시**. 후자는 순수 성능(호스트 응답시간 단축) 목적이고 FTL 매핑 로직과는 별개 계층.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>Caching_Mechanism</code> = ADVANCED</td><td>단순 통과(SIMPLE) 대신 실제 캐시 라인 관리(적중/치환)를 하는 구현 사용</td><td><code>Data_Cache_Manager_Flash_Advanced</code></td></tr>
<tr><td><code>Data_Cache_Capacity</code> = 268435456 (256MB)</td><td>DRAM 쓰기 캐시 크기</td><td><code>Data_Cache_Manager_Base::dram_row_size</code> 등</td></tr>
<tr><td><code>Data_Cache_DRAM_tRCD/tCL/tRP</code></td><td>실제 DDR DRAM 타이밍 파라미터 — 캐시 접근도 공짜가 아니라는 것을 모델링</td><td><code>estimate_dram_access_time()</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 6. Host Interface — 큐 구조

**FTL 개념이라기보다 "FTL 에 도달하기 전 단계"** : 호스트가 어떤 프로토콜/큐 구조로 요청을 SSD 에 전달하는지. NVMe 의 multi-queue 는 여러 CPU 코어가 락 경합 없이 동시에 요청을 넣을 수 있게 하는 것이 핵심 아이디어.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>HostInterface_Type</code> = NVME</td><td>스트림마다 독립된 SQ/CQ 링버퍼( multi-queue ) — SATA 는 단일 큐</td><td><code>Host_Interface_NVMe</code> vs <code>Host_Interface_SATA</code></td></tr>
<tr><td><code>IO_Queue_Depth</code> = 65535</td><td>큐 하나에 최대 몇 개 명령을 담아둘 수 있는지 — 클수록 호스트가 더 많이 미리 던져둘 수 있음</td><td><code>Input_Stream_NVMe::Submission_queue_size</code></td></tr>
<tr><td><code>Queue_Fetch_Size</code> = 512</td><td>디바이스가 한 번에 SQ 에서 몇 개 명령을 미리 가져와둘지</td><td><code>Input_Stream_Manager_NVMe::Queue_fetch_size</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 7. 트랜잭션 스케줄링 (TSU)

**FTL 개념** : 매핑이 끝나 "이 논리 요청은 이 물리 채널/칩의 이 위치"까지 정해진 뒤, 실제로 그 물리 자원(채널/칩)을 여러 요청(사용자 read/write, 매핑 read/write, GC read/write/erase)이 어떤 순서로 나눠 쓸지 정하는 문제.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>Transaction_Scheduling_Policy</code> = PRIORITY_OUT_OF_ORDER</td><td>도착 순서를 지키지 않고(Out-of-Order) 우선순위/소스별로 재정렬해서 실행 — read 를 GC/매핑 write 보다 먼저</td><td><code>TSU_Priority_OutOfOrder::Schedule()</code>( [코드 분석 7-4절](/ftl-visual-simulator/mqsim/code-analysis/) 참고 )</td></tr>
<tr><td><code>Plane_Allocation_Scheme</code> = CWDP</td><td>연속된 논리 주소를 채널(C)/칩(W=Chip 약자와 무관, MQSim 표기)/다이(D)/플레인(P) 중 어느 순서로 흩뿌릴지 — 순서에 따라 병렬성 패턴이 달라짐</td><td><code>Flash_Plane_Allocation_Scheme_Type</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 8. 물리 계층 타이밍

**FTL 개념이 아니라 그 아래 NAND 물리 특성** — 왜 read 는 빠르고 program 은 느리고 erase 는 아주 느린지, 왜 채널 하나를 여러 칩이 나눠 써야 하는지의 근거.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파라미터</th><th>의미</th><th>담당 코드</th></tr>
<tr><td><code>Page_Read_Latency_*</code> = 75,000ns</td><td>페이지 하나 read 지연( LSB/CSB/MSB 로 세분화 — MLC 는 페이지당 2비트라 위치별 지연이 다름 )</td><td><code>Flash_Chip::Get_command_execution_latency()</code></td></tr>
<tr><td><code>Page_Program_Latency_*</code> = 750,000ns</td><td>program(쓰기)이 read 보다 10배 느린 이유 — NAND 셀의 전하 주입이 훨씬 느린 물리 과정이기 때문</td><td>〃</td></tr>
<tr><td><code>Block_Erase_Latency</code> = 3,800,000ns</td><td>erase 가 program 보다도 5배 느림 — GC 가 "비싼" 이유가 여기( migration write + 이 긴 erase )</td><td>〃</td></tr>
<tr><td><code>Flash_Channel_Count</code>=8, <code>Chip_No_Per_Channel</code>=4</td><td>채널 하나를 여러 칩이 시분할로 공유( 버스 경합 ) — TSU 가 라운드로빈으로 공평하게 나눠줘야 하는 이유</td><td><code>ONFI_Channel_Base</code></td></tr>
<tr><td><code>CMD_Suspension_Support</code> = ERASE</td><td>긴 erase 도중 급한 read 가 오면 잠깐 멈추고 read 부터 처리 — QoS 를 위한 타협</td><td><code>Flash_Chip::Suspend()</code>/<code>Resume()</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [MQSim 개요](/ftl-visual-simulator/mqsim/overview/) · [MQSim 코드 분석](/ftl-visual-simulator/mqsim/code-analysis/) · [MQSim 코드 분석 계획](/ftl-visual-simulator/mqsim/code-analysis-plan/) · [개발 계획](/ftl-visual-simulator/plan/)
