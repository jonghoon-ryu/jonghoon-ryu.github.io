---
layout: default
title: fio 사용법
permalink: /old-ssd-experiments/fio/
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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>묻는 것</th>
<th>예</th>
</tr></thead><tbody>
<tr><td><code>--name</code></td><td><strong>누가</strong> : job 의 이름. 출력 · JSON · 로그 파일 이름에 쓰인다</td><td><code>--name=slc</code></td></tr>
<tr><td><code>--filename</code></td><td><strong>어디에</strong> : 파일 또는 장치</td><td><code>--filename=test.img</code>, <code>/dev/sda</code></td></tr>
<tr><td><code>--rw</code></td><td><strong>무엇을</strong> : 읽기 / 쓰기, 순차 / 랜덤</td><td><code>read</code>, <code>write</code>, <code>randread</code>, <code>randwrite</code></td></tr>
<tr><td><code>--bs</code></td><td><strong>얼마나 크게</strong> : I/O 하나의 크기</td><td><code>4k</code>, <code>1M</code></td></tr>
<tr><td><code>--iodepth</code></td><td><strong>동시에 몇 개</strong> : 한꺼번에 걸어 둘 I/O 수 (큐 깊이)</td><td><code>1</code>, <code>32</code></td></tr>
<tr><td><code>--size</code></td><td><strong>얼마나 많이</strong> : 다룰 범위</td><td><code>1G</code>, <code>100%</code></td></tr>
<tr><td><code>--runtime=S --time_based</code></td><td><strong>얼마나 오래</strong> : S 초 동안 (범위를 다 돌아도 다시 처음부터)</td><td><code>--runtime=60 --time_based</code></td></tr>
<tr><td><code>--direct=1</code></td><td><strong>RAM 캐시를 건너뛰고</strong> : 페이지 캐시가 아니라 장치를 잰다</td><td>실험에서는 항상</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>줄</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>first: (g=0): rw=read, bs=… ioengine=psync, iodepth=1</code></td><td>fio 가 이해한 설정. 적지 않은 것은 기본값 : 엔진 <code>psync</code>, 큐 깊이 1</td></tr>
<tr><td><code>Laying out IO file</code></td><td>파일이 없어서 1 GiB 를 먼저 썼다 (처음 한 번만)</td></tr>
<tr><td><code>read: IOPS=1698, BW=1698MiB/s (1781MB/s)(1024MiB/603msec)</code></td><td><strong>결과의 중심.</strong> 초당 I/O 수, 대역폭 (MiB/s = 2^20, 괄호 안 MB/s = 10^6), 옮긴 양 / 걸린 시간</td></tr>
<tr><td><code>clat (usec): min=311, max=4798, avg=587.71</code></td><td>completion latency : I/O 하나를 커널에 넘긴 뒤 끝날 때까지 (µs)</td></tr>
<tr><td><code>lat (usec)</code></td><td>전체 지연 = slat (넘기는 데 든 시간) + clat. psync 는 slat 이 0 이라 따로 안 나온다</td></tr>
<tr><td><code>clat percentiles</code></td><td>지연의 분포. <code>50.00th=[562]</code> = 절반은 562 µs 안에 끝났다. <code>99.00th=[1012]</code> = 100개 중 99개는 1 ms 안에</td></tr>
<tr><td><code>bw (MiB/s): … samples=1</code></td><td>대역폭을 시간 구간마다 잰 값의 최소 · 최대 · 평균 (짧은 실행이라 표본 1개)</td></tr>
<tr><td><code>lat (usec) : 500=29.98%, 750=58.50%</code></td><td>지연 막대그래프 : 500 µs 이하 30%, 500–750 µs 58.5% …</td></tr>
<tr><td><code>cpu : usr= sys= ctx=</code></td><td>fio 프로세스의 CPU 사용 (CPU 가 한계인지 볼 때)</td></tr>
<tr><td><code>IO depths : 1=100.0%</code></td><td>실제로 동시에 걸려 있던 I/O 수의 분포. 큐 깊이를 32 로 줬는데 여기가 1=100% 면 설정이 먹지 않은 것이다 (5절)</td></tr>
<tr><td><code>issued rwts: total=1024,0,0,0</code></td><td>실제로 낸 읽기 · 쓰기 · trim · sync 수</td></tr>
<tr><td><code>Run status group 0</code></td><td>같은 그룹의 job 들을 합친 요약</td></tr>
<tr><td><code>Disk stats</code></td><td>커널이 센 그 디스크의 요청 수. 1 MiB 1024개를 냈는데 <code>ios=6969</code> 인 것은 커널이 큰 요청을 장치 한도에 맞게 쪼갰기 때문이다</td></tr>
</tbody></table></div>

