---
layout: default
title: 0. 준비
permalink: /old-ssd-experiments/0-setup/
---
@@STYLE@@

# 0. 준비 : 드라이브, 도구, 기준값

<div class="glance">
<b>목표</b><span>실험할 드라이브를 확실히 알아보고, 도구를 깔고, 실험 전 SMART 값 (기준값) 을 남긴다</span>
<b>지우나?</b><span>아니오. 읽기만 한다</span>
<b>연결</b><span>메인보드 SATA</span>
<b>시간</b><span>30분</span>
<b>명령</b><span><code>sudo ./lab.sh check</code></span>
</div>

## 드라이브

```table
항목 | 값 | 출처
모델 | Samsung SSD 840 EVO 120GB | `lsblk`
시리얼 | `S1D6NSAFB40389K` | `lsblk`, `/dev/disk/by-id`
펌웨어 | `EXT0CB6Q` | `lsblk -o REV`
용량 | 120,034,123,776 B (234,441,648 섹터) | 커널 로그
NAND | TLC, 128 GiB 로 알려짐 | 리뷰 · 자료 (확인 필요)
SLC 버퍼 (TurboWrite) | 120GB 모델은 약 3 GB 로 알려짐 | Samsung 자료 (확인 필요)
컨트롤러 | Samsung MEX (ARM 코어 3개로 알려짐) | 리뷰 (실험 19 에서 확인)
지금 내용 | 옛 Windows 디스크 : EFI · MSR · NTFS 111 GB (91% 참) · 복구 | `lsblk -f`, `df`
파일 날짜 | 2018 – 2024.12 (hiberfil.sys 마지막 수정 2024.12.08) | `ls -la`
지난 이력 | 2024.12 쯤 마지막으로 쓴 뒤 **1년 넘게 전원 없이** 보관. 2026.10.17 에 다시 연결해 Ryu 가 파일 몇 개를 읽고 몇 개를 새로 씀 (약 17.6 MB). 원래 Windows 부팅 드라이브였고, 가끔 블루 스크린이 떠서 새로 PC 를 조립했고, 이 SSD 는 그 뒤로 쓰지 않고 두었다. 그러다 심심해서 이 SSD 로 실험해 보기로 했다 | Ryu, `/proc/diskstats`
연결 | 메인보드 SATA `ata5` (`/dev/sda`), SATA 3 (6.0 Gbps), TRIM 됨 (`DISC-GRAN 512B`, `DISC-MAX 2G`) | `lsblk -o NAME,TRAN,DISC-MAX`, `journalctl -k`
```

<div class="check" markdown="1">
**840 EVO 와 '오래된 데이터 읽기 저하'.** 840 EVO 는 2014년, 오래전에 쓴 데이터를 읽는 속도가 크게 떨어지는 문제로 널리 알려졌다. Samsung 은 그해 10월 펌웨어 `EXT0BB6Q` 와 복구 도구를, 2015년에 오래된 데이터를 주기적으로 다시 쓰는 펌웨어 `EXT0DB6Q` 를 냈다고 기억한다 (버전과 날짜는 확인이 필요하다).
이 드라이브의 `EXT0CB6Q` 가 그 사이 어디에 있는지는 확인하지 못했다.
어느 쪽이든, '주기적으로 다시 쓰기' 는 **전원이 있을 때만** 할 수 있다. 이 드라이브는 1년 넘게 꺼져 있었으니 펌웨어와 상관없이 모든 데이터가 오래 방치된 상태다 : **실험 1 에 특히 좋은 이유다.**
</div>

## 1단계 : 데이터가 필요한지 정하기 (Ryu)

실험 1 과 2 는 지금 데이터를 **읽기만** 한다. 실험 3 부터는 모두 지운다. 그 전에 남길 것이 있으면 다른 디스크로 복사한다 (Windows 의 `Users`, `C++ Master pdf` 폴더 등).
복사 자체도 오래된 데이터를 읽는 일이므로, 실험 1 을 **먼저** 한 뒤에 복사한다. 10.17 에 이미 열어 본 파일과 새로 쓴 파일은 실험 1 이 따로 나누어 재므로 지우지 않고 그대로 둔다.

## 2단계 : 도구 설치

```
$ sudo apt install --no-install-recommends smartmontools fio sysstat
$ fio --version            # fio-3.36 이 나와야 한다
$ smartctl --version | head -1
```

`--no-install-recommends` 를 붙이는 이유 : `smartmontools` 는 메일 알림용으로 `postfix` (메일 서버) 를 추천 패키지로 끌고 오고, 그러면 설치 도중 메일 설정 화면이 뜬다. 실험에는 필요 없다.
`hdparm` 과 `ntfs-3g` 는 이 컴퓨터에 이미 있다 (2026.10.17 확인).

