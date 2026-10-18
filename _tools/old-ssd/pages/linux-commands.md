---
layout: default
title: SSD 를 다루는 Linux 명령
permalink: /old-ssd-experiments/linux-commands/
---
@@STYLE@@

# SSD 를 다루는 Linux 명령

**처음 보는 사람을 위한 안내.** 디스크를 찾고, 상태를 보고, 속도를 재고, (조심해서) 지우는 명령을 차례로 익힌다.
여기 나오는 출력은 모두 **이 컴퓨터 (MSI B760M, Ubuntu 24.04) 에서 실제로 나온 것** 이다 (2026.10.18). 실험할 840 EVO 120GB 는 메인보드 SATA 에 붙은 `sda` 다. `sudo` 가 필요한 명령은 출력을 아직 받지 못해서 명령과 읽는 법만 적었다.

<div class="glance">
<b>읽는 순서</b><span>1 층 그림 → 2 디스크 찾기 → 3 마운트 → 4 연결 → 5 SMART → 6 TRIM → 7 속도 재기 → 8 지켜보기 → 9 위험한 명령 → 10 요약표. fio 는 <a href="/old-ssd-experiments/fio/">따로 한 페이지</a></span>
<b>준비</b><span><code>sudo apt install smartmontools fio sysstat</code> (smartctl, fio, iostat)</span>
<b>약속</b><span><code>$</code> 로 시작하는 줄 = 입력하는 명령, 나머지 = 출력. <code>…</code> = 줄임</span>
</div>

## 1. 디스크는 여러 층으로 보인다

파일 하나를 쓰면 여러 층을 거쳐 NAND 에 닿는다. 명령마다 **어느 층을 보는지** 가 다르다. 헷갈릴 때는 이 그림으로 돌아온다.

@@FIG cmd_layers@@

## 2. 어떤 디스크가 있나

### `lsblk` : 블록 장치 목록

가장 먼저, 가장 자주 쓰는 명령이다. `-e7` 은 snap 이 만드는 loop 장치를 숨긴다. sudo 가 필요 없다.

```
$ lsblk -e7
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda           8:0    0 111.8G  0 disk
├─sda1        8:1    0   100M  0 part
├─sda2        8:2    0    16M  0 part
├─sda3        8:3    0 111.2G  0 part /mnt/old840
└─sda4        8:4    0   532M  0 part
sdb           8:16   0 465.8G  0 disk
└─sdb1        8:17   0 465.8G  0 part /mnt/c4305fe5-2710-0000-9b3d-7085c278815e
…
nvme0n1     259:0    0   1.8T  0 disk
├─nvme0n1p1 259:1    0   512M  0 part /boot/efi
└─nvme0n1p2 259:2    0   1.8T  0 part /
```

```table
열 | 뜻
`NAME` | 장치 이름. 들여쓴 줄은 그 디스크의 파티션
`SIZE` | 크기. **GiB** (2³⁰ 바이트) 단위라서 120 GB 디스크가 111.8G 로 보인다
`RO` | 1 이면 읽기 전용
`TYPE` | `disk` = 디스크 전체, `part` = 파티션
`MOUNTPOINTS` | 파일 시스템이 붙은 폴더. 비어 있으면 마운트 안 됨
```

이름 읽는 법 :

@@FIG cmd_names@@

### 열을 골라서 보기 : `-o`

`-o` 로 보고 싶은 열만 고른다. 실험에 필요한 것은 모델, 시리얼, 연결 방식 (`TRAN`), 회전 여부 (`ROTA`) 다.

```
$ lsblk -e7 -d -o NAME,MODEL,SERIAL,SIZE,TRAN,ROTA,TYPE
NAME        MODEL                     SERIAL            SIZE TRAN   ROTA TYPE
sda         Samsung SSD 840 EVO 120GB S1D6NSAFB40389K 111.8G sata      0 disk
sdb         Samsung SSD 750 EVO 500GB S36TNWAH617826R 465.8G sata      0 disk
sdc         WDC WD10EZEX-00BN5A0      WD-WCC3F3YSLLZ4 931.5G sata      1 disk
sdd         ST2000DM008-2UB102        WK30NGZQ          1.8T sata      1 disk
sde         Samsung SSD 870 EVO 500GB S6R0NX0TC15146K 465.8G usb       1 disk
sdf         PSSD T7                   S5SYNJ0R103097F 931.5G usb       0 disk
sdg         TOSHIBA MQ04UBD200        78S4T02VT         1.8T usb       1 disk
nvme0n1     Samsung SSD 990 EVO 2TB   S7GDNS0X212722L   1.8T nvme      0 disk
```

(`-d` 는 파티션 줄을 빼고 디스크만 보인다.)

