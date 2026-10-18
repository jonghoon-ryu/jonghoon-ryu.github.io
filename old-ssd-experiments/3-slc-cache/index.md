---
layout: default
title: 3. SLC 캐시
permalink: /old-ssd-experiments/3-slc-cache/
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

# 3. SLC 캐시 : 빠른 쓰기는 몇 GB 까지인가

<div class="glance">
<b>목표</b><span>TurboWrite 버퍼의 크기, 버퍼를 넘긴 뒤 TLC 에 바로 쓰는 속도, 버퍼가 다시 비는 데 걸리는 시간을 잰다</span>
<b>보는 FTL 개념</b><span>SLC 캐시 (pseudo-SLC), 쉬는 동안의 데이터 옮기기 (folding / migration)</span>
<b>지우나?</b><span>예. 드라이브 전체를 TRIM 하고 처음부터 끝까지 쓴다</span>
<b>연결</b><span>SATA (TRIM 이 필요하다)</span>
<b>시간</b><span>전체 쓰기 15–20분 + 회복 측정 30분</span>
<b>명령</b><span><code>sudo ./lab.sh slc</code>, <code>sudo ./lab.sh slc-idle 0 1 5 15</code>, <code>sudo ./lab.sh scan fresh 8</code></span>
</div>

## 왜 SLC 캐시를 쓰나

TLC 는 셀 하나에 3비트를 담느라 전압을 8단계로 정밀하게 맞춰야 해서, 쓰기가 느리다. 같은 셀에 1비트만 담으면 (SLC 처럼 쓰면) 훨씬 빠르게 쓸 수 있다.
840 EVO 는 TLC 의 일부를 이렇게 SLC 처럼 써서 **들어오는 쓰기를 빠르게 받아 두고**, 쉬는 동안 TLC 로 옮긴다. Samsung 은 이것을 TurboWrite 라고 불렀다.

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="TurboWrite"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">TurboWrite : TLC 의 일부를 SLC 처럼 써서 빠르게 받아 둔다</text><rect x="20" y="110" width="130" height="60" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="85.0" y="144.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">호스트 쓰기</text><rect x="230" y="45" width="220" height="80" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="340.0" y="73.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">SLC 버퍼 (약 3 GB)</text><text x="340.0" y="89.0" font-size="11.5" fill="#4d5656" text-anchor="middle">셀 하나에 1비트 : 빠르게 쓴다</text><text x="340.0" y="105.0" font-size="11.5" fill="#4d5656" text-anchor="middle">120GB 모델 기준 (알려진 값)</text><rect x="230" y="165" width="220" height="80" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="340.0" y="193.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TLC 영역</text><text x="340.0" y="209.0" font-size="11.5" fill="#4d5656" text-anchor="middle">셀 하나에 3비트 : 느리게 쓴다</text><text x="340.0" y="225.0" font-size="11.5" fill="#4d5656" text-anchor="middle">데이터가 최종적으로 사는 곳</text><line x1="150" y1="130" x2="228" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="175.0" y="100.0" font-size="11.5" fill="#566573" text-anchor="middle">평소</text><line x1="150" y1="150" x2="228" y2="200" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="150.0" y="205.0" font-size="11.5" fill="#566573" text-anchor="middle">버퍼가 다 차면</text><path d="M450,85 C540,85 540,205 452,205" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="600.0" y="140.0" font-size="12" font-weight="700" fill="#1f6f5c" text-anchor="middle">쉬는 동안 옮겨 쓴다</text><text x="600.0" y="158.0" font-size="11.5" fill="#4d5656" text-anchor="middle">(그래서 버퍼가 다시 빈다)</text><text x="380.0" y="278.0" font-size="11.5" fill="#566573" text-anchor="middle">SLC 는 쓰기가 빠르고 덜 닳는다. 대신 같은 셀에 1/3 만 담는다</text></svg>

이 구조 때문에 '쓰기 속도' 는 하나의 숫자가 아니다. 버퍼에 들어가는 동안의 속도와, 버퍼가 다 찬 뒤 TLC 에 바로 쓰는 속도가 따로 있다.

## 가설과 예상

