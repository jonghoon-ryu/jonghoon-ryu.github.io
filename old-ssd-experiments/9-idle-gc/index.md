---
layout: default
title: 9. 쉬는 동안 GC
permalink: /old-ssd-experiments/9-idle-gc/
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

# 9. 쉬는 동안의 GC : 드라이브는 놀 때 청소하나

<div class="glance">
<b>목표</b><span>write cliff 로 steady state 에 들어간 드라이브를 0 · 1 · 5 · 15 · 30분 쉬게 한 뒤 다시 쓰기를 시작해서, 쉬는 동안 빈 블록을 미리 만들어 두는지 (background GC), 얼마나 만드는지 잰다</span>
<b>보는 FTL 개념</b><span>foreground GC vs background (idle) GC, 빈 블록 풀의 목표 크기, 쓰기 폭주 (burst) 의 흡수</span>
<b>지우나?</b><span>예 (덮어쓴다. 처음의 TRIM 은 하지 않는다 : steady state 를 유지해야 하므로)</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>사전 쓰기 10분 + (쉬는 시간 + 2분) 의 합 : <code>0 1 5 15 30</code> 이면 약 1시간 20분</span>
<b>명령</b><span><code>sudo ./lab.sh idlegc 0 1 5 15 30</code> (실험 8 바로 뒤에)</span>
</div>

## 배경

실험 8 의 steady state 에서는 쓰기 하나를 받을 때마다 GC 가 그만큼 빈 공간을 만들어야 한다 (foreground GC) : 그래서 느리다.
그런데 호스트가 쉬는 동안 컨트롤러가 미리 GC 를 해서 빈 블록을 쌓아 둔다면, 다시 쓰기가 시작될 때 **처음 얼마 동안은 GC 없이** 빠르게 쓸 수 있다. 쌓아 둔 빈 블록이 다 쓰이면 다시 steady state 로 떨어진다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>쉬는 동안 하는 일</th>
<th>다시 쓸 때 보일 것</th>
</tr></thead><tbody>
<tr><td>아무것도 안 함</td><td>쉰 시간과 상관없이 처음부터 steady state 속도</td></tr>
<tr><td>background GC (한도 있음)</td><td>처음 몇 초–몇십 초가 빠름. 빠른 구간의 길이가 쉰 시간에 따라 늘다가 어느 값에서 멈춘다 (그 값 = 미리 만들어 두는 빈 블록의 목표)</td></tr>
<tr><td>SLC 버퍼 비우기만</td><td>실험 3 의 회복과 같은 모양. 그러나 steady state 에서는 SLC 도 GC 의 영향을 받는다</td></tr>
</tbody></table></div>

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 쉬면 빨라진다</td><td><code>idle5</code> · <code>idle15</code> 의 첫 구간 IOPS 가 <code>idle0</code> 보다 높다</td></tr>
<tr><td>H2 회복에는 한도가 있다</td><td>빠른 구간에 쓴 양 (GB) 이 15분과 30분에서 비슷하다</td></tr>
<tr><td>H3 빠른 구간에 쓴 양 ≈ 미리 만든 빈 공간</td><td>빠른 구간의 GB × WAF 근처의 값이 숨은 여유 (실험 10) 의 일부와 맞는다</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh cliff 100          # 실험 8 (끝나면 바로)
$ sudo ./lab.sh idlegc 0 1 5 15 30
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td>1</td><td>4 KiB 랜덤 쓰기 QD32 를 10분 : 확실히 steady state 로</td></tr>
<tr><td>2</td><td>각 숫자 M 마다 : M 분 쉼 → 4 KiB 랜덤 쓰기 QD32 를 2분, IOPS 를 1초마다 기록 (<code>idleM_iops.log</code>)</td></tr>
</tbody></table></div>

쉬는 동안 컴퓨터의 다른 일은 괜찮다. 이 드라이브에만 I/O 가 없으면 된다 (마운트하지 않은 상태라 다른 프로그램이 건드리지 않는다).

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-idlegc | tail -1)
$ python3 plot.py idlegc.png $D/idle{0,1,5,15,30}_iops.log
```

1. 곡선마다 **처음 빠른 구간** 의 길이 (GB) 와 높이. x 축이 '쓴 GB' 라 바로 읽힌다.
2. 쉰 시간 – 빠른 구간 GB 의 표 → H1, H2.
3. `idle0` 은 쉬지 않은 기준선이다. 그것과 다르지 않으면 이 드라이브는 쉬는 동안 GC 를 하지 않는다 (또는 아주 조금).

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/8-write-cliff/' | relative_url }}">← 8. Write cliff</a><a href="{{ '/old-ssd-experiments/10-over-provisioning/' | relative_url }}">10. Over-provisioning →</a></div>