## 4. 꼭 알아야 할 옵션

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>뜻</th>
<th>실험에서</th>
</tr></thead><tbody>
<tr><td><code>--name=X</code></td><td>job 이름. 새 <code>--name</code> 이 나올 때마다 새 job 이 시작된다 (8절)</td><td>결과 파일 이름</td></tr>
<tr><td><code>--filename=F</code></td><td>대상 : 파일 또는 장치 (<code>/dev/sda</code>)</td><td><code>lab.sh</code> 는 시리얼로 찾은 장치</td></tr>
<tr><td><code>--rw=</code></td><td><code>read</code> · <code>write</code> (순차), <code>randread</code> · <code>randwrite</code> (랜덤), <code>rw</code> · <code>randrw</code> (섞기, <code>--rwmixread=70</code>), <code>trim</code> · <code>randtrim</code></td><td>실험마다</td></tr>
<tr><td><code>--bs=4k</code></td><td>I/O 하나의 크기</td><td>4k = FTL 매핑 단위</td></tr>
<tr><td><code>--size=</code></td><td>다룰 범위 (<code>1G</code>, <code>100%</code> = 장치 전체)</td><td><code>100%</code>, 또는 앞 80% (실험 10)</td></tr>
<tr><td><code>--offset=</code></td><td>범위의 시작 (<code>16G</code>, <code>50%</code>)</td><td>영역 나누기</td></tr>
<tr><td><code>--io_size=</code></td><td>총 I/O 양. 없으면 size 만큼 한 번</td><td><code>cliff</code> : 용량의 2배</td></tr>
<tr><td><code>--runtime=60 --time_based</code></td><td>60초 동안 (범위를 다 돌아도 처음부터 다시)</td><td>대부분</td></tr>
<tr><td><code>--ramp_time=2</code></td><td>처음 2초는 재지 않는다 (안정되기 전)</td><td><code>perfmap</code></td></tr>
<tr><td><code>--direct=1</code></td><td>페이지 캐시를 거치지 않는다 (O_DIRECT)</td><td><strong>항상</strong> (6절)</td></tr>
<tr><td><code>--ioengine=</code></td><td>I/O 를 내는 방법 : <code>psync</code>, <code>libaio</code>, <code>io_uring</code> …</td><td><code>libaio</code></td></tr>
<tr><td><code>--iodepth=32</code></td><td>동시에 걸어 둘 I/O 수 (큐 깊이, QD)</td><td>1 (지연), 32 (최대 IOPS)</td></tr>
<tr><td><code>--numjobs=4</code></td><td>같은 job 을 4개 프로세스로</td><td>쓰지 않음 (QD 로 충분)</td></tr>
<tr><td><code>--group_reporting</code></td><td>numjobs 를 합쳐 한 덩어리로 보고</td><td><code>run_fio</code></td></tr>
<tr><td><code>--output-format=json --output=F</code></td><td>결과를 JSON 파일로 (9절)</td><td>모든 실행</td></tr>
</tbody></table></div>

### `--name` : job 의 이름

job 하나 = **I/O 작업 하나의 설명** (모양 하나, 대상 하나, 옵션 한 벌). `--name` 은 그 job 의 이름이고, 세 가지 일을 한다.

**1. 결과에 이름표를 붙인다.** 출력의 줄마다 앞에 붙고 (`first: (groupid=0, jobs=1) …`), JSON 에서는 `"jobname"`, `fiosum.py` 의 `job` 열이 된다. job 이 여러 개일 때 어느 숫자가 어느 job 것인지 알려 준다.

**2. 명령 줄에서 `--name` 은 새 job 의 시작이다.** fio 는 옵션을 왼쪽부터 읽는다 : 첫 `--name` **앞** 의 옵션은 모든 job 에 공통 (global), `--name` **뒤** 의 옵션은 다음 `--name` 까지 **그 job** 의 것이다.