<div class="tip" markdown="1">
**`ROTA` 를 보라.** `ROTA` 는 '회전하는 디스크인가' 다. 하드디스크 (`sdc`, `sdd`, `sdg`) 는 `1`, SSD 는 `0` 이어야 한다. 그런데 `sde` 는 SSD (870 EVO) 인데 `1` 이다 : USB 어댑터가 커널에게 그렇게 알려 주기 때문이다.
USB 를 거치면 드라이브에 대한 정보가 이렇게 바뀌거나 사라진다 (TRIM, SMART 도). 그래서 실험은 SATA 에 직접 붙여서 한다.
</div>

`lsblk` 의 열 목록은 `lsblk --help` 맨 아래에 있다. 이 페이지에서 쓰는 것은 `FSTYPE` (파일 시스템), `DISC-GRAN` · `DISC-MAX` (TRIM, 6절), `REV` (펌웨어) 정도다.

### `/dev/disk/by-id/` : 바뀌지 않는 이름

`sda` 의 `a` 는 커널이 디스크를 찾은 순서로 붙는다. 디스크를 더하거나 빼거나, 포트를 바꾸면 다른 글자가 될 수 있다. **지우는 명령에 `/dev/sdX` 를 직접 쓰는 것이 위험한 이유다.**
`/dev/disk/by-id/` 에는 모델과 시리얼로 만든, 바뀌지 않는 이름이 있다 (실제 장치로 가는 바로가기).

```
$ ls -l /dev/disk/by-id/ | grep 840_EVO_120
lrwxrwxrwx 1 root root  9 Oct 18 08:05 ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K -> ../../sda
lrwxrwxrwx 1 root root 10 Oct 18 08:05 ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K-part1 -> ../../sda1
…
$ readlink -f /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K
/dev/sda
```

`lab.sh` 는 이 방법으로 시리얼에서 장치를 찾는다. 사람도 똑같이 할 수 있다 : `DEV=$(readlink -f /dev/disk/by-id/ata-…_S1D6NSAFB40389K)`.

## 3. 마운트 : 디스크와 폴더 잇기

**마운트** = 파티션 안의 파일 시스템을 폴더 하나에 붙이는 일이다. 붙은 동안에는 그 파티션에 직접 쓰면 안 된다 (파일 시스템이 망가진다).

### `findmnt`, `df` : 무엇이 어디에 붙어 있나

```
$ findmnt -t ext4,fuseblk,vfat
TARGET                                       SOURCE         FSTYPE  OPTIONS
/                                            /dev/nvme0n1p2 ext4    rw,relatime,errors=remount-ro
├─/boot/efi                                  /dev/nvme0n1p1 vfat    rw,relatime,fmask=0077,…
├─/mnt/a43c4a49-0587-46c6-b310-ebae2da0429c  /dev/sdc1      ext4    rw,nosuid,nodev,relatime
…
├─/mnt/old840                                /dev/sda3      fuseblk ro,relatime,user_id=0,group_id=0,allow_other,blksize=4096
…

$ df -hT -x tmpfs -x squashfs
Filesystem     Type      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2 ext4      1.8T  1.7T   61G  97% /
…
/dev/sda3      fuseblk   112G  101G   11G  91% /mnt/old840
```

- `OPTIONS` 의 `rw` = 읽고 쓰기, `ro` = 읽기만. 실험할 디스크의 `/mnt/old840` 은 `ro` 다 ([0. 준비](/old-ssd-experiments/0-setup/) 5단계).
- `fuseblk` = NTFS 를 사용자 공간 프로그램 (`ntfs-3g`) 이 다루고 있다는 뜻. 커널 안의 `ntfs3` 드라이버로 마운트할 수도 있다.
- `df` 의 `Use%` 는 **파일 시스템** 이 보는 사용량이다. SSD 안의 FTL 은 이것을 모른다 (6절 TRIM 이 그 틈을 메운다).

### `mount`, `umount` : 붙이고 떼기

```
$ sudo mkdir -p /mnt/old840
$ sudo mount -t ntfs-3g -o ro /dev/disk/by-id/ata-Samsung_SSD_840_EVO_120GB_S1D6NSAFB40389K-part3 /mnt/old840   # 읽기 전용으로 붙이기
$ findmnt /mnt/old840                                       # OPTIONS 에 ro 가 있는지 확인
$ sudo umount /mnt/old840                                   # 떼기 (실험 3 부터는 떼어 둔다)
```

`umount` 가 `target is busy` 로 실패하면, 그 폴더를 연 터미널이나 파일 관리자 창을 닫는다. 누가 쓰는지는 `sudo fuser -vm /mnt/old840` 로 본다.

## 4. 어떻게 연결되어 있나

