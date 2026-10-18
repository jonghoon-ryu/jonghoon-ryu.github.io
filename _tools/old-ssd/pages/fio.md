---
layout: default
title: fio 사용법
permalink: /old-ssd-experiments/fio/
---
@@STYLE@@

# fio 사용법 : 실험의 주 도구를 자세히

<div class="glance">
<b>목표</b><span>fio 로 원하는 I/O 를 정확히 만들고, 출력의 숫자 하나하나를 읽을 수 있게 된다</span>
<b>버전</b><span>fio-3.36 (Ubuntu 의 <code>apt install fio</code> 와 같은 버전)</span>
<b>출력</b><span>이 페이지의 출력은 모두 <b>실제 출력</b> 이다 : 2026.10.18, 이 컴퓨터의 시스템 디스크 (NVMe) 위의 1 GiB 파일 <code>~/fiotest/test.img</code>. 840 EVO 의 숫자가 아니다 (훨씬 느릴 것이다)</span>
<b>안전</b><span>여기서는 <b>파일</b> 에만 쓴다. <code>--filename=/dev/sdX</code> 에 쓰는 것은 그 디스크를 지운다 : 13절</span>
</div>

## 1. fio 란

fio (flexible I/O tester) 는 Linux 블록 계층의 관리자인 Jens Axboe 가 만든 **I/O 부하 생성기** 다.
'4 KiB 를 무작위 위치에서, 동시에 32개씩, 60초 동안 읽어라' 처럼 I/O 의 모양을 말로 적으면, fio 가 그대로 만들어 내고 속도 · 지연을 잰다.
`dd` 는 순차로 한 줄씩만 할 수 있지만 fio 는 모양 (순차 / 랜덤, 크기, 동시성, 섞기, 분포) 을 거의 다 바꿀 수 있다. SSD 연구 · 리뷰의 표준 도구다.

**한 줄로 보는 fio** : I/O 의 모양을 옵션으로 적으면, fio 가 그대로 만들어 내고 잰다.

```
fio --name=NAME --filename=TARGET --rw=PATTERN --bs=SIZE --iodepth=N --size=RANGE [--runtime=S --time_based] --direct=1
      누가        어디에           무엇을         얼마나 크게  동시에 몇 개     얼마나 많이 / 얼마나 오래        RAM 캐시를 건너뛰고
```

```table
옵션 | 묻는 것 | 예
`--name` | **누가** : job 의 이름. 출력 · JSON · 로그 파일 이름에 쓰인다 | `--name=slc`
`--filename` | **어디에** : 파일 또는 장치 | `--filename=test.img`, `/dev/sda`
`--rw` | **무엇을** : 읽기 / 쓰기, 순차 / 랜덤 | `read`, `write`, `randread`, `randwrite`
`--bs` | **얼마나 크게** : I/O 하나의 크기 | `4k`, `1M`
`--iodepth` | **동시에 몇 개** : 한꺼번에 걸어 둘 I/O 수 (큐 깊이) | `1`, `32`
`--size` | **얼마나 많이** : 다룰 범위 | `1G`, `100%`
`--runtime=S --time_based` | **얼마나 오래** : S 초 동안 (범위를 다 돌아도 다시 처음부터) | `--runtime=60 --time_based`
`--direct=1` | **RAM 캐시를 건너뛰고** : 페이지 캐시가 아니라 장치를 잰다 | 실험에서는 항상
```

옵션 하나하나는 4절, 큐 깊이는 5절, 캐시는 6절에서 자세히 본다.

이 실험 시리즈의 `lab.sh` 는 거의 모든 측정을 fio 로 한다. 이 페이지를 읽고 나면 `lab.sh` 안의 fio 줄을 직접 읽고 바꿀 수 있다.

## 2. 설치와 확인

```
$ sudo apt install fio
$ fio --version
fio-3.36
$ fio --enghelp            # 이 fio 가 쓸 수 있는 I/O 엔진 목록
Available IO engines:
	cpuio
	mmap
	sync
	psync
	...
	io_uring
	io_uring_cmd
```

apt 의 fio 에는 `libaio` 도 들어 있다 (`lab.sh` 의 기본값). 위 목록은 Claude 가 소스로 빌드한 fio 라 `libaio` 가 빠져 있다. 엔진은 5절.

## 3. 첫 실행 : 1 GiB 파일을 1 MiB 씩 순차로 읽기

