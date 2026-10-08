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

<p class="subtitle">xv6-riscv on an x86-64 PC</p>

| | |
|---|---|
| **Previous tag** | MIT xv6-riscv commit `06aad25` (the `upstream` remote) |
| **This tag** | `v0.1-x86_64-c` (commit `daa09f5`, 2026-09-27), branch `main` |
| **In one line** | still C, but the machine changes from RISC-V (QEMU `virt`) to a 64-bit x86 PC (UEFI) |
| **Verified** | QEMU + OVMF (1 and 4 CPUs) and VirtualBox (EFI): the shell starts and all of `usertests` pass |

```sh
cd ~/Ryu/xv6-x86_64
git diff --stat 06aad25 v0.1-x86_64-c -- . ':!docs'
git checkout v0.1-x86_64-c && make clean && make qemu CPUS=2   # a shell; quit with Ctrl-a x
```

## 1. Before: xv6-riscv

MIT's original. It runs **only on QEMU's virtual machine `virt`** (why: see the [goal page](/xv6/goal/), in Korean).

- QEMU loads the kernel file at `0x80000000` with its `-kernel` option and starts every CPU (hart) together
- every device sits at a fixed address: UART `0x10000000`, virtio disk `0x10001000`, PLIC `0x0c000000`
- traps go through one register (`stvec`), system calls use `ecall`, page tables have 3 levels (Sv39), the CPU number lives in `tp`

These machine-dependent parts are almost all in `kernel/riscv.h` (417 lines), `trampoline.S`, `trap.c`, `start.c`, `plic.c` and `virtio_disk.c`.
**Processes, the file system and the system calls don't depend on the machine, so they could stay almost as they were.**

## 2. What changed

<!-- fig:map_v0_1_x86_64_c -->
<svg viewBox="0 0 1000 704" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="files changed from 06aad25 to v0.1-x86_64-c"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: 06aad25 → v0.1-x86_64-c  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">boot/loader.c</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="200.75804333491618" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="820.8" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+299</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/x86.h</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="191.75660307921757" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="811.8" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+272</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">boot/efi.h</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="108" width="161.251787448632" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="781.3" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+190</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/acpi.c</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="130" width="144.40388539201751" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="764.4" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+151</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/lapic.c</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="152" width="142.5584176784753" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="762.6" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+147</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/entryother.S</text><text x="570.0" y="185.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="174" width="127.82957786664727" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="747.8" y="185.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+117</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/ioapic.c</text><text x="570.0" y="207.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="196" width="106.74066237203265" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="726.7" y="207.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+80</text><rect x="305" y="217" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="229.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/ramdisk.c</text><text x="570.0" y="229.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="218" width="84.84203920677707" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="704.8" y="229.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+49</text><rect x="305" y="239" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="251.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/bootinfo.h</text><text x="570.0" y="251.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="240" width="68.71055659833439" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="688.7" y="251.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+31</text><rect x="305" y="261" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="273.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">vbox.sh</text><text x="570.0" y="273.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="262" width="64.52503614791799" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="684.5" y="273.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+27</text><rect x="305" y="283" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="295.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/trampoline.S</text><text x="570.0" y="295.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="166.65089065973993" y="284" width="128.34910934026007" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="161.7" y="295.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−118</text><rect x="615" y="284" width="129.3816095807386" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="749.4" y="295.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+120</text><rect x="305" y="305" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="317.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/trap.c</text><text x="570.0" y="317.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="182.7436699586283" y="306" width="112.2563300413717" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="177.7" y="317.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−89</text><rect x="615" y="306" width="142.5584176784753" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="762.6" y="317.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+147</text><rect x="305" y="327" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="339.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kernelvec.S</text><text x="570.0" y="339.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="210.96661846944266" y="328" width="84.03338153055732" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="206.0" y="339.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−48</text><rect x="615" y="328" width="106.10905324677897" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="726.1" y="339.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+79</text><rect x="305" y="349" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="361.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="361.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="200.31388035466992" y="350" width="94.68611964533008" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="195.3" y="361.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−62</text><rect x="615" y="350" width="94.68611964533008" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="714.7" y="361.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+62</text><rect x="305" y="371" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="383.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.h</text><text x="570.0" y="383.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="206.2331001412387" y="372" width="88.76689985876128" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="201.2" y="383.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−54</text><rect x="615" y="372" width="91.03490607861316" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="711.0" y="383.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+57</text><rect x="305" y="393" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="405.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/start.c</text><text x="570.0" y="405.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="212.60961050816258" y="394" width="82.39038949183744" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="207.6" y="405.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−46</text><rect x="615" y="394" width="67.6908047903693" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="687.7" y="405.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+30</text><rect x="305" y="415" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="427.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/vm.c</text><text x="570.0" y="427.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="232.68425770944495" y="416" width="62.31574229055506" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="227.7" y="427.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−25</text><rect x="615" y="416" width="79.85740360414981" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="699.9" y="427.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+43</text><rect x="305" y="437" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="449.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.c</text><text x="570.0" y="449.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="261.4110333804129" y="438" width="33.58896661958709" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="256.4" y="449.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−6</text><rect x="615" y="438" width="93.96800159465006" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="714.0" y="449.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="459" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="471.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/memlayout.h</text><text x="570.0" y="471.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="220.48894258581618" y="460" width="74.51105741418382" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="215.5" y="471.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−37</text><rect x="615" y="460" width="67.6908047903693" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="687.7" y="471.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+30</text><rect x="305" y="481" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="493.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/swtch.S</text><text x="570.0" y="493.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="225.28601078207117" y="482" width="69.71398921792883" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="220.3" y="493.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−32</text><rect x="615" y="482" width="58.82884903315484" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="678.8" y="493.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+22</text><rect x="305" y="503" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="515.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.c</text><text x="570.0" y="515.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="251.6443626063758" y="504" width="43.35563739362418" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="246.6" y="515.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−11</text><rect x="615" y="504" width="64.52503614791799" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="684.5" y="515.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+27</text><rect x="305" y="525" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="537.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">README</text><text x="570.0" y="537.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="526" width="70.7018619148769" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="690.7" y="537.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+33</text><rect x="305" y="547" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="559.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="559.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="253.38279724775563" y="548" width="41.617202752244374" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="248.4" y="559.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−10</text><rect x="615" y="548" width="55.09492591500185" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="675.1" y="559.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+19</text><rect x="305" y="569" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="581.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/exec.c</text><text x="570.0" y="581.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="255.210554625667" y="570" width="39.78944537433303" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="250.2" y="581.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−9</text><rect x="615" y="570" width="56.37033118601632" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="676.4" y="581.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+20</text><rect x="305" y="591" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="603.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kalloc.c</text><text x="570.0" y="603.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="273.0715026955178" y="592" width="21.928497304482207" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="268.1" y="603.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−2</text><rect x="615" y="592" width="58.82884903315484" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="678.8" y="603.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+22</text><rect x="305" y="613" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="625.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/syscall.c</text><text x="570.0" y="625.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="251.6443626063758" y="614" width="43.35563739362418" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="246.6" y="625.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−11</text><rect x="615" y="614" width="46.60985928888242" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="666.6" y="625.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+13</text><text x="320.0" y="647.0" font-size="11" fill="#566573" text-anchor="start">… 25 more files (changed 21, deleted 4): +71 −955</text><text x="500.0" y="680.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 51 files, +2219 −1515 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_v0_1_x86_64_c -->