연결 방식 (SATA, USB, NVMe) 에 따라 쓸 수 있는 기능이 다르다 (TRIM, SMART, 속도).

### `/sys/block/` : 커널이 아는 모든 것

`/sys` 는 커널이 자기 정보를 파일처럼 보여 주는 곳이다. 읽기만 하면 sudo 가 필요 없다.

```
$ readlink -f /sys/block/sda
/sys/devices/pci0000:00/0000:00:17.0/ata5/host4/target4:0:0/4:0:0:0/block/sda
```

경로를 읽으면 연결이 보인다 : **SATA 컨트롤러 (PCI 00:17.0) → `ata5` 포트 → 디스크 `sda`**. 디스크 하나의 설정은 `queue/` 아래에 있다 :

```
$ for f in rotational logical_block_size discard_max_bytes max_sectors_kb; do echo "$f = $(cat /sys/block/sda/queue/$f)"; done
rotational = 0
logical_block_size = 512
discard_max_bytes = 2147450880
max_sectors_kb = 1280
```

```table
파일 | 값 | 뜻
`rotational` | 0 | SSD (회전하지 않음)
`logical_block_size` | 512 | 호스트가 보는 섹터 크기 (실험 6)
`discard_max_bytes` | 2147450880 | TRIM 명령 하나로 약 2 GB 까지 보낼 수 있다. 0 이면 TRIM 을 못 보낸다
`max_sectors_kb` | 1280 | 커널이 요청 하나를 이 크기 (KiB) 보다 크게 만들지 않는다
```

### `journalctl -k` : 부팅할 때 커널이 한 말

디스크를 찾으면 커널이 기록을 남긴다. `dmesg` 로도 같은 것을 본다 (Ubuntu 에서는 `sudo dmesg`).

```
$ journalctl -k -b | grep -E "ata5|\[sda\]| sda"
ata5: SATA link up 6.0 Gbps (SStatus 133 SControl 300)
ata5.00: Model 'Samsung SSD 840 EVO 120GB', rev 'EXT0CB6Q', applying quirks: noncqtrim zeroaftertrim nodmalog
ata5.00: ATA-9: Samsung SSD 840 EVO 120GB, EXT0CB6Q, max UDMA/133
ata5.00: 234441648 sectors, multi 1: LBA48 NCQ (depth 32), AA
ata5.00: Features: Trust
ata5.00: configured for UDMA/133
sd 4:0:0:0: [sda] 234441648 512-byte logical blocks: (120 GB/112 GiB)
sd 4:0:0:0: [sda] Write cache: enabled, read cache: enabled, doesn't support DPO or FUA
 sda: sda1 sda2 sda3 sda4
sd 4:0:0:0: [sda] supports TCG Opal
sd 4:0:0:0: [sda] Attached SCSI disk
```

(앞의 날짜 · 호스트 이름은 줄였다.) 실험에 쓸 정보가 많다 :

