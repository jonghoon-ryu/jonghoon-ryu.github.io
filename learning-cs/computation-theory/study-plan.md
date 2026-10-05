---
layout: default
title: 1년 학습 계획 — 계산 이론 & 불완전성 정리
permalink: /learning-cs/computation-theory/study-plan/
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

# 계산 이론 & Gödel 불완전성 정리 — 1년 학습 계획

**2026년 11월 7일 (토) 시작 · 52주 · 매주 토요일 3시간**

주말 6시간을 반씩 나눈다: **토요일 3시간 = 이 계획**, **일요일 3시간 = [xv6 C++ 변환](/xv6/plan/)**.

목표: 취미로, 하지만 제대로.
Sipser 강의로 계산 이론을 공부하고, 그 위에서 Gödel 의 불완전성 정리를 **증명 구조까지** 이해한다.

<div style="margin-top: 100px;"></div>

## 1년 안에 가능한가?

- **시간 예산:** 3h × 52주 ≈ 156시간. 휴가·명절·바쁜 주말을 빼면 현실적으로 **약 130시간**.
- **Sipser 강의:** 약 80분 × 25편 ≈ 33시간. 읽기·연습문제까지 보통 영상의 3배 → **약 100시간**.
- **논리 복습 + 불완전성 정리:** 제2 정리까지 "증명 흐름을 이해하는" 수준으로 **약 60–70시간**.

**결론: 핵심(Phase 0–3)은 가능하다. 시간이 빠듯하므로 연습문제는 "많이"보다 "제대로" 푼다.** Phase 4 (복잡도) 는 밀리면 줄이는 구간이다.

- ✅ 계산 가능성 (Sipser 수준, 제대로)
- ✅ Gödel 제1·제2 불완전성 정리 (증명 구조와 핵심 보조정리)
- ✅ 계산 복잡도 (P, NP, PSPACE, 조금 가볍게)
- ❌ 대학원 수준의 엄밀함 (예: 완전성 정리 증명을 세부까지). 취미로는 괜찮다, 2년차에 하면 된다

<div style="margin-top: 100px;"></div>

## 교재와 강의

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:22%"><col style="width:53%"><col style="width:25%"></colgroup>
  <thead><tr><th>역할</th><th>자료</th><th>비용</th></tr></thead>
  <tbody>
    <tr><td>계산 이론 교재</td><td>Michael Sipser, <em>Introduction to the Theory of Computation</em> (3rd ed.)</td><td>책 구매</td></tr>
    <tr><td>계산 이론 강의</td><td><a href="https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/">MIT 18.404J Fall 2020, Sipser</a> (OCW / YouTube)<br>L1–L26, L13 은 시험일이라 영상 없음</td><td>무료</td></tr>
    <tr><td>1차 논리 복습</td><td>Leary &amp; Kristiansen, <a href="https://milneopentextbooks.org/a-friendly-introduction-to-mathematical-logic/"><em>A Friendly Introduction to Mathematical Logic</em></a> (2nd ed.) — 이하 L&amp;K</td><td>무료 (오픈 교재)</td></tr>
    <tr><td>불완전성 정리 (주교재)</td><td>Peter Smith, <a href="https://www.logicmatters.net/igt/"><em>Gödel Without (Too Many) Tears</em></a> (2nd ed., 146쪽) — 이하 GWT</td><td>무료 PDF</td></tr>
    <tr><td>불완전성 정리 (심화, 선택)</td><td>Peter Smith, <a href="https://www.logicmatters.net/igt/"><em>An Introduction to Gödel's Theorems</em></a> (2nd ed., 388쪽)</td><td>무료 PDF</td></tr>
    <tr><td>가벼운 읽을거리</td><td>Nagel &amp; Newman, <em>Gödel's Proof</em></td><td>얇은 책</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top: 100px;"></div>

## 주간 리듬

토요일 3시간 한 번에:

- **📖 앞 1.5시간:** 강의 1편 시청 또는 교재 1절 읽기 + 노트
- **✏️ 뒤 1.5시간:** 연습문제 (각 주에 적힌 것 중 2–3개면 충분). **절대 건너뛰지 않는다.** 강의만 보면 이해한 느낌만 든다. 실제 이해는 문제를 풀 때 생긴다
- 토요일 하나를 통째로 놓치면 **두 주 분량을 한 주에 몰아서 하지 않는다.** 그냥 한 주 밀고, 여유 주간(Week 7, 18, 26, 44, 49–51)에서 흡수한다

### Claude 를 스터디 파트너로 쓰기

- 증명을 직접 써서 보여주고 **빈틈을 찾아달라고** 요청 (답을 먼저 달라고 하지 않기)
- 막힌 연습문제는 **힌트만** 요청
- 이해 안 된 강의 부분은 "L8 의 xx 분 부분 설명해 줘" 처럼 구체적으로

<div style="margin-top: 100px;"></div>

## 전체 로드맵

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:32%"><col style="width:30%"><col style="width:38%"></colgroup>
  <thead><tr><th>단계</th><th>기간</th><th>내용</th></tr></thead>
  <tbody>
      <tr><td>Phase 0 · 수학 준비</td><td>Week 1–3<br>2026.11.7 ~ 2026.11.21</td><td>대각선 논법까지</td></tr>
      <tr><td>Phase 1 · 계산 가능성 (Sipser 1부)</td><td>Week 4–18<br>2026.11.28 ~ 2027.3.6</td><td>오토마타 → 튜링 기계 → 정지 문제 → 재귀 정리</td></tr>
      <tr><td>Phase 2 · 1차 논리 복습</td><td>Week 19–26<br>2027.3.13 ~ 2027.5.1</td><td>Leary & Kristiansen Ch.1–3</td></tr>
      <tr><td>Phase 3 · 불완전성 정리</td><td>Week 27–39<br>2027.5.8 ~ 2027.7.31</td><td>Gödel Without (Too Many) Tears 전체</td></tr>
      <tr><td>Phase 4 · 계산 복잡도 (Sipser 2부)</td><td>Week 40–48<br>2027.8.7 ~ 2027.10.2</td><td>P, NP, PSPACE, L, NL</td></tr>
      <tr><td>여유 주간 + 회고</td><td>Week 49–52<br>2027.10.9 ~ 2027.10.30</td><td>밀린 것 따라잡기, 선택 주제</td></tr>
  </tbody>
</table>
</div>

**왜 이 순서인가?**
정지 문제와 대각선 논법은 불완전성 정리로 들어가는 가장 쉬운 입구다. 그래서 계산 가능성을 먼저 한다.
Sipser Ch.6 (재귀 정리 + 논리 이론) 이 곧바로 Gödel 로 이어지므로, 기억이 생생할 때 논리 → 불완전성으로 간다.
복잡도는 Gödel 과의 연결이 가장 약하고, 시간이 모자랄 때 줄이기 가장 쉬워서 마지막에 둔다.
(주 3시간이라 빠듯하다. 밀리면 Phase 4 는 **P, NP, NP-완전성** 까지만 해도 충분하다.)

<div style="margin-top: 100px;"></div>

## 진도

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 52</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 100px;"></div>

## Phase 0 · 수학 준비

*Week 1–3 · 2026.11.7 ~ 2026.11.21 · 대각선 논법까지*

<div class="session" data-session="1" markdown="1">

### Week 1 · 2026.11.7 (토) — 오리엔테이션 + 집합·함수·그래프

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Sipser **Ch.0.1–0.2** (수학적 개념과 용어). 이 페이지 전체를 한 번 훑고 교재 PDF 준비
- **✏️ 연습문제 (~1.5h):** Ch.0 연습문제 0.1–0.6 중 3–4개
- 💡 가볍게: Nagel & Newman *Gödel's Proof* 1–2장 (출퇴근용)

