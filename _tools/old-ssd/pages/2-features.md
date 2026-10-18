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
줄 (예) | 뜻 | 이 정보를 쓰는 실험 (번호)
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

## 결과

<div class="result" markdown="1">
### 1단계 : `features`

2026.10.18 09:41, 결과 폴더 `20261018-094145-features`.

**ATA 기능** (`hdparm -I`, `hdparm -N -W -A -B`)

```table
보이는 것 | 뜻 | 이 정보를 쓰는 실험 (번호)
`Data Set Management TRIM supported (limit 8 blocks)` | TRIM 지원. 명령 하나에 범위 8개 블록 (블록 하나에 범위 64개) | 4
`Deterministic read ZEROs after TRIM` 줄 **없음** | 드라이브는 'TRIM 한 곳은 0' 을 약속하지 않는다 (커널은 `zeroaftertrim` 으로 0 이라고 믿는다) | 4
`Device encrypts all user data` | 항상 암호화하는 드라이브 (SED) | 14
Security : `supported` · `not enabled` · `not locked` · **`frozen`** · `supported: enhanced erase` · `2min … 8min` | Secure Erase 를 할 수 있지만 지금은 BIOS 가 잠갔다. 드라이브가 말하는 시간 : 보통 2분, enhanced 8분 | 14
`max sectors = 234441648/234441648, HPA is disabled` | 보이는 크기 = 진짜 크기. 숨긴 영역 없음 | 10
`write-caching = 1 (on)`, `look-ahead = 1 (on)` | 쓰기 캐시 켜짐, 미리 읽기 켜짐 | 7
`APM_level = not supported` | 전원 관리 (APM) 설정은 없다 : SSD 에서는 흔하다 | —
`Queue depth: 32`, `Native Command Queueing (NCQ)`, `Gen3 (6.0Gb/s)` | 명령 32개까지 한꺼번에, SATA 3 | 5
`Logical / Physical Sector size: 512 bytes` | 호스트에는 512 B 섹터로 보인다 (안쪽의 4 KiB 매핑 단위는 실험 6 이 찾는다) | 6
```

**SMART 로그**

```table
로그 | 내용 | 읽는 법
오류 로그 (`error`, `xerror`) | `No Errors Logged` | 드라이브가 기억하는 명령 오류가 하나도 없다 : 13년 동안, 그리고 오늘의 느린 읽기에서도
자가 진단 기록 (`selftest`) | `No self-tests have been logged` | 한 번도 자가 진단을 한 적이 없다 : 2단계가 첫 번째다
장치 통계 (`devstat`) | `not supported` | 이 드라이브에는 없다 (더 새 드라이브의 기능)
SATA 링크 (`sataphy`, 켠 뒤부터 센 값) | CRC · R_ERR 오류 모두 0. `PhyRdy → PhyNRdy` 31번, `COMRESET` 2번 | 링크 오류 없음. 31번은 오류가 아니라 링크가 쉬는 상태로 들어갔다 나온 횟수 (link power management), COMRESET 2번은 부팅 때의 초기화
로그 목록 (`directory`) | Samsung 전용 로그 `0xa1`, `0xce`, `0xde` 가 있다 | 내용은 공개되어 있지 않다 (펌웨어 내부 기록)
```

**온도 기록** (`scttemp`, 10분마다) : 이번 실험들 동안의 드라이브 온도가 그대로 남았다.

```table
시각 | 온도 | 그때 한 일
08:20 – 08:50 | 28 → 31 °C | 켠 뒤, 실험 0 (`check`)
09:00 – 09:10 | **38 – 40 °C** | 실험 1 파일별 측정 (느린 읽기가 계속됨)
09:20 | 33 °C | 쉬는 시간, 다시 읽기
09:30 | **38 °C** | 실험 1 드라이브 전체 지도
09:40 | 31 °C | 쉼
```