```
$ mkdir -p ~/fiotest && cd ~/fiotest
$ fio --name=first --filename=test.img --size=1G --rw=read --bs=1M
```

옵션 다섯 개가 I/O 를 설명한다 : 이름 (`first`), 대상 (`test.img`, 없으면 만든다), 크기 (1 GiB), 모양 (`read` = 순차 읽기), 한 번에 읽는 크기 (1 MiB). 출력 (실제) :

```
first: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=psync, iodepth=1
fio-3.36
Starting 1 process
first: Laying out IO file (1 file / 1024MiB)

first: (groupid=0, jobs=1): err= 0: pid=14968: Sun Oct 18 08:23:56 2026
  read: IOPS=1698, BW=1698MiB/s (1781MB/s)(1024MiB/603msec)
    clat (usec): min=311, max=4798, avg=587.71, stdev=191.72
     lat (usec): min=311, max=4799, avg=587.77, stdev=191.74
    clat percentiles (usec):
     |  1.00th=[  347],  5.00th=[  388], 10.00th=[  420], 20.00th=[  465],
     | 30.00th=[  502], 40.00th=[  537], 50.00th=[  562], 60.00th=[  603],
     | 70.00th=[  644], 80.00th=[  701], 90.00th=[  766], 95.00th=[  832],
     | 99.00th=[ 1012], 99.50th=[ 1074], 99.90th=[ 1172], 99.95th=[ 4817],
     | 99.99th=[ 4817]
   bw (  MiB/s): min= 1698, max= 1698, per=99.99%, avg=1698.00, stdev= 0.00, samples=1
   iops        : min= 1698, max= 1698, avg=1698.00, stdev= 0.00, samples=1
  lat (usec)   : 500=29.98%, 750=58.50%, 1000=10.45%
  lat (msec)   : 2=0.98%, 10=0.10%
  cpu          : usr=0.00%, sys=45.35%, ctx=2814, majf=0, minf=264
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued rwts: total=1024,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=1

Run status group 0 (all jobs):
   READ: bw=1698MiB/s (1781MB/s), 1698MiB/s-1698MiB/s (1781MB/s-1781MB/s), io=1024MiB (1074MB), run=603-603msec

Disk stats (read/write):
  nvme0n1: ios=6969/0, sectors=1784064/0, merge=0/0, ticks=1062/0, in_queue=1063, util=58.31%
```

줄마다 :

```table
줄 | 뜻
`first: (g=0): rw=read, bs=… ioengine=psync, iodepth=1` | fio 가 이해한 설정. 적지 않은 것은 기본값 : 엔진 `psync`, 큐 깊이 1
`Laying out IO file` | 파일이 없어서 1 GiB 를 먼저 썼다 (처음 한 번만)
`read: IOPS=1698, BW=1698MiB/s (1781MB/s)(1024MiB/603msec)` | **결과의 중심.** 초당 I/O 수, 대역폭 (MiB/s = 2^20, 괄호 안 MB/s = 10^6), 옮긴 양 / 걸린 시간
`clat (usec): min=311, max=4798, avg=587.71` | completion latency : I/O 하나를 커널에 넘긴 뒤 끝날 때까지 (µs)
`lat (usec)` | 전체 지연 = slat (넘기는 데 든 시간) + clat. psync 는 slat 이 0 이라 따로 안 나온다
`clat percentiles` | 지연의 분포. `50.00th=[562]` = 절반은 562 µs 안에 끝났다. `99.00th=[1012]` = 100개 중 99개는 1 ms 안에
`bw (MiB/s): … samples=1` | 대역폭을 시간 구간마다 잰 값의 최소 · 최대 · 평균 (짧은 실행이라 표본 1개)
`lat (usec) : 500=29.98%, 750=58.50%` | 지연 막대그래프 : 500 µs 이하 30%, 500–750 µs 58.5% …
`cpu : usr= sys= ctx=` | fio 프로세스의 CPU 사용 (CPU 가 한계인지 볼 때)
`IO depths : 1=100.0%` | 실제로 동시에 걸려 있던 I/O 수의 분포. 큐 깊이를 32 로 줬는데 여기가 1=100% 면 설정이 먹지 않은 것이다 (5절)
`issued rwts: total=1024,0,0,0` | 실제로 낸 읽기 · 쓰기 · trim · sync 수
`Run status group 0` | 같은 그룹의 job 들을 합친 요약
`Disk stats` | 커널이 센 그 디스크의 요청 수. 1 MiB 1024개를 냈는데 `ios=6969` 인 것은 커널이 큰 요청을 장치 한도에 맞게 쪼갰기 때문이다
```

