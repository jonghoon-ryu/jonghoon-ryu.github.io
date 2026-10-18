---
layout: default
title: 7. 쓰기 캐시 · FLUSH
permalink: /old-ssd-experiments/7-flush/
---
@@STYLE@@

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

```table
설정 | '끝났다' 가 오는 때 | fio 로
쓰기 캐시 켬 (기본) | DRAM 에 들어갔을 때 | `--rw=randwrite` (그냥)
켬 + 쓰기마다 FLUSH | DRAM → NAND (SLC 버퍼) 에 쓴 뒤 | `--fsync=1` (블록 장치에서 fsync = FLUSH)
쓰기 캐시 끔 | 쓰기 하나하나가 NAND 에 닿은 뒤 | `hdparm -W0` 뒤 `--rw=randwrite`
```

840 EVO 는 소비자용이라 전원이 끊길 때 캐시를 비울 축전기 (power-loss protection) 가 없는 것으로 알려져 있다. 그래서 FLUSH 를 지키는지가 중요하다 : 실험 17 에서 직접 전원을 끊어 확인한다.

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 캐시를 켜면 4 KiB QD1 쓰기는 아주 빠르다 | `wc1-4k` 의 평균 지연 수십 µs (DRAM 까지)
H2 FLUSH 를 하면 NAND 프로그램 시간이 보인다 | `wc1-4k-fsync` 의 지연 = 쓰기 + FLUSH : 수백 µs – ms (SLC 프로그램 시간 근처)
H3 캐시를 끄면 FLUSH 를 매번 한 것과 비슷하다 | `wc0-4k` ≈ `wc1-4k-fsync`. 크게 다르면 캐시를 끄는 방식이 FLUSH 와 다르게 구현되어 있다
H4 캐시를 꺼도 큐 깊이로 일부 되찾는다 | `wc0-4k-qd32` 의 IOPS 가 `wc0-4k` 의 몇 배 (여러 die 에 동시에 쓰기)
H5 FLUSH 를 무시하는 드라이브라면 | `wc1-4k-fsync` 가 `wc1-4k` 와 같다 : 위험 신호 (실험 17 로 확인)
```

## 절차

```
$ sudo ./lab.sh flush
```

```table
실행 | 캐시 | 하는 일
`wc1-4k` | 켬 | 4 KiB 랜덤 쓰기 QD1, 30초
`wc1-4k-fsync` | 켬 | 같은 것 + 쓰기마다 fsync
`wc1-1m-fsync` | 켬 | 1 MiB 순차 쓰기 + 쓰기마다 fsync (큰 쓰기에서 FLUSH 비용의 비율)
`wc0-4k` | 끔 | 4 KiB 랜덤 쓰기 QD1
`wc0-4k-qd32` | 끔 | 4 KiB 랜덤 쓰기 QD32
`wc0-1m` | 끔 | 1 MiB 순차 쓰기 QD1
```

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

```table
실행 | 캐시 | IOPS | MB/s | 쓰기 하나 (평균) | FLUSH 하나 (평균 · 99%) | 쓰기 하나에 드는 전체 시간
`wc1-4k` (4 KiB 랜덤, QD1) | 켬 | **27,255** | 111.6 | **32 µs** | — | 32 µs
`wc1-4k-fsync` (+ 쓰기마다 fsync) | 켬 | **604** | 2.5 | 50 µs | **1,643 µs** · 8.1 ms | 약 1.7 ms
`wc0-4k` | **끔** | **618** | 2.5 | **1,609 µs** | — | 1.6 ms
`wc0-4k-qd32` | 끔 | 5,758 | 23.6 | 5.6 ms | — | (32개가 동시에)
`wc1-1m-fsync` (1 MiB 순차 + fsync) | 켬 | 100 | 105.0 | 2.2 ms | 9.8 ms | 약 10 ms
`wc0-1m` (1 MiB 순차) | 끔 | 102 | 106.5 | 9.7 ms | — | 9.7 ms
```

FLUSH 의 시간은 fio JSON 의 `sync` 부분에 따로 있다 (`fiosum.py` 의 표에는 나오지 않는다).

**H1 (캐시를 켜면 4 KiB QD1 쓰기는 아주 빠르다) : 맞다.** 32 µs : DRAM 에 담기면 '끝' 이다. NAND 에 쓰는 시간이 아니다.

**H2 (FLUSH 를 하면 NAND 에 쓰는 시간이 보인다) : 맞다, 생각보다 크다.** FLUSH 하나가 평균 **1.6 ms** (99% 8.1 ms). 쓰기 자체 (50 µs) 의 30배다. 4 KiB 하나를 NAND 에 확실히 적는 데 드는 시간에, 매핑 표 같은 내부 기록을 함께 저장하는 시간이 더해진 것으로 보인다. 결과 : 쓰기마다 fsync 하면 **27,255 → 604 IOPS, 45배 느려진다.**

**H3 (캐시를 끄면 FLUSH 를 매번 한 것과 비슷하다) : 맞다, 거의 같다.** 캐시 끔 618 IOPS · 1.6 ms, 캐시 켬 + fsync 604 IOPS · 1.7 ms. 캐시를 끄는 것은 '쓰기마다 FLUSH' 와 같은 비용이다.

**H4 (캐시를 꺼도 큐 깊이로 일부 되찾는다) : 맞다.** 캐시 끔 QD32 는 5,758 IOPS 로 QD1 의 **9.3배** : 32개를 함께 걸어 두면 드라이브가 NAND 칩 여럿에 나눠 쓴다. 그래도 캐시 켬 QD1 (27k) 의 5분의 1이다.

**H5 (FLUSH 를 무시하는 드라이브라면) : 이 드라이브는 무시하지 않는다.** fsync 를 하면 정말로 45배 느려진다. 약속을 지키는 모습이다. 전원이 끊겼을 때 정말 남는지는 [실험 17](/old-ssd-experiments/17-power-loss/) 이 확인한다.

**큰 쓰기에서는 FLUSH 비용의 비율이 작다** : 1 MiB 를 쓰고 fsync 하면 한 번에 약 10 ms (쓰기 2.2 ms + FLUSH 9.8 ms) 로 105 MB/s. 캐시를 끈 1 MiB 쓰기 (106.5 MB/s) 와 같고, TLC 직접 쓰기 속도 ([실험 3](/old-ssd-experiments/3-slc-cache/), 약 150 MB/s) 의 70% 다. 4 KiB 에서는 FLUSH 가 시간의 97% 였는데, 1 MiB 에서는 데이터를 실제로 옮기는 시간이 대부분이다. **'작은 쓰기를 모아서 한 번에 커밋하라'** 는 데이터베이스의 규칙 (group commit) 이 여기서 나온다. [Ref: fio test](/old-ssd-experiments/fio/ref-fio-test/) 의 990 EVO 에서도 `fsync=1` 이 115배, `fsync=32` 가 그보다 4배 나았다.
</div>

@@NAV@@
