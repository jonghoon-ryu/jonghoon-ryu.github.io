---
layout: default
title: v0.1-x86_64-c
permalink: /xv6/tutorial/v0.1-x86_64-c/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# v0.1-x86_64-c

<p class="subtitle">xv6-riscv 를 x86-64 PC 로</p>

| | |
|---|---|
| **앞 태그** | MIT xv6-riscv 커밋 `06aad25` (저장소의 `upstream` 리모트) |
| **이 태그** | `v0.1-x86_64-c` (`daa09f5`, 2026.9.27), 브랜치 `main` |
| **한 줄** | 언어는 C 그대로, 기계를 RISC-V (QEMU `virt`) 에서 64비트 x86 PC (UEFI) 로 바꿨다 |
| **확인** | QEMU + OVMF (CPU 1개, 4개), VirtualBox (EFI) 에서 셸이 뜨고 `usertests` 전체 통과 |

```sh
cd ~/Ryu/xv6-x86_64
git diff --stat 06aad25 v0.1-x86_64-c -- . ':!docs'
git checkout v0.1-x86_64-c && make clean && make qemu CPUS=2   # 셸이 뜬다. 끝내기 : Ctrl-a x
```

## 1. 이전 상태 : xv6-riscv

MIT 의 원본. **QEMU 의 가상 기계 `virt` 위에서만** 돈다 (이유는 [목표](/xv6/goal/) 의 "출발점").

- QEMU 가 `-kernel` 옵션으로 커널 파일을 `0x80000000` 에 직접 올리고 모든 CPU (hart) 를 함께 출발시킨다
- 장치는 모두 정해진 주소 : UART `0x10000000`, virtio 디스크 `0x10001000`, PLIC `0x0c000000`
- 트랩은 `stvec` 레지스터 하나, 시스템 콜은 `ecall`, 페이지 테이블은 3단계 (Sv39), CPU 번호는 `tp` 레지스터

이 기계 의존 부분이 거의 모두 `kernel/riscv.h` (417줄), `trampoline.S`, `trap.c`, `start.c`, `plic.c`, `virtio_disk.c` 에 모여 있다.
**프로세스, 파일 시스템, 시스템 콜의 내용은 기계와 상관없어서 거의 그대로 둘 수 있었다.**

## 2. 바꾼 것

<!-- fig:map_v0_1_x86_64_c -->
<svg viewBox="0 0 1000 704" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="06aad25 에서 v0.1-x86_64-c 로 바뀐 파일"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">변경 지도 : 06aad25 → v0.1-x86_64-c  (파일마다 더한 줄 / 지운 줄, 막대 길이는 √줄 수)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">지운 줄 ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">파일</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ 더한 줄</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">boot/loader.c</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="64" width="200.75804333491618" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="820.8" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+299</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/x86.h</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="86" width="191.75660307921757" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="811.8" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+272</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">boot/efi.h</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="108" width="161.251787448632" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="781.3" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+190</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/acpi.c</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="130" width="144.40388539201751" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="764.4" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+151</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/lapic.c</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="152" width="142.5584176784753" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="762.6" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+147</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/entryother.S</text><text x="570.0" y="185.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="174" width="127.82957786664727" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="747.8" y="185.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+117</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/ioapic.c</text><text x="570.0" y="207.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="196" width="106.74066237203265" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="726.7" y="207.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+80</text><rect x="305" y="217" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="229.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/ramdisk.c</text><text x="570.0" y="229.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="218" width="84.84203920677707" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="704.8" y="229.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+49</text><rect x="305" y="239" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="251.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/bootinfo.h</text><text x="570.0" y="251.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="240" width="68.71055659833439" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="688.7" y="251.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+31</text><rect x="305" y="261" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="273.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">vbox.sh</text><text x="570.0" y="273.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="262" width="64.52503614791799" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="684.5" y="273.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+27</text><rect x="305" y="283" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="295.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/trampoline.S</text><text x="570.0" y="295.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="166.65089065973993" y="284" width="128.34910934026007" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="161.7" y="295.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−118</text><rect x="615" y="284" width="129.3816095807386" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="749.4" y="295.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+120</text><rect x="305" y="305" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="317.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/trap.c</text><text x="570.0" y="317.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="182.7436699586283" y="306" width="112.2563300413717" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="177.7" y="317.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−89</text><rect x="615" y="306" width="142.5584176784753" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="762.6" y="317.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+147</text><rect x="305" y="327" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="339.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kernelvec.S</text><text x="570.0" y="339.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="210.96661846944266" y="328" width="84.03338153055732" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="206.0" y="339.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−48</text><rect x="615" y="328" width="106.10905324677897" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="726.1" y="339.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+79</text><rect x="305" y="349" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="361.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="361.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="200.31388035466992" y="350" width="94.68611964533008" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="195.3" y="361.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−62</text><rect x="615" y="350" width="94.68611964533008" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="714.7" y="361.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+62</text><rect x="305" y="371" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="383.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.h</text><text x="570.0" y="383.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="206.2331001412387" y="372" width="88.76689985876128" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="201.2" y="383.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−54</text><rect x="615" y="372" width="91.03490607861316" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="711.0" y="383.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+57</text><rect x="305" y="393" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="405.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/start.c</text><text x="570.0" y="405.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="212.60961050816258" y="394" width="82.39038949183744" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="207.6" y="405.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−46</text><rect x="615" y="394" width="67.6908047903693" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="687.7" y="405.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+30</text><rect x="305" y="415" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="427.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/vm.c</text><text x="570.0" y="427.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="232.68425770944495" y="416" width="62.31574229055506" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="227.7" y="427.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−25</text><rect x="615" y="416" width="79.85740360414981" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="699.9" y="427.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+43</text><rect x="305" y="437" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="449.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.c</text><text x="570.0" y="449.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="261.4110333804129" y="438" width="33.58896661958709" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="256.4" y="449.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−6</text><rect x="615" y="438" width="93.96800159465006" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="714.0" y="449.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="459" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="471.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/memlayout.h</text><text x="570.0" y="471.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="220.48894258581618" y="460" width="74.51105741418382" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="215.5" y="471.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−37</text><rect x="615" y="460" width="67.6908047903693" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="687.7" y="471.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+30</text><rect x="305" y="481" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="493.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/swtch.S</text><text x="570.0" y="493.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="225.28601078207117" y="482" width="69.71398921792883" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="220.3" y="493.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−32</text><rect x="615" y="482" width="58.82884903315484" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="678.8" y="493.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+22</text><rect x="305" y="503" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="515.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.c</text><text x="570.0" y="515.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="251.6443626063758" y="504" width="43.35563739362418" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="246.6" y="515.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−11</text><rect x="615" y="504" width="64.52503614791799" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="684.5" y="515.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+27</text><rect x="305" y="525" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="537.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">README</text><text x="570.0" y="537.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="526" width="70.7018619148769" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="690.7" y="537.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+33</text><rect x="305" y="547" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="559.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="559.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="253.38279724775563" y="548" width="41.617202752244374" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="248.4" y="559.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−10</text><rect x="615" y="548" width="55.09492591500185" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="675.1" y="559.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+19</text><rect x="305" y="569" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="581.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/exec.c</text><text x="570.0" y="581.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="255.210554625667" y="570" width="39.78944537433303" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="250.2" y="581.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−9</text><rect x="615" y="570" width="56.37033118601632" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="676.4" y="581.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+20</text><rect x="305" y="591" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="603.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kalloc.c</text><text x="570.0" y="603.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="273.0715026955178" y="592" width="21.928497304482207" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="268.1" y="603.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−2</text><rect x="615" y="592" width="58.82884903315484" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="678.8" y="603.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+22</text><rect x="305" y="613" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="625.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/syscall.c</text><text x="570.0" y="625.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="251.6443626063758" y="614" width="43.35563739362418" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="246.6" y="625.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−11</text><rect x="615" y="614" width="46.60985928888242" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="666.6" y="625.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+13</text><text x="320.0" y="647.0" font-size="11" fill="#566573" text-anchor="start">… 그 밖에 25 파일 (바뀜 21, 지움 4) : +71 −955</text><text x="500.0" y="680.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">합계 51 파일, +2219 −1515 줄 (docs, PDF 제외)</text></svg>
<!-- /fig:map_v0_1_x86_64_c -->

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `.gitignore` | 바뀜 | 6 | 0 |
| `LICENSE` | 바뀜 | 13 | 0 |
| `Makefile` | 바뀜 | 62 | 62 |
| `README` | 바뀜 | 33 | 0 |
| `boot/efi.h` | 새 파일 | 190 | 0 |
| `boot/loader.c` | 새 파일 | 299 | 0 |
| `kernel/acpi.c` | 새 파일 | 151 | 0 |
| `kernel/bio.c` | 바뀜 | 3 | 3 |
| `kernel/bootinfo.h` | 새 파일 | 31 | 0 |
| `kernel/console.c` | 바뀜 | 1 | 1 |
| `kernel/defs.h` | 바뀜 | 19 | 10 |
| `kernel/entry.S` | 바뀜 | 10 | 13 |
| `kernel/entryother.S` | 새 파일 | 117 | 0 |
| `kernel/exec.c` | 바뀜 | 20 | 9 |
| `kernel/file.c` | 바뀜 | 1 | 1 |
| `kernel/fs.c` | 바뀜 | 1 | 1 |
| `kernel/ioapic.c` | 새 파일 | 80 | 0 |
| `kernel/kalloc.c` | 바뀜 | 22 | 2 |
| `kernel/kernel.ld` | 바뀜 | 11 | 11 |
| `kernel/kernelvec.S` | 바뀜 | 79 | 48 |
| `kernel/lapic.c` | 새 파일 | 147 | 0 |
| `kernel/log.c` | 바뀜 | 1 | 1 |
| `kernel/main.c` | 바뀜 | 61 | 6 |
| `kernel/memlayout.h` | 바뀜 | 30 | 37 |
| `kernel/pipe.c` | 바뀜 | 1 | 1 |
| `kernel/plic.c` | 지움 | 0 | 47 |
| `kernel/printk.c` | 바뀜 | 1 | 1 |
| `kernel/proc.c` | 바뀜 | 27 | 11 |
| `kernel/proc.h` | 바뀜 | 57 | 54 |
| `kernel/ramdisk.c` | 새 파일 | 49 | 0 |
| `kernel/riscv.h` | 지움 | 0 | 417 |
| `kernel/sleeplock.c` | 바뀜 | 1 | 1 |
| `kernel/spinlock.c` | 바뀜 | 3 | 3 |
| `kernel/start.c` | 바뀜 | 30 | 46 |
| `kernel/swtch.S` | 바뀜 | 22 | 32 |
| `kernel/syscall.c` | 바뀜 | 13 | 11 |
| `kernel/sysfile.c` | 바뀜 | 1 | 1 |
| `kernel/sysproc.c` | 바뀜 | 1 | 1 |
| `kernel/trampoline.S` | 바뀜 | 120 | 118 |
| `kernel/trap.c` | 바뀜 | 147 | 89 |
| `kernel/uart.c` | 바뀜 | 6 | 8 |
| `kernel/virtio.h` | 지움 | 0 | 99 |
| `kernel/virtio_disk.c` | 지움 | 0 | 333 |
| `kernel/vm.c` | 바뀜 | 43 | 25 |
| `kernel/x86.h` | 새 파일 | 272 | 0 |
| `user/grind.c` | 바뀜 | 1 | 1 |
| `user/ulib.c` | 바뀜 | 1 | 1 |
| `user/user.ld` | 바뀜 | 2 | 7 |
| `user/usertests.c` | 바뀜 | 1 | 1 |
| `user/usys.pl` | 바뀜 | 5 | 2 |
| `vbox.sh` | 새 파일 | 27 | 0 |
| **합계** (51 파일) | | **2219** | **1515** |

