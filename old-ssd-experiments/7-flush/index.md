---
layout: default
title: 7. 쓰기 캐시 · FLUSH
permalink: /old-ssd-experiments/7-flush/
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

# 7. 쓰기 캐시와 FLUSH : '다 썼다' 는 대답은 언제 오나

<div class="glance">
<b>목표</b><span>드라이브의 쓰기 캐시를 켜고 끄며, 그리고 쓰기마다 FLUSH 를 보내며 4 KiB 쓰기의 지연을 잰다. '쓰기 완료' 가 DRAM · SLC · TLC 중 어디에 닿았을 때 오는지 밖에서 짐작한다</span>
<b>보는 FTL 개념</b><span>휘발성 쓰기 캐시, FLUSH CACHE 명령, FUA, fsync 의 비용, 전원 차단과 데이터 안전 (실험 17 의 준비)</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>약 15분</span>
<b>명령</b><span><code>sudo ./lab.sh flush</code></span>
</div>

## 배경

드라이브는 쓰기를 받으면 보통 **DRAM 의 쓰기 캐시** 에 넣고 곧바로 '끝났다' 고 대답한다. NAND 에 실제로 쓰는 것은 나중이다. 빠르지만, 그 사이에 전원이 끊기면 '끝났다' 고 한 데이터가 사라진다.
그래서 운영체제는 데이터가 꼭 남아야 할 때 (`fsync`, 데이터베이스의 커밋) 드라이브에 **FLUSH CACHE** 를 보낸다 : '캐시에 있는 것을 다 NAND 에 쓰고 나서 대답하라'.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>설정</th>
<th>'끝났다' 가 오는 때</th>
<th>fio 로</th>
</tr></thead><tbody>
<tr><td>쓰기 캐시 켬 (기본)</td><td>DRAM 에 들어갔을 때</td><td><code>--rw=randwrite</code> (그냥)</td></tr>
<tr><td>켬 + 쓰기마다 FLUSH</td><td>DRAM → NAND (SLC 버퍼) 에 쓴 뒤</td><td><code>--fsync=1</code> (블록 장치에서 fsync = FLUSH)</td></tr>
<tr><td>쓰기 캐시 끔</td><td>쓰기 하나하나가 NAND 에 닿은 뒤</td><td><code>hdparm -W0</code> 뒤 <code>--rw=randwrite</code></td></tr>
</tbody></table></div>

840 EVO 는 소비자용이라 전원이 끊길 때 캐시를 비울 축전기 (power-loss protection) 가 없는 것으로 알려져 있다. 그래서 FLUSH 를 지키는지가 중요하다 : 실험 17 에서 직접 전원을 끊어 확인한다.

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 캐시를 켜면 4 KiB QD1 쓰기는 아주 빠르다</td><td><code>wc1-4k</code> 의 평균 지연 수십 µs (DRAM 까지)</td></tr>
<tr><td>H2 FLUSH 를 하면 NAND 프로그램 시간이 보인다</td><td><code>wc1-4k-fsync</code> 의 지연 = 쓰기 + FLUSH : 수백 µs – ms (SLC 프로그램 시간 근처)</td></tr>
<tr><td>H3 캐시를 끄면 FLUSH 를 매번 한 것과 비슷하다</td><td><code>wc0-4k</code> ≈ <code>wc1-4k-fsync</code>. 크게 다르면 캐시를 끄는 방식이 FLUSH 와 다르게 구현되어 있다</td></tr>
<tr><td>H4 캐시를 꺼도 큐 깊이로 일부 되찾는다</td><td><code>wc0-4k-qd32</code> 의 IOPS 가 <code>wc0-4k</code> 의 몇 배 (여러 die 에 동시에 쓰기)</td></tr>
<tr><td>H5 FLUSH 를 무시하는 드라이브라면</td><td><code>wc1-4k-fsync</code> 가 <code>wc1-4k</code> 와 같다 : 위험 신호 (실험 17 로 확인)</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh flush
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실행</th>
<th>캐시</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td><code>wc1-4k</code></td><td>켬</td><td>4 KiB 랜덤 쓰기 QD1, 30초</td></tr>
<tr><td><code>wc1-4k-fsync</code></td><td>켬</td><td>같은 것 + 쓰기마다 fsync</td></tr>
<tr><td><code>wc1-1m-fsync</code></td><td>켬</td><td>1 MiB 순차 쓰기 + 쓰기마다 fsync (큰 쓰기에서 FLUSH 비용의 비율)</td></tr>
<tr><td><code>wc0-4k</code></td><td>끔</td><td>4 KiB 랜덤 쓰기 QD1</td></tr>
<tr><td><code>wc0-4k-qd32</code></td><td>끔</td><td>4 KiB 랜덤 쓰기 QD32</td></tr>
<tr><td><code>wc0-1m</code></td><td>끔</td><td>1 MiB 순차 쓰기 QD1</td></tr>
</tbody></table></div>

실행 사이에 60초 쉰다. 끝나면 (또는 Ctrl+C 로 멈춰도) 쓰기 캐시를 다시 켠다 (`hdparm -W1`, 스크립트의 `trap`). 혹시 꺼진 채로 남았다면 `sudo hdparm -W1 /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K` 로 켠다. 이 설정은 전원을 껐다 켜면 원래대로 돌아오기도 한다.

## 결과 읽는 법

```
$ column -s, -t $(ls -d ~/Ryu/old_ssd_results/*-flush | tail -1)/summary.csv
```

