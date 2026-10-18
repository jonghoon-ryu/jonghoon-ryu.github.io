---
layout: default
title: 헌 SSD 로 하는 실험
permalink: /old-ssd-experiments/
---
@@STYLE@@

# 헌 SSD 로 하는 실험

**아무도 원하지 않을 헌 SSD 를, 버리기 전에 할 수 있는 실험을 다 해 보는 데 쓴다.** (2026.10.16 시작)

이 드라이브는 팔 수도 없고, 실험이 끝나면 버린다. 그래서 아끼는 드라이브로는 할 수 없는 실험 : 데이터를 지우고, 닳게 하고, 전원을 갑자기 끊고, 마지막에는 열어 보는 것까지 모두 한다.
실험은 SSD 안에서 일어나는 일 (FTL : 매핑, GC, SLC 캐시, 마모, 오류 정정, 전원 차단 복구) 을 밖에서 재는 것으로 골랐다. [FTL Visual Simulator](/ftl-visual-simulator/) 와 겹치는 실험은 그 페이지에 '덤' 으로 비교를 적었다.

이 페이지는 전체 그림만 담는다. 실험마다 따로 튜토리얼 페이지가 있다 : 목표, 배경, 가설, 절차, 결과 읽는 법.
결과가 나오면 각 페이지의 **결과** 절에 그래프와 분석을 붙인다.

## 실험할 드라이브

```table
항목 | 값
모델 | Samsung SSD 840 EVO 120GB (2013년 출시 제품군)
시리얼 · 펌웨어 | `S1D6NSAFB40389K` · `EXT0CB6Q`
용량 | 120,034,123,776 바이트 (234,441,648 섹터 × 512 B)
NAND | TLC (셀 하나에 3비트), SLC 버퍼 TurboWrite 약 3 GB (알려진 값)
지금 상태 | 옛 Windows 디스크, 91% 차 있음, 파일 날짜 2018–2024
지난 이력 | 2024.12 쯤 마지막으로 쓴 뒤 **1년 넘게 전원 없이** 보관. 2026.10.17 다시 연결 : Ryu 가 파일 몇 개를 읽고, 몇 개를 새로 씀. 원래 Windows 부팅 드라이브였고, 가끔 블루 스크린이 떠서 새로 PC 를 조립했고, 이 SSD 는 그 뒤로 쓰지 않고 두었다. 그러다 심심해서 이 SSD 로 실험해 보기로 했다
연결 | 메인보드 SATA (`ata5`, SATA 3) : TRIM 됨 (`DISC-MAX 2G`)
```

1년 넘게 전원 없이 있었다는 것이 실험 1 을 특별하게 만든다 : 켜져 있어야만 할 수 있는 펌웨어의 '오래된 데이터 다시 쓰기' 가 그동안 한 번도 없었다. 그래서 **실험 1 은 가장 먼저, 되도록 빨리** 한다.

## 실험 순서

@@FIG overview_map@@

```table
# | 실험 | 무엇을 보나 | 지우나? | 시간 (대략)
0 | [준비](/old-ssd-experiments/0-setup/) | 드라이브 · 도구 · SMART 기준값 | 아니오 | 30분
1 | [오래된 데이터 읽기](/old-ssd-experiments/1-old-data/) | 1년 넘게 전원 없이 둔 데이터의 읽기 속도, 한 번 읽히면 다시 쓰이나 | **아니오 (지우기 전에 한 번뿐)** | 1–2시간
2 | [기능 · 자가 진단](/old-ssd-experiments/2-features/) | ATA 기능, 로그, SMART 자가 진단의 시간 | 아니오 | 1시간
3 | [SLC 캐시](/old-ssd-experiments/3-slc-cache/) | TurboWrite 버퍼 크기, TLC 쓰기 속도, 회복 | 예 | 1시간
4 | [TRIM 과 매핑 없는 읽기](/old-ssd-experiments/4-trim/) | 매핑 없는 LBA 읽기는 NAND 를 안 거친다 | 예 | 30분
5 | [성능 지도](/old-ssd-experiments/5-perf-map/) | 블록 크기 × 큐 깊이, 데이터 내용 (압축?) | 예 | 1.5시간
6 | [쓰기 크기 · 정렬](/old-ssd-experiments/6-write-size/) | 512 B 쓰기, 어긋난 4 KiB : 매핑 단위 | 예 | 40분
7 | [쓰기 캐시 · FLUSH](/old-ssd-experiments/7-flush/) | '다 썼다' 는 대답이 언제 오나 | 예 | 15분
8 | [Write cliff](/old-ssd-experiments/8-write-cliff/) | 빈 블록이 바닥나며 GC 시작 : FOB → steady state | 예 | 밤새 (4–8시간)
9 | [쉬는 동안 GC](/old-ssd-experiments/9-idle-gc/) | 쉬면 빈 블록을 미리 만드나 | 예 | 1.5시간
10 | [Over-provisioning](/old-ssd-experiments/10-over-provisioning/) | 덜 쓰면 steady state 가 몇 배 빨라지나 | 예 | 밤새 × 2–4
11 | [뜨거운 데이터](/old-ssd-experiments/11-hot-cold/) | 쓰기가 일부에 몰리면 WAF 가 낮아지나 | 예 | 밤새 × 1–2
12 | [WAF (SMART)](/old-ssd-experiments/12-waf/) | 드라이브가 센 값으로 WAF 추정 : 순차 vs 랜덤 | 예 | 2시간 + 앞의 기록
13 | [읽기 · 쓰기 간섭](/old-ssd-experiments/13-interference/) | 쓰기가 돌 때 읽기의 꼬리 지연 | 예 | 40분
14 | [Secure Erase](/old-ssd-experiments/14-secure-erase/) | 드라이브가 스스로 지우는 시간, FOB 로 돌아오나 | 예 | 1시간
15 | [Read disturb](/old-ssd-experiments/15-read-disturb/) | 같은 곳을 수억 번 읽으면 | 예 | 밤새
16 | [Retention](/old-ssd-experiments/16-retention/) | 전원 없이 몇 주 둔 데이터 (통제된 실험 1) | 예 | 2–4주 기다림
17 | [전원 차단](/old-ssd-experiments/17-power-loss/) | FLUSH 한 데이터는 전원이 끊겨도 남나 | 예 (망가질 수 있음) | 1–2시간
18 | [끝까지 쓰기](/old-ssd-experiments/18-endurance/) | 수명이 다할 때 SMART 와 컨트롤러의 행동 | 예 (소모) | 몇 주–몇 달
19 | [열어 보기](/old-ssd-experiments/19-teardown/) | 컨트롤러 · DRAM · NAND 패키지 | — | 1시간
```