```
fio --filename=test.img --size=1G --direct=1 \        ← 공통 : 두 job 모두
    --name=reader --rw=randread --bs=4k \             ← job 1
    --name=writer --rw=write --bs=1M                  ← job 2
```

job 파일 (8절) 에서는 같은 것을 `[global]`, `[reader]`, `[writer]` 절로 적는다.

**3. `--filename` 이 없으면 이름이 파일 이름이 된다** (실제 출력, 2026.10.18) :

```
$ fio --name=hello --size=16M --rw=write --bs=1M
hello: Laying out IO file (1 file / 16MiB)
$ ls
hello.0.0
$ fio --name=hello --size=16M --rw=read --bs=1M --numjobs=2
hello: (groupid=0, jobs=1): err= 0: pid=51749: …
hello: (groupid=0, jobs=1): err= 0: pid=51750: …
$ ls
hello.0.0  hello.1.0
```

파일 이름은 `이름.job번호.파일번호` 다. `--numjobs=2` (같은 job 의 복사본 둘) 는 복사본마다 자기 파일을 가지고, 둘 다 `hello` 라는 이름으로 (다른 `pid` 로) 보고한다. 로그 파일 (`--write_bw_log` …) 도 보통 이름을 앞에 붙인다 : `lab.sh` 가 job 이름을 `slc`, `rd-mapped`, `cliff` 처럼 재는 것으로 짓는 이유다. `--name` 은 꼭 있어야 하고, I/O 자체는 바꾸지 않는다.

### job 은 무엇인가 : 동시에 하는 세 가지 방법

job 하나 = **일꾼 하나 + 작업 하나** 다. job 마다 프로세스가 하나씩 생기고, **여러 job 은 기본으로 동시에** 돈다. 같은 파일에 4 KiB 랜덤 읽기를 3초씩 (실제 출력, 이 컴퓨터의 NVMe) :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>설정</th>
<th>일어난 일</th>
<th>IOPS</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td>job 2개 (A, B)</td><td><code>Starting 2 processes</code>, 둘 다 같은 3초에 (<code>groupid=0</code>)</td><td>A 14.4k + B 14.8k = <strong>29.2k</strong></td><td>서로 다른 작업 둘이 <strong>동시에</strong>, 프로세스 둘</td></tr>
<tr><td>job 2개 + <code>--stonewall</code></td><td>B 가 <code>groupid=1</code> : <strong>A 가 끝나기를 기다렸다</strong></td><td>A 16.5k, 그다음 B 14.4k</td><td><code>stonewall</code> = 앞의 job 들이 끝난 뒤에 시작 (<strong>차례로</strong>)</td></tr>
<tr><td>job 1개, <code>--iodepth=1</code></td><td>프로세스 하나, I/O 하나씩</td><td>14.5k</td><td>기준 (job 하나가 낼 수 있는 만큼)</td></tr>
<tr><td>job 1개, <code>--iodepth=2</code></td><td>프로세스 하나가 I/O 둘을 걸어 둠</td><td><strong>27.7k</strong> (거의 2배)</td><td>프로세스를 늘리지 않고 job <strong>안에서</strong> 동시에</td></tr>
</tbody></table></div>

'동시에' 에는 세 가지가 있다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>방법</th>
<th>무엇을 동시에</th>
<th>언제 쓰나</th>
</tr></thead><tbody>
<tr><td>job 여러 개</td><td><strong>서로 다른</strong> 작업 : 예를 들어 읽기 + 쓰기</td><td>실험 13 (간섭) : <code>lab.sh mixed</code></td></tr>
<tr><td><code>--numjobs=N</code></td><td><strong>같은</strong> job 의 복사본 N 개</td><td>여러 프로그램이 같은 일을 하는 모습</td></tr>
<tr><td><code>--iodepth=N</code></td><td>job 하나가 장치에 N 개의 요청을 걸어 둠</td><td>SSD 에 짐을 싣는 보통 방법 : <code>lab.sh</code> 의 QD8 · QD32</td></tr>
</tbody></table></div>

