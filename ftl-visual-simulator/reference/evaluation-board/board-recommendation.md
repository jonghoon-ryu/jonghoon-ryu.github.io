---
layout: default
title: 평가 보드 추천과 부트로더 역할 분담
permalink: /ftl-visual-simulator/reference/evaluation-board/board-recommendation/
---
# 평가 보드 추천과 부트로더 역할 분담

2026-10-04 에 Claude 와 나눈 논의 기록. 질문은 두 가지였다.

1. 평가 보드를 사면 부트로더 코드는 Claude 가 준비해 주고, 나는 실제 FTL 코드에만 집중할 수 있는가?
2. FTL 테스트용으로 어떤 평가 보드를 추천하는가?

<div style="margin-top: 60px;"></div>

## 1. 부트로더는 누가 준비하나

**대체로 가능하지만, 어느 보드를 사느냐에 따라 달라진다.**

### Claude 가 잘 할 수 있는 것

- 스타트업 코드, 링커 스크립트, 벡터 테이블, 클럭/DRAM/UART 초기화, "부팅 → 시리얼 출력 → `main()` 실행" 최소 뼈대
- NAND/플래시 드라이버 계층 (커맨드 시퀀스, ONFI, ECC 훅) 과 HAL. FTL 은 보드를 모르고 `read_page / program_page / erase_block` 만 본다
- 빌드 환경 (Makefile 또는 CMake, 크로스 툴체인, 플래시/디버그 스크립트), RAM 으로 만든 가짜 NAND 에 FTL 을 붙여 호스트에서 돌리는 테스트 하네스

### Claude 가 할 수 없는 것

- 실제 보드에서 코드를 실행해 볼 수 없다. 사용자가 실행해서 UART 출력이나 fault 덤프를 알려 주고, 같이 반복해서 고쳐야 한다. 클럭 설정 오류, DRAM 타이밍, 핀 먹스 같은 bring-up 버그는 이 왕복이 필요해서 시간이 든다.
- 특정 칩의 레지스터 주소와 초기화 순서를 기억에 의존해 쓰면 틀릴 수 있다. 생성한 코드는 벤더의 레퍼런스 매뉴얼이나 SDK 와 대조해야 하므로, 해당 자료를 줘야 정확해진다.

<div style="margin-top: 60px;"></div>

## 2. 보드 후보

보드를 고르는 일이 "누가 부트로더를 쓰느냐" 보다 훨씬 중요하다.

| 후보 | 장점 | 단점 |
|------|------|------|
| **Cosmos+ OpenSSD** (Hanyang Univ. ENC Lab) | SSD 컨트롤러 연구용으로 만든 플랫폼. 실제 NAND 와 실제 타이밍. 벤더(연구실)가 부팅/플래시 드라이버/펌웨어를 제공하고 [오픈 소스 저장소](https://github.com/openssd/openssd) 가 있음. FTL 연구에 가장 가깝다 | **구하기 어렵다** (아래 참고) |
| **SPI-NAND 칩 + MCU 보드** (예: STM32 Nucleo 계열 + SPI-NAND 브레이크아웃) | 싸고 bring-up 이 쉽다. 컨트롤러가 FTL 을 숨기지 않아서 원시(raw) NAND 의 배드 블록, ECC, erase 제약을 직접 다룬다. 학습용으로 적합 | 용량이 작고 병렬성(채널/웨이) 이 없어서 성능/GC 병렬성 실험은 못 한다 |
| **FPGA 보드 + NAND 도터보드** 직접 구성 | 구성을 마음대로 할 수 있다 | NAND 컨트롤러 IP 부터 만들어야 해서 FTL 이전에 일이 너무 많다 |
| **SD / eMMC / 일반 SSD 가 붙은 보드** | 쉽다 | 장치 안의 컨트롤러가 이미 자체 FTL 을 돌려서 내 FTL 을 시험하는 의미가 없다 |

위 표의 SPI-NAND + MCU 구성은 Claude 의 제안이며, 구체적인 부품 선정과 가격은 아직 조사하지 않았다.

### Cosmos+ OpenSSD 를 구하기 어려운 점

- 사양: XC7Z045 Zynq-7000 FPGA (Cortex-A9 듀얼 코어 1GHz), 1GB DDR3, SO-DIMM NAND 슬롯 2개 (슬롯당 4-way). 출처: [Technion PSL 의 플랫폼 소개](https://psl.technion.ac.il/?p=1591)
- 문의처는 openssd@enc.hanyang.ac.kr 이다. 다만 [coreboot 메일링 리스트의 글](https://mail.coreboot.org/pipermail/coreboot/2017-April/083918.html) 에 따르면 구매 문의에 답을 받지 못한 연구자가 있었다고 한다.
- 현재 판매 여부와 가격은 확인하지 못했다. 구매하기 전에 직접 문의해서 확인해야 한다.

<div style="margin-top: 60px;"></div>

## 3. 권장 방향

1. **FTL 은 이식 가능한 C/C++ 로 쓰고, 보드 접근은 얇은 HAL 뒤에 둔다.** 같은 FTL 코드가 (a) 시각화 시뮬레이터, (b) 가짜 NAND 를 붙인 호스트 테스트, (c) 실제 보드에서 돌게 한다. 그러면 보드는 맨 마지막 단계가 되고, 부트로더는 작고 교체 가능한 부품이 된다.
2. **벤더가 부트/플래시 드라이버를 제공하는 보드를 고른다.** Cosmos+ OpenSSD 가 구해지면 그것이 1순위이고, 그 경우 Claude 는 접착 코드만 쓰면 된다.
3. **Cosmos+ 를 못 구하면** SPI-NAND + MCU 구성으로 raw NAND 의 현실 (배드 블록, ECC, erase 단위) 을 먼저 경험한다. 병렬성/성능 실험은 MQSim 과 시각화 시뮬레이터에서 한다.
4. 그러면 사용자는 매핑, GC, 마모 평준화에 거의 모든 시간을 쓸 수 있고, 그 부분의 코드와 HAL, 테스트는 Claude 가 대부분 작성할 수 있다.

<div style="margin-top: 60px;"></div>

## 열린 질문

- 구체적으로 염두에 둔 보드나 칩이 있는지 (있으면 부트 경로 중 이미 제공되는 부분과 직접 써야 하는 부분을 구분할 수 있다)
- Cosmos+ OpenSSD 구매 가능 여부 (연구실에 직접 문의)
- 목표가 "FTL 알고리즘 검증" 인지 "실제 SSD 성능 측정" 인지. 전자는 SPI-NAND 구성으로도 충분하다.

<div style="margin-top: 60px;"></div>

## 관련 문서

- [Evaluation Board](/ftl-visual-simulator/reference/evaluation-board/)
- [FTL Visual Simulator](/ftl-visual-simulator/)
