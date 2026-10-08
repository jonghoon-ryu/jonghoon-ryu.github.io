---
layout: default
title: 1. 실행 명령과 main()
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step1-run-and-main/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 1. 실행 명령과 main()

이 튜토리얼은 터미널에 한 줄을 치는 순간부터 시작한다. FTL 이 일을 시작하기까지 **어떤 함수가 어떤 순서로 불리는지**를 한 단계씩 따라간다. 파일 이름과 줄 번호는 모두 MQSim 원본 `51f0f2d` 커밋 기준이다.


<div style="margin-top: 60px;"></div>

## 1. 실행 명령

```bash
git clone https://github.com/CMU-SAFARI/MQSim && cd MQSim
make
./MQSim -i ssdconfig.xml -w workload.xml
```

<svg viewBox="0 0 980 240" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="입력 파일과 출력 파일"><defs><marker id="aio" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aios" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><rect x="20" y="30" width="200" height="70" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="120.0" y="55.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">ssdconfig.xml</text><text x="120.0" y="74.5" font-size="11" fill="#4d5656" text-anchor="middle">SSD 의 사양</text><text x="120.0" y="89.5" font-size="11" fill="#4d5656" text-anchor="middle">(채널·칩·캐시·GC 정책 …)</text><rect x="20" y="130" width="200" height="70" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="120.0" y="155.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">workload.xml</text><text x="120.0" y="174.5" font-size="11" fill="#4d5656" text-anchor="middle">호스트가 가할 부하</text><text x="120.0" y="189.5" font-size="11" fill="#4d5656" text-anchor="middle">(시나리오 · IO flow)</text><rect x="340" y="60" width="300" height="120" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="490.0" y="96.5" font-size="15" font-weight="700" fill="#2c3e50" text-anchor="middle">./MQSim</text><text x="490.0" y="115.5" font-size="11" fill="#4d5656" text-anchor="middle">-i ssdconfig.xml</text><text x="490.0" y="130.5" font-size="11" fill="#4d5656" text-anchor="middle">-w workload.xml</text><text x="490.0" y="145.5" font-size="11" fill="#4d5656" text-anchor="middle"></text><text x="490.0" y="160.5" font-size="11" fill="#4d5656" text-anchor="middle">시나리오마다 시뮬레이션 1회</text><rect x="760" y="30" width="200" height="70" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="860.0" y="62.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">workload_scenario_1.xml</text><text x="860.0" y="81.5" font-size="11" fill="#4d5656" text-anchor="middle">시나리오 1 결과</text><rect x="760" y="130" width="200" height="70" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="860.0" y="162.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">workload_scenario_2.xml …</text><text x="860.0" y="181.5" font-size="11" fill="#4d5656" text-anchor="middle">시나리오 N 결과 (입력 아님!)</text><line x1="220" y1="65" x2="340" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aio)"/><line x1="220" y1="165" x2="340" y2="140" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aio)"/><line x1="640" y1="105" x2="760" y2="65" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aio)"/><line x1="640" y1="140" x2="760" y2="165" stroke="#7f8c8d" stroke-width="2" marker-end="url(#aio)"/></svg>

인자는 정확히 두 쌍이다. SSD 자체의 사양은 `ssdconfig.xml` 에, 그 SSD 에 가할 **부하만** `workload.xml` 에 있다. 결과는 같은 폴더에 `workload_scenario_N.xml` 로 써진다 — 이름이 비슷하지만 입력이 아니라 **출력**이다.


<div style="margin-top: 60px;"></div>

## 2. main() 의 뼈대

```
main()                                         main.cpp:260
 ├─ argc != 5 이면 도움말 출력 후 종료           :263
 ├─ command_line_args()                          :269   -i / -w 뒤의 경로를 꺼냄
 ├─ read_configuration_parameters()              :272   ssdconfig.xml → exec_params
 ├─ read_workload_definitions()                  :273   workload.xml → 시나리오 목록
 └─ for 각 시나리오:                              :276
     ├─ Simulator->Reset()                        :284
     ├─ SSD_Device ssd(...)                       :291   ← 2단계
     ├─ Host_System host(...)                     :293   ← 2단계
     ├─ host.Attach_ssd_device(&ssd)              :294
     ├─ Simulator->Start_simulation()             :296   ← 3단계
     └─ collect_results(...)                      :306   ← 11단계
```

