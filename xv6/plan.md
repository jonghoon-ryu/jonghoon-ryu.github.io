---
layout: default
title: xv6 진행 현황
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
# 진행 현황

**2026년 11월 7일 (토) 시작 · 토요일 2시간 + 일요일 2시간 · 42회 · 2027년 3월 28일 (일) 마무리 예정**

주말 시간 배분 : **토요일·일요일 각각 = [계산 이론 & Gödel](/learning-cs/computation-theory/study-plan/) 2시간 + xv6 2시간**.

[목표](/xv6/goal/) 의 2단계 : 부팅 스켈레톤에서 출발해서, C 버전의 한 부분씩을 C++ 로 옮겨 되살린다.

<div style="margin-top: 100px;"></div>

## 지금까지 (2026.10.7)

[목표](/xv6/goal/) 에 견주어 지금 어디까지 왔나. 태그마다 코드가 어떻게 바뀌었는지는 [튜토리얼](/xv6/tutorial/) 에 있다.

| 판 | QEMU | VirtualBox | 실제 PC (베어본) |
|---|---|---|---|
| xv6-riscv (MIT 원본) | ✅ `-machine virt` 에서만 | ✗ (RISC-V 가 아님) | ✗ (공식 지원 없음) |
| xv6-x86_64 C 판 (`v0.2-x86_64-c`) | ✅ 셸, `usertests` 통과 | ✅ 셸, `usertests` 통과 | 시험 안 함. 키보드가 PS/2 뿐이라 베어본에서는 입력 불가 |
| xv6-x86_64 C++ 판, 지금 (`step-10`) | ✅ 부팅, 화면, 키보드 | ✅ 부팅, 화면, 키보드 | ✅ **부팅, 화면, USB 키보드** (2026.10.7) |
| **최종 목표 (`v1.0-cpp`)** | 셸, `usertests` 통과 | 셸, `usertests` 통과 | **셸, `usertests` 통과** |

### 1단계 : RISC-V → x86-64 포팅, C (완료)

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
v0.1 ──(+ 화면 콘솔, 키보드)──▶ v0.2 ──(C++ 로 한 단계씩)──▶ step-01 … step-10 … v1.0-cpp
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

### 2단계 : C → C++ 번역 (진행 중)

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

### 남은 일 (일정 밖)

- USB : 부팅 뒤에 허브에 꽂은 장치, 키 반복 (타이머 필요), Caps Lock 불, 폴링 대신 xHCI 인터럽트 (Step 19 에서)
- 실제 PC (선택) : 앞면 소켓 (high speed 허브 뒤일 수 있음) 의 키보드로 Transaction Translator 경로 시험
- 정리 : 저장소의 RISC-V 용 CI (<code>.github/workflows/test.yml</code>), <code>make qemu-gdb</code> 를 x86-64 용으로, 블로그의 안 쓰는 그림 <code>xv6-cpp-skeleton.png</code>

<div style="margin-top: 100px;"></div>

## 진행 방식

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:20%"><col style="width:80%"></colgroup>
  <thead><tr><th>누가</th><th>할 일</th></tr></thead>
  <tbody>
    <tr><td>🤖 Claude<br>(세션 전)</td><td>그 회차 부분을 C 버전 (<code>main</code> 브랜치) 에서 가져와 C++ 로 변환 · 빌드 · QEMU 와 VirtualBox 에서 부팅 확인 · 로컬 커밋<br>변환 기록 <a href="https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/cpp-conversion.md"><code>docs/cpp-conversion.md</code></a> (+ PDF) 에 그 단계의 장 추가 : C ↔ C++ 대응, 바뀐 이유, 플랫폼별 차이, 시험 결과<br>단계가 끝나면 태그 <code>step-NN</code> (그 단계의 코드로 돌아가기 : <code>git checkout step-NN</code>)</td></tr>
    <tr><td>👤 Ryu<br>(토·일 2h)</td><td>① 리뷰 노트를 보며 C 판과 C++ 판을 나란히 읽기 (~1h)<br>② 직접 띄워 보기, 같은 내용의 xv6 책 읽기 (~1h)<br>③ 그 단계의 <code>usb.img</code> 를 실제 PC 에서 부팅<br>④ 질문 · 수정 요청 → 승인하면 GitHub 에 push</td></tr>
  </tbody>
