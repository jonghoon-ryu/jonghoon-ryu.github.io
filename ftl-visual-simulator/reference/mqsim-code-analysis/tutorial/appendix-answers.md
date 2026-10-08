---
layout: default
title: 부록 D. 확인해 보기 — 풀이
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 부록 D. 확인해 보기 — 풀이

각 단계 끝의 **확인해 보기** 문제의 답을 모았다. **먼저 스스로 코드에서 찾아 본 뒤** 확인하자. 줄 번호는 `51f0f2d` 기준이고, 답을 찾을 때 쓴 줄을 함께 적었다.

<svg viewBox="0 0 980 220" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="문제 푸는 법"><defs><marker id="aans" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="aanss" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="18" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">확인 문제를 푸는 법 — 모르면 먼저 이 세 가지를 한다</text><rect x="15" y="40" width="300" height="150" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="165.0" y="98.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">① 줄을 찾는다</text><text x="165.0" y="117.0" font-size="11" fill="#4d5656" text-anchor="middle">문제에 적힌 `파일:줄` 을 연다</text><text x="165.0" y="132.0" font-size="11" fill="#4d5656" text-anchor="middle">없으면 함수 이름으로 grep</text><text x="165.0" y="147.0" font-size="11" fill="#4d5656" text-anchor="middle">(`grep -n 이름 src/ssd/*.cpp`)</text><rect x="340" y="40" width="300" height="150" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="490.0" y="98.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">② 직접 돌려 본다</text><text x="490.0" y="117.0" font-size="11" fill="#4d5656" text-anchor="middle">부록 C 의 20개 실험으로</text><text x="490.0" y="132.0" font-size="11" fill="#4d5656" text-anchor="middle">파라미터를 하나만 바꿔 본다</text><text x="490.0" y="147.0" font-size="11" fill="#4d5656" text-anchor="middle">결과 파일의 숫자가 답을 준다</text><rect x="665" y="40" width="300" height="150" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="815.0" y="98.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">③ 중단점을 건다</text><text x="815.0" y="117.0" font-size="11" fill="#4d5656" text-anchor="middle">gdb 로 해당 함수에서 멈추고</text><text x="815.0" y="132.0" font-size="11" fill="#4d5656" text-anchor="middle">`bt`, `p` 로 값을 본다</text><text x="815.0" y="147.0" font-size="11" fill="#4d5656" text-anchor="middle">&quot;어느 분기인지&quot; 를 직접 확인</text></svg>

<div style="margin-top: 60px;"></div>

## 1단계 — 실행 명령과 main()

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step1-run-and-main/)

1. 인자를 하나 빼면 `argc != 5` 이므로(`main.cpp:263`) 사용법(`print_help`)을 찍고 `return 1` — 아무 것도 실행하지 않는다. `-i` 와 `-w` 는 각각 "스위치 + 값" 이라 인자 4개 + 프로그램 이름 = 5 이다. 하나를 빼면 5 가 아니다.
2. 파일이 없으면 오류가 **아니다.** "The specified SSD configuration file does not exist" 라고 알리고 **기본 설정을 그 이름으로 저장**한 뒤(`exec_params->XML_serialize`) 그 기본값으로 진행한다(`main.cpp:38` 이후). 경로 오타가 조용히 새 파일을 만든다.
3. 시나리오 개수만큼 **3 번**. `main()` 의 `for` 루프 안에서 `SSD_Device ssd(…)` 가 지역 변수로 만들어지고 루프가 끝나면 소멸한다. 시작 전에 `Simulator->Reset()` 이 이벤트 목록과 객체 목록을 비운다.

## 2단계 — SSD 와 호스트 만들기

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step2-build-ssd/)

1. 파서(`Device_Parameter_Set.cpp:544`)는 `FLIN` 을 받아들이지만 `SSD_Device.cpp` 의 `switch` 에서 해당 `case` 가 **주석 처리**되어 있어 `default` 로 떨어진다. `std::invalid_argument("No implementation is available for the specified transaction scheduling algorithm")` 가 던져지고 시뮬레이션은 시작되지 못한다. 선택할 수 있는 정책은 `OUT_OF_ORDER` 와 `PRIORITY_OUT_OF_ORDER` 둘뿐이다.
2. 둘 다 **본문이 비어 있다**(`FTL.cpp:891`, `:895`). FTL 객체는 껍데기라서 자기 이벤트를 만들지 않는다. 일은 AMU · 블록 매니저 · GC_WL · TSU · 캐시가 각자 한다.
3. 채널(`ONFI_Channel_NVDDR2`)은 **`Sim_Object` 가 아니라** 단순한 자료 객체이기 때문이다. 스스로 이벤트를 받지 않고 PHY(`NVM_PHY_ONFI_NVDDR2`)가 대신 이벤트를 만들고 채널의 상태(IDLE/BUSY)만 갱신한다.

