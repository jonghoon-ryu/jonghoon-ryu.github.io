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

( FTL 과는 직접적인 관계는 없음 )

- 많은 사람들이 앱을 만들지만, 대부분 텍스트 위주 혹은 bat, py 위주의 앱
- 관리가 어렵고 직관적이지 않음
- 이 앱은 GUI 를 쉽게 만들 수 있게 하는 앱
- drag and drop 으로 영역, 박스, 라디오 버튼, 드롭 박스 등을 쉽게 만들 수 있음
- 동작은 해당 오브젝트를 눌러서 Claude 에게 해 달라고 하면 됨

![GUI 앱 빌더 화면 1]({{ '/ftl-visual-simulator/image/retrospective/gui-builder-1.png' | relative_url }})

![GUI 앱 빌더 화면 2]({{ '/ftl-visual-simulator/image/retrospective/gui-builder-2.png' | relative_url }})

### 두번째 앱 : FTL Visual Simulator

- open source FTL 앱을 visual simulator 로 변환하는 것

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

<div style="margin-top: 60px;"></div>

## 소회

(작성 예정)
