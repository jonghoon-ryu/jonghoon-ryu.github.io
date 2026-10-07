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
MIT 의 xv6 는 QEMU 의 가상 기계에서만 돈다. 이 프로젝트는 그것을 실제 PC 에서도 도는 운영체제로 만드는 것이 목표다.

<div style="margin-top: 60px;"></div>

## 우리 목표 : 세 곳 모두에서

| 판 | QEMU | VirtualBox | 실제 PC (베어본) |
|---|---|---|---|
| xv6-riscv (MIT 원본) | ✅ `-machine virt` 에서만 | ✗ (RISC-V 가 아님) | ✗ (공식 지원 없음) |
| xv6-x86_64 C 판 (`v0.2-x86_64-c`) | ✅ 셸, `usertests` 통과 | ✅ 셸, `usertests` 통과 | 시험 안 함. 키보드가 PS/2 뿐이라 베어본에서는 입력 불가 |
| xv6-x86_64 C++ 판, 지금 (`step-10`) | ✅ 부팅, 화면, 키보드 | ✅ 부팅, 화면, 키보드 | ✅ **부팅, 화면, USB 키보드** (2026.10.7) |
| **최종 목표 (`v1.0-cpp`)** | 셸, `usertests` 통과 | 셸, `usertests` 통과 | **셸, `usertests` 통과** |

- **실제 PC 에서 안 되면 끝난 것이 아니다.** QEMU 와 VirtualBox 는 개발 도구다. 단계마다 그 단계의 `usb.img` 를 베어본에서 부팅해 본다
- 같은 `usb.img` 하나가 세 곳 모두에서 부팅한다. 장치가 있는지는 실행 중에 알아본다 (예 : USB 컨트롤러가 없으면 PS/2 키보드)
- 커널과 사용자 프로그램 모두 C++ 로. 다시 셸 (`$`) 이 뜨고 `usertests` 가 전부 통과해야 끝

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
2026.10.7 에 C++ 판 (Step 10) 이 베어본에서 부팅하고 USB 키보드 입력을 받았다.

