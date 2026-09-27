---
layout: default
title: xv6 x86-64 + C++ 1년 계획
permalink: /learning-cs/os/study-plan/
---
<style>
.progress-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  color: #555;
}
.progress-bar-track {
  flex: 1;
  max-width: 280px;
  height: 6px;
  border-radius: 4px;
  background: #e2e2e2;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  width: 0%;
  background: #3a7d44;
  transition: width 0.2s ease;
}
.session-check {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #777;
  cursor: pointer;
  user-select: none;
  margin: 0.2rem 0 0.6rem;
}
.session-check input {
  cursor: pointer;
}
.session.done h3 {
  color: #999;
  text-decoration: line-through;
  text-decoration-color: #bbb;
}
.session.done {
  opacity: 0.6;
}
.session {
  margin-top: 70px;
  padding-top: 32px;
  border-top: 1px solid #ddd;
}
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

# xv6 를 x86-64 와 C++ 로 다시 쓰기 — 1년 계획

**2026년 11월 8일 (일) 시작 · 52주 · 매주 일요일 3시간**

주말 6시간을 반씩 나눈다: **토요일 3시간 = [계산 이론 & Gödel](/learning-cs/computation-theory/study-plan/)**, **일요일 3시간 = 이 계획**.

<div style="margin-top: 100px;"></div>

## 목표

1. 지금도 관리되고 있는 **xv6-riscv** 를 **x86-64** 로 포팅한다 (C 그대로)
2. 포팅된 xv6 를 **C++ 로 한 파일씩 번역**한다
3. **QEMU, VirtualBox, 실제 PC (UEFI 전용)** 세 곳에서 모두 동작시킨다

1년 동안 천천히: **매주 Claude 가 코드를 쓰고, Ryu 는 코드와 책을 함께 읽으며 리뷰**한다.

**왜 x86 판 xv6 (xv6-public) 가 아니라 xv6-riscv 에서 출발하나?**
- xv6-riscv 는 MIT 6.1810 수업과 함께 지금도 계속 수정된다. x86 판은 2024년 이후 멈췄다
- 책도 RISC-V 판 (rev5) 이 최신이고 더 잘 정리되어 있다
- xv6-riscv 는 이미 **64비트**라서 x86-64 로 바로 옮길 수 있다. 32비트를 거쳤다가 64비트로 다시 옮기는 수고가 없다

**얼마나 바뀌나?** 커널 약 6,500줄 중 기계 의존 부분은 **최대 약 2,200줄 (1/3)**. 파일 시스템, 로그, 파이프, 사용자 프로그램 등 나머지는 거의 그대로다.

<div style="margin-top: 100px;"></div>

## 역할 분담

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:20%"><col style="width:80%"></colgroup>
  <thead><tr><th>누가</th><th>할 일</th></tr></thead>
  <tbody>
    <tr><td>🤖 Claude<br>(주중)</td><td>그 주 분량의 포팅 또는 C++ 번역 · 빌드 · QEMU (Week 14 부터 VirtualBox 도) 에서 부팅과 <code>usertests</code> 확인 · 로컬 커밋 · 리뷰 노트 <code>docs/review/weekNN.md</code> 작성 (원본 ↔ 새 코드 대응표, 설계 결정, 봐야 할 곳)</td></tr>
    <tr><td>👤 Ryu<br>(일요일 3h)</td><td>① 리뷰 노트를 보고 원본과 새 코드를 나란히 읽기 (~1.5h)<br>② 같은 내용의 xv6 책 장 읽기 (~1.5h)<br>③ 질문·수정 요청 → 승인하면 GitHub 에 push</td></tr>
  </tbody>
</table>
</div>

- 시작 방법: 주중에 Claude 에게 **"xv6 Week N 진행해"** 라고 말하면 된다
- **push 는 Ryu 의 리뷰와 승인 후에만** 한다 (코드 저장소 규칙)

<div style="margin-top: 100px;"></div>