<svg viewBox="0 0 760 340" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="SLC 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 : 순차 쓰기 속도, 처음 몇 GB 만 빠르다</text><line x1="85" y1="265.0" x2="725" y2="265.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="221.0" x2="725" y2="221.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="177.0" x2="725" y2="177.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="133.0" x2="725" y2="133.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="89.0" x2="725" y2="89.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="45.0" x2="725" y2="45.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="265" x2="725" y2="265" stroke="#566573" stroke-width="1.5"/><line x1="85" y1="45" x2="85" y2="265" stroke="#566573" stroke-width="1.5"/><line x1="85.0" y1="265" x2="85.0" y2="270" stroke="#566573" stroke-width="1.2"/><text x="85.0" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><line x1="191.66666666666666" y1="265" x2="191.66666666666666" y2="270" stroke="#566573" stroke-width="1.2"/><text x="191.7" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">20</text><line x1="298.3333333333333" y1="265" x2="298.3333333333333" y2="270" stroke="#566573" stroke-width="1.2"/><text x="298.3" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">40</text><line x1="405.0" y1="265" x2="405.0" y2="270" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">60</text><line x1="511.66666666666663" y1="265" x2="511.66666666666663" y2="270" stroke="#566573" stroke-width="1.2"/><text x="511.7" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">80</text><line x1="618.3333333333334" y1="265" x2="618.3333333333334" y2="270" stroke="#566573" stroke-width="1.2"/><text x="618.3" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">100</text><line x1="725.0" y1="265" x2="725.0" y2="270" stroke="#566573" stroke-width="1.2"/><text x="725.0" y="284.0" font-size="11.5" fill="#4d5656" text-anchor="middle">120</text><line x1="80" y1="265.0" x2="85" y2="265.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="269.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="80" y1="221.0" x2="85" y2="221.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="225.0" font-size="11.5" fill="#4d5656" text-anchor="end">100</text><line x1="80" y1="177.0" x2="85" y2="177.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="181.0" font-size="11.5" fill="#4d5656" text-anchor="end">200</text><line x1="80" y1="133.0" x2="85" y2="133.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="137.0" font-size="11.5" fill="#4d5656" text-anchor="end">300</text><line x1="80" y1="89.0" x2="85" y2="89.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="end">400</text><line x1="80" y1="45.0" x2="85" y2="45.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="49.0" font-size="11.5" fill="#4d5656" text-anchor="end">500</text><text x="405.0" y="305.0" font-size="12" fill="#2c3e50" text-anchor="middle">지금까지 쓴 양 (GB)</text><text x="33.0" y="155.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 33.0 155.0)">쓰기 속도 (MB/s)</text><rect x="85.0" y="45.0" width="16.0" height="220.0" rx="0" fill="#1f6f5c" fill-opacity="0.15" stroke="none" stroke-width="1.0"/><text x="93.0" y="61.0" font-size="11.5" font-weight="700" fill="#1f6f5c" text-anchor="middle">SLC</text><polyline points="85.0,89.0 101.0,89.0 102.6,203.4 725.0,203.4" fill="none" fill-opacity="1.0" stroke="#c0392b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><text x="117.0" y="80.2" font-size="11.5" fill="#2c3e50" text-anchor="start">사양 : 최대 약 410 MB/s (SATA, 120GB 모델)</text><text x="245.0" y="192.4" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="start">버퍼가 차면 TLC 에 바로 : 약 140 MB/s 로 알려져 있다</text><text x="245.0" y="234.2" font-size="11.5" fill="#2c3e50" text-anchor="start">꺾이는 위치 = 버퍼 크기, 낮은 쪽 높이 = TLC 쓰기 속도</text><text x="400.0" y="330.0" font-size="11.5" fill="#566573" text-anchor="middle">숫자는 리뷰 · 사양에서 기억하는 값 : 이 드라이브에서 직접 잰다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 버퍼는 약 3 GB 다</td><td>순차 쓰기 속도가 3 GB 근처에서 계단처럼 떨어진다</td></tr>
<tr><td>H2 버퍼 밖 TLC 쓰기는 약 100–150 MB/s 다</td><td>떨어진 뒤 끝까지 그 높이가 유지된다</td></tr>
<tr><td>H3 쉬면 버퍼가 다시 빈다</td><td>slc-idle 에서 쉰 시간이 길수록 빠르게 쓴 양이 3 GB 에 가까워진다</td></tr>
</tbody></table></div>

