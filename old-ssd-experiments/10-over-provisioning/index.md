---
layout: default
title: 10. Over-provisioning
permalink: /old-ssd-experiments/10-over-provisioning/
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

# 10. Over-provisioning : 덜 쓰면 얼마나 빨라지나

<div class="glance">
<b>목표</b><span>실험 8 을 드라이브의 앞쪽 80% 에만 해서, 남긴 20% 가 여유 공간으로 쓰일 때 steady state 가 몇 배 빨라지는지 재고, 모델의 예측과 비교한다</span>
<b>보는 FTL 개념</b><span>over-provisioning (OP), 여유 비율과 WAF 의 관계, TRIM 된 공간을 FTL 이 여유로 쓰기</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>span 마다 3–6시간 : 80% 는 필수, 90% · 70% 는 선택</span>
<b>명령</b><span><code>sudo ./lab.sh cliff 80</code> (선택 : <code>cliff 90</code>, <code>cliff 70</code>)</span>
</div>

## 배경 : 여유 공간이 왜 중요한가

GC 의 비용은 victim 블록에 남은 유효 페이지 수로 정해진다 (실험 8). 랜덤 쓰기에서 victim 이 얼마나 비어 있는지는 **데이터에 비해 NAND 가 얼마나 넉넉한가** 로 정해진다.

이 여유를 OP 라고 한다. 드라이브는 처음부터 숨은 여유를 가지고 있고 (사용자에게 보이지 않는 NAND), 사용자가 일부 LBA 를 **TRIM 된 채로 두고 쓰지 않으면** 그만큼도 FTL 의 여유가 된다. 파티션을 일부러 작게 만드는 것과 같은 효과다.

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="OP span"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 NAND, 다른 여유 : 앞쪽 80% 만 쓰면 나머지 20% 도 여유 공간이 된다</text><text x="20.0" y="84.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">span 100%</text><rect x="140" y="60" width="524.0174672489082" height="38" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="402.0" y="83.0" font-size="11.5" fill="#4d5656" text-anchor="middle">사용자 LBA 120 GB (전부 씀)</text><rect x="664.0174672489082" y="60" width="39.301310043668124" height="38" rx="0" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="683.7" y="54.0" font-size="11.5" font-weight="700" fill="#4d5656" text-anchor="middle">SLC</text><rect x="703.3187772925763" y="60" width="36.68122270742358" height="38" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="721.7" y="54.0" font-size="11.5" font-weight="700" fill="#4d5656" text-anchor="middle">여유</text><text x="20.0" y="164.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">span 80%</text><rect x="140" y="140" width="419.2139737991266" height="38" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="349.6" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="middle">쓰는 LBA 96 GB</text><rect x="559.2139737991266" y="140" width="104.80349344978166" height="38" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="611.6" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="middle">TRIM 된 24 GB</text><rect x="664.0174672489082" y="140" width="39.301310043668124" height="38" rx="0" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="683.7" y="134.0" font-size="11.5" font-weight="700" fill="#4d5656" text-anchor="middle">SLC</text><rect x="703.3187772925763" y="140" width="36.68122270742358" height="38" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="721.7" y="134.0" font-size="11.5" font-weight="700" fill="#4d5656" text-anchor="middle">여유</text><text x="440.0" y="205.0" font-size="12" fill="#2c3e50" text-anchor="middle">NAND 전체 약 137 GB (128 GiB) = 사용자 120 GB + 숨은 공간 약 17 GB</text><text x="440.0" y="228.0" font-size="12" fill="#2c3e50" text-anchor="middle">숨은 공간에서 SLC 버퍼 (3 GB × 3) 를 빼면 진짜 여유는 약 8 GB 일 것으로 가정</text><text x="440.0" y="262.0" font-size="12.5" font-weight="700" fill="#c0392b" text-anchor="middle">ρ (여유 ÷ 쓰는 데이터) : 100% → 8.4/120 = 0.07,  80% → 32.4/96 = 0.34</text></svg>

## 모델 : 여유 비율 ρ 와 WAF

균일한 랜덤 쓰기에서, 유효 페이지가 가장 적은 블록 (또는 가장 오래된 블록) 을 고르는 GC 의 WAF 는 여유 비율 ρ 만으로 거의 정해진다는 분석이 있다 (Desnoyers, *Analytic Modeling of SSD Write Performance*, SYSTOR 2012).
α = 1 + ρ 라고 하면 WAF = α / (α + W(−α·e^(−α))). 여기서 W 는 Lambert W 함수다. 아래 곡선이 그 식이다.

