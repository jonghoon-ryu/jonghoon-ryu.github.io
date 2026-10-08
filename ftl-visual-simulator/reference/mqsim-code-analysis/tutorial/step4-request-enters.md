---
layout: default
title: 4. 요청의 탄생 — SSD 입구까지
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step4-request-enters/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 4. 요청의 탄생 — SSD 입구까지

시각 1 ns 에 `IO_Flow_Synthetic` 의 첫 이벤트가 터지는 순간부터 요청이 SSD 안으로 들어가는 과정을 따라간다. 쓰기 전용 + NVMe 인 경우다.

<svg viewBox="0 0 980 330" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="호스트에서 SSD 입구까지"><defs><marker id="anvme" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="anvmes" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">요청 하나가 SSD 입구에 닿을 때까지 (쓰기 기준)</text><rect x="5" y="35" width="150" height="46" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="80.0" y="62.75" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">IO_Flow</text><line x1="80" y1="81" x2="80" y2="315" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/><rect x="185" y="35" width="150" height="46" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="260.0" y="55.5" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">호스트 메모리</text><text x="260.0" y="74.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(SQ/CQ)</text><line x1="260" y1="81" x2="260" y2="315" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/><rect x="365" y="35" width="150" height="46" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="440.0" y="62.75" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">PCIe</text><line x1="440" y1="81" x2="440" y2="315" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/><rect x="545" y="35" width="150" height="46" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="620.0" y="55.5" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Request_Fetch</text><text x="620.0" y="74.0" font-size="10.5" fill="#4d5656" text-anchor="middle">_Unit_NVMe</text><line x1="620" y1="81" x2="620" y2="315" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/><rect x="725" y="35" width="150" height="46" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="800.0" y="55.5" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Input_Stream</text><text x="800.0" y="74.0" font-size="10.5" fill="#4d5656" text-anchor="middle">_Manager_NVMe</text><line x1="800" y1="81" x2="800" y2="315" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/><line x1="80" y1="110" x2="260" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#anvme)"/><text x="170.0" y="104" font-size="10" fill="#2c3e50" text-anchor="middle">① SQ 에 명령 기록, tail++</text><line x1="80" y1="140" x2="440" y2="140" stroke="#7f8c8d" stroke-width="2" marker-end="url(#anvme)"/><text x="260.0" y="134" font-size="10" fill="#2c3e50" text-anchor="middle">② doorbell (Write_to_device)</text><line x1="440" y1="170" x2="620" y2="170" stroke="#7f8c8d" stroke-width="2" marker-end="url(#anvme)"/><text x="530.0" y="164" font-size="10" fill="#2c3e50" text-anchor="middle">③ 전송 지연 후 도착</text><line x1="620" y1="200" x2="440" y2="200" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#anvme)"/><text x="530.0" y="194" font-size="10" fill="#2c3e50" text-anchor="middle">④ SQ 항목 DMA 읽기</text><line x1="440" y1="230" x2="620" y2="230" stroke="#7f8c8d" stroke-width="2" marker-end="url(#anvme)"/><text x="530.0" y="224" font-size="10" fill="#2c3e50" text-anchor="middle">⑤ 명령 내용 도착</text><line x1="620" y1="260" x2="800" y2="260" stroke="#7f8c8d" stroke-width="2" marker-end="url(#anvme)"/><text x="710.0" y="254" font-size="10" fill="#2c3e50" text-anchor="middle">⑥ User_Request 생성</text><text x="800" y="290" font-size="10" fill="#7d3c98" text-anchor="middle">⑦ (쓰기) 데이터도 DMA → page 단위 쪼갬</text></svg>


<div style="margin-top: 60px;"></div>

## 1. 호스트가 요청을 만든다

`IO_Flow_Synthetic::Execute_simulator_event()` (`IO_Flow_Synthetic.cpp:219`). `QUEUE_DEPTH` 방식은 `Average_No_of_Reqs_in_Queue` 개의 요청을 한꺼번에 만든다.

