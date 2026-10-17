---
layout: default
title: 13. 읽기 · 쓰기 간섭
permalink: /old-ssd-experiments/13-interference/
---
@@STYLE@@

# 13. 읽기와 쓰기의 간섭 : 쓰기가 돌면 읽기는 얼마나 기다리나

<div class="glance">
<b>목표</b><span>4 KiB 읽기 (QD1) 의 지연을 혼자일 때, 순차 쓰기와 함께일 때, 랜덤 쓰기 (GC 가 도는) 와 함께일 때 재서, 꼬리 지연이 얼마나 길어지는지 본다</span>
<b>보는 FTL 개념</b><span>NAND 의 프로그램 · 지우기 시간, die 를 차지하는 동안의 읽기 대기, GC 와 꼬리 지연, (더 좋은 드라이브의) program/erase suspend</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>약 40분 (채우기 15분 + 사전 쓰기 10분 + 측정 3 × 2분)</span>
<b>명령</b><span><code>sudo ./lab.sh mixed</code></span>
</div>

## 배경

NAND die 하나는 한 번에 한 가지 일만 한다. TLC 의 프로그램 (쓰기) 은 ms 단위, 블록 지우기는 그보다 길다. 그동안 **같은 die 에 있는 데이터를 읽으려는 요청은 기다린다.**
그래서 읽기만 할 때는 100 µs 근처이던 지연이, 쓰기가 섞이면 가끔 수 ms – 수십 ms 가 된다. 평균은 조금만 늘어도 99.9% 는 크게 는다. 데이터베이스 · 웹 서버가 SSD 의 '꼬리 지연' 을 따지는 이유다.

[fio 페이지 8절](/old-ssd-experiments/fio/) 에서 이 컴퓨터의 NVMe 로 같은 시험을 미리 해 봤다 : 혼자일 때 99.9% = 186 µs, 순차 쓰기와 함께일 때 11,207 µs (60배).

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 순차 쓰기가 읽기의 꼬리를 늘린다 | `seqwrite` 의 읽기 99.9% 가 `alone` 의 10배 이상
H2 GC 가 도는 랜덤 쓰기는 더 나쁘다 | `randwrite` 의 읽기 99.9% · max 가 `seqwrite` 보다도 길다 (GC 의 복사 · 지우기가 더해진다)
H3 50% 지연은 덜 늘어난다 | 중앙값은 2–3배 안 : 대부분의 읽기는 바쁜 die 에 걸리지 않는다
H4 1초마다의 최대 지연이 출렁인다 | `*-rd_lat.log` (1초마다 가장 느린 읽기) 그래프에 GC 의 리듬이 보인다
```

## 절차

```
$ sudo ./lab.sh mixed
```

```table
단계 | 하는 일
1 | 전체 TRIM, 1 MiB 순차로 전체를 채움 (읽기가 진짜 NAND 를 읽게)
2 | 4 KiB 랜덤 쓰기 QD32 를 10분 (GC 가 일하는 상태로)
3 | `alone` : 4 KiB 랜덤 읽기 QD1, 60초
4 | `seqwrite` : 같은 읽기 + 다른 job 이 뒤쪽 절반에 1 MiB 순차 쓰기 QD8
5 | `randwrite` : 같은 읽기 + 다른 job 이 4 KiB 랜덤 쓰기 QD32 (전체 범위)
```

각 측정 사이에 60초 쉰다. 읽기 job 은 1초마다 **가장 느렸던 읽기** 를 기록한다 (`--log_max_value=1`).

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-mixed | tail -1)
$ column -s, -t $D/summary.csv
$ python3 plot.py mixed.png $D/alone-rd_lat.log=alone $D/seqwrite-rd_lat.log=seqwrite $D/randwrite-rd_lat.log=randwrite
```

1. `summary.csv` 의 `rd` 줄 세 개 : IOPS, 50%, 99%, 99.9%, max.
2. 그림 : 1초마다의 최대 지연. 쓰기의 IOPS (`wr` 줄) 와 함께 보면 '쓰기 속도를 얻은 대신 읽기 지연을 얼마나 냈나' 가 보인다.
3. 비교 : 실험 5 의 `randread-4k-qd1` 칸 (쓰기 없음, 깨끗한 상태) 과 `alone` 이 같은지. 다르면 GC 가 쉬는 동안에도 남아 있던 일이 읽기를 방해한 것이다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
