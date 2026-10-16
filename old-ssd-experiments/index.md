---
layout: default
title: 헌 SSD 로 하는 실험
permalink: /old-ssd-experiments/
---
<style>
.warn { background:#fdf2f0; border-left:4px solid #c0392b; padding:10px 14px; margin:1.2rem 0; }
.todo { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; }
</style>

# 헌 SSD 로 하는 실험

**믿을 수 없게 된 헌 SSD 를 버리는 대신, SSD 안에서 일어나는 일 (FTL) 을 직접 눈으로 보는 실험에 쓴다.** (2026.10.16 시작)

헌 드라이브는 이런 실험에 오히려 딱 맞다. 제일 배울 것이 많은 실험은 **데이터를 지우고 드라이브를 닳게 하는** 것이라, 아끼는 드라이브로는 할 수 없기 때문이다.
실험은 [FTL Visual Simulator](/ftl-visual-simulator/) 에서 모델로 만든 것 (GC, WAF, OP, SLC 캐시, 매핑 없는 읽기) 을 **실제 드라이브에서 확인** 하는 쪽으로 골랐다.

<div class="todo" markdown="1">
**다음에 할 일 (2026.10.17~)**
1. 드라이브 모델과 연결 방식 (SATA / NVMe) 확인 : `sudo smartctl -a /dev/sdX` 결과를 Claude 에게 보여 주기
2. 그 드라이브가 SMART 로 어떤 카운터를 보여 주는지 확인 (특히 NAND 쓰기량 : 실험 3 이 가능한지)
3. 실험 1–2 를 돌리는 스크립트와, 결과를 시뮬레이터와 나란히 보는 그래프 만들기
</div>

<div style="margin-top: 60px;"></div>

## 실험 목록 (추천 순서)

### 1. Write cliff : GC 가 눈에 보이는 순간 ⭐ 여기서 시작

- 드라이브 전체를 지운 뒤 (`blkdiscard`), 4 KB 랜덤 쓰기를 **용량의 약 2배** 만큼 계속하면서 1초마다 IOPS 를 기록한다
- 세 구간이 보인다 : 처음엔 빠르고 (빈 블록이 넉넉함) → 갑자기 떨어지고 (GC 시작) → 낮은 수준에서 안정 (steady state)
- 시뮬레이터의 **빈 블록 차트** 의 실제 드라이브 판이다

### 2. Over-provisioning : 실제 하드웨어의 WAF–OP 곡선

- 실험 1 을 다시 하되, 드라이브의 **80% 만** 쓴다 (나머지 20% 는 TRIM 된 채로 둔다)
- FTL 이 쓸 수 있는 여유 블록이 늘어나니 steady state IOPS 가 눈에 띄게 올라가야 한다
- 시뮬레이터의 OP 20% 기본값, WAF–OP 곡선과 숫자를 비교한다

### 3. 드라이브가 직접 세는 WAF

- 많은 드라이브가 SMART 에 **호스트가 쓴 양** 과 **NAND 에 실제로 쓴 양** 을 따로 보여 준다 (예 : Crucial/Micron 의 246/247 번, Samsung · Intel 에도 비슷한 항목)
- 실험 앞뒤로 읽어서 **WAF = NAND 쓰기 ÷ 호스트 쓰기** 를 구한다
- 순차 쓰기는 1 에 가깝고, 랜덤 쓰기는 훨씬 커야 한다. 드라이브가 스스로 잰 write amplification 이다
- 드라이브가 NAND 쓰기량을 보여 주지 않으면 이 실험은 할 수 없다 (다음 할 일 2번)

### 4. SLC 캐시 크기

- 큰 파일 하나를 순차로 쓰면서 속도를 기록한다
- 몇 GB 쯤에서 속도가 뚝 떨어진다. 빠른 SLC 캐시가 다 차고, TLC/QLC 에 바로 쓰기 시작한 지점이다

### 5. TRIM 과 매핑 없는 읽기

- TRIM 된 LBA 를 읽으면 0 이 **아주 빨리** 돌아온다. FTL 에 매핑이 없어서 NAND 를 아예 건드리지 않기 때문이다
- 시뮬레이터의 `Unmapped_Reads_Return_Zeros` 읽기 지연 차트와 같은 현상이다
- TRIM 을 하고 꽉 채운 경우와 TRIM 없이 꽉 채운 경우의 steady state 속도도 비교한다

### 6. Retention : "믿을 수 없음" 이 쓸모 있어지는 실험

- 체크섬과 함께 정해진 패턴을 써 두고, 드라이브를 **2–4주 동안 전원 없이** 둔 뒤 다시 읽는다
- 영역별 읽기 지연을 잰다. 닳은 셀은 **read retry** 가 필요해서, 오류가 나기 전에 지연부터 늘어난다
- 약한 드라이브라면 실제 읽기 오류도 볼 수 있다

### 7. (선택) 끝까지 쓰기

- 쉬지 않고 쓰면서 한 시간마다 SMART 를 기록한다. 드라이브가 죽거나 읽기 전용으로 바뀔 때까지
- 여분 블록이 줄어드는 모습과, 수명이 다할 때 컨트롤러가 어떻게 행동하는지 본다

### 8. 마지막 : 열어 보기

- 케이스를 열고 컨트롤러, NAND 패키지, DRAM (DRAM 없는 드라이브도 있다), 커패시터를 찾는다. 부품 번호를 검색한다
- 시뮬레이터의 "채널 × 칩" 을 실제 부품과 연결해 본다

<div style="margin-top: 60px;"></div>

## 도구 (모두 Linux)

| 도구 | 쓰는 곳 |
|---|---|
| `smartctl` (smartmontools) | SMART 읽기 (실험 3, 6, 7) |
| `nvme-cli` | NVMe 드라이브라면 `nvme smart-log` |
| `fio` | 쓰기 · 읽기 부하와 1초 단위 로그 (실험 1, 2, 4, 5, 6) |
| `blkdiscard` | 드라이브 전체 TRIM (실험 1, 2, 5 시작 전) |
| Python (matplotlib) | fio 로그를 그래프로 |

명령어의 대략적인 모습 (드라이브를 확인한 뒤 실제 값으로 다듬는다. `/dev/sdX` 는 반드시 직접 확인할 것) :

```sh
# 0. 어떤 드라이브인지, 무엇을 보여 주는지
lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN
sudo smartctl -a /dev/sdX

# 1. write cliff : 전부 지우고, 4 KB 랜덤 쓰기를 용량의 2배, 1초마다 IOPS 기록
sudo blkdiscard /dev/sdX
sudo fio --name=cliff --filename=/dev/sdX --direct=1 --ioengine=libaio \
         --rw=randwrite --bs=4k --iodepth=32 --size=100% --loops=2 \
         --norandommap --randrepeat=0 \
         --write_iops_log=cliff --log_avg_msec=1000

# 2. OP 20% : 같은 실험을 앞쪽 80% 에만
sudo blkdiscard /dev/sdX
sudo fio --name=op20 ... --size=80% ...

# 4. SLC 캐시 : 1 MB 순차 쓰기, 1초마다 대역폭 기록
sudo blkdiscard /dev/sdX
sudo fio --name=slc --filename=/dev/sdX --direct=1 --ioengine=libaio \
         --rw=write --bs=1M --iodepth=8 --size=100% \
         --write_bw_log=slc --log_avg_msec=1000

# 6. retention : 체크섬과 함께 쓰고, 몇 주 뒤 확인만
sudo fio --name=ret --filename=/dev/sdX --direct=1 --rw=write --bs=1M \
         --size=100% --verify=crc32c --do_verify=0
#   ... 2–4주 전원 없이 보관 ...
sudo fio --name=ret --filename=/dev/sdX --direct=1 --rw=write --bs=1M \
         --size=100% --verify=crc32c --verify_only
```

<div style="margin-top: 60px;"></div>

## 안전

<div class="warn" markdown="1">
- 이 실험들은 **드라이브 전체를 지운다.** 지우는 명령 전에는 매번 `lsblk -o NAME,MODEL,SERIAL,SIZE` 로 장치 이름을 확인한다. `/dev/sdX` 를 잘못 쓰면 시스템 디스크가 지워진다
- 가능하면 시스템 디스크와 확실히 구분되게 연결한다
- USB–SATA 어댑터는 TRIM 이나 SMART 를 전달하지 못하는 것이 많다. 실험 3 과 5 에는 SATA / NVMe 직접 연결이 낫다
</div>