**출처** : [MIT 6.828 의 xv6 소개 (2012)](https://pdos.csail.mit.edu/6.828/2012/xv6.html) : *"developed in the summer of 2006 … running on multiprocessor Intel x86 machines"* · [xv6-public README](https://github.com/mit-pdos/xv6-public) · [xv6-riscv README](https://github.com/mit-pdos/xv6-riscv) ·
[*xv6: a simple, Unix-like teaching operating system*, RISC-V rev5](https://pdos.csail.mit.edu/6.1810/2025/xv6/book-riscv-rev5.pdf) (서문, 1장, 3장) ·
xv6-riscv 의 `kernel/memlayout.h`, `Makefile` (`QEMUOPTS = -machine virt -bios none -kernel …`)

<div style="margin-top: 100px;"></div>

## 1단계 : RISC-V → x86-64 포팅 (완료)

xv6-riscv 를 64비트 x86 PC 에서 돌도록 옮겼다. 언어는 C 그대로.

- 저장소 : [github.com/jonghoon-ryu/xv6-x86_64](https://github.com/jonghoon-ryu/xv6-x86_64), `main` 브랜치
- QEMU (CPU 1개·4개) 와 VirtualBox 에서 `usertests` 전체 통과 (실제 PC 는 시험하지 않았다)

C 버전에는 태그가 두 개 있다. 이름의 `x86_64-c` 는 "x86-64 판, C 로 작성" 이라는 뜻이다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:22%"><col style="width:78%"></colgroup>
  <thead><tr><th>태그</th><th>내용</th></tr></thead>
  <tbody>
    <tr><td><a href="https://github.com/jonghoon-ryu/xv6-x86_64/tree/v0.1-x86_64-c"><code>v0.1-x86_64-c</code></a><br>2026.9.27</td><td><b>첫 C 판.</b> UEFI 부팅, CPU 1–4개, 셸까지 뜨고 <code>usertests</code> 전체 통과.<br>입출력은 <b>시리얼 포트만</b> : QEMU 는 터미널로 쓰면 되지만, VirtualBox 는 창이 비어 있고 <code>socat</code> 으로 시리얼에 붙어야 셸을 쓸 수 있다</td></tr>
    <tr><td><a href="https://github.com/jonghoon-ryu/xv6-x86_64/tree/v0.2-x86_64-c"><code>v0.2-x86_64-c</code></a><br>현재 <code>main</code></td><td><b>v0.1 + 화면 콘솔 + PS/2 키보드</b> (<code>fbcons.c</code>, <code>font.h</code>, <code>kbd.c</code>). VirtualBox 창에 글자가 나오고 바로 쳐서 셸을 쓸 수 있다.<br><b>C++ 변환의 각 단계는 이 판과 비교한다</b> (Step 4–5 에서 옮기는 화면·키보드 코드가 여기에만 있다). 이 판을 둘러보는 <a href="https://github.com/jonghoon-ryu/xv6-x86_64/blob/main/docs/tutorial/step00.md">Step 0 튜토리얼</a> 포함</td></tr>
  </tbody>
</table>
</div>

```
v0.1 ──(+ 화면 콘솔, 키보드)──▶ v0.2 ──(C++ 로 한 단계씩)──▶ step-01 … step-05 … v1.0-cpp
```

모든 태그 설명 : [docs/tags.md](https://github.com/jonghoon-ryu/xv6-x86_64/blob/main/docs/tags.md)

바뀐 곳은 기계에 의존하는 부분이다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:30%"><col style="width:35%"><col style="width:35%"></colgroup>
  <thead><tr><th>개념</th><th>xv6-riscv</th><th>xv6-x86_64</th></tr></thead>
  <tbody>
    <tr><td>부팅</td><td>QEMU <code>-kernel</code>, <code>entry.S</code>, <code>start.c</code></td><td>UEFI 로더 (<code>boot/loader.c</code>) → <code>entry.S</code></td></tr>
    <tr><td>페이지 테이블</td><td>Sv39 (3단계), <code>satp</code></td><td>4단계, <code>CR3</code></td></tr>
    <tr><td>트랩</td><td><code>stvec</code>, <code>ecall</code></td><td>IDT, GDT/TSS, <code>int $64</code></td></tr>
    <tr><td>인터럽트 / 타이머</td><td>PLIC, <code>stimecmp</code></td><td>IOAPIC, LAPIC 타이머 (ACPI 로 찾음)</td></tr>
    <tr><td>CPU 번호</td><td><code>tp</code> 레지스터</td><td>GS base</td></tr>
    <tr><td>디스크</td><td>virtio</td><td>램디스크 (UEFI 로더가 fs.img 를 메모리에 올림)</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 2단계 : C → C++ 번역 (진행 중)

이번에는 완성된 C 코드를 그대로 두고 고쳐 나가는 대신, **처음부터 다시 쌓는다.**

1. **부팅 코드만 남기고 전부 지운다.** (`cpp` 브랜치)
   - 남긴 것 : UEFI 로더, `entry.S`, 링커 스크립트, 헤더 몇 개
   - 새로 쓴 것 : `start.cpp`, `main.cpp` — 시리얼에 한 줄 찍고, 화면을 칠하고, "xv6" 글자를 그린 뒤 멈춘다
2. **작은 C++ 코드를 한 단계씩 더한다.**
   - 한 단계 = 원래 C 코드의 한 부분 (예 : 콘솔, 메모리 할당, 페이지 테이블, 타이머 …) 을 C++ 로 옮겨 되살리기
   - 매 단계마다 빌드하고 QEMU · VirtualBox, **그리고 실제 PC (베어본)** 에서 부팅되는 것을 확인한다
   - C 버전 (`main` 브랜치, 태그 `v0.2-x86_64-c`) 이 그대로 남아 있어서 언제든 나란히 비교할 수 있다

지금 상태 (Step 10, 태그 `step-10`, 2026.10.7) — **실제 PC (베어본) 에서** C++ 커널이 부팅하고, 자기 USB 드라이버 (xHCI) 로 USB 키보드 입력을 받는다.
그 PC 에는 PS/2 컨트롤러가 없어서, 원래 계획에 없던 USB 키보드 드라이버를 Step 6–10 으로 넣었다 :

![C++ 커널 Step 10 : 실제 PC 에서 USB 키보드로 입력](/assets/image/xv6-realpc-usb-keyboard.jpg)

VirtualBox 에서의 Step 5 (화면 콘솔과 PS/2 키보드) :

![C++ 커널 Step 5 : 화면 콘솔과 키보드 입력](/assets/image/xv6-cpp-step05.png)

<div style="margin-top: 100px;"></div>

## 원칙

- **언제나 부팅되는 상태 유지** : 어느 단계에서 멈춰도 커널은 부팅된다
- **책과 대조 가능하게** : 파일 이름과 함수 이름은 원본 xv6 를 따른다
- **freestanding C++20** : 예외, RTTI, 표준 라이브러리 없음
  - `#define` 상수 → `constexpr`, 매크로 → `inline` 함수, 플래그 → `enum class`
  - `acquire`/`release` → RAII `LockGuard`
  - 멤버 함수는 자연스러운 곳에만
- **어셈블리 (`.S`) 는 그대로** 둔다
