---
layout: default
title: xv6 C++ 포팅 1년 계획
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

# xv6 를 C++ 로 다시 쓰기 — 1년 계획

**2026년 11월 8일 (일) 시작 · 52주 · 매주 일요일 3시간**

주말 6시간을 반씩 나눈다: **토요일 3시간 = [계산 이론 & Gödel](/learning-cs/computation-theory/study-plan/)**, **일요일 3시간 = 이 계획**.

<div style="margin-top: 100px;"></div>

## 목표

- C 로 쓰인 **xv6 (x86 판, xv6-public)** 를 **C++ 로 한 파일씩 번역**한다
- 1년 동안 천천히: **매주 Claude 가 번역하고, Ryu 는 코드와 책을 함께 읽으며 리뷰**한다
- 최종 목표: **QEMU, VirtualBox, 실제 PC (UEFI 전용)** 세 곳에서 모두 동작

**왜 RISC-V 판이 아니라 x86 판인가?**
최신 xv6 (xv6-riscv) 는 RISC-V 용이라 VirtualBox 나 일반 PC 에서 돌 수 없다. 그래서 마지막 x86 판인 xv6-public 과 그 짝인 책 rev11 을 쓴다.

<div style="margin-top: 100px;"></div>

## 역할 분담

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:20%"><col style="width:80%"></colgroup>
  <thead><tr><th>누가</th><th>할 일</th></tr></thead>
  <tbody>
    <tr><td>🤖 Claude<br>(주중)</td><td>그 주 분량의 C 파일을 C++ 로 번역 · 빌드 · QEMU (Week 9 부터 VirtualBox 도) 에서 부팅과 <code>usertests</code> 확인 · 로컬 커밋 · 리뷰 노트 <code>docs/review/weekNN.md</code> 작성 (C → C++ 대응표, 설계 결정, 봐야 할 곳)</td></tr>
    <tr><td>👤 Ryu<br>(일요일 3h)</td><td>① 리뷰 노트를 보고 원본 C 와 번역된 C++ 를 나란히 읽기 (~1.5h)<br>② 같은 내용의 xv6 책 장 읽기 (~1.5h)<br>③ 질문·수정 요청 → 승인하면 GitHub 에 push</td></tr>
  </tbody>
</table>
</div>

- 시작 방법: 주중에 Claude 에게 **"xv6-cpp Week N 진행해"** 라고 말하면 된다
- **push 는 Ryu 의 리뷰와 승인 후에만** 한다 (코드 저장소 규칙)

<div style="margin-top: 100px;"></div>

## 자료

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:25%"><col style="width:75%"></colgroup>
  <thead><tr><th>역할</th><th>자료</th></tr></thead>
  <tbody>
    <tr><td>원본 코드</td><td><a href="https://github.com/mit-pdos/xv6-public">mit-pdos/xv6-public</a> (x86, MIT 라이선스)</td></tr>
    <tr><td>책</td><td><a href="https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf"><em>xv6: a simple, Unix-like teaching operating system</em>, rev11</a> (x86 판, 무료 PDF)</td></tr>
    <tr><td>원본 소스 인쇄본</td><td><a href="https://pdos.csail.mit.edu/6.828/2018/xv6/xv6-rev11.pdf">xv6-rev11.pdf</a> (줄 번호가 붙은 전체 소스, 책과 대조할 때 편함)</td></tr>
    <tr><td>번역 저장소</td><td><code>github.com/jonghoon-ryu/xv6-cpp</code> (Week 1 에 생성, 공개)</td></tr>
    <tr><td>Phase 8 참고</td><td><a href="https://github.com/uchan-nos/mikanos">MikanOS</a> (C++ 로 쓰인 UEFI 부트 로더와 xHCI USB 드라이버)</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 번역 원칙

- **매주 동작하는 상태 유지:** C 와 C++ 파일을 함께 링크해서, 어느 주에 멈춰도 커널은 부팅되고 `usertests` 를 통과한다
- **책과 대조 가능하게:** 함수 이름과 파일 구조는 원본을 따른다. 그래야 책을 읽으며 리뷰할 수 있다
- **커널은 freestanding C++20:** 예외·RTTI·표준 라이브러리 없음 (`-ffreestanding -fno-exceptions -fno-rtti`)
- **C++ 다운 부분만 바꾼다:**
  - `#define` 상수 → `constexpr`, 정수 상수 모음 → `enum class`
  - `acquire`/`release` 짝 → RAII `LockGuard`
  - 구조체 + 함수 → 필요한 곳에서 멤버 함수 (`Proc`, `Buf`, `Inode` 등)
  - 포인터 인자 중 null 이 될 수 없는 것 → 참조
