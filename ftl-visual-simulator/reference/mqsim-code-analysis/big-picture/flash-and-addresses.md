---
layout: default
title: 플래시 구조와 주소 체계
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-and-addresses/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 플래시 구조와 주소 체계


<div style="margin-top: 60px;"></div>

## 1. 플래시는 6단 계층이다

<svg viewBox="0 0 980 360" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="플래시 계층 구조"><defs><marker id="ahier" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="ahiers" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="22" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">기본 설정(ssdconfig.xml)의 물리 구조 — 원시 용량 512 GiB</text><rect x="15" y="60" width="150" height="90" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="90.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Channel</text><text x="90.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">8개</text><line x1="165" y1="105" x2="177" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ahier)"/><rect x="177" y="60" width="150" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="252.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Chip (way)</text><text x="252.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">채널당 4개 = 32개</text><line x1="327" y1="105" x2="339" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ahier)"/><rect x="339" y="60" width="150" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="414.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Die</text><text x="414.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">칩당 2개</text><line x1="489" y1="105" x2="501" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ahier)"/><rect x="501" y="60" width="150" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="576.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Plane</text><text x="576.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">다이당 2개 = 128개</text><line x1="651" y1="105" x2="663" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ahier)"/><rect x="663" y="60" width="150" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="738.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Block</text><text x="738.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">플레인당 2,048개</text><line x1="813" y1="105" x2="825" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ahier)"/><rect x="825" y="60" width="150" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="900.0" y="103.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Page</text><text x="900.0" y="122.0" font-size="11" fill="#4d5656" text-anchor="middle">block 당 256개 · 8KB</text><text x="490" y="190" font-size="12.5" font-weight="700" fill="#7d3c98" text-anchor="middle">&quot;어디에 쓰는가&quot; = 이 6단계를 모두 지정하는 것</text><rect x="15" y="215" width="450" height="125" rx="8" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="240.0" y="260.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">병렬성의 단위</text><text x="240.0" y="279.5" font-size="11" fill="#4d5656" text-anchor="middle">서로 다른 채널 → 버스를 동시에 쓴다</text><text x="240.0" y="294.5" font-size="11" fill="#4d5656" text-anchor="middle">같은 채널의 서로 다른 칩 → 버스는 나눠 쓰고 칩은 동시에 동작</text><text x="240.0" y="309.5" font-size="11" fill="#4d5656" text-anchor="middle">같은 칩의 서로 다른 다이/플레인 → 한 명령으로 묶어 실행 가능</text><rect x="490" y="215" width="475" height="125" rx="8" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="727.5" y="259.75" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">&quot;지우기&quot;의 단위</text><text x="727.5" y="279.25" font-size="11.5" fill="#4d5656" text-anchor="middle">page 는 쓰고 읽는 최소 단위지만</text><text x="727.5" y="294.75" font-size="11.5" fill="#4d5656" text-anchor="middle">지우는 단위는 block 전체 (256 page)</text><text x="727.5" y="310.25" font-size="11.5" fill="#4d5656" text-anchor="middle">→ 그래서 GC 가 필요하다</text></svg>

- 숫자는 `ssdconfig.xml` 의 기본값이다(8 채널 × 4 칩 × 2 다이 × 2 플레인 × 2,048 block × 256 page × 8 KB = 512 GiB).
- 이 프로젝트의 시뮬레이터는 채널·다이·플레인을 1 로 고정하고 칩 수(1/2/4)와 block·page 수만 줄여서 화면에 다 그린다. 같은 로직을 작은 SSD 에 돌리는 것이다.


<div style="margin-top: 60px;"></div>

## 2. 지연 시간

| 동작 | MLC 기본값 | 의미 |
|---|--:|---|
| page read | 75 µs | 가장 빠르다 |
| page program | 750 µs | read 의 10배 — 쓰기가 비싼 이유 |
| block erase | 3.8 ms | program 의 5배 — GC 가 비싼 이유 |

지연은 `Flash_Chip::Get_command_execution_latency()` 가 정한다. MLC 는 page 위치(LSB/MSB)에 따라, TLC 는 3단계로 다르게 **설계되어 있다.** 다만 기본 `ssdconfig.xml` 은 LSB · CSB · MSB 지연을 **같은 값**(read 75 µs, program 750 µs)으로 두고 있어서 기본 설정에서는 차이가 드러나지 않는다. 이 세 숫자의 비율이 FTL 의 모든 정책 선택을 좌우한다 — **지우기를 피하고, 쓰기를 줄이고, 읽기는 아끼지 않는다.**


<div style="margin-top: 60px;"></div>

## 3. 주소는 네 번 모양이 바뀐다