## 3단계 — 엔진 시작과 이벤트 루프

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/)

1. `Engine::Start_simulation` 이 시작할 때 **`IsTriggersSetUp()` 이 거짓인 객체에 대신 `Setup_triggers()` 를 불러 준다**(`Engine.cpp:60`). 그래서 호출을 빼먹는 일은 거의 없다. 하지만 어떤 클래스의 `Setup_triggers` 안에서 `Connect…Signal` 을 빠뜨리면 **신호의 구독자가 0명**이고, `Validate_simulation_config` 는 그것을 검사하지 않으므로 오류 없이 요청이 영영 완료되지 않는다(조용한 실패). 위 "어떤 검사가 먼저" 에 대한 답은 *없다* 이다.
2. `Store_mapping_table_on_flash_at_start` 가 GTD 의 `MPPN` 을 채운다. 시뮬레이션 시작 때 AMU 의 `Start_simulation`(`Address_Mapping_Unit_Page_Level.cpp:410`)이 부르고, preconditioning 이면 `FTL::Perform_precondition`(`FTL.cpp:49`)도 부른다. 비어 있으면(`NO_MPPN`) `request_mapping_entry` 가 "처음 쓰는 translation page" 로 보고 **flash 를 읽지 않고** 빈 항목만 만든다 — CMT miss 가 공짜가 된다. 이 호출이 있어야 miss 때 translation page 읽기가 발생한다(부록 A 의 매핑 읽기 20번).
3. `_EventList->Count == 0` 이라 `while` 의 첫 반복에서 `break`(`Engine.cpp:82`) — 시뮬레이션 시간 0 에서 바로 끝난다. 정상 설정에서는 각 객체의 `Start_simulation` 이 첫 이벤트를 등록하므로(호스트의 flow 가 첫 요청을 예약) 목록이 비지 않는다.

## 4단계 — 요청의 탄생

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step4-request-enters/)

1. 기본 page 는 8 KB = 16 sector 이다. LHA 20 → `LPA = 20 / 16 = 1`, page 안 오프셋 `20 % 16 = 4`. 8 sector 이므로 sector 4~11 이 한 page 안에 들어가서 **transaction 1 개**. bitmap 은 `((1<<8)-1) << 4 = 0xFF0` (`Host_Interface_NVMe.cpp:192-195`). page 경계를 넘는 요청(예: LHA 12, 8 sector)이면 2 개로 쪼개진다.
2. `Handle_serviced_request` (`:98`)가 **한 요청을 끝낼 때마다** SQ head 와 tail 이 다르면 `Fetch_next_request` 를 불러 하나를 더 가져온다. 즉 `Queue_Fetch_Size` 는 "동시에 처리 중인 요청 수의 상한" 이고 나머지는 완료가 생길 때마다 하나씩 풀린다.
3. **LPA 숫자는 같을 수 있다.** `internal_lsa = lsa - Start_logical_sector_address` (`:185`)로 각 flow 안의 상대 주소로 바꾸기 때문이다. 하지만 매핑 테이블(`AddressMappingDomain`)이 stream 마다 따로이므로 **같은 LPA 라도 서로 다른 PPA 에 간다.** (flow 의 LHA 범위가 겹치면 같은 상대 주소를 받는다.)

## 5단계 — 데이터 캐시

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step5-cache/)

1. 캐시를 끄면 **2 번**. WRITE_CACHE 이면 bloom filter 가 갈라 준다(`write_to_destage_buffer` 의 hot/cold 분기, `:310` 근방). **첫 쓰기**는 filter 에 없는 LPA 라서 "cold" 로 보고 DRAM 에 쓰면서 **즉시 flash 로도 내려보낸다**(eager write-back). **둘째 쓰기**(filter 가 리셋되기 전, 1초 이내)는 filter 에 있으므로 "hot" — DRAM slot 만 갱신하고 flash 로는 **나중에 쫓겨날 때** 간다. 짧게 끝나는 실험이면 1 번, 쫓겨나는 데까지 가면 2 번이다. [데이터 캐시 깊이 보기]({BP}/data-cache/) 의 hot/cold 절 참고.
2. `process_new_user_request` (`Data_Cache_Manager_Flash_Advanced.cpp:186`)의 `case Caching_Mode::TURNED_OFF:` 에서 곧바로 `Translate_lpa_to_ppa_and_dispatch` 를 부른다(`:196` 근방).
3. **DRAM 쓰기가 끝난 뒤.** WRITE_CACHE 에서는 `MEMORY_WRITE_FOR_USERIO_FINISHED` 이벤트에서 `Sectors_serviced_from_cache` 가 0 이 되면 요청 완료(`:546`). flash program 은 그 뒤에 따로 진행된다. 캐시가 꺼져 있으면 마지막 transaction 의 flash 완료 신호가 요청을 끝낸다. (측정: 부록 B 의 854 µs ↔ 43 µs)

