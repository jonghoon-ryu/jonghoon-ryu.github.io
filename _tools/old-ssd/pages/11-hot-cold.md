---
layout: default
title: 11. 뜨거운 데이터
permalink: /old-ssd-experiments/11-hot-cold/
---
@@STYLE@@

# 11. 뜨거운 데이터와 차가운 데이터 : 쓰기가 고르지 않으면 WAF 는

<div class="glance">
<b>목표</b><span>실험 8 의 랜덤 쓰기를 '일부 LBA 에 몰리는' 분포 (zipf, 80/20) 로 바꿔, steady state 의 IOPS 와 WAF 가 고른 랜덤보다 얼마나 좋아지는지 잰다</span>
<b>보는 FTL 개념</b><span>hot / cold 데이터, GC victim 선택 (greedy), hot/cold 분리, 실제 작업 부하가 벤치마크보다 나은 이유</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>분포마다 3–6시간 (실험 8 과 같은 양 : 용량의 2배)</span>
<b>명령</b><span><code>sudo ./lab.sh cliff 100 2 zipf:1.2</code>, <code>sudo ./lab.sh cliff 100 2 zoned:80/20:20/80</code></span>
</div>

## 배경

실험 8 은 모든 LBA 에 똑같이 쓴다 (uniform). 실제 컴퓨터는 그렇지 않다 : 로그 · 브라우저 캐시 · 데이터베이스의 일부는 자주 바뀌고 (뜨거운 데이터), 사진 · 프로그램은 한 번 쓰고 그대로다 (차가운 데이터).

GC 의 비용은 victim 블록에 남은 유효 페이지 수다. 뜨거운 데이터만 든 블록은 금방 거의 다 무효가 되므로 공짜로 지울 수 있다. 차가운 데이터와 섞인 블록은 차가운 데이터를 계속 복사해야 한다. 그래서 :
- 고르지 않은 쓰기는 그 자체로 WAF 를 낮춘다 (greedy GC 가 빈 블록을 쉽게 찾는다)
- FTL 이 뜨거운 것과 차가운 것을 **다른 블록에 나눠 쓰면** 더 낮아진다

## 분포

```table
이름 | fio | 뜻
uniform | (실험 8) | 모든 LBA 가 같은 확률
`zipf:1.2` | `--random_distribution=zipf:1.2` | 순위가 k 인 LBA 의 확률 ∝ 1/k^1.2 : 소수의 LBA 가 대부분의 쓰기를 받는다
`zoned:80/20:20/80` | `--random_distribution=zoned:80/20:20/80` | 쓰기의 80% 가 공간의 20% 에, 나머지 20% 가 80% 에
```

`lab.sh cliff` 의 세 번째 인자가 이 값이다. 결과 폴더 이름에 분포가 붙는다 (`…-cliff-span100-zipf_1.2`).

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 고르지 않으면 steady state 가 빠르다 | zipf · zoned 의 마지막 1/4 평균 IOPS 가 uniform (실험 8) 보다 높다
H2 WAF 가 낮다 | smartdiff 의 WAF : uniform > zoned > zipf (몰림이 클수록 낮다)
H3 절벽이 늦게 온다 | 쓴 GB 기준 절벽 위치가 뒤로 밀린다 (차가운 LBA 는 사실상 OP 처럼 쓰인다)
```

## 절차

```
$ sudo ./lab.sh cliff 100 2 zipf:1.2
$ sudo ./lab.sh cliff 100 2 zoned:80/20:20/80     # 선택
```

나머지는 실험 8 과 똑같다 (전체 TRIM, SMART 앞뒤, 4 KiB QD32, 총 240 GB). 그래서 실험 8 의 곡선과 바로 겹쳐 그릴 수 있다.

## 결과 읽는 법

```
$ R=~/Ryu/old_ssd_results
$ python3 plot.py hotcold.png $R/*-cliff-span100/cliff_iops.log=uniform $R/*-cliff-span100-zipf_1.2/cliff_iops.log=zipf1.2
$ python3 smartdiff.py $(ls -d $R/*-cliff-span100-zipf_1.2 | tail -1)
```

WAF 는 177 의 눈금 (약 137 GB) 때문에 오차가 크다 (실험 12 참고). 몰림이 아주 크면 177 이 몇 칸밖에 늘지 않을 수 있다 : 그것도 '낮은 WAF' 의 증거다.

## 시뮬레이터와의 연결 (덤)

[FTL Visual Simulator](/ftl-visual-simulator/) 의 GC 정책 비교 (greedy, cost-benefit …) 는 이런 몰린 부하에서 차이가 커진다. 같은 zipf 를 시뮬레이터에 넣어 곡선을 나란히 놓을 수 있다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
