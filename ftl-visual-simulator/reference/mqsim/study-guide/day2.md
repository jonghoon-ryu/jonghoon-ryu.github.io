---
layout: default
title: MQSim 학습 가이드 Day 2 — FTL · 스케줄러 · flash 칩
permalink: /ftl-visual-simulator/reference/mqsim/study-guide/day2/
---
<style>
table.plan-calendar { width:100% !important; table-layout:fixed !important; border-collapse:collapse; font-size:0.85rem; margin:1rem 0; }
table.plan-calendar th, table.plan-calendar td { border:1px solid #ddd; padding:6px 10px; text-align:left; overflow-wrap:break-word; word-break:break-word; }
table.plan-calendar th { background:#f5f5f5; color:#333; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.fig { font-size:0.85rem; color:#666; text-align:center; margin:-0.4rem 0 1.4rem; }
svg.d2 { width:100%; height:auto; display:block; margin:1rem auto; }
svg.d2 text { font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif; }
svg.d2 .b { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
svg.d2 .h { fill:#fdf2e9; stroke:#ca6f1e; stroke-width:2; }
svg.d2 .g { fill:#e9f7ef; stroke:#1e8449; stroke-width:2; }
svg.d2 .y { fill:#fef9e7; stroke:#b7950b; stroke-width:2; }
svg.d2 .r { fill:#fdedec; stroke:#c0392b; stroke-width:2; }
svg.d2 .w { fill:#ffffff; stroke:#95a5a6; stroke-width:1.5; }
svg.d2 .pv { fill:#58d68d; stroke:#1e8449; stroke-width:1; }
svg.d2 .pi { fill:#ec7063; stroke:#922b21; stroke-width:1; }
svg.d2 .pf { fill:#f2f3f4; stroke:#95a5a6; stroke-width:1; }
svg.d2 .t { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
svg.d2 .s { fill:#566573; font-size:11.5px; text-anchor:middle; }
svg.d2 .sl { fill:#566573; font-size:11.5px; text-anchor:start; }
svg.d2 .c { fill:#7f8c8d; font-size:11px; text-anchor:middle; font-style:italic; }
svg.d2 .f { stroke:#7f8c8d; stroke-width:2; fill:none; marker-end:url(#d2a); }
svg.d2 .fr { stroke:#c0392b; stroke-width:2; fill:none; marker-end:url(#d2ar); }
svg.d2 .fd { stroke:#7f8c8d; stroke-width:1.5; fill:none; stroke-dasharray:5 4; marker-end:url(#d2a); }
</style>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <marker id="d2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker>
    <marker id="d2ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>
  </defs>
</svg>

# MQSim 학습 가이드 Day 2 — FTL · 스케줄러 · flash 칩

[← Day 1](/ftl-visual-simulator/reference/mqsim/study-guide/day1/) · [학습 가이드 목차](/ftl-visual-simulator/reference/mqsim/study-guide/)

어제는 요청이 DRAM 캐시까지 오는 길을 봤다. 오늘은 캐시를 지나 **flash 에 실제로 닿는** 쪽이다. 순서는 이렇다: flash 가 어떻게 생겼는지 → 논리 주소를 물리 주소로 바꾸는 표(매핑) → 빈 공간을 관리하는 block 관리 → 공간을 되찾는 GC 와 마모를 고르게 하는 WL → 명령을 칩에 보내는 스케줄러와 칩 자체. 마지막에 쓰기 하나를 처음부터 끝까지 따라간다.

<div style="margin-top: 60px;"></div>

<h2 id="session-2-1">세션 2-1 · flash 구조와 주소 (1시간)</h2>

### 여섯 단계의 계층

<svg class="d2" viewBox="0 0 900 300" style="max-width:860px">
  <rect class="w" x="10" y="20" width="200" height="260" rx="10"/><text class="t" x="110" y="44">채널 × 8</text><text class="s" x="110" y="64">데이터 버스. 한 번에 한 칩만</text><text class="s" x="110" y="80">명령·데이터를 주고받음</text>
  <rect class="g" x="30" y="100" width="160" height="160" rx="8"/><text class="t" x="110" y="124">칩 × 4 (채널당)</text><text class="s" x="110" y="144">각 칩은 독립적으로 동작</text><text class="s" x="110" y="160">→ 병렬 처리의 단위</text>
  <rect class="w" x="240" y="20" width="200" height="260" rx="10"/><text class="t" x="340" y="44">다이 × 2 (칩당)</text><text class="s" x="340" y="64">명령을 실행하는 단위</text>
  <rect class="w" x="260" y="90" width="160" height="170" rx="8"/><text class="t" x="340" y="114">플레인 × 2 (다이당)</text><text class="s" x="340" y="134">같은 다이의 플레인은</text><text class="s" x="340" y="150">같은 명령을 동시에(multi-plane)</text>
  <rect class="w" x="470" y="20" width="200" height="260" rx="10"/><text class="t" x="570" y="44">블록 × 2048 (플레인당)</text><text class="s" x="570" y="64">지우기(erase)의 최소 단위</text>
  <rect class="w" x="490" y="90" width="160" height="170" rx="8"/><text class="t" x="570" y="114">페이지 × 256 (블록당)</text><text class="s" x="570" y="134">읽기·쓰기의 최소 단위</text><text class="s" x="570" y="150">8KB = 섹터 16개</text>
  <rect class="y" x="700" y="20" width="190" height="260" rx="10"/><text class="t" x="795" y="44">시간 (MLC, 기본값)</text>
  <text class="sl" x="715" y="80">읽기</text><text class="sl" x="800" y="80">75 µs</text>
  <text class="sl" x="715" y="110">쓰기(program)</text><text class="sl" x="800" y="110">750 µs</text>
  <text class="sl" x="715" y="140">지우기(erase)</text><text class="sl" x="800" y="140">3,800 µs</text>
  <text class="s" x="795" y="180">읽기 : 쓰기 : 지우기</text><text class="s" x="795" y="198">≈ 1 : 10 : 50</text>
  <text class="s" x="795" y="236">(MLC 는 page 위치에 따라</text><text class="s" x="795" y="252">LSB/CSB/MSB 지연이 다름)</text>
  <path class="f" d="M210,150 L238,150"/><path class="f" d="M440,150 L468,150"/>
</svg>
<div class="fig">그림 2-1-1. 채널 → 칩 → 다이 → 플레인 → 블록 → 페이지, 그리고 연산별 시간</div>

### flash 의 세 가지 규칙 — FTL 이 존재하는 이유

<svg class="d2" viewBox="0 0 900 200" style="max-width:860px">
  <rect class="r" x="20" y="20" width="270" height="160" rx="10"/><text class="t" x="155" y="46">① 덮어쓰기 불가</text><text class="s" x="155" y="74">한 번 쓴 page 는</text><text class="s" x="155" y="92">지우기 전까지 다시 못 쓴다</text><text class="s" x="155" y="130">→ 수정할 때는 새 page 에 쓰고</text><text class="s" x="155" y="148">예전 page 는 "무효" 표시</text>
  <rect class="r" x="315" y="20" width="270" height="160" rx="10"/><text class="t" x="450" y="46">② 지우기는 block 단위</text><text class="s" x="450" y="74">page 하나만 지울 수 없고</text><text class="s" x="450" y="92">256 page 를 통째로 지운다</text><text class="s" x="450" y="130">→ 살아있는 page 를 먼저</text><text class="s" x="450" y="148">다른 곳으로 옮겨야 함 (GC)</text>
  <rect class="r" x="610" y="20" width="270" height="160" rx="10"/><text class="t" x="745" y="46">③ 지울수록 닳는다</text><text class="s" x="745" y="74">block 마다 지울 수 있는</text><text class="s" x="745" y="92">횟수(P/E cycle)가 정해져 있다</text><text class="s" x="745" y="130">→ 골고루 지우도록</text><text class="s" x="745" y="148">관리 (마모평준화, WL)</text>
</svg>
<div class="fig">그림 2-1-2. flash 의 세 규칙과 FTL 의 대응</div>

### 주소 두 종류: LPA 와 PPA

- **LPA**(Logical Page Address): 호스트가 보는 page 번호. Day 1 에서 섹터 주소를 16 으로 나눠 만든 그것.
- **PPA**(Physical Page Address): flash 의 실제 위치 = (채널, 칩, 다이, 플레인, 블록, 페이지). 코드에서는 이 6개를 하나의 정수로 합친 `PPA_type` 과, 풀어놓은 `Physical_Page_Address` 구조체를 오간다.

### LPA 는 어느 플레인으로 가나 — 고정 배정 (CWDP)

MQSim 에서 LPA 가 **어느 플레인**에 저장될지는 **LPA 번호만으로 미리 정해진다**. 기본 방식 CWDP 는 이름 순서(Channel → Way(칩) → Die → Plane)대로 번갈아 배정한다. 그 플레인 **안에서** 어느 block, 어느 page 에 쓸지는 쓸 때마다 정해진다(세션 2-3).

<svg class="d2" viewBox="0 0 900 250" style="max-width:860px">
  <text class="sl" x="20" y="28">CWDP: 채널 = LPA % 8,  칩 = (LPA / 8) % 4,  다이 = (LPA / 32) % 2,  플레인 = (LPA / 64) % 2</text>
  <text class="sl" x="20" y="68">LPA</text>
  <rect class="h" x="70" y="50" width="40" height="30"/><text class="s" x="90" y="70">0</text>
  <rect class="h" x="112" y="50" width="40" height="30"/><text class="s" x="132" y="70">1</text>
  <rect class="h" x="154" y="50" width="40" height="30"/><text class="s" x="174" y="70">2</text>
  <text class="s" x="215" y="70">…</text>
  <rect class="h" x="236" y="50" width="40" height="30"/><text class="s" x="256" y="70">7</text>
  <rect class="h" x="278" y="50" width="40" height="30"/><text class="s" x="298" y="70">8</text>
  <rect class="h" x="320" y="50" width="40" height="30"/><text class="s" x="340" y="70">9</text>
  <text class="s" x="385" y="70">…</text>
  <rect class="h" x="410" y="50" width="40" height="30"/><text class="s" x="430" y="70">32</text>
  <rect class="h" x="452" y="50" width="40" height="30"/><text class="s" x="472" y="70">64</text>
  <rect class="g" x="70" y="130" width="120" height="60" rx="6"/><text class="s" x="130" y="155">채널0·칩0</text><text class="s" x="130" y="172">다이0·플레인0</text>
  <rect class="g" x="200" y="130" width="120" height="60" rx="6"/><text class="s" x="260" y="155">채널1·칩0</text><text class="s" x="260" y="172">다이0·플레인0</text>
  <rect class="g" x="330" y="130" width="120" height="60" rx="6"/><text class="s" x="390" y="155">채널0·칩1</text><text class="s" x="390" y="172">다이0·플레인0</text>
  <rect class="g" x="460" y="130" width="120" height="60" rx="6"/><text class="s" x="520" y="155">채널0·칩0</text><text class="s" x="520" y="172">다이1·플레인0</text>
  <rect class="g" x="590" y="130" width="120" height="60" rx="6"/><text class="s" x="650" y="155">채널0·칩0</text><text class="s" x="650" y="172">다이0·플레인1</text>
  <path class="f" d="M90,80 L125,128"/><path class="f" d="M132,80 L255,128"/><path class="f" d="M298,80 L385,128"/><path class="f" d="M430,80 L515,128"/><path class="f" d="M472,80 L645,128"/>
  <text class="c" x="450" y="225">연속된 LPA 가 서로 다른 채널로 흩어진다 → 큰 요청은 여러 칩이 동시에 처리 (병렬성). 대신 LPA 가 다른 플레인으로 옮겨가는 일은 없다</text>
</svg>
<div class="fig">그림 2-1-3. CWDP: LPA 번호로 플레인이 정해진다</div>

<div class="check" markdown="1">
**확인 질문**
1. page, block, plane 중 쓰기의 단위는? 지우기의 단위는? 같은 명령을 동시에 할 수 있는 단위는?
2. 기본 설정에서 LPA 100 은 어느 채널·칩·다이·플레인으로 가나? (힌트: 100 % 8, 100/8 % 4, …)
3. flash 의 세 규칙이 각각 어떤 FTL 기능을 필요하게 만드나?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-2-2">세션 2-2 · 주소 매핑 — GMT · CMT · GTD (1시간)</h2>

### 표 세 개

"LPA 가 지금 어느 PPA 에 있나"를 기억하는 표가 FTL 의 심장이다. `Address_Mapping_Unit_Page_Level`(AMU)이 관리하고, flow(stream)마다 따로 **domain** 을 가진다.

<svg class="d2" viewBox="0 0 900 310" style="max-width:860px">
  <rect class="g" x="20" y="20" width="270" height="270" rx="10"/><text class="t" x="155" y="46">GMT — 전체 매핑표</text><text class="s" x="155" y="66">Global Mapping Table</text>
  <text class="sl" x="40" y="96">LPA  →  PPA,  쓴 섹터 bitmap,  시각</text>
  <rect class="w" x="40" y="108" width="230" height="24"/><text class="sl" x="50" y="125">0 → (ch2, chip1, …, blk17, pg3)</text>
  <rect class="w" x="40" y="132" width="230" height="24"/><text class="sl" x="50" y="149">1 → (ch3, chip0, …, blk4, pg90)</text>
  <rect class="w" x="40" y="156" width="230" height="24"/><text class="sl" x="50" y="173">2 → 아직 안 씀 (NO_PPA)</text>
  <text class="s" x="155" y="208">개념상 flash 의 "매핑 page"에 저장</text><text class="s" x="155" y="226">(page 하나에 항목 수천 개)</text><text class="s" x="155" y="260">너무 커서 전부 DRAM 에 못 둔다</text>
  <rect class="y" x="315" y="20" width="270" height="270" rx="10"/><text class="t" x="450" y="46">CMT — 매핑 캐시</text><text class="s" x="450" y="66">Cached Mapping Table (DRAM)</text>
  <text class="s" x="450" y="100">GMT 중 최근에 쓴 항목만</text><text class="s" x="450" y="118">기본 2MB 크기</text>
  <text class="s" x="450" y="152">LRU 로 관리: 꽉 차면</text><text class="s" x="450" y="170">가장 오래 안 쓴 항목을 내보냄</text>
  <text class="s" x="450" y="204">내보낼 항목이 바뀐 적 있으면(dirty)</text><text class="s" x="450" y="222">→ flash 의 매핑 page 를 갱신</text>
  <text class="s" x="450" y="256">(DFTL 이라는 방식)</text>
  <rect class="b" x="610" y="20" width="270" height="270" rx="10"/><text class="t" x="745" y="46">GTD — 매핑 page 의 위치</text><text class="s" x="745" y="66">Global Translation Directory</text>
  <text class="sl" x="630" y="96">MVPN → MPPN</text>
  <text class="s" x="745" y="126">MVPN = LPA ÷ (page 당 항목 수)</text><text class="s" x="745" y="144">= "이 LPA 의 매핑이 담긴</text><text class="s" x="745" y="160">매핑 page 번호"</text>
  <text class="s" x="745" y="194">MPPN = 그 매핑 page 가</text><text class="s" x="745" y="212">flash 의 어디에 있나</text>
  <text class="s" x="745" y="246">GTD 는 작아서 항상 DRAM 에</text>
</svg>
<div class="fig">그림 2-2-1. 매핑 표 세 개. 설정 Ideal_Mapping_Table=true 면 CMT 가 무한대라고 가정하고 매핑 page 입출력을 생략한다</div>

### 번역 — CMT hit 와 miss

<svg class="d2" viewBox="0 0 900 330" style="max-width:860px">
  <rect class="h" x="20" y="20" width="180" height="50" rx="8"/><text class="t" x="110" y="50">트랜잭션 (LPA)</text>
  <polygon points="330,15 450,45 330,75 210,45" class="y"/><text class="s" x="330" y="49">CMT 에 있나?</text>
  <path class="f" d="M200,45 L208,45"/>
  <rect class="g" x="520" y="20" width="360" height="50" rx="8"/><text class="t" x="700" y="42">hit: 바로 PPA 확정 → TSU 로</text><text class="s" x="700" y="60">추가 flash 접근 없음</text>
  <path class="f" d="M450,45 L518,45"/><text class="c" x="485" y="38">예</text>
  <path class="f" d="M330,75 L330,110"/><text class="c" x="350" y="98">아니오</text>
  <rect class="r" x="150" y="112" width="360" height="56" rx="8"/><text class="t" x="330" y="136">miss: 트랜잭션은 대기 목록으로</text><text class="s" x="330" y="156">Waiting_unmapped_read/program_transactions</text>
  <path class="f" d="M330,168 L330,196"/>
  <rect class="b" x="150" y="198" width="360" height="56" rx="8"/><text class="t" x="330" y="222">GTD 로 매핑 page 위치를 찾아</text><text class="s" x="330" y="242">매핑 page 를 flash 에서 읽음 (출처 MAPPING)</text>
  <path class="f" d="M330,254 L330,282"/>
  <rect class="g" x="150" y="284" width="360" height="40" rx="8"/><text class="s" x="330" y="308">읽기 완료 → CMT 에 넣고 → 대기하던 트랜잭션 번역·제출</text>
  <rect class="y" x="560" y="120" width="320" height="130" rx="8"/><text class="t" x="720" y="144">CMT 가 꽉 찼다면</text><text class="s" x="720" y="170">LRU 항목 하나를 쫓아냄</text><text class="s" x="720" y="190">dirty 면: 그 항목의 매핑 page 를</text><text class="s" x="720" y="208">읽어서(합치기) 새 위치에 다시 씀</text><text class="s" x="720" y="228">(매핑 read + 매핑 write)</text>
  <path class="fd" d="M510,140 L558,160"/>
</svg>
<div class="fig">그림 2-2-2. 번역 과정. miss 는 사용자 요청 하나에 flash 읽기(와 쓰기)를 더 붙인다 — 이것도 쓰기 증폭의 원인</div>

### 쓰기 = 새 자리 + 예전 자리 무효 (out-of-place update)

<svg class="d2" viewBox="0 0 900 260" style="max-width:860px">
  <text class="t" x="220" y="24">쓰기 전</text><text class="t" x="680" y="24">LPA 7 을 다시 쓴 후</text>
  <rect class="w" x="40" y="40" width="360" height="60" rx="6"/><text class="sl" x="50" y="58">block 17</text>
  <rect class="pv" x="60" y="66" width="30" height="26"/><rect class="pv" x="92" y="66" width="30" height="26"/><rect class="pv" x="124" y="66" width="30" height="26"/><rect class="pf" x="156" y="66" width="30" height="26"/><rect class="pf" x="188" y="66" width="30" height="26"/>
  <text class="s" x="107" y="112">↑ page 1 = LPA 7 (valid)</text>
  <rect class="w" x="40" y="150" width="360" height="60" rx="6"/><text class="sl" x="50" y="168">GMT</text><text class="sl" x="60" y="195">LPA 7 → block 17, page 1</text>
  <rect class="w" x="500" y="40" width="360" height="60" rx="6"/><text class="sl" x="510" y="58">block 17</text>
  <rect class="pv" x="520" y="66" width="30" height="26"/><rect class="pi" x="552" y="66" width="30" height="26"/><rect class="pv" x="584" y="66" width="30" height="26"/><rect class="pv" x="616" y="66" width="30" height="26"/><rect class="pf" x="648" y="66" width="30" height="26"/>
  <text class="s" x="567" y="112">page 1 → invalid</text><text class="s" x="631" y="128">page 3 = 새 LPA 7</text>
  <rect class="w" x="500" y="150" width="360" height="60" rx="6"/><text class="sl" x="510" y="168">GMT</text><text class="sl" x="520" y="195">LPA 7 → block 17, page 3</text>
  <path class="f" d="M400,70 L498,70"/>
  <text class="c" x="450" y="240">초록 = valid, 빨강 = invalid(쓰레기), 회색 = free. 새 page 는 그 순간의 "쓰기 전선(write frontier)" block 의 다음 칸 — 세션 2-3</text>
</svg>
<div class="fig">그림 2-2-3. out-of-place update: 같은 LPA 를 다시 쓰면 새 page 에 쓰고 예전 page 는 invalid</div>

**page 일부만 쓰는 경우**(Day 1 세션 1-4의 bitmap)는 한 단계가 더 있다: 새 page 에 page 전체를 써야 하므로, 이번에 안 쓰는 섹터를 **예전 page 에서 먼저 읽어온다**(update read). 쓰기 하나가 읽기+쓰기가 된다.

### LPA barrier — GC 와 사용자가 부딪힐 때

GC 가 어떤 page 를 옮기는 중인데 그 LPA 에 사용자 쓰기가 오면, 옮긴 결과와 새 쓰기가 뒤섞일 수 있다. 그래서 GC 가 옮기기 시작할 때 그 LPA 들을 **잠그고**(`Locked_LPAs`), 그동안 온 요청은 barrier 뒤에서 기다리게 한다. 이동이 끝나면 잠금을 풀고 기다리던 요청을 처리한다.

<svg class="d2" viewBox="0 0 900 170" style="max-width:860px">
  <rect class="r" x="20" y="50" width="200" height="60" rx="8"/><text class="t" x="120" y="76">GC: LPA 7 이동 시작</text><text class="s" x="120" y="96">→ LPA 7 잠금</text>
  <rect class="h" x="270" y="50" width="200" height="60" rx="8"/><text class="t" x="370" y="76">사용자: LPA 7 쓰기</text><text class="s" x="370" y="96">잠겨 있음 → barrier 뒤 대기</text>
  <rect class="g" x="520" y="50" width="160" height="60" rx="8"/><text class="t" x="600" y="76">GC 이동 완료</text><text class="s" x="600" y="96">잠금 해제</text>
  <rect class="b" x="730" y="50" width="160" height="60" rx="8"/><text class="t" x="810" y="76">대기 요청 처리</text>
  <path class="f" d="M220,80 L268,80"/><path class="f" d="M470,80 L518,80"/><path class="f" d="M680,80 L728,80"/>
  <text class="c" x="450" y="145">매핑 page 이동에도 같은 방식의 잠금(Locked_MVPNs)이 있다</text>
</svg>
<div class="fig">그림 2-2-4. LPA barrier</div>

<div class="check" markdown="1">
**확인 질문**
1. GMT, CMT, GTD 는 각각 무엇을 무엇으로 대응시키고, 어디에 있나?
2. CMT miss 인 쓰기 하나는 flash 명령을 최대 몇 개 만들 수 있나? (사용자 쓰기 + 매핑 read + dirty 항목을 내보내며 생기는 매핑 read/write)
3. 같은 LPA 를 세 번 쓰면(캐시 없이) invalid page 는 몇 개 생기나?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-2-3">세션 2-3 · block 관리 — write frontier, free pool, page 상태 (1시간)</h2>

### 플레인 하나의 장부

`Flash_Block_Manager`(FBM)는 플레인마다 장부(`PlaneBookKeepingType`)를 하나씩 들고 있다.

<svg class="d2" viewBox="0 0 900 360" style="max-width:860px">
  <rect class="w" x="10" y="10" width="880" height="340" rx="12"/><text class="t" x="450" y="34">플레인 하나의 장부 (PlaneBookKeepingType)</text>
  <rect class="y" x="30" y="50" width="250" height="170" rx="8"/><text class="t" x="155" y="74">빈 block 모음</text><text class="s" x="155" y="92">Free_block_pool (erase 횟수 순)</text>
  <rect class="w" x="50" y="104" width="210" height="24"/><text class="sl" x="60" y="121">erase 3 → block 402</text>
  <rect class="w" x="50" y="128" width="210" height="24"/><text class="sl" x="60" y="145">erase 3 → block 17</text>
  <rect class="w" x="50" y="152" width="210" height="24"/><text class="sl" x="60" y="169">erase 5 → block 88</text>
  <text class="s" x="155" y="200">꺼낼 땐 항상 맨 앞(가장 덜 닳은 것)</text>
  <rect class="g" x="310" y="50" width="280" height="170" rx="8"/><text class="t" x="450" y="74">쓰기 전선 (write frontier)</text><text class="s" x="450" y="92">stream(flow) 마다 3개씩</text>
  <text class="sl" x="330" y="122">Data_wf — 사용자 데이터</text><text class="sl" x="330" y="146">GC_wf — GC 가 옮기는 데이터</text><text class="sl" x="330" y="170">Translation_wf — 매핑 page</text>
  <text class="s" x="450" y="200">각각 "지금 채우고 있는 block"</text>
  <rect class="b" x="620" y="50" width="250" height="170" rx="8"/><text class="t" x="745" y="74">block 2048 개의 상태</text>
  <text class="sl" x="640" y="104">Current_page_write_index</text><text class="sl" x="640" y="120">  — 다음에 쓸 page 번호</text>
  <text class="sl" x="640" y="144">Invalid_page_count, bitmap</text><text class="sl" x="640" y="160">  — 어느 page 가 invalid 인가</text>
  <text class="sl" x="640" y="184">Erase_count — 몇 번 지웠나</text><text class="sl" x="640" y="204">Stream_id, 매핑용 여부 …</text>
  <text class="sl" x="40" y="252">플레인 합계: Free_pages_count, Valid_pages_count, Invalid_pages_count</text>
  <text class="sl" x="40" y="276">진행 중 GC 목록: Ongoing_erase_operations</text>
  <text class="sl" x="40" y="300">FIFO 정책용 할당 순서: Block_usage_history</text>
  <text class="c" x="450" y="334">stream 마다 frontier 가 따로라서, 서로 다른 flow 의 데이터는 같은 block 에 섞이지 않는다</text>
</svg>
<div class="fig">그림 2-3-1. 플레인 장부의 세 부분: 빈 block 모음, 쓰기 전선, block 별 상태</div>

### page 쓰기 할당과 전선 교체

<svg class="d2" viewBox="0 0 900 250" style="max-width:860px">
  <text class="sl" x="20" y="28">Data_wf = block 17 (write index = 254 / 256)</text>
  <rect class="w" x="20" y="40" width="560" height="44" rx="6"/>
  <rect class="pv" x="30" y="48" width="24" height="28"/><rect class="pi" x="56" y="48" width="24" height="28"/><rect class="pv" x="82" y="48" width="24" height="28"/><text class="s" x="150" y="67">… (254개 사용)</text><rect class="pv" x="480" y="48" width="24" height="28"/><rect class="pf" x="508" y="48" width="24" height="28"/><rect class="pf" x="536" y="48" width="24" height="28"/>
  <text class="c" x="520" y="100">↑ 다음 쓰기는 여기, 그다음 마지막 칸</text>
  <path class="f" d="M580,62 L640,62"/>
  <rect class="y" x="645" y="30" width="235" height="70" rx="8"/><text class="t" x="762" y="56">block 이 가득 차면</text><text class="s" x="762" y="78">free pool 맨 앞 block 을 새 전선으로</text>
  <path class="f" d="M762,100 L762,140"/>
  <rect class="r" x="620" y="142" width="270" height="80" rx="8"/><text class="t" x="755" y="166">GC 검사</text><text class="s" x="755" y="188">빈 block 수 &lt; GC 임계값?</text><text class="s" x="755" y="206">→ 세션 2-4</text>
  <text class="sl" x="20" y="150">page 는 반드시 block 안에서 0, 1, 2 … 순서대로만 쓴다</text>
  <text class="sl" x="20" y="174">(flash 규칙: 블록 안 순차 쓰기)</text>
  <text class="sl" x="20" y="210">빈 block 을 꺼낼 때 가장 덜 닳은 것을 고르는 것 = 동적 마모평준화</text>
</svg>
<div class="fig">그림 2-3-2. 쓰기 전선이 차면 가장 덜 닳은 빈 block 으로 교체하고, 그때 GC 가 필요한지 본다</div>

### page 의 일생과 block 의 일생

<svg class="d2" viewBox="0 0 900 260" style="max-width:860px">
  <text class="t" x="220" y="24">page</text>
  <circle cx="80" cy="110" r="50" class="pf"/><text class="t" x="80" y="115">free</text>
  <circle cx="220" cy="110" r="50" class="pv"/><text class="t" x="220" y="115">valid</text>
  <circle cx="360" cy="110" r="50" class="pi"/><text class="t" x="360" y="115">invalid</text>
  <path class="f" d="M130,110 L168,110"/><text class="c" x="150" y="98">쓰기</text>
  <path class="f" d="M270,110 L308,110"/><text class="c" x="290" y="98">덮어씀/GC 이동</text>
  <path class="fd" d="M360,160 C360,220 80,220 80,162"/><text class="c" x="220" y="235">block 전체 erase</text>
  <text class="t" x="680" y="24">block</text>
  <rect class="y" x="480" y="60" width="120" height="50" rx="8"/><text class="t" x="540" y="90">free pool</text>
  <rect class="g" x="640" y="60" width="120" height="50" rx="8"/><text class="t" x="700" y="90">쓰기 전선</text>
  <rect class="b" x="780" y="60" width="110" height="50" rx="8"/><text class="t" x="835" y="90">가득 참</text>
  <rect class="r" x="700" y="160" width="140" height="50" rx="8"/><text class="t" x="770" y="182">GC victim</text><text class="s" x="770" y="200">valid 옮기는 중</text>
  <path class="f" d="M600,85 L638,85"/><path class="f" d="M760,85 L778,85"/><path class="f" d="M835,110 L800,158"/><path class="f" d="M700,185 L540,112"/><text class="c" x="590" y="165">erase (횟수+1)</text>
</svg>
<div class="fig">그림 2-3-3. page 는 free → valid → invalid → (erase) → free, block 은 free pool → 전선 → 가득 참 → victim → free pool</div>

<div class="check" markdown="1">
**확인 질문**
1. stream 마다 쓰기 전선이 세 개인 이유는? 각각 무엇을 담나?
2. free pool 에서 block 을 꺼낼 때 무엇을 기준으로 고르나? 그게 어떤 FTL 기능인가?
3. 왜 GC 검사는 "block 이 가득 차서 전선을 바꿀 때" 하는 걸까?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-2-4">세션 2-4 · GC 와 마모평준화 (1시간)</h2>

### GC 는 언제 시작하나

<svg class="d2" viewBox="0 0 900 230" style="max-width:860px">
  <text class="sl" x="20" y="28">플레인의 빈 block 수 (기본: 2048 중)</text>
  <rect class="w" x="20" y="40" width="860" height="40" rx="6"/>
  <rect x="20" y="40" width="120" height="40" fill="#fdedec" stroke="#c0392b"/>
  <text class="s" x="80" y="65">GC 시작 구간</text>
  <line x1="140" y1="32" x2="140" y2="92" stroke="#c0392b" stroke-width="2" stroke-dasharray="5 4"/>
  <text class="sl" x="146" y="106">GC 임계값 = GC_Exec_Threshold(0.05) × 2048 = 102 block</text>
  <text class="sl" x="146" y="124">(최소 10 — 평면당 동시에 돌 수 있는 GC 수 max_ongoing_gc_reqs_per_plane)</text>
  <line x1="40" y1="32" x2="40" y2="92" stroke="#922b21" stroke-width="2"/>
  <text class="sl" x="30" y="150">빈 block 이 더 적어지면(10 미만) 사용자 쓰기 자체를 멈추고 GC 만 돌린다</text>
  <text class="sl" x="30" y="170">GC_Hard_Threshold(0.005) 아래면 GC 가 "급한 상태" → 스케줄러가 GC 명령을 우선 (세션 2-5)</text>
  <text class="c" x="450" y="210">검사 시점: 쓰기 전선이 새 block 으로 바뀔 때, 그리고 GC 의 erase 가 끝났을 때</text>
</svg>
<div class="fig">그림 2-4-1. GC 트리거 — 빈 block 수가 임계값 아래로 내려가면</div>

### 누구를 청소하나 — victim 선택 정책 6가지

<svg class="d2" viewBox="0 0 900 300" style="max-width:860px">
  <text class="sl" x="20" y="24">예: 다 쓴 block 들과 각자의 invalid page 수 (많을수록 청소 이득)</text>
  <rect class="w" x="20" y="36" width="100" height="40" rx="4"/><text class="s" x="70" y="61">A: 200</text>
  <rect class="w" x="130" y="36" width="100" height="40" rx="4"/><text class="s" x="180" y="61">B: 30</text>
  <rect class="w" x="240" y="36" width="100" height="40" rx="4"/><text class="s" x="290" y="61">C: 150</text>
  <rect class="w" x="350" y="36" width="100" height="40" rx="4"/><text class="s" x="400" y="61">D: 0</text>
  <rect class="w" x="460" y="36" width="100" height="40" rx="4"/><text class="s" x="510" y="61">E: 90</text>
  <text class="sl" x="580" y="52">A 를 고르면 56 page 만 옮기고</text><text class="sl" x="580" y="70">block 하나를 되찾음 (가장 쌈)</text>
  <rect class="b" x="20" y="100" width="420" height="190" rx="8"/>
  <text class="sl" x="35" y="126">GREEDY — 전부 보고 invalid 최다(A)</text>
  <text class="sl" x="35" y="152">RGA — 무작위로 d개(log₂ block 수) 뽑아</text><text class="sl" x="35" y="168">          그중 invalid 최다 ← 기본값</text>
  <text class="sl" x="35" y="194">RANDOM — 아무 block 이나 무작위</text>
  <text class="sl" x="35" y="220">RANDOM_P — 다 쓴 block 중 무작위</text>
  <text class="sl" x="35" y="246">RANDOM_PP — invalid 가 일정 수 이상인 것 중 무작위</text>
  <text class="sl" x="35" y="272">FIFO — 가장 먼저 쓰기 시작한 block</text>
  <rect class="y" x="460" y="100" width="420" height="190" rx="8"/>
  <text class="t" x="670" y="126">공통 조건 (안전한 후보)</text>
  <text class="sl" x="475" y="156">• 지금 쓰기 전선이 아닐 것</text>
  <text class="sl" x="475" y="180">• 진행 중인 쓰기가 없을 것</text>
  <text class="sl" x="475" y="204">• 이미 GC 중이 아닐 것</text>
  <text class="sl" x="475" y="236">RGA 가 기본인 이유: GREEDY 에 가깝게 좋으면서</text><text class="sl" x="475" y="254">2048 개를 매번 다 보지 않아도 됨</text>
  <text class="c" x="670" y="280">(원본에서 이 공통 조건 확인이 일부 정책에서 빠져 있었다 — 버그 목록 참고)</text>
</svg>
<div class="fig">그림 2-4-2. victim 선택 정책. invalid 가 많을수록 옮길 valid page 가 적어 GC 가 싸다</div>

### GC 한 번의 흐름

<svg class="d2" viewBox="0 0 900 400" style="max-width:860px">
  <rect class="r" x="20" y="20" width="240" height="60" rx="8"/><text class="t" x="140" y="46">① victim 선택</text><text class="s" x="140" y="66">block 에 "GC 중" 표시</text>
  <rect class="r" x="330" y="20" width="240" height="60" rx="8"/><text class="t" x="450" y="46">② valid page 의 LPA 잠금</text><text class="s" x="450" y="66">(LPA barrier)</text>
  <rect class="y" x="640" y="20" width="240" height="60" rx="8"/><text class="t" x="760" y="46">③ 진행 중 요청 있나?</text><text class="s" x="760" y="66">있으면 끝날 때까지 대기(park)</text>
  <path class="f" d="M260,50 L328,50"/><path class="f" d="M570,50 L638,50"/>
  <path class="f" d="M760,80 L760,110"/>
  <rect class="b" x="560" y="112" width="320" height="70" rx="8"/><text class="t" x="720" y="136">④ erase 1개 + valid page 마다 GC read</text><text class="s" x="720" y="156">TSU 에 제출. erase 는 이동이 다 끝날 때까지</text><text class="s" x="720" y="172">큐에서 기다림</text>
  <path class="f" d="M560,147 L480,147"/>
  <rect class="b" x="160" y="112" width="320" height="70" rx="8"/><text class="t" x="320" y="136">⑤ GC read 완료</text><text class="s" x="320" y="156">GC_wf 에 새 page 할당 · 매핑 갱신</text><text class="s" x="320" y="172">→ GC write 제출</text>
  <path class="f" d="M320,182 L320,212"/>
  <rect class="b" x="160" y="214" width="320" height="60" rx="8"/><text class="t" x="320" y="238">⑥ GC write 완료</text><text class="s" x="320" y="258">그 LPA 잠금 해제 (대기 요청 처리)</text>
  <path class="f" d="M480,244 L558,244"/>
  <rect class="g" x="560" y="214" width="320" height="60" rx="8"/><text class="t" x="720" y="238">⑦ 모든 이동이 끝나면 erase 실행</text><text class="s" x="720" y="258">3.8 ms</text>
  <path class="f" d="M720,274 L720,304"/>
  <rect class="g" x="560" y="306" width="320" height="70" rx="8"/><text class="t" x="720" y="330">⑧ erase 완료</text><text class="s" x="720" y="350">block → free pool (erase 횟수+1)</text><text class="s" x="720" y="366">빈 page 기다리던 쓰기 재개 · GC 재검사</text>
  <text class="sl" x="20" y="320">GC 비용 = valid page 수 × (읽기 + 쓰기)</text><text class="sl" x="20" y="344">+ erase 1번</text>
  <text class="sl" x="20" y="376">옮긴 쓰기는 호스트가 요청하지 않은 쓰기 → WAF 증가</text>
</svg>
<div class="fig">그림 2-4-3. GC 한 번: 선택 → 잠금 → (대기) → 읽기·쓰기로 이동 → erase → free pool</div>

### WAF — GC 가 치르는 대가

**WAF**(Write Amplification Factor) = flash 에 실제로 쓴 page 수 ÷ 호스트가 쓴 page 수. GC 가 옮긴 page, 매핑 page 쓰기가 전부 분자에 더해진다. over-provisioning(OP, 기본 7% — 호스트에게 안 보여주는 여유 공간)이 클수록 victim 에 invalid 가 더 쌓여서 WAF 가 내려간다.

### 마모평준화 두 가지

<svg class="d2" viewBox="0 0 900 290" style="max-width:860px">
  <rect class="g" x="20" y="20" width="420" height="250" rx="10"/><text class="t" x="230" y="46">동적 WL (dynamic)</text>
  <text class="s" x="230" y="74">새 쓰기 전선을 고를 때</text><text class="s" x="230" y="92">가장 덜 닳은 빈 block 을 준다</text>
  <rect class="w" x="60" y="120" width="60" height="40"/><text class="s" x="90" y="145">3회</text>
  <rect class="w" x="130" y="120" width="60" height="40"/><text class="s" x="160" y="145">3회</text>
  <rect class="w" x="200" y="120" width="60" height="40"/><text class="s" x="230" y="145">5회</text>
  <path class="f" d="M90,160 L90,200"/><text class="s" x="120" y="218">이것부터 사용</text>
  <text class="s" x="230" y="248">비용 없음. 하지만 빈 block 사이에서만 고르므로</text><text class="s" x="230" y="264">한 번 쓰고 안 바뀌는 데이터가 붙잡은 block 은 못 건드림</text>
  <rect class="y" x="460" y="20" width="420" height="250" rx="10"/><text class="t" x="670" y="46">정적 WL (static)</text>
  <text class="s" x="670" y="74">가장 많이 지운 block 과 가장 적게 지운 block 의</text><text class="s" x="670" y="92">erase 횟수 차이 ≥ 임계값(기본 100) 이면</text>
  <rect class="w" x="520" y="120" width="80" height="40"/><text class="s" x="560" y="137">cold</text><text class="s" x="560" y="152">0회</text>
  <rect class="w" x="740" y="120" width="80" height="40"/><text class="s" x="780" y="137">hot</text><text class="s" x="780" y="152">120회</text>
  <path class="f" d="M600,140 L738,140"/><text class="c" x="670" y="132">차이 120</text>
  <text class="s" x="670" y="190">덜 닳은 block 의 (cold) 데이터를 다른 곳으로 옮기고</text><text class="s" x="670" y="208">그 block 을 지워 다시 쓰이게 한다</text>
  <text class="s" x="670" y="240">옮기는 방식은 GC 와 같다(같은 코드 경로)</text><text class="s" x="670" y="258">erase 가 끝날 때마다 필요 여부를 검사</text>
</svg>
<div class="fig">그림 2-4-4. 동적 WL 은 "빈 block 중 덜 닳은 것부터", 정적 WL 은 "안 바뀌는 데이터를 억지로 옮겨서"</div>

<div class="check" markdown="1">
**확인 질문**
1. 기본 설정에서 GC 는 빈 block 이 몇 개 아래로 내려가면 시작하나?
2. invalid 200, valid 56 인 block 을 청소하면 flash 명령이 몇 개 생기나? (read, write, erase 각각)
3. 동적 WL 만으로는 해결 못 하는 상황은? 정적 WL 은 그걸 어떻게 해결하나?
</div>

<div style="margin-top: 60px;"></div>

<h2 id="session-2-5">세션 2-5 · TSU · PHY · flash 칩, 그리고 총정리 (1시간)</h2>

### TSU — 칩마다 큐 7개

FTL 이 만든 flash 트랜잭션은 모두 **TSU**(Transaction Scheduling Unit)에 들어간다. TSU 는 **칩마다** 종류별 큐를 가진다. 기본 스케줄러는 `TSU_Priority_OutOfOrder` — 도착 순서보다 종류와 우선순위를 본다.

<svg class="d2" viewBox="0 0 900 330" style="max-width:860px">
  <rect class="w" x="20" y="20" width="560" height="290" rx="10"/><text class="t" x="300" y="44">칩 하나의 큐 (채널 × 칩 마다)</text>
  <rect class="h" x="40" y="60" width="250" height="32" rx="4"/><text class="sl" x="50" y="81">MappingReadTRQueue</text>
  <rect class="h" x="40" y="96" width="250" height="32" rx="4"/><text class="sl" x="50" y="117">UserReadTRQueue (우선순위별)</text>
  <rect class="r" x="40" y="132" width="250" height="32" rx="4"/><text class="sl" x="50" y="153">GCReadTRQueue</text>
  <rect class="h" x="310" y="60" width="250" height="32" rx="4"/><text class="sl" x="320" y="81">MappingWriteTRQueue</text>
  <rect class="h" x="310" y="96" width="250" height="32" rx="4"/><text class="sl" x="320" y="117">UserWriteTRQueue (우선순위별)</text>
  <rect class="r" x="310" y="132" width="250" height="32" rx="4"/><text class="sl" x="320" y="153">GCWriteTRQueue</text>
  <rect class="r" x="175" y="176" width="250" height="32" rx="4"/><text class="sl" x="185" y="197">GCEraseTRQueue</text>
  <text class="sl" x="40" y="236">사용자 쓰기와 캐시 write-back(CACHE)은 UserWrite 큐로,</text>
  <text class="sl" x="40" y="256">GC/WL 이동은 GC 큐로, 매핑 page 입출력은 Mapping 큐로</text>
  <text class="sl" x="40" y="286">우선순위 클래스: URGENT, HIGH, MEDIUM, LOW (flow 마다 지정)</text>
  <rect class="y" x="610" y="20" width="270" height="290" rx="10"/><text class="t" x="745" y="44">Schedule() 의 순서</text>
  <text class="sl" x="625" y="76">채널마다 (채널이 쉬고 있으면):</text>
  <text class="sl" x="625" y="100">  칩을 돌아가며(round-robin)</text>
  <text class="sl" x="625" y="124">    ① 읽기를 보낼 수 있나?</text>
  <text class="sl" x="625" y="144">       매핑 읽기 먼저,</text>
  <text class="sl" x="625" y="164">       GC 가 급하면 GC 읽기도</text>
  <text class="sl" x="625" y="188">    ② 아니면 쓰기</text>
  <text class="sl" x="625" y="212">    ③ 아니면 erase</text>
  <text class="sl" x="625" y="244">  채널이 바빠지면 그 채널은</text><text class="sl" x="625" y="262">  다음 기회로</text>
  <text class="c" x="745" y="296">읽기 우선 = 사용자 지연을 줄이려고</text>
</svg>
<div class="fig">그림 2-5-1. TSU 의 큐 7종과 스케줄 순서</div>

같은 칩에 보낼 트랜잭션 중 **같은 다이의 서로 다른 플레인**으로 가는 것들은 하나의 multi-plane 명령으로 묶어 동시에 보낸다.

### 채널과 칩 — 전송은 한 번에 하나, 실행은 동시에

<svg class="d2" viewBox="0 0 900 250" style="max-width:860px">
  <text class="sl" x="20" y="24">채널 0 에 칩 4개. 채널(버스)은 한 번에 한 칩의 명령/데이터만 전송, 칩들은 각자 실행</text>
  <text class="sl" x="20" y="64">채널</text>
  <rect x="80" y="48" width="40" height="24" fill="#5d6d7e"/><rect x="130" y="48" width="40" height="24" fill="#5d6d7e"/><rect x="180" y="48" width="40" height="24" fill="#5d6d7e"/><rect x="480" y="48" width="60" height="24" fill="#5d6d7e"/>
  <text class="sl" x="20" y="104">칩 0</text><rect x="80" y="88" width="40" height="24" fill="#5d6d7e"/><rect x="120" y="88" width="330" height="24" fill="#58d68d"/><text class="s" x="285" y="105">쓰기 750µs</text>
  <text class="sl" x="20" y="144">칩 1</text><rect x="130" y="128" width="40" height="24" fill="#5d6d7e"/><rect x="170" y="128" width="40" height="24" fill="#f5b041"/><text class="s" x="190" y="170"></text><rect x="480" y="128" width="60" height="24" fill="#5d6d7e"/><text class="s" x="240" y="145">읽기 75µs</text>
  <text class="sl" x="20" y="184">칩 2</text><rect x="180" y="168" width="40" height="24" fill="#5d6d7e"/><rect x="220" y="168" width="600" height="24" fill="#ec7063"/><text class="s" x="520" y="185">erase 3.8ms</text>
  <text class="c" x="450" y="225">회색 = 채널로 명령·데이터 전송, 색 = 칩 내부 실행. 칩 1 의 읽기 데이터는 채널이 비었을 때 가져온다(오른쪽 회색)</text>
</svg>
<div class="fig">그림 2-5-2. 채널은 공유, 칩은 병렬 — 칩이 많을수록 느린 연산을 겹쳐서 처리한다</div>

### 칩의 상태 (PHY 가 칩마다 기록)

<svg class="d2" viewBox="0 0 900 260" style="max-width:860px">
  <rect class="g" x="20" y="100" width="100" height="50" rx="25"/><text class="t" x="70" y="130">IDLE</text>
  <rect class="b" x="170" y="100" width="130" height="50" rx="25"/><text class="t" x="235" y="122">CMD_IN</text><text class="s" x="235" y="140">명령(+쓸 데이터) 전송</text>
  <rect class="h" x="350" y="20" width="140" height="50" rx="25"/><text class="t" x="420" y="50">READING</text>
  <rect class="h" x="350" y="100" width="140" height="50" rx="25"/><text class="t" x="420" y="130">WRITING</text>
  <rect class="r" x="350" y="180" width="140" height="50" rx="25"/><text class="t" x="420" y="210">ERASING</text>
  <rect class="y" x="540" y="20" width="170" height="50" rx="25"/><text class="t" x="625" y="42">WAIT_FOR_DATA_OUT</text><text class="s" x="625" y="60">채널 비길 기다림</text>
  <rect class="b" x="750" y="20" width="130" height="50" rx="25"/><text class="t" x="815" y="42">DATA_OUT</text><text class="s" x="815" y="60">읽은 데이터 전송</text>
  <path class="f" d="M120,125 L168,125"/><path class="f" d="M300,115 L348,50"/><path class="f" d="M300,125 L348,125"/><path class="f" d="M300,135 L348,200"/>
  <path class="f" d="M490,45 L538,45"/><path class="f" d="M710,45 L748,45"/>
  <path class="fd" d="M815,70 C815,250 70,250 70,152"/><path class="fd" d="M490,125 C520,125 520,240 120,240 L100,152"/>
  <text class="c" x="620" y="150">쓰기·erase 는 끝나면 바로 IDLE</text>
  <text class="c" x="620" y="170">(완료 → FTL·캐시·Host Interface 에 알림)</text>
</svg>
<div class="fig">그림 2-5-3. 칩 상태 기계 (ChipStatus). 읽기만 데이터를 다시 채널로 보내는 단계가 있다</div>

### suspend — 긴 작업을 잠깐 멈추고 읽기 먼저

erase(3.8ms)나 쓰기(750µs) 중인 칩에 급한 읽기가 오면, 기다리는 대신 **그 작업을 일시정지**하고 읽기를 먼저 한 뒤 **재개**할 수 있다(설정 CMD_Suspension_Support, 기본 ERASE). 남은 시간이 짧으면(예: erase 가 0.7ms 안에 끝날 예정) 그냥 기다린다.

<svg class="d2" viewBox="0 0 900 170" style="max-width:860px">
  <text class="sl" x="20" y="30">suspend 없음</text>
  <rect x="140" y="16" width="500" height="22" fill="#ec7063"/><text class="s" x="390" y="32">erase</text><rect x="640" y="16" width="60" height="22" fill="#f5b041"/><text class="s" x="670" y="32">읽기</text>
  <text class="c" x="780" y="32">읽기가 erase 끝까지 대기</text>
  <text class="sl" x="20" y="90">suspend 있음</text>
  <rect x="140" y="76" width="150" height="22" fill="#ec7063"/><rect x="290" y="76" width="20" height="22" fill="#5d6d7e"/><rect x="310" y="76" width="60" height="22" fill="#f5b041"/><text class="s" x="340" y="92">읽기</text><rect x="370" y="76" width="350" height="22" fill="#ec7063"/><text class="s" x="545" y="92">erase 나머지</text>
  <text class="c" x="300" y="120">↑ 멈춤</text><text class="c" x="380" y="120">↑ 재개</text>
  <text class="c" x="450" y="155">읽기는 훨씬 빨리 끝나고, erase 는 조금 늦게 끝난다 — 사용자 읽기 지연(특히 최악)을 줄이는 장치</text>
</svg>
<div class="fig">그림 2-5-4. suspend/resume (원본에서는 이 경로가 여러 버그 때문에 실제로 동작하지 않았다 — 버그 목록 #14~17)</div>

### 완료는 어떻게 퍼지나

칩이 작업을 끝내면 PHY 가 **"트랜잭션 완료" 신호를 broadcast** 한다. 이 신호를 구독한 부품들(`Setup_triggers` 에서 등록)이 각자 할 일을 한다: 캐시는 back-pressure 를 줄이고, 매핑 유닛은 매핑 page 결과를 CMT 에 넣고, GC 유닛은 이동의 다음 단계를 진행하고, Host Interface 는 요청의 조각이 다 끝났는지 세어 CQ 에 완료를 쓴다.

<svg class="d2" viewBox="0 0 900 200" style="max-width:860px">
  <rect class="g" x="20" y="70" width="170" height="60" rx="8"/><text class="t" x="105" y="96">칩: 작업 완료</text><text class="s" x="105" y="116">→ PHY</text>
  <rect class="y" x="240" y="70" width="170" height="60" rx="8"/><text class="t" x="325" y="96">PHY: 완료 신호</text><text class="s" x="325" y="116">broadcast</text>
  <rect class="b" x="480" y="10" width="200" height="40" rx="6"/><text class="s" x="580" y="35">DRAM 캐시 — back-pressure 감소</text>
  <rect class="b" x="480" y="58" width="200" height="40" rx="6"/><text class="s" x="580" y="83">AMU — 매핑 page 결과 반영</text>
  <rect class="b" x="480" y="106" width="200" height="40" rx="6"/><text class="s" x="580" y="131">GC/WL — 이동 다음 단계</text>
  <rect class="b" x="480" y="154" width="200" height="40" rx="6"/><text class="s" x="580" y="179">TSU — 다음 명령 스케줄</text>
  <rect class="h" x="720" y="70" width="160" height="60" rx="8"/><text class="t" x="800" y="96">Host Interface</text><text class="s" x="800" y="116">요청 조각 다 끝나면 CQ</text>
  <path class="f" d="M190,100 L238,100"/><path class="f" d="M410,95 L478,30"/><path class="f" d="M410,98 L478,78"/><path class="f" d="M410,102 L478,126"/><path class="f" d="M410,106 L478,174"/><path class="f" d="M680,30 L718,85"/>
</svg>
<div class="fig">그림 2-5-5. 완료 신호의 전파 — 신호(콜백) 방식이라 부품끼리 서로를 몰라도 된다</div>

### 총정리 — 쓰기 하나의 일생

LPA 7 에 대한 4KB 쓰기 하나가, 캐시가 이미 LPA 7 을 한 번 본 적 있고 CMT 에도 있는 상황에서 겪는 일. Day 1 과 Day 2 가 한 줄로 이어진다.

<svg class="d2" viewBox="0 0 900 560" style="max-width:860px">
  <rect class="h" x="20" y="10" width="420" height="40" rx="6"/><text class="sl" x="32" y="35">1. IO flow 가 요청 생성 → SQ + doorbell   (Day 1 · 1-3, 1-4)</text>
  <rect class="b" x="20" y="60" width="420" height="40" rx="6"/><text class="sl" x="32" y="85">2. Host Interface 가 가져와 LPA 7 트랜잭션 1개로   (1-4)</text>
  <rect class="y" x="20" y="110" width="420" height="40" rx="6"/><text class="sl" x="32" y="135">3. 캐시: 이미 본 LPA → DRAM 에 쓰고 요청 완료   (1-5)</text>
  <rect class="g" x="20" y="160" width="420" height="40" rx="6"/><text class="sl" x="32" y="185">4. CQ 완료 → 호스트가 다음 요청 생성</text>
  <text class="c" x="230" y="222">… 시간이 흘러 캐시가 차고, LPA 7 칸이 LRU 로 쫓겨난다 …</text>
  <rect class="y" x="460" y="240" width="420" height="40" rx="6"/><text class="sl" x="472" y="265">5. 쫓겨난 dirty 칸 → CACHE 쓰기 트랜잭션   (1-5)</text>
  <rect class="b" x="460" y="290" width="420" height="40" rx="6"/><text class="sl" x="472" y="315">6. AMU: CMT hit → CWDP 로 플레인 결정   (2-1, 2-2)</text>
  <rect class="b" x="460" y="340" width="420" height="40" rx="6"/><text class="sl" x="472" y="365">7. FBM: Data_wf 의 다음 page, 예전 page 는 invalid   (2-2, 2-3)</text>
  <rect class="r" x="460" y="390" width="420" height="40" rx="6"/><text class="sl" x="472" y="415">8. (전선이 가득 찼다면) 새 block + GC 검사   (2-3, 2-4)</text>
  <rect class="b" x="460" y="440" width="420" height="40" rx="6"/><text class="sl" x="472" y="465">9. TSU: 그 칩의 UserWrite 큐 → 차례가 오면 전송   (2-5)</text>
  <rect class="g" x="460" y="490" width="420" height="50" rx="6"/><text class="sl" x="472" y="512">10. PHY → 칩 WRITING 750µs → 완료 broadcast →</text><text class="sl" x="472" y="530">      캐시 back-pressure 감소   (2-5)</text>
  <path class="f" d="M230,50 L230,58"/><path class="f" d="M230,100 L230,108"/><path class="f" d="M230,150 L230,158"/>
  <path class="fd" d="M440,180 C520,180 670,200 670,238"/>
  <path class="f" d="M670,280 L670,288"/><path class="f" d="M670,330 L670,338"/><path class="f" d="M670,380 L670,388"/><path class="f" d="M670,430 L670,438"/><path class="f" d="M670,480 L670,488"/>
  <text class="sl" x="20" y="300">호스트가 보는 쓰기 지연 = 1~4</text><text class="sl" x="20" y="320">(DRAM 쓰기 시간 정도)</text>
  <text class="sl" x="20" y="360">flash 쓰기(5~10)는 나중에, 호스트 모르게</text>
  <text class="sl" x="20" y="400">하지만 캐시가 flash 를 못 따라가면</text><text class="sl" x="20" y="420">back-pressure 로 3단계가 막혀 결국 호스트도 느려진다</text>
  <text class="sl" x="20" y="460">GC 가 돌면 9단계에서 GC 명령과 경쟁 →</text><text class="sl" x="20" y="480">사용자 읽기·쓰기가 느려진다</text>
</svg>
<div class="fig">그림 2-5-6. 캡스톤 — 쓰기 하나의 일생 (괄호는 해당 세션)</div>

이 그림을 보지 않고 1~10을 말로 설명할 수 있으면, [개발 계획](/ftl-visual-simulator/plan/full-plan/) Session 12 의 캡스톤("host write 요청 하나를 매핑 → GC → flash 까지 설명")을 통과한 것이다. 앱의 로그에서 LPN 하나를 클릭해 5~10단계가 실제로 어떻게 보이는지 확인해보자.

<div class="check" markdown="1">
**확인 질문**
1. TSU 가 한 칩에서 읽기·쓰기·erase 중 무엇을 먼저 보내나? 왜?
2. 칩이 많으면 왜 빨라지나? 채널이 하나뿐이어도 효과가 있나?
3. 읽기 한 번에서 칩이 거치는 상태를 순서대로 말해보자.
4. suspend 가 없으면 erase 중인 칩에 온 읽기는 최대 얼마나 기다리나?
</div>

<div style="margin-top: 60px;"></div>

## 다음 단계

- 코드를 직접 열어보고 싶다면: [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/)의 "주요 콜 플로우" 8개가 오늘 그림들의 함수 이름판이다.
- 원본이 어디서 틀렸는지: [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/upstream-diff/) — 오늘 배운 부품(A4 GC 선정, A5 스케줄러·suspend, A6 WL, A7 barrier·멈춤)별로 정리돼 있다.

[← Day 1](/ftl-visual-simulator/reference/mqsim/study-guide/day1/) · [목차](/ftl-visual-simulator/reference/mqsim/study-guide/)
