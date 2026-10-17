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
아직 실행 전.
</div>

@@NAV@@
