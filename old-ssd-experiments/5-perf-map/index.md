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

## 결과

<div class="result" markdown="1">
### 1단계 : `perfmap`

2026.10.18 13:14 – 14:03, 결과 폴더 `20261018-131446-perfmap`. 전체 TRIM → 1 MiB 순차로 전체를 채움 (약 143 MB/s) → 읽기 24칸 (각 20초) → 쓰기 12칸 (각 15초, 사이 30초 쉼).

#### 읽기

![읽기 대역 : 블록 크기 × 큐 깊이](/old-ssd-experiments/5-perf-map/reads.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>랜덤 읽기</th>
<th>QD1</th>
<th>QD4</th>
<th>QD32</th>
</tr></thead><tbody>
<tr><td>4 KiB</td><td>7.0k IOPS · 29 MB/s · 127 µs</td><td>25.1k · 103 MB/s · 152 µs</td><td><strong>90.7k</strong> · 372 MB/s · 351 µs</td></tr>
<tr><td>16 KiB</td><td>5.9k · 97 MB/s · 153 µs</td><td>17.2k · 281 MB/s · 222 µs</td><td>30.4k · 499 MB/s · 1.0 ms</td></tr>
<tr><td>128 KiB</td><td>2.3k · 300 MB/s · 394 µs</td><td>4.2k · <strong>549 MB/s</strong> · 0.9 ms</td><td>4.2k · 550 MB/s · 7.6 ms</td></tr>
<tr><td>1 MiB</td><td>419 · 439 MB/s · 2.1 ms</td><td>527 · <strong>553 MB/s</strong> · 7.4 ms</td><td>525 · 552 MB/s · 61 ms</td></tr>
</tbody></table></div>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>순차 읽기</th>
<th>QD1</th>
<th>QD4</th>
<th>QD32</th>
</tr></thead><tbody>
<tr><td>4 KiB</td><td><strong>19.4k</strong> IOPS · 80 MB/s · <strong>44 µs</strong></td><td><strong>94.4k</strong> · 387 MB/s · 41 µs</td><td>94.2k · 386 MB/s · 337 µs</td></tr>
<tr><td>16 KiB</td><td>13.1k · 214 MB/s · 65 µs</td><td>30.9k · 506 MB/s · 123 µs</td><td>30.8k · 505 MB/s · 1.0 ms</td></tr>
<tr><td>128 KiB</td><td>3.2k · 421 MB/s · 272 µs</td><td>4.2k · <strong>551 MB/s</strong> · 0.9 ms</td><td>4.0k · 527 MB/s · 7.9 ms</td></tr>
<tr><td>1 MiB</td><td>470 · 493 MB/s · 1.9 ms</td><td>503 · 527 MB/s · 7.7 ms</td><td>517 · 544 MB/s · 62 ms</td></tr>
</tbody></table></div>

(칸마다 IOPS · MB/s · 평균 지연)

- **H1 (QD1 랜덤 읽기는 NAND 읽기에 묶인다) : 맞다.** 4 KiB QD1 은 7.0k IOPS, 127 µs. [실험 4](/old-ssd-experiments/4-trim/) 에서 같은 측정이 121 µs (중앙값) 였다 : 그중 약 60 µs 가 NAND 페이지 읽기다.
- **H2 (큐 깊이로 병렬성이 드러난다) : 맞다.** 4 KiB 랜덤 : QD4 에서 3.6배, QD32 에서 12.9배 (**90.7k**, Samsung 이 밝힌 9.4만 근처). 칸마다 '깊이 ÷ 평균 지연' 이 IOPS 와 맞는다 (4 ÷ 152 µs = 26k, 32 ÷ 351 µs = 91k : Little 의 법칙). QD4 → QD32 에서 지연이 2.3배로 늘었으니, 그 사이 어딘가에서 드라이브 안의 칩들이 다 바빠졌다.
- **H3 (큰 블록은 SATA 한계에 닿는다) : 맞다.** 128 KiB 와 1 MiB 는 QD4 에서 이미 549 – 553 MB/s : 그림의 점선 (SATA 3, 약 550 MB/s). 그 뒤로 큐를 늘리면 지연만 는다 (1 MiB QD32 = 61 ms).
- **새로 보인 것 : 순차 4 KiB 는 QD1 에서도 44 µs.** 랜덤 (127 µs) 의 3분의 1이고, 실험 4 에서 어림한 NAND 페이지 읽기 (약 60 µs) 보다도 짧다 : 드라이브가 순차 읽기를 알아채고 **다음 데이터를 미리 읽어 두는 (read-ahead)** 것으로 보인다. 큰 NAND 페이지 하나에 4 KiB 가 여럿 들어 있으니, 한 번 읽은 페이지에서 다음 4 KiB 를 바로 꺼낼 수도 있다.
- **4 KiB 의 천장은 약 9.4만 IOPS** (순차 QD4 · QD32, 랜덤 QD32 모두) : 실험 4 의 결론과 같은 **SATA 명령 처리의 한계** 다. 순차는 QD4 에서 벌써 닿았다 (미리 읽기 덕분에 하나의 시간이 41 µs).

#### 쓰기

![쓰기 대역과 99.9% 지연 (실행 순서대로)](/old-ssd-experiments/5-perf-map/writes.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실행 순서</th>
<th>쓰기</th>
<th>MB/s</th>
<th>평균 지연</th>
<th>99.9% 지연</th>
<th>가장 긴 것</th>
</tr></thead><tbody>
<tr><td>1</td><td>랜덤 4 KiB QD1</td><td>74 (18.0k IOPS)</td><td><strong>47 µs</strong></td><td>0.1 ms</td><td>0.5 ms</td></tr>
<tr><td>2</td><td>랜덤 4 KiB QD32</td><td>223 (54.5k IOPS)</td><td>0.6 ms</td><td>35 ms</td><td>261 ms</td></tr>
<tr><td>3</td><td>랜덤 128 KiB QD1</td><td>208</td><td>0.6 ms</td><td>63 ms</td><td>276 ms</td></tr>
<tr><td>4</td><td>랜덤 128 KiB QD32</td><td><strong>71</strong></td><td>59 ms</td><td>463 ms</td><td>588 ms</td></tr>
<tr><td>5</td><td>랜덤 1 MiB QD1</td><td><strong>34</strong></td><td>30 ms</td><td>100 ms</td><td>100 ms</td></tr>
<tr><td>6</td><td>랜덤 1 MiB QD32</td><td><strong>29</strong></td><td><strong>1.15 s</strong></td><td><strong>4.6 s</strong></td><td>4.6 s</td></tr>
<tr><td>7</td><td>순차 4 KiB QD1</td><td>48 (11.8k IOPS)</td><td>76 µs</td><td>13 ms</td><td>111 ms</td></tr>
<tr><td>8</td><td>순차 4 KiB QD32</td><td>142</td><td>0.9 ms</td><td>31 ms</td><td>242 ms</td></tr>
<tr><td>9</td><td>순차 128 KiB QD1</td><td>197</td><td>0.6 ms</td><td>21 ms</td><td>240 ms</td></tr>
<tr><td>10</td><td>순차 128 KiB QD32</td><td>256</td><td>16 ms</td><td>230 ms</td><td>249 ms</td></tr>
<tr><td>11</td><td>순차 1 MiB QD1</td><td>276</td><td>3.5 ms</td><td>215 ms</td><td>291 ms</td></tr>
<tr><td>12</td><td>순차 1 MiB QD32</td><td>290</td><td>116 ms</td><td>518 ms</td><td>523 ms</td></tr>
</tbody></table></div>

**H4 (짧은 쓰기는 모두 SLC 버퍼 안의 속도) : 아니다.** 쓰기는 블록 크기 · 큐 깊이보다 **드라이브가 꽉 찬 상태에서 무엇을 먼저 썼나** 에 따라 움직였다 :
- 이 측정 전에 드라이브 전체를 채웠다 (120 GB). 그러니 쓰기는 모두 **덮어쓰기** 이고, 빈 블록은 숨은 여유 공간 (OP) 뿐이다.
- **랜덤 덮어쓰기가 이어질수록 무너졌다** : 223 → 208 → 71 → 34 → **29 MB/s**, 마지막에는 1 MiB 쓰기 하나가 평균 1.15 초, 가장 길게 4.6 초. 랜덤으로 덮어쓰면 옛 데이터가 여러 블록에 흩어지고, 빈 블록을 만들려면 GC 가 남은 데이터를 복사해야 한다. 30초 쉼으로는 따라잡지 못했다. **[실험 8](/old-ssd-experiments/8-write-cliff/) 의 write cliff 를 미리 본 것이다.**
- **순차 쓰기로 바꾸자 회복했다** : 48 → 142 → 197 → 256 → 276 → **290 MB/s**. 순차 덮어쓰기는 블록을 통째로 무효로 만들어 GC 가 쉽다. 마지막의 290 MB/s 는 TLC 직접 쓰기 (약 150 MB/s, [실험 3](/old-ssd-experiments/3-slc-cache/)) 보다 빠르다 : SLC 버퍼가 다시 일부 쓰이고 있다.
- **랜덤 4 KiB QD1 은 47 µs** : NAND 에 쓰는 시간이 아니다. 드라이브의 쓰기 캐시 (DRAM) 에 담기면 '끝' 이다 ([실험 7](/old-ssd-experiments/7-flush/) 이 이것을 잰다).
- 이 표의 쓰기 숫자는 '이 드라이브의 쓰기 속도' 가 아니라 '**이 순서로 썼을 때**' 의 숫자다. Ref 페이지의 990 EVO 에서 본 것 (쓰기 결과는 그 앞에 쓴 양에 달렸다) 과 같은 교훈이다.

**SMART** : 177 이 120 → 121, 241 이 +27.9 GB (쓰기 12칸). 오류 0, 온도 최고 47 °C.

### 2단계 : `pattern` (데이터 내용이 쓰기 속도를 바꾸나)

2026.10.18 13:57 – 14:13, 결과 폴더 `20261018-135737-pattern`. 전체 TRIM 뒤, 서로 다른 16 GiB 구간에 1 MiB 순차 쓰기를 16 GiB 씩, 다섯 가지 내용으로 (사이 3분 쉼).

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>내용</th>
<th>MB/s</th>
<th>버퍼 (533 MB/s) 로 쓴 양</th>
<th>버퍼 뒤 속도</th>
<th>평균 지연</th>
<th>99.9% 지연</th>
<th>241 증가</th>
</tr></thead><tbody>
<tr><td><code>zeros</code> (모두 0)</td><td>173.5</td><td>3.18 GB</td><td>151 MB/s</td><td>48.1 ms</td><td>71 ms</td><td>16 GiB</td></tr>
<tr><td><code>random</code> (압축 안 됨)</td><td>171.7</td><td>3.15 GB</td><td>151 MB/s</td><td>48.2 ms</td><td>200 ms</td><td>16 GiB</td></tr>
<tr><td><code>comp50</code> (50% 압축됨)</td><td>171.3</td><td>3.16 GB</td><td>151 MB/s</td><td>48.5 ms</td><td>308 ms</td><td>16 GiB</td></tr>
<tr><td><code>comp90</code> (90% 압축됨)</td><td>171.7</td><td>3.15 GB</td><td>151 MB/s</td><td>48.5 ms</td><td>228 ms</td><td>16 GiB</td></tr>
<tr><td><code>deadbeef</code> (4바이트 무늬 반복)</td><td>172.7</td><td>3.17 GB</td><td>151 MB/s</td><td>48.5 ms</td><td>215 ms</td><td>16 GiB</td></tr>
</tbody></table></div>

**H5 (데이터 내용은 속도를 바꾸지 않는다) : 맞다.** 다섯 가지가 **1.3% 안** (171.3 – 173.5 MB/s) 에 있다. 버퍼 크기 (약 3.2 GB), 버퍼 뒤 속도 (151 MB/s), 평균 지연도 모두 같다. 이 컨트롤러는 압축도, 중복 제거도, 0 을 특별히 다루지도 않는다 (SandForce 계열은 압축되는 데이터를 훨씬 빨리 썼다).

- 숫자가 모델과 딱 맞는다 : 3.2 GB 를 533 MB/s 로, 나머지 13.98 GB 를 150 MB/s 로 쓰면 평균 **173 MB/s** ([실험 3](/old-ssd-experiments/3-slc-cache/) 의 두 속도로 계산).
- SMART 241 (호스트가 쓴 양) 은 다섯 번 모두 정확히 16 GiB 씩 늘었다 : 0 으로만 된 데이터도 드라이브는 그대로 받아 적는다.
- 하나 다른 것 : `zeros` 의 99.9% 지연이 71 ms 로 나머지 (200 – 308 ms) 보다 짧았다. 첫 실행이라 드라이브가 2분 쉰 직후였기 때문일 수 있다 (나머지는 앞 실행에 이어서). 한 번뿐이라 이유를 단정하지 않는다.

**실험 5 정리** : 읽기는 큐 깊이로 병렬성이 드러나고 (4 KiB 랜덤 QD1 7.0k → QD32 90.7k), 큰 블록과 4 KiB 모두 SATA 의 한계 (약 550 MB/s, 약 9.4만 IOPS) 에 닿는다. 쓰기는 데이터 내용과 상관없고, 꽉 찬 드라이브에서는 **덮어쓰는 순서** (랜덤이냐 순차냐) 가 속도를 정한다.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/4-trim/' | relative_url }}">← 4. TRIM 과 매핑 없는 읽기</a><a href="{{ '/old-ssd-experiments/6-write-size/' | relative_url }}">6. 쓰기 크기 · 정렬 →</a></div>
