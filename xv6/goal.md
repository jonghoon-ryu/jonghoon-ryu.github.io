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

<div style="margin-top: 100px;"></div>

## 1단계 : RISC-V → x86-64 포팅 (완료)

xv6-riscv 를 64비트 x86 PC 에서 돌도록 옮겼다. 언어는 C 그대로.

- 저장소 : [github.com/jonghoon-ryu/xv6-x86_64](https://github.com/jonghoon-ryu/xv6-x86_64), `main` 브랜치, 태그 `v0.1-x86_64-c`
- QEMU (CPU 1개·4개) 와 VirtualBox 에서 `usertests` 전체 통과
- 화면 콘솔과 PS/2 키보드까지 붙여서 VirtualBox 창에서 바로 셸을 쓸 수 있다

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
   - 매 단계마다 빌드하고 QEMU · VirtualBox 에서 부팅되는 것을 확인한다
   - C 버전 (`main` 브랜치) 이 그대로 남아 있어서 언제든 나란히 비교할 수 있다

지금 상태 — C++ 커널이 VirtualBox 화면에 그린 글자 :

![C++ 스켈레톤이 그린 xv6](/assets/image/xv6-cpp-skeleton.png)

<div style="margin-top: 100px;"></div>

## 최종 목표

**C 코드를 C++ 로 완전히 번역한다.** 커널과 사용자 프로그램 모두.

- 다시 셸 (`$`) 이 뜨고 `usertests` 가 전부 통과해야 끝
- QEMU, VirtualBox, 그리고 실제 PC 에서도 부팅

<div style="margin-top: 100px;"></div>

## 원칙

- **언제나 부팅되는 상태 유지** : 어느 단계에서 멈춰도 커널은 부팅된다
- **책과 대조 가능하게** : 파일 이름과 함수 이름은 원본 xv6 를 따른다
- **freestanding C++20** : 예외, RTTI, 표준 라이브러리 없음
  - `#define` 상수 → `constexpr`, 매크로 → `inline` 함수, 플래그 → `enum class`
  - `acquire`/`release` → RAII `LockGuard`
  - 멤버 함수는 자연스러운 곳에만
- **어셈블리 (`.S`) 는 그대로** 둔다
