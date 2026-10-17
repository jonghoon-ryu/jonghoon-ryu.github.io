---
layout: default
title: 9. 열어 보기
permalink: /old-ssd-experiments/9-teardown/
---
<style>
.glance { display:grid; grid-template-columns: 9rem 1fr; gap:4px 14px; background:#f4f8f6; border:1px solid #cfe3db; border-left:4px solid #1f6f5c; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.glance b { color:#1f6f5c; }
.warn { background:#fdf2f0; border-left:4px solid #c0392b; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.93rem; }
.result { background:#fffbea; border:1px dashed #b7950b; padding:12px 16px; margin:1.2rem 0; font-size:0.93rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2.5rem 0 0; font-size:0.95rem; }
table.t { table-layout:fixed !important; width:100% !important; border-collapse:collapse; font-size:0.86rem; margin:1rem 0; }
table.t th { background:#e8f3ef !important; color:#1f3d34 !important; text-align:left; padding:6px 8px; border:1px solid #cfe3db; overflow-wrap:break-word; word-break:break-word; }
table.t td { padding:6px 8px; border:1px solid #e5e8e8; vertical-align:top; overflow-wrap:break-word; word-break:break-word; }
table.t code { font-size:0.82rem; }
@media (max-width: 640px) { .glance { grid-template-columns: 1fr; } }
</style>

# 9. 열어 보기 : 시뮬레이터의 '채널 × 칩' 을 손으로 만지기

<div class="glance">
<b>목표</b><span>케이스를 열고 컨트롤러 · DRAM · NAND 패키지를 찾아, 부품 표기로 사양을 확인하고 시뮬레이터의 구조와 잇는다</span>
<b>보는 것</b><span>컨트롤러, DRAM, NAND 패키지 수, 채널 배선, 전원 부품</span>
<b>지우나?</b><span>— (보통 마지막에 한다. 조심하면 다시 조립해 쓸 수도 있다)</span>
<b>준비물</b><span>정밀 드라이버 (나사 종류는 열어 봐야 안다), 플라스틱 헤라, 휴대폰 카메라, 정전기 조심</span>
<b>시간</b><span>1시간</span>
</div>

## 찾을 것

<svg viewBox="0 0 760 345" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="기판"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">SSD 기판에서 찾을 것</text><rect x="20" y="120" width="90" height="80" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="65.0" y="156.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">SATA</text><text x="65.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="middle">커넥터</text><rect x="160" y="100" width="200" height="120" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="260.0" y="140.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">컨트롤러 (MEX)</text><text x="260.0" y="156.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ARM 코어 3개 (알려진 값)</text><text x="260.0" y="172.0" font-size="11.5" fill="#4d5656" text-anchor="middle">FTL 펌웨어가 도는 곳</text><text x="260.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ECC, SATA, NAND 채널</text><rect x="160" y="250" width="200" height="55" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="260.0" y="273.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">DRAM</text><text x="260.0" y="289.5" font-size="11.5" fill="#4d5656" text-anchor="middle">매핑 표 · 캐시</text><line x1="110" y1="160" x2="158" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="260" y1="220" x2="260" y2="250" stroke="#7d3c98" stroke-width="2"/><rect x="470" y="50" width="240" height="52" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="590.0" y="72.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND 패키지 1?</text><text x="590.0" y="88.0" font-size="11.5" fill="#4d5656" text-anchor="middle">안에 die 여러 장</text><path d="M360,160 C420,160 420,76 468,76" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="470" y="115" width="240" height="52" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="590.0" y="137.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND 패키지 2?</text><text x="590.0" y="153.0" font-size="11.5" fill="#4d5656" text-anchor="middle">안에 die 여러 장</text><path d="M360,160 C420,160 420,141 468,141" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="470" y="180" width="240" height="52" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="590.0" y="202.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND 패키지 3?</text><text x="590.0" y="218.0" font-size="11.5" fill="#4d5656" text-anchor="middle">안에 die 여러 장</text><path d="M360,160 C420,160 420,206 468,206" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="470" y="245" width="240" height="52" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="590.0" y="267.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">NAND 패키지 4?</text><text x="590.0" y="283.0" font-size="11.5" fill="#4d5656" text-anchor="middle">안에 die 여러 장</text><path d="M360,160 C420,160 420,271 468,271" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="415.0" y="337.0" font-size="11.5" fill="#566573" text-anchor="middle">패키지 수 · 표기는 열어 봐야 안다 : 사진을 찍어 오면 부품 번호로 찾아본다</text></svg>

<div style="overflow-x:auto;"><table class="t">
<thead><tr>
<th>부품</th>
<th>보는 법</th>
<th>확인하고 싶은 것</th>
</tr></thead><tbody>
<tr><td>컨트롤러</td><td>가장 큰 칩, 'SAMSUNG' 과 부품 번호</td><td>MEX 인지, 코어 수 (자료로)</td></tr>
<tr><td>DRAM</td><td>컨트롤러 옆 작은 칩</td><td>용량 : 매핑 표가 다 들어가는 크기인가 (120 GB ÷ 4 KiB × 4 B ≈ 117 MB)</td></tr>
<tr><td>NAND 패키지</td><td>같은 모양의 칩 여러 개 (양면일 수 있다)</td><td>개수, 표기 → die 수, 용량, 세대 (19 nm TLC 로 알려짐)</td></tr>
<tr><td>기판 배선</td><td>컨트롤러에서 NAND 로 가는 선 묶음</td><td>채널 수 짐작</td></tr>
</tbody></table></div>

DRAM 계산 : 4 KiB 페이지마다 4바이트 주소를 하나씩 두는 매핑 표라면, 120 GB ÷ 4 KiB ≈ 2,930만 줄 × 4 B ≈ 117 MB 다. 그래서 이 시대 SSD 는 '용량 1 GB 당 DRAM 1 MB' 를 흔히 붙였다. 실제 DRAM 용량과 비교해 보면 FTL 이 표를 어떻게 들고 있는지 짐작할 수 있다.

## 시뮬레이터와 잇기

<svg viewBox="0 0 760 220" style="font-variant-ligatures:none;width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="계층"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="380.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">시뮬레이터의 계층과 실제 부품</text><rect x="10" y="50" width="135" height="55" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="77.5" y="73.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">채널</text><text x="77.5" y="89.5" font-size="11.5" fill="#4d5656" text-anchor="middle">컨트롤러 핀 묶음</text><rect x="160" y="50" width="135" height="55" rx="8" fill="#e8f3ef" stroke="#1f6f5c" stroke-width="2"/><text x="227.5" y="73.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">칩</text><text x="227.5" y="89.5" font-size="11.5" fill="#4d5656" text-anchor="middle">NAND 패키지 안 die</text><line x1="147" y1="77" x2="158" y2="77" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="310" y="50" width="135" height="55" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="377.5" y="73.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">plane</text><text x="377.5" y="89.5" font-size="11.5" fill="#4d5656" text-anchor="middle">die 안</text><line x1="297" y1="77" x2="308" y2="77" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="460" y="50" width="135" height="55" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="527.5" y="73.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">블록</text><text x="527.5" y="89.5" font-size="11.5" fill="#4d5656" text-anchor="middle">지움 단위</text><line x1="447" y1="77" x2="458" y2="77" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="610" y="50" width="135" height="55" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="677.5" y="73.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">페이지</text><text x="677.5" y="89.5" font-size="11.5" fill="#4d5656" text-anchor="middle">읽기 · 쓰기 단위</text><line x1="597" y1="77" x2="608" y2="77" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="150.0" font-size="12" fill="#2c3e50" text-anchor="middle">열어서 볼 수 있는 것은 앞의 둘 (채널은 배선, 칩은 패키지) 까지</text><text x="380.0" y="175.0" font-size="12" fill="#2c3e50" text-anchor="middle">나머지는 데이터시트와 실험 (블록 크기 · 페이지 크기 추정) 으로</text></svg>

## 절차

1. 사진을 찍어 둔다 : 열기 전, 연 뒤, 칩마다 가까이 (표기가 읽히게)
2. 사진을 `~/Ryu/old_ssd_results/teardown/` 에 넣고 Claude 에게 알린다 : 부품 번호를 읽어 데이터시트 · 자료와 맞춰 본다
3. 결과를 이 페이지의 '결과' 에 사진과 함께 적는다

<div class="warn" markdown="1">
- 정전기 : 금속에 손을 대어 몸의 전하를 빼고 만진다.
- 케이스가 걸쇠로 끼워져 있으면 무리하게 비틀지 않는다. 840 EVO 는 나사 + 걸쇠로 알려져 있다 (확인 필요).
- 개인 사진에 시리얼 스티커가 보이는 것은 상관없지만, 블로그에 올릴 때는 가리는 편이 낫다.
</div>

## 결과

<div class="result" markdown="1">
아직 실행 전.
</div>

<div class="step-nav"><a href="{{ '/old-ssd-experiments/8-endurance/' | relative_url }}">← 8. 끝까지 쓰기</a><span></span></div>
