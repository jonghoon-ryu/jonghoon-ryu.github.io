---
layout: default
title: 0. 준비
permalink: /old-ssd-experiments/0-setup/
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

# 0. 준비 : 드라이브, 도구, 기준값

<div class="glance">
<b>목표</b><span>실험할 드라이브를 확실히 알아보고, 도구를 깔고, 실험 전 SMART 값 (기준값) 을 남긴다</span>
<b>지우나?</b><span>아니오. 읽기만 한다</span>
<b>연결</b><span>SATA (2026.10.17 에 옮김 : 6단계)</span>
<b>시간</b><span>30분</span>
<b>명령</b><span><code>sudo ./lab.sh check</code></span>
</div>

## 드라이브

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>항목</th>
<th>값</th>
<th>출처</th>
</tr></thead><tbody>
<tr><td>모델</td><td>Samsung SSD 840 EVO 120GB</td><td><code>lsblk</code></td></tr>
<tr><td>시리얼</td><td><code>S1D6NSAFB40389K</code></td><td><code>lsblk</code>, <code>/dev/disk/by-id</code></td></tr>
<tr><td>펌웨어</td><td><code>EXT0CB6Q</code></td><td><code>lsblk -o REV</code> (같은 컴퓨터의 840 EVO 500GB 는 <code>EXT0BB6Q</code>)</td></tr>
<tr><td>용량</td><td>120,034,123,776 B (234,441,648 섹터)</td><td>커널 로그</td></tr>
<tr><td>NAND</td><td>TLC, 128 GiB 로 알려짐</td><td>리뷰 · 자료 (확인 필요)</td></tr>
<tr><td>SLC 버퍼 (TurboWrite)</td><td>120GB 모델은 약 3 GB 로 알려짐</td><td>Samsung 자료 (확인 필요)</td></tr>
<tr><td>컨트롤러</td><td>Samsung MEX (ARM 코어 3개로 알려짐)</td><td>리뷰 (실험 9 에서 확인)</td></tr>
<tr><td>지금 내용</td><td>옛 Windows 디스크 : EFI · MSR · NTFS 111 GB (91% 참) · 복구</td><td><code>lsblk -f</code>, <code>df</code></td></tr>
<tr><td>파일 날짜</td><td>2018 – 2024.12 (hiberfil.sys 마지막 수정 2024.12.08)</td><td><code>ls -la</code></td></tr>
<tr><td>지금 연결</td><td>메인보드 SATA <code>ata5</code> (<code>/dev/sda</code>), TRIM 됨 (<code>DISC-GRAN 512B</code>, <code>DISC-MAX 2G</code>). 처음에는 USB 3.0 어댑터 (ASMedia 19da:1125, <code>uas</code>) 로 <code>/dev/sdg</code> 였고 TRIM 이 안 됐다</td><td><code>lsblk -o NAME,TRAN,DISC-MAX</code>, <code>/sys/block/sda</code></td></tr>
</tbody></table></div>

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

<svg viewBox="0 0 760 210" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="안전 확인"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">lab.sh 가 지우기 전에 하는 확인</text><rect x="10" y="50" width="135" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="77.5" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">시리얼로 찾기</text><text x="77.5" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">S1D6NSAFB40389K</text><rect x="160" y="50" width="135" height="60" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="227.5" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">시스템 디스크?</text><text x="227.5" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">/ 가 있으면 중단</text><line x1="147" y1="80" x2="158" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="310" y="50" width="135" height="60" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="377.5" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">마운트됨?</text><text x="377.5" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">있으면 중단</text><line x1="297" y1="80" x2="308" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="460" y="50" width="135" height="60" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="527.5" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">TRIM 되나?</text><text x="527.5" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">USB 면 중단</text><line x1="447" y1="80" x2="458" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="610" y="50" width="135" height="60" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="677.5" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">시리얼 끝 5자리</text><text x="677.5" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">직접 입력</text><line x1="597" y1="80" x2="608" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="250" y="140" width="260" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="380.0" y="161.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">실행 → 결과 폴더</text><text x="380.0" y="177.0" font-size="11.5" fill="#4d5656" text-anchor="middle">~/Ryu/old_ssd_results/날짜-실험/</text><line x1="680" y1="110" x2="512" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/></svg>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>보는 것</th>
<th>왜</th>
</tr></thead><tbody>
<tr><td>펌웨어</td><td>읽기 저하 수정판인지 : 실험 1 의 해석이 달라진다</td></tr>
<tr><td>9 Power_On_Hours</td><td>얼마나 쓰였나</td></tr>
<tr><td>177 Wear_Leveling_Count</td><td>지금까지의 평균 P/E : 실험 8 의 남은 수명 계산</td></tr>
<tr><td>241 Total_LBAs_Written</td><td>지금까지 호스트가 쓴 양</td></tr>
<tr><td>5 · 179 · 181 · 182 · 183 · 187</td><td>'믿을 수 없게 됨' 이 실제로 무엇인지 : 재할당, 예비 블록, 실패, 고치지 못한 오류</td></tr>
<tr><td>195 ECC_Error_Rate</td><td>셀 상태</td></tr>
</tbody></table></div>

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

## 6단계 : SATA 로 옮기기 (2026.10.17 완료)

처음 계획은 실험 1 을 USB 로 한 뒤 `sdc` (WD 1TB HDD) 자리에 꽂는 것이었다. 실제로는 **실험 1 전에** 옮겼고, 자리도 달랐다 :
840 EVO 120GB 가 `ata5` 에 있던 **840 EVO 500GB 와 자리를 바꿨다**. 500GB 는 대신 USB 어댑터로 간다.

