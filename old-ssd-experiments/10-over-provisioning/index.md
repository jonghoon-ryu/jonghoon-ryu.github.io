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
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/9-idle-gc/' | relative_url }}">← 9. 쉬는 동안 GC</a><a href="{{ '/old-ssd-experiments/11-hot-cold/' | relative_url }}">11. 뜨거운 데이터 →</a></div>