51 개 파일 중 `fs.c`, `file.c`, `pipe.c`, `log.c`, `sysfile.c` 같은 파일은 `#include "riscv.h"` 를 `"x86.h"` 로 바꾼 한 줄뿐이다.
진짜로 바뀐 것은 아래 일곱 가지다.

<!-- fig:regmap -->
<svg viewBox="0 0 1000 520" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="RISC-V 와 x86-64 레지스터 대응"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 일, 다른 장치 : riscv.h ↔ x86.h (xv6 가 쓰는 것만)</text><text x="160.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">하는 일</text><text x="450.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">RISC-V (riscv.h)</text><text x="790.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">x86-64 (x86.h)</text><rect x="20" y="62" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle">페이지 테이블 시작</text><rect x="310" y="62" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">satp  (w_satp)</text><line x1="592" y1="80" x2="618" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="62" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">CR3  (w_cr3)</text><rect x="20" y="102" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="124.0" font-size="11.0" fill="#4d5656" text-anchor="middle">트랩 처리 주소</text><rect x="310" y="102" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="124.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stvec  (w_stvec)</text><line x1="592" y1="120" x2="618" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="102" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="124.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">IDT  (lidt)</text><rect x="20" y="142" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="164.0" font-size="11.0" fill="#4d5656" text-anchor="middle">트랩 원인</text><rect x="310" y="142" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="164.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">scause  (r_scause)</text><line x1="592" y1="160" x2="618" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="142" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="164.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">벡터 번호 trapno (스텁이 push)</text><rect x="20" y="182" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="204.0" font-size="11.0" fill="#4d5656" text-anchor="middle">잘못된 주소</text><rect x="310" y="182" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="204.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stval  (r_stval)</text><line x1="592" y1="200" x2="618" y2="200" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="182" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="204.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">CR2  (r_cr2)</text><rect x="20" y="222" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="244.0" font-size="11.0" fill="#4d5656" text-anchor="middle">트랩 난 곳</text><rect x="310" y="222" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="244.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sepc  (r_sepc)</text><line x1="592" y1="240" x2="618" y2="240" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="222" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="244.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">trapframe 의 rip (CPU 가 push)</text><rect x="20" y="262" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="284.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPU 번호</text><rect x="310" y="262" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="284.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">tp  (r_tp, w_tp)</text><line x1="592" y1="280" x2="618" y2="280" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="262" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="284.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">GS base MSR  (r_gsbase, wrmsr)</text><rect x="20" y="302" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle">인터럽트 켬/끔</text><rect x="310" y="302" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sstatus.SIE  (intr_on/off)</text><line x1="592" y1="320" x2="618" y2="320" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="302" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">RFLAGS.IF  (sti / cli)</text><rect x="20" y="342" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="364.0" font-size="11.0" fill="#4d5656" text-anchor="middle">시스템 콜 명령</text><rect x="310" y="342" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="364.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ecall</text><line x1="592" y1="360" x2="618" y2="360" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="342" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="364.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">int $64</text><rect x="20" y="382" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="404.0" font-size="11.0" fill="#4d5656" text-anchor="middle">사용자로 돌아가기</text><rect x="310" y="382" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="404.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sret</text><line x1="592" y1="400" x2="618" y2="400" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="382" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="404.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">iretq</text><rect x="20" y="422" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="444.0" font-size="11.0" fill="#4d5656" text-anchor="middle">TLB 비우기</text><rect x="310" y="422" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="444.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sfence.vma</text><line x1="592" y1="440" x2="618" y2="440" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="422" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="444.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">CR3 다시 쓰기  (sfence_vma)</text><rect x="20" y="462" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="484.0" font-size="11.0" fill="#4d5656" text-anchor="middle">타이머</text><rect x="310" y="462" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="484.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stimecmp</text><line x1="592" y1="480" x2="618" y2="480" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="462" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="484.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">LAPIC 타이머</text><text x="500.0" y="514.0" font-size="11.5" fill="#4d5656" text-anchor="middle">x86 에는 같은 이름의 레지스터가 없는 것도 있다 : 트랩 원인과 위치는 CPU 와 스텁이 스택에 push 한다</text></svg>
<!-- /fig:regmap -->

