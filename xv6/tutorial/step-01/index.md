---
layout: default
title: "step-01 : C++ 판의 출발, 부팅 뼈대"
permalink: /xv6/tutorial/step-01/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-01` : C++ 판의 출발, 부팅 뼈대

| | |
|---|---|
| **앞 태그** | `v0.2-x86_64-c` (완성된 C 판) |
| **이 태그** | `step-01` (커밋 `ddd9638`), 브랜치 `cpp` |
| **한 줄** | C 판의 커널을 **거의 다 지우고**, 부팅에 필요한 것만 남긴 뒤 `start.cpp`, `main.cpp` 두 파일을 C++ 로 새로 썼다 |
| **계획** | [진행 현황](/xv6/plan/) 의 Step 1 (2026.11.7) |

```sh
git diff --stat v0.2-x86_64-c step-01 -- . ':!docs' ':!*.pdf'
git checkout step-01 && make clean && make qemu
```

## 1. 이전 상태 : 완성된 C 판 (`v0.2`)

셸이 뜨고 `usertests` 가 통과하는 C 커널 (커널 45 파일, 사용자 프로그램 26 파일). 화면 콘솔과 PS/2 키보드까지 ([`v0.2-x86_64-c`](/xv6/tutorial/v0.2-x86_64-c/)).

C 판을 고쳐 가며 C++ 로 바꾸는 대신 **처음부터 다시 쌓기** 로 했다. 한 조각씩 C++ 로 되살리면서 그 조각을 C 판, 그리고 xv6 책과 나란히 읽기 위해서다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `.gitignore` | 바뀜 | 1 | 0 |
| `Makefile` | 바뀜 | 64 | 125 |
| `README` | 바뀜 | 48 | 26 |
| `boot/efi.h` | 바뀜 | 2 | 1 |
| `boot/loader.c` | 바뀜 | 92 | 4 |
| `kernel/acpi.c` | 지움 | 0 | 151 |
| `kernel/bio.c` | 지움 | 0 | 153 |
| `kernel/buf.h` | 지움 | 0 | 11 |
| `kernel/console.c` | 지움 | 0 | 213 |
| `kernel/defs.h` | 지움 | 0 | 203 |
| `kernel/elf.h` | 지움 | 0 | 42 |
| `kernel/entry.S` | 바뀜 | 3 | 3 |
| `kernel/entryother.S` | 지움 | 0 | 117 |
| `kernel/exec.c` | 지움 | 0 | 187 |
| `kernel/fbcons.c` | 지움 | 0 | 151 |
| `kernel/fcntl.h` | 지움 | 0 | 5 |
| `kernel/file.c` | 지움 | 0 | 179 |
| `kernel/file.h` | 지움 | 0 | 40 |
| `kernel/font.h` | 지움 | 0 | 547 |
| `kernel/fs.c` | 지움 | 0 | 741 |
| `kernel/fs.h` | 지움 | 0 | 61 |
| `kernel/ioapic.c` | 지움 | 0 | 80 |
| `kernel/kalloc.c` | 지움 | 0 | 102 |
| `kernel/kbd.c` | 지움 | 0 | 112 |
| `kernel/kbd.h` | 지움 | 0 | 112 |
| `kernel/kernel.ld` | 바뀜 | 9 | 4 |
| `kernel/kernelvec.S` | 지움 | 0 | 95 |
| `kernel/lapic.c` | 지움 | 0 | 147 |
| `kernel/log.c` | 지움 | 0 | 261 |
| `kernel/main.c` | 지움 | 0 | 105 |
| `kernel/main.cpp` | 새 파일 | 104 | 0 |
| `kernel/pipe.c` | 지움 | 0 | 143 |
| `kernel/printk.c` | 지움 | 0 | 152 |
| `kernel/proc.c` | 지움 | 0 | 719 |
| `kernel/proc.h` | 지움 | 0 | 107 |
| `kernel/ramdisk.c` | 지움 | 0 | 49 |
| `kernel/sleeplock.c` | 지움 | 0 | 55 |
| `kernel/sleeplock.h` | 지움 | 0 | 9 |
| `kernel/spinlock.c` | 지움 | 0 | 116 |
| `kernel/spinlock.h` | 지움 | 0 | 8 |
| `kernel/start.c` | 지움 | 0 | 50 |
| `kernel/start.cpp` | 새 파일 | 38 | 0 |
| `kernel/stat.h` | 지움 | 0 | 11 |
| `kernel/string.c` | 지움 | 0 | 106 |
| `kernel/swtch.S` | 지움 | 0 | 32 |
| `kernel/syscall.c` | 지움 | 0 | 153 |
| `kernel/syscall.h` | 지움 | 0 | 23 |
| `kernel/sysfile.c` | 지움 | 0 | 530 |
| `kernel/sysproc.c` | 지움 | 0 | 112 |
| `kernel/trampoline.S` | 지움 | 0 | 155 |
| `kernel/trap.c` | 지움 | 0 | 282 |
| `kernel/uart.c` | 지움 | 0 | 153 |
| `kernel/vm.c` | 지움 | 0 | 519 |
| `kernel/vm.h` | 지움 | 0 | 2 |
| `kernel/x86.h` | 바뀜 | 2 | 2 |
| `mkfs/mkfs.c` | 지움 | 0 | 307 |
| `test-xv6.py` | 지움 | 0 | 226 |
| `user/cat.c` | 지움 | 0 | 43 |
| `user/dorphan.c` | 지움 | 0 | 35 |
| `user/echo.c` | 지움 | 0 | 19 |
| `user/forktest.c` | 지움 | 0 | 56 |
| `user/forphan.c` | 지움 | 0 | 40 |
| `user/grep.c` | 지움 | 0 | 108 |
| `user/grind.c` | 지움 | 0 | 351 |
| `user/init.c` | 지움 | 0 | 54 |
| `user/kill.c` | 지움 | 0 | 17 |
| `user/ln.c` | 지움 | 0 | 15 |
| `user/logstress.c` | 지움 | 0 | 48 |
| `user/ls.c` | 지움 | 0 | 88 |
| `user/mkdir.c` | 지움 | 0 | 23 |
| `user/printf.c` | 지움 | 0 | 135 |
| `user/rm.c` | 지움 | 0 | 23 |
| `user/sh.c` | 지움 | 0 | 499 |
| `user/stressfs.c` | 지움 | 0 | 50 |
| `user/sync.c` | 지움 | 0 | 10 |
| `user/ulib.c` | 지움 | 0 | 162 |
| `user/umalloc.c` | 지움 | 0 | 90 |
| `user/user.h` | 지움 | 0 | 50 |
| `user/user.ld` | 지움 | 0 | 34 |
| `user/usertests.c` | 지움 | 0 | 3538 |
| `user/usys.pl` | 지움 | 0 | 48 |
| `user/wc.c` | 지움 | 0 | 55 |
| `user/zombie.c` | 지움 | 0 | 14 |
| `vbox.sh` | 바뀜 | 2 | 2 |
| **합계** (84 파일) | | **365** | **13606** |

<svg viewBox="0 0 1000 380" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="step-01 의 파일"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">step-01 의 kernel/ : 커널 파일 거의 전부를 지우고 부팅 뼈대만 남겼다</text><rect x="20" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">acpi.c</text><rect x="142" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">bio.c</text><rect x="264" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">buf.h</text><rect x="386" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">console.c</text><rect x="508" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">defs.h</text><rect x="630" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="689.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">elf.h</text><rect x="752" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="811.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">entryother.S</text><rect x="874" y="50" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="933.0" y="67.0" font-size="10.0" fill="#4d5656" text-anchor="middle">exec.c</text><rect x="20" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">fbcons.c</text><rect x="142" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">fcntl.h</text><rect x="264" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">file.c</text><rect x="386" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">file.h</text><rect x="508" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">font.h</text><rect x="630" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="689.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">fs.c</text><rect x="752" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="811.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">fs.h</text><rect x="874" y="80" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="933.0" y="97.0" font-size="10.0" fill="#4d5656" text-anchor="middle">ioapic.c</text><rect x="20" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kalloc.c</text><rect x="142" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kbd.c</text><rect x="264" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kbd.h</text><rect x="386" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kernelvec.S</text><rect x="508" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">lapic.c</text><rect x="630" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="689.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">log.c</text><rect x="752" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="811.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">main.c</text><rect x="874" y="110" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="933.0" y="127.0" font-size="10.0" fill="#4d5656" text-anchor="middle">pipe.c</text><rect x="20" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">printk.c</text><rect x="142" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">proc.c</text><rect x="264" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">proc.h</text><rect x="386" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">ramdisk.c</text><rect x="508" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">sleeplock.c</text><rect x="630" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="689.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">sleeplock.h</text><rect x="752" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="811.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">spinlock.c</text><rect x="874" y="140" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="933.0" y="157.0" font-size="10.0" fill="#4d5656" text-anchor="middle">spinlock.h</text><rect x="20" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">start.c</text><rect x="142" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">stat.h</text><rect x="264" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">string.c</text><rect x="386" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">swtch.S</text><rect x="508" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">syscall.c</text><rect x="630" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="689.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">syscall.h</text><rect x="752" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="811.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">sysfile.c</text><rect x="874" y="170" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="933.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">sysproc.c</text><rect x="20" y="200" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="79.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">trampoline.S</text><rect x="142" y="200" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="201.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">trap.c</text><rect x="264" y="200" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="323.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">uart.c</text><rect x="386" y="200" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="445.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">vm.c</text><rect x="508" y="200" width="118" height="26" rx="3" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="567.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">vm.h</text><text x="20.0" y="250.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">남김 (그대로 또는 조금 바뀜)</text><rect x="20" y="262" width="102" height="28" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="71.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">entry.S</text><rect x="128" y="262" width="102" height="28" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="179.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kernel.ld</text><rect x="236" y="262" width="102" height="28" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="287.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">x86.h</text><rect x="344" y="262" width="102" height="28" rx="3" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="395.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">bootinfo.h</text><rect x="452" y="262" width="102" height="28" rx="3" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="503.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">memlayout.h</text><rect x="560" y="262" width="102" height="28" rx="3" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="611.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">param.h</text><rect x="668" y="262" width="102" height="28" rx="3" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="719.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">types.h</text><rect x="776" y="262" width="102" height="28" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="827.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">boot/loader.c</text><rect x="884" y="262" width="102" height="28" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="935.0" y="280.0" font-size="10.0" fill="#4d5656" text-anchor="middle">boot/efi.h</text><text x="20.0" y="320.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">새로 (C++)</text><rect x="20" y="332" width="150" height="28" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="95.0" y="350.0" font-size="10.5" fill="#4d5656" text-anchor="middle">start.cpp</text><rect x="178" y="332" width="150" height="28" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="253.0" y="350.0" font-size="10.5" fill="#4d5656" text-anchor="middle">main.cpp</text><text x="345.0" y="351.0" font-size="11" fill="#4d5656" text-anchor="start">user/ 의 파일 26개, mkfs/mkfs.c 도 지웠다 (Part 6, 7 에서 돌아온다)</text><rect x="700" y="236" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="720.0" y="246.0" font-size="10.5" fill="#4d5656" text-anchor="start">새로 생김</text><rect x="795" y="236" width="14" height="12" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="815.0" y="246.0" font-size="10.5" fill="#4d5656" text-anchor="start">바뀜</text><rect x="851" y="236" width="14" height="12" rx="2" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="871.0" y="246.0" font-size="10.5" fill="#4d5656" text-anchor="start">지움</text></svg>

### 2.1 남긴 것과 그 이유

| 파일 | 왜 남겼나 |
|---|---|
| `boot/loader.c`, `boot/efi.h` | UEFI 로더. C 로 남는다 (clang 으로 만드는 별도 프로그램. 커널이 아니다) |
| `kernel/entry.S` | 커널의 첫 명령. 어셈블리는 그대로 둔다는 원칙 |
| `kernel/kernel.ld` | 링커 스크립트 |
| `bootinfo.h`, `memlayout.h`, `param.h`, `types.h`, `x86.h` | 상수와 작은 inline 함수. 다음 단계들이 그대로 쓴다 |

### 2.2 `start.cpp` : C 판의 `start.c` 를 C++ 로

[`kernel/start.cpp:5–10`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-01/kernel/start.cpp#L5-L10) (태그 `step-01`)

```cpp
void main();