job 2개 (29.2k) 와 job 1개 · 깊이 2 (27.7k) 가 거의 같다 : 어느 쪽이든 NVMe 는 요청 2개를 함께 받았다. 읽기 하나의 시간은 그대로 (64 – 67 µs) 였으니, 걸린 요청이 많을수록 IOPS 가 는다 (5절의 Little 의 법칙).

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>경우</th>
<th>큐 깊이</th>
<th>평균 지연</th>
<th>큐 깊이 ÷ 지연</th>
<th>fio 의 IOPS</th>
</tr></thead><tbody>
<tr><td>(a) psync</td><td>1</td><td>79.3 µs</td><td>12,600</td><td>12.5k</td></tr>
<tr><td>(c) io_uring</td><td>32</td><td>78.9 µs</td><td>405,600</td><td>398k</td></tr>
</tbody></table></div>

NVMe 는 안에서 수십 개를 동시에 처리할 수 있어서, 32개를 걸어도 하나하나의 지연이 늘지 않았다. **SSD 의 병렬성 (채널 × die) 이 이것이다.**
840 EVO (SATA) 는 NCQ 한도가 32 이고 안의 병렬성도 작으니, 큐 깊이를 올리면 어느 지점부터 지연이 같이 늘 것이다 : 실험 5 에서 그 지점을 찾는다.

### `--ioengine` 이란

`--ioengine` 은 **fio 가 I/O 하나를 커널에 넘기는 방법** 이다 : 어떤 시스템 호출 (또는 커널 인터페이스) 로 '여기서 4 KiB 를 읽어 달라' 고 말하나. 드라이브가 받는 읽기 · 쓰기는 같다. 달라지는 것은 프로그램이 그것을 어떻게 기다리느냐, 그래서 **한꺼번에 몇 개를 걸어 둘 수 있느냐** 다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>엔진</th>
<th>커널 인터페이스</th>
<th>하는 방식</th>
<th>걸어 둘 수 있는 수</th>
</tr></thead><tbody>
<tr><td><code>sync</code></td><td><code>read()</code> / <code>write()</code></td><td>요청하고 데이터가 올 때까지 <strong>기다린 뒤</strong> 다음 요청</td><td>1</td></tr>
<tr><td><code>psync</code> (기본값)</td><td><code>pread()</code> / <code>pwrite()</code></td><td>같다. 위치를 같은 호출에 넣는다 (<code>lseek</code> 가 따로 없다)</td><td>1 (늘리려면 <code>--numjobs</code>)</td></tr>
<tr><td><code>libaio</code></td><td>Linux AIO : <code>io_submit()</code> + <code>io_getevents()</code></td><td><strong>여러 요청을 넘기고, 끝난 것은 나중에 모아 받는다.</strong> <code>--direct=1</code> 일 때만 진짜 비동기</td><td><code>iodepth</code> 만큼</td></tr>
<tr><td><code>io_uring</code></td><td>커널과 함께 쓰는 링 버퍼 둘 : 제출 큐와 완료 큐</td><td>libaio 와 같은 일을 시스템 호출을 훨씬 적게 하며 : 요청과 완료가 공유 메모리로 오간다 (Linux 5.1+)</td><td><code>iodepth</code> 만큼</td></tr>
<tr><td><code>posixaio</code></td><td>POSIX <code>aio_read()</code></td><td>겉보기만 비동기 : glibc 가 도우미 스레드로 흉내 낸다</td><td>흉내</td></tr>
<tr><td><code>mmap</code></td><td>메모리에 대응시킨 파일</td><td>메모리를 읽고 쓰듯이 I/O</td><td>—</td></tr>
<tr><td><code>null</code></td><td>없음</td><td>I/O 를 하지 않는다 : fio 자신의 비용을 잰다</td><td>—</td></tr>
<tr><td><code>sg</code>, <code>io_uring_cmd</code></td><td>SCSI · NVMe 직접 전달</td><td>블록 계층을 건너뛰고 SCSI · NVMe 명령을 그대로 보낸다</td><td>—</td></tr>
</tbody></table></div>

**두 가지 방식**

```
동기 (psync) :          넘김 ─ 기다림 ─ 끝 │ 넘김 ─ 기다림 ─ 끝 │ …          한 번에 하나
비동기 (libaio, io_uring) :
                        넘김 ×32 ─────────────────────────────────▶
                        끝난 것을 오는 대로 받고, 다시 채워서 늘 32개가 걸려 있게
```

그래서 **`--iodepth` 는 비동기 엔진에서만 뜻이 있다.** 위의 (b) 처럼 `psync` 에 `--iodepth=32` 를 주면 `queue depth will be capped at 1` 이 나오고 12.5k IOPS 그대로다. 같은 NVMe 에서 `io_uring` 에 `--iodepth=32` 는 398k IOPS 였다 : 읽기 하나의 시간 (약 79 µs) 은 같은데 걸어 둔 수가 32배다.

