---
layout: default
title: SSD Q&A
permalink: /old-ssd-experiments/ssd-tutorial/
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

# SSD Q&A : 120 GB 드라이브는 왜 111.8 GiB 로 보이나

실험할 840 EVO 의 용량은 **234,441,648 섹터 × 512 B** 다. 이 숫자 하나에서 시작해, SSD 의 용량이 어떻게 정해지는지를 차례로 따라간다 : GB 와 GiB, 왜 두 단위가 섞였나, SSD 안의 2진 NAND 와 밖에 보이는 10진 용량, 섹터 수를 정하는 IDEMA 공식, over-provisioning 과 스페어 영역, 용량을 나누는 세 층 (드라이브 · 네임스페이스 · 파티션), USB 로 붙인 NVMe, 그리고 읽을 수 없는 섹터가 생겼을 때 드라이브 · 커널 · OS 가 하는 일.

<div class="glance">
<b>이 페이지는</b><span>Claude 와 나눈 질문과 답을 다듬어 정리한 것 (2026.10.18)</span>
<b>먼저 알면 좋은 것</b><span>섹터 · LBA (<a href="/old-ssd-experiments/linux-commands/">Linux 명령</a> 페이지), FTL 이 무엇인지 대강</span>
<b>이어지는 실험</b><span><a href="/old-ssd-experiments/10-over-provisioning/">10. Over-provisioning</a>, <a href="/old-ssd-experiments/19-teardown/">19. 열어 보기</a></span>
</div>

## 1. 섹터 수에서 바이트로

드라이브는 자기 크기를 **섹터 (LBA) 수** 로 알려 준다. 840 EVO 120GB 는 234,441,648 섹터, 섹터 하나는 512 바이트다.

```
234,441,648 × 512 = 120,034,123,776 바이트
```

512 = 2⁹ 이므로, 234,441,648 을 아홉 번 두 배 하는 것과 같다.

## 2. GB 와 GiB

같은 바이트 수를 두 가지 단위로 읽을 수 있다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>단위</th><th>1 단위 =</th><th>120,034,123,776 바이트는</th></tr></thead><tbody>
<tr><td><strong>GB</strong> (기가바이트, 10진)</td><td>10⁹ = 1,000,000,000 바이트</td><td><strong>120.03 GB</strong></td></tr>
<tr><td><strong>GiB</strong> (기비바이트, 2진)</td><td>2³⁰ = 1,073,741,824 바이트</td><td><strong>111.79 GiB</strong></td></tr>
</tbody></table></div>

용량이 사라진 것이 아니다. 같은 양을 더 큰 자로 재었을 뿐이다. GiB 값은 언제나 GB 값의 약 **93.1%** (10⁹ ÷ 2³⁰ ≈ 0.9313) 다.

## 3. SSD 는 GB 로 판다

SSD 는 (HDD, USB 메모리와 마찬가지로) **10진 GB** 로 판다 : 1 GB = 10⁹ 바이트. 그래서 '120 GB' 드라이브는 정말로 120.03 × 10⁹ 바이트를 담고, 모자라지 않다.

헷갈리는 것은 운영 체제가 보여 주는 숫자다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>어디서</th><th>무엇으로 계산하나</th><th>840 EVO 가 보이는 값</th></tr></thead><tbody>
<tr><td>Windows</td><td>GiB 로 계산하고 'GB' 라고 적는다</td><td>111 GB</td></tr>
<tr><td>macOS (10.6 부터)</td><td>10진 GB</td><td>120 GB</td></tr>
<tr><td>Linux <code>lsblk</code></td><td>GiB ('G' 라고 적는다)</td><td>111.8G</td></tr>
<tr><td>Linux <code>df -H</code>, <code>smartctl -i</code></td><td>10진 GB</td><td>120 GB</td></tr>
</tbody></table></div>

## 4. 왜 두 단위가 섞였나

### 4.1 컴퓨터는 2의 거듭제곱으로 생각한다

메모리는 2진 주소선으로 주소를 고르기 때문에, RAM 은 자연스럽게 1024, 65,536 … 같은 크기로 만들어진다. 초기 엔지니어들은 1024 가 1000 에 가깝다는 이유로 이것을 '킬로바이트' 라고 불렀다. 차이가 2.4% 뿐이라 아무도 신경 쓰지 않았다.

### 4.2 단계가 올라갈수록 차이가 커진다

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>접두어</th><th>10진</th><th>2진</th><th>차이</th></tr></thead><tbody>
<tr><td>kilo / kibi</td><td>10³</td><td>2¹⁰</td><td>2.4%</td></tr>
<tr><td>mega / mebi</td><td>10⁶</td><td>2²⁰</td><td>4.9%</td></tr>
<tr><td>giga / gibi</td><td>10⁹</td><td>2³⁰</td><td>7.4%</td></tr>
<tr><td>tera / tebi</td><td>10¹²</td><td>2⁴⁰</td><td>10.0%</td></tr>
</tbody></table></div>

2.4% 는 무시할 수 있었지만, 1 TB 드라이브가 약 931 'GB' 로 보이는 10% 는 누구나 알아챈다.

### 4.3 HDD 는 2진일 이유가 없었다

하드 디스크는 주소선이 아니라 트랙과 섹터로 이루어져 있어서, 크기가 아무 숫자나 될 수 있다. 드라이브 회사들은 SI 의 10진 의미 (giga = 10⁹) 를 썼다. 표준으로 보아도 맞고, 상자에 적힌 숫자도 커진다.

### 4.4 해결책이 늦게 나왔다

1998년 IEC 가 2진 전용 접두어 **KiB · MiB · GiB · TiB** (kibi, mebi, gibi) 를 만들었다. 이제 'GB' 는 10⁹ 만 뜻해야 한다. 하지만 이미 굳은 습관은 그대로 남았다.

- **Windows** 는 아직도 GiB 값을 'GB' 라고 적는다
- **RAM** 은 아직도 '16 GB' 로 팔지만 실제로는 16 GiB 다 (JEDEC 메모리 표준이 옛 2진 의미를 쓴다)
- **macOS** (2009 부터) 와 많은 Linux 도구는 10진 GB 로 바꾸었거나 GiB 를 제대로 적는다

### 4.5 소송까지 갔다

Western Digital (2006) 과 Seagate (2007) 는 '용량을 속았다' 는 집단 소송에서 합의했다. 둘 다 용량을 세는 방법은 바꾸지 않고, '1 GB = 10억 바이트' 라는 작은 글씨를 붙였다.

<div class="tip" markdown="1">
**요약.** 저장 장치와 네트워크 속도에서 'GB' 는 10⁹, RAM 과 Windows 에서는 2³⁰ 이다. 2진을 뜻할 때 'GiB' 라고 적으면 헷갈릴 일이 없다.
</div>

## 5. SSD 안은 2진이다 : FTL 이 안과 밖을 떼어 놓는다

4.3 의 'HDD 는 2진일 이유가 없었다' 는 SSD 에는 그대로 맞지 않는다. SSD 안의 NAND 는 정말로 2진이다.

