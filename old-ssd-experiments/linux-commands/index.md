---
layout: default
title: SSD 를 다루는 Linux 명령
permalink: /old-ssd-experiments/linux-commands/
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

<svg viewBox="0 0 760 470" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="디스크 층과 명령"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">디스크가 보이는 층과, 각 층을 보는 명령</text><rect x="20" y="40" width="400" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="220.0" y="61.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">응용 프로그램</text><text x="220.0" y="77.0" font-size="11.5" fill="#4d5656" text-anchor="middle">cp, 브라우저, fio …</text><rect x="450" y="46" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="69.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ps, iotop</text><line x1="420" y1="65" x2="448" y2="65" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="100" width="400" height="50" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="220.0" y="121.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">파일 시스템</text><text x="220.0" y="137.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ext4, NTFS, vfat : 파일 이름 → 위치</text><rect x="450" y="106" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="129.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">df, findmnt, mount</text><line x1="420" y1="125" x2="448" y2="125" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="160" width="400" height="50" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="220.0" y="181.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">페이지 캐시 (RAM)</text><text x="220.0" y="197.0" font-size="11.5" fill="#4d5656" text-anchor="middle">읽은 것 · 쓸 것을 잠시 담아 둔다</text><rect x="450" y="166" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="189.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">free, dd oflag=direct</text><line x1="420" y1="185" x2="448" y2="185" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="220" width="400" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="220.0" y="241.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">블록 장치</text><text x="220.0" y="257.0" font-size="11.5" fill="#4d5656" text-anchor="middle">/dev/sda, /dev/sda3 : 512 B 섹터의 줄</text><rect x="450" y="226" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="249.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">lsblk, blockdev, /dev/disk/by-id</text><line x1="420" y1="245" x2="448" y2="245" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="280" width="400" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="220.0" y="301.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">드라이버 · 연결</text><text x="220.0" y="317.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA (ahci) · NVMe</text><rect x="450" y="286" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="309.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">/sys/block, journalctl -k</text><line x1="420" y1="305" x2="448" y2="305" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="340" width="400" height="50" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="220.0" y="361.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">SSD 컨트롤러 (FTL)</text><text x="220.0" y="377.0" font-size="11.5" fill="#4d5656" text-anchor="middle">LBA → NAND 위치, GC, 마모 평준화</text><rect x="450" y="346" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="369.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">smartctl, hdparm -I, nvme</text><line x1="420" y1="365" x2="448" y2="365" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="400" width="400" height="50" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="220.0" y="421.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND 플래시</text><text x="220.0" y="437.0" font-size="11.5" fill="#4d5656" text-anchor="middle">실제로 데이터가 사는 곳</text><rect x="450" y="406" width="290" height="38" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="595.0" y="429.0" font-size="11.5" fill="#4d5656" text-anchor="middle">(직접은 못 본다 : 실험으로 추측)</text><line x1="420" y1="425" x2="448" y2="425" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/></svg>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>열</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>NAME</code></td><td>장치 이름. 들여쓴 줄은 그 디스크의 파티션</td></tr>
<tr><td><code>SIZE</code></td><td>크기. <strong>GiB</strong> (2³⁰ 바이트) 단위라서 120 GB 디스크가 111.8G 로 보인다</td></tr>
<tr><td><code>RO</code></td><td>1 이면 읽기 전용</td></tr>
<tr><td><code>TYPE</code></td><td><code>disk</code> = 디스크 전체, <code>part</code> = 파티션</td></tr>
<tr><td><code>MOUNTPOINTS</code></td><td>파일 시스템이 붙은 폴더. 비어 있으면 마운트 안 됨</td></tr>
</tbody></table></div>

