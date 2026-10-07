---
layout: default
title: xv6 할 일
permalink: /xv6/todo/
---
<style>
.progress-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  color: #555;
}
.progress-bar-track {
  flex: 1;
  max-width: 280px;
  height: 6px;
  border-radius: 4px;
  background: #e2e2e2;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  width: 0%;
  background: #3a7d44;
  transition: width 0.2s ease;
}
ul.todo {
  list-style: none;
  padding-left: 0.2rem;
}
ul.todo li {
  margin: 0.45rem 0;
}
ul.todo label {
  cursor: pointer;
}
ul.todo li.done label {
  color: #999;
  text-decoration: line-through;
  text-decoration-color: #bbb;
}
.who {
  display: inline-block;
  font-size: 0.8rem;
  color: #fff;
  background: #2d5f8a;
  border-radius: 3px;
  padding: 0 5px;
  margin-right: 4px;
}
.who.ryu { background: #3a7d44; }
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

# 할 일

**2026.10.7 기준.** Step 1–10 완료 (태그 `step-01` ~ `step-10`). **실제 PC (베어본) 에서 동작** : 부팅하고, xv6 자신의 USB 드라이버로 USB 키보드 입력이 된다.

체크 표시는 이 브라우저에만 저장된다. 같은 목록이 저장소의 [TODO.md](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/TODO.md) 에도 있다.

<div class="progress-box">
  <span>완료: <span id="progress-count">0 / 0</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 60px;"></div>

## 1. 끝남 : 실제 PC 시험 (2026.10.7)

![실제 PC 에서 USB 키보드로 친 글](/assets/image/xv6-realpc-usb-keyboard.jpg)

- ✅ 진단 빌드 : 커널은 돈다 (흰 네모 8개, 화면, 메모리 맵). **PS/2 컨트롤러가 없다** (포트 `0x64` 가 `0x55` 로 읽힘) → USB 키보드 드라이버가 필요
- ✅ USB 키보드 드라이버 (xHCI) 를 계획의 **Step 6–10** 으로 넣음 : PCI, 컨트롤러 시작, 장치 설정, 키보드, 허브
- ✅ 실제 PC 1차 : 메인보드의 MSI 장치 (`db0:76`) 를 끝없이 다시 설정 → 고침 (Step 7 의 `porthandled`)
- ✅ 실제 PC 2차 : **입력됨** ("Hi, claude / It looks like it works!")

- ✅ 임시 브랜치 정리 (<code>diag-realpc</code>, 초안 <code>usb-keyboard</code>, <code>cpp-usb</code>, <code>cpp-steps</code>) : 2026.10.7

<div style="margin-top: 60px;"></div>

## 2. USB 키보드 : 아직 없는 것

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="usb-tt"> <span class="who ryu">Ryu</span> (선택) 실제 PC 의 앞면 소켓 (high speed 허브 뒤일 수 있다) 에 키보드를 꽂고 부팅 : QEMU 로는 시험할 수 없는 Transaction Translator 경로 (Step 10 튜토리얼 연습 5)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-hubplug"> <span class="who">Claude</span> 부팅 뒤에 허브에 꽂은 장치 (허브의 interrupt 엔드포인트)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-repeat"> <span class="who">Claude</span> 키 반복 (타이머 필요), Caps Lock 불 (<code>SET_REPORT</code>)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-msi"> <span class="who">Claude</span> 폴링 대신 xHCI 인터럽트 (MSI) : 계획의 트랩과 인터럽트 부분 (Step 19) 에서</label></li>
</ul>

<div style="margin-top: 60px;"></div>

## 3. 계획 진행 (2026.11.7 부터)

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="plan-review10"> <span class="who ryu">Ryu</span> Step 1–10 리뷰 : 튜토리얼 <code>docs/tutorial/step00</code> ~ <code>step10</code> (코드는 완료)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="plan-step11"> <span class="who">Claude</span> Step 11 (spinlock) 부터 : "xv6 step N 진행해" 라고 하면 시작. 단계마다 변환 기록 장, 영어 튜토리얼, 태그 <code>step-NN</code>. <b>실제 PC 에서 돼야 그 단계가 끝난다</b></label></li>
</ul>

<div style="margin-top: 60px;"></div>

## 4. 작은 정리 (아무 때나)

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="clean-ci"> <span class="who">Claude</span> <code>.github/workflows/test.yml</code> : 아직 원본의 RISC-V 용 CI. x86-64 빌드 확인으로 바꾸거나 지우기</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="clean-gdb"> <span class="who">Claude</span> <code>make qemu-gdb</code> 를 x86-64 용으로 정리</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="clean-img"> <span class="who">Claude</span> 블로그 : 더 이상 안 쓰는 <code>assets/image/xv6-cpp-skeleton.png</code> 지우기</label></li>
</ul>

<script>
(function () {
  var STORAGE_KEY = 'xv6-todo';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('.todo-check'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = boxes.length;
    var state = load();

    function render() {
      var done = 0;
      boxes.forEach(function (cb) {
        var isDone = !!state[cb.getAttribute('data-id')];
        cb.checked = isDone;
        var li = cb.closest('li');
        if (li) li.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    boxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        state[cb.getAttribute('data-id')] = cb.checked;
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