```table
줄 | 뜻 | 이 정보를 쓰는 실험 (번호)
`SATA link up 6.0 Gbps` | SATA 3 로 붙었다 : 상한 약 550 MB/s | 5
`applying quirks: noncqtrim zeroaftertrim …` | 커널이 이 모델에 맞춰 바꾸는 동작 : TRIM 은 NCQ 없이 보내고 (`noncqtrim`), TRIM 한 곳은 0 으로 읽힌다고 믿는다 (`zeroaftertrim`) | 4
`NCQ (depth 32)` | 명령을 32개까지 한꺼번에 받는다 | 5
`234441648 512-byte logical blocks` | 정확한 용량. 234,441,648 × 512 = 120,034,123,776 바이트 | 0 (준비)
`Write cache: enabled … doesn't support DPO or FUA` | 쓰기 캐시가 켜져 있고, '이 쓰기만 바로 NAND 에' (FUA) 는 지원하지 않는다 : 데이터를 지키려면 FLUSH 뿐 | 7, 17
`supports TCG Opal` | 자체 암호화 드라이브 (SED) 의 표준을 지원한다 | 14
```

새 디스크가 안 보일 때는 **이 로그에 아무것도 없는지** 부터 본다. 없으면 전원 · 케이블 · 포트 문제다.

## 5. SMART : 드라이브가 스스로 센 숫자

SMART 는 드라이브 안의 펌웨어가 세는 카운터들이다 : 전원 켠 시간, 쓴 양, 지운 횟수, 고친 오류, 남은 예비 블록… FTL 을 밖에서 들여다보는 가장 좋은 창이다.

### `smartctl` (smartmontools)

```
$ sudo smartctl -i /dev/sda            # 정보 : 모델, 펌웨어, SATA 속도
$ sudo smartctl -H /dev/sda            # 한 줄 판정 : PASSED / FAILED
$ sudo smartctl -A /dev/sda            # 속성 표 (아래)
$ sudo smartctl -x /dev/sda            # 전부 (로그, 온도 기록 포함)
```

`-A` 의 속성 표는 이렇게 생겼다 (열 이름만, 실제 값은 실험 0 에서 받는다) :

```
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
```

```table
열 | 뜻
`ID#` · `ATTRIBUTE_NAME` | 속성 번호와 이름. 번호의 뜻은 제조사마다 조금씩 다르다
`VALUE` · `WORST` | **정규화 값** (보통 100 또는 200 에서 시작해 내려간다), 지금까지의 최저
`THRESH` | `VALUE` 가 이 아래로 내려가면 '실패'
`RAW_VALUE` | **진짜 숫자** (시간, 횟수, 섹터 수). 실험에서 주로 보는 열
```

Samsung SATA SSD 에서 흔히 보이는 속성 중 실험에 쓰는 것 :

```table
ID | 이름 | 실험에서의 의미
9 | Power_On_Hours | 전원이 켜져 있던 시간
177 | Wear_Leveling_Count | raw = 블록들의 **평균 지움 횟수** (P/E). 실험 12, 18
179 | Used_Rsvd_Blk_Cnt_Tot | 써 버린 예비 블록 수. 수명 끝에 늘어난다
181 · 182 | Program_Fail · Erase_Fail | 쓰기 · 지우기 실패 횟수
187 | Uncorrectable_Error_Cnt | ECC 로도 못 고친 오류
195 | ECC_Error_Rate | ECC 가 고친 오류 (늘어날수록 셀 상태가 나쁘다)
241 | Total_LBAs_Written | 호스트가 쓴 양 (512 바이트 단위). 실험 12
```

### SMART 한 줄 읽기 : 예 (190 온도)

실험 3 (2026.10.18) 의 한 줄이다 :

```
190 Airflow_Temperature_Cel   -O--CK   069   052   000    -    31
                               플래그  VALUE WORST THRESH FAIL RAW
```

```table
열 | 값 | 읽는 법
플래그 `-O--CK` | `P` 가 없다 | 고장 예고 (pre-failure) 속성이 아니다 : 온도가 높다는 것만으로 '고장' 판정은 나지 않는다. `O` 평소에도 갱신, `C` 수를 세는 속성, `K` 저절로 저장 (첫 자리 `P` 가 있는 5 · 177 · 179 등은 기준값 아래로 내려가면 '고장 임박' 이다)
**RAW** | **31** | 실제 숫자 : **지금 31 °C**
**VALUE** | **069** | 정규화 값. 온도는 Samsung 이 **100 − 온도** 로 정한다 : 100 − 31 = 69. 클수록 시원하다
**WORST** | **052** | 지금까지 가장 낮았던 VALUE = **가장 뜨거웠던 때** : 100 − 52 = **48 °C**
**THRESH** | **000** | 고장 기준값. 0 = 이 속성으로는 고장 판정을 하지 않는다
FAIL | `-` | 지금도, 예전에도 기준값에 닿은 적이 없다
```

**분석하는 법**

1. **WORST 가 바뀌었는지 본다.** 이날 아침 (실험 0–2) 의 WORST 는 053 (13년 동안 가장 뜨거웠던 때 47 °C) 이었고, 실험 3 의 전체 쓰기 뒤에는 052 (48 °C) 가 되었다 : **이 드라이브의 평생 최고 온도를 우리 실험이 새로 썼다.**
2. **RAW 를 실험마다 이어 본다** : 드라이브가 얼마나 일했는지가 보인다.

```table
때 | RAW | 하던 일
켠 뒤 (08:20) | 28 °C | 쉼
오래된 데이터 읽기 (실험 1, 2) | **38 – 40 °C** | 다시 읽기가 많은 느린 읽기
오래된 데이터의 자가 진단 (실험 2) | 31 → 39 °C | 드라이브가 안에서 전체를 읽음
120 GB 쓰기 (실험 3, 1단계) | 32 → **48 °C** | 13분 쉬지 않고 쓰기 : 가장 힘든 일
새 데이터 읽기 (실험 3, 3단계) | 31 → 33 °C | 빠른 읽기, 다시 읽기 없음
```

   같은 양을 같은 방법으로 읽었는데, 오래된 데이터는 약 9 °C, 새 데이터는 약 2 °C 올렸다 : 다시 읽기 (read retry) 의 또 다른 증거다.
3. **위험한 값인가** : SSD 의 동작 온도는 보통 0 – 70 °C 로 정해져 있고, 많은 드라이브가 70 °C 근처부터 스스로 속도를 낮춘다 (thermal throttling). 48 °C 는 괜찮다. 밤새 쓰는 실험 8 과 실험 18 에서는 지켜본다.

**모든 SMART 줄에 쓰는 규칙** : 실제 숫자는 **RAW**, 제조사의 판정은 **VALUE 와 THRESH** 의 비교, 드라이브 역사의 가장 나빴던 순간은 **WORST**. VALUE 가 무엇을 뜻하는지는 속성과 제조사마다 다르다 : 190 은 '100 − 온도', 177 은 '정해진 수명 중 남은 %'.

### `lab.sh` 가 실험마다 찍는 SMART 14줄

`lab.sh` 는 드라이브에 무언가를 하는 실험마다 **앞 (`smart-before`)** 과 **뒤 (`smart-after`)** 에 SMART 를 저장하고, 그중 실험에 쓰는 속성 14개를 화면에 찍는다. 예 : 실험 8 을 시작할 때 (2026.10.18 15:36)

```
     5 Reallocated_Sector_Ct   PO--CK   100   100   010    -    0
     9 Power_On_Hours          -O--CK   097   097   000    -    10379
    12 Power_Cycle_Count       -O--CK   095   095   000    -    4600
   177 Wear_Leveling_Count     PO--C-   089   089   000    -    123
   179 Used_Rsvd_Blk_Cnt_Tot   PO--C-   100   100   010    -    0
   181 Program_Fail_Cnt_Total  -O--CK   100   100   010    -    0
   182 Erase_Fail_Count_Total  -O--CK   100   100   010    -    0
   183 Runtime_Bad_Block       PO--C-   100   100   010    -    0
   187 Uncorrectable_Error_Cnt -O--CK   100   100   000    -    0
   190 Airflow_Temperature_Cel -O--CK   068   052   000    -    32
   195 ECC_Error_Rate          -O-RC-   200   200   000    -    0
   199 CRC_Error_Count         -OSRCK   100   100   000    -    0
   235 POR_Recovery_Count      -O--C-   099   099   000    -    1036
   241 Total_LBAs_Written      -O--CK   099   099   000    -    23723464395
