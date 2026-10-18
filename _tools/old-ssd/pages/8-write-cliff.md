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
<b>시간</b><span>2–6시간으로 어림했지만 실제로는 81분 (steady state 가 약 24 MB/s 였다)</span>
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

### `sudo ./lab.sh cliff 100` 이 하는 일

이 명령은 **빈 드라이브에 4 KiB 랜덤 쓰기를 쉬지 않고 용량의 2배 (240 GB) 만큼** 해서, 빈 블록이 바닥나 GC 가 시작되는 순간 속도가 어떻게 무너지는지를 1초 단위로 기록한다. [실험 5](/old-ssd-experiments/5-perf-map/) 의 쓰기에서 잠깐 본 '랜덤 덮어쓰기가 이어지면 무너진다' 를, 처음부터 끝까지 한 줄로 본다.

```table
단계 | 하는 일 | 왜
1. 안전 확인 + `0389K` 입력 | 시리얼, 시스템 디스크 아님, 마운트 없음, **TRIM 되는 연결** | TRIM 이 안 되면 1단계의 'FOB' 상태를 만들 수 없다
2. **전체 TRIM** (`blkdiscard`), 2분 쉼 | 모든 매핑을 지운다 | **FOB** (막 산 상태) : 모든 블록이 비어 있는 출발점
3. SMART 기록 (`smart-before`) | 177 · 241 등 | [실험 12](/old-ssd-experiments/12-waf/) 의 WAF 계산의 앞 값
4. **fio 로 랜덤 쓰기** : `--rw=randwrite --bs=4k --iodepth=32`, 범위 = 드라이브 전체 (120 GB), 총량 = 용량의 2배 (`--io_size`, 240 GB) | 같은 LBA 를 여러 번 덮어쓴다 | 처음 한 바퀴로 빈 블록을 다 쓰고, 두 번째 바퀴부터는 쓰기마다 GC 가 필요하다
5. 1초마다 IOPS · 대역폭 · 지연을 로그로 (`cliff_iops.log`, `cliff_bw.log`, `cliff_lat.log`) | 평균이 아닌 1초 단위 | 절벽의 모양과 steady state 의 출렁임
6. SMART 기록 (`smart-after`) | 177 · 241 의 뒤 값 | WAF = (NAND 에 쓴 양) ÷ (호스트가 쓴 양) 의 재료
```

fio 의 랜덤 옵션 :
- `--norandommap` : 같은 LBA 를 여러 번 쓸 수 있게 (진짜 랜덤). 없으면 fio 가 모든 LBA 를 한 번씩 쓴 뒤에야 반복한다
- `--randrepeat=0` : 실행할 때마다 다른 난수
- `--random_generator=tausworthe64` : 120 GB 전체에 고르게 퍼지는 64비트 난수

**예상되는 세 구간** (SNIA PTS 의 이름) :

```table
구간 | 쓴 양 (대략) | 무슨 일이 | 예상 속도
FOB (막 산 상태) | 0 – 약 130 GB | 빈 블록이 남아 있다 : GC 없이 SLC 버퍼와 빈 블록에 쓴다 | 처음 몇 GB 는 SLC 버퍼 속도, 그 뒤 TLC 쓰기 속도 근처 (실험 5 의 랜덤 4 KiB QD32 는 약 223 MB/s)
절벽 (전환) | 약 120 – 160 GB | 사용자 용량 120 GB + 숨은 여유 (OP 약 17 GB) 를 다 쓰는 지점 : GC 시작 | 급히 떨어진다
steady state | 약 160 – 240 GB | 쓰기 하나마다 GC 가 유효 페이지를 옮겨 빈 블록을 만든다 | 모델 (WAF 약 7.8) 이 맞다면 NAND 쓰기 약 150 MB/s ÷ 7.8 ≈ 약 **20 MB/s (약 5천 IOPS)**, 1초마다 크게 출렁인다
```

**시간** : FOB 구간은 20 – 30분, steady state 구간 (약 80 – 120 GB) 은 20 MB/s 면 1 – 2시간, 그보다 느리면 더 걸린다 (5 MB/s 면 5시간 이상). 그래서 **2 – 6시간, 밤새 돌린다.** 진행 줄의 `eta` 는 그때의 속도로 계산하므로, 절벽 뒤에 크게 늘어난다.

<div class="tip" markdown="1">
**돌리는 동안**
- **절전 (suspend) 을 끈다.** 화면 잠금 · 화면 끄기는 괜찮다
- 다른 터미널에서 `iostat -x 1 sda` 로 보면 IOPS 가 출렁이는 것이 실시간으로 보인다 (`w/s`, `wMB/s`, `w_await`)
- 온도 (SMART 190) 가 오를 수 있다. 70 °C 를 넘으면 드라이브가 스스로 느려질 수 있다
- **끝나면 바로** [실험 9](/old-ssd-experiments/9-idle-gc/) (`sudo ./lab.sh idlegc 0 1 5 15 30`) 를 한다 : steady state 그대로의 드라이브가 필요하다
</div>