- NAND 칩은 행 · 열 주소 (address cycle) 로 주소를 고른다. 그래서 페이지 크기 (4 / 8 / 16 KiB), 블록당 페이지 수, 다이 용량 (256 Gbit, 512 Gbit, 1 Tbit) 이 모두 2의 거듭제곱이다
- 그래서 원래 NAND 를 더하면 보통 2진 크기가 된다. 예를 들어 '120 GB' 드라이브에 128 GiB 의 NAND
- 그것도 깔끔한 2진은 아니다. NAND 페이지마다 숨은 **스페어 영역** 이 붙어 있다 (8 절). '16 KiB' 페이지가 실제로는 16,384 + 2,208 바이트일 수 있다

그런데 밖 (호스트) 에서는 10진 용량이 보인다. 그 사이에 **FTL (Flash Translation Layer)** 이 있기 때문이다.
호스트는 평평한 논리 섹터 (LBA) 목록만 보고, FTL 이 LBA 마다 어느 물리 페이지에 둘지를 정한다. 이 층이 있어서 드라이브가 보여 주는 LBA 수는 물리 구조와 맞을 필요가 없다. **회사는 LBA 수를 마음대로 고를 수 있고, 실제로는 IDEMA 가 정한 수를 고른다** (6 절). NAND 와 그 수의 차이는 over-provisioning 이 된다 (8 절).

<div class="check" markdown="1">
**정리.** SSD 의 물리 매체는 2진이지만, 호스트에 보이는 크기는 컨트롤러가 따로 정하고, 업계는 10진을 골랐다. HDD 는 매체도, 보이는 크기도 2진일 필요가 없다.
</div>

## 6. IDEMA 공식 : 섹터 수는 어떻게 정해지나

**IDEMA** (International Disk Drive Equipment and Materials Association) 는 저장 장치 업계 단체다. 그 표준 **LBA1-03** 이 '광고 용량 몇 GB 이면 섹터가 정확히 몇 개' 인지를 정한다.

### 6.1 공식

512 바이트 섹터일 때 :

```
LBA 수 = 97,696,368 + 1,953,504 × (광고 GB − 50)
```

840 EVO 에 넣으면 97,696,368 + 1,953,504 × 70 = **234,441,648**. 드라이브가 알려 준 값과 정확히 같다.

공식은 늘 광고 용량보다 조금 더 많이 준다 (120 GB 가 아니라 120.03 GB). 그래서 어느 회사의 '120 GB' 든 섹터 수가 같고, 회사가 달라도 드라이브를 바꿔 끼우거나 디스크를 복제하거나 RAID 를 다시 짤 때 몇 섹터가 모자라는 일이 없다.

### 6.2 1 GB 마다 1,953,504 섹터

두 상수 모두 같은 규칙에서 나온다 : **10⁹ 바이트를 옛 CHS 실린더 단위로 올림한다.**

- 1 GB = 10⁹ 바이트 = 512 B 섹터 1,953,125 개
- 옛 BIOS 의 CHS 변환은 헤드 16 × 트랙당 섹터 63 = **실린더당 1,008 섹터** 를 썼다
- 1,953,125 ÷ 1,008 = 1,937.6 → **올려서** 1,938 실린더
- 1,938 × 1,008 = **1,953,504** 섹터 = 1,000,194,048 바이트

즉 1 GB 가 늘 때마다, 10⁹ 바이트를 담을 수 있는 가장 작은 실린더 수만큼 늘어난다. 올림이므로 광고 용량보다 작아지는 일은 없다.

### 6.3 50 GB 의 기준값 97,696,368

- 97,696,368 ÷ 1,008 = **96,921** 실린더로 나누어떨어진다. 이것도 실린더 단위다
- 꼭 필요한 최소값은 50 × 10⁹ / 512 = 97,656,250 섹터 → 올리면 96,882 실린더
- 기준값은 이 최소값보다 39 실린더 (약 20 MB) 크다. 이 여유의 공식 이유는 찾지 못했다. 표준이 나올 때 이미 팔리던 '50 GB' 드라이브 중 가장 큰 것을 덮도록 정했을 가능성이 크다 (그래야 기존 드라이브가 표준보다 작아지지 않는다)

공식이 50 에서 시작하는 것은 표준이 50 GB 이상만 다루기 때문이다. 더 작은 옛 드라이브는 회사마다 크기가 이미 정해져 있었다.

### 6.4 덤 : 4K 섹터에도 맞는다

1,008 = 16 × 63 은 8 로 나누어떨어진다. 그래서 두 상수 모두 8 섹터 (4,096 바이트) 의 배수이고, 4Kn 드라이브용 공식은 그냥 8 로 나눈 것이다.

```
LBA 수 (4K) = 12,212,046 + 244,188 × (광고 GB − 50)
```

<div class="check" markdown="1">
**정리.** IDEMA 용량은 (1) 언제나 광고 GB **이상** 이고 (1 GB 마다 약 0.02%, 기준값에서 조금 더), (2) 실린더 단위로 끝나서 옛 BIOS · 파티션 도구가 실린더 조각을 버리지 않고, (3) 회사가 달라도 같은 크기면 섹터 수가 정확히 같다.
</div>

## 7. SSD 도 IDEMA 를 따른다

CHS 실린더는 수십 년 동안 아무도 쓰지 않았으니 IDEMA 는 옛 HDD 의 것이라고 생각하기 쉽다. 시작은 HDD 였지만 **SSD 도 따른다.** 실험할 드라이브가 바로 그 증거다 : 234,441,648 은 120 GB 의 IDEMA 값이다.

- **그대로 바꿔 끼우기.** SSD 는 HDD 를 바꾸는 물건으로 팔렸다. 옛 120 GB HDD 를 120 GB SSD 로 복제하려면 SSD 가 섹터 하나라도 작으면 안 된다
- **RAID 와 회사 바꾸기.** 고장 난 RAID 디스크를 다른 회사의 같은 크기 드라이브로 바꿀 수 있다
- **FTL 덕분에 공짜.** 5 절에서 본 대로 컨트롤러는 아무 LBA 수나 보여 줄 수 있으니, IDEMA 에 맞추는 데 드는 것이 없다

요즘 NVMe 드라이브에서도 흔히 보는 크기는 모두 이 공식에서 나온다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>광고</th><th>LBA 수 (512 B)</th><th>바이트</th><th>실제 GB</th><th>실제 GiB</th></tr></thead><tbody>
<tr><td>120 GB</td><td>234,441,648</td><td>120,034,123,776</td><td>120.034</td><td>111.790</td></tr>
<tr><td>250 GB</td><td>488,397,168</td><td>250,059,350,016</td><td>250.059</td><td>232.886</td></tr>
<tr><td>500 GB</td><td>976,773,168</td><td>500,107,862,016</td><td>500.108</td><td>465.762</td></tr>
<tr><td>1 TB</td><td>1,953,525,168</td><td>1,000,204,886,016</td><td>1,000.205</td><td>931.513 (0.910 TiB)</td></tr>
<tr><td>2 TB</td><td>3,907,029,168</td><td>2,000,398,934,016</td><td>2,000.399</td><td>1,863.017 (1.819 TiB)</td></tr>
</tbody></table></div>