**libaio 와 io_uring** : 둘 다 요청을 많이 걸어 둔다. `io_uring` 은 더 새롭고 요청마다 드는 비용이 더 작다 : 한 묶음을 시스템 호출 하나로, 폴링 모드에서는 시스템 호출 없이 넘기고 받는다. 빠른 NVMe 에서 초당 수백만 번을 할 때 차이가 난다. 120GB SSD (SATA, 10만 IOPS 이하) 에서는 둘이 같은 숫자를 낸다.

**SSD 를 잴 때** : `libaio` 나 `io_uring` 을 쓰고 늘 `--direct=1` 을 함께 준다. `psync` 는 '한 번에 하나' 를 일부러 보고 싶을 때 쓴다 : `read()` 를 되풀이하는 단순한 프로그램과 같은 모습이다.

`lab.sh` 는 모든 fio 빌드에 들어 있는 `libaio` 가 기본이고, `sudo ENGINE=io_uring ./lab.sh …` 로 바꿀 수 있다.

### `iodepth` 가 1 보다 크면 요청을 한꺼번에 보내나

꼭 그렇지는 않다. `--iodepth=N` 은 **'보냈지만 아직 끝나지 않은 요청을 최대 N 개까지 둔다'** 는 뜻이다. N 개를 같은 순간에 쏘는 것이 아니다.

**1. fio 가 큐를 채우고 유지하는 방법**

```
시작 :   1, 2, 3 … 32 까지 차례로 넘긴다        (큐를 채우는 데 몇 µs)
그 뒤 :  하나가 끝나면 → 하나를 새로 넘긴다      (늘 32개가 걸려 있게)
         또 하나가 끝나면 → 또 하나를 넘긴다
         …
```

처음 뒤로는 **끊임없이 채우는** 일이다 : 걸린 수가 N 근처에 머물고, 끝날 때마다 새로 넘긴다. `--iodepth_batch_submit`, `--iodepth_batch_complete` 로 더 큰 묶음으로 넘기고 받게 할 수 있지만 생각은 같다. 실제로 몇 개가 걸려 있었는지는 출력의 `IO depths` 줄이 알려 준다 (예 : `32=100.0%` = 거의 늘 32개).

**2. 드라이브로 가는 길에서도 '동시' 가 아니다.** 요청은 여러 층을 지나고, 층마다 한도가 있다 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>층</th>
<th>하는 일</th>
<th>이 컴퓨터의 한도</th>
</tr></thead><tbody>
<tr><td>fio</td><td>N 개를 걸어 둔다</td><td><code>iodepth</code></td></tr>
<tr><td>블록 계층 (I/O 스케줄러)</td><td>이웃한 요청을 합치고 순서를 바꿀 수 있다 (<code>sda</code> 는 <code>mq-deadline</code>)</td><td><code>/sys/block/sda/queue/nr_requests</code></td></tr>
<tr><td>SATA 드라이버 + 링크</td><td>명령은 <strong>케이블 하나</strong> 로 <strong>차례로</strong> 간다. 명령마다 번호표 (tag) 가 붙는다</td><td>NCQ 번호표 <strong>32개</strong> (<code>/sys/block/sda/device/queue_depth</code> = 32)</td></tr>
<tr><td>SSD 안</td><td>컨트롤러가 여러 명령을 동시에 다룬다 : NAND 칩 (die) 여럿에 나눠 주고, 끝나는 순서는 <strong>들어온 순서와 다를 수 있다</strong></td><td>드라이브 안의 병렬성</td></tr>
</tbody></table></div>

진짜 '동시' 는 맨 아래에서 일어난다 : **드라이브가 명령을 32개까지 받아 두고**, NAND 칩들이 그중 여럿을 같은 때에 처리한다 (칩마다 한 페이지를 읽거나 쓰는 중). `iodepth=1` 이면 칩 하나만 일하고 나머지는 논다.