| File | | Added | Removed |
|---|---|---:|---:|
| `.gitignore` | changed | 6 | 0 |
| `LICENSE` | changed | 13 | 0 |
| `Makefile` | changed | 62 | 62 |
| `README` | changed | 33 | 0 |
| `boot/efi.h` | new | 190 | 0 |
| `boot/loader.c` | new | 299 | 0 |
| `kernel/acpi.c` | new | 151 | 0 |
| `kernel/bio.c` | changed | 3 | 3 |
| `kernel/bootinfo.h` | new | 31 | 0 |
| `kernel/console.c` | changed | 1 | 1 |
| `kernel/defs.h` | changed | 19 | 10 |
| `kernel/entry.S` | changed | 10 | 13 |
| `kernel/entryother.S` | new | 117 | 0 |
| `kernel/exec.c` | changed | 20 | 9 |
| `kernel/file.c` | changed | 1 | 1 |
| `kernel/fs.c` | changed | 1 | 1 |
| `kernel/ioapic.c` | new | 80 | 0 |
| `kernel/kalloc.c` | changed | 22 | 2 |
| `kernel/kernel.ld` | changed | 11 | 11 |
| `kernel/kernelvec.S` | changed | 79 | 48 |
| `kernel/lapic.c` | new | 147 | 0 |
| `kernel/log.c` | changed | 1 | 1 |
| `kernel/main.c` | changed | 61 | 6 |
| `kernel/memlayout.h` | changed | 30 | 37 |
| `kernel/pipe.c` | changed | 1 | 1 |
| `kernel/plic.c` | deleted | 0 | 47 |
| `kernel/printk.c` | changed | 1 | 1 |
| `kernel/proc.c` | changed | 27 | 11 |
| `kernel/proc.h` | changed | 57 | 54 |
| `kernel/ramdisk.c` | new | 49 | 0 |
| `kernel/riscv.h` | deleted | 0 | 417 |
| `kernel/sleeplock.c` | changed | 1 | 1 |
| `kernel/spinlock.c` | changed | 3 | 3 |
| `kernel/start.c` | changed | 30 | 46 |
| `kernel/swtch.S` | changed | 22 | 32 |
| `kernel/syscall.c` | changed | 13 | 11 |
| `kernel/sysfile.c` | changed | 1 | 1 |
| `kernel/sysproc.c` | changed | 1 | 1 |
| `kernel/trampoline.S` | changed | 120 | 118 |
| `kernel/trap.c` | changed | 147 | 89 |
| `kernel/uart.c` | changed | 6 | 8 |
| `kernel/virtio.h` | deleted | 0 | 99 |
| `kernel/virtio_disk.c` | deleted | 0 | 333 |
| `kernel/vm.c` | changed | 43 | 25 |
| `kernel/x86.h` | new | 272 | 0 |
| `user/grind.c` | changed | 1 | 1 |
| `user/ulib.c` | changed | 1 | 1 |
| `user/user.ld` | changed | 2 | 7 |
| `user/usertests.c` | changed | 1 | 1 |
| `user/usys.pl` | changed | 5 | 2 |
| `vbox.sh` | new | 27 | 0 |
| **Total** (51 files) | | **2219** | **1515** |

Of the 51 files, files such as `fs.c`, `file.c`, `pipe.c`, `log.c` and `sysfile.c` changed only one line: `#include "riscv.h"` became `"x86.h"`.
The real changes are the seven below.