- **어셈블리 (`.S`) 는 그대로 둔다:** 부트 코드, 트랩 진입, 컨텍스트 스위치는 C++ 로 쓸 수 없다
- **호스트 도구 (`mkfs`) 는 일반 C++17:** 표준 라이브러리 사용

<div style="margin-top: 100px;"></div>

## 전체 로드맵

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:34%"><col style="width:28%"><col style="width:38%"></colgroup>
  <thead><tr><th>단계</th><th>기간</th><th>내용</th></tr></thead>
  <tbody>
      <tr><td>Phase 1 · 기반</td><td>Week 1–4<br>2026.11.8 ~ 2026.11.29</td><td>빌드 체계, 부트 로더, 헤더, 콘솔</td></tr>
      <tr><td>Phase 2 · 메모리</td><td>Week 5–9<br>2026.12.6 ~ 2027.1.3</td><td>kalloc, 페이지 테이블, exec, VirtualBox 첫 부팅</td></tr>
      <tr><td>Phase 3 · 트랩, 인터럽트, 드라이버</td><td>Week 10–15<br>2027.1.10 ~ 2027.2.14</td><td>trap, syscall, APIC, MP, IDE</td></tr>
      <tr><td>Phase 4 · 락, 프로세스, 스케줄링</td><td>Week 16–22<br>2027.2.21 ~ 2027.4.4</td><td>spinlock, proc, pipe, sleeplock</td></tr>
      <tr><td>Phase 5 · 파일 시스템</td><td>Week 23–31<br>2027.4.11 ~ 2027.6.6</td><td>bio, log, fs, file, sysfile, mkfs</td></tr>
      <tr><td>Phase 6 · 사용자 프로그램 → v1.0</td><td>Week 32–35<br>2027.6.13 ~ 2027.7.4</td><td>ulib, sh, 유틸리티, usertests</td></tr>
      <tr><td>Phase 7 · x86-64 → v2.0</td><td>Week 36–42<br>2027.7.11 ~ 2027.8.22</td><td>롱 모드, 4단계 페이징, 64비트 트랩</td></tr>
      <tr><td>Phase 8 · UEFI 베어메탈 → v3.0</td><td>Week 43–52<br>2027.8.29 ~ 2027.10.31</td><td>UEFI 로더, 프레임버퍼, ACPI, PCI, xHCI USB 키보드</td></tr>
  </tbody>
</table>
</div>

**순서의 이유:** Phase 1–6 은 책의 장 순서를 따라 번역하므로, 매주 번역된 코드와 책의 같은 장을 함께 읽을 수 있다.
Phase 7–8 은 실제 PC 를 위한 확장이다.

**실제 PC (UEFI 전용) 가 가장 어려운 이유:**
원본 xv6 는 레거시 BIOS 부팅, IDE 디스크, PS/2 키보드, VGA 텍스트 화면을 가정한다. 최신 UEFI 전용 PC 에는 이 중 어느 것도 없다.
그래서 Phase 8 에서는 **UEFI 로더, 프레임버퍼 콘솔, ACPI, USB 키보드 (xHCI)** 를 새로 만들고, 디스크 대신 **램디스크**를 쓴다.
xHCI USB 드라이버 구간 (Week 48–49) 이 1년 중 가장 위험한 구간이다.

<div style="margin-top: 100px;"></div>

## 진도

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 52</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Phase 1 · 기반

*Week 1–4 · 2026.11.8 ~ 2026.11.29 · 빌드 체계, 부트 로더, 헤더, 콘솔*

<div class="session" data-session="1" markdown="1">

