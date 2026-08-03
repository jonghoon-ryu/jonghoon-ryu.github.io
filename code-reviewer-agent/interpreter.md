---
layout: default
title: 3주차 교육 (Interpreter 만들기)
permalink: /code-reviewer-agent/interpreter/
---
# Interpreter 란 ?

* 소스 코드(텍스트)를 입력받아 그 자리에서 바로 실행하고  결과를 내놓는 프로그램
* 컴파일러처럼 별도의 실행 파일을 만드는 게 아니라, 코드를 읽으면서 즉시 해석·실행한다는 점이 핵심

## 프로젝트를 위한 언어 문법

문법 트리는 Token → Expr/Stmt 두 종류의 노드로 구성되며, 규칙은 다음 원칙을 따릅니다.

- Expr(표현식): 실행하면 값 하나로 평가(evaluate)되는 단위. Expr과 Token을 조합해서 만든다.
- Stmt(문장): 값 반환 없이 동작을 수행하는 단위. Expr, Stmt, Token을 조합해서 만든다.
- 제약: Expr 내부의 자식으로 Stmt를 가질 수 없다 (Stmt는 Expr을 가질 수 있지만 역은 불가). 트리의 루트는 항상 Stmt.
- Token 자체는 노드가 아니라 각 노드의 필드로만 보관된다(예: `=`, `;` 같은 실행에 불필요한 토큰은 트리에 노드로 남지 않음).

### Expr 종류

| Expr | 예시 | 의미 |
|---|---|---|
| Literal | `3`, `"hi"`, `true` | 리터럴 값 생성 |
| Variable | `a` | 변수 참조 |
| Assign | `a = 3` | 변수 대입 |
| Binary | `1 + 2`, `a > 0` | 이항 연산 |
| Unary | `-x`, `!isExist` | 단항 연산 |
| Grouping | `(1 + 2)` | 괄호 묶음 |
| Logical | `a and b` | 논리 연산 |

### Stmt 종류

| Stmt | 예시 |
|---|---|
| Expression | `a + 1;` (Expr을 감싸는 Wrapper) |
| Print | `print a;` |
| VarDeclare | `var a = 3;` |
| Block | `{ ... }` |
| If | `if (a > 0) { ... } else { ... }` |
| For | `for (var i = 0; i < 3; i = i + 1) { ... }` |
