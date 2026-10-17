---
layout: default
title: 10. Over-provisioning
permalink: /old-ssd-experiments/10-over-provisioning/
---
@@STYLE@@

# 10. Over-provisioning : 덜 쓰면 얼마나 빨라지나

<div class="glance">
<b>목표</b><span>실험 8 을 드라이브의 앞쪽 80% 에만 해서, 남긴 20% 가 여유 공간으로 쓰일 때 steady state 가 몇 배 빨라지는지 재고, 모델의 예측과 비교한다</span>
<b>보는 FTL 개념</b><span>over-provisioning (OP), 여유 비율과 WAF 의 관계, TRIM 된 공간을 FTL 이 여유로 쓰기</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>span 마다 3–6시간 : 80% 는 필수, 90% · 70% 는 선택</span>
<b>명령</b><span><code>sudo ./lab.sh cliff 80</code> (선택 : <code>cliff 90</code>, <code>cliff 70</code>)</span>
</div>

## 배경 : 여유 공간이 왜 중요한가

GC 의 비용은 victim 블록에 남은 유효 페이지 수로 정해진다 (실험 8). 랜덤 쓰기에서 victim 이 얼마나 비어 있는지는 **데이터에 비해 NAND 가 얼마나 넉넉한가** 로 정해진다.

이 여유를 OP 라고 한다. 드라이브는 처음부터 숨은 여유를 가지고 있고 (사용자에게 보이지 않는 NAND), 사용자가 일부 LBA 를 **TRIM 된 채로 두고 쓰지 않으면** 그만큼도 FTL 의 여유가 된다. 파티션을 일부러 작게 만드는 것과 같은 효과다.

@@FIG op_span@@

## 모델 : 여유 비율 ρ 와 WAF

균일한 랜덤 쓰기에서, 유효 페이지가 가장 적은 블록 (또는 가장 오래된 블록) 을 고르는 GC 의 WAF 는 여유 비율 ρ 만으로 거의 정해진다는 분석이 있다 (Desnoyers, *Analytic Modeling of SSD Write Performance*, SYSTOR 2012).
α = 1 + ρ 라고 하면 WAF = α / (α + W(−α·e^(−α))). 여기서 W 는 Lambert W 함수다. 아래 곡선이 그 식이다.

@@FIG op_curve@@

이 그림의 점들은 **가정** 위에 있다 : NAND 128 GiB (137.4 GB), SLC 버퍼 3 GB 가 TLC 9 GB 를 차지, 나머지가 모두 GC 의 여유. 펌웨어가 불량 블록 예비분이나 메타데이터로 일부를 더 쓰면 실제 여유는 더 작다.
**이 실험의 재미는 거꾸로 하는 데 있다** : 잰 WAF (실험 12) 를 곡선에 대어 이 드라이브의 실제 여유 공간을 추정한다.

## 가설과 예상

@@FIG op_expect@@

```table
가설 | 맞다면 보일 것
H1 OP 를 늘리면 steady state 가 빨라진다 | span 80% 의 steady IOPS 가 span 100% 보다 몇 배 높다 (모델 : 약 3.6배)
H2 절벽이 늦게, 덜 깊게 온다 | 쓴 양 기준 절벽 위치가 뒤로 밀리고, 바닥이 높다
H3 WAF 가 모델 근처다 | SMART 로 잰 WAF : span 100% ≈ 7–8, span 80% ≈ 2 근처
```

## 절차

```
$ sudo ./lab.sh cliff 80           # 앞쪽 96 GB 에만 4 KiB 랜덤 쓰기, 총 240 GB
$ sudo ./lab.sh cliff 90           # 선택
$ sudo ./lab.sh cliff 70           # 선택
```

- 매번 전체 TRIM 으로 시작하므로, 쓰지 않는 뒤쪽 LBA 는 TRIM 된 채로 남는다 : FTL 이 여유로 쓸 수 있다.
- 총 쓰기 양은 span 과 상관없이 용량의 2배 (240 GB) 로 같다. 그래서 span 이 작을수록 같은 LBA 를 더 여러 번 덮어쓴다 : steady state 에 더 확실히 들어간다.
- 실험 8 과 같은 날, 같은 연결에서 하는 것이 좋다 (온도와 조건을 맞추려고).

<div class="tip" markdown="1">
**다른 방법 : HPA.** `hdparm -N` 으로 드라이브가 보여 주는 최대 섹터 수를 줄이면 (Host Protected Area), 운영체제에게 드라이브가 정말로 작아진다. TRIM 된 뒤쪽을 '안 쓰기로 약속' 하는 span 방식과 같은 효과일 것이다 (FTL 에게는 둘 다 매핑 없는 LBA). 둘이 같은지 확인하고 싶다면 span 80% 실행 뒤 `sudo hdparm -Np187553318 장치` (80%) 로 바꾸고 `cliff 100` 을 한 번 더 한다 (그러면 '100%' 가 새 크기의 100%). 원래대로 : `sudo hdparm -Np234441648 장치`. `p` 는 '전원을 꺼도 유지' 라는 뜻이고, 설정 뒤 전원을 껐다 켜야 적용되는 드라이브가 많다.
</div>

## 결과 읽는 법

```
$ R=~/Ryu/old_ssd_results
$ python3 plot.py op.png $R/*-cliff-span100/cliff_iops.log=100% $R/*-cliff-span80/cliff_iops.log=80%
$ python3 smartdiff.py $(ls -d $R/*-cliff-span80 | tail -1)
```

1. 두 곡선의 steady state 평균의 비율 → 그림의 '× 3.6' 과 비교.
2. 각 span 의 WAF (smartdiff) 를 ρ–WAF 곡선 위에 찍는다. 점이 곡선보다 위에 있으면 실제 여유가 가정보다 작다는 뜻이고, 그 차이로 숨은 여유를 추정한다 (Claude 가 계산한다).
3. 시간이 되어 90% · 70% 도 했다면, 점 네 개로 이 드라이브의 **실제 WAF–OP 곡선** 이 생긴다.

## 시뮬레이터와의 연결 (덤)

시뮬레이터의 기본값 OP 20% 와 **WAF–OP 곡선** 이 이것의 모델 판이다. 실제 드라이브의 점들을 시뮬레이터 곡선 위에 겹쳐 그리는 것이 이 실험의 최종 그림이다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