### Week 1 · 2026.11.8 (일) — 저장소, 빌드, C/C++ 혼합 링크

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- **🤖 Claude (주중):** `xv6-cpp` 저장소 생성 (원본 xv6-public 을 첫 커밋으로) · Makefile 에 `g++ -m32 -ffreestanding -fno-exceptions -fno-rtti` 추가 · C 와 C++ 파일이 섞여도 링크되게 구성 · C++ 최소 런타임 (`operator new` 없음, `__cxa_pure_virtual`, 전역 생성자 호출)
- **👤 Ryu (일요일 3h):** 책 **Ch.0** Operating system interfaces · 원본 xv6 를 QEMU 에서 `make qemu` 로 직접 띄워 보기 · 빌드 변경 리뷰
- 💡 원칙: **매주 커널이 부팅되고 `usertests` 를 통과해야 한다.** C 파일이 매주 조금씩 C++ 로 바뀔 뿐, 항상 동작하는 상태 유지

</div>

<div class="session" data-session="2" markdown="1">

### Week 2 · 2026.11.15 (일) — 부트 로더

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- **🤖 Claude (주중):** `bootmain.c` → `bootmain.cpp` (`bootasm.S` 는 어셈블리 그대로) · 512 바이트 부트 섹터 크기 제한 안에 들어가는지 확인
- **👤 Ryu (일요일 3h):** 책 **Appendix B** The boot loader · `bootasm.S` 를 한 줄씩 따라가며 리얼 모드 → 보호 모드 전환 이해
- 🔍 리뷰 포인트: C++ 로 바꿔도 생성된 기계어 크기가 거의 같은가?

</div>

<div class="session" data-session="3" markdown="1">

### Week 3 · 2026.11.22 (일) — 기본 헤더: 타입, x86, MMU

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- **🤖 Claude (주중):** `types.h`, `param.h`, `x86.h`, `mmu.h`, `memlayout.h`, `elf.h` → C++ 헤더 · `#define` 상수 → `constexpr`, 매크로 함수 → `inline` 함수
- **👤 Ryu (일요일 3h):** 책 **Ch.1** Operating system organization + **Appendix A** PC hardware
- 🔍 리뷰 포인트: 매크로를 `constexpr` 로 바꿨을 때 달라지는 점 (타입 검사, 디버깅)

</div>

<div class="session" data-session="4" markdown="1">

### Week 4 · 2026.11.29 (일) — 콘솔 출력

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- **🤖 Claude (주중):** `uart.c`, `console.c` (CGA 텍스트 출력, `cprintf`) · `string.c` → C++
- **👤 Ryu (일요일 3h):** `console.c` 의 CGA 메모리(0xB8000) 쓰기 방식 이해 · 커널 `cprintf` 동작 확인
- 🎯 **마일스톤:** C++ 코드가 화면에 글자를 찍는다

</div>

<div style="margin-top: 100px;"></div>

## Phase 2 · 메모리

*Week 5–9 · 2026.12.6 ~ 2027.1.3 · kalloc, 페이지 테이블, exec, VirtualBox 첫 부팅*

<div class="session" data-session="5" markdown="1">

### Week 5 · 2026.12.6 (일) — 물리 메모리 할당자

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- **🤖 Claude (주중):** `kalloc.c` → `Kmem` 클래스 (free list, `kalloc`/`kfree`)
- **👤 Ryu (일요일 3h):** 책 **Ch.2** Page tables 앞부분 (물리 메모리 할당)

</div>

<div class="session" data-session="6" markdown="1">

### Week 6 · 2026.12.13 (일) — 페이지 테이블 1: 커널 주소 공간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- **🤖 Claude (주중):** `vm.c` 앞부분: `walkpgdir`, `mappages`, `setupkvm`, `kvmalloc`
- **👤 Ryu (일요일 3h):** 책 **Ch.2** 중간 (x86 2단계 페이지 테이블, 커널 매핑)
- ✏️ 직접 해보기: 가상 주소 하나를 골라 PDE → PTE → 물리 주소 변환을 손으로 계산

</div>

<div class="session" data-session="7" markdown="1">

### Week 7 · 2026.12.20 (일) — 페이지 테이블 2: 사용자 주소 공간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- **🤖 Claude (주중):** `vm.c` 나머지: `inituvm`, `loaduvm`, `allocuvm`, `deallocuvm`, `copyuvm`, `switchuvm`
- **👤 Ryu (일요일 3h):** 책 **Ch.2** 나머지 (프로세스 주소 공간)

</div>

<div class="session" data-session="8" markdown="1">

