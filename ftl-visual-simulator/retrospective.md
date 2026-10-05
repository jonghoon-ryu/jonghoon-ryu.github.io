---
layout: default
title: 9/4 - 10/5 동안 뭘 했을까... 그리고 어땠을까
permalink: /ftl-visual-simulator/retrospective/
---
# 9/4 - 10/5 동안 뭘 했을까... 그리고 어땠을까

## 왜 시작했을까

Code Review Agent 는 현업 과제로, 여러 옵션이 있었음.

- 그 중 하나는 TDD 를 이용한 코드 개발
- 다른 하나는 업무에 도움이 되는 앱 개발
- 현 상황에 비추어 보면, 업무에 도움이 되는 앱 개발 쪽이 맞다고 판단


### 첫번째 앱 : 앱을 만드는 앱

( FTL 과는 직접적인 관계는 없음 ) — [GitHub : ai-gui-builder-app](https://github.com/jonghoon-ryu/ai-gui-builder-app)

- 많은 사람들이 앱을 만들지만, 대부분 텍스트 위주 혹은 bat, py 위주의 앱
- 관리가 어렵고 직관적이지 않음
- 이 앱은 GUI 를 쉽게 만들 수 있게 하는 앱
- drag and drop 으로 영역, 박스, 라디오 버튼, 드롭 박스 등을 쉽게 만들 수 있음
- 동작은 해당 오브젝트를 눌러서 Claude 에게 해 달라고 하면 됨

![GUI 앱 빌더 화면 1]({{ '/ftl-visual-simulator/image/retrospective/gui-builder-1.png' | relative_url }})

![GUI 앱 빌더 화면 2]({{ '/ftl-visual-simulator/image/retrospective/gui-builder-2.png' | relative_url }})

### 두번째 앱 : FTL Visual Simulator

- open source FTL 앱을 visual simulator 로 변환하는 것
- [GitHub : ftl-visual-simulator-app](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)

<div style="margin-top: 60px;"></div>

## FTL Visual Simulator : 계획과 실제

1. GitHub 에 있는 다양한 open source 중에서 MQSim 선정 ( [선정 이유](/ftl-visual-simulator/reference/mqsim/#결론--왜-mqsim-인가) )
2. 지난 번 app 으로 만들었을 때의 문제점
    - 사람들이 앱 설치를 귀찮아 함
    - 앱을 믿지 않음 ( 보안 등 )
    - 그러나 웹에서 실행하도록 하면 안전함 ( sandbox )
3. 웹에서 해당 open source 를 눈으로 볼 수 있도록 visual simulator 를 만듦 ( 거의 대부분 Claude 가 함 )
4. 동작시켜 보고 Claude 에게 수정하도록 하는 일을 반복하여 기본 기능 완성
5. 원래 코드에 없던 내용 추가 ( [원본 대비 변경 사항](/ftl-visual-simulator/reference/code-change/upstream-diff/), [Code Change](/ftl-visual-simulator/reference/code-change/) )
    - 새 기능 : Cost-Benefit GC 정책, TRIM, 한 번도 안 쓴 LPA 읽기 옵션 ( `Unmapped_Reads_Return_Zeros` ) — [6절](/ftl-visual-simulator/reference/code-change/upstream-diff/)
    - 시뮬레이터를 위한 변경 — [7절](/ftl-visual-simulator/reference/code-change/upstream-diff/)
    - 화면에 다 보이도록 block 수를 줄인 데모 규모 튜닝 — [튜닝된 코드](/ftl-visual-simulator/reference/code-change/tweaked-code/)
    - 이 과정에서 원본의 버그 28개도 발견해서 수정 — [버그 목록](/ftl-visual-simulator/reference/code-change/bug-list/)

<div style="margin-top: 60px;"></div>

## 소회

처음에는 코드 분석과 구현을 동시에 진행하려고 했었다. 그러나 하다 보니 구현을 먼저 하게 되었다.

구현을 먼저 한 이유 중 하나는 Claude 가 처음에 좀 자신 없는 듯한 말투로 "어떤 어떤 위험이 있다" 라고 해서, 일단 되는지부터 해 본 것이다.

구현하면서, 그리고 동작시키면서 문제점을 수정해 나가다 보니 코드는 수박 겉핥기로만 알고, 실제로 나는 Claude 가 구현한 것을 동작시켜 보는 오퍼레이터가 되어 있었다.

MQSim 이라는 원본 코드가 FTL 의 일부만을 구현한 코드다 보니, 원본을 변환한 Visual Simulator 또한 한계가 있다.

어디까지를 Claude 에게 맡겨야 하고, 어디까지를 직접 검수해야 할 것인가가 중요하다.