</div>

<div class="session" data-session="2" markdown="1">

### Week 2 · 2026.11.14 (토) — 증명 기법: 직접·귀류·귀납

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Sipser **Ch.0.3–0.4** (정의, 정리, 증명 / 증명의 종류)
- **✏️ 연습문제 (~1.5h):** 귀납법 증명 2개, 귀류법 증명 2개를 직접 써 보기 (예: √2 무리수, 소수 무한)

</div>

<div class="session" data-session="3" markdown="1">

### Week 3 · 2026.11.21 (토) — 가산성과 대각선 논법

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Sipser **Ch.4.2 앞부분** "The Diagonalization Method" 만 먼저 읽기 (N, Q 가산 / R 비가산)
- **✏️ 연습문제 (~1.5h):** 노트 없이 R 비가산 증명 재현. 유리수가 가산인 이유도 설명해 보기
- 🎯 **마일스톤:** 대각선 논법을 백지에 재현할 수 있다. 앞으로 1년 내내 이 논법이 반복된다

</div>

<div style="margin-top: 100px;"></div>

## Phase 1 · 계산 가능성 (Sipser 1부)

*Week 4–18 · 2026.11.28 ~ 2027.3.6 · 오토마타 → 튜링 기계 → 정지 문제 → 재귀 정리*

<div class="session" data-session="4" markdown="1">

### Week 4 · 2026.11.28 (토) — 유한 오토마타, 정규 언어

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L1** Introduction, Finite Automata, Regular Expressions · Sipser **Ch.1.1**
- **✏️ 연습문제 (~1.5h):** Ch.1 연습문제: DFA 상태도 그리기 3–4개

</div>

<div class="session" data-session="5" markdown="1">

### Week 5 · 2026.12.5 (토) — 비결정성, 닫힘 성질

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L2** Nondeterminism, Closure Properties, Regular Expressions → Finite Automata · Sipser **Ch.1.2–1.3**
- **✏️ 연습문제 (~1.5h):** NFA → DFA 부분집합 구성(subset construction) 손으로 1회, 정규식 → NFA 1회

</div>

<div class="session" data-session="6" markdown="1">

### Week 6 · 2026.12.12 (토) — 펌핑 보조정리, FA → 정규식

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L3** Regular Pumping Lemma, Finite Automata → Regular Expressions, CFGs (앞부분) · Sipser **Ch.1.4**
- **✏️ 연습문제 (~1.5h):** {0ⁿ1ⁿ} 이 정규 언어가 아님을 펌핑 보조정리로 증명 + 비슷한 문제 2개

</div>

<div class="session" data-session="7" markdown="1">

### Week 7 · 2026.12.19 (토) — Ch.1 정리 + 코딩

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Ch.1 노트 정리, 헷갈린 문제 다시 풀기
- **✏️ 연습문제 (~1.5h):** 🛠 Python 으로 DFA/NFA 시뮬레이터 작성 (NFA 는 상태 집합으로 시뮬레이션)
- 💡 이번 주는 여유 주간을 겸함. 밀렸으면 따라잡기에 쓴다

</div>

<div class="session" data-session="8" markdown="1">

### Week 8 · 2026.12.26 (토) — 문맥 자유 문법, 푸시다운 오토마타

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L3 뒷부분 + L4** Pushdown Automata, CFG ↔ PDA · Sipser **Ch.2.1–2.2**
- **✏️ 연습문제 (~1.5h):** 문법 설계 2개 (예: 괄호 짝 맞추기), PDA 설계 1개

</div>

<div class="session" data-session="9" markdown="1">

### Week 9 · 2027.1.2 (토) — CF 펌핑 보조정리 → 튜링 기계 입문

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L5** CF Pumping Lemma, Turing Machines · Sipser **Ch.2.3**
- **✏️ 연습문제 (~1.5h):** {aⁿbⁿcⁿ} 이 CFL 이 아님을 증명. Ch.2.4 (DCFL) 는 건너뛰어도 됨