## 자료

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:25%"><col style="width:75%"></colgroup>
  <thead><tr><th>역할</th><th>자료</th></tr></thead>
  <tbody>
    <tr><td>원본 코드</td><td><a href="https://github.com/mit-pdos/xv6-riscv">mit-pdos/xv6-riscv</a> (MIT 라이선스)</td></tr>
    <tr><td>책</td><td><a href="https://pdos.csail.mit.edu/6.1810/2025/xv6/book-riscv-rev5.pdf"><em>xv6: a simple, Unix-like teaching operating system</em>, RISC-V rev5</a> (무료 PDF)</td></tr>
    <tr><td>원본 소스 인쇄본</td><td><a href="https://pdos.csail.mit.edu/6.1810/2025/xv6/xv6-src-booklet-rev5.pdf">xv6-src-booklet-rev5.pdf</a> (줄 번호가 붙은 전체 소스)</td></tr>
    <tr><td>x86-64 참고</td><td><a href="https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html">Intel SDM</a> Vol.3 (시스템 프로그래밍) · <a href="https://wiki.osdev.org/">OSDev Wiki</a></td></tr>
    <tr><td>Phase C 참고</td><td><a href="https://github.com/uchan-nos/mikanos">MikanOS</a> (C++ 로 쓰인 UEFI 로더와 xHCI USB 드라이버)</td></tr>
    <tr><td>새 저장소</td><td><code>github.com/jonghoon-ryu/xv6-x86_64</code> (Week 1 에 공개 저장소로 생성)</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## RISC-V ↔ x86-64 대응

Phase A 에서 바뀌는 곳은 거의 이 표가 전부다. 책은 왼쪽을 설명하고, 리뷰할 코드는 오른쪽이다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:34%"><col style="width:33%"><col style="width:33%"></colgroup>
  <thead><tr><th>개념</th><th>xv6-riscv</th><th>xv6-x86_64</th></tr></thead>
  <tbody>
    <tr><td>부팅</td><td>QEMU <code>-kernel</code>, <code>entry.S</code>, <code>start.c</code> (M-mode → S-mode)</td><td>UEFI 로더 → 커널 진입 (이미 64비트 롱 모드)</td></tr>
    <tr><td>페이지 테이블</td><td>Sv39 (3단계), <code>satp</code></td><td>4단계, <code>CR3</code></td></tr>
    <tr><td>트랩 진입</td><td><code>stvec</code>, <code>kernelvec.S</code></td><td>IDT, GDT/TSS</td></tr>
    <tr><td>시스템 콜</td><td><code>ecall</code>, <code>trampoline.S</code></td><td><code>syscall</code>/<code>sysret</code>, <code>swapgs</code>, 트램펄린 (KPTI 구조)</td></tr>
    <tr><td>트랩 원인</td><td><code>scause</code>, <code>stval</code>, <code>sepc</code></td><td>벡터 번호, 에러 코드, <code>CR2</code>, <code>RIP</code></td></tr>
    <tr><td>인터럽트 컨트롤러</td><td>PLIC</td><td>IOAPIC (ACPI MADT 로 찾음)</td></tr>
    <tr><td>타이머</td><td><code>stimecmp</code></td><td>LAPIC 타이머</td></tr>
    <tr><td>CPU 번호</td><td><code>tp</code> 레지스터</td><td>GS base</td></tr>
    <tr><td>원자 연산</td><td><code>amoswap</code></td><td><code>xchg</code></td></tr>
    <tr><td>시리얼</td><td>UART (메모리 매핑)</td><td>16550 (I/O 포트)</td></tr>
    <tr><td>디스크</td><td>virtio-mmio</td><td>램디스크 (UEFI 로더가 이미지를 메모리에 올림)</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 원칙

- **매주 동작하는 상태 유지:** 어느 주에 멈춰도 커널은 부팅되고 `usertests` 를 통과한다
- **책과 대조 가능하게:** 함수 이름과 파일 구조는 원본을 따른다
- **포팅은 기계 의존 부분만:** 기계 독립 코드는 최대한 손대지 않는다
- **원본 설계 유지:** 커널/사용자 페이지 테이블 분리와 트램펄린 구조를 x86-64 에서도 그대로 쓴다
- **처음부터 UEFI 부팅, ACPI, 램디스크:** 그래야 QEMU · VirtualBox · 실제 PC 가 같은 코드로 돈다
- **C++ 번역 (Phase B):** freestanding C++20 (예외·RTTI·표준 라이브러리 없음). `#define` → `constexpr`, `acquire`/`release` → RAII `LockGuard`, 필요한 곳에만 멤버 함수. 어셈블리는 그대로. 호스트 도구 `mkfs` 는 일반 C++17

