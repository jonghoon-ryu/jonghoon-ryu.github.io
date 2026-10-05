---
layout: default
title: xv6 계획
permalink: /xv6/plan/
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
# 계획

**2026년 11월 7일 (토) 시작 · 토요일 2시간 + 일요일 2시간 · 36회 (18주) · 2027년 3월 7일 (일) 마무리 예정**

주말 시간 배분 : **토요일 = [계산 이론 & Gödel](/learning-cs/computation-theory/study-plan/) 2시간 + xv6 2시간**, **일요일 = xv6 2시간**.

[목표](/xv6/goal/) 의 2단계 : 부팅 스켈레톤에서 출발해서, C 버전의 한 부분씩을 C++ 로 옮겨 되살린다.

<div style="margin-top: 100px;"></div>

## 진행 방식

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:20%"><col style="width:80%"></colgroup>
  <thead><tr><th>누가</th><th>할 일</th></tr></thead>
  <tbody>
    <tr><td>🤖 Claude<br>(세션 전)</td><td>그 회차 부분을 C 버전 (<code>main</code> 브랜치) 에서 가져와 C++ 로 변환 · 빌드 · QEMU 와 VirtualBox 에서 부팅 확인 · 로컬 커밋<br>리뷰 노트 <code>docs/review/stepNN.md</code> : C ↔ C++ 대응, 바뀐 이유, 봐야 할 곳</td></tr>
    <tr><td>👤 Ryu<br>(토·일 2h)</td><td>① 리뷰 노트를 보며 C 판과 C++ 판을 나란히 읽기 (~1h)<br>② 직접 띄워 보기, 같은 내용의 xv6 책 읽기 (~1h)<br>③ 질문 · 수정 요청 → 승인하면 GitHub 에 push</td></tr>
  </tbody>
</table>
</div>

- 시작 방법 : Claude 에게 **"xv6 step N 진행해"** 라고 말하면 된다
- 한 회차를 놓치면 몰아서 하지 않고 한 칸씩 민다. 여유 회차 (20, 33) 에서 흡수
- **push 는 Ryu 의 리뷰와 승인 후에만** 한다

<div style="margin-top: 100px;"></div>

## 자료

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:25%"><col style="width:75%"></colgroup>
  <thead><tr><th>역할</th><th>자료</th></tr></thead>
  <tbody>
    <tr><td>코드</td><td><a href="https://github.com/jonghoon-ryu/xv6-x86_64">github.com/jonghoon-ryu/xv6-x86_64</a> · <code>main</code> = C 버전, <code>cpp</code> = C++ 작업 중</td></tr>
    <tr><td>원본</td><td><a href="https://github.com/mit-pdos/xv6-riscv">mit-pdos/xv6-riscv</a></td></tr>
    <tr><td>책</td><td><a href="https://pdos.csail.mit.edu/6.1810/2025/xv6/book-riscv-rev5.pdf"><em>xv6: a simple, Unix-like teaching operating system</em>, RISC-V rev5</a> (무료 PDF)</td></tr>
    <tr><td>x86-64 참고</td><td><a href="https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html">Intel SDM</a> Vol.3 · <a href="https://wiki.osdev.org/">OSDev Wiki</a></td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 진도

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 36</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Part 1 · 부팅과 콘솔

*책 Ch.1–2 · 화면에 printk 가 찍히기까지*

<div class="session" data-session="1" markdown="1">

### Step 1 · 2026.11.7 (토) — 스켈레톤 둘러보기

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- **🤖 Claude :** 리뷰 노트 <code>docs/review/step01.md</code> : 로더 → <code>entry.S</code> → <code>start.cpp</code> → <code>main.cpp</code> 흐름, Makefile 의 C++ 옵션, <code>kernel.ld</code> 의 <code>.init_array</code>
- **👤 Ryu (2h) :** 노트 보며 코드 읽기 · <code>make qemu</code> / <code>make vbox</code> 직접 띄우기 · gdb 로 <code>_entry</code> → <code>main</code> 따라가기 · 책 <b>Ch.1</b>

</div>

<div class="session" data-session="2" markdown="1">

### Step 2 · 2026.11.8 (일) — uart.cpp, string.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- **🤖 Claude :** 16550 UART 드라이버 (출력만, 폴링) · <code>memset</code> / <code>memmove</code> / <code>strlen</code> 등
- **👤 Ryu (2h) :** C 판 <code>uart.c</code> 와 나란히 읽기 · 책 <b>Ch.2</b> 앞부분

</div>