</div>

<div class="session" data-session="10" markdown="1">

### Week 10 · 2027.1.9 (토) — 튜링 기계

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L6** TM Variants, Church-Turing Thesis · Sipser **Ch.3.1–3.2**
- **✏️ 연습문제 (~1.5h):** TM 상태도 1개 직접 설계, 다중 테이프 TM ≡ 단일 테이프 TM 논증 따라가기

</div>

<div class="session" data-session="11" markdown="1">

### Week 11 · 2027.1.16 (토) — Church–Turing 논제 + 코딩

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Sipser **Ch.3.3** (알고리즘의 정의, Hilbert 10번 문제)
- **✏️ 연습문제 (~1.5h):** 🛠 Python 으로 튜링 기계 시뮬레이터 작성, {0^(2ⁿ)} 인식 TM 돌려 보기

</div>

<div class="session" data-session="12" markdown="1">

### Week 12 · 2027.1.23 (토) — 결정 가능 언어

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L7** Decision Problems for Automata and Grammars · Sipser **Ch.4.1**
- **✏️ 연습문제 (~1.5h):** A_DFA, E_DFA, EQ_DFA 가 결정 가능한 이유를 각각 한 문단으로 설명

</div>

<div class="session" data-session="13" markdown="1">

### Week 13 · 2027.1.30 (토) — 결정 불가능성: 정지 문제

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L8** Undecidability · Sipser **Ch.4.2** (나머지)
- **✏️ 연습문제 (~1.5h):** A_TM 결정 불가능 증명을 노트 없이 재현
- 🎯 **마일스톤:** "A_TM 이 결정 불가능하다"를 대각선 논법으로 설명할 수 있다

</div>

<div class="session" data-session="14" markdown="1">

### Week 14 · 2027.2.6 (토) — 환원 가능성

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L9** Reducibility · Sipser **Ch.5.1 (앞부분), 5.3**
- **✏️ 연습문제 (~1.5h):** HALT_TM, E_TM 결정 불가능성을 A_TM 에서 환원으로 증명. 사상 환원(≤m) 문제 2개

</div>

<div class="session" data-session="15" markdown="1">

### Week 15 · 2027.2.13 (토) — 계산 이력 방법, PCP

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L10** Computation History Method · Sipser **Ch.5.1 (LBA 부분), 5.2**
- **✏️ 연습문제 (~1.5h):** PCP 예제 손으로 풀기, 계산 이력 아이디어를 자기 말로 정리

</div>

<div class="session" data-session="16" markdown="1">

### Week 16 · 2027.2.20 (토) — 재귀 정리: 자기 자신을 아는 기계

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="16"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L11** Recursion Theorem and Logic (앞부분) · Sipser **Ch.6.1**
- **✏️ 연습문제 (~1.5h):** 🛠 C 또는 Python 으로 quine 작성 → 재귀 정리 증명 구조(A, B 부분)와 대응시키기

</div>

<div class="session" data-session="17" markdown="1">

### Week 17 · 2027.2.27 (토) — 논리 이론의 결정 가능성 ★ Gödel 과의 첫 만남

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="17"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L11** (뒷부분) · Sipser **Ch.6.2** (Th(ℕ,+) 결정 가능, Th(ℕ,+,×) 결정 불가능, 증명 불가능한 참인 문장)
- **✏️ 연습문제 (~1.5h):** Ch.6.2 의 "Turing-unprovable statement" 증명을 재귀 정리로 설명해 보기
- 💡 연결: [Busy Beaver Problem](/learning-cs/open-problems/busy-beaver/) 페이지. BB(n) 이 계산 불가능한 이유 = 정지 문제

</div>

<div class="session" data-session="18" markdown="1">

