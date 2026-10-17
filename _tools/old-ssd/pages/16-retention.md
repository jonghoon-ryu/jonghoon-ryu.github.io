---
layout: default
title: 16. Retention
permalink: /old-ssd-experiments/16-retention/
---
@@STYLE@@

# 16. Retention : 전원 없이 둔 데이터

<div class="glance">
<b>목표</b><span>검사할 수 있는 패턴으로 드라이브를 채우고, 전원 없이 몇 주 둔 뒤 다시 읽어 속도 변화와 오류를 본다</span>
<b>보는 FTL 개념</b><span>data retention, 전하 누설, ECC 의 한계, read retry (실험 1 의 '통제된' 판)</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>쓰기 20분 + 2–4주 보관 + 확인 1시간</span>
<b>명령</b><span><code>sudo ./lab.sh ret-write</code>, (몇 주 뒤) <code>sudo ./lab.sh ret-check</code></span>
</div>

## 배경

@@FIG ret_leak@@

실험 1 의 데이터는 이미 **1년 넘게 전원 없이** 지냈다. 그러나 파일마다 쓴 뒤 전원이 켜져 있던 기간과, 그동안 펌웨어가 다시 썼는지는 모른다. 그리고 전원이 끊긴 날도 짐작 (2024.12 쯤) 일 뿐이다. 이 실험은 그것을 통제한다 : **정확히 언제 썼고, 그날부터 전원이 없었다.**

몇 주는 짧다. 새 드라이브라면 차이가 거의 없을 것이다. 그러나 이 드라이브는 이미 닳았고 (실험 0 의 177), 실험 8–15 에서 더 닳는다. 닳은 셀일수록 전하를 빨리 잃는다.

<div class="tip" markdown="1">
**더 강하게 하고 싶다면** 실험 18 (끝까지 쓰기) 을 중간에 멈추고, 마모가 많이 된 상태에서 이 실험을 한 번 더 한다. 같은 2–4주라도 결과가 훨씬 클 수 있다.
</div>

## 시간표

@@FIG ret_timeline@@

## 가설과 예상

@@FIG ret_expect@@

```table
가설 | 맞다면 보일 것
H1 몇 주 보관으로도 읽기가 느려진다 | ret-check 의 스캔이 ret-write 직후 (또는 실험 3 의 fresh) 보다 느리고, `max_ms` 꼬리가 길다
H2 ECC 가 아직 다 고친다 | fio verify 의 '나쁜 블록' = 0
H3 닳은 정도가 클수록 효과가 크다 | (실험 18 중간에 한 번 더 했을 때) 차이가 커진다
```

## 절차

```
# 0일 : 전체를 1 MiB 순차로 쓰되, 4 KiB 마다 crc32c 체크섬 머리말을 넣는다
$ sudo ./lab.sh ret-write
$ sudo poweroff                 # 끄고, 드라이브의 SATA 전원 케이블을 뺀다 (또는 드라이브를 꺼낸다)

# 보관 : 2–4주. 날짜와 보관 장소 (대략의 온도) 를 적어 둔다

# N일 : 다시 연결하고 켠 뒤, 다른 것을 하기 전에 바로
$ sudo ./lab.sh ret-check
```

`ret-check` 가 하는 일 (쓰지 않는다) :
1. SMART 기록
2. **전체 스캔** (256 MiB 구간 전부) : 보관한 데이터를 '처음' 읽는 속도와 가장 느린 읽기. 두 번째 읽기는 펌웨어가 이미 고쳐 썼을 수 있으므로 이것이 먼저다
3. fio `--verify_only` : 모든 4 KiB 블록의 체크섬 확인. 틀린 블록 수를 `verify-summary.txt` 에 적는다
4. SMART 기록 (187, 195 가 늘었는지)

<div class="warn" markdown="1">
- 보관 중에 컴퓨터를 켜야 하면 **드라이브의 전원 케이블을 뺀 채로** 켠다. 전원이 들어가면 펌웨어가 백그라운드에서 데이터를 고쳐 쓸 수 있다.
- 따뜻한 곳은 누설을 빠르게 한다 (온도가 10 °C 오를 때마다 몇 배라는 Arrhenius 관계가 흔히 쓰인다). 방 온도면 되고, 온도를 적어 두면 해석에 도움이 된다.
- **(선택) 빠르게 하기** : 어차피 버릴 드라이브이므로 한 번은 따뜻한 곳 (40–50 °C) 에 두어 보는 것도 방법이다. 840 EVO 의 보관 온도 한도 (−55–95 °C 로 알려짐, 확인 필요) 를 넘지 않고, 불이 날 수 있는 곳은 피한다.
- 비교 기준이 되는 '0일' 의 스캔이 필요하면, `ret-write` 직후 `sudo ./lab.sh scan ret-day0` 를 한 번 하고 끈다 (선택).
</div>

## 결과 읽는 법

```
$ R=~/Ryu/old_ssd_results
$ python3 plot.py ret.png $R/*-scan-fresh/scan.csv=fresh $R/*-ret-check/scan.csv=weeks $R/*-scan-old/scan.csv=years
$ cat $R/*-ret-check/verify-summary.txt
$ python3 smartdiff.py $(ls -d $R/*-ret-check | tail -1)
```

세 곡선 (막 쓴 · 몇 주 · 1년 넘게) 을 한 그림에 놓는 것이 목표다. 세 곡선 모두 같은 SATA 연결에서 잰다. '1년 넘게' 곡선 (`scan-old`) 은 실험 1 에서 이미 쟀다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
