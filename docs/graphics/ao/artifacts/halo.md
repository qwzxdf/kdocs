---
title: Halo
tags:
  - 描画
---

# Halo

<strong>ハロー</strong>は、物体の輪郭の周りに、明るい（または暗い）縁が出る現象です。手前の物体と奥の面で、深度が大きく違う所で、サンプルが、手前の物体を遮蔽物と誤認すると、奥の面が暗くなる（または、逆に明るくなる）ためです。このページでは、ハローの原因・距離による減衰（範囲チェック）・対策を説明します。

!!! tip "ポイント"
    - ハロー ＝ 輪郭の周りの、明るい・暗い縁。
    - 原因 ＝ 大きく離れた物を、遮蔽物として扱う。
    - 対策 ＝ 範囲チェック：サンプルと中心の深度差が、半径より大きければ、遮蔽に数えない。
    - 滑らかな範囲チェック（`smoothstep`）で境を柔らかく。

!!! info "このページを読む前に"
    - [AO Artifacts](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ハロー
### 症状

<strong>手前にある物体の輪郭の周り</strong>（背景側）に、暗い光の輪が出ます。人物の頭の周りの壁が暗く縁取られるような見た目です。

### 原因

手前の物体（人物）と、奥の背景（壁）の深度差が大きい境界で、背景の画素の周りのサンプルが、手前の物体の内側に入ります。深度バッファでは、人物は面として存在するので、背景の点が人物に遮られていると判定されます。しかし、実際には人物は壁から離れて立っているので、壁を暗くする理由はありません。

<svg class="fig illust" viewBox="0 0 760 260" role="img" aria-label="ハローの原因">
<text x="20" y="24" class="fig-title">深度の差が大きいと、奥の壁が、手前の人物に「遮られている」と誤判定される</text>
<line x1="60" y1="220" x2="700" y2="220" stroke="currentColor" stroke-width="3"/>
<text x="60" y="244" style="font-size:12px">奥の壁（面）</text>
<rect x="320" y="80" width="40" height="140" fill="rgba(76,139,245,0.3)" stroke="currentColor" stroke-width="2" transform="translate(0,-30)"/>
<text x="300" y="42" style="font-size:12px">手前の人物</text>
<circle cx="260" cy="220" r="7" fill="currentColor"/><text x="250" y="206" style="font-size:12px">p</text>
<circle cx="260" cy="220" r="70" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>
<g fill="#e5484d"><circle cx="310" cy="190" r="5"/><circle cx="320" cy="150" r="5"/></g>
<text x="410" y="110" style="font-weight:700">赤いサンプルが「人物の中」に入る</text>
<text x="410" y="134" style="font-size:12px">→ 壁の p が、人物に遮られていると判定される</text>
<text x="410" y="164" style="font-size:12px">実際には、人物は壁から離れているので、遮蔽は起きない</text>
</svg>

### なぜ「深度が離れている」だけで誤判定になるのか

深度バッファは、画面から見て一番手前の面しか記録していません。つまり「p の周りの半球の中に、本当に物体があるか」を調べているのではなく、「画面上の隣の画素の深度が、p より手前か」を調べているだけです。この近道が、ハローの根本原因です。

具体的な数字で考えます。カメラから人物までが 3 m、壁までが 5 m、AO の半径 R が 0.5 m だとします。壁の点 p のすぐ隣に、人物の輪郭の画素があります。その画素の深度は 3 m で、p の深度 5 m より 2 m も手前です。もし「サンプルが p より手前にあれば遮蔽」とだけ判定すると、人物は p を遮蔽していることになり、半径 0.5 m のはずの AO が、2 m 離れた物体の影響を受けてしまいます。人物がカメラに近づくほど、また壁が遠いほど、この誤判定は広がります。

結果として、人物の輪郭に沿って、壁が暗く縁取られます。これが暗いハローです。

逆向きの問題もあります。法線を深度から再構成している方式では、輪郭の画素で法線が不連続になり、バイラテラル ブラーで輪郭をまたいで平均すると、明るい縁が出ることがあります（[Bilateral Blur](../filtering/bilateral-blur.md)）。暗いハローも明るいハローも、「深度の離れた画素を、同じ面の一部として扱ってしまう」ことが共通の原因です。

<!-- fig:halo-range:begin -->

<svg class="fig illust motion" data-fig="halo-range" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-halo-range" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">範囲チェック: 遠い物を遮蔽に数えると、手前の人物の周りに、暗いハロー(輪)が出る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。人物(深度 1)の後ろに、壁(深度 6)。壁の画素の AO を、範囲チェックなし / 硬い切り捨て / なめらかに弱める、で比べる</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度(濃い = 手前)</text>
<rect x="60.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="77.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="94.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="111.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="128.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="145.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="162.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="179.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="196.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="213.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="230.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="247.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="264.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="281.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="298.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="315.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="332.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="349.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="366.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="383.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="400.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="417.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="434.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="451.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="468.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="485.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="502.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="519.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#334155"/></rect>
<rect x="536.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="553.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="570.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="587.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="604.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="621.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="638.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="655.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="672.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="689.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="706.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="723.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="740.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="757.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="774.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="791.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="808.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="825.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="842.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="859.0" y="106.0" width="17.3" height="22.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e8f0"/></rect>
<rect x="60.0" y="106" width="816.0" height="22.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="160" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">範囲チェックなし</text>
<rect x="60.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#ffffff"/></rect>
<rect x="77.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0689" values="#e5e7eb;#ffffff"/></rect>
<rect x="94.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#ffffff"/></rect>
<rect x="111.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0733" values="#e5e7eb;#ffffff"/></rect>
<rect x="128.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#ffffff"/></rect>
<rect x="145.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0778" values="#e5e7eb;#ffffff"/></rect>
<rect x="162.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#ffffff"/></rect>
<rect x="179.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#ffffff"/></rect>
<rect x="196.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#ffffff"/></rect>
<rect x="213.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867" values="#e5e7eb;#ffffff"/></rect>
<rect x="230.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#ffffff"/></rect>
<rect x="247.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#e5e7eb;#ffffff"/></rect>
<rect x="264.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#ffffff"/></rect>
<rect x="281.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956" values="#e5e7eb;#ffffff"/></rect>
<rect x="298.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#ffffff"/></rect>
<rect x="315.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="332.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#cccccc"/></rect>
<rect x="349.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="366.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#999999"/></rect>
<rect x="383.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089" values="#e5e7eb;#808080"/></rect>
<rect x="400.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#ffffff"/></rect>
<rect x="417.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#ffffff"/></rect>
<rect x="434.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#e5e7eb;#ffffff"/></rect>
<rect x="468.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1222" values="#e5e7eb;#ffffff"/></rect>
<rect x="502.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#ffffff"/></rect>
<rect x="519.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1267" values="#e5e7eb;#ffffff"/></rect>
<rect x="536.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#808080"/></rect>
<rect x="553.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#e5e7eb;#999999"/></rect>
<rect x="570.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="587.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1356" values="#e5e7eb;#cccccc"/></rect>
<rect x="604.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="621.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1400" values="#e5e7eb;#ffffff"/></rect>
<rect x="638.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#ffffff"/></rect>
<rect x="655.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#ffffff"/></rect>
<rect x="689.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1489" values="#e5e7eb;#ffffff"/></rect>
<rect x="706.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#ffffff"/></rect>
<rect x="723.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1533" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1556" values="#e5e7eb;#ffffff"/></rect>
<rect x="757.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1578" values="#e5e7eb;#ffffff"/></rect>
<rect x="774.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#ffffff"/></rect>
<rect x="791.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1622" values="#e5e7eb;#ffffff"/></rect>
<rect x="808.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1644" values="#e5e7eb;#ffffff"/></rect>
<rect x="825.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1667" values="#e5e7eb;#ffffff"/></rect>
<rect x="842.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1689" values="#e5e7eb;#ffffff"/></rect>
<rect x="859.0" y="164.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1711" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="164" width="816.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1732;0.1733;1.0000" values="0;0;1;1"/><text x="884.0" y="182" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">ハロー 8 画素</text>
</g>
<text x="60.0" y="226" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">硬い切り捨て(Δz &lt; 3.0)</text>
<rect x="60.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#ffffff"/></rect>
<rect x="77.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2822" values="#e5e7eb;#ffffff"/></rect>
<rect x="94.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#ffffff"/></rect>
<rect x="111.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2867" values="#e5e7eb;#ffffff"/></rect>
<rect x="128.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#ffffff"/></rect>
<rect x="145.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2911" values="#e5e7eb;#ffffff"/></rect>
<rect x="162.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#ffffff"/></rect>
<rect x="179.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2956" values="#e5e7eb;#ffffff"/></rect>
<rect x="196.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#ffffff"/></rect>
<rect x="213.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#ffffff"/></rect>
<rect x="230.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#ffffff"/></rect>
<rect x="247.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3044" values="#e5e7eb;#ffffff"/></rect>
<rect x="264.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#ffffff"/></rect>
<rect x="281.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3089" values="#e5e7eb;#ffffff"/></rect>
<rect x="298.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3111" values="#e5e7eb;#ffffff"/></rect>
<rect x="315.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3133" values="#e5e7eb;#ffffff"/></rect>
<rect x="332.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3156" values="#e5e7eb;#ffffff"/></rect>
<rect x="349.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3178" values="#e5e7eb;#ffffff"/></rect>
<rect x="366.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#ffffff"/></rect>
<rect x="383.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3222" values="#e5e7eb;#ffffff"/></rect>
<rect x="400.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#e5e7eb;#ffffff"/></rect>
<rect x="417.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3267" values="#e5e7eb;#ffffff"/></rect>
<rect x="434.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3289" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3311" values="#e5e7eb;#ffffff"/></rect>
<rect x="468.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3356" values="#e5e7eb;#ffffff"/></rect>
<rect x="502.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3378" values="#e5e7eb;#ffffff"/></rect>
<rect x="519.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3400" values="#e5e7eb;#ffffff"/></rect>
<rect x="536.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#e5e7eb;#ffffff"/></rect>
<rect x="553.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#ffffff"/></rect>
<rect x="570.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#ffffff"/></rect>
<rect x="587.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3489" values="#e5e7eb;#ffffff"/></rect>
<rect x="604.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3511" values="#e5e7eb;#ffffff"/></rect>
<rect x="621.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#ffffff"/></rect>
<rect x="638.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#e5e7eb;#ffffff"/></rect>
<rect x="655.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#ffffff"/></rect>
<rect x="689.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622" values="#e5e7eb;#ffffff"/></rect>
<rect x="706.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644" values="#e5e7eb;#ffffff"/></rect>
<rect x="723.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#e5e7eb;#ffffff"/></rect>
<rect x="757.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711" values="#e5e7eb;#ffffff"/></rect>
<rect x="774.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#ffffff"/></rect>
<rect x="791.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756" values="#e5e7eb;#ffffff"/></rect>
<rect x="808.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778" values="#e5e7eb;#ffffff"/></rect>
<rect x="825.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3800" values="#e5e7eb;#ffffff"/></rect>
<rect x="842.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#e5e7eb;#ffffff"/></rect>
<rect x="859.0" y="230.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3844" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="230" width="816.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;1.0000" values="0;0;1;1"/><text x="884.0" y="248" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">ハロー 0 画素</text>
</g>
<text x="60.0" y="292" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">なめらかに弱める</text>
<rect x="60.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#ffffff"/></rect>
<rect x="77.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4956" values="#e5e7eb;#ffffff"/></rect>
<rect x="94.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#e5e7eb;#ffffff"/></rect>
<rect x="111.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5000" values="#e5e7eb;#ffffff"/></rect>
<rect x="128.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#ffffff"/></rect>
<rect x="145.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044" values="#e5e7eb;#ffffff"/></rect>
<rect x="162.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#ffffff"/></rect>
<rect x="179.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5089" values="#e5e7eb;#ffffff"/></rect>
<rect x="196.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5111" values="#e5e7eb;#ffffff"/></rect>
<rect x="213.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5133" values="#e5e7eb;#ffffff"/></rect>
<rect x="230.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5156" values="#e5e7eb;#ffffff"/></rect>
<rect x="247.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5178" values="#e5e7eb;#ffffff"/></rect>
<rect x="264.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5200" values="#e5e7eb;#ffffff"/></rect>
<rect x="281.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5222" values="#e5e7eb;#ffffff"/></rect>
<rect x="298.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5244" values="#e5e7eb;#ffffff"/></rect>
<rect x="315.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5267" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="332.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5289" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="349.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5311" values="#e5e7eb;#eeeeee"/></rect>
<rect x="366.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5333" values="#e5e7eb;#e9e9e9"/></rect>
<rect x="383.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5356" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="400.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5378" values="#e5e7eb;#ffffff"/></rect>
<rect x="417.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5400" values="#e5e7eb;#ffffff"/></rect>
<rect x="434.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5422" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5444" values="#e5e7eb;#ffffff"/></rect>
<rect x="468.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5467" values="#e5e7eb;#ffffff"/></rect>
<rect x="485.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5489" values="#e5e7eb;#ffffff"/></rect>
<rect x="502.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5511" values="#e5e7eb;#ffffff"/></rect>
<rect x="519.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5533" values="#e5e7eb;#ffffff"/></rect>
<rect x="536.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5556" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="553.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5578" values="#e5e7eb;#e9e9e9"/></rect>
<rect x="570.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5600" values="#e5e7eb;#eeeeee"/></rect>
<rect x="587.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5622" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="604.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5644" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="621.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5667" values="#e5e7eb;#ffffff"/></rect>
<rect x="638.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5689" values="#e5e7eb;#ffffff"/></rect>
<rect x="655.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5711" values="#e5e7eb;#ffffff"/></rect>
<rect x="672.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5733" values="#e5e7eb;#ffffff"/></rect>
<rect x="689.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5756" values="#e5e7eb;#ffffff"/></rect>
<rect x="706.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5778" values="#e5e7eb;#ffffff"/></rect>
<rect x="723.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5800" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5822" values="#e5e7eb;#ffffff"/></rect>
<rect x="757.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5844" values="#e5e7eb;#ffffff"/></rect>
<rect x="774.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5867" values="#e5e7eb;#ffffff"/></rect>
<rect x="791.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5889" values="#e5e7eb;#ffffff"/></rect>
<rect x="808.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5911" values="#e5e7eb;#ffffff"/></rect>
<rect x="825.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5933" values="#e5e7eb;#ffffff"/></rect>
<rect x="842.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5956" values="#e5e7eb;#ffffff"/></rect>
<rect x="859.0" y="296.0" width="17.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5978" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="296" width="816.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><text x="884.0" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">ハロー 2 画素</text>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">壁にできる暗い輪(画素):</text>
<text x="240" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1732;0.1733;1.0000" values="1;1;0;0"/></text>
<text x="240" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1732;0.1733;0.3865;0.3867;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3865;0.3867;0.5998;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6887;0.6889;1.0000" values="0;0;1;1"/><rect x="40" y="430" width="880" height="76" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="454" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">範囲チェックなしでは、人物の左右 8 画素ぶん、壁が暗くなる(本当は、人物と壁は 5 も離れている)</text>
<text x="56" y="477" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">硬い切り捨ては、しきい値の前後で、急に変わる(少し深度が違う面で、ちらつく)。なめらかに弱める(smoothstep)と、自然につながる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">AO は、近くの物を遮蔽として数える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">深度が大きく離れた物は、実際には影響しないので、重みを下げる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">範囲チェックで、ハローが消える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:halo-range:end -->

### 範囲チェック：遠い遮蔽物の寄与を弱める

対策の基本は、「p から半径 R より遠い物は、遮蔽物と見なさない」というルールです。これを範囲チェック（range check）と呼びます。Crytek の SSAO（2007 年）から使われている古典的な方法です。

式にすると、サンプルの深度と p の深度の差 Δz = |z_p − z_s| に対して、重みを次のように決めます。

<div class="formula">w = smoothstep(0, 1, R / Δz)</div>

Δz が R 以下なら R / Δz は 1 以上になり、smoothstep は 1 に張り付くので、遮蔽として満額で数えます。Δz が R の 2 倍なら重みは 0.5 の smoothstep（約 0.5）、Δz が R の 10 倍ならほぼ 0 です。つまり「近い遮蔽物は全部数え、遠い遮蔽物ほど急に効かなくなる」という振る舞いになります。

`smoothstep` を使うのは、境界の段差を作らないためです。「Δz > R なら 0、そうでなければ 1」という 2 値の切り替えにすると、物体の端で AO が急に切り替わり、ちらついたり輪郭が見えたりします。

```hlsl
float RangeCheck(float z_center, float z_sample, float radius) {
  float dz = abs(z_center - z_sample);
  return smoothstep(0.0, 1.0, radius / max(dz, 1e-4));
}

// サンプルが手前にあれば遮蔽として数える（重み付き）
occlusion += (z_sample < z_center - kBias ? 1.0 : 0.0)
           * RangeCheck(z_center, z_sample, kRadius);
```

この重みは、AO の「見た目の半径」を守る役目もあります。範囲チェックがなければ、半径をパラメータで 0.5 m に設定しても、実際にはもっと遠くの物体まで AO に効いてしまい、パラメータが意味を失うからです。

### 方式ごとの距離の弱め方

範囲チェックの考え方は、どの方式にも形を変えて入っています。

[Alchemy AO](../alchemy-ao.md) や [HBAO](../hbao.md) は、サンプル点までの距離 r に応じた減衰項を式の中に持ちます。HBAO の論文（Bavoil ら、2008）では、W(r) = 1 − (r / R)² のような、R で 0 になる減衰を使って、遠い点の寄与を滑らかに消します。距離が R を超えたサンプルは、地平線の更新自体を行いません。

[GTAO](../gtao.md)（Jimenez ら、2016）は、さらに一歩進めます。遠い遮蔽物を無視するだけでなく、手前の物体には厚みがあると仮定します。地平線を探す途中で、サンプルが遠い（減衰が効く）場合は、地平線を「その遠い物体まで上げる」のではなく、元の値に近いままにして、「壁の手前に立っている薄い物は、壁を全部は隠さない」ように扱います。この仮定は、柱や人物のような「厚みが有限の物」には正しく、「ずっと奥まで続く壁」には少し甘くなる、割り切りです。

### それでも残る問題と、より良いやり方

範囲チェックにも副作用があります。本当に大きな遮蔽物も、遠ければ無視してしまうことです。たとえば、天井が高い部屋で床の AO を取るとき、半径 R を小さくすると、天井が遮蔽に効かなくなります。これは AO が「近くの」遮蔽だけを見る近似であることの、正しい帰結です。遠くの大きな遮蔽は、AO ではなく、シャドウやライトプローブの役目です（[AO の使い方と誤解](../theory/usage-misconceptions.md)）。

ハローを根本から減らすための選択肢を、効果の大きい順に挙げます。

1. 半径を小さくする。ハローの太さは、おおむね半径に比例します。ゲームでは 0.3〜1 m 程度が普通です。
2. バイラテラル ブラーで輪郭をまたがない。ぼかしが輪郭を越えて平均すると、ハローが広がります。深度と法線の差で重みを落とします。
3. GTAO の厚みヒューリスティックを使う。上で述べた、手前の物体の厚みを有限と仮定する方法です。
4. レイトレース AO を使う（[RTAO](../world-space/rtao.md)）。レイは実際に空間を進むので、「深度が離れているだけ」の誤判定が起きません。最大距離 R で打ち切るだけで、ハローはほぼ出ません。
5. 2 層の深度を持つ。手前の面の「裏側」の深度（depth peeling で得る 2 枚目）も使えば、手前の物体の厚みを実測できます。コストが高いので、実際のゲームではほとんど使われません。

## 確認の手順

ハローを直すときは、まず<strong>AO だけを画面に出して</strong>、輪郭の周りを見ます。人物の頭の周りに、背景側へ帯状の暗い領域が見えたら、ハローです。次に、半径のパラメータを半分にして、帯の幅が半分になるかを確かめます。幅が半径に比例していれば、原因は範囲チェックの不足です。幅が変わらなければ、ブラーが輪郭をまたいでいる可能性が高いので、ブラー前の AO を出して比べてください。

## よくあるミス

??? failure "輪郭に、黒いハローが出る"
    <strong>範囲チェック（深度差が半径内のときだけ、遮蔽に数える）</strong>を入れる。それでも残るなら、ブラーが輪郭をまたいでいないかを確認する。

??? failure "範囲チェックを入れたら、大きな遮蔽がなくなった"
    範囲チェックは「半径より遠い遮蔽を無視する」仕組みなので、意図どおりの動作。広い範囲の遮蔽は、シャドウやプローブに任せる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 離れた物を遮蔽と誤認するのが原因
    - [x] 範囲チェックで防ぐ

## 参考

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- McGuire, Osman, Bukowski, Hennessy, "The Alchemy Screen-Space Ambient Obscurance Algorithm", High-Performance Graphics 2011
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice

## 関連ページ

- [AO Artifacts](index.md)
- [Self-Occlusion](self-occlusion.md)
- [Hemisphere SSAO](../ssao-hemisphere.md)