```

열의 뜻 (플래그, VALUE, WORST, THRESH, RAW) 은 위의 'SMART 한 줄 읽기' 를 본다. 짧게 : **RAW** = 실제 숫자, **VALUE** = 제조사의 점수 (보통 100 에서 내려간다), **WORST** = 가장 나빴던 점수, **THRESH** = 고장 판정선, 플래그의 첫 글자 **P** = 그 선에 닿으면 '고장 임박'.

**14줄 하나하나** (값은 위의 스냅숏, '오늘' = 2026.10.18 실험 0 – 7)

```table
ID | 이름 | 지금 (RAW / VALUE) | 무엇을 세나 | 오늘 어떻게 변했나 | 쓰는 실험
5 | Reallocated_Sector_Ct | 0 / 100 | 나빠서 예비로 바꿔 단 블록 수 | 0 그대로 | 18
9 | Power_On_Hours | 10,379 시간 / 97 | 전원이 켜져 있던 시간의 합 | 10,373 → 10,379 (오늘 켠 시간만큼) | 0
12 | Power_Cycle_Count | 4,600 / 95 | 전원을 켠 횟수 | 그대로 (오늘은 한 번 켰다) | 0
177 | Wear_Leveling_Count | **123** / **89** | 블록들의 **평균 지움 횟수** (P/E). VALUE 는 펌웨어가 보는 남은 수명 % | **117 → 123** : 드라이브 전체를 약 6번 덮어쓴 만큼. VALUE 는 122 에서 90 → 89 | 12, 18
179 | Used_Rsvd_Blk_Cnt_Tot | 0 / 100 | 써 버린 예비 블록 수 (수명 끝에 는다) | 0 그대로 | 18
181 | Program_Fail_Cnt_Total | 0 / 100 | NAND 쓰기 (프로그램) 실패 | 0 그대로 | 18
182 | Erase_Fail_Count_Total | 0 / 100 | 블록 지우기 실패 | 0 그대로 | 18
183 | Runtime_Bad_Block | 0 / 100 | 쓰는 동안 나빠진 블록 | 0 그대로 | 18
187 | Uncorrectable_Error_Cnt | 0 / 100 | ECC 와 다시 읽기로도 고치지 못한 읽기 | 0 그대로 (오래된 데이터를 아주 느리게 읽었을 때도) | 1, 15, 16
190 | Airflow_Temperature_Cel | **32 °C** / 68 (WORST **52**) | 지금 온도. VALUE = 100 − 온도, WORST = 평생 가장 뜨거웠던 때 | 28 – 48 °C 를 오갔다. WORST 53 → **52** : 평생 최고 48 °C 를 실험 3 이 새로 썼다 | 모든 실험
195 | ECC_Error_Rate | 0 / 200 | ECC 가 고친 오류의 비율 (Samsung 은 늘 0 에 가깝게 보고한다) | 0 그대로 | 1, 15
199 | CRC_Error_Count | 0 / 100 | SATA 케이블 위에서 깨진 전송 (드라이브 탓이 아니라 연결 탓) | 0 그대로 | 0
235 | POR_Recovery_Count | 1,036 / 99 | **정상 종료 없이** 전원이 끊긴 횟수 (Samsung) | 그대로 | 17
241 | Total_LBAs_Written | **23,723,464,395** / 99 | 호스트가 쓴 512 B 섹터의 합 | 22,481,189,514 → 23,723,464,395 : **오늘 636 GB** (평생 12.1 TB) | 12, 18
```

**빠르게 읽는 순서**

1. **오류 8줄이 모두 0 인가** : 5 · 179 · 181 · 182 · 183 · 187 · 195 · 199. 하나라도 앞보다 늘었다면 그 실험의 가장 중요한 결과다. 지금까지 모두 0 이다
2. **177 과 241 의 차이** : 이번 실험이 NAND 를 얼마나 닳게 했고 (177), 호스트가 얼마나 썼나 (241 × 512 B). 둘의 비율이 WAF 다 : `python3 smartdiff.py 결과폴더` 가 계산한다 ([실험 12](/old-ssd-experiments/12-waf/))
3. **190** : 지금 온도와 WORST (평생 최고). 70 °C 근처면 드라이브가 스스로 느려질 수 있다
4. **9 · 12 · 235** : 드라이브의 이력. 실험 17 (전원 차단) 뒤에는 235 가 늘어야 한다

**오늘의 흐름** (실험마다 앞 → 뒤)

```table
실험 | 177 | 241 (× 512 B) | 190 (°C)
0 · 1 · 2 : 읽기만 | 117 그대로 | 그대로 | 31 → 40 (오래된 데이터 읽기가 뜨겁다)
3 `slc` : 120 GB 쓰기 | 117 → 118 | +120.0 GB | 32 → **48**
3 `scan fresh`, `selftest` : 읽기만 | 118 그대로 | 그대로 | 31 → 33 · 31 → 42
4 · 5 : TRIM, 채우기, 쓰기 지도 | 118 → 121 | +490 GB 쯤 | 32 – 47
6 `wsize` : 채우기 + 작은 쓰기 | 122 → 123 | +48.6 GB (측정 부분) | 48 → 43
8 `cliff` 시작 직전 | **123** (VALUE 89) | 평생 **12.1 TB** | 32
```

177 이 6 늘어날 때 241 은 약 636 GB 늘었다 : 6 × 137 GB (NAND 128 GiB) ≈ 822 GB 를 NAND 에 썼다고 보면, 오늘 전체의 WAF 는 약 1.3 (177 의 눈금이 커서 대략의 값이다).

NVMe 드라이브라면 `sudo nvme smart-log /dev/nvme0` (nvme-cli) 가 같은 일을 한다. NVMe 는 속성 번호 대신 정해진 항목 (`data_units_written`, `percentage_used` …) 을 보여 준다.

### `hdparm -I` : ATA 기능 목록

```
$ sudo hdparm -I /dev/sda | grep -iE "model|firmware|trim"
```

`Data Set Management TRIM supported` 같은 줄이 나온다. **`Deterministic read ZEROs after TRIM`** 이 있으면 TRIM 한 LBA 를 읽을 때 반드시 0 이 나온다는 약속이다 (실험 4).

## 6. TRIM : SSD 에게 '이제 안 쓴다' 고 알리기

@@FIG cmd_trim@@

### `lsblk` 로 TRIM 이 되는지 보기

```
$ lsblk -d -o NAME,DISC-GRAN,DISC-MAX,DISC-ZERO /dev/sda /dev/nvme0n1
NAME    DISC-GRAN DISC-MAX DISC-ZERO
sda          512B       2G         0
nvme0n1      512B       2T         0
```

`DISC-GRAN` = TRIM 의 최소 단위, `DISC-MAX` = 명령 하나의 최대 크기 (4절의 `discard_max_bytes`). `DISC-MAX` 가 `0B` 이면 TRIM 을 못 보낸다 (USB 어댑터 중에 그런 것이 많다).

### `fstrim` : 파일 시스템의 빈 곳을 한꺼번에

```
$ sudo fstrim -v /                     # / 의 빈 공간 전부를 TRIM (안전 : 파일은 그대로)
$ systemctl status fstrim.timer
● fstrim.timer - Discard unused filesystem blocks once a week
     Loaded: loaded (/usr/lib/systemd/system/fstrim.timer; enabled; preset: enabled)
     Active: active (waiting) since Sat 2026-10-17 07:24:35 KST; 7h ago
    Trigger: Mon 2026-10-19 01:17:42 KST; 1 day 10h left