**3. 그래서 `iodepth` 를 늘리는 것은 드라이브에 노는 칩이 있을 때만 도움이 된다** (Little 의 법칙 : IOPS ≈ 걸린 수 ÷ 하나의 시간) :
- 칩이 남아 있는 동안 : 걸린 수가 늘면 IOPS 가 늘고, 하나의 시간은 그대로다. 이 컴퓨터의 NVMe 에서 1 → 32 가 12.5k → 398k, 하나에 약 79 µs 그대로였다
- 칩이 모두 바빠진 뒤 : 더 걸어 둔 요청은 **줄을 서서 기다린다**. IOPS 는 그대로이고 **지연이 는다**

120GB SSD 에서 그 지점이 어디인지가 실험 5 (`iodepth` 1 · 4 · 32) 다. SATA 에는 딱 막힌 한도도 있다 : 드라이브가 받는 명령은 32개까지다. `sda` 에 `--iodepth=64` 를 주면 넘친 32개는 드라이브가 아니라 커널에서 기다린다.

### `iodepth=1` 이면 동기와 비동기 엔진이 다른가

**거의 같다.** 둘 다 걸린 요청이 딱 하나라 드라이브가 받는 것이 같다. 같은 파일에 4 KiB 랜덤 읽기를 5초씩, 두 번씩 (실제 출력, 이 컴퓨터의 NVMe) :

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>엔진</th>
<th>IOPS (1번 / 2번)</th>
<th>slat (넘기기)</th>
<th>clat (끝나기까지)</th>
<th>lat (전체)</th>
</tr></thead><tbody>
<tr><td><code>psync</code></td><td>15.0k / 15.4k</td><td>— (나오지 않음)</td><td>65.7 / 64.3 µs</td><td><strong>65.8 / 64.4 µs</strong></td></tr>
<tr><td><code>io_uring</code></td><td>14.8k / 15.2k</td><td>4.2 / 3.9 µs</td><td>62.7 / 61.2 µs</td><td><strong>66.9 / 65.1 µs</strong></td></tr>
</tbody></table></div>

실행마다의 차이 (±0.4k) 가 엔진 사이의 차이만큼 크다. 작게 다른 것들 :

1. **시간을 나누는 법.** 비동기 엔진은 두 단계 (넘기기, 모아 받기) 라서 넘기는 시간 **slat** (약 4 µs) 을 따로 보여 준다. `psync` 는 `pread()` 하나 안에서 넘기고 기다리므로 모두 clat 에 들어간다. **전체 (`lat`) 는 같다** : 엔진끼리 비교할 때는 `clat` 이 아니라 `lat` 을 본다.
2. **CPU 와 시스템 호출.** 비동기 엔진은 I/O 하나에 단계가 더 많다 (`libaio` 는 `io_submit` + `io_getevents` 두 번, `pread` 는 한 번). I/O 마다 CPU 몇 µs (`usr` 3–4% 대 2–3%). 아주 빠른 장치에서만 보인다 : 읽기 하나 65 µs 인 이 NVMe 에서는 잡음에 묻히고, 120GB SSD (읽기 하나 약 100 µs 이상) 에서는 보이지 않는다.
3. **`libaio` 의 함정** : `--direct=1` 이 없으면 `libaio` 는 조용히 동기가 된다. 그러면 어차피 엔진을 고른 뜻이 없다.

