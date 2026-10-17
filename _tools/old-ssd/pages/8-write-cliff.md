---
layout: default
title: 8. Write cliff
permalink: /old-ssd-experiments/8-write-cliff/
---
@@STYLE@@

# 8. Write cliff : GC 가 눈에 보이는 순간

<div class="glance">
<b>목표</b><span>빈 드라이브에 4 KiB 랜덤 쓰기를 용량의 2배만큼 계속하며, 빈 블록이 바닥나 GC 가 시작될 때 IOPS 가 어떻게 무너지는지 본다</span>
<b>보는 FTL 개념</b><span>빈 블록 풀, GC (victim 선택, 유효 페이지 복사), WAF, steady state</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>4–8시간 (steady state 의 속도에 달렸다) : 밤새 돌린다</span>
<b>명령</b><span><code>sudo ./lab.sh cliff 100</code></span>
</div>

## 배경 : 빈 블록과 GC

NAND 는 **페이지** (몇 KiB–몇십 KiB) 단위로 쓰고, 그보다 훨씬 큰 **블록** (페이지 수백 개) 단위로만 지운다. 이미 쓴 페이지는 덮어쓸 수 없다.
그래서 FTL 은 새 데이터를 늘 빈 페이지에 쓰고, 예전 자리는 '무효' 로 표시한다. 빈 블록은 계속 줄어든다.

@@FIG cliff_fill@@

빈 블록이 바닥에 가까워지면 FTL 은 GC 를 해야 한다 : 무효 페이지가 많은 블록을 골라, 남은 유효 페이지를 다른 곳에 복사하고, 블록을 지운다.
복사하는 양만큼 NAND 는 호스트가 시킨 것보다 더 많이 쓴다. 이 비율이 **WAF** (write amplification factor) 다.

@@FIG cliff_cost@@

랜덤 쓰기는 무효 페이지를 모든 블록에 고르게 흩어 놓는다. 그래서 victim 블록에도 유효 페이지가 많이 남아 있고, GC 비용이 크다.

## 가설과 예상

SNIA 의 SSD 성능 시험 방법 (PTS) 은 이 곡선을 세 구간으로 나눈다 : 막 지운 상태 (FOB, fresh-out-of-box), 전환, steady state.

@@FIG cliff_expect@@

```table
가설 | 맞다면 보일 것
H1 처음엔 빠르다 | 처음 수십 GB 는 높은 IOPS (SLC 버퍼와 빈 블록 덕분)
H2 용량 근처에서 급히 떨어진다 | 쓴 양이 사용자 용량 (120 GB) + 숨은 여유 공간에 가까워질 때 절벽
H3 steady state 는 수천 IOPS 이하 | 쓴 양이 용량의 1.5배를 넘으면 평평해지고, 처음보다 몇 배–몇십 배 낮다
H4 steady state 의 들쭉날쭉함 | 1초 단위로 보면 GC 때문에 위아래로 크게 흔들린다 (평균만 보면 안 보인다)
```

실험 10 페이지의 모델에 따르면 span 100% 의 WAF 는 약 7.8 이다. 즉 steady state 의 NAND 쓰기 속도가 TLC 쓰기 속도에 묶여 있다면, 호스트가 볼 수 있는 속도는 그 1/7.8 정도다.

## 절차

```
$ sudo ./lab.sh cliff 100          # SPAN% = 100 (전체), TIMES = 2 (용량의 2배) 가 기본값
```

```table
단계 | 하는 일
1 | 전체 TRIM (`blkdiscard`), 2분 쉼 : FOB 상태
2 | SMART 기록 (`smart-before`)
3 | fio : `--rw=randwrite --bs=4k --iodepth=32 --norandommap --randrepeat=0`, 대상 = 전체 120 GB, 총 240 GB
4 | 1초마다 IOPS · 대역폭 · 지연 기록
5 | SMART 기록 (`smart-after`) → 실험 12 의 WAF 계산에 쓴다
```

- `--norandommap` : 같은 LBA 를 여러 번 쓸 수 있게 (진짜 랜덤). 없으면 fio 가 모든 LBA 를 한 번씩 쓴 뒤에야 반복한다.
- `--randrepeat=0` : 실행할 때마다 다른 난수.
- 끝나는 시간은 진행 줄의 `eta` 로 본다. steady state 가 아주 느리면 (1천 IOPS 이하) 8시간을 넘을 수 있다.

<div class="tip" markdown="1">
**돌리는 동안** 다른 터미널에서 `iostat -x 1` 로 보면 IOPS 가 출렁이는 것이 실시간으로 보인다. 컴퓨터의 절전 · 화면 잠금은 상관없지만 **절전 모드 (suspend)** 는 꺼 둔다.
</div>

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-cliff-span100 | tail -1)
$ python3 plot.py cliff.png $D/cliff_iops.log=span100
$ python3 smartdiff.py $D
```

1. **세 구간 찾기** : x 축 (쓴 GB) 에서 절벽이 시작하는 곳과 평평해지는 곳. 절벽 위치 − 120 GB ≈ FTL 이 쓸 수 있었던 숨은 빈 공간.
2. **steady state 값** : 마지막 1/4 구간의 평균 IOPS 와 흔들림 (표준편차, 최소값).
3. **WAF** : `smartdiff.py` 가 177 과 241 로 계산한다 (실험 12). 이 실행만으로 177 이 10 이상 늘 것으로 예상한다.
4. **FOB IOPS ÷ steady IOPS** 를 WAF 와 비교 : 대략 비슷하다면 'GC 의 복사가 느려진 이유의 대부분' 이다.

## 시뮬레이터와의 연결 (덤)

시뮬레이터의 **빈 블록 차트** 와 **GC 정책 비교** 의 실제 판이다. 시뮬레이터를 같은 조건 (span 100%, OP 를 이 드라이브의 숨은 여유와 비슷하게, 4 KiB 랜덤) 으로 돌려 곡선 모양과 WAF 를 나란히 놓는다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