```

Ubuntu 는 일주일에 한 번 `fstrim` 을 자동으로 돌린다. 다른 방법은 마운트 옵션 `discard` (지울 때마다 바로 TRIM) 다.

### `blkdiscard` : 디스크 전체를 TRIM — 위험

```
$ sudo blkdiscard /dev/sdX             # 장치 전체의 모든 LBA 를 TRIM : 데이터가 사라진다
```

파일 시스템과 상관없이 **장치 전체** 를 버린다. 지우는 실험을 시작할 때 드라이브를 '막 산' 상태에 가깝게 되돌리는 데 쓴다. 9절의 확인 절차를 거친 뒤에만 쓴다.

## 7. 속도 재기

### 함정 하나 : 페이지 캐시

@@FIG cmd_cache@@

이 컴퓨터의 NVMe 에서 1 GiB 를 쓴 실제 결과다 :

```
$ dd if=/dev/zero of=dd.img bs=1M count=1024
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 0.234506 s, 4.6 GB/s      ← RAM 에 쓴 속도
$ dd if=/dev/zero of=dd.img bs=1M count=1024 oflag=direct
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 0.395092 s, 2.7 GB/s      ← 디스크에 쓴 속도
```

`oflag=direct` (읽기는 `iflag=direct`) 가 없으면 디스크가 아니라 RAM 을 잰다.

### `hdparm -t` : 가장 빠른 읽기 확인

```
$ sudo hdparm -t /dev/sdX               # 3초 동안 순차 읽기 속도 (읽기만 한다)
```

### `fio` : 제대로 재는 도구

`fio` 는 '어떤 모양의 입출력을' (순차 / 랜덤, 크기, 동시에 몇 개) 정확히 만들어 내고, 결과를 자세히 보여 준다. 실험은 모두 fio 로 한다. 옵션과 출력을 하나하나 읽는 법은 [fio 사용법](/old-ssd-experiments/fio/) 페이지에 따로 있다.

```table
옵션 | 뜻 | 실험에서 쓰는 값
`--filename` | 대상 (파일 또는 장치) | 장치 전체
`--rw` | `read` · `write` (순차), `randread` · `randwrite` (랜덤) | 실험마다 다름
`--bs` | 한 번에 읽고 쓰는 크기 | 4k (랜덤), 1M (순차)
`--iodepth` | 동시에 걸어 두는 요청 수 (queue depth, QD) | 1 (지연 측정), 32 (최대 IOPS)
`--direct=1` | 페이지 캐시를 건너뛴다 | 항상
`--ioengine` | 요청을 넣는 방법 | `libaio`
`--size` · `--io_size` | 다룰 범위 · 총 입출력 양 | 장치의 몇 % · 용량의 2배
`--runtime` · `--time_based` | 시간으로 정하기 | 60초 (읽기 측정)
`--write_iops_log` 등 + `--log_avg_msec=1000` | 1초마다 기록 | 그래프용
```

이 컴퓨터의 NVMe 에서, 1 GiB 파일을 4 KiB 랜덤으로 5초 동안 읽은 실제 출력 (`ioengine` 은 시험용 빌드라 `io_uring`) :

```
$ fio --name=demo --filename=demo.img --size=1G --direct=1 --ioengine=io_uring \
      --rw=randread --bs=4k --iodepth=32 --runtime=5 --time_based