<div style="margin-top: 100px;"></div>

## 전체 로드맵

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:34%"><col style="width:28%"><col style="width:38%"></colgroup>
  <thead><tr><th>단계</th><th>기간</th><th>내용</th></tr></thead>
  <tbody>
      <tr><td>Phase A · xv6-riscv → x86-64 포팅 (C)</td><td>Week 1–14<br>2026.11.8 ~ 2027.2.7</td><td>UEFI 로더, 4단계 페이징, 트랩, syscall, ACPI, 램디스크</td></tr>
      <tr><td>Phase B · C → C++ 번역</td><td>Week 15–40<br>2027.2.14 ~ 2027.8.8</td><td>책 장 순서대로 파일 하나씩</td></tr>
      <tr><td>Phase C · 실제 PC</td><td>Week 41–52<br>2027.8.15 ~ 2027.10.31</td><td>프레임버퍼, PCI, xHCI USB 키보드, 실제 부팅</td></tr>
  </tbody>
</table>
</div>

**위험한 구간:**
- Phase A 는 참고할 기존 포팅이 없다. 매주 `usertests` 로 확인하는 것이 안전장치다
- Phase C 의 xHCI USB 드라이버 (Week 43–46) 가 1년 중 가장 어렵다
- 실제 PC 에서는 램디스크라서 파일 변경이 재부팅 후 사라진다. 영구 저장 (NVMe/AHCI) 은 2년차 목표

<div style="margin-top: 100px;"></div>

## 진도

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 52</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Phase A · xv6-riscv → x86-64 포팅 (C)

*Week 1–14 · 2026.11.8 ~ 2027.2.7 · UEFI 로더, 4단계 페이징, 트랩, syscall, ACPI, 램디스크*

<div class="session" data-session="1" markdown="1">

### Week 1 · 2026.11.8 (일) — 저장소와 빌드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- **🤖 Claude (주중):** `xv6-x86_64` 저장소 생성 (xv6-riscv 의 git 이력 위에 포팅 커밋을 쌓음) · x86-64 크로스 빌드 Makefile · 기계 의존 파일 목록과 RISC-V ↔ x86-64 대응표 작성
- **👤 Ryu (일요일 3h):** 책 **Ch.1** Operating system interfaces · 원본 xv6-riscv 를 QEMU (riscv) 에서 직접 띄워 `ls`, `cat`, 파이프 써 보기
- 💡 원칙: 포팅 중에도 **기계 독립 코드 (fs, log, pipe, 사용자 프로그램 등) 는 최대한 손대지 않는다**

</div>

<div class="session" data-session="2" markdown="1">

### Week 2 · 2026.11.15 (일) — UEFI 로더

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- **🤖 Claude (주중):** C 로 작은 UEFI 로더 작성 (clang + lld-link, edk2 없이): 커널 ELF 와 파일 시스템 이미지를 메모리에 올리고, 메모리 맵 · GOP 프레임버퍼 · ACPI RSDP 를 커널에 넘긴 뒤 `ExitBootServices`
- **👤 Ryu (일요일 3h):** 책 **Ch.2** Operating system organization (2.6 xv6 시작 과정) · UEFI 부팅 흐름 공부 · QEMU + OVMF 에서 로더 동작 확인
- 💡 처음부터 UEFI 로 부팅하면 QEMU, VirtualBox, 실제 PC 가 **같은 부팅 경로**를 쓴다

</div>

<div class="session" data-session="3" markdown="1">

