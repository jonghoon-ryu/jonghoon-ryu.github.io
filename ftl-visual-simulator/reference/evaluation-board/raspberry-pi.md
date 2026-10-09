---
layout: default
title: 라즈베리파이로 FTL 테스트하기 — 조사와 의견
permalink: /ftl-visual-simulator/reference/evaluation-board/raspberry-pi/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 라즈베리파이로 FTL 테스트하기 — 조사와 의견

"라즈베리파이(Pi)로 FTL 을 시험해 볼 수 있을까?" 에 대해 2026-10-04 에 조사하고 정리한 의견이다. 결론부터 말하면 **Pi 는 FTL 이 사는 하드웨어로는 부족하지만, SPI NAND 칩을 붙여 원시 NAND 를 만져 보는 연습장으로는 쓸 만하다.**

<div class="check">
<b>이 글의 신뢰도</b> — 웹 검색으로 확인한 사실(링크 표시)과, 일반 지식이나 추론으로 쓴 부분(<b>추정</b>)을 구분해 적었다. 칩 가격 · 재고 · 특정 보드의 호환성은 조사하지 않았다.
</div>


<div style="margin-top: 60px;"></div>

## 1. 결론

<svg viewBox="0 0 980 400" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="라즈베리파이의 역할 비교"><defs><marker id="apiroles" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="apiroless" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">라즈베리파이로 할 수 있는 네 가지 — 그리고 FTL 시험에 쓸모 있는 정도</text><rect x="15" y="45" width="228" height="190" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="129.0" y="122.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">A. NVMe SSD 의 호스트</text><text x="129.0" y="141.75" font-size="11" fill="#4d5656" text-anchor="middle">Pi 5 + M.2 HAT+</text><text x="129.0" y="156.75" font-size="11" fill="#4d5656" text-anchor="middle">SSD 안에 이미 FTL 이 있다</text><text x="129.0" y="171.75" font-size="11" fill="#4d5656" text-anchor="middle">→ 내 FTL 을 시험 못 함</text><rect x="49" y="250" width="160" height="36" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="129.0" y="273.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓸모 낮음</text><rect x="256" y="45" width="228" height="190" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="370.0" y="115.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">B. SPI NAND 를 직접 만짐</text><text x="370.0" y="134.25" font-size="11" fill="#4d5656" text-anchor="middle">Pi + SPI NAND 칩</text><text x="370.0" y="149.25" font-size="11" fill="#4d5656" text-anchor="middle">원시(raw) NAND 에 내 FTL 을</text><text x="370.0" y="164.25" font-size="11" fill="#4d5656" text-anchor="middle">올려 시험</text><text x="370.0" y="179.25" font-size="11" fill="#4d5656" text-anchor="middle">→ 학습용으로 적합</text><rect x="290" y="250" width="160" height="36" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="370.0" y="273.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓸모 높음</text><rect x="497" y="45" width="228" height="190" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="611.0" y="122.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">C. 병렬 NAND 를 GPIO 로</text><text x="611.0" y="141.75" font-size="11" fill="#4d5656" text-anchor="middle">타이밍을 소프트웨어로 만들어야</text><text x="611.0" y="156.75" font-size="11" fill="#4d5656" text-anchor="middle">함 · 조사에서 사례를 못 찾음</text><text x="611.0" y="171.75" font-size="11" fill="#4d5656" text-anchor="middle">→ 비현실적</text><rect x="531" y="250" width="160" height="36" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="611.0" y="273.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓸모 낮음</text><rect x="738" y="45" width="228" height="190" rx="8" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="852.0" y="122.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">D. FPGA·OpenSSD 의 호스트</text><text x="852.0" y="141.75" font-size="11" fill="#4d5656" text-anchor="middle">Pi 가 NVMe/제어 쪽을 맡음</text><text x="852.0" y="156.75" font-size="11" fill="#4d5656" text-anchor="middle">진짜 FTL 은 보드 쪽</text><text x="852.0" y="171.75" font-size="11" fill="#4d5656" text-anchor="middle">→ 보조 역할</text><rect x="772" y="250" width="160" height="36" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="852.0" y="273.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">보조</text><rect x="15" y="310" width="950" height="70" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="334.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">의견</text><text x="490.0" y="354.25" font-size="11.5" fill="#4d5656" text-anchor="middle">Pi 는 &quot;FTL 이 사는 보드&quot; 가 아니라 &quot;FTL 을 올려 볼 수 있는 리눅스 작업대&quot; 에 가깝다.</text><text x="490.0" y="369.75" font-size="11.5" fill="#4d5656" text-anchor="middle">진짜 FTL 연구용 하드웨어(병렬 NAND · 채널 · 플레인)는 Cosmos+ 같은 보드가 필요하고, Pi 는 그 전 단계의 싼 연습장이다.</text></svg>

