---
layout: default
title: 15. Read disturb
permalink: /old-ssd-experiments/15-read-disturb/
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

# 15. Read disturb : 같은 곳을 수억 번 읽으면

<div class="glance">
<b>목표</b><span>드라이브를 검사 가능한 무늬로 채운 뒤, 맨 앞 1 MiB 만 몇 시간 동안 계속 읽는다. 펌웨어가 그 블록을 옮기는 순간 (지연이 튀는 곳) 이 보이는지, 이웃 데이터가 상했는지 확인한다</span>
<b>보는 FTL 개념</b><span>read disturb (읽기 전압이 이웃 셀을 조금씩 프로그램함), 읽기 횟수 세기, read reclaim (블록 옮기기), ECC</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>채우기 20분 + 두드리기 HOURS (기본 6시간) + 확인 20분</span>
<b>명령</b><span><code>sudo ./lab.sh disturb 6</code></span>
</div>

## 배경

NAND 에서 한 페이지를 읽으려면 같은 블록의 **다른 모든 줄 (word line)** 에 높은 '통과 전압' 을 건다. 이 전압이 그 줄들의 셀에 전자를 아주 조금씩 밀어 넣는다. 한두 번은 아무 일도 없지만, 같은 블록을 수만–수십만 번 읽으면 이웃 셀의 전압이 올라가 비트 오류가 생긴다 : **read disturb**.
그래서 FTL 은 블록마다 읽은 횟수를 세고, 한도를 넘으면 그 블록의 데이터를 새 블록으로 옮긴다 (read reclaim). 그 순간 그 블록을 읽는 요청은 기다린다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>이 실험에서</th>
<th>크기</th>
</tr></thead><tbody>
<tr><td>두드리는 영역</td><td>맨 앞 1 MiB (4 KiB × 256개). TLC 블록 하나 (수 MiB 로 짐작) 안이거나 두세 개에 걸친다</td></tr>
<tr><td>읽기 속도</td><td>QD32 4 KiB 랜덤 읽기 : 수만 IOPS</td></tr>
<tr><td>6시간 동안</td><td>수억 번 읽기 → 블록 하나가 수억 번 읽힌다 (흔히 말하는 한도 : 수만–수십만 번)</td></tr>
</tbody></table></div>

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 펌웨어가 읽기 횟수를 세어 블록을 옮긴다</td><td><code>hammer_lat.log</code> (1초마다 가장 느린 읽기) 에 주기적인 큰 튐 : 옮기는 동안의 대기. 튀는 간격 = 읽기 한도 ÷ IOPS</td></tr>
<tr><td>H2 옮기기 덕분에 데이터는 상하지 않는다</td><td>verify 의 나쁜 블록 = 0</td></tr>
<tr><td>H3 옮기기 전까지는 이웃이 조금씩 나빠진다</td><td><code>near-after</code> 의 지연 (앞 1 GiB) 이 <code>near-before</code> 보다 길거나, SMART 195 (ECC 로 고친 오류) 가 는다</td></tr>
<tr><td>H4 컨트롤러가 읽기를 RAM 에 담아 둔다면</td><td>IOPS 가 SATA 한계 (약 10만) 근처이고 지연이 아주 짧고 고르다 : NAND 를 안 읽는다 (그러면 이 실험은 다른 방법이 필요하다)</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh disturb 6        # 숫자 = 두드릴 시간 (시간 단위). 밤새 하려면 10–12
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td>1</td><td>전체를 1 MiB 순차로 쓰되 4 KiB 마다 crc32c 머리말 (실험 16 과 같은 무늬)</td></tr>
<tr><td>2</td><td><code>near-before</code> : 앞 1 GiB 안의 4 KiB 랜덤 읽기 QD1, 60초</td></tr>
<tr><td>3</td><td>SMART 기록</td></tr>
<tr><td>4</td><td><code>hammer</code> : 앞 1 MiB 만 4 KiB 랜덤 읽기 QD32, HOURS 시간. 1초마다 IOPS 와 가장 느린 읽기 기록</td></tr>
<tr><td>5</td><td>SMART 기록, <code>near-after</code> (2 와 같은 측정)</td></tr>
<tr><td>6</td><td>전체 verify : 모든 4 KiB 블록의 체크섬 → <code>verify-summary.txt</code></td></tr>
</tbody></table></div>

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-disturb-* | tail -1)
$ python3 plot.py hammer-lat.png $D/hammer_lat.log=max
$ python3 plot.py hammer-iops.png $D/hammer_iops.log
$ cat $D/verify-summary.txt; python3 smartdiff.py $D
$ column -s, -t $D/summary.csv
```

1. **튐의 간격** : 두 튐 사이의 시간 × 평균 IOPS ÷ (1 MiB 가 걸친 블록 수) ≈ 펌웨어의 읽기 한도. Claude 가 로그에서 튐을 찾아 계산한다.
2. **verify** : 0 이 아니면 read disturb 로 상한 데이터를 ECC 도 펌웨어도 막지 못한 것이다.
3. **near-before / after** 의 50% · 99% 지연.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/14-secure-erase/' | relative_url }}">← 14. Secure Erase</a><a href="{{ '/old-ssd-experiments/16-retention/' | relative_url }}">16. Retention →</a></div>
