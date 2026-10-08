---
layout: default
title: 5. 데이터 캐시 — FTL 의 문턱
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step5-cache/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 5. 데이터 캐시 — FTL 의 문턱

호스트 인터페이스가 방송한 "요청 도착" 신호를 `Data_Cache_Manager` 가 받으면(`handle_user_request_arrived_signal`, `Data_Cache_Manager_Base.cpp:62`, 연결은 `:29`), 요청이 **FTL 에 닿기 직전의 마지막 관문**을 지난다.

<svg viewBox="0 0 980 380" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="캐시의 분기"><defs><marker id="acache" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="acaches" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="15" y="16" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="start">Data_Cache_Manager_Flash_Advanced::process_new_user_request (:187)</text><rect x="15" y="175" width="150" height="60" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="90.0" y="203.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">요청 도착</text><text x="90.0" y="222.0" font-size="11" fill="#4d5656" text-anchor="middle">신호 → 캐시</text><rect x="200" y="165" width="170" height="80" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="285.0" y="203.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">읽기? 쓰기?</text><text x="285.0" y="222.0" font-size="11" fill="#4d5656" text-anchor="middle">+ 캐시 모드</text><rect x="420" y="36" width="250" height="66" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="545.0" y="67.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">읽기 · 캐시 꺼짐</text><text x="545.0" y="86.0" font-size="11" fill="#4d5656" text-anchor="middle">곧바로 FTL (:197)</text><rect x="420" y="120" width="250" height="66" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="545.0" y="143.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">읽기 · 캐시 켜짐</text><text x="545.0" y="162.5" font-size="11" fill="#4d5656" text-anchor="middle">캐시 조회 → 있는 만큼 DRAM 에서</text><text x="545.0" y="177.5" font-size="11" fill="#4d5656" text-anchor="middle">없는 만큼만 FTL (:233)</text><rect x="420" y="204" width="250" height="66" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="545.0" y="235.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 · 캐시 꺼짐</text><text x="545.0" y="254.0" font-size="11" fill="#4d5656" text-anchor="middle">곧바로 FTL (:246)</text><rect x="420" y="288" width="250" height="66" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="545.0" y="319.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 · WRITE_CACHE</text><text x="545.0" y="338.0" font-size="11" fill="#4d5656" text-anchor="middle">write_to_destage_buffer() (:266)</text><line x1="165" y1="205" x2="200" y2="205" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="370" y1="185" x2="420" y2="69" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="370" y1="195" x2="420" y2="153" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="370" y1="215" x2="420" y2="237" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="370" y1="225" x2="420" y2="321" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><rect x="720" y="36" width="245" height="80" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="842.5" y="66.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">★ FTL 입구</text><text x="842.5" y="85.25" font-size="11" fill="#4d5656" text-anchor="middle">Address_Mapping_Unit -&gt;</text><text x="842.5" y="100.25" font-size="11" fill="#4d5656" text-anchor="middle">Translate_lpa_to_ppa_and_dispatch()</text><line x1="670" y1="69" x2="720" y2="69" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="670" y1="237" x2="735" y2="116" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><rect x="720" y="160" width="245" height="200" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="842.5" y="207.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">write_to_destage_buffer</text><text x="842.5" y="225.5" font-size="10.5" fill="#4d5656" text-anchor="middle">① LPA 가 캐시에 있으면 갱신</text><text x="842.5" y="240.0" font-size="10.5" fill="#4d5656" text-anchor="middle">② 없으면 슬롯 확보 (가득 차면</text><text x="842.5" y="254.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   LRU 로 하나 evict → dirty 면</text><text x="842.5" y="269.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   flash 쓰기 transaction 생성)</text><text x="842.5" y="283.5" font-size="10.5" fill="#4d5656" text-anchor="middle">③ DRAM 쓰기 시간 모델링 (이벤트)</text><text x="842.5" y="298.0" font-size="10.5" fill="#4d5656" text-anchor="middle">④ bloom filter 에 처음 보는 LPA 면</text><text x="842.5" y="312.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   &quot;cold&quot; → 곧바로 flash 에도 쓴다</text><text x="842.5" y="327.0" font-size="10.5" fill="#4d5656" text-anchor="middle">⑤ 모인 쓰기 transaction → FTL 입구</text><line x1="670" y1="321" x2="720" y2="290" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/><line x1="842" y1="160" x2="842" y2="116" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acache)"/></svg>


<div style="margin-top: 60px;"></div>

## 1. 캐시 모드에 따라 FTL 로 가는 길이 갈린다

