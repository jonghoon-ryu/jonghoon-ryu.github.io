---
layout: default
title: 4. Write cliff
permalink: /old-ssd-experiments/4-write-cliff/
---
<style>
.glance { display:grid; grid-template-columns: 9rem 1fr; gap:4px 14px; background:#f4f8f6; border:1px solid #cfe3db; border-left:4px solid #1f6f5c; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.glance b { color:#1f6f5c; }
.warn { background:#fdf2f0; border-left:4px solid #c0392b; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.result { background:#fffbea; border:1px dashed #b7950b; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2.5rem 0 0; font-size:0.95rem; }
table.t { table-layout:fixed !important; width:100% !important; border-collapse:collapse; font-size:0.86rem; margin:1rem 0; }
table.t th { background:#e8f3ef !important; color:#1f3d34 !important; text-align:left; padding:6px 8px; border:1px solid #cfe3db; overflow-wrap:break-word; word-break:break-word; }
table.t td { padding:6px 8px; border:1px solid #e5e8e8; vertical-align:top; overflow-wrap:break-word; word-break:break-word; }
table.t code { font-size:0.82rem; }
@media (max-width: 640px) { .glance { grid-template-columns: 1fr; } }
</style>

# 4. Write cliff : GC 가 눈에 보이는 순간

<div class="glance">
<b>목표</b><span>빈 드라이브에 4 KiB 랜덤 쓰기를 용량의 2배만큼 계속하며, 빈 블록이 바닥나 GC 가 시작될 때 IOPS 가 어떻게 무너지는지 본다</span>
<b>보는 FTL 개념</b><span>빈 블록 풀, GC (victim 선택, 유효 페이지 복사), WAF, steady state</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>4–8시간 (steady state 의 속도에 달렸다) : 밤새 돌린다</span>
<b>명령</b><span><code>sudo ./lab.sh cliff 100</code></span>
</div>

## 배경 : 빈 블록과 GC

NAND 는 **페이지** (몇 KiB–몇십 KiB) 단위로 쓰고, 그보다 훨씬 큰 **블록** (페이지 수백 개) 단위로만 지운다. 이미 쓴 페이지는 덮어쓸 수 없다.
그래서 FTL 은 새 데이터를 늘 빈 페이지에 쓰고, 예전 자리는 '무효' 로 표시한다. 빈 블록은 계속 줄어든다.

<svg viewBox="0 0 760 330" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="블록과 GC"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">빈 블록이 바닥나는 순간 GC 가 시작된다</text><text x="100.0" y="50.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1. 막 지운 드라이브</text><rect x="15" y="62" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="49" y="62" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="83" y="62" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="117" y="62" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="151" y="62" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="15" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="49" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="83" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="117" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="151" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="15" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="49" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="83" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="117" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="151" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="288.0" y="50.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2. 쓰는 중</text><rect x="203" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="237" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="271" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="305" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="339" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="203" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="237" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="271" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="305" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="339" y="96" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="203" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="237" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="271" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="305" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="339" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="476.0" y="50.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">3. 빈 블록이 바닥</text><rect x="391" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="425" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="459" y="62" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="493" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="527" y="62" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="391" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="425" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="459" y="96" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="493" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="527" y="96" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="391" y="130" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="425" y="130" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="459" y="130" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="493" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="527" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="664.0" y="50.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">4. GC</text><rect x="579" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="613" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="647" y="62" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="681" y="62" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="715" y="62" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="579" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="613" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="647" y="96" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="681" y="96" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="715" y="96" width="31" height="31" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="579" y="130" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="613" y="130" width="31" height="31" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><rect x="647" y="130" width="31" height="31" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="681" y="130" width="31" height="31" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="715" y="130" width="31" height="31" rx="3" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><rect x="60" y="190" width="14" height="12" rx="2" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="80.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">빈 블록</text><rect x="142" y="190" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="162.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">유효 데이터로 가득</text><rect x="302" y="190" width="14" height="12" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="322.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">유효 + 무효 섞임</text><rect x="462" y="190" width="14" height="12" rx="2" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="482.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">GC 대상 (victim)</text><rect x="674" y="190" width="14" height="12" rx="2" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="1.5"/><text x="694.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">옮겨 받는 블록</text><rect x="80" y="230" width="600" height="80" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="380.0" y="258.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">4. GC 한 번</text><text x="380.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">무효 페이지가 가장 많은 블록을 고른다 → 유효 페이지만 새 블록으로 복사 → 지운다</text><text x="380.0" y="290.0" font-size="11.5" fill="#4d5656" text-anchor="middle">복사하는 동안 호스트 쓰기는 기다린다 : 이것이 IOPS 가 떨어지는 이유</text></svg>

빈 블록이 바닥에 가까워지면 FTL 은 GC 를 해야 한다 : 무효 페이지가 많은 블록을 골라, 남은 유효 페이지를 다른 곳에 복사하고, 블록을 지운다.
복사하는 양만큼 NAND 는 호스트가 시킨 것보다 더 많이 쓴다. 이 비율이 **WAF** (write amplification factor) 다.

<svg viewBox="0 0 760 270" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="GC 비용"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">GC 한 번의 비용 : 블록에 유효 페이지가 v 개 남아 있으면</text><rect x="40" y="60" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="80" y="60" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="120" y="60" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="160" y="60" width="36" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="200" y="60" width="36" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="240" y="60" width="36" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="280" y="60" width="36" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="320" y="60" width="36" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="200.0" y="52.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">victim 블록 (페이지 N = 8, 유효 v = 3)</text><line x1="200" y1="100" x2="200" y2="140" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="270.0" y="114.0" font-size="11.5" fill="#566573" text-anchor="middle">유효 3개를 복사</text><rect x="40" y="145" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="80" y="145" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="120" y="145" width="36" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="160" y="145" width="36" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="200" y="145" width="36" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="240" y="145" width="36" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="280" y="145" width="36" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><rect x="320" y="145" width="36" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="200.0" y="200.0" font-size="12" fill="#4d5656" text-anchor="middle">빈 자리 5개가 생긴다 → 호스트가 5개 쓸 때마다 NAND 에는 8개</text><rect x="430" y="60" width="310" height="125" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="585.0" y="94.5" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">WAF = N / (N − v)</text><text x="585.0" y="110.5" font-size="12.5" fill="#4d5656" text-anchor="middle">v = 0 → 1.0 (공짜)</text><text x="585.0" y="126.5" font-size="12.5" fill="#4d5656" text-anchor="middle">v = 3 → 8/5 = 1.6</text><text x="585.0" y="142.5" font-size="12.5" fill="#4d5656" text-anchor="middle">v = 6 → 8/2 = 4.0</text><text x="585.0" y="158.5" font-size="12.5" fill="#4d5656" text-anchor="middle">빈 공간 (OP) 이 적을수록 v 가 크다</text><text x="380.0" y="250.0" font-size="12" font-weight="700" fill="#c0392b" text-anchor="middle">steady state 의 IOPS ≈ 빈 드라이브 IOPS ÷ WAF (대략)</text></svg>

랜덤 쓰기는 무효 페이지를 모든 블록에 고르게 흩어 놓는다. 그래서 victim 블록에도 유효 페이지가 많이 남아 있고, GC 비용이 크다.

## 가설과 예상

SNIA 의 SSD 성능 시험 방법 (PTS) 은 이 곡선을 세 구간으로 나눈다 : 막 지운 상태 (FOB, fresh-out-of-box), 전환, steady state.

<svg viewBox="0 0 760 360" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="cliff 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 : 4 KiB 랜덤 쓰기 IOPS, 용량의 2배를 쓰는 동안 (가설)</text><line x1="90" y1="270.0" x2="720" y2="270.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="226.0" x2="720" y2="226.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="182.0" x2="720" y2="182.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="138.0" x2="720" y2="138.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="94.0" x2="720" y2="94.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="50.0" x2="720" y2="50.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="270" x2="720" y2="270" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="50" x2="90" y2="270" stroke="#566573" stroke-width="1.5"/><line x1="90.0" y1="270" x2="90.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="90.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><line x1="195.0" y1="270" x2="195.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="195.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">40</text><line x1="300.0" y1="270" x2="300.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="300.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">80</text><line x1="405.0" y1="270" x2="405.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">120</text><line x1="510.0" y1="270" x2="510.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="510.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">160</text><line x1="615.0" y1="270" x2="615.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="615.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">200</text><line x1="720.0" y1="270" x2="720.0" y2="275" stroke="#566573" stroke-width="1.2"/><text x="720.0" y="289.0" font-size="11.5" fill="#4d5656" text-anchor="middle">240</text><line x1="85" y1="270.0" x2="90" y2="270.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="85" y1="226.0" x2="90" y2="226.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="230.0" font-size="11.5" fill="#4d5656" text-anchor="end">10</text><line x1="85" y1="182.0" x2="90" y2="182.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="end">20</text><line x1="85" y1="138.0" x2="90" y2="138.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="142.0" font-size="11.5" fill="#4d5656" text-anchor="end">30</text><line x1="85" y1="94.0" x2="90" y2="94.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="98.0" font-size="11.5" fill="#4d5656" text-anchor="end">40</text><line x1="85" y1="50.0" x2="90" y2="50.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="54.0" font-size="11.5" fill="#4d5656" text-anchor="end">50</text><text x="405.0" y="310.0" font-size="12" fill="#2c3e50" text-anchor="middle">지금까지 쓴 양 (GB)</text><text x="38.0" y="160.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 38.0 160.0)">IOPS (천)</text><rect x="90.0" y="50.0" width="249.4" height="220.0" rx="0" fill="#1f6f5c" fill-opacity="0.1" stroke="none" stroke-width="1.0"/><text x="214.7" y="66.0" font-size="11.5" font-weight="700" fill="#1f6f5c" text-anchor="middle">FOB (빈 드라이브)</text><rect x="339.4" y="50.0" width="144.4" height="220.0" rx="0" fill="#b7950b" fill-opacity="0.12" stroke="none" stroke-width="1.0"/><text x="411.6" y="66.0" font-size="11.5" font-weight="700" fill="#b7950b" text-anchor="middle">전환</text><rect x="483.8" y="50.0" width="236.2" height="220.0" rx="0" fill="#c0392b" fill-opacity="0.08" stroke="none" stroke-width="1.0"/><text x="601.9" y="66.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="middle">steady state</text><polyline points="90.0,102.8 142.5,107.2 247.5,111.6 326.2,120.4 352.5,190.8 378.8,230.4 418.1,248.0 483.8,254.6 720.0,255.5" fill="none" fill-opacity="1.0" stroke="#2874a6" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><line x1="405.0" y1="50" x2="405.0" y2="270" stroke="#566573" stroke-width="1.4" stroke-dasharray="4 4"/><text x="410.0" y="150.0" font-size="11.5" fill="#566573" text-anchor="start">용량 120 GB</text><text x="510.0" y="217.2" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="start">수천 IOPS : GC 가 쓰기를 막는다</text><text x="400.0" y="340.0" font-size="11.5" fill="#566573" text-anchor="middle">높이와 위치는 예시 (사양서 최대 랜덤 쓰기는 수만 IOPS) : 진짜 곡선은 실험으로</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 처음엔 빠르다</td><td>처음 수십 GB 는 높은 IOPS (SLC 버퍼와 빈 블록 덕분)</td></tr>
<tr><td>H2 용량 근처에서 급히 떨어진다</td><td>쓴 양이 사용자 용량 (120 GB) + 숨은 여유 공간에 가까워질 때 절벽</td></tr>
<tr><td>H3 steady state 는 수천 IOPS 이하</td><td>쓴 양이 용량의 1.5배를 넘으면 평평해지고, 처음보다 몇 배–몇십 배 낮다</td></tr>
<tr><td>H4 steady state 의 들쭉날쭉함</td><td>1초 단위로 보면 GC 때문에 위아래로 크게 흔들린다 (평균만 보면 안 보인다)</td></tr>
</tbody></table></div>

실험 5 페이지의 모델에 따르면 span 100% 의 WAF 는 약 7.8 이다. 즉 steady state 의 NAND 쓰기 속도가 TLC 쓰기 속도에 묶여 있다면, 호스트가 볼 수 있는 속도는 그 1/7.8 정도다.

## 절차

```
$ sudo ./lab.sh cliff 100          # SPAN% = 100 (전체), TIMES = 2 (용량의 2배) 가 기본값
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td>1</td><td>전체 TRIM (<code>blkdiscard</code>), 2분 쉼 : FOB 상태</td></tr>
<tr><td>2</td><td>SMART 기록 (<code>smart-before</code>)</td></tr>
<tr><td>3</td><td>fio : <code>--rw=randwrite --bs=4k --iodepth=32 --norandommap --randrepeat=0</code>, 대상 = 전체 120 GB, 총 240 GB</td></tr>
<tr><td>4</td><td>1초마다 IOPS · 대역폭 · 지연 기록</td></tr>
<tr><td>5</td><td>SMART 기록 (<code>smart-after</code>) → 실험 6 의 WAF 계산에 쓴다</td></tr>
</tbody></table></div>

- `--norandommap` : 같은 LBA 를 여러 번 쓸 수 있게 (진짜 랜덤). 없으면 fio 가 모든 LBA 를 한 번씩 쓴 뒤에야 반복한다.
- `--randrepeat=0` : 실행할 때마다 다른 난수.
- 끝나는 시간은 진행 줄의 `eta` 로 본다. steady state 가 아주 느리면 (1천 IOPS 이하) 8시간을 넘을 수 있다.

<div class="tip" markdown="1">
**돌리는 동안** 다른 터미널에서 `iostat -x 1` 로 보면 IOPS 가 출렁이는 것이 실시간으로 보인다. 컴퓨터의 절전 · 화면 잠금은 상관없지만 **절전 모드 (suspend)** 는 꺼 둔다.
</div>

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-cliff-span100 | tail -1)
$ python3 plot.py cliff.png $D/cliff_iops.log=span100
$ python3 smartdiff.py $D
```

1. **세 구간 찾기** : x 축 (쓴 GB) 에서 절벽이 시작하는 곳과 평평해지는 곳. 절벽 위치 − 120 GB ≈ FTL 이 쓸 수 있었던 숨은 빈 공간.
2. **steady state 값** : 마지막 1/4 구간의 평균 IOPS 와 흔들림 (표준편차, 최소값).
3. **WAF** : `smartdiff.py` 가 177 과 241 로 계산한다 (실험 6). 이 실행만으로 177 이 10 이상 늘 것으로 예상한다.
4. **FOB IOPS ÷ steady IOPS** 를 WAF 와 비교 : 대략 비슷하다면 'GC 의 복사가 느려진 이유의 대부분' 이다.

## 시뮬레이터와의 연결

시뮬레이터의 **빈 블록 차트** 와 **GC 정책 비교** 의 실제 판이다. 시뮬레이터를 같은 조건 (span 100%, OP 를 이 드라이브의 숨은 여유와 비슷하게, 4 KiB 랜덤) 으로 돌려 곡선 모양과 WAF 를 나란히 놓는다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/3-trim/' | relative_url }}">← 3. TRIM 과 매핑 없는 읽기</a><a href="{{ '/old-ssd-experiments/5-over-provisioning/' | relative_url }}">5. Over-provisioning →</a></div>