## 4. 꼭 알아야 할 옵션

```table
옵션 | 뜻 | 실험에서
`--name=X` | job 이름. 새 `--name` 이 나올 때마다 새 job 이 시작된다 (8절) | 결과 파일 이름
`--filename=F` | 대상 : 파일 또는 장치 (`/dev/sda`) | `lab.sh` 는 시리얼로 찾은 장치
`--rw=` | `read` · `write` (순차), `randread` · `randwrite` (랜덤), `rw` · `randrw` (섞기, `--rwmixread=70`), `trim` · `randtrim` | 실험마다
`--bs=4k` | I/O 하나의 크기 | 4k = FTL 매핑 단위
`--size=` | 다룰 범위 (`1G`, `100%` = 장치 전체) | `100%`, 또는 앞 80% (실험 10)
`--offset=` | 범위의 시작 (`16G`, `50%`) | 영역 나누기
`--io_size=` | 총 I/O 양. 없으면 size 만큼 한 번 | `cliff` : 용량의 2배
`--runtime=60 --time_based` | 60초 동안 (범위를 다 돌아도 처음부터 다시) | 대부분
`--ramp_time=2` | 처음 2초는 재지 않는다 (안정되기 전) | `perfmap`
`--direct=1` | 페이지 캐시를 거치지 않는다 (O_DIRECT) | **항상** (6절)
`--ioengine=` | I/O 를 내는 방법 : `psync`, `libaio`, `io_uring` … | `libaio`
`--iodepth=32` | 동시에 걸어 둘 I/O 수 (큐 깊이, QD) | 1 (지연), 32 (최대 IOPS)
`--numjobs=4` | 같은 job 을 4개 프로세스로 | 쓰지 않음 (QD 로 충분)
`--group_reporting` | numjobs 를 합쳐 한 덩어리로 보고 | `run_fio`
`--output-format=json --output=F` | 결과를 JSON 파일로 (9절) | 모든 실행
```

## 5. 엔진과 큐 깊이 : IOPS = 큐 깊이 ÷ 지연

4 KiB 랜덤 읽기를 세 번 했다 (모두 `--direct=1 --runtime=10 --time_based`).

**(a) psync, iodepth=1**

```
$ fio --name=rr --filename=test.img --size=1G --rw=randread --bs=4k --direct=1 --runtime=10 --time_based
  read: IOPS=12.5k, BW=48.8MiB/s (51.2MB/s)(488MiB/10001msec)
    clat (usec): min=25, max=3106, avg=79.28, stdev=19.80
```

**(b) psync 에 iodepth=32 를 주면**

```
$ fio ... --iodepth=32
note: both iodepth >= 1 and synchronous I/O engine are selected, queue depth will be capped at 1
  read: IOPS=12.5k, BW=48.8MiB/s (51.2MB/s)(488MiB/10001msec)
```

fio 가 경고하고 1 로 낮춘다. `psync` 는 `pread()` 를 부르고 **끝날 때까지 기다리는** 동기 엔진이라, 한 번에 하나만 걸 수 있다.

**(c) io_uring, iodepth=32**

```
$ fio ... --ioengine=io_uring --iodepth=32
  read: IOPS=398k, BW=1556MiB/s (1632MB/s)(15.2GiB/10001msec)
    slat (nsec): min=745, max=101909, avg=1220.68, stdev=629.40
    clat (usec): min=17, max=2070, avg=78.91, stdev=48.22
  ...
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=100.0%, >=64=0.0%
```

지연은 거의 같은데 (79 µs) IOPS 는 32배다. **Little 의 법칙** : 동시에 걸린 수 = 처리율 × 머무는 시간. 그러니

```table
경우 | 큐 깊이 | 평균 지연 | 큐 깊이 ÷ 지연 | fio 의 IOPS
(a) psync | 1 | 79.3 µs | 12,600 | 12.5k
(c) io_uring | 32 | 78.9 µs | 405,600 | 398k
```

NVMe 는 안에서 수십 개를 동시에 처리할 수 있어서, 32개를 걸어도 하나하나의 지연이 늘지 않았다. **SSD 의 병렬성 (채널 × die) 이 이것이다.**
840 EVO (SATA) 는 NCQ 한도가 32 이고 안의 병렬성도 작으니, 큐 깊이를 올리면 어느 지점부터 지연이 같이 늘 것이다 : 실험 5 에서 그 지점을 찾는다.

