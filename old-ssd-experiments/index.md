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

**아무도 원하지 않을 헌 SSD 를, 버리기 전에 할 수 있는 실험을 다 해 보는 데 쓴다.** (2026.10.16 시작)

이 드라이브는 팔 수도 없고, 실험이 끝나면 버린다. 그래서 아끼는 드라이브로는 할 수 없는 실험 : 데이터를 지우고, 닳게 하고, 전원을 갑자기 끊고, 마지막에는 열어 보는 것까지 모두 한다.
실험은 SSD 안에서 일어나는 일 (FTL : 매핑, GC, SLC 캐시, 마모, 오류 정정, 전원 차단 복구) 을 밖에서 재는 것으로 골랐다. [FTL Visual Simulator](/ftl-visual-simulator/) 와 겹치는 실험은 그 페이지에 '덤' 으로 비교를 적었다.

이 페이지는 전체 그림만 담는다. 실험마다 따로 튜토리얼 페이지가 있다 : 목표, 배경, 가설, 절차, 결과 읽는 법.
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
<tr><td>지난 이력</td><td>2024.12 쯤 마지막으로 쓴 뒤 <strong>1년 넘게 전원 없이</strong> 보관. 2026.10.17 다시 연결 : Ryu 가 파일 몇 개를 읽고, 몇 개를 새로 씀. 원래 Windows 부팅 드라이브였다. 가끔 블루 스크린이 떠서 새로 PC 를 조립했고, 이 SSD 는 그 뒤로 쓰지 않고 두었다. 그러다 심심해서 이 SSD 로 실험해 보기로 했다</td></tr>
<tr><td>연결</td><td>메인보드 SATA (<code>ata5</code>, SATA 3) : TRIM 됨 (<code>DISC-MAX 2G</code>)</td></tr>
</tbody></table></div>

1년 넘게 전원 없이 있었다는 것이 실험 1 을 특별하게 만든다 : 켜져 있어야만 할 수 있는 펌웨어의 '오래된 데이터 다시 쓰기' 가 그동안 한 번도 없었다. 그래서 **실험 1 은 가장 먼저, 되도록 빨리** 한다.

## 실험 순서