**저장되는 것** (`~/Ryu/old_ssd_results/<날짜>-cliff-span100/`) : `cliff_iops.log` · `cliff_bw.log` · `cliff_lat.log` (1초마다), `cliff.json` (fio 요약), `smart-before` · `smart-after` (텍스트 + JSON), `meta.txt` (범위 · 총량).

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
2026.10.18 15:36 – 16:57 (**81분**), 결과 폴더 `20261018-153629-cliff-span100`. 전체 TRIM → 4 KiB 랜덤 쓰기 QD32 를 120 GB 범위에 240 GB.

![write cliff : 쓴 양에 따른 IOPS](/old-ssd-experiments/8-write-cliff/cliff.png)

**교과서 같은 세 구간**

```table
쓴 양 | IOPS (평균, 범위) | MB/s | 무슨 일이
0 – 약 3 GB | **약 8만** (최고 80.6k) | 약 330 | SLC 버퍼 (TurboWrite) 에 쓴다
약 3 – 125 GB | **약 3.6만** (2.7 – 3.8만, 평평) | 약 148 | 빈 블록에 TLC 로 바로 쓴다 : GC 없음 (FOB)
약 125 – 130 GB | 3.6만 → 0.8만 | | **절벽** : 빈 블록이 바닥난다
130 – 160 GB | 약 0.8만 (0.54 – 1.27만) | 약 32 | GC 가 시작된다 : 쓰기마다 유효 페이지를 옮긴다
160 – 200 GB | 약 0.7만 | 약 28 | 조금씩 더 내려간다
200 – 240 GB (마지막 4분의 1) | **약 0.6만** (0.47 – 0.96만, 표준편차 655) | 약 **24** | steady state
```

전체 : 240 GB 를 81분에, 평균 12.1k IOPS · 49.4 MB/s. 쓰기 하나의 지연 평균 2.7 ms, 99% 26 ms, 99.9% 37 ms, 가장 길게 281 ms. 오류 0. 온도 32 → 44 °C.

**가설 확인**

```table
가설 | 결과
H1 처음엔 빠르다 | **맞다** : 처음 약 3 GB 는 8만 IOPS (SLC 버퍼), 그 뒤 125 GB 까지 3.6만 IOPS 로 평평
H2 용량 근처에서 급히 떨어진다 | **맞다** : 125 – 130 GB 에서 몇 분 만에 3.6만 → 0.8만. 사용자 용량 120 GB 를 넘긴 바로 뒤
H3 steady state 는 수천 IOPS 이하 | **맞다** : 마지막 4분의 1 평균 **약 6천 IOPS**, 처음 평평한 구간의 **6분의 1**
H4 steady state 는 크게 흔들린다 | **맞다** : 1초 값이 4.7 – 9.6천 사이를 오간다 (평균의 ±10% 가 보통, 때로 +60%)
```

**절벽의 자리로 숨은 여유를 어림하기.** 절벽은 약 125 – 130 GB 에서 왔다. 사용자 용량 120 GB 를 다 쓰고도 **약 5 – 10 GB** 를 GC 없이 더 썼다는 뜻이다. [실험 10](/old-ssd-experiments/10-over-provisioning/) 의 모델은 NAND 137.4 GB − 사용자 120 GB = OP 17.4 GB 에서 SLC 버퍼 (TLC 로 약 9 GB) 를 빼고 'GC 가 쓰는 여유 약 8 GB' 를 가정했다 : **측정과 맞는다.**

**steady state 와 모델.** 모델의 예측은 약 20 MB/s (약 5천 IOPS) 였고, 측정은 약 24 MB/s (약 6천 IOPS) 이며 아직 조금씩 내려가고 있었다. 평평한 구간 (약 148 MB/s) 과 steady state 의 비 **약 6** 은, NAND 쓰기 속도가 그대로라면 'NAND 에 쓰는 양이 호스트가 쓰는 양의 약 6배' (WAF 약 6) 라는 뜻이다.

**그런데 SMART 177 은 다른 말을 한다.** 177 은 123 → **126 (+3)**, 241 은 +240.1 GB : `smartdiff.py` 의 WAF 는 약 **1.7** (177 이 정수로만 늘어서 1.15 – 2.29). 첫 120 GB 를 WAF 1 로 보면 나머지 120 GB 의 WAF 는 약 2.4 다. 속도로 어림한 '약 6' 과 크게 다르다. 가능한 이유 :
- 177 이 늦게 반영된다 (평균 지움 횟수를 나중에 계산), 또는 SLC 영역의 지움을 세지 않는다
- steady state 의 느림이 GC 의 복사만이 아니라 다른 일 (SLC → TLC 옮기기, 매핑 표 저장) 에서도 온다
- steady state 에 아직 다 이르지 않았다 (마지막까지 내려가고 있었다)
[실험 12](/old-ssd-experiments/12-waf/) 가 순차 쓰기 5번으로 177 의 눈금을 따로 재고, 이 실행의 WAF 를 다시 본다. 실험 9 직후의 SMART 도 177 이 늦게 오르는지 알려 줄 것이다.

**실험 5 와 이어서** : [실험 5](/old-ssd-experiments/5-perf-map/) 의 쓰기 지도에서 '꽉 찬 드라이브의 랜덤 덮어쓰기는 무너진다' 를 몇 분 동안 보았다. 이 실험은 그 무너짐이 **어디서 시작해서 어디까지 내려가는지** 를 보여 준다.
</div>

@@NAV@@