- `Generate_next_request()` (`:74`) 가 주소 · 크기 · 읽기/쓰기를 난수로 정한다.
- `IO_Flow_Base::Submit_io_request()` (`IO_Flow_Base.cpp:405`) 가 NVMe submission queue(호스트 메모리)에 항목을 쓰고 tail 을 올린 다음, `PCIe_Root_Complex::Write_to_device()` 로 **doorbell** 을 울린다 — "새 명령이 있다".

**닫힌 루프다.** `QUEUE_DEPTH` 방식의 flow 는 요청이 **완료될 때마다** 새 요청을 하나 만든다. 그래서 큐 깊이가 일정하게 유지되고, SSD 가 느려지면 요청 생성도 느려진다.

## 2. PCIe 를 건너 SSD 가 명령을 가져간다

doorbell 은 `PCIe_Link` 에서 전송 시간만큼 기다린 뒤(이벤트 예약) `PCIe_Switch` 를 거쳐 호스트 인터페이스에 도착한다.

```
Host_Interface::Consume_pcie_message()                      Host_Interface_Base.h:113
 └ Request_Fetch_Unit_NVMe::Process_pcie_write_message()    Host_Interface_NVMe.cpp:219
     └ Input_Stream_Manager_NVMe::Submission_queue_tail_pointer_update()   :40
         └ (대기 중 요청 < Queue_Fetch_Size 이면) Fetch_next_request()
             └ Send_read_message_to_host(SQE 주소)   "그 명령 내용을 읽어 가겠다" (DMA)
```

디바이스가 **먼저 가져가는 쪽**이다. 호스트가 명령을 밀어 넣는 게 아니라 doorbell 로 알리면 SSD 가 읽어 간다. 한 번에 가져오는 개수는 `Queue_Fetch_Size`(512)가 제한한다.

호스트가 항목을 돌려주면 `Request_Fetch_Unit_NVMe::Process_pcie_read_message()` (`:278`) 가 NVMe 명령(Opcode · LBA · 크기)을 `User_Request` 로 바꾸고 `Handle_new_arrived_request()` (`:69`) 로 넘긴다.

- **읽기**: 곧바로 `segment_user_request()` 와 도착 신호.
- **쓰기**: `Fetch_write_data()` 로 **데이터도 DMA 로 가져온 뒤** `Handle_arrived_write_data()` (`:92`) 에서 같은 일을 한다.


<div style="margin-top: 60px;"></div>

## 3. 요청을 page 단위 transaction 으로 쪼갠다 (`segment_user_request`, `Host_Interface_NVMe.cpp:170`)

