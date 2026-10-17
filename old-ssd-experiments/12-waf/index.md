---
layout: default
title: 12. WAF (SMART)
permalink: /old-ssd-experiments/12-waf/
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

# 12. WAF : 드라이브가 직접 센 숫자로 쓰기 증폭 재기

<div class="glance">
<b>목표</b><span>SMART 의 '호스트가 쓴 양' (241) 과 '평균 지움 횟수' (177) 로 실제 WAF 를 추정한다. 순차 쓰기 (WAF ≈ 1 예상) 와 랜덤 쓰기 (실험 8, 10) 를 비교한다</span>
<b>보는 FTL 개념</b><span>write amplification, 마모 평준화가 세는 지움 횟수</span>
<b>지우나?</b><span>예 (순차 쓰기 실행). 랜덤 쪽은 실험 8, 10 의 기록을 그대로 쓴다</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>순차 5회 쓰기 약 1.5–2시간</span>
<b>명령</b><span><code>sudo ./lab.sh seqwaf 5</code>, <code>python3 smartdiff.py 결과폴더</code></span>
</div>

## 배경

<svg viewBox="0 0 760 230" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="WAF 흐름"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">호스트가 쓴 양과 NAND 에 쓴 양</text><rect x="20" y="70" width="160" height="60" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="100.0" y="96.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">호스트</text><text x="100.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">100 GB 를 쓰라고 함</text><rect x="260" y="70" width="200" height="60" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="360.0" y="96.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">FTL</text><text x="360.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">쓸 자리 마련 = GC</text><rect x="540" y="40" width="200" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="640.0" y="69.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">새 데이터 100 GB</text><rect x="540" y="110" width="200" height="50" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="640.0" y="139.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">GC 복사 (WAF−1)×100 GB</text><line x1="180" y1="100" x2="258" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="219.0" y="90.0" font-size="11.5" fill="#566573" text-anchor="middle">241 이 센다</text><line x1="460" y1="90" x2="538" y2="65" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="460" y1="110" x2="538" y2="135" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="640.0" y="190.0" font-size="12" font-weight="700" fill="#c0392b" text-anchor="middle">합계 = NAND 쓰기 : 177 로 추정</text><text x="380.0" y="218.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">WAF = NAND 쓰기 ÷ 호스트 쓰기</text></svg>

많은 드라이브는 SMART 에 'NAND 에 쓴 양' 을 따로 보여 준다 (Crucial · Micron 의 247/248, Intel 의 NAND writes 등). 840 EVO 에는 그런 항목이 없는 것으로 알고 있다 (실험 0 의 SMART 출력으로 확인). 대신 177 을 쓴다.

<svg viewBox="0 0 760 290" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="177"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">177 Wear_Leveling_Count : 블록들의 평균 지움 횟수</text><rect x="30" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="58.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">412</text><rect x="92" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="120.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">413</text><rect x="154" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="182.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">412</text><rect x="216" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="244.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">414</text><rect x="278" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="306.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">413</text><rect x="340" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="368.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">412</text><rect x="402" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="430.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">413</text><rect x="464" y="60" width="56" height="56" rx="4" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="492.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">413</text><text x="270.0" y="52.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">블록마다 지운 횟수 (예)</text><text x="270.0" y="140.0" font-size="12.5" font-weight="700" fill="#1f6f5c" text-anchor="middle">평균 413 → 177 의 raw 값</text><rect x="560" y="60" width="180" height="80" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="650.0" y="80.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">모든 블록을 한 번씩</text><text x="650.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">더 지우면 +1</text><text x="650.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">= NAND 전체를 한 번</text><text x="650.0" y="128.0" font-size="11.5" fill="#4d5656" text-anchor="middle">더 쓴 것 (약 137 GB)</text><rect x="30" y="175" width="700" height="85" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="380.0" y="197.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">그래서</text><text x="380.0" y="213.5" font-size="11.5" fill="#4d5656" text-anchor="middle">NAND 쓰기 ≈ (177 이 늘어난 수) × 137 GB</text><text x="380.0" y="229.5" font-size="11.5" fill="#4d5656" text-anchor="middle">눈금이 137 GB 씩이라 거칠다 : 177 이 5 이상 늘 만큼 써야 오차가 ±20% 안쪽</text><text x="380.0" y="245.5" font-size="11.5" fill="#4d5656" text-anchor="middle">smartdiff.py 가 이 계산과 오차 범위를 함께 출력한다</text></svg>

