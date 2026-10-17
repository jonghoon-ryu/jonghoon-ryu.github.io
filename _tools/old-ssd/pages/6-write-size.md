---
layout: default
title: 6. 쓰기 크기 · 정렬
permalink: /old-ssd-experiments/6-write-size/
---
@@STYLE@@

# 6. 쓰기 크기와 정렬 : 4 KiB 보다 작게, 4 KiB 에서 어긋나게 쓰면

<div class="glance">
<b>목표</b><span>512 B 부터 64 KiB 까지 랜덤 쓰기의 속도 · 지연을 재고, 4 KiB 경계에서 512 B 어긋난 4 KiB 쓰기와 비교해서 FTL 의 매핑 단위와 '읽고-고치고-쓰기' 비용을 밖에서 찾는다</span>
<b>보는 FTL 개념</b><span>매핑 단위 (4 KiB), read-modify-write, 섹터 크기 (512 B 논리 / 4 KiB 내부), 파티션 정렬</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>약 40분 (채우기 15분 + 크기 18개 × 1.5분)</span>
<b>명령</b><span><code>sudo ./lab.sh wsize</code></span>
</div>

## 배경 : 드라이브는 512 B 를 받지만 4 KiB 로 기억한다

호스트에게 이 드라이브의 섹터는 512 바이트다 (`lsblk -o PHY-SEC,LOG-SEC`). 그러나 FTL 의 매핑 표는 **4 KiB 마다 한 줄** 이 보통이다 (실험 19 의 DRAM 계산 참고).
그러면 512 B 를 쓰는 요청은 이렇게 된다 :

```table
요청 | FTL 이 할 일
4 KiB, 4 KiB 경계에 맞춤 | 새 4 KiB 자리에 쓰고 표의 한 줄을 바꾼다
512 B | 그 4 KiB 의 나머지 3.5 KiB 를 **읽어서** 합친 뒤 새 4 KiB 자리에 쓴다 (read-modify-write)
4 KiB, 512 B 어긋남 | 두 개의 4 KiB 에 걸친다 : 둘 다 읽고-고치고-쓰기
8 KiB · 16 KiB … | 4 KiB 여러 개. NAND 페이지 (8 KiB 또는 16 KiB 로 짐작) 를 한 번에 채울 수 있다
```

옛날에 'Windows XP 의 파티션은 63 섹터에서 시작해서 SSD 에서 느리다' 고 했던 이유가 이 어긋남이다. 지금 도구들은 파티션을 1 MiB 경계에 맞춘다.

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 매핑 단위는 4 KiB 다 | 512 B · 1 KiB · 2 KiB 의 IOPS 가 4 KiB 보다 높지 않다 (오히려 낮다), QD1 지연이 4 KiB 보다 길다
H2 어긋난 4 KiB 는 두 배 일이다 | `mis4k` 의 IOPS 가 `bs4k` 의 절반쯤, 지연은 두 배쯤
H3 큰 쓰기는 MB/s 가 오른다 | 4 → 64 KiB 로 MB/s 가 오르다가 어느 크기에서 평평해진다 (그 크기 ≈ 한 번에 프로그램하는 단위 × 병렬성)
```

`wsize` 는 드라이브를 먼저 다 채운 뒤 측정한다 : 512 B 쓰기의 '나머지를 읽기' 가 진짜 NAND 를 읽게 하려고. 각 측정은 30초로 짧아서 대부분 SLC 버퍼 안에서 일어난다. 그래도 크기끼리의 비교는 공정하다 (모두 같은 조건).

## 절차

```
$ sudo ./lab.sh wsize
```

```table
단계 | 하는 일
1 | 전체 TRIM, 1 MiB 순차로 전체를 채움
2 | 앞 8 GiB 안의 랜덤 쓰기 : `--bs=512 · 1k · 2k · 4k · 8k · 16k · 32k · 64k` × QD 1 · 32, 각 30초, 사이에 60초 쉼
3 | 어긋난 4 KiB : `--bs=4k --blockalign=4k --offset=512` × QD 1 · 32
4 | `summary.csv`
```

## 결과 읽는 법

```
$ column -s, -t $(ls -d ~/Ryu/old_ssd_results/*-wsize | tail -1)/summary.csv
```

1. **QD1 지연 – 크기** : 4 KiB 에서 가장 낮고 그보다 작으면 다시 오르면 H1.
2. **`mis4k` ÷ `bs4k`** : IOPS 비와 지연 비 (H2).
3. **MB/s – 크기** : 평평해지는 지점 (H3). QD32 와 QD1 을 따로 본다.
4. 실험 5 의 `randwrite 4k` 칸과 같은 값이 나오는지 (같은 조건이면 같아야 한다).

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
