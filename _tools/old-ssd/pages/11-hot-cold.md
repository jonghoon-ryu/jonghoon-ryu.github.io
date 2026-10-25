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
### zipf:1.2, 4배 (2026.10.25 15:32 – 16:05, 33분)

결과 폴더 `20261025-153227-cliff-span100-zipf_1.2`. 페이지에는 2배를 적었지만, 균일 랜덤 (span 100%) 은 약 350 GB 에서 한 번 더 떨어지므로 [실험 10](/old-ssd-experiments/10-over-provisioning/) 의 span 100%, 4배와 같은 480 GB 로 돌렸다.

![uniform (span 100%, 4배) 과 zipf:1.2 (4배)](/old-ssd-experiments/11-hot-cold/hotcold.png)

```
 177 Wear_Leveling_Count                     162            164           +2
 190 Airflow_Temperature_Cel                  31             44          +13
 241 Total_LBAs_Written              29519438871    30457203735    +937764864

host writes (241):       480.1 GB
erase count (177):  +2  ->  NAND writes ~ 275 GB
WAF ~ 0.57   (177 counts whole steps, so between 0.29 and 0.86)
```
</div>

**절벽이 없다.** 480 GB 를 33분에 썼다 (균일 랜덤은 302분). 처음 약 9 GB 는 SLC 속도 (약 80k IOPS), 그 뒤 약 320 GB 까지 **63k IOPS 로 평평**, 320 – 335 GB 에서 약 52k 로 한 칸 내려와 끝까지 그대로다 (마지막 40 GB 51,657).

```table
잰 것 | uniform (span 100%, 4배) | zipf:1.2 (4배)
절벽 | 약 128 GB 에서 37k → 약 9k | **없음**
끝 (440 – 480 GB) | 3,253 IOPS | **51,657 IOPS (약 16배)**
WAF (177) | 약 3.7 (절벽 뒤 약 4.7) | **약 0.57 (0.29 – 0.86)**
전체 시간 | 302 분 | 33 분
지연 p99.9 / 최대 | — | 16.1 ms / 36.1 ms
```

**WAF 가 1 보다 작다 : NAND 에 쓴 양이 호스트가 쓴 양보다 적다.** 177 의 눈금 (+2, 한 칸 약 137 GB) 때문에 정확한 값은 모르지만, 가장 크게 잡아도 0.86 이다. GC 로는 이런 값이 나올 수 없다 : GC 는 쓰기를 늘리기만 한다. 그 이유는 zipf:1.2 가 생각보다 훨씬 몰린 분포이기 때문이다. fio 가 쓴 것과 같은 분포 (4 KiB 블록 약 2,930만 개, 쓰기 1억 1,700만 번) 로 계산하면 :

```table
가장 뜨거운 곳 | 받는 쓰기
1 MB (블록 256개) | **72.6%**
100 MB | 90.9%
1 GiB | 95.4%
3.2 GB (SLC 버퍼 크기) | 96.9%
12 GB (드라이브의 10%) | 98.3%
한 번이라도 쓰인 곳 | 약 15 GB (드라이브의 약 13%)
```

**쓰기의 약 3/4 이 1 MB 에 몰린다.** 같은 LBA 를 몇 ms 안에 다시 쓰면, 앞의 데이터는 NAND 에 닿기 전에 (DRAM 의 쓰기 캐시나 SLC 버퍼 안에서) 새 데이터로 바뀐다. 그러면 NAND 는 마지막 것만 쓴다. 호스트가 1 MB 를 수만 번 써도 NAND 쓰기는 조금만 늘어난다 : 이것이 'WAF < 1' 이다. 63k IOPS 가 TLC 에 바로 쓰는 속도 (37k) 보다 훨씬 높은 것도 같은 이유다. 첫 SLC 구간이 버퍼 크기 (약 3.2 GB) 보다 긴 약 9 GB 였던 것도, 버퍼 안의 데이터가 계속 덮어쓰여 버퍼가 덜 찼기 때문으로 보인다.

**절벽이 없는 이유** : 한 번이라도 쓰인 곳이 약 15 GB 뿐이라, 드라이브 입장에서는 'span 13%' 와 같다. 유효한 데이터가 15 GB 면 빈 블록이 바닥나지 않는다. H3 (차가운 LBA 는 OP 처럼 쓰인다) 의 가장 극단적인 모습이다.

**덤 : 177 은 SLC 의 지움을 (적어도 전부는) 세지 않는 것 같다.** 480 GB 가 모두 SLC 버퍼 (3.2 GB) 를 거쳤다면 버퍼 블록은 약 150번 지워졌을 것이다. 버퍼는 TLC 로 치면 약 10 GB, 전체 블록의 약 7% 이니, 평균 (177) 은 약 10 올라야 한다. 실제는 +2 다. 그러니 둘 중 하나다 : 반복된 쓰기의 대부분이 SLC 에도 닿지 않고 DRAM 안에서 사라졌거나, 177 이 SLC 영역의 지움을 세지 않는다. 밖에서는 어느 쪽인지 가를 수 없다. 어느 쪽이든 실험 10 · 12 의 177 WAF 는 'TLC 영역의 WAF' 로 읽는 것이 맞다.

**320 GB 의 한 칸 (63k → 52k) 은 설명하지 못했다.** 15 GB 의 차가운 꼬리가 다 쓰인 자리와도, 온도 (끝 44 °C, 균일 랜덤의 끝 46 °C 보다 낮음) 와도 맞아떨어지는 근거가 없다. 펌웨어의 어떤 배경 작업 (마모 평준화로 블록 옮기기 등) 이 시작된 자리일 수 있다.

```table
가설 | 결과
H1 고르지 않으면 steady 가 빠르다 | **맞음** : 끝에서 약 16배
H2 WAF 가 낮다 | **맞음, 지나치게** : 1 보다 작음. GC 가 아니라 캐시가 덮어쓰기를 흡수한 결과
H3 절벽이 늦게 온다 | **맞음, 극단적으로** : 480 GB 까지 절벽 없음
```

**그래서 zipf:1.2 는 'GC 가 뜨거운 데이터와 차가운 데이터를 어떻게 다루나' 를 재기에는 너무 몰렸다.** 이 실행이 잰 것은 주로 캐시의 덮어쓰기 흡수다. GC 를 재려면 뜨거운 곳이 캐시 · SLC 보다 훨씬 크고, 드라이브 전체가 쓰여서 꽉 차야 한다.

<div class="result" markdown="1">
**다음에 해 볼 것**
- `sudo ./lab.sh cliff 100 4 zoned:80/20:20/80` : 쓰기의 80% 가 24 GB (SLC 버퍼의 약 7배) 에, 20% 가 나머지 96 GB 에. 드라이브 전체가 쓰이니 절벽이 오고, 그 뒤 steady 와 WAF 를 uniform 과 바로 비교할 수 있다. 이것이 GC 의 hot/cold 시험이다
- (선택) zipf 를 약하게 (`zipf:0.8`) : 몰림의 정도를 바꾸며 '캐시 흡수' 에서 'GC' 로 넘어가는 자리 찾기
</div>

@@NAV@@