**이 시점까지 FTL 은 존재하지 않는다.** 아직은 설정 파일을 읽는 일뿐이고, 시뮬레이터 객체는 하나도 만들어지지 않았다.


<div style="margin-top: 60px;"></div>

## 3. 설정 읽기 (`read_configuration_parameters`, main.cpp:38)

1. `Execution_Parameter_Set` 을 코드에 박힌 기본값으로 만든다.
2. 파일이 **없으면** 기본값을 그 경로에 XML 로 써 놓고 계속한다.
3. 파일이 있으면 rapidxml 로 파싱해 `XML_deserialize()` 로 기본값을 덮어쓴다.

결과인 `exec_params` 에는 호스트 설정과 SSD 설정이 들어 있다. 여기서 읽힌 값들이 이후 모든 클래스의 생성자 인자가 된다.

## 4. workload 읽기 (`read_workload_definitions`, main.cpp:88)

`workload.xml` 은 두 단계 구조다.

```
<MQSim_IO_Scenarios>
  <IO_Scenario>                          ← 시나리오 하나 = 시뮬레이션 한 번
    <IO_Flow_Parameter_Set_Synthetic>    ← flow 하나 = 호스트의 I/O 발생기 하나
    <IO_Flow_Parameter_Set_Synthetic> …
  </IO_Scenario>
  <IO_Scenario> … </IO_Scenario>
</MQSim_IO_Scenarios>
```

- 시나리오끼리는 서로 독립이다. 매번 처음부터 새로 시뮬레이션한다.
- flow 는 한 시나리오 안에서 **동시에** 실행된다. flow 마다 NVMe 큐 한 쌍이 생기고 SSD 쪽에서는 stream 하나가 된다.
- flow 종류는 `Synthetic`(파라미터로 만드는 가짜 부하)과 `Trace_Based`(실제 trace 재생)이다.

원본의 샘플 `workload.xml` 은 시나리오가 3개다.

| | 시나리오 1 | 시나리오 2 | 시나리오 3 |
|---|---|---|---|
| flow | Synthetic ×2 | Synthetic ×2 | Trace_Based ×1 |
| 읽기 비율 | 0% (전부 쓰기) | 100% (전부 읽기) | trace 에 따름 |
| 큐 깊이 | 16 / 2 | 16 / 16 | trace 의 도착 시각 |
| 우선순위 | HIGH / HIGH | URGENT / HIGH | HIGH |

시나리오 1 은 큐 깊이 16 대 2 의 두 쓰기 flow 가 같은 SSD 를 나눠 쓸 때를, 시나리오 2 는 우선순위가 다른 두 읽기 flow 의 응답 시간을, 시나리오 3 은 실제 trace(tpcc)를 본다. 파일에 의도가 적혀 있지는 않아서 이 해석에는 추정이 섞여 있다.

<div class="check">
<b>읽을 때 주의</b><br>
• <code>Initial_Occupancy_Percentage</code> 는 preconditioning 이 켜졌을 때만 쓰인다. 샘플 <code>ssdconfig.xml</code> 은 <code>Enabled_Preconditioning</code> = false 라서 <b>세 시나리오 모두 빈 SSD 에서 시작</b>한다.<br>
• <code>&lt;Intensity&gt;</code> 태그는 파서가 읽지 않는다. 읽는 것은 <code>Bandwidth</code> 뿐이다.
</div>


<div style="margin-top: 60px;"></div>

## 5. 시나리오 루프의 첫 줄 — Reset

```cpp
Simulator->Reset();   // main.cpp:284
```

`Reset()` 은 이벤트 리스트와 객체 목록을 비우고 시각을 0 으로 되돌린다(`Engine.cpp:16`). 시나리오끼리 아무것도 공유하지 않게 하는 장치다. `Simulator` 는 `Engine` 의 싱글턴을 가리키는 매크로여서, 뒤에서 나오는 모든 `Simulator->AddObject()` 와 `Register_sim_event()` 가 **같은 엔진 하나**로 들어간다.


<div style="margin-top: 60px;"></div>

## 확인해 보기

1. `./MQSim -i ssdconfig.xml` 처럼 인자를 하나 빼면 무슨 일이 일어나나? (`main.cpp:263`)
2. `ssdconfig.xml` 을 지우고 실행하면? (`main.cpp:38` 이후)
3. 시나리오가 3개면 `SSD_Device` 는 몇 번 만들어지나?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 튜토리얼 목차](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)</span><span>[2. SSD 와 호스트 만들기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step2-build-ssd/)</span></div>
