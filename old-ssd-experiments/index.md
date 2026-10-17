---
layout: default
title: 헌 SSD 로 하는 실험
permalink: /old-ssd-experiments/
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

# 헌 SSD 로 하는 실험

**믿을 수 없게 된 헌 SSD 를 버리는 대신, SSD 안에서 일어나는 일 (FTL) 을 직접 눈으로 보는 실험에 쓴다.** (2026.10.16 시작)

헌 드라이브는 이런 실험에 오히려 딱 맞다. 배울 것이 가장 많은 실험은 **데이터를 지우고 드라이브를 닳게 하는** 것이라, 아끼는 드라이브로는 할 수 없기 때문이다.
실험은 [FTL Visual Simulator](/ftl-visual-simulator/) 에서 모델로 만든 것 (GC, WAF, OP, SLC 캐시, 매핑 없는 읽기) 을 **실제 드라이브에서 확인** 하는 쪽으로 골랐다.

이 페이지는 전체 그림만 담는다. 실험마다 따로 튜토리얼 페이지가 있다 : 목표, 배경, 예상 결과, 절차, 결과 읽는 법.
결과가 나오면 각 페이지의 **결과** 절에 그래프와 분석을 붙인다.

## 실험할 드라이브

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>항목</th>
<th>값</th>
</tr></thead><tbody>
<tr><td>모델</td><td>Samsung SSD 840 EVO 120GB (2013년 출시 제품군)</td></tr>
<tr><td>시리얼 · 펌웨어</td><td><code>S1D6NSAFB40389K</code> · <code>EXT0CB6Q</code></td></tr>
<tr><td>용량</td><td>120,034,123,776 바이트 (234,441,648 섹터 × 512 B)</td></tr>
<tr><td>NAND</td><td>TLC (셀 하나에 3비트), SLC 버퍼 TurboWrite 약 3 GB (알려진 값)</td></tr>
<tr><td>지금 상태</td><td>옛 Windows 디스크, 91% 차 있음, 파일 날짜 2018–2024</td></tr>
<tr><td>지금 연결</td><td>USB–SATA 어댑터 (ASMedia, <code>uas</code>) : TRIM 이 통과하지 않는다</td></tr>
</tbody></table></div>

## 실험 순서

<svg viewBox="0 0 760 375" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="실험 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">실험 순서 : 지우지 않는 것부터, 기다려야 하는 것은 나중에</text><rect x="20" y="42" width="165" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="102.5" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">A. 지우기 전</text><text x="102.5" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">USB 그대로</text><rect x="30" y="108" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="50.0" y="130.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">0</text><text x="66.0" y="130.0" font-size="12" fill="#4d5656" text-anchor="start">준비 · SMART</text><rect x="30" y="150" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="50.0" y="172.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">1</text><text x="66.0" y="172.0" font-size="12" fill="#4d5656" text-anchor="start">오래된 데이터 읽기</text><rect x="205" y="42" width="165" height="50" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="287.5" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">B. SATA 로 옮긴 뒤</text><text x="287.5" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">드라이브를 지우며</text><rect x="215" y="108" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="235.0" y="130.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">2</text><text x="251.0" y="130.0" font-size="12" fill="#4d5656" text-anchor="start">SLC 캐시</text><rect x="215" y="150" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="235.0" y="172.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">3</text><text x="251.0" y="172.0" font-size="12" fill="#4d5656" text-anchor="start">TRIM · 빈 읽기</text><rect x="215" y="192" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="235.0" y="214.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">4</text><text x="251.0" y="214.0" font-size="12" fill="#4d5656" text-anchor="start">Write cliff</text><rect x="215" y="234" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="235.0" y="256.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">5</text><text x="251.0" y="256.0" font-size="12" fill="#4d5656" text-anchor="start">Over-provisioning</text><rect x="215" y="276" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="235.0" y="298.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">6</text><text x="251.0" y="298.0" font-size="12" fill="#4d5656" text-anchor="start">WAF (SMART)</text><rect x="390" y="42" width="165" height="50" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="472.5" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">C. 기다리기</text><text x="472.5" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">전원 없이 2–4주</text><rect x="400" y="108" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="420.0" y="130.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">7</text><text x="436.0" y="130.0" font-size="12" fill="#4d5656" text-anchor="start">Retention</text><rect x="575" y="42" width="165" height="50" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="657.5" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">D. 마지막</text><text x="657.5" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">드라이브를 소모</text><rect x="585" y="108" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="605.0" y="130.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">8</text><text x="621.0" y="130.0" font-size="12" fill="#4d5656" text-anchor="start">끝까지 쓰기</text><rect x="585" y="150" width="145" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="605.0" y="172.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">9</text><text x="621.0" y="172.0" font-size="12" fill="#4d5656" text-anchor="start">열어 보기</text><line x1="185" y1="67" x2="205" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="370" y1="67" x2="390" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="555" y1="67" x2="575" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="362.0" font-size="11.5" fill="#566573" text-anchor="middle">실험 6 은 따로 돌리기도 하지만, 실험 2–5 의 SMART 앞뒤 기록으로도 계산한다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>#</th>
<th>실험</th>
<th>무엇을 보나</th>
<th>지우나?</th>
<th>연결</th>
<th>시간 (대략)</th>
</tr></thead><tbody>
<tr><td>0</td><td><a href="/old-ssd-experiments/0-setup/">준비</a></td><td>드라이브 · 도구 · SMART 기준값</td><td>아니오</td><td>USB 그대로</td><td>30분</td></tr>
<tr><td>1</td><td><a href="/old-ssd-experiments/1-old-data/">오래된 데이터 읽기</a></td><td>몇 년 된 데이터의 읽기 속도 : read retry</td><td><strong>아니오 (지우기 전에 한 번뿐)</strong></td><td>USB 그대로</td><td>1–2시간</td></tr>
<tr><td>2</td><td><a href="/old-ssd-experiments/2-slc-cache/">SLC 캐시</a></td><td>TurboWrite 버퍼 크기, TLC 쓰기 속도</td><td>예</td><td>SATA</td><td>30분 + 회복 측정</td></tr>
<tr><td>3</td><td><a href="/old-ssd-experiments/3-trim/">TRIM 과 매핑 없는 읽기</a></td><td>매핑 없는 LBA 읽기는 NAND 를 안 거친다</td><td>예</td><td>SATA</td><td>30분</td></tr>
<tr><td>4</td><td><a href="/old-ssd-experiments/4-write-cliff/">Write cliff</a></td><td>빈 블록이 바닥나며 GC 시작 : FOB → steady state</td><td>예</td><td>SATA</td><td>밤새 (4–8시간)</td></tr>
<tr><td>5</td><td><a href="/old-ssd-experiments/5-over-provisioning/">Over-provisioning</a></td><td>앞쪽 80% 만 쓰면 steady state 가 몇 배 빨라지나</td><td>예</td><td>SATA</td><td>밤새</td></tr>
<tr><td>6</td><td><a href="/old-ssd-experiments/6-waf/">WAF (SMART)</a></td><td>드라이브가 센 값으로 WAF 추정 : 순차 vs 랜덤</td><td>예</td><td>SATA</td><td>2시간 + 실험 4–5 의 기록</td></tr>
<tr><td>7</td><td><a href="/old-ssd-experiments/7-retention/">Retention</a></td><td>전원 없이 몇 주 둔 데이터</td><td>예</td><td>SATA</td><td>2–4주 기다림</td></tr>
<tr><td>8</td><td><a href="/old-ssd-experiments/8-endurance/">끝까지 쓰기</a></td><td>수명이 다할 때 SMART 와 컨트롤러의 행동</td><td>예 (소모)</td><td>SATA</td><td>몇 주–몇 달</td></tr>
<tr><td>9</td><td><a href="/old-ssd-experiments/9-teardown/">열어 보기</a></td><td>컨트롤러 · DRAM · NAND 패키지</td><td>—</td><td>—</td><td>1시간</td></tr>
</tbody></table></div>