</table>
</div>

- 시작 방법 : Claude 에게 **"xv6 step N 진행해"** 라고 말하면 된다
- **2026.10.5 업데이트** : Step 1–5 코드는 미리 완성했다 (태그 <code>step-01</code> ~ <code>step-05</code>). Step 5 (키보드 폴링 데모) 는 이때 새로 넣은 회차다. 이 회차들은 완성된 코드를 리뷰하는 시간으로 쓴다
- **2026.10.7 업데이트** : 실제 PC (베어본) 에 PS/2 컨트롤러가 없어서 키보드가 안 됐다. **USB 키보드 드라이버를 Step 6–10 으로 Step 5 뒤에 넣었다** (코드 완료, 실제 PC 에서 입력 확인). 원래의 Step 6–37 은 Step 11–42 가 되고, 마무리가 2027.3.13 에서 3.28 로 밀렸다
- **실제 PC 에서 돼야 그 단계가 끝난다.** QEMU 와 VirtualBox 는 개발 도구다
- 한 회차를 놓치면 몰아서 하지 않고 한 칸씩 민다. 여유 회차 (26, 39) 에서 흡수
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
  <span>Progress: <span id="progress-count">0 / 42</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Part 1 · 부팅과 콘솔

*책 Ch.1–2 · 화면에 printk 가 찍히기까지*

<div class="session" data-session="1" markdown="1">

### Step 1 · 2026.11.7 (토) — 스켈레톤 둘러보기

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- ✅ **코드 완료 (2026.10.5)** · 태그 [<code>step-01</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-01) · 이 회차는 리뷰

- **🤖 Claude :** 변환 기록의 Step 1 장 : 로더 → <code>entry.S</code> → <code>start.cpp</code> → <code>main.cpp</code> 흐름, Makefile 의 C++ 옵션, <code>kernel.ld</code> 의 <code>.init_array</code>
- **👤 Ryu (2h) :** 노트 보며 코드 읽기 · <code>make qemu</code> / <code>make vbox</code> 직접 띄우기 · gdb 로 <code>_entry</code> → <code>main</code> 따라가기 · 책 <b>Ch.1</b>

</div>

<div class="session" data-session="2" markdown="1">

### Step 2 · 2026.11.8 (일) — uart.cpp, string.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- ✅ **코드 완료 (2026.10.5)** · 태그 [<code>step-02</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-02) · 이 회차는 리뷰

- **🤖 Claude :** 16550 UART 드라이버 (출력만, 폴링) · <code>memset</code> / <code>memmove</code> / <code>strlen</code> 등
- **👤 Ryu (2h) :** C 판 <code>uart.c</code> 와 나란히 읽기 · 책 <b>Ch.2</b> 앞부분

</div>

<div class="session" data-session="3" markdown="1">

### Step 3 · 2026.11.14 (토) — printk.cpp, console.cpp (출력)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- ✅ **코드 완료 (2026.10.5)** · 태그 [<code>step-03</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-03) · 이 회차는 리뷰

- **🤖 Claude :** <code>printk("%d %x %p %s")</code>, <code>panic()</code> · 콘솔 출력 경로
- **👤 Ryu (2h) :** 가변 인자와 포맷 처리가 C++ 에서 어떻게 바뀌었는지 보기 · 책 <b>Ch.2</b>

</div>

<div class="session" data-session="4" markdown="1">

