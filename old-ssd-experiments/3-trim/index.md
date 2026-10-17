---
layout: default
title: 3. TRIM 과 매핑 없는 읽기
permalink: /old-ssd-experiments/3-trim/
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

# 3. TRIM 과 매핑 없는 읽기 : NAND 를 안 거치는 읽기

<div class="glance">
<b>목표</b><span>TRIM 된 (매핑이 없는) LBA 를 읽으면 무엇이 얼마나 빨리 오는지, 데이터가 있는 LBA 와 비교한다</span>
<b>보는 FTL 개념</b><span>매핑 표 (L2P), TRIM, 매핑 없는 읽기, 'deterministic read zero after TRIM'</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA (USB 는 TRIM 이 안 되고, 어댑터 지연이 µs 단위 차이를 덮는다)</span>
<b>시간</b><span>약 30분</span>
<b>명령</b><span><code>sudo ./lab.sh trim</code></span>
</div>

## 배경 : 매핑 표

호스트는 디스크를 LBA (논리 블록 주소) 의 줄로 본다. NAND 에는 덮어쓰기가 안 되므로, FTL 은 쓸 때마다 새 자리에 쓰고 **LBA → NAND 위치** 를 표에 적는다. 읽을 때는 이 표를 찾아 그 자리를 읽는다.

<svg viewBox="0 0 760 325" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="매핑 표"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">FTL 의 매핑 표 : LBA 마다 &#x27;NAND 의 어디&#x27; 를 적어 둔다</text><text x="160.0" y="52.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LBA → NAND 위치</text><rect x="60" y="62" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="78.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><rect x="120" y="62" width="180" height="24" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="78.0" font-size="11.5" fill="#4d5656" text-anchor="middle">블록 12, 페이지 3</text><rect x="60" y="89" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="105.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1</text><rect x="120" y="89" width="180" height="24" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="105.0" font-size="11.5" fill="#4d5656" text-anchor="middle">블록 12, 페이지 4</text><rect x="60" y="116" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="132.0" font-size="11.5" fill="#4d5656" text-anchor="middle">2</text><rect x="120" y="116" width="180" height="24" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="132.0" font-size="11.5" fill="#4d5656" text-anchor="middle">블록 40, 페이지 0</text><rect x="60" y="143" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="159.0" font-size="11.5" fill="#4d5656" text-anchor="middle">3</text><rect x="120" y="143" width="180" height="24" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="159.0" font-size="11.5" fill="#4d5656" text-anchor="middle">블록 7, 페이지 9</text><rect x="60" y="170" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">4</text><rect x="120" y="170" width="180" height="24" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="210.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">없음</text><rect x="60" y="197" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="213.0" font-size="11.5" fill="#4d5656" text-anchor="middle">5</text><rect x="120" y="197" width="180" height="24" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="210.0" y="213.0" font-size="11.5" fill="#4d5656" text-anchor="middle">없음</text><rect x="60" y="224" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="240.0" font-size="11.5" fill="#4d5656" text-anchor="middle">6</text><rect x="120" y="224" width="180" height="24" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="210.0" y="240.0" font-size="11.5" fill="#4d5656" text-anchor="middle">없음</text><rect x="60" y="251" width="60" height="24" rx="0" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="90.0" y="267.0" font-size="11.5" fill="#4d5656" text-anchor="middle">7</text><rect x="120" y="251" width="180" height="24" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="210.0" y="267.0" font-size="11.5" fill="#4d5656" text-anchor="middle">없음</text><rect x="360" y="70" width="380" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="550.0" y="93.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">LBA 0–3 : 쓴 적 있음</text><text x="550.0" y="109.0" font-size="11.5" fill="#4d5656" text-anchor="middle">읽으면 → 표에서 위치 찾기 → NAND 읽기</text><text x="550.0" y="125.0" font-size="11.5" fill="#4d5656" text-anchor="middle">→ 수십 µs 이상</text><rect x="360" y="170" width="380" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="550.0" y="193.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">LBA 4–7 : TRIM 됨 (또는 쓴 적 없음)</text><text x="550.0" y="209.0" font-size="11.5" fill="#4d5656" text-anchor="middle">읽으면 → 표에 없음 → 바로 0 을 돌려줌</text><text x="550.0" y="225.0" font-size="11.5" fill="#4d5656" text-anchor="middle">→ NAND 를 안 건드린다 : 훨씬 빠름</text><line x1="300" y1="115" x2="358" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="300" y1="225" x2="358" y2="205" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="312.0" font-size="11.5" font-weight="700" fill="#1f6f5c" text-anchor="middle">시뮬레이터의 Unmapped_Reads_Return_Zeros 와 같은 동작</text></svg>