**읽기만 하는데도 7–9 °C 가 오른다.** 정상 SSD 의 읽기는 거의 열을 내지 않는다. 이 드라이브는 읽기 하나에 여러 번 다시 읽으므로 (read retry) 컨트롤러와 NAND 가 쉬지 않고 일한다. 실험 1 의 해석과 맞는 독립된 증거다.

**가설 확인 (1단계까지)**

```table
가설 | 결과
H1 TRIM 뒤 0 이 보장된다 | **아니다** (약속 줄이 없다). 실제로 0 이 나오는지는 실험 4
H2 Secure Erase 를 할 수 있다 | **할 수 있다, 단 지금은 frozen** : 실험 14 에서 절전 → 깨우기
H3 자가 진단이 예상보다 오래 걸린다 | 2단계 (`selftest long`) 에서 확인. 권장 시간 70분
H4 '믿을 수 없게 됨' 의 흔적이 로그에 있다 | **아니다** : 오류 로그 · 링크 오류 모두 0. 남은 흔적은 '느림' 과 '열' 뿐
```

### 2단계 : `selftest long`

2026.10.18 09:47 – 10:50, 결과 폴더 `20261018-094708-selftest-long`.

```
SMART Self-test log structure revision number 1
Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error
# 1  Extended offline    Completed without error       00%         2         -
```

```table
항목 | 값 | 읽는 법
결과 | `Completed without error`, `LBA_of_first_error -` | 드라이브가 스스로 전체를 검사했고, 읽지 못한 곳이 없다
드라이브가 말한 시간 | 70분 | `smartctl -c` 의 권장 대기 시간
실제 걸린 시간 | **3,758초 = 62.6분** | 말한 시간보다 **짧았다**
진행 | 10% 마다 약 7.7분 (8 · 16 · 23 · 31 · 39 · 47 · 54 · 62분) | 처음부터 끝까지 고르다 : 특별히 느린 구간이 없다
온도 | 31 → 39 °C | 자가 진단 동안 계속 일했다
SMART 앞뒤 | 5 · 179 · 181–183 · 187 · 195 · 199 모두 0 그대로 | 고치지 못한 오류 없음
`LifeTime(hours)` 2 | Power_On_Hours (10,375) 와 다르다 | 이 펌웨어가 이 칸에 무엇을 적는지는 알 수 없다 (켠 뒤의 시간으로 보인다 : 오늘 08:05 에 켰다)
```

**속도로 바꾸면** : 120 GB 를 62.6분에 다 읽었다면 약 **32 MB/s** 다. 실험 1 에서 호스트가 `O_DIRECT` 로 읽은 속도 (데이터가 있는 곳 약 9 MB/s) 의 3–4배다. 가능한 이유 :
- 자가 진단은 SATA 링크 · 커널 · 명령 대기 없이 드라이브 안에서 바로 읽는다
- 데이터가 없는 곳 (TRIM 된 곳, 파일 시스템의 빈 공간 약 9%) 은 NAND 를 읽지 않는다
- 자가 진단이 모든 페이지를 호스트 읽기와 같은 방식 (같은 다시 읽기 단계) 으로 읽는지는 공개되어 있지 않다

**가설 확인**

```table
가설 | 결과
H3 오래된 데이터 때문에 자가 진단이 오래 걸린다 | 드라이브가 말한 70분보다는 7분 짧았다. 그러나 **실험 3 에서 새 데이터로 다시 하니 9.5분** : 오래된 데이터의 자가 진단이 **6.6배** 길었다. 곧 **그렇다** ([실험 3 의 결과](/old-ssd-experiments/3-slc-cache/))
H4 '믿을 수 없게 됨' 의 흔적이 로그에 있다 | **아니다** : 자가 진단도 오류 없이 끝났다
```

**실험 2 정리** : 이 드라이브는 지원하는 기능 · 로그 · 자가 진단 모두 '건강' 하다고 말한다. 남은 이상은 실험 1 에서 잰 **아주 느린 읽기와 그때의 열** 뿐이다 : SMART 와 로그만 보면 이 드라이브의 문제를 알 수 없다는 것이 실험 0–2 의 결론이다.
</div>

@@NAV@@
