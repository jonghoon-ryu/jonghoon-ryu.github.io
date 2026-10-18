---
layout: default
title: 6. 쓰기 크기 · 정렬
permalink: /old-ssd-experiments/6-write-size/
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

# 6. 쓰기 크기와 정렬 : 4 KiB 보다 작게, 4 KiB 에서 어긋나게 쓰면

<div class="glance">
<b>목표</b><span>512 B 부터 64 KiB 까지 랜덤 쓰기의 속도 · 지연을 재고, 4 KiB 경계에서 512 B 어긋난 4 KiB 쓰기와 비교해서 FTL 의 매핑 단위와 '읽고-고치고-쓰기' 비용을 밖에서 찾는다</span>
<b>보는 FTL 개념</b><span>매핑 단위 (4 KiB), read-modify-write, 섹터 크기 (512 B 논리 / 4 KiB 내부), 파티션 정렬</span>
<b>지우나?</b><span>예</span>
<b>연결</b><span>SATA</span>
<b>시간</b><span>약 40분 (채우기 15분 + 크기 18개 × 1.5분)</span>
<b>명령</b><span><code>sudo ./lab.sh wsize</code></span>
</div>

## 배경 : 드라이브는 512 B 를 받지만 4 KiB 로 기억한다

호스트에게 이 드라이브의 섹터는 512 바이트다 (`lsblk -o PHY-SEC,LOG-SEC`). 그러나 FTL 의 매핑 표는 **4 KiB 마다 한 줄** 이 보통이다 (실험 19 의 DRAM 계산 참고).
그러면 512 B 를 쓰는 요청은 이렇게 된다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>요청</th>
<th>FTL 이 할 일</th>
</tr></thead><tbody>
<tr><td>4 KiB, 4 KiB 경계에 맞춤</td><td>새 4 KiB 자리에 쓰고 표의 한 줄을 바꾼다</td></tr>
<tr><td>512 B</td><td>그 4 KiB 의 나머지 3.5 KiB 를 <strong>읽어서</strong> 합친 뒤 새 4 KiB 자리에 쓴다 (read-modify-write)</td></tr>
<tr><td>4 KiB, 512 B 어긋남</td><td>두 개의 4 KiB 에 걸친다 : 둘 다 읽고-고치고-쓰기</td></tr>
<tr><td>8 KiB · 16 KiB …</td><td>4 KiB 여러 개. NAND 페이지 (8 KiB 또는 16 KiB 로 짐작) 를 한 번에 채울 수 있다</td></tr>
</tbody></table></div>

옛날에 'Windows XP 의 파티션은 63 섹터에서 시작해서 SSD 에서 느리다' 고 했던 이유가 이 어긋남이다. 지금 도구들은 파티션을 1 MiB 경계에 맞춘다.

## 가설과 예상

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>가설</th>
<th>맞다면 보일 것</th>
</tr></thead><tbody>
<tr><td>H1 매핑 단위는 4 KiB 다</td><td>512 B · 1 KiB · 2 KiB 의 IOPS 가 4 KiB 보다 높지 않다 (오히려 낮다), QD1 지연이 4 KiB 보다 길다</td></tr>
<tr><td>H2 어긋난 4 KiB 는 두 배 일이다</td><td><code>mis4k</code> 의 IOPS 가 <code>bs4k</code> 의 절반쯤, 지연은 두 배쯤</td></tr>
<tr><td>H3 큰 쓰기는 MB/s 가 오른다</td><td>4 → 64 KiB 로 MB/s 가 오르다가 어느 크기에서 평평해진다 (그 크기 ≈ 한 번에 프로그램하는 단위 × 병렬성)</td></tr>
</tbody></table></div>

`wsize` 는 드라이브를 먼저 다 채운 뒤 측정한다 : 512 B 쓰기의 '나머지를 읽기' 가 진짜 NAND 를 읽게 하려고. 각 측정은 30초로 짧아서 대부분 SLC 버퍼 안에서 일어난다. 그래도 크기끼리의 비교는 공정하다 (모두 같은 조건).

## 절차

```
$ sudo ./lab.sh wsize
```

### `sudo ./lab.sh wsize` 가 하는 일

