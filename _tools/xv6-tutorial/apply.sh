#!/bin/bash
# apply.sh : (re)insert every figure into every tutorial page. idempotent.
set -e
cd "$(dirname "$0")"
F() { python3 fig.py "$@"; }
M='^## 2\. 바꾼 것'
# change maps (one per tag page)
for t in v0.1-x86_64-c v0.2-x86_64-c step-01 step-02 step-03 step-04 step-05 step-06 step-07 step-08 step-09 step-10; do
  F $t "map_${t//[-.]/_}" "$M" maps
done
# v0.1
F v0.1-x86_64-c regmap '^진짜로 바뀐 것은 아래' v01
F v0.1-x86_64-c pagewalk '^PTE 의 비트 이름은' v01
F v0.1-x86_64-c ptebits '^<!-- /fig:pagewalk -->' v01
F v0.1-x86_64-c swtch 'jmp \*0\(%rsi\)' v01
# index (big picture)
F index system '^## 태그' index
F index lines '^<!-- /fig:system -->' index
# v0.2
F v0.2-x86_64-c backspace '^`console.c` 는 한 글자마다' v02
F v0.2-x86_64-c kbdflow '^### 2\.2 PS/2 키보드' v02
# step-01
F step-01 mangle '^### 2\.2 `start\.cpp`' step01
F step-01 pipeline '^### 2\.4 `Makefile`' step01
# step-02
F step-02 uartinit '^### 2\.1 `uart\.cpp`' step02
F step-02 lsrbits '^<!-- /fig:uartinit -->' step02
# step-03
F step-03 printkflow '^### 2\.1 `printk\.cpp`' step03
F step-03 printint '^<!-- /fig:printkflow -->' step03
# step-04
F step-04 beforeafter '^## 1\. 이전 상태' step04
F step-04 cursorrules '^### 2\.1 `fbcons\.cpp`' step04
# step-05
F step-05 ps2bits '^### 2\.2 `kbd\.cpp`' step05
F step-05 ring '^### 2\.3 `console\.cpp` 의' step05
# step-06
F step-06 pcitree '^### 2\.1 `pci\.cpp`' step06
F step-06 gate '^### 2\.2 `earlyvec\.S`' step06
# step-07
F step-07 regspace '^### 2\.2 컨트롤러 시작' step07
F step-07 dcbaa '^<!-- /fig:regspace -->' step07
F step-07 portsc '^### 2\.3 포트' step07
# step-08
F step-08 contexts '^### 2\.2 slot 과 컨텍스트' step08
F step-08 lifecycle '^<!-- /fig:contexts -->' step08
# step-09
F step-09 dci '^### 2\.1 키보드 설정' step09
F step-09 keypath '^### 2\.3 리포트' step09
# step-10
F step-10 route '^### 2\.2 허브의 포트마다' step10
F step-10 tt '^<!-- /fig:route -->' step10
F step-10 hubstatus '^<!-- /fig:tt -->' step10