### Week 8 · 2026.12.27 (일) — exec

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- **🤖 Claude (주중):** `exec.c` → C++ (ELF 로딩, 사용자 스택 구성)
- **👤 Ryu (일요일 3h):** 책 **Ch.2** 의 exec 절 · 사용자 스택에 argv 가 쌓이는 그림 직접 그려 보기

</div>

<div class="session" data-session="9" markdown="1">

### Week 9 · 2027.1.3 (일) — VirtualBox 첫 부팅 + 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- **🤖 Claude (주중):** 디스크 이미지를 VirtualBox 용으로 변환 (`VBoxManage convertfromraw`), VM 설정 스크립트 작성 · 밀린 부분 정리
- **👤 Ryu (일요일 3h):** VirtualBox 에서 부팅 확인 · Phase 1–2 코드 전체 리뷰
- 🎯 **마일스톤:** 같은 C++ 커널이 **QEMU 와 VirtualBox** 에서 둘 다 부팅된다

</div>

<div style="margin-top: 100px;"></div>

## Phase 3 · 트랩, 인터럽트, 드라이버

*Week 10–15 · 2027.1.10 ~ 2027.2.14 · trap, syscall, APIC, MP, IDE*

<div class="session" data-session="10" markdown="1">

### Week 10 · 2027.1.10 (일) — 트랩과 IDT

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- **🤖 Claude (주중):** `trap.c` → C++, `vectors.pl` 생성 코드 연동 (`trapasm.S` 는 그대로)
- **👤 Ryu (일요일 3h):** 책 **Ch.3** Traps, interrupts, and drivers 앞부분 (x86 트랩 처리 흐름)

</div>

<div class="session" data-session="11" markdown="1">

### Week 11 · 2027.1.17 (일) — 시스템 콜

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **🤖 Claude (주중):** `syscall.c`, `sysproc.c` → C++ · 시스템 콜 테이블을 `constexpr` 배열로
- **👤 Ryu (일요일 3h):** 책 **Ch.3** 시스템 콜 절 · `int $64` 에서 `sys_*` 함수까지 경로 따라가기

</div>

<div class="session" data-session="12" markdown="1">

### Week 12 · 2027.1.24 (일) — 인터럽트 컨트롤러

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **🤖 Claude (주중):** `lapic.c`, `ioapic.c`, `picirq.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.3** 인터럽트 절 · LAPIC 타이머가 스케줄링을 일으키는 원리

</div>

<div class="session" data-session="13" markdown="1">

### Week 13 · 2027.1.31 (일) — 멀티프로세서 시작

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **🤖 Claude (주중):** `mp.c` (MP 테이블 파싱), `main.c` (`mpmain`, `startothers`) → C++ (`entryother.S` 는 그대로)
- **👤 Ryu (일요일 3h):** 책 **Ch.1** 의 첫 프로세스 절 다시 읽기 · 다른 CPU 가 깨어나는 순서 정리
- 💡 나중에 Phase 8 에서 `mp.c` 는 ACPI MADT 파싱으로 교체된다 (최신 PC 에는 MP 테이블이 없음)

</div>

<div class="session" data-session="14" markdown="1">

### Week 14 · 2027.2.7 (일) — 키보드와 디스크 드라이버

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **🤖 Claude (주중):** `kbd.c`, `ide.c`, `memide.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.3** 드라이버 절 (IDE 디스크, 인터럽트 기반 I/O)

</div>

<div class="session" data-session="15" markdown="1">

### Week 15 · 2027.2.14 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리, 코드 스타일 통일
- **👤 Ryu (일요일 3h):** Phase 3 코드 전체 리뷰 · 트랩 → 시스템 콜 → 드라이버 흐름을 한 장 그림으로 정리

</div>

<div style="margin-top: 100px;"></div>

## Phase 4 · 락, 프로세스, 스케줄링

*Week 16–22 · 2027.2.21 ~ 2027.4.4 · spinlock, proc, pipe, sleeplock*

<div class="session" data-session="16" markdown="1">