`process_new_user_request()` (`Data_Cache_Manager_Flash_Advanced.cpp:187`) 가 요청 종류와 stream 의 캐시 모드를 보고 나눈다.

- **캐시 꺼짐(`TURNED_OFF`)**: 읽기든 쓰기든 캐시를 보지 않고 곧바로 `Translate_lpa_to_ppa_and_dispatch()` 를 부른다.
- **읽기 + 캐시 켜짐**: 먼저 캐시를 조회한다. 전부 캐시에 있으면 **FTL 을 건드리지 않고** DRAM 읽기 시간만 모델링한다. 없는 부분만 FTL 로 보낸다.
- **쓰기 + `WRITE_CACHE`**: `write_to_destage_buffer()` 로 간다 — 쓰기 데이터를 DRAM 에 먼저 받아 둔다.

> 이 때문에 캐시를 켜면 호스트가 보낸 수백만 개의 쓰기 요청 중 **flash 까지 내려가는 것은 훨씬 적다.** 같은 page 를 계속 덮어쓰면 DRAM 이 흡수하기 때문이다. (이 프로젝트의 시뮬레이터에서 "DRAM 쓰기 캐시" 를 껐다 켜며 GC 횟수를 비교해 보면 바로 보인다.)


<div style="margin-top: 60px;"></div>

## 2. write_to_destage_buffer (`:266`)

transaction 마다 이렇게 처리한다.

1. **이미 캐시에 있는 LPA**: 데이터만 갱신한다. flash 로 안 내려간다.
2. **없는 LPA**: 슬롯이 부족하면 LRU 로 하나 쫓아낸다(`Evict_one_slot_lru`). 쫓겨난 슬롯이 dirty 면 **flash 쓰기 transaction**(소스 `CACHE`)을 만든다. 그다음 새 데이터를 넣는다.
3. 사용자 요청에게는 **DRAM 쓰기 시간**(이벤트)이 지나면 완료를 알린다. flash 쓰기가 끝나기를 기다리지 않는다 — 이것이 write-back 캐시가 응답을 빠르게 하는 방법이다.

### 처음 보는 LPA 는 "차가운 데이터"로 본다 (`:312`)

```cpp
//hot/cold data separation
if (bloom_filter[tr->Stream_id].find(tr->LPA) == bloom_filter[...].end()) {
    per_stream_cache[...]->Change_slot_status_to_writeback(...);  // Eagerly write back cold data
    ...
    writeback_transactions.push_back(tr);
}
```

bloom filter 에 없는 LPA, 즉 **처음 보는 LPA 는 cold 로 간주해 곧바로 flash 로도 쓴다.** 두 번째로 쓰이는 LPA(= 자주 바뀌는 hot 데이터)는 캐시에 머물며 반복 쓰기를 흡수한다. MQSim 에서 실제로 동작하는 hot/cold 구분은 이것뿐이다. block 을 나눠 쓰는 분리는 아니다([원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/)).

이렇게 모인 `writeback_transactions` 가 **FTL 의 입구**로 들어간다 (`:347`).

```cpp
static_cast<FTL*>(nvm_firmware)->Address_Mapping_Unit->Translate_lpa_to_ppa_and_dispatch(writeback_transactions);
```


<div style="margin-top: 60px;"></div>

## 3. 여기서부터가 FTL 이다

`Translate_lpa_to_ppa_and_dispatch()` (`Address_Mapping_Unit_Page_Level.cpp:480`) 가 FTL 의 실제 입구다. 이 함수가 하는 일은 단 세 가지로 요약된다.

1. transaction 마다 `query_cmt()` — **LPA 의 매핑이 있는가?** → [6단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)
2. 물리 주소가 정해진 transaction 을 `TSU->Submit_transaction()` 으로 넘긴다 → [8단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/)
3. `TSU->Schedule()` 로 실행을 시작시킨다

쓰기라면 1번 안에서 **물리 page 를 새로 할당**한다 → [7단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/).

## 확인해 보기

1. 같은 LPA 에 두 번 쓰면 flash 쓰기는 몇 번 일어나나? (bloom filter 와 캐시 갱신 경로를 따라가 보자)
2. 캐시가 꺼져 있고 읽기 요청이면 어느 줄에서 FTL 로 가나?
3. 사용자 요청의 "완료" 는 flash program 이 끝난 뒤인가, DRAM 쓰기가 끝난 뒤인가?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 4. 요청의 탄생 — SSD 입구까지](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step4-request-enters/)</span><span>[6. FTL ① 주소 변환 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)</span></div>