<svg viewBox="0 0 760 380" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="WAF-OP 곡선"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">모델이 예측하는 WAF : 여유 비율 ρ 가 작으면 WAF 가 급히 커진다</text><line x1="90" y1="290.0" x2="720" y2="290.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="242.0" x2="720" y2="242.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="194.0" x2="720" y2="194.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="146.0" x2="720" y2="146.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="98.0" x2="720" y2="98.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="50.0" x2="720" y2="50.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="290" x2="720" y2="290" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="50" x2="90" y2="290" stroke="#566573" stroke-width="1.5"/><line x1="90.0" y1="290" x2="90.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="90.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0.0</text><line x1="195.0" y1="290" x2="195.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="195.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0.2</text><line x1="300.0" y1="290" x2="300.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="300.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0.4</text><line x1="405.0" y1="290" x2="405.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0.6</text><line x1="510.00000000000006" y1="290" x2="510.00000000000006" y2="295" stroke="#566573" stroke-width="1.2"/><text x="510.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0.8</text><line x1="615.0" y1="290" x2="615.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="615.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1.0</text><line x1="720.0" y1="290" x2="720.0" y2="295" stroke="#566573" stroke-width="1.2"/><text x="720.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1.2</text><line x1="85" y1="290.0" x2="90" y2="290.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="294.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="85" y1="242.0" x2="90" y2="242.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="246.0" font-size="11.5" fill="#4d5656" text-anchor="end">2</text><line x1="85" y1="194.0" x2="90" y2="194.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="198.0" font-size="11.5" fill="#4d5656" text-anchor="end">4</text><line x1="85" y1="146.0" x2="90" y2="146.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="150.0" font-size="11.5" fill="#4d5656" text-anchor="end">6</text><line x1="85" y1="98.0" x2="90" y2="98.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="end">8</text><line x1="85" y1="50.0" x2="90" y2="50.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="54.0" font-size="11.5" fill="#4d5656" text-anchor="end">10</text><text x="405.0" y="330.0" font-size="12" fill="#2c3e50" text-anchor="middle">ρ = 여유 공간 ÷ 쓰는 데이터</text><text x="38.0" y="170.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 38.0 170.0)">WAF</text><polyline points="121.5,73.8 126.8,102.4 132.0,123.8 137.2,140.4 142.5,153.7 147.8,164.6 153.0,173.7 158.2,181.4 163.5,187.9 168.8,193.6 174.0,198.6 179.2,203.0 184.5,206.9 189.8,210.4 195.0,213.5 200.2,216.3 205.5,218.9 210.8,221.2 216.0,223.4 221.2,225.4 226.5,227.2 231.8,228.9 237.0,230.4 242.2,231.9 247.5,233.3 252.8,234.5 258.0,235.7 263.2,236.8 268.5,237.9 273.8,238.9 279.0,239.8 284.2,240.7 289.5,241.5 294.8,242.3 300.0,243.0 305.2,243.7 310.5,244.4 315.8,245.1 321.0,245.7 326.2,246.3 331.5,246.8 336.8,247.4 342.0,247.9 347.2,248.4 352.5,248.8 357.8,249.3 363.0,249.7 368.2,250.1 373.5,250.5 378.8,250.9 384.0,251.3 389.2,251.6 394.5,252.0 399.8,252.3 405.0,252.6 410.2,252.9 415.5,253.2 420.8,253.5 426.0,253.8 431.3,254.1 436.5,254.3 441.8,254.6 447.0,254.8 452.2,255.0 457.5,255.3 462.8,255.5 468.0,255.7 473.3,255.9 478.5,256.1 483.8,256.3 489.0,256.5 494.3,256.7 499.5,256.9 504.8,257.1 510.0,257.2 515.2,257.4 520.5,257.6 525.8,257.7 531.0,257.9 536.2,258.0 541.5,258.2 546.8,258.3 552.0,258.5 557.2,258.6 562.5,258.7 567.8,258.8 573.0,259.0 578.2,259.1 583.5,259.2 588.8,259.3 594.0,259.4 599.2,259.6 604.5,259.7 609.8,259.8 615.0,259.9 620.2,260.0 625.5,260.1 630.8,260.2 636.0,260.3 641.3,260.4 646.5,260.5 651.8,260.5 657.0,260.6 662.3,260.7 667.5,260.8 672.8,260.9 678.0,261.0 683.2,261.0 688.5,261.1 693.8,261.2 699.0,261.3 704.2,261.3 709.5,261.4 714.8,261.5 720.0,261.6" fill="none" fill-opacity="1.0" stroke="#1f6f5c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="126.8" cy="102.4" r="6" fill="#c0392b" stroke="none" stroke-width="1.5"/><text x="142.5" y="94.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="start">span 100% : ρ 0.07, WAF 7.8</text><circle cx="189.2" cy="210.0" r="6" fill="#b7950b" stroke="none" stroke-width="1.5"/><text x="204.9" y="201.6" font-size="11.5" font-weight="700" fill="#b7950b" text-anchor="start">span 90% : ρ 0.19, WAF 3.3</text><circle cx="267.2" cy="237.6" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><text x="282.9" y="229.2" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="start">span 80% : ρ 0.34, WAF 2.2</text><circle cx="367.5" cy="250.1" r="6" fill="#7d3c98" stroke="none" stroke-width="1.5"/><text x="383.3" y="241.7" font-size="11.5" font-weight="700" fill="#7d3c98" text-anchor="start">span 70% : ρ 0.53, WAF 1.7</text><text x="400.0" y="350.0" font-size="11.5" fill="#566573" text-anchor="middle">모델 : 균일한 랜덤 쓰기 + FIFO/greedy 류 GC (Desnoyers 2012). 실제 펌웨어는 다를 수 있다</text><text x="400.0" y="368.0" font-size="11.5" fill="#566573" text-anchor="middle">가정 (NAND 128 GiB, SLC 버퍼 9 GB 차지) 이 틀리면 점들이 옆으로 움직인다 : 측정으로 거꾸로 추정한다</text></svg>

이 그림의 점들은 **가정** 위에 있다 : NAND 128 GiB (137.4 GB), SLC 버퍼 3 GB 가 TLC 9 GB 를 차지, 나머지가 모두 GC 의 여유. 펌웨어가 불량 블록 예비분이나 메타데이터로 일부를 더 쓰면 실제 여유는 더 작다.
**이 실험의 재미는 거꾸로 하는 데 있다** : 잰 WAF (실험 12) 를 곡선에 대어 이 드라이브의 실제 여유 공간을 추정한다.

