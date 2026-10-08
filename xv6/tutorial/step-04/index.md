---
layout: default
title: "step-04 : 화면에 글자"
permalink: /xv6/tutorial/step-04/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-04` : 화면에 글자

| | |
|---|---|
| **앞 태그** | `step-03` |
| **이 태그** | `step-04` (커밋 `918bf02`) |
| **한 줄** | C 판의 화면 콘솔 `fbcons.c` 와 글꼴 `font.h` 를 옮겼다. `printk()` 가 시리얼과 **화면** 둘 다에 나온다. 남색 화면과 손그림 글자는 사라졌다 |
| **비교할 C 코드** | `git show v0.2-x86_64-c:kernel/fbcons.c` ([v0.2 튜토리얼](/xv6/tutorial/v0.2-x86_64-c/) 2.1 에 그림) |

```sh
git diff --stat step-03 step-04 -- . ':!docs' ':!*.pdf'
git diff v0.2-x86_64-c:kernel/fbcons.c step-04:kernel/fbcons.cpp    # C 판과 C++ 판의 차이
git checkout step-04 && make clean && make vbox
```

## 1. 이전 상태 (`step-03`)

`printk()` 는 시리얼로만 나갔다. 화면에는 `main.cpp` 가 칠한 남색 바탕과 손으로 그린 8×8 글자 "xv6" 만 있었다. 시리얼 포트가 없는 실제 PC 에서는 부팅 메시지를 볼 수 없었다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 1 | 0 |
| `kernel/console.cpp` | 바뀜 | 6 | 0 |
| `kernel/defs.h` | 바뀜 | 4 | 0 |
| `kernel/fbcons.cpp` | 새 파일 | 153 | 0 |
| `kernel/font.h` | 새 파일 | 547 | 0 |
| `kernel/main.cpp` | 바뀜 | 4 | 46 |
| **합계** (6 파일) | | **715** | **46** |

`font.h` 는 C 판 그대로 (Spleen 글꼴의 비트맵, 547줄). `main.cpp` 에서는 `paintscreen()`, `drawglyph()`, 손그림 글자가 모두 빠졌다 (-50줄).

### 2.1 `fbcons.cpp` : 하는 일은 C 판과 같고, 모양이 C++

글자 그리기, 커서, 스크롤의 원리는 [v0.2 튜토리얼](/xv6/tutorial/v0.2-x86_64-c/) 2.1 의 그림 그대로다. 바뀐 것은 코드의 짜임새 :

<svg viewBox="0 0 1000 300" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="fbcons 구조"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">fbcons : C 의 &#x27;전역 구조체 + 함수&#x27; → C++ 의 &#x27;구조체 + 멤버 함수&#x27;</text><rect x="20" y="55" width="440" height="200" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="240.0" y="111.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C 판 (fbcons.c)</text><text x="240.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">static struct { fb, stride, cols, rows,</text><text x="240.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">  cx, cy, charw, charh; lock } cons;</text><text x="240.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace"></text><text x="240.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">static void fillrect(...)  { cons.fb ... }</text><text x="240.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">static void drawchar(...)  { cons.fb ... }</text><text x="240.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">static void cursor(...), scroll(...)</text><line x1="460" y1="155" x2="528" y2="155" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="530" y="55" width="450" height="200" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="95.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ 판 (fbcons.cpp)</text><text x="755.0" y="111.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">namespace {</text><text x="755.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">struct FbCons {</text><text x="755.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">  uint *fb; int stride; ...</text><text x="755.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">  void fillrect(...) { fb ... }</text><text x="755.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">  void drawchar(...), cursor(...), scroll()</text><text x="755.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">};</text><text x="755.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">FbCons cons;</text><text x="755.0" y="223.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">}</text><text x="500.0" y="285.0" font-size="11.5" fill="#4d5656" text-anchor="middle">익명 namespace = C 의 static : 이 파일 밖에서는 안 보인다. 잠금 (cons.lock) 은 spinlock.cpp 와 함께 돌아온다</text></svg>

[`kernel/fbcons.cpp:33–44`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L33-L44) (태그 `step-04`)

```cpp
namespace {

// the C version keeps the same fields in a static struct and has
// free functions fillrect(), drawchar(), cursor(), scroll() that
// use it; here they are its member functions.
// (the C version's cons.lock comes back with spinlock.cpp.)
struct FbCons {
  uint *fb;         // frame buffer, 32 bits per pixel
  int stride;       // pixels per scan line
  int cols, rows;   // screen size in characters
  int cx, cy;       // cursor position, in characters
  int charw, charh; // character cell size in pixels: the font size
```

멤버 함수 안에서는 `cons.fb` 대신 그냥 `fb`. 스크롤 :

[`kernel/fbcons.cpp:82–92`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L82-L92) (태그 `step-04`)

```cpp
  // move every line up by one, and clear the bottom line.
  void
  scroll()
  {
    auto dst = reinterpret_cast<uint64 *>(fb);
    auto src = reinterpret_cast<uint64 *>(fb + charh * stride);
    uint64 n = (uint64)(rows - 1) * charh * stride / 2;
    for (uint64 i = 0; i < n; i++)
      dst[i] = src[i];
    fillrect(0, (rows - 1) * charh, cols * charw, charh, BG);
  }
```

C 판의 `#define BIGSCREEN 2560`, `FG`, `BG` 는 `constexpr` 이 되었다. 각 플랫폼에서 어느 글꼴이 쓰이는지 주석 `[platform: ...]` 으로 적었다 :

[`kernel/fbcons.cpp:24–31`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L24-L31) (태그 `step-04`)

```cpp
// the big font on screens at least this wide.
// [platform: VirtualBox] vbox.sh sets 2560x1440, so VirtualBox gets
// the 32x64 font; QEMU's 1280x800 gets 16x32. [platform: real PC]
// depends on the monitor: 4K screens get the big font.
constexpr uint64 BIGSCREEN = 2560;

constexpr uint FG = 0x00D0D0D0; // light gray; the same in RGB and BGR pixel formats
constexpr uint BG = 0x00000000;
```

### 2.2 `console.cpp` : 화면에도 보내기

`consputc()` 가 시리얼보다 **화면에 먼저** 보낸다 (시리얼 소켓이 막혀 있어도 화면은 보이게). `consoleinit()` 이 `fbconsinit()` 도 부른다 :

[`kernel/console.cpp:26–41`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/console.cpp#L26-L41) (태그 `step-04`)

```cpp
consputc(int c)
{
  if (c == BACKSPACE) {
    // if the user typed backspace, overwrite with a space.
    // the screen first: a serial line may be slow, or blocked.
    fbconsputc('\b');
    fbconsputc(' ');
    fbconsputc('\b');
    uartputc_sync('\b');
    uartputc_sync(' ');
    uartputc_sync('\b');
  } else {
    fbconsputc(c);
    uartputc_sync(c);
  }
}
```

## 3. 바뀐 뒤

QEMU (1280 × 800, 16×32 글꼴) :

![step-04 QEMU 화면](/assets/image/xv6-tut-step-04-step04-qemu.png)

VirtualBox (2560 × 1440, 32×64 글꼴) :

![step-04 VirtualBox 화면](/assets/image/xv6-tut-step-04-step04-vbox.png)

- 시리얼 출력은 `step-03` 과 같다. 같은 글이 이제 화면에도
- **실제 PC 에서도 부팅 메시지가 보인다.** 2026.10.7 베어본의 첫 사진 ([step-06](/xv6/tutorial/step-06/)) 이 이 화면 콘솔이다

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `fbcons.cpp` 의 `FbCons` 멤버 함수 4개가 C 판의 어느 `static` 함수였는지 짝짓기
- `namespace {` 를 지우면 무엇이 달라지나 : `nm kernel/kernel | grep cons` 로 심볼 이름 비교
- `BIGSCREEN` 을 1024 로 바꾸고 QEMU 를 창으로 띄우기 : 큰 글꼴. 창 명령 : `qemu-system-x86_64 -machine q35 -m 512M -serial stdio -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd -drive if=pflash,format=raw,file=ovmf_vars.fd -drive format=raw,file=usb.img`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-03/">step-03</a></span><span><a href="/xv6/tutorial/step-05/">step-05</a> →</span></div>