### 2.1 부팅 : UEFI 로더 (`boot/loader.c`, 새 파일)

<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="RISC-V 와 x86-64 의 부팅 경로"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">부팅 : 누가 커널을 메모리에 올리고 main() 까지 오나</text><text x="20.0" y="58.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">xv6-riscv (QEMU virt)</text><rect x="20" y="70" width="190" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="115.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">QEMU</text><text x="115.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">-kernel 로 커널을</text><text x="115.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">0x80000000 에 올림</text><rect x="250" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="345.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">entry.S</text><text x="345.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">machine mode</text><text x="345.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPU 마다 스택</text><rect x="480" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="575.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.c</text><text x="575.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">machine → supervisor</text><text x="575.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">(mret)</text><rect x="710" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="805.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">main.c</text><text x="805.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kinit, kvminit, ...</text><text x="805.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">scheduler()</text><line x1="210" y1="105" x2="248" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="105" x2="478" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="670" y1="105" x2="708" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="20.0" y="178.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">xv6-x86_64 (UEFI PC)</text><rect x="20" y="190" width="150" height="110" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="95.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">UEFI 펌웨어</text><text x="95.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">64비트 모드</text><text x="95.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">페이지 켜짐</text><text x="95.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">메모리 = 물리 주소</text><rect x="200" y="190" width="230" height="110" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="315.0" y="217.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">boot/loader.c (새로)</text><text x="315.0" y="233.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kernel, fs.img 읽기</text><text x="315.0" y="249.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ACPI, 화면, 메모리 맵</text><text x="315.0" y="265.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ExitBootServices</text><text x="315.0" y="281.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ _entry(bootinfo)</text><rect x="460" y="190" width="150" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="535.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">entry.S</text><text x="535.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">0x100000</text><text x="535.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">스택 잡고</text><text x="535.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">start() 호출</text><rect x="640" y="190" width="150" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="715.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.c</text><text x="715.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">bootinfo 복사</text><text x="715.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">EFER.NXE 켬</text><text x="715.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">GS base = 0</text><rect x="820" y="190" width="160" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="900.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">main.c</text><text x="900.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ acpiinit</text><text x="900.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ ioapic, lapic</text><text x="900.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ startothers</text><line x1="170" y1="245" x2="198" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="430" y1="245" x2="458" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="610" y1="245" x2="638" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="790" y1="245" x2="818" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="312" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="40.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">새로 생김</text><rect x="115" y="312" width="14" height="12" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="135.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">바뀜</text><rect x="171" y="312" width="14" height="12" rx="2" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="191.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">지움</text></svg>

PC 에는 QEMU 의 `-kernel` 같은 것이 없다. 전원이 들어오면 **UEFI 펌웨어** 가 USB 메모리의 `EFI/BOOT/BOOTX64.EFI` 를 찾아 실행한다.
그 프로그램 (우리 로더) 이 커널을 읽어 메모리에 올리고 뛰어야 한다. 로더는 clang 과 lld-link 로 Windows 형식 (PE/COFF) 으로 만든다 : UEFI 가 그 형식만 실행한다.

로더의 마지막 부분. 커널이 알아야 할 것을 `struct bootinfo` 에 모으고, 펌웨어의 서비스를 끝내고 (`ExitBootServices`), 커널로 뛴다 :