<div class="session" data-session="3" markdown="1">

### Step 3 · 2026.11.14 (토) — printk.cpp, console.cpp (출력)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- **🤖 Claude :** <code>printk("%d %x %p %s")</code>, <code>panic()</code> · 콘솔 출력 경로
- **👤 Ryu (2h) :** 가변 인자와 포맷 처리가 C++ 에서 어떻게 바뀌었는지 보기 · 책 <b>Ch.2</b>

</div>

<div class="session" data-session="4" markdown="1">

### Step 4 · 2026.11.15 (일) — fbcons.cpp, font.h

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- **🤖 Claude :** 화면 콘솔 : Spleen 폰트, 커서, 스크롤 · 손으로 그린 "xv6" 글자를 대체
- **👤 Ryu (2h) :** VirtualBox 창에서 부팅 메시지 확인 · 책 <b>Ch.2</b> 끝
- 🎯 **이정표 : 화면에 printk 글자**

</div>

<div style="margin-top: 100px;"></div>

## Part 2 · 메모리

*책 Ch.3 · 커널이 자기 페이지 테이블을 갖기까지*

<div class="session" data-session="5" markdown="1">

### Step 5 · 2026.11.21 (토) — spinlock.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- **🤖 Claude :** 최소한의 <code>struct cpu</code>, <code>push_off</code> / <code>pop_off</code>, RAII <code>LockGuard</code>
- **👤 Ryu (2h) :** <code>acquire</code>/<code>release</code> 짝이 <code>LockGuard</code> 로 바뀌는 것 보기 · 책 <b>Ch.6</b> 앞부분

</div>

<div class="session" data-session="6" markdown="1">

### Step 6 · 2026.11.22 (일) — kalloc.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- **🤖 Claude :** UEFI 메모리 맵으로 빈 페이지 목록 만들기 · "N pages free" 출력
- **👤 Ryu (2h) :** 책 <b>Ch.3</b> 3.5 (물리 메모리 할당)

</div>

<div class="session" data-session="7" markdown="1">

### Step 7 · 2026.11.28 (토) — vm.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- **🤖 Claude :** 4단계 페이지 테이블 : <code>walk</code>, <code>mappages</code>
- **👤 Ryu (2h) :** RISC-V Sv39 (3단계) 와 x86-64 (4단계) 비교 · 책 <b>Ch.3</b> 3.1–3.3

</div>

<div class="session" data-session="8" markdown="1">

### Step 8 · 2026.11.29 (일) — vm.cpp ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- **🤖 Claude :** <code>kvmmake</code>, <code>kvminithart</code> (CR3 교체)
- **👤 Ryu (2h) :** 커널 페이지 테이블로 바꾼 뒤에도 화면이 그대로 나오는지 · 책 <b>Ch.3</b> 끝
- 🎯 **이정표 : 커널 자신의 페이지 테이블**

</div>

<div style="margin-top: 100px;"></div>

## Part 3 · 트랩과 인터럽트

*책 Ch.4–5 · 처음으로 화면이 "움직이기" 까지*

<div class="session" data-session="9" markdown="1">

### Step 9 · 2026.12.5 (토) — acpi.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- **🤖 Claude :** RSDP → XSDT → MADT 읽기, CPU 와 IOAPIC 목록 출력
- **👤 Ryu (2h) :** ACPI 표 구조 · OSDev Wiki 의 MADT 항목

</div>

<div class="session" data-session="10" markdown="1">

### Step 10 · 2026.12.6 (일) — trap.cpp ①, kernelvec.S

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- **🤖 Claude :** GDT, IDT, 예외 처리 → 일부러 0 으로 나눠서 panic 메시지 확인
- **👤 Ryu (2h) :** 책 <b>Ch.4</b> (트랩) · RISC-V <code>stvec</code> ↔ x86 IDT

</div>

<div class="session" data-session="11" markdown="1">

### Step 11 · 2026.12.12 (토) — lapic.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **🤖 Claude :** LAPIC 타이머 인터럽트, <code>ticks</code> · 화면에 초 단위 카운터
- **👤 Ryu (2h) :** <code>hlt</code> 가 이제는 타이머가 깨울 때까지만 잔다 · 책 <b>Ch.5</b> 5.4
- 🎯 **이정표 : 화면이 움직인다 (타이머)**

</div>

<div class="session" data-session="12" markdown="1">