### Week 16 · 2027.2.21 (일) — 스핀락

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **🤖 Claude (주중):** `spinlock.c` → `Spinlock` 클래스 + **RAII `LockGuard`** (스코프를 벗어나면 자동 해제)
- **👤 Ryu (일요일 3h):** 책 **Ch.4** Locking
- 🔍 리뷰 포인트: RAII 로 바꿨을 때 원본의 `acquire`/`release` 짝이 전부 보존되는가? (락 해제 순서가 중요한 곳 주의)

</div>

<div class="session" data-session="17" markdown="1">

### Week 17 · 2027.2.28 (일) — 프로세스 1: 생성

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **🤖 Claude (주중):** `proc.c` 앞부분: `allocproc`, `userinit`, `growproc`, `fork`
- **👤 Ryu (일요일 3h):** 책 **Ch.1** 첫 프로세스 절 + **Ch.5** Scheduling 앞부분

</div>

<div class="session" data-session="18" markdown="1">

### Week 18 · 2027.3.7 (일) — 프로세스 2: 스케줄러

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **🤖 Claude (주중):** `proc.c`: `scheduler`, `sched`, `yield`, `forkret` (`swtch.S` 는 그대로)
- **👤 Ryu (일요일 3h):** 책 **Ch.5** 컨텍스트 스위치 절 · `swtch` 전후 스택 상태 그림 그리기

</div>

<div class="session" data-session="19" markdown="1">

### Week 19 · 2027.3.14 (일) — sleep / wakeup, exit / wait

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **🤖 Claude (주중):** `proc.c` 나머지: `sleep`, `wakeup`, `exit`, `wait`, `kill`, `procdump`
- **👤 Ryu (일요일 3h):** 책 **Ch.5** sleep/wakeup 절 (lost wakeup 문제)

</div>

<div class="session" data-session="20" markdown="1">

### Week 20 · 2027.3.21 (일) — 파이프

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **🤖 Claude (주중):** `pipe.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.5** 의 pipe 절

</div>

<div class="session" data-session="21" markdown="1">

### Week 21 · 2027.3.28 (일) — 슬립락

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **🤖 Claude (주중):** `sleeplock.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.4** 슬립락 부분 + Ch.6 앞부분 미리 보기

</div>

<div class="session" data-session="22" markdown="1">

### Week 22 · 2027.4.4 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리
- **👤 Ryu (일요일 3h):** Phase 4 코드 전체 리뷰
- 🎯 **마일스톤:** 파일 시스템을 뺀 커널 전체가 C++

</div>

<div style="margin-top: 100px;"></div>

## Phase 5 · 파일 시스템

*Week 23–31 · 2027.4.11 ~ 2027.6.6 · bio, log, fs, file, sysfile, mkfs*

<div class="session" data-session="23" markdown="1">

### Week 23 · 2027.4.11 (일) — 버퍼 캐시

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **🤖 Claude (주중):** `bio.c` → C++ (LRU 이중 연결 리스트)
- **👤 Ryu (일요일 3h):** 책 **Ch.6** File system: 계층 구조 + buffer cache 절

</div>

<div class="session" data-session="24" markdown="1">

### Week 24 · 2027.4.18 (일) — 로깅 (크래시 복구)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **🤖 Claude (주중):** `log.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.6** logging 절
- 💡 FTL 과의 연결: 쓰기 순서와 원자성 문제는 FTL 매핑 테이블 복구와 같은 문제

</div>

<div class="session" data-session="25" markdown="1">

### Week 25 · 2027.4.25 (일) — 파일 시스템 1: 블록과 inode

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **🤖 Claude (주중):** `fs.c` 앞부분: `balloc`, `bfree`, `ialloc`, `iget`, `ilock`, `iput`, `bmap`
- **👤 Ryu (일요일 3h):** 책 **Ch.6** block allocator + inode 절

</div>

<div class="session" data-session="26" markdown="1">

### Week 26 · 2027.5.2 (일) — 파일 시스템 2: 디렉터리와 경로

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **🤖 Claude (주중):** `fs.c` 나머지: `readi`, `writei`, `dirlookup`, `dirlink`, `namei`
- **👤 Ryu (일요일 3h):** 책 **Ch.6** directory + path name 절

</div>

<div class="session" data-session="27" markdown="1">

### Week 27 · 2027.5.9 (일) — 파일 디스크립터

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **🤖 Claude (주중):** `file.c` → C++
- **👤 Ryu (일요일 3h):** 책 **Ch.6** file descriptor 절