demo: (groupid=0, jobs=1): err= 0: pid=76591: Sat Oct 17 14:46:05 2026
  read: IOPS=479k, BW=1873MiB/s (1963MB/s)(9365MiB/5001msec)
    clat (usec): min=19, max=1986, avg=65.21, stdev=18.20
    clat percentiles (usec):
     |  1.00th=[   48],  5.00th=[   50], 10.00th=[   52], 20.00th=[   54],
     | 50.00th=[   60], 90.00th=[   88], 99.00th=[  129], 99.99th=[  269]
…
Disk stats (read/write):
  nvme0n1: ios=2390881/67, …, util=76.40%
```

- `IOPS=479k` : 1초에 4 KiB 읽기 47만 9천 번. `BW` = 대역폭 (IOPS × 4 KiB).
- `clat` : 요청 하나가 끝나기까지의 시간. **평균보다 percentile** 이 중요하다 : `99.00th=[129]` = 100번 중 99번은 129 µs 안에 끝났다.
- 같은 SSD 라도 QD1 과 QD32, 순차와 랜덤의 숫자가 몇 배씩 다르다. 그래서 숫자를 말할 때는 항상 조건을 같이 말한다.

## 8. 돌아가는 동안 지켜보기

### `/proc/diskstats` 와 `iostat`

커널은 디스크마다 '몇 번 읽었나, 얼마나 걸렸나' 를 센다. 원본은 `/proc/diskstats`, 보기 좋게 바꿔 주는 것이 `iostat` (sysstat 패키지).

```
$ grep " sda " /proc/diskstats
   8       0 sda 1179 0 58267 4053 4 0 4 0 0 1952 4053 0 0 0 0 0 0