처음 시작한다면 먼저 [SSD 를 다루는 Linux 명령](/old-ssd-experiments/linux-commands/) 을 읽는다. 실험에 나오는 명령 (`lsblk`, `smartctl`, `fio`, `blkdiscard` …) 이 모두 거기 설명되어 있다.

## 스크립트

모든 실험은 스크립트 하나 [`lab.sh`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/old-ssd-experiments/scripts) 로 돌린다. 블로그 저장소의 `old-ssd-experiments/scripts/` 에 있다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>파일</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td><code>lab.sh</code></td><td>실험마다 하나씩 있는 명령 (<code>check</code>, <code>scan</code>, <code>slc</code>, <code>cliff</code> …). 드라이브를 <strong>시리얼로</strong> 찾고, 지우기 전에 다섯 가지를 확인한다</td></tr>
<tr><td><code>readscan.py</code></td><td>드라이브 전체를 읽으며 구간마다 속도, 가장 느린 읽기, 0 으로만 된 비율을 기록 (읽기만 한다)</td></tr>
<tr><td><code>fileage.py</code></td><td>파일마다 '언제 썼나' 와 '얼마나 빨리 읽히나' (읽기만 한다)</td></tr>
<tr><td><code>plot.py</code></td><td>결과 폴더의 로그로 그래프 그리기</td></tr>
<tr><td><code>smartdiff.py</code></td><td>실험 앞뒤 SMART 비교, 177 · 241 로 WAF 추정</td></tr>
</tbody></table></div>

결과는 `~/Ryu/old_ssd_results/<날짜>-<실험>/` 에 쌓인다. Claude 가 같은 컴퓨터에서 바로 읽고 분석한다.

## 진행 상황

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실험</th>
<th>상태</th>
</tr></thead><tbody>
<tr><td>0 준비</td><td>SMART 출력 기다리는 중 (<code>sudo apt install smartmontools fio</code> 다음 <code>sudo ./lab.sh check</code>)</td></tr>
<tr><td>1 – 9</td><td>아직</td></tr>
</tbody></table></div>

<div class="warn" markdown="1">
**안전.** 실험 2–8 은 드라이브 전체를 지운다. `lab.sh` 는 시리얼 `S1D6NSAFB40389K` 인 드라이브에만 쓰고, 시스템 디스크 · 마운트된 디스크 · TRIM 이 안 되는 연결이면 멈추며, 지우기 전에 시리얼 끝 5자리를 직접 입력하게 한다.
`lab.sh` 를 거치지 않고 `dd`, `blkdiscard`, `fio` 를 직접 쓸 때는 [Linux 명령 페이지의 위험한 명령 절](/old-ssd-experiments/linux-commands/#danger) 을 먼저 읽는다.
</div>

<div class="step-nav"><span></span><a href="{{ '/old-ssd-experiments/linux-commands/' | relative_url }}">SSD 를 다루는 Linux 명령 →</a></div>