<svg viewBox="0 0 760 370" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="실험 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">실험 순서 : 읽기만 하는 것 → 성능 → GC · 마모 → 기다리기 · 소모</text><rect x="10" y="42" width="140" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="80.0" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">A. 지우기 전</text><text x="80.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">읽기만 한다</text><rect x="14" y="108" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="30.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0</text><text x="44.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="start">준비 · SMART</text><rect x="14" y="150" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="30.0" y="172.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">1</text><text x="44.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="start">오래된 데이터</text><rect x="14" y="192" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="30.0" y="214.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">2</text><text x="44.0" y="214.0" font-size="11.5" fill="#4d5656" text-anchor="start">기능 · 자가 진단</text><rect x="160" y="42" width="140" height="50" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="230.0" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">B. 기본 성능</text><text x="230.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA · 막 지운 상태</text><rect x="164" y="108" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="180.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">3</text><text x="194.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="start">SLC 캐시</text><rect x="164" y="150" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="180.0" y="172.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">4</text><text x="194.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="start">TRIM · 빈 읽기</text><rect x="164" y="192" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="180.0" y="214.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">5</text><text x="194.0" y="214.0" font-size="11.5" fill="#4d5656" text-anchor="start">성능 지도</text><rect x="164" y="234" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="180.0" y="256.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">6</text><text x="194.0" y="256.0" font-size="11.5" fill="#4d5656" text-anchor="start">쓰기 크기 · 정렬</text><rect x="164" y="276" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="180.0" y="298.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">7</text><text x="194.0" y="298.0" font-size="11.5" fill="#4d5656" text-anchor="start">쓰기 캐시 · FLUSH</text><rect x="310" y="42" width="140" height="50" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="380.0" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">C. GC 와 여유</text><text x="380.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">꽉 찬 상태</text><rect x="314" y="108" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="330.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">8</text><text x="344.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="start">Write cliff</text><rect x="314" y="150" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="330.0" y="172.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">9</text><text x="344.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="start">쉬는 동안 GC</text><rect x="314" y="192" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="330.0" y="214.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">10</text><text x="344.0" y="214.0" font-size="11.5" fill="#4d5656" text-anchor="start">Over-provisioning</text><rect x="314" y="234" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="330.0" y="256.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">11</text><text x="344.0" y="256.0" font-size="11.5" fill="#4d5656" text-anchor="start">뜨거운 데이터</text><rect x="314" y="276" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="330.0" y="298.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">12</text><text x="344.0" y="298.0" font-size="11.5" fill="#4d5656" text-anchor="start">WAF (SMART)</text><rect x="460" y="42" width="140" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="530.0" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">D. 간섭 · 지우기</text><text x="530.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">읽기와 쓰기 사이</text><rect x="464" y="108" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="480.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">13</text><text x="494.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="start">읽기 · 쓰기 간섭</text><rect x="464" y="150" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="480.0" y="172.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">14</text><text x="494.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="start">Secure Erase</text><rect x="464" y="192" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="480.0" y="214.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">15</text><text x="494.0" y="214.0" font-size="11.5" fill="#4d5656" text-anchor="start">Read disturb</text><rect x="610" y="42" width="140" height="50" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="680.0" y="63.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">E. 마지막</text><text x="680.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle">기다리기 · 소모</text><rect x="614" y="108" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="630.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">16</text><text x="644.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="start">Retention</text><rect x="614" y="150" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="630.0" y="172.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">17</text><text x="644.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="start">전원 차단</text><rect x="614" y="192" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="630.0" y="214.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">18</text><text x="644.0" y="214.0" font-size="11.5" fill="#4d5656" text-anchor="start">끝까지 쓰기</text><rect x="614" y="234" width="132" height="34" rx="6" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="630.0" y="256.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">19</text><text x="644.0" y="256.0" font-size="11.5" fill="#4d5656" text-anchor="start">열어 보기</text><line x1="150" y1="67" x2="160" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="300" y1="67" x2="310" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="450" y1="67" x2="460" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="600" y1="67" x2="610" y2="67" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="335.0" font-size="11.5" fill="#566573" text-anchor="middle">실험 12 (WAF) 는 따로도 돌리지만, 실험 3–11 의 SMART 앞뒤 기록으로도 계산한다</text><text x="380.0" y="355.0" font-size="11.5" fill="#566573" text-anchor="middle">17 (전원 차단) 은 드라이브를 망가뜨릴 수 있어서, 18 (끝까지 쓰기) 은 드라이브를 소모해서 뒤에 둔다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>#</th>
<th>실험</th>
<th>무엇을 보나</th>
<th>지우나?</th>
<th>시간 (대략)</th>
</tr></thead><tbody>
<tr><td>0</td><td><a href="/old-ssd-experiments/0-setup/">준비</a></td><td>드라이브 · 도구 · SMART 기준값</td><td>아니오</td><td>30분</td></tr>
<tr><td>1</td><td><a href="/old-ssd-experiments/1-old-data/">오래된 데이터 읽기</a></td><td>1년 넘게 전원 없이 둔 데이터의 읽기 속도, 한 번 읽히면 다시 쓰이나</td><td><strong>아니오 (지우기 전에 한 번뿐)</strong></td><td>1–2시간</td></tr>
<tr><td>2</td><td><a href="/old-ssd-experiments/2-features/">기능 · 자가 진단</a></td><td>ATA 기능, 로그, SMART 자가 진단의 시간</td><td>아니오</td><td>1시간</td></tr>
<tr><td>3</td><td><a href="/old-ssd-experiments/3-slc-cache/">SLC 캐시</a></td><td>TurboWrite 버퍼 크기, TLC 쓰기 속도, 회복</td><td>예</td><td>1시간</td></tr>
<tr><td>4</td><td><a href="/old-ssd-experiments/4-trim/">TRIM 과 매핑 없는 읽기</a></td><td>매핑 없는 LBA 읽기는 NAND 를 안 거친다</td><td>예</td><td>30분</td></tr>
<tr><td>5</td><td><a href="/old-ssd-experiments/5-perf-map/">성능 지도</a></td><td>블록 크기 × 큐 깊이, 데이터 내용 (압축?)</td><td>예</td><td>1.5시간</td></tr>
<tr><td>6</td><td><a href="/old-ssd-experiments/6-write-size/">쓰기 크기 · 정렬</a></td><td>512 B 쓰기, 어긋난 4 KiB : 매핑 단위</td><td>예</td><td>40분</td></tr>
<tr><td>7</td><td><a href="/old-ssd-experiments/7-flush/">쓰기 캐시 · FLUSH</a></td><td>'다 썼다' 는 대답이 언제 오나</td><td>예</td><td>15분</td></tr>
<tr><td>8</td><td><a href="/old-ssd-experiments/8-write-cliff/">Write cliff</a></td><td>빈 블록이 바닥나며 GC 시작 : FOB → steady state</td><td>예</td><td>밤새 (4–8시간)</td></tr>
<tr><td>9</td><td><a href="/old-ssd-experiments/9-idle-gc/">쉬는 동안 GC</a></td><td>쉬면 빈 블록을 미리 만드나</td><td>예</td><td>1.5시간</td></tr>
<tr><td>10</td><td><a href="/old-ssd-experiments/10-over-provisioning/">Over-provisioning</a></td><td>덜 쓰면 steady state 가 몇 배 빨라지나</td><td>예</td><td>밤새 × 2–4</td></tr>
<tr><td>11</td><td><a href="/old-ssd-experiments/11-hot-cold/">뜨거운 데이터</a></td><td>쓰기가 일부에 몰리면 WAF 가 낮아지나</td><td>예</td><td>밤새 × 1–2</td></tr>
<tr><td>12</td><td><a href="/old-ssd-experiments/12-waf/">WAF (SMART)</a></td><td>드라이브가 센 값으로 WAF 추정 : 순차 vs 랜덤</td><td>예</td><td>2시간 + 앞의 기록</td></tr>
<tr><td>13</td><td><a href="/old-ssd-experiments/13-interference/">읽기 · 쓰기 간섭</a></td><td>쓰기가 돌 때 읽기의 꼬리 지연</td><td>예</td><td>40분</td></tr>
<tr><td>14</td><td><a href="/old-ssd-experiments/14-secure-erase/">Secure Erase</a></td><td>드라이브가 스스로 지우는 시간, FOB 로 돌아오나</td><td>예</td><td>1시간</td></tr>
<tr><td>15</td><td><a href="/old-ssd-experiments/15-read-disturb/">Read disturb</a></td><td>같은 곳을 수억 번 읽으면</td><td>예</td><td>밤새</td></tr>
<tr><td>16</td><td><a href="/old-ssd-experiments/16-retention/">Retention</a></td><td>전원 없이 몇 주 둔 데이터 (통제된 실험 1)</td><td>예</td><td>2–4주 기다림</td></tr>
<tr><td>17</td><td><a href="/old-ssd-experiments/17-power-loss/">전원 차단</a></td><td>FLUSH 한 데이터는 전원이 끊겨도 남나</td><td>예 (망가질 수 있음)</td><td>1–2시간</td></tr>
<tr><td>18</td><td><a href="/old-ssd-experiments/18-endurance/">끝까지 쓰기</a></td><td>수명이 다할 때 SMART 와 컨트롤러의 행동</td><td>예 (소모)</td><td>몇 주–몇 달</td></tr>
<tr><td>19</td><td><a href="/old-ssd-experiments/19-teardown/">열어 보기</a></td><td>컨트롤러 · DRAM · NAND 패키지</td><td>—</td><td>1시간</td></tr>
</tbody></table></div>