// entry.S needs one stack per CPU.
extern "C" {
__attribute__((aligned(16))) char stack0[4096 * NCPU];
}
```

C 판과 다른 점 :

- `extern "C"` : `entry.S` 는 어셈블리라서 C++ 의 **이름 맹글링** 된 이름 (`_Z5startP8bootinfo`) 을 모른다. `start` 와 `stack0` 을 C 이름 그대로 내보낸다
- **전역 생성자 실행** : C++ 의 전역 객체는 `main()` 전에 생성자가 돌아야 한다. 보통은 C 런타임이 하는 일인데 커널에는 없다

<svg viewBox="0 0 1000 270" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="전역 생성자 실행"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ 전역 객체의 생성자 : 런타임이 없으니 start() 가 직접 부른다</text><rect x="20" y="60" width="260" height="100" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="150.0" y="90.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">컴파일러 (g++)</text><text x="150.0" y="106.0" font-size="11.0" fill="#4d5656" text-anchor="middle">전역 객체마다</text><text x="150.0" y="122.0" font-size="11.0" fill="#4d5656" text-anchor="middle">생성자를 부르는 함수를 만들고</text><text x="150.0" y="138.0" font-size="11.0" fill="#4d5656" text-anchor="middle">그 주소를 .init_array 에</text><rect x="330" y="60" width="300" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="480.0" y="90.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">kernel.ld (링커 스크립트)</text><text x="480.0" y="106.0" font-size="11.0" fill="#4d5656" text-anchor="middle">.init_array 를 모아</text><text x="480.0" y="122.0" font-size="11.0" fill="#4d5656" text-anchor="middle">__init_array_start</text><text x="480.0" y="138.0" font-size="11.0" fill="#4d5656" text-anchor="middle">__init_array_end 를 정의</text><rect x="680" y="60" width="300" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="830.0" y="90.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.cpp : start()</text><text x="830.0" y="106.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">for (ctor = start; ctor != end; ctor++)</text><text x="830.0" y="122.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">  (*ctor)();</text><text x="830.0" y="138.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">main();</text><line x1="280" y1="110" x2="328" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="630" y1="110" x2="678" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="185" width="960" height="65" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="205.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">보통의 C++ 프로그램에서는</text><text x="500.0" y="221.5" font-size="10.5" fill="#4d5656" text-anchor="middle">C 런타임 (crt0, __libc_start_main) 이 main() 전에 이 일을 한다. 커널에는 그런 것이 없다.</text><text x="500.0" y="237.5" font-size="10.5" fill="#4d5656" text-anchor="middle">kernel.ld 에서 trampoline 구역 (trampsec) 은 지웠다 : trampoline.S 가 돌아오는 Step 23 에서 다시</text></svg>

- C 판 `start()` 의 `EFER.NXE` 켜기, GS base 설정은 아직 없다 (페이지 테이블, CPU 여러 개와 함께 돌아온다)

### 2.3 `main.cpp` : 커널이 살아 있다는 것만 보여 주기

콘솔 코드 (`uart.c`, `printk.c`, `console.c`, `fbcons.c`) 를 모두 지웠으므로, `main.cpp` 가 직접 시리얼 포트에 쓰고 화면을 칠한다 :

[`kernel/main.cpp:87–104`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-01/kernel/main.cpp#L87-L104) (태그 `step-01`)

```cpp
main()
{
  earlyuartinit();
  earlyputs("\nxv6 kernel is booting (C++ skeleton)\n");
  paintscreen(0x00203060); // dark blue

  // "xv6" in white (the same in RGB and BGR pixel formats),
  // each letter 8 * scale pixels wide.
  uint64 scale = bootinfo.fb_width / 80;
  const uchar *word[] = { glyph_x, glyph_v, glyph_6 };
  for (int i = 0; i < 3; i++)
    drawglyph(word[i], scale * 8 * (1 + i), scale * 8, scale, 0x00FFFFFF);

  earlyputs("nothing else yet; halting\n");

  for (;;)
    asm volatile("hlt");
}
```

<svg viewBox="0 0 1000 250" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="step-01 의 실행 흐름"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">step-01 에서 도는 것 : 로더 → entry.S → start() → main() → hlt</text><rect x="15" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="105.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">boot/loader.c</text><text x="105.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kernel, fs.img 읽기</text><text x="105.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">bootinfo 채우기</text><rect x="213" y="60" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="303.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">entry.S</text><text x="303.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">스택 잡기</text><text x="303.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">call start</text><line x1="195" y1="100" x2="212" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="411" y="60" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="501.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.cpp</text><text x="501.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">bootinfo 복사</text><text x="501.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">전역 생성자 실행</text><line x1="393" y1="100" x2="410" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="609" y="60" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="699.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">main.cpp</text><text x="699.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">COM1 에 두 줄</text><text x="699.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">화면 칠하기, &quot;xv6&quot;</text><line x1="591" y1="100" x2="608" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="807" y="60" width="180" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="897.0" y="96.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">for (;;) hlt</text><text x="897.0" y="112.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPU 쉼</text><line x1="789" y1="100" x2="806" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="165" width="970" height="65" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="193.5" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">C 판의 main() 이 하던 일 (kinit, kvminit, trapinit, …, scheduler) 은 아무것도 없다</text><text x="500.0" y="209.5" font-size="11.0" fill="#4d5656" text-anchor="middle">다음 단계들이 그것을 한 조각씩 C++ 로 되살린다. 그 사이에도 언제나 부팅되는 상태를 유지한다</text></svg>

C++ 다운 점 몇 가지 :

| C 라면 | 여기서는 |
|---|---|
| `#define LSR 5` | `constexpr int LSR = 5;` (타입이 있고, 디버거에 보인다) |
| `(uint *)bootinfo.fb_base` | `reinterpret_cast<uint *>(bootinfo.fb_base)` (위험한 변환이 눈에 띈다) |
| `uint *fb = ...` | `auto fb = ...` |