숫자는 기억하는 리뷰 · 사양 값이라 틀릴 수 있다. 어긋나면 그것이 이 드라이브의 진짜 값이다.

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="버퍼 회복"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">버퍼는 쉬면 다시 빈다 : 얼마나 쉬어야 할까</text><line x1="85" y1="215.0" x2="725" y2="215.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="172.5" x2="725" y2="172.5" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="130.0" x2="725" y2="130.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="87.5" x2="725" y2="87.5" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="45.0" x2="725" y2="45.0" stroke="#eaeded" stroke-width="1"/><line x1="85" y1="215" x2="725" y2="215" stroke="#566573" stroke-width="1.5"/><line x1="85" y1="45" x2="85" y2="215" stroke="#566573" stroke-width="1.5"/><line x1="213.0" y1="215" x2="213.0" y2="220" stroke="#566573" stroke-width="1.2"/><text x="213.0" y="234.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><line x1="341.0" y1="215" x2="341.0" y2="220" stroke="#566573" stroke-width="1.2"/><text x="341.0" y="234.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1</text><line x1="469.0" y1="215" x2="469.0" y2="220" stroke="#566573" stroke-width="1.2"/><text x="469.0" y="234.0" font-size="11.5" fill="#4d5656" text-anchor="middle">5</text><line x1="597.0" y1="215" x2="597.0" y2="220" stroke="#566573" stroke-width="1.2"/><text x="597.0" y="234.0" font-size="11.5" fill="#4d5656" text-anchor="middle">15</text><line x1="80" y1="215.0" x2="85" y2="215.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="219.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="80" y1="172.5" x2="85" y2="172.5" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="176.5" font-size="11.5" fill="#4d5656" text-anchor="end">1</text><line x1="80" y1="130.0" x2="85" y2="130.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="134.0" font-size="11.5" fill="#4d5656" text-anchor="end">2</text><line x1="80" y1="87.5" x2="85" y2="87.5" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="91.5" font-size="11.5" fill="#4d5656" text-anchor="end">3</text><line x1="80" y1="45.0" x2="85" y2="45.0" stroke="#566573" stroke-width="1.2"/><text x="76.0" y="49.0" font-size="11.5" fill="#4d5656" text-anchor="end">4</text><text x="405.0" y="255.0" font-size="12" fill="#2c3e50" text-anchor="middle">쉰 시간 (분)</text><text x="33.0" y="130.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 33.0 130.0)">빠르게 쓴 양 (GB)</text><rect x="183.0" y="206.5" width="60.0" height="8.5" rx="0" fill="#1f6f5c" fill-opacity="0.55" stroke="none" stroke-width="1.0"/><rect x="311.0" y="151.2" width="60.0" height="63.8" rx="0" fill="#1f6f5c" fill-opacity="0.55" stroke="none" stroke-width="1.0"/><rect x="439.0" y="87.5" width="60.0" height="127.5" rx="0" fill="#1f6f5c" fill-opacity="0.55" stroke="none" stroke-width="1.0"/><rect x="567.0" y="87.5" width="60.0" height="127.5" rx="0" fill="#1f6f5c" fill-opacity="0.55" stroke="none" stroke-width="1.0"/><line x1="85" y1="87.5" x2="725" y2="87.5" stroke="#c0392b" stroke-width="1.4" stroke-dasharray="4 4"/><text x="721.0" y="81.5" font-size="11.5" fill="#c0392b" text-anchor="end">버퍼 크기 (약 3 GB)</text><text x="400.0" y="290.0" font-size="11.5" fill="#566573" text-anchor="middle">막대 높이는 상상한 값 : slc-idle 0 1 5 15 로 잰 뒤 진짜 막대로 바꾼다</text></svg>

## 절차

```
# 0. check 를 다시 해서 DISC-MAX 가 0B 가 아닌지
$ sudo ./lab.sh check

# 1. 전체 TRIM → 2분 쉼 → 1 MiB 순차 쓰기 QD8 로 처음부터 끝까지, 1초마다 속도 기록
$ sudo ./lab.sh slc

# 2. 버퍼 회복 : 8 GiB 로 버퍼를 채운 뒤, 0 / 1 / 5 / 15 분 쉬고 다시 8 GiB 씩
$ sudo ./lab.sh slc-idle 0 1 5 15

# 3. 실험 1 의 비교 기준 : 방금 쓴 '새 데이터' 의 위치별 읽기 속도
$ sudo ./lab.sh scan fresh 8

# 4. 실험 2 의 비교 기준 : 새 데이터로 가득한 드라이브의 자가 진단 시간
$ sudo ./lab.sh selftest long
```

