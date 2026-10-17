---
layout: default
title: 5. 성능 지도
permalink: /old-ssd-experiments/5-perf-map/
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

# 5. 성능 지도 : 블록 크기 × 큐 깊이, 그리고 데이터 내용

<div class="glance">
<b>목표</b><span>읽기 · 쓰기 속도를 블록 크기와 큐 깊이의 모든 조합으로 재서 이 드라이브의 '지도' 를 만들고, 큐 깊이로 드러나는 안쪽 병렬성과 SATA 의 한계를 찾는다. 데이터 내용 (0, 무작위, 압축되는 것) 이 쓰기 속도를 바꾸는지도 본다</span>
<b>보는 FTL 개념</b><span>채널 · die 병렬성, NCQ, Little 의 법칙, 인터페이스 한계, 컨트롤러의 압축 · 중복 제거 (있는가?)</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span><code>perfmap</code> 약 1시간 (채우기 포함), <code>pattern</code> 약 30분</span>
<b>명령</b><span><code>sudo ./lab.sh perfmap</code>, <code>sudo ./lab.sh pattern</code></span>
</div>

## 배경 : 큐 깊이가 왜 속도를 바꾸나

SSD 안에는 NAND 칩 (die) 이 여러 개 있고, 컨트롤러는 여러 채널로 동시에 일을 시킬 수 있다. 그러나 호스트가 **한 번에 하나씩만** 요청하면 (큐 깊이 1) 다른 die 들은 놀고 있다.
요청을 여러 개 걸어 두면 (NCQ, SATA 는 최대 32개) 컨트롤러가 여러 die 에 나눠 준다. 그래서 큐 깊이를 올리면 IOPS 가 오르다가, die 들이 다 바빠지거나 SATA 링크가 한계에 닿는 지점에서 멈춘다. 그 뒤로는 지연만 는다.

[fio 페이지 5절](/old-ssd-experiments/fio/) 의 **Little 의 법칙** : IOPS ≈ 큐 깊이 ÷ 지연. 큐 깊이를 올렸는데 IOPS 가 그대로면 지연이 그만큼 늘었다는 뜻이다.

## 가설과 예상

Samsung 이 밝힌 840 EVO 120GB 의 값 (기억하는 사양 값, 확인 필요) : 순차 읽기 540 MB/s, 순차 쓰기 410 MB/s (TurboWrite 안), 4 KiB 랜덤 읽기 QD32 94K IOPS, 랜덤 쓰기 QD32 35K IOPS.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 QD1 랜덤 읽기는 NAND 읽기 지연에 묶인다</td><td>4k QD1 : 약 1만 IOPS 이하 (지연 약 100 µs)</td></tr>
<tr><td>H2 큐 깊이로 병렬성이 드러난다</td><td>4k : QD4 에서 3–4배, QD32 에서 사양 값 근처 (94K). 오름이 멈추는 큐 깊이 = 안쪽 병렬성의 크기</td></tr>
<tr><td>H3 큰 블록은 SATA 한계에 닿는다</td><td>128k · 1m 읽기 : QD 와 상관없이 약 530–550 MB/s</td></tr>
<tr><td>H4 쓰기는 SLC 버퍼 안에서 빠르다</td><td>15초 쓰기들은 모두 버퍼 안의 속도 (실험 3 의 '빠른 구간' 과 같아야 한다)</td></tr>
<tr><td>H5 데이터 내용은 속도를 바꾸지 않는다</td><td><code>pattern</code> 의 다섯 가지가 같은 속도. 0 이나 압축되는 데이터가 빠르면 컨트롤러가 압축 · 중복 제거 · 0 특별 처리를 한다는 뜻 (SandForce 계열은 그랬다)</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh perfmap
$ sudo ./lab.sh pattern
```

`perfmap` 이 하는 일 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
<th>왜</th>
</tr></thead><tbody>
<tr><td>1</td><td>전체 TRIM, 그다음 1 MiB 순차로 전체를 채운다</td><td>읽기가 진짜 NAND 를 읽게 (TRIM 된 곳을 읽으면 NAND 를 안 거친다 : 실험 4)</td></tr>
<tr><td>2</td><td>읽기 : <code>randread</code> · <code>read</code> × <code>4k</code> · <code>16k</code> · <code>128k</code> · <code>1m</code> × QD <code>1</code> · <code>4</code> · <code>32</code>, 각 20초 (처음 2초는 빼고)</td><td>24칸의 읽기 지도</td></tr>
<tr><td>3</td><td>쓰기 : <code>randwrite</code> · <code>write</code> × <code>4k</code> · <code>128k</code> · <code>1m</code> × QD <code>1</code> · <code>32</code>, 각 15초, 사이에 30초 쉼</td><td>12칸의 쓰기 지도 (버퍼 안)</td></tr>
<tr><td>4</td><td><code>summary.csv</code> : 칸마다 IOPS, MB/s, 지연 평균 · 50% · 99% · 99.9% · 최대</td><td>표와 그림의 재료</td></tr>
</tbody></table></div>

`pattern` 이 하는 일 : 전체 TRIM 뒤, 서로 다른 16 GiB 구간마다 1 MiB 순차 쓰기를 16 GiB (SLC 버퍼의 몇 배) 씩, 다섯 가지 내용으로 한다. 사이에 3분 쉰다 (버퍼가 비게).

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>이름</th>
<th>fio 옵션</th>
<th>내용</th>
</tr></thead><tbody>
<tr><td><code>zeros</code></td><td><code>--zero_buffers</code></td><td>모두 0</td></tr>
<tr><td><code>random</code></td><td><code>--refill_buffers</code></td><td>I/O 마다 새 무작위 (압축 불가)</td></tr>
<tr><td><code>comp50</code></td><td><code>--buffer_compress_percentage=50</code></td><td>절반쯤 압축되는 내용</td></tr>
<tr><td><code>comp90</code></td><td><code>--buffer_compress_percentage=90</code></td><td>90% 압축되는 내용</td></tr>
<tr><td><code>deadbeef</code></td><td><code>--buffer_pattern=0xdeadbeef</code></td><td>4바이트 무늬 반복 (중복 제거가 있다면 가장 유리)</td></tr>
</tbody></table></div>

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-perfmap | tail -1)
$ column -s, -t $D/summary.csv
$ column -s, -t $(ls -d ~/Ryu/old_ssd_results/*-pattern | tail -1)/summary.csv
```

1. **4k randread 의 IOPS – QD 곡선** : QD1 → 4 → 32 의 배수. 각 칸에서 `QD ÷ 평균 지연` 을 계산해 IOPS 와 맞는지 본다 (Little).
2. **블록 크기 – MB/s** : 어느 크기부터 SATA 한계에 붙나. 그 아래에서는 무엇이 한계인가 (die 의 페이지 읽기 시간 × 병렬성).
3. **꼬리** : QD32 의 99.9% 지연. 실험 13 에서 '쓰기가 섞일 때' 와 비교한다.
4. **pattern** : 다섯 줄의 MB/s 가 ±5% 안이면 H5 가 맞다.

Claude 가 `summary.csv` 로 열 지도 (heatmap) 와 QD 곡선을 그려 결과에 붙인다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/4-trim/' | relative_url }}">← 4. TRIM 과 매핑 없는 읽기</a><a href="{{ '/old-ssd-experiments/6-write-size/' | relative_url }}">6. 쓰기 크기 · 정렬 →</a></div>
