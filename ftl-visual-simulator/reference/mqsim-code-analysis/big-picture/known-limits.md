---
layout: default
title: 원본의 알려진 한계
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 원본의 알려진 한계

MQSim 원본으로 FTL 을 공부하거나 논문 수치를 낼 때 **믿으면 안 되는 것**과 **아예 없는 것**을 모았다. 모두 코드로 확인한 것이다.


<div style="margin-top: 60px;"></div>

## 1. 없는 기능

| 기대할 수 있는 것 | 실제 |
|---|---|
| **Hybrid(log-block) 매핑** | `Address_Mapping_Unit_Hybrid.cpp` 는 클래스 뼈대만 있고 로직이 비어 있다. 설정에 `HYBRID` 를 써도 실제로 구성되지 않는다 |
| **Bad block 관리** | 없다. `bad_block` 관련 코드가 전혀 없고, `Block_PE_Cycles_Limit` 도 block 을 퇴역시키지 않는다 |
| **FLIN 스케줄러** | `TSU_FLIN.*` 전체와 `SSD_Device.cpp` 의 생성부가 주석 처리되어 있다. 설정 파서는 `FLIN` 을 받지만 고르면 `No implementation is available …` 예외 ([TSU 정책 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/tsu-policies/)) |
| **TRIM / deallocate** | 없다. 호스트가 데이터를 지웠다고 알릴 방법이 없다(이 프로젝트가 직접 추가했다 — [Code Change](/ftl-visual-simulator/reference/code-change/upstream-diff/)) |
| **block 단위 Hot/cold 분리** | `Block_Pool_Slot_Type::Hot_block` 필드는 선언만 있고 어디서도 쓰지 않는다. 있는 것은 (a) 사용자 쓰기와 GC 쓰기를 나눈 "double write frontier", (b) 캐시의 bloom filter 가 "처음 보는 LPA 는 cold" 로 보고 곧바로 flash 에도 내리는 휴리스틱 뿐이다 |
| **ECC · read disturb · retention** | 모델링하지 않는다 |

## 2. 있지만 효과가 없는 설정

| 설정 | 왜 |
|---|---|
| `Initial_Occupancy_Percentage` (workload) | preconditioning 이 켜져 있을 때만 쓰인다. 기본 `ssdconfig.xml` 은 `Enabled_Preconditioning` = false |
| `GC_Hard_Threshold` | `Preemptible_GC_Enabled` = false 면 `GC_is_in_urgent_mode()` 가 이 값을 보기 전에 true 를 돌려준다 |
| `Block_PE_Cycles_Limit` | 통계 배열 크기를 정할 뿐 강제되지 않는다 |
| `<Intensity>` (workload) | 파서가 읽지 않는다. 읽는 것은 `Bandwidth` 뿐인데 `BANDWIDTH` 방식에서만 쓰인다 |
| `Static_Wearleveling_Threshold` | 원본에서는 SSD 설정으로 전달되지 않아 값을 바꿔도 소용없었다 → [고친 기록](/ftl-visual-simulator/reference/code-change/bug-list/wl-threshold-not-wired-bug/) |

## 3. 읽다가 놀라기 쉬운 동작

- **쓴 적 없는 LPA 를 읽으면 물리 page 가 소비된다.** 원본은 그 자리에서 page 를 예약한다([설명](/ftl-visual-simulator/reference/mqsim-code-analysis/read-before-write/)).
- **`FTL` 클래스는 껍데기다.** 이름만 보고 FTL 로직을 찾으면 빈 함수만 나온다. 일은 `Address_Mapping_Unit` · `Flash_Block_Manager` · `GC_and_WL_Unit` · `TSU` 가 한다.
- **`Do_warmup()` 은 비어 있다.** 데이터 캐시의 워밍업 함수는 `switch` 의 뼈대만 있고 본문이 없다. 캐시를 미리 채워 주지 않는다([데이터 캐시](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/data-cache/)).
- **우선순위 스케줄러의 서스펜드는 원본에서 한 번도 발동하지 않는다.** `TSU_Priority_OutOfOrder` 의 세 `switch` 가 `suspensionRequired = true` 다음에 `break` 없이 `default: return false` 로 떨어진다(`:417`, `:427`, `:528`). 이 프로젝트가 고친 내용은 [서스펜드·재개 버그](/ftl-visual-simulator/reference/code-change/bug-list/suspend-resume-deadlock-bug/) 에 있다.
- **합계 칸 `CMT_Misses` 는 일부 miss 를 빠뜨린다.** flash 에서 매핑을 읽어야 하는 miss 는 `…_For_Read/Write` 에만 센다([읽기 따라가기](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-read-path/)).
- **프로그램이 끝날 때 키 입력을 기다린다.** `main()` 마지막의 `cin.get()` 과 `PRINT_ERROR` 의 `cin.get()` 때문에 배치 실행에는 `echo |` 가 필요하다([디버깅](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-debugging/)).
- **GC 는 매 쓰기마다 검사하지 않는다.** write frontier 가 가득 차 새 block 을 받을 때만 검사한다.
- **객체의 `Start_simulation()` 호출 순서가 정해져 있지 않다.** 엔진이 `unordered_map` 을 돈다.
- **정적 마모평준화가 거의 발동하지 않는다.** 대상 선정이 plane 전체의 가장 덜 닳은 block 만 보는데, 그것이 대개 아직 쓰지 않은 frontier 라서 "안전하지 않음" 으로 거절된다 → [고친 기록](/ftl-visual-simulator/reference/code-change/bug-list/wl-target-and-stall-bugs/).

## 4. 실제 버그

이 프로젝트가 원본을 컴파일해 작은 규모와 반복 실행으로 돌리면서 **28개의 버그**를 찾아 고쳤다 — 이식성 문제, use-after-free, 초기화되지 않은 필드, 전달되지 않는 설정, 스케줄러의 서스펜드 교착, 조용히 멈추는 시뮬레이션, GC victim 선정 오류 등. 대부분은 큰 SSD 를 한 번 끝까지 돌리는 원래 용도에서는 드러나지 않는다.

- [버그 목록표](/ftl-visual-simulator/reference/code-change/bug-list/table/) — 전체 요약
- [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/code-change/upstream-diff/) — 코드 차이 전체


<div style="margin-top: 60px;"></div>

## 관련 문서

- [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) · [Code Change](/ftl-visual-simulator/reference/code-change/)
