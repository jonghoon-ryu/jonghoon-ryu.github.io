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

## 결과

<div class="result" markdown="1">
2026.10.18 12:53 – 13:07, 결과 폴더 `20261018-125336-trim`.

### H1 : TRIM 한 곳은 0 으로 읽히나

```table
스캔 (256 MiB 마다 32 MiB) | 앞쪽 절반 | 뒤쪽 절반
전체 TRIM 직후 (`scan-trimmed`) | 0 으로만 읽힘 **100%**, 451 MB/s | 0 으로만 읽힘 **100%**, 456 MB/s
앞쪽 절반을 쓴 뒤 (`scan-half`) | 0 으로만 읽힘 **0%** (데이터), 463 MB/s | 0 으로만 읽힘 **100%**, 462 MB/s
```

**맞다.** 448개 구간 (15 GB) 이 하나도 빠짐없이 0 이었다. 이 드라이브는 `hdparm -I` 에 'TRIM 뒤 0 을 약속' (`Deterministic read ZEROs after TRIM`) 하지 않지만 ([실험 2](/old-ssd-experiments/2-features/)), 실제로는 0 을 돌려준다. 커널이 이 모델에 `zeroaftertrim` 예외를 두는 것과 맞는다. 앞쪽에 데이터를 쓰자 정확히 앞쪽 절반만 0 이 아니게 되었다 : TRIM 은 위치마다 정확하다.

![TRIM 직후와 앞쪽 절반을 쓴 뒤의 스캔](/old-ssd-experiments/4-trim/scans.png)

순차로 크게 (1 MiB 씩) 읽는 스캔에서는 데이터가 있는 곳과 0 인 곳이 모두 약 455 MB/s 로 **같다** : 이 읽기는 SATA 링크가 한계라 NAND 를 읽든 안 읽든 차이가 보이지 않는다. 차이는 아래의 4 KiB 읽기 하나하나에서 보인다.

### H2 · H3 : 매핑 없는 읽기는 NAND 를 안 거치나

![지연 percentile](/old-ssd-experiments/4-trim/latency.png)

```table
4 KiB 랜덤 읽기 60초 | IOPS | 평균 | 1% | 50% | 99% | 99.9%
QD1, 매핑 있음 (앞쪽 절반, 데이터) | 7,164 | 126 µs | 100 µs | 121 µs | 153 µs | 206 µs
QD1, **매핑 없음** (뒤쪽 절반, TRIM) | **13,987** | **61 µs** | 35 µs | 63 µs | 78 µs | 134 µs
QD32, 매핑 있음 | 90,475 | 351 µs | 322 µs | 334 µs | **506 µs** | 618 µs
QD32, 매핑 없음 | 95,111 | 334 µs | 326 µs | 334 µs | 342 µs | 399 µs
```

- **H2 : 맞다.** 한 번에 하나씩 (QD1) 읽으면, 매핑 없는 읽기가 **두 배 빠르다** (63 µs 대 121 µs, 중앙값). 차이 약 **58 µs** 가 'NAND 에서 페이지를 읽어 ECC 로 확인하는 시간' 이다 : 매핑이 없으면 컨트롤러는 표만 보고 0 을 돌려준다. 남은 약 60 µs 는 SATA 명령 · 링크 · 컨트롤러 · 매핑 표 찾기 · 커널의 몫이다.
- 이 드라이브의 TLC 페이지 읽기 시간을 밖에서 어림한 값 : **약 60 µs** (새 데이터 기준. 실험 1 의 오래된 데이터는 다시 읽기 때문에 1 MiB 에 수백 ms 였다).
- **H3 : 일부만 맞다.** 32개씩 걸어 두면 (QD32) 둘 다 약 **9만 IOPS** 로 거의 같다 (90k 대 95k) : 중앙값 지연이 둘 다 334 µs 이고, 32 ÷ 334 µs ≈ 9.6만이다. 곧 이 때의 한계는 NAND 가 아니라 **SATA 명령 처리** (링크와 컨트롤러가 명령을 주고받는 속도) 다. NAND 를 읽는 쪽은 꼬리에서만 티가 난다 (99% 506 µs 대 342 µs).
- 이 '약 9.5만 IOPS' 는 Samsung 이 밝힌 4 KiB 랜덤 읽기 QD32 값 (9.4만, 120GB) 과 거의 같다.

### 덤 : 앞쪽 절반 쓰기

앞쪽 절반 (60 GB) 을 1 MiB 순차로 쓰는 데 평균 **151.5 MB/s** (화면의 `w=144MiB/s`). [실험 3](/old-ssd-experiments/3-slc-cache/) 의 TLC 직접 쓰기 속도 (약 150 MB/s) 와 같다. 한 번 33% 근처에서 109 MiB/s 로 잠깐 떨어졌고, 1 MiB 쓰기 하나의 최대가 381 ms 였다 : 쓰기 도중 드라이브 안의 일 (버퍼 정리, 블록 준비) 이 잠깐 끼어든 것으로 보인다.

### 정리

```table
가설 | 결과
H1 TRIM 된 LBA 는 0 으로 읽힌다 | **맞다** : 100%. 약속 (hdparm) 은 없지만 실제로는 0
H2 매핑 없는 읽기는 NAND 를 안 거친다 | **맞다** : QD1 지연이 절반 (63 대 121 µs). 차이 약 60 µs = NAND 페이지 읽기
H3 그래서 IOPS 도 높다 | QD1 에서는 2배. **QD32 에서는 거의 같다** (95k 대 90k) : 둘 다 SATA 명령 처리 (약 9.5만 IOPS) 에 묶인다
```
</div>

@@NAV@@
