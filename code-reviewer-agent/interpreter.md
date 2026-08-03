---
layout: default
title: 3주차 교육 (Interpreter 만들기)
permalink: /code-reviewer-agent/interpreter/
---
# Interpreter 란 ?

* 소스 코드(텍스트)를 입력받아 그 자리에서 바로 실행하고  결과를 내놓는 프로그램
* 컴파일러처럼 별도의 실행 파일을 만드는 게 아니라, 코드를 읽으면서 즉시 해석·실행한다는 점이 핵심



<div style="margin-top: 100px;"></div>

## 프로젝트를 위한 언어 문법

문법 트리는 Token → Expr/Stmt 두 종류의 노드로 구성되며, 규칙은 다음 원칙을 따름

- Expr(표현식): 실행하면 값 하나로 평가(evaluate)되는 단위. Expr과 Token을 조합해서 만든다.
- Stmt(문장): 값 반환 없이 동작을 수행하는 단위. Expr, Stmt, Token을 조합해서 만든다.
- 제약: Expr 내부의 자식으로 Stmt를 가질 수 없다 (Stmt는 Expr을 가질 수 있지만 역은 불가). 트리의 루트는 항상 Stmt.
- Token 자체는 노드가 아니라 각 노드의 필드로만 보관된다(예: `=`, `;` 같은 실행에 불필요한 토큰은 트리에 노드로 남지 않음).
- Assembler Unit 과 checker Unit 사이의  interface : AST ( Abstract Syntax Tree)


<div style="margin-top: 100px;"></div>

### Expr 종류

| Expr     | 예시                      | 의미           |
| -------- | ------------------------- | -------------- |
| Literal  | `3`, `"hi"`, `true` | 리터럴 값 생성 |
| Variable | `a`                     | 변수 참조      |
| Assign   | `a = 3`                 | 변수 대입      |
| Binary   | `1 + 2`, `a > 0`      | 이항 연산      |
| Unary    | `-x`, `!isExist`      | 단항 연산      |
| Grouping | `(1 + 2)`               | 괄호 묶음      |
| Logical  | `a and b`               | 논리 연산      |

### Stmt 종류

| Stmt       | 예시                                          |
| ---------- | --------------------------------------------- |
| Expression | `a + 1;` (Expr을 감싸는 Wrapper)            |
| Print      | `print a;`                                  |
| VarDeclare | `var a = 3;`                                |
| Block      | `{ ... }`                                   |
| If         | `if (a > 0) { ... } else { ... }`           |
| For        | `for (var i = 0; i < 3; i = i + 1) { ... }` |



<div style="margin-top: 100px;"></div>

# 전체 파이프 라인

```
소스코드 입력                                                  실행 결과
     │                                                              ▲
     ▼                                                              │
  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ Assembler Unit   │───▶│  Checker Unit    │───▶│  Executor Unit   │
  │                  │    │                  │    │                  │
  │ 1) 소스코드 →    │    │ 문법 트리를 DFS  │    │ 문법 트리를 DFS  │
  │    Token 분해     │    │ 순회하며 의미    │    │ 순회하며 실제    │
  │ 2) Token →        │    │ 오류 검사        │    │ 실행             │
  │    Expr/Stmt 조립 │    │ (중복선언,       │    │ (변수 저장소     │
  │    (문법 트리)     │    │  자기참조 등)    │    │  읽기/쓰기 등)   │
  └─────────────────┘    └──────────────────┘    └──────────────────┘
```


<div style="margin-top: 100px;"></div>


# 목표

* TDD 를 이용하여 각 pipeline 단계를 구현하고 최종적으로 전체를 테스트 할 수 있는 UT 를 만든다.



<div style="margin-top: 100px;"></div>

# 실행결과

* 입력
  ![입력]({{ '/code-reviewer-agent/image/interpreter/1785721055882.png' | relative_url }})
* 출력
  ![출력]({{ '/code-reviewer-agent/image/interpreter/1785721084221.png' | relative_url }})
