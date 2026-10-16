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

### 질문 : 그런데 왜 하필 RISC-V 로 갔을까? (2026.10.16)

**Q.** RISC-V 로 된 PC 는 거의 없으니, 사람들이 자기 PC 에서 xv6 를 돌리려면 x86 판밖에 없다. 같은 이미지가 실제 PC 에서도 돈다면, 사람들은 베어본에서 바로 돌려 보고 싶어 할 것이고, 그러면 더 손에 잡히게 이해할 수 있다. 그런데 MIT 는 왜 x86 을 두고 RISC-V 로 옮겼을까?

**A.** 먼저 전제 하나를 바로잡아야 한다. **MIT 의 x86 판도 요즘 PC 에서는 돌지 않았다.** x86-64 판은 원래 없었고, `xv6-public` 은 **32비트 x86** 이며, 지금의 RISC-V 판처럼 **QEMU 용** 이었다. 요즘 PC 에는 없는 장치를 가정했다 :

| MIT 의 x86 판이 필요로 한 것 | 지금의 베어본 |
|---|---|
| BIOS 부팅 (512바이트 부트 섹터) | UEFI 만 (레거시 BIOS 모드, CSM 없음) |
| PS/2 키보드 | 없음, USB 만 |
| IDE 디스크 | 없음, NVMe / SATA (AHCI) 만 |
| CGA 문자 화면 (`0xB8000`) | 없음, UEFI frame buffer 만 |
| MP 표 (CPU 찾기) | 대신 ACPI 표 |

"이미지 하나가 세 곳에서 돈다" 는 것은 **이 프로젝트의 판** 에서만 맞는 말이다. UEFI 로더, frame buffer 콘솔, ACPI, USB 키보드 (Step 6–10) 를 따로 만들었기 때문이다 ([세 대의 기계, 하나의 프로그램](/xv6/tutorial/code-explanation-step-10/#11-one-program-three-machines)).

그러면 MIT 는 왜 RISC-V 로 갔나. 공식 설명은 위 README 의 한 줄뿐이고, 아래는 **흔히 드는 이유** 다 :

1. **x86 은 40년 묵은 짐을 진다.** 운영체제의 생각을 배우기 전에 16비트 real mode 부팅, A20, 세그먼트, GDT, TSS, 16 → 32 → 64비트 모드 전환을 먼저 넘어야 한다. 운영체제와 상관없는 데 몇 주가 간다. RISC-V 에는 그런 것이 없다 : 트랩은 `stvec` 하나, 페이지 테이블은 단순한 Sv39, 부팅은 몇 줄
2. **수업의 목표는 생각이지 하드웨어가 아니다.** 6.1810 은 프로세스, 가상 메모리, 락, 파일 시스템을 가르친다. 실제 기계에서 도는 것은 목표가 아니다. 모두가 같은 QEMU 를 쓰니 실습을 자동으로 채점할 수 있고, 누구도 메인보드마다 다른 문제에 막히지 않는다
3. **다른 수업과 맞는다.** MIT 의 컴퓨터 구조 수업 (6.004, 지금 6.191) 도 RISC-V 를 쓴다. 학생들은 이미 그 명령어 집합을 안다
4. **RISC-V 는 공개되어 있고, 단순하게 설계되었다.** 버클리에서 교육용으로도 쓰려고 만들었고, 명세가 짧고 무료다

**잃은 것 : 질문이 맞게 짚었다.** RISC-V 보드 (VisionFive 2, Milk-V 등) 는 있지만 xv6-riscv 는 거기서도 돌지 않는다. RAM 과 장치 주소를 QEMU `virt` 에 맞춰 박아 두었기 때문이다 (위 표). 그래서 지금의 xv6 는 **누구도 자기 기계에서 부팅해 볼 수 없다.** MIT 는 가르치기 깔끔한 명령어 집합을 얻고, "내 PC 에서 돈다" 는 경험을 내준 것이다.

**이 프로젝트는 그 경험을 되찾는다.** 커널은 xv6-riscv 의 구조를 따르므로 rev5 책과 나란히 읽을 수 있고, x86-64 의 짐은 로더와 몇 개 파일에 가둔다. 실제 기계에서 돌려 보면 더 구체적으로 이해하게 된다는 점은 Step 6–10 이 보여 주었다 : 없는 PS/2 컨트롤러, 아직 펌웨어가 쥐고 있던 USB 컨트롤러, 끝없이 반복되던 USB 장치 설정 버그는 QEMU 에서는 결코 배우지 못했을 것들이다.

<div style="margin-top: 100px;"></div>

## 원칙

- **언제나 부팅되는 상태 유지** : 어느 단계에서 멈춰도 커널은 부팅된다
- **책과 대조 가능하게** : 파일 이름과 함수 이름은 원본 xv6 를 따른다
- **freestanding C++20** : 예외, RTTI, 표준 라이브러리 없음
  - `#define` 상수 → `constexpr`, 매크로 → `inline` 함수, 플래그 → `enum class`
  - `acquire`/`release` → RAII `LockGuard`
  - 멤버 함수는 자연스러운 곳에만
- **어셈블리 (`.S`) 는 그대로** 둔다