`slc` 와 `slc-idle` 은 지우기 전에 시리얼 끝 5자리 (`0389K`) 를 묻는다.

## 저장되는 것

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>파일</th>
<th>내용</th>
</tr></thead><tbody>
<tr><td><code>…-slc/slc_bw.log</code></td><td>1초마다 쓰기 대역폭 (KiB/s)</td></tr>
<tr><td><code>…-slc/slc_iops.log</code>, <code>slc_lat.log</code></td><td>1초마다 IOPS, 평균 지연</td></tr>
<tr><td><code>…-slc/slc.json</code></td><td>fio 요약 (전체 평균, 지연 분포)</td></tr>
<tr><td><code>…-slc-idle/fill_bw.log</code>, <code>idle0_bw.log</code>, <code>idle1_bw.log</code> …</td><td>회복 측정</td></tr>
<tr><td><code>…-scan-fresh/scan.csv</code></td><td>새 데이터의 위치별 읽기 속도</td></tr>
</tbody></table></div>

## 결과

<div class="result" markdown="1">
### 1단계 : `slc` (드라이브 전체 순차 쓰기)

2026.10.18 11:21, 결과 폴더 `20261018-112114-slc`. 전체 TRIM → 2분 쉼 → 1 MiB 순차 쓰기 QD8 로 120 GB 전체를 786초 동안.

![순차 쓰기 속도](/old-ssd-experiments/3-slc-cache/slc.png)

**교과서 같은 계단 하나**

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>구간</th>
<th>쓴 양</th>
<th>속도</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td>처음 약 6초</td><td>약 <strong>3.2 GB</strong></td><td><strong>533 MB/s</strong> (1초마다 533, 533, 533, 533, 533, 515)</td><td>SLC 버퍼 (TurboWrite) 에 쓰는 속도. 533 MB/s 는 SATA 3 의 한계 근처라, 버퍼 자체는 더 빠를 수도 있다</td></tr>
<tr><td>그 뒤 끝까지 (약 780초)</td><td>약 116.8 GB</td><td><strong>약 150 MB/s</strong> (147 – 153, 거의 평평)</td><td>버퍼가 다 찬 뒤 TLC 에 바로 쓰는 속도</td></tr>
<tr><td>전체 평균</td><td>120.03 GB / 786.6 s</td><td>152.6 MB/s</td><td>거의 전부가 TLC 직접 쓰기라 그 속도에 가깝다</td></tr>
</tbody></table></div>

화면의 fio 진행 줄 `w=144MiB/s` 는 같은 값이다 : 144 MiB/s × 1.049 = 151 MB/s (MiB 와 MB 의 차이는 [fio 사용법](/old-ssd-experiments/fio/) 3절).

**지연** : 1 MiB 쓰기 하나의 평균 54.7 ms, 99% 71.8 ms, 최대 137.6 ms. Little 의 법칙으로 맞춰 보면 : 동시에 8개 ÷ 54.7 ms × 1 MiB ≈ 153 MB/s. 측정값과 같다.

**SMART 앞뒤**

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>속성</th>
<th>앞</th>
<th>뒤</th>
<th>읽는 법</th>
</tr></thead><tbody>
<tr><td>241 Total_LBAs_Written</td><td>22,481,189,514</td><td>22,715,630,218</td><td>+234,440,704 × 512 B = <strong>120.03 GB</strong> : 정확히 드라이브 하나만큼 썼다</td></tr>
<tr><td>177 Wear_Leveling_Count</td><td>117</td><td><strong>118</strong></td><td>블록마다 평균 1번 더 지웠다 : 드라이브 전체를 한 번 쓴 것과 맞다</td></tr>
<tr><td>190 온도</td><td>32 °C</td><td><strong>48 °C</strong></td><td>13분 쓰기로 16 °C 올랐다 (정규화 값 100 − 48 = 52 가 지금까지의 최저 = 가장 뜨거웠던 때)</td></tr>
<tr><td>5 · 179 · 181–183 · 187 · 195 · 199</td><td>0</td><td>0</td><td>쓰기 실패 · 오류 없음</td></tr>
</tbody></table></div>