```table
엔진 | 방식 | 큐 깊이
`sync` · `psync` | `read()`/`pread()` : 끝날 때까지 기다림 | 1 (늘리려면 `--numjobs`)
`libaio` | Linux 비동기 I/O (`io_submit`). `--direct=1` 일 때만 진짜 비동기 | iodepth 만큼
`io_uring` | 새 비동기 인터페이스 (Linux 5.1+) : 호출 비용이 가장 작다 | iodepth 만큼
`posixaio` | POSIX AIO (glibc 가 스레드로 흉내) | 흉내
```

`lab.sh` 는 `ENGINE=libaio` 가 기본이고, `sudo ENGINE=io_uring ./lab.sh …` 로 바꿀 수 있다. SATA SSD 의 속도에서는 둘의 차이가 거의 없다.

## 6. 페이지 캐시와 `--direct=1`

3절의 첫 실행은 `--direct` 를 주지 않았다 : 읽기가 **페이지 캐시** (RAM) 를 거쳤다. 같은 읽기를 `--direct=1` 로 하면 :

```
$ fio --name=first --filename=test.img --size=1G --rw=read --bs=1M --direct=1
  read: IOPS=2151, BW=2151MiB/s (2256MB/s)(1024MiB/476msec)
    clat (usec): min=357, max=3082, avg=421.03, stdev=91.10
```

fio 는 기본값 `--invalidate=1` 로 **시작 전에 그 파일의 캐시를 버린다.** 그래서 첫 실행도 RAM 이 아니라 디스크에서 읽었다. 캐시를 버리지 않게 하면 (`--invalidate=0`, 파일이 이미 RAM 에 있음) :

```
$ fio --name=cached --filename=test.img --size=1G --rw=read --bs=1M --invalidate=0
  read: IOPS=2632, BW=2632MiB/s (2760MB/s)(1024MiB/389msec)
```

이 NVMe 는 RAM 복사와 속도가 비슷해서 차이가 작다. **840 EVO 에서는 다르다** : 디스크는 수백 MB/s 인데 RAM 은 수 GB/s 라, 캐시를 거치면 디스크가 아니라 RAM 을 재게 된다. 쓰기는 더 심하다 : 캐시를 거친 쓰기는 RAM 에 담기만 하고 '끝났다' 고 하기 때문이다.
그래서 `lab.sh` 의 fio 는 **모두 `--direct=1`** 이다. `fileage.py` 와 `readscan.py` 도 같은 이유로 `posix_fadvise(DONTNEED)` · `O_DIRECT` 를 쓴다.

## 7. 지연을 읽는 법

```table
이름 | 구간 | 무엇이 보이나
`slat` | fio 가 I/O 를 만들어 커널에 넘기는 데까지 | 보통 µs 이하. 크면 CPU · 엔진 문제
`clat` | 커널에 넘긴 뒤 끝났다는 알림까지 | **장치의 시간** (+ 커널 · 드라이버). 주로 이것을 본다
`lat` | slat + clat | 응용 프로그램이 느끼는 시간
```

평균만 보면 안 된다. SSD 는 대부분의 I/O 를 빨리 끝내다가 가끔 (GC, 지우기, read retry) 아주 늦는다. 이 '가끔' 이 **꼬리 지연** (tail latency) 이고, `99.00th` · `99.90th` · `99.99th` 와 `max` 에 보인다.
기본 percentile 목록을 바꾸려면 `--percentile_list=50:99:99.9:99.99`. 

## 8. job 파일 : 여러 job 을 동시에

명령 줄이 길어지면 같은 내용을 파일로 적는다. `[global]` 은 모든 job 의 공통값, `[이름]` 마다 job 하나다. 아래는 **한 job 이 순차로 쓰는 동안 다른 job 이 4 KiB 를 읽는** 시험이다 (실험 13 의 미리 보기).

```
; two.fio : 4 KiB random reads while another job writes sequentially
[global]
filename=test.img
size=1G
direct=1
ioengine=io_uring
time_based
runtime=10

[reader]
rw=randread
bs=4k
iodepth=1

[writer]
rw=write
bs=1M
iodepth=8
offset=512M
size=512M
```

