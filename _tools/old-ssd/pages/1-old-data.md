---
layout: default
title: 1. 오래된 데이터 읽기
permalink: /old-ssd-experiments/1-old-data/
---
@@STYLE@@

# 1. 오래된 데이터 읽기 : 몇 년 묵은 데이터는 얼마나 느린가

<div class="glance">
<b>목표</b><span>데이터를 쓴 지 오래될수록 읽기가 느려지는지, 얼마나 느려지는지를 이 드라이브의 실제 파일로 잰다</span>
<b>보는 FTL 개념</b><span>셀 전압의 이동 (charge loss), ECC, read retry, 펌웨어의 데이터 새로 쓰기 (refresh)</span>
<b>지우나?</b><span><b>아니오.</b> 그리고 <b>지우기 전에만 할 수 있다</b> : 한 번 지우면 몇 년 된 데이터는 다시 만들 수 없다</span>
<b>연결</b><span>USB 그대로 (속도의 '비교' 만 보므로 괜찮다)</span>
<b>시간</b><span>1–2시간 (데이터가 아주 느리게 읽히면 더 걸린다)</span>
<b>명령</b><span><code>./lab.sh oldfiles /mnt/old840</code>, <code>sudo ./lab.sh scan old 8</code></span>
</div>

## 왜 오래된 데이터가 느려지나

NAND 셀은 전하 (전자) 를 가두어 데이터를 기억한다. TLC 는 셀 하나에 3비트를 담으려고 전압을 **8단계** 로 나눈다. 읽을 때는 그 사이에 놓은 기준 전압 7개와 비교한다.

@@FIG old_states_fresh@@

시간이 지나면 가둔 전자가 조금씩 빠져나간다. 전압이 높은 (전자가 많은) 상태일수록 더 많이 빠지고, 봉우리는 왼쪽으로 밀리며 넓어진다. 기준 전압을 넘어간 셀은 틀린 값으로 읽힌다.

@@FIG old_states_drift@@

틀린 비트는 ECC (오류 정정 부호) 가 고친다. 그러나 오류가 ECC 가 고칠 수 있는 수보다 많으면, 컨트롤러는 **기준 전압을 옮겨 가며 다시 읽는다** (read retry). 다시 읽을 때마다 페이지 읽기 시간 (TLC 에서 수십 µs 이상) 이 더해진다.

@@FIG old_retry@@

840 EVO 는 2014년, 오래된 데이터의 읽기 속도가 새 데이터의 몇 분의 일로 떨어지는 문제로 널리 알려졌다. 원인은 이 전압 이동과 그에 맞지 않은 읽기 방식으로 설명되었고, Samsung 은 펌웨어로 대응했다 ([0. 준비](/old-ssd-experiments/0-setup/) 의 펌웨어 설명 참고).

<div class="check" markdown="1">
**이미 보이는 단서.** 이 드라이브를 오늘 아침 꽂은 뒤 커널 통계 (`/proc/diskstats`) 에 따르면, 2.8 GB 를 읽는 동안 디스크가 **40분** 바빴다 : 약 1.2 MB/s. 누가 읽었는지 (파일 관리자, 색인 프로그램) 와 어떤 데이터였는지 모르니 측정은 아니다. 그래도 가설과 같은 쪽을 가리킨다.
</div>

## 가설과 예상

@@FIG old_expect@@

```table
가설 | 맞다면 보일 것 | 아니라면
H1 오래된 데이터일수록 느리다 | 해마다 중앙값이 내려간다 | 해마다 비슷하다
H2 느린 원인은 read retry 다 | 1 MiB 읽기 하나의 최대 시간 (`max_ms`) 이 오래된 파일에서 길다 | 모든 읽기가 고르게 느리다 (어댑터 · 조각난 파일 등 다른 원인)
H3 펌웨어가 오래된 데이터를 새로 쓰지 않았다 | 2018–2021 파일이 가장 느리다 | 모든 해가 빠르다 = 새로 쓰기를 했거나 문제가 없는 펌웨어
```

## 측정 방법

두 가지를 잰다.

**A. 파일별 (`fileage.py`)** : 파일마다 '데이터를 쓴 날' 을 알 수 있으니 나이와 속도를 바로 짝지을 수 있다.

@@FIG old_method@@

- '쓴 날' = NTFS **생성 시각** 과 **수정 시각** 중 늦은 쪽. 설치 프로그램은 파일의 수정 시각을 원본 날짜로 남기는 일이 많아서, 이 디스크에 실제로 쓴 날은 생성 시각이 더 정확하다.
- 해마다 25개씩 (16 MiB 이상인 파일 중에서 무작위, 같은 seed), 파일마다 앞 16 MiB 만 읽는다. 순서도 섞는다 : 측정 중 드라이브 상태가 변해도 특정 해에만 몰리지 않게.
- 읽기 전에 `posix_fadvise(DONTNEED)` 로 그 파일의 페이지 캐시를 버린다. 그래야 RAM 이 아니라 드라이브를 잰다.