- **GB** : 모두 광고보다 조금 **크다** (1,000 GB 마다 약 0.2 GB). IDEMA 공식의 올림이다
- **GiB** : 언제나 GB 의 약 93.1%. Windows 에서 '사라지는' 7.4% 다
- **TiB** : TB 드라이브는 TiB 와 비교하면 차이가 약 9% 로 더 크다. '1 TB' 가 Windows 에서 약 931 GB 로 보이는 이유다

주의할 점 :

- 상수 뒤의 CHS 이야기는 순전히 역사다. 숫자가 바뀌지 않는 것은 호환성 때문이다
- IDEMA 를 따르는 것은 관례이지 법이 아니다. 기업용이나 OEM 드라이브 중에는 조금 다른 수를 쓰는 것도 있다. 일반 소비자용은 대부분 따른다
- 120, 240, 480, 960 GB 같은 어중간한 크기는 SSD 쪽 사정에서 나온다 : 2진 NAND (128, 256, 512, 1024 GiB) 에서 over-provisioning 을 뺀 것. 회사가 광고 GB 를 고르면, 정확한 섹터 수는 IDEMA 공식이 정한다

## 8. 스페어 영역과 over-provisioning

5 절에서 NAND 페이지에 숨은 스페어 영역이 있다고 했다. 이것은 over-provisioning 에 들어가지 **않는다.** 둘은 따로 셈하는 예산이다.

### 8.1 over-provisioning 은 무엇을 재나

```
OP = (원래 NAND 의 main 영역 용량 − 사용자 용량) / 사용자 용량
```

여기서 '원래 용량' 은 페이지의 **main (데이터) 영역** 만, 즉 2진인 부분만 센다. '512 Gbit 다이' 는 main 영역이 512 Gbit 라는 뜻이고, 스페어 바이트는 그 위에 따로 있다.

### 8.2 스페어 영역에는 무엇이 있나

- **ECC 패리티.** 대부분이 LDPC 에 쓰인다 (옛 드라이브는 BCH). TLC · QLC 셀은 오류가 많아서 꼭 필요하다
- **메타데이터.** 페이지의 LBA (전원이 끊긴 뒤 매핑 표를 다시 만들 수 있게), 순서 · 버전 번호, 배드 블록 표시

사용자 데이터에는 절대 쓰이지 않고, FTL 이 GC 나 wear-leveling 에 쓸 수도 없다.

<svg viewBox="0 0 760 250" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="NAND 의 세 층 : 사용자 용량, OP, 스페어 영역"><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">840 EVO 120GB 의 NAND : 사용자 용량 · OP · 스페어 영역</text><rect x="20" y="60" width="540" height="56" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="290.0" y="84.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">사용자 용량 (IDEMA LBA)</text><text x="290.0" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="middle">120.03 GB = 111.79 GiB : 내 데이터</text><rect x="560" y="60" width="78" height="56" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="599.0" y="84.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">OP</text><text x="599.0" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="middle">17.4 GB</text><rect x="638" y="60" width="63" height="56" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4"/><text x="669.5" y="84.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">스페어</text><text x="669.5" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="middle">+10–13%</text><path d="M20,128 L20,138 L638,138 L638,128" fill="none" stroke="#2c3e50" stroke-width="1.5"/><text x="329.0" y="158.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND main 영역 128 GiB = 137.4 GB (2진, 'raw 용량')</text><path d="M638,128 L638,138 L701,138 L701,128" fill="none" stroke="#7f8c8d" stroke-width="1.5"/><text x="669.5" y="158.0" font-size="11.5" fill="#566573" text-anchor="middle">raw 용량에 안 넣음</text><text x="20.0" y="196.0" font-size="11.5" fill="#4d5656" text-anchor="start">OP = (137.4 − 120.03) / 120.03 ≈ 14.5% : GC, wear-leveling, 배드 블록 교체, TurboWrite SLC 버퍼가 여기서 나온다</text><text x="20.0" y="218.0" font-size="11.5" fill="#4d5656" text-anchor="start">스페어 영역 = 페이지마다 붙은 ECC (LDPC) 와 메타데이터 : FTL 도 쓸 수 없다</text><text x="20.0" y="240.0" font-size="11.5" fill="#566573" text-anchor="start">(가로 길이는 GB 비례, 스페어 영역은 대략)</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>층</th><th>쓰는 곳</th><th>OP 에 들어가나</th></tr></thead><tbody>
<tr><td>페이지마다 붙은 스페어 바이트</td><td>ECC, 메타데이터</td><td>아니오 : 'raw' 용량 밑에 숨어 있다</td></tr>
<tr><td>사용자 용량을 넘는 main 영역</td><td>GC, wear-leveling, 배드 블록 교체</td><td><strong>예 : 이것이 OP</strong></td></tr>
<tr><td>사용자 용량 (IDEMA LBA)</td><td>내 데이터</td><td>—</td></tr>
</tbody></table></div>

### 8.3 예외 : 다이 단위 패리티

어떤 컨트롤러는 페이지마다의 ECC 위에 **다이 단위 패리티** 를 한 겹 더 둔다. Samsung 이나 SandForce 의 'RAISE' 같은 방식으로, 한 다이 몫의 페이지에 나머지 다이의 패리티를 RAID-5 처럼 적는다. 이 패리티는 **main 영역** 에 쓰이므로 OP 를 깎아 먹는다.

## 9. 실험할 드라이브에 대입하면

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>항목</th><th>값</th><th>어디서</th></tr></thead><tbody>
<tr><td>사용자 용량</td><td>234,441,648 섹터 = 120.03 GB = 111.79 GiB</td><td>드라이브가 알려 준 값, IDEMA 120 GB 와 같음</td></tr>
<tr><td>NAND main 영역</td><td>128 GiB = 137.4 GB (TLC)</td><td>리뷰에 알려진 값. <a href="/old-ssd-experiments/19-teardown/">실험 19</a> 에서 패키지 표시로 확인</td></tr>
<tr><td>OP</td><td>약 17.4 GB ≈ 14.5%</td><td>위 두 값으로 계산</td></tr>
<tr><td>그중 TurboWrite (SLC 버퍼)</td><td>약 3 GB (TLC 로는 약 9 GB 를 차지)</td><td>알려진 값, <a href="/old-ssd-experiments/3-slc-cache/">실험 3</a> 에서 잰다</td></tr>
<tr><td>GC 가 실제로 쓰는 여유</td><td>약 8 GB 로 가정</td><td><a href="/old-ssd-experiments/10-over-provisioning/">실험 10</a> 의 모델</td></tr>
</tbody></table></div>