연결은 실험 17 만 USB 어댑터 (전원을 끊기 쉽게), 나머지는 모두 메인보드 SATA 다.

처음 시작한다면 먼저 [SSD Q&A](/old-ssd-experiments/ssd-tutorial/) (용량 · GB 와 GiB · over-provisioning · 드라이브 · 네임스페이스 · 파티션), [SSD 를 다루는 Linux 명령](/old-ssd-experiments/linux-commands/), [fio 사용법](/old-ssd-experiments/fio/) 을 읽는다. fio 의 옵션을 하나씩 바꿔 잰 참고 자료는 [Ref: fio test](/old-ssd-experiments/fio/ref-fio-test/). 실험에 나오는 명령 (`lsblk`, `smartctl`, `hdparm`, `blkdiscard`, `fio` …) 이 거기 설명되어 있다.

## 더 해 볼 수 있는 것

시간이 남으면 (각각 실험 하나 크기) : 파일 시스템별 WAF (ext4 · f2fs · btrfs 로 같은 작업을 하고 SMART 로 비교), 온도와 속도 (SMART 190 을 보며 오래 쓰기 : 열 때문에 느려지나), 순차와 랜덤이 섞인 '실제 같은' 부하 (fio 의 `rwmixread`), 비어 있는 드라이브와 꽉 찬 드라이브의 TRIM 처리 시간.

## 스크립트