### Step 12 · 2026.12.13 (일) — ioapic.cpp, console.cpp (입력)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **🤖 Claude :** IOAPIC, UART 인터럽트, <code>consoleintr</code> · 시리얼로 친 글자 에코
- **👤 Ryu (2h) :** 책 <b>Ch.5</b> 5.1–5.3 (콘솔 입력)

</div>

<div class="session" data-session="13" markdown="1">

### Step 13 · 2026.12.19 (토) — kbd.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **🤖 Claude :** PS/2 키보드 · VirtualBox 창에서 타이핑
- **👤 Ryu (2h) :** 책 <b>Ch.5</b> 끝
- 🎯 **이정표 : 키보드 입력**

</div>

<div style="margin-top: 100px;"></div>

## Part 4 · 프로세스

*책 Ch.4, 7 · 첫 사용자 프로그램과 시스템 콜*

<div class="session" data-session="14" markdown="1">

### Step 14 · 2026.12.20 (일) — proc.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **🤖 Claude :** <code>struct proc</code>, 프로세스 표, 커널 스택
- **👤 Ryu (2h) :** 책 <b>Ch.7</b> 앞부분

</div>

<div class="session" data-session="15" markdown="1">

### Step 15 · 2026.12.26 (토) — swtch.S, scheduler

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **🤖 Claude :** 문맥 교환 · 커널 스레드 두 개가 번갈아 출력
- **👤 Ryu (2h) :** <code>swtch</code> 에서 저장하는 레지스터 (RISC-V ↔ x86-64) · 책 <b>Ch.7</b> 7.1–7.4

</div>

<div class="session" data-session="16" markdown="1">

### Step 16 · 2026.12.27 (일) — sleep / wakeup, sleeplock.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **🤖 Claude :** 잠들기와 깨우기, sleep lock
- **👤 Ryu (2h) :** 책 <b>Ch.7</b> 7.5–7.9

</div>

<div class="session" data-session="17" markdown="1">

### Step 17 · 2027.1.2 (토) — trampoline.S, 사용자 모드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **🤖 Claude :** 사용자 페이지 테이블, <code>usertrap</code> / <code>usertrapret</code> · 임시 initcode 를 사용자 모드로 실행
- **👤 Ryu (2h) :** TSS, <code>iretq</code>, CPUTABLES 페이지 · 책 <b>Ch.4</b> 4.2–4.4

</div>

<div class="session" data-session="18" markdown="1">

### Step 18 · 2027.1.3 (일) — syscall.cpp, sysproc.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **🤖 Claude :** <code>int $64</code> 시스템 콜 · <code>fork</code> / <code>exit</code> / <code>wait</code> / <code>getpid</code> / <code>sbrk</code> / <code>uptime</code>
- **👤 Ryu (2h) :** 책 <b>Ch.4</b> 4.3–4.5
- 🎯 **이정표 : 첫 시스템 콜**

</div>

<div class="session" data-session="19" markdown="1">

### Step 19 · 2027.1.9 (토) — entryother.S, 다중 CPU

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **🤖 Claude :** <code>startothers</code> 로 나머지 CPU 깨우기 · <code>CPUS=4</code>
- **👤 Ryu (2h) :** AP 부팅 (16비트 → 64비트) 과정 · 책 <b>Ch.6</b> 6.1–6.3

</div>

<div class="session" data-session="20" markdown="1">

### Step 20 · 2027.1.10 (일) — 여유

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **🤖 Claude :** 밀린 단계 마무리
- **👤 Ryu (2h) :** 밀린 리뷰 · 지금까지의 C++ 코드 훑어보기

</div>

<div style="margin-top: 100px;"></div>

## Part 5 · 파일 시스템

*책 Ch.8 · /init 이 실행되기까지*

<div class="session" data-session="21" markdown="1">

### Step 21 · 2027.1.16 (토) — mkfs (호스트 C++17), ramdisk.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **🤖 Claude :** 진짜 <code>fs.img</code> 만들기 · 램디스크에서 슈퍼블록 읽어 출력
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.1–8.2 (디스크 구조)

</div>

<div class="session" data-session="22" markdown="1">

### Step 22 · 2027.1.17 (일) — bio.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **🤖 Claude :** 버퍼 캐시
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.3

</div>

<div class="session" data-session="23" markdown="1">

### Step 23 · 2027.1.23 (토) — log.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **🤖 Claude :** 로그 (crash 복구)
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.4–8.6

</div>

<div class="session" data-session="24" markdown="1">

### Step 24 · 2027.1.24 (일) — fs.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **🤖 Claude :** 블록 할당, inode
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.7–8.10

</div>

<div class="session" data-session="25" markdown="1">