<svg viewBox="0 0 980 250" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="요청을 page 단위로 쪼개기"><defs><marker id="aseg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asegs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">segment_user_request: sector 요청 → page 단위 transaction (page = 16 sector)</text><text x="20" y="55" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">예) 12 KB(24 sector) 쓰기, LHA = 8</text><rect x="20.0" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="39.2" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="58.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="77.6" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="96.8" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="116.0" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="135.2" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="154.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="173.6" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="192.8" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="212.0" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="231.2" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="250.4" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="269.6" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="288.8" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="308.0" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="327.2" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="346.4" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="365.6" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="384.8" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="404.0" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="423.2" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="442.4" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="461.6" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="480.8" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="500.0" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="519.2" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="538.4" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="557.6" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="576.8" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="596.0" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="615.2" y="70" width="17" height="30" fill="#fdf2e9" stroke="#ca6f1e"/><rect x="634.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="653.6" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="672.8" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="692.0" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="711.2" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="730.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="749.6" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="768.8" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="788.0" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="807.2" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="826.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="845.6" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="864.8" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="884.0" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="903.2" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="922.4" y="70" width="17" height="30" fill="#f4f6f7" stroke="#bbb"/><rect x="20.0" y="66" width="305.2" height="38" fill="none" stroke="#34495e" stroke-width="2" rx="4"/><text x="173.6" y="120" font-size="11.5" font-weight="700" fill="#34495e" text-anchor="middle">LPA 0</text><rect x="327.2" y="66" width="305.2" height="38" fill="none" stroke="#34495e" stroke-width="2" rx="4"/><text x="480.79999999999995" y="120" font-size="11.5" font-weight="700" fill="#34495e" text-anchor="middle">LPA 1</text><rect x="634.4" y="66" width="305.2" height="38" fill="none" stroke="#34495e" stroke-width="2" rx="4"/><text x="788.0" y="120" font-size="11.5" font-weight="700" fill="#34495e" text-anchor="middle">LPA 2</text><rect x="20" y="150" width="300" height="80" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="170.0" y="180.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">transaction 1</text><text x="170.0" y="199.5" font-size="11" fill="#4d5656" text-anchor="middle">LPA 0 · sector 8~15 (8개)</text><text x="170.0" y="214.5" font-size="11" fill="#4d5656" text-anchor="middle">bitmap = 0xFF00</text><rect x="340" y="150" width="300" height="80" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="180.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">transaction 2</text><text x="490.0" y="199.5" font-size="11" fill="#4d5656" text-anchor="middle">LPA 1 · sector 0~15 (16개)</text><text x="490.0" y="214.5" font-size="11" fill="#4d5656" text-anchor="middle">bitmap = 0xFFFF</text><text x="800" y="185" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LPA = (LHA − stream 시작 주소) ÷ 16</text><text x="800" y="205" font-size="11" fill="#4d5656" text-anchor="middle">시작 sector % 16 부터 page 끝까지가 한 조각</text></svg>

```cpp
LPA_type lpa = internal_lsa / host_interface->sectors_per_page;      // :188
transaction_size = sectors_per_page - (lsa % sectors_per_page);       // 이 page 에 남은 sector 수
access_status_bitmap = temp << (internal_lsa % sectors_per_page);     // 어느 sector 를 쓰는지
```

- 호스트는 **sector(512 B)** 로 말하지만 FTL 은 **page(8 KB = 16 sector)** 단위로 일한다. 이 함수가 그 번역이다.
- 만들어지는 `NVM_Transaction_Flash_RD/WR` 에는 LPA, 그 page 의 **어느 sector 를 건드리는지의 bitmap**(`write_sectors_bitmap`), 소스(`USERIO`)가 담긴다.
- 기본 workload 는 요청 크기가 8 sector(4 KB)라서 **page 의 절반만 쓰는 transaction** 이 흔하다. 이 bitmap 은 7단계에서 "옛 데이터를 읽어서 합쳐야 하는가"(update read)를 판단하는 근거가 된다.

마지막으로 `broadcast_user_request_arrival_signal()` 이 3단계에서 연결한 신호를 방송해 **데이터 캐시**가 요청을 받는다.


<div style="margin-top: 60px;"></div>

## 정리

| 단계 | 호출하는 쪽 | 효과 |
|---|---|---|
| 요청 생성 | `IO_Flow_*` | SQ 에 기록, doorbell |
| 명령 가져오기 | `Request_Fetch_Unit_NVMe` | PCIe 읽기 (DMA) |
| 쪼개기 | `Input_Stream_Manager_NVMe` | 요청 → page 단위 transaction |
| 전달 | 신호 | 캐시가 받는다 |

## 확인해 보기

1. LHA = 20 인 4 KB(8 sector) 쓰기는 transaction 몇 개로 쪼개지나? bitmap 은?
2. `Queue_Fetch_Size` 보다 많은 요청이 SQ 에 쌓이면 나머지는 언제 가져오나? (`Handle_serviced_request`, `:98`)
3. flow 가 둘일 때 같은 LHA 를 쓰면 LPA 가 같을까? (`internal_lsa` 계산을 보자)

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 3. 엔진 시작과 이벤트 루프](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)</span><span>[5. 데이터 캐시 — FTL 의 문턱 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step5-cache/)</span></div>