1. 네 줄 (`wc1-4k`, `wc1-4k-fsync`, `wc0-4k`, `wc0-4k-qd32`) 의 평균 · 99% 지연을 한 표로.
2. `wc1-4k-fsync` 의 지연 − `wc1-4k` 의 지연 ≈ FLUSH 하나의 비용.
3. `wc1-1m-fsync` : 1 MiB 를 쓰는 시간에 비해 FLUSH 비용이 얼마나 작은가 → '큰 단위로 모아서 커밋하라' 는 데이터베이스의 규칙이 왜 생겼는지.

## 결과

<div class="result" markdown="1">
2026.10.18 15:19 – 15:34, 결과 폴더 `20261018-151945-flush`. 시작할 때 쓰기 캐시는 켜져 있었고 (`write-caching = 1`), 끝에 다시 켰다.

![4 KiB 랜덤 쓰기 하나에 드는 시간](/old-ssd-experiments/7-flush/flush.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실행</th>
<th>캐시</th>
<th>IOPS</th>
<th>MB/s</th>
<th>쓰기 하나 (평균)</th>
<th>FLUSH 하나 (평균 · 99%)</th>
<th>쓰기 하나에 드는 전체 시간</th>
</tr></thead><tbody>
<tr><td><code>wc1-4k</code> (4 KiB 랜덤, QD1)</td><td>켬</td><td><strong>27,255</strong></td><td>111.6</td><td><strong>32 µs</strong></td><td>—</td><td>32 µs</td></tr>
<tr><td><code>wc1-4k-fsync</code> (+ 쓰기마다 fsync)</td><td>켬</td><td><strong>604</strong></td><td>2.5</td><td>50 µs</td><td><strong>1,643 µs</strong> · 8.1 ms</td><td>약 1.7 ms</td></tr>
<tr><td><code>wc0-4k</code></td><td><strong>끔</strong></td><td><strong>618</strong></td><td>2.5</td><td><strong>1,609 µs</strong></td><td>—</td><td>1.6 ms</td></tr>
<tr><td><code>wc0-4k-qd32</code></td><td>끔</td><td>5,758</td><td>23.6</td><td>5.6 ms</td><td>—</td><td>(32개가 동시에)</td></tr>
<tr><td><code>wc1-1m-fsync</code> (1 MiB 순차 + fsync)</td><td>켬</td><td>100</td><td>105.0</td><td>2.2 ms</td><td>9.8 ms</td><td>약 10 ms</td></tr>
<tr><td><code>wc0-1m</code> (1 MiB 순차)</td><td>끔</td><td>102</td><td>106.5</td><td>9.7 ms</td><td>—</td><td>9.7 ms</td></tr>
</tbody></table></div>

FLUSH 의 시간은 fio JSON 의 `sync` 부분에 따로 있다 (`fiosum.py` 의 표에는 나오지 않는다).

**H1 (캐시를 켜면 4 KiB QD1 쓰기는 아주 빠르다) : 맞다.** 32 µs : DRAM 에 담기면 '끝' 이다. NAND 에 쓰는 시간이 아니다.

**H2 (FLUSH 를 하면 NAND 에 쓰는 시간이 보인다) : 맞다, 생각보다 크다.** FLUSH 하나가 평균 **1.6 ms** (99% 8.1 ms). 쓰기 자체 (50 µs) 의 30배다. 4 KiB 하나를 NAND 에 확실히 적는 데 드는 시간에, 매핑 표 같은 내부 기록을 함께 저장하는 시간이 더해진 것으로 보인다. 결과 : 쓰기마다 fsync 하면 **27,255 → 604 IOPS, 45배 느려진다.**

**H3 (캐시를 끄면 FLUSH 를 매번 한 것과 비슷하다) : 맞다, 거의 같다.** 캐시 끔 618 IOPS · 1.6 ms, 캐시 켬 + fsync 604 IOPS · 1.7 ms. 캐시를 끄는 것은 '쓰기마다 FLUSH' 와 같은 비용이다.

**H4 (캐시를 꺼도 큐 깊이로 일부 되찾는다) : 맞다.** 캐시 끔 QD32 는 5,758 IOPS 로 QD1 의 **9.3배** : 32개를 함께 걸어 두면 드라이브가 NAND 칩 여럿에 나눠 쓴다. 그래도 캐시 켬 QD1 (27k) 의 5분의 1이다.

**H5 (FLUSH 를 무시하는 드라이브라면) : 이 드라이브는 무시하지 않는다.** fsync 를 하면 정말로 45배 느려진다. 약속을 지키는 모습이다. 전원이 끊겼을 때 정말 남는지는 [실험 17](/old-ssd-experiments/17-power-loss/) 이 확인한다.

**큰 쓰기에서는 FLUSH 비용의 비율이 작다** : 1 MiB 를 쓰고 fsync 하면 한 번에 약 10 ms (쓰기 2.2 ms + FLUSH 9.8 ms) 로 105 MB/s. 캐시를 끈 1 MiB 쓰기 (106.5 MB/s) 와 같고, TLC 직접 쓰기 속도 ([실험 3](/old-ssd-experiments/3-slc-cache/), 약 150 MB/s) 의 70% 다. 4 KiB 에서는 FLUSH 가 시간의 97% 였는데, 1 MiB 에서는 데이터를 실제로 옮기는 시간이 대부분이다. **'작은 쓰기를 모아서 한 번에 커밋하라'** 는 데이터베이스의 규칙 (group commit) 이 여기서 나온다. [Ref: fio test](/old-ssd-experiments/fio/ref-fio-test/) 의 990 EVO 에서도 `fsync=1` 이 115배, `fsync=32` 가 그보다 4배 나았다.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/6-write-size/' | relative_url }}">← 6. 쓰기 크기 · 정렬</a><a href="{{ '/old-ssd-experiments/8-write-cliff/' | relative_url }}">8. Write cliff →</a></div>
