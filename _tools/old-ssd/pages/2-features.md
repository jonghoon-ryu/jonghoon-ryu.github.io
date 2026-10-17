---
layout: default
title: 2. 기능 · 자가 진단
permalink: /old-ssd-experiments/2-features/
---
@@STYLE@@

# 2. 드라이브가 스스로 알려 주는 것 : ATA 기능, 로그, 자가 진단

<div class="glance">
<b>목표</b><span>지우기 전에, 드라이브가 보고하는 모든 기능 · 로그 · 통계를 남기고, 드라이브 스스로 전체를 검사하게 해서 (SMART 자가 진단) 걸린 시간과 결과를 본다</span>
<b>보는 것</b><span>ATA 기능 목록, 보안 (Secure Erase) 상태, HPA, 쓰기 캐시, SMART 오류 · 자가 진단 로그, 장치 통계, 온도 기록, SATA 링크 오류</span>
<b>지우나?</b><span>아니오. 읽기만 한다 (자가 진단은 드라이브 안에서 읽기만 한다)</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>features 1분, 자가 진단 (long) 은 드라이브가 알려 주는 시간 (보통 수십 분)</span>
<b>명령</b><span><code>sudo ./lab.sh features</code>, <code>sudo ./lab.sh selftest long</code></span>
</div>

## 왜 지금 하나

뒤의 실험들이 쓰는 기능 (TRIM 뒤 0 읽기, Secure Erase, 쓰기 캐시 끄기, HPA) 을 이 드라이브가 정말 지원하는지 **먼저 확인** 한다. 그리고 드라이브가 기억하는 과거 (오류 로그, 자가 진단 기록, 온도 기록) 는 지우는 실험을 하면 섞이거나 덮인다 : 지금 남겨야 한다.

**자가 진단을 실험 1 뒤에 하는 이유** : long 자가 진단은 드라이브가 안에서 모든 LBA 를 읽는다. 오래된 데이터를 읽는 일이라, 펌웨어가 그 블록들을 다시 써 버릴 수 있다. 실험 1 의 측정을 먼저 끝낸다.

## 1단계 : 기능과 로그 모으기

```
$ sudo ./lab.sh features
```

하는 일 (아무것도 쓰지 않는다) :

```table
명령 | 저장 파일 | 보는 것
`hdparm -I` | `hdparm-I.txt` | ATA 기능 전체 : 지원 (`*` 가 붙으면 켜짐)
`hdparm -N -W -A -B` | `hdparm-NWAB.txt` | 보이는 최대 섹터 / 진짜 최대 (HPA), 쓰기 캐시, 미리 읽기, 전원 관리 (APM)
`smartctl -x` | `smart-features.*` | 속성 표와 모든 로그
`smartctl -l devstat` | `smart-log-devstat.txt` | 장치 통계 : 전원 켠 횟수 · 시간, 읽고 쓴 섹터, 보고한 고치지 못한 오류
`smartctl -l error` · `xerror` | `smart-log-error.txt` · `xerror` | 드라이브가 기억하는 최근 오류 (시각은 전원 켠 시간 기준)
`smartctl -l selftest` | `smart-log-selftest.txt` | 지난 자가 진단 기록 (Windows 시절 것이 남아 있을 수 있다)
`smartctl -l scttemp` | `smart-log-scttemp.txt` | 온도 기록 (지원하면)
`smartctl -l sataphy` | `smart-log-sataphy.txt` | SATA 링크의 CRC 오류 · 재접속 횟수 (케이블 · 어댑터 문제)
```

`hdparm -I` 에서 특히 볼 줄 :

```table
줄 (예) | 뜻 | 어느 실험
`Data Set Management TRIM supported (limit 8 blocks)` | TRIM 지원, 명령 하나에 몇 개 범위 | 4
`Deterministic read ZEROs after TRIM` | TRIM 한 곳을 읽으면 반드시 0 | 4
`Write cache` (앞에 `*`) | 쓰기 캐시가 켜져 있다 | 7
`Native Command Queueing (NCQ)`, `Queue depth: 32` | 동시에 받을 수 있는 명령 수 | 5
`Security:` 아래 `supported`, `not enabled`, `not frozen`, `supported: enhanced erase`, `2min for SECURITY ERASE UNIT` | Secure Erase 를 할 수 있는 상태인가, 걸린다고 말하는 시간 | 14
`max sectors = 234441648/234441648, HPA is disabled` | 숨겨 둔 영역 (HPA) 이 없다 | 10 (덤)
`SATA Rev 3.0` / `Gen3 signaling speed (6.0Gb/s)` | 링크 속도 : SATA 3 이면 상한 약 550 MB/s | 5
```

## 2단계 : SMART 자가 진단

```
$ sudo ./lab.sh selftest long
```

1. `smartctl -c` 가 알려 주는 '권장 대기 시간' 을 보여 준다 (드라이브가 스스로 예상한 시간)
2. `smartctl -t long` 으로 시작하고, 30초마다 진행 (`% of test remaining`) 을 찍는다
3. 끝나면 **실제로 걸린 시간** 과 자가 진단 로그 (`Completed without error` 또는 `read failure` 와 첫 오류 LBA) 를 남긴다

자가 진단 동안에는 드라이브를 쓰지 않는다 (다른 I/O 가 있으면 진단이 늦어지거나 멈춘다).

## 가설과 예상

```table
가설 | 맞다면 보일 것
H1 TRIM 뒤 0 이 보장된다 | `Deterministic read ZEROs after TRIM` 줄이 있다 (실험 4 가 실제로 확인한다)
H2 Secure Erase 를 할 수 있다 | `supported`, `not enabled`, `not frozen` (frozen 이면 실험 14 에서 절전 → 깨우기로 푼다)
H3 오래된 데이터 때문에 자가 진단이 예상보다 오래 걸린다 | 실제 시간 > 권장 시간. 실험 3 뒤 (새 데이터) 다시 하면 짧아진다
H4 '믿을 수 없게 됨' 의 흔적이 로그에 있다 | 오류 로그에 항목이 있거나, 자가 진단이 `read failure` 로 끝난다
```

H3 의 비교를 위해, **실험 3 (드라이브 전체를 새로 씀) 이 끝난 뒤** `sudo ./lab.sh selftest long` 을 한 번 더 한다. 같은 드라이브가 같은 일을 하는데 데이터의 나이만 다르다.

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-features | tail -1)
$ less $D/hdparm-I.txt
$ grep -E "seconds|Completed|failure" ~/Ryu/old_ssd_results/*-selftest-long/{meta.txt,selftest-log.txt}
```

Claude 가 두 결과 폴더를 읽어 '지원하는 기능' 표와 '두 번의 자가 진단 시간' 을 이 페이지의 결과에 붙인다. 뒤 실험들 (4, 7, 14) 이 기대하는 기능이 없으면 그 실험의 절차를 바꾼다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