`smartdiff.py` 의 WAF : 177 이 1 만 늘어서 약 1.15 (눈금이 커서 0 – 2.3 사이라는 것만 말할 수 있다). 순차 쓰기의 WAF 는 실험 12 에서 5번 써서 다시 잰다.

**가설 확인**

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>결과</th>
</tr></thead><tbody>
<tr><td>H1 버퍼는 약 3 GB 다</td><td><strong>맞다</strong> : 약 3.2 GB 에서 계단처럼 떨어진다 (1초 단위라 ±0.5 GB)</td></tr>
<tr><td>H2 버퍼 밖 TLC 쓰기는 약 100–150 MB/s 다</td><td><strong>맞다, 위쪽 끝</strong> : 약 150 MB/s, 120 GB 내내 거의 흔들림 없이 평평</td></tr>
<tr><td>H3 쉬면 버퍼가 다시 빈다</td><td>2단계 (<code>slc-idle</code>) 에서 확인</td></tr>
</tbody></table></div>

**실험 1 과 비교** : 이 드라이브는 **쓰기는 정상** 이다 (버퍼 533 MB/s, TLC 150 MB/s : 이 모델에 알려진 값과 비슷하다). 문제는 오래 둔 데이터를 **읽을 때** 뿐이었다 (약 9 MB/s). 이제 드라이브 전체가 막 쓴 데이터이므로, 같은 지도 (`scan fresh 8`) 를 다시 그리면 '데이터의 나이' 만 다른 비교가 된다.

### 3단계 : `scan fresh 8` (새 데이터의 지도)

2026.10.18 11:45, 결과 폴더 `20261018-114459-scan-fresh`. 1단계가 드라이브 전체를 쓴 직후, 실험 1 의 지도와 **똑같은 방법** (256 MiB 마다 8 MiB, `O_DIRECT`, 같은 SATA 연결) 으로 다시 읽었다. 다른 것은 **데이터의 나이** 뿐이다.