이름 읽는 법 :

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="장치 이름"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">장치 이름 읽는 법</text><rect x="20" y="50" width="180" height="60" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="110.0" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">/dev/sda</text><text x="110.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">디스크 하나</text><rect x="260" y="30" width="230" height="38" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="375.0" y="53.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sda1   100 MB vfat</text><text x="505.0" y="54.0" font-size="12" fill="#4d5656" text-anchor="start">EFI 부트</text><path d="M200,80 C230,80 230,49 258,49" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="260" y="75" width="230" height="38" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="375.0" y="98.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sda2   16 MB</text><text x="505.0" y="99.0" font-size="12" fill="#4d5656" text-anchor="start">MSR (예약)</text><path d="M200,80 C230,80 230,94 258,94" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="260" y="120" width="230" height="38" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="375.0" y="143.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sda3   111 GB ntfs</text><text x="505.0" y="144.0" font-size="12" fill="#4d5656" text-anchor="start">Windows C:</text><path d="M200,80 C230,80 230,139 258,139" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="260" y="165" width="230" height="38" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="375.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">sda4   532 MB ntfs</text><text x="505.0" y="189.0" font-size="12" fill="#4d5656" text-anchor="start">복구</text><path d="M200,80 C230,80 230,184 258,184" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="225" width="180" height="55" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="110.0" y="248.5" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">/dev/nvme0n1</text><text x="110.0" y="264.5" font-size="11.5" fill="#4d5656" text-anchor="middle">NVMe 디스크</text><rect x="260" y="225" width="230" height="55" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="375.0" y="248.5" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">nvme0n1p1, nvme0n1p2</text><text x="375.0" y="264.5" font-size="11.5" fill="#4d5656" text-anchor="middle">(파티션 앞에 p 가 붙는다)</text><line x1="200" y1="252" x2="258" y2="252" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="625.0" y="232.0" font-size="11.5" fill="#4d5656" text-anchor="middle">sd = SCSI disk : SATA · USB 디스크 이름</text><text x="625.0" y="249.0" font-size="11.5" fill="#4d5656" text-anchor="middle">a, b, c … 는 찾은 순서로 붙어 바뀔 수 있다</text><text x="625.0" y="272.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="middle">→ 실험에서는 시리얼로 찾는다</text></svg>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>파일</th>
<th>값</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>rotational</code></td><td>0</td><td>SSD (회전하지 않음)</td></tr>
<tr><td><code>logical_block_size</code></td><td>512</td><td>호스트가 보는 섹터 크기 (실험 6)</td></tr>
<tr><td><code>discard_max_bytes</code></td><td>2147450880</td><td>TRIM 명령 하나로 약 2 GB 까지 보낼 수 있다. 0 이면 TRIM 을 못 보낸다</td></tr>
<tr><td><code>max_sectors_kb</code></td><td>1280</td><td>커널이 요청 하나를 이 크기 (KiB) 보다 크게 만들지 않는다</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>줄</th>
<th>뜻</th>
<th>어느 실험</th>
</tr></thead><tbody>
<tr><td><code>SATA link up 6.0 Gbps</code></td><td>SATA 3 로 붙었다 : 상한 약 550 MB/s</td><td>5</td></tr>
<tr><td><code>applying quirks: noncqtrim zeroaftertrim …</code></td><td>커널이 이 모델에 맞춰 바꾸는 동작 : TRIM 은 NCQ 없이 보내고 (<code>noncqtrim</code>), TRIM 한 곳은 0 으로 읽힌다고 믿는다 (<code>zeroaftertrim</code>)</td><td>4</td></tr>
<tr><td><code>NCQ (depth 32)</code></td><td>명령을 32개까지 한꺼번에 받는다</td><td>5</td></tr>
<tr><td><code>234441648 512-byte logical blocks</code></td><td>정확한 용량. 234,441,648 × 512 = 120,034,123,776 바이트</td><td>0</td></tr>
<tr><td><code>Write cache: enabled … doesn't support DPO or FUA</code></td><td>쓰기 캐시가 켜져 있고, '이 쓰기만 바로 NAND 에' (FUA) 는 지원하지 않는다 : 데이터를 지키려면 FLUSH 뿐</td><td>7, 17</td></tr>
<tr><td><code>supports TCG Opal</code></td><td>자체 암호화 드라이브 (SED) 의 표준을 지원한다</td><td>14</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>열</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>ID#</code> · <code>ATTRIBUTE_NAME</code></td><td>속성 번호와 이름. 번호의 뜻은 제조사마다 조금씩 다르다</td></tr>
<tr><td><code>VALUE</code> · <code>WORST</code></td><td><strong>정규화 값</strong> (보통 100 또는 200 에서 시작해 내려간다), 지금까지의 최저</td></tr>
<tr><td><code>THRESH</code></td><td><code>VALUE</code> 가 이 아래로 내려가면 '실패'</td></tr>
<tr><td><code>RAW_VALUE</code></td><td><strong>진짜 숫자</strong> (시간, 횟수, 섹터 수). 실험에서 주로 보는 열</td></tr>
</tbody></table></div>