TRIM 은 '이 LBA 들은 이제 쓰지 않는다' 는 알림이다. FTL 은 표에서 그 줄을 지우고, 그 NAND 페이지를 무효로 표시한다. 그 뒤 그 LBA 를 읽으면 :
- 표에 없으니 NAND 를 읽을 것이 없다
- 컨트롤러는 0 (또는 정해진 값) 을 바로 돌려줄 수 있다

`hdparm -I` 에 **Deterministic read ZEROs after TRIM** 이 있으면 0 이 보장된다. 없으면 '정해지지 않음' 이지만, 실제로는 대부분 0 이다. 둘 다 이 실험에서 확인한다.

TRIM 이 성능에 중요한 또 다른 이유는 GC 다 :

<svg viewBox="0 0 760 270" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="TRIM 과 GC"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 이 GC 를 돕는 이유 : 지운 파일은 복사할 필요가 없다</text><text x="160.0" y="52.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 없이 : 지운 파일 (빨강) 도 &#x27;유효&#x27;</text><rect x="20" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="55" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="90" y="62" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="125" y="62" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="160" y="62" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="195" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="230" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="265" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="20" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="55" y="97" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="90" y="97" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="125" y="97" width="32" height="32" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><rect x="160" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="195" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="230" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="265" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="540.0" y="52.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 뒤 : 지운 파일은 &#x27;무효&#x27;</text><rect x="400" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="435" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="470" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="505" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="540" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="575" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="610" y="62" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="645" y="62" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="400" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="435" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="470" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="505" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="540" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><rect x="575" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="610" y="97" width="32" height="32" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><rect x="645" y="97" width="32" height="32" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="160.0" y="160.0" font-size="12.5" font-weight="700" fill="#c0392b" text-anchor="middle">GC 가 옮길 페이지 : 12개</text><text x="540.0" y="160.0" font-size="12.5" font-weight="700" fill="#1f6f5c" text-anchor="middle">GC 가 옮길 페이지 : 6개</text><rect x="150" y="190" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="170.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">유효</text><rect x="206" y="190" width="14" height="12" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="226.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">무효</text><rect x="262" y="190" width="14" height="12" rx="2" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="282.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="start">지웠지만 SSD 는 모름</text><text x="380.0" y="245.0" font-size="11.5" fill="#566573" text-anchor="middle">블록 하나 (페이지 16개) 를 비울 때 : 옮길 페이지가 적을수록 WAF 가 작다</text></svg>

## 가설과 예상