<svg viewBox="0 0 760 300" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="SATA 포트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">SATA 포트 4개가 모두 차 있다 : 실험 동안 840 EVO 500GB 와 자리를 바꿨다</text><rect x="20" y="45" width="170" height="230" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="105.0" y="124.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">메인보드</text><text x="105.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle">MAG B760M</text><text x="105.0" y="156.0" font-size="11.5" fill="#4d5656" text-anchor="middle">MORTAR II</text><text x="105.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="105.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Intel B760</text><text x="105.0" y="204.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA 컨트롤러</text><rect x="230" y="50" width="120" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="76.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA (ata5)</text><line x1="190" y1="72" x2="230" y2="72" stroke="#7d3c98" stroke-width="2"/><rect x="380" y="50" width="170" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="465.0" y="68.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">sda</text><text x="465.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle">840 EVO 120GB (실험용)</text><line x1="350" y1="72" x2="380" y2="72" stroke="#7f8c8d" stroke-width="2"/><rect x="230" y="107" width="120" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="133.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA (ata6)</text><line x1="190" y1="129" x2="230" y2="129" stroke="#7d3c98" stroke-width="2"/><rect x="380" y="107" width="170" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="465.0" y="125.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">sdb</text><text x="465.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="middle">750 EVO 500GB</text><line x1="350" y1="129" x2="380" y2="129" stroke="#7f8c8d" stroke-width="2"/><rect x="230" y="164" width="120" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="190.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA (ata7)</text><line x1="190" y1="186" x2="230" y2="186" stroke="#7d3c98" stroke-width="2"/><rect x="380" y="164" width="170" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="465.0" y="182.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">sdc</text><text x="465.0" y="198.0" font-size="11.5" fill="#4d5656" text-anchor="middle">WD 1TB HDD</text><line x1="350" y1="186" x2="380" y2="186" stroke="#7f8c8d" stroke-width="2"/><rect x="230" y="221" width="120" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="247.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA (ata8)</text><line x1="190" y1="243" x2="230" y2="243" stroke="#7d3c98" stroke-width="2"/><rect x="380" y="221" width="170" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="465.0" y="239.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">sdd</text><text x="465.0" y="255.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Seagate 2TB HDD</text><line x1="350" y1="243" x2="380" y2="243" stroke="#7f8c8d" stroke-width="2"/><rect x="590" y="120" width="155" height="60" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="667.5" y="138.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">sde</text><text x="667.5" y="154.0" font-size="11.5" fill="#4d5656" text-anchor="middle">840 EVO 500GB</text><text x="667.5" y="170.0" font-size="11.5" fill="#4d5656" text-anchor="middle">USB 어댑터로</text><path d="M552,72 C575,72 575,135 590,135" fill="none" stroke="#c0392b" stroke-width="2" marker-end="url(#ae)"/><text x="668.0" y="206.0" font-size="12" fill="#c0392b" text-anchor="middle">120GB 는 USB 의 sdg 였다</text><text x="668.0" y="223.0" font-size="12" fill="#c0392b" text-anchor="middle">끝나면 500GB 를 ata5 로</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>디스크</th>
<th>전</th>
<th>지금 (2026.10.17 16:44 부팅 뒤)</th>
</tr></thead><tbody>
<tr><td>840 EVO 120GB (실험용, <code>…40389K</code>)</td><td><code>sdg</code>, USB, TRIM 안 됨</td><td><strong><code>sda</code>, SATA <code>ata5</code>, TRIM 됨</strong></td></tr>
<tr><td>840 EVO 500GB (<code>…85299B</code>)</td><td><code>sda</code>, SATA <code>ata5</code></td><td><code>sde</code>, USB (<code>/etc/fstab</code> 에 <code>nofail</code> 이라 부팅에 문제 없음)</td></tr>
<tr><td>750 EVO · WD 1TB · Seagate 2TB</td><td><code>sdb</code> · <code>sdc</code> · <code>sdd</code> (<code>ata6</code>–<code>ata8</code>)</td><td>그대로</td></tr>
</tbody></table></div>

<div class="check" markdown="1">
**글자가 바뀌었다.** 전에 `sda` 는 500GB 였고, 지금 `sda` 는 실험용 120GB 다. 옛 메모의 `/dev/sdX` 를 그대로 쓰면 다른 디스크를 지운다.
`lab.sh` 는 장치를 이름이 아니라 **시리얼** 로 찾으므로 그대로 쓰면 된다.
</div>

**실험 1 에는 오히려 좋다.** 실험 1 (오래된 데이터) 과 실험 2 의 `scan fresh` (새 데이터) 를 같은 SATA 연결에서 재므로, 두 곡선의 차이는 '데이터의 나이' 뿐이다. USB 로 다시 옮겨 한 번 더 재는 단계는 필요 없어졌다.

확인 : `sudo ./lab.sh check` 를 SATA 에서 실행하면 SMART 와 `hdparm -I` (TRIM 지원 줄) 이 모두 나와야 한다 (USB 와 달리 `-d sat` 없이).

<div class="tip" markdown="1">
**실험이 다 끝나면** 500GB 를 `ata5` 로 되돌린다. 다른 방법 : PCIe SATA 카드 (ASM1166 · JMB585 칩) 를 쓰면 포트를 바꿀 필요가 없다.
</div>

## 결과

<div class="result" markdown="1">
아직 실행 전. `sudo ./lab.sh check` 결과가 나오면 여기에 SMART 표와 해석을 붙인다.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/linux-commands/' | relative_url }}">← SSD 를 다루는 Linux 명령</a><a href="{{ '/old-ssd-experiments/1-old-data/' | relative_url }}">1. 오래된 데이터 읽기 →</a></div>