손으로 그린 8×8 글자 `x`, `v`, `6` 은 [step-04](/xv6/tutorial/step-04/) 의 진짜 글꼴이 대신한다.

### 2.4 `Makefile` : C++ 로 빌드

[`Makefile:38–44`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-01/Makefile#L38-L44) (태그 `step-01`)

```
# freestanding C++20: no exceptions, RTTI, or standard library,
# and nothing that needs a C++ runtime (thread-safe statics,
# atexit-registered destructors).
CXXFLAGS = $(COMMONFLAGS) -std=c++20
CXXFLAGS += -fno-exceptions -fno-rtti
CXXFLAGS += -fno-threadsafe-statics -fno-use-cxa-atexit
CXXFLAGS += -Wno-main
```

| 옵션 | 이유 |
|---|---|
| `-fno-exceptions` | `throw` 는 스택을 되감는 런타임이 필요하다 |
| `-fno-rtti` | `dynamic_cast`, `typeid` 도 런타임이 필요하다 |
| `-fno-threadsafe-statics` | 함수 안의 `static` 객체를 초기화할 때 `__cxa_guard_*` 를 부르지 않게 |
| `-fno-use-cxa-atexit` | 전역 객체의 소멸자를 `__cxa_atexit` 에 등록하지 않게 (커널은 끝나지 않는다) |

`kernel.ld` 에서는 `trampoline.S` 를 위한 구역 (`trampsec`) 을 지우고 `.init_array` 를 더했다 (위 그림).

### 2.5 실제 PC 를 위한 것 (`boot/loader.c`, `Makefile`)

이 태그에는 실제 PC 에서 부팅하기 위한 변경도 들어 있다 :

| 변경 | 이유 |
|---|---|
| 커널 페이지를 `EfiLoaderCode` 로 할당 | 요즘 펌웨어는 data 페이지를 실행 금지로 매핑할 수 있다. 커널은 한동안 펌웨어의 페이지 테이블로 돈다 |
| 640KB 아래 페이지가 없어도 계속 | 다른 CPU 를 깨울 때만 필요하다. 실제 PC 에는 없을 수 있다 |
| 커널 자리가 차 있으면 그 근처 메모리 맵 출력 | 실제 PC 에서 실패하면 사진으로 원인을 보려고 |
| 로더가 화면 크기, 픽셀 형식을 출력 + 3초 대기 | 같은 이유 |
| `usb.img` (GPT 디스크 이미지) | 실제 PC 는 파티션 표 없는 FAT 이미지 (`esp.img`) 로는 부팅하지 않는다 |

<svg viewBox="0 0 1000 230" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="usb.img 의 모양"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">usb.img : 실제 PC 가 부팅할 수 있는 디스크 모양 (GPT + EFI System Partition)</text><rect x="20" y="60" width="140" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="90.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">GPT</text><text x="90.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">보호 MBR,</text><text x="90.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">파티션 표</text><rect x="160" y="60" width="560" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="440.0" y="96.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">파티션 1 : EFI System (FAT32, 64MB) = esp.img</text><text x="440.0" y="112.0" font-size="11.0" fill="#4d5656" text-anchor="middle">EFI/BOOT/BOOTX64.EFI (로더)   /kernel   /fs.img</text><rect x="720" y="60" width="120" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="780.0" y="104.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">GPT 백업</text><text x="20.0" y="165.0" font-size="10.5" fill="#566573" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="160.0" y="165.0" font-size="10.5" fill="#566573" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">1MB</text><text x="720.0" y="165.0" font-size="10.5" fill="#566573" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">65MB</text><text x="840.0" y="165.0" font-size="10.5" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">66MB</text><rect x="870" y="55" width="115" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="927.5" y="80.0" font-size="10.0" fill="#4d5656" text-anchor="middle">QEMU,</text><text x="927.5" y="96.0" font-size="10.0" fill="#4d5656" text-anchor="middle">VirtualBox,</text><text x="927.5" y="112.0" font-size="10.0" fill="#4d5656" text-anchor="middle">실제 PC 모두</text><text x="927.5" y="128.0" font-size="10.0" fill="#4d5656" text-anchor="middle">이 이미지로</text><text x="500.0" y="205.0" font-size="11" fill="#4d5656" text-anchor="middle">Makefile : sgdisk 로 표를 만들고, esp.img 를 1MB 위치에 dd. USB 메모리에 쓰기 : sudo dd if=usb.img of=/dev/sdX</text></svg>

## 3. 바뀐 뒤

QEMU (`make qemu`) 의 시리얼 :

```
xv6 kernel is booting (C++ skeleton)
nothing else yet; halting
```

화면은 남색으로 칠해지고 흰 글자 "xv6" :

![step-01 QEMU 화면](/assets/image/xv6-tut-step-01-step01-qemu.png)

VirtualBox (2560 × 1440) :

![step-01 VirtualBox 화면](/assets/image/xv6-tut-step-01-step01-vbox.png)

로더 화면 (3초 동안 보인다. 실제 PC 에서 사진 찍을 시간) :

![step-01 로더 화면](/assets/image/xv6-tut-step-01-step01-loader-qemu.png)

- 셸도, 키보드도, `printk()` 도 없다. 그래도 **세 곳 모두에서 부팅한다**
- 다음 단계부터 C 판의 조각이 하나씩 돌아온다. 첫 조각은 시리얼 드라이버

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `nm kernel/kernel | grep -i " start$\| stack0$"` : `extern "C"` 덕분에 맹글링 안 된 이름. `extern "C"` 를 지우고 빌드하면 링커가 `start` 를 못 찾는다
- `objdump -h kernel/kernel` 에 `.init_array` 구역이 있는지 (지금은 전역 객체가 없어서 크기 0)
- `git show v0.2-x86_64-c:kernel/start.c` 와 `kernel/start.cpp` 를 나란히
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/v0.2-x86_64-c/">v0.2-x86_64-c</a></span><span><a href="/xv6/tutorial/step-02/">step-02</a> →</span></div>
