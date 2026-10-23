---
layout: default
title: 1년 학습 계획 — CS:APP
permalink: /learning-cs/csapp/study-plan/
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

# CS:APP — 1년 학습 계획

**2026년 11월 7일 (토) 시작 · 52주 · 매주 토요일 2시간 + 일요일 2시간**

주말 시간 배분: **토요일·일요일 각각 = 이 계획 2시간 + [계산 이론 & Gödel](/learning-cs/computation-theory/study-plan/) 2시간**.
[xv6 C++ 변환](/xv6/plan/) 리뷰는 이 계획을 마친 뒤로 미뤘다.

목표: Bryant & O'Hallaron, *Computer Systems: A Programmer's Perspective* (3rd ed.) 로
**C 프로그램이 기계 위에서 실제로 어떻게 돌아가는지** 를 이해한다. 어셈블리를 읽고, 링커·프로세스·가상 메모리·캐시를 손으로 만져 본다.

<div style="margin-top: 100px;"></div>

## 왜 xv6 보다 먼저인가?

xv6 의 코드는 이 책이 설명하는 것들의 **구현** 이다.

- `swtch.S`, 트랩 진입 코드 → Ch.3 (어셈블리, 스택 프레임, 레지스터 규약)
- `kernel.ld`, 부트 로더 → Ch.7 (링킹, ELF, 로딩)
- 트랩, 시스템 콜, 프로세스 → Ch.8 (예외적 제어 흐름)
- `vm.c`, `kalloc.c` → Ch.9 (페이지 테이블, 할당기)
- 스핀락, sleep/wakeup → Ch.12 (동시성)

이 책을 먼저 하면 xv6 리뷰는 "처음 보는 개념" 이 아니라 "아는 개념의 구현을 확인하는" 일이 된다.

<div style="margin-top: 100px;"></div>

## 1년 안에 가능한가?

- **시간 예산:** (토 2h + 일 2h) × 52주 ≈ 208시간. 휴가·명절·바쁜 주말을 빼면 현실적으로 **약 180시간**.
- **읽기 + Practice Problem:** 핵심 장 (1–3, 5–10, 12) 약 **105시간**.
- **랩 6개:** Data 10h, Bomb 10h, Attack 10h, Cache 10h, Shell 10h, Malloc 20h ≈ **70시간**.

**결론: 가능하다.** 필요한 시간 (약 175시간) 과 예산 (약 180시간) 이 거의 같아서 빠듯하다. 그래서 다음은 처음부터 뺐다.

- ⏭ Ch.**4** 프로세서 구조 (Y86-64): CMU 15-213 강의도 다루지 않는다. 소프트웨어 쪽에는 영향이 적다
- ⏭ Ch.**11** 네트워크 + Proxy Lab: 여유 주간의 선택 주제로
- ⏭ Ch.**5** 최적화: 1주로 가볍게
- ⏭ Homework Problem (답 없음): 여유가 있을 때만

<div style="margin-top: 100px;"></div>

