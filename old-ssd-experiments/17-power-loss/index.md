---
layout: default
title: 17. 전원 차단
permalink: /old-ssd-experiments/17-power-loss/
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

# 17. 전원 차단 : '저장했다' 고 한 데이터는 정말 남나

<div class="glance">
<b>목표</b><span>번호를 매긴 기록을 쓰며 일정량마다 FLUSH 하고, 쓰는 도중 (또는 쓰기를 마치고 쉬는 동안) 드라이브의 전원을 갑자기 끊는다. 다시 켠 뒤, FLUSH 가 '끝났다' 고 대답한 기록이 모두 살아 있는지 확인한다</span>
<b>보는 FTL 개념</b><span>휘발성 쓰기 캐시, FLUSH 의 약속, 매핑 표의 저장 (journal), TLC 의 paired page (나중 쓰기가 끊기면 예전 데이터가 상함), 전원이 돌아온 뒤의 복구</span>
<b>지우나?</b><span>예. 그리고 <b>드라이브가 망가질 수 있다</b> (매핑 표가 깨지면 인식되지 않는다). 그래서 실험 18 앞, 다른 실험을 다 마친 뒤에 한다</span>
<b>연결</b><span><b>USB 어댑터</b> (어댑터의 USB 선을 뽑으면 = 전원 차단). 이 실험은 TRIM 이 필요 없다</span>
<b>시간</b><span>한 번에 5–15분. 5–10번 되풀이</span>
<b>명령</b><span><code>sudo ./lab.sh pl-write</code>, (전원을 끊고 다시 연결한 뒤) <code>sudo ./lab.sh pl-check 결과폴더</code></span>
</div>

## 배경

[실험 7](/old-ssd-experiments/7-flush/) 에서 본 것처럼, 드라이브는 쓰기를 DRAM 에 받고 먼저 '끝났다' 고 한다. FLUSH 를 받으면 그때까지의 것을 NAND 에 쓰고 대답한다. 따라서 **FLUSH 가 대답한 뒤의 데이터는 전원이 끊겨도 남아야 한다.** 파일 시스템과 데이터베이스는 모두 이 약속 위에 서 있다.

소비자용 SSD 는 전원이 끊기는 순간 캐시를 비울 축전기가 없다. 그래서 잘 만든 펌웨어는 FLUSH 를 정직하게 지키고, 끊긴 뒤 다시 켤 때 매핑 표를 복구한다. 덜 만든 펌웨어는 :
- FLUSH 에 너무 빨리 대답하거나 (캐시를 비우지 않고)
- TLC 의 한 셀에 3비트를 나눠 쓰는 중에 끊기면, **예전에 쓴 비트까지 상하게** 하거나 (paired page)
- 매핑 표를 잃어 드라이브 전체가 사라지기도 한다

## 측정 방법 (`plcheck.py`)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td>쓰기</td><td>드라이브의 처음부터 4 KiB 기록을 차례로 쓴다. 기록 i 에는 '이번 실행의 번호 (run id) · i · 체크섬 · 무작위 내용' 이 들어 있다. 1 MiB 씩 O_DIRECT 로 쓴다</td></tr>
<tr><td>약속</td><td>8 MiB 마다 <code>fdatasync</code> (커널이 FLUSH CACHE 를 보냄). 대답이 오면 '여기까지 확인됨 (acked)' 을 <strong>이 컴퓨터의 디스크</strong> 의 <code>acked.csv</code> 에 적고 fsync</td></tr>
<tr><td>끊기</td><td>Ryu 가 아무 때나 어댑터의 USB 선을 뽑는다. 쓰기가 오류로 멈춘다</td></tr>
<tr><td>확인</td><td>다시 꽂고 <code>pl-check</code> : 칸마다 ok (이번 기록, 체크섬 맞음) · zero · other (이번 기록이 아님) · torn (반쯤 쓴 기록) 으로 나눈다</td></tr>
<tr><td>판정</td><td>acked 아래 칸은 <strong>모두 ok</strong> 여야 한다. 하나라도 아니면 '약속한 데이터를 잃었다'. acked 위쪽은 몇 칸이 살아남았는지 (FLUSH 하지 않은 꼬리)</td></tr>
</tbody></table></div>