```

```table
위치 | 값 | 뜻
4번째 | 1179 | 끝난 읽기 요청 수
6번째 | 58267 | 읽은 섹터 수 (× 512 B = 29.8 MB)
7번째 | 4053 | 읽기에 쓴 시간의 합 (ms, 요청마다 더함)
8번째 | 4 | 끝난 쓰기 요청 수
13번째 | 1952 | 디스크가 바빴던 시간 (ms)
```

숫자는 부팅한 뒤부터 센다. 읽은 양 ÷ 바빴던 시간이 대략의 읽기 속도다 : 위의 경우 29.8 MB ÷ 1.95 s ≈ 15 MB/s (작은 읽기가 대부분이라 낮다). [실험 1](/old-ssd-experiments/1-old-data/) 의 '이미 보이는 단서' 가 이 계산이다.

```
$ iostat -x 1 sda        # 1초마다 : r/s, rMB/s, r_await (읽기 하나의 평균 대기 ms), %util
```

`r_await` 가 수십–수백 ms 로 올라가면 드라이브가 읽기 하나에 오래 걸리고 있다는 뜻이다.

## 9. 위험한 명령 {#danger}

<div class="warn" markdown="1">
아래 명령은 **확인 없이 바로** 디스크를 지운다. 장치 이름을 한 글자만 틀려도 다른 디스크가 사라진다.

```table
명령 | 하는 일
`dd of=/dev/sdX …` | 장치에 바로 쓴다 (`of` = output file). `if` 와 `of` 를 바꿔 쓰면 원본이 지워진다
`blkdiscard /dev/sdX` | 장치 전체 TRIM : 즉시 전부 사라진다
`mkfs.* /dev/sdX1` | 새 파일 시스템 = 그 파티션의 기존 파일 목록이 사라진다
`wipefs -a /dev/sdX` | 파티션 표 · 파일 시스템 표시를 지운다
`fio --rw=write --filename=/dev/sdX` | 장치에 직접 쓴다 (파일 이름이 아니라 장치면)
`hdparm --security-erase` | 드라이브 자체의 전체 지우기. 중간에 끊기면 잠긴 상태가 될 수 있다
```

**매번 하는 확인** :
1. `lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,MOUNTPOINTS` 로 이름 · 모델 · **시리얼** 을 확인한다
2. 장치 이름 대신 `/dev/disk/by-id/…_시리얼` 을 쓴다
3. 그 장치의 파티션이 마운트되어 있지 않은지 본다 (`MOUNTPOINTS` 가 비어 있어야 한다)
4. `/` 가 있는 디스크 (`findmnt -no SOURCE /`) 가 아닌지 본다
5. 실험에서는 이 확인을 대신 해 주는 `lab.sh` 를 쓴다
</div>

## 10. 요약표

```table
하고 싶은 일 | 명령 | sudo
디스크 목록 | `lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,ROTA` | 아니오
바뀌지 않는 이름 | `ls -l /dev/disk/by-id/` | 아니오
무엇이 어디에 마운트 | `findmnt`, `df -hT` | 아니오
떼기 · 읽기 전용으로 붙이기 | `umount`, `mount -o ro` | 예
연결 경로 · 설정 | `readlink -f /sys/block/sdX`, `cat /sys/block/sdX/queue/…` | 아니오
부팅 · 연결 로그 | `journalctl -k` | 아니오 (Ubuntu 는 `dmesg` 에 sudo)
SMART | `smartctl -a`, NVMe 는 `nvme smart-log` | 예
ATA 기능 · TRIM 지원 | `hdparm -I` | 예
TRIM 가능? | `lsblk -d -o NAME,DISC-MAX` | 아니오
빈 공간 TRIM | `fstrim -v /` | 예
전체 TRIM (위험) | `blkdiscard` | 예
빠른 읽기 확인 | `hdparm -t` | 예
제대로 재기 | `fio …` | 장치면 예
지켜보기 | `iostat -x 1`, `/proc/diskstats` | 아니오
```

@@NAV@@
