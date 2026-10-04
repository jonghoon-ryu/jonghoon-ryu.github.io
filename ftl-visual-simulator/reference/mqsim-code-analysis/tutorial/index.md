---
layout: default
title: 튜토리얼 — MQSim 을 한 단계씩
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 튜토리얼 — MQSim 을 한 단계씩, FTL 중심으로

터미널에서 `./MQSim` 을 실행하는 순간부터 시작해, **함수 호출을 하나씩 따라가며** FTL 이 요청을 처리하는 과정을 이해하는 튜토리얼이다. 앞쪽 단계(1~5)는 FTL 에 닿기까지의 길이고, 뒤쪽 단계(6~10)가 FTL 자체다.


<div style="margin-top: 60px;"></div>

## 준비

```bash
git clone https://github.com/CMU-SAFARI/MQSim && cd MQSim
git checkout 51f0f2d      # 이 문서가 기준으로 삼은 커밋 (줄 번호도 이 커밋의 것)
make
./MQSim -i ssdconfig.xml -w workload.xml
```

- 코드를 **옆에 열어 두고** 읽는 것이 좋다. 각 단계마다 `파일:줄` 을 적어 두었다.
- 먼저 [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/)을 훑어보면 용어와 전체 구조가 익숙해져서 따라가기 쉽다. 특히 [요청 하나가 지나가는 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/) 과 [FTL 의 부품들](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) 이 지도 역할을 한다.
- 기본 `ssdconfig.xml` 과 `workload.xml` 로 설명하며, 숫자(채널 수, 지연 시간 …)는 그 값이다.


<div style="margin-top: 60px;"></div>

## 단계

| 단계 | 내용 |
|---|---|
| [1. 실행 명령과 main()](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step1-run-and-main/) | `./MQSim -i … -w …` 부터 설정·workload 읽기, 시나리오 루프까지 |
| [2. SSD 와 호스트 만들기](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step2-build-ssd/) | `SSD_Device` 와 `Host_System` 이 부품을 만들고 연결하는 법 |
| [3. 엔진 시작과 이벤트 루프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/) | 신호 연결 · 검증 · 초기화 · 이벤트 루프 |
| [4. 요청의 탄생 — SSD 입구까지](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step4-request-enters/) | 호스트가 요청을 만들어 NVMe · PCIe 를 건너 SSD 에 닿고 page 단위로 쪼개지기까지 |
| [5. 데이터 캐시 — FTL 의 문턱](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step5-cache/) | 캐시 모드별 갈림길과 FTL 입구(`Translate_lpa_to_ppa_and_dispatch`) |
| [6. FTL ① 주소 변환](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/) | CMT hit/miss, translation page 읽기 |
| [7. FTL ② 쓰기와 page 할당](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/) | plane 결정 · 옛 page invalid · 새 page 할당 · 매핑 갱신 |
| [8. FTL ③ 스케줄러와 플래시 칩](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/) | TSU 의 큐와 우선순위, PHY · 칩, 완료 신호 |
| [9. FTL ④ 가비지 컬렉션](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/) | 트리거 · victim 정책 · page 이동 · erase |
| [10. FTL ⑤ 마모평준화](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/) | dynamic(free pool 정렬) · static(cold 데이터 꺼내기)와 원본의 함정 |
| [11. 마무리 — 전체 콜 그래프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step11-wrapup/) | 요청 완료, 결과 파일, 전체 콜 그래프, 다음 읽을 곳 |


<div style="margin-top: 60px;"></div>

## 부록

| 부록 | 내용 |
|---|---|
| [A. 읽기 요청 따라가기](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-read-path/) | 본문은 쓰기 중심이었다. 읽기는 CMT · barrier · 캐시 부분 hit 와 어떻게 만나나 |
| [B. 완료 경로](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-completion/) | flash 연산이 끝난 뒤 신호가 올라가 호스트 통계가 바뀌기까지 |
| [C. 디버깅과 작은 실험](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-debugging/) | 빌드 · 20개 요청 실험 · `DEBUG` 로그 · gdb |
| [D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) | 각 단계 끝 문제의 답과 근거 줄 |


<div style="margin-top: 60px;"></div>

## 이 튜토리얼을 읽는 요령

- **"이 함수가 이벤트를 예약하는가?"** 를 먼저 본다. 예약하면 흐름이 끊기고 나중에 이어진다([이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/)).
- **FTL 객체는 껍데기다.** 이름만 따라가면 빈 함수만 나온다. FTL 의 일은 AMU · 블록 매니저 · GC/WL · TSU 가 한다.
- 각 단계 끝의 **확인해 보기**는 코드를 열어야 답이 나온다. 답을 아는 것보다 **답을 찾는 줄을 아는 것**이 목표다.
- 원본에 알려진 함정이 있는 곳에는 그렇다고 적고 [Code Change](/ftl-visual-simulator/reference/code-change/) 로 연결했다.


<div style="margin-top: 60px;"></div>

## 관련 문서

- [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) — 구조를 먼저 보고 싶다면
- [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim-code-analysis/)