### Week 18 · 2027.3.6 (토) — Phase 1 복습 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="18"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Ch.3–6 노트 다시 보기, 이해 안 된 강의 부분 재시청
- **✏️ 연습문제 (~1.5h):** 밀린 연습문제, 또는 Claude 와 증명 검토 세션
- 🎯 **Phase 1 완료 점검:** TM · 결정 가능성 · 환원 · 재귀 정리를 설명할 수 있는가?

</div>

<div style="margin-top: 100px;"></div>

## Phase 2 · 1차 논리 복습

*Week 19–26 · 2027.3.13 ~ 2027.5.1 · Leary & Kristiansen Ch.1–3*

<div class="session" data-session="19" markdown="1">

### Week 19 · 2027.3.13 (토) — 1차 논리: 언어, 항, 논리식

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="19"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **§1.1–1.5** (Naïvely, Languages, Terms and Formulas, Induction, Sentences)
- **✏️ 연습문제 (~1.5h):** 자유 변수 / 속박 변수 구분 연습, 구조적 귀납법 증명 1개

</div>

<div class="session" data-session="20" markdown="1">

### Week 20 · 2027.3.20 (토) — 구조와 참 (⊨)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="20"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **§1.6–1.7** Structures, Truth in a Structure
- **✏️ 연습문제 (~1.5h):** 주어진 구조에서 문장의 참·거짓 판정 연습 3–4개
- 💡 핵심: ⊨ 은 "의미"의 세계다

</div>

<div class="session" data-session="21" markdown="1">

### Week 21 · 2027.3.27 (토) — 치환, 논리적 함의

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="21"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **§1.8–1.10** Substitutions and Substitutability, Logical Implication
- **✏️ 연습문제 (~1.5h):** 치환 가능성(substitutable) 연습문제, Σ ⊨ φ 판정 연습

</div>

<div class="session" data-session="22" markdown="1">

### Week 22 · 2027.4.3 (토) — 연역 (⊢)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="22"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **§2.1–2.4** Deductions, Logical Axioms, Rules of Inference
- **✏️ 연습문제 (~1.5h):** 짧은 형식 연역 2개를 직접 작성
- 💡 핵심: ⊢ 은 "기호 조작"의 세계다. 컴퓨터가 검사할 수 있다

</div>

<div class="session" data-session="23" markdown="1">

### Week 23 · 2027.4.10 (토) — 건전성, 비논리 공리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="23"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **§2.5–2.9** Soundness … Nonlogical Axioms (산술 공리 N 등장)
- **✏️ 연습문제 (~1.5h):** 건전성 정리 증명 흐름 요약, 공리 N 으로 간단한 사실 연역

</div>

<div class="session" data-session="24" markdown="1">

### Week 24 · 2027.4.17 (토) — 완전성 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="24"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **Ch.3** 앞부분: 완전성 정리의 진술 + Henkin 구성 개요 (세부 증명은 훑기만)
- **✏️ 연습문제 (~1.5h):** "완전성 정리(1929) vs 불완전성 정리(1931)" 차이를 한 문단으로 정리

</div>

<div class="session" data-session="25" markdown="1">

### Week 25 · 2027.4.24 (토) — 컴팩트성, 비표준 모형

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="25"> 완료</label>

- **📖 강의·읽기 (~1.5h):** L&K **Ch.3** 뒷부분: 컴팩트성 정리와 응용
- **✏️ 연습문제 (~1.5h):** 컴팩트성으로 비표준 자연수 모형이 존재함을 논증해 보기

</div>

<div class="session" data-session="26" markdown="1">

### Week 26 · 2027.5.1 (토) — Phase 2 복습 / 여유 주간

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="26"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Ch.1–3 노트 정리
- **✏️ 연습문제 (~1.5h):** 밀린 문제, 또는 Claude 와 ⊢ / ⊨ 문답
- 🎯 **마일스톤:** "증명 가능(⊢)"과 "참(⊨)"의 차이를 명확히 설명할 수 있다. 불완전성 이야기는 전부 이 차이 위에 있다

</div>

<div style="margin-top: 100px;"></div>