Samsung SATA SSD 에서 흔히 보이는 속성 중 실험에 쓰는 것 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>ID</th>
<th>이름</th>
<th>실험에서의 의미</th>
</tr></thead><tbody>
<tr><td>9</td><td>Power_On_Hours</td><td>전원이 켜져 있던 시간</td></tr>
<tr><td>177</td><td>Wear_Leveling_Count</td><td>raw = 블록들의 <strong>평균 지움 횟수</strong> (P/E). 실험 12, 18</td></tr>
<tr><td>179</td><td>Used_Rsvd_Blk_Cnt_Tot</td><td>써 버린 예비 블록 수. 수명 끝에 늘어난다</td></tr>
<tr><td>181 · 182</td><td>Program_Fail · Erase_Fail</td><td>쓰기 · 지우기 실패 횟수</td></tr>
<tr><td>187</td><td>Uncorrectable_Error_Cnt</td><td>ECC 로도 못 고친 오류</td></tr>
<tr><td>195</td><td>ECC_Error_Rate</td><td>ECC 가 고친 오류 (늘어날수록 셀 상태가 나쁘다)</td></tr>
<tr><td>241</td><td>Total_LBAs_Written</td><td>호스트가 쓴 양 (512 바이트 단위). 실험 12</td></tr>
</tbody></table></div>

NVMe 드라이브라면 `sudo nvme smart-log /dev/nvme0` (nvme-cli) 가 같은 일을 한다. NVMe 는 속성 번호 대신 정해진 항목 (`data_units_written`, `percentage_used` …) 을 보여 준다.

### `hdparm -I` : ATA 기능 목록

```
$ sudo hdparm -I /dev/sda | grep -iE "model|firmware|trim"
```

`Data Set Management TRIM supported` 같은 줄이 나온다. **`Deterministic read ZEROs after TRIM`** 이 있으면 TRIM 한 LBA 를 읽을 때 반드시 0 이 나온다는 약속이다 (실험 4).

## 6. TRIM : SSD 에게 '이제 안 쓴다' 고 알리기

<svg viewBox="0 0 760 260" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="TRIM 흐름"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">파일을 지우면 SSD 는 언제 알게 되나 : TRIM</text><rect x="15" y="50" width="170" height="62" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="100.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">rm file</text><text x="100.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">파일 시스템 표에서만 지움</text><rect x="203" y="50" width="170" height="62" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="288.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">fstrim / discard</text><text x="288.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">&quot;이 LBA 들은 이제 안 쓴다&quot;</text><line x1="185" y1="81" x2="201" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="391" y="50" width="170" height="62" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="476.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 명령</text><text x="476.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA 의 DSM 명령</text><line x1="373" y1="81" x2="389" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="579" y="50" width="170" height="62" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="664.0" y="77.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">FTL</text><text x="664.0" y="93.0" font-size="11.5" fill="#4d5656" text-anchor="middle">LBA → NAND 연결을 끊는다</text><line x1="561" y1="81" x2="577" y2="81" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="150" width="355" height="85" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="192.5" y="172.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 이 없으면</text><text x="192.5" y="188.5" font-size="11.5" fill="#4d5656" text-anchor="middle">SSD 는 지운 데이터를 아직 &quot;유효&quot; 로 여긴다</text><text x="192.5" y="204.5" font-size="11.5" fill="#4d5656" text-anchor="middle">→ GC 가 쓸모없는 데이터까지 복사한다</text><text x="192.5" y="220.5" font-size="11.5" fill="#4d5656" text-anchor="middle">→ 느려지고, 더 닳는다</text><rect x="390" y="150" width="355" height="85" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="567.5" y="172.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 이 있으면</text><text x="567.5" y="188.5" font-size="11.5" fill="#4d5656" text-anchor="middle">그 페이지는 &quot;무효&quot; : GC 가 건너뛴다</text><text x="567.5" y="204.5" font-size="11.5" fill="#4d5656" text-anchor="middle">그 LBA 를 읽으면 NAND 를 안 읽고</text><text x="567.5" y="220.5" font-size="11.5" fill="#4d5656" text-anchor="middle">0 을 돌려줄 수 있다 (실험 4)</text></svg>

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