### Step 4 · 2026.11.15 (일) — fbcons.cpp, font.h

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- ✅ **코드 완료 (2026.10.5)** · 태그 [<code>step-04</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-04) · 이 회차는 리뷰

- **🤖 Claude :** 화면 콘솔 : Spleen 폰트, 커서, 스크롤 · 손으로 그린 "xv6" 글자를 대체
- **👤 Ryu (2h) :** VirtualBox 창에서 부팅 메시지 확인 · 책 <b>Ch.2</b> 끝
- 🎯 **이정표 : 화면에 printk 글자**

</div>

<div class="session" data-session="5" markdown="1">

### Step 5 · 2026.11.21 (토) — 키보드 폴링 데모

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- ✅ **코드 완료 (2026.10.5)** · 태그 [<code>step-05</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-05) · 이 회차는 리뷰

- **🤖 Claude :** <code>kbd.cpp</code>, <code>kbd.h</code> (키 표를 <code>constexpr</code> 로), <code>consoleintr()</code>, <code>uartintr()</code> · 인터럽트 없이 <code>main()</code> 이 키보드와 시리얼을 계속 물어보는 (폴링) 루프
- **👤 Ryu (2h) :** VirtualBox 창에서 쳐 보기 · 폴링과 인터럽트의 차이 (CPU 100% vs 0%) · 원래 계획에서는 키보드 인터럽트 (지금 Step 19) 에서야 키보드가 돌아온다는 점
- 🎯 **이정표 : 치면 화면에 나온다**

</div>

<div style="margin-top: 100px;"></div>

## Part 2 · USB 키보드 (실제 PC)

*책에 없음 · xHCI 1.2, USB 2.0, USB HID 1.11 명세 · 실제 PC 에 PS/2 컨트롤러가 없어서 새로 넣은 부분 (2026.10.7)*

![실제 PC 에서 USB 키보드로 친 글 : "Hi, claude / It looks like it works!"](/assets/image/xv6-realpc-usb-keyboard.jpg)

<div class="session" data-session="6" markdown="1">

### Step 6 · 2026.11.22 (일) — PCI 버스, 예외 화면

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- ✅ **코드 완료 (2026.10.7)** · 태그 [<code>step-06</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-06) · 튜토리얼 [<code>docs/tutorial/step06.md</code>](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/tutorial/step06.md) · 이 회차는 리뷰

- **🤖 Claude :** <code>pci.cpp</code> : PCI 설정 공간 (포트 <code>0xCF8</code>/<code>0xCFC</code>), 종류별로 장치 찾기, PCI 장치 목록 · <code>earlytrap.cpp</code> : CPU 예외를 화면에 (실제 PC 에서 조용히 재부팅하지 않게) · PS/2 루프를 16바이트로 제한 (실제 PC 의 없는 컨트롤러가 <code>0x55</code> 로 읽힘)
- **👤 Ryu (2h) :** <code>make qemu USB=1</code> 의 PCI 목록을 <code>lspci -nn</code> 과 비교 · 일부러 0 으로 나눠 보기 (<code>1 / zero</code> 는 왜 예외가 안 날까)

</div>

<div class="session" data-session="7" markdown="1">

### Step 7 · 2026.11.28 (토) — xHCI 컨트롤러 시작

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- ✅ **코드 완료 (2026.10.7)** · 태그 [<code>step-07</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-07) · 튜토리얼 [<code>docs/tutorial/step07.md</code>](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/tutorial/step07.md) · 이 회차는 리뷰

- **🤖 Claude :** <code>xhci.cpp</code> : 펌웨어에게서 넘겨받기, 리셋, 명령·이벤트 링 (cycle 비트), scratchpad, 포트 리셋 · <code>#if</code> 가 아니라 실행 중에 PCI 에서 찾는다
- **👤 Ryu (2h) :** 링과 doorbell 그림 따라가기 · 실제 PC 에서 찾은 끝없는 반복 버그를 직접 되살려 보기 (튜토리얼 연습 3) · xHCI 명세 4.2, 4.9