**B. 드라이브 전체 (`readscan.py`)** : 256 MiB 구간마다 앞 8 MiB 를 `O_DIRECT` 로 읽는다. 파일 시스템을 거치지 않으므로 EFI · 복구 파티션과 빈 공간 (TRIM 되었으면 0) 까지 다 보인다. 결과 = 위치별 속도 지도.

## 절차

```
# 0. 준비 페이지의 1–5단계를 마친 상태 : 도구, check, 읽기 전용 마운트 (/mnt/old840)
$ cd ~/Ryu/jonghoon-ryu.github.io/old-ssd-experiments/scripts

# 1. 파일별 측정 (sudo 필요 없음). 해마다 몇 개의 파일이 있는지 먼저 출력한다
$ ./lab.sh oldfiles /mnt/old840

# 2. 드라이브 전체 지도 : 256 MiB 마다 8 MiB (전체의 1/32), 읽기만
$ sudo ./lab.sh scan old 8

# 3. 끝나면 Claude 에게 알리기
```

<div class="warn" markdown="1">
- **같은 데이터를 여러 번 읽지 않는다.** 오래된 데이터를 읽으면 펌웨어가 그 블록을 새로 써 버릴 수 있다 (읽으며 오류가 많았던 블록을 옮기는 것은 흔한 동작이다). 그러면 두 번째 측정은 '새 데이터' 를 잰다. 그래서 백업 복사도 이 실험 **뒤에** 한다.
- 중간에 멈추면 (Ctrl+C) 그때까지의 CSV 는 남는다. 다시 돌릴 때는 다른 `--seed` 로 다른 파일을 고르게 하는 것이 낫다 (Claude 에게 말하면 명령을 바꿔 준다).
- 너무 오래 걸리면 (1 MB/s 근처라면 파일별 측정만 30–50분) 그것 자체가 결과다. 진행 줄에 MB/s 가 계속 나온다.
</div>

## 저장되는 것

```table
파일 | 내용
`…-oldfiles/fileage.csv` | 파일마다 : written, age_days, mib, mbps, max_ms, path
`…-scan-old/scan.csv` | 구간마다 : offset_gib, mib, mbps, mean_ms, max_ms, zero_frac
`…-scan-old/smart-before/after.*` | 측정 앞뒤 SMART (195 ECC 같은 값이 읽는 동안 늘었는지)
```

## 결과 읽는 법

```
$ python3 plot.py age.png ~/Ryu/old_ssd_results/*-oldfiles/fileage.csv
$ python3 plot.py scan.png ~/Ryu/old_ssd_results/*-scan-old/scan.csv=old
```

1. **나이 – 속도 그림** : 점 = 파일 하나, 빨간 선 = 해마다 중앙값. H1 은 중앙값의 기울기로, H2 는 `max_ms` 의 꼬리로 본다.
2. **위치 지도** : 0 으로만 읽힌 구간 (점) 은 쓴 적이 없거나 Windows 가 TRIM 한 곳이다. 이런 곳은 NAND 를 읽지 않으므로 아주 빠를 것이다 (실험 3 미리 보기). 데이터가 있는 곳의 속도가 위치에 따라 고르게 낮은지, 띠 모양으로 다른지 본다.
3. **비교 기준** : 실험 2 가 드라이브 전체를 새로 쓴 직후에 같은 스캔을 한 번 더 한다 (`sudo ./lab.sh scan fresh 8`, SATA). 두 곡선을 겹치면 '나이' 만 다른 비교가 된다. USB 와 SATA 의 차이도 있으므로, 공정하게 비교하려면 SATA 에서 '새 데이터' 를 USB 로 한 번 더 읽을 수도 있다 (실험 2 페이지).
4. **SMART** : 앞뒤로 195 ECC_Error_Rate 나 187 이 늘었다면 읽는 동안 고친 (또는 못 고친) 오류가 있었다는 뜻이다.

## 시뮬레이터와의 연결

시뮬레이터의 NAND 모델에는 읽기 지연이 하나의 상수다. 실제 드라이브에서는 데이터의 나이 · 셀의 마모 · 온도에 따라 읽기 시간이 몇 배씩 달라진다. 이 결과는 시뮬레이터에 'read retry 모델' 을 넣을지 판단하는 근거가 된다.

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

@@NAV@@
