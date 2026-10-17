---
layout: default
title: 2. 기능 · 자가 진단
permalink: /old-ssd-experiments/2-features/
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

# 2. 드라이브가 스스로 알려 주는 것 : ATA 기능, 로그, 자가 진단

<div class="glance">
<b>목표</b><span>지우기 전에, 드라이브가 보고하는 모든 기능 · 로그 · 통계를 남기고, 드라이브 스스로 전체를 검사하게 해서 (SMART 자가 진단) 걸린 시간과 결과를 본다</span>
<b>보는 것</b><span>ATA 기능 목록, 보안 (Secure Erase) 상태, HPA, 쓰기 캐시, SMART 오류 · 자가 진단 로그, 장치 통계, 온도 기록, SATA 링크 오류</span>
<b>지우나?</b><span>아니오. 읽기만 한다 (자가 진단은 드라이브 안에서 읽기만 한다)</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>features 1분, 자가 진단 (long) 은 드라이브가 알려 주는 시간 (보통 수십 분)</span>
<b>명령</b><span><code>sudo ./lab.sh features</code>, <code>sudo ./lab.sh selftest long</code></span>
</div>

## 왜 지금 하나

뒤의 실험들이 쓰는 기능 (TRIM 뒤 0 읽기, Secure Erase, 쓰기 캐시 끄기, HPA) 을 이 드라이브가 정말 지원하는지 **먼저 확인** 한다. 그리고 드라이브가 기억하는 과거 (오류 로그, 자가 진단 기록, 온도 기록) 는 지우는 실험을 하면 섞이거나 덮인다 : 지금 남겨야 한다.

**자가 진단을 실험 1 뒤에 하는 이유** : long 자가 진단은 드라이브가 안에서 모든 LBA 를 읽는다. 오래된 데이터를 읽는 일이라, 펌웨어가 그 블록들을 다시 써 버릴 수 있다. 실험 1 의 측정을 먼저 끝낸다.

## 1단계 : 기능과 로그 모으기

```
$ sudo ./lab.sh features
```

하는 일 (아무것도 쓰지 않는다) :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>명령</th>
<th>저장 파일</th>
<th>보는 것</th>
</tr></thead><tbody>
<tr><td><code>hdparm -I</code></td><td><code>hdparm-I.txt</code></td><td>ATA 기능 전체 : 지원 (<code>*</code> 가 붙으면 켜짐)</td></tr>
<tr><td><code>hdparm -N -W -A -B</code></td><td><code>hdparm-NWAB.txt</code></td><td>보이는 최대 섹터 / 진짜 최대 (HPA), 쓰기 캐시, 미리 읽기, 전원 관리 (APM)</td></tr>
<tr><td><code>smartctl -x</code></td><td><code>smart-features.*</code></td><td>속성 표와 모든 로그</td></tr>
<tr><td><code>smartctl -l devstat</code></td><td><code>smart-log-devstat.txt</code></td><td>장치 통계 : 전원 켠 횟수 · 시간, 읽고 쓴 섹터, 보고한 고치지 못한 오류</td></tr>
<tr><td><code>smartctl -l error</code> · <code>xerror</code></td><td><code>smart-log-error.txt</code> · <code>xerror</code></td><td>드라이브가 기억하는 최근 오류 (시각은 전원 켠 시간 기준)</td></tr>
<tr><td><code>smartctl -l selftest</code></td><td><code>smart-log-selftest.txt</code></td><td>지난 자가 진단 기록 (Windows 시절 것이 남아 있을 수 있다)</td></tr>
<tr><td><code>smartctl -l scttemp</code></td><td><code>smart-log-scttemp.txt</code></td><td>온도 기록 (지원하면)</td></tr>
<tr><td><code>smartctl -l sataphy</code></td><td><code>smart-log-sataphy.txt</code></td><td>SATA 링크의 CRC 오류 · 재접속 횟수 (케이블 · 어댑터 문제)</td></tr>
</tbody></table></div>