### Week 3 · 2026.11.22 (일) — 커널 진입: GDT, 시리얼, printf

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- **🤖 Claude (주중):** `entry.S`/`start.c` 대체: 커널 진입, GDT/TSS 설정, CPU 별 데이터 (GS base) · `uart.c` 를 16550 I/O 포트 방식으로 · `printf` 동작
- **👤 Ryu (일요일 3h):** RISC-V 의 machine mode → supervisor mode 전환이 x86-64 에서는 무엇에 해당하는지 대응표로 정리
- 🎯 **마일스톤:** x86-64 커널이 시리얼 콘솔에 글자를 찍는다

</div>

<div class="session" data-session="4" markdown="1">

### Week 4 · 2026.11.29 (일) — 페이지 테이블: Sv39 → 4단계

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- **🤖 Claude (주중):** `riscv.h` → `x86.h` · `vm.c` 의 `walk`, `mappages`, `kvmmake` 를 x86-64 4단계 페이지 테이블로 · `kalloc` 을 UEFI 메모리 맵 기반으로
- **👤 Ryu (일요일 3h):** 책 **Ch.3** Page tables 3.1–3.5 · Sv39 (3단계) 와 x86-64 (4단계) 주소 변환을 손으로 계산해 비교

</div>

<div class="session" data-session="5" markdown="1">

### Week 5 · 2026.12.6 (일) — 주소 공간 설계: 트램펄린

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- **🤖 Claude (주중):** xv6-riscv 처럼 **커널 페이지 테이블과 사용자 페이지 테이블을 분리** · 트램펄린 페이지에 IDT/GDT/TSS/진입 코드를 매핑 (리눅스 KPTI 와 같은 구조)
- **👤 Ryu (일요일 3h):** 책 **Ch.3.6** Process address space + **Ch.4** 앞부분의 trampoline 설명
- 🔍 리뷰 포인트: 트랩이 들어오는 순간 CR3 가 사용자 페이지 테이블이어도 진입 코드가 실행될 수 있는가?

</div>

<div class="session" data-session="6" markdown="1">

### Week 6 · 2026.12.13 (일) — 트랩: IDT

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- **🤖 Claude (주중):** `kernelvec.S`, `trap.c` 대체: IDT 설정, 예외·인터럽트 진입/복귀, 커널 모드 트랩 처리
- **👤 Ryu (일요일 3h):** 책 **Ch.4.1** RISC-V trap machinery + **4.5** Traps from kernel space · `stvec`/`scause`/`sepc` ↔ IDT/벡터 번호/`RIP` 대응 정리

</div>

<div class="session" data-session="7" markdown="1">

### Week 7 · 2026.12.20 (일) — 시스템 콜: syscall / sysret

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- **🤖 Claude (주중):** `trampoline.S` 대체: `syscall` 명령어 진입, 사용자 ↔ 커널 전환 (`swapgs`, CR3 교체) · `usys.pl` 이 `ecall` 대신 `syscall` 생성 · 인자 레지스터 대응
- **👤 Ryu (일요일 3h):** 책 **Ch.4.2–4.4** Traps from user space, Calling system calls, System call arguments
- 🎯 **마일스톤:** 첫 사용자 프로그램 (`initcode`) 이 시스템 콜을 부른다

</div>

<div class="session" data-session="8" markdown="1">

### Week 8 · 2026.12.27 (일) — 페이지 폴트

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- **🤖 Claude (주중):** `vmfault` (게으른 할당) 을 x86-64 페이지 폴트 (CR2, 에러 코드) 로 연결
- **👤 Ryu (일요일 3h):** 책 **Ch.5** Page faults

</div>

<div class="session" data-session="9" markdown="1">

### Week 9 · 2027.1.3 (일) — 인터럽트: ACPI, LAPIC, IOAPIC

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- **🤖 Claude (주중):** `plic.c` 대체: ACPI MADT 파싱으로 CPU 와 IOAPIC 찾기 · LAPIC 타이머 · 시리얼·키보드 인터럽트 연결
- **👤 Ryu (일요일 3h):** 책 **Ch.6** Interrupts and device drivers · PLIC ↔ IOAPIC, CLINT/`stimecmp` ↔ LAPIC 타이머 대응 정리

</div>

<div class="session" data-session="10" markdown="1">

