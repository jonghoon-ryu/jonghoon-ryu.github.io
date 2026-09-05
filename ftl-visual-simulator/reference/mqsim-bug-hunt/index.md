---
layout: default
title: MQSim 버그 헌트
permalink: /ftl-visual-simulator/reference/mqsim-bug-hunt/
---
<style>
table.plan-calendar {
  width: 100% !important;
  table-layout: fixed !important;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: break-word;
  word-break: break-word;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
</style>

# MQSim 버그 헌트

Session 4 에서 WASM 바인딩( `init`/`step`/`run`/`configure` )을 검증하다가, **MQSim 을 WASM 으로 컴파일한 결과가 네이티브 빌드와 다른 시뮬레이션 결과를 낸다**는 걸 발견했다. "MQSim 원본을 그대로 WASM 으로 컴파일해서 쓴다"는 이 프로젝트의 핵심 전제( [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) 참고 )가 흔들리는 심각한 문제라서, 하루 동안 깊게 파고들어 실제 원인을 찾아 고쳤다. 이 문서는 그 조사 전체 기록이다.

**결론만 먼저 말하면** : 원인은 MQSim 원본 코드 한 곳이 C++ 표준이 보장하지 않는 동작( `std::multimap::find()` 가 중복 키 중 "첫 번째" 항목을 반환한다는 가정 )에 의존하고 있었기 때문이었다. 네이티브 빌드가 쓰는 표준 라이브러리( libstdc++ )에서는 우연히 항상 그렇게 동작했지만, WASM 빌드가 쓰는 표준 라이브러리( libc++ )에서는 아니었다 — 그래서 지금까지 아무도 눈치채지 못한 채 숨어 있던, MQSim 원본 자체의 이식성 버그였다.

<div style="margin-top: 60px;"></div>

## 어쩌다 발견했나

WASM 바인딩을 만든 뒤, 시나리오를 실행해서 네이티브 빌드와 결과를 직접 비교( 이전까지는 WASM 실행 결과끼리만 비교했지, 진짜 네이티브 결과와 대조한 적이 없었다 )해봤더니:

- **시나리오 1( synthetic )** : 네이티브는 요청 330,160 개를 생성해서 전부 처리, WASM 은 140,103 개만 생성되고 그마저 다 처리되지도 않음
- **시나리오 3( trace 기반, tpcc-small.trace 재생 )** : 생성된 요청 수는 양쪽 다 6,999 개로 동일( trace 재생이라 결정론적 ). 하지만 네이티브는 6,999 개 전부 처리, **WASM 은 2,418 개만 처리하고 이벤트 큐가 완전히 비어서 시뮬레이션이 끝나버림**

시나리오 3 은 랜덤성이 전혀 없는 순수 재현 케이스라 디버깅 대상으로 훨씬 깨끗했다 — 이후 조사는 전부 이 시나리오로 진행했다.

<div style="margin-top: 60px;"></div>

## 발견한 버그 4개 요약

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>#</th><th>위치</th><th>문제</th><th>WASM 결과에 미친 영향</th></tr>
<tr><td>1</td><td><code>utils/CMRRandomGenerator.h</code></td><td>정수 오버플로우(UB)</td><td>일부 영향(정확한 원인은 아님)</td></tr>
<tr><td>2</td><td>6개 클래스 소멸자</td><td>non-virtual 소멸자로 다형적 delete(UB)</td><td>없음(정리 시점에만 실행됨)</td></tr>
<tr><td>3</td><td><code>host/IO_Flow_Synthetic.h</code></td><td>미초기화 포인터</td><td>2번 고치자 드러난 크래시</td></tr>
<tr><td>4</td><td><code>ssd/Address_Mapping_Unit_Page_Level.cpp</code></td><td><code>multimap::find()</code> 가정 오류</td><td><b>근본 원인</b> — 이거였음</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 버그 1 — RNG 의 정수 오버플로우 (undefined behavior)

**위치** : `utils/CMRRandomGenerator.h` 의 `mm_mul`/`mv_mul` 함수( 행렬 곱셈 후 modulo 연산 )

MQSim 전역에서 쓰이는 범용 난수 생성기( `Utils::RandomGenerator` → `Utils::CMRRandomGenerator` )가 `int64_t` 로 곱셈 후 modulo 를 계산하는데, 곱해지는 두 값이 MRG32k3a 방식의 modulus( `m1=4294967087`, `m2=4294944443`, 둘 다 2^32 근처 )에 가까운 값이라 곱하면 최대 약 1.84×10^19 까지 커진다 — 이건 **signed 64-bit 정수의 최댓값( 약 9.22×10^18 )을 넘는다.**

네이티브 빌드를 UBSan( Undefined Behavior Sanitizer )으로 빌드해서 실행하자 바로 이 오류가 잡혔다:
```
CMRRandomGenerator.h:109:27: runtime error: signed integer overflow:
4294156359 * 4294156359 cannot be represented in type 'long int'
```

signed overflow 는 undefined behavior 라서, 실제 결과값이 컴파일러·플랫폼마다 달라질 수 있다 — 정확히 이번 사례처럼.

**수정** : 곱셈·누적 계산을 `int64_t` 대신 `uint64_t` 로 하도록 변경. `(m-1)^2` 은 unsigned 64-bit 범위 안에 정확히 들어가기 때문에( 약 1.844×10^19 < UINT64_MAX 약 1.8447×10^19 ), 이건 우회가 아니라 **수학적으로 정확한 계산**이 되는 것 — 그냥 UB 만 없앤 것이다.

**검증된 영향** : 이 수정 하나만으로 WASM 의 synthetic 시나리오 숫자가 바뀌긴 했지만( 140,103 → 150,804 ), 네이티브의 329,898 과는 여전히 거리가 멀었다. 게다가 **이 RNG 는 시나리오 3( trace 기반 )에서는 아예 호출되지 않는다는 걸 직접 계측으로 확인**했다 — `NextDouble()` 안에 호출 횟수를 세는 코드를 넣어봤더니 시나리오 3 실행 내내 0번 호출됐다. 즉 이 버그는 실재하고 고칠 가치는 있었지만, 시나리오 3 의 문제와는 무관했다.

<div style="margin-top: 60px;"></div>

## 버그 2 — 6개 클래스의 소멸자가 virtual 이 아님 (undefined behavior)

파생 클래스 객체를 베이스 클래스 포인터로 `delete` 하는데 베이스 소멸자가 virtual 이 아니면, 표준상 undefined behavior 다 — 파생 클래스의 소멸자가 호출되지 않고, `operator delete` 에 넘어가는 크기 정보도 틀리게 된다.

AddressSanitizer( ASan )가 이걸 정확히 잡아냈다:
```
AddressSanitizer: new-delete-type-mismatch
  size of the allocated type:   160 bytes;
  size of the deallocated type: 128 bytes.
    #4 NVM_PHY_ONFI::broadcastTransactionServicedSignal(...)
```

`NVM_Transaction_Flash_RD/WR/ER` 를 `NVM_Transaction*` 포인터로 `delete` 하는데( transaction 처리가 끝날 때마다 실행되는 코드 ), `NVM_Transaction` 에 소멸자가 아예 선언돼 있지 않았다.

**고친 6개 클래스** : `NVM_Transaction`, `NVM_PHY_Base`, `GC_and_WL_Unit_Base`, `NVM_Firmware`, `Host_Components::IO_Flow_Base`, `NVM_Channel_Base` — 전부 `virtual` 소멸자를 추가하거나( 이미 있던 경우 ) 새로 선언했다.

**검증된 영향** : 이 6개를 전부 고치자 네이티브 빌드가 ASan+UBSan 을 켠 채로 3개 시나리오 전부 **에러 없이** 완주했다( 고치기 전에는 시나리오 종료 시점의 정리(cleanup) 코드에서 크래시가 났다 ). 다만 이 delete 들은 전부 **시나리오가 끝나고 정리할 때만 실행**되기 때문에, WASM 이 계산한 시뮬레이션 숫자 자체에는 전혀 영향을 주지 않았다 — 여전히 시나리오 3 은 2,418 개에서 멈췄다.

<div style="margin-top: 60px;"></div>

## 버그 3 — `IO_Flow_Synthetic` 의 미초기화 포인터

버그 2 를 고치자( 파생 클래스 소멸자가 태어나서 처음으로 실제로 호출되기 시작하면서 ) 곧바로 새로운 크래시가 났다 — `IO_Flow_Synthetic` 의 소멸자가 6개의 `RandomGenerator*` 멤버를 조건 없이 전부 `delete` 하는데, 그중 4개( `random_hot_address_generator` 등 )는 생성자에서 **조건부로만** `new` 되고 있었다. 조건이 안 맞으면 그 포인터는 초기화되지 않은 채( garbage 값 ) 남아있었고, 소멸자가 이걸 `delete` 하려다 SEGV 가 났다.

**왜 이제껏 안 터졌나** : 버그 2 때문에 이 소멸자 자체가 **한 번도 실제로 실행된 적이 없었다.** 버그 2 를 고치고 나서야 이 오래된 버그가 드러난 것 — 죽어있던 코드가 처음 살아나면서 자기 안의 버그를 드러낸 셈이다.

**수정** : 헤더에서 6개 포인터 전부 `= nullptr` 로 초기화. `delete nullptr` 은 표준상 항상 안전한 no-op 이라, 조건부 `new` 가 실행 안 됐어도 소멸자가 안전해진다.

<div style="margin-top: 60px;"></div>

## 버그 4 — `std::multimap::find()` 에 대한 잘못된 가정 (근본 원인)

**위치** : `ssd/Address_Mapping_Unit_Page_Level.cpp` 의 `handle_transaction_serviced_signal_from_PHY()`

CMT( Cached Mapping Table ) 에 없는 페이지에 쓰기 요청이 들어오면( CMT miss ), MQSim 은 매핑 정보를 flash 에서 읽어오는 별도의 "매핑 읽기" 트랜잭션을 만들고, 원래의 쓰기 요청은 그 읽기가 끝날 때까지 `ArrivingMappingEntries` 라는 `std::multimap<MVPN_type, LPA_type>` 에 대기시켜 둔다. 매핑 읽기가 끝나면 이 핸들러가 불려서, 그 MVPN 을 기다리던 쓰기 요청들을 찾아 다시 제출한다:

```cpp
auto it = ArrivingMappingEntries.find(mvpn);
while (it != ArrivingMappingEntries.end()) {
    if (it->first == mvpn) { /* 이 lpa 의 쓰기 요청 처리 */ }
    else break;
    it = ArrivingMappingEntries.erase(it);  // (원래 코드는 erase(it++))
}
```

이 코드는 **"같은 mvpn 키를 가진 항목이 여러 개 있을 때, `find()` 가 그중 맨 처음(가장 먼저 들어온) 항목을 반환한다"** 는 가정 위에 짜여 있다 — 그래야 정방향으로만 걷는 이 while 문이 같은 키를 가진 항목을 전부 방문할 수 있기 때문이다.

**그런데 C++ 표준은 이걸 보장하지 않는다.** cppreference 의 `multimap::find` 설명 : *"If there are several elements with key in the container, any of them may be returned"* — 여러 개 중 아무거나 반환해도 표준을 어기는 게 아니라는 뜻이다. 네이티브가 쓰는 libstdc++ 는 실제로는 항상 첫 번째를 반환했지만( 표준이 보장하는 게 아니라 그냥 그 구현이 우연히 그렇게 동작하는 것 ), WASM 이 쓰는 libc++ 는 항상 그렇지는 않았다 — 직접 계측으로 확인했다.

두 개의 인접한 LPA( 같은 MVPN 에 속하는 두 쓰기 요청 )가 동시에 같은 매핑 읽기를 기다리는 상황에서, WASM 의 `find()` 가 **두 번째로 들어온 항목**을 반환하면, 정방향 while 문은 그 지점부터만 훑기 때문에 **첫 번째 항목은 영원히 스킵된다** — 컨테이너 안에는 계속 남아있지만( 삭제되지 않으니까 ), 다시는 처리되지 않는다. 그 쓰기 요청은 완료되지 못하고, 그걸 위해 예약해 둔 CMT 슬롯도 영원히 반환되지 않는다.

이게 시나리오 3 에서 관찰된 모든 증상을 정확히 설명한다 — 처음 몇 개 완료 시점부터 이미 어긋나기 시작하는 것( 이런 충돌이 아주 초반부터 발생 ), 특정 LPA 하나가 완료 로그에서 통째로 사라지는 것( 전체 로그 2만 줄을 다 뒤져도 단 한 번도 안 나타남 — "늦게" 처리된 게 아니라 "영원히" 처리 안 된 것 ), 그리고 시간이 지날수록 이런 게 쌓여 CMT 슬롯이 하나씩 영구히 잠기다가 결국 파이프라인 전체가 멈춰버리는 것( 시뮬레이션 시간은 네이티브의 97% 까지 진행했는데도 이벤트가 완전히 고갈됨 )까지.

### 어떻게 여기까지 추적했나

1. 완료 로그( 매 트랜잭션이 끝날 때 시각·타입·LPA 를 출력 )를 네이티브·WASM 양쪽에서 뽑아 diff — 두 로그가 처음 몇 십 줄 안에서부터 이미 다르다는 걸 확인( 서서히 벌어지는 게 아니라 초반부터 다름 )
2. 네이티브 로그에만 있고 WASM 로그 전체( 7천여 줄 )에는 단 한 번도 없는 LPA 하나를 특정( `grep -c` 로 등장 횟수를 세어 확인 )
3. 그 LPA 하나의 일생을 단계별로 추적 — 요청 도착 → CMT miss 판정 → 매핑 읽기 트랜잭션 생성 → **매핑 읽기 자체는 네이티브·WASM 양쪽에서 정확히 같은 시각에 완료됨( 여기까진 문제 없음 )** → 매핑 읽기 완료 핸들러의 while 문 내부 — **바로 여기서 네이티브는 이 LPA 를 방문하고 WASM 은 건너뛴다**는 걸 확인
4. 포인터 값을 태그로 붙여서( LPA 필드가 매핑 읽기 트랜잭션에서는 다른 용도로 재사용되기 때문에 ) 로그 여러 단계에 걸쳐 같은 트랜잭션을 정확히 추적

### 수정

`find()` + 수동 while 문 패턴 3곳( `ArrivingMappingEntries`, `Waiting_unmapped_read_transactions`, `Waiting_unmapped_program_transactions` — 전부 같은 패턴 ) 을 전부 **`std::multimap::equal_range()`** 로 교체했다. `equal_range()` 는 구현체와 무관하게 "같은 키를 가진 항목 전체의 범위"를 표준이 보장하는 방식으로 반환한다.

```cpp
auto range = ArrivingMappingEntries.equal_range(mvpn);
for (auto it = range.first; it != range.second; ) {
    LPA_type lpa = it->second;
    /* 처리 */
    it = ArrivingMappingEntries.erase(it);
}
```

<div style="margin-top: 40px;"></div>

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 260" style="width:100%;max-width:760px;height:auto;display:block;margin:1.5rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-bh1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .boxbad { fill:#fdecea; stroke:#c0392b; stroke-width:2; }
    .title { fill:#2c3e50; font-size:13px; font-weight:700; text-anchor:middle; }
    .body { fill:#3d4a5a; font-size:11px; text-anchor:middle; }
    .flow { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-bh1); fill:none; }
    .rowlabel { fill:#2c3e50; font-size:13px; font-weight:700; }
    .note { fill:#7f8c8d; font-size:11px; font-style:italic; }
  </style>

  <text x="10" y="25" class="rowlabel">Native (libstdc++) — find() 가 우연히 첫 항목을 반환</text>
  <rect x="10" y="45" width="260" height="55" rx="8" class="box"/>
  <text x="140" y="68" class="title">ArrivingMappingEntries</text>
  <text x="140" y="88" class="body">[mvpn:14401310, mvpn:14401311]</text>
  <line x1="270" y1="72" x2="310" y2="72" class="flow"/>
  <rect x="310" y="45" width="280" height="55" rx="8" class="box"/>
  <text x="450" y="68" class="title">find() → 14401310 부터 순회</text>
  <text x="450" y="88" class="body">두 항목 모두 처리됨 ✅</text>

  <line x1="20" y1="130" x2="880" y2="130" stroke="#ddd" stroke-width="1"/>

  <text x="10" y="160" class="rowlabel">WASM (libc++) — find() 가 두 번째 항목을 반환할 수 있음</text>
  <rect x="10" y="180" width="260" height="55" rx="8" class="box"/>
  <text x="140" y="203" class="title">ArrivingMappingEntries</text>
  <text x="140" y="223" class="body">[mvpn:14401310, mvpn:14401311]</text>
  <line x1="270" y1="207" x2="310" y2="207" class="flow"/>
  <rect x="310" y="180" width="280" height="55" rx="8" class="boxbad"/>
  <text x="450" y="203" class="title">find() → 14401311 부터 순회</text>
  <text x="450" y="223" class="body">14401310 은 영원히 스킵 ❌</text>
</svg>
</div>

**1차 검증** : 시나리오 1( synthetic )은 네이티브·WASM 이 요청 수( 329,898 / 41,238 )까지 완전히 동일해졌고, 시나리오 3( trace )은 양쪽 다 6,999 개 전부 처리로 완전히 일치했다.

<div style="margin-top: 60px;"></div>

## 해결된 별개 이슈 — 시나리오 2 의 `std::bad_alloc` (버그 아님)

버그 4 를 고친 뒤 시나리오 2( synthetic, 가장 큰 시나리오 )를 WASM 으로 돌리면 처음엔 `std::bad_alloc` 이 발생했다. 이건 실제로 catch 되는 C++ 예외로 직접 확인한 것이지 추측이 아니다 — Emscripten 에 `-fexceptions` 를 켜고 예외를 잡아 메시지를 출력해서 확인했다.

이건 **버그가 아니라 WASM32 의 태생적 한계**였다. WASM32 는 32비트 주소 공간이라 메모리 한계가 4GB 인데, 빌드 스크립트가 테스트 중에는 메모리 상한을 2GB 로 잡아뒀었다 — `AddressMappingDomain` 생성자 하나가 약 1.5GB 짜리 배열을 요청하는 걸 ASan 으로 확인했으니, 큰 설정에서는 2GB 로 빠듯했던 것. **`-sMAXIMUM_MEMORY` 를 WASM32 의 실제 한계인 4GB 로 올리자 시나리오 2 도 완주하고 네이티브와 정확히 일치**했다( 아래 "추가 검증" 참고 ). 이 값은 실제 `engine/build-wasm.sh` 에도 반영해 뒀다.

<div style="margin-top: 60px;"></div>

## 추가 검증 — 더 다양한 테스트 케이스로 재확인

수정한 뒤에도 "혹시 이 특정 설정 하나에만 우연히 맞아떨어진 건 아닐까" 하는 의심이 남아서, 훨씬 다양한 입력으로 다시 검증했다.

**MQSim 자체 샘플 설정 4개** ( `-sMAXIMUM_MEMORY=4GB` 로 재빌드 후, 이전에 테스트 안 해본 두 번째 trace 파일(`wsrch-small.trace`)도 추가 ) — 4개 시나리오 전부 **결과 XML 파일이 완전히 MD5 일치**( 요약 숫자만이 아니라 파일 전체 ):

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>시나리오</th><th>종류</th><th>결과</th></tr>
<tr><td>1</td><td>Synthetic(소)</td><td>✅ MD5 완전 일치( 329,898 / 41,238 )</td></tr>
<tr><td>2</td><td>Synthetic(대)</td><td>✅ MD5 완전 일치( 907,628 / 623,472 ) — 위의 bad_alloc 이슈 해결 후</td></tr>
<tr><td>3</td><td>Trace(tpcc)</td><td>✅ MD5 완전 일치( 6,999/6,999 ) — 원래 버그 발견 전 네이티브 기준값과도 동일</td></tr>
<tr><td>4( 신규 )</td><td>Trace(wsrch)</td><td>✅ MD5 완전 일치( 24,783/24,783 )</td></tr>
</table>
</div>

**MQSim 원본 저장소의 FAST 2018 논문 재현 테스트 스위트도 통째로 돌려봤다** ( `fast18/` 디렉터리 — 이 프로젝트가 만든 게 아니라 CMU-SAFARI 가 원래 논문 실험을 재현하려고 만들어 둔 것 ). `backend-contention`, `data-cache-contention`, `queue-fetch-size`( 큐 크기 16/1024 두 버전 ) 세 그룹, 총 64개 시나리오 실행분을 네이티브·WASM 로 각각 돌려 비교했는데 **전부 바이트 단위로 일치**했다. 이 중 하나( `queue-fetch-size` 설정 )는 `Ideal_Mapping_Table=true` 를 쓰는 완전히 다른 코드 경로라 — CMT miss 처리 자체를 안 타므로 버그 4 를 아예 건드리지 않는 케이스인데, 이것도 이상 없이 일치해서 "고친 부분 말고 다른 데를 건드리지 않았다"는 확인도 됐다.

이 과정에서 **이번 조사와 무관한, MQSim 원본에 이미 있던 버그 2개**를 우연히 발견했다( 참고용으로 남겨둠, 고치지는 않음 ) :

1. `fast18/backend-contention/workload-backend-contention-flow-1.xml` 파일 안에 **git 병합 충돌 마커(`<<<<<<< HEAD`)가 그대로 커밋돼 있어서** 어느 빌드로 돌려도 XML 파싱에 실패한다 — CMU-SAFARI 원본 저장소 자체의 오래된 실수로 보인다.
2. `fast18/data-cache-contention` 의 flow-1-flow-2 동시 실행 워크로드는 시나리오 3( `Working_Set_Percentage=1`, `RANDOM_HOTCOLD`, `Percentage_of_Hot_Region=1` — 극단적으로 작은 비율 조합 )에서 **부동소수점 예외(SIGFPE, 아마 hot region 크기가 0 으로 반올림되면서 생기는 0-나누기)로 크래시**한다. **아무것도 수정하지 않은 원본 MQSim 을 그대로 빌드해서 똑같이 크래시하는 걸 확인**했으니 이번 조사에서 건드린 것과는 무관한, 원본에 이미 있던 별개의 버그다.

<div style="margin-top: 60px;"></div>

## 조사에 쓴 도구

- **UBSan( Undefined Behavior Sanitizer )** : 버그 1( 정수 오버플로우 )을 즉시 잡아냄
- **ASan( Address Sanitizer )** : 버그 2( new/delete 타입 불일치, SEGV )를 잡아냄. Emscripten 자체 ASan 도 시도했지만 이 정도 규모 시나리오에는 메모리가 부족해서 실용적이지 않았음( 버그 4 의 std::bad_alloc 규명에는 오히려 도움이 됨 )
- **완료 로그 diff + 포인터 태깅** : 버그 4( 근본 원인 )를 찾아낸 결정적 방법. 최종 결과만 비교해서는 못 찾고, 트랜잭션 하나의 전체 생애주기를 단계별로 추적해서야 발견함

<div style="margin-top: 60px;"></div>

## 참고

- 원본 디버깅 로그( 조사 중 시도했다가 기각한 가설들 포함 ) : `engine/WASM_PARITY_DEBUG_LOG.md` ( ftl-visual-simulator 저장소 )
- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/)
- [MQSim](/ftl-visual-simulator/reference/mqsim/)
- [ftl-visual-simulator 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator)
