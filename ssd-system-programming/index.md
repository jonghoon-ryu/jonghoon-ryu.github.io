---
layout: default
title: "TBD : system programming for SSD"
permalink: /ssd-system-programming/
---
<style>
.glance { display:grid; grid-template-columns: 9rem 1fr; gap:4px 14px; background:#f4f8f6; border:1px solid #cfe3db; border-left:4px solid #1f6f5c; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.glance b { color:#1f6f5c; }
.warn { background:#fdf2f0; border-left:4px solid #c0392b; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.result { background:#fffbea; border:1px dashed #b7950b; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
table.t { table-layout:fixed !important; width:100% !important; border-collapse:collapse; font-size:0.86rem; margin:1rem 0; }
table.t th { background:#e8f3ef !important; color:#1f3d34 !important; text-align:left; padding:6px 8px; border:1px solid #cfe3db; overflow-wrap:break-word; word-break:break-word; }
table.t td { padding:6px 8px; border:1px solid #e5e8e8; vertical-align:top; overflow-wrap:break-word; word-break:break-word; }
table.t code { font-size:0.82rem; }
@media (max-width: 640px) { .glance { grid-template-columns: 1fr; } }
</style>

# TBD : system programming for SSD

**SSD 테스트 도구를 C 로 직접 쓰면서 시스템 프로그래밍을 배운다.** (2026.10.18 시작, 아직 진행 중 : TBD)

[헌 SSD 로 하는 실험](/old-ssd-experiments/) 은 fio 와 `lab.sh` 같은 남이 만든 도구로 잰다. 이 페이지는 한 걸음 더 들어가, **내 코드가 직접 `open` · `pwrite` · `fsync` · `ioctl` 을 불러 드라이브를 재게** 한다. 그러면서 SSD 안의 일 (SLC 캐시, GC, FLUSH, TRIM) 을 fio 의 평균 뒤에 숨지 않은 모습으로 본다.

<div class="glance">
<b>나</b><span>C / C++ 는 안다. 시스템 프로그래밍은 처음</span>
<b>만들 것</b><span>840 EVO 를 재는 C 프로그램 + 이 컴퓨터에서만 여는 웹 페이지 (파라미터 정하기, 실시간 그래프)</span>
<b>대상 드라이브</b><span>Samsung 840 EVO 120GB (<code>sda</code>) : <a href="/old-ssd-experiments/">헌 SSD 실험</a> 의 그 드라이브</span>
<b>코드</b><span><a href="https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/ssd-system-programming/code"><code>ssd-system-programming/code/</code></a></span>
<b>이 페이지는</b><span>Claude 와 나눈 질문과 답, 그리고 실제로 만든 코드와 출력을 정리한 것</span>
</div>

## 1. 시스템 프로그래밍을 배우면 SSD 테스트에 도움이 되나

**많이 된다.** SSD 테스트에서 어려운 부분은 대부분 시스템 프로그래밍이다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>알아야 할 것</th><th>왜 필요한가</th><th>이어지는 실험</th></tr></thead><tbody>
<tr><td><code>open()</code> 의 <code>O_DIRECT</code> · <code>O_SYNC</code>, <code>fsync()</code> · <code>fdatasync()</code>, 페이지 캐시</td><td>모르면 드라이브가 아니라 RAM 을 잰다. 실험 1 에서 ntfs-3g/FUSE 캐시 때문에 다시 읽기가 RAM 을 읽었던 것이 바로 이것</td><td>1, 7</td></tr>
<tr><td><code>posix_memalign()</code>, 4 KiB 정렬</td><td><code>O_DIRECT</code> 는 정렬된 버퍼 · 길이 · 오프셋만 받는다</td><td>6</td></tr>
<tr><td><code>io_uring</code> · <code>libaio</code></td><td>큐 깊이 (QD) 를 직접 다룬다. fio 가 안에서 쓰는 것</td><td>5</td></tr>
<tr><td><code>ioctl()</code> : <code>BLKDISCARD</code>, <code>SG_IO</code>, <code>NVME_IOCTL_ADMIN_CMD</code></td><td>TRIM, SMART, Secure Erase 처럼 드라이브에 직접 명령을 보낸다 (<code>smartctl</code>, <code>hdparm</code>, <code>nvme-cli</code> 가 하는 일)</td><td>4, 12, 14</td></tr>
<tr><td><code>clock_gettime(CLOCK_MONOTONIC)</code>, CPU 고정, 인터럽트</td><td>지연 시간, 특히 꼬리 지연을 믿을 수 있게</td><td>13</td></tr>
<tr><td>블록 층 : I/O 스케줄러, <code>/sys/block/sda/queue/*</code>, <code>blktrace</code> · <code>bpftrace</code></td><td>OS 가 드라이브에 실제로 무엇을 보냈는지 본다</td><td>전부</td></tr>
<tr><td>쓰기 → FLUSH → 대답</td><td>데이터가 언제 '안전' 한지</td><td>7, 17</td></tr>
</tbody></table></div>

시스템 프로그래밍이 다루지 **않는** 것 : NAND 물리, FTL 의 내부, ECC. 이것은 저장 장치 지식이고, [헌 SSD 실험](/old-ssd-experiments/) 과 [FTL Visual Simulator](/ftl-visual-simulator/) 로 익힌다.

## 2. 코드를 고쳐서 내 SSD 테스트를 할 수 있나

**할 수 있다.** 망가져도 되는 드라이브가 있고, `lab.sh` 와 Python 도구, fio 작업이 모두 읽을 수 있는 스크립트 ([`old-ssd-experiments/scripts/`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/tree/main/old-ssd-experiments/scripts)) 다. 고치는 단계는 셋이다.

1. **실험의 숫자 하나 바꾸기.** `lab.sh` 의 fio 명령에서 하나만 바꾼다 : 블록 크기, 큐 깊이, `randwrite` 와 `write`, span, 압축되는 데이터와 랜덤 데이터. **먼저 결과를 예측하고** 돌린다. 예측이 틀린 곳에서 FTL 에 대해 몰랐던 것을 찾는다
2. **분석 스크립트 고치기.** `smartdiff.py` 가 단계마다 WAF 를 내게, `plot.py` 가 두 실행을 겹쳐 그리게, `readscan.py` 가 지연 분포를 남기게
3. **C 로 작은 테스트 도구 쓰기.** 각각 100–200 줄 :
   - **지연 기록기** : `O_DIRECT` 4 KiB 쓰기의 지연을 하나하나 기록. SLC 캐시가 바닥나는 순간과 GC 의 멈춤이 평균 없이 바로 보인다 (→ 5 절의 step 1)
   - **FLUSH 시계** : 쓰기와 `fdatasync()` 의 시간을 따로 (실험 7)
   - **TRIM 탐침** : 무늬를 쓰고, 일부를 TRIM 하고, 다시 읽기 (실험 4)
   - **작은 fio** : `io_uring` 으로 큐 깊이를 직접 정하고 fio 와 비교

## 3. 얼마나 걸리나

C/C++ 를 알고 시스템 프로그래밍은 처음, 일주일에 5–10 시간이라면 대략 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>단계</th><th>익히는 것</th><th>시간</th></tr></thead><tbody>
<tr><td>1. 첫 쓸모 있는 도구 : <code>O_DIRECT</code> 지연 기록기</td><td><code>open</code> / <code>pread</code> / <code>pwrite</code>, 파일 디스크립터, <code>O_DIRECT</code> 정렬, <code>posix_memalign</code>, <code>clock_gettime</code>, <code>fsync</code></td><td><strong>2–3 주</strong></td></tr>
<tr><td>2. 믿을 수 있는 측정</td><td>페이지 캐시, 처음 숫자가 왜 틀렸나, CPU 고정, 워밍업, <code>/sys/block/*/queue</code></td><td>+2 주</td></tr>
<tr><td>3. 진짜 큐 깊이</td><td><code>io_uring</code> (또는 <code>libaio</code>), 제출과 완료, QD 가 처리량을 바꾸는 이유</td><td>+3–4 주</td></tr>
<tr><td>4. 드라이브와 직접 말하기</td><td><code>ioctl</code>, <code>BLKDISCARD</code> 로 TRIM, <code>SG_IO</code> 로 SMART · ATA 명령</td><td>+3–4 주</td></tr>
</tbody></table></div>

**약 한 달** 이면 fio 의 요약이 숨기는 것 (SLC 캐시 바닥, GC 멈춤) 을 보여 주는 작은 도구가, **약 석 달** 이면 실험 대부분을 내 코드로 하는 도구가 된다.

- **생각보다 빠른 이유** : 새 언어가 아니라 시스템 호출 스무 개 남짓과 그 함정을 배우는 것. fio 를 다시 만들 필요 없이 한 가지만 잘하면 되고 (fio 는 숫자를 맞춰 보는 기준), 무엇을 잴지는 이미 실험 페이지에 있다
- **느려지는 곳** : 이상하게 좋은 숫자 (드라이브가 아니라 캐시를 잼), `O_DIRECT` 의 정렬 오류 (`EINVAL`), `io_uring` 의 배우는 곡선. 각각 며칠씩 막히는 것이 보통이고, 거기서 가장 많이 배운다
- **읽을거리** : *The Linux Programming Interface* (Kerrisk) 4–5 장 (파일 I/O), 13 장 (버퍼링, `O_DIRECT`). 큐 깊이 단계에서는 `io_uring` man 페이지와 liburing 예제

## 4. 웹으로 하려면 : 두 가지 길

[FTL Visual Simulator](/ftl-visual-simulator/) 처럼 웹에서 하고 싶었다. 그런데 FTL 시뮬레이터는 MQSim 을 WASM 으로 컴파일해서 **시뮬레이션된 SSD 가 페이지 안에 있기 때문에** 브라우저에서 돈다. 시스템 프로그래밍에는 넘을 수 없는 벽이 있다 : **웹 페이지는 진짜 디스크에 닿을 수 없다.** 브라우저의 샌드박스가 `open("/dev/sda", O_DIRECT)`, `fsync`, `ioctl` 을 모두 막는다. 그래서 '웹으로' 는 두 가지 다른 프로젝트가 된다.

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th></th><th>A. 브라우저 안의 시뮬레이터</th><th>B. 진짜 테스트 도구 + 웹 화면</th></tr></thead><tbody>
<tr><td>내 코드가 말하는 상대</td><td><strong>가짜 SSD</strong> : C 코드를 WASM 으로 컴파일, <em>흉내 낸</em> <code>open</code> / <code>pwrite</code> / <code>fsync</code> 를 부른다</td><td><strong>진짜 840 EVO</strong> : 이 PC 에서 도는 C 프로그램</td></tr>
<tr><td>보이는 것</td><td>호출 하나가 층을 따라 내려가는 애니메이션 (페이지 캐시 → 블록 층 → 드라이브 → SLC 캐시 · GC)</td><td>이 PC 에서만 여는 페이지 (<code>localhost</code>) : 파라미터를 정하고, 시작을 누르고, 실시간 지연 · 처리량 그래프</td></tr>
<tr><td>숫자</td><td>모델에서 (MQSim WASM 을 '드라이브' 로 쓸 수도)</td><td><strong>실제 측정값</strong></td></tr>
<tr><td>공개</td><td>GitHub Pages 에 그대로, 누구나 연다</td><td>조종 화면은 이 PC 에서만. 결과와 그래프를 블로그에 올린다</td></tr>
<tr><td>배우는 것</td><td>시스템 호출이 <em>무엇을 하는지</em>, 그림으로</td><td>시스템 호출을 <em>직접 쓰는 것</em>, 그리고 진짜 SSD 의 행동</td></tr>
<tr><td>비유</td><td>비행 시뮬레이터 : 이해에는 좋지만 땅을 떠나지 않는다</td><td>진짜 비행기 : 진짜 숫자, 진짜 놀람</td></tr>
</tbody></table></div>

**B 를 골랐다.** 목표가 '시스템 프로그래밍을 배워서 SSD 를 더 깊이 이해하기' 이고, 내가 직접 시스템 호출을 쓰고 진짜 드라이브의 SLC 캐시와 GC 를 보는 것은 B 뿐이다. 이미 있는 것 (`lab.sh` 의 안전 확인, 가짜 장치 시험 모드, 실험 목록) 위에 쌓을 수도 있다. A 는 FTL 시뮬레이터 옆에 둘 좋은 교재라, B 의 C 코드를 다시 써서 나중에 할 수 있다.

## 5. 계획 : 여섯 단계

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>단계</th><th>하는 일</th><th>새로 배우는 것</th><th>상태</th></tr></thead><tbody>
<tr><td>1</td><td><code>O_DIRECT</code> 쓰기 하나하나의 시간 재기 (CSV)</td><td><code>open</code>, <code>O_DIRECT</code>, <code>posix_memalign</code>, <code>pwrite</code>, <code>clock_gettime</code>, 페이지 캐시</td><td><strong>끝</strong> (6 절)</td></tr>
<tr><td>2</td><td>구간마다 통계 (MB/s, IOPS, p50 · p99 · 최대 지연) 를 JSON 한 줄씩. 순차 · 랜덤, 읽기 · 쓰기</td><td>통계, 난수 오프셋, 출력 형식</td><td>다음</td></tr>
<tr><td>3</td><td>진짜 드라이브를 위한 안전 확인 : 블록 장치인가, 크기, 시리얼, 마운트되어 있나, 시스템 디스크인가, 확인 입력</td><td><code>fstat</code>, <code>ioctl(BLKGETSIZE64)</code>, <code>/sys</code> · <code>/proc/mounts</code> 읽기</td><td>아직</td></tr>
<tr><td>4</td><td>이 PC 에서만 여는 웹 페이지 : 파라미터 정하기, 시작 · 멈춤, 실시간 그래프</td><td>프로세스 띄우기와 파이프, 작은 HTTP 서버, 스트리밍 (SSE)</td><td>아직</td></tr>
<tr><td>5</td><td>큐 깊이 : 여러 I/O 를 동시에</td><td><code>io_uring</code> (liburing : <code>sudo apt install liburing-dev</code>)</td><td>아직</td></tr>
<tr><td>6</td><td>FLUSH 시간, TRIM</td><td><code>fdatasync</code>, <code>ioctl(BLKDISCARD)</code></td><td>아직</td></tr>
</tbody></table></div>

<div class="warn" markdown="1">
**안전 : 먼저 가짜 장치로.** `lab.sh` 에는 시험 모드 `LAB_TESTDEV` 가 있다 : 보통 파일을 SSD 대신 쓰고, 진짜 디스크에서만 뜻 있는 확인 (시리얼, `sudo`, SMART) 은 건너뛰고, TRIM 대신 파일에 구멍을 뚫는다 (`fallocate --punch-hole`). 이 도구도 같은 순서로 한다 : **새 코드는 먼저 파일에, 동작하면 진짜 드라이브에.** 진짜 `/dev/sda` 에 쓰는 것은 3 단계의 안전 확인이 들어간 뒤, 직접 한다.

**한계.** 파일은 SSD 가 아니다. 페이지 캐시, 파일 시스템, 그 밑의 시스템 디스크가 끼어든다. 가짜 장치는 **코드가 맞는지** 확인하는 데에만 쓰고, 거기서 나온 **숫자는 840 EVO 의 숫자가 아니다.**
</div>

## 6. Step 1 : O_DIRECT 쓰기 하나하나의 시간 재기

코드 : [`code/step1.c`](https://github.com/jonghoon-ryu/jonghoon-ryu.github.io/blob/main/ssd-system-programming/code/step1.c) (주석 포함 약 90 줄)

### 6.1 하는 일

4 KiB 블록을 0, 1, 2 … 번째 자리에 차례로 쓰고, `pwrite()` 하나하나의 시간을 재서 CSV (`i,offset,lat_us`) 로 낸다. 세 번째 인자로 `buffered` 를 주면 `O_DIRECT` 없이 보통 쓰기로 한다 : 둘을 비교하는 것이 이 단계의 요점이다.

### 6.2 코드의 네 부분

**① 열기 : `O_DIRECT`**

```c
#define _GNU_SOURCE             // O_DIRECT 는 Linux 확장 : 이것이 있어야 <fcntl.h> 가 정의한다
int flags = O_WRONLY | (buffered ? 0 : O_DIRECT);
int fd = open(path, flags);
if (fd < 0) { perror("open"); return 1; }
```

`O_DIRECT` 는 커널에게 '내 버퍼와 장치 사이에서 바로 옮기고, 페이지 캐시에 복사하지 마' 라고 한다. 없으면 `write()` 는 **RAM 에 복사만 하고 바로 돌아온다.** 디스크에는 나중에 커널이 쓴다. 그러면 재는 것은 RAM 의 속도다.
`perror()` 는 실패 이유 (`errno`) 를 사람이 읽는 말로 찍는다 : 시스템 호출은 실패하면 -1 을 돌려주고 이유를 `errno` 에 둔다.

**② 정렬된 버퍼 : `posix_memalign`**

```c
void *buf;
int err = posix_memalign(&buf, 4096, bs);
```

`O_DIRECT` 는 **버퍼 주소, 길이, 파일 오프셋** 이 모두 장치의 논리 블록 크기에 맞아야 한다 (4096 이면 언제나 안전). `malloc()` 은 16 바이트 정렬만 보장하므로 `posix_memalign()` 을 쓴다. 이것은 실패하면 `errno` 대신 오류 번호를 **돌려준다** (그래서 `perror` 가 아니라 `strerror(err)`).

**③ 버퍼 채우기 : 0 이 아니라 랜덤**

```c
uint64_t x = 88172645463325252ULL;           // xorshift : 빠르고 간단한 의사 난수
for (size_t i = 0; i < bs / 8; i++) {
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    ((uint64_t *)buf)[i] = x;
}
```

어떤 컨트롤러는 0 으로만 된 데이터를 압축하거나 쓰지 않고 넘긴다. 그러면 NAND 가 아니라 그 지름길을 재게 된다.

**④ 쓰고, 재기 : `pwrite` + `clock_gettime`**

```c
static double now_us(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);      // 절대 뒤로 가지 않는 시계
    return t.tv_sec * 1e6 + t.tv_nsec / 1e3;
}
...
off_t off = (off_t)i * bs;
double t0 = now_us();
ssize_t n = pwrite(fd, buf, bs, off);
double t1 = now_us();
if (n != (ssize_t)bs) { ... }                // -1 = 오류, 작으면 = 덜 씀 (short write)
printf("%ld,%lld,%.1f\n", i, (long long)off, t1 - t0);
```

- `pwrite()` 는 **오프셋을 직접 주는** `write()` 다. `lseek()` 이 필요 없고, 나중에 여러 I/O 를 동시에 낼 때 공유된 파일 위치가 꼬이지 않는다
- `CLOCK_MONOTONIC` 은 NTP 가 벽시계를 옮겨도 뛰지 않는다. 그래서 두 값의 차이가 진짜 걸린 시간이다 (`gettimeofday()` 는 그렇지 않다)
- 돌려준 바이트 수를 **늘 확인한다.** 시스템 호출은 조용히 덜 쓸 수 있다

### 6.3 실행

```sh
cd ssd-system-programming/code
gcc -O2 -Wall -o step1 step1.c
truncate -s 1G /tmp/fake-ssd.img                    # 가짜 '드라이브' : 1 GB 짜리 빈 파일
./step1 /tmp/fake-ssd.img 2000 > direct.csv           # O_DIRECT
./step1 /tmp/fake-ssd.img 2000 buffered > buf.csv     # 보통 쓰기 (페이지 캐시로)
head -4 direct.csv
```

실제 출력 (2026.10.18, 이 컴퓨터) :

```
i,offset,lat_us
0,0,103.7
1,4096,40.9
2,8192,34.1
```

2,000 번 쓰기를 정리하면 :

<div style="overflow-x:auto;"><table class="t">
<thead><tr><th>모드</th><th>중앙값</th><th>p99</th><th>최대</th><th>2,000 번 합</th></tr></thead><tbody>
<tr><td><code>O_DIRECT</code></td><td>30.8 µs</td><td>41.2 µs</td><td>115.7 µs</td><td>61.4 ms</td></tr>
<tr><td><code>buffered</code></td><td><strong>5.3 µs</strong></td><td>13.6 µs</td><td>66.1 µs</td><td>12.3 ms</td></tr>
</tbody></table></div>

### 6.4 결과 읽기

<div class="result" markdown="1">
- **보통 쓰기가 약 6 배 빠르다 : 드라이브가 빨라서가 아니라 드라이브에 가지 않아서다.** `buffered` 의 5.3 µs 는 4 KiB 를 RAM 에 복사하는 시간이다. 이것이 '이상하게 좋은 숫자' 의 정체이고, SSD 를 잴 때 `O_DIRECT` 가 필요한 이유다
- **`O_DIRECT` 의 약 31 µs 도 840 EVO 의 숫자가 아니다.** 가짜 장치는 시스템 디스크 (990 EVO, NVMe) 의 ext4 위에 있는 파일이다. 재는 것은 ext4 + 990 EVO 의 쓰기 캐시다. 840 EVO 의 숫자는 3 단계 뒤 `/dev/sda` 에서 나온다
- **첫 쓰기 (103.7 µs) 가 가장 느리다.** 처음 닿는 자리라 파일 시스템이 블록을 잡고, 캐시 · TLB 가 비어 있다. 측정에서 처음 몇 개를 버리는 '워밍업' 이 필요한 이유 (2 단계)
</div>

일부러 틀려 보기 : 버퍼를 `malloc(bs + 1)` 로 잡고 주소를 1 바이트 밀면 (정렬이 깨지면) :

```
i,offset,lat_us
pwrite: Invalid argument
```

`EINVAL` : `O_DIRECT` 의 정렬 규칙을 어긴 것이다. 처음 `O_DIRECT` 를 쓸 때 가장 자주 만나는 오류다. 오프셋을 4096 의 배수가 아닌 곳 (예 : `i * bs + 512`) 으로 해도 같다.

### 6.5 해 볼 것

1. `count` 를 2,000 에서 200,000 (약 800 MB) 으로 늘려 `buffered` 를 다시 돌린다. 지연이 어느 순간 크게 튀나? (힌트 : 커널이 쌓인 더러운 페이지를 디스크로 내보내기 시작하면 `write()` 가 기다리게 된다. `/proc/sys/vm/dirty_ratio`)
2. `buffered` 로 쓴 직후 `sync` 명령이 얼마나 걸리는지 `time sync` 로 잰다. 그 시간은 어디서 온 것인가?
3. 블록 크기 `bs` 를 512, 4096, 65536, 1 MiB 로 바꿔 본다. 512 에서는 `EINVAL` 이 나나? (장치의 논리 블록 크기 : `cat /sys/block/nvme0n1/queue/logical_block_size`)
4. `head` 대신 그래프로 : CSV 를 `plot.py` 나 스프레드시트에 넣어 `i` 에 대한 `lat_us` 를 그린다. 이 그래프를 실시간으로 보는 것이 4 단계의 웹 페이지다

## 7. 다음 : step 2

한 줄씩 2,000 개를 찍는 것은 진짜 드라이브에서 수백만 번 쓰면 감당이 안 된다. 2 단계에서는 **구간 (예 : 0.5 초) 마다** MB/s, IOPS, p50 · p99 · 최대 지연을 계산해 JSON 한 줄로 낸다. 이 형식이 그대로 4 단계 웹 페이지의 실시간 그래프로 들어간다. 랜덤 오프셋 (FTL 에게 가장 힘든 쓰기) 과 읽기도 더한다.