## 가설과 예상

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="OP 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 : steady state IOPS 는 1/WAF 에 비례 (span 100% = 1 로 놓고)</text><line x1="90" y1="225.0" x2="720" y2="225.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="189.0" x2="720" y2="189.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="153.0" x2="720" y2="153.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="117.0" x2="720" y2="117.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="81.0" x2="720" y2="81.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="45.0" x2="720" y2="45.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="225" x2="720" y2="225" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="45" x2="90" y2="225" stroke="#566573" stroke-width="1.5"/><line x1="216.0" y1="225" x2="216.0" y2="230" stroke="#566573" stroke-width="1.2"/><text x="216.0" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">span 100%</text><line x1="342.0" y1="225" x2="342.0" y2="230" stroke="#566573" stroke-width="1.2"/><text x="342.0" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">span 90%</text><line x1="468.0" y1="225" x2="468.0" y2="230" stroke="#566573" stroke-width="1.2"/><text x="468.0" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">span 80%</text><line x1="594.0" y1="225" x2="594.0" y2="230" stroke="#566573" stroke-width="1.2"/><text x="594.0" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">span 70%</text><line x1="85" y1="225.0" x2="90" y2="225.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="229.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="85" y1="189.0" x2="90" y2="189.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="193.0" font-size="11.5" fill="#4d5656" text-anchor="end">1</text><line x1="85" y1="153.0" x2="90" y2="153.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="157.0" font-size="11.5" fill="#4d5656" text-anchor="end">2</text><line x1="85" y1="117.0" x2="90" y2="117.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="121.0" font-size="11.5" fill="#4d5656" text-anchor="end">3</text><line x1="85" y1="81.0" x2="90" y2="81.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="85.0" font-size="11.5" fill="#4d5656" text-anchor="end">4</text><line x1="85" y1="45.0" x2="90" y2="45.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="49.0" font-size="11.5" fill="#4d5656" text-anchor="end">5</text><text x="38.0" y="135.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 38.0 135.0)">상대 IOPS</text><rect x="181.0" y="189.0" width="70.0" height="36.0" rx="0" fill="#c0392b" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="216.0" y="181.0" font-size="12.5" font-weight="700" fill="#c0392b" text-anchor="middle">× 1.0</text><rect x="307.0" y="140.6" width="70.0" height="84.4" rx="0" fill="#b7950b" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="342.0" y="132.6" font-size="12.5" font-weight="700" fill="#b7950b" text-anchor="middle">× 2.3</text><rect x="433.0" y="96.1" width="70.0" height="128.9" rx="0" fill="#2874a6" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="468.0" y="88.1" font-size="12.5" font-weight="700" fill="#2874a6" text-anchor="middle">× 3.6</text><rect x="559.0" y="55.9" width="70.0" height="169.1" rx="0" fill="#7d3c98" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="594.0" y="47.9" font-size="12.5" font-weight="700" fill="#7d3c98" text-anchor="middle">× 4.7</text><text x="400.0" y="270.0" font-size="11.5" fill="#566573" text-anchor="middle">필수는 100% (실험 8) 와 80%. 90% · 70% 는 시간이 되면 : 점이 많을수록 곡선과 비교하기 좋다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 OP 를 늘리면 steady state 가 빨라진다</td><td>span 80% 의 steady IOPS 가 span 100% 보다 몇 배 높다 (모델 : 약 3.6배)</td></tr>
<tr><td>H2 절벽이 늦게, 덜 깊게 온다</td><td>쓴 양 기준 절벽 위치가 뒤로 밀리고, 바닥이 높다</td></tr>
<tr><td>H3 WAF 가 모델 근처다</td><td>SMART 로 잰 WAF : span 100% ≈ 7–8, span 80% ≈ 2 근처</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh cliff 80           # 앞쪽 96 GB 에만 4 KiB 랜덤 쓰기, 총 240 GB
$ sudo ./lab.sh cliff 90           # 선택
$ sudo ./lab.sh cliff 70           # 선택
```

- 매번 전체 TRIM 으로 시작하므로, 쓰지 않는 뒤쪽 LBA 는 TRIM 된 채로 남는다 : FTL 이 여유로 쓸 수 있다.
- 총 쓰기 양은 span 과 상관없이 용량의 2배 (240 GB) 로 같다. 그래서 span 이 작을수록 같은 LBA 를 더 여러 번 덮어쓴다 : steady state 에 더 확실히 들어간다.
- 실험 8 과 같은 날, 같은 연결에서 하는 것이 좋다 (온도와 조건을 맞추려고).

<div class="tip" markdown="1">
**다른 방법 : HPA.** `hdparm -N` 으로 드라이브가 보여 주는 최대 섹터 수를 줄이면 (Host Protected Area), 운영체제에게 드라이브가 정말로 작아진다. TRIM 된 뒤쪽을 '안 쓰기로 약속' 하는 span 방식과 같은 효과일 것이다 (FTL 에게는 둘 다 매핑 없는 LBA). 둘이 같은지 확인하고 싶다면 span 80% 실행 뒤 `sudo hdparm -Np187553318 장치` (80%) 로 바꾸고 `cliff 100` 을 한 번 더 한다 (그러면 '100%' 가 새 크기의 100%). 원래대로 : `sudo hdparm -Np234441648 장치`. `p` 는 '전원을 꺼도 유지' 라는 뜻이고, 설정 뒤 전원을 껐다 켜야 적용되는 드라이브가 많다.
</div>

## 결과 읽는 법

```
$ R=~/Ryu/old_ssd_results
$ python3 plot.py op.png $R/*-cliff-span100/cliff_iops.log=100% $R/*-cliff-span80/cliff_iops.log=80%
$ python3 smartdiff.py $(ls -d $R/*-cliff-span80 | tail -1)
```

1. 두 곡선의 steady state 평균의 비율 → 그림의 '× 3.6' 과 비교.
2. 각 span 의 WAF (smartdiff) 를 ρ–WAF 곡선 위에 찍는다. 점이 곡선보다 위에 있으면 실제 여유가 가정보다 작다는 뜻이고, 그 차이로 숨은 여유를 추정한다 (Claude 가 계산한다).
3. 시간이 되어 90% · 70% 도 했다면, 점 네 개로 이 드라이브의 **실제 WAF–OP 곡선** 이 생긴다.

## 시뮬레이터와의 연결 (덤)

시뮬레이터의 기본값 OP 20% 와 **WAF–OP 곡선** 이 이것의 모델 판이다. 실제 드라이브의 점들을 시뮬레이터 곡선 위에 겹쳐 그리는 것이 이 실험의 최종 그림이다.

## 결과

<div class="result" markdown="1">
### span 80% (2026.10.18 19:06 – 20:12, 66분)

결과 폴더 `20261018-190605-cliff-span80`. [실험 8](/old-ssd-experiments/8-write-cliff/) (span 100%) 과 똑같이, 다만 앞쪽 96 GB 에만 4 KiB 랜덤 쓰기를 240 GB.

![span 100% 와 80%](/old-ssd-experiments/10-over-provisioning/op.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>쓴 양</th>
<th>span 100% (IOPS)</th>
<th>span 80% (IOPS)</th>
<th>80 ÷ 100</th>
</tr></thead><tbody>
<tr><td>처음 약 3 GB (SLC 버퍼)</td><td>약 8만</td><td>약 8만</td><td>1.0</td></tr>
<tr><td>평평한 구간 (20 – 100 GB, 중앙값)</td><td>36,575</td><td>36,813</td><td>1.0</td></tr>
<tr><td><strong>절벽의 자리</strong></td><td><strong>126.5 GB</strong></td><td><strong>126.9 GB</strong></td><td>같다</td></tr>
<tr><td>120 – 140 GB</td><td>11,782</td><td>14,986</td><td>1.27</td></tr>
<tr><td>140 – 160 GB</td><td>7,969</td><td>9,999</td><td>1.25</td></tr>
<tr><td>160 – 180 GB</td><td>7,115</td><td>9,722</td><td>1.37</td></tr>
<tr><td>180 – 200 GB</td><td>6,769</td><td>8,417</td><td>1.24</td></tr>
<tr><td>200 – 220 GB</td><td>6,104</td><td>7,553</td><td>1.24</td></tr>
<tr><td>220 – 240 GB</td><td>5,985</td><td>7,739</td><td><strong>1.29</strong></td></tr>
<tr><td>전체 시간</td><td>81 분</td><td>66 분</td><td>0.81</td></tr>
</tbody></table></div>

**H1 (OP 를 늘리면 steady state 가 빨라진다) : 맞다, 그러나 모델보다 훨씬 작게.** 절벽 뒤 내내 span 80% 가 **약 1.25 – 1.37배** 빠르다. 모델 (Desnoyers) 은 **약 3.6배** 를 예측했다.

**H2 (절벽이 늦게, 덜 깊게 온다) : 늦게는 아니다, 덜 깊게는 맞다.** 절벽은 두 실행 모두 **약 127 GB** 에서 왔다. 생각해 보면 당연하다 : 두 실행 모두 전체 TRIM 으로 시작했으니 NAND 전체가 비어 있었고, 랜덤 쓰기는 매번 새 페이지를 쓰므로, **빈 페이지가 처음 바닥나는 때는 범위와 상관없이 '쓴 양' 으로 정해진다** (사용자 용량 + 숨은 여유). 범위가 바꾸는 것은 그 뒤 GC 가 고르는 블록 (victim) 안에 무효 페이지가 얼마나 많으냐, 곧 절벽 **뒤의 높이** 다. 예측을 잘못 세웠다.

**왜 1.3배뿐인가 : 셋의 후보**
1. **steady state 에 아직 이르지 않았다.** 두 곡선 모두 끝까지 조금씩 내려가고 있다. GC 가 고르는 블록의 무효 페이지 분포가 자리 잡으려면 범위를 여러 번 덮어써야 하는데, 240 GB 는 96 GB 범위를 약 2.5번 덮을 뿐이다 (절벽 뒤로는 1.2번).
2. **TRIM 된 뒤쪽 20% 를 FTL 이 생각만큼 여유로 쓰지 않는다.** 모델은 쓰지 않은 LBA 의 NAND 가 모두 GC 의 여유가 된다고 가정한다.
3. **느림이 GC 의 복사만은 아니다.** 실험 8 에서 본 것처럼 SMART 177 이 말하는 WAF (작다) 와 속도가 말하는 WAF (크다) 가 맞지 않는다. 쓰기 대역의 일부를 SLC → TLC 옮기기 같은 다른 일이 쓴다면, OP 를 늘려 줄이는 몫 (복사) 은 전체 느림의 일부일 뿐이다.

**속도로 어림한 WAF** (NAND 쓰기 약 150 MB/s 가 그대로라고 보면) : span 100% 약 6.1, span 80% 약 4.7. 모델은 7.8 과 2.2. 100% 는 모델보다 낫고 80% 는 모델보다 나쁘다 : 두 점 사이의 차이가 모델보다 작다.

**SMART** : 177 이 127 → 129 (+2), 241 +240.1 GB → `smartdiff.py` 의 WAF 약 1.15 (0.57 – 1.72). 240 GB 를 썼는데 177 이 2 만 오른 것은 (최소 1.75) 177 이 덜 센다는 뜻이다 : 이 드라이브에서 177 로 WAF 를 재는 것은 믿기 어렵다 ([실험 12](/old-ssd-experiments/12-waf/) 에서 따로 확인).

**다음에 해 볼 것 (선택)**
- ~~**더 길게** : `sudo ./lab.sh cliff 80 4` (용량의 4배 = 480 GB) 로 정말 steady state 에 이르렀을 때의 비를 본다. 1번 후보를 가른다~~ → 아래 결과 (2026.10.23)
- **더 작게** : `sudo ./lab.sh cliff 50` (앞쪽 절반만) : 여유가 아주 크면 차이가 분명해지는지. 2 · 3번 후보를 가른다
- 90% · 70% 는 위의 두 가지를 본 뒤로 미룬다
</div>

<div class="result" markdown="1">
### span 80%, 4배 (2026.10.23 09:03 – 12:39, 214분)

결과 폴더 `20261023-090309-cliff-span80`. 위와 같은 실험을 총 480 GB (용량의 4배) 로, 전체 TRIM 부터 처음부터 다시 했다. 도중에 멈춘 두 번 (10.22 밤 268 GB, 10.23 아침 137 GB) 은 쓰지 않는다.

![span 100% (2배), span 80% (2배), span 80% (4배)](/old-ssd-experiments/10-over-provisioning/op-long.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>쓴 양</th>
<th>span 100%, 2배 (IOPS)</th>
<th>span 80%, 2배 (IOPS)</th>
<th>span 80%, 4배 (IOPS)</th>
</tr></thead><tbody>
<tr><td>처음 약 3 GB (SLC 버퍼)</td><td>약 8만</td><td>약 8만</td><td>약 8만</td></tr>
<tr><td>평평한 구간 (20 – 100 GB, 중앙값)</td><td>36,575</td><td>36,813</td><td>36,855</td></tr>
<tr><td><strong>절벽의 자리</strong></td><td>126.5 GB</td><td>126.9 GB</td><td>약 128 GB</td></tr>
<tr><td>120 – 140 GB</td><td>11,782</td><td>14,986</td><td>14,797</td></tr>
<tr><td>140 – 160 GB</td><td>7,969</td><td>9,999</td><td>10,677</td></tr>
<tr><td>160 – 180 GB</td><td>7,115</td><td>9,722</td><td>9,632</td></tr>
<tr><td>180 – 200 GB</td><td>6,769</td><td>8,417</td><td>8,972</td></tr>
<tr><td>200 – 220 GB</td><td>6,104</td><td>7,553</td><td>7,656</td></tr>
<tr><td>220 – 240 GB</td><td><strong>5,985</strong></td><td>7,739</td><td>7,380</td></tr>
<tr><td>240 – 280 GB</td><td>–</td><td>–</td><td>7,243</td></tr>
<tr><td>280 – 320 GB</td><td>–</td><td>–</td><td>6,405</td></tr>
<tr><td>320 – 360 GB</td><td>–</td><td>–</td><td>6,711</td></tr>
<tr><td>360 – 400 GB</td><td>–</td><td>–</td><td>6,475</td></tr>
<tr><td>400 – 440 GB</td><td>–</td><td>–</td><td>6,301</td></tr>
<tr><td>440 – 480 GB</td><td>–</td><td>–</td><td><strong>6,321</strong></td></tr>
<tr><td>240 GB 까지 걸린 시간</td><td>81 분</td><td>66 분</td><td>65 분</td></tr>
</tbody></table></div>

**되풀이는 잘 된다.** 처음 240 GB 는 10.18 의 span 80% 실행을 거의 그대로 다시 그렸다 (절벽 뒤 20 GB 구간마다 ±7% 안, 240 GB 까지 65분 대 66분).

**약 300 GB 부터 평평해진다.** 320 – 480 GB 는 20 GB 구간 평균이 6,300 – 6,700 이고 더 내려가지 않는다 (1초 값의 중앙값은 약 6,050 – 6,150). 300 GB 는 96 GB 범위를 약 3번 덮은 양이다. 이것이 span 80% 의 steady state : **약 6,350 IOPS (340 – 480 GB 평균), 약 26 MB/s**.

**1번 후보 (steady state 에 아직 이르지 않았다) 는 아니다.** *(같은 날 저녁 고침 : 이 결론은 틀렸다. span 80% 는 steady 에 이르렀지만, 비교한 span 100% 가 240 GB 에서 steady 가 아니었다. 아래 'span 100%, 4배' 를 보라.)* 더 길게 쓰자 차이가 벌어지기는커녕, span 80% 가 계속 내려와 span 100% 가 240 GB 에서 보인 값 (5,985) 의 **약 1.06배** 에서 멈췄다. span 100% 도 240 GB 에서 아직 조금씩 내려가고 있었으니 steady state 끼리의 비는 이보다 크겠지만 (아마 1.1 – 1.3배), 모델의 3.6배와는 거리가 멀다. **H1 은 '맞다, 그러나 아주 작게'** 로 더 약해졌다.

**속도로 어림한 WAF** (NAND 쓰기 약 150 MB/s) : 150 ÷ 26 ≈ **5.8**. 모델은 2.2. span 100% 의 240 GB 무렵 값 (6.1) 과 거의 같다.

**SMART** : 177 이 133 → 140 (+7), 241 +480.1 GB → `smartdiff.py` 의 WAF 약 2.0 (1.72 – 2.29). 실험 8 처럼 첫 약 128 GB 를 WAF 1 로 보면, 절벽 뒤 352 GB 의 WAF 는 **약 2.4** (2.0 – 2.8). 실험 8 (span 100%) 에서 같은 방법으로 얻은 값도 약 2.4 였다. 곧 세 가지 WAF 가 서로 다르다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>WAF</th>
<th>span 100%</th>
<th>span 80%</th>
</tr></thead><tbody>
<tr><td>모델 (Desnoyers)</td><td>7.8</td><td>2.2</td></tr>
<tr><td>속도로 어림</td><td>약 6.1 (240 GB, 아직 내려가는 중)</td><td>약 5.8 (steady)</td></tr>
<tr><td>SMART 177 (절벽 뒤)</td><td>약 2.4 (실험 8, 120 GB 분량)</td><td>약 2.4 (352 GB 분량)</td></tr>
</tbody></table></div>

**남은 후보는 2 와 3.** 둘 다 'span 을 줄여도 steady 속도가 거의 그대로' 와 맞는다. 둘을 가르는 것은 177 이다 :
- **2번** (TRIM 된 뒤쪽을 여유로 쓰지 않는다) 이 맞다면 GC 의 복사 양도 span 과 상관없이 같으므로, 같은 480 GB 를 썼을 때 177 의 증가가 span 100% 와 80% 에서 같아야 한다.
- **3번** (느림이 GC 복사만이 아니다) 이 맞다면 복사 양은 모델처럼 span 100% 가 훨씬 많아야 한다 (모델대로라면 +7 이 아니라 +20 근처). 그런데도 속도는 비슷하다.

**다음에 해 볼 것**
- ~~**`sudo ./lab.sh cliff 100 4`** (약 3.5 – 4시간) : span 100% 의 steady state 와 177 의 증가를 같은 480 GB 로 잰다. steady 속도의 정확한 비와, 2 · 3번 후보를 한 번에 가른다~~ → 아래 결과 (2026.10.23)
- 그 다음 `cliff 50 4` : 여유를 아주 크게 했을 때도 속도와 177 이 그대로인지
</div>

<div class="result" markdown="1">
### span 100%, 4배 (2026.10.23 12:58 – 18:00, 302분)

결과 폴더 `20261023-125809-cliff-span100`. 실험 8 을 총 480 GB 로. span 80%, 4배와 같은 날, 같은 양.

![span 100% (4배) 와 span 80% (4배)](/old-ssd-experiments/10-over-provisioning/op-4x.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>쓴 양</th>
<th>span 100%, 4배 (IOPS)</th>
<th>span 80%, 4배 (IOPS)</th>
<th>80 ÷ 100</th>
</tr></thead><tbody>
<tr><td>평평한 구간 (20 – 100 GB, 중앙값)</td><td>36,969</td><td>36,855</td><td>1.0</td></tr>
<tr><td><strong>절벽의 자리</strong></td><td>약 128 GB</td><td>약 128 GB</td><td>같다</td></tr>
<tr><td>120 – 140 GB</td><td>12,674</td><td>14,797</td><td>1.17</td></tr>
<tr><td>140 – 160 GB</td><td>8,268</td><td>10,677</td><td>1.29</td></tr>
<tr><td>160 – 180 GB</td><td>7,307</td><td>9,632</td><td>1.32</td></tr>
<tr><td>180 – 200 GB</td><td>6,636</td><td>8,972</td><td>1.35</td></tr>
<tr><td>200 – 240 GB</td><td>6,063</td><td>7,518</td><td>1.24</td></tr>
<tr><td>240 – 280 GB</td><td>5,702</td><td>7,243</td><td>1.27</td></tr>
<tr><td>280 – 320 GB</td><td>5,556</td><td>6,405</td><td>1.15</td></tr>
<tr><td>320 – 360 GB</td><td>5,373</td><td>6,710</td><td>1.25</td></tr>
<tr><td>360 – 400 GB</td><td><strong>4,336</strong></td><td>6,474</td><td>1.49</td></tr>
<tr><td>400 – 440 GB</td><td><strong>3,545</strong></td><td>6,300</td><td>1.78</td></tr>
<tr><td>440 – 480 GB</td><td><strong>3,253</strong></td><td>6,320</td><td><strong>1.94</strong></td></tr>
<tr><td>240 GB 까지 걸린 시간</td><td>80 분</td><td>65 분 |</td></tr>
<tr><td>전체 시간</td><td>302 분</td><td>214 분</td><td>0.71</td></tr>
</tbody></table></div>

**처음 240 GB 는 실험 8 을 되풀이했다** (구간마다 ±7% 안, 240 GB 까지 80분 대 81분). 그런데 그 뒤가 새롭다.

**약 350 GB 에서 두 번째 내리막이 온다.** span 100% 는 320 – 350 GB 에서 약 5,450 으로 거의 평평하다가, 350 GB 부터 내려가기 시작해 480 GB 에서 약 **3,130** 이 되었다 (10 GB 구간 평균 : 5,376 → 4,799 → 4,205 → 3,728 → 3,475 → 3,282 → 3,130). 끝에서도 아주 조금씩 내려가고 있다. 350 GB 는 드라이브 전체 (120 GB) 를 약 3번 덮은 양으로, span 80% 가 평평해진 '범위를 약 3번 덮은 양' (약 300 GB) 과 같은 꼴이다. span 100% 에게는 그 자리가 평평해지는 곳이 아니라 한 번 더 떨어지는 곳이었다.

**그래서 아침의 결론을 고친다 : 1번 후보가 맞았다.** 240 GB 에서 잰 '1.3배' 는 span 100% 가 아직 steady 가 아니어서 나온 값이다. 같은 480 GB 끝에서의 비는 **약 1.9 – 2.0배** 이고, span 100% 가 아직 조금씩 내려가니 진짜 steady 끼리의 비는 이보다 조금 더 크다. 모델의 3.6배에는 못 미치지만, 'OP 를 늘리면 steady 가 몇 배 빨라진다' (H1) 는 이제 분명히 보인다.

**SMART 177** : 140 → 153 (**+13**), 241 +480.1 GB → `smartdiff.py` 의 WAF 약 3.7 (3.44 – 4.01). 첫 약 128 GB 를 WAF 1 로 보면 절벽 뒤 352 GB 의 WAF 는 **약 4.7** (4.3 – 5.1). span 80% 는 +7, 약 2.4 였다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>WAF</th>
<th>span 100%</th>
<th>span 80%</th>
<th>100 ÷ 80</th>
</tr></thead><tbody>
<tr><td>모델 (Desnoyers, steady)</td><td>7.8</td><td>2.2</td><td>3.5</td></tr>
<tr><td>속도로 어림 (끝, NAND 150 MB/s 가정)</td><td>약 11.7 (12.8 MB/s)</td><td>약 5.8 (26 MB/s)</td><td>약 2.0</td></tr>
<tr><td>SMART 177 (절벽 뒤 평균)</td><td>약 4.7</td><td>약 2.4</td><td>약 2.0</td></tr>
</tbody></table></div>

**2번 후보 (TRIM 된 뒤쪽을 여유로 쓰지 않는다) 는 아니다.** 같은 480 GB 를 쓰는 동안 span 80% 가 지운 횟수는 span 100% 의 약 절반이다 (+7 대 +13). TRIM 된 20% 는 분명 GC 의 여유로 쓰인다. 그리고 **177 의 비 (약 2.0) 와 속도의 비 (약 2.0) 가 맞는다** : 느려지는 만큼 GC 가 더 일한다.

**3번 후보는 '절대값' 에만 남는다.** 두 span 모두 속도로 어림한 WAF 가 177 의 WAF 의 약 2.4 – 2.5배다. 비율은 맞고 크기만 일정한 배수로 다르다는 것은, 둘 중 하나가 일정하게 어긋난다는 뜻이다 : 'NAND 쓰기 150 MB/s' 가정이 GC 중에는 너무 크거나 (실제로는 약 60 MB/s), 177 이 지움을 덜 센다 (실험 8 에서 의심한 것). [실험 12](/old-ssd-experiments/12-waf/) 의 순차 쓰기 (WAF ≈ 1 이어야 하는) 에서 177 이 얼마나 오르는지 보면 어느 쪽인지 가를 수 있다.

**조심할 것 : 온도.** 드라이브 온도 (SCT 기록, 10분마다) 는 span 80% 실행 내내 약 40 °C, span 100% 실행에서는 40 °C 로 시작해 두 번째 내리막 무렵 45 – 46 °C 까지 올랐다. 840 EVO 가 속도를 줄이는 온도는 이보다 훨씬 높은 것으로 알려져 있고, 177 (지운 횟수) 도 같은 방향을 가리키므로 열 때문만은 아닐 것이다. 그래도 같은 조건을 원하면 다음 실행에 바람을 쐬어 온도를 맞춘다.

**다음에 해 볼 것**
- ~~[실험 12](/old-ssd-experiments/12-waf/) `sudo ./lab.sh seqwaf`~~ **했음 (2026.10.25)** : 순차 쓰기의 WAF 가 약 1.14 로, 177 은 제대로 센다. 틀린 쪽은 'NAND 쓰기 150 MB/s' 가정이었다 : GC 중의 NAND 쓰기는 두 span 모두 약 60 MB/s. 위 표의 '속도로 어림' 줄은 약 2.5배 크게 나온 값이다
- ~~`cliff 50 4`~~ **했음 (2026.10.25)** : 아래 'span 50%, 4배'
- span 100% 를 더 길게 (`cliff 100 6`) : 3,130 아래로 얼마나 더 내려가는지
</div>

<div class="result" markdown="1">
### span 50%, 4배 (2026.10.25 12:55 – 14:37, 102분)

결과 폴더 `20261025-125522-cliff-span50`. 앞쪽 절반 (60 GB) 에만 4 KiB 랜덤 쓰기, 총 480 GB (4배). [실험 12](/old-ssd-experiments/12-waf/) 로 177 을 믿을 수 있게 된 뒤의 첫 실행이다.

![span 100% · 80% · 50% (모두 4배)](/old-ssd-experiments/10-over-provisioning/op-span50.png)

```
 177 Wear_Leveling_Count                     158            162           +4
 190 Airflow_Temperature_Cel                  32             43          +11
 241 Total_LBAs_Written              28581674007    29519438871    +937764864

host writes (241):       480.1 GB
erase count (177):  +4  ->  NAND writes ~ 550 GB
WAF ~ 1.15   (177 counts whole steps, so between 0.86 and 1.43)
```
</div>

**절벽은 이번에도 약 128 GB 에 있다.** span 50% 는 60 GB 만 쓰니, 약 60 GB 부터는 모든 쓰기가 덮어쓰기다. 그래도 드라이브는 128 GB 까지 37k IOPS 로 평평하게 쓰다가 그 자리에서 떨어진다. 세 번 모두 같은 자리 : **절벽은 덮어쓴 양이 아니라 '쓴 양' 으로 정해진다.** 드라이브는 빈 블록 (TRIM 뒤 약 128 GB) 을 다 쓸 때까지 GC 를 미룬다.

**절벽 뒤 steady 는 약 15,600 IOPS (64 MB/s)** 로, 140 GB 부근의 약 19,500 에서 천천히 내려와 약 280 GB 부터 평평하다 (340 – 360 GB 15,675, 마지막 10 GB 15,603).

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>span</th>
<th>steady IOPS (끝)</th>
<th>span 100% 의 몇 배</th>
<th>WAF (177, 절벽 뒤)</th>
<th>모델 WAF (Desnoyers)</th>
</tr></thead><tbody>
<tr><td>100%</td><td>3,171</td><td>1</td><td>약 4.7</td><td>7.8</td></tr>
<tr><td>80%</td><td>6,189</td><td>2.0</td><td>약 2.4</td><td>2.2</td></tr>
<tr><td><strong>50%</strong></td><td><strong>15,603</strong></td><td><strong>4.9</strong></td><td><strong>약 1.2 (1.0 – 1.4)</strong></td><td><strong>1.3</strong></td></tr>
</tbody></table></div>

절벽 뒤 WAF 는 앞의 128 GB 를 WAF 1 로 보고 셈했다 : (4 × 137 − 128) ÷ 352 ≈ 1.19. 177 의 눈금 때문에 1.0 – 1.4 다.

**WAF 는 모델과 맞는다.** span 80% (2.4 대 2.2) 와 span 50% (1.2 대 1.3) 는 모델 안쪽이다. span 100% 만 모델보다 훨씬 낮은데 (4.7 대 7.8), 드라이브가 사용자 용량 밖에 숨겨 둔 여유가 모델에 넣은 값보다 크다는 뜻일 수 있다. 여유가 클 때는 숨은 여유의 몫이 작아져서, 모델과 더 잘 맞는다.

**그런데 속도의 비 (4.9배) 가 WAF 의 비 (4.7 ÷ 1.2 ≈ 3.9배) 보다 크다.** 실험 12 의 방식으로 NAND 쓰기 속도를 셈하면 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>span</th>
<th>호스트 속도</th>
<th>× WAF</th>
<th>= NAND 쓰기</th>
</tr></thead><tbody>
<tr><td>100%</td><td>12.8 MB/s</td><td>4.7</td><td>약 60 MB/s</td></tr>
<tr><td>80%</td><td>25 MB/s</td><td>2.4</td><td>약 61 MB/s</td></tr>
<tr><td>50%</td><td>64 MB/s</td><td>1.2 (1.0 – 1.4)</td><td><strong>약 76 MB/s (64 – 89)</strong></td></tr>
</tbody></table></div>

span 100% 와 80% 는 약 60 MB/s 로 같았지만, span 50% 는 약 76 MB/s 로 더 높다. 'GC 중에는 NAND 가 약 60 MB/s' 는 고정된 값이 아니다. 고른 블록에 남은 유효 페이지가 적을수록 (WAF 1.2 면 약 16%) 옮기기 위해 읽는 일이 줄어 NAND 가 더 많은 시간을 쓰기에 쓴다. 그래도 순차 쓰기 (실험 12, 약 150 MB/s) 의 절반이다 : 옮길 페이지가 거의 없어도 지우기와 블록 관리에 시간이 든다. 무엇이 얼마인지는 밖에서는 가를 수 없다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>잰 것</th>
<th>값</th>
</tr></thead><tbody>
<tr><td>지연 (4 KiB, QD32, 전체)</td><td>p99.9 34.9 ms, 최대 93.9 ms</td></tr>
<tr><td>온도 (190)</td><td>32 → 43 °C</td></tr>
<tr><td>전체 시간</td><td>102 분 (span 80% 의 214 분, span 100% 의 302 분과 비교)</td></tr>
</tbody></table></div>

**정리 : 실험 10 의 H1 (OP 를 늘리면 steady 가 몇 배 빨라진다) 은 분명하다.** span 을 100 → 80 → 50% 로 줄이면 steady 는 1 : 2.0 : 4.9 로 빨라지고, 177 의 WAF 는 4.7 → 2.4 → 1.2 로 줄어든다. 파티션을 절반만 쓰고 나머지를 TRIM 해 두면, 이 드라이브의 랜덤 쓰기는 약 5배 빠르다.

<div class="result" markdown="1">
**다음에 해 볼 것**
- [실험 11](/old-ssd-experiments/11-hot-cold/) (뜨거운 데이터) : `sudo ./lab.sh cliff 100 4 zipf:1.2`. 실험 11 페이지는 2배를 적었지만, span 100% 는 약 350 GB 에서 한 번 더 떨어지니 4배로 해야 균일 랜덤 (span 100%, 4배) 과 비교할 수 있다
- span 100% 를 더 길게 (`cliff 100 6`) : 3,130 아래로 얼마나 더 내려가는지
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/9-idle-gc/' | relative_url }}">← 9. 쉬는 동안 GC</a><a href="{{ '/old-ssd-experiments/11-hot-cold/' | relative_url }}">11. 뜨거운 데이터 →</a></div>