### Week 10 · 2027.1.10 (일) — 락과 멀티코어

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- **🤖 Claude (주중):** `spinlock.c` 의 `push_off`/`pop_off` → `cli`/`sti`, 원자 연산 → `xchg` · 다른 CPU 깨우기 (INIT-SIPI)
- **👤 Ryu (일요일 3h):** 책 **Ch.7** Locking (특히 7.5 Locks and interrupts, 7.6 memory ordering) · x86 메모리 순서 모델과 RISC-V 비교

</div>

<div class="session" data-session="11" markdown="1">

### Week 11 · 2027.1.17 (일) — 컨텍스트 스위치

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **🤖 Claude (주중):** `swtch.S` 를 x86-64 호출 규약 (callee-saved 레지스터) 에 맞게 재작성 · `mycpu`/`myproc`
- **👤 Ryu (일요일 3h):** 책 **Ch.8** Scheduling · `swtch` 전후 스택 그림 그리기

</div>

<div class="session" data-session="12" markdown="1">

### Week 12 · 2027.1.24 (일) — 램디스크와 파일 시스템

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **🤖 Claude (주중):** `virtio_disk.c` 대체: UEFI 로더가 올린 파일 시스템 이미지를 램디스크로 사용 · `mkfs` 호스트 빌드
- **👤 Ryu (일요일 3h):** 책 **Ch.10.1** 파일 시스템 개요 · 원본 virtio 드라이버가 하던 일 정리
- 💡 램디스크는 QEMU · VirtualBox · 실제 PC 에서 모두 똑같이 동작한다 (디스크 드라이버는 2년차 목표)

</div>

<div class="session" data-session="13" markdown="1">

### Week 13 · 2027.1.31 (일) — usertests 통과

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **🤖 Claude (주중):** 전체 `usertests` 통과까지 디버깅 · 여유 주간
- **👤 Ryu (일요일 3h):** 포팅된 기계 의존 코드 전체를 대응표와 함께 리뷰
- 🎯 **마일스톤:** x86-64 xv6 가 QEMU 에서 `usertests` 를 모두 통과

</div>

<div class="session" data-session="14" markdown="1">

### Week 14 · 2027.2.7 (일) — VirtualBox + v0.1

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **🤖 Claude (주중):** VirtualBox EFI 모드 부팅 스크립트 · 태그 `v0.1-x86_64-c`
- **👤 Ryu (일요일 3h):** VirtualBox 에서 직접 셸 써 보기 · Phase A 회고
- 🎯 **마일스톤 v0.1:** C 로 된 x86-64 xv6 가 QEMU + VirtualBox 에서 동작

</div>

<div style="margin-top: 100px;"></div>

## Phase B · C → C++ 번역

*Week 15–40 · 2027.2.14 ~ 2027.8.8 · 책 장 순서대로 파일 하나씩*

<div class="session" data-session="15" markdown="1">

### Week 15 · 2027.2.14 (일) — C++ 빌드 기반

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **🤖 Claude (주중):** freestanding C++20 설정 (`-fno-exceptions -fno-rtti`), C/C++ 혼합 링크, 최소 런타임 · `types.h`, `param.h`, `x86.h`, `memlayout.h` → `constexpr`
- **👤 Ryu (일요일 3h):** 책 **Ch.2** 다시 읽기 · 매크로 → `constexpr` 변환 리뷰
- 💡 원칙: **매주 커널이 부팅되고 `usertests` 를 통과해야 한다.** C 파일이 조금씩 C++ 로 바뀔 뿐

</div>

<div class="session" data-session="16" markdown="1">