## 3단계 : 스크립트 받기

스크립트는 블로그 저장소에 있다. 이미 받아 둔 저장소라면 `git pull` 만 한다.

```
$ cd ~/Ryu/jonghoon-ryu.github.io && git pull
$ cd old-ssd-experiments/scripts
$ ./lab.sh                 # 사용법이 나온다
```

`lab.sh` 의 안전장치 :

@@FIG setup_safety@@

- 대상 시리얼은 스크립트 안에 고정되어 있다 (`readonly SERIAL=S1D6NSAFB40389K`). 환경 변수로 바꿀 수 없다.
- 시리얼이 정확히 하나의 장치에 맞고, 그 장치가 같은 시리얼을 보고할 때만 진행한다.
- 결과 폴더는 `~/Ryu/old_ssd_results/<날짜-시각>-<실험>/` : `meta.txt` (날짜, 명령, 장치, 커널, fio 버전), SMART 앞뒤 (텍스트 + JSON), fio 로그, CSV.

## 4단계 : `check` 와 SMART 기준값

```
$ sudo ./lab.sh check
```

하는 일 (아무것도 쓰지 않는다) :
1. 시리얼로 장치를 찾고, 연결 방식과 TRIM 가능 여부를 보여 준다
2. `hdparm -I` 로 펌웨어 · TRIM 지원 줄을 보여 준다
3. `smartctl -x` 를 텍스트와 JSON 으로 저장하고, 실험에 쓰는 속성만 골라 보여 준다

`check` 가 끝나면 Claude 에게 알린다. 결과 폴더를 직접 읽어서 다음을 확인한다 :

```table
보는 것 | 왜
펌웨어 | 읽기 저하 수정판인지 : 실험 1 의 해석이 달라진다
9 Power_On_Hours | 얼마나 쓰였나. 달력의 시간 (2013년 제품) 과 비교하면 켜져 있던 비율이 보인다
12 Power_Cycle_Count | 몇 번 켜졌나 (10.17 의 연결도 들어 있다)
177 Wear_Leveling_Count | 지금까지의 평균 P/E : 실험 18 의 남은 수명 계산
241 Total_LBAs_Written | 지금까지 호스트가 쓴 양 (10.17 에 쓴 것도 들어 있다)
5 · 179 · 181 · 182 · 183 · 187 | '믿을 수 없게 됨' 이 실제로 무엇인지 : 재할당, 예비 블록, 실패, 고치지 못한 오류
195 ECC_Error_Rate | 셀 상태
```

## 5단계 : 읽기 전용으로 다시 마운트

2026.10.17 에 Ryu 가 파일을 읽고 쓴 기록 (쓴 시각, 접근 시각) 이 실험 1 에서 파일을 세 무리로 나누는 근거가 된다. 실험 1 동안 접근 시각 같은 작은 쓰기도 없도록 NTFS 파티션을 **읽기 전용** 으로 붙인다. 이미 다른 곳에 붙어 있으면 먼저 뗀다 (`findmnt` 로 확인, `sudo umount 그곳`).

```
$ sudo mkdir -p /mnt/old840
$ sudo mount -t ntfs-3g -o ro /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K-part3 /mnt/old840
$ findmnt /mnt/old840          # OPTIONS 에 ro
```

**그 전까지 이 파티션을 파일 관리자로 열지 않는다.** 썸네일 · 미리 보기를 만드느라 오래된 데이터를 읽어 버린다 (읽힌 데이터는 펌웨어가 새로 쓸 수 있다 : 실험 1 의 H5).
읽기 전용 마운트는 접근 시각도 바꾸지 않으므로, 10.17 에 남은 접근 시각이 그대로 보존된다.
`umount` 가 `target is busy` 라고 하면 그 폴더를 연 창이나 터미널을 닫고 다시 한다.

`ntfs-3g` 로 붙여야 `fileage.py` 가 NTFS 생성 시각 (`system.ntfs_crtime`) 을 읽을 수 있다.
Windows 가 최대 절전 상태 (hiberfil.sys) 로 꺼져 있어서 `ntfs-3g` 가 마운트를 거절하면, 읽기 전용 (`-o ro`) 이므로 그대로 진행해도 된다는 안내가 나온다.

## 결과

<div class="result" markdown="1">
**2026.10.18 08:49, `sudo ./lab.sh check`** (결과 폴더 `20261018-084956-check`). 연결 : SATA 3.1, 6.0 Gb/s. SMART 판정 `PASSED`.

**SMART 속성** (raw 값)