연결은 실험 17 만 USB 어댑터 (전원을 끊기 쉽게), 나머지는 모두 메인보드 SATA 다.

처음 시작한다면 먼저 [SSD 를 다루는 Linux 명령](/old-ssd-experiments/linux-commands/) 과 [fio 사용법](/old-ssd-experiments/fio/) 을 읽는다. 실험에 나오는 명령 (`lsblk`, `smartctl`, `hdparm`, `blkdiscard`, `fio` …) 이 거기 설명되어 있다.

## 더 해 볼 수 있는 것

시간이 남으면 (각각 실험 하나 크기) : 파일 시스템별 WAF (ext4 · f2fs · btrfs 로 같은 작업을 하고 SMART 로 비교), 온도와 속도 (SMART 190 을 보며 오래 쓰기 : 열 때문에 느려지나), 순차와 랜덤이 섞인 '실제 같은' 부하 (fio 의 `rwmixread`), 비어 있는 드라이브와 꽉 찬 드라이브의 TRIM 처리 시간.

## 스크립트

모든 실험은 스크립트 하나 [`lab.sh`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/old-ssd-experiments/scripts) 로 돌린다. 블로그 저장소의 `old-ssd-experiments/scripts/` 에 있다.

```table
파일 | 하는 일
`lab.sh` | 실험마다 하나씩 있는 명령 (`check`, `oldfiles`, `features`, `slc`, `perfmap`, `cliff`, `mixed`, `secerase`, `pl-write` …). 드라이브를 **시리얼로** 찾고, 지우기 전에 다섯 가지를 확인한다. `./lab.sh` 만 치면 전체 목록
`readscan.py` | 드라이브 전체를 읽으며 구간마다 속도, 가장 느린 읽기, 0 으로만 된 비율을 기록 (읽기만 한다)
`fileage.py` | 파일마다 '언제 썼나', '다시 연결한 뒤 읽혔나', '얼마나 빨리 읽히나' (읽기만 한다)
`fiosum.py` | fio 의 JSON 결과들을 한 표 (`summary.csv`) 로
`plcheck.py` | 전원 차단 실험 : 번호 붙은 기록 쓰기와 확인
`plot.py` | 결과 폴더의 로그로 그래프 그리기
`smartdiff.py` | 실험 앞뒤 SMART 비교, 177 · 241 로 WAF 추정
```

결과는 `~/Ryu/old_ssd_results/<날짜>-<실험>/` 에 쌓인다. Claude 가 같은 컴퓨터에서 바로 읽고 분석한다.
모든 명령은 실제 드라이브에 쓰기 전에, 파일을 가짜 장치로 쓰는 시험 모드 (`LAB_TESTDEV`) 로 시간과 크기를 줄여 한 번씩 돌려 보았다.

## 진행 상황

```table
실험 | 상태
0 준비 | **끝** (2026.10.18) : SMART 오류 0, 평생 WAF ≈ 1.4, 177 = 117 (수명의 약 10%), Security frozen. [결과](/old-ssd-experiments/0-setup/)
1 오래된 데이터 | **끝** (2026.10.18) : 데이터가 있는 곳은 약 9 MB/s, 빈 곳은 400–520 MB/s. 나이와 상관없이 모두 느리고, 오류는 없다. 블루 스크린은 이 SSD 탓이 아닐 가능성이 크다. [결과](/old-ssd-experiments/1-old-data/)
2 기능 · 자가 진단 | `features` **끝** : 오류 로그 · 링크 오류 0, Security frozen, 읽기만 해도 31 → 40 °C. `selftest long` 다음. [결과](/old-ssd-experiments/2-features/)
3 – 19 | 아직
```

<div class="warn" markdown="1">
**안전.** 실험 3–18 은 드라이브 전체를 지운다. `lab.sh` 는 시리얼 `S1D6NSAFB40389K` 인 드라이브에만 쓰고, 시스템 디스크 · 마운트된 디스크 · (TRIM 이 필요한 실험에서) TRIM 이 안 되는 연결이면 멈추며, 지우기 전에 시리얼 끝 5자리를 직접 입력하게 한다.
`lab.sh` 를 거치지 않고 `dd`, `blkdiscard`, `fio` 를 직접 쓸 때는 [Linux 명령 페이지의 위험한 명령 절](/old-ssd-experiments/linux-commands/#danger) 을 먼저 읽는다.
</div>

@@NAV@@