<svg viewBox="0 0 980 300" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="주소 변환 사슬"><defs><marker id="achain" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="achains" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="22" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">주소는 네 번 모양이 바뀐다</text><rect x="20" y="50" width="190" height="90" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="115.0" y="86.5" font-size="15" font-weight="700" fill="#2c3e50" text-anchor="middle">LHA</text><text x="115.0" y="105.5" font-size="11" fill="#4d5656" text-anchor="middle">호스트의 sector 주소</text><text x="115.0" y="120.5" font-size="11" fill="#4d5656" text-anchor="middle">(512B 단위)</text><line x1="210" y1="95" x2="255" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#achain)"/><rect x="255" y="50" width="190" height="90" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="350.0" y="86.5" font-size="15" font-weight="700" fill="#2c3e50" text-anchor="middle">LPA</text><text x="350.0" y="105.5" font-size="11" fill="#4d5656" text-anchor="middle">logical page 주소</text><text x="350.0" y="120.5" font-size="11" fill="#4d5656" text-anchor="middle">= LHA ÷ 16</text><line x1="445" y1="95" x2="490" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#achain)"/><rect x="490" y="50" width="190" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="585.0" y="86.5" font-size="15" font-weight="700" fill="#2c3e50" text-anchor="middle">PPA</text><text x="585.0" y="105.5" font-size="11" fill="#4d5656" text-anchor="middle">physical page 번호</text><text x="585.0" y="120.5" font-size="11" fill="#4d5656" text-anchor="middle">(한 줄짜리 정수)</text><line x1="680" y1="95" x2="725" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#achain)"/><rect x="725" y="50" width="190" height="90" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="820.0" y="86.5" font-size="15" font-weight="700" fill="#2c3e50" text-anchor="middle">물리 주소</text><text x="820.0" y="105.5" font-size="11" fill="#4d5656" text-anchor="middle">channel · chip · die</text><text x="820.0" y="120.5" font-size="11" fill="#4d5656" text-anchor="middle">plane · block · page</text><text x="335" y="87" font-size="11" fill="#566573" text-anchor="middle">쪼개기</text><text x="570" y="87" font-size="11" fill="#566573" text-anchor="middle">매핑 테이블</text><text x="805" y="87" font-size="11" fill="#566573" text-anchor="middle">숫자 나눗셈</text><text x="335" y="152" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">segment_user_request</text><text x="570" y="152" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">AMU: CMT / GMT</text><text x="805" y="152" font-size="10.5" font-style="italic" fill="#566573" text-anchor="middle">Convert_ppa_to_address</text><rect x="20" y="190" width="940" height="90" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="225.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">16 = 8192 B (page) ÷ 512 B (sector)</text><text x="490.0" y="244.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PPA 는 채널 → 칩 → 다이 → 플레인 → block → page 순으로 큰 자리에서 작은 자리로 이어 붙인 번호다.</text><text x="490.0" y="258.5" font-size="10.5" fill="#4d5656" text-anchor="middle">예: PPA = page_no_per_chip × (channel × 칩 수 + chip) + page_no_per_die × die + page_no_per_plane × plane + 256 × block + page</text></svg>

호스트는 **sector 번호(LHA)** 로 말한다. SSD 는 이를 page 크기로 나눠 **LPA** 로 바꾸고, 매핑 테이블로 **PPA** 를 찾고, 그 숫자를 나눠서 **물리 좌표**를 얻는다. FTL 의 핵심은 LPA → PPA 한 단계이고, 나머지는 산수다.


<div style="margin-top: 60px;"></div>

## 4. 어느 plane 에 쓸까 — Plane Allocation Scheme

쓰기에서 FTL 이 가장 먼저 정하는 것은 **plane** 이다. 기본값 `CWDP` 는 LPN 을 채널 → 칩(Way) → 다이 → 플레인 순으로 돌려가며 나눈다(`allocate_plane_for_user_write`, `Address_Mapping_Unit_Page_Level.cpp:987`).

```
channel = LPN % 8
chip    = (LPN / 8) % 4
die     = (LPN / 32) % 2
plane   = (LPN / 64) % 2
```

| LPN | channel | chip | die | plane |
|--:|--:|--:|--:|--:|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 0 | 0 | 0 |
| 2 | 2 | 0 | 0 | 0 |
| 7 | 7 | 0 | 0 | 0 |
| 8 | 0 | 1 | 0 | 0 |
| 9 | 1 | 1 | 0 | 0 |
| 31 | 7 | 3 | 0 | 0 |
| 32 | 0 | 0 | 1 | 0 |
| 64 | 0 | 0 | 0 | 1 |
| 65 | 1 | 0 | 0 | 1 |
| 128 | 0 | 0 | 0 | 0 |
| 256 | 0 | 0 | 0 | 0 |

연속된 LPN 0~7 이 **서로 다른 8개 채널**로 흩어진다. 순차 쓰기가 모든 채널을 동시에 쓰게 하려는 설계다. 이름의 글자 순서(C-W-D-P)가 "연속 주소에서 가장 빨리 바뀌는 차원" 순서이다.

> **plane 이 정해져도 block·page 는 아직 모른다.** 그 plane 의 현재 write frontier block 에서 다음 빈 page 를 받는 것은 블록 매니저의 일이다([7단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/)).


<div style="margin-top: 60px;"></div>

## 관련 문서

- [FTL 의 부품들과 자료구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) · [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/)
