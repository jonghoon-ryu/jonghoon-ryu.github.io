---
layout: default
title: 12. WAF (SMART)
permalink: /old-ssd-experiments/12-waf/
---
@@STYLE@@

# 12. WAF : 드라이브가 직접 센 숫자로 쓰기 증폭 재기

<div class="glance">
<b>목표</b><span>SMART 의 '호스트가 쓴 양' (241) 과 '평균 지움 횟수' (177) 로 실제 WAF 를 추정한다. 순차 쓰기 (WAF ≈ 1 예상) 와 랜덤 쓰기 (실험 8, 10) 를 비교한다</span>
<b>보는 FTL 개념</b><span>write amplification, 마모 평준화가 세는 지움 횟수</span>
<b>지우나?</b><span>예 (순차 쓰기 실행). 랜덤 쪽은 실험 8, 10 의 기록을 그대로 쓴다</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>순차 5회 쓰기 약 1.5–2시간</span>
<b>명령</b><span><code>sudo ./lab.sh seqwaf 5</code>, <code>python3 smartdiff.py 결과폴더</code></span>
</div>

## 배경

@@FIG waf_flow@@

많은 드라이브는 SMART 에 'NAND 에 쓴 양' 을 따로 보여 준다 (Crucial · Micron 의 247/248, Intel 의 NAND writes 등). 840 EVO 에는 그런 항목이 없는 것으로 알고 있다 (실험 0 의 SMART 출력으로 확인). 대신 177 을 쓴다.

@@FIG waf_177@@

## 가설과 예상

@@FIG waf_expect@@

```table
가설 | 맞다면 보일 것
H1 순차 쓰기의 WAF 는 1 에 가깝다 | seqwaf 5 : 호스트 600 GB, 177 이 약 4–5 증가 → WAF ≈ 0.9–1.2
H2 랜덤 쓰기 (span 100%) 의 WAF 는 크다 | 실험 8 : 호스트 240 GB, 177 이 10 이상 증가 → WAF 5–10
H3 OP 가 크면 WAF 가 작다 | 실험 10 (span 80%) 의 WAF 가 실험 8 보다 확실히 작다
```

## 절차

```
# 순차 : 전체 TRIM → 128 KiB 순차 쓰기로 드라이브 전체를 5번
$ sudo ./lab.sh seqwaf 5

# 각 실행의 SMART 앞뒤 비교 (실험 3–11 의 결과 폴더에도 그대로 쓸 수 있다)
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-seqwaf-x5
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-cliff-span100
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-cliff-span80
```

`smartdiff.py` 의 출력 예 (가짜 숫자로 만든 시험 출력) :

```
 177 Wear_Leveling_Count                     300            312          +12
 241 Total_LBAs_Written               1000000000     1937766592   +937766592

host writes (241):       480.1 GB
erase count (177):  +12  ->  NAND writes ~ 1649 GB
WAF ~ 3.43   (177 counts whole steps, so between 3.15 and 3.72)
```

## 주의할 점

<div class="warn" markdown="1">
- **177 의 눈금은 약 137 GB 다.** 177 이 1–2 만 늘면 WAF 오차가 ±50% 를 넘는다. 순차 쓰기를 5회로 정한 이유다.
- 177 이 TurboWrite 영역 (SLC 로 쓰는 블록) 의 지움도 같이 세는지, 펌웨어가 평균을 어떻게 내는지는 알 수 없다. 순차 쓰기에서 WAF 가 1 보다 확실히 크게 나오면, SLC → TLC 옮기기 (데이터를 두 번 씀) 가 섞인 것일 수 있다 : 그것도 결과다.
- 실험 사이에 드라이브가 쉬는 동안 하는 일 (버퍼 비우기, 마모 평준화) 도 177 을 올린다. 그래서 `smart-before` 는 실행 직전, `smart-after` 는 실행 직후에 찍는다 (`lab.sh` 가 그렇게 한다).
</div>

## 결과 읽는 법

1. 실행마다 WAF 와 오차 범위를 표로 : 순차, 랜덤 100%, 랜덤 80% (+ 90%, 70%).
2. 랜덤의 값들을 실험 10 의 ρ–WAF 곡선에 찍는다 → 숨은 여유 공간 추정.
3. 순차 WAF 가 1 보다 얼마나 큰지 → 'SLC 버퍼를 거친 비용' 의 추정.

## 시뮬레이터와의 연결 (덤)

시뮬레이터는 GC 가 복사한 페이지를 직접 세어 WAF 를 낸다. 실제 드라이브는 그 숫자를 보여 주지 않으니 177 로 거꾸로 추정한다. 두 방법의 차이 자체가 '밖에서 FTL 을 재는 일' 의 한계를 보여 준다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
