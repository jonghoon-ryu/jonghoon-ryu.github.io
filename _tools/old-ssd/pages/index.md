---
layout: default
title: 헌 SSD 로 하는 실험
permalink: /old-ssd-experiments/
---
@@STYLE@@

# 헌 SSD 로 하는 실험

**믿을 수 없게 된 헌 SSD 를 버리는 대신, SSD 안에서 일어나는 일 (FTL) 을 직접 눈으로 보는 실험에 쓴다.** (2026.10.16 시작)

헌 드라이브는 이런 실험에 오히려 딱 맞다. 배울 것이 가장 많은 실험은 **데이터를 지우고 드라이브를 닳게 하는** 것이라, 아끼는 드라이브로는 할 수 없기 때문이다.
실험은 [FTL Visual Simulator](/ftl-visual-simulator/) 에서 모델로 만든 것 (GC, WAF, OP, SLC 캐시, 매핑 없는 읽기) 을 **실제 드라이브에서 확인** 하는 쪽으로 골랐다.

이 페이지는 전체 그림만 담는다. 실험마다 따로 튜토리얼 페이지가 있다 : 목표, 배경, 예상 결과, 절차, 결과 읽는 법.
결과가 나오면 각 페이지의 **결과** 절에 그래프와 분석을 붙인다.

## 실험할 드라이브

```table
항목 | 값
모델 | Samsung SSD 840 EVO 120GB (2013년 출시 제품군)
시리얼 · 펌웨어 | `S1D6NSAFB40389K` · `EXT0CB6Q`
용량 | 120,034,123,776 바이트 (234,441,648 섹터 × 512 B)
NAND | TLC (셀 하나에 3비트), SLC 버퍼 TurboWrite 약 3 GB (알려진 값)
지금 상태 | 옛 Windows 디스크, 91% 차 있음, 파일 날짜 2018–2024
지금 연결 | 메인보드 SATA (`ata5`, 2026.10.17 부터) : TRIM 됨 (`DISC-MAX 2G`). 그 전에는 USB 어댑터라 TRIM 이 통과하지 않았다
```

## 실험 순서

@@FIG overview_map@@

```table
# | 실험 | 무엇을 보나 | 지우나? | 연결 | 시간 (대략)
0 | [준비](/old-ssd-experiments/0-setup/) | 드라이브 · 도구 · SMART 기준값 | 아니오 | SATA | 30분
1 | [오래된 데이터 읽기](/old-ssd-experiments/1-old-data/) | 몇 년 된 데이터의 읽기 속도 : read retry | **아니오 (지우기 전에 한 번뿐)** | SATA | 1–2시간
2 | [SLC 캐시](/old-ssd-experiments/2-slc-cache/) | TurboWrite 버퍼 크기, TLC 쓰기 속도 | 예 | SATA | 30분 + 회복 측정
3 | [TRIM 과 매핑 없는 읽기](/old-ssd-experiments/3-trim/) | 매핑 없는 LBA 읽기는 NAND 를 안 거친다 | 예 | SATA | 30분
4 | [Write cliff](/old-ssd-experiments/4-write-cliff/) | 빈 블록이 바닥나며 GC 시작 : FOB → steady state | 예 | SATA | 밤새 (4–8시간)
5 | [Over-provisioning](/old-ssd-experiments/5-over-provisioning/) | 앞쪽 80% 만 쓰면 steady state 가 몇 배 빨라지나 | 예 | SATA | 밤새
6 | [WAF (SMART)](/old-ssd-experiments/6-waf/) | 드라이브가 센 값으로 WAF 추정 : 순차 vs 랜덤 | 예 | SATA | 2시간 + 실험 4–5 의 기록
7 | [Retention](/old-ssd-experiments/7-retention/) | 전원 없이 몇 주 둔 데이터 | 예 | SATA | 2–4주 기다림
8 | [끝까지 쓰기](/old-ssd-experiments/8-endurance/) | 수명이 다할 때 SMART 와 컨트롤러의 행동 | 예 (소모) | SATA | 몇 주–몇 달
9 | [열어 보기](/old-ssd-experiments/9-teardown/) | 컨트롤러 · DRAM · NAND 패키지 | — | — | 1시간
```

처음 시작한다면 먼저 [SSD 를 다루는 Linux 명령](/old-ssd-experiments/linux-commands/) 을 읽는다. 실험에 나오는 명령 (`lsblk`, `smartctl`, `fio`, `blkdiscard` …) 이 모두 거기 설명되어 있다.

## 스크립트

모든 실험은 스크립트 하나 [`lab.sh`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/old-ssd-experiments/scripts) 로 돌린다. 블로그 저장소의 `old-ssd-experiments/scripts/` 에 있다.

```table
파일 | 하는 일
`lab.sh` | 실험마다 하나씩 있는 명령 (`check`, `scan`, `slc`, `cliff` …). 드라이브를 **시리얼로** 찾고, 지우기 전에 다섯 가지를 확인한다
`readscan.py` | 드라이브 전체를 읽으며 구간마다 속도, 가장 느린 읽기, 0 으로만 된 비율을 기록 (읽기만 한다)
`fileage.py` | 파일마다 '언제 썼나' 와 '얼마나 빨리 읽히나' (읽기만 한다)
`plot.py` | 결과 폴더의 로그로 그래프 그리기
`smartdiff.py` | 실험 앞뒤 SMART 비교, 177 · 241 로 WAF 추정
```

결과는 `~/Ryu/old_ssd_results/<날짜>-<실험>/` 에 쌓인다. Claude 가 같은 컴퓨터에서 바로 읽고 분석한다.

## 진행 상황

```table
실험 | 상태
0 준비 | SMART 출력 기다리는 중 (`sudo apt install smartmontools fio` 다음 `sudo ./lab.sh check`)
1 – 9 | 아직
```

<div class="warn" markdown="1">
**안전.** 실험 2–8 은 드라이브 전체를 지운다. `lab.sh` 는 시리얼 `S1D6NSAFB40389K` 인 드라이브에만 쓰고, 시스템 디스크 · 마운트된 디스크 · TRIM 이 안 되는 연결이면 멈추며, 지우기 전에 시리얼 끝 5자리를 직접 입력하게 한다.
`lab.sh` 를 거치지 않고 `dd`, `blkdiscard`, `fio` 를 직접 쓸 때는 [Linux 명령 페이지의 위험한 명령 절](/old-ssd-experiments/linux-commands/#danger) 을 먼저 읽는다.
</div>

@@NAV@@