## Phase 3 · 불완전성 정리

*Week 27–39 · 2027.5.8 ~ 2027.7.31 · Gödel Without (Too Many) Tears 전체*

<div class="session" data-session="27" markdown="1">

### Week 27 · 2027.5.8 (토) — 불완전성이란 무엇인가

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="27"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.1–3** (Gödel 소개, Incompleteness the very idea, The First Theorem two versions)
- **✏️ 연습문제 (~1.5h):** "완전하다", "효과적으로 공리화되었다" 의 정의를 자기 말로 정리
- 💡 가볍게: Nagel & Newman *Gödel's Proof* 나머지

</div>

<div class="session" data-session="28" markdown="1">

### Week 28 · 2027.5.15 (토) — 증명 개요, 결정 불가능성과의 관계

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="28"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.4–5** Outlining a Gödelian proof, Undecidability and incompleteness
- **✏️ 연습문제 (~1.5h):** Ch.5 의 논증을 Sipser 의 정지 문제와 연결해 정리

</div>

<div class="session" data-session="29" markdown="1">

### Week 29 · 2027.5.22 (토) — 약한 산술 체계: BA, Q

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="29"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.6** Two weak arithmetics
- **✏️ 연습문제 (~1.5h):** Q 의 공리 목록 외우기, Q 에서 2+2=4 연역 따라가기

</div>

<div class="session" data-session="30" markdown="1">

### Week 30 · 2027.5.29 (토) — Peano 산술, 양화사 복잡도

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="30"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.7–8** First-order Peano Arithmetic, Quantifier complexity (+ Interlude)
- **✏️ 연습문제 (~1.5h):** Δ₀ / Σ₁ / Π₁ 문장 분류 연습. Gödel 문장이 Π₁ 이라는 점 기억하기

</div>

<div class="session" data-session="31" markdown="1">

### Week 31 · 2027.6.5 (토) — 원시 재귀 함수

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="31"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.9** Primitive recursive functions
- **✏️ 연습문제 (~1.5h):** 덧셈 → 곱셈 → 거듭제곱 → 소수 판정이 원시 재귀임을 보이기
- 🛠 Python 으로 원시 재귀 연산자(합성, 원시 재귀) 구현해 보기

</div>

<div class="session" data-session="32" markdown="1">

### Week 32 · 2027.6.12 (토) — 원시 재귀 함수의 표현과 포착

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="32"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.10** Expressing and capturing the primitive recursive functions
- **✏️ 연습문제 (~1.5h):** "표현(express)"과 "포착(capture)"의 차이 정리 (다시 ⊨ vs ⊢)

</div>

<div class="session" data-session="33" markdown="1">

### Week 33 · 2027.6.19 (토) — 구문의 산술화: Gödel 번호

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="33"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.11** The arithmetization of syntax
- **✏️ 연습문제 (~1.5h):** 🛠 Python 으로 논리식 ↔ Gödel 번호 인코더/디코더 작성
- 💡 "Prf(m, n): m 은 n 번 논리식의 증명이다"가 원시 재귀인 이유 = 증명 검사는 기계적이다

</div>

<div class="session" data-session="34" markdown="1">

### Week 34 · 2027.6.26 (토) — 제1 불완전성 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="34"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.12–13** First Incompleteness Theorem, semantic / syntactic version (+ Interlude)
- **✏️ 연습문제 (~1.5h):** 두 버전의 가정 차이 정리 (건전성 vs ω-무모순성)

</div>

<div class="session" data-session="35" markdown="1">

### Week 35 · 2027.7.3 (토) — 대각화 보조정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="35"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.14** The Diagonalization Lemma
- **✏️ 연습문제 (~1.5h):** 대각화 보조정리 증명을 재현하고, Week 16 의 quine 과 비교
- 💡 quine ≈ 대각화 보조정리 ≈ 재귀 정리. 모두 같은 아이디어

</div>

<div class="session" data-session="36" markdown="1">