```
$ fio two.fio
reader: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=io_uring, iodepth=1
writer: (g=0): rw=write, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=io_uring, iodepth=8
fio-3.36
Starting 2 processes

reader: (groupid=0, jobs=1): err= 0: pid=15203: Sun Oct 18 08:24:49 2026
  read: IOPS=3535, BW=13.8MiB/s (14.5MB/s)(138MiB/10001msec)
    clat percentiles (usec):
     |  1.00th=[   62],  5.00th=[   78], 10.00th=[   87], 20.00th=[  105],
     | 30.00th=[  125], 40.00th=[  145], 50.00th=[  167], 60.00th=[  190],
     | 70.00th=[  215], 80.00th=[  253], 90.00th=[  457], 95.00th=[  644],
     | 99.00th=[ 1582], 99.50th=[ 3884], 99.90th=[11207], 99.95th=[13042],
     | 99.99th=[65274]
writer: (groupid=0, jobs=1): err= 0: pid=15204: Sun Oct 18 08:24:49 2026
  write: IOPS=3057, BW=3058MiB/s (3206MB/s)(29.9GiB/10006msec); 0 zone resets
```

같은 4 KiB QD1 읽기가 혼자일 때 (5절 (a)) 와 비교하면 :

```table
읽기 job | IOPS | 50% | 99% | 99.9%
혼자 | 12.5k | 73 µs | 117 µs | 186 µs
쓰기와 함께 | 3.5k | 167 µs | 1,582 µs | 11,207 µs
```

쓰기가 있으면 읽기의 꼬리가 **60배** 길어졌다. NAND 칩이 프로그램 · 지우기를 하는 동안 같은 칩의 읽기는 기다려야 하기 때문이다. 840 EVO 에서 이 차이를 재는 것이 실험 13 이다.

job 파일 안에서도 명령 줄과 똑같은 이름을 쓴다 (`--` 만 뺀다). 명령 줄로도 할 수 있다 : 첫 `--name` 앞의 옵션은 global, 그 뒤는 그 job 의 옵션이다 (`lab.sh mixed` 가 이렇게 한다).

## 9. JSON 출력과 `fiosum.py`

사람이 읽는 출력은 보기 좋지만 숫자를 꺼내기 어렵다. `--output-format=json --output=r.json` 으로 저장하면 :

```
$ python3 -c "import json; d = json.load(open('r.json')); j = d['jobs'][0]; print(list(d)); print(list(j)[:12])"
['fio version', 'timestamp', 'timestamp_ms', 'time', 'jobs', 'disk_util']
['jobname', 'groupid', 'job_start', 'error', 'eta', 'elapsed', 'job options', 'read', 'write', 'trim', 'sync', 'job_runtime']
$ python3 -c "import json; j = json.load(open('r.json'))['jobs'][0]; print(j['read']['iops'], j['read']['clat_ns']['percentile']['99.000000'])"
137047.390522 107008
```

`read` · `write` 안에 `iops`, `bw_bytes`, `clat_ns` (`mean`, `max`, `percentile`) 가 있다. 지연은 **나노초** 다 (107008 ns = 107 µs).
`fiosum.py` 가 결과 폴더의 JSON 들을 한 표로 만든다 (`lab.sh` 가 실험 끝에 `summary.csv` 로 부른다) :

```
$ python3 fiosum.py sum.csv r.json | column -s, -t
run  job   rw        bs  qd  dir   iops    mbps   lat_mean_us  p50_us  p99_us  p999_us  max_us
r    json  randread  4k  8   read  137047  561.3  57           51      107     153      488
```

## 10. 시간에 따른 기록 (로그)

요약은 실행 전체의 평균이다. write cliff 처럼 **시간에 따라 바뀌는 것** 은 로그로 본다.

```table
옵션 | 기록하는 것 | 파일
`--write_bw_log=X` | 대역폭 (KiB/s) | `X_bw.log`
`--write_iops_log=X` | IOPS | `X_iops.log`
`--write_lat_log=X` | 지연 (ns) : slat · clat · lat 세 파일 | `X_lat.log`, `X_clat.log`, `X_slat.log`
`--log_avg_msec=1000` | 1초마다 평균 한 줄 (없으면 **I/O 마다** 한 줄 : 파일이 거대해진다) | (위 파일들의 형식)
`--log_max_value=1` | 평균 대신 그 구간의 **최댓값** (꼬리를 볼 때) | 실험 13, 15
`--per_job_logs=0` | 파일 이름에 job 번호 (`.1`) 를 붙이지 않는다 | `X_iops.log` (없으면 `X_iops.1.log`)
```