[`boot/loader.c:239–296`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/boot/loader.c#L239-L296) (태그 `v0.1-x86_64-c`)

```cpp
  // the file system image, which the kernel uses as a RAM disk.
  UINT64 size;
  EFI_FILE *f = openfile(root, L"\\fs.img", &size);
  bi->fsimg = lowpages((size + PGSIZE - 1) / PGSIZE, PHYSTOP);
  bi->fsimg_size = size;
  readfile(f, (void *)bi->fsimg, size);
  f->Close(f);

  // a page below 1MB, where other CPUs start in 16-bit mode.
  bi->apboot = lowpages(1, 0xA0000);

  // the ACPI tables describe the CPUs and interrupt controllers.
  EFI_GUID acpi20 = ACPI_20_TABLE_GUID, acpi10 = ACPI_10_TABLE_GUID;
  for (UINTN i = 0; i < ST->NumberOfTableEntries; i++) {
    EFI_CONFIGURATION_TABLE *t = &ST->ConfigurationTable[i];
    if (guideq(&t->VendorGuid, &acpi20)) {
      bi->rsdp = (UINT64)t->VendorTable;
      break;
    }
    if (guideq(&t->VendorGuid, &acpi10))
      bi->rsdp = (UINT64)t->VendorTable;
  }

  // the frame buffer, for a screen console on machines
  // without a serial port.
  EFI_GRAPHICS_OUTPUT *gop;
  EFI_GUID gopguid = GRAPHICS_OUTPUT_GUID;
  if (!EFI_ERROR(BS->LocateProtocol(&gopguid, 0, (void **)&gop))) {
    bi->fb_base = gop->Mode->FrameBufferBase;
    bi->fb_size = gop->Mode->FrameBufferSize;
    bi->fb_width = gop->Mode->Info->HorizontalResolution;
    bi->fb_height = gop->Mode->Info->VerticalResolution;
    bi->fb_stride = gop->Mode->Info->PixelsPerScanLine;
  }

  // get the memory map, and leave boot services. the map must be
  // current, so allocate the buffer first; ExitBootServices fails
  // if the map changed since GetMemoryMap, so retry.
  UINTN mapbytes = 16 * PGSIZE;
  bi->memmap = lowpages(mapbytes / PGSIZE, PHYSTOP);
  print(L"starting kernel\r\n");
  for (int tries = 0;; tries++) {
    UINTN mapsize = mapbytes, mapkey, descsize;
    UINT32 descversion;
    s = BS->GetMemoryMap(&mapsize, (EFI_MEMORY_DESCRIPTOR *)bi->memmap,
                         &mapkey, &descsize, &descversion);
    if (EFI_ERROR(s))
      fail(L"cannot get memory map", s);
    bi->memmap_size = mapsize;
    bi->memmap_descsize = descsize;
    s = BS->ExitBootServices(imagehandle, mapkey);
    if (!EFI_ERROR(s))
      break;
    if (tries > 10)
      fail(L"cannot exit boot services", s);
  }

  ((kernel_entry)entry)(bi);
```

| `bootinfo` 의 항목 | 왜 필요한가 | RISC-V 판에서는 |
|---|---|---|
| `fsimg`, `fsimg_size` | 디스크 대신 메모리에 올린 파일 시스템 (2.6) | virtio 디스크 |
| `apboot` | 다른 CPU 가 16비트로 시작할 1MB 아래 페이지 (2.5) | 필요 없음 |
| `rsdp` | ACPI 표의 시작 : CPU 와 인터럽트 장치 목록 (2.4) | 주소가 고정이라 필요 없음 |
| `fb_*` | 화면 (이 태그에서는 아직 안 씀. `v0.2` 에서) | 화면 없음 |
| `memmap` | 어느 RAM 이 비어 있나 (2.2) | `0x80000000` ~ `PHYSTOP` 전부 |

커널의 첫 코드 `entry.S` 는 RISC-V 판처럼 스택만 잡고 `start()` 를 부른다. 다른 점은 `bootinfo` 의 주소가 `%rdi` 에 들어 있다는 것 :

[`kernel/entry.S:7–16`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/entry.S#L7-L16) (태그 `v0.1-x86_64-c`)

```asm
_entry:
        cli
        # set up a stack for C.
        # stack0 is declared in start.c,
        # with a 4096-byte stack per CPU.
        # %rsp = stack0 + 4096, for CPU 0
        leaq stack0+4096(%rip), %rsp
        # jump to start() in start.c; %rdi still holds bootinfo.
        call start
spin:
```

`start.c` 는 RISC-V 판에서 machine mode → supervisor mode 로 내려가는 일을 했다. UEFI 가 이미 64비트 모드, 최고 권한 (ring 0), 페이지 켜짐 상태로 넘겨주므로 할 일이 거의 없다 :

[`kernel/start.c:24–37`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/start.c#L24-L37) (태그 `v0.1-x86_64-c`)

```cpp
start(struct bootinfo *bi)
{
  // the loader's copy lives in memory that kinit() will not
  // free, but keep a copy in the kernel anyway.
  bootinfo = *bi;

  // allow page table entries to forbid execution.
  wrmsr(MSR_EFER, rdmsr(MSR_EFER) | EFER_NXE);

  // keep each CPU's id in its GS base register, for cpuid().
  w_gsbase(0);

  main();
}
```

### 2.2 메모리

<svg viewBox="0 0 1000 500" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="x86-64 판의 물리 메모리 배치"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">물리 메모리 (x86-64 판, QEMU 512MB 의 예)</text><rect x="140" y="60" width="260" height="34" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="270.0" y="81.0" font-size="11" fill="#4d5656" text-anchor="middle">LAPIC (CPU 마다의 인터럽트 장치)</text><text x="134.0" y="98.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0xFEE00000</text><rect x="140" y="94" width="260" height="34" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="270.0" y="115.0" font-size="11" fill="#4d5656" text-anchor="middle">IOAPIC (장치 인터럽트)</text><text x="134.0" y="132.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0xFEC00000</text><rect x="140" y="128" width="260" height="50" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="157.0" font-size="11" fill="#4d5656" text-anchor="middle">…  (PHYSTOP 위 : xv6 는 안 씀)</text><text x="134.0" y="182.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">PHYSTOP = 128MB</text><rect x="140" y="178" width="260" height="110" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="237.0" font-size="11" fill="#4d5656" text-anchor="middle">빈 페이지 → kalloc()</text><rect x="140" y="288" width="260" height="40" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="270.0" y="312.0" font-size="11" fill="#4d5656" text-anchor="middle">fs.img (램디스크), bootinfo</text><rect x="140" y="328" width="260" height="60" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="362.0" font-size="11" fill="#4d5656" text-anchor="middle">빈 페이지 → kalloc()</text><text x="134.0" y="392.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">end</text><rect x="140" y="388" width="260" height="50" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="417.0" font-size="11" fill="#4d5656" text-anchor="middle">커널 text, data, bss</text><text x="134.0" y="442.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00100000</text><rect x="140" y="438" width="260" height="40" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="462.0" font-size="11" fill="#4d5656" text-anchor="middle">낮은 메모리 : 펌웨어, AP 시작 페이지</text><text x="134.0" y="482.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00000000</text><rect x="470" y="70" width="500" height="120" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="720.0" y="102.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">kinit() 이 바뀐 점</text><text x="720.0" y="118.0" font-size="11.0" fill="#4d5656" text-anchor="middle">RISC-V : end ~ PHYSTOP 을 통째로 비어 있다고 본다</text><text x="720.0" y="134.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86-64 : UEFI 메모리 맵에서 &#x27;conventional&#x27; (빈) 영역만</text><text x="720.0" y="150.0" font-size="11.0" fill="#4d5656" text-anchor="middle">         end ~ PHYSTOP 사이에서 골라 free</text><text x="720.0" y="166.0" font-size="11.0" fill="#4d5656" text-anchor="middle">PC 의 RAM 에는 구멍이 있고, 펌웨어가 쓰는 곳도 있다</text><rect x="470" y="220" width="500" height="100" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="720.0" y="250.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">장치는 주소가 정해져 있지 않다</text><text x="720.0" y="266.0" font-size="11.0" fill="#4d5656" text-anchor="middle">RISC-V virt : UART 0x10000000, PLIC 0x0c000000 (고정)</text><text x="720.0" y="282.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86-64 : LAPIC, IOAPIC 주소를 ACPI 표 (MADT) 에서 읽는다</text><text x="720.0" y="298.0" font-size="11.0" fill="#4d5656" text-anchor="middle">시리얼 COM1 은 메모리가 아니라 I/O 포트 0x3F8</text><rect x="470" y="350" width="500" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="720.0" y="378.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">디스크가 없다</text><text x="720.0" y="394.0" font-size="11.0" fill="#4d5656" text-anchor="middle">virtio 디스크 (가상 장치) 대신, 로더가 fs.img 를</text><text x="720.0" y="410.0" font-size="11.0" fill="#4d5656" text-anchor="middle">메모리에 올리고 ramdisk.c 가 그것을 디스크처럼 읽고 쓴다</text></svg>

`kinit()` 은 UEFI 메모리 맵의 빈 영역만 free 한다 :

[`kernel/kalloc.c:34–51`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/kalloc.c#L34-L51) (태그 `v0.1-x86_64-c`)

```cpp
kinit()
{
  initlock(&kmem.lock, "kmem");
  for (uint64 off = 0; off < bootinfo.memmap_size;
       off += bootinfo.memmap_descsize) {
    struct efi_memdesc *d = (struct efi_memdesc *)(bootinfo.memmap + off);
    if (d->type != EFI_CONVENTIONAL_MEMORY)
      continue;
    uint64 start = d->phys_start;
    uint64 stop = d->phys_start + d->npages * PGSIZE;
    if (start < (uint64)end)
      start = (uint64)end;
    if (stop > PHYSTOP)
      stop = PHYSTOP;
    if (start < stop)
      freerange((void *)start, (void *)stop);
  }
}
```

페이지 테이블은 RISC-V Sv39 (3단계, 9비트씩) 대신 x86-64 4단계 (9비트씩, 한 단계 더). `walk()` 의 고리가 `level = 2` 대신 `level = 3` 에서 시작한다 ([`kernel/vm.c:108`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/vm.c#L108)).
PTE 의 비트 이름은 RISC-V 와 맞추려고 `PTE_R`, `PTE_X` 를 소프트웨어 비트로 남기고, 실행 금지는 x86 의 `PTE_NX` (비트 63) 로 바꾼다. 그래서 `start()` 에서 `EFER.NXE` 를 켠다.

<!-- fig:pagewalk -->
<svg viewBox="0 0 1000 420" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="페이지 테이블 단계 비교"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">가상 주소 → 물리 주소 : Sv39 (3단계) 와 x86-64 (4단계)</text><text x="20.0" y="58.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">RISC-V Sv39</text><rect x="150" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="244.6" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L2 (9비트)</text><text x="152.0" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">38</text><text x="337.2" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30</text><rect x="339.2307692307692" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="433.8" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L1 (9비트)</text><text x="341.2" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">29</text><text x="526.5" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">21</text><rect x="528.4615384615385" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="623.1" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L0 (9비트)</text><text x="530.5" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">20</text><text x="715.7" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="717.6923076923076" y="66" width="252.30769230769232" height="34" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="843.8" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">페이지 안 오프셋 (12)</text><text x="719.7" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><text x="968.0" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="20.0" y="160.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">x86-64</text><rect x="150" y="168" width="153.75" height="34" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="226.9" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PML4 (L3)</text><text x="152.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">47</text><text x="301.8" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">39</text><rect x="303.75" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="380.6" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PDPT (L2)</text><text x="305.8" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">38</text><text x="455.5" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30</text><rect x="457.5" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="534.4" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PD (L1)</text><text x="459.5" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">29</text><text x="609.2" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">21</text><rect x="611.25" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="688.1" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PT (L0)</text><text x="613.2" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">20</text><text x="763.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="765.0" y="168" width="205.0" height="34" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="867.5" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">오프셋 (12)</text><text x="767.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><text x="968.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="20" y="240" width="470" height="160" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="255.0" y="276.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">walk() 이 바뀐 곳 (vm.c)</text><text x="255.0" y="292.0" font-size="11.0" fill="#4d5656" text-anchor="middle">for (level = 2 …)  →  for (level = 3 …)</text><text x="255.0" y="308.0" font-size="11.0" fill="#4d5656" text-anchor="middle">PX(level, va) : 9비트씩, 한 단계 더</text><text x="255.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle"></text><text x="255.0" y="340.0" font-size="11.0" fill="#4d5656" text-anchor="middle">중간 단계 PTE 에 W | U 도 켠다 :</text><text x="255.0" y="356.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86 은 모든 단계에서 W, U 를 검사하므로</text><text x="255.0" y="372.0" font-size="11.0" fill="#4d5656" text-anchor="middle">마지막 (leaf) PTE 만 권한을 정하게</text><rect x="510" y="240" width="470" height="160" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="745.0" y="276.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">MAXVA 는 RISC-V 그대로 (2³⁸)</text><text x="745.0" y="292.0" font-size="11.0" fill="#4d5656" text-anchor="middle">사용자 주소 배치를 바꾸지 않으려고</text><text x="745.0" y="308.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86 이 허용하는 2⁴⁷ 대신 2³⁸ 까지만 쓴다</text><text x="745.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle"></text><text x="745.0" y="340.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ 맨 위 PML4 의 인덱스는 언제나 0</text><text x="745.0" y="356.0" font-size="11.0" fill="#4d5656" text-anchor="middle">  (가상 주소 비트 47:39 가 0)</text><text x="745.0" y="372.0" font-size="11.0" fill="#4d5656" text-anchor="middle">TRAMPOLINE = MAXVA − 4096</text></svg>
<!-- /fig:pagewalk -->

<!-- fig:ptebits -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="x86-64 PTE 비트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">x86-64 PTE (64비트) : xv6 가 쓰는 비트</text><rect x="60" y="60" width="65.85365853658537" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="92.9" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">NX</text><text x="92.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">63</text><rect x="125.85365853658537" y="60" width="109.75609756097562" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="180.7" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(안 씀)</text><text x="127.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">62</text><text x="233.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">52</text><rect x="235.609756097561" y="60" width="307.31707317073176" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="389.3" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">물리 페이지 번호 (PTE2PA)</text><text x="237.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">51</text><text x="540.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="542.9268292682927" y="60" width="21.951219512195124" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="553.9" y="86.0" font-size="9.5" fill="#4d5656" text-anchor="middle"></text><text x="553.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><rect x="564.8780487804879" y="60" width="43.90243902439025" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="586.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">X*</text><text x="586.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10</text><rect x="608.7804878048781" y="60" width="43.90243902439025" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="630.7" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">R*</text><text x="630.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">9</text><rect x="652.6829268292684" y="60" width="87.8048780487805" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="696.6" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(안 씀)</text><text x="654.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><text x="738.5" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="740.4878048780488" y="60" width="43.90243902439025" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="762.4" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PCD</text><text x="762.4" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="784.390243902439" y="60" width="43.90243902439025" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="806.3" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PWT</text><text x="806.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><rect x="828.2926829268292" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="850.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">U</text><text x="850.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="872.1951219512194" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="894.1" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">W</text><text x="894.1" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="916.0975609756097" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="938.0" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">P (V)</text><text x="938.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="60" y="140" width="430" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="275.0" y="165.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">하드웨어 비트</text><text x="275.0" y="181.0" font-size="10.5" fill="#4d5656" text-anchor="middle">P = PTE_V (있음), W 쓰기, U 사용자</text><text x="275.0" y="197.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PCD : 캐시 끔 (LAPIC, IOAPIC 매핑)</text><text x="275.0" y="213.0" font-size="10.5" fill="#4d5656" text-anchor="middle">NX (63) : 실행 금지 → EFER.NXE 를 켜야 동작</text><rect x="510" y="140" width="450" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="735.0" y="165.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">* 소프트웨어 비트 (CPU 는 무시)</text><text x="735.0" y="181.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PTE_R (9), PTE_X (10) : RISC-V 코드의 권한 인자를</text><text x="735.0" y="197.0" font-size="10.5" fill="#4d5656" text-anchor="middle">그대로 쓰려고 남겼다. mappages() 가</text><text x="735.0" y="213.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PTE_X 가 없으면 NX 를 켠다</text></svg>
<!-- /fig:ptebits -->

<svg viewBox="0 0 1000 400" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="가상 주소 공간 꼭대기 비교"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">가상 주소 공간의 꼭대기 : x86-64 판에 CPUTABLES 페이지가 생겼다</text><text x="270.0" y="62.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xv6-riscv : 사용자 페이지 테이블</text><rect x="120" y="70" width="300" height="40" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="94.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAMPOLINE (trampoline.S)</text><rect x="120" y="110" width="300" height="40" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="134.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAPFRAME (p-&gt;trapframe)</text><rect x="120" y="150" width="300" height="30" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="169.0" font-size="11" fill="#4d5656" text-anchor="middle">…</text><rect x="120" y="180" width="300" height="80" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="224.0" font-size="11" fill="#4d5656" text-anchor="middle">사용자 메모리 (text, data, stack, heap)</text><text x="114.0" y="264.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="750.0" y="62.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xv6-x86_64 : 사용자 페이지 테이블</text><rect x="600" y="70" width="300" height="40" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="750.0" y="94.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAMPOLINE (trampoline.S)</text><rect x="600" y="110" width="300" height="40" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="750.0" y="134.0" font-size="11" fill="#4d5656" text-anchor="middle">CPUTABLES (IDT, GDT, TSS)</text><rect x="600" y="150" width="300" height="40" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="750.0" y="174.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAPFRAME (p-&gt;trapframe)</text><rect x="600" y="190" width="300" height="30" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="750.0" y="209.0" font-size="11" fill="#4d5656" text-anchor="middle">…</text><rect x="600" y="220" width="300" height="80" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="750.0" y="264.0" font-size="11" fill="#4d5656" text-anchor="middle">사용자 메모리</text><text x="594.0" y="304.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="120" y="336" width="780" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="510.0" y="357.0" font-size="10.5" fill="#4d5656" text-anchor="middle">CPU 는 트랩이 나면 IDT·GDT·TSS 를 읽는다. 사용자 페이지 테이블이 켜진 채로 트랩이 나도 읽을 수 있도록,</text><text x="510.0" y="373.0" font-size="10.5" fill="#4d5656" text-anchor="middle">이 표들이 든 페이지를 모든 페이지 테이블의 같은 주소 (TRAMPOLINE 바로 아래) 에 둔다</text></svg>

### 2.3 트랩과 시스템 콜 (`trampoline.S`, `trap.c`, `kernelvec.S`, `x86.h`)

가장 크게 다시 쓴 부분. x86 의 CPU 는 트랩이 나면 **IDT** (Interrupt Descriptor Table) 에서 처리 코드 주소를 찾고, 사용자 모드에서 왔으면 **TSS** 의 `rsp0` 로 스택을 바꾼 뒤 몇 개의 레지스터를 그 스택에 push 한다.

<svg viewBox="0 0 1000 450" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="시스템 콜의 경로와 trapframe"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">사용자 프로그램의 시스템 콜 : int $64 부터 usertrap() 까지</text><rect x="20" y="60" width="200" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="120.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">사용자 프로그램</text><text x="120.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">usys.S : rax = 번호</text><text x="120.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">int $64</text><rect x="270" y="60" width="220" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="380.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU (하드웨어)</text><text x="380.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">TSS.rsp0 로 스택을 바꾸고</text><text x="380.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ss, rsp, rflags, cs, rip push</text><rect x="540" y="60" width="200" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="640.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">trampoline.S : uvec64</text><text x="640.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">err (0), trapno (64)</text><text x="640.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">push</text><rect x="790" y="60" width="190" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="885.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uservec</text><text x="885.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">범용 레지스터 15개</text><text x="885.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">push, cld</text><line x1="220" y1="95" x2="268" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="490" y1="95" x2="538" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="740" y1="95" x2="788" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="790" y="170" width="190" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="885.0" y="187.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uservec (계속)</text><text x="885.0" y="203.0" font-size="11.0" fill="#4d5656" text-anchor="middle">GS = cpu id</text><text x="885.0" y="219.0" font-size="11.0" fill="#4d5656" text-anchor="middle">cr3 = 커널 페이지 테이블</text><text x="885.0" y="235.0" font-size="11.0" fill="#4d5656" text-anchor="middle">rsp = 커널 스택</text><text x="885.0" y="251.0" font-size="11.0" fill="#4d5656" text-anchor="middle">call usertrap</text><line x1="885" y1="130" x2="885" y2="168" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="540" y="170" width="200" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="640.0" y="195.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">usertrap() (trap.c)</text><text x="640.0" y="211.0" font-size="11.0" fill="#4d5656" text-anchor="middle">lidt(kidt) : 커널용 IDT</text><text x="640.0" y="227.0" font-size="11.0" fill="#4d5656" text-anchor="middle">trapno == 64 → syscall()</text><text x="640.0" y="243.0" font-size="11.0" fill="#4d5656" text-anchor="middle">rip 은 이미 int 다음</text><line x1="790" y1="215" x2="742" y2="215" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="160.0" y="182.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">TRAPFRAME 페이지 (p-&gt;trapframe)</text><rect x="30" y="192" width="260" height="30" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="160.0" y="211.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kernel_cr3, kernel_sp, kernel_trap, kernel_hartid</text><rect x="30" y="222" width="260" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="160.0" y="243.0" font-size="10.0" fill="#4d5656" text-anchor="middle">r15 … rax  (uservec 가 push)</text><rect x="30" y="256" width="260" height="26" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="160.0" y="273.0" font-size="10.0" fill="#4d5656" text-anchor="middle">trapno, err  (vector stub 가 push)</text><rect x="30" y="282" width="260" height="34" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="160.0" y="303.0" font-size="10.0" fill="#4d5656" text-anchor="middle">rip, cs, rflags, rsp, ss  (CPU 가 push)</text><text x="296.0" y="320.0" font-size="10.5" fill="#566573" text-anchor="start">← TSS.rsp0 = TRAPFRAME 의 끝</text><text x="160.0" y="346.0" font-size="10.5" fill="#4d5656" text-anchor="middle">그림은 아래로 갈수록 주소가 크다. push 는 끝 (아래) 에서 위로 채운다</text><rect x="20" y="360" width="960" height="70" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="383.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">RISC-V 와 비교</text><text x="500.0" y="399.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V : ecall → stvec 이 가리키는 uservec 이 sscratch 로 TRAPFRAME 을 찾아 레지스터를 하나씩 저장 (CPU 는 sepc 만 저장)</text><text x="500.0" y="415.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64 : CPU 가 일부를 스택에 push 하므로, 스택 (rsp0) 을 TRAPFRAME 끝으로 두면 push 만으로 trapframe 이 채워진다</text></svg>

`p->trapframe` 의 모양이 이렇게 바뀌었다. 위에서부터 채워지는 순서와 아래에서부터 읽는 필드 위치 (`/* 0 */` …) 를 보자 :

[`kernel/proc.h:53–80`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/proc.h#L53-L80) (태그 `v0.1-x86_64-c`)

```cpp
struct trapframe {
  /*   0 */ uint64 kernel_cr3;    // kernel page table
  /*   8 */ uint64 kernel_sp;     // top of process's kernel stack
  /*  16 */ uint64 kernel_trap;   // usertrap()
  /*  24 */ uint64 kernel_hartid; // saved kernel GS base (the cpu id)
  /*  32 */ uint64 r15;
  /*  40 */ uint64 r14;
  /*  48 */ uint64 r13;
  /*  56 */ uint64 r12;
  /*  64 */ uint64 r11;
  /*  72 */ uint64 r10;
  /*  80 */ uint64 r9;
  /*  88 */ uint64 r8;
  /*  96 */ uint64 rdi;
  /* 104 */ uint64 rsi;
  /* 112 */ uint64 rbp;
  /* 120 */ uint64 rdx;
  /* 128 */ uint64 rcx;
  /* 136 */ uint64 rbx;
  /* 144 */ uint64 rax;
  /* 152 */ uint64 trapno; // pushed by the vector stub
  /* 160 */ uint64 err;    // pushed by the CPU, or 0 by the stub
  /* 168 */ uint64 rip;    // user program counter (RISC-V epc)
  /* 176 */ uint64 cs;
  /* 184 */ uint64 rflags;
  /* 192 */ uint64 rsp;    // user stack pointer
  /* 200 */ uint64 ss;
};
```

`trampoline.S` 의 앞부분은 매크로로 만든 **벡터마다의 짧은 진입점** (`uvec0` … `uvec64`). x86 은 처리 코드에게 몇 번 벡터로 왔는지 알려 주지 않아서 각자 번호를 push 한다 :

[`kernel/trampoline.S:24–32`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/trampoline.S#L24-L32) (태그 `v0.1-x86_64-c`)

```asm
.macro uvec n
uvec\n:
  .if (\n == 8) || (\n == 10) || (\n == 11) || (\n == 12) || (\n == 13) || (\n == 14) || (\n == 17) || (\n == 21) || (\n == 29) || (\n == 30)
  .else
        pushq $0
  .endif
        pushq $\n
        jmp uservec
.endm
```

IDT 가 **두 벌** 이다. RISC-V 판이 `stvec` 을 `uservec` 과 `kernelvec` 사이에서 바꾸듯, `usertrap()` 은 커널용 IDT 를, 사용자로 돌아갈 때는 사용자용 IDT (`trampoline.S` 를 가리킴) 를 `lidt` 한다 ([`kernel/trap.c:129`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/trap.c#L129)).

시스템 콜 인자는 Linux 와 같은 레지스터 (`rdi, rsi, rdx, r10, r8, r9`), 번호는 `rax`, 들어가는 명령은 `int $64` :

[`kernel/syscall.c:35–56`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/syscall.c#L35-L56) (태그 `v0.1-x86_64-c`)

```cpp
argraw(int n)
{
  struct proc *p = myproc();
  // the same registers as Linux on x86-64; usys.pl moves
  // the fourth argument from rcx to r10.
  switch (n) {
  case 0:
    return p->trapframe->rdi;
  case 1:
    return p->trapframe->rsi;
  case 2:
    return p->trapframe->rdx;
  case 3:
    return p->trapframe->r10;
  case 4:
    return p->trapframe->r8;
  case 5:
    return p->trapframe->r9;
  }
  panic("argraw");
  return -1;
}
```

문맥 교환 `swtch.S` : RISC-V 는 돌아갈 주소가 `ra` 레지스터에 있지만 x86-64 는 스택에 있다. 그래서 스택 맨 위의 반환 주소를 `context.ra` 로 저장하고, 새 문맥으로는 `jmp *ra` 로 "돌아간다" :

[`kernel/swtch.S:12–32`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/swtch.S#L12-L32) (태그 `v0.1-x86_64-c`)

```asm
swtch:
        movq (%rsp), %rax
        movq %rax, 0(%rdi)
        leaq 8(%rsp), %rax
        movq %rax, 8(%rdi)
        movq %rbx, 16(%rdi)
        movq %rbp, 24(%rdi)
        movq %r12, 32(%rdi)
        movq %r13, 40(%rdi)
        movq %r14, 48(%rdi)
        movq %r15, 56(%rdi)

        movq 8(%rsi), %rsp
        movq 16(%rsi), %rbx
        movq 24(%rsi), %rbp
        movq 32(%rsi), %r12
        movq 40(%rsi), %r13
        movq 48(%rsi), %r14
        movq 56(%rsi), %r15
        
        jmp *0(%rsi)
```

<!-- fig:swtch -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="swtch"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">문맥 교환 swtch(old, new) : 반환 주소가 스택에 있는 x86-64</text><rect x="20" y="55" width="300" height="200" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="170.0" y="111.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">struct context</text><text x="170.0" y="127.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ra   ← 스택 맨 위의 반환 주소</text><text x="170.0" y="143.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sp   ← 돌아간 뒤의 rsp</text><text x="170.0" y="159.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx</text><text x="170.0" y="175.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbp</text><text x="170.0" y="191.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">r12  r13  r14  r15</text><text x="170.0" y="207.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">(callee-saved, System V ABI)</text><rect x="360" y="55" width="280" height="90" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="500.0" y="80.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">저장 (old)</text><text x="500.0" y="96.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">movq (%rsp), %rax → old-&gt;ra</text><text x="500.0" y="112.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">leaq 8(%rsp) → old-&gt;sp</text><text x="500.0" y="128.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx, rbp, r12–r15</text><rect x="360" y="165" width="280" height="90" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="500.0" y="190.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">복원 (new)</text><text x="500.0" y="206.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">new-&gt;sp → %rsp</text><text x="500.0" y="222.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx, rbp, r12–r15</text><text x="500.0" y="238.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">jmp *new-&gt;ra</text><rect x="680" y="55" width="300" height="200" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="830.0" y="111.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">RISC-V 와 다른 점</text><text x="830.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V : ra 레지스터에 반환 주소</text><text x="830.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ ret 로 돌아간다</text><text x="830.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="830.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64 : call 이 반환 주소를 스택에 push</text><text x="830.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 저장할 때 꺼내 ra 에 두고,</text><text x="830.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle">  복원할 때 jmp 로 &#x27;돌아간다&#x27;</text></svg>
<!-- /fig:swtch -->

### 2.4 인터럽트 장치 (`acpi.c`, `lapic.c`, `ioapic.c` 새 파일, `plic.c` 지움)

<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="ACPI 로 LAPIC, IOAPIC 찾기"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">인터럽트 장치 찾기 : ACPI 표를 따라가서 (acpi.c)</text><rect x="20" y="70" width="160" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="100.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">RSDP</text><text x="100.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">로더가 UEFI 에서</text><text x="100.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">받아 bootinfo 로</text><rect x="230" y="70" width="160" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="310.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">XSDT</text><text x="310.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">모든 표의</text><text x="310.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">주소 목록</text><rect x="440" y="70" width="200" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="540.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">MADT (&quot;APIC&quot;)</text><text x="540.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPU 와 인터럽트</text><text x="540.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">컨트롤러 목록</text><line x1="180" y1="105" x2="228" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="390" y1="105" x2="438" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="700" y="40" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="66.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">LAPIC 항목 → apicids[] (CPU 목록)</text><rect x="700" y="92" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="118.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">IOAPIC 항목 → ioapicaddr</text><rect x="700" y="144" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="170.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">ISO 항목 → IRQ 재배선 (ISA → GSI)</text><line x1="640" y1="105" x2="698" y2="62" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="640" y1="105" x2="698" y2="114" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="640" y1="105" x2="698" y2="166" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="200" width="960" height="80" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="228.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">RISC-V 와 비교</text><text x="500.0" y="244.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V virt : PLIC (장치 인터럽트) 와 CLINT (타이머) 가 정해진 주소에 있어서 memlayout.h 의 상수로 충분하다</text><text x="500.0" y="260.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64 : 주소와 CPU 수가 기계마다 다르다. lapic.c, ioapic.c 는 옛 x86 판 (xv6-public) 에서 가져와 64비트로 고쳤다</text></svg>

[`kernel/acpi.c:91–131`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/acpi.c#L91-L131) (태그 `v0.1-x86_64-c`)

```cpp
acpiinit(void)
{
  for (int i = 0; i < 16; i++)
    isairq[i] = i;

  struct acpi_rsdp *rsdp = (struct acpi_rsdp *)bootinfo.rsdp;
  if (rsdp == 0 || memcmp(rsdp->signature, "RSD PTR ", 8) != 0)
    panic("acpiinit: no RSDP");

  struct acpi_madt *madt = (struct acpi_madt *)findtable(rsdp, "APIC");
  if (madt == 0)
    panic("acpiinit: no MADT");

  lapicaddr = madt->lapic;
  uchar *p = madt->entries;
  uchar *e = (uchar *)madt + madt->h.length;
  while (p < e) {
    int type = p[0], len = p[1];
    if (type == MADT_LAPIC) {
      uint flags = *(uint *)(p + 4);
      if ((flags & 1) && ncpu < NCPU) // enabled
        apicids[ncpu++] = p[3];
    } else if (type == MADT_IOAPIC) {
      if (ioapicaddr == 0) // xv6 uses only the first IOAPIC
        ioapicaddr = *(uint *)(p + 4);
    } else if (type == MADT_ISO) {
      int source = p[3];
      uint gsi = *(uint *)(p + 4);
      if (source < 16)
        isairq[source] = gsi;
    } else if (type == MADT_LAPIC_ADDR) {
      lapicaddr = *(uint64 *)(p + 4);
    }
    if (len == 0)
      break;
    p += len;
  }

  if (ncpu == 0 || ioapicaddr == 0)
    panic("acpiinit: no CPUs or IOAPIC");
}
```

타이머는 RISC-V 의 `stimecmp` 대신 각 CPU 의 LAPIC 타이머, 시리얼 포트 인터럽트는 IOAPIC 을 거쳐 온다.

### 2.5 다른 CPU 깨우기 (`entryother.S` 새 파일, `main.c`)

<svg viewBox="0 0 1000 320" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="AP 시작 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">다른 CPU 깨우기 (startothers, entryother.S)</text><rect x="15" y="70" width="150" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="90.0" y="100.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">BSP : main.c</text><text x="90.0" y="116.0" font-size="10.5" fill="#4d5656" text-anchor="middle">entryother 코드를</text><text x="90.0" y="132.0" font-size="10.5" fill="#4d5656" text-anchor="middle">1MB 아래 페이지에 복사</text><text x="90.0" y="148.0" font-size="10.5" fill="#4d5656" text-anchor="middle">스택, cr3, 진입점 채움</text><rect x="180" y="70" width="150" height="100" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="255.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">lapicstartap()</text><text x="255.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">INIT, SIPI 신호</text><text x="255.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(LAPIC 명령)</text><line x1="165" y1="120" x2="179" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="345" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="420.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP : 16비트</text><text x="420.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">real mode 로 시작</text><text x="420.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">GDT 로드</text><line x1="330" y1="120" x2="344" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="510" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="585.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP : 32비트</text><text x="585.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">protected mode</text><text x="585.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PAE, EFER.LME</text><line x1="495" y1="120" x2="509" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="675" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="750.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP : 64비트</text><text x="750.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">long mode</text><text x="750.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">커널 cr3, 스택</text><line x1="660" y1="120" x2="674" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="840" y="70" width="150" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="915.0" y="100.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">mpenter()</text><text x="915.0" y="116.0" font-size="10.5" fill="#4d5656" text-anchor="middle">GS = id</text><text x="915.0" y="132.0" font-size="10.5" fill="#4d5656" text-anchor="middle">apstarted = 1</text><text x="915.0" y="148.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ main()</text><line x1="825" y1="120" x2="839" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="205" width="970" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="230.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">왜 이렇게 번거로운가</text><text x="500.0" y="246.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86 의 CPU 는 켜질 때 1978년 8086 처럼 16비트 real mode 에서 시작한다 (UEFI 가 깨운 첫 CPU 만 64비트).</text><text x="500.0" y="262.0" font-size="10.5" fill="#4d5656" text-anchor="middle">그래서 나머지 CPU 는 1MB 아래의 코드에서 시작해 32비트, 64비트로 직접 올라가야 한다.</text><text x="500.0" y="278.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V virt 는 모든 hart 가 처음부터 같은 커널 코드에서 함께 시작한다</text></svg>

[`kernel/main.c:57–100`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/main.c#L57-L100) (태그 `v0.1-x86_64-c`)

```cpp
startothers(void)
{
  extern struct bootinfo bootinfo;
  extern pagetable_t kernel_pagetable;
  extern char stack0[];
  extern volatile int apstarted;
  extern int ncpu;
  extern uchar apicids[];
  extern char entryother_start[], entryother_end[], eo_gdt[], eo_gdtdesc[],
      eo_far32[], eo_far64[], eo_start32[], eo_start64[], eo_cr3[],
      eo_stack[], eo_id[], eo_entry[];
  void mpenter(uint64);

#define OFF(sym) ((uint64)(sym) - (uint64)entryother_start)

  // copy entryother.S's code to the low page the loader set aside,
  // and fill in the addresses it needs.
  uint64 base = bootinfo.apboot;
  char *code = (char *)base;
  memmove(code, entryother_start, entryother_end - entryother_start);
  *(uint *)(code + OFF(eo_gdtdesc) + 2) = base + OFF(eo_gdt);
  *(uint *)(code + OFF(eo_far32)) = base + OFF(eo_start32);
  *(uint *)(code + OFF(eo_far64)) = base + OFF(eo_start64);
  *(uint64 *)(code + OFF(eo_cr3)) = MAKE_CR3(kernel_pagetable);
  *(uint64 *)(code + OFF(eo_entry)) = (uint64)mpenter;

  for (int i = 1; i < ncpu; i++) {
    *(uint64 *)(code + OFF(eo_stack)) = (uint64)stack0 + 4096 * (i + 1);
    *(uint64 *)(code + OFF(eo_id)) = i;
    apstarted = 0;
    lapicstartap(apicids[i], base);

    // wait for the CPU to reach mpenter(), which means
    // it is done with entryother's page.
    int t;
    for (t = 0; t < 1000000; t++) {
      if (__atomic_load_n(&apstarted, __ATOMIC_ACQUIRE))
        break;
      microdelay(1);
    }
    if (t == 1000000)
      printk("cpu %d did not start\n", i);
  }
}
```

CPU 번호는 RISC-V 의 `tp` 레지스터 대신 **GS base** 레지스터 (MSR) 에 둔다 : `w_gsbase(id)`. 사용자 프로그램이 들어왔다 나갈 때 `uservec` 이 다시 써 준다 (`kernel_hartid`).

### 2.6 디스크 대신 램디스크 (`ramdisk.c` 새 파일, `virtio_disk.c` 지움)

실제 PC 의 디스크 (AHCI, NVMe) 는 드라이버가 크다. 로더가 `fs.img` 를 메모리에 올려 두었으므로, "디스크 읽기 = 메모리 복사" 로 충분하다 :

[`kernel/ramdisk.c:39–49`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/ramdisk.c#L39-L49) (태그 `v0.1-x86_64-c`)

```cpp
ramdisk_rw(struct buf *b, int write)
{
  if (b->blockno >= FSSIZE)
    panic("ramdisk_rw: blockno");

  char *addr = disk + b->blockno * BSIZE;
  if (write)
    memmove(addr, b->data, BSIZE);
  else
    memmove(b->data, addr, BSIZE);
}
```

`bio.c` 의 `virtio_disk_rw(b, 0)` 이 `ramdisk_rw(b, 0)` 으로 바뀐 것이 전부다. 대신 **쓴 내용은 전원을 끄면 사라진다**.

### 2.7 사용자 쪽 (`usys.pl`, `exec.c`, `user.ld`)

- `usys.pl` : 시스템 콜 스텁이 `li a7, N; ecall` 대신 `mov $N, %rax; mov %rcx, %r10; int $64` (넷째 인자는 Linux 처럼 `r10`)
- `exec.c` : `main(argc, argv)` 의 인자를 `rdi`, `rsi` 로. 스택에 가짜 반환 주소 0 을 하나 push (x86-64 함수는 들어올 때 스택에 반환 주소가 있다고 가정). 그리고 :

[`kernel/exec.c:146–148`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/exec.c#L146-L148) (태그 `v0.1-x86_64-c`)

```cpp
  p->trapframe->rip = elf.entry; // initial program counter = ulib.c:start()
  p->trapframe->rsp = sp;        // initial stack pointer
  p->trapframe->rflags = FL_IF;  // no leftover flags, e.g. single-step
```

### 2.8 포팅하며 잡은 버그 (모두 RISC-V 에는 없는 x86 의 함정)

| 증상 | 원인 | 고친 곳 |
|---|---|---|
| 사용자 프로그램이 한 명령씩 트랩 | `kalloc` 의 쓰레기 값 (`0x05`) 이 남은 `rflags` 의 TF (single-step) 비트 | `exec.c` : `rflags = FL_IF` 로 새로 설정 |
| 커널의 문자열 명령이 거꾸로 돌 수 있음 | 사용자 프로그램이 켠 방향 플래그 (DF) 가 트랩 뒤 커널까지 남는다 (커널의 C 코드는 DF = 0 을 가정) | `uservec` 에 `cld` |
| 할 일 없는 CPU 가 영원히 잠듦 | `hlt` 전에 인터럽트가 꺼져 있었다 | `scheduler()` 에 `sti; hlt` ([`kernel/proc.c:483`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/proc.c#L483)) |
| 다른 CPU 가 캐시 없이 돎 (매우 느림) | INIT 신호로 깨어난 CPU 는 CR0 의 캐시 끔 비트 (CD, NW) 가 켜진 채 시작한다 | `entryother.S` 에서 지움 |

## 3. 바뀐 뒤

`make qemu CPUS=2` (QEMU + OVMF 펌웨어, CPU 2개) 로 부팅하면, 로더의 두 줄 뒤에 RISC-V 판과 **같은** 화면이 나온다 (실제로 돌려 본 출력) :

```
xv6 loader
starting kernel

xv6 kernel is booting

hart 1 starting
init: starting sh
$
```

- 입출력은 **시리얼 포트 (COM1) 만**. QEMU 는 터미널이 곧 시리얼이라 편하지만, VirtualBox 는 창이 까맣고 `socat` 으로 시리얼 소켓에 붙어야 셸을 쓸 수 있다 (`vbox.sh` 의 headless 모드)
- `usertests` 전체 통과 : QEMU CPU 1개, 4개. VirtualBox EFI CPU 2개
- 실제 PC 는 시험하지 않았다. 시리얼 포트가 없는 요즘 PC 에서는 아무것도 보이지 않을 것이다 → 다음 태그

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `git show 06aad25:kernel/riscv.h` 와 `kernel/x86.h` : 같은 일을 하는 함수끼리 짝짓기 (`w_satp` ↔ `w_cr3`, `intr_on` ↔ `sti` …)
- `git diff 06aad25 v0.1-x86_64-c -- kernel/fs.c` : 정말 한 줄뿐인지
- `kernel/trampoline.S` 의 `uservec` 에서 `-8(%rsp)` … `-32(%rsp)` 가 trapframe 의 어느 필드인지 (위 `struct trapframe` 의 오프셋으로)
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/">튜토리얼 목록</a></span><span><a href="/xv6/tutorial/v0.2-x86_64-c/">v0.2-x86_64-c</a> →</span></div>
