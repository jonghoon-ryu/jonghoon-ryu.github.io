---
layout: default
title: xv6 튜토리얼
permalink: /xv6/tutorial/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
table { font-size:0.88rem; }
</style>

# 튜토리얼 : 태그를 따라가며 코드 읽기

저장소 [jonghoon-ryu/xv6-x86_64](https://github.com/jonghoon-ryu/xv6-x86_64) 의 **git 태그 하나마다 한 페이지**.
각 페이지는 세 부분으로 되어 있다 :

1. **이전 상태** — 바로 앞 태그에서 코드가 어땠고 무엇을 했나
2. **바꾼 것** — 파일마다, 무엇을 왜 바꿨나. 코드 조각은 그 태그의 실제 코드에서 그대로 가져왔고, 링크는 GitHub 의 그 태그, 그 줄로 간다
3. **바뀐 뒤** — 부팅하면 무엇이 달라졌나 (화면, 사진)

그림의 색 : <span style="background:#eafaf1;border:1px solid #1e8449;padding:0 4px">새로 생김</span>
<span style="background:#fef9e7;border:1px solid #b7950b;padding:0 4px">바뀜</span>
<span style="background:#fdedec;border:1px solid #c0392b;padding:0 4px">지움</span>
<span style="background:#f4ecf7;border:1px solid #7d3c98;padding:0 4px">하드웨어, 펌웨어</span>

<svg viewBox="0 0 1000 300" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="태그 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">태그의 순서 : 각 태그는 바로 앞 태그에서 출발한다</text><text x="20.0" y="62.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">main 브랜치 (C)</text><text x="80.0" y="178.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">cpp 브랜치 (C++)</text><rect x="20" y="75" width="130" height="54" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="85.0" y="98.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">06aad25</text><text x="85.0" y="114.0" font-size="11.0" fill="#4d5656" text-anchor="middle">MIT xv6-riscv</text><rect x="190" y="75" width="150" height="54" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="265.0" y="98.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">v0.1-x86_64-c</text><text x="265.0" y="114.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86-64 포팅 (C)</text><rect x="380" y="75" width="150" height="54" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="455.0" y="98.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">v0.2-x86_64-c</text><text x="455.0" y="114.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ 화면, 키보드</text><line x1="150" y1="102" x2="188" y2="102" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="340" y1="102" x2="378" y2="102" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="190" width="88" height="46" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="64.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-01</text><rect x="115" y="190" width="88" height="46" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="159.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-02</text><line x1="108" y1="213" x2="115" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="210" y="190" width="88" height="46" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="254.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-03</text><line x1="203" y1="213" x2="210" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="305" y="190" width="88" height="46" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="349.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-04</text><line x1="298" y1="213" x2="305" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="400" y="190" width="88" height="46" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="444.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-05</text><line x1="393" y1="213" x2="400" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="495" y="190" width="88" height="46" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="539.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-06</text><line x1="488" y1="213" x2="495" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="590" y="190" width="88" height="46" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="634.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-07</text><line x1="583" y1="213" x2="590" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="685" y="190" width="88" height="46" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="729.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-08</text><line x1="678" y1="213" x2="685" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="780" y="190" width="88" height="46" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="824.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-09</text><line x1="773" y1="213" x2="780" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="875" y="190" width="88" height="46" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="919.0" y="217.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">step-10</text><line x1="868" y1="213" x2="875" y2="213" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><path d="M455,129 L455,150 L64,150 L64,188" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="470.0" y="154.0" font-size="10.5" fill="#566573" text-anchor="start">← C 판을 거의 다 지우고 부팅 뼈대만 남긴 뒤 다시 쌓는다</text><text x="232.0" y="262.0" font-size="11" fill="#4d5656" text-anchor="middle">Step 1–5 : 부팅, 콘솔, 화면, 키보드 (C 판에서 옮김)</text><text x="737.0" y="262.0" font-size="11" fill="#4d5656" text-anchor="middle">Step 6–10 : USB 키보드 (실제 PC 때문에 새로 씀)</text><rect x="380" y="280" width="14" height="12" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="400.0" y="290.0" font-size="10.5" fill="#4d5656" text-anchor="start">C 판의 코드를 C++ 로</text><rect x="592" y="280" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="612.0" y="290.0" font-size="10.5" fill="#4d5656" text-anchor="start">C 판에 없던 코드</text></svg>

## 태그

| 태그 | 앞 태그 | 한 줄 요약 |
|---|---|---|
| [`v0.1-x86_64-c`](/xv6/tutorial/v0.1-x86_64-c/) | MIT `06aad25` | xv6-riscv 를 x86-64 PC 로 옮김 (C). UEFI 부팅, CPU 여러 개, `usertests` 통과. 입출력은 시리얼만 |
| [`v0.2-x86_64-c`](/xv6/tutorial/v0.2-x86_64-c/) | `v0.1-x86_64-c` | + 화면 콘솔 (GOP 프레임버퍼, 글꼴), PS/2 키보드 |
| [`step-01`](/xv6/tutorial/step-01/) | `v0.2-x86_64-c` | C++ 판의 출발 : 부팅 뼈대만 남기고 지움. `start.cpp`, `main.cpp` |
| [`step-02`](/xv6/tutorial/step-02/) | `step-01` | `uart.cpp`, `string.cpp` : 시리얼 출력 |
| [`step-03`](/xv6/tutorial/step-03/) | `step-02` | `printk.cpp`, `console.cpp` : `printk()`, `panic()` |
| [`step-04`](/xv6/tutorial/step-04/) | `step-03` | `fbcons.cpp`, `font.h` : 화면에 글자 |
| [`step-05`](/xv6/tutorial/step-05/) | `step-04` | `kbd.cpp` : 키보드 입력 (폴링) |
| [`step-06`](/xv6/tutorial/step-06/) | `step-05` | `pci.cpp`, `earlytrap.cpp` : PCI 버스, CPU 예외 화면 |
| [`step-07`](/xv6/tutorial/step-07/) | `step-06` | `xhci.cpp` : USB 컨트롤러 시작 |
| [`step-08`](/xv6/tutorial/step-08/) | `step-07` | `usb.cpp` : USB 장치 알아보기 |
| [`step-09`](/xv6/tutorial/step-09/) | `step-08` | USB 키보드로 입력 |
| [`step-10`](/xv6/tutorial/step-10/) | `step-09` | USB 허브. 실제 PC 에서 확인한 코드 |

## 읽는 법

<div class="tip" markdown="1">
**한 태그를 공부할 때** (예 : `step-03`)

```sh
cd ~/Ryu/xv6-x86_64
git fetch --tags
git diff --stat step-02 step-03        # 바뀐 파일 목록 (페이지의 "바꾼 것" 표와 같다)
git diff step-02 step-03 -- kernel     # 바뀐 줄 전부
git checkout step-03                   # 그 태그의 코드로 (읽기 전용으로 보기)
make clean && make qemu                # 그 상태 그대로 부팅
git checkout cpp                       # 돌아오기
```

두 태그를 나란히 열어 두고 싶으면 : `git worktree add ../xv6-step03 step-03`
</div>

- 페이지의 코드 조각 위 링크 (예 : [`kernel/main.cpp:12–30`]) 는 **그 태그의 그 줄** 로 간다. 체크아웃한 코드의 줄 번호와 같다
- 문서는 이 블로그에만 둔다. (예전 태그 `step-01` … `step-10` 안에는 그때 쓴 영어 튜토리얼 `docs/tutorial/stepNN.md` 와 변환 기록 `docs/cpp-conversion.md` 가 남아 있다 : `git show step-06:docs/tutorial/step06.md`)
- 일정은 [진행 현황](/xv6/plan/), 최종 목표는 [목표](/xv6/goal/)