<div class="warn" markdown="1">
**주의.** 섹터 수만으로는 원래 NAND 크기를 알 수 없다. 컨트롤러는 그것을 보통의 인터페이스로 알려 주지 않는다. 같은 '120 GB' 라도 128 GiB 에 OP 14.5% 일 수도, 다이 패리티가 있어 실제 여유가 더 적을 수도, OEM 모델이라 NAND 구성이 아예 다를 수도 있다. 확인하려면 모델의 데이터시트 · 리뷰를 보거나, 드라이브를 열어 NAND 패키지의 부품 번호를 읽는다.
</div>

## 10. 직접 확인하는 명령

실험 드라이브는 `sda` 다 (<a href="/old-ssd-experiments/linux-commands/">Linux 명령</a> 페이지).

```sh
cat /sys/block/sda/size                  # 섹터 수 (512 B 단위로 센다) : 234441648
lsblk -b -o NAME,SIZE,MODEL /dev/sda     # 바이트 : 120034123776
lsblk -o NAME,SIZE /dev/sda              # GiB 로 : 111.8G
sudo smartctl -i /dev/sda                # User Capacity: 120,034,123,776 bytes [120 GB]
```

<div class="tip" markdown="1">
**IDEMA 값인지 확인하기.** `(섹터 수 − 97696368) / 1953504 + 50` 이 정수로 떨어지면 IDEMA 크기다. 840 EVO 는 `(234441648 − 97696368) / 1953504 + 50 = 120`.
</div>

## 11. 드라이브, 네임스페이스, 파티션 : 용량을 나누는 세 층

용량을 나누는 방법은 하나가 아니다. **드라이브** 가 있고, NVMe 드라이브는 그 안을 **네임스페이스** 로 나눌 수 있고, OS 는 각 디스크를 **파티션** 으로 나눈다. 셋 다 '용량을 쪼갠다' 는 점은 같아서 헷갈리지만, **누가 나누고 누가 그 경계를 아는지** 가 다르다.

<svg viewBox="0 0 760 330" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="드라이브, 네임스페이스, 파티션"><text x="380" y="22" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">용량을 나누는 세 층 : 누가 나누고, 누가 아나</text><rect x="20" y="40" width="720" height="250" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="36" y="62" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">① 드라이브 (NVMe 컨트롤러 nvme0) : NAND 전체 + FTL</text><text x="36" y="80" font-size="11.5" fill="#4d5656" text-anchor="start">나누는 것 : 드라이브 펌웨어 (NVMe 관리 명령)  ·  OS 에는 보이지 않는 NAND 와 OP 도 여기 있다</text><rect x="40" y="94" width="480" height="180" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="56" y="116" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">② 네임스페이스 1 (nvme0n1) : OS 에게는 '디스크 하나'</text><text x="56" y="134" font-size="11.5" fill="#4d5656" text-anchor="start">LBA 0 … 3,907,029,167 (512 B 섹터)</text><rect x="60" y="146" width="140" height="98" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="130" y="170" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">③ 파티션 1</text><text x="130" y="188" font-size="11.5" fill="#2c3e50" text-anchor="middle">nvme0n1p1</text><text x="130" y="206" font-size="11.5" fill="#2c3e50" text-anchor="middle">EFI, 512 MiB</text><text x="130" y="224" font-size="11.5" fill="#2c3e50" text-anchor="middle">LBA 2048 부터</text><rect x="212" y="146" width="290" height="98" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="357" y="170" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">③ 파티션 2</text><text x="357" y="188" font-size="11.5" fill="#2c3e50" text-anchor="middle">nvme0n1p2</text><text x="357" y="206" font-size="11.5" fill="#2c3e50" text-anchor="middle">ext4 (/), 1.8 TiB</text><text x="357" y="224" font-size="11.5" fill="#2c3e50" text-anchor="middle">LBA 1,050,624 부터</text><text x="280" y="262" font-size="11.5" fill="#1e8449" text-anchor="middle">나누는 것 : OS (디스크 맨 앞의 GPT 표)</text><rect x="536" y="94" width="190" height="180" rx="8" fill="#ffffff" stroke="#2874a6" stroke-width="2" stroke-dasharray="6 4"/><text x="631" y="118" font-size="12.5" font-weight="700" fill="#2874a6" text-anchor="middle">(네임스페이스 2 …)</text><text x="631" y="140" font-size="11.5" fill="#4d5656" text-anchor="middle">만들 수 있다면 nvme0n2</text><text x="631" y="158" font-size="11.5" fill="#4d5656" text-anchor="middle">따로 LBA 0 부터 시작</text><text x="631" y="190" font-size="11.5" fill="#4d5656" text-anchor="middle">어느 네임스페이스에도</text><text x="631" y="208" font-size="11.5" fill="#4d5656" text-anchor="middle">넣지 않은 용량은</text><text x="631" y="226" font-size="11.5" font-weight="700" fill="#7d3c98" text-anchor="middle">FTL 이 OP 처럼 쓸 수 있다</text><text x="380" y="318" font-size="11.5" fill="#566573" text-anchor="middle">SATA (840 EVO) 에는 ② 가 없다 : 드라이브 = 디스크 하나 (sda), 그 안에 파티션 (sda1 …)</text></svg>

### 11.1 세 층의 차이

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th></th><th>① 드라이브</th><th>② 네임스페이스 (NVMe)</th><th>③ 파티션</th></tr></thead><tbody>
<tr><td>무엇인가</td><td>물건 하나 : 컨트롤러 + DRAM + NAND</td><td>드라이브가 OS 에게 내보이는 '디스크'. 드라이브 하나가 여러 개를 내보일 수 있다</td><td>디스크 안의 LBA 구간 하나</td></tr>
<tr><td>누가 만드나</td><td>공장</td><td><strong>드라이브 펌웨어</strong> : NVMe 관리 명령 (<code>nvme create-ns</code>, <code>attach-ns</code>)</td><td><strong>OS · 도구</strong> : <code>fdisk</code>, <code>parted</code>, 설치 프로그램</td></tr>
<tr><td>경계가 적힌 곳</td><td>—</td><td>드라이브 안 (펌웨어의 표)</td><td>디스크 맨 앞의 <strong>파티션 표</strong> (GPT : LBA 1–33, 끝에 백업)</td></tr>
<tr><td>LBA 번호</td><td>밖에서는 보이지 않는다 (NAND 주소는 FTL 만 안다)</td><td>네임스페이스마다 <strong>0 부터 따로</strong> 센다</td><td>디스크의 LBA 를 그대로 쓴다 : 시작 위치 (예 : 2048) 만 표에 적혀 있다</td></tr>
<tr><td>Linux 이름</td><td>컨트롤러 <code>nvme0</code> (SATA 는 이름 없이 <code>ata5</code> 포트)</td><td><code>nvme0n1</code>, <code>nvme0n2</code> … (SATA 는 <code>sda</code> 하나)</td><td><code>nvme0n1p1</code> · <code>sda1</code></td></tr>
<tr><td>경계를 넘을 수 있나</td><td>—</td><td><strong>없다.</strong> 다른 네임스페이스의 블록은 주소로 가리킬 수조차 없다</td><td><strong>있다.</strong> 표의 숫자일 뿐이라, 디스크 전체 (<code>/dev/sda</code>) 에 쓰는 프로그램은 모든 파티션을 덮어쓸 수 있다</td></tr>
<tr><td>따로 정할 수 있는 것</td><td>—</td><td>섹터 크기 (512 B / 4 KiB), 암호화 키, 쓰기 보호, VM 에 따로 붙이기</td><td>파일 시스템 종류, 용도 표시 (EFI, Linux …)</td></tr>
<tr><td>FTL 이 아나</td><td>FTL 그 자체</td><td><strong>안다</strong> : 어느 네임스페이스에도 넣지 않은 용량은 쓰지 않을 것이 확실하다</td><td><strong>모른다.</strong> 파티션 표도 FTL 에게는 그냥 데이터. 빈 곳은 TRIM 으로만 알려 줄 수 있다</td></tr>
<tr><td>흔히 쓰는 곳</td><td>—</td><td>서버 · 가상 머신 : SSD 하나를 여러 '디스크' 로 나눠 손님마다 하나씩</td><td>모든 PC : EFI · Linux · Windows 나누기</td></tr>
</tbody></table></div>

