---
layout: default
title: 용어집
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/glossary/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 용어집

MQSim 코드와 이 문서에 나오는 용어를 모았다. 모르는 말이 나오면 여기로 돌아오면 된다.

<div style="margin-top: 60px;"></div>

## 주소

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **LHA** | Logical Host Address | 호스트가 쓰는 sector(512 B) 단위 주소 |
| **LPA** | Logical Page Address | LHA ÷ (page 당 sector 수) — FTL 이 매핑하는 단위 |
| **PPA** | Physical Page Address | 채널·칩·다이·플레인·block·page 를 이어 붙인 정수 |
| **MVPN / MPPN** | Mapping Virtual/Physical Page Number | translation page 의 번호 / 그 물리 위치 |
| **NO_PPA · NO_LPA** | — | "아직 없음" 을 뜻하는 특수값 |

## 매핑

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **GMT** | Global Mapping Table | 모든 LPA → PPA (flash 에 저장되는 원본) |
| **CMT** | Cached Mapping Table | DRAM 에 둔 매핑 일부 (LRU, DFTL 방식) |
| **GTD** | Global Translation Directory | MVPN → MPPN. translation page 가 flash 어디 있나 |
| **translation page** | — | 매핑 항목 여러 개를 담은 flash page |
| **AMU** | Address Mapping Unit | FTL 의 주소 변환 부품 (Address_Mapping_Unit_*) |

## block 관리

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **write frontier (WF)** | — | 지금 쓰고 있는 block. Data_wf · GC_wf · Translation_wf 가 stream 마다 |
| **free block pool** | — | 지운 block 의 모음. erase 횟수로 정렬되어 dynamic WL 을 만든다 |
| **victim** | — | GC 가 청소하려고 고른 block |
| **valid / invalid page** | — | 최신 데이터 / 옛 복사본 |
| **OP** | Over-provisioning | 호스트에 안 보이게 남겨 두는 여유 공간 비율 |
| **WAF** | Write Amplification Factor | (호스트 쓰기 + GC·WL 이동 쓰기) ÷ 호스트 쓰기 |

## GC · WL

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **GC** | Garbage Collection | valid page 를 옮기고 block 을 지워 공간을 되찾기 |
| **RGA** | Randomized-Greedy (d-choices) | 무작위로 d 개를 뽑아 그중 invalid 가 가장 많은 block |
| **dynamic WL** | — | 새 write block 을 고를 때 덜 닳은 것을 우선 |
| **static WL** | — | 안 바뀌는 cold 데이터를 덜 닳은 block 에서 꺼내 옮기기 |
| **copyback** | — | GC 이동을 컨트롤러 밖으로 내보내지 않고 칩 안에서 |
| **barrier** | — | GC 중인 LPA/block 을 잠가 사용자 요청을 줄 세우는 것 |

## 시스템

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **flow** | — | 호스트의 I/O 발생기 하나 (workload.xml) |
| **stream** | — | flow 에 대응하는 SSD 쪽 단위 (큐·주소 범위·자원·write frontier) |
| **SQ / CQ** | Submission / Completion Queue | NVMe 의 명령 / 완료 큐 (flow 마다 한 쌍) |
| **transaction** | — | page 단위로 쪼갠 flash 작업 하나 (NVM_Transaction_Flash) |
| **User_Request** | — | 호스트 요청 하나 (여러 transaction 으로 쪼개짐) |
| **TSU** | Transaction Scheduling Unit | transaction 을 칩 명령으로 내리는 스케줄러 |
| **PHY / ONFI** | — | 채널 위에서 칩과 대화하는 계층 / 표준 인터페이스 |
| **NVDDR2** | — | ONFI 의 빠른 데이터 전송 모드 |

## 플래시

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **multiplane** | — | 같은 die 의 여러 plane 에 같은 page 번호로 한 명령 |
| **die interleaving** | — | 여러 die 에 명령을 번갈아 보내 동시에 실행 |
| **suspend / resume** | — | 긴 program/erase 를 잠깐 멈추고 read 를 먼저 처리 |
| **LSB / MSB** | — | MLC 한 셀의 두 비트 (page 번호 홀짝으로 지연이 다름) |
| **tR / tPROG / tBERS** | — | read / program / erase 의 연산 시간 |

## 캐시 · 시뮬레이션

| 용어 | 풀어 쓰면 | 뜻 |
|---|---|---|
| **destage** | — | 캐시의 쓰기를 flash 로 내려보내기 |
| **bloom filter** | — | "이 LPA 를 최근에 봤나" 를 근사로 기억하는 자료구조 (hot/cold 판별) |
| **back-pressure** | — | 내려보낼 양이 한도를 넘으면 새 요청을 기다리게 하는 것 |
| **preconditioning** | — | 측정 전에 SSD 를 오래 쓴 상태로 만들기 |
| **steady state** | — | GC 가 정상적으로 돌고 있는 안정 상태 |
| **이산 이벤트** | — | 시각을 "다음 이벤트" 로 점프시키며 진행하는 시뮬레이션 |


<div style="margin-top: 60px;"></div>

## 관련 문서

- [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) · [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/)