**정리** : `iodepth=1` 에서는 엔진이 재는 값을 바꾸지 않는다. 엔진이 중요해지는 것은 **요청을 둘 이상 걸어 두고 싶을 때** 부터다. `lab.sh` 는 일관성을 위해 모든 곳에서 `libaio` 를 쓴다.

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>이름</th>
<th>구간</th>
<th>무엇이 보이나</th>
</tr></thead><tbody>
<tr><td><code>slat</code></td><td>fio 가 I/O 를 만들어 커널에 넘기는 데까지</td><td>보통 µs 이하. 크면 CPU · 엔진 문제</td></tr>
<tr><td><code>clat</code></td><td>커널에 넘긴 뒤 끝났다는 알림까지</td><td><strong>장치의 시간</strong> (+ 커널 · 드라이버). 주로 이것을 본다</td></tr>
<tr><td><code>lat</code></td><td>slat + clat</td><td>응용 프로그램이 느끼는 시간</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>읽기 job</th>
<th>IOPS</th>
<th>50%</th>
<th>99%</th>
<th>99.9%</th>
</tr></thead><tbody>
<tr><td>혼자</td><td>12.5k</td><td>73 µs</td><td>117 µs</td><td>186 µs</td></tr>
<tr><td>쓰기와 함께</td><td>3.5k</td><td>167 µs</td><td>1,582 µs</td><td>11,207 µs</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>기록하는 것</th>
<th>파일</th>
</tr></thead><tbody>
<tr><td><code>--write_bw_log=X</code></td><td>대역폭 (KiB/s)</td><td><code>X_bw.log</code></td></tr>
<tr><td><code>--write_iops_log=X</code></td><td>IOPS</td><td><code>X_iops.log</code></td></tr>
<tr><td><code>--write_lat_log=X</code></td><td>지연 (ns) : slat · clat · lat 세 파일</td><td><code>X_lat.log</code>, <code>X_clat.log</code>, <code>X_slat.log</code></td></tr>
<tr><td><code>--log_avg_msec=1000</code></td><td>1초마다 평균 한 줄 (없으면 <strong>I/O 마다</strong> 한 줄 : 파일이 거대해진다)</td><td>(위 파일들의 형식)</td></tr>
<tr><td><code>--log_max_value=1</code></td><td>평균 대신 그 구간의 <strong>최댓값</strong> (꼬리를 볼 때)</td><td>실험 13, 15</td></tr>
<tr><td><code>--per_job_logs=0</code></td><td>파일 이름에 job 번호 (<code>.1</code>) 를 붙이지 않는다</td><td><code>X_iops.log</code> (없으면 <code>X_iops.1.log</code>)</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>뜻</th>
</tr></thead><tbody>
<tr><td><code>--verify=crc32c</code></td><td>체크섬 종류 (md5, sha256 … 도 된다. crc32c 가 빠르다)</td></tr>
<tr><td><code>--verify_interval=4096</code></td><td>4 KiB 마다 머리말 하나 : 틀린 곳을 4 KiB 단위로 짚는다</td></tr>
<tr><td><code>--do_verify=0</code></td><td>쓰기만 하고 바로 확인하지 않는다 (나중에 따로 확인)</td></tr>
<tr><td><code>--verify_only</code></td><td>쓰지 않고, 같은 설정으로 '썼을 내용' 을 읽어서 확인만</td></tr>
<tr><td><code>--verify_fatal=0</code></td><td>틀린 것을 찾아도 멈추지 않고 끝까지</td></tr>
<tr><td><code>--verify_dump=0</code></td><td>틀린 블록을 파일로 쏟아 내지 않는다</td></tr>
</tbody></table></div>

확인할 때의 옵션 (`--rw`, `--bs`, `--size`, `--verify*`) 은 **쓸 때와 같아야** 한다. 그래서 `lab.sh` 는 쓰기와 확인에 같은 줄을 쓴다.