### Week 36 · 2027.7.10 (토) — Rosser 정리, Tarski 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="36"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.15–16** Rosser's Theorem, Tarski's Theorem
- **✏️ 연습문제 (~1.5h):** Rosser 문장이 왜 ω-무모순성 가정을 없애는지, 산술적 참이 정의 불가능한 이유 정리

</div>

<div class="session" data-session="37" markdown="1">

### Week 37 · 2027.7.17 (토) — 재귀 함수, 정지 문제 (다시)

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="37"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.17–18** Recursive functions, Decidability and the Halting Problem
- **✏️ 연습문제 (~1.5h):** Sipser 의 TM 관점과 GWT 의 재귀 함수 관점이 같은 개념임을 정리

</div>

<div class="session" data-session="38" markdown="1">

### Week 38 · 2027.7.24 (토) — 제2 불완전성 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="38"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.19–20** The Second Theorem and Hilbert's Programme, Proving the Second Incompleteness Theorem
- **✏️ 연습문제 (~1.5h):** 유도 가능성 조건(derivability conditions) 세 개 정리, Con(PA) → G 의 흐름 따라가기

</div>

<div class="session" data-session="39" markdown="1">

### Week 39 · 2027.7.31 (토) — Phase 3 마무리: 나만의 증명 스케치

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="39"> 완료</label>

- **📖 강의·읽기 (~1.5h):** GWT **Ch.21** Complications + Appendix (Kripke on diagonalization)
- **✏️ 연습문제 (~1.5h):** 두 정리의 증명 스케치를 2–3 페이지로 직접 작성 → Claude 에게 검토 요청
- 🎯 **마일스톤:** 제1·제2 불완전성 정리를 증명 구조까지 설명할 수 있다
- 💡 더 깊이: Goodstein 정리, Paris–Harrington 정리 (PA 에서 증명 불가능한 "자연스러운" 참)

</div>

<div style="margin-top: 100px;"></div>

## Phase 4 · 계산 복잡도 (Sipser 2부)

*Week 40–48 · 2027.8.7 ~ 2027.10.2 · P, NP, PSPACE, L, NL*

<div class="session" data-session="40" markdown="1">

### Week 40 · 2027.8.7 (토) — 시간 복잡도

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="40"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L12** Time Complexity · Sipser **Ch.7.1**
- **✏️ 연습문제 (~1.5h):** big-O 연습, 다중 테이프 TM 을 단일 테이프로 바꿀 때의 시간 증가 분석

</div>

<div class="session" data-session="41" markdown="1">

### Week 41 · 2027.8.14 (토) — P 와 NP

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="41"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L14** P and NP, SAT, Poly-Time Reducibility · Sipser **Ch.7.2–7.3**
- **✏️ 연습문제 (~1.5h):** 문제 3개가 NP 에 속함을 검증자(verifier)로 보이기

</div>

<div class="session" data-session="42" markdown="1">

### Week 42 · 2027.8.21 (토) — NP-완전성

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="42"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L15** NP-Completeness · Sipser **Ch.7.4** 앞부분
- **✏️ 연습문제 (~1.5h):** 3SAT ≤p CLIQUE 환원 재현

</div>

<div class="session" data-session="43" markdown="1">

### Week 43 · 2027.8.28 (토) — Cook–Levin 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="43"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L16** Cook-Levin Theorem · Sipser **Ch.7.4** (Cook–Levin 증명)
- **✏️ 연습문제 (~1.5h):** tableau 구성의 각 부분 (φ_cell, φ_start, φ_move, φ_accept) 설명해 보기
- 🎯 **마일스톤:** SAT 가 NP-완전인 이유를 설명할 수 있다

</div>

<div class="session" data-session="44" markdown="1">

### Week 44 · 2027.9.4 (토) — NP-완전 문제 모음

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="44"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Sipser **Ch.7.5** (VERTEX-COVER, HAMPATH, SUBSET-SUM)
- **✏️ 연습문제 (~1.5h):** 환원 1개를 처음부터 스스로 설계해 보기
- 💡 이번 주는 여유 주간을 겸함