<svg viewBox="0 0 760 250" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="페이지 캐시"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 dd 인데 숫자가 다른 이유 : 페이지 캐시</text><rect x="20" y="45" width="150" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="95.0" y="74.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">dd (보통)</text><rect x="250" y="45" width="200" height="50" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="350.0" y="66.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">페이지 캐시 (RAM)</text><text x="350.0" y="82.0" font-size="11.5" fill="#4d5656" text-anchor="middle">&quot;다 썼다&quot; 고 바로 대답</text><rect x="540" y="45" width="200" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="640.0" y="66.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">디스크</text><text x="640.0" y="82.0" font-size="11.5" fill="#4d5656" text-anchor="middle">나중에 천천히 쓴다</text><line x1="170" y1="70" x2="248" y2="70" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="209.0" y="64.0" font-size="11.5" fill="#566573" text-anchor="middle">4.6 GB/s ?!</text><line x1="450" y1="70" x2="538" y2="70" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="494.0" y="64.0" font-size="11.5" fill="#566573" text-anchor="middle">나중에</text><rect x="20" y="150" width="150" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="95.0" y="179.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">dd oflag=direct</text><rect x="540" y="150" width="200" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="640.0" y="171.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">디스크</text><text x="640.0" y="187.0" font-size="11.5" fill="#4d5656" text-anchor="middle">다 쓴 뒤에 대답</text><line x1="170" y1="175" x2="538" y2="175" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="354.0" y="169.0" font-size="11.5" fill="#566573" text-anchor="middle">2.7 GB/s : 디스크의 진짜 속도 (캐시를 건너뜀)</text><text x="380.0" y="235.0" font-size="12" font-weight="700" fill="#1f6f5c" text-anchor="middle">실험의 모든 측정은 direct I/O (fio --direct=1, O_DIRECT) 로 한다</text></svg>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>뜻</th>
<th>실험에서 쓰는 값</th>
</tr></thead><tbody>
<tr><td><code>--filename</code></td><td>대상 (파일 또는 장치)</td><td>장치 전체</td></tr>
<tr><td><code>--rw</code></td><td><code>read</code> · <code>write</code> (순차), <code>randread</code> · <code>randwrite</code> (랜덤)</td><td>실험마다 다름</td></tr>
<tr><td><code>--bs</code></td><td>한 번에 읽고 쓰는 크기</td><td>4k (랜덤), 1M (순차)</td></tr>
<tr><td><code>--iodepth</code></td><td>동시에 걸어 두는 요청 수 (queue depth, QD)</td><td>1 (지연 측정), 32 (최대 IOPS)</td></tr>
<tr><td><code>--direct=1</code></td><td>페이지 캐시를 건너뛴다</td><td>항상</td></tr>
<tr><td><code>--ioengine</code></td><td>요청을 넣는 방법</td><td><code>libaio</code></td></tr>
<tr><td><code>--size</code> · <code>--io_size</code></td><td>다룰 범위 · 총 입출력 양</td><td>장치의 몇 % · 용량의 2배</td></tr>
<tr><td><code>--runtime</code> · <code>--time_based</code></td><td>시간으로 정하기</td><td>60초 (읽기 측정)</td></tr>
<tr><td><code>--write_iops_log</code> 등 + <code>--log_avg_msec=1000</code></td><td>1초마다 기록</td><td>그래프용</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>위치</th>
<th>값</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td>4번째</td><td>1179</td><td>끝난 읽기 요청 수</td></tr>
<tr><td>6번째</td><td>58267</td><td>읽은 섹터 수 (× 512 B = 29.8 MB)</td></tr>
<tr><td>7번째</td><td>4053</td><td>읽기에 쓴 시간의 합 (ms, 요청마다 더함)</td></tr>
<tr><td>8번째</td><td>4</td><td>끝난 쓰기 요청 수</td></tr>
<tr><td>13번째</td><td>1952</td><td>디스크가 바빴던 시간 (ms)</td></tr>
</tbody></table></div>

숫자는 부팅한 뒤부터 센다. 읽은 양 ÷ 바빴던 시간이 대략의 읽기 속도다 : 위의 경우 29.8 MB ÷ 1.95 s ≈ 15 MB/s (작은 읽기가 대부분이라 낮다). [실험 1](/old-ssd-experiments/1-old-data/) 의 '이미 보이는 단서' 가 이 계산이다.

```
$ iostat -x 1 sda        # 1초마다 : r/s, rMB/s, r_await (읽기 하나의 평균 대기 ms), %util
```

