---
layout: default
title: 시뮬레이터 실행
permalink: /ftl-visual-simulator/run-simulator/
---
<style>
.run-sim-cta {
  display: block;
  margin: 1.5rem 0;
  padding: 1.1rem 1.4rem;
  border-radius: 10px;
  background: #2f6fd6;
  color: #fff !important;
  text-decoration: none;
  font-weight: 700;
  font-size: 1.05rem;
  text-align: center;
}
.run-sim-cta:hover {
  background: #24589f;
}
</style>

# 시뮬레이터 실행

FTL 시각화 시뮬레이터를 브라우저에서 직접 열어볼 수 있는 링크. `main` 브랜치에 코드가 머지(push)될 때마다 자동으로 다시 배포되므로, 항상 최신 상태를 보여준다.

<a class="run-sim-cta" href="https://jonghoon-ryu.github.io/ftl-visual-simulator-app/" target="_blank" rel="noopener">▶ 시뮬레이터 열기 (jonghoon-ryu.github.io/ftl-visual-simulator-app)</a>

<div style="margin-top: 40px;"></div>

## 지금 상태 (2026-10-04)

**동작하는 시뮬레이터다.** 세 프리셋이 모두 실제 MQSim WASM 엔진 위에서 돌고, 화면에 보이는 숫자와 그림은 전부 그 엔진이 낸 값이다(가짜 목업 데이터는 없다).

| 프리셋 | 보여주는 개념 | 눈여겨볼 것 |
|---|---|---|
| **매핑 기본** | 주소 매핑, out-of-place update | 로그의 LPN 을 클릭하면 그 데이터가 거친 물리 page 의 여정이 격자에 표시된다 |
| **GC 시연** | 가비지 컬렉션, WAF, Over-provisioning | 격자 위 "왜 이 block 을 골랐나요?", 그리고 오른쪽 **비교 실험실** 탭 |
| **마모평준화 시연** | dynamic / static 마모 평준화 | block 별 erase 횟수와 cold/hot 데이터 열, static WL 이 발동하면 재생이 자동으로 멈춘다 |

처음이라면 화면 위쪽의 **레슨 바**를 따라 매핑 → GC → 마모평준화 순으로 보면 된다. 첫 방문에는 "왜 FTL 이 필요할까?" 인트로가 먼저 열린다.

<div style="margin-top: 60px;"></div>

## 화면 구성

- **위쪽**: 레슨 바(지금 무엇을 볼지 안내) · 프리셋 탭 · 재생 컨트롤(⏮ 처음부터, ▶ 재생, 속도, "로그 1줄" · "로그 5줄" 단계 실행 — `→` 키로도 한 줄씩).
- **왼쪽**: flash 격자(block × page, 색 = valid · invalid · 이동 중 · free). 위에 "예측해보기" 퀴즈.
- **가운데**: 이벤트 로그. 줄을 클릭하면 그 LPN 을 따라간다.
- **오른쪽 — 두 개의 탭**
  - **설정 · 통계**(기본): 파라미터(칩 · block · page 개수, Over-provisioning, GC 임계값 …), workload(접근 패턴, 읽기 비율, DRAM 쓰기 캐시), 통계(WAF, valid page 비율, GC · WL 횟수 …). 자주 안 쓰는 설정은 "고급 설정" 안에 접혀 있다.
  - **비교 실험실**(**GC 시연에서만** 나타남): 같은 설정으로 시뮬레이션을 끝까지 다시 돌려서 비교하는 실험 5개와, 재생을 따라가는 차트 2개.
- 용어에 점선 밑줄이 있으면 마우스를 올리거나 Tab 으로 포커스하면 쉬운 말 설명이 뜬다. 오른쪽 아래 "사용법" 버튼에는 더 자세한 안내가 있다.

### 비교 실험실에 있는 것

| 실험 | 알려주는 것 |
|---|---|
| GC 알고리즘 비교 | 7개 victim 선정 정책의 GC 비용과 WAF |
| TRIM | 호스트가 데이터를 지웠다고 알리면(TRIM) GC 가 싸지는 정도. "지금 TRIM 하기" 로 격자의 valid page 가 invalid 로 바뀌는 것도 볼 수 있다 |
| 핫/콜드 분리 | 자주 바뀌는 데이터와 안 바뀌는 데이터를 같은 block 에 섞어 쓸 때와 분리해 쓸 때의 WAF |
| 순차 vs 무작위 쓰기 | 쓰기 패턴이 GC 비용에 미치는 영향 |
| Over-provisioning 별 WAF | OP 0~30% 곡선 |
| 빈 block 수 변화 (맨 아래) | 빈 block 이 임계값 아래로 내려가면 GC 가 시작되는 톱니 모양 |
| 읽기 지연 (맨 아래) | GC 가 도는 동안 읽기가 느려지는 정도 |

<div style="margin-top: 60px;"></div>

## 알려진 제한

- **Hybrid(log-block) 매핑은 없다.** 원본 MQSim 에도 구현돼 있지 않아서 선택할 수 없다([원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/)).
- 화면에 다 그리려고 **작은 SSD**(기본 block 12~24개, 채널·다이·플레인은 1개 고정, 칩 1/2/4개)를 돌린다. 같은 로직을 줄인 것이다.
- Bad block · ECC 는 원본에 없어서 다루지 않는다.
- 휴대폰 폭 레이아웃은 따로 확인하지 않았다.

<div style="margin-top: 60px;"></div>

## 참고

- [개발 계획](/ftl-visual-simulator/plan/) — 어떻게 여기까지 왔는지
- [Code Change](/ftl-visual-simulator/reference/code-change/) — 엔진이 원본 MQSim 과 다른 점
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드 · README · 테스트