`pl-write 숫자` 로 하면 그 GB 만큼 쓰고 FLUSH 한 뒤 **멈춰서 기다린다.** 그때 끊으면 '호스트는 쉬지만 드라이브는 안에서 일하는 중' (SLC 에서 TLC 로 옮기기, GC) 에 전원이 끊긴다. 이것이 paired page 문제를 일으키기 쉬운 순간이다.

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 FLUSH 는 지켜진다</td><td>모든 실행에서 'every acknowledged record survived'</td></tr>
<tr><td>H2 FLUSH 하지 않은 꼬리는 일부만 남는다</td><td>acked 위쪽의 ok 가 0 – 수 MB (캐시와 SLC 에 있던 만큼)</td></tr>
<tr><td>H3 쓰는 중에 끊어도 반쯤 쓴 기록은 드물다</td><td>torn 이 0 이거나 경계의 몇 칸뿐</td></tr>
<tr><td>H4 쉬는 동안 끊는 것이 더 위험하다</td><td><code>pl-write 20</code> 뒤 쉬는 동안 끊은 실행에서만 acked 아래가 상한다면 : 안에서 옮기던 데이터 (paired page)</td></tr>
<tr><td>H5 드라이브는 살아 돌아온다</td><td>매번 다시 인식되고, SMART 의 'Unsafe shutdown' 류 값 (Samsung 은 235 POR_Recovery_Count) 이 1씩 는다</td></tr>
</tbody></table></div>

## 절차

드라이브를 USB 어댑터로 옮긴다 (컴퓨터를 끄고 SATA 에서 뺀 뒤 어댑터에 끼운다). 어댑터가 따로 전원 어댑터를 쓰는 종류라면 그 전원을 뽑아도 된다.

```
# 1. 쓰는 중에 끊기 (3–5번 되풀이, 매번 다른 순간에)
$ sudo ./lab.sh pl-write
   (화면에 acked … GB 가 올라가는 것을 보다가, 아무 때나 어댑터의 USB 선을 뽑는다)
   (10초 기다렸다 다시 꽂는다. lsblk 에 다시 보일 때까지 기다린다)
$ sudo ./lab.sh pl-check ~/Ryu/old_ssd_results/<방금 폴더>-pl-write

# 2. 다 쓰고 쉬는 동안 끊기 (2–3번)
$ sudo ./lab.sh pl-write 20
   ('now idle' 이 나온 뒤 0초, 10초, 60초 … 지나서 뽑는다 : 매번 다르게)
$ sudo ./lab.sh pl-check ~/Ryu/old_ssd_results/<방금 폴더>-pl-write
```

<div class="warn" markdown="1">
- 뽑기 전에, 이 드라이브가 마운트되지 않았는지 확인한다 (`lab.sh` 가 확인한다). 다른 USB 디스크의 선을 뽑지 않게 **선에 표시** 를 해 둔다.
- 메인보드 SATA 에서 전원 케이블을 뽑는 방법도 있지만, 켜진 컴퓨터의 전원 케이블을 뽑고 꽂는 일은 권하지 않는다.
- 다시 꽂았는데 드라이브가 보이지 않거나 용량이 이상하면 (`lsblk`) : 컴퓨터를 껐다 켜 본다. 그래도 안 되면 그것이 결과다 (H5 실패) : 실험 18 대신 실험 19 로 간다.
- USB 어댑터가 FLUSH (SYNCHRONIZE CACHE) 를 드라이브까지 전하지 않는 것이 문제의 원인일 수도 있다. acked 아래가 상하면 다른 어댑터로 한 번 더 해 본다.
</div>

## 결과 읽는 법

`pl-check` 가 바로 판정을 출력하고 `check.txt` 로 남긴다. 아래는 파일로 한 자체 시험의 실제 출력이다 : 일부러 3000번째 기록을 망가뜨려서, acked 아래의 손상을 잡아내는지 확인했다.

```
run id e822461ceb14bc12, records of 4096 B
acknowledged (FLUSH returned): 10240 records = 41.9 MB
below the acknowledged mark : ok 10239, zero 0, other 0, torn 1
above it (unflushed tail)   : ok 6144, zero 33617, other 0, torn 0
last ok record               : 16383 (25.2 MB past the mark)
RESULT: LOST ACKNOWLEDGED DATA, first bad slot 3000 (12.3 MB into the drive)
```

드라이브가 약속을 지켰다면 마지막 줄이 `RESULT: every acknowledged record survived.` 다.
Claude 가 모든 실행의 `check.txt` 와 SMART 를 모아 표로 만든다 : 끊은 순간 (쓰는 중 / 쉰 지 몇 초), acked 아래의 결과, 꼬리의 길이.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/16-retention/' | relative_url }}">← 16. Retention</a><a href="{{ '/old-ssd-experiments/18-endurance/' | relative_url }}">18. 끝까지 쓰기 →</a></div>