`r_await` 가 수십–수백 ms 로 올라가면 드라이브가 읽기 하나에 오래 걸리고 있다는 뜻이다.

## 9. 위험한 명령 {#danger}

<div class="warn" markdown="1">
아래 명령은 **확인 없이 바로** 디스크를 지운다. 장치 이름을 한 글자만 틀려도 다른 디스크가 사라진다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>명령</th>
<th>하는 일</th>
</tr></thead><tbody>
<tr><td><code>dd of=/dev/sdX …</code></td><td>장치에 바로 쓴다 (<code>of</code> = output file). <code>if</code> 와 <code>of</code> 를 바꿔 쓰면 원본이 지워진다</td></tr>
<tr><td><code>blkdiscard /dev/sdX</code></td><td>장치 전체 TRIM : 즉시 전부 사라진다</td></tr>
<tr><td><code>mkfs.* /dev/sdX1</code></td><td>새 파일 시스템 = 그 파티션의 기존 파일 목록이 사라진다</td></tr>
<tr><td><code>wipefs -a /dev/sdX</code></td><td>파티션 표 · 파일 시스템 표시를 지운다</td></tr>
<tr><td><code>fio --rw=write --filename=/dev/sdX</code></td><td>장치에 직접 쓴다 (파일 이름이 아니라 장치면)</td></tr>
<tr><td><code>hdparm --security-erase</code></td><td>드라이브 자체의 전체 지우기. 중간에 끊기면 잠긴 상태가 될 수 있다</td></tr>
</tbody></table></div>

**매번 하는 확인** :
1. `lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,MOUNTPOINTS` 로 이름 · 모델 · **시리얼** 을 확인한다
2. 장치 이름 대신 `/dev/disk/by-id/…_시리얼` 을 쓴다
3. 그 장치의 파티션이 마운트되어 있지 않은지 본다 (`MOUNTPOINTS` 가 비어 있어야 한다)
4. `/` 가 있는 디스크 (`findmnt -no SOURCE /`) 가 아닌지 본다
5. 실험에서는 이 확인을 대신 해 주는 `lab.sh` 를 쓴다
</div>

## 10. 요약표

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>하고 싶은 일</th>
<th>명령</th>
<th>sudo</th>
</tr></thead><tbody>
<tr><td>디스크 목록</td><td><code>lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,ROTA</code></td><td>아니오</td></tr>
<tr><td>바뀌지 않는 이름</td><td><code>ls -l /dev/disk/by-id/</code></td><td>아니오</td></tr>
<tr><td>무엇이 어디에 마운트</td><td><code>findmnt</code>, <code>df -hT</code></td><td>아니오</td></tr>
<tr><td>떼기 · 읽기 전용으로 붙이기</td><td><code>umount</code>, <code>mount -o ro</code></td><td>예</td></tr>
<tr><td>연결 경로 · 설정</td><td><code>readlink -f /sys/block/sdX</code>, <code>cat /sys/block/sdX/queue/…</code></td><td>아니오</td></tr>
<tr><td>부팅 · 연결 로그</td><td><code>journalctl -k</code></td><td>아니오 (Ubuntu 는 <code>dmesg</code> 에 sudo)</td></tr>
<tr><td>SMART</td><td><code>smartctl -a</code>, NVMe 는 <code>nvme smart-log</code></td><td>예</td></tr>
<tr><td>ATA 기능 · TRIM 지원</td><td><code>hdparm -I</code></td><td>예</td></tr>
<tr><td>TRIM 가능?</td><td><code>lsblk -d -o NAME,DISC-MAX</code></td><td>아니오</td></tr>
<tr><td>빈 공간 TRIM</td><td><code>fstrim -v /</code></td><td>예</td></tr>
<tr><td>전체 TRIM (위험)</td><td><code>blkdiscard</code></td><td>예</td></tr>
<tr><td>빠른 읽기 확인</td><td><code>hdparm -t</code></td><td>예</td></tr>
<tr><td>제대로 재기</td><td><code>fio …</code></td><td>장치면 예</td></tr>
<tr><td>지켜보기</td><td><code>iostat -x 1</code>, <code>/proc/diskstats</code></td><td>아니오</td></tr>
</tbody></table></div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/ssd-tutorial/' | relative_url }}">← SSD tutorial</a><a href="{{ '/old-ssd-experiments/fio/' | relative_url }}">fio 사용법 →</a></div>
