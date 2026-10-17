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
<b>연결</b><span>USB 그대로 (지금 상태)</span>
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
컨트롤러 | Samsung MEX (ARM 코어 3개로 알려짐) | 리뷰 (실험 9 에서 확인)
지금 내용 | 옛 Windows 디스크 : EFI · MSR · NTFS 111 GB (91% 참) · 복구 | `lsblk -f`, `df`
파일 날짜 | 2018 – 2024.12 (hiberfil.sys 마지막 수정 2024.12.08) | `ls -la`
지금 연결 | USB 3.0 어댑터 (ASMedia 19da:1125), 드라이버 `uas`, TRIM 안 됨 | `lsusb -t`, `lsblk`
```

<div class="check" markdown="1">
**840 EVO 와 '오래된 데이터 읽기 저하'.** 840 EVO 는 2014년, 오래전에 쓴 데이터를 읽는 속도가 크게 떨어지는 문제로 널리 알려졌다. Samsung 은 그해 10월 펌웨어 `EXT0BB6Q` 와 복구 도구를, 2015년에 오래된 데이터를 주기적으로 다시 쓰는 펌웨어 `EXT0DB6Q` 를 냈다고 기억한다 (버전과 날짜는 확인이 필요하다).
이 드라이브의 `EXT0CB6Q` 가 그 사이 어디에 있는지는 확인하지 못했다. **이 드라이브가 실험 1 에 특히 좋은 이유다.**
</div>

## 1단계 : 데이터가 필요한지 정하기 (Ryu)

실험 1 은 지금 데이터를 **읽기만** 한다. 실험 2 부터는 모두 지운다. 그 전에 남길 것이 있으면 다른 디스크로 복사한다 (Windows 의 `Users`, `C++ Master pdf` 폴더 등).
복사 자체도 오래된 데이터를 읽는 일이므로, 실험 1 을 **먼저** 한 뒤에 복사하는 편이 측정에 좋다.

## 2단계 : 도구 설치

```
$ sudo apt install smartmontools fio sysstat
$ fio --version            # fio-3.36 이 나와야 한다
$ smartctl --version | head -1
```

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
9 Power_On_Hours | 얼마나 쓰였나
177 Wear_Leveling_Count | 지금까지의 평균 P/E : 실험 8 의 남은 수명 계산
241 Total_LBAs_Written | 지금까지 호스트가 쓴 양
5 · 179 · 181 · 182 · 183 · 187 | '믿을 수 없게 됨' 이 실제로 무엇인지 : 재할당, 예비 블록, 실패, 고치지 못한 오류
195 ECC_Error_Rate | 셀 상태
```

## 5단계 : 읽기 전용으로 다시 마운트

지금 NTFS 파티션은 읽고 쓰기 (`rw`) 로 붙어 있다. 실험 1 동안 접근 시각 같은 작은 쓰기도 없도록 읽기 전용으로 바꾼다.

```
$ sudo umount /media/ryuj/C8922986922979D8
$ sudo mkdir -p /mnt/old840
$ sudo mount -t ntfs-3g -o ro /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K-part3 /mnt/old840
$ findmnt /mnt/old840          # OPTIONS 에 ro
```

`ntfs-3g` 로 붙여야 `fileage.py` 가 NTFS 생성 시각 (`system.ntfs_crtime`) 을 읽을 수 있다.
Windows 가 최대 절전 상태 (hiberfil.sys) 로 꺼져 있어서 `ntfs-3g` 가 마운트를 거절하면, 읽기 전용 (`-o ro`) 이므로 그대로 진행해도 된다는 안내가 나온다.

## 6단계 : SATA 로 옮기기 (실험 1 이 끝난 뒤)

메인보드 (MSI MAG B760M MORTAR II) 의 SATA 포트는 4개로 알고 있고, 모두 차 있다 (`ata5`–`ata8`).
Linux 에 보이는 `ata1`–`ata4` 는 칩셋이 늘 보여 주는 이름일 뿐 커넥터가 없을 가능성이 크다 (매뉴얼의 SATA1–4 그림으로 확인).

@@FIG setup_sata@@

1. 실험 1 이 끝나고, 남길 데이터를 복사한다
2. `sdc` (WD 1TB HDD) 의 파일 시스템 두 개가 쓰이고 있지 않은지 확인하고, **컴퓨터를 끈다** (SATA hot-plug 는 꺼져 있을 가능성이 크다)
3. `sdc` 에서 SATA 데이터 케이블과 전원 케이블을 빼서 840 EVO 120GB 에 꽂는다
4. 켠 뒤 확인 : `lsblk -o NAME,MODEL,SERIAL,TRAN,DISC-MAX` 에서 840 EVO 120GB 가 `sata`, `DISC-MAX` 가 `0B` 가 아니어야 한다 (`sdX` 글자는 바뀔 수 있다 : 상관없다)
5. `/etc/fstab` 에 `sdc` 의 파일 시스템 두 개 (HDD_WD_1st_488G, HDD_WD_2nd_443G) 가 있지만 둘 다 `nofail` 이 붙어 있다 (2026.10.17 확인) : 디스크가 없어도 부팅은 그대로 된다. 그 폴더 (`/mnt/a43c4a49-…`, `/mnt/ac82f667-…`) 만 비어 보인다
6. `sudo ./lab.sh check` 를 한 번 더 : SATA 에서의 SMART · `hdparm -I` (TRIM 지원 줄) 을 남긴다

<div class="tip" markdown="1">
**실험이 다 끝나면** 케이블을 원래대로 `sdc` 에 꽂는다. 다른 방법 : PCIe SATA 카드 (ASM1166 · JMB585 칩) 를 쓰면 포트를 바꿀 필요가 없다.
</div>

## 결과

<div class="result" markdown="1">
아직 실행 전. `sudo ./lab.sh check` 결과가 나오면 여기에 SMART 표와 해석을 붙인다.
</div>

@@NAV@@