## 12. 랜덤 · 데이터 내용을 정하는 옵션

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>옵션</th>
<th>뜻</th>
<th>실험</th>
</tr></thead><tbody>
<tr><td><code>--norandommap</code></td><td>이미 쓴 LBA 도 다시 고를 수 있다 (진짜 랜덤). 없으면 모든 블록을 한 번씩 다 쓴 뒤에야 반복</td><td>8, 10, 11</td></tr>
<tr><td><code>--randrepeat=0</code></td><td>실행마다 다른 난수 (기본 1 = 매번 같은 순서)</td><td>대부분</td></tr>
<tr><td><code>--random_generator=tausworthe64</code></td><td>큰 장치에서도 고르게 퍼지는 64비트 난수</td><td>8</td></tr>
<tr><td><code>--random_distribution=zipf:1.2</code></td><td>일부 LBA 가 훨씬 자주 (뜨거운 데이터). <code>pareto:0.9</code>, <code>zoned:80/20:20/80</code> (쓰기의 80% 가 공간의 20% 에)</td><td>11</td></tr>
<tr><td><code>--refill_buffers</code></td><td>I/O 마다 새 무작위 내용 (압축 · 중복 제거가 안 되게)</td><td>5</td></tr>
<tr><td><code>--zero_buffers</code></td><td>0 으로만</td><td>5</td></tr>
<tr><td><code>--buffer_compress_percentage=50</code></td><td>절반쯤 압축되는 내용</td><td>5</td></tr>
<tr><td><code>--buffer_pattern=0xdeadbeef</code></td><td>정해진 무늬 반복</td><td>5</td></tr>
<tr><td><code>--fsync=1</code></td><td>쓰기 1번마다 fsync (장치에 FLUSH)</td><td>7</td></tr>
<tr><td><code>--blockalign=4k --offset=512</code></td><td>4 KiB 경계에서 512 B 어긋난 쓰기</td><td>6</td></tr>
</tbody></table></div>

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

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실험</th>
<th>그 실험만의 fio 옵션</th>
</tr></thead><tbody>
<tr><td>3 SLC 캐시</td><td><code>--rw=write --bs=1M --iodepth=8 --size=100%</code></td></tr>
<tr><td>4 TRIM</td><td><code>--rw=randread --bs=4k --iodepth=1</code> 과 <code>32</code>, 앞 절반 / 뒤 절반 (<code>--offset</code>)</td></tr>
<tr><td>5 성능 지도</td><td><code>--rw=randread·read·randwrite·write</code> × <code>--bs=4k…1m</code> × <code>--iodepth=1·4·32</code>, <code>--runtime=20</code></td></tr>
<tr><td>6 쓰기 크기</td><td><code>--bs=512…64k</code>, <code>--blockalign=4k --offset=512</code></td></tr>
<tr><td>7 FLUSH</td><td><code>--fsync=1</code>, (hdparm <code>-W0</code> 와 함께)</td></tr>
<tr><td>8 · 10 · 11 cliff</td><td><code>--rw=randwrite --bs=4k --iodepth=32 --norandommap --io_size=용량×2 --random_distribution=…</code></td></tr>
<tr><td>13 간섭</td><td>job 두 개 : <code>randread</code> QD1 + <code>write</code> 또는 <code>randwrite</code>, <code>--log_max_value=1</code></td></tr>
<tr><td>15 read disturb</td><td><code>--size=1M --rw=randread --iodepth=32 --runtime=시간</code></td></tr>
<tr><td>16 retention</td><td><code>--verify=crc32c --verify_interval=4096</code> 쓰기 → 몇 주 뒤 <code>--verify_only</code></td></tr>
</tbody></table></div>

## 15. 자주 하는 실수

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>실수</th>
<th>증상</th>
<th>고치기</th>
</tr></thead><tbody>
<tr><td><code>--direct=1</code> 을 빠뜨림</td><td>읽기 · 쓰기가 비현실적으로 빠르다</td><td>항상 <code>--direct=1</code></td></tr>
<tr><td>동기 엔진에 iodepth</td><td><code>queue depth will be capped at 1</code></td><td><code>--ioengine=libaio</code> 또는 <code>io_uring</code></td></tr>
<tr><td><code>--size</code> 가 작고 <code>--time_based</code></td><td>같은 작은 영역만 반복 : 캐시 · SLC 에 다 들어간다</td><td>범위를 크게 (<code>100%</code>)</td></tr>
<tr><td>TRIM 된 장치를 읽음</td><td>읽기가 NAND 를 안 거쳐 아주 빠르다 (실험 4)</td><td>먼저 채운다 (<code>lab.sh</code> 의 <code>fill_all</code>)</td></tr>
<tr><td>쓰기를 짧게 한 번만</td><td>SLC 버퍼 안의 속도만 봄</td><td>버퍼보다 많이 쓰거나 (실험 3), 버퍼 속도라고 적는다</td></tr>
<tr><td><code>MiB</code> 와 <code>MB</code> 를 섞음</td><td>5% 차이</td><td>fio 는 둘 다 보여 준다 : 표에는 하나만</td></tr>
<tr><td>평균만 봄</td><td>GC 의 멈춤이 안 보인다</td><td>percentile, 1초 로그 (<code>--log_max_value=1</code>)</td></tr>
</tbody></table></div>

## 16. 더 읽을 것

- `man fio`, 또는 공식 문서 [fio.readthedocs.io](https://fio.readthedocs.io/en/latest/fio_doc.html) : 옵션 전체 (수백 개)
- `/usr/share/doc/fio/examples/` : job 파일 예제 (apt 로 깔면 있다)
- `fio --cmdhelp=옵션이름` : 옵션 하나의 설명. 예 : `fio --cmdhelp=norandommap`

<div class="step-nav"><a href="{{ '/old-ssd-experiments/linux-commands/' | relative_url }}">← SSD 를 다루는 Linux 명령</a><a href="{{ '/old-ssd-experiments/0-setup/' | relative_url }}">0. 준비 →</a></div>