```
$ fio --name=log --filename=test.img --size=1G --rw=randread --bs=4k --direct=1 --ioengine=io_uring --iodepth=4 \
      --runtime=4 --time_based --write_iops_log=lg --log_avg_msec=1000 --per_job_logs=0
$ cat lg_iops.log
1000, 57860, 0, 0, 0
2000, 60684, 0, 0, 0
3000, 59914, 0, 0, 0
```

열 : 시각 (ms), 값, 방향 (0 읽기, 1 쓰기, 2 trim), 블록 크기 (평균 로그에서는 0), 위치 (평균 로그에서는 0). `plot.py` 가 이 파일을 그린다.

## 11. 데이터 확인 (verify)

fio 는 쓸 때 블록마다 체크섬을 넣고, 나중에 읽어서 확인할 수 있다. 실험 15 (read disturb) 와 16 (retention) 이 이것을 쓴다.

```
$ fio --name=v --filename=v.img --size=64M --rw=write --bs=1M --verify=crc32c --verify_interval=4096 --do_verify=0
  write: IOPS=1777, BW=1778MiB/s (1864MB/s)(64.0MiB/36msec); 0 zone resets
$ fio --name=v --filename=v.img --size=64M --rw=write --bs=1M --verify=crc32c --verify_interval=4096 --verify_only
  read: IOPS=2133, BW=2133MiB/s (2237MB/s)(64.0MiB/30msec)          # err= 0 : 모두 맞다
```

일부러 5 MiB 지점의 4바이트를 망가뜨린 뒤 다시 확인하면 :

```
$ printf 'XXXX' | dd of=v.img bs=1 seek=$((5*1048576+100)) conv=notrunc status=none
$ fio --name=v --filename=v.img --size=64M --rw=write --bs=1M --verify=crc32c --verify_interval=4096 \
      --verify_only --verify_fatal=0 --verify_dump=0
crc32c: verify failed at file v.img offset 5242880, length 4096 (requested block: offset=5242880, length=1048576, flags=88)
       Expected CRC: 5c975db9
       Received CRC: dd783b93
```

```table
옵션 | 뜻
`--verify=crc32c` | 체크섬 종류 (md5, sha256 … 도 된다. crc32c 가 빠르다)
`--verify_interval=4096` | 4 KiB 마다 머리말 하나 : 틀린 곳을 4 KiB 단위로 짚는다
`--do_verify=0` | 쓰기만 하고 바로 확인하지 않는다 (나중에 따로 확인)
`--verify_only` | 쓰지 않고, 같은 설정으로 '썼을 내용' 을 읽어서 확인만
`--verify_fatal=0` | 틀린 것을 찾아도 멈추지 않고 끝까지
`--verify_dump=0` | 틀린 블록을 파일로 쏟아 내지 않는다
```

확인할 때의 옵션 (`--rw`, `--bs`, `--size`, `--verify*`) 은 **쓸 때와 같아야** 한다. 그래서 `lab.sh` 는 쓰기와 확인에 같은 줄을 쓴다.

## 12. 랜덤 · 데이터 내용을 정하는 옵션

```table
옵션 | 뜻 | 실험
`--norandommap` | 이미 쓴 LBA 도 다시 고를 수 있다 (진짜 랜덤). 없으면 모든 블록을 한 번씩 다 쓴 뒤에야 반복 | 8, 10, 11
`--randrepeat=0` | 실행마다 다른 난수 (기본 1 = 매번 같은 순서) | 대부분
`--random_generator=tausworthe64` | 큰 장치에서도 고르게 퍼지는 64비트 난수 | 8
`--random_distribution=zipf:1.2` | 일부 LBA 가 훨씬 자주 (뜨거운 데이터). `pareto:0.9`, `zoned:80/20:20/80` (쓰기의 80% 가 공간의 20% 에) | 11
`--refill_buffers` | I/O 마다 새 무작위 내용 (압축 · 중복 제거가 안 되게) | 5
`--zero_buffers` | 0 으로만 | 5
`--buffer_compress_percentage=50` | 절반쯤 압축되는 내용 | 5
`--buffer_pattern=0xdeadbeef` | 정해진 무늬 반복 | 5
`--fsync=1` | 쓰기 1번마다 fsync (장치에 FLUSH) | 7
`--blockalign=4k --offset=512` | 4 KiB 경계에서 512 B 어긋난 쓰기 | 6
```