```table
ID | 이름 | 값 | 읽는 법
9 | Power_On_Hours | 10,373 시간 | 켜져 있던 시간을 다 합해 약 432일
12 | Power_Cycle_Count | 4,600 번 | 한 번 켜면 평균 2.3시간 : 매일 켰다 끈 데스크톱 · 노트북 디스크의 모습
235 | POR_Recovery_Count | 1,036 번 | **정상적으로 끄지 않고 전원이 끊긴 횟수** (Samsung 의 뜻). 켠 횟수의 약 22%
177 | Wear_Leveling_Count | 117 (정규화 90) | 블록 평균 117번 지워졌다. 정규화 값이 100 → 90 으로 10 내려갔으니, 펌웨어는 대략 **1,170번** 을 수명으로 보는 셈이다
241 | Total_LBAs_Written | 22,481,189,514 | × 512 B = 호스트가 쓴 양 **11.5 TB**
5 · 179 · 181 · 182 · 183 | 재할당 · 예비 블록 · 쓰기 실패 · 지우기 실패 · 불량 블록 | 모두 0 | 아직 고장 난 블록이 없다
187 · 195 | 고치지 못한 오류 · ECC 오류율 | 0 · 0 | 읽기 오류도 없었다 (아직)
199 | CRC_Error_Count | 0 | SATA 케이블 · 링크 문제 없음
190 | 온도 | 31 °C | 켠 뒤 40분 동안 28 → 31 °C
```

**지금까지의 WAF (평생)** : NAND 에 쓴 양 ≈ 177 × 128 GiB ≈ 16.1 TB, 호스트가 쓴 양 11.5 TB → **WAF ≈ 1.4**. 보통 PC 의 쓰기 (대부분 순차, 빈 공간 넉넉, TRIM) 에서 기대하는 값이다. 실험 8 의 랜덤 쓰기 (모델 예측 7.8) 와 비교할 기준이 된다. (177 의 눈금이 크고, NAND 128 GiB 는 알려진 값이라 ±10% 쯤의 어림이다.)

**남은 수명** : 1,170 − 117 ≈ 1,050번 더 지울 수 있다 (펌웨어의 기준으로). 실험 18 에서 이 기준을 실제로 넘겨 본다.

**'믿을 수 없게 됨' 은 SMART 에 보이지 않는다.** 오류 · 불량 블록 카운터가 모두 0 이고, 오류 로그 (`No Errors Logged`) 도 자가 진단 기록도 비어 있다. 문제가 있다면 오래된 데이터의 읽기 속도 쪽일 것이다 : 실험 1 이 확인한다.

**ATA 기능** (`hdparm -I`)

```table
보이는 것 | 뜻 | 어느 실험
`Data Set Management TRIM supported (limit 8 blocks)` | TRIM 지원 | 4
`Deterministic read ZEROs after TRIM` **줄이 없다** | 드라이브는 '0 으로 읽힌다' 를 약속하지 않는다. 그런데 커널은 이 모델에 `zeroaftertrim` 예외를 적용한다 ([Linux 명령 4절](/old-ssd-experiments/linux-commands/)). 누가 맞는지 실험 4 가 잰다 | 4
`Device encrypts all user data` | **항상 암호화하는 드라이브** : Secure Erase 가 키 교체일 가능성이 크다 | 14
Security : `supported`, `not enabled`, **`frozen`**, `enhanced erase`, `2min … 8min` | BIOS 가 보안 명령을 잠갔다. 실험 14 전에 절전 → 깨우기로 푼다. 드라이브가 말하는 지우기 시간 : 보통 2분, enhanced 8분 | 14
`Write cache` (켜짐), `WRITE_DMA_FUA_EXT` 지원 | 드라이브는 FUA 를 지원하지만 커널은 쓰지 않는다 (`doesn't support DPO or FUA` 는 커널의 기본 설정). 데이터를 지키는 방법은 FLUSH 뿐 | 7, 17
`Host Protected Area feature set` (켜짐), `max sectors` 같음 | HPA 를 쓸 수 있고, 지금 숨긴 영역은 없다 | 10
`Queue depth: 32`, Gen3 (6.0 Gb/s) | NCQ 32, SATA 3 | 5
Extended self-test : **70분** (SMART 가 권하는 시간) | 실험 2 에서 실제 시간과 비교 | 2
Device Statistics log : 지원하지 않음 | 실험 2 의 `devstat` 는 비어 있을 것이다 | 2
```

같은 명령을 08:44 에도 한 번 했다 (`20261018-084416-check`) : 켜진 시간이 1시간 늘어난 것 말고는 같다.
</div>

@@NAV@@
