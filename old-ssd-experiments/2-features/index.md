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
<th>이 정보를 쓰는 실험 (번호)</th>
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

## 결과

<div class="result" markdown="1">
### 1단계 : `features`

2026.10.18 09:41, 결과 폴더 `20261018-094145-features`.

**ATA 기능** (`hdparm -I`, `hdparm -N -W -A -B`)

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>보이는 것</th>
<th>뜻</th>
<th>이 정보를 쓰는 실험 (번호)</th>
</tr></thead><tbody>
<tr><td><code>Data Set Management TRIM supported (limit 8 blocks)</code></td><td>TRIM 지원. 명령 하나에 범위 8개 블록 (블록 하나에 범위 64개)</td><td>4</td></tr>
<tr><td><code>Deterministic read ZEROs after TRIM</code> 줄 <strong>없음</strong></td><td>드라이브는 'TRIM 한 곳은 0' 을 약속하지 않는다 (커널은 <code>zeroaftertrim</code> 으로 0 이라고 믿는다)</td><td>4</td></tr>
<tr><td><code>Device encrypts all user data</code></td><td>항상 암호화하는 드라이브 (SED)</td><td>14</td></tr>
<tr><td>Security : <code>supported</code> · <code>not enabled</code> · <code>not locked</code> · <strong><code>frozen</code></strong> · <code>supported: enhanced erase</code> · <code>2min … 8min</code></td><td>Secure Erase 를 할 수 있지만 지금은 BIOS 가 잠갔다. 드라이브가 말하는 시간 : 보통 2분, enhanced 8분</td><td>14</td></tr>
<tr><td><code>max sectors = 234441648/234441648, HPA is disabled</code></td><td>보이는 크기 = 진짜 크기. 숨긴 영역 없음</td><td>10</td></tr>
<tr><td><code>write-caching = 1 (on)</code>, <code>look-ahead = 1 (on)</code></td><td>쓰기 캐시 켜짐, 미리 읽기 켜짐</td><td>7</td></tr>
<tr><td><code>APM_level = not supported</code></td><td>전원 관리 (APM) 설정은 없다 : SSD 에서는 흔하다</td><td>—</td></tr>
<tr><td><code>Queue depth: 32</code>, <code>Native Command Queueing (NCQ)</code>, <code>Gen3 (6.0Gb/s)</code></td><td>명령 32개까지 한꺼번에, SATA 3</td><td>5</td></tr>
<tr><td><code>Logical / Physical Sector size: 512 bytes</code></td><td>호스트에는 512 B 섹터로 보인다 (안쪽의 4 KiB 매핑 단위는 실험 6 이 찾는다)</td><td>6</td></tr>
</tbody></table></div>

**SMART 로그**

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>로그</th>
<th>내용</th>
<th>읽는 법</th>
</tr></thead><tbody>
<tr><td>오류 로그 (<code>error</code>, <code>xerror</code>)</td><td><code>No Errors Logged</code></td><td>드라이브가 기억하는 명령 오류가 하나도 없다 : 13년 동안, 그리고 오늘의 느린 읽기에서도</td></tr>
<tr><td>자가 진단 기록 (<code>selftest</code>)</td><td><code>No self-tests have been logged</code></td><td>한 번도 자가 진단을 한 적이 없다 : 2단계가 첫 번째다</td></tr>
<tr><td>장치 통계 (<code>devstat</code>)</td><td><code>not supported</code></td><td>이 드라이브에는 없다 (더 새 드라이브의 기능)</td></tr>
<tr><td>SATA 링크 (<code>sataphy</code>, 켠 뒤부터 센 값)</td><td>CRC · R_ERR 오류 모두 0. <code>PhyRdy → PhyNRdy</code> 31번, <code>COMRESET</code> 2번</td><td>링크 오류 없음. 31번은 오류가 아니라 링크가 쉬는 상태로 들어갔다 나온 횟수 (link power management), COMRESET 2번은 부팅 때의 초기화</td></tr>
<tr><td>로그 목록 (<code>directory</code>)</td><td>Samsung 전용 로그 <code>0xa1</code>, <code>0xce</code>, <code>0xde</code> 가 있다</td><td>내용은 공개되어 있지 않다 (펌웨어 내부 기록)</td></tr>
</tbody></table></div>

**온도 기록** (`scttemp`, 10분마다) : 이번 실험들 동안의 드라이브 온도가 그대로 남았다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>시각</th>
<th>온도</th>
<th>그때 한 일</th>
</tr></thead><tbody>
<tr><td>08:20 – 08:50</td><td>28 → 31 °C</td><td>켠 뒤, 실험 0 (<code>check</code>)</td></tr>
<tr><td>09:00 – 09:10</td><td><strong>38 – 40 °C</strong></td><td>실험 1 파일별 측정 (느린 읽기가 계속됨)</td></tr>
<tr><td>09:20</td><td>33 °C</td><td>쉬는 시간, 다시 읽기</td></tr>
<tr><td>09:30</td><td><strong>38 °C</strong></td><td>실험 1 드라이브 전체 지도</td></tr>
<tr><td>09:40</td><td>31 °C</td><td>쉼</td></tr>
</tbody></table></div>

**읽기만 하는데도 7–9 °C 가 오른다.** 정상 SSD 의 읽기는 거의 열을 내지 않는다. 이 드라이브는 읽기 하나에 여러 번 다시 읽으므로 (read retry) 컨트롤러와 NAND 가 쉬지 않고 일한다. 실험 1 의 해석과 맞는 독립된 증거다.

**가설 확인 (1단계까지)**

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>결과</th>
</tr></thead><tbody>
<tr><td>H1 TRIM 뒤 0 이 보장된다</td><td><strong>아니다</strong> (약속 줄이 없다). 실제로 0 이 나오는지는 실험 4</td></tr>
<tr><td>H2 Secure Erase 를 할 수 있다</td><td><strong>할 수 있다, 단 지금은 frozen</strong> : 실험 14 에서 절전 → 깨우기</td></tr>
<tr><td>H3 자가 진단이 예상보다 오래 걸린다</td><td>2단계 (<code>selftest long</code>) 에서 확인. 권장 시간 70분</td></tr>
<tr><td>H4 '믿을 수 없게 됨' 의 흔적이 로그에 있다</td><td><strong>아니다</strong> : 오류 로그 · 링크 오류 모두 0. 남은 흔적은 '느림' 과 '열' 뿐</td></tr>
</tbody></table></div>

### 2단계 : `selftest long`

아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/1-old-data/' | relative_url }}">← 1. 오래된 데이터 읽기</a><a href="{{ '/old-ssd-experiments/3-slc-cache/' | relative_url }}">3. SLC 캐시 →</a></div>