### Step 25 · 2027.1.30 (토) — fs.cpp ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **🤖 Claude :** 디렉터리, 경로 찾기
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.11–8.12

</div>

<div class="session" data-session="26" markdown="1">

### Step 26 · 2027.1.31 (일) — file.cpp, pipe.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **🤖 Claude :** 파일 표, 파이프
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.13 · <b>Ch.1</b> 파이프 다시 보기

</div>

<div class="session" data-session="27" markdown="1">

### Step 27 · 2027.2.6 (토) — sysfile.cpp, exec.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **🤖 Claude :** 파일 시스템 콜, ELF 로딩 · <code>/init</code> 실행
- **👤 Ryu (2h) :** 책 <b>Ch.3</b> 3.8 (exec)
- 🎯 **이정표 : /init 실행**

</div>

<div style="margin-top: 100px;"></div>

## Part 6 · 사용자 프로그램

*셸이 다시 뜨고 usertests 가 통과하기까지*

<div class="session" data-session="28" markdown="1">

### Step 28 · 2027.2.7 (일) — 사용자 라이브러리, init, sh

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **🤖 Claude :** <code>ulib</code>, <code>printf</code>, <code>umalloc</code>, <code>usys</code> 를 C++ 로 · <code>init</code>, <code>sh</code>
- **👤 Ryu (2h) :** 셸에서 <code>ls</code>, 파이프 써 보기 · 책 <b>Ch.1</b> 다시 보기
- 🎯 **이정표 : 셸 ($) 복귀**

</div>

<div class="session" data-session="29" markdown="1">

### Step 29 · 2027.2.13 (토) — 사용자 프로그램 ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **🤖 Claude :** <code>cat</code>, <code>echo</code>, <code>ls</code>, <code>grep</code>, <code>wc</code>
- **👤 Ryu (2h) :** C 판과 C++ 판 나란히 비교

</div>

<div class="session" data-session="30" markdown="1">

### Step 30 · 2027.2.14 (일) — 사용자 프로그램 ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **🤖 Claude :** <code>mkdir</code>, <code>rm</code>, <code>ln</code>, <code>kill</code>, <code>forktest</code>, <code>zombie</code> 등

</div>

<div class="session" data-session="31" markdown="1">

### Step 31 · 2027.2.20 (토) — usertests ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **🤖 Claude :** usertests 앞 절반 변환
- **👤 Ryu (2h) :** 실패하는 테스트가 있으면 함께 원인 보기

</div>

<div class="session" data-session="32" markdown="1">

### Step 32 · 2027.2.21 (일) — usertests ②, grind

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **🤖 Claude :** 나머지 변환 · <code>usertests</code> 전체 통과 · <code>grind</code>
- **👤 Ryu (2h) :** 책 <b>Ch.9</b> (동시성 다시 보기)
- 🎯 **이정표 : usertests 전체 통과**

</div>

<div class="session" data-session="33" markdown="1">

### Step 33 · 2027.2.27 (토) — 여유

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **🤖 Claude :** 밀린 단계 마무리
- **👤 Ryu (2h) :** 밀린 리뷰

</div>

<div style="margin-top: 100px;"></div>

## Part 7 · 마무리

*C++ 다듬기, 실제 PC, 회고*

<div class="session" data-session="34" markdown="1">

### Step 34 · 2027.2.28 (일) — C++ 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **🤖 Claude :** <code>defs.h</code> 를 모듈별 헤더로 · <code>param.h</code> / <code>memlayout.h</code> / <code>x86.h</code> 의 매크로를 <code>constexpr</code> / <code>inline</code> 으로
- **👤 Ryu (2h) :** 남은 C 흔적 찾기

</div>

<div class="session" data-session="35" markdown="1">

### Step 35 · 2027.3.6 (토) — 실제 PC

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **🤖 Claude :** GPT 파티션이 있는 <code>usb.img</code> · USB 메모리로 실제 PC 부팅
- **👤 Ryu (2h) :** Secure Boot 끄고 USB 부팅 · 화면 콘솔 확인 (키보드는 PS/2 가 없으면 안 됨)

</div>

<div class="session" data-session="36" markdown="1">

### Step 36 · 2027.3.7 (일) — v1.0-cpp, 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **🤖 Claude :** 태그 <code>v1.0-cpp</code>
- **👤 Ryu (2h) :** 회고 글 : C → C++ 로 바꾸며 배운 것, 다음 목표

</div>

<script>
(function () {
  var STORAGE_KEY = 'xv6-cpp-steps-progress';

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
