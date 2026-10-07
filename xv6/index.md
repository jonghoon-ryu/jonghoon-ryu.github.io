---
layout: default
title: xv6
permalink: /xv6/
---
# xv6 를 C++ 로 다시 쓰기

MIT 의 교육용 OS **xv6-riscv** 를 x86-64 PC 로 옮기고, 그 코드를 **C 에서 C++ 로** 한 조각씩 다시 쓴다.

<div style="margin-top: 100px;"></div>

## 페이지

- [목표](/xv6/goal/) — 지금까지 한 일, 앞으로 할 일, 최종 목표
- [계획](/xv6/plan/) — 토요일·일요일 각 2시간씩, 단계별 일정
- [할 일](/xv6/todo/) — 실제 PC 시험 끝 (USB 키보드 동작). 남은 일 : USB 의 빠진 부분, 정리할 것

<div style="margin-top: 100px;"></div>

## 저장소

- [github.com/jonghoon-ryu/xv6-x86_64](https://github.com/jonghoon-ryu/xv6-x86_64)
  - `main` 브랜치 : x86-64 로 포팅된 C 버전, 완성. 태그 `v0.1-x86_64-c` (시리얼만), `v0.2-x86_64-c` (+ 화면 콘솔, 키보드. C++ 변환의 비교 기준)
  - `cpp` 브랜치 : C++ 변환 작업 중
