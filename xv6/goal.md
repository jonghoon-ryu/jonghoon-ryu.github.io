---
layout: default
title: xv6 목표
permalink: /xv6/goal/
---
<style>
table.plan-calendar {
  width: 100% !important;
  table-layout: fixed !important;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: break-word;
  word-break: break-word;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
</style>

# 목표

**xv6-riscv → xv6-x86_64 (C) → xv6-x86_64 (C++)**

**QEMU, VirtualBox, 그리고 실제 PC (베어본) 세 곳 모두에서 도는 C++ 판 xv6 를 만든다.**

MIT 의 xv6 는 QEMU 의 가상 기계에서만 돈다. 이 프로젝트는 그것을 64비트 x86 PC 로 옮기고, C++ 로 다시 써서, **요즘의 실제 PC 에서도 도는 운영체제** 로 만드는 것이 목표다.

<div style="margin-top: 60px;"></div>

## 최종 목표 : 세 곳 모두에서 도는 C++ xv6

완성된 모습 (`v1.0-cpp`) :

| | QEMU | VirtualBox | 실제 PC (베어본) |
|---|---|---|---|
| 부팅 (UEFI) | ✅ | ✅ | ✅ |
| 화면 콘솔과 키보드 | ✅ | ✅ | ✅ (USB 키보드) |
| 셸 (`$`) 과 사용자 프로그램 | ✅ | ✅ | ✅ |
| `usertests` 전체 통과 | ✅ | ✅ | ✅ |
| CPU 여러 개 | ✅ | ✅ | ✅ |

- **커널과 사용자 프로그램 모두 C++.** 원래 C 코드의 한 줄 한 줄이 어디로 갔는지 책 (xv6 RISC-V rev5) 과 대조할 수 있게
- **같은 `usb.img` 하나가 세 곳 모두에서** 부팅한다. 장치가 있는지는 실행 중에 알아본다
- **실제 PC 에서 안 되면 끝난 것이 아니다.** QEMU 와 VirtualBox 는 개발 도구다
- 지금 어디까지 왔는지는 [진행 현황](/xv6/plan/), 각 태그에서 코드가 어떻게 바뀌었는지는 [튜토리얼](/xv6/tutorial/)

<div style="margin-top: 100px;"></div>

## 출발점 : xv6 는 왜 RISC-V 로 갔고, 왜 QEMU 에서만 도나

### xv6 의 역사

| 해 | 일 |
|---|---|
| 1975 | Unix Version 6 (v6) : PDP-11 에서 도는 유닉스. 라이언스의 주석서로 운영체제 수업의 교재가 됨 |
| 2006 | MIT 가 v6 를 **x86 (32비트)** 용 ANSI C 로 다시 쓴 **xv6** 를 만듦 (6.828 수업). 저장소 [`mit-pdos/xv6-public`](https://github.com/mit-pdos/xv6-public) |
| 2019 | xv6 를 **RISC-V (64비트)** 로 옮기고, 새 수업 6.S081 (지금 6.1810) 과 새 실습을 만듦. 저장소 [`mit-pdos/xv6-riscv`](https://github.com/mit-pdos/xv6-riscv) |
| 지금 | x86 판은 더 이상 관리하지 않는다. xv6-public 의 README : *"we have stopped maintaining the x86 version of xv6, and switched our efforts to the RISC-V version"* |

### 왜 RISC-V 인가

저자들 (Russ Cox, Frans Kaashoek, Robert Morris) 이 이유를 따로 글로 남기지는 않았다 (찾아본 곳 : 두 저장소의 README, 책의 서문, 2019년 공개 때의 토론).
책은 xv6 를 *"implemented in ANSI C for a multi-core RISC-V"* 라고만 소개한다. 흔히 드는 이유는 **x86 의 오래된 짐** 이다 :
학생이 운영체제의 생각 (프로세스, 페이지 테이블, 트랩) 보다 x86 의 옛날 규칙과 씨름하는 시간이 길었다. RISC-V 는 2010년대에 새로 설계된, 작고 공개된 명령어 집합이다.

이 프로젝트의 1단계 (RISC-V → x86-64) 에서 **직접 겪은 차이** 가 그 이유를 잘 보여 준다. RISC-V 판에 없던 것을 x86-64 판에 새로 만들어야 했다 :

| 하는 일 | xv6-riscv | x86-64 에서 필요했던 것 |
|---|---|---|
| 부팅 | QEMU 가 커널을 메모리에 올리고 바로 뛰어 준다 (`-bios none -kernel`) | UEFI 로더 (`boot/loader.c`) 를 직접 작성. 옛 x86 판 xv6 는 16비트 real mode 에서 시작하는 부트 섹터 (`bootasm.S`) 였다 |
| 다른 CPU 깨우기 | 모든 CPU 가 같이 시작 | 16비트 real mode 에서 시작하는 코드 (`entryother.S`) 를 1MB 아래에 두고 신호를 보냄 |
| 트랩 | `stvec` 레지스터 하나에 주소 | IDT, GDT, TSS (세그먼트 시절의 표들). 사용자 ↔ 커널 전환에 두 IDT |
| 인터럽트 컨트롤러 | PLIC 가 정해진 주소 (`0x0c000000`) 에 | LAPIC, IOAPIC 를 ACPI 표 (MADT) 에서 찾아야 함 |
| CPU 번호 | `tp` 레지스터 | GS base MSR |

### 왜 QEMU 에서만 도나

xv6-riscv 는 **실제 컴퓨터가 아니라 QEMU 의 가상 기계 `virt` 를 위해** 쓰였다. 책이 그렇게 말한다 :

> *"Xv6 is written for the support hardware simulated by qemu's "-machine virt" option."*
>
> *"[the] assumption that there is physical RAM at address 0x80000000 … works with QEMU, but on real hardware it turns out to be a bad idea; real hardware places RAM and devices at unpredictable physical addresses"*

| xv6-riscv 가 가정하는 것 | QEMU `virt` | 실제 RISC-V 보드 |
|---|---|---|
| RAM 이 `0x80000000` 에 | ✅ | 보드마다 다름 |
| 시리얼 (16550 UART) 이 `0x10000000` 에 | ✅ | 보드마다 다름 |
| 디스크가 virtio (`0x10001000`) | ✅ (가상 장치) | 실제 하드웨어에는 virtio 가 없다 |
| 키보드, 화면 | 없음 : 시리얼 콘솔 하나 | — |

그래서 공식 xv6 는 실제 기계에서 돌지 않는다 (몇몇 사람이 특정 RISC-V 보드용으로 따로 옮긴 판이 있을 뿐이다).
옛 x86 판도 실제로는 QEMU 와 Bochs 에서 썼다 : 디스크는 IDE, 키보드는 PS/2, 화면은 VGA 문자 모드, 부팅은 레거시 BIOS. 요즘 PC (UEFI 만, PS/2 없음, NVMe/USB) 에는 거의 남아 있지 않은 장치들이다.

**이 프로젝트는 여기서 한 걸음 더 간다** : UEFI 로더, GOP 화면, ACPI, USB 키보드 (xHCI) 처럼 **요즘 실제 PC 에 있는 장치** 를 쓴다.

**출처** : [MIT 6.828 의 xv6 소개 (2012)](https://pdos.csail.mit.edu/6.828/2012/xv6.html) : *"developed in the summer of 2006 … running on multiprocessor Intel x86 machines"* · [xv6-public README](https://github.com/mit-pdos/xv6-public) · [xv6-riscv README](https://github.com/mit-pdos/xv6-riscv) ·
[*xv6: a simple, Unix-like teaching operating system*, RISC-V rev5](https://pdos.csail.mit.edu/6.1810/2025/xv6/book-riscv-rev5.pdf) (서문, 1장, 3장) ·
xv6-riscv 의 `kernel/memlayout.h`, `Makefile` (`QEMUOPTS = -machine virt -bios none -kernel …`)

<div style="margin-top: 100px;"></div>

## 원칙

- **언제나 부팅되는 상태 유지** : 어느 단계에서 멈춰도 커널은 부팅된다
- **책과 대조 가능하게** : 파일 이름과 함수 이름은 원본 xv6 를 따른다
- **freestanding C++20** : 예외, RTTI, 표준 라이브러리 없음
  - `#define` 상수 → `constexpr`, 매크로 → `inline` 함수, 플래그 → `enum class`
  - `acquire`/`release` → RAII `LockGuard`
  - 멤버 함수는 자연스러운 곳에만
- **어셈블리 (`.S`) 는 그대로** 둔다