## 가설과 예상

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="WAF 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 WAF (모델 · 가설)</text><line x1="90" y1="225.0" x2="720" y2="225.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="185.0" x2="720" y2="185.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="145.0" x2="720" y2="145.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="105.0" x2="720" y2="105.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="65.0" x2="720" y2="65.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="225" x2="720" y2="225" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="45" x2="90" y2="225" stroke="#566573" stroke-width="1.5"/><line x1="247.5" y1="225" x2="247.5" y2="230" stroke="#566573" stroke-width="1.2"/><text x="247.5" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">순차 쓰기</text><line x1="405.0" y1="225" x2="405.0" y2="230" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">랜덤 span 100%</text><line x1="562.5" y1="225" x2="562.5" y2="230" stroke="#566573" stroke-width="1.2"/><text x="562.5" y="244.0" font-size="11.5" fill="#4d5656" text-anchor="middle">랜덤 span 80%</text><line x1="85" y1="225.0" x2="90" y2="225.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="229.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="85" y1="185.0" x2="90" y2="185.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="189.0" font-size="11.5" fill="#4d5656" text-anchor="end">2</text><line x1="85" y1="145.0" x2="90" y2="145.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="149.0" font-size="11.5" fill="#4d5656" text-anchor="end">4</text><line x1="85" y1="105.0" x2="90" y2="105.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="109.0" font-size="11.5" fill="#4d5656" text-anchor="end">6</text><line x1="85" y1="65.0" x2="90" y2="65.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="69.0" font-size="11.5" fill="#4d5656" text-anchor="end">8</text><text x="38.0" y="135.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 38.0 135.0)">WAF</text><rect x="202.5" y="203.0" width="90.0" height="22.0" rx="0" fill="#1f6f5c" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="247.5" y="195.0" font-size="13" font-weight="700" fill="#1f6f5c" text-anchor="middle">≈ 1</text><rect x="360.0" y="68.7" width="90.0" height="156.3" rx="0" fill="#c0392b" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="405.0" y="60.7" font-size="13" font-weight="700" fill="#c0392b" text-anchor="middle">≈ 7.8</text><rect x="517.5" y="181.3" width="90.0" height="43.7" rx="0" fill="#2874a6" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="562.5" y="173.3" font-size="13" font-weight="700" fill="#2874a6" text-anchor="middle">≈ 2.2</text><text x="400.0" y="272.0" font-size="11.5" fill="#566573" text-anchor="middle">순차 쓰기는 블록이 통째로 무효가 되어 GC 복사가 거의 없다 : WAF ≈ 1</text><text x="400.0" y="290.0" font-size="11.5" fill="#566573" text-anchor="middle">랜덤 쓰기 값은 실험 10 의 모델 값 : SMART 로 잰 값과 맞춰 본다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 순차 쓰기의 WAF 는 1 에 가깝다</td><td>seqwaf 5 : 호스트 600 GB, 177 이 약 4–5 증가 → WAF ≈ 0.9–1.2</td></tr>
<tr><td>H2 랜덤 쓰기 (span 100%) 의 WAF 는 크다</td><td>실험 8 : 호스트 240 GB, 177 이 10 이상 증가 → WAF 5–10</td></tr>
<tr><td>H3 OP 가 크면 WAF 가 작다</td><td>실험 10 (span 80%) 의 WAF 가 실험 8 보다 확실히 작다</td></tr>
</tbody></table></div>

## 절차

```
# 순차 : 전체 TRIM → 128 KiB 순차 쓰기로 드라이브 전체를 5번
$ sudo ./lab.sh seqwaf 5

# 각 실행의 SMART 앞뒤 비교 (실험 3–11 의 결과 폴더에도 그대로 쓸 수 있다)
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-seqwaf-x5
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-cliff-span100
$ python3 smartdiff.py ~/Ryu/old_ssd_results/<날짜>-cliff-span80
```

`smartdiff.py` 의 출력 예 (가짜 숫자로 만든 시험 출력) :

```
 177 Wear_Leveling_Count                     300            312          +12
 241 Total_LBAs_Written               1000000000     1937766592   +937766592

host writes (241):       480.1 GB
erase count (177):  +12  ->  NAND writes ~ 1649 GB
WAF ~ 3.43   (177 counts whole steps, so between 3.15 and 3.72)
```

## 주의할 점

<div class="warn" markdown="1">
- **177 의 눈금은 약 137 GB 다.** 177 이 1–2 만 늘면 WAF 오차가 ±50% 를 넘는다. 순차 쓰기를 5회로 정한 이유다.
- 177 이 TurboWrite 영역 (SLC 로 쓰는 블록) 의 지움도 같이 세는지, 펌웨어가 평균을 어떻게 내는지는 알 수 없다. 순차 쓰기에서 WAF 가 1 보다 확실히 크게 나오면, SLC → TLC 옮기기 (데이터를 두 번 씀) 가 섞인 것일 수 있다 : 그것도 결과다.
- 실험 사이에 드라이브가 쉬는 동안 하는 일 (버퍼 비우기, 마모 평준화) 도 177 을 올린다. 그래서 `smart-before` 는 실행 직전, `smart-after` 는 실행 직후에 찍는다 (`lab.sh` 가 그렇게 한다).
</div>

## 결과 읽는 법

1. 실행마다 WAF 와 오차 범위를 표로 : 순차, 랜덤 100%, 랜덤 80% (+ 90%, 70%).
2. 랜덤의 값들을 실험 10 의 ρ–WAF 곡선에 찍는다 → 숨은 여유 공간 추정.
3. 순차 WAF 가 1 보다 얼마나 큰지 → 'SLC 버퍼를 거친 비용' 의 추정.

## 시뮬레이터와의 연결 (덤)

시뮬레이터는 GC 가 복사한 페이지를 직접 세어 WAF 를 낸다. 실제 드라이브는 그 숫자를 보여 주지 않으니 177 로 거꾸로 추정한다. 두 방법의 차이 자체가 '밖에서 FTL 을 재는 일' 의 한계를 보여 준다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/11-hot-cold/' | relative_url }}">← 11. 뜨거운 데이터</a><a href="{{ '/old-ssd-experiments/13-interference/' | relative_url }}">13. 읽기 · 쓰기 간섭 →</a></div>