<svg viewBox="0 0 760 330" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="TRIM 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 : 4 KiB 랜덤 읽기 지연 (QD1)</text><line x1="85" y1="255" x2="725" y2="255" stroke="#566573" stroke-width="1.5"/><line x1="85" y1="45" x2="85" y2="255" stroke="#566573" stroke-width="1.5"/><line x1="85.0" y1="255" x2="85.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="85.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><line x1="165.0" y1="255" x2="165.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="165.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">25</text><line x1="245.0" y1="255" x2="245.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="245.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">50</text><line x1="325.0" y1="255" x2="325.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="325.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">75</text><line x1="405.0" y1="255" x2="405.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">100</text><line x1="485.0" y1="255" x2="485.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="485.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">125</text><line x1="565.0" y1="255" x2="565.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="565.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">150</text><line x1="645.0" y1="255" x2="645.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="645.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">175</text><line x1="725.0" y1="255" x2="725.0" y2="260" stroke="#566573" stroke-width="1.2"/><text x="725.0" y="274.0" font-size="11.5" fill="#4d5656" text-anchor="middle">200</text><text x="405.0" y="295.0" font-size="12" fill="#2c3e50" text-anchor="middle">읽기 한 번의 지연 (µs)</text><text x="33.0" y="150.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 33.0 150.0)">비율</text><polyline points="117.0,255.0 117.0,255.0 120.2,254.9 123.4,254.9 126.6,254.8 129.8,254.6 133.0,254.3 136.2,253.7 139.4,252.9 142.6,251.6 145.8,249.5 149.0,246.6 152.2,242.5 155.4,236.7 158.6,229.2 161.8,219.4 165.0,207.4 168.2,193.0 171.4,176.5 174.6,158.3 177.8,139.2 181.0,120.1 184.2,102.1 187.4,86.5 190.6,74.4 193.8,66.7 197.0,64.1 200.2,66.7 203.4,74.4 206.6,86.5 209.8,102.1 213.0,120.1 216.2,139.2 219.4,158.3 222.6,176.5 225.8,193.0 229.0,207.4 232.2,219.4 235.4,229.2 238.6,236.7 241.8,242.5 245.0,246.6 248.2,249.5 251.4,251.6 254.6,252.9 257.8,253.7 261.0,254.3 264.2,254.6 267.4,254.8 270.6,254.9 273.8,254.9 277.0,255.0 280.2,255.0 283.4,255.0 286.6,255.0 289.8,255.0 293.0,255.0 296.2,255.0 299.4,255.0 302.6,255.0 305.8,255.0 309.0,255.0 309.0,255.0" fill="#1f6f5c" fill-opacity="0.3" stroke="none" stroke-width="0" stroke-linejoin="round" stroke-linecap="round"/><polyline points="117.0,255.0 120.2,254.9 123.4,254.9 126.6,254.8 129.8,254.6 133.0,254.3 136.2,253.7 139.4,252.9 142.6,251.6 145.8,249.5 149.0,246.6 152.2,242.5 155.4,236.7 158.6,229.2 161.8,219.4 165.0,207.4 168.2,193.0 171.4,176.5 174.6,158.3 177.8,139.2 181.0,120.1 184.2,102.1 187.4,86.5 190.6,74.4 193.8,66.7 197.0,64.1 200.2,66.7 203.4,74.4 206.6,86.5 209.8,102.1 213.0,120.1 216.2,139.2 219.4,158.3 222.6,176.5 225.8,193.0 229.0,207.4 232.2,219.4 235.4,229.2 238.6,236.7 241.8,242.5 245.0,246.6 248.2,249.5 251.4,251.6 254.6,252.9 257.8,253.7 261.0,254.3 264.2,254.6 267.4,254.8 270.6,254.9 273.8,254.9 277.0,255.0 280.2,255.0 283.4,255.0 286.6,255.0 289.8,255.0 293.0,255.0 296.2,255.0 299.4,255.0 302.6,255.0 305.8,255.0 309.0,255.0" fill="none" fill-opacity="1.0" stroke="#1f6f5c" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/><polyline points="245.0,255.0 245.0,254.8 252.5,254.7 259.9,254.6 267.4,254.4 274.9,254.0 282.3,253.6 289.8,252.9 297.3,252.0 304.7,250.8 312.2,249.2 319.7,247.1 327.1,244.5 334.6,241.1 342.1,237.1 349.5,232.2 357.0,226.4 364.5,219.8 371.9,212.5 379.4,204.4 386.9,195.7 394.3,186.8 401.8,177.8 409.3,169.1 416.7,161.1 424.2,153.9 431.7,148.0 439.1,143.7 446.6,141.2 454.1,140.5 461.5,141.7 469.0,144.8 476.5,149.6 483.9,155.8 491.4,163.3 498.9,171.6 506.3,180.4 513.8,189.4 521.3,198.3 528.7,206.7 536.2,214.6 543.7,221.8 551.1,228.2 558.6,233.7 566.1,238.3 573.5,242.2 581.0,245.3 588.5,247.8 595.9,249.7 603.4,251.2 610.9,252.3 618.3,253.1 625.8,253.7 633.3,254.1 640.7,254.4 648.2,254.6 655.7,254.8 663.1,254.9 670.6,254.9 678.1,254.9 685.5,255.0 693.0,255.0 693.0,255.0" fill="#2874a6" fill-opacity="0.3" stroke="none" stroke-width="0" stroke-linejoin="round" stroke-linecap="round"/><polyline points="245.0,254.8 252.5,254.7 259.9,254.6 267.4,254.4 274.9,254.0 282.3,253.6 289.8,252.9 297.3,252.0 304.7,250.8 312.2,249.2 319.7,247.1 327.1,244.5 334.6,241.1 342.1,237.1 349.5,232.2 357.0,226.4 364.5,219.8 371.9,212.5 379.4,204.4 386.9,195.7 394.3,186.8 401.8,177.8 409.3,169.1 416.7,161.1 424.2,153.9 431.7,148.0 439.1,143.7 446.6,141.2 454.1,140.5 461.5,141.7 469.0,144.8 476.5,149.6 483.9,155.8 491.4,163.3 498.9,171.6 506.3,180.4 513.8,189.4 521.3,198.3 528.7,206.7 536.2,214.6 543.7,221.8 551.1,228.2 558.6,233.7 566.1,238.3 573.5,242.2 581.0,245.3 588.5,247.8 595.9,249.7 603.4,251.2 610.9,252.3 618.3,253.1 625.8,253.7 633.3,254.1 640.7,254.4 648.2,254.6 655.7,254.8 663.1,254.9 670.6,254.9 678.1,254.9 685.5,255.0 693.0,255.0" fill="none" fill-opacity="1.0" stroke="#2874a6" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/><text x="229.0" y="73.6" font-size="11.5" font-weight="700" fill="#1f6f5c" text-anchor="start">매핑 없음 (TRIM 된 절반)</text><text x="485.0" y="129.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="start">매핑 있음 (쓴 절반) : NAND 읽기</text><text x="400.0" y="320.0" font-size="11.5" fill="#566573" text-anchor="middle">위치와 폭은 예시 : USB 로는 어댑터 지연이 둘 다에 더해지므로 SATA 에서 잰다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 TRIM 된 LBA 는 0 으로 읽힌다</td><td>전체 TRIM 직후 스캔의 <code>zero_frac</code> 이 모든 구간에서 1.0</td></tr>
<tr><td>H2 매핑 없는 읽기는 NAND 를 안 거친다</td><td>QD1 4 KiB 랜덤 읽기 지연 : 매핑 없음이 매핑 있음보다 확실히 짧다 (NAND 페이지 읽기 시간만큼)</td></tr>
<tr><td>H3 그래서 IOPS 도 높다</td><td>QD32 IOPS : 매핑 없음 &gt; 매핑 있음. 단 SATA 인터페이스 한계 (약 10만 IOPS) 에 둘 다 걸리면 차이가 줄어든다</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh trim
```

스크립트가 하는 일 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
<th>왜</th>
</tr></thead><tbody>
<tr><td>1</td><td><code>blkdiscard</code> 로 전체 TRIM, 2분 쉼</td><td>모든 매핑을 지운 출발점</td></tr>
<tr><td>2</td><td>스캔 (256 MiB 마다 32 MiB) → <code>scan-trimmed.csv</code></td><td>H1 : 다 0 인가, 얼마나 빠른가</td></tr>
<tr><td>3</td><td>앞쪽 절반을 1 MiB 순차로 쓴다</td><td>앞 절반만 매핑이 생긴다</td></tr>
<tr><td>4</td><td>4 KiB 랜덤 읽기 QD1, 60초 : 앞 절반 → <code>rd-mapped</code>, 뒤 절반 → <code>rd-unmapped</code></td><td>H2 : 읽기 하나의 지연</td></tr>
<tr><td>5</td><td>같은 것을 QD32 로 → <code>rd32-mapped</code>, <code>rd32-unmapped</code></td><td>H3 : IOPS</td></tr>
<tr><td>6</td><td>다시 스캔 → <code>scan-half.csv</code></td><td>앞 절반은 데이터, 뒤 절반은 0 인지 한 그림으로</td></tr>
</tbody></table></div>

실험을 시작하기 전에 `sudo hdparm -I /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K | grep -i trim` 의 출력을 남겨 둔다 (`check` 결과 폴더의 `hdparm-I.txt` 에도 있다).

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-trim | tail -1)
$ python3 plot.py lat.png $D/rd-mapped_lat.log=mapped $D/rd-unmapped_lat.log=unmapped
$ python3 plot.py scans.png $D/scan-trimmed.csv=trimmed $D/scan-half.csv=half
```