### Week 16 · 2027.2.21 (일) — 콘솔과 출력

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **🤖 Claude (주중):** `string.c`, `printf.c`, `uart.c`, `console.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.6.1–6.2** Console input / output

</div>

<div class="session" data-session="17" markdown="1">

### Week 17 · 2027.2.28 (일) — 물리 메모리 할당자

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **🤖 Claude (주중):** `kalloc.c` → `Kmem` 클래스
- **👤 Ryu (일요일 3h):** 책 **Ch.3.4–3.5**

</div>

<div class="session" data-session="18" markdown="1">

### Week 18 · 2027.3.7 (일) — vm 1: 커널 페이지 테이블

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **🤖 Claude (주중):** `vm.c` 앞부분 (`walk`, `mappages`, `kvmmake`) → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.3.1–3.3**

</div>

<div class="session" data-session="19" markdown="1">

### Week 19 · 2027.3.14 (일) — vm 2: 사용자 주소 공간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **🤖 Claude (주중):** `vm.c` 나머지 (`uvm*`, `copyin`/`copyout`, `vmfault`) → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.3.6** + **Ch.5**

</div>

<div class="session" data-session="20" markdown="1">

### Week 20 · 2027.3.21 (일) — exec

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **🤖 Claude (주중):** `exec.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.3.7** Code: exec · 사용자 스택에 argv 가 쌓이는 그림 그리기

</div>

<div class="session" data-session="21" markdown="1">

### Week 21 · 2027.3.28 (일) — 트랩과 시스템 콜

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **🤖 Claude (주중):** `trap.c`, `syscall.c` → C++ (시스템 콜 테이블을 `constexpr` 배열로)
- **👤 Ryu (일요일 3h):** 책 **Ch.4** 복습

</div>

<div class="session" data-session="22" markdown="1">

### Week 22 · 2027.4.4 (일) — sysproc, 인터럽트 컨트롤러

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **🤖 Claude (주중):** `sysproc.c`, ACPI / LAPIC / IOAPIC 코드 → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.6.4** Timer interrupts

</div>

<div class="session" data-session="23" markdown="1">

### Week 23 · 2027.4.11 (일) — 스핀락

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **🤖 Claude (주중):** `spinlock.c` → `Spinlock` 클래스 + **RAII `LockGuard`**
- **👤 Ryu (일요일 3h):** 책 **Ch.7.1–7.6**
- 🔍 리뷰 포인트: RAII 로 바꿔도 원본의 `acquire`/`release` 순서가 그대로인가?

</div>

<div class="session" data-session="24" markdown="1">

### Week 24 · 2027.4.18 (일) — 슬립락 + 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **🤖 Claude (주중):** `sleeplock.c` → C++ · 밀린 부분 정리
- **👤 Ryu (일요일 3h):** 책 **Ch.7.7** Sleep locks

</div>

<div class="session" data-session="25" markdown="1">

### Week 25 · 2027.4.25 (일) — proc 1: 생성

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **🤖 Claude (주중):** `proc.c`: `allocproc`, `userinit`, `fork`, `growproc` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.2.5–2.6**

</div>

<div class="session" data-session="26" markdown="1">

### Week 26 · 2027.5.2 (일) — proc 2: 스케줄러

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **🤖 Claude (주중):** `proc.c`: `scheduler`, `sched`, `yield`, `forkret` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.8**

</div>

<div class="session" data-session="27" markdown="1">

### Week 27 · 2027.5.9 (일) — proc 3: sleep / wakeup

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **🤖 Claude (주중):** `proc.c`: `sleep`, `wakeup`, `exit`, `wait`, `kill` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.9.1–9.2, 9.4–9.5**

</div>

<div class="session" data-session="28" markdown="1">

### Week 28 · 2027.5.16 (일) — 파이프

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **🤖 Claude (주중):** `pipe.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.9.3** Code: Pipes

</div>

<div class="session" data-session="29" markdown="1">

### Week 29 · 2027.5.23 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리
- **👤 Ryu (일요일 3h):** 지금까지 C++ 코드 전체 리뷰
- 🎯 **마일스톤:** 파일 시스템을 뺀 커널 전체가 C++

</div>

<div class="session" data-session="30" markdown="1">

### Week 30 · 2027.5.30 (일) — 버퍼 캐시

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **🤖 Claude (주중):** `bio.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.10.2–10.3**

</div>

<div class="session" data-session="31" markdown="1">