`hdparm -I` 에서 특히 볼 줄 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>줄 (예)</th>
<th>뜻</th>
<th>어느 실험</th>
</tr></thead><tbody>
<tr><td><code>Data Set Management TRIM supported (limit 8 blocks)</code></td><td>TRIM 지원, 명령 하나에 몇 개 범위</td><td>4</td></tr>
<tr><td><code>Deterministic read ZEROs after TRIM</code></td><td>TRIM 한 곳을 읽으면 반드시 0</td><td>4</td></tr>
<tr><td><code>Write cache</code> (앞에 <code>*</code>)</td><td>쓰기 캐시가 켜져 있다</td><td>7</td></tr>
<tr><td><code>Native Command Queueing (NCQ)</code>, <code>Queue depth: 32</code></td><td>동시에 받을 수 있는 명령 수</td><td>5</td></tr>
<tr><td><code>Security:</code> 아래 <code>supported</code>, <code>not enabled</code>, <code>not frozen</code>, <code>supported: enhanced erase</code>, <code>2min for SECURITY ERASE UNIT</code></td><td>Secure Erase 를 할 수 있는 상태인가, 걸린다고 말하는 시간</td><td>14</td></tr>
<tr><td><code>max sectors = 234441648/234441648, HPA is disabled</code></td><td>숨겨 둔 영역 (HPA) 이 없다</td><td>10 (덤)</td></tr>
<tr><td><code>SATA Rev 3.0</code> / <code>Gen3 signaling speed (6.0Gb/s)</code></td><td>링크 속도 : SATA 3 이면 상한 약 550 MB/s</td><td>5</td></tr>
</tbody></table></div>

## 2단계 : SMART 자가 진단

```
$ sudo ./lab.sh selftest long
```

1. `smartctl -c` 가 알려 주는 '권장 대기 시간' 을 보여 준다 (드라이브가 스스로 예상한 시간)
2. `smartctl -t long` 으로 시작하고, 30초마다 진행 (`% of test remaining`) 을 찍는다
3. 끝나면 **실제로 걸린 시간** 과 자가 진단 로그 (`Completed without error` 또는 `read failure` 와 첫 오류 LBA) 를 남긴다

자가 진단 동안에는 드라이브를 쓰지 않는다 (다른 I/O 가 있으면 진단이 늦어지거나 멈춘다).

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 TRIM 뒤 0 이 보장된다</td><td><code>Deterministic read ZEROs after TRIM</code> 줄이 있다 (실험 4 가 실제로 확인한다)</td></tr>
<tr><td>H2 Secure Erase 를 할 수 있다</td><td><code>supported</code>, <code>not enabled</code>, <code>not frozen</code> (frozen 이면 실험 14 에서 절전 → 깨우기로 푼다)</td></tr>
<tr><td>H3 오래된 데이터 때문에 자가 진단이 예상보다 오래 걸린다</td><td>실제 시간 &gt; 권장 시간. 실험 3 뒤 (새 데이터) 다시 하면 짧아진다</td></tr>
<tr><td>H4 '믿을 수 없게 됨' 의 흔적이 로그에 있다</td><td>오류 로그에 항목이 있거나, 자가 진단이 <code>read failure</code> 로 끝난다</td></tr>
</tbody></table></div>

H3 의 비교를 위해, **실험 3 (드라이브 전체를 새로 씀) 이 끝난 뒤** `sudo ./lab.sh selftest long` 을 한 번 더 한다. 같은 드라이브가 같은 일을 하는데 데이터의 나이만 다르다.

## 결과 읽는 법

```
$ D=$(ls -d ~/Ryu/old_ssd_results/*-features | tail -1)
$ less $D/hdparm-I.txt
$ grep -E "seconds|Completed|failure" ~/Ryu/old_ssd_results/*-selftest-long/{meta.txt,selftest-log.txt}
```

Claude 가 두 결과 폴더를 읽어 '지원하는 기능' 표와 '두 번의 자가 진단 시간' 을 이 페이지의 결과에 붙인다. 뒤 실험들 (4, 7, 14) 이 기대하는 기능이 없으면 그 실험의 절차를 바꾼다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/1-old-data/' | relative_url }}">← 1. 오래된 데이터 읽기</a><a href="{{ '/old-ssd-experiments/3-slc-cache/' | relative_url }}">3. SLC 캐시 →</a></div>