## 13. 장치에 직접 쓸 때 {#danger}

<div class="warn" markdown="1">
`--filename=/dev/sdX` 로 쓰기 (`write`, `randwrite`, `trim`, verify 의 쓰기) 를 하면 **파티션 표와 파일 시스템까지 그 자리에서 덮어쓴다.** 묻지 않는다.
- 읽기만 할 때는 `--readonly` 를 붙인다 : 쓰기 옵션이 섞여 있으면 fio 가 거부한다.
- `lab.sh` 를 거치면 시리얼 확인 · 마운트 확인 · 시리얼 끝 5자리 입력을 거친다. 직접 fio 를 쓸 때는 `lsblk -o NAME,MODEL,SERIAL` 로 이름을 **매번** 확인한다 (이 컴퓨터에서는 디스크 이름이 이미 두 번 바뀌었다).
</div>

## 14. `lab.sh` 안의 fio

모든 실험은 `run_fio 이름 옵션…` 한 함수를 거친다. 공통 옵션 :

```
fio --name=NAME --filename=$DEV --direct=1 --ioengine=$ENGINE \
    --group_reporting --per_job_logs=0 --log_avg_msec=1000 \
    --write_bw_log=$OUT/NAME --write_iops_log=$OUT/NAME --write_lat_log=$OUT/NAME \
    --output-format=json --output=$OUT/NAME.json --verify_state_save=0 \
    --eta=always --eta-newline=30  (그리고 실험마다의 옵션)
```

```table
실험 | 그 실험만의 fio 옵션
3 SLC 캐시 | `--rw=write --bs=1M --iodepth=8 --size=100%`
4 TRIM | `--rw=randread --bs=4k --iodepth=1` 과 `32`, 앞 절반 / 뒤 절반 (`--offset`)
5 성능 지도 | `--rw=randread·read·randwrite·write` × `--bs=4k…1m` × `--iodepth=1·4·32`, `--runtime=20`
6 쓰기 크기 | `--bs=512…64k`, `--blockalign=4k --offset=512`
7 FLUSH | `--fsync=1`, (hdparm `-W0` 와 함께)
8 · 10 · 11 cliff | `--rw=randwrite --bs=4k --iodepth=32 --norandommap --io_size=용량×2 --random_distribution=…`
13 간섭 | job 두 개 : `randread` QD1 + `write` 또는 `randwrite`, `--log_max_value=1`
15 read disturb | `--size=1M --rw=randread --iodepth=32 --runtime=시간`
16 retention | `--verify=crc32c --verify_interval=4096` 쓰기 → 몇 주 뒤 `--verify_only`
```

## 15. 자주 하는 실수

```table
실수 | 증상 | 고치기
`--direct=1` 을 빠뜨림 | 읽기 · 쓰기가 비현실적으로 빠르다 | 항상 `--direct=1`
동기 엔진에 iodepth | `queue depth will be capped at 1` | `--ioengine=libaio` 또는 `io_uring`
`--size` 가 작고 `--time_based` | 같은 작은 영역만 반복 : 캐시 · SLC 에 다 들어간다 | 범위를 크게 (`100%`)
TRIM 된 장치를 읽음 | 읽기가 NAND 를 안 거쳐 아주 빠르다 (실험 4) | 먼저 채운다 (`lab.sh` 의 `fill_all`)
쓰기를 짧게 한 번만 | SLC 버퍼 안의 속도만 봄 | 버퍼보다 많이 쓰거나 (실험 3), 버퍼 속도라고 적는다
`MiB` 와 `MB` 를 섞음 | 5% 차이 | fio 는 둘 다 보여 준다 : 표에는 하나만
평균만 봄 | GC 의 멈춤이 안 보인다 | percentile, 1초 로그 (`--log_max_value=1`)
```

## 16. 더 읽을 것

- `man fio`, 또는 공식 문서 [fio.readthedocs.io](https://fio.readthedocs.io/en/latest/fio_doc.html) : 옵션 전체 (수백 개)
- `/usr/share/doc/fio/examples/` : job 파일 예제 (apt 로 깔면 있다)
- `fio --cmdhelp=옵션이름` : 옵션 하나의 설명. 예 : `fio --cmdhelp=norandommap`

@@NAV@@