<!-- fig:regmap -->
<svg viewBox="0 0 1000 520" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="RISC-V and x86-64 register mapping"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Same job, different hardware: riscv.h ↔ x86.h (only what xv6 uses)</text><text x="160.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">what</text><text x="450.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">RISC-V (riscv.h)</text><text x="790.0" y="52.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">x86-64 (x86.h)</text><rect x="20" y="62" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle">page table base</text><rect x="310" y="62" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">satp  (w_satp)</text><line x1="592" y1="80" x2="618" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="62" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="84.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">CR3  (w_cr3)</text><rect x="20" y="102" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="124.0" font-size="11.0" fill="#4d5656" text-anchor="middle">trap handler address</text><rect x="310" y="102" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="124.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stvec  (w_stvec)</text><line x1="592" y1="120" x2="618" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="102" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">IDT  (lidt)</text><rect x="20" y="142" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="164.0" font-size="11.0" fill="#4d5656" text-anchor="middle">trap cause</text><rect x="310" y="142" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="164.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">scause  (r_scause)</text><line x1="592" y1="160" x2="618" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="142" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="164.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">vector number trapno (pushed by stub)</text><rect x="20" y="182" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="204.0" font-size="11.0" fill="#4d5656" text-anchor="middle">faulting address</text><rect x="310" y="182" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="204.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stval  (r_stval)</text><line x1="592" y1="200" x2="618" y2="200" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="182" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="204.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">CR2  (r_cr2)</text><rect x="20" y="222" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="244.0" font-size="11.0" fill="#4d5656" text-anchor="middle">where the trap happened</text><rect x="310" y="222" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="244.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sepc  (r_sepc)</text><line x1="592" y1="240" x2="618" y2="240" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="222" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="244.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rip in the trapframe (pushed by CPU)</text><rect x="20" y="262" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="284.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPU number</text><rect x="310" y="262" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="284.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">tp  (r_tp, w_tp)</text><line x1="592" y1="280" x2="618" y2="280" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="262" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="284.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">GS base MSR  (r_gsbase, wrmsr)</text><rect x="20" y="302" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle">interrupts on/off</text><rect x="310" y="302" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sstatus.SIE  (intr_on/off)</text><line x1="592" y1="320" x2="618" y2="320" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="302" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="324.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">RFLAGS.IF  (sti / cli)</text><rect x="20" y="342" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="364.0" font-size="11.0" fill="#4d5656" text-anchor="middle">system call instruction</text><rect x="310" y="342" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="364.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ecall</text><line x1="592" y1="360" x2="618" y2="360" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="342" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="364.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">int $64</text><rect x="20" y="382" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="404.0" font-size="11.0" fill="#4d5656" text-anchor="middle">return to user</text><rect x="310" y="382" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="404.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sret</text><line x1="592" y1="400" x2="618" y2="400" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="382" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="404.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">iretq</text><rect x="20" y="422" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="444.0" font-size="11.0" fill="#4d5656" text-anchor="middle">flush the TLB</text><rect x="310" y="422" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="444.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sfence.vma</text><line x1="592" y1="440" x2="618" y2="440" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="422" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="444.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rewrite CR3  (sfence_vma)</text><rect x="20" y="462" width="280" height="36" rx="3" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="160.0" y="484.0" font-size="11.0" fill="#4d5656" text-anchor="middle">timer</text><rect x="310" y="462" width="280" height="36" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="450.0" y="484.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">stimecmp</text><line x1="592" y1="480" x2="618" y2="480" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="620" y="462" width="360" height="36" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="800.0" y="484.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">LAPIC timer</text><text x="500.0" y="514.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Some RISC-V registers have no x86 counterpart: trap cause and location are pushed on the stack by the CPU and the stubs</text></svg>
<!-- /fig:regmap -->

### 2.1 Booting: the UEFI loader (`boot/loader.c`, new)

<!-- fig:boot -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="boot paths of RISC-V and x86-64"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Booting: who puts the kernel in memory and gets to main()</text><text x="20.0" y="58.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">xv6-riscv (QEMU virt)</text><rect x="20" y="70" width="190" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="115.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">QEMU</text><text x="115.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">-kernel loads the kernel</text><text x="115.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">at 0x80000000</text><rect x="250" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="345.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">entry.S</text><text x="345.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">machine mode</text><text x="345.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">a stack per CPU</text><rect x="480" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="575.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.c</text><text x="575.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">machine → supervisor</text><text x="575.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">(mret)</text><rect x="710" y="70" width="190" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="805.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">main.c</text><text x="805.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kinit, kvminit, …</text><text x="805.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">scheduler()</text><line x1="210" y1="105" x2="248" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="105" x2="478" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="670" y1="105" x2="708" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="20.0" y="178.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">xv6-x86_64 (UEFI PC)</text><rect x="20" y="190" width="150" height="110" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="95.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">UEFI firmware</text><text x="95.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">64-bit mode</text><text x="95.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">paging on</text><text x="95.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">memory = physical</text><rect x="200" y="190" width="230" height="110" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="315.0" y="217.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">boot/loader.c (new)</text><text x="315.0" y="233.0" font-size="11.0" fill="#4d5656" text-anchor="middle">reads kernel, fs.img</text><text x="315.0" y="249.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ACPI, screen, memory map</text><text x="315.0" y="265.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ExitBootServices</text><text x="315.0" y="281.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ _entry(bootinfo)</text><rect x="460" y="190" width="150" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="535.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">entry.S</text><text x="535.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">at 0x100000</text><text x="535.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">sets a stack</text><text x="535.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">calls start()</text><rect x="640" y="190" width="150" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="715.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">start.c</text><text x="715.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">copies bootinfo</text><text x="715.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">sets EFER.NXE</text><text x="715.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">GS base = 0</text><rect x="820" y="190" width="160" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="900.0" y="225.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">main.c</text><text x="900.0" y="241.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ acpiinit</text><text x="900.0" y="257.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ ioapic, lapic</text><text x="900.0" y="273.0" font-size="11.0" fill="#4d5656" text-anchor="middle">+ startothers</text><line x1="170" y1="245" x2="198" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="430" y1="245" x2="458" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="610" y1="245" x2="638" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="790" y1="245" x2="818" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="312" width="14" height="12" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="40.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">new</text><rect x="89" y="312" width="14" height="12" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="109.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">changed</text><rect x="210" y="312" width="14" height="12" rx="2" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="230.0" y="322.0" font-size="10.5" fill="#4d5656" text-anchor="start">deleted</text></svg>
<!-- /fig:boot -->

A PC has nothing like QEMU's `-kernel`. At power-on the **UEFI firmware** finds `EFI/BOOT/BOOTX64.EFI` on the USB stick and runs it.
That program (our loader) must read the kernel into memory and jump to it. The loader is built with clang and lld-link in the Windows format (PE/COFF), the only format UEFI runs.

