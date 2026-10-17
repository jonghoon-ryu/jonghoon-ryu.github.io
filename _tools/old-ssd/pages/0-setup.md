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
<b>연결</b><span>SATA (2026.10.17 에 옮김 : 6단계)</span>
<b>시간</b><span>30분</span>
<b>명령</b><span><code>sudo ./lab.sh check</code></span>
</div>

## 드라이브

```table
항목 | 값 | 출처
모델 | Samsung SSD 840 EVO 120GB | `lsblk`
시리얼 | `S1D6NSAFB40389K` | `lsblk`, `/dev/disk/by-id`
펌웨어 | `EXT0CB6Q` | `lsblk -o REV` (같은 컴퓨터의 840 EVO 500GB 는 `EXT0BB6Q`)
용량 | 120,034,123,776 B (234,441,648 섹터) | 커널 로그
NAND | TLC, 128 GiB 로 알려짐 | 리뷰 · 자료 (확인 필요)
SLC 버퍼 (TurboWrite) | 120GB 모델은 약 3 GB 로 알려짐 | Samsung 자료 (확인 필요)
컨트롤러 | Samsung MEX (ARM 코어 3개로 알려짐) | 리뷰 (실험 19 에서 확인)
지금 내용 | 옛 Windows 디스크 : EFI · MSR · NTFS 111 GB (91% 참) · 복구 | `lsblk -f`, `df`
파일 날짜 | 2018 – 2024.12 (hiberfil.sys 마지막 수정 2024.12.08) | `ls -la`
지난 이력 | 2024.12 쯤 마지막으로 쓴 뒤 **1년 넘게 전원 없이** 보관. 2026.10.17 에 다시 연결해 Ryu 가 파일 몇 개를 읽고 몇 개를 새로 씀 (약 17.6 MB) | Ryu, `/proc/diskstats`
지금 연결 | 메인보드 SATA `ata5` (`/dev/sda`), TRIM 됨 (`DISC-GRAN 512B`, `DISC-MAX 2G`). 처음에는 USB 3.0 어댑터 (ASMedia 19da:1125, `uas`) 로 `/dev/sdg` 였고 TRIM 이 안 됐다 | `lsblk -o NAME,TRAN,DISC-MAX`, `/sys/block/sda`
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
2. `hdparm -I` 로 펌웨어 · TRIM 지원 줄을 보여 준다 (USB 어댑터가 막으면 비어 있을 수 있다)
3. `smartctl -x` (USB 면 `-d sat`) 를 텍스트와 JSON 으로 저장하고, 실험에 쓰는 속성만 골라 보여 준다

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

10.17 에는 NTFS 파티션이 파일 관리자를 통해 읽고 쓰기 (`rw`) 로 붙어 있었다 (`/media/ryuj/C8922986922979D8`). 그때 Ryu 가 파일을 읽고 쓴 기록 (쓴 시각, 접근 시각) 이 실험 1 에서 파일을 세 무리로 나누는 근거가 된다.
2026.10.18 아침에는 붙어 있지 않다 (`lsblk` 에 마운트 지점 없음). 실험 1 동안 접근 시각 같은 작은 쓰기도 없도록 **읽기 전용** 으로 붙인다.

```
$ findmnt /media/ryuj/C8922986922979D8 && sudo umount /media/ryuj/C8922986922979D8   # 붙어 있을 때만
$ sudo mkdir -p /mnt/old840
$ sudo mount -t ntfs-3g -o ro /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K-part3 /mnt/old840
$ findmnt /mnt/old840          # OPTIONS 에 ro
```

**그 전까지 이 파티션을 파일 관리자로 열지 않는다.** 썸네일 · 미리 보기를 만드느라 오래된 데이터를 읽어 버린다 (읽힌 데이터는 펌웨어가 새로 쓸 수 있다 : 실험 1 의 H5).
읽기 전용 마운트는 접근 시각도 바꾸지 않으므로, 10.17 에 남은 접근 시각이 그대로 보존된다.
`umount` 가 `target is busy` 라고 하면 그 폴더를 연 창이나 터미널을 닫고 다시 한다.

`ntfs-3g` 로 붙여야 `fileage.py` 가 NTFS 생성 시각 (`system.ntfs_crtime`) 을 읽을 수 있다.
Windows 가 최대 절전 상태 (hiberfil.sys) 로 꺼져 있어서 `ntfs-3g` 가 마운트를 거절하면, 읽기 전용 (`-o ro`) 이므로 그대로 진행해도 된다는 안내가 나온다.

## 6단계 : SATA 로 옮기기 (2026.10.17 완료)

처음 계획은 실험 1 을 USB 로 한 뒤 `sdc` (WD 1TB HDD) 자리에 꽂는 것이었다. 실제로는 **실험 1 전에** 옮겼고, 자리도 달랐다 :
840 EVO 120GB 가 `ata5` 에 있던 **840 EVO 500GB 와 자리를 바꿨다**. 500GB 는 대신 USB 어댑터로 간다.

@@FIG setup_sata@@

```table
디스크 | 전 | 지금 (2026.10.17 16:44 부팅 뒤)
840 EVO 120GB (실험용, `…40389K`) | `sdg`, USB, TRIM 안 됨 | **`sda`, SATA `ata5`, TRIM 됨**
840 EVO 500GB (`…85299B`) | `sda`, SATA `ata5` | `sde`, USB (`/etc/fstab` 에 `nofail` 이라 부팅에 문제 없음)
750 EVO · WD 1TB · Seagate 2TB | `sdb` · `sdc` · `sdd` (`ata6`–`ata8`) | 그대로
```

<div class="check" markdown="1">
**글자가 바뀌었다.** 전에 `sda` 는 500GB 였고, 지금 `sda` 는 실험용 120GB 다. 옛 메모의 `/dev/sdX` 를 그대로 쓰면 다른 디스크를 지운다.
`lab.sh` 는 장치를 이름이 아니라 **시리얼** 로 찾으므로 그대로 쓰면 된다.
2026.10.18 아침의 `lsblk` 에서는 USB 쪽 디스크 구성이 또 달랐다 (실험용 120GB 는 그대로 `sda`). 글자는 부팅 · 연결마다 바뀔 수 있다.
</div>

**실험 1 에는 오히려 좋다.** 실험 1 (오래된 데이터) 과 실험 3 의 `scan fresh` (새 데이터) 를 같은 SATA 연결에서 재므로, 두 곡선의 차이는 '데이터의 나이' 뿐이다. USB 로 다시 옮겨 한 번 더 재는 단계는 필요 없어졌다.

확인 : `sudo ./lab.sh check` 를 SATA 에서 실행하면 SMART 와 `hdparm -I` (TRIM 지원 줄) 이 모두 나와야 한다 (USB 와 달리 `-d sat` 없이).

<div class="tip" markdown="1">
**실험이 다 끝나면** 500GB 를 `ata5` 로 되돌린다. 다른 방법 : PCIe SATA 카드 (ASM1166 · JMB585 칩) 를 쓰면 포트를 바꿀 필요가 없다.
</div>

## 결과

<div class="result" markdown="1">
아직 실행 전. `sudo ./lab.sh check` 결과가 나오면 여기에 SMART 표와 해석을 붙인다.
</div>

@@NAV@@
