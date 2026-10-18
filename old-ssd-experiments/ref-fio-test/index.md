---
layout: default
title: "Ref: fio test"
permalink: /old-ssd-experiments/ref-fio-test/
---
<style>
.glance { display:grid; grid-template-columns: 9rem 1fr; gap:4px 14px; background:#f4f8f6; border:1px solid #cfe3db; border-left:4px solid #1f6f5c; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.glance b { color:#1f6f5c; }
.warn { background:#fdf2f0; border-left:4px solid #c0392b; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.result { background:#fffbea; border:1px dashed #b7950b; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2.5rem 0 0; font-size:0.95rem; }
table.t { table-layout:fixed !important; width:100% !important; border-collapse:collapse; font-size:0.86rem; margin:1rem 0; }
table.t th { background:#e8f3ef !important; color:#1f3d34 !important; text-align:left; padding:6px 8px; border:1px solid #cfe3db; overflow-wrap:break-word; word-break:break-word; }
table.t td { padding:6px 8px; border:1px solid #e5e8e8; vertical-align:top; overflow-wrap:break-word; word-break:break-word; }
table.t code { font-size:0.82rem; }
@media (max-width: 640px) { .glance { grid-template-columns: 1fr; } }
</style>

# Ref: fio test : 옵션 하나씩 바꿔 보기 (NVMe 990 EVO)

<div class="glance">
<b>목표</b><span>fio 의 옵션이 결과를 어떻게 바꾸는지, <b>한 번에 옵션 하나만</b> 바꿔 가며 실제로 잰다. <a href="/old-ssd-experiments/fio/">fio 사용법</a> 의 참고 자료</span>
<b>장치</b><span>Samsung SSD 990 EVO 2TB (펌웨어 <code>0B2QKXJ7</code>), PCIe 4.0 × 4 (16 GT/s), DRAM 없이 HMB (PC 의 RAM 일부를 매핑 표에 빌려 씀)</span>
<b>대상</b><span>시스템 디스크의 ext4 위 4 GiB 파일 (장치에 직접 쓰지 않았다). CPU Intel Core i5-14600K, Linux 6.14, fio-3.36 (소스 빌드 : <code>libaio</code> 는 없다)</span>
<b>날짜</b><span>2026.10.18 12:37 – 12:55. 실행 59번, 하나에 약 15초</span>
<b>결과</b><span><code>~/Ryu/old_ssd_results/20261018-nvme-fio-sweep/</code> : 실행마다 JSON, 모두 모은 <code>results.csv</code>. 스크립트 : <code>scripts/fiosweep.py</code>, <code>scripts/sweepplot.py</code></span>
</div>

## 방법

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="방법"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">방법 : 기준 하나에서 옵션을 딱 하나만 바꾼다</text><rect x="20" y="50" width="220" height="200" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="130.0" y="98.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">기준 (baseline)</text><text x="130.0" y="114.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--rw=randread</text><text x="130.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--bs=4k</text><text x="130.0" y="146.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--iodepth=32</text><text x="130.0" y="162.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--ioengine=io_uring</text><text x="130.0" y="178.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--direct=1 --size=4G</text><text x="130.0" y="194.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--numjobs=1</text><text x="130.0" y="210.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--runtime=10</text><rect x="290" y="50" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="66.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--rw</text><text x="452.0" y="67.0" font-size="11.5" fill="#4d5656" text-anchor="start">randread, read, randwrite, write, randrw, rw</text><line x1="240" y1="150" x2="288" y2="62" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="79" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="95.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--bs</text><text x="452.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="start">512, 4k, 16k, 64k, 128k, 1m</text><line x1="240" y1="150" x2="288" y2="91" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="108" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="124.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--iodepth</text><text x="452.0" y="125.0" font-size="11.5" fill="#4d5656" text-anchor="start">1, 2, 4, 8, 16, 32, 64, 128, 256</text><line x1="240" y1="150" x2="288" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="137" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="153.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--numjobs</text><text x="452.0" y="154.0" font-size="11.5" fill="#4d5656" text-anchor="start">1, 2, 4, 8, 16</text><line x1="240" y1="150" x2="288" y2="149" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="166" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="182.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--ioengine</text><text x="452.0" y="183.0" font-size="11.5" fill="#4d5656" text-anchor="start">io_uring, psync, sync, pvsync2, posixaio, mmap</text><line x1="240" y1="150" x2="288" y2="178" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="195" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="211.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">--direct / --size</text><text x="452.0" y="212.0" font-size="11.5" fill="#4d5656" text-anchor="start">0 / 1,  16M – 4G</text><line x1="240" y1="150" x2="288" y2="207" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="224" width="150" height="24" rx="4" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="365.0" y="240.0" font-size="11.5" fill="#4d5656" text-anchor="middle">그 밖</text><text x="452.0" y="241.0" font-size="11.5" fill="#4d5656" text-anchor="start">--thread, 분포 (zipf, pareto), io_uring 옵션</text><line x1="240" y1="150" x2="288" y2="236" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="280.0" font-size="11.5" fill="#566573" text-anchor="middle">쓰기에만 있는 옵션 (--fsync, 쓰기의 --bs · --direct) 은 rw=randwrite 인 쓰기 기준에서 하나만 바꾼다</text></svg>

- **기준** : `--rw=randread --bs=4k --iodepth=32 --ioengine=io_uring --direct=1 --size=4G --numjobs=1 --runtime=10 --ramp_time=2 --time_based --group_reporting`
- 실행마다 **옵션 하나만** 기준과 다르다. 쓰기에만 뜻이 있는 옵션은 `--rw=randwrite` 인 **쓰기 기준** 에서 하나만 바꾼다.
- 그림마다 왼쪽 = 처리량 (IOPS, 블록 크기 그림은 MB/s), 오른쪽 = I/O 하나의 지연 (평균 `lat` 과 99% `clat`, **로그 눈금**). 읽기와 쓰기가 섞인 실행은 처리량을 읽기 (파랑) · 쓰기 (주황) 로 쌓고, 지연은 읽기 쪽을 보인다.
- 수가 있는 옵션 (`bs`, `iodepth`, `numjobs`, `size`) 은 선으로, 이름뿐인 옵션 (`rw`, `ioengine` …) 은 막대와 점으로 그렸다.

<div class="warn" markdown="1">
**같은 명령이 같은 숫자를 내지 않는다.** 기준을 맨 처음에 세 번 돌렸을 때는 **474k · 474k · 479k IOPS** 였는데, 같은 설정이 뒤쪽 그룹들에서는 **395k – 405k**, 모두 끝난 뒤 다시 하니 **375k · 377k** 였다. 그 사이에 같은 파일에 약 40 GB 를 썼고 (`rw` 그룹과 쓰기 그룹), 드라이브 온도가 약 60 °C 까지 올랐다. 랜덤 쓰기 뒤에는 파일의 데이터가 NAND 곳곳에 흩어지고, 매핑 표 조각도 늘어난다 (HMB 드라이브는 매핑을 PC 의 RAM 에서 빌려 쓴다). 어느 것이 원인인지 이 측정으로는 가를 수 없다.
그래서 **비교는 한 그룹 안에서만** 한다 : 한 그룹의 실행들은 이어서 돌았다. 그룹 사이의 절대 숫자는 비교하지 않는다. 숫자를 낼 때는 **드라이브의 상태 (얼마나 찼고, 무엇을 썼고, 몇 도인지) 도 함께 적는다.**
</div>

## `--rw` : I/O 의 모양

![--rw](/old-ssd-experiments/ref-fio-test/rw.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>값</th>
<th>IOPS</th>
<th>MB/s</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td><code>randread</code></td><td>473k</td><td>1,938</td><td>67 µs</td><td>127 µs</td></tr>
<tr><td><code>read</code></td><td><strong>543k</strong></td><td><strong>2,225</strong></td><td>59 µs</td><td>67 µs</td></tr>
<tr><td><code>randwrite</code></td><td>320k</td><td>1,312</td><td>100 µs</td><td>326 µs</td></tr>
<tr><td><code>write</code></td><td>365k</td><td>1,496</td><td>87 µs</td><td>189 µs</td></tr>
<tr><td><code>randrw</code> (읽기 50 : 쓰기 50)</td><td>132k + 132k</td><td>1,082</td><td>204 µs (읽기)</td><td>1,532 µs (읽기)</td></tr>
<tr><td><code>rw</code> (순차, 50 : 50)</td><td>58k + 58k</td><td>475</td><td>387 µs (읽기)</td><td>1,876 µs (읽기)</td></tr>
</tbody></table></div>

- 순차가 랜덤보다 빠르다 (읽기 +15%, 쓰기 +14%). NVMe 에서는 차이가 작다 : 디스크와 달리 머리가 움직이지 않는다. 차이는 미리 읽기 · 같은 페이지 안의 읽기 같은 컨트롤러 쪽 이득이다.
- 쓰기는 읽기보다 지연의 **꼬리** 가 길다 (99% 326 µs) : NAND 프로그램은 읽기보다 느리고, 가끔 SLC 버퍼 정리 · GC 가 끼어든다.
- **섞으면 둘 다 나빠진다** : `randrw` 의 읽기 99% 지연은 1.5 ms 로, 읽기만 할 때의 12배다. 읽기가 쓰기 (프로그램) 뒤에서 기다린다 ([실험 13](/old-ssd-experiments/13-interference/) 이 120GB SSD 에서 이것을 잰다).
- `rw` (순차로 섞기) 는 `randrw` 보다도 느렸다 : 읽기와 쓰기가 같은 위치를 바로 이어서 지나가므로, 방금 쓴 곳을 곧바로 읽는 경우가 많다. 이 결과만으로 이유를 단정하지는 않는다.

## `--bs` : I/O 하나의 크기

![--bs](/old-ssd-experiments/ref-fio-test/bs.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>bs</code></th>
<th>IOPS</th>
<th>MB/s</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td>512 B</td><td>408k</td><td>209</td><td>78 µs</td><td>268 µs</td></tr>
<tr><td>4 KiB</td><td>402k</td><td>1,646</td><td>79 µs</td><td>261 µs</td></tr>
<tr><td>16 KiB</td><td>139k</td><td><strong>2,277</strong></td><td>230 µs</td><td>668 µs</td></tr>
<tr><td>64 KiB</td><td>29k</td><td>1,911</td><td>1.1 ms</td><td>1.5 ms</td></tr>
<tr><td>128 KiB</td><td>15k</td><td>1,929</td><td>2.2 ms</td><td>2.9 ms</td></tr>
<tr><td>1 MiB</td><td>1.7k</td><td>1,832</td><td>18 ms</td><td>28 ms</td></tr>
</tbody></table></div>

- **512 B 와 4 KiB 의 IOPS 가 같다** (408k / 402k) : 드라이브는 4 KiB 단위로 일한다. 512 B 를 읽어도 일은 4 KiB 만큼 하니, MB/s 만 8분의 1이 된다 ([실험 6](/old-ssd-experiments/6-write-size/) 이 120GB SSD 의 쓰기에서 이것을 본다).
- **16 KiB 부터 MB/s 가 천장 (약 1.9 – 2.3 GB/s) 에 닿는다.** 그 뒤로는 블록이 커질수록 IOPS 는 줄고 지연은 크기에 비례해 늘 뿐이다. 이 장치 · 이 설정 (큐 깊이 32 랜덤 읽기) 의 대역 한계다.
- 숫자를 말할 때 IOPS 와 MB/s 는 늘 블록 크기와 함께 말해야 하는 이유다 : `400k IOPS` 는 512 B 면 0.2 GB/s, 4 KiB 면 1.6 GB/s 다.

## `--iodepth` : 동시에 걸어 둔 요청 수

![--iodepth](/old-ssd-experiments/ref-fio-test/iodepth.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>iodepth</code></th>
<th>IOPS</th>
<th>평균 지연</th>
<th>99% 지연</th>
<th>깊이 ÷ 지연 (Little)</th>
</tr></thead><tbody>
<tr><td>1</td><td>13.5k</td><td>73 µs</td><td>112 µs</td><td>13.7k</td></tr>
<tr><td>2</td><td>25.3k</td><td>78 µs</td><td>118 µs</td><td>25.6k</td></tr>
<tr><td>4</td><td>58.3k</td><td>68 µs</td><td>122 µs</td><td>58.8k</td></tr>
<tr><td>8</td><td>127k</td><td>63 µs</td><td>134 µs</td><td>127k</td></tr>
<tr><td>16</td><td>246k</td><td>65 µs</td><td>163 µs</td><td>246k</td></tr>
<tr><td>32</td><td>396k</td><td>81 µs</td><td>268 µs</td><td>395k</td></tr>
<tr><td>64</td><td><strong>478k</strong></td><td>134 µs</td><td>569 µs</td><td>478k</td></tr>
<tr><td>128</td><td>474k</td><td>270 µs</td><td>733 µs</td><td>474k</td></tr>
<tr><td>256</td><td>480k</td><td>533 µs</td><td>1,057 µs</td><td>481k</td></tr>
</tbody></table></div>

- **16 까지는 지연이 그대로이고 IOPS 가 깊이에 비례한다** : 드라이브 안에 노는 칩이 있다.
- **64 에서 천장 (약 480k)** : 그 뒤로는 IOPS 가 늘지 않고 **지연이 깊이에 비례해 는다** (128 → 270 µs, 256 → 533 µs). 더 걸어 둔 요청은 줄을 서서 기다릴 뿐이다.
- 마지막 열 '깊이 ÷ 평균 지연' 이 측정한 IOPS 와 모든 줄에서 맞는다 : [fio 사용법 5절](/old-ssd-experiments/fio/) 의 Little 의 법칙.
- 좋은 설정 = 천장 바로 앞 (여기서는 32 – 64) : 처리량은 거의 다 얻고, 지연은 아직 짧다.

## `--numjobs` : 같은 job 의 복사본 수

![--numjobs](/old-ssd-experiments/ref-fio-test/numjobs.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>numjobs</code></th>
<th>IOPS (합계)</th>
<th>평균 지연</th>
<th>99% 지연</th>
<th>걸린 요청 (job × 32)</th>
</tr></thead><tbody>
<tr><td>1</td><td>399k</td><td>80 µs</td><td>268 µs</td><td>32</td></tr>
<tr><td>2</td><td>496k</td><td>129 µs</td><td>627 µs</td><td>64</td></tr>
<tr><td>4</td><td>501k</td><td>255 µs</td><td>782 µs</td><td>128</td></tr>
<tr><td>8</td><td>505k</td><td>507 µs</td><td>1,188 µs</td><td>256</td></tr>
<tr><td>16</td><td>506k</td><td>1,011 µs</td><td>3,031 µs</td><td>512</td></tr>
</tbody></table></div>

- job 마다 큐 깊이 32 이므로, job 2개 = 걸린 요청 64 : `iodepth` 64 와 같은 자리 (천장) 에 닿는다. 그 뒤는 `iodepth` 를 늘릴 때와 똑같이 지연만 는다.
- 천장이 `iodepth` 그룹 (약 480k) 보다 조금 높다 (약 505k) : 프로세스가 여럿이면 CPU 코어 여럿이 요청을 넘기고 받는다. job 하나가 CPU 를 많이 쓰고 있었다 (`sys` 63%).

## `--ioengine` : 요청을 넘기는 방법

![--ioengine](/old-ssd-experiments/ref-fio-test/ioengine.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>엔진</th>
<th>IOPS</th>
<th>평균 지연</th>
<th>실제 걸린 깊이</th>
<th>읽는 법</th>
</tr></thead><tbody>
<tr><td><code>io_uring</code></td><td><strong>403k</strong></td><td>79 µs</td><td>32</td><td>비동기 : 32개를 걸어 둔다</td></tr>
<tr><td><code>psync</code></td><td>13.5k</td><td>73 µs</td><td>1</td><td>동기 : <code>iodepth=32</code> 가 1 로 깎인다</td></tr>
<tr><td><code>sync</code></td><td>13.2k</td><td>75 µs</td><td>1</td><td>동기</td></tr>
<tr><td><code>pvsync2</code></td><td>13.4k</td><td>74 µs</td><td>1</td><td>동기 (<code>preadv2</code>)</td></tr>
<tr><td><code>posixaio</code></td><td>13.2k</td><td><strong>2,411 µs</strong></td><td>16 (fio 가 본 것)</td><td>glibc 가 흉내 내는 비동기 : 요청은 많이 걸어 두지만 실제로는 하나씩 처리되어 기다리는 시간만 길어진다</td></tr>
<tr><td><code>mmap</code></td><td>11.8k</td><td>84 µs</td><td>1</td><td>파일을 메모리처럼 : 페이지 폴트마다 하나씩</td></tr>
</tbody></table></div>

- **비동기 엔진만 `iodepth` 를 쓸 수 있다** : 같은 명령에서 `io_uring` 은 30배.
- `posixaio` 는 IOPS 가 동기 엔진과 같은데 지연이 33배다 : Little 의 법칙대로 (요청 32 ÷ 2.4 ms ≈ 13k), 기다리는 줄만 길어진 것이다. 겉모습만 비동기인 엔진의 함정.
- 이 fio 빌드에는 `libaio` 가 없어 뺐다. `libaio` 는 `io_uring` 과 같은 무리다 (120GB SSD 의 `lab.sh` 가 쓴다).

## `--direct` : 페이지 캐시를 건너뛰나

![--direct](/old-ssd-experiments/ref-fio-test/direct.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>direct</code></th>
<th>IOPS</th>
<th>평균 지연</th>
<th>CPU (usr / sys)</th>
</tr></thead><tbody>
<tr><td>1</td><td>400k</td><td>80 µs</td><td>18% / 60%</td></tr>
<tr><td>0</td><td>334k</td><td>95 µs</td><td>12% / <strong>85%</strong></td></tr>
</tbody></table></div>

- 이 파일 (4 GiB) 은 RAM 보다 작은데도 버퍼 읽기가 **더 느렸다** : 10초 동안의 랜덤 읽기는 대부분 처음 읽는 블록이라 캐시에 없고, 캐시를 거치는 일 (페이지 할당, 복사) 만 더해졌다 (`sys` 85%). `io_uring` 의 버퍼 읽기는 커널의 도우미 스레드를 거치는 것도 이유다.
- 읽기에서도 쓰기에서도 `--direct=0` 의 숫자는 '장치' 가 아니다. 쓰기 쪽은 아래 `wdirect` 와 [fio 사용법 6절](/old-ssd-experiments/fio/) 을 본다.

## `--size` : 읽는 범위의 크기

![--size](/old-ssd-experiments/ref-fio-test/size.png)

16 MiB · 256 MiB · 1 GiB · 4 GiB 가 모두 **395k – 405k** 로 같다. `--direct=1` 이므로 PC 의 캐시는 없고, 드라이브 쪽에도 범위가 작다고 빨라지는 캐시가 보이지 않는다. 디스크 (HDD) 라면 범위가 작을수록 머리가 덜 움직여 빨라진다 : SSD 와 HDD 가 다른 점.

## `--random_distribution` : 어디를 고르나

![--random_distribution](/old-ssd-experiments/ref-fio-test/random_distribution.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>분포</th>
<th>IOPS</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td><code>random</code> (고르게)</td><td>398k</td><td>80 µs</td><td>268 µs</td></tr>
<tr><td><code>zipf:1.2</code> (몇 곳에 몰림)</td><td><strong>534k</strong></td><td>60 µs</td><td><strong>149 µs</strong></td></tr>
<tr><td><code>pareto:0.9</code></td><td>398k</td><td>80 µs</td><td>264 µs</td></tr>
</tbody></table></div>

- **`zipf:1.2` 가 34% 빠르고 꼬리가 절반** : 같은 몇몇 블록을 되풀이해 읽으면 빨라진다. 이 드라이브는 DRAM 이 없고 매핑 표를 HMB (PC 의 RAM 조금) 와 컨트롤러 안의 작은 메모리에 캐시한다. 몰린 읽기는 매핑을 캐시에서 찾고, 고른 읽기는 4 GiB 전체의 매핑을 오가야 한다. 그럴듯한 설명이지만 이 측정이 증명하지는 않는다.
- `pareto:0.9` 는 고른 분포와 차이가 없었다 : 이 값에서는 몰림이 약하다.
- 실제 작업 (데이터베이스, 파일 시스템의 메타데이터) 은 고른 분포보다 몰린 쪽에 가깝다. 고른 랜덤 읽기 벤치마크가 실제보다 나쁘게 보일 수 있는 이유다 ([실험 11](/old-ssd-experiments/11-hot-cold/) 은 쓰기에서 같은 것을 본다).

## `--thread` : 프로세스 대신 스레드

![--thread](/old-ssd-experiments/ref-fio-test/thread.png)

398k (프로세스) 와 394k (스레드) : 차이 없음. job 이 하나일 때 프로세스냐 스레드냐는 I/O 에 영향이 없다. job 이 아주 많을 때 메모리 · 시작 비용에서만 다르다.

## io_uring 의 추가 옵션

![io_uring options](/old-ssd-experiments/ref-fio-test/io_uring_opt.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>IOPS</th>
<th>slat</th>
<th>CPU (usr / sys)</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td>(없음)</td><td>398k</td><td>1.4 µs</td><td>19% / 61%</td><td>기준</td></tr>
<tr><td><code>--fixedbufs</code></td><td>400k</td><td>1.2 µs</td><td>19% / 57%</td><td>버퍼를 미리 등록 : 요청마다 페이지를 고정하지 않는다</td></tr>
<tr><td><code>--registerfiles</code></td><td>398k</td><td>1.5 µs</td><td>20% / 63%</td><td>파일을 미리 등록</td></tr>
<tr><td><code>--sqthread_poll</code></td><td>405k</td><td><strong>0</strong></td><td><strong>100% / 0%</strong></td><td>커널 스레드가 제출 큐를 계속 지켜본다 : 시스템 호출 없이 넘긴다. 대신 CPU 코어 하나가 늘 바쁘다</td></tr>
<tr><td><code>--hipri</code></td><td>실패</td><td>—</td><td>—</td><td><code>Operation not supported</code> : 폴링 I/O 에는 NVMe 의 poll queue 가 필요한데 이 커널은 <code>poll_queues=0</code></td></tr>
</tbody></table></div>

이 속도 (약 400k IOPS, 장치가 한계) 에서는 어느 옵션도 처리량을 바꾸지 못했다. 이 옵션들은 **CPU 가 한계일 때** (수백만 IOPS, 여러 드라이브) 의 도구다. `sqthread_poll` 은 '요청을 넘기는 비용 (slat) 0' 을 코어 하나를 통째로 쓰는 것과 바꾼다.

## 쓰기 기준 : `--fsync`

![--fsync](/old-ssd-experiments/ref-fio-test/fsync.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>fsync</code></th>
<th>IOPS</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td>0 (안 함)</td><td>299k</td><td>107 µs</td><td>326 µs</td></tr>
<tr><td>1 (쓰기마다)</td><td><strong>2.6k</strong></td><td>242 µs</td><td>2.1 ms</td></tr>
<tr><td>32 (32번마다)</td><td>10.2k</td><td>236 µs</td><td>1.4 ms</td></tr>
</tbody></table></div>

- 쓰기마다 FLUSH 를 하면 **115배 느려진다.** `fsync` 는 앞의 쓰기가 끝날 때까지 기다리고 FLUSH 를 보내므로, 큐 깊이 32 가 사실상 1 이 된다. 거기에 FLUSH 하나의 비용 (수백 µs) 이 더해진다.
- 32번마다 하면 4배 나아진다. 데이터베이스가 커밋을 모아서 한 번에 `fsync` 하는 (group commit) 이유다.
- [실험 7](/old-ssd-experiments/7-flush/) 이 120GB SSD 에서 이것을 잰다.

## 쓰기 기준 : `--bs`

![--bs (randwrite)](/old-ssd-experiments/ref-fio-test/wbs.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>bs</code></th>
<th>IOPS</th>
<th>MB/s</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td>4 KiB</td><td>298k</td><td>1,222</td><td>107 µs</td><td>326 µs</td></tr>
<tr><td>64 KiB</td><td>18.2k</td><td>1,190</td><td>1.8 ms</td><td>30 ms</td></tr>
<tr><td>1 MiB</td><td>372</td><td><strong>393</strong></td><td>85 ms</td><td><strong>667 ms</strong></td></tr>
</tbody></table></div>

**쓰기 결과는 그 앞에 쓴 양에 달렸다.** 1 MiB 실행은 이 시점까지 약 40 GB 를 쓴 뒤에 돌았고, 99% 지연이 0.67 초까지 늘었다. 이 드라이브는 97% 차 있어서 (빈 공간 약 56 GB) SLC 버퍼가 작다. 버퍼가 차면 TLC 에 바로 쓰는 느린 속도 (약 400 MB/s) 와 버퍼 정리가 겹쳐 꼬리가 길어진다. 120GB SSD 의 [실험 3](/old-ssd-experiments/3-slc-cache/) 에서 본 '계단' 과 같은 일이다. 쓰기 벤치마크는 **얼마나 썼는지, 드라이브가 얼마나 찼는지** 를 함께 적어야 한다.

## 쓰기 기준 : `--direct`

![--direct (randwrite)](/old-ssd-experiments/ref-fio-test/wdirect.png)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th><code>direct</code></th>
<th>IOPS</th>
<th>평균 지연</th>
<th>99% 지연</th>
</tr></thead><tbody>
<tr><td>1</td><td>303k</td><td>105 µs</td><td>354 µs</td></tr>
<tr><td>0</td><td>308k</td><td>120 µs</td><td><strong>85 µs</strong></td></tr>
</tbody></table></div>

IOPS 는 비슷한데 버퍼 쓰기의 99% 지연이 4배 짧다 : 쓰기가 RAM 에 담기면 바로 '끝' 이기 때문이다. 드라이브는 아직 그 데이터를 받지 않았다. [fio 사용법 6절](/old-ssd-experiments/fio/) 의 1 GiB 쓰기 비교와 같은 이야기다.

## 기준 세 번 : 잡음은 얼마나 되나

![baseline](/old-ssd-experiments/ref-fio-test/baseline.png)

같은 기준을 이어서 세 번 : 474k · 474k · 479k IOPS (±0.5%). 이어서 돈 실행끼리의 잡음은 1% 안이다. 그러니 한 그룹 안의 차이가 몇 % 넘으면 진짜 차이다. 그룹 사이에서는 위의 경고처럼 드라이브의 상태가 바뀌어 20% 까지 달라졌다.

## 정리

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>바꾸면</th>
<th>가장 큰 차이</th>
<th>배운 것</th>
</tr></thead><tbody>
<tr><td><code>--iodepth</code></td><td>1 → 64</td><td>IOPS <strong>35배</strong>, 그 뒤로는 지연만 는다</td><td>장치의 병렬성을 쓰려면 요청을 걸어 둬야 한다. 천장 뒤로는 줄 서기</td></tr>
<tr><td><code>--ioengine</code></td><td><code>io_uring</code> → <code>psync</code></td><td>IOPS <strong>30배 낮음</strong></td><td>동기 엔진은 <code>iodepth</code> 를 무시한다. <code>posixaio</code> 는 겉모습만 비동기</td></tr>
<tr><td><code>--fsync</code></td><td>0 → 1</td><td>쓰기 IOPS <strong>115배 낮음</strong></td><td>FLUSH 는 비싸다 : 모아서 한다</td></tr>
<tr><td><code>--bs</code></td><td>4k → 1m</td><td>IOPS 230배 낮음, MB/s 는 천장 근처</td><td>512 B 와 4 KiB 는 같은 일, 16 KiB 부터 대역 천장</td></tr>
<tr><td><code>--rw</code></td><td>randread → randrw</td><td>읽기 99% 지연 <strong>12배</strong></td><td>섞인 쓰기가 읽기의 꼬리를 늘린다</td></tr>
<tr><td><code>--random_distribution</code></td><td>random → zipf:1.2</td><td>IOPS +34%, 꼬리 절반</td><td>몰린 접근은 빨라진다 (매핑 캐시)</td></tr>
<tr><td><code>--numjobs</code></td><td>1 → 2</td><td>+24%, 그 뒤로는 지연만</td><td>job × iodepth 가 걸린 요청의 합</td></tr>
<tr><td><code>--direct</code></td><td>1 → 0</td><td>읽기 −17%, 쓰기의 꼬리는 RAM 의 것</td><td>캐시를 거친 숫자는 장치가 아니다</td></tr>
<tr><td><code>--size</code>, <code>--thread</code>, io_uring 옵션</td><td>무엇이든</td><td>거의 없음</td><td>이 속도에서는 장치가 한계</td></tr>
<tr><td>드라이브의 상태</td><td>같은 명령, 앞에 40 GB 쓰기</td><td><strong>최대 20%</strong></td><td>숫자와 함께 상태를 적는다. 비교는 이어서 돈 것끼리</td></tr>
</tbody></table></div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/fio/' | relative_url }}">← fio 사용법</a><a href="{{ '/old-ssd-experiments/0-setup/' | relative_url }}">0. 준비 →</a></div>