![같은 드라이브, 오래된 데이터와 새 데이터](/old-ssd-experiments/3-slc-cache/scan-old-vs-fresh.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>지도</th>
<th>걸린 시간</th>
<th>구간 속도 중앙값</th>
<th>1 MiB 읽기 하나 (평균, 중앙값)</th>
<th>가장 느린 1 MiB 읽기 (중앙값 / 최악)</th>
</tr></thead><tbody>
<tr><td>오래된 데이터 (실험 1, 677일 전원 없음)</td><td>8.0 분</td><td><strong>9.8 MB/s</strong></td><td>107 ms</td><td>208 ms / <strong>1,008 ms</strong></td></tr>
<tr><td><strong>새 데이터 (방금 씀)</strong></td><td><strong>0.1 분 (약 9초)</strong></td><td><strong>444.7 MB/s</strong></td><td><strong>2.4 ms</strong></td><td>2.4 ms / <strong>2.6 ms</strong></td></tr>
<tr><td>차이</td><td>약 55배</td><td>약 45배</td><td>약 45배</td><td>최악 약 390배</td></tr>
</tbody></table></div>

- **새 데이터는 448개 구간 전부 381 – 481 MB/s** 다. 빠진 곳도, 느린 띠도 없다. 0 으로만 읽힌 구간은 0개 : 모두 진짜 NAND 를 읽었다.
- 실험 1 에서 빨랐던 곳 (TRIM 된 빈 곳, NAND 를 안 읽음) 과 거의 같은 속도다. 곧 **새 데이터는 NAND 에서 읽어도 SATA 링크의 한계까지 나온다.**
- 가장 느린 읽기가 2.6 ms 로 고르다 : 다시 읽기 (read retry) 가 거의 없다는 뜻이다.
- SMART : 187 · 195 0 그대로, 온도 31 → 33 °C (실험 1 의 지도 때는 31 → 40 °C).

**화면 출력 읽기.** `sudo ./lab.sh scan fresh 8` 의 터미널 출력 (SMART 표는 줄였다) :

```
[sudo] password for ryuj:
Sorry, try again.
[sudo] password for ryuj:
== results -> /home/ryuj/Ryu/old_ssd_results/20261018-114459-scan-fresh
   177 Wear_Leveling_Count     PO--C-   090   090   000    -    118
   187 Uncorrectable_Error_Cnt -O--CK   100   100   000    -    0
   190 Airflow_Temperature_Cel -O--CK   069   052   000    -    31
   241 Total_LBAs_Written      -O--CK   099   099   000    -    22715630218
   …
448/448   111.8 GiB    445.8 MB/s  max     2.4 ms  zero 0.00  ETA   0.0 min
read 3.8 GB in 0.1 min, mean 437.1 MB/s -> /home/ryuj/Ryu/old_ssd_results/20261018-114459-scan-fresh/scan.csv
   177 Wear_Leveling_Count     PO--C-   090   090   000    -    118
   187 Uncorrectable_Error_Cnt -O--CK   100   100   000    -    0
   190 Airflow_Temperature_Cel -O--CK   067   052   000    -    33
   241 Total_LBAs_Written      -O--CK   099   099   000    -    22715630218
   …
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>줄</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>Sorry, try again.</code></td><td>sudo 비밀번호를 한 번 잘못 쳤다. 실험과 상관없다</td></tr>
<tr><td><code>== results -&gt;</code></td><td>결과 폴더. 이름 = 시작 시각 (11:44:59) + 붙인 이름 (<code>fresh</code>). 실험 1 의 <code>scan-old</code> 와 구별된다</td></tr>
<tr><td>첫 SMART 표</td><td>읽기 전의 값 (마지막 열이 실제 숫자). 오류 (5 · 179 · 181–183 · 187 · 195) 모두 0. <strong>177 = 118</strong> : 아침 (117) 보다 1 늘었다 = 1단계에서 드라이브 전체를 한 번 썼다. <strong>241</strong> 은 1단계의 120 GB 가 더해진 값 (× 512 B = 11.63 TB). 온도 31 °C (1단계 끝에는 48 °C)</td></tr>
<tr><td><code>448/448</code></td><td>448개 구간 (256 MiB 씩) 중 마지막</td></tr>
<tr><td><code>111.8 GiB</code></td><td>위치 : 드라이브의 맨 끝</td></tr>
<tr><td><code>445.8 MB/s</code></td><td>이 구간의 읽기 속도</td></tr>
<tr><td><code>max 2.4 ms</code></td><td>이 구간에서 가장 느린 1 MiB 읽기. 오래된 데이터에서는 100 – 1,000 ms 였다</td></tr>
<tr><td><code>zero 0.00</code></td><td>0 으로만 읽힌 비율 = 0 : TRIM 된 빈 곳이 아니라 진짜 NAND 의 데이터다</td></tr>
<tr><td><code>ETA 0.0 min</code></td><td>남은 시간 : 끝</td></tr>
<tr><td><code>read 3.8 GB in 0.1 min, mean 437.1 MB/s</code></td><td>합계 : 3.8 GB (8 MiB × 448) 를 약 9초에, <strong>평균 437 MB/s</strong>. 아침의 같은 스캔은 8분, 7.9 MB/s : <strong>약 55배</strong></td></tr>
<tr><td>두 번째 SMART 표</td><td>읽은 뒤 : 오류 모두 0 그대로. 241 · 177 도 그대로 (읽기만 했다). 온도 <strong>31 → 33 °C</strong> : 오래된 데이터를 읽을 때 (31 → 40 °C) 와 달리 다시 읽기가 없어 거의 데워지지 않는다</td></tr>
</tbody></table></div>

**결론 : 실험 1 의 느림은 '데이터의 나이' 가 전부였다.** 같은 드라이브, 같은 연결, 같은 위치, 같은 방법에서, 1년 넘게 전원 없이 둔 데이터는 약 10 MB/s, 막 쓴 데이터는 약 445 MB/s 로 읽혔다. 드라이브 (컨트롤러, NAND, 연결) 자체는 멀쩡하다. 오래 둔 셀은 전하가 빠져 기준 전압을 여러 번 옮겨 가며 다시 읽어야 했고 (그래서 느리고 뜨거웠고), 새로 쓴 셀은 한 번에 읽힌다.

### 2단계 : `slc-idle` · 4단계 : `selftest long`

아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/2-features/' | relative_url }}">← 2. 기능 · 자가 진단</a><a href="{{ '/old-ssd-experiments/4-trim/' | relative_url }}">4. TRIM 과 매핑 없는 읽기 →</a></div>