</div>

<div class="session" data-session="8" markdown="1">

### Step 8 · 2026.11.29 (일) — USB 장치 알아보기

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- ✅ **코드 완료 (2026.10.7)** · 태그 [<code>step-08</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-08) · 튜토리얼 [<code>docs/tutorial/step08.md</code>](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/tutorial/step08.md) · 이 회차는 리뷰

- **🤖 Claude :** <code>usb.cpp</code> : slot, Address Device, 입력·장치 컨텍스트, 제어 전송 (setup / data / status), STALL 복구, 디스크립터 → <code>id 627:1, a keyboard</code>
- **👤 Ryu (2h) :** 장치 디스크립터를 바이트 단위로 읽기 · 제품 이름 문자열 찍기 · <code>lsusb</code> 와 비교 · USB 2.0 명세 9장

</div>

<div class="session" data-session="9" markdown="1">

### Step 9 · 2026.12.5 (토) — USB 키보드로 입력

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- ✅ **코드 완료 (2026.10.7)** · 태그 [<code>step-09</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-09) · 튜토리얼 [<code>docs/tutorial/step09.md</code>](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/tutorial/step09.md) · 이 회차는 리뷰

- **🤖 Claude :** Configure Endpoint (interrupt IN), <code>SET_PROTOCOL</code> (boot), 8바이트 리포트 → 글자 → <code>consoleintr()</code>
- **👤 Ryu (2h) :** 날 리포트 보기 · PS/2 경로와 표로 비교 · 키를 꾹 눌러도 한 번만 나오는 이유 (타이머가 없다)

</div>

<div class="session" data-session="10" markdown="1">