1. **지연** : 각 `rd-*.json` 의 `clat` percentile (50%, 99%, 99.9%) 을 표로 놓는다. 차이 = NAND 페이지 읽기 + FTL 의 일. 840 EVO 의 TLC 페이지 읽기 시간을 거꾸로 추정해 볼 수 있다.
2. **IOPS** : `rd32-*` 의 IOPS. 매핑 없는 쪽이 SATA 한계에 붙으면, 그 값이 '인터페이스의 한계' 다.
3. **0 확인** : `scan-trimmed.csv` 의 `zero_frac` 이 모두 1 이 아니면, TRIM 뒤에 0 이 아닌 값이 나온 것이다 (흥미로운 결과).
4. **실험 1 과 연결** : 실험 1 의 위치 지도에서 0 으로 읽힌 빈 공간이 빨랐다면, 같은 현상이다.

## 시뮬레이터와의 연결

시뮬레이터의 `Unmapped_Reads_Return_Zeros` 와 읽기 지연 차트가 바로 이 동작이다. 실제 드라이브에서 잰 두 지연 (매핑 있음 / 없음) 을 시뮬레이터 설정의 읽기 시간과 비교한다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/2-slc-cache/' | relative_url }}">← 2. SLC 캐시</a><a href="{{ '/old-ssd-experiments/4-write-cliff/' | relative_url }}">4. Write cliff →</a></div>