The end of the loader: it collects what the kernel needs into `struct bootinfo`, leaves the firmware's services (`ExitBootServices`) and jumps to the kernel:

[`boot/loader.c:239–296`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/boot/loader.c#L239-L296) (tag `v0.1-x86_64-c`)

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

| `bootinfo` field | Why the kernel needs it | On RISC-V |
|---|---|---|
| `fsimg`, `fsimg_size` | the file system, in memory instead of on a disk (2.6) | virtio disk |
| `apboot` | a page below 1 MB where other CPUs start in 16-bit mode (2.5) | not needed |
| `rsdp` | start of the ACPI tables: CPUs and interrupt controllers (2.4) | fixed addresses, not needed |
| `fb_*` | the screen (unused in this tag; used from `v0.2`) | no screen |
| `memmap` | which RAM is free (2.2) | all of `0x80000000` … `PHYSTOP` |

The kernel's first code, `entry.S`, sets up a stack and calls `start()` as on RISC-V. The difference: the address of `bootinfo` is in `%rdi`:

[`kernel/entry.S:7–16`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/entry.S#L7-L16) (tag `v0.1-x86_64-c`)

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

On RISC-V, `start.c` drops from machine mode to supervisor mode. UEFI already hands over 64-bit mode, the highest privilege (ring 0) and paging, so little is left to do:

[`kernel/start.c:24–37`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/start.c#L24-L37) (tag `v0.1-x86_64-c`)

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

### 2.2 Memory

<!-- fig:memmap -->
<svg viewBox="0 0 1000 500" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="physical memory layout of the x86-64 version"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Physical memory (x86-64 version, QEMU with 512 MB)</text><rect x="140" y="60" width="260" height="34" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="270.0" y="81.0" font-size="11" fill="#4d5656" text-anchor="middle">LAPIC (per-CPU interrupt unit)</text><text x="134.0" y="98.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0xFEE00000</text><rect x="140" y="94" width="260" height="34" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="270.0" y="115.0" font-size="11" fill="#4d5656" text-anchor="middle">IOAPIC (device interrupts)</text><text x="134.0" y="132.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0xFEC00000</text><rect x="140" y="128" width="260" height="50" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="157.0" font-size="11" fill="#4d5656" text-anchor="middle">… (above PHYSTOP: unused)</text><text x="134.0" y="182.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">PHYSTOP = 128MB</text><rect x="140" y="178" width="260" height="110" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="237.0" font-size="11" fill="#4d5656" text-anchor="middle">free pages → kalloc()</text><rect x="140" y="288" width="260" height="40" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="270.0" y="312.0" font-size="11" fill="#4d5656" text-anchor="middle">fs.img (RAM disk), bootinfo</text><rect x="140" y="328" width="260" height="60" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="362.0" font-size="11" fill="#4d5656" text-anchor="middle">free pages → kalloc()</text><text x="134.0" y="392.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">end</text><rect x="140" y="388" width="260" height="50" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="417.0" font-size="11" fill="#4d5656" text-anchor="middle">kernel text, data, bss</text><text x="134.0" y="442.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00100000</text><rect x="140" y="438" width="260" height="40" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="462.0" font-size="11" fill="#4d5656" text-anchor="middle">low memory: firmware, AP start page</text><text x="134.0" y="482.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00000000</text><rect x="470" y="70" width="500" height="120" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="720.0" y="102.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">What changed in kinit()</text><text x="720.0" y="118.0" font-size="11.0" fill="#4d5656" text-anchor="middle">RISC-V: everything from end to PHYSTOP is free</text><text x="720.0" y="134.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86-64: only the &#x27;conventional&#x27; (free) regions of the</text><text x="720.0" y="150.0" font-size="11.0" fill="#4d5656" text-anchor="middle">UEFI memory map between end and PHYSTOP are freed</text><text x="720.0" y="166.0" font-size="11.0" fill="#4d5656" text-anchor="middle">a PC&#x27;s RAM has holes, and the firmware uses some of it</text><rect x="470" y="220" width="500" height="100" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="720.0" y="250.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Devices have no fixed addresses</text><text x="720.0" y="266.0" font-size="11.0" fill="#4d5656" text-anchor="middle">RISC-V virt: UART 0x10000000, PLIC 0x0c000000 (fixed)</text><text x="720.0" y="282.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86-64: LAPIC and IOAPIC addresses come from ACPI (MADT)</text><text x="720.0" y="298.0" font-size="11.0" fill="#4d5656" text-anchor="middle">the COM1 serial port is not memory but I/O port 0x3F8</text><rect x="470" y="350" width="500" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="720.0" y="378.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">No disk</text><text x="720.0" y="394.0" font-size="11.0" fill="#4d5656" text-anchor="middle">instead of a virtio disk (a virtual device), the loader puts</text><text x="720.0" y="410.0" font-size="11.0" fill="#4d5656" text-anchor="middle">fs.img in memory and ramdisk.c reads and writes it as a disk</text></svg>
<!-- /fig:memmap -->

`kinit()` frees only the free regions of the UEFI memory map:

[`kernel/kalloc.c:34–51`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/kalloc.c#L34-L51) (tag `v0.1-x86_64-c`)

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

Page tables have 4 levels (9 bits each, one more than RISC-V Sv39). `walk()`'s loop starts at `level = 3` instead of `level = 2` ([`kernel/vm.c:108`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/vm.c#L108)).
The PTE bit names stay RISC-V's: `PTE_R` and `PTE_X` survive as software bits, and no-execute becomes x86's `PTE_NX` (bit 63). That is why `start()` sets `EFER.NXE`.

<!-- fig:pagewalk -->
<svg viewBox="0 0 1000 420" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="page table levels compared"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Virtual → physical: Sv39 (3 levels) and x86-64 (4 levels)</text><text x="20.0" y="58.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">RISC-V Sv39</text><rect x="150" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="244.6" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L2 (9 bits)</text><text x="152.0" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">38</text><text x="337.2" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30</text><rect x="339.2307692307692" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="433.8" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L1 (9 bits)</text><text x="341.2" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">29</text><text x="526.5" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">21</text><rect x="528.4615384615385" y="66" width="189.23076923076923" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="623.1" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">L0 (9 bits)</text><text x="530.5" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">20</text><text x="715.7" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="717.6923076923076" y="66" width="252.30769230769232" height="34" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="843.8" y="87.0" font-size="10.5" fill="#4d5656" text-anchor="middle">page offset (12)</text><text x="719.7" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><text x="968.0" y="62.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="20.0" y="160.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="start">x86-64</text><rect x="150" y="168" width="153.75" height="34" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="226.9" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PML4 (L3)</text><text x="152.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">47</text><text x="301.8" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">39</text><rect x="303.75" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="380.6" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PDPT (L2)</text><text x="305.8" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">38</text><text x="455.5" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30</text><rect x="457.5" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="534.4" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PD (L1)</text><text x="459.5" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">29</text><text x="609.2" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">21</text><rect x="611.25" y="168" width="153.75" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="688.1" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PT (L0)</text><text x="613.2" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">20</text><text x="763.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="765.0" y="168" width="205.0" height="34" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="867.5" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">offset (12)</text><text x="767.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><text x="968.0" y="164.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="20" y="240" width="470" height="160" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="255.0" y="276.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">What changed in walk() (vm.c)</text><text x="255.0" y="292.0" font-size="11.0" fill="#4d5656" text-anchor="middle">for (level = 2 …)  →  for (level = 3 …)</text><text x="255.0" y="308.0" font-size="11.0" fill="#4d5656" text-anchor="middle">PX(level, va): 9 bits each, one more level</text><text x="255.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle"></text><text x="255.0" y="340.0" font-size="11.0" fill="#4d5656" text-anchor="middle">intermediate PTEs also get W | U:</text><text x="255.0" y="356.0" font-size="11.0" fill="#4d5656" text-anchor="middle">x86 checks W and U at every level,</text><text x="255.0" y="372.0" font-size="11.0" fill="#4d5656" text-anchor="middle">so only the leaf PTE decides</text><rect x="510" y="240" width="470" height="160" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="745.0" y="276.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">MAXVA stays at RISC-V&#x27;s 2³⁸</text><text x="745.0" y="292.0" font-size="11.0" fill="#4d5656" text-anchor="middle">to keep the user address layout unchanged,</text><text x="745.0" y="308.0" font-size="11.0" fill="#4d5656" text-anchor="middle">xv6 uses up to 2³⁸ instead of x86&#x27;s 2⁴⁷</text><text x="745.0" y="324.0" font-size="11.0" fill="#4d5656" text-anchor="middle"></text><text x="745.0" y="340.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ the top PML4 index is always 0</text><text x="745.0" y="356.0" font-size="11.0" fill="#4d5656" text-anchor="middle">  (virtual address bits 47:39 are 0)</text><text x="745.0" y="372.0" font-size="11.0" fill="#4d5656" text-anchor="middle">TRAMPOLINE = MAXVA − 4096</text></svg>
<!-- /fig:pagewalk -->

<!-- fig:ptebits -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="x86-64 PTE bits"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">x86-64 PTE (64 bits): the bits xv6 uses</text><rect x="60" y="60" width="65.85365853658537" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="92.9" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">NX</text><text x="92.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">63</text><rect x="125.85365853658537" y="60" width="109.75609756097562" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="180.7" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(unused)</text><text x="127.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">62</text><text x="233.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">52</text><rect x="235.609756097561" y="60" width="307.31707317073176" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="389.3" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">physical page number (PTE2PA)</text><text x="237.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">51</text><text x="540.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="542.9268292682927" y="60" width="21.951219512195124" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="553.9" y="86.0" font-size="9.5" fill="#4d5656" text-anchor="middle"></text><text x="553.9" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><rect x="564.8780487804879" y="60" width="43.90243902439025" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="586.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">X*</text><text x="586.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10</text><rect x="608.7804878048781" y="60" width="43.90243902439025" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="630.7" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">R*</text><text x="630.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">9</text><rect x="652.6829268292684" y="60" width="87.8048780487805" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="696.6" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(unused)</text><text x="654.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><text x="738.5" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="740.4878048780488" y="60" width="43.90243902439025" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="762.4" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PCD</text><text x="762.4" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="784.390243902439" y="60" width="43.90243902439025" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="806.3" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PWT</text><text x="806.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><rect x="828.2926829268292" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="850.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">U</text><text x="850.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="872.1951219512194" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="894.1" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">W</text><text x="894.1" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="916.0975609756097" y="60" width="43.90243902439025" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="938.0" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">P (V)</text><text x="938.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="60" y="140" width="430" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="275.0" y="165.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Hardware bits</text><text x="275.0" y="181.0" font-size="10.5" fill="#4d5656" text-anchor="middle">P = PTE_V (present), W writable, U user</text><text x="275.0" y="197.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PCD: cache disabled (LAPIC, IOAPIC mappings)</text><text x="275.0" y="213.0" font-size="10.5" fill="#4d5656" text-anchor="middle">NX (63): no execute → needs EFER.NXE</text><rect x="510" y="140" width="450" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="735.0" y="165.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">* software bits (ignored by the CPU)</text><text x="735.0" y="181.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PTE_R (9) and PTE_X (10) keep the RISC-V code&#x27;s</text><text x="735.0" y="197.0" font-size="10.5" fill="#4d5656" text-anchor="middle">permission arguments working. mappages()</text><text x="735.0" y="213.0" font-size="10.5" fill="#4d5656" text-anchor="middle">sets NX when PTE_X is absent</text></svg>
<!-- /fig:ptebits -->

<!-- fig:vmtop -->
<svg viewBox="0 0 1000 400" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="top of the address space"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The top of the address space: the x86-64 version adds a CPUTABLES page</text><text x="270.0" y="62.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xv6-riscv: user page table</text><rect x="120" y="70" width="300" height="40" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="94.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAMPOLINE (trampoline.S)</text><rect x="120" y="110" width="300" height="40" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="270.0" y="134.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAPFRAME (p-&gt;trapframe)</text><rect x="120" y="150" width="300" height="30" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="270.0" y="169.0" font-size="11" fill="#4d5656" text-anchor="middle">…</text><rect x="120" y="180" width="300" height="80" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="270.0" y="224.0" font-size="11" fill="#4d5656" text-anchor="middle">user memory (text, data, stack, heap)</text><text x="114.0" y="264.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="750.0" y="62.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xv6-x86_64: user page table</text><rect x="600" y="70" width="300" height="40" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="750.0" y="94.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAMPOLINE (trampoline.S)</text><rect x="600" y="110" width="300" height="40" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="750.0" y="134.0" font-size="11" fill="#4d5656" text-anchor="middle">CPUTABLES (IDT, GDT, TSS)</text><rect x="600" y="150" width="300" height="40" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="750.0" y="174.0" font-size="11" fill="#4d5656" text-anchor="middle">TRAPFRAME (p-&gt;trapframe)</text><rect x="600" y="190" width="300" height="30" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="750.0" y="209.0" font-size="11" fill="#4d5656" text-anchor="middle">…</text><rect x="600" y="220" width="300" height="80" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="750.0" y="264.0" font-size="11" fill="#4d5656" text-anchor="middle">user memory</text><text x="594.0" y="304.0" font-size="10" fill="#566573" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="120" y="336" width="780" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="510.0" y="357.0" font-size="10.5" fill="#4d5656" text-anchor="middle">On a trap the CPU reads the IDT, GDT and TSS. So that it can read them while a user page table is active,</text><text x="510.0" y="373.0" font-size="10.5" fill="#4d5656" text-anchor="middle">the page holding them is mapped at the same address (just below TRAMPOLINE) in every page table</text></svg>
<!-- /fig:vmtop -->

### 2.3 Traps and system calls (`trampoline.S`, `trap.c`, `kernelvec.S`, `x86.h`)

The biggest rewrite. On a trap an x86 CPU looks up the handler in the **IDT** (Interrupt Descriptor Table); coming from user mode it also switches to the stack in the **TSS**'s `rsp0` and pushes some registers onto it.

<!-- fig:trap -->
<svg viewBox="0 0 1000 450" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="system call path and trapframe"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">A system call from a user program: from int $64 to usertrap()</text><rect x="20" y="60" width="200" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="120.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">user program</text><text x="120.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">usys.S: rax = number</text><text x="120.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">int $64</text><rect x="270" y="60" width="220" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="380.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU (hardware)</text><text x="380.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">switches to the TSS.rsp0 stack,</text><text x="380.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">pushes ss, rsp, rflags, cs, rip</text><rect x="540" y="60" width="200" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="640.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">trampoline.S: uvec64</text><text x="640.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">pushes err (0)</text><text x="640.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">and trapno (64)</text><rect x="790" y="60" width="190" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="885.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uservec</text><text x="885.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle">pushes the 15</text><text x="885.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle">general registers, cld</text><line x1="220" y1="95" x2="268" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="490" y1="95" x2="538" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="740" y1="95" x2="788" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="790" y="170" width="190" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="885.0" y="187.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uservec (cont.)</text><text x="885.0" y="203.0" font-size="11.0" fill="#4d5656" text-anchor="middle">GS = cpu id</text><text x="885.0" y="219.0" font-size="11.0" fill="#4d5656" text-anchor="middle">cr3 = kernel page table</text><text x="885.0" y="235.0" font-size="11.0" fill="#4d5656" text-anchor="middle">rsp = kernel stack</text><text x="885.0" y="251.0" font-size="11.0" fill="#4d5656" text-anchor="middle">call usertrap</text><line x1="885" y1="130" x2="885" y2="168" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="540" y="170" width="200" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="640.0" y="195.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">usertrap() (trap.c)</text><text x="640.0" y="211.0" font-size="11.0" fill="#4d5656" text-anchor="middle">lidt(kidt): kernel IDT</text><text x="640.0" y="227.0" font-size="11.0" fill="#4d5656" text-anchor="middle">trapno == 64 → syscall()</text><text x="640.0" y="243.0" font-size="11.0" fill="#4d5656" text-anchor="middle">rip already after the int</text><line x1="790" y1="215" x2="742" y2="215" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="160.0" y="182.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">TRAPFRAME page (p-&gt;trapframe)</text><rect x="30" y="192" width="260" height="30" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="160.0" y="211.0" font-size="10.0" fill="#4d5656" text-anchor="middle">kernel_cr3, kernel_sp, kernel_trap, kernel_hartid</text><rect x="30" y="222" width="260" height="34" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="160.0" y="243.0" font-size="10.0" fill="#4d5656" text-anchor="middle">r15 … rax  (pushed by uservec)</text><rect x="30" y="256" width="260" height="26" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="160.0" y="273.0" font-size="10.0" fill="#4d5656" text-anchor="middle">trapno, err  (pushed by the vector stub)</text><rect x="30" y="282" width="260" height="34" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="160.0" y="303.0" font-size="10.0" fill="#4d5656" text-anchor="middle">rip, cs, rflags, rsp, ss  (pushed by the CPU)</text><text x="296.0" y="320.0" font-size="10.5" fill="#566573" text-anchor="start">← TSS.rsp0 = end of TRAPFRAME</text><text x="30.0" y="346.0" font-size="10.5" fill="#4d5656" text-anchor="start">addresses grow downward here; pushes fill it from the bottom up</text><rect x="20" y="360" width="960" height="70" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="383.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Compared with RISC-V</text><text x="500.0" y="399.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V: ecall → uservec (from stvec) finds TRAPFRAME through sscratch and stores each register (the CPU saves only sepc)</text><text x="500.0" y="415.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64: the CPU pushes part of the state itself, so pointing the stack (rsp0) at the end of TRAPFRAME fills it by pushes alone</text></svg>
<!-- /fig:trap -->

So `p->trapframe` changed shape. Note the order it is filled in (from the end) and the field offsets (`/* 0 */` …):

[`kernel/proc.h:53–80`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/proc.h#L53-L80) (tag `v0.1-x86_64-c`)

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

The start of `trampoline.S` is a set of **short per-vector entry points** made by a macro (`uvec0` … `uvec64`). x86 doesn't tell the handler which vector it came through, so each stub pushes its number:

[`kernel/trampoline.S:24–32`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/trampoline.S#L24-L32) (tag `v0.1-x86_64-c`)

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

There are **two IDTs**. Just as RISC-V switches `stvec` between `uservec` and `kernelvec`, `usertrap()` loads the kernel IDT and the return to user loads the user IDT (pointing into `trampoline.S`) with `lidt` ([`kernel/trap.c:129`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/trap.c#L129)).

System call arguments use the same registers as Linux (`rdi, rsi, rdx, r10, r8, r9`), the number goes in `rax`, and the instruction is `int $64`:

[`kernel/syscall.c:35–56`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/syscall.c#L35-L56) (tag `v0.1-x86_64-c`)

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

The context switch `swtch.S`: on RISC-V the return address is in `ra`; on x86-64 it is on the stack. So the return address on top of the stack is saved as `context.ra`, and the new context is entered with `jmp *ra`:

[`kernel/swtch.S:12–32`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/swtch.S#L12-L32) (tag `v0.1-x86_64-c`)

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
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="swtch"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Context switch swtch(old, new): on x86-64 the return address is on the stack</text><rect x="20" y="55" width="300" height="200" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="170.0" y="111.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">struct context</text><text x="170.0" y="127.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ra   ← return address on the stack</text><text x="170.0" y="143.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sp   ← rsp after returning</text><text x="170.0" y="159.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx</text><text x="170.0" y="175.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbp</text><text x="170.0" y="191.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">r12  r13  r14  r15</text><text x="170.0" y="207.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">(callee-saved, System V ABI)</text><rect x="360" y="55" width="280" height="90" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="500.0" y="80.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">save (old)</text><text x="500.0" y="96.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">movq (%rsp), %rax → old-&gt;ra</text><text x="500.0" y="112.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">leaq 8(%rsp) → old-&gt;sp</text><text x="500.0" y="128.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx, rbp, r12–r15</text><rect x="360" y="165" width="280" height="90" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="500.0" y="190.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">restore (new)</text><text x="500.0" y="206.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">new-&gt;sp → %rsp</text><text x="500.0" y="222.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">rbx, rbp, r12–r15</text><text x="500.0" y="238.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">jmp *new-&gt;ra</text><rect x="680" y="55" width="300" height="200" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="830.0" y="111.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Unlike RISC-V</text><text x="830.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V: the return address is in ra</text><text x="830.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ ret goes back</text><text x="830.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="830.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64: call pushes the return address</text><text x="830.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ swtch pops it into ra when saving,</text><text x="830.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle">  and &#x27;returns&#x27; with jmp when restoring</text></svg>
<!-- /fig:swtch -->

### 2.4 Interrupt controllers (`acpi.c`, `lapic.c`, `ioapic.c` new; `plic.c` deleted)

<!-- fig:acpi -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="finding LAPIC and IOAPIC through ACPI"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Finding the interrupt controllers: following the ACPI tables (acpi.c)</text><rect x="20" y="70" width="160" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="100.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">RSDP</text><text x="100.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">the loader gets it</text><text x="100.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">from UEFI → bootinfo</text><rect x="230" y="70" width="160" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="310.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">XSDT</text><text x="310.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">list of all</text><text x="310.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">table addresses</text><rect x="440" y="70" width="200" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="540.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">MADT (&quot;APIC&quot;)</text><text x="540.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">CPUs and</text><text x="540.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">interrupt controllers</text><line x1="180" y1="105" x2="228" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="390" y1="105" x2="438" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="700" y="40" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="66.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">LAPIC entries → apicids[] (CPU list)</text><rect x="700" y="92" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="118.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">IOAPIC entry → ioapicaddr</text><rect x="700" y="144" width="280" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="840.0" y="170.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">ISO entries → IRQ overrides (ISA → GSI)</text><line x1="640" y1="105" x2="698" y2="62" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="640" y1="105" x2="698" y2="114" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="640" y1="105" x2="698" y2="166" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="200" width="960" height="80" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="228.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Compared with RISC-V</text><text x="500.0" y="244.0" font-size="10.5" fill="#4d5656" text-anchor="middle">RISC-V virt: the PLIC (device interrupts) and CLINT (timer) sit at fixed addresses, so constants in memlayout.h suffice</text><text x="500.0" y="260.0" font-size="10.5" fill="#4d5656" text-anchor="middle">x86-64: addresses and CPU counts differ per machine. lapic.c and ioapic.c come from the old x86 xv6 (xv6-public), made 64-bit</text></svg>
<!-- /fig:acpi -->

[`kernel/acpi.c:91–131`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/acpi.c#L91-L131) (tag `v0.1-x86_64-c`)

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

The timer is each CPU's LAPIC timer instead of RISC-V's `stimecmp`; serial port interrupts come through the IOAPIC.

### 2.5 Starting the other CPUs (`entryother.S` new, `main.c`)

<!-- fig:ap -->
<svg viewBox="0 0 1000 320" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="AP start-up sequence"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Starting the other CPUs (startothers, entryother.S)</text><rect x="15" y="70" width="150" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="90.0" y="100.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">BSP: main.c</text><text x="90.0" y="116.0" font-size="10.5" fill="#4d5656" text-anchor="middle">copies entryother to</text><text x="90.0" y="132.0" font-size="10.5" fill="#4d5656" text-anchor="middle">a page below 1 MB,</text><text x="90.0" y="148.0" font-size="10.5" fill="#4d5656" text-anchor="middle">fills stack, cr3, entry</text><rect x="180" y="70" width="150" height="100" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="255.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">lapicstartap()</text><text x="255.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">INIT, SIPI signals</text><text x="255.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(LAPIC commands)</text><line x1="165" y1="120" x2="179" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="345" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="420.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP: 16-bit</text><text x="420.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">starts in real mode</text><text x="420.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">loads a GDT</text><line x1="330" y1="120" x2="344" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="510" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="585.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP: 32-bit</text><text x="585.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">protected mode</text><text x="585.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PAE, EFER.LME</text><line x1="495" y1="120" x2="509" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="675" y="70" width="150" height="100" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="750.0" y="108.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">AP: 64-bit</text><text x="750.0" y="124.0" font-size="10.5" fill="#4d5656" text-anchor="middle">long mode</text><text x="750.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">kernel cr3, stack</text><line x1="660" y1="120" x2="674" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="840" y="70" width="150" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="915.0" y="100.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">mpenter()</text><text x="915.0" y="116.0" font-size="10.5" fill="#4d5656" text-anchor="middle">GS = id</text><text x="915.0" y="132.0" font-size="10.5" fill="#4d5656" text-anchor="middle">apstarted = 1</text><text x="915.0" y="148.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ main()</text><line x1="825" y1="120" x2="839" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="205" width="970" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="230.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Why so much work</text><text x="500.0" y="246.0" font-size="10.5" fill="#4d5656" text-anchor="middle">An x86 CPU wakes up in 16-bit real mode, like a 1978 8086 (only the first CPU, started by UEFI, is already 64-bit).</text><text x="500.0" y="262.0" font-size="10.5" fill="#4d5656" text-anchor="middle">So the other CPUs start in code below 1 MB and climb to 32-bit and then 64-bit mode themselves.</text><text x="500.0" y="278.0" font-size="10.5" fill="#4d5656" text-anchor="middle">On RISC-V virt every hart starts together in the same kernel code</text></svg>
<!-- /fig:ap -->

[`kernel/main.c:57–100`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/main.c#L57-L100) (tag `v0.1-x86_64-c`)

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

The CPU number lives in the **GS base** register (an MSR) instead of RISC-V's `tp`: `w_gsbase(id)`. `uservec` restores it on every entry from user space (`kernel_hartid`).

### 2.6 A RAM disk instead of a disk (`ramdisk.c` new, `virtio_disk.c` deleted)

Real PC disk controllers (AHCI, NVMe) need big drivers. The loader has already put `fs.img` in memory, so "reading the disk" is just a memory copy:

[`kernel/ramdisk.c:39–49`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/ramdisk.c#L39-L49) (tag `v0.1-x86_64-c`)

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

In `bio.c`, `virtio_disk_rw(b, 0)` became `ramdisk_rw(b, 0)`, and that's all. The catch: **whatever is written is lost at power-off**.

### 2.7 The user side (`usys.pl`, `exec.c`, `user.ld`)

- `usys.pl`: system call stubs become `mov $N, %rax; mov %rcx, %r10; int $64` instead of `li a7, N; ecall` (the fourth argument moves to `r10`, as on Linux)
- `exec.c`: `main(argc, argv)`'s arguments go in `rdi` and `rsi`; a fake return address 0 is pushed on the stack (x86-64 functions expect a return address on the stack at entry). And:

[`kernel/exec.c:146–148`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/exec.c#L146-L148) (tag `v0.1-x86_64-c`)

```cpp
  p->trapframe->rip = elf.entry; // initial program counter = ulib.c:start()
  p->trapframe->rsp = sp;        // initial stack pointer
  p->trapframe->rflags = FL_IF;  // no leftover flags, e.g. single-step
```

### 2.8 Bugs found while porting (all x86 traps RISC-V doesn't have)

| Symptom | Cause | Fix |
|---|---|---|
| user programs trap after every instruction | garbage from `kalloc` (`0x05` bytes) left the TF (single-step) bit set in `rflags` | `exec.c`: set `rflags = FL_IF` |
| the kernel's string instructions can run backwards | a direction flag (DF) set by a user program survives the trap into the kernel (kernel C code assumes DF = 0) | `cld` in `uservec` |
| an idle CPU sleeps forever | interrupts were off before `hlt` | `sti; hlt` in `scheduler()` ([`kernel/proc.c:483`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/v0.1-x86_64-c/kernel/proc.c#L483)) |
| other CPUs run without caches (very slow) | a CPU woken by INIT starts with CR0's cache-disable bits (CD, NW) set | cleared in `entryother.S` |

## 3. After

Booting with `make qemu CPUS=2` (QEMU + OVMF firmware, 2 CPUs) gives, after the loader's two lines, **the same** output as RISC-V xv6 (a real run):

```
xv6 loader
starting kernel

xv6 kernel is booting

hart 1 starting
init: starting sh
$
```

- input and output are **the serial port (COM1) only**. In QEMU the terminal is the serial port, which is convenient; VirtualBox shows a black window, and the shell needs `socat` on the serial socket (`vbox.sh`'s headless mode)
- all of `usertests` pass: QEMU with 1 and 4 CPUs, VirtualBox EFI with 2 CPUs
- not tried on a real PC. Today's PCs mostly have no serial port, so nothing would be visible → next tag

<div class="check" markdown="1">
**Check against the code**

- `git show 06aad25:kernel/riscv.h` and `kernel/x86.h`: pair up the functions that do the same job (see the first diagram)
- `git diff 06aad25 v0.1-x86_64-c -- kernel/fs.c`: really just one line?
- in `uservec` of `kernel/trampoline.S`, which trapframe fields are `-8(%rsp)` … `-32(%rsp)`? (use the offsets in `struct trapframe` above)
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/">Tutorial</a></span><span><a href="/xv6/tutorial/v0.2-x86_64-c/">v0.2-x86_64-c</a> →</span></div>
