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

**2026.10.5 기준.** Step 1–5 완료 (태그 `step-01` ~ `step-05`), QEMU · VirtualBox 에서 동작. **실제 PC 에서는 아직 시험 전.**

체크 표시는 이 브라우저에만 저장된다. 같은 목록이 저장소의 [TODO.md](https://github.com/jonghoon-ryu/xv6-x86_64/blob/cpp/TODO.md) 에도 있다.

<div class="progress-box">
  <span>완료: <span id="progress-count">0 / 0</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="margin-top: 60px;"></div>

## 1. 지금 : 실제 PC 시험

<span class="who ryu">Ryu</span> 진단 빌드 (`diag-realpc` 브랜치) 로 실제 PC (USB 키보드, UEFI 전용) 부팅해 보기.
진단 빌드는 화면 오른쪽 위에 부팅 단계마다 흰 네모를 하나씩 (최대 8개) 그리고, 로더 화면을 10초 동안 보여 준다.

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="pc-build"> <span class="who ryu">Ryu</span> USB 이미지 만들기 : <code>cd ~/Ryu/xv6-x86_64 &amp;&amp; git switch diag-realpc &amp;&amp; make clean &amp;&amp; make usb.img</code></label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="pc-dd"> <span class="who ryu">Ryu</span> USB 메모리에 쓰기 : <code>lsblk</code> 로 장치 확인 (예 : <code>/dev/sdb</code>, <code>sdb1</code> 아님) → <code>sudo dd if=usb.img of=/dev/sdX bs=4M conv=fsync</code></label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="pc-boot"> <span class="who ryu">Ryu</span> 펌웨어 설정에서 Secure Boot 끄기 → 일회용 부팅 메뉴 (F8 / F11 / F12 / Esc) 로 USB 부팅</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="pc-photo"> <span class="who ryu">Ryu</span> 사진 찍기 : ① 로더 화면 (10초 대기 중) ② 멈춘 화면, 오른쪽 위 흰 네모 포함 ③ 저절로 재부팅되면 그것도 기록</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="pc-send"> <span class="who ryu">Ryu</span> 사진과 결과를 Claude 에게 전달</label></li>
</ul>

결과 읽는 법 : 저장소 `diag-realpc` 브랜치의 `docs/diag-realpc.md`.

<div style="margin-top: 60px;"></div>

## 2. 다음 : 결과에 따라

<div style="overflow-x:auto;">
<table class="plan-calendar">
  <colgroup><col style="width:45%"><col style="width:55%"></colgroup>
  <thead><tr><th>결과</th><th>할 일</th></tr></thead>
  <tbody>
    <tr><td>로더가 <code>kernel start: READ-ONLY</code> 또는 <code>NO-EXECUTE</code> 라고 하거나, 흰 네모가 1개뿐</td><td>로더가 커널로 넘어가기 전에 자기 페이지 테이블을 만든다</td></tr>
    <tr><td><code>memory for kernel is not free</code></td><td>커널을 다른 주소에 올린다</td></tr>
    <tr><td>흰 네모 8개, <code>PS/2 controller: present</code>, 타이핑 됨</td><td>할 일 없음 : 펌웨어가 USB 키보드를 PS/2 로 흉내 내 준다</td></tr>
    <tr><td><code>PS/2 controller: NONE</code>, 또는 타이핑이 안 됨</td><td>USB 키보드 드라이버 (아래 3)</td></tr>
    <tr><td>그 밖의 경우</td><td>사진을 같이 보고 정한다</td></tr>
  </tbody>
</table>
</div>

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="fix"> <span class="who">Claude</span> 위 표에 따라 고치기</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="diag-delete"> <span class="who">Claude</span> 시험이 끝나면 <code>diag-realpc</code> 브랜치 지우기 (임시 진단용) 와 <code>make clean</code></label></li>
</ul>

<div style="margin-top: 60px;"></div>

## 3. USB 키보드 (xHCI 드라이버) — 필요하면

약 1,500줄 C++. 계획에 5–6개 단계로 따로 넣는다. QEMU (`-device qemu-xhci -device usb-kbd`) 에서 먼저 만들고 시험한 뒤 실제 PC 로.

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="usb-pci"> <span class="who">Claude</span> PCI 검색 : xHCI 컨트롤러 찾기</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-xhci"> <span class="who">Claude</span> xHCI : 펌웨어로부터 넘겨받기, 초기화, 명령 / 이벤트 링</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-dev"> <span class="who">Claude</span> USB 장치 설정 : 포트 리셋, 주소, 디스크립터, 구성</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-hid"> <span class="who">Claude</span> HID 키보드 : 키 보고서 → 글자 → <code>consoleintr()</code></label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-hub"> <span class="who">Claude</span> USB 허브 (PC 안에서 허브를 거치는 경우가 많다)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-test"> <span class="who ryu">Ryu</span> 실제 PC 에서 USB 키보드로 타이핑 시험</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="usb-docs"> <span class="who">Claude</span> 단계 태그, 변환 기록, 튜토리얼, <a href="/xv6/plan/">계획</a> 갱신</label></li>
</ul>

<div style="margin-top: 60px;"></div>

## 4. 계획 진행 (2026.11.7 부터)

<ul class="todo">
  <li><label><input type="checkbox" class="todo-check" data-id="plan-review"> <span class="who ryu">Ryu</span> Step 1–5 리뷰 : 튜토리얼 <code>docs/tutorial/step00</code> ~ <code>step05</code> (코드는 완료)</label></li>
  <li><label><input type="checkbox" class="todo-check" data-id="plan-step6"> <span class="who">Claude</span> Step 6 (spinlock) 부터 : "xv6 step N 진행해" 라고 하면 시작. 단계마다 변환 기록 장, 영어 튜토리얼, 태그 <code>step-NN</code></label></li>
</ul>

<div style="margin-top: 60px;"></div>

## 5. 작은 정리 (아무 때나)

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
