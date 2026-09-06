---
layout: default
title: 마모 평준화 버그와 의도적 동작 변경
permalink: /ftl-visual-simulator/reference/wl-bug-deviation/
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
pre {
  background: #f5f5f5;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>

# 마모 평준화 버그와 의도적 동작 변경

Session 6(마모 평준화 hook)을 진행하다가, 원본 MQSim 코드에서 static 마모 평준화(wear-leveling)가 사실상 제대로 동작하지 않는 버그 2개를 발견했다. 이 문서는 그 버그가 정확히 뭔지, 왜 [MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/)의 4개 버그와 성격이 다른지, 그리고 **왜 "원본 그대로 재현"이라는 이 프로젝트의 원칙을 깨고 고치기로 했는지**를 상세히 기록한 것.

<div style="margin-top: 60px;"></div>

## 1. 이게 왜 "버그 헌트"와 다른 문서인가

[MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/) 문서의 버그 4개는 전부 **이식성(portability) 버그** 였다 — 네이티브 빌드와 WASM 빌드가 서로 다른 결과를 냈던 원인들(RNG 정수 오버플로우, 소멸자, 미초기화 포인터, `multimap::find()` 가정 오류). 그 버그들을 고친다고 해서 "네이티브 MQSim이 원래 하던 동작"이 바뀌지는 않는다 — 오히려 WASM 이 네이티브와 **똑같이** 동작하도록 맞추는, 이 프로젝트의 핵심 전제("실제 MQSim 과 100% 동일하게 동작")를 **지키기 위한** 수정이었다.

이번에 찾은 버그 2개는 다르다. **둘 다 네이티브 MQSim 자체의 로직 오류**다 — 플랫폼과 무관하게, CMU-SAFARI 원본 저장소를 그대로 빌드해도 존재하는 문제다. 이걸 고친다는 건 "이 프로젝트의 시뮬레이터가 upstream MQSim 과 다르게 동작하기로 의도적으로 결정한다"는 뜻이다. 그래서 별도 문서로 명확히 남겨둔다.

<div style="margin-top: 60px;"></div>

## 2. 버그 1 — `run_static_wearleveling()`이 블록 ID를 주소로 착각

`GC_and_WL_Unit_Base.cpp`의 `run_static_wearleveling()` 함수는 마모 평준화 대상 블록을 고른 뒤, 그 블록에 "지금 GC/WL 작업 중"이라고 표시해두는 상태 갱신 함수를 호출한다.

**수정 전**
```cpp
NVM::FlashMemory::Physical_Page_Address wl_candidate_address(plane_address);
wl_candidate_address.BlockID = wl_candidate_block_id;
Block_Pool_Slot_Type* block = &pbke->Blocks[wl_candidate_block_id];

//Run the state machine to protect against race condition
block_manager->GC_WL_started(wl_candidate_block_id);   // ← 버그
```

`GC_WL_started()`의 실제 시그니처는 이렇다:

```cpp
void GC_WL_started(const NVM::FlashMemory::Physical_Page_Address& block_address);
```

`Physical_Page_Address`는 채널·칩·다이·플레인·블록, 5개 좌표를 갖는 구조체다. 그런데 위 호출은 정수 하나(`wl_candidate_block_id`, 그 플레인 안에서 블록의 순번)를 그대로 넘기고 있다. `Physical_Page_Address`의 생성자가 모든 인자에 기본값(0)을 갖고 있어서, 인자를 하나만 주면 C++ 이 그 값을 **첫 번째 파라미터인 `ChannelID`** 자리에 채워 넣은 채로 암묵적으로 변환해버린다. 즉 "이 채널·칩·다이·플레인의 블록 N"을 표시하려던 호출이 실제로는 "채널 N, 칩 0, 다이 0, 플레인 0의 블록 0"을 갱신하는 호출이 되어버린 것이다.

바로 위 두 줄에서 이미 올바른 주소(`wl_candidate_address`)를 만들어뒀는데 그걸 안 쓰고 다시 정수를 넘긴 게 원인 — 아마 GC 쪽(`Check_gc_required()`)의 비슷한 호출을 복사하다가 실수로 다른 변수를 넣은 것으로 보인다.

**왜 심각한가** : `wl_candidate_block_id` 값이 실제 채널 개수(예: 8개)보다 크면 — 블록 개수가 보통 채널 개수보다 훨씬 많으므로(예: 2048개) 거의 항상 그렇다 — 존재하지 않는 채널 인덱스로 배열에 접근하게 된다. C++ 배열은 범위를 검사하지 않으므로 이건 **정의되지 않은 동작(undefined behavior)** 이다. 운이 나쁘면 크래시, 운이 좋으면(?) 조용히 엉뚱한 메모리를 가리키는 포인터를 따라가서 아무 상관없는 블록의 상태를 망가뜨린다.

**수정 후**
```cpp
block->Is_wl_triggered = true;
block_manager->GC_WL_started(wl_candidate_address);   // 이미 만들어둔 올바른 주소를 사용
```

<div style="margin-top: 60px;"></div>

## 3. 버그 2 — "erase count 차이"가 실제로는 "블록 번호 차이"였다

Static 마모 평준화가 필요한지 판단하는 함수는 `check_static_wl_required()`이고, 그 핵심 계산은 `Flash_Block_Manager_Base::Get_min_max_erase_difference()`가 한다 — 이름 그대로 "가장 많이 지워진 블록과 가장 적게 지워진 블록의 erase 횟수 차이"를 구하는 함수여야 한다.

**수정 전**
```cpp
unsigned int Flash_Block_Manager_Base::Get_min_max_erase_difference(...)
{
	unsigned int min_erased_block = 0;
	unsigned int max_erased_block = 0;
	...
	for (unsigned int i = 1; i < block_no_per_plane; i++) {
		if (plane_record->Blocks[i].Erase_count > plane_record->Blocks[max_erased_block].Erase_count) {
			max_erased_block = i;
		}
		if (plane_record->Blocks[i].Erase_count < plane_record->Blocks[min_erased_block].Erase_count) {
			min_erased_block = i;
		}
	}

	return max_erased_block - min_erased_block;   // ← 버그
}
```

루프 자체는 맞다 — `max_erased_block`/`min_erased_block`에는 정확히 "가장 많이/적게 지워진 블록의 **번호(인덱스)**"가 담긴다. 문제는 반환값이다. `check_static_wl_required()`는 이 반환값을 `Static_Wearleveling_Threshold`(예: 100)와 비교하는데, 정작 돌려주는 건 **블록 번호 그 자체의 차이**지 **erase 횟수의 차이**가 아니다.

```cpp
inline bool GC_and_WL_Unit_Base::check_static_wl_required(...)
{
	return static_wearleveling_enabled && (block_manager->Get_min_max_erase_difference(plane_address) >= static_wearleveling_threshold);
}
```

예를 들어 "블록 5번이 40번 지워졌고 블록 1500번이 0번 지워졌다"면, 진짜 마모 불균형(40)과는 무관하게 `1500 - 5 = 1495`가 반환된다. 반대로 "블록 1500번이 40번 지워졌고 블록 5번이 0번 지워졌다"면 `5 - 1500`을 **부호 없는 정수(unsigned int)** 로 빼기 때문에 언더플로우가 나서 `4294967295`(약 43억)라는 사실상 무한대에 가까운 값이 나온다.

실제로 이 프로젝트의 스트레스 테스트로 직접 확인한 값:
```
[디버그 로그] diff=4294967295, threshold=100, result=1(트리거됨)
```

즉 `check_static_wl_required()`가 참을 반환하는지 여부가 **실제 마모 불균형과 사실상 무관하게, 어느 블록이 우연히 최댓값/최솟값을 갖고 있고 그 블록 번호가 얼마인지에 따라 결정**되고 있었다. Threshold 를 아무리 신중하게 설정해도 의미가 없는 상태.

**수정 후**
```cpp
return plane_record->Blocks[max_erased_block].Erase_count - plane_record->Blocks[min_erased_block].Erase_count;
```

`Get_coldest_block_id()`(실제로 어떤 블록을 마모 평준화 대상으로 고를지 정하는 함수)는 처음부터 `Erase_count`를 올바르게 비교하고 있었다 — 버그는 오직 "지금 마모 평준화를 시작해야 하는가"를 판단하는 이 트리거 조건에만 있었다.

<div style="margin-top: 60px;"></div>

## 4. 왜 "원본 그대로 재현"을 깨고 고치기로 했는가

이 프로젝트의 핵심 전제는 [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) 문서에 적어둔 대로 "TS 로 새로 짜지 않고 실제 MQSim 을 그대로 컴파일해서 쓴다 — 그래야 우리가 이해한 대로가 아니라 실제 MQSim 이 하는 그대로를 보여줄 수 있다"는 것이었다. 그런데 이번 버그는 그 전제를 살짝 뒤튼다: **"실제 MQSim 이 하는 그대로"를 보여주면, 정작 static 마모 평준화가 언제 발동하는지는 사실상 무작위(또는 항상 발동, 또는 항상 미발동)가 되어버린다.**

이 프로젝트가 static WL hook 을 만드는 목적은 "static 마모 평준화가 실제로 어떻게 동작하는지 시각적으로 보여주는 것"이다. 버그를 그대로 둔 채 hook 만 붙이면, 화면에 보이는 "지금 마모 평준화가 일어났어요"라는 이벤트가 실제 마모 상태와 아무 상관 없는, 우연에 가까운 타이밍에 뜨게 된다 — 이건 도구의 목적 자체를 배신하는 것이라고 판단해서, **이번만은 upstream 과 다르게 동작하더라도 고치는 쪽을 택했다.**

정리하면:

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th></th><th>MQSim 버그 헌트(4개)</th><th>이 문서의 버그(2개)</th></tr>
<tr><td>성격</td><td>이식성 버그(WASM 전용으로 드러남)</td><td>로직 버그(네이티브에도 그대로 있음)</td></tr>
<tr><td>고치면</td><td>WASM 이 네이티브와 같아짐</td><td>이 프로젝트가 upstream MQSim 과 달라짐</td></tr>
<tr><td>이 프로젝트의 원칙과 관계</td><td>원칙(원본과 동일 동작)을 <b>지키기 위해</b> 고침</td><td>원칙을 <b>의도적으로 깨고</b> 고침</td></tr>
<tr><td>고친 이유</td><td>네이티브/WASM 결과 불일치는 이 프로젝트의 핵심 전제 위반</td><td>버그를 그대로 두면 static WL hook 이 무의미해짐</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 5. 실제로 결과가 달라지는가 — 검증 중 확인한 사실

버그 2를 고치기 전/후로 정말 시뮬레이션 결과가 달라지는지 직접 비교해봤다. 결과는 예상과 달랐다.

- 이 프로젝트에 커밋된 샘플 시나리오 3개(`engine/tests/golden/`)는 버그 수정 전/후 결과 XML이 **완전히 동일**하다 — 애초에 이 정도로 짧은 워크로드에서는 static WL 이 필요할 만큼 마모가 불균형해지지 않기 때문에, 버그가 있든 없든 아무 차이가 없다.
- static WL 을 실제로 발동시키려고 만든 별도의 스트레스 설정(occupancy·GC 임계값을 크게 높인 설정)으로도, **버그 수정 전/후 결과가 동일했다.** 원인은 별도의(세 번째) 구조적 한계 때문이다 — "가장 안 지워진 블록"으로 뽑히는 블록이 매번 GC/번역 데이터용 write frontier 블록이었는데, 이 블록은 아주 가끔만 채워지는 페이지를 받기 때문에 이 프로젝트가 쓸 수 있는 현실적인 테스트 시간 안에서는 다 채워져서 교체되는 일이 없었다. 그래서 static WL 은 버그가 있든 없든 **한 번도 실제로 발동하지 못했다.**

즉, 이번 버그가 "실제로 다른 결과를 낳는다"는 걸 이 프로젝트 안에서 직접 재현하지는 못했다 — 논리적으로는 명백히 잘못된 코드지만, 그 잘못된 계산이 실제 결과에 영향을 주려면 static WL 이 최소 한 번은 성공적으로 실행돼야 하는데, 그 조건 자체를 이 프로젝트의 테스트 규모 안에서 만들어내지 못했다.

> **( 이후 기록 )** "마모평준화 시연" 프리셋을 실제로 연동하면서 **세 번째 버그**(`Static_Wearleveling_Threshold`가 설정과 무관하게 항상 무시되던 문제)를 찾아 고쳤고, 그 뒤 이 프로젝트 최초로 static WL 을 실제로 1회 발동시키는 데 성공했다 — 즉 이 문서에서 고친 두 로직 버그가 실제로 유효한 상태에서 작동하는 걸 확인했다는 뜻이다. 자세한 내용은 [정적 마모 평준화 설정이 아예 전달되지 않던 버그](/ftl-visual-simulator/reference/wl-threshold-not-wired-bug/) 참고.

<div style="margin-top: 60px;"></div>

## 6. 요약

- **두 버그 모두 고쳐서 유지한다.** 롤백하지 않는다.
- 버그 1(`GC_WL_started` 인자 타입 오류)은 메모리 안전성 문제라 고치는 데 이견의 여지가 없다.
- 버그 2(`Get_min_max_erase_difference` 계산 오류)는 **이 프로젝트가 upstream MQSim 과 의도적으로 다르게 동작하기로 한 지점**이다 — static 마모 평준화 hook 이 실제 마모 상태를 반영하도록 하기 위한 선택.
- 커밋된 샘플 시나리오들에는 관찰 가능한 영향이 없다(golden 회귀 테스트로 확인). 영향이 있을 만한 시나리오(오래 지속되는 GC 압박)는 아직 실증하지 못했다.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/) — 이식성 버그 4개(성격이 다름, 1절 참고)
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 6
- [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) — 3-4절(마모 평준화 hook)
- [ftl-visual-simulator 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator) — 실제 코드
- [PR #5](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/5) — 이 문서에서 다루는 버그 수정 (hook 과 분리된 순수 버그 수정 커밋)
- [PR #7](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/7) — 이 버그 수정을 베이스로 한 static WL hook 추가
