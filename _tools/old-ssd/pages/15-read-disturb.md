---
layout: default
title: 15. Read disturb
permalink: /old-ssd-experiments/15-read-disturb/
---
@@STYLE@@

# 15. Read disturb : 같은 곳을 수억 번 읽으면

<div class="glance">
<b>목표</b><span>드라이브를 검사 가능한 무늬로 채운 뒤, 맨 앞 1 MiB 만 몇 시간 동안 계속 읽는다. 펌웨어가 그 블록을 옮기는 순간 (지연이 튀는 곳) 이 보이는지, 이웃 데이터가 상했는지 확인한다</span>
<b>보는 FTL 개념</b><span>read disturb (읽기 전압이 이웃 셀을 조금씩 프로그램함), 읽기 횟수 세기, read reclaim (블록 옮기기), ECC</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>채우기 20분 + 두드리기 HOURS (기본 6시간) + 확인 20분</span>
<b>명령</b><span><code>sudo ./lab.sh disturb 6</code></span>
</div>

## 배경

NAND 에서 한 페이지를 읽으려면 같은 블록의 **다른 모든 줄 (word line)** 에 높은 '통과 전압' 을 건다. 이 전압이 그 줄들의 셀에 전자를 아주 조금씩 밀어 넣는다. 한두 번은 아무 일도 없지만, 같은 블록을 수만–수십만 번 읽으면 이웃 셀의 전압이 올라가 비트 오류가 생긴다 : **read disturb**.
그래서 FTL 은 블록마다 읽은 횟수를 세고, 한도를 넘으면 그 블록의 데이터를 새 블록으로 옮긴다 (read reclaim). 그 순간 그 블록을 읽는 요청은 기다린다.

```table
이 실험에서 | 크기
두드리는 영역 | 맨 앞 1 MiB (4 KiB × 256개). TLC 블록 하나 (수 MiB 로 짐작) 안이거나 두세 개에 걸친다
읽기 속도 | QD32 4 KiB 랜덤 읽기 : 수만 IOPS
6시간 동안 | 수억 번 읽기 → 블록 하나가 수억 번 읽힌다 (흔히 말하는 한도 : 수만–수십만 번)
```

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 펌웨어가 읽기 횟수를 세어 블록을 옮긴다 | `hammer_lat.log` (1초마다 가장 느린 읽기) 에 주기적인 큰 튐 : 옮기는 동안의 대기. 튀는 간격 = 읽기 한도 ÷ IOPS
H2 옮기기 덕분에 데이터는 상하지 않는다 | verify 의 나쁜 블록 = 0
H3 옮기기 전까지는 이웃이 조금씩 나빠진다 | `near-after` 의 지연 (앞 1 GiB) 이 `near-before` 보다 길거나, SMART 195 (ECC 로 고친 오류) 가 는다
H4 컨트롤러가 읽기를 RAM 에 담아 둔다면 | IOPS 가 SATA 한계 (약 10만) 근처이고 지연이 아주 짧고 고르다 : NAND 를 안 읽는다 (그러면 이 실험은 다른 방법이 필요하다)
```

## 절차

```
$ sudo ./lab.sh disturb 6        # 숫자 = 두드릴 시간 (시간 단위). 밤새 하려면 10–12
```

```table
단계 | 하는 일
1 | 전체를 1 MiB 순차로 쓰되 4 KiB 마다 crc32c 머리말 (실험 16 과 같은 무늬)
2 | `near-before` : 앞 1 GiB 안의 4 KiB 랜덤 읽기 QD1, 60초
3 | SMART 기록
4 | `hammer` : 앞 1 MiB 만 4 KiB 랜덤 읽기 QD32, HOURS 시간. 1초마다 IOPS 와 가장 느린 읽기 기록
5 | SMART 기록, `near-after` (2 와 같은 측정)
6 | 전체 verify : 모든 4 KiB 블록의 체크섬 → `verify-summary.txt`
```

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-disturb-* | tail -1)
$ python3 plot.py hammer-lat.png $D/hammer_lat.log=max
$ python3 plot.py hammer-iops.png $D/hammer_iops.log
$ cat $D/verify-summary.txt; python3 smartdiff.py $D
$ column -s, -t $D/summary.csv
```

1. **튐의 간격** : 두 튐 사이의 시간 × 평균 IOPS ÷ (1 MiB 가 걸친 블록 수) ≈ 펌웨어의 읽기 한도. Claude 가 로그에서 튐을 찾아 계산한다.
2. **verify** : 0 이 아니면 read disturb 로 상한 데이터를 ECC 도 펌웨어도 막지 못한 것이다.
3. **near-before / after** 의 50% · 99% 지연.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
