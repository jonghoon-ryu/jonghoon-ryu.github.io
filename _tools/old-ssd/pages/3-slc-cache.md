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
<b>연결</b><span>SATA (TRIM 이 필요하다)</span>
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
# 0. check 를 다시 해서 DISC-MAX 가 0B 가 아닌지
$ sudo ./lab.sh check

# 1. 전체 TRIM → 2분 쉼 → 1 MiB 순차 쓰기 QD8 로 처음부터 끝까지, 1초마다 속도 기록
$ sudo ./lab.sh slc

# 2. 버퍼 회복 : 8 GiB 로 버퍼를 채운 뒤, 0 / 1 / 5 / 15 분 쉬고 다시 8 GiB 씩
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

## 결과

<div class="result" markdown="1">
### 1단계 : `slc` (드라이브 전체 순차 쓰기)

2026.10.18 11:21, 결과 폴더 `20261018-112114-slc`. 전체 TRIM → 2분 쉼 → 1 MiB 순차 쓰기 QD8 로 120 GB 전체를 786초 동안.

![순차 쓰기 속도](/old-ssd-experiments/3-slc-cache/slc.png)

**교과서 같은 계단 하나**

```table
구간 | 쓴 양 | 속도 | 뜻
처음 약 6초 | 약 **3.2 GB** | **533 MB/s** (1초마다 533, 533, 533, 533, 533, 515) | SLC 버퍼 (TurboWrite) 에 쓰는 속도. 533 MB/s 는 SATA 3 의 한계 근처라, 버퍼 자체는 더 빠를 수도 있다
그 뒤 끝까지 (약 780초) | 약 116.8 GB | **약 150 MB/s** (147 – 153, 거의 평평) | 버퍼가 다 찬 뒤 TLC 에 바로 쓰는 속도
전체 평균 | 120.03 GB / 786.6 s | 152.6 MB/s |
```

화면의 fio 진행 줄 `w=144MiB/s` 는 같은 값이다 : 144 MiB/s × 1.049 = 151 MB/s (MiB 와 MB 의 차이는 [fio 사용법](/old-ssd-experiments/fio/) 3절).

**지연** : 1 MiB 쓰기 하나의 평균 54.7 ms, 99% 71.8 ms, 최대 137.6 ms. Little 의 법칙으로 맞춰 보면 : 동시에 8개 ÷ 54.7 ms × 1 MiB ≈ 153 MB/s. 측정값과 같다.

**SMART 앞뒤**

```table
속성 | 앞 | 뒤 | 읽는 법
241 Total_LBAs_Written | 22,481,189,514 | 22,715,630,218 | +234,440,704 × 512 B = **120.03 GB** : 정확히 드라이브 하나만큼 썼다
177 Wear_Leveling_Count | 117 | **118** | 블록마다 평균 1번 더 지웠다 : 드라이브 전체를 한 번 쓴 것과 맞다
190 온도 | 32 °C | **48 °C** | 13분 쓰기로 16 °C 올랐다 (정규화 값 100 − 48 = 52 가 지금까지의 최저 = 가장 뜨거웠던 때)
5 · 179 · 181–183 · 187 · 195 · 199 | 0 | 0 | 쓰기 실패 · 오류 없음
```

`smartdiff.py` 의 WAF : 177 이 1 만 늘어서 약 1.15 (눈금이 커서 0 – 2.3 사이라는 것만 말할 수 있다). 순차 쓰기의 WAF 는 실험 12 에서 5번 써서 다시 잰다.

**가설 확인**

```table
가설 | 결과
H1 버퍼는 약 3 GB 다 | **맞다** : 약 3.2 GB 에서 계단처럼 떨어진다 (1초 단위라 ±0.5 GB)
H2 버퍼 밖 TLC 쓰기는 약 100–150 MB/s 다 | **맞다, 위쪽 끝** : 약 150 MB/s, 120 GB 내내 거의 흔들림 없이 평평
H3 쉬면 버퍼가 다시 빈다 | 2단계 (`slc-idle`) 에서 확인
```

**실험 1 과 비교** : 이 드라이브는 **쓰기는 정상** 이다 (버퍼 533 MB/s, TLC 150 MB/s : 이 모델에 알려진 값과 비슷하다). 문제는 오래 둔 데이터를 **읽을 때** 뿐이었다 (약 9 MB/s). 이제 드라이브 전체가 막 쓴 데이터이므로, 같은 지도 (`scan fresh 8`) 를 다시 그리면 '데이터의 나이' 만 다른 비교가 된다.

### 2단계 : `slc-idle` · 3단계 : `scan fresh 8` · 4단계 : `selftest long`

아직 실행 전.
</div>

@@NAV@@