그래서 이름에서 **파티션이 네임스페이스 아래** 에 온다 (<code>nvme0n1<strong>p1</strong></code>). 네임스페이스는 '파티션 비슷한 것' 이 아니라 **디스크 하나** 이고, OS 는 그 디스크를 받아 늘 하던 대로 파티션을 나눈다. 일반 PC 에서는 네임스페이스가 1번 하나뿐이고 드라이브 전체를 차지해서, 사람이 다루는 것은 파티션뿐이다. 그래서 둘이 '거의 같다' 고 느껴진다.

### 11.2 이 컴퓨터의 실제 숫자

파티션의 시작과 크기는 <code>/sys</code> 에 섹터 (512 B) 단위로 있다 (2026.10.18 실제 값) :

```
$ for p in sda1 sda2 sda3 sda4; do echo "$p start $(cat /sys/block/sda/$p/start) size $(cat /sys/block/sda/$p/size)"; done
sda1 start 2048 size 204800
sda2 start 206848 size 32768
sda3 start 239616 size 233108373
sda4 start 233349120 size 1089536
$ cat /sys/block/nvme0n1/nsid
1
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>디스크</th><th>전체 (섹터)</th><th>파티션</th><th>읽는 법</th></tr></thead><tbody>
<tr><td><code>sda</code> (840 EVO 120GB, SATA)</td><td>234,441,648</td><td>sda1 EFI 100 MiB · sda2 MSR 16 MiB · sda3 NTFS 111.2 GiB · sda4 복구 532 MiB</td><td>첫 파티션이 LBA 2048 = <strong>1 MiB</strong> 에서 시작한다 : 1 MiB 정렬 (그 앞은 GPT 표). 마지막 파티션 뒤에 2,992 섹터 (1.5 MiB) 가 남는다 : GPT 백업 표와 여분</td></tr>
<tr><td><code>nvme0n1</code> (990 EVO 2TB, NVMe, 네임스페이스 1)</td><td>3,907,029,168</td><td>p1 EFI 512 MiB · p2 ext4 1.8 TiB</td><td>같은 1 MiB 정렬. <code>nsid</code> = 1 : 이 네임스페이스의 번호</td></tr>
</tbody></table></div>

1 MiB 정렬은 실험 6 과 이어진다 : 파티션이 4 KiB 경계에서 어긋나 있으면, 파일 시스템의 4 KiB 쓰기가 모두 FTL 의 4 KiB 칸 두 개에 걸친다 (옛 Windows XP 의 63 섹터 시작이 그랬다).

### 11.3 직접 확인하는 명령

```sh
lsblk -o NAME,SIZE,TYPE,PARTTYPENAME,FSTYPE      # 디스크 · 파티션과 그 용도
cat /sys/block/sda/sda1/start                    # 파티션의 시작 섹터
sudo parted /dev/sda unit s print                # 파티션 표 전체를 섹터 단위로
sudo nvme list                                   # NVMe 네임스페이스 목록 (nvme-cli)
sudo nvme id-ctrl /dev/nvme0 | grep -E '^(nn|tnvmcap|unvmcap) '
                                                 # nn : 만들 수 있는 네임스페이스 수
                                                 # tnvmcap / unvmcap : 전체 / 어느 네임스페이스에도 안 넣은 용량