## 교재, 강의, 랩

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:22%"><col style="width:53%"><col style="width:25%"></colgroup>
  <thead><tr><th>역할</th><th>자료</th><th>비용</th></tr></thead>
  <tbody>
    <tr><td>교재</td><td>Randal E. Bryant, David R. O'Hallaron, <em>Computer Systems: A Programmer's Perspective</em> (<strong>3rd ed.</strong>, x86-64) · <a href="http://csapp.cs.cmu.edu/3e/home.html">책 홈페이지</a><br>⚠️ "Global Edition" 은 Practice Problem 에 오류가 많다고 알려져 있다. 가능하면 북미판</td><td>책 구매</td></tr>
    <tr><td>강의</td><td><a href="https://www.cs.cmu.edu/afs/cs/academic/class/15213-f15/www/schedule.html">CMU 15-213 Fall 2015</a> (저자 Bryant, O'Hallaron 직강) · 슬라이드 + 녹화 영상. 아래에서 <strong>L1–L27</strong> 은 이 강의 번호</td><td>무료</td></tr>
    <tr><td>랩</td><td><a href="http://csapp.cs.cmu.edu/3e/labs.html">CS:APP Lab Assignments</a> 의 <strong>Self-Study Handout</strong>: Data, Bomb, Attack, Cache, Shell, Malloc (+ 선택: Performance, Proxy)</td><td>무료</td></tr>
    <tr><td>도구</td><td><code>gcc</code>, <code>gdb</code> + <a href="https://github.com/hugsy/gef">GEF</a>, <code>objdump</code>, <code>readelf</code>, <code>valgrind</code>, <code>perf</code>, <a href="https://godbolt.org">Compiler Explorer</a><br>Data Lab 과 Malloc Lab 은 <code>-m32</code> 로 빌드하므로 <code>gcc-multilib</code> 필요</td><td>무료</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 주간 리듬

- **📖 토요일 2시간:** 강의 1편 + 교재 해당 절 읽기 + 노트
- **✏️ 일요일 2시간:** 그 절의 **Practice Problem** (답이 각 장 끝에 있다) 또는 랩
- 책의 예제는 **반드시 직접 컴파일해서** 확인한다. `gcc -Og -S foo.c` (책과 같은 옵션), `objdump -d`, GDB 의 `layout asm` + `stepi`
- 어셈블리는 **먼저 예측하고, 그다음 컴파일해서 맞춰 본다**. 틀린 곳이 곧 배울 곳이다
- 랩 주간에는 토·일 모두 랩. 랩이 밀리면 다음 여유 주간에서 흡수한다
- 주말 하나를 통째로 놓치면 **두 주 분량을 한 주에 몰아서 하지 않는다.** 한 주 밀고, 여유 주간 (Week 7, 19, 26, 34, 43, 48, 49–51) 에서 흡수한다

### Claude 를 스터디 파트너로 쓰기

- 랩은 답이 아니라 **힌트** 만 요청 (특히 Bomb Lab, Data Lab)
- 내가 손으로 복원한 C 코드나 스택 그림을 보여주고 **틀린 곳을 찾아달라고** 요청
- "3.7.4 의 이 그림에서 왜 `%rbx` 를 push 하나" 처럼 구체적으로 질문
- 교재의 문제 원문은 공개 블로그에 옮기지 않는다 (번호로만 언급)

### 🧩 C++ 연결 (선택)

Week 12 부터 일부 주에는 **C++ 연결** 줄이 있다. 일요일 마지막 10–15분, 그 주에 배운 것으로 C++ 기능 하나를 어셈블리로 들여다본다.

- [godbolt.org](https://godbolt.org) 에서 작은 함수 하나만. `<iostream>` 같은 큰 헤더는 피한다
- `-Og` (책과 같음) 와 `-O2` (실제 배포) 를 둘 다 본다
- 어셈블리는 **한 컴파일러의 선택** 일 뿐, 언어가 보장하는 것은 아니다. 규칙은 표준·learncpp 로, 구현은 어셈블리로 확인한다
- Week 12 (3.7 프로시저) 전에는 C++ 어셈블리가 잡음으로 보인다. 그 전에는 하지 않아도 된다

<div style="margin-top: 100px;"></div>

## 전체 로드맵

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:36%"><col style="width:26%"><col style="width:38%"></colgroup>
  <thead><tr><th>단계</th><th>기간</th><th>내용</th></tr></thead>
  <tbody>
      <tr><td>Phase 0 · 준비</td><td>Week 1<br>2026.11.7</td><td>환경 설정 + 전체 지도</td></tr>
      <tr><td>Phase 1 · 데이터 표현 (Ch.2)</td><td>Week 2–7<br>2026.11.14 ~ 2026.12.19</td><td>비트, 정수, 부동소수점 + Data Lab</td></tr>
      <tr><td>Phase 2 · 기계 수준 프로그램 = 어셈블리 (Ch.3)</td><td>Week 8–19<br>2026.12.26 ~ 2027.3.13</td><td>x86-64 어셈블리 읽기 + Bomb Lab + Attack Lab</td></tr>
      <tr><td>Phase 3 · 성능과 메모리 계층 (Ch.5–6)</td><td>Week 20–26<br>2027.3.20 ~ 2027.5.1</td><td>최적화 맛보기, 캐시 + Cache Lab</td></tr>
      <tr><td>Phase 4 · 링킹 (Ch.7)</td><td>Week 27–28<br>2027.5.8 ~ 2027.5.15</td><td>오브젝트 파일, 심볼, 재배치</td></tr>
      <tr><td>Phase 5 · 예외적 제어 흐름 (Ch.8)</td><td>Week 29–34<br>2027.5.22 ~ 2027.6.26</td><td>예외, 프로세스, 시그널 + Shell Lab</td></tr>
      <tr><td>Phase 6 · 가상 메모리 (Ch.9)</td><td>Week 35–43<br>2027.7.3 ~ 2027.8.28</td><td>페이지 테이블, mmap, malloc + Malloc Lab</td></tr>
      <tr><td>Phase 7 · 시스템 I/O 와 동시성 (Ch.10, 12)</td><td>Week 44–48<br>2027.9.4 ~ 2027.10.2</td><td>파일 디스크립터, 스레드, 동기화</td></tr>
      <tr><td>여유 주간 + 회고</td><td>Week 49–52<br>2027.10.9 ~ 2027.10.30</td><td>밀린 것 따라잡기, 선택 주제, xv6 로 넘어갈 준비</td></tr>
  </tbody>
</table>
</div>

**왜 이 순서인가?** 책의 순서이자 CMU 15-213 의 순서다. 각 장이 앞 장 위에 쌓인다.
데이터 표현 (Ch.2) 을 알아야 어셈블리의 조건 코드가 읽히고, 어셈블리 (Ch.3) 를 알아야 링커가 무엇을 고치는지 보이고,
프로세스 (Ch.8) 를 알아야 가상 메모리 (Ch.9) 가 왜 필요한지 보인다.
랩은 각 장 바로 뒤에 둬서 읽은 것을 곧바로 손으로 확인한다.

**밀리면 줄이는 순서:** Ch.5 → Ch.12.6–12.7 → Cache Lab Part B 의 64×64 → Attack Lab 의 `rtarget`.
Ch.3, Ch.8, Ch.9 와 Bomb / Shell / Malloc Lab 은 xv6 와 직접 연결되므로 줄이지 않는다.

<div style="margin-top: 100px;"></div>

## 진도

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 52</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Phase 0 · 준비

*Week 1 · 2026.11.7 · 환경 설정 + 전체 지도*

<div class="session" data-session="1" markdown="1">

### Week 1 · 2026.11.7–8 (토·일) — 환경 설정 + 컴퓨터 시스템 여행

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.1 전체 (가볍게, 지도만 그리기) · 강의 **L1** Overview
- **✏️ 연습·랩 (일 2h):** 환경 설정: `sudo apt install gcc-multilib gdb` (Data Lab 과 Malloc Lab 은 `-m32` 로 빌드), 랩 핸드아웃 7개 내려받기, 노트 폴더 만들기. `hello.c` 를 `gcc -Og -S` / `objdump -d` 로 열어 보기
- 🛠 **GDB + [GEF](https://github.com/hugsy/gef)** (2026.10.23 설치 완료: `~/.gef-2026.01.py`, `~/.gdbinit`). `gdb ./hello` → `break main` → `run` → `stepi` 를 몇 번: 단계마다 레지스터·스택·코드가 한 화면에 나오고, 바뀐 레지스터는 색으로 표시된다. GEF 는 기본값이 Intel 문법이라 `~/.gdbinit` 에 `set disassembly-flavor att` 를 넣어 책과 같은 AT&T 로 맞춰 두었다
- 💡 짧은 실험은 브라우저의 [x86-64 Playground](https://x64.halb.it/) 로도 된다 (GNU as, 단계 실행, 레지스터·메모리 보기)
- 💡 Ch.1 은 책 전체의 예고편이다. 지금 다 이해할 필요 없다. 1년 뒤에 다시 읽으면 모든 문장이 이해된다

</div>

<div style="margin-top: 100px;"></div>

## Phase 1 · 데이터 표현 (Ch.2)

*Week 2–7 · 2026.11.14 ~ 2026.12.19 · 비트, 정수, 부동소수점 + Data Lab*

<div class="session" data-session="2" markdown="1">

### Week 2 · 2026.11.14–15 (토·일) — 비트, 바이트, 정보의 저장

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**2.1** (16진수, 워드, 바이트 순서, 비트 연산, 시프트) · 강의 **L2** Bits, Bytes, Integers I
- **✏️ 연습·랩 (일 2h):** 2.1절 Practice Problem 전부. `show_bytes` 예제를 직접 돌려서 내 PC 가 little endian 인지 확인

</div>

<div class="session" data-session="3" markdown="1">

### Week 3 · 2026.11.21–22 (토·일) — 정수: unsigned 와 2의 보수

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**2.2–2.3** (정수 표현, 변환, 확장/절단, 덧셈·곱셈·나눗셈) · 강의 **L3** Bits, Bytes, Integers II
- **✏️ 연습·랩 (일 2h):** 2.2–2.3절 Practice Problem 전부. 특히 signed/unsigned 비교 함정 문제를 코드로 확인
- 🔗 Ch.3 의 `cmp`, 조건 코드 (CF, OF) 를 이해하는 바탕이 여기다

</div>

<div class="session" data-session="4" markdown="1">

### Week 4 · 2026.11.28–29 (토·일) — 부동소수점

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**2.4** (IEEE 754, 반올림, 연산) · 강의 **L4** Floating Point
- **✏️ 연습·랩 (일 2h):** 2.4절 Practice Problem 중 절반. 8비트 소형 float 표를 손으로 한 번 채워 보기
- 💡 Phase 1 에서 가장 덜 중요한 부분. 시간이 모자라면 형식 (부호/지수/가수) 과 비정규화 수 개념만 잡고 넘어간다

</div>

<div class="session" data-session="5" markdown="1">

### Week 5 · 2026.12.5–6 (토·일) — 🧪 Data Lab (1)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- **📖 강의·읽기 (토 2h):** Data Lab 핸드아웃 읽기, `bits.c` 의 규칙 (허용 연산자, 연산자 개수) 이해, 쉬운 퍼즐부터
- **✏️ 연습·랩 (일 2h):** 퍼즐 풀기 + `./btest`, `./dlc` 로 채점
- 💡 막히면 답이 아니라 **힌트** 를 Claude 에게 요청

</div>

<div class="session" data-session="6" markdown="1">

### Week 6 · 2026.12.12–13 (토·일) — 🧪 Data Lab (2)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- **📖 강의·읽기 (토 2h):** 남은 정수 퍼즐
- **✏️ 연습·랩 (일 2h):** float 퍼즐 + 전체 채점 (`./driver.pl`)
- 🎯 **마일스톤:** Data Lab 만점 (또는 남은 퍼즐을 적어 두고 넘어가기)

</div>

<div class="session" data-session="7" markdown="1">

### Week 7 · 2026.12.19–20 (토·일) — Phase 1 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.2 노트 정리, 틀렸던 Practice Problem 다시 풀기
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기. 여유가 있으면 Ch.2 Homework Problem (답 없음) 몇 개를 풀고 Claude 에게 검토 요청

</div>

<div style="margin-top: 100px;"></div>

## Phase 2 · 기계 수준 프로그램 = 어셈블리 (Ch.3)

*Week 8–19 · 2026.12.26 ~ 2027.3.13 · x86-64 어셈블리 읽기 + Bomb Lab + Attack Lab*

<div class="session" data-session="8" markdown="1">

### Week 8 · 2026.12.26–27 (토·일) — 어셈블리 첫걸음: 레지스터와 mov

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.1–3.4** (역사, 프로그램 인코딩, 데이터 형식, 오퍼랜드, `mov`, `push`/`pop`) · 강의 **L5** Machine-Level Programming I: Basics
- **✏️ 연습·랩 (일 2h):** 3.2–3.4절 Practice Problem 전부. 책의 예제를 `gcc -Og -S` 로 직접 만들어 책과 비교
- 💡 책은 **AT&T 문법** (`mov src, dst`). GCC 기본값이고 xv6 소스도 AT&T 다

</div>

<div class="session" data-session="9" markdown="1">

### Week 9 · 2027.1.2–3 (토·일) — 산술·논리 연산과 lea

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.5** (`lea`, 단항/이항 연산, 시프트, 128비트 곱셈·나눗셈)
- **✏️ 연습·랩 (일 2h):** 3.5절 Practice Problem 전부. C 함수 3개를 직접 써서 어셈블리를 먼저 **예측** 하고 컴파일해서 맞춰 보기 ([godbolt.org](https://godbolt.org))

</div>

<div class="session" data-session="10" markdown="1">

### Week 10 · 2027.1.9–10 (토·일) — 제어 (1): 조건 코드와 분기

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.6.1–3.6.6** (조건 코드, `cmp`/`test`, `set`, 점프, 조건 이동 `cmov`) · 강의 **L6** Machine-Level Programming II: Control
- **✏️ 연습·랩 (일 2h):** 3.6절 앞부분 Practice Problem. `if` 문이 `jmp` 버전과 `cmov` 버전으로 각각 언제 나오는지 `-Og` / `-O2` 로 비교

</div>

<div class="session" data-session="11" markdown="1">

### Week 11 · 2027.1.16–17 (토·일) — 제어 (2): 반복문과 switch

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.6.7–3.6.8** (do-while, while, for 의 번역, switch 와 점프 테이블)
- **✏️ 연습·랩 (일 2h):** 3.6절 뒷부분 Practice Problem. 어셈블리만 보고 원래 C 코드를 복원하는 문제에 집중

</div>

<div class="session" data-session="12" markdown="1">

### Week 12 · 2027.1.23–24 (토·일) — 프로시저: 스택 프레임

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.7** (런타임 스택, `call`/`ret`, 인자 레지스터, 지역 변수, callee/caller-saved, 재귀) · 강의 **L7** Machine-Level Programming III: Procedures
- **✏️ 연습·랩 (일 2h):** 3.7절 Practice Problem. **GDB 실습:** 재귀 함수를 `stepi` 로 따라가며 `info registers`, `x/8gx $rsp` 로 스택 변화를 그림으로 그리기
- 🔗 xv6 의 문맥 교환 (`swtch.S`) 은 이 절 하나로 읽힌다
- 🧩 **C++ 연결 (선택, 10–15분):** 멤버 함수 `p.get()` 과 자유 함수 `get(&p)` 를 나란히 컴파일: `this` 는 `%rdi` 로 넘어가는 숨은 첫 인자다. `int&` 와 `int*` 인자도 같은 코드가 나오는지 확인

</div>

<div class="session" data-session="13" markdown="1">

### Week 13 · 2027.1.30–31 (토·일) — 배열, 구조체, 공용체, 정렬

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.8–3.9** · 강의 **L8** Machine-Level Programming IV: Data
- **✏️ 연습·랩 (일 2h):** 3.8–3.9절 Practice Problem. 구조체 필드 순서를 바꿔 `sizeof` 와 오프셋이 어떻게 변하는지 확인
- 🧩 **C++ 연결 (선택, 10–15분):** 가상 함수가 하나 있는 클래스의 `sizeof` (vtable 포인터 8바이트 + 패딩) 와, `-Og` 에서 가상 호출이 `movq (%rdi), %rax` → `call *(%rax)` (간접 호출) 로 나오는 것 확인

</div>

<div class="session" data-session="14" markdown="1">

### Week 14 · 2027.2.6–7 (토·일) — 포인터, GDB, 버퍼 오버플로

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**3.10** (포인터 정리, GDB, 버퍼 오버플로, 스택 보호, 가변 크기 스택 프레임) · 강의 **L9** Machine-Level Programming V: Advanced Topics
- **✏️ 연습·랩 (일 2h):** 3.10절 Practice Problem. 일부러 오버플로가 나는 프로그램을 만들고 `-fno-stack-protector` 유무로 차이 보기
- 💡 Ch.**3.11** (부동소수점 어셈블리) 은 가볍게 훑기만. 필요해지면 나중에 본다
- 🧩 **C++ 연결 (선택, 10–15분):** `std::array` 의 `a[i]` 와 `a.at(i)` 비교: `at()` 에만 `cmpq` + 예외 던지는 함수 호출 (경계 검사) 이 붙는다

</div>

<div class="session" data-session="15" markdown="1">

### Week 15 · 2027.2.13–14 (토·일) — 🧪 Bomb Lab (1)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **📖 강의·읽기 (토 2h):** Bomb Lab 시작: `objdump -d bomb`, GDB 에서 `explode_bomb` 에 breakpoint 걸기. phase 1–2
- **✏️ 연습·랩 (일 2h):** phase 3–4
- 💡 Self-Study 판 폭탄은 터져도 서버에 기록되지 않는다. 마음껏 터뜨려도 된다

</div>

<div class="session" data-session="16" markdown="1">

### Week 16 · 2027.2.20–21 (토·일) — 🧪 Bomb Lab (2)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **📖 강의·읽기 (토 2h):** phase 5–6
- **✏️ 연습·랩 (일 2h):** (선택) secret phase. 각 phase 마다 해당하는 C 코드를 손으로 복원해서 노트에 남기기
- 🎯 **마일스톤:** 어셈블리만 보고 프로그램이 무엇을 하는지 읽어낼 수 있다

</div>

<div class="session" data-session="17" markdown="1">

### Week 17 · 2027.2.27–28 (토·일) — 🧪 Attack Lab (1): 코드 주입

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **📖 강의·읽기 (토 2h):** Attack Lab 핸드아웃 읽기 (`target1`), `ctarget` level 1–2
- **✏️ 연습·랩 (일 2h):** `ctarget` level 3

</div>

<div class="session" data-session="18" markdown="1">

### Week 18 · 2027.3.6–7 (토·일) — 🧪 Attack Lab (2): ROP

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **📖 강의·읽기 (토 2h):** `rtarget` level 2 (Return-Oriented Programming, 가젯 찾기)
- **✏️ 연습·랩 (일 2h):** (선택) `rtarget` level 3. Ch.3.10.4 의 방어 기법 (스택 랜덤화, canary, NX) 과 각 공격을 연결해 정리
- 🎯 **마일스톤:** `call`/`ret` 과 스택이 실제 메모리라는 것을 손으로 확인했다

</div>

<div class="session" data-session="19" markdown="1">

### Week 19 · 2027.3.13–14 (토·일) — Phase 2 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.3 노트 정리: 레지스터 표, 스택 프레임 그림, 제어문 번역 패턴을 한 장으로
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기 또는 Ch.3 Homework Problem

</div>

<div style="margin-top: 100px;"></div>

## Phase 3 · 성능과 메모리 계층 (Ch.5–6)

*Week 20–26 · 2027.3.20 ~ 2027.5.1 · 최적화 맛보기, 캐시 + Cache Lab*

<div class="session" data-session="20" markdown="1">

### Week 20 · 2027.3.20–21 (토·일) — 프로그램 성능 최적화 (맛보기)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**5.1–5.6, 5.12–5.14** 위주로 훑기 (최적화 방해 요인, CPE, 메모리 앨리어싱, 병목 찾기) · 강의 **L10** Program Optimization
- **✏️ 연습·랩 (일 2h):** 책의 `combine` 예제를 직접 돌려 `-O1` / `-O2` 와 루프 펼치기의 효과를 `perf stat` 으로 측정
- 💡 Ch.**4** (Y86-64 프로세서 설계) 는 CMU 강의처럼 건너뛴다. 하드웨어 쪽이 궁금하면 여유 주간에 4.1, 4.4 만 읽는다
- 🧩 **C++ 연결 (선택, 10–15분):** `std::vector<int>` 의 range-for 합계와 C 포인터 루프 합계를 `-O2` 로 비교: 추상화가 정말 비용 0 인지 직접 보기

</div>

<div class="session" data-session="21" markdown="1">

### Week 21 · 2027.3.27–28 (토·일) — 저장 장치와 지역성

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**6.1–6.3** (DRAM, 디스크, **SSD**, 지역성, 메모리 계층) · 강의 **L11** The Memory Hierarchy
- **✏️ 연습·랩 (일 2h):** 6.1–6.3절 Practice Problem
- 🔗 6.1 의 SSD 절은 [헌 SSD 실험](/old-ssd-experiments/) 과 바로 연결된다

</div>

<div class="session" data-session="22" markdown="1">

### Week 22 · 2027.4.3–4 (토·일) — 캐시 메모리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**6.4** (직접 사상, 집합 연관, 완전 연관, 쓰기 정책) · 강의 **L12** Cache Memories
- **✏️ 연습·랩 (일 2h):** 6.4절 Practice Problem: 주소를 tag / set index / block offset 으로 손으로 나누는 연습을 충분히

</div>

<div class="session" data-session="23" markdown="1">

### Week 23 · 2027.4.10–11 (토·일) — 캐시 친화적인 코드

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**6.5–6.7** (캐시 친화적 코드, 메모리 산, 행렬 곱셈 루프 순서)
- **✏️ 연습·랩 (일 2h):** 행렬 곱셈 6가지 루프 순서를 직접 구현해 시간 측정. 책의 그래프와 비교
- 🧩 **C++ 연결 (선택, 10–15분):** `std::vector<std::vector<int>>` 와 1차원 `std::vector<int>` (행 우선 인덱싱) 의 행렬 순회 시간 비교: 메모리 배치가 캐시에 미치는 영향

</div>

<div class="session" data-session="24" markdown="1">

### Week 24 · 2027.4.17–18 (토·일) — 🧪 Cache Lab (1): 캐시 시뮬레이터

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **📖 강의·읽기 (토 2h):** Cache Lab Part A: `csim.c` (valgrind 트레이스를 읽는 LRU 캐시 시뮬레이터)
- **✏️ 연습·랩 (일 2h):** Part A 완성 + `./test-csim`

</div>

<div class="session" data-session="25" markdown="1">

### Week 25 · 2027.4.24–25 (토·일) — 🧪 Cache Lab (2): 행렬 전치 최적화

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **📖 강의·읽기 (토 2h):** Part B: 블로킹으로 캐시 미스 줄이기 (32×32)
- **✏️ 연습·랩 (일 2h):** 64×64, 61×67 + `./driver.py`
- 🎯 **마일스톤:** 캐시 미스를 계산하고 줄일 수 있다

</div>

<div class="session" data-session="26" markdown="1">

### Week 26 · 2027.5.1–2 (토·일) — Phase 3 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.6 노트 정리
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기. 여유가 있으면 Performance Lab (선택)

</div>

<div style="margin-top: 100px;"></div>

## Phase 4 · 링킹 (Ch.7)

*Week 27–28 · 2027.5.8 ~ 2027.5.15 · 오브젝트 파일, 심볼, 재배치*

<div class="session" data-session="27" markdown="1">

### Week 27 · 2027.5.8–9 (토·일) — 링킹 (1): 오브젝트 파일과 심볼

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**7.1–7.6** (컴파일러 드라이버, 재배치 가능 오브젝트, 심볼과 심볼 테이블, 심볼 해석, 정적 라이브러리) · 강의 **L13** Linking
- **✏️ 연습·랩 (일 2h):** 7.1–7.6절 Practice Problem. `readelf -s`, `nm` 으로 내가 만든 `.o` 의 심볼 테이블 직접 보기
- 🔗 C++ 강좌의 binary tools 장 에서 본 도구들을 여기서 제대로 쓴다
- 🧩 **C++ 연결 (선택, 10–15분):** `nm a.o` 로 맹글링된 이름 (`_Z3addii`) 보기 → `nm -C` / `c++filt` 로 풀기. `extern "C"` 를 붙이면 이름이 어떻게 바뀌는지

</div>

<div class="session" data-session="28" markdown="1">

### Week 28 · 2027.5.15–16 (토·일) — 링킹 (2): 재배치, 로딩, 동적 링킹

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**7.7–7.14** (재배치, 실행 파일, 로딩, 공유 라이브러리, PIC, 라이브러리 끼워넣기)
- **✏️ 연습·랩 (일 2h):** 7.7절 Practice Problem. `LD_PRELOAD` 로 `malloc` 끼워넣기 (7.13) 직접 해 보기
- 🔗 xv6 의 `kernel.ld` 링커 스크립트를 읽을 준비가 된다
- 🧩 **C++ 연결 (선택, 10–15분):** 함수 템플릿을 `int`, `double` 로 쓰고 `-O0` 오브젝트를 `nm -C` 로 보기: 인스턴스마다 별도 함수가 **W** (weak) 심볼로 생긴다. 여러 `.o` 에 같은 인스턴스가 있어도 링커가 하나만 남기는 이유

</div>

<div style="margin-top: 100px;"></div>

## Phase 5 · 예외적 제어 흐름 (Ch.8)

*Week 29–34 · 2027.5.22 ~ 2027.6.26 · 예외, 프로세스, 시그널 + Shell Lab*

<div class="session" data-session="29" markdown="1">

### Week 29 · 2027.5.22–23 (토·일) — 예외와 프로세스

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**8.1–8.3** (예외의 종류, 인터럽트, 트랩, 시스템 콜, 프로세스, 사용자/커널 모드, 문맥 교환) · 강의 **L14** Exceptional Control Flow: Exceptions and Processes
- **✏️ 연습·랩 (일 2h):** 8.1–8.3절 Practice Problem. `strace ./hello` 로 실제 시스템 콜 목록 보기
- 🔗 xv6 의 트랩 처리 전체가 이 절의 구체적인 구현이다

</div>

<div class="session" data-session="30" markdown="1">

### Week 30 · 2027.5.29–30 (토·일) — 프로세스 제어: fork, wait, execve

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**8.4** (프로세스 생성, 종료, 회수, `execve`, 프로그램 실행)
- **✏️ 연습·랩 (일 2h):** 8.4절 Practice Problem (fork 출력 개수 맞히기 문제는 **프로세스 그래프를 그려서**). 아주 작은 셸 (`fork` + `execve` + `waitpid`) 직접 작성
- 🧩 **C++ 연결 (선택, 10–15분):** 전역 객체의 소멸자를 만들고 `exit()` 와 `_exit()` 로 각각 끝내 보기: 어느 쪽에서 소멸자가 실행되는가

</div>

<div class="session" data-session="31" markdown="1">

### Week 31 · 2027.6.5–6 (토·일) — 시그널

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**8.5–8.8** (시그널, 핸들러, 경쟁 상태, 비지역 점프, 프로세스 도구) · 강의 **L15** Exceptional Control Flow: Signals and Nonlocal Jumps
- **✏️ 연습·랩 (일 2h):** 8.5절 Practice Problem. 안전한 시그널 핸들러 규칙 (async-signal-safe) 을 노트에 정리
- 💡 Ch.**10** 앞부분 (10.1–10.4) 을 함께 훑어 두면 Shell Lab 의 I/O 리다이렉션 부분이 쉬워진다
- 🧩 **C++ 연결 (선택, 10–15분):** 시그널 핸들러에서 써도 되는 C++ 타입은 `volatile std::sig_atomic_t` (또는 lock-free `std::atomic`). 핸들러 안에서 `std::cout` 을 쓰면 왜 위험한지 8.5.5 의 규칙으로 설명

</div>

<div class="session" data-session="32" markdown="1">

### Week 32 · 2027.6.12–13 (토·일) — 🧪 Shell Lab (1)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **📖 강의·읽기 (토 2h):** Shell Lab 핸드아웃 읽기, `tsh.c` 의 `eval`, `builtin_cmd`
- **✏️ 연습·랩 (일 2h):** `waitfg`, `sigchld_handler`, trace01–08 통과

</div>

<div class="session" data-session="33" markdown="1">

### Week 33 · 2027.6.19–20 (토·일) — 🧪 Shell Lab (2)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **📖 강의·읽기 (토 2h):** `sigint_handler`, `sigtstp_handler`, `do_bgfg` (작업 제어)
- **✏️ 연습·랩 (일 2h):** trace09–16 통과, `tshref` 와 출력 비교
- 🎯 **마일스톤:** 셸이 어떻게 동작하는지 직접 만들어서 안다

</div>

<div class="session" data-session="34" markdown="1">

### Week 34 · 2027.6.26–27 (토·일) — Phase 5 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.8 노트 정리: 예외 표, 프로세스 상태도, 시그널 흐름도
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기

</div>

<div style="margin-top: 100px;"></div>

## Phase 6 · 가상 메모리 (Ch.9)

*Week 35–43 · 2027.7.3 ~ 2027.8.28 · 페이지 테이블, mmap, malloc + Malloc Lab*

<div class="session" data-session="35" markdown="1">

### Week 35 · 2027.7.3–4 (토·일) — 가상 메모리 개념

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**9.1–9.6** (물리/가상 주소, 캐싱 도구·관리 도구·보호 도구로서의 VM, 주소 변환, TLB, 다단계 페이지 테이블) · 강의 **L17** Virtual Memory: Concepts
- **✏️ 연습·랩 (일 2h):** 9.1–9.6절 Practice Problem. 가상 주소 → 물리 주소 변환을 TLB → 페이지 테이블 → 캐시 순서로 손으로 끝까지 해 보기
- 🔗 xv6 의 `vm.c` (페이지 테이블) 를 읽는 데 꼭 필요한 주

</div>

<div class="session" data-session="36" markdown="1">

### Week 36 · 2027.7.10–11 (토·일) — 실제 시스템의 VM: Core i7 / Linux, mmap

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**9.7–9.8** (x86-64 4단계 페이지 테이블, Linux 가상 메모리 영역, 페이지 폴트, 메모리 매핑, `fork` 와 copy-on-write) · 강의 **L18** Virtual Memory: Systems
- **✏️ 연습·랩 (일 2h):** 9.8절 Practice Problem. `mmap` 으로 파일을 복사하는 프로그램 작성, `/proc/self/maps` 읽어 보기

</div>

<div class="session" data-session="37" markdown="1">

### Week 37 · 2027.7.17–18 (토·일) — 동적 메모리 할당 (1)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="37"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**9.9.1–9.9.6** (`malloc`/`free`, 단편화, 암시적 가용 리스트) · 강의 **L19** Dynamic Memory Allocation: Basic Concepts
- **✏️ 연습·랩 (일 2h):** 9.9절 Practice Problem. 책의 암시적 리스트 할당기 (9.9.12) 를 소리 내어 읽듯이 한 줄씩 따라가기
- 🧩 **C++ 연결 (선택, 10–15분):** `new int(5)` 를 컴파일하면 `call operator new(unsigned long)` 이 나온다. `operator new` 가 결국 `malloc` 을 부른다는 것을 GDB 에서 `break malloc` → `bt` (호출 스택) 로 확인

</div>

<div class="session" data-session="38" markdown="1">

### Week 38 · 2027.7.24–25 (토·일) — 동적 메모리 할당 (2)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="38"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**9.9.7–9.11** (배치, 분할, 연결, 경계 태그, 명시적 리스트, 분리 리스트, GC, 흔한 메모리 버그) · 강의 **L20** Dynamic Memory Allocation: Advanced Concepts
- **✏️ 연습·랩 (일 2h):** Malloc Lab 핸드아웃 읽기, 트레이스 파일 형식 이해, 설계 노트 (어떤 리스트 구조로 갈지) 작성

</div>

<div class="session" data-session="39" markdown="1">

### Week 39 · 2027.7.31–8.1 (토·일) — 🧪 Malloc Lab (1)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="39"> 완료</label>

- **📖 강의·읽기 (토 2h):** 책의 암시적 리스트 할당기를 그대로 옮겨 일단 모든 트레이스 통과
- **✏️ 연습·랩 (일 2h):** `mm_checkheap` (힙 일관성 검사기) 작성. 이후 모든 디버깅의 기본 도구

</div>

<div class="session" data-session="40" markdown="1">

### Week 40 · 2027.8.7–8 (토·일) — 🧪 Malloc Lab (2)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="40"> 완료</label>

- **📖 강의·읽기 (토 2h):** 명시적 가용 리스트로 바꾸기
- **✏️ 연습·랩 (일 2h):** 처리량 (throughput) 측정, 병목 확인

</div>

<div class="session" data-session="41" markdown="1">

### Week 41 · 2027.8.14–15 (토·일) — 🧪 Malloc Lab (3)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="41"> 완료</label>

- **📖 강의·읽기 (토 2h):** 분리 가용 리스트 (segregated free list)
- **✏️ 연습·랩 (일 2h):** 이용률 (utilization) 개선: `realloc` 최적화, 배치 정책 실험

</div>

<div class="session" data-session="42" markdown="1">

### Week 42 · 2027.8.21–22 (토·일) — 🧪 Malloc Lab (4)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="42"> 완료</label>

- **📖 강의·읽기 (토 2h):** 마무리, 점수 확인 (`./mdriver -V`)
- **✏️ 연습·랩 (일 2h):** 설계와 점수 변화를 블로그 노트로 정리
- 🎯 **마일스톤:** `malloc` 을 직접 만들어 봤다. 1년 계획에서 가장 큰 랩

</div>

<div class="session" data-session="43" markdown="1">

### Week 43 · 2027.8.28–29 (토·일) — Phase 6 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="43"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.9 노트 정리: 주소 변환 그림 한 장
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기 (Malloc Lab 은 자주 밀린다)

</div>

<div style="margin-top: 100px;"></div>

## Phase 7 · 시스템 I/O 와 동시성 (Ch.10, 12)

*Week 44–48 · 2027.9.4 ~ 2027.10.2 · 파일 디스크립터, 스레드, 동기화*

<div class="session" data-session="44" markdown="1">

### Week 44 · 2027.9.4–5 (토·일) — 시스템 수준 I/O

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="44"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**10** 전체 (Unix I/O, 파일 메타데이터, 디렉터리, 공유와 리다이렉션, RIO, 표준 I/O) · 강의 **L16** System-Level I/O
- **✏️ 연습·랩 (일 2h):** 10장 Practice Problem. `dup2` 로 리다이렉션을 직접 구현해 보기
- 🔗 파일 시스템 튜토리얼 과 xv6 의 `file.c`/`sysfile.c` 로 이어진다

</div>

<div class="session" data-session="45" markdown="1">

### Week 45 · 2027.9.11–12 (토·일) — 동시성 프로그래밍: 세 가지 방법

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="45"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**12.1–12.3** (프로세스, I/O 다중화 `select`, 스레드) · 강의 **L23** Concurrent Programming
- **✏️ 연습·랩 (일 2h):** 12.1–12.3절 Practice Problem. 간단한 echo 서버를 스레드 버전으로 작성 (Ch.11 은 소켓 함수 부분만 필요할 때 참고)
- 🧩 **C++ 연결 (선택, 10–15분):** 캡처가 있는 람다를 `std::thread` 에 넘기고 어셈블리 보기: 람다는 캡처를 필드로 가진 작은 구조체 + `operator()` 다. `std::thread` 아래에는 `pthread_create` 가 있다

</div>

<div class="session" data-session="46" markdown="1">

### Week 46 · 2027.9.18–19 (토·일) — 공유 변수와 세마포어

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="46"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**12.4–12.5** (공유 변수, 경쟁, 세마포어로 상호 배제, 생산자-소비자, readers-writers) · 강의 **L24** Synchronization: Basics
- **✏️ 연습·랩 (일 2h):** 12.5절 Practice Problem. `badcnt.c` 를 직접 돌려 경쟁 상태를 재현하고 세마포어로 고치기
- 🔗 Spinlock/Mutex/Semaphore 입문서 와 같이 보면 좋다
- 🧩 **C++ 연결 (선택, 10–15분):** `std::atomic<int>` 의 `g++` 가 `lock addl` 한 줄로 나오는 것 확인. `badcnt` 를 `std::atomic` 으로 고친 버전과 세마포어 버전의 속도 비교

</div>

<div class="session" data-session="47" markdown="1">

### Week 47 · 2027.9.25–26 (토·일) — 병렬성과 동시성의 함정

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="47"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.**12.6–12.7** (병렬 프로그램 성능, 스레드 안전성, 재진입성, 경쟁, 교착 상태) · 강의 **L25** Synchronization: Advanced, **L26** Thread-Level Parallelism
- **✏️ 연습·랩 (일 2h):** 12.7절 Practice Problem. 교착 상태가 나는 프로그램을 일부러 만들고 진행 그래프 (progress graph) 로 설명하기
- 🧩 **C++ 연결 (선택, 10–15분):** `std::atomic` 의 `store()` 를 기본 (seq_cst) 과 `memory_order_release` 로 비교: x86-64 에서 앞은 `xchg`, 뒤는 평범한 `mov`. 메모리 순서가 어셈블리에서 어떻게 보이는지

</div>

<div class="session" data-session="48" markdown="1">

### Week 48 · 2027.10.2–3 (토·일) — Phase 7 정리 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="48"> 완료</label>

- **📖 강의·읽기 (토 2h):** Ch.10, 12 노트 정리
- **✏️ 연습·랩 (일 2h):** 밀린 것 따라잡기

</div>

<div style="margin-top: 100px;"></div>

## 여유 주간 + 회고

*Week 49–52 · 2027.10.9 ~ 2027.10.30 · 밀린 것 따라잡기, 선택 주제, xv6 로 넘어갈 준비*

<div class="session" data-session="49" markdown="1">

### Week 49 · 2027.10.9–10 (토·일) — 여유 주간 1 / 선택: 네트워크 프로그래밍

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="49"> 완료</label>

- **📖 강의·읽기 (토 2h):** (선택) Ch.**11** (소켓, 웹 서버 Tiny) · 강의 **L21–L22** Network Programming
- **✏️ 연습·랩 (일 2h):** 밀린 주차 따라잡기 또는 Tiny 웹 서버 돌려 보기

</div>

<div class="session" data-session="50" markdown="1">

### Week 50 · 2027.10.16–17 (토·일) — 여유 주간 2 / 선택: Proxy Lab

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="50"> 완료</label>

- **📖 강의·읽기 (토 2h):** (선택) Proxy Lab Part I (순차 프록시)
- **✏️ 연습·랩 (일 2h):** (선택) Part II–III (동시성 + 캐시). 다 못해도 괜찮다

</div>

<div class="session" data-session="51" markdown="1">

### Week 51 · 2027.10.23–24 (토·일) — 여유 주간 3 / xv6 로 넘어갈 준비

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="51"> 완료</label>

- **📖 강의·읽기 (토 2h):** xv6 book 1–2장 훑기 + `swtch.S`, `trampoline`/트랩 진입 어셈블리를 Ch.3 지식으로 읽어 보기
- **✏️ 연습·랩 (일 2h):** 1년 동안 쓴 노트를 xv6 의 각 부분 (트랩, 프로세스, VM, 파일) 에 연결하는 표 만들기

</div>

<div class="session" data-session="52" markdown="1">

### Week 52 · 2027.10.30–31 (토·일) — 1년 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="52"> 완료</label>

- **📖 강의·읽기 (토 2h):** Week 1 의 `hello.c` 를 다시 열고 Ch.1 을 다시 읽기. 이제 모든 문장이 이해되는지 확인
- **✏️ 연습·랩 (일 2h):** 회고 글: 가장 어려웠던 것, 가장 재미있었던 랩, xv6 에서 써먹을 것
- 🎯 **최종:** 이 블로그에 회고 페이지 게시

</div>


<script>
(function () {
  var STORAGE_KEY = 'csapp-study-plan-progress';

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