모든 실험은 스크립트 하나 [`lab.sh`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/old-ssd-experiments/scripts) 로 돌린다. 블로그 저장소의 `old-ssd-experiments/scripts/` 에 있다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>파일</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td><code>lab.sh</code></td><td>실험마다 하나씩 있는 명령 (<code>check</code>, <code>oldfiles</code>, <code>features</code>, <code>slc</code>, <code>perfmap</code>, <code>cliff</code>, <code>mixed</code>, <code>secerase</code>, <code>pl-write</code> …). 드라이브를 <strong>시리얼로</strong> 찾고, 지우기 전에 다섯 가지를 확인한다. <code>./lab.sh</code> 만 치면 전체 목록</td></tr>
<tr><td><code>readscan.py</code></td><td>드라이브 전체를 읽으며 구간마다 속도, 가장 느린 읽기, 0 으로만 된 비율을 기록 (읽기만 한다)</td></tr>
<tr><td><code>fileage.py</code></td><td>파일마다 '언제 썼나', '다시 연결한 뒤 읽혔나', '얼마나 빨리 읽히나' (읽기만 한다)</td></tr>
<tr><td><code>fiosum.py</code></td><td>fio 의 JSON 결과들을 한 표 (<code>summary.csv</code>) 로</td></tr>
<tr><td><code>plcheck.py</code></td><td>전원 차단 실험 : 번호 붙은 기록 쓰기와 확인</td></tr>
<tr><td><code>plot.py</code></td><td>결과 폴더의 로그로 그래프 그리기</td></tr>
<tr><td><code>fiosweep.py</code> · <code>sweepplot.py</code></td><td>fio 옵션을 하나씩 바꿔 재고 그리기 (<a href="/old-ssd-experiments/fio/ref-fio-test/">Ref: fio test</a>)</td></tr>
<tr><td><code>smartdiff.py</code></td><td>실험 앞뒤 SMART 비교, 177 · 241 로 WAF 추정</td></tr>
</tbody></table></div>

결과는 `~/Ryu/old_ssd_results/<날짜>-<실험>/` 에 쌓인다. Claude 가 같은 컴퓨터에서 바로 읽고 분석한다.
모든 명령은 실제 드라이브에 쓰기 전에, 파일을 가짜 장치로 쓰는 시험 모드 (`LAB_TESTDEV`) 로 시간과 크기를 줄여 한 번씩 돌려 보았다.

## 진행 상황

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실험</th>
<th>상태</th>
</tr></thead><tbody>
<tr><td>0 준비</td><td><strong>끝</strong> (2026.10.18) : SMART 오류 0, 평생 WAF ≈ 1.4, 177 = 117 (수명의 약 10%), Security frozen. <a href="/old-ssd-experiments/0-setup/">결과</a></td></tr>
<tr><td>1 오래된 데이터</td><td><strong>끝</strong> (2026.10.18) : 데이터가 있는 곳은 약 9 MB/s, 빈 곳은 400–520 MB/s. 나이와 상관없이 모두 느리고, 오류는 없다. 블루 스크린은 이 SSD 탓이 아닐 가능성이 크다. <a href="/old-ssd-experiments/1-old-data/">결과</a></td></tr>
<tr><td>2 기능 · 자가 진단</td><td><strong>끝</strong> (2026.10.18) : 오류 로그 · 링크 오류 0, 자가 진단 <code>Completed without error</code> (62.6분, 예상 70분), Security frozen, 읽기만 해도 31 → 40 °C. <a href="/old-ssd-experiments/2-features/">결과</a></td></tr>
<tr><td>3 SLC 캐시</td><td><strong>끝</strong> (2026.10.18) : 버퍼 약 3.2 GB 를 533 MB/s, 그 뒤 TLC 약 150 MB/s, 버퍼는 몇 초 안에 다시 빈다. <strong>새 데이터는 약 445 MB/s 로 읽히고 (오래된 데이터의 약 45배), 자가 진단은 9.5분 (오래된 데이터는 62.6분)</strong> : 느림의 원인은 데이터의 나이였다. <a href="/old-ssd-experiments/3-slc-cache/">결과</a></td></tr>
<tr><td>4 TRIM 과 매핑 없는 읽기</td><td><strong>끝</strong> (2026.10.18) : TRIM 한 곳은 100% 0 으로 읽힌다 (약속은 없지만). QD1 지연 : 매핑 없음 63 µs, 있음 121 µs → NAND 페이지 읽기 약 60 µs. QD32 에서는 둘 다 약 9.5만 IOPS (SATA 한계). <a href="/old-ssd-experiments/4-trim/">결과</a></td></tr>
<tr><td>5 성능 지도</td><td>다음</td></tr>
<tr><td>6 – 19</td><td>아직</td></tr>
</tbody></table></div>

<div class="warn" markdown="1">
**안전.** 실험 3–18 은 드라이브 전체를 지운다. `lab.sh` 는 시리얼 `S1D6NSAFB40389K` 인 드라이브에만 쓰고, 시스템 디스크 · 마운트된 디스크 · (TRIM 이 필요한 실험에서) TRIM 이 안 되는 연결이면 멈추며, 지우기 전에 시리얼 끝 5자리를 직접 입력하게 한다.
`lab.sh` 를 거치지 않고 `dd`, `blkdiscard`, `fio` 를 직접 쓸 때는 [Linux 명령 페이지의 위험한 명령 절](/old-ssd-experiments/linux-commands/#danger) 을 먼저 읽는다.
</div>

<div class="step-nav"><span></span><a href="{{ '/old-ssd-experiments/ssd-tutorial/' | relative_url }}">SSD Q&A →</a></div>