| 질문 | 답 |
|---|---|
| Pi 로 FTL 을 시험할 수 있나? | **가능하다, 단 SPI NAND 한정.** 원시 NAND 에 내가 만든 FTL 을 올릴 수 있다 |
| 연구용 하드웨어로 충분한가? | **아니다.** 채널 · 다이 · 플레인 병렬성이 없고 용량이 작다 |
| 지금 단계에서 살 가치가 있나? | **싸게 시작하는 연습장으로는 있다.** 진짜 목표(Cosmos+ 급)를 대신하지는 못한다 |
| 먼저 할 일은? | 하드웨어보다 **HAL 뒤에 가짜 NAND 를 붙인 호스트 테스트**(이전 [논의](/ftl-visual-simulator/reference/evaluation-board/board-recommendation/)) |

**A 에 대해** — Pi 5 의 [M.2 HAT+](https://www.canakit.com/raspberry-pi-m2-hat.html)는 단일 레인 PCIe 2.0 으로 NVMe SSD 를 붙이는 부품이다(공식은 Gen 2 기준). 하지만 NVMe SSD 는 컨트롤러와 FTL 이 이미 들어 있는 완제품이어서, 내 FTL 이 아니라 **그 SSD 의 FTL 을 호스트에서 바라보는** 구성이 된다. FTL 이 만든 차이(예: 쓰기 증폭)를 측정해 볼 수는 있지만 FTL 을 바꿀 수는 없다.


<div style="margin-top: 60px;"></div>

## 2. Pi 에는 무엇이 없나

- **NAND 컨트롤러가 없다.** Pi 의 SoC 에는 NAND 인터페이스(ONFI 타이밍 · ECC 엔진)가 없다. 그래서 일반 NAND 칩을 직접 연결하려면 GPIO 로 타이밍을 만들어야 하는데, 이를 다룬 사례를 이번 조사에서 찾지 못했다(Pico 의 PIO 는 [사용자 정의 인터페이스를 만드는 장치](https://blues.com/blog/raspberry-pi-pico-pio/)지만, 그것으로 병렬 NAND 를 구동한 사례도 찾지 못했다). **추정**: 속도와 안정성 모두 비현실적이다.
- **그래서 현실적 접점은 SPI NAND 다.** SPI NAND 는 NAND 의 구조(page · block · erase)는 그대로 두고 인터페이스만 SPI 로 단순화한 칩이다. Pi 의 SPI 로 직접 말할 수 있다.
- **SPI 속도에 한계가 있다.** BCM2835 계열 SPI 컨트롤러는 시스템 클럭의 절반이 이론상 최대(250 MHz → 125 MHz)이고, 실제로는 연결한 장치와 배선이 정한다([LinuxCNC hm2_rpspi 문서](https://www.linuxcnc.org/docs/devel/html/ru/man/man9/hm2_rpspi.9.html)). 클럭은 단순한 분주기라 값이 이산적이다([Pi 커널 이슈](https://github.com/raspberrypi/linux/issues/2165)). 또한 이번 조사에서 **quad SPI 지원을 확인하지 못했다**. **추정**: 단일 비트 SPI 라서 대용량 NAND 의 성능 시험에는 맞지 않는다.


<div style="margin-top: 60px;"></div>

## 3. 현실적인 구성 — Pi + SPI NAND

<svg viewBox="0 0 980 385" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="Pi 위의 FTL 시험 구조"><defs><marker id="apistack" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="apistacks" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Pi + SPI NAND 에서 FTL 을 시험하는 구조</text><rect x="150" y="45" width="680" height="48" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="490.0" y="66.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">시험 프로그램</text><text x="490.0" y="85.75" font-size="11" fill="#4d5656" text-anchor="middle">임의/순차 쓰기, 카운터 출력 (WAF · GC 횟수 · erase 분포)</text><line x1="490" y1="93" x2="490" y2="103" stroke="#7f8c8d" stroke-width="2" marker-end="url(#apistack)"/><rect x="150" y="103" width="680" height="48" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="124.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">내 FTL (또는 Dhara)</text><text x="490.0" y="143.75" font-size="11" fill="#4d5656" text-anchor="middle">매핑 · GC · 마모 평준화 — 사용자 공간 C/C++</text><line x1="490" y1="151" x2="490" y2="161" stroke="#7f8c8d" stroke-width="2" marker-end="url(#apistack)"/><rect x="150" y="161" width="680" height="48" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="490.0" y="182.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND HAL</text><text x="490.0" y="201.75" font-size="11" fill="#4d5656" text-anchor="middle">read_page · program_page · erase_block · is_bad · mark_bad</text><line x1="490" y1="209" x2="490" y2="219" stroke="#7f8c8d" stroke-width="2" marker-end="url(#apistack)"/><rect x="150" y="219" width="680" height="48" rx="8" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="490.0" y="240.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">spidev (/dev/spidevX.Y)</text><text x="490.0" y="259.75" font-size="11" fill="#4d5656" text-anchor="middle">리눅스 SPI 드라이버를 통해 칩 명령을 그대로 전송</text><line x1="490" y1="267" x2="490" y2="277" stroke="#7f8c8d" stroke-width="2" marker-end="url(#apistack)"/><rect x="150" y="277" width="680" height="48" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="490.0" y="298.75" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">SPI NAND 칩</text><text x="490.0" y="317.75" font-size="11" fill="#4d5656" text-anchor="middle">page / block 구조 · 칩 안에서 program/erase 시간을 처리</text><text x="920" y="70" font-size="11" fill="#7f8c8d" text-anchor="end">Pi (리눅스)</text><rect x="140" y="38" width="700" height="226" rx="10" fill="none" stroke="#bbb" stroke-dasharray="6 4"/><text x="165" y="360" font-size="11" font-style="italic" fill="#7d3c98" text-anchor="start">※ 같은 HAL 뒤에 메모리 배열(가짜 NAND)을 붙이면 Pi 없이 PC 에서도 같은 FTL 코드를 돌릴 수 있다</text></svg>

### 접근 방법 두 가지

| 방법 | 설명 | 장단점 |
|---|---|---|
| **spidev 로 직접** | `spi_bcm2835` 모듈이 `/dev/spidev*` 를 만든다([설명](https://blog.ittraining.com.tw/2023/10/)). 사용자 공간 프로그램이 칩 명령을 그대로 보낸다 | 내 FTL 이 모든 것을 직접 본다. 학습용으로 가장 좋다 |
| **리눅스 MTD · spi-nand** | 커널의 SPI NAND 프레임워크가 칩을 MTD 장치로 노출한다. W25N · GD5F 같은 칩 지원 패치가 있다([예](https://lkml.iu.edu/hypermail/linux/kernel/1501.0/03745.html)) | UBI/UBIFS 같은 기존 소프트웨어를 쓸 수 있으나, 내 FTL 은 MTD 위에 얹어야 한다. Pi 용 device tree 설정이 필요하다(**추정**, 확인 안 함) |

### 칩 후보 — W25N 계열

조사에서 확인된 것: W25N 은 NuttX 가 지원하는 SPI NAND 계열이고, 지원되는 변종은 1 Gbit(128 MB)이다([NuttX 문서](https://nuttx.apache.org/docs/latest/components/drivers/special/mtd/devices/w25n.html)). 128 MB 면 FTL 의 매핑·GC 동작을 눈으로 보기에는 충분하지만 성능 시험에는 작다.

**추정 (확인 안 함)**: 대부분의 SPI NAND 는 칩 안에 ECC 가 들어 있어서 원시 비트 오류를 볼 수 없고, 출고 시 불량 block 이 있다. 불량 block 처리는 FTL 이 해야 한다 — 아래 Dhara 의 `nand.h` 도 `is_bad` / `mark_bad` 를 요구한다.


<div style="margin-top: 60px;"></div>

## 4. 올려 볼 FTL — Dhara 로 시작

[Dhara](https://www.github.com/dlbeer/dhara) 는 자원이 작은 시스템용 NAND FTL 라이브러리다. 확인된 특징은 다음과 같다.

- 완벽한 마모 평준화(어떤 두 block 의 erase 횟수 차이가 최대 1), **trim**, 전원 차단에도 안전한 원자적 쓰기를 제공한다.
- `map.h` 가 위쪽 인터페이스(init · read · write · trim · sync · gc …)이고, **`nand.h` 를 직접 구현해야** 한다(`is_bad` · `mark_bad` 포함).
- ESP 칩용 SPI NAND 드라이버가 Dhara 를 쓰는 등 마이크로컨트롤러에서 실제로 쓰인다([Espressif 컴포넌트](https://components.espressif.com/components/espressif/spi_nand_flash/versions/1.4.3/readme)).

그래서 순서는 이렇게 잡는 것이 좋다고 본다.

1. **Dhara 를 먼저 올려서 동작을 본다** — "실제로 동작하는 FTL" 을 하나 알고 시작하면, 내 FTL 의 결과를 비교할 기준이 생긴다.
2. 같은 HAL 위에 **내 FTL**(page-level 매핑 + 이 프로젝트에서 본 GC 정책)을 올린다.
3. 시뮬레이터에서 보던 지표(WAF · GC 횟수 · erase 분포)를 **카운터로 직접 세어** 비교한다. 같은 워크로드를 [MQSim 시뮬레이터](/ftl-visual-simulator/run-simulator/)에서도 돌려 보면 "모델과 실제" 의 차이가 보인다.


<div style="margin-top: 60px;"></div>

## 5. Pi 없이 먼저 — 소프트웨어 NAND

하드웨어를 사기 전에 해 볼 수 있는 것이 있다.

- **리눅스 `nandsim`** 은 호스트 RAM 안에 가상 NAND 장치를 만드는 커널 모듈이다. UBI 구현을 시험하는 데 쓰이고, 전원 차단 에뮬레이션 계층까지 추가됐다([메일링 리스트](https://lkml.iu.edu/hypermail/linux/kernel/1509.3/01099.html)). 자체 FTL 을 `/dev/mtd0` 위에서 시험해 본 개발자 사례도 있다([토론](https://lists.infradead.org/pipermail/linux-mtd/2014-April/053419.html)). Pi OS 커널에서 쓸 수 있는지는 **확인하지 않았다.**
- **HAL 뒤에 배열을 붙인 가짜 NAND** — 더 단순하고, PC 에서 FTL 로직을 먼저 다듬을 수 있다. [이전 논의](/ftl-visual-simulator/reference/evaluation-board/board-recommendation/)에서 권했던 방식 그대로다.
- 이 프로젝트의 **시뮬레이터와 MQSim** 은 이미 같은 일을 하는 도구다.


<div style="margin-top: 60px;"></div>

## 6. 한계 — Pi 로는 못 보는 것

| 보고 싶은 것 | Pi + SPI NAND |
|---|---|
| 채널 · 칩 · 다이 · 플레인 병렬성, Plane Allocation | **볼 수 없다** (칩 1개, 채널 1개) |
| 대용량에서의 GC 압력, steady state | 어렵다 (128 MB 급) |
| 실제 NVMe 요청·큐 | 없다 (SPI 는 단순 명령) |
| 원시 비트 오류 · ECC | 칩 안 ECC 에 가려질 가능성이 크다 (**추정**) |
| 매핑 · GC · 마모 평준화의 논리 | **볼 수 있다** — 이 부분이 Pi 의 가치다 |

반대로 이 한계가 **FTL 알고리즘 검증**이 목표라면 문제가 안 된다. 목표가 "실제 SSD 성능 측정" 이면 Pi 는 답이 아니다.


<div style="margin-top: 60px;"></div>

## 7. 다른 선택과 비교

| | Pi + SPI NAND | Pico (RP2040 등) + SPI NAND | Cosmos+ OpenSSD | 소프트웨어 NAND |
|---|---|---|---|---|
| 목적 | 리눅스 작업대 + 원시 NAND | 베어메탈 FTL 연습 | 실제 SSD 컨트롤러 연구 | 알고리즘 먼저 |
| 병렬성 | 없음 | 없음 | 있음 (4-way × 2 슬롯) | 모델링 가능 |
| 입문 난이도 | 낮음 | 중간 (직접 드라이버) | 높음 | 가장 낮음 |
| 구하기 | 쉬움 | 쉬움 | **어려움** ([이전 조사](/ftl-visual-simulator/reference/evaluation-board/board-recommendation/)) | 불필요 |
| 내 의견 | **연습장으로 추천** | Dhara 를 MCU 에서 보고 싶을 때 | 진짜 목표 | **가장 먼저** |

**추정**: Pico 계열은 PIO 로 quad SPI 같은 인터페이스를 직접 만들 수 있어 Pi 의 SPI 한계를 넘을 수 있지만, 이번 조사에서 그 구성의 사례를 찾지 못했다.


<div style="margin-top: 60px;"></div>

## 8. 내 의견과 제안

1. **하드웨어보다 HAL 을 먼저.** `read_page / program_page / erase_block / is_bad / mark_bad` 다섯 함수 뒤에 가짜 NAND 를 붙여서 PC 에서 FTL 로직을 먼저 만든다. 이 단계는 보드가 필요 없다.
2. **그다음 Pi + SPI NAND 로 같은 FTL 을 옮긴다.** 같은 HAL 이라 FTL 코드는 바뀌지 않는다. 처음으로 "진짜 NAND 의 불량 block 과 erase 시간" 을 만난다.
3. **연구 수준의 하드웨어가 필요해지면 Cosmos+ 등으로.** 그때는 1~2 단계에서 만든 FTL 과 HAL 을 가져가면 된다.
4. **분담**: HAL · 가짜 NAND · SPI 드라이버 · 시험 하네스 · 카운터는 제가 대부분 쓸 수 있다. 다만 실제 칩과의 bring-up(배선 · 칩 ID 읽기 · 불량 block 확인)은 직접 실행하고 결과를 알려 주셔야 한다. 칩 데이터시트를 주시면 명령 코드를 대조해서 쓰겠다.

### 아직 모르는 것

- Pi OS 커널에서 `nandsim` · `spi-nand` 를 바로 쓸 수 있는지
- Pi 5 / Pi 4 / Zero 사이의 SPI 차이
- SPI NAND 브레이크아웃 보드의 현재 가격과 재고
- Pico PIO 로 quad SPI NAND 를 구동한 사례


<div style="margin-top: 60px;"></div>

## 출처

- [LinuxCNC hm2_rpspi — Pi SPI 최대 클럭](https://www.linuxcnc.org/docs/devel/html/ru/man/man9/hm2_rpspi.9.html)
- [Raspberry Pi 커널 이슈 — SPI 클럭](https://github.com/raspberrypi/linux/issues/2165)
- [Pico PIO 소개 (Blues)](https://blues.com/blog/raspberry-pi-pico-pio/)
- [NuttX — W25N NAND Flash](https://nuttx.apache.org/docs/latest/components/drivers/special/mtd/devices/w25n.html)
- [Raw SPI Device Access (spidev)](https://blog.ittraining.com.tw/2023/10/)
- [mtd: spi-nand framework (LKML)](https://lkml.iu.edu/hypermail/linux/kernel/1501.0/03745.html)
- [Dhara — NAND flash translation layer](https://www.github.com/dlbeer/dhara)
- [Espressif spi_nand_flash (Dhara 사용 예)](https://components.espressif.com/components/espressif/spi_nand_flash/versions/1.4.3/readme)
- [nandsim 전원 차단 에뮬레이션 (LKML)](https://lkml.iu.edu/hypermail/linux/kernel/1509.3/01099.html)
- [FTL 시험을 NAND 시뮬레이터로 (linux-mtd)](https://lists.infradead.org/pipermail/linux-mtd/2014-April/053419.html)
- [Raspberry Pi M.2 HAT+ (Pi 5, PCIe Gen 2) — CanaKit](https://www.canakit.com/raspberry-pi-m2-hat.html)


<div style="margin-top: 60px;"></div>

## 관련 문서

- [Evaluation Board](/ftl-visual-simulator/reference/evaluation-board/) · [평가 보드 추천과 부트로더 역할 분담](/ftl-visual-simulator/reference/evaluation-board/board-recommendation/)
- [Dhara 를 비롯한 다른 SSD/FTL 도구 비교](/ftl-visual-simulator/reference/mqsim/)
