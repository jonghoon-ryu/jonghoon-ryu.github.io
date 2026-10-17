---
layout: default
title: 3. SLC 캐시
permalink: /old-ssd-experiments/3-slc-cache/
---
@@STYLE@@

# 3. SLC 캐시 : 빠른 쓰기는 몇 GB 까지인가

<div class="glance">
<b>목표</b><span>TurboWrite 버퍼의 크기, 버퍼를 넘긴 뒤 TLC 에 바로 쓰는 속도, 버퍼가 다시 비는 데 걸리는 시간을 잰다</span>
<b>보는 FTL 개념</b><span>SLC 캐시 (pseudo-SLC), 쉬는 동안의 데이터 옮기기 (folding / migration)</span>
<b>지우나?</b><span>예. 드라이브 전체를 TRIM 하고 처음부터 끝까지 쓴다</span>
<b>연결</b><span>SATA (TRIM 이 필요하고, USB 는 속도 상한이 낮다)</span>
<b>시간</b><span>전체 쓰기 15–20분 + 회복 측정 30분</span>
<b>명령</b><span><code>sudo ./lab.sh slc</code>, <code>sudo ./lab.sh slc-idle 0 1 5 15</code>, <code>sudo ./lab.sh scan fresh 8</code></span>
</div>

## 왜 SLC 캐시를 쓰나

TLC 는 셀 하나에 3비트를 담느라 전압을 8단계로 정밀하게 맞춰야 해서, 쓰기가 느리다. 같은 셀에 1비트만 담으면 (SLC 처럼 쓰면) 훨씬 빠르게 쓸 수 있다.
840 EVO 는 TLC 의 일부를 이렇게 SLC 처럼 써서 **들어오는 쓰기를 빠르게 받아 두고**, 쉬는 동안 TLC 로 옮긴다. Samsung 은 이것을 TurboWrite 라고 불렀다.

@@FIG slc_concept@@

이 구조 때문에 '쓰기 속도' 는 하나의 숫자가 아니다. 버퍼에 들어가는 동안의 속도와, 버퍼가 다 찬 뒤 TLC 에 바로 쓰는 속도가 따로 있다.

## 가설과 예상

@@FIG slc_expect@@

```table
가설 | 맞다면 보일 것
H1 버퍼는 약 3 GB 다 | 순차 쓰기 속도가 3 GB 근처에서 계단처럼 떨어진다
H2 버퍼 밖 TLC 쓰기는 약 100–150 MB/s 다 | 떨어진 뒤 끝까지 그 높이가 유지된다
H3 쉬면 버퍼가 다시 빈다 | slc-idle 에서 쉰 시간이 길수록 빠르게 쓴 양이 3 GB 에 가까워진다
```

숫자는 기억하는 리뷰 · 사양 값이라 틀릴 수 있다. 어긋나면 그것이 이 드라이브의 진짜 값이다.

@@FIG slc_idle@@

## 절차

```
# 3. SATA 에 연결된 상태 (0. 준비 6단계). check 를 다시 해서 DISC-MAX 가 0B 가 아닌지
$ sudo ./lab.sh check

# 3. 전체 TRIM → 2분 쉼 → 1 MiB 순차 쓰기 QD8 로 처음부터 끝까지, 1초마다 속도 기록
$ sudo ./lab.sh slc

# 3. 버퍼 회복 : 8 GiB 로 버퍼를 채운 뒤, 0 / 1 / 5 / 15 분 쉬고 다시 8 GiB 씩
$ sudo ./lab.sh slc-idle 0 1 5 15

# 3. 실험 1 의 비교 기준 : 방금 쓴 '새 데이터' 의 위치별 읽기 속도
$ sudo ./lab.sh scan fresh 8

# 4. 실험 2 의 비교 기준 : 새 데이터로 가득한 드라이브의 자가 진단 시간
$ sudo ./lab.sh selftest long
```

`slc` 와 `slc-idle` 은 지우기 전에 시리얼 끝 5자리 (`0389K`) 를 묻는다.

## 저장되는 것

```table
파일 | 내용
`…-slc/slc_bw.log` | 1초마다 쓰기 대역폭 (KiB/s)
`…-slc/slc_iops.log`, `slc_lat.log` | 1초마다 IOPS, 평균 지연
`…-slc/slc.json` | fio 요약 (전체 평균, 지연 분포)
`…-slc-idle/fill_bw.log`, `idle0_bw.log`, `idle1_bw.log` … | 회복 측정
`…-scan-fresh/scan.csv` | 새 데이터의 위치별 읽기 속도
```

## 결과 읽는 법

```
$ python3 plot.py slc.png ~/Ryu/old_ssd_results/*-slc/slc_bw.log=slc
$ python3 plot.py idle.png ~/Ryu/old_ssd_results/*-slc-idle/idle{0,1,5,15}_bw.log
$ python3 plot.py age-vs-fresh.png ~/Ryu/old_ssd_results/*-scan-old/scan.csv=old ~/Ryu/old_ssd_results/*-scan-fresh/scan.csv=fresh
```

1. **꺾이는 위치** (x 축 GB) = 버퍼 크기. 꺾이는 곳이 하나 이상이면 (예 : 버퍼 → TLC → 더 느린 구간) 그 수와 위치를 적는다.
2. **낮은 쪽의 높이** = TLC 직접 쓰기 속도. 들쭉날쭉하면 버퍼를 비우는 일과 새 쓰기가 섞이는 것이다.
3. **회복** : 그래프마다 처음 몇 GB 가 빠른지 읽어 쉰 시간별 막대로 만든다 (Claude 가 계산한다).
4. **old vs fresh** : 같은 위치, 같은 연결 (가능하면) 에서 '나이' 만 다른 두 곡선.

## 시뮬레이터와의 연결 (덤)

시뮬레이터의 DRAM 캐시 토글은 쓰기를 RAM 에 받아 두는 것이고, SLC 캐시는 NAND 안의 빠른 영역이다. 둘 다 '처음엔 빠르다가 넘치면 원래 속도' 라는 같은 모양을 만든다. 이 결과의 버퍼 크기와 두 속도로 시뮬레이터에 SLC 영역 모델을 만들 수 있다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