</div>

<div class="session" data-session="28" markdown="1">

### Week 28 · 2027.5.16 (일) — 파일 시스템 콜 1

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **🤖 Claude (주중):** `sysfile.c` 앞부분: `dup`, `read`, `write`, `close`, `fstat`, `link`, `unlink`
- **👤 Ryu (일요일 3h):** 책 **Ch.6** 나머지

</div>

<div class="session" data-session="29" markdown="1">

### Week 29 · 2027.5.23 (일) — 파일 시스템 콜 2

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **🤖 Claude (주중):** `sysfile.c` 나머지: `open`, `mkdir`, `mknod`, `chdir`, `exec`, `pipe`
- **👤 Ryu (일요일 3h):** `unlink` 와 `open` 경로에서 락 순서가 어떻게 지켜지는지 확인

</div>

<div class="session" data-session="30" markdown="1">

### Week 30 · 2027.5.30 (일) — mkfs (호스트 도구)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **🤖 Claude (주중):** `mkfs.c` → C++17 (호스트에서 도는 프로그램이라 표준 라이브러리 사용 가능)
- **👤 Ryu (일요일 3h):** 디스크 이미지 레이아웃 (boot / super / log / inode / bitmap / data) 그림 그리기

</div>

<div class="session" data-session="31" markdown="1">

### Week 31 · 2027.6.6 (일) — 커널 100% C++ + 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **🤖 Claude (주중):** 남은 커널 C 파일 정리, QEMU + VirtualBox 에서 `usertests` 전체 실행
- **👤 Ryu (일요일 3h):** Phase 5 리뷰 · 책 **Ch.7** Summary
- 🎯 **마일스톤:** 커널에 C 파일이 하나도 남지 않는다 (어셈블리 제외)

</div>

<div style="margin-top: 100px;"></div>

## Phase 6 · 사용자 프로그램 → v1.0

*Week 32–35 · 2027.6.13 ~ 2027.7.4 · ulib, sh, 유틸리티, usertests*

<div class="session" data-session="32" markdown="1">

### Week 32 · 2027.6.13 (일) — 사용자 라이브러리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **🤖 Claude (주중):** `ulib.c`, `printf.c`, `umalloc.c` → C++ (`usys.S` 는 그대로)
- **👤 Ryu (일요일 3h):** 사용자 프로그램이 시스템 콜을 부르는 경로 복습 (Ch.0, Ch.3)

</div>

<div class="session" data-session="33" markdown="1">

### Week 33 · 2027.6.20 (일) — init 과 셸

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **🤖 Claude (주중):** `init.c`, `sh.c` → C++ (셸 파서의 명령 구조체를 클래스 계층으로)
- **👤 Ryu (일요일 3h):** 책 **Ch.0** 셸 절 다시 읽기 · 파이프·리다이렉션이 `fork`/`exec`/`dup` 으로 구현되는 방식

</div>

<div class="session" data-session="34" markdown="1">

### Week 34 · 2027.6.27 (일) — 유틸리티

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **🤖 Claude (주중):** `ls`, `cat`, `echo`, `grep`, `wc`, `mkdir`, `rm`, `ln`, `kill`, `zombie`, `forktest`, `stressfs` → C++
- **👤 Ryu (일요일 3h):** 작은 프로그램 몇 개를 골라 원본과 비교 리뷰

</div>

<div class="session" data-session="35" markdown="1">

### Week 35 · 2027.7.4 (일) — usertests + v1.0

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **🤖 Claude (주중):** `usertests.c` → C++ · 전체 테스트 통과 확인 · 태그 `v1.0-x86_32`
- **👤 Ryu (일요일 3h):** QEMU + VirtualBox 에서 직접 셸을 써 보기 · Phase 1–6 회고
- 🎯 **마일스톤 v1.0:** xv6 전체가 C++ (어셈블리 제외), QEMU + VirtualBox 에서 동작

</div>

<div style="margin-top: 100px;"></div>

## Phase 7 · x86-64 → v2.0

*Week 36–42 · 2027.7.11 ~ 2027.8.22 · 롱 모드, 4단계 페이징, 64비트 트랩*

<div class="session" data-session="36" markdown="1">

