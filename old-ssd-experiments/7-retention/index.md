---
layout: default
title: 7. Retention
permalink: /old-ssd-experiments/7-retention/
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

# 7. Retention : 전원 없이 둔 데이터

<div class="glance">
<b>목표</b><span>검사할 수 있는 패턴으로 드라이브를 채우고, 전원 없이 몇 주 둔 뒤 다시 읽어 속도 변화와 오류를 본다</span>
<b>보는 FTL 개념</b><span>data retention, 전하 누설, ECC 의 한계, read retry (실험 1 의 '통제된' 판)</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>쓰기 20분 + 2–4주 보관 + 확인 1시간</span>
<b>명령</b><span><code>sudo ./lab.sh ret-write</code>, (몇 주 뒤) <code>sudo ./lab.sh ret-check</code></span>
</div>

## 배경

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="전하 누설"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">전원이 없어도 셀의 전하는 조금씩 빠져나간다</text><rect x="60" y="50" width="260" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="190.0" y="74.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">제어 게이트</text><rect x="60" y="95" width="260" height="50" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="190.0" y="112.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">전하 저장층 (전자 = 데이터)</text><rect x="60" y="150" width="260" height="30" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="190.0" y="169.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">얇은 절연막</text><rect x="60" y="185" width="260" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="190.0" y="209.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">채널 (실리콘)</text><circle cx="100.0" cy="132.0" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><circle cx="150.0" cy="132.0" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><circle cx="200.0" cy="132.0" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><circle cx="250.0" cy="132.0" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><circle cx="290.0" cy="132.0" r="6" fill="#2874a6" stroke="none" stroke-width="1.5"/><line x1="150" y1="140" x2="135" y2="200" stroke="#c0392b" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><line x1="250" y1="140" x2="265" y2="200" stroke="#c0392b" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="210.0" y="250.0" font-size="12" font-weight="700" fill="#c0392b" text-anchor="middle">새는 전자 → 문턱 전압이 내려간다</text><rect x="400" y="50" width="340" height="175" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="570.0" y="93.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">빨리 새게 만드는 것</text><text x="570.0" y="109.5" font-size="11.5" fill="#4d5656" text-anchor="middle">온도 : 따뜻할수록 빠르다</text><text x="570.0" y="125.5" font-size="11.5" fill="#4d5656" text-anchor="middle">닳은 정도 : P/E 가 많을수록 절연막이 약하다</text><text x="570.0" y="141.5" font-size="11.5" fill="#4d5656" text-anchor="middle">시간 : 몇 주 → 몇 년</text><text x="570.0" y="157.5" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="570.0" y="173.5" font-size="11.5" fill="#4d5656" text-anchor="middle">JEDEC 클라이언트 SSD 기준 : 수명이 다한 뒤에도</text><text x="570.0" y="189.5" font-size="11.5" fill="#4d5656" text-anchor="middle">30 °C 에서 1년 보관 (기준으로 알려진 값)</text></svg>

실험 1 은 '몇 년' 을 이미 겪은 데이터지만, 언제 썼는지 · 그동안 전원이 켜져 있었는지 · 펌웨어가 다시 썼는지를 모른다. 이 실험은 그것을 통제한다 : **정확히 언제 썼고, 그동안 전원이 없었다.**

몇 주는 짧다. 새 드라이브라면 차이가 거의 없을 것이다. 그러나 이 드라이브는 이미 닳았고 (실험 0 의 177), 실험 4–6 에서 더 닳는다. 닳은 셀일수록 전하를 빨리 잃는다.

<div class="tip" markdown="1">
**더 강하게 하고 싶다면** 실험 8 (끝까지 쓰기) 을 중간에 멈추고, 마모가 많이 된 상태에서 이 실험을 한 번 더 한다. 같은 2–4주라도 결과가 훨씬 클 수 있다.
</div>

## 시간표