## 6단계 — 주소 변환

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step6-translate/)

1. `CMT_Misses_For_Read/Write` 와 `Issued_Flash_Read_CMD_For_Mapping` 이 늘고, 쫓겨난 dirty 항목 때문에 `Issued_Flash_Program_CMD_For_Mapping` 도 는다. **합계 칸 `CMT_Misses` 는 믿으면 안 된다** — flash 읽기가 필요한 miss 를 세지 않는다(부록 A).
2. `handle_transaction_serviced_signal_from_PHY` (`Address_Mapping_Unit_Page_Level.cpp:1665`) 안에서, translation page 읽기가 끝난 `mvpn` 의 도착 항목을 CMT 에 넣은 직후 `Waiting_unmapped_read_transactions` 를 `lpa` 로 찾아 `translate_lpa_to_ppa` 후 TSU 로 제출하고 `erase` 한다(`:1700` 근방). 사용자 쓰기용 `Waiting_unmapped_program_transactions` 도 같은 자리.
3. `Mapping_entry_accessible` 이 항상 참을 돌려주므로 `query_cmt` 의 **`else`(Limited CMT) 전체**가 실행되지 않는다: `request_mapping_entry`, `Waiting_unmapped_*` 보관, `generate_flash_read_request_for_mapping_data`. 그래서 매핑 flash 접근이 0 이 되고 `handle_transaction_serviced_signal_from_PHY` 는 "ideal 인데 flash 접근?" 이라며 예외를 던지도록 되어 있다(`:1672`).

## 7단계 — 쓰기와 page 할당

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/)

1. **invalid 2 개.** 첫 쓰기는 `old_ppa == NO_PPA` 라 invalid 가 없고, 둘째 쓰기가 첫 page 를, 셋째가 둘째 page 를 invalid 로 만든다. 마지막 page 만 valid. 같은 plane 이면(CWDP 처럼 LPA 로 plane 이 정해지는 static 할당) 보통 **같은 block** — write frontier 가 한 block 을 채우는 동안은 연속한 page 에 쌓인다. frontier 가 넘어가면 두 block 에 걸칠 수 있다.
2. **가능하다.** `Check_gc_required` 는 **write frontier block 이 가득 차서 새 block 을 받을 때만** 불린다(`Flash_Block_Manager.cpp:33`, GC 용 frontier 는 `:52`). 한 block 이 256 page 이면 255 번 쓰는 동안 한 번도 안 불린다. 그래서 "GC 는 쓰기마다 검사" 가 아니라 "block 이 찰 때마다" 이다.
3. **아니오.** `old_ppa == NO_PPA` 는 이 LPA 의 옛 데이터가 없다는 뜻이라 병합할 상대가 없다. update read(부분 쓰기의 나머지 sector 를 읽어 오는 읽기)는 `old_ppa != NO_PPA` 이고 새 쓰기가 page 일부만 덮는 경우에만 만들어진다.

## 8단계 — 스케줄러와 플래시 칩

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/)

1. `GC_is_in_urgent_mode(chip)` 로 갈린다(`TSU_Priority_OutOfOrder.cpp`). **긴급 모드**(비선점 GC 이면 항상 참)에서는 GC write 큐를 먼저 보고 사용자 큐는 `sourceQueue2` 로 뒤따라간다 → **GC write 가 먼저**. **선점 모드**에서는 사용자 큐가 먼저이고 GC write 큐가 뒤를 따른다 → **사용자 write 가 먼저**. 둘이 같이 한 명령(multiplane)에 묶일 수는 있다.
2. `GC_is_in_urgent_mode`(`GC_and_WL_Unit_Page_Level.cpp:24`)가 `!preemptible_gc_enabled` 면 즉시 `true` 이던 것이 `false` 로 시작해, 칩의 **어느 plane 이든 free block 수가 `GC_Hard_Threshold`(→ `block_pool_gc_hard_threshold`) 미만일 때만** `true`. 즉 `GC_Hard_Threshold` 는 선점 모드에서만 읽힌다. 비선점에서는 그 값을 아무도 쓰지 않는다.
3. 채널은 명령·데이터를 전송하는 동안 점유되어 **다른 칩은 그 채널로 새 명령을 못 받지만**, 이미 명령을 받은 칩들은 자기 안에서 tR/tPROG 를 **병렬로 실행**한다. 이것이 chip interleaving 이다. 채널이 idle 이 되면(`handle_channel_idle_signal`, `TSU_Base.cpp:50`) 라운드 로빈으로 다음 칩에 명령을 준다.