### Step 10 · 2026.12.6 (일) — USB 허브, 실제 PC

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- ✅ **코드 완료 (2026.10.7)** · 태그 [<code>step-10</code>](https://github.com/jonghoon-ryu/xv6-x86_64/tree/step-10) · 튜토리얼 [<code>docs/tutorial/step10.md</code>](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/docs/tutorial/step10.md) · 이 회차는 리뷰

- **🤖 Claude :** 허브 (hub descriptor, 포트 전원·리셋), route string, Transaction Translator · Intel 7/8/9 시리즈 소켓 연결
- **👤 Ryu (2h) :** 실제 PC 화면을 한 줄씩 읽기 · (선택) 앞면 소켓의 키보드로 TT 경로 시험
- 🎯 **이정표 : 실제 PC 에서 USB 키보드로 입력** (2026.10.7 확인)

</div>

<div style="margin-top: 100px;"></div>

## Part 3 · 메모리

*책 Ch.3 · 커널이 자기 페이지 테이블을 갖기까지*

<div class="session" data-session="11" markdown="1">

### Step 11 · 2026.12.12 (토) — spinlock.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **🤖 Claude :** 최소한의 <code>struct cpu</code>, <code>push_off</code> / <code>pop_off</code>, RAII <code>LockGuard</code>
- **👤 Ryu (2h) :** <code>acquire</code>/<code>release</code> 짝이 <code>LockGuard</code> 로 바뀌는 것 보기 · 책 <b>Ch.6</b> 앞부분

</div>

<div class="session" data-session="12" markdown="1">

### Step 12 · 2026.12.13 (일) — kalloc.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **🤖 Claude :** UEFI 메모리 맵으로 빈 페이지 목록 만들기 · "N pages free" 출력
- **👤 Ryu (2h) :** 책 <b>Ch.3</b> 3.5 (물리 메모리 할당)

</div>

<div class="session" data-session="13" markdown="1">

### Step 13 · 2026.12.19 (토) — vm.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **🤖 Claude :** 4단계 페이지 테이블 : <code>walk</code>, <code>mappages</code>
- **👤 Ryu (2h) :** RISC-V Sv39 (3단계) 와 x86-64 (4단계) 비교 · 책 <b>Ch.3</b> 3.1–3.3

</div>

<div class="session" data-session="14" markdown="1">

### Step 14 · 2026.12.20 (일) — vm.cpp ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **🤖 Claude :** <code>kvmmake</code>, <code>kvminithart</code> (CR3 교체)
- **👤 Ryu (2h) :** 커널 페이지 테이블로 바꾼 뒤에도 화면이 그대로 나오는지 · 책 <b>Ch.3</b> 끝
- 🎯 **이정표 : 커널 자신의 페이지 테이블**

</div>

<div style="margin-top: 100px;"></div>

## Part 4 · 트랩과 인터럽트

*책 Ch.4–5 · 처음으로 화면이 "움직이기" 까지*

<div class="session" data-session="15" markdown="1">

### Step 15 · 2026.12.26 (토) — acpi.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **🤖 Claude :** RSDP → XSDT → MADT 읽기, CPU 와 IOAPIC 목록 출력
- **👤 Ryu (2h) :** ACPI 표 구조 · OSDev Wiki 의 MADT 항목

</div>

<div class="session" data-session="16" markdown="1">

### Step 16 · 2026.12.27 (일) — trap.cpp ①, kernelvec.S

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **🤖 Claude :** GDT, IDT, 예외 처리 → 일부러 0 으로 나눠서 panic 메시지 확인 (Step 6 의 임시 <code>earlytrap.cpp</code> 를 대신)
- **👤 Ryu (2h) :** 책 <b>Ch.4</b> (트랩) · RISC-V <code>stvec</code> ↔ x86 IDT

</div>

<div class="session" data-session="17" markdown="1">

### Step 17 · 2027.1.2 (토) — lapic.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **🤖 Claude :** LAPIC 타이머 인터럽트, <code>ticks</code> · 화면에 초 단위 카운터
- **👤 Ryu (2h) :** <code>hlt</code> 가 이제는 타이머가 깨울 때까지만 잔다 · 책 <b>Ch.5</b> 5.4
- 🎯 **이정표 : 화면이 움직인다 (타이머)**

</div>

<div class="session" data-session="18" markdown="1">

### Step 18 · 2027.1.3 (일) — ioapic.cpp, UART 인터럽트

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **🤖 Claude :** IOAPIC, UART 인터럽트 · Step 5 의 폴링 대신 인터럽트가 <code>uartintr()</code> 를 부른다
- **👤 Ryu (2h) :** 책 <b>Ch.5</b> 5.1–5.3 (콘솔 입력)

</div>

<div class="session" data-session="19" markdown="1">

### Step 19 · 2027.1.9 (토) — 키보드 인터럽트

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **🤖 Claude :** 키보드 인터럽트 (IRQ1) 가 <code>kbdintr()</code> 를 부른다 · USB 키보드는 xHCI 인터럽트 (MSI) 로 · 폴링 루프를 지우고 다시 <code>hlt</code> (CPU 100% → 0%)
- **👤 Ryu (2h) :** 책 <b>Ch.5</b> 끝
- 🎯 **이정표 : 인터럽트로 키보드 입력**

</div>

<div style="margin-top: 100px;"></div>

## Part 5 · 프로세스

*책 Ch.4, 7 · 첫 사용자 프로그램과 시스템 콜*

<div class="session" data-session="20" markdown="1">

### Step 20 · 2027.1.10 (일) — proc.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **🤖 Claude :** <code>struct proc</code>, 프로세스 표, 커널 스택
- **👤 Ryu (2h) :** 책 <b>Ch.7</b> 앞부분

</div>

<div class="session" data-session="21" markdown="1">

### Step 21 · 2027.1.16 (토) — swtch.S, scheduler

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **🤖 Claude :** 문맥 교환 · 커널 스레드 두 개가 번갈아 출력
- **👤 Ryu (2h) :** <code>swtch</code> 에서 저장하는 레지스터 (RISC-V ↔ x86-64) · 책 <b>Ch.7</b> 7.1–7.4

</div>

<div class="session" data-session="22" markdown="1">

### Step 22 · 2027.1.17 (일) — sleep / wakeup, sleeplock.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **🤖 Claude :** 잠들기와 깨우기, sleep lock
- **👤 Ryu (2h) :** 책 <b>Ch.7</b> 7.5–7.9

</div>

<div class="session" data-session="23" markdown="1">

### Step 23 · 2027.1.23 (토) — trampoline.S, 사용자 모드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **🤖 Claude :** 사용자 페이지 테이블, <code>usertrap</code> / <code>usertrapret</code> · 임시 initcode 를 사용자 모드로 실행
- **👤 Ryu (2h) :** TSS, <code>iretq</code>, CPUTABLES 페이지 · 책 <b>Ch.4</b> 4.2–4.4

</div>

<div class="session" data-session="24" markdown="1">

### Step 24 · 2027.1.24 (일) — syscall.cpp, sysproc.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **🤖 Claude :** <code>int $64</code> 시스템 콜 · <code>fork</code> / <code>exit</code> / <code>wait</code> / <code>getpid</code> / <code>sbrk</code> / <code>uptime</code>
- **👤 Ryu (2h) :** 책 <b>Ch.4</b> 4.3–4.5
- 🎯 **이정표 : 첫 시스템 콜**

</div>

<div class="session" data-session="25" markdown="1">

### Step 25 · 2027.1.30 (토) — entryother.S, 다중 CPU

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **🤖 Claude :** <code>startothers</code> 로 나머지 CPU 깨우기 · <code>CPUS=4</code>
- **👤 Ryu (2h) :** AP 부팅 (16비트 → 64비트) 과정 · 책 <b>Ch.6</b> 6.1–6.3

</div>

<div class="session" data-session="26" markdown="1">

### Step 26 · 2027.1.31 (일) — 여유

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **🤖 Claude :** 밀린 단계 마무리
- **👤 Ryu (2h) :** 밀린 리뷰 · 지금까지의 C++ 코드 훑어보기

</div>

<div style="margin-top: 100px;"></div>

## Part 6 · 파일 시스템

*책 Ch.8 · /init 이 실행되기까지*

<div class="session" data-session="27" markdown="1">

### Step 27 · 2027.2.6 (토) — mkfs (호스트 C++17), ramdisk.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **🤖 Claude :** 진짜 <code>fs.img</code> 만들기 · 램디스크에서 슈퍼블록 읽어 출력
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.1–8.2 (디스크 구조)

</div>

<div class="session" data-session="28" markdown="1">

### Step 28 · 2027.2.7 (일) — bio.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **🤖 Claude :** 버퍼 캐시
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.3

</div>

<div class="session" data-session="29" markdown="1">

### Step 29 · 2027.2.13 (토) — log.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **🤖 Claude :** 로그 (crash 복구)
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.4–8.6

</div>

<div class="session" data-session="30" markdown="1">

### Step 30 · 2027.2.14 (일) — fs.cpp ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **🤖 Claude :** 블록 할당, inode
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.7–8.10

</div>

<div class="session" data-session="31" markdown="1">

### Step 31 · 2027.2.20 (토) — fs.cpp ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **🤖 Claude :** 디렉터리, 경로 찾기
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.11–8.12

</div>

<div class="session" data-session="32" markdown="1">

### Step 32 · 2027.2.21 (일) — file.cpp, pipe.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **🤖 Claude :** 파일 표, 파이프
- **👤 Ryu (2h) :** 책 <b>Ch.8</b> 8.13 · <b>Ch.1</b> 파이프 다시 보기

</div>

<div class="session" data-session="33" markdown="1">

### Step 33 · 2027.2.27 (토) — sysfile.cpp, exec.cpp

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **🤖 Claude :** 파일 시스템 콜, ELF 로딩 · <code>/init</code> 실행
- **👤 Ryu (2h) :** 책 <b>Ch.3</b> 3.8 (exec)
- 🎯 **이정표 : /init 실행**

</div>

<div style="margin-top: 100px;"></div>

## Part 7 · 사용자 프로그램

*셸이 다시 뜨고 usertests 가 통과하기까지*

<div class="session" data-session="34" markdown="1">

### Step 34 · 2027.2.28 (일) — 사용자 라이브러리, init, sh

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **🤖 Claude :** <code>ulib</code>, <code>printf</code>, <code>umalloc</code>, <code>usys</code> 를 C++ 로 · <code>init</code>, <code>sh</code>
- **👤 Ryu (2h) :** 셸에서 <code>ls</code>, 파이프 써 보기 · 책 <b>Ch.1</b> 다시 보기
- 🎯 **이정표 : 셸 ($) 복귀**

</div>

<div class="session" data-session="35" markdown="1">

### Step 35 · 2027.3.6 (토) — 사용자 프로그램 ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **🤖 Claude :** <code>cat</code>, <code>echo</code>, <code>ls</code>, <code>grep</code>, <code>wc</code>
- **👤 Ryu (2h) :** C 판과 C++ 판 나란히 비교

</div>

<div class="session" data-session="36" markdown="1">

### Step 36 · 2027.3.7 (일) — 사용자 프로그램 ②

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **🤖 Claude :** <code>mkdir</code>, <code>rm</code>, <code>ln</code>, <code>kill</code>, <code>forktest</code>, <code>zombie</code> 등

</div>

<div class="session" data-session="37" markdown="1">

### Step 37 · 2027.3.13 (토) — usertests ①

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="37"> 완료</label>

- **🤖 Claude :** usertests 앞 절반 변환
- **👤 Ryu (2h) :** 실패하는 테스트가 있으면 함께 원인 보기

</div>

<div class="session" data-session="38" markdown="1">

### Step 38 · 2027.3.14 (일) — usertests ②, grind

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="38"> 완료</label>

- **🤖 Claude :** 나머지 변환 · <code>usertests</code> 전체 통과 · <code>grind</code>
- **👤 Ryu (2h) :** 책 <b>Ch.9</b> (동시성 다시 보기)
- 🎯 **이정표 : usertests 전체 통과**

</div>

<div class="session" data-session="39" markdown="1">

### Step 39 · 2027.3.20 (토) — 여유

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="39"> 완료</label>

- **🤖 Claude :** 밀린 단계 마무리
- **👤 Ryu (2h) :** 밀린 리뷰

</div>

<div style="margin-top: 100px;"></div>

## Part 8 · 마무리

*C++ 다듬기, 실제 PC, 회고*

<div class="session" data-session="40" markdown="1">

### Step 40 · 2027.3.21 (일) — C++ 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="40"> 완료</label>

- **🤖 Claude :** <code>defs.h</code> 를 모듈별 헤더로 · <code>param.h</code> / <code>memlayout.h</code> / <code>x86.h</code> 의 매크로를 <code>constexpr</code> / <code>inline</code> 으로
- **👤 Ryu (2h) :** 남은 C 흔적 찾기

</div>

<div class="session" data-session="41" markdown="1">

### Step 41 · 2027.3.27 (토) — 실제 PC

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="41"> 완료</label>

- **🤖 Claude :** 실제 PC 에서 전체 확인 : 부팅, USB 키보드, 셸, usertests · 남은 실제 PC 문제 고치기
- **👤 Ryu (2h) :** USB 메모리로 부팅해서 셸 쓰기 (USB 키보드는 Step 6–10 에서 이미 동작)

</div>

<div class="session" data-session="42" markdown="1">

### Step 42 · 2027.3.28 (일) — v1.0-cpp, 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="42"> 완료</label>

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