### Week 36 · 2027.7.11 (일) — x86-64 설계

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **🤖 Claude (주중):** 64비트 이식 설계 문서 작성: 4단계 페이지 테이블, 주소 공간 배치, 호출 규약, 시스템 콜 진입 방식
- **👤 Ryu (일요일 3h):** 설계 문서 리뷰 · 32비트와 64비트 페이징 차이 공부
- 💡 왜 64비트가 필요한가: UEFI 는 64비트 모드로 커널에 제어를 넘기고, 최신 PC 의 장치 주소(프레임버퍼, xHCI)는 4GB 위에 있을 수 있다

</div>

<div class="session" data-session="37" markdown="1">

### Week 37 · 2027.7.18 (일) — 롱 모드 진입

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="37"> 완료</label>

- **🤖 Claude (주중):** 부트 코드에서 32비트 → 64비트 전환 (임시 페이지 테이블, EFER, CR4.PAE)
- **👤 Ryu (일요일 3h):** Intel/AMD 롱 모드 전환 절차 공부 · 전환 코드 리뷰

</div>

<div class="session" data-session="38" markdown="1">

### Week 38 · 2027.7.25 (일) — 64비트 가상 메모리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="38"> 완료</label>

- **🤖 Claude (주중):** `vm` 을 4단계 페이지 테이블로 재작성
- **👤 Ryu (일요일 3h):** PML4 → PDPT → PD → PT 변환을 손으로 계산

</div>

<div class="session" data-session="39" markdown="1">

### Week 39 · 2027.8.1 (일) — 64비트 트랩과 컨텍스트 스위치

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="39"> 완료</label>

- **🤖 Claude (주중):** IDT 64비트 게이트, `trapasm`, `swtch` 재작성 · 트랩 프레임 구조 변경
- **👤 Ryu (일요일 3h):** 64비트에서 인터럽트 시 스택에 쌓이는 값 정리

</div>

<div class="session" data-session="40" markdown="1">

### Week 40 · 2027.8.8 (일) — 64비트 시스템 콜과 사용자 프로그램

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="40"> 완료</label>

- **🤖 Claude (주중):** 시스템 콜 인자 전달을 레지스터 방식으로 · 사용자 프로그램 64비트 빌드
- **👤 Ryu (일요일 3h):** 32비트(스택) vs 64비트(레지스터) 인자 전달 비교

</div>

<div class="session" data-session="41" markdown="1">

### Week 41 · 2027.8.15 (일) — v2.0: 64비트로 QEMU + VirtualBox

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="41"> 완료</label>

- **🤖 Claude (주중):** `usertests` 전체 통과 · 태그 `v2.0-x86_64`
- **👤 Ryu (일요일 3h):** Phase 7 리뷰
- 🎯 **마일스톤 v2.0:** 64비트 xv6-cpp 가 QEMU + VirtualBox 에서 동작

</div>

<div class="session" data-session="42" markdown="1">

### Week 42 · 2027.8.22 (일) — 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="42"> 완료</label>

- **🤖 Claude (주중):** 밀린 부분 정리
- **👤 Ryu (일요일 3h):** MikanOS 책의 UEFI 부트 로더 장 복습 (Phase 8 준비)

</div>

<div style="margin-top: 100px;"></div>

## Phase 8 · UEFI 베어메탈 → v3.0

*Week 43–52 · 2027.8.29 ~ 2027.10.31 · UEFI 로더, 프레임버퍼, ACPI, PCI, xHCI USB 키보드*

<div class="session" data-session="43" markdown="1">

### Week 43 · 2027.8.29 (일) — UEFI 부트 로더

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="43"> 완료</label>

- **🤖 Claude (주중):** C++ 로 작은 UEFI 로더 작성 (MikanOS 방식): 커널 ELF + 파일 시스템 이미지를 메모리에 올리고, GOP 프레임버퍼·메모리 맵·ACPI RSDP 를 넘긴 뒤 `ExitBootServices`
- **👤 Ryu (일요일 3h):** UEFI 부팅 흐름 공부 · QEMU + OVMF 에서 부팅 확인

</div>

<div class="session" data-session="44" markdown="1">

### Week 44 · 2027.9.5 (일) — 메모리 맵과 램디스크

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="44"> 완료</label>

