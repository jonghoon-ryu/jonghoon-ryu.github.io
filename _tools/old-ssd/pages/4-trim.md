---
layout: default
title: 4. TRIM 과 매핑 없는 읽기
permalink: /old-ssd-experiments/4-trim/
---
@@STYLE@@

# 4. TRIM 과 매핑 없는 읽기 : NAND 를 안 거치는 읽기

<div class="glance">
<b>목표</b><span>TRIM 된 (매핑이 없는) LBA 를 읽으면 무엇이 얼마나 빨리 오는지, 데이터가 있는 LBA 와 비교한다</span>
<b>보는 FTL 개념</b><span>매핑 표 (L2P), TRIM, 매핑 없는 읽기, 'deterministic read zero after TRIM'</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA (TRIM 이 필요하다)</span>
<b>시간</b><span>약 30분</span>
<b>명령</b><span><code>sudo ./lab.sh trim</code></span>
</div>

## 배경 : 매핑 표

호스트는 디스크를 LBA (논리 블록 주소) 의 줄로 본다. NAND 에는 덮어쓰기가 안 되므로, FTL 은 쓸 때마다 새 자리에 쓰고 **LBA → NAND 위치** 를 표에 적는다. 읽을 때는 이 표를 찾아 그 자리를 읽는다.

@@FIG trim_table@@

TRIM 은 '이 LBA 들은 이제 쓰지 않는다' 는 알림이다. FTL 은 표에서 그 줄을 지우고, 그 NAND 페이지를 무효로 표시한다. 그 뒤 그 LBA 를 읽으면 :
- 표에 없으니 NAND 를 읽을 것이 없다
- 컨트롤러는 0 (또는 정해진 값) 을 바로 돌려줄 수 있다

`hdparm -I` 에 **Deterministic read ZEROs after TRIM** 이 있으면 0 이 보장된다. 없으면 '정해지지 않음' 이지만, 실제로는 대부분 0 이다. 둘 다 이 실험에서 확인한다.

TRIM 이 성능에 중요한 또 다른 이유는 GC 다 :

@@FIG trim_gc@@

## 가설과 예상

@@FIG trim_expect@@

```table
가설 | 맞다면 보일 것
H1 TRIM 된 LBA 는 0 으로 읽힌다 | 전체 TRIM 직후 스캔의 `zero_frac` 이 모든 구간에서 1.0
H2 매핑 없는 읽기는 NAND 를 안 거친다 | QD1 4 KiB 랜덤 읽기 지연 : 매핑 없음이 매핑 있음보다 확실히 짧다 (NAND 페이지 읽기 시간만큼)
H3 그래서 IOPS 도 높다 | QD32 IOPS : 매핑 없음 > 매핑 있음. 단 SATA 인터페이스 한계 (약 10만 IOPS) 에 둘 다 걸리면 차이가 줄어든다
```

## 절차

```
$ sudo ./lab.sh trim
```

스크립트가 하는 일 :

```table
단계 | 하는 일 | 왜
1 | `blkdiscard` 로 전체 TRIM, 2분 쉼 | 모든 매핑을 지운 출발점
2 | 스캔 (256 MiB 마다 32 MiB) → `scan-trimmed.csv` | H1 : 다 0 인가, 얼마나 빠른가
3 | 앞쪽 절반을 1 MiB 순차로 쓴다 | 앞 절반만 매핑이 생긴다
4 | 4 KiB 랜덤 읽기 QD1, 60초 : 앞 절반 → `rd-mapped`, 뒤 절반 → `rd-unmapped` | H2 : 읽기 하나의 지연
5 | 같은 것을 QD32 로 → `rd32-mapped`, `rd32-unmapped` | H3 : IOPS
6 | 다시 스캔 → `scan-half.csv` | 앞 절반은 데이터, 뒤 절반은 0 인지 한 그림으로
```

실험을 시작하기 전에 `sudo hdparm -I /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K | grep -i trim` 의 출력을 남겨 둔다 (`check` 결과 폴더의 `hdparm-I.txt` 에도 있다).

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-trim | tail -1)
$ python3 plot.py lat.png $D/rd-mapped_lat.log=mapped $D/rd-unmapped_lat.log=unmapped
$ python3 plot.py scans.png $D/scan-trimmed.csv=trimmed $D/scan-half.csv=half
```

1. **지연** : 각 `rd-*.json` 의 `clat` percentile (50%, 99%, 99.9%) 을 표로 놓는다. 차이 = NAND 페이지 읽기 + FTL 의 일. 840 EVO 의 TLC 페이지 읽기 시간을 거꾸로 추정해 볼 수 있다.
2. **IOPS** : `rd32-*` 의 IOPS. 매핑 없는 쪽이 SATA 한계에 붙으면, 그 값이 '인터페이스의 한계' 다.
3. **0 확인** : `scan-trimmed.csv` 의 `zero_frac` 이 모두 1 이 아니면, TRIM 뒤에 0 이 아닌 값이 나온 것이다 (흥미로운 결과).
4. **실험 1 과 연결** : 실험 1 의 위치 지도에서 0 으로 읽힌 빈 공간이 빨랐다면, 같은 현상이다.

## 시뮬레이터와의 연결 (덤)

시뮬레이터의 `Unmapped_Reads_Return_Zeros` 와 읽기 지연 차트가 바로 이 동작이다. 실제 드라이브에서 잰 두 지연 (매핑 있음 / 없음) 을 시뮬레이터 설정의 읽기 시간과 비교한다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