## 9단계 — 가비지 컬렉션

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/)

1. `Check_gc_required` 의 조건은 `free_block_pool_size < block_pool_gc_threshold` 이고 `block_pool_gc_threshold = GC_Exec_Threshold × plane 당 block 수`(`GC_and_WL_Unit_Base.cpp:22`) 이다. 0.5 로 올리면 free block 이 **절반 아래로 내려가자마자** 시작하므로 **더 일찍, 즉 쓰기가 더 적을 때** GC 가 시작된다(여유 공간은 늘고 이동 page 수는 늘 수 있다). 단 검사 시점은 위에서 말한 "frontier 가 찰 때" 이다.
2. `Current_page_write_index - Invalid_page_count > 0` 이 거짓이므로 **이동 transaction 은 0 개**이고 erase transaction 하나만 `tsu->Submit_transaction` 된다. erase 는 GC erase 큐에 들어가며 해당 칩의 사용자 읽기·쓰기 큐가 비었을 때(또는 긴급 모드에서) 서비스된다. 단, `Invalid_page_count == 0` 인 block(전부 valid)은 `return` 되어 GC 자체가 일어나지 않는다(`:143`).
3. `Set_barrier_for_accessing_physical_block` 이 victim 의 유효 LPA 를 전부 `Locked_LPAs` 에 넣었으므로 사용자 요청은 `Translate_lpa_to_ppa_and_dispatch` 의 `is_lpa_locked_for_gc` 에서 **barrier 에 걸려** `Write_transactions_behind_LPA_barrier` 로 간다. GC 가 그 LPA 를 옮긴 뒤 barrier 가 풀리면 보관된 요청은 "GC 가 옮긴 최신 데이터로 서비스 가능" 하다고 보고 **즉시 완료** 처리된다(`Address_Mapping_Unit_Page_Level.cpp:1806` 근방). 원본 주석이 밝힌 단순화다 — [동시성 제어]({BP}/concurrency-control/).

## 10단계 — 마모평준화

[문제로 가기 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/)

1. `Flash_Block_Manager_Base.cpp:135` 의 `Add_to_free_block_pool(block, consider_dynamic_wl)`. 켜지면 키가 `block->Erase_count`, 꺼지면 모두 `0` 이다. 지운 block 을 되돌릴 때 `Flash_Block_Manager.cpp:144` 가 `Use_dynamic_wearleveling()` 값을 넘긴다. (처음 채울 때 `Flash_Block_Manager_Base.cpp:48` 은 항상 `false` — 모든 block 의 erase 횟수가 0 이라 상관없다.)
2. **WAF 의 분자(flash 에 쓴 총 page 수)에 들어가고 분모(호스트가 쓴 page 수)에는 안 들어간다.** GC 이동과 같은 "쓰기 증폭" 이지만 `Total_page_movements_for_wl` 로 따로 센다([9단계]({TU}/step9-gc/)의 표). 그래서 static WL 이 자주 일어나면 WAF 가 오른다.
3. **그렇다.** 발동 조건(`check_static_wl_required`, `GC_and_WL_Unit_Base.cpp:245`)은 static WL 이 켜져 있고 plane 안 최대·최소 erase 횟수의 **차이**가 `Static_Wearleveling_Threshold` **이상**일 때이다. 고르게 닳고 있으면 차이가 작으므로 안 일어나는 것이 정상이다. 반대로 cold 데이터가 있는 block 은 거의 안 지워져서 차이가 벌어질 때 일어난다.


<div style="margin-top: 60px;"></div>

## 11단계는?

11단계(마무리)는 직접 해 보는 단계라 정해진 답이 없다. [시뮬레이터](/ftl-visual-simulator/run-simulator/)에서 장면을 눈으로 확인해 보자.


<div class="step-nav"><span>[◂ 부록 C. 디버깅과 작은 실험](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-debugging/)</span><span>[튜토리얼 목차 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)</span></div>
