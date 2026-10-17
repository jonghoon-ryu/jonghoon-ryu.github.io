---
layout: default
title: 18. 끝까지 쓰기
permalink: /old-ssd-experiments/18-endurance/
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

# 18. 끝까지 쓰기 : 수명이 다할 때 무슨 일이 생기나

<div class="glance">
<b>목표</b><span>쉬지 않고 랜덤 쓰기를 하며 한 시간마다 SMART 를 남긴다. 예비 블록이 줄어드는 모습과, 수명이 다할 때 컨트롤러가 어떻게 행동하는지 본다</span>
<b>보는 FTL 개념</b><span>P/E 한도, 마모 평준화, 불량 블록 관리, 예비 블록, end-of-life 동작</span>
<b>지우나?</b><span>예. 드라이브를 <b>소모</b> 한다 (돌아오지 않는다)</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>몇 주–몇 달 (아래 계산)</span>
<b>명령</b><span><code>sudo ./lab.sh endurance 720</code> (최대 720시간 = 30일, 숫자는 바꿀 수 있다)</span>
</div>

## 배경

NAND 블록은 지우고 쓰기 (P/E) 를 할 때마다 절연막이 조금씩 상한다. 어느 횟수를 넘으면 쓰기 · 지우기에 실패하거나 데이터를 오래 붙잡지 못한다.
FTL 은 이것을 숨기려고 :
- **마모 평준화** 로 모든 블록을 고르게 쓰고 (177 의 평균이 의미 있는 이유)
- 실패한 블록을 **예비 블록** 으로 바꾸고 (179, 5)
- 예비가 바닥나면 보통 **읽기 전용** 으로 바뀌어 데이터라도 지키려 한다 (제조사마다 다르다)

<svg viewBox="0 0 760 380" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="수명 그래프"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">끝까지 쓰면 SMART 에서 보일 것 (가설)</text><line x1="90" y1="270" x2="720" y2="270" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="50" x2="90" y2="270" stroke="#566573" stroke-width="1.5"/><text x="405.0" y="310.0" font-size="12" fill="#2c3e50" text-anchor="middle">시간 (쓴 양) →</text><polyline points="90.0,226.0 720.0,67.6" fill="none" fill-opacity="1.0" stroke="#1f6f5c" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><text x="468.0" y="111.6" font-size="11.5" font-weight="700" fill="#1f6f5c" text-anchor="start">177 : 평균 지움 횟수 (꾸준히 증가)</text><polyline points="90.0,265.6 468.0,263.4 594.0,252.4 657.0,215.0 694.8,138.0" fill="none" fill-opacity="1.0" stroke="#c0392b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><text x="436.5" y="204.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="start">179 · 5 : 쓴 예비 블록 · 재할당 (끝에 급증)</text><line x1="694.8" y1="50" x2="694.8" y2="270" stroke="#566573" stroke-width="1.4" stroke-dasharray="4 4"/><text x="682.2" y="56.6" font-size="11.5" fill="#566573" text-anchor="end">끝 : 읽기 전용? 응답 없음?</text><text x="400.0" y="350.0" font-size="11.5" fill="#566573" text-anchor="middle">177 의 &#x27;정규화 값&#x27; (100 에서 시작해 내려감) 은 펌웨어가 보는 남은 수명 %</text><text x="400.0" y="368.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">끝나는 모습 (읽기 전용으로 바뀌는지, 갑자기 사라지는지) 이 이 실험의 핵심 관찰</text></svg>

## 얼마나 걸릴까

<svg viewBox="0 0 760 250" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="수명 계산"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">얼마나 걸릴까 : 거친 계산 (가정이 많다)</text><rect x="15" y="50" width="170" height="62" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="100.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">P/E 한도</text><text x="100.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">TLC 약 1,000회?</text><rect x="203" y="50" width="170" height="62" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="288.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">× NAND 137 GB</text><text x="288.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">= 137 TB</text><line x1="187" y1="81" x2="201" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="391" y="50" width="170" height="62" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="476.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">÷ WAF ≈ 7.8</text><text x="476.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">≈ 18 TB 호스트 쓰기</text><line x1="375" y1="81" x2="389" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="579" y="50" width="170" height="62" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="664.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">÷ 12 MB/s</text><text x="664.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">≈ 17일</text><line x1="563" y1="81" x2="577" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="150.0" font-size="12" fill="#2c3e50" text-anchor="middle">TLC 840 은 공개된 내구성 실험에서 한도보다 훨씬 오래 버틴 것으로 알려져 있다</text><text x="380.0" y="172.0" font-size="12" font-weight="700" fill="#c0392b" text-anchor="middle">→ 몇 주에서 몇 달 : 시작하기 전에 기간 (HOURS) 과 멈출 기준을 정한다</text><text x="380.0" y="210.0" font-size="11.5" fill="#566573" text-anchor="middle">이미 쓴 만큼 (지금 177 값) 은 빼야 한다 : 실험 0 의 SMART 로 다시 계산한다</text></svg>

