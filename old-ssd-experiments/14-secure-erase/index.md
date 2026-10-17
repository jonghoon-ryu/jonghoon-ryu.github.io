---
layout: default
title: 14. Secure Erase
permalink: /old-ssd-experiments/14-secure-erase/
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

# 14. ATA Secure Erase : 드라이브가 스스로 지우는 데 걸리는 시간

<div class="glance">
<b>목표</b><span>꽉 차고 GC 로 지친 드라이브에 ATA SECURITY ERASE UNIT 을 보내, 걸린 시간 · 지운 뒤의 내용 (모두 0?) · 쓰기 속도가 처음 상태로 돌아오는지를 재고, <code>blkdiscard</code> (TRIM) 와 비교한다</span>
<b>보는 FTL 개념</b><span>블록 지우기 (erase), 매핑 표 초기화, 자체 암호화 드라이브의 암호 키 교체 (crypto erase), FOB 상태 되돌리기</span>
<b>지우나?</b><span>예 (그것이 실험이다)</span>
<b>연결</b><span>SATA (USB 어댑터는 보안 명령을 막는 일이 많다)</span>
<b>시간</b><span>채우기 15분 + 사전 쓰기 10분 + 지우기 (드라이브가 말하는 시간, 보통 몇 분) + 확인 15분</span>
<b>명령</b><span><code>sudo ./lab.sh secerase</code>, <code>sudo ./lab.sh secerase enhanced</code></span>
</div>

## 배경

`blkdiscard` (TRIM) 는 '이 LBA 들은 이제 안 쓴다' 는 알림일 뿐이다. 드라이브는 매핑을 지우고 블록은 나중에 (GC 가) 지운다.
**Secure Erase** 는 ATA 표준 명령으로, 드라이브에게 '사용자 영역 전부를 지금 지워라' 고 시킨다. 컨트롤러가 무엇을 하는지는 드라이브마다 다르다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>방법</th>
<th>하는 일</th>
<th>걸리는 시간</th>
</tr></thead><tbody>
<tr><td>모든 블록 지우기</td><td>NAND 블록을 하나씩 erase</td><td>블록 수 × 지우기 시간 ÷ 병렬성 : 수십 초–몇 분</td></tr>
<tr><td>암호 키 교체 (crypto erase)</td><td>항상 암호화하는 드라이브 (SED) 는 키만 새로 만든다 : 옛 데이터는 읽어도 의미 없는 값</td><td>거의 즉시. 보통 매핑 초기화 · 블록 지우기도 같이 한다</td></tr>
<tr><td>Enhanced</td><td>표준상 '제조사가 정한 무늬로 덮어쓰기' 도 포함 (예비 영역 등)</td><td>드라이브가 말하는 시간</td></tr>
</tbody></table></div>

840 EVO 는 AES-256 으로 항상 암호화하는 드라이브로 알려져 있다 (확인 필요). 그렇다면 Secure Erase 는 키 교체를 포함할 것이다.

## 꼭 알아야 할 것 : frozen, 비밀번호

<div class="warn" markdown="1">
- **frozen** : 많은 BIOS 가 부팅할 때 보안 명령을 잠근다 (`hdparm -I` 의 Security 아래 `frozen`). 그러면 `lab.sh` 가 멈춘다. 푸는 법 : `sudo systemctl suspend` 로 절전했다가 깨운다 (드라이브가 전원을 다시 받으며 잠금이 풀린다). 그래도 frozen 이면 드라이브의 SATA 전원을 잠깐 뽑았다 꽂는 방법이 있지만, 실험 17 처럼 USB 어댑터에서 하는 편이 안전하다 (그런데 어댑터가 보안 명령을 막을 수 있다).
- **비밀번호** : Secure Erase 를 하려면 먼저 사용자 비밀번호를 정해야 한다 (표준이 그렇다). `lab.sh` 는 임시 비밀번호 `lab` 을 쓰고, 지우기가 성공하면 비밀번호도 사라진다.
- **중간에 끊기면** (전원, Ctrl+C) 비밀번호가 남아 드라이브가 **잠긴다**. 풀기 :

```
$ D=/dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K
$ sudo hdparm --user-master u --security-unlock lab $D
$ sudo hdparm --user-master u --security-disable lab $D
```
</div>

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 지우기는 빠르다</td><td><code>erase_seconds</code> 가 <code>hdparm -I</code> 의 예상 시간 (예 : <code>2min for SECURITY ERASE UNIT</code>) 이하. 몇 초라면 키 교체 + 매핑 초기화</td></tr>
<tr><td>H2 지운 뒤에는 모두 0 으로 읽힌다</td><td><code>scan.csv</code> 의 <code>zero_frac</code> 이 모든 구간에서 1 (매핑이 없으니 NAND 를 안 읽고 0)</td></tr>
<tr><td>H3 FOB 로 돌아온다</td><td><code>after-4k</code> 의 처음 몇 분 IOPS 가 <code>before-4k</code> (지친 상태) 보다 훨씬 높고, 실험 8 의 시작 부분과 같다</td></tr>
<tr><td>H4 블록을 실제로 지웠다면 마모가 는다</td><td>SMART 177 이 +1 쯤 (모든 블록 한 번 지움). 그대로면 지우기를 미루거나 하지 않았다</td></tr>
<tr><td>H5 enhanced 는 다르다</td><td><code>secerase enhanced</code> 의 시간이 확실히 다르면, 두 명령의 구현이 다르다</td></tr>
</tbody></table></div>

## 절차

```
$ sudo ./lab.sh features              # Security 부분을 먼저 본다 (실험 2 에서 이미 했다면 생략)
$ sudo ./lab.sh secerase              # normal
$ sudo ./lab.sh secerase enhanced     # 선택 : 다시 채우고 지친 상태에서 enhanced
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td>0</td><td>Security 상태 확인 : supported, not enabled, not frozen 이 아니면 멈춘다</td></tr>
<tr><td>1</td><td>1 MiB 순차로 전체를 채우고, 4 KiB 랜덤 쓰기 10분 (<code>before-4k</code>) : 꽉 차고 지친 상태</td></tr>
<tr><td>2</td><td>SMART 기록, 임시 비밀번호 설정</td></tr>
<tr><td>3</td><td><code>hdparm --security-erase</code> (또는 <code>-enhanced</code>) : 드라이브가 끝낼 때까지 기다리며 시간을 잰다</td></tr>
<tr><td>4</td><td>Security 상태 (비밀번호가 사라졌나), SMART 기록</td></tr>
<tr><td>5</td><td>스캔 (256 MiB 마다 8 MiB) : 모두 0 인가</td></tr>
<tr><td>6</td><td>4 KiB 랜덤 쓰기 10분 (<code>after-4k</code>) : 빈 블록이 돌아왔나</td></tr>
</tbody></table></div>

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-secerase-normal | tail -1)
$ grep erase_seconds $D/meta.txt
$ python3 plot.py se.png $D/before-4k_iops.log=before $D/after-4k_iops.log=after
$ python3 smartdiff.py $D
```

비교 기준 : 실험 8 은 매번 `blkdiscard` 로 시작한다. 실험 8 의 처음 몇 분과 `after-4k` 가 같은 높이라면, 이 드라이브에서 TRIM 전체와 Secure Erase 는 성능상 같은 결과를 낸다 (차이는 '데이터를 정말 지웠나' 쪽에 있다).

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/13-interference/' | relative_url }}">← 13. 읽기 · 쓰기 간섭</a><a href="{{ '/old-ssd-experiments/15-read-disturb/' | relative_url }}">15. Read disturb →</a></div>