</div>

<div class="session" data-session="45" markdown="1">

### Week 45 · 2027.9.11 (토) — 공간 복잡도, Savitch 정리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="45"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L17** Space Complexity, PSPACE, Savitch's Theorem · Sipser **Ch.8.1–8.2**
- **✏️ 연습문제 (~1.5h):** Savitch 정리 증명의 재귀 구조 정리

</div>

<div class="session" data-session="46" markdown="1">

### Week 46 · 2027.9.18 (토) — PSPACE-완전성, 게임

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="46"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L18–L19** PSPACE-Completeness / Games, Generalized Geography · Sipser **Ch.8.3**
- **✏️ 연습문제 (~1.5h):** TQBF 가 PSPACE-완전인 이유 요약, 일반화 지리 게임 예제 풀기

</div>

<div class="session" data-session="47" markdown="1">

### Week 47 · 2027.9.25 (토) — L 과 NL

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="47"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L20** L and NL, NL = coNL · Sipser **Ch.8.4–8.6**
- **✏️ 연습문제 (~1.5h):** PATH ∈ NL 설명, NL = coNL 증명 흐름 요약

</div>

<div class="session" data-session="48" markdown="1">

### Week 48 · 2027.10.2 (토) — 계층 정리, 오라클

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="48"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 강의 **L21–L22** Hierarchy Theorems / Provably Intractable Problems, Oracles · Sipser **Ch.9.1–9.2**
- **✏️ 연습문제 (~1.5h):** 계층 정리에 다시 등장하는 대각선 논법 확인, 상대화가 P vs NP 에 주는 의미 정리
- 🎯 **Phase 4 완료:** P, NP, PSPACE, L, NL 의 관계도를 그릴 수 있다

</div>

<div style="margin-top: 100px;"></div>

## 여유 주간 + 회고

*Week 49–52 · 2027.10.9 ~ 2027.10.30 · 밀린 것 따라잡기, 선택 주제*

<div class="session" data-session="49" markdown="1">

### Week 49 · 2027.10.9 (토) — 여유 주간 1

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="49"> 완료</label>

- **📖 강의·읽기 (~1.5h):** 밀린 주차 따라잡기
- **✏️ 연습문제 (~1.5h):** 밀린 주차 따라잡기

</div>

<div class="session" data-session="50" markdown="1">

### Week 50 · 2027.10.16 (토) — 여유 주간 2 / 선택: 확률적 계산

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="50"> 완료</label>

- **📖 강의·읽기 (~1.5h):** (선택) 강의 **L23–L24** Probabilistic Computation, BPP · Sipser **Ch.10.2**
- **✏️ 연습문제 (~1.5h):** 밀린 주차 따라잡기 또는 BPP 연습문제

</div>

<div class="session" data-session="51" markdown="1">

### Week 51 · 2027.10.23 (토) — 여유 주간 3 / 선택: 대화형 증명

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="51"> 완료</label>

- **📖 강의·읽기 (~1.5h):** (선택) 강의 **L25–L26** Interactive Proof Systems, IP / coNP ⊆ IP · Sipser **Ch.10.4**
- **✏️ 연습문제 (~1.5h):** 밀린 주차 따라잡기

</div>

<div class="session" data-session="52" markdown="1">

### Week 52 · 2027.10.30 (토) — 1년 회고

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="52"> 완료</label>

- **📖 강의·읽기 (~1.5h):** Week 1 노트와 지금 노트 비교
- **✏️ 연습문제 (~1.5h):** 회고 글 작성: 가장 어려웠던 것, 가장 놀라웠던 것, 2년차에 할 것
- 🎯 **최종:** 이 블로그에 회고 페이지 게시

</div>


<script>
(function () {
  var STORAGE_KEY = 'toc-godel-study-plan-progress';

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