- **🤖 Claude (주중):** 고정된 `PHYSTOP` 대신 UEFI 메모리 맵으로 물리 메모리 초기화 · 디스크 대신 램디스크 (`memide` 확장)
- **👤 Ryu (일요일 3h):** 램디스크를 쓰는 이유 정리 (최신 PC 는 IDE 가 없고 NVMe/AHCI 드라이버는 범위 밖)
- ⚠️ 베어메탈에서는 파일 변경이 재부팅 후 사라진다. 영구 저장(AHCI/NVMe)은 2년차 목표

</div>

<div class="session" data-session="45" markdown="1">

### Week 45 · 2027.9.12 (일) — 프레임버퍼 콘솔

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="45"> 완료</label>

- **🤖 Claude (주중):** CGA 텍스트 모드 대신 비트맵 폰트로 프레임버퍼에 글자 그리기
- **👤 Ryu (일요일 3h):** 픽셀 형식 (RGB/BGR), 스크롤 구현 리뷰

</div>

<div class="session" data-session="46" markdown="1">

### Week 46 · 2027.9.19 (일) — ACPI

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="46"> 완료</label>

- **🤖 Claude (주중):** RSDP → XSDT → MADT 파싱으로 `mp.c` 교체 (CPU 목록, IOAPIC 주소) · ACPI PM 타이머로 LAPIC 타이머 보정
- **👤 Ryu (일요일 3h):** ACPI 테이블 구조 공부

</div>

<div class="session" data-session="47" markdown="1">

### Week 47 · 2027.9.26 (일) — PCI 열거

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="47"> 완료</label>

- **🤖 Claude (주중):** MCFG 테이블로 PCIe 설정 공간 접근, 장치 목록 출력
- **👤 Ryu (일요일 3h):** PCI 설정 공간과 BAR 개념 공부

</div>

<div class="session" data-session="48" markdown="1">

### Week 48 · 2027.10.3 (일) — xHCI 1: 컨트롤러 초기화

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="48"> 완료</label>

- **🤖 Claude (주중):** xHCI 컨트롤러 리셋, 링(ring) 구조 설정 (MikanOS 의 USB 드라이버를 참고)
- **👤 Ryu (일요일 3h):** xHCI 링 구조 (command / event / transfer ring) 공부

</div>

<div class="session" data-session="49" markdown="1">

### Week 49 · 2027.10.10 (일) — xHCI 2: USB 키보드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="49"> 완료</label>

- **🤖 Claude (주중):** USB 장치 열거, HID 부트 프로토콜 키보드 입력 → 콘솔 입력으로 연결
- **👤 Ryu (일요일 3h):** USB 열거 순서 리뷰
- ⚠️ 1년 계획에서 가장 위험한 구간. 밀리면 Week 52 회고 주를 여기에 쓰고, 회고는 짧게 한다

</div>

<div class="session" data-session="50" markdown="1">

### Week 50 · 2027.10.17 (일) — VirtualBox UEFI 모드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="50"> 완료</label>

- **🤖 Claude (주중):** VirtualBox 를 EFI 모드로 설정해 부팅 · USB 부팅용 FAT32 ESP 이미지 만들기
- **👤 Ryu (일요일 3h):** VirtualBox UEFI 부팅 확인

</div>

<div class="session" data-session="51" markdown="1">

### Week 51 · 2027.10.24 (일) — 실제 PC 부팅

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="51"> 완료</label>

- **🤖 Claude (주중):** USB 스틱으로 실제 PC 부팅 · 시리얼 포트가 없으므로 프레임버퍼 로그로 디버깅
- **👤 Ryu (일요일 3h):** 실제 PC 에서 부팅 시도, 화면 사진으로 결과 공유
- 🎯 **마일스톤 v3.0:** 실제 UEFI PC 에서 xv6-cpp 셸이 뜨고 USB 키보드로 명령을 친다

</div>

<div class="session" data-session="52" markdown="1">

### Week 52 · 2027.10.31 (일) — 1년 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="52"> 완료</label>

- **🤖 Claude (주중):** `v3.0-uefi` 태그 · README 정리
- **👤 Ryu (일요일 3h):** 회고 글 작성: C → C++ 로 바꾸며 배운 것, 가장 어려웠던 버그, 2년차 목표 (AHCI/NVMe, 멀티코어 베어메탈 등)

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