이 명령은 **120GB SSD 가 안에서 실제로 어떤 크기로 일하는지**, 그리고 그보다 작게 · 어긋나게 쓰면 얼마나 비싼지를 찾는다. 컴퓨터에는 512 바이트 섹터로 보이지만, FTL 의 매핑 표는 거의 틀림없이 **4 KiB 단위** 다. 그래서 :
- **512 B 쓰기** : FTL 이 그 4 KiB 의 나머지를 **읽어서**, 새 512 B 를 합친 뒤, 4 KiB 전체를 새 자리에 쓴다 (read-modify-write). 4 KiB 를 통째로 쓰는 것보다 일이 많다
- **4 KiB 쓰기인데 4 KiB 경계에서 512 B 어긋남** : 단위 **두 개** 에 걸친다. 둘 다 읽고-고치고-쓰기 : 일이 약 두 배

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>단계</th>
<th>하는 일</th>
<th>왜</th>
</tr></thead><tbody>
<tr><td>1. 안전 확인 + <code>0389K</code> 입력</td><td>늘 하던 대로</td><td>입력하기 전에는 아무것도 지우지 않는다</td></tr>
<tr><td>2. 전체 TRIM, 2분 쉼</td><td>| 깨끗한 출발점</td></tr>
<tr><td>3. <strong>드라이브 전체를 채운다</strong> (1 MiB 순차, 약 14분)</td><td>모든 주소에 데이터가 있게</td><td>512 B 쓰기가 정말로 옛 데이터를 읽어 합쳐야 하게</td></tr>
<tr><td>4. SMART 기록</td><td>|</td></tr>
<tr><td>5. <strong>앞 8 GiB 안의 랜덤 쓰기</strong>, 각 30초, 사이 60초 쉼 : 크기 <strong>512 B · 1 · 2 · 4 · 8 · 16 · 32 · 64 KiB</strong>, 크기마다 <strong>QD1 과 QD32</strong></td><td>측정 16번</td><td>크기 지도. QD1 은 쓰기 하나의 시간, QD32 는 처리량</td></tr>
<tr><td>6. <strong>어긋난 4 KiB 쓰기</strong> (<code>--blockalign=4k --offset=512</code>), QD1 과 QD32</td><td>측정 2번</td><td>걸치는 경우</td></tr>
<tr><td>7. SMART 기록, <code>summary.csv</code></td><td>측정마다 한 줄 : IOPS, MB/s, 지연 percentile |</td></tr>
</tbody></table></div>

- **60초 쉼** 은 실행 사이에 SLC 버퍼가 비게 해서, 측정마다 비슷한 상태에서 시작하게 한다. [실험 5](/old-ssd-experiments/5-perf-map/) 에서 본 것처럼 쓰기는 그 앞에 무엇을 썼는지에 크게 좌우되기 때문이다.
- **앞 8 GiB 안** 에서만 쓰는 것은 모든 측정이 같은 구간에서 일어나게 하려는 것이다.
- **시간** : 약 **40분** (채우기 14분 + 18번 × 90초). 모두 합쳐 약 25 – 30 GB 를 쓴다.

**실제로 왜 중요한가** : 파티션이 1 MiB (섹터 2048) 에서 시작하는 이유가 이것이다 (이 컴퓨터의 디스크들도 그렇다 : [SSD Q&A 11절](/old-ssd-experiments/ssd-tutorial/)). 옛 Windows XP 의 파티션은 섹터 63 에서 시작해서, SSD 에서는 4 KiB 쓰기마다 단위 두 개에 걸쳐 느렸다.

## 결과 읽는 법

```
$ column -s, -t $(ls -d ~/Ryu/old_ssd_results/*-wsize | tail -1)/summary.csv
```

1. **QD1 지연 – 크기** : 4 KiB 에서 가장 낮고 그보다 작으면 다시 오르면 H1.
2. **`mis4k` ÷ `bs4k`** : IOPS 비와 지연 비 (H2).
3. **MB/s – 크기** : 평평해지는 지점 (H3). QD32 와 QD1 을 따로 본다.
4. 실험 5 의 `randwrite 4k` 칸과 같은 값이 나오는지 (같은 조건이면 같아야 한다).

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/5-perf-map/' | relative_url }}">← 5. 성능 지도</a><a href="{{ '/old-ssd-experiments/7-flush/' | relative_url }}">7. 쓰기 캐시 · FLUSH →</a></div>