<svg viewBox="0 0 760 200" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="시간표"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">실험 7 의 시간표</text><line x1="60" y1="120" x2="700" y2="120" stroke="#566573" stroke-width="3"/><rect x="40" y="50" width="170" height="50" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="125.0" y="71.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">ret-write</text><text x="125.0" y="87.0" font-size="11.5" fill="#4d5656" text-anchor="middle">전체에 검사 가능한 패턴</text><circle cx="125.0" cy="120.0" r="7" fill="#2c3e50" stroke="none" stroke-width="1.5"/><text x="125.0" y="145.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">0일</text><rect x="300" y="50" width="170" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="385.0" y="71.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">보관</text><text x="385.0" y="87.0" font-size="11.5" fill="#4d5656" text-anchor="middle">전원 없이 2–4주</text><circle cx="385.0" cy="120.0" r="7" fill="#2c3e50" stroke="none" stroke-width="1.5"/><text x="385.0" y="145.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle"></text><rect x="560" y="50" width="170" height="50" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="645.0" y="71.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">ret-check</text><text x="645.0" y="87.0" font-size="11.5" fill="#4d5656" text-anchor="middle">속도 + 체크섬 확인</text><circle cx="645.0" cy="120.0" r="7" fill="#2c3e50" stroke="none" stroke-width="1.5"/><text x="645.0" y="145.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">N일</text><text x="380.0" y="185.0" font-size="11.5" fill="#566573" text-anchor="middle">가능하면 실험 1 의 &#x27;몇 년 된 데이터&#x27; 와 같은 그래프에 놓는다</text></svg>

## 가설과 예상

<svg viewBox="0 0 760 310" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="retention 예상"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">예상 : 같은 드라이브, 데이터 나이만 다르게 (가설)</text><line x1="90" y1="235.0" x2="720" y2="235.0" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="192.77777777777777" x2="720" y2="192.77777777777777" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="150.55555555555554" x2="720" y2="150.55555555555554" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="108.33333333333334" x2="720" y2="108.33333333333334" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="66.11111111111111" x2="720" y2="66.11111111111111" stroke="#eaeded" stroke-width="1"/><line x1="90" y1="235" x2="720" y2="235" stroke="#566573" stroke-width="1.5"/><line x1="90" y1="45" x2="90" y2="235" stroke="#566573" stroke-width="1.5"/><line x1="247.5" y1="235" x2="247.5" y2="240" stroke="#566573" stroke-width="1.2"/><text x="247.5" y="254.0" font-size="11.5" fill="#4d5656" text-anchor="middle">막 쓴 데이터</text><line x1="405.0" y1="235" x2="405.0" y2="240" stroke="#566573" stroke-width="1.2"/><text x="405.0" y="254.0" font-size="11.5" fill="#4d5656" text-anchor="middle">2–4주 보관</text><line x1="562.5" y1="235" x2="562.5" y2="240" stroke="#566573" stroke-width="1.2"/><text x="562.5" y="254.0" font-size="11.5" fill="#4d5656" text-anchor="middle">몇 년 된 데이터 (실험 1)</text><line x1="85" y1="235.0" x2="90" y2="235.0" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="239.0" font-size="11.5" fill="#4d5656" text-anchor="end">0</text><line x1="85" y1="192.77777777777777" x2="90" y2="192.77777777777777" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="196.8" font-size="11.5" fill="#4d5656" text-anchor="end">100</text><line x1="85" y1="150.55555555555554" x2="90" y2="150.55555555555554" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="154.6" font-size="11.5" fill="#4d5656" text-anchor="end">200</text><line x1="85" y1="108.33333333333334" x2="90" y2="108.33333333333334" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="112.3" font-size="11.5" fill="#4d5656" text-anchor="end">300</text><line x1="85" y1="66.11111111111111" x2="90" y2="66.11111111111111" stroke="#566573" stroke-width="1.2"/><text x="81.0" y="70.1" font-size="11.5" fill="#4d5656" text-anchor="end">400</text><text x="38.0" y="140.0" font-size="12" fill="#2c3e50" text-anchor="middle" transform="rotate(-90 38.0 140.0)">읽기 속도 (MB/s)</text><rect x="202.5" y="66.1" width="90.0" height="168.9" rx="0" fill="#1f6f5c" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="247.5" y="58.1" font-size="14" font-weight="700" fill="#1f6f5c" text-anchor="middle">?</text><rect x="360.0" y="83.0" width="90.0" height="152.0" rx="0" fill="#b7950b" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="405.0" y="75.0" font-size="14" font-weight="700" fill="#b7950b" text-anchor="middle">?</text><rect x="517.5" y="209.7" width="90.0" height="25.3" rx="0" fill="#c0392b" fill-opacity="0.6" stroke="none" stroke-width="1.0"/><text x="562.5" y="201.7" font-size="14" font-weight="700" fill="#c0392b" text-anchor="middle">?</text><text x="400.0" y="282.0" font-size="11.5" fill="#566573" text-anchor="middle">몇 주 만으로는 차이가 작을 수 있다 : 차이가 없다는 것도 결과다</text><text x="400.0" y="300.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="middle">체크섬 오류가 0 이 아니면 : 드라이브가 ECC 로도 못 고친 데이터</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 몇 주 보관으로도 읽기가 느려진다</td><td>ret-check 의 스캔이 ret-write 직후 (또는 실험 2 의 fresh) 보다 느리고, <code>max_ms</code> 꼬리가 길다</td></tr>
<tr><td>H2 ECC 가 아직 다 고친다</td><td>fio verify 의 '나쁜 블록' = 0</td></tr>
<tr><td>H3 닳은 정도가 클수록 효과가 크다</td><td>(실험 8 중간에 한 번 더 했을 때) 차이가 커진다</td></tr>
</tbody></table></div>