### Week 31 · 2027.6.6 (일) — 로깅

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **🤖 Claude (주중):** `log.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.10.4–10.6**
- 💡 FTL 과의 연결: 쓰기 순서와 원자성은 FTL 매핑 테이블 복구와 같은 문제

</div>

<div class="session" data-session="32" markdown="1">

### Week 32 · 2027.6.13 (일) — fs 1: 블록과 inode

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **🤖 Claude (주중):** `fs.c` 앞부분 → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.10.7–10.9**

</div>

<div class="session" data-session="33" markdown="1">

### Week 33 · 2027.6.20 (일) — fs 2: 디렉터리와 경로

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **🤖 Claude (주중):** `fs.c` 나머지 → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.10** 디렉터리·경로 절

</div>

<div class="session" data-session="34" markdown="1">

### Week 34 · 2027.6.27 (일) — 파일 디스크립터와 파일 시스템 콜 1

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **🤖 Claude (주중):** `file.c`, `sysfile.c` 앞부분 → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.10** 나머지

</div>

<div class="session" data-session="35" markdown="1">

### Week 35 · 2027.7.4 (일) — 파일 시스템 콜 2 + 램디스크

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **🤖 Claude (주중):** `sysfile.c` 나머지, 램디스크 드라이버 → C++
- **👤 Ryu (일요일 3h):** `open` 과 `unlink` 경로의 락 순서 확인

</div>

<div class="session" data-session="36" markdown="1">

### Week 36 · 2027.7.11 (일) — mkfs + 커널 100% C++

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **🤖 Claude (주중):** `mkfs.c` → C++17 (호스트 도구라 표준 라이브러리 사용)
- **👤 Ryu (일요일 3h):** 책 **Ch.11** Concurrency revisited
- 🎯 **마일스톤:** 커널에 C 파일이 하나도 남지 않는다 (어셈블리 제외)

</div>

<div class="session" data-session="37" markdown="1">

### Week 37 · 2027.7.18 (일) — 사용자 라이브러리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="37"> 완료</label>

- **🤖 Claude (주중):** `ulib.c`, `printf.c`, `umalloc.c` → C++
- **👤 Ryu (일요일 3h):** 사용자 프로그램 → 시스템 콜 경로 복습

</div>

<div class="session" data-session="38" markdown="1">

### Week 38 · 2027.7.25 (일) — init 과 셸

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="38"> 완료</label>

- **🤖 Claude (주중):** `init.c`, `sh.c` → C++ (명령 구조체를 클래스 계층으로)
- **👤 Ryu (일요일 3h):** 책 **Ch.1** 셸 부분 다시 읽기

</div>

<div class="session" data-session="39" markdown="1">

### Week 39 · 2027.8.1 (일) — 유틸리티와 usertests

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="39"> 완료</label>

- **🤖 Claude (주중):** `ls`, `cat`, `grep`, `wc` 등 유틸리티와 `usertests` → C++
- **👤 Ryu (일요일 3h):** 원본과 비교 리뷰

</div>

<div class="session" data-session="40" markdown="1">

### Week 40 · 2027.8.8 (일) — v1.0: 전체 C++

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="40"> 완료</label>

- **🤖 Claude (주중):** QEMU + VirtualBox 에서 `usertests` 전체 통과 · 태그 `v1.0-cpp`
- **👤 Ryu (일요일 3h):** 책 **Ch.12** Summary · Phase B 회고
- 🎯 **마일스톤 v1.0:** 전체가 C++ 인 x86-64 xv6 가 QEMU + VirtualBox 에서 동작

</div>

<div style="margin-top: 100px;"></div>

## Phase C · 실제 PC

*Week 41–52 · 2027.8.15 ~ 2027.10.31 · 프레임버퍼, PCI, xHCI USB 키보드, 실제 부팅*

<div class="session" data-session="41" markdown="1">

### Week 41 · 2027.8.15 (일) — 프레임버퍼 콘솔

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="41"> 완료</label>

- **🤖 Claude (주중):** GOP 프레임버퍼에 비트맵 폰트로 글자 그리기 (실제 PC 에는 시리얼 포트가 없음)
- **👤 Ryu (일요일 3h):** 픽셀 형식, 스크롤 구현 리뷰

</div>

<div class="session" data-session="42" markdown="1">

### Week 42 · 2027.8.22 (일) — PCI 열거

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="42"> 완료</label>

- **🤖 Claude (주중):** ACPI MCFG 로 PCIe 설정 공간 접근, 장치 목록 출력
- **👤 Ryu (일요일 3h):** PCI 설정 공간과 BAR 개념 공부

</div>

<div class="session" data-session="43" markdown="1">

### Week 43 · 2027.8.29 (일) — xHCI 1: 컨트롤러 초기화

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="43"> 완료</label>

- **🤖 Claude (주중):** xHCI 리셋, 레지스터 설정 (MikanOS 의 USB 드라이버 참고)
- **👤 Ryu (일요일 3h):** xHCI 구조 공부

</div>

<div class="session" data-session="44" markdown="1">

### Week 44 · 2027.9.5 (일) — xHCI 2: 링

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="44"> 완료</label>

- **🤖 Claude (주중):** command / event / transfer ring 구현
- **👤 Ryu (일요일 3h):** 링 구조 리뷰

</div>

<div class="session" data-session="45" markdown="1">

### Week 45 · 2027.9.12 (일) — USB 열거

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="45"> 완료</label>

- **🤖 Claude (주중):** 포트 리셋, 주소 할당, 디스크립터 읽기
- **👤 Ryu (일요일 3h):** USB 열거 순서 공부
- ⚠️ 1년 중 가장 위험한 구간. 밀리면 여유 주간 (Week 47, 50, 51) 을 쓴다

</div>

<div class="session" data-session="46" markdown="1">

### Week 46 · 2027.9.19 (일) — USB 키보드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="46"> 완료</label>

- **🤖 Claude (주중):** HID 부트 프로토콜 키보드 입력 → 콘솔 입력
- **👤 Ryu (일요일 3h):** QEMU `-device qemu-xhci -device usb-kbd` 로 확인

</div>

<div class="session" data-session="47" markdown="1">

### Week 47 · 2027.9.26 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="47"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리
- **👤 Ryu (일요일 3h):** Phase C 리뷰

</div>

<div class="session" data-session="48" markdown="1">

### Week 48 · 2027.10.3 (일) — 실제 PC 1: 부팅

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="48"> 완료</label>

- **🤖 Claude (주중):** USB 스틱용 FAT32 ESP 이미지 · 실제 PC 부팅 시도, 프레임버퍼 로그로 디버깅
- **👤 Ryu (일요일 3h):** 실제 PC 에서 부팅해 화면 사진 공유

</div>

<div class="session" data-session="49" markdown="1">

### Week 49 · 2027.10.10 (일) — 실제 PC 2: 하드웨어 차이

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="49"> 완료</label>

- **🤖 Claude (주중):** 실제 하드웨어에서만 나오는 문제 수정 (타이머 보정, 멀티코어, ACPI 테이블 차이)
- **👤 Ryu (일요일 3h):** 문제 원인 리뷰

</div>

<div class="session" data-session="50" markdown="1">

### Week 50 · 2027.10.17 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="50"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리
- **👤 Ryu (일요일 3h):** 밀린 리뷰

</div>

<div class="session" data-session="51" markdown="1">

### Week 51 · 2027.10.24 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="51"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리, README 정리
- **👤 Ryu (일요일 3h):** 밀린 리뷰
- 🎯 **마일스톤 v2.0:** 실제 UEFI PC 에서 셸이 뜨고 USB 키보드로 명령을 친다

</div>

<div class="session" data-session="52" markdown="1">

### Week 52 · 2027.10.31 (일) — 1년 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="52"> 완료</label>

- **🤖 Claude (주중):** 태그 `v2.0-baremetal`
- **👤 Ryu (일요일 3h):** 회고 글: RISC-V 와 x86-64 의 차이, C → C++ 로 바꾸며 배운 것, 2년차 목표 (NVMe/AHCI 디스크 등)

</div>


<script>
(function () {
  var STORAGE_KEY = 'xv6-cpp-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('.session-checkbox'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = boxes.length;
    var state = load();

    function render() {
      var done = 0;
      boxes.forEach(function (cb) {
        var id = cb.getAttribute('data-session');
        var isDone = !!state[id];
        cb.checked = isDone;
        var wrap = cb.closest('.session');
        if (wrap) wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    boxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        state[cb.getAttribute('data-session')] = cb.checked;
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