TLC 의 P/E 한도는 흔히 1,000회 안팎으로 말해지지만, TLC 를 쓴 Samsung 840 은 2013–2015년의 공개 내구성 실험 (Tech Report) 에서 한도보다 훨씬 많이 쓰고서야 죽은 것으로 알려져 있다. **실제로는 더 오래 걸릴 가능성이 크다.** 기간과 멈출 기준을 먼저 정한다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>멈출 기준</th>
<th>이유</th>
</tr></thead><tbody>
<tr><td>드라이브가 쓰기를 거부 (fio 오류)</td><td>끝 : 스크립트가 스스로 멈춘다</td></tr>
<tr><td>정해 둔 시간 (<code>endurance 720</code>)</td><td>컴퓨터를 계속 켜 둘 수 있는 기간</td></tr>
<tr><td>177 의 정규화 값이 1 근처</td><td>펌웨어가 보는 수명 끝 : 여기서 멈추고 실험 16 을 한 번 더 할 수도 있다</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh endurance 720
```

- 전체 TRIM 뒤, **1시간짜리 fio 실행** (4 KiB 랜덤 쓰기 QD32, 전체 범위) 을 반복한다
- 매시간 끝에 SMART 를 `smart-h0001.txt/json`, `smart-h0002…` 로 남기고, `hours.csv` 에 한 줄 (시간, 날짜, ok / fio-error)
- fio 가 오류로 끝나면 '쓰기를 거부했다' 로 보고 멈춘다
- 중간에 멈추고 (Ctrl+C) 나중에 다시 시작해도 된다 : 새 결과 폴더가 생긴다. 다시 시작할 때 처음의 전체 TRIM 이 한 번 더 일어나는 것은 괜찮다

<div class="warn" markdown="1">
- 몇 주 동안 컴퓨터가 켜져 있어야 한다. 절전 (suspend) 을 끄고, 드라이브 주변의 바람길을 막지 않는다. 840 EVO 의 온도는 SMART 190 으로 본다.
- 끝에서 드라이브가 갑자기 사라지면 (응답 없음) 커널 로그에 오류가 쌓인다. 다른 디스크에는 영향이 없지만, `journalctl -k` 를 같이 남겨 둔다.
- 이 실험 뒤에는 실험 19 (열어 보기) 만 남는다. 앞의 실험들을 다 끝낸 뒤에 한다.
</div>

## 결과 읽는 법

Claude 가 `smart-h*.json` 전부를 읽어 시간에 따른 표와 그래프를 만든다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>본다</th>
<th>무엇을</th>
</tr></thead><tbody>
<tr><td>177 raw</td><td>하루에 몇씩 오르나 → P/E 속도, 그리고 NAND 쓰기 양 (× 137 GB)</td></tr>
<tr><td>177 정규화 값</td><td>펌웨어가 보는 남은 수명 % 가 P/E 와 어떻게 대응하나 → 펌웨어가 가정한 P/E 한도를 거꾸로 계산</td></tr>
<tr><td>179 · 5 · 181 · 182 · 183</td><td>언제부터 오르기 시작하나 (마모가 한도를 넘는 시점)</td></tr>
<tr><td>187 · 195</td><td>고친 · 못 고친 오류의 증가</td></tr>
<tr><td>fio 의 시간별 IOPS</td><td>끝으로 갈수록 느려지나 (프로그램 시간이 길어지고, 재시도가 늘어남)</td></tr>
<tr><td>끝나는 모습</td><td>읽기 전용? 사라짐? 오류만 늘어남?</td></tr>
</tbody></table></div>

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/17-power-loss/' | relative_url }}">← 17. 전원 차단</a><a href="{{ '/old-ssd-experiments/19-teardown/' | relative_url }}">19. 열어 보기 →</a></div>