## 절차

```
# 0일 : 전체를 1 MiB 순차로 쓰되, 4 KiB 마다 crc32c 체크섬 머리말을 넣는다
$ sudo ./lab.sh ret-write
$ sudo poweroff                 # 끄고, 드라이브의 SATA 전원 케이블을 뺀다 (또는 드라이브를 꺼낸다)

# 보관 : 2–4주. 날짜와 보관 장소 (대략의 온도) 를 적어 둔다

# N일 : 다시 연결하고 켠 뒤, 다른 것을 하기 전에 바로
$ sudo ./lab.sh ret-check
```

`ret-check` 가 하는 일 (쓰지 않는다) :
1. SMART 기록
2. **전체 스캔** (256 MiB 구간 전부) : 보관한 데이터를 '처음' 읽는 속도와 가장 느린 읽기. 두 번째 읽기는 펌웨어가 이미 고쳐 썼을 수 있으므로 이것이 먼저다
3. fio `--verify_only` : 모든 4 KiB 블록의 체크섬 확인. 틀린 블록 수를 `verify-summary.txt` 에 적는다
4. SMART 기록 (187, 195 가 늘었는지)

<div class="warn" markdown="1">
- 보관 중에 컴퓨터를 켜야 하면 **드라이브의 전원 케이블을 뺀 채로** 켠다. 전원이 들어가면 펌웨어가 백그라운드에서 데이터를 고쳐 쓸 수 있다.
- 따뜻한 곳은 누설을 빠르게 하지만 일부러 가열하지는 않는다 (방 온도면 된다). 온도를 적어 두면 해석에 도움이 된다.
- 비교 기준이 되는 '0일' 의 스캔이 필요하면, `ret-write` 직후 `sudo ./lab.sh scan ret-day0` 를 한 번 하고 끈다 (선택).
</div>

## 결과 읽는 법

```
$ R=~/Ryu/old_ssd_results
$ python3 plot.py ret.png $R/*-scan-fresh/scan.csv=fresh $R/*-ret-check/scan.csv=weeks $R/*-scan-old/scan.csv=years
$ cat $R/*-ret-check/verify-summary.txt
$ python3 smartdiff.py $(ls -d $R/*-ret-check | tail -1)
```

세 곡선 (막 쓴 · 몇 주 · 몇 년) 을 한 그림에 놓는 것이 목표다. 세 곡선 모두 같은 SATA 연결에서 잰다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/6-waf/' | relative_url }}">← 6. WAF (SMART)</a><a href="{{ '/old-ssd-experiments/8-endurance/' | relative_url }}">8. 끝까지 쓰기 →</a></div>