```

PC 용 NVMe 드라이브는 대개 네임스페이스를 하나만 지원한다 (<code>nn</code> = 1). 여러 개를 만들 수 있는 것은 주로 데이터센터용이다. SATA 에는 네임스페이스가 없지만, 비슷하게 '드라이브가 정하는 경계' 로 <strong>HPA</strong> (보이는 최대 섹터를 줄이기, <a href="/old-ssd-experiments/10-over-provisioning/">실험 10</a>) 가 있다.

### 11.4 FTL 에게 '여기는 안 쓴다' 를 알리는 세 방법

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>방법</th><th>층</th><th>FTL 이 아는가</th><th>OP 로 쓰이나</th></tr></thead><tbody>
<tr><td>파티션을 작게 만들고 뒤를 비워 둠</td><td>OS</td><td>비운 곳을 한 번도 쓰지 않았거나 TRIM 했을 때만</td><td>그때만 예 (<a href="/old-ssd-experiments/10-over-provisioning/">실험 10</a> 의 span 방식)</td></tr>
<tr><td>HPA 로 보이는 크기를 줄임 (SATA)</td><td>드라이브</td><td>숨긴 곳은 OS 가 쓸 수 없다. 이미 쓴 데이터가 있었다면 TRIM 이 먼저 필요</td><td>예</td></tr>
<tr><td>네임스페이스를 작게 만듦 (NVMe)</td><td>드라이브</td><td>예 : 펌웨어가 경계를 직접 안다</td><td>예, 가장 확실하다</td></tr>
</tbody></table></div>

## 12. USB 로 붙인 NVMe : USB 는 NVMe 를 모른다

USB 외장 SSD 의 안에는 NVMe SSD 가 들어 있는 경우가 많다. 그런데 **USB 에는 NVMe 를 실어 나르는 방법이 없다.** USB 저장 장치는 SCSI 명령으로 말한다 (USB 메모리와 같다). 그래서 케이스 안의 **브리지 칩** 이 둘 사이를 번역한다.

<svg viewBox="0 0 760 250" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="USB NVMe 외장 SSD 의 구조"><defs><marker id="au" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380" y="22" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">USB 외장 NVMe : 가운데의 브리지 칩이 번역한다</text><rect x="20" y="50" width="170" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="105" y="78" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PC (Linux)</text><text x="105" y="98" font-size="11.5" fill="#2c3e50" text-anchor="middle">uas 드라이버 → /dev/sdf</text><text x="105" y="116" font-size="11.5" fill="#2c3e50" text-anchor="middle">SCSI 명령을 보낸다</text><line x1="190" y1="90" x2="268" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#au)"/><text x="229.0" y="82" font-size="11" fill="#566573" text-anchor="middle">USB (SCSI)</text><rect x="270" y="50" width="200" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="370" y="78" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">브리지 칩</text><text x="370" y="98" font-size="11.5" fill="#2c3e50" text-anchor="middle">SCSI READ / WRITE / UNMAP</text><text x="370" y="116" font-size="11.5" fill="#2c3e50" text-anchor="middle">→ NVMe Read / Write / Deallocate</text><line x1="470" y1="90" x2="548" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#au)"/><text x="509.0" y="82" font-size="11" fill="#566573" text-anchor="middle">PCIe (NVMe)</text><rect x="550" y="50" width="190" height="80" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="645" y="78" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NVMe SSD</text><text x="645" y="98" font-size="11.5" fill="#2c3e50" text-anchor="middle">컨트롤러 + FTL + NAND</text><text x="645" y="116" font-size="11.5" fill="#2c3e50" text-anchor="middle">NVMe 명령만 안다</text><rect x="20" y="150" width="720" height="80" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2" stroke-dasharray="5 4"/><text x="380" y="174" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Linux 는 브리지만 본다 : 이름은 nvme0n1 이 아니라 sdX</text><text x="380" y="194" font-size="11.5" fill="#4d5656" text-anchor="middle">잃는 것 : NVMe 이름 · 큐 · 네임스페이스, 그냥은 안 되는 SMART, 번역되어야 하는 TRIM, USB 링크의 속도</text><text x="380" y="214" font-size="11.5" fill="#4d5656" text-anchor="middle">예외 : Thunderbolt · USB4 외장은 PCIe 를 그대로 터널링해서 진짜 nvme1n1 으로 보인다</text></svg>

### 12.1 이름 : 왜 sdX 인가

Linux 에서 `sd` 는 **SCSI disk** 다 (드라이버 `drivers/scsi/sd.c`). SATA 디스크 (`libata` 가 SCSI 명령을 ATA 명령으로 번역), USB 디스크 (원래 SCSI 명령을 USB 로 보냄), 진짜 SCSI · SAS 디스크가 모두 이 층을 지나므로 `sda`, `sdb` … 가 된다. NVMe 는 SCSI 층을 거치지 않는 자기 드라이버가 있어서 `nvme0n1` 이다.
그런데 USB 브리지 뒤의 NVMe SSD 는 Linux 에게 **USB 저장 장치** 로 보인다 : 그래서 다시 `sd` 이름을 받는다.

(덤 : 파티션 번호의 `p` 는 커널의 규칙 하나에서 나온다. 디스크 이름이 숫자로 끝나면 `p` 를 넣는다 : `nvme0n1` → `nvme0n1p1`, `mmcblk0` → `mmcblk0p1`, `loop0` → `loop0p1`. 넣지 않으면 `nvme0n11` 이 '네임스페이스 11' 인지 '네임스페이스 1 의 파티션 1' 인지 알 수 없다. 글자로 끝나는 `sda` 는 그냥 `sda1` 이다.)

### 12.2 이 컴퓨터의 예 : Samsung T7

이 컴퓨터의 `sdf` 가 바로 그것이다 : Samsung T7 외장 SSD, 안은 NVMe, 브리지가 케이스에 들어 있다 (2026.10.18 실제 출력).

```
$ lsblk -d -o NAME,MODEL,TRAN,DISC-MAX,ROTA /dev/sdf
NAME MODEL   TRAN DISC-MAX ROTA
sdf  PSSD T7 usb        0B    0
$ lsusb | grep T7
Bus 001 Device 007: ID 04e8:4001 Samsung Electronics Co., Ltd PSSD T7
$ basename $(readlink /sys/bus/usb/devices/1-8:1.0/driver)
uas
$ cat /sys/bus/usb/devices/1-8/speed
480
```

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>보이는 것</th><th>뜻</th></tr></thead><tbody>
<tr><td><code>TRAN usb</code>, 이름 <code>sdf</code></td><td>NVMe 가 아니라 USB 저장 장치로 보인다</td></tr>
<tr><td><code>driver uas</code></td><td>USB Attached SCSI : USB 위의 SCSI (옛 방식은 <code>usb-storage</code>)</td></tr>
<tr><td><code>DISC-MAX 0B</code></td><td>지금 이 연결로는 TRIM 이 지나가지 않는다 (브리지가 SCSI <code>UNMAP</code> 을 NVMe <code>Deallocate</code> 로 번역해 줘야 한다)</td></tr>
<tr><td><code>speed 480</code></td><td><strong>USB 2.0 속도 (480 Mb/s)</strong> 로 붙어 있다. T7 은 10 Gb/s 포트에서 약 1,000 MB/s 인데, 지금은 약 40 MB/s 가 한계다. USB 2.0 케이블이거나 USB 2.0 포트 (흔히 검은색) 에 꽂힌 것이다. T7 의 USB-C 케이블로 파란색 · USB-C 포트에 꽂으면 <code>5000</code> 또는 <code>10000</code> 이 나와야 한다</td></tr>
</tbody></table></div>

### 12.3 브리지를 지나면 달라지는 것

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>항목</th><th>안쪽 (NVMe 로 바로)</th><th>USB 브리지를 지나면</th></tr></thead><tbody>
<tr><td>이름</td><td><code>nvme0n1</code></td><td><code>sdX</code></td></tr>
<tr><td>명령 큐</td><td>큐 여러 개, 큐마다 수천 개</td><td>UAS 는 작은 큐 하나 (BOT 방식은 한 번에 하나)</td></tr>
<tr><td>네임스페이스</td><td>보인다</td><td>보이지 않는다 (브리지가 하나만 내보인다)</td></tr>
<tr><td>SMART</td><td><code>smartctl -a /dev/nvme0</code></td><td>브리지에 맞는 옵션이 필요하다 : <code>-d sntrealtek</code>, <code>-d sntjmicron</code>, <code>-d sntasmedia</code> (지원하는 브리지만)</td></tr>
<tr><td>TRIM</td><td><code>Deallocate</code></td><td>브리지가 <code>UNMAP</code> 을 번역해야 한다 : 안 되는 것도 많다</td></tr>
<tr><td>속도</td><td>PCIe : 수 GB/s</td><td>USB 링크가 한계 : 10 Gb/s 에서 약 1 GB/s, 5 Gb/s 에서 약 450 MB/s, USB 2.0 에서 약 40 MB/s</td></tr>
</tbody></table></div>

흔한 브리지 칩 : Realtek RTL9210, JMicron JMS583, ASMedia ASM2362. **Thunderbolt · USB4** 외장은 다르다 : PCIe 를 그대로 터널링하므로 안의 SSD 가 진짜 `nvme1n1` 으로 보이고, 번역도 없다.

같은 이야기가 SATA SSD 를 USB 어댑터에 넣을 때도 그대로다 : 어댑터가 SCSI 를 ATA 로 번역하고, SMART 는 `-d sat`, TRIM 은 어댑터가 허락할 때만 지나간다.

## 13. 읽을 수 없는 섹터가 생기면

드라이브가 아무리 애써도 어떤 페이지를 읽지 못할 때가 있다. 그때 무슨 일이 일어나고, 섹터 하나 때문에 OS 전체가 망가지는지, OS 는 이것을 어떻게 견디는지를 층마다 따라간다.

### 13.1 드라이브 안 : 예비 블록과 '고칠 수 없는 오류'

드라이브는 공장에서 일부 블록을 **예비 블록** 으로 떼어 숨겨 둔다 (8 절의 OP 의 일부). 블록이 닳아 쓰기 · 지우기에 실패하거나 (SMART 181 · 182), 읽을 때 오류가 너무 많으면, FTL 은 데이터를 옮기고 그 블록을 '불량' 으로 표시한 뒤 예비 블록으로 바꾼다. 컴퓨터는 알아채지 못한다 : 같은 LBA 가 그대로 쓰인다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>SMART</th><th>이름</th><th>세는 것</th></tr></thead><tbody>
<tr><td>179</td><td>Used_Rsvd_Blk_Cnt_Tot</td><td>써 버린 예비 블록 수. 젊은 드라이브는 0 이고, 수명 (지움 한도) 끝에 가까워질수록 빨리 는다. 정규화 값은 100 (예비가 그대로) 에서 내려가고, 기준값 (이 드라이브는 10) 에 닿으면 SMART 가 '실패' 로 판정한다</td></tr>
<tr><td>5 · 183</td><td>Reallocated_Sector_Ct · Runtime_Bad_Block</td><td>바꿔 단 블록, 쓰는 동안 나빠진 블록</td></tr>
<tr><td>187</td><td>Uncorrectable_Error_Cnt</td><td>ECC 와 다시 읽기 (read retry) 를 다 해도 고치지 못한 읽기</td></tr>
</tbody></table></div>

예비가 바닥나면 더는 나쁜 블록을 바꿀 수 없다. 많은 드라이브가 이때 **읽기 전용** 으로 바뀌어 데이터라도 지킨다 (<a href="/old-ssd-experiments/18-endurance/">실험 18</a> 이 이 끝을 본다).

ECC 와 다시 읽기로도 페이지를 살리지 못하면, 드라이브는 데이터 대신 **오류** 를 돌려준다 (ATA 의 `UNC`, SCSI 로는 *Medium Error / Unrecovered read error*). 187 이 하나 늘고, 오류 로그에 한 줄이 남는다. 다시 읽기를 다 해 본 뒤라 보통 **오래 걸린 뒤에** 온다.

### 13.2 커널 : 디스크 드라이버에서 프로그램까지

커널 로그에는 이런 줄이 남는다 (모양을 보이는 예다. 이 드라이브의 실제 출력이 아니다) :

```
ata5.00: failed command: READ FPDMA QUEUED
ata5.00: status: { DRDY ERR }
ata5.00: error: { UNC }
sd 4:0:0:0: [sda] Sense Key : Medium Error
sd 4:0:0:0: [sda] Add. Sense: Unrecovered read error
I/O error, dev sda, sector 123456 op 0x0:(READ)
```

- NCQ 로 명령 32 개가 함께 걸려 있었다면, 오류 처리기가 드라이브의 NCQ 오류 로그를 읽어 **어느 것이 실패했는지** 찾고, 나머지는 다시 보낸다. 진짜 매체 오류는 되풀이하지 않는다 : 드라이브가 이미 할 수 있는 것을 다 했기 때문이다.
- **느린** 것과 **실패** 는 다르다. 커널은 명령 하나를 **30 초** (`/sys/block/sda/device/timeout`) 기다린다. 드라이브가 그보다 오래 다시 읽고 있으면 커널은 포기하고 명령을 취소한 뒤 **링크를 다시 연결한다** (`hard resetting link`).

실패한 섹터는 데이터 대신 오류 (`-EIO`) 로 위로 올라간다. 그다음은 **누가 읽고 있었나** 에 달렸다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>읽고 있던 것</th><th>결과</th></tr></thead><tbody>
<tr><td>프로그램의 <code>read()</code></td><td><code>EIO</code> : <code>cp: error reading 'x': Input/output error</code>. 실험 1 의 <code>fileage.py</code> 는 이것을 <code>fileage-errors.csv</code> 에 적는다</td></tr>
<tr><td>파일 시스템 자신의 데이터 (inode, 디렉터리, 저널)</td><td>ext4 가 오류를 알린다. 이 컴퓨터의 <code>/</code> 는 <code>errors=remount-ro</code> 로 마운트되어 있어서 (<a href="/old-ssd-experiments/linux-commands/">Linux 명령</a> 3 절의 <code>findmnt</code>), 더 망가지지 않도록 <strong>읽기 전용</strong> 으로 바뀐다</td></tr>
<tr><td>디스크에서 올리는 프로그램 코드 (<code>mmap</code>, 실행 파일)</td><td>그 프로세스가 <strong><code>SIGBUS</code></strong> 를 받고 끝난다</td></tr>
<tr><td>스왑 (디스크로 내린 메모리)</td><td>그 메모리를 쓰던 프로세스가 끝난다</td></tr>
<tr><td>RAID 1 (<code>md</code> 미러) · 복사본이 있는 btrfs/ZFS</td><td><strong>저절로 고친다</strong> : 다른 디스크의 복사본을 읽고, 나쁜 섹터를 좋은 데이터로 다시 쓴다</td></tr>
</tbody></table></div>

Windows 도 같은 사슬이다 : 이벤트 로그의 디스크 이벤트 **7** ('bad block') 이나 51 · 153, 그리고 커널 자신의 메모리를 읽다 실패하면 블루 스크린 **`0x7A KERNEL_DATA_INPAGE_ERROR`**. (<a href="/old-ssd-experiments/1-old-data/">실험 1</a> 에서 읽은 이 드라이브의 옛 Windows 로그에는 이것들이 없었다.)

나쁜 섹터를 '고치는' 방법은 **다시 쓰기** 다. SSD 에서 쓰기는 늘 새 페이지로 가고 매핑이 바뀌므로, 나쁜 페이지는 다시 읽히지 않는다 (HDD 는 그 섹터를 예비로 바꾼다 : 197 'pending' → 5 'reallocated'). 그래서 상한 파일은 백업에서 되살리거나 덮어쓸 수는 있어도, 읽을 수는 없다.

### 13.3 섹터 하나로 OS 전체가 망가지나

대개 **아니다.** 섹터 하나는 그 안에 있던 것만 망가뜨리고, 디스크의 대부분은 평범한 파일 내용이다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>나쁜 섹터에 있던 것</th><th>결과</th></tr></thead><tbody>
<tr><td>사진 · 동영상 · 문서의 일부</td><td>그 파일 하나만 상한다</td></tr>
<tr><td>쓰지 않는 곳, 지운 파일의 자리</td><td>아무 일도 없다 : 알아채지도 못한다</td></tr>
<tr><td>프로그램 · 라이브러리 파일</td><td>그 프로그램이 그 부분을 올릴 때 죽는다. 패키지를 다시 설치하면 고쳐진다</td></tr>
<tr><td>파일 시스템의 구조 (디렉터리, inode 표, 저널)</td><td>일부 파일 · 디렉터리에 닿을 수 없게 된다. 파일 시스템이 자신을 지킨다 (아래)</td></tr>
<tr><td>부팅에 꼭 필요한 파일, 커널</td><td>부팅이 안 될 수 있다 : 드물지만 가장 나쁜 경우</td></tr>
</tbody></table></div>

### 13.4 OS 는 어떻게 견디나 : 여섯 겹

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>층</th><th>하는 일</th></tr></thead><tbody>
<tr><td>1. 드라이브</td><td>페이지마다의 ECC, 다시 읽기, 예비 블록, 약해진 블록을 <strong>실패하기 전에</strong> 옮기기. '거의 나쁜' 섹터는 대부분 드라이브가 조용히 옮겨서 OS 의 문제가 되지 않는다. 187 은 이 모든 것을 뚫은 것만 센다</td></tr>
<tr><td>2. 파일 시스템</td><td>중요한 구조는 두 벌, 그리고 검사한다. <strong>ext4</strong> : 디스크 곳곳에 superblock 백업, 메타데이터 체크섬 (<code>metadata_csum</code>), 저널, 오류 때 읽기 전용, 다음 부팅 때 <code>fsck</code>. <strong>NTFS</strong> : MFT 앞부분의 거울 (<code>$MFTMirr</code>), <code>chkdsk</code>. <strong>btrfs · ZFS</strong> : 데이터까지 <strong>모든 블록에 체크섬</strong>, 메타데이터는 기본으로 두 벌. 나쁜 블록을 몰래 돌려주지 않고 찾아내며, 복사본이 있으면 저절로 고친다</td></tr>
<tr><td>3. OS 다시 세우기</td><td>시스템 파일을 알려진 좋은 사본과 비교해 다시 설치한다. <strong>Ubuntu</strong> : <code>debsums</code> · <code>dpkg --verify</code> 로 검사, <code>apt install --reinstall</code> 로 고침. <strong>Windows</strong> : <code>sfc /scannow</code>, <code>DISM /RestoreHealth</code>, 그리고 복구 파티션 (이 드라이브의 <code>sda4</code>, 532 MB). 켜져 있는 동안은 OS 의 많은 부분이 이미 RAM 에 있어서, 나중에 생긴 나쁜 섹터는 다음 부팅까지 드러나지 않을 수도 있다</td></tr>
<tr><td>4. 디스크 사이의 중복</td><td><strong>RAID 1 · 미러</strong> (<code>md</code>, btrfs · ZFS 미러) : 모든 블록이 두 디스크에 있다. 실패한 읽기는 다른 디스크가 대신하고, 나쁜 쪽을 다시 쓴다. 서버는 이렇게 해서 나쁜 섹터 하나, 디스크 하나가 통째로 죽어도 멈추지 않는다</td></tr>
<tr><td>5. 미리 알리기</td><td><code>smartd</code> (smartmontools 에 들어 있다) 가 SMART 의 5 · 179 · 187 · 197 을 지켜보다가 오르기 시작하면 알린다 : 드라이브를 바꿀 때다</td></tr>
<tr><td>6. 백업</td><td>나머지 모두를 덮는 마지막 층 : 죽은 드라이브, 지운 파일, 랜섬웨어까지</td></tr>
</tbody></table></div>

**정리하면** : 나쁜 섹터 하나의 값은 보통 **파일 하나** 다. 파일 시스템은 자기 구조가 상해도 견디도록 만들어져 있고, OS 는 고칠 수 있다. 시스템 전체를 잃는 것은 운이 나쁠 때 (부팅에 꼭 필요한 구조) 나, 드라이브가 넓게 망가져 갈 때다.

이 드라이브는 지금 187 = 0, 179 = 0, 오류 로그가 비어 있다. 읽기가 아주 느릴 뿐 (<a href="/old-ssd-experiments/1-old-data/">실험 1</a>) 모든 읽기가 결국 성공했다. 고칠 수 없는 오류를 처음 볼 가능성이 있는 것은 <a href="/old-ssd-experiments/15-read-disturb/">실험 15</a> (read disturb), <a href="/old-ssd-experiments/16-retention/">16</a> (retention), <a href="/old-ssd-experiments/18-endurance/">18</a> (끝까지 쓰기) 이다. 그래서 이 실험들은 체크섬으로 데이터를 확인하고 (<code>verify</code>), 오류가 나도 멈추지 않고 기록한다.

## 요약

- 840 EVO 120GB = 234,441,648 섹터 × 512 B = **120.03 GB = 111.79 GiB.** 같은 양을 다른 자로 잰 것이다
- SSD 는 10진 GB 로 판다. Windows 는 GiB 로 계산하고 'GB' 라고 적어서 7.4% 가 사라진 것처럼 보인다
- 1024 를 '킬로' 라고 부른 옛 습관, 1998년에야 나온 KiB · GiB, 그리고 이미 굳은 Windows · RAM 의 관례가 지금의 혼란을 만들었다
- SSD 안의 NAND 는 2진이지만, FTL 이 안과 밖을 떼어 놓아서 밖에 보이는 섹터 수는 회사가 고를 수 있다
- 그 섹터 수는 IDEMA 공식이 정한다. 상수는 10⁹ 바이트를 CHS 실린더 (1,008 섹터) 로 올림한 값이고, SSD · NVMe 도 호환성 때문에 그대로 따른다
- NAND main 영역과 사용자 용량의 차이가 over-provisioning (이 드라이브는 약 14.5%) 이다. 페이지마다 붙은 스페어 영역 (ECC · 메타데이터) 은 OP 에 들어가지 않는다
- 용량은 세 층으로 나뉜다 : **드라이브** (물건), **네임스페이스** (드라이브가 내보이는 디스크, NVMe), **파티션** (OS 가 디스크 안에 적은 표). 네임스페이스는 드라이브가 경계를 알고, 파티션은 모른다. 그래서 이름도 `nvme0n1p1` 처럼 파티션이 네임스페이스 아래에 온다
- USB 는 NVMe 를 모른다. USB 외장 NVMe 는 케이스 안의 브리지 칩이 SCSI 를 NVMe 로 번역하고, Linux 에는 `sdX` (SCSI disk) 로 보인다. SMART · TRIM · 속도는 브리지와 USB 링크에 달렸다
- 드라이브가 고치지 못한 읽기 (SMART 187) 는 커널을 거쳐 `EIO` 로 올라간다. 섹터 하나의 값은 보통 파일 하나다 : 드라이브의 예비 블록, 파일 시스템의 두 벌 구조 · 체크섬 · 읽기 전용 전환, OS 다시 설치, RAID, SMART 감시, 백업이 겹겹이 막는다

<div class="step-nav"><a href="{{ '/old-ssd-experiments/' | relative_url }}">← 헌 SSD 로 하는 실험</a><a href="{{ '/old-ssd-experiments/linux-commands/' | relative_url }}">SSD 를 다루는 Linux 명령 →</a></div>
