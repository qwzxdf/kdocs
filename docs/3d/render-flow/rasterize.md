---
title: ラスタライズ
tags:
  - 3Dゲーム
  - 描画
---

# ラスタライズ

**ここまでで三角形は「画面の座標が決まった 3 つの点」になりました**。**次の工程はその三角形が画面のどのピクセルを覆っているか**を**見つけること**です。これが**ラスタライズ**です。**3D のデータ（頂点）を、2D のピクセルの集まりに変える**、**描画パイプラインの中核**です。このページでは、**ピクセルの中心で判定するしくみ・辺の式による内外判定・頂点の値の補間（重心座標）・裏面カリング・2×2 のクワッド・MSAA** を説明します。

!!! tip "ポイント"
    - ラスタライズ ＝ <strong>三角形が覆うピクセルを見つけ、ピクセルごとに頂点の値を補間する</strong>。
    - 判定は<strong>ピクセルの中心が三角形の内側か</strong>（<strong>中心が内側ならそのピクセルを描く</strong>）。
    - 内外は<strong>3 本の辺それぞれについて、どちら側か</strong>で決まる（<strong>辺の式</strong>）。
    - 頂点の色・UV・法線は<strong>重心座標</strong>で<strong>ピクセルごとに補間</strong>される。<strong>遠近法に合わせた補正も自動</strong>。
    - <strong>裏向きの三角形</strong>は、<strong>設定で捨てられる（バックフェイス カリング）</strong>。
    - GPU は<strong>2×2 のピクセル（クワッド）単位</strong>で処理する。<strong>細長い三角形は無駄が多い</strong>。

## 三角形をピクセルに分ける

**画面はピクセルの格子**です。**三角形の各ピクセルの「中心」が、三角形の内側にあるかどうか**で**判定します**。**中心が内側なら、そのピクセルは三角形に覆われている**と**みなされます**。

<svg class="fig illust" viewBox="0 0 720 470" role="img" aria-label="ラスタライズの例">
<text x="20" y="24" class="fig-title">16×10 ピクセルの画面と三角形：ピクセルの中心が内側なら塗る（34 個）</text>
<rect x="40" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="280" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="320" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="360" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="40" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="60.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="280" y="80" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="100.0" r="3" fill="#fff"/>
<rect x="320" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="360" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="80" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="100.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="280" y="120" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="140.0" r="3" fill="#fff"/>
<rect x="320" y="120" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="140.0" r="3" fill="#fff"/>
<rect x="360" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="120" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="140.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="160" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="180.0" r="3" fill="#fff"/>
<rect x="280" y="160" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="180.0" r="3" fill="#fff"/>
<rect x="320" y="160" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="180.0" r="3" fill="#fff"/>
<rect x="360" y="160" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="180.0" r="3" fill="#fff"/>
<rect x="400" y="160" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="180.0" r="3" fill="#fff"/>
<rect x="440" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="160" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="180.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="220.0" r="3" fill="#fff"/>
<rect x="280" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="220.0" r="3" fill="#fff"/>
<rect x="320" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="220.0" r="3" fill="#fff"/>
<rect x="360" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="220.0" r="3" fill="#fff"/>
<rect x="400" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="220.0" r="3" fill="#fff"/>
<rect x="440" y="200" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="220.0" r="3" fill="#fff"/>
<rect x="480" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="200" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="220.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="260.0" r="3" fill="#fff"/>
<rect x="240" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="260.0" r="3" fill="#fff"/>
<rect x="280" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="260.0" r="3" fill="#fff"/>
<rect x="320" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="260.0" r="3" fill="#fff"/>
<rect x="360" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="260.0" r="3" fill="#fff"/>
<rect x="400" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="260.0" r="3" fill="#fff"/>
<rect x="440" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="260.0" r="3" fill="#fff"/>
<rect x="480" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="260.0" r="3" fill="#fff"/>
<rect x="520" y="240" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="260.0" r="3" fill="#fff"/>
<rect x="560" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="240" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="260.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="300.0" r="3" fill="#fff"/>
<rect x="200" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="300.0" r="3" fill="#fff"/>
<rect x="240" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="300.0" r="3" fill="#fff"/>
<rect x="280" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="300.0" r="3" fill="#fff"/>
<rect x="320" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="300.0" r="3" fill="#fff"/>
<rect x="360" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="300.0" r="3" fill="#fff"/>
<rect x="400" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="300.0" r="3" fill="#fff"/>
<rect x="440" y="280" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="300.0" r="3" fill="#fff"/>
<rect x="480" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="280" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="300.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="320" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="340.0" r="3" fill="#fff"/>
<rect x="200" y="320" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="340.0" r="3" fill="#fff"/>
<rect x="240" y="320" width="40" height="40" fill="#4c8bf5" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="340.0" r="3" fill="#fff"/>
<rect x="280" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="320" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="360" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="320" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="340.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="280" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="320" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="360" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="360" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="380.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="40" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="60.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="80" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="100.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="120" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="140.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="160" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="180.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="200" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="220.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="240" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="260.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="280" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="300.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="320" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="340.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="360" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="380.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="400" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="420.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="440" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="460.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="480" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="500.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="520" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="540.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="560" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="580.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="600" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="620.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<rect x="640" y="400" width="40" height="40" fill="none" fill-opacity="0.55" stroke="currentColor" stroke-opacity="0.2"/>
<circle cx="660.0" cy="420.0" r="2" fill="currentColor" fill-opacity="0.35"/>
<polygon points="128.0,372.0 576.0,284.0 300.0,96.0" fill="none" stroke="#e5484d" stroke-width="3"/>

<text x="20" y="458" style="font-size:12px">白い点 ＝ 内側のピクセル中心（塗る）　灰色の点 ＝ 外側（塗らない）</text>
</svg>

| 点 | 説明 |
| --- | --- |
| **ピクセルの中心** | <strong>ピクセルの座標 (x, y) の中心は (x + 0.5, y + 0.5)</strong> |
| **境界線上** | **ちょうど辺の上にあるとき、隣り合う三角形の両方で描かれたり、どちらでも描かれなかったりしないよう、決まったルール（トップレフト ルール）で片方に割り当てる** |
| **細い三角形** | **ピクセルの中心を 1 つも覆わない細い三角形は、描かれない**（**線が途切れる原因**） |
| **ジャギー** | **ピクセル単位の判定なので、斜めの線が階段状になる**（[アンチエイリアス](../../graphics/postprocess/index.md)） |

## 内側かどうかの判定（辺の式）

**点が三角形の内側かどうか**は、<strong>3 本の辺それぞれについて「点が辺のどちら側にあるか」</strong>を**調べる**ことで**分かります**。**3 本とも同じ側なら内側**です。

**辺 AB と点 P について**、次の式の**符号**で**どちら側か**が決まります。

<div class="formula">E(P) = (P.x − A.x)(B.y − A.y) − (P.y − A.y)(B.x − A.x)</div>

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="辺の式">
<text x="20" y="24" class="fig-title">3 本の辺の「同じ側」が内側</text>
<polygon points="120,210 360,170 230,50" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/>
<circle cx="240" cy="150" r="6" fill="#2ea043"/><text x="250" y="146" style="font-size:12px">P（内側）</text>
<circle cx="380" cy="80" r="6" fill="#e5484d"/><text x="390" y="76" style="font-size:12px">Q（外側）</text>
<g font-size="12">
<text x="440" y="70" style="font-weight:700">P：3 本の辺で E の符号がすべて同じ → 内側</text>
<text x="440" y="96" style="font-weight:700">Q：1 本の辺で符号が違う → 外側</text>
<text x="440" y="140">・GPU は、この計算を何千ものピクセルで</text><text x="440" y="160">　同時にハードウェアで行う</text>
<text x="440" y="190">・隣のピクセルへの E の増え方は一定</text><text x="440" y="210">　（足し算だけで更新できる）</text>
</g>
</svg>

**E の計算は単純な掛け算と引き算**で、**隣のピクセルへ動くと E は決まった量だけ増減**します。**GPU はこれをハードウェアで一気に行います**。

## 値の補間（重心座標）

**三角形の頂点は、色・UV・法線などの値を持っています**。**内側のピクセルの値は、頂点の値を混ぜて作ります**。<strong>混ぜる割合が「重心座標」</strong>です。

<div class="formula">値(P) = λ₁ · 値(A) + λ₂ · 値(B) + λ₃ · 値(C)　（λ₁ + λ₂ + λ₃ = 1）</div>

| 位置 | λ₁, λ₂, λ₃ |
| --- | --- |
| **頂点 A の上** | <strong>(1, 0, 0)</strong> |
| **辺 AB の真ん中** | <strong>(0.5, 0.5, 0)</strong> |
| **三角形の中心** | <strong>(1/3, 1/3, 1/3)</strong> |

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="重心座標による補間">
<text x="20" y="24" class="fig-title">頂点の色（赤・緑・青）が、ピクセルの位置に応じて混ざる</text>
<polygon points="90,230 330,230 210,50" fill="#fff" fill-opacity="0.04" stroke="currentColor" stroke-opacity="0.6" stroke-width="2"/>
<circle cx="90" cy="230" r="8" fill="#e5484d"/><circle cx="330" cy="230" r="8" fill="#2ea043"/><circle cx="210" cy="50" r="8" fill="#4c8bf5"/>
<text x="60" y="254" style="font-size:12px">A（赤）</text><text x="310" y="254" style="font-size:12px">B（緑）</text><text x="224" y="52" style="font-size:12px">C（青）</text>
<g stroke="#8a8a8a" stroke-dasharray="3 3">
<line x1="150" y1="230" x2="210" y2="170"/><line x1="270" y1="230" x2="210" y2="170"/>
</g>
<circle cx="210" cy="170" r="7" fill="#9664e6" stroke="#fff" stroke-width="2"/>
<text x="224" y="172" style="font-size:12px">P：赤・緑・青が混ざった色</text>
<g font-size="12">
<text x="440" y="90" style="font-weight:700">近い頂点の色ほど強く混ざる</text>
<text x="440" y="116">P が A に近い → 赤が強い</text>
<text x="440" y="140">P が三角形の中心 → 3 色が等しく</text>
<text x="440" y="176" style="font-weight:700">補間されるもの</text>
<text x="440" y="200">色・UV・法線・ワールド位置・深度 …</text>
<text x="440" y="224">（頂点シェーダーの出力のうち SV_POSITION 以外）</text>
</g>
</svg>

### 遠近法に合わせた補間

**単純にピクセルの座標で線形に混ぜる**と、**遠近法のある三角形ではテクスチャが歪んで見えます**。**GPU は奥行き（w）を考慮して補正した、パースペクティブ コレクトな補間**を**自動で**行います。

<div class="formula">値 = ( Σ λᵢ · 値ᵢ / wᵢ ) / ( Σ λᵢ / wᵢ )</div>

**ふだんは意識しなくてよい**ですが、**補間をやめたいときは `nointerpolation`、画面空間の線形補間にしたいときは `noperspective`** を**HLSL で指定できます**。

```hlsl
struct VSOutput {
  float4 position : SV_POSITION;
  float2 uv : TEXCOORD0;
  nointerpolation uint material_id : TEXCOORD1;
};
```

## 裏面カリング

**閉じたモデル（球・箱・キャラクター）は、裏側の面は手前の面に隠れて見えません**。**カメラに背を向けた三角形を早めに捨てる**と、**ピクセル シェーダーの無駄が減ります**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="裏面カリング">
<text x="20" y="24" class="fig-title">画面から見て時計回り ＝ 表、反時計回り ＝ 裏（左手系）</text>
<g transform="translate(80,60)">
<polygon points="0,110 60,10 120,110" fill="#2ea043" fill-opacity="0.3" stroke="#2ea043" stroke-width="2"/>
<text x="-4" y="130" style="font-size:12px">0</text><text x="52" y="2" style="font-size:12px">1</text><text x="122" y="130" style="font-size:12px">2</text>
<text x="0" y="160" style="font-size:12px">0→1→2 が時計回り ＝ 表（描く）</text>
</g>
<g transform="translate(400,60)">
<polygon points="0,110 120,110 60,10" fill="#e5484d" fill-opacity="0.3" stroke="#e5484d" stroke-width="2"/>
<text x="-4" y="130" style="font-size:12px">0</text><text x="122" y="130" style="font-size:12px">1</text><text x="52" y="2" style="font-size:12px">2</text>
<text x="0" y="160" style="font-size:12px">0→1→2 が反時計回り ＝ 裏（捨てる）</text>
</g>
</svg>

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.FillMode = D3D11_FILL_SOLID;
desc.CullMode = D3D11_CULL_BACK;
desc.FrontCounterClockwise = FALSE;
desc.DepthClipEnable = TRUE;
device->CreateRasterizerState(&desc, rasterizer_state.GetAddressOf());
context->RSSetState(rasterizer_state.Get());
```

| 設定 | 意味 |
| --- | --- |
| **`CULL_BACK`** | **裏向きを捨てる**（標準） |
| **`CULL_FRONT`** | **表向きを捨てる**（アウトラインの裏面膨らませ法など） |
| **`CULL_NONE`** | **両面描く**（葉・布・薄い板） |
| **`FrontCounterClockwise`** | **FALSE ＝ 時計回りが表**（このサイトの左手系） |
| **`FILL_WIREFRAME`** | **ワイヤーフレーム**（デバッグ） |

**頂点の並びの向きは、頂点インデックスの順で決まる**ので、**モデルを作る・読み込むときに揃えます**（右手系のモデルは 2 番目と 3 番目を入れ替える）。

## 2×2 のクワッド

**GPU はピクセルを 1 個ずつでなく、2×2 の 4 個のまとまり（クワッド）で処理**します。**隣のピクセルとの値の差から、テクスチャのミップ レベルを選ぶ**ためです（[ピクセルの色](pixel-shader.md)）。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="クワッド">
<text x="20" y="24" class="fig-title">2×2 のクワッド：三角形の端では、覆っていないピクセルも計算される</text>
<g transform="translate(60,50)">
<g stroke="currentColor" stroke-opacity="0.25" fill="none">
<rect x="0" y="0" width="40" height="40"/><rect x="40" y="0" width="40" height="40"/><rect x="80" y="0" width="40" height="40"/><rect x="120" y="0" width="40" height="40"/><rect x="160" y="0" width="40" height="40"/>
<rect x="0" y="40" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/><rect x="80" y="40" width="40" height="40"/><rect x="120" y="40" width="40" height="40"/><rect x="160" y="40" width="40" height="40"/>
<rect x="0" y="80" width="40" height="40"/><rect x="40" y="80" width="40" height="40"/><rect x="80" y="80" width="40" height="40"/><rect x="120" y="80" width="40" height="40"/><rect x="160" y="80" width="40" height="40"/>
<rect x="0" y="120" width="40" height="40"/><rect x="40" y="120" width="40" height="40"/><rect x="80" y="120" width="40" height="40"/><rect x="120" y="120" width="40" height="40"/><rect x="160" y="120" width="40" height="40"/>
</g>
<g fill="#4c8bf5" fill-opacity="0.6"><rect x="0" y="120" width="40" height="40"/><rect x="40" y="120" width="40" height="40"/><rect x="80" y="120" width="40" height="40"/><rect x="40" y="80" width="40" height="40"/><rect x="80" y="80" width="40" height="40"/><rect x="80" y="40" width="40" height="40"/></g>
<g fill="#e5484d" fill-opacity="0.3"><rect x="0" y="80" width="40" height="40"/><rect x="40" y="40" width="40" height="40"/><rect x="120" y="120" width="40" height="40"/><rect x="120" y="80" width="40" height="40"/><rect x="120" y="40" width="40" height="40"/></g>
<polygon points="0,160 130,160 82,32" fill="none" stroke="currentColor" stroke-width="2"/>
<rect x="0" y="80" width="80" height="80" fill="none" stroke="#e5aa28" stroke-width="3"/>
</g>
<g font-size="12">
<text x="330" y="80" style="font-weight:700">青 ＝ 三角形が覆うピクセル</text>
<text x="330" y="104" style="font-weight:700;fill:#e5484d">赤 ＝ 覆っていないが、クワッドの一部なので計算される（捨てる）</text>
<text x="330" y="140">・黄色い枠が 1 つのクワッド（2×2 の 4 ピクセル）</text>
<text x="330" y="164">・クワッドが一部しか覆われないと、計算のムダになる</text>
<text x="330" y="196" style="font-weight:700">細長い三角形・小さい三角形は効率が悪い</text>
<text x="330" y="220">→ 小さな三角形を大量に描くと、ピクセル シェーダーが空回り</text>
</g>
</svg>

| 点 | 説明 |
| --- | --- |
| **ヘルパー ピクセル** | **覆っていないがクワッド計算のために動くピクセル**。**結果は捨てる** |
| **小さい三角形に弱い** | **1 ピクセル未満の三角形でも、4 ピクセル分のシェーダーが走る** |
| **LOD が必要** | **遠くのモデルは、頂点数を減らす**（[LOD](../../rendering/lod.md)） |

## MSAA（マルチサンプル アンチエイリアス）

**ピクセル 1 個につき複数のサンプル点（4 個・8 個）を持ち、辺をまたぐピクセルだけ細かく判定する**のが**MSAA** です。**ピクセル シェーダーは 1 ピクセルにつき 1 回**で、**覆っているサンプル点の数に応じて、辺の色が滑らかになります**。

| 項目 | 内容 |
| --- | --- |
| **サンプル数** | **2・4・8 個**。**多いほど滑らか、メモリと帯域を消費** |
| **効く場所** | **三角形の外周（辺）のジャギー** |
| **効かない場所** | **テクスチャ内のちらつき・ピクセル シェーダー内の高周波** |
| **ディファードと相性が悪い** | **G バッファに複数サンプルが必要で重い**（[フォワードとディファード](../../rendering/forward-deferred.md)） |

## ラスタライズが見える失敗

| 見た目 | 原因 |
| --- | --- |
| **面が消える** | **頂点の並びが逆（裏面）でカリングされている** |
| **斜めの線が階段状** | **ピクセル判定の限界**。**アンチエイリアスで緩和** |
| **細い物が途切れる** | **ピクセルの中心を覆わない** |
| **遠くがちらつく** | **サブピクセルの動きで判定が変わる**（**TAA・MSAA で緩和**） |
| **画面の端で歪む** | **視野角が大きすぎる** |

## よくあるミス

??? failure "モデルの表と裏が逆で、中身が見える"
    **三角形の頂点の順（巻き方向）を直す**、**または `FrontCounterClockwise` を切り替える**。

??? failure "薄い板（葉・布）が片面しか見えない"
    **`CULL_NONE`（両面描画）にする**。**裏面は法線を反転**。

??? failure "細い三角形が多く、ピクセル シェーダーが重い"
    **LOD で頂点を減らし、細長い三角形を作らないモデリング**にする。

??? failure "補間した法線を、そのままライティングに使って暗くなる"
    **補間すると長さが 1 でなくなる**。**ピクセル シェーダーで正規化する**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ラスタライズ ＝ <strong>三角形が覆うピクセルを見つけ、頂点の値を補間する</strong>
    - [x] 判定は<strong>ピクセルの中心が内側か</strong>。<strong>辺の式</strong>の符号で決まる
    - [x] 値は<strong>重心座標</strong>で混ぜる。<strong>遠近法の補正は自動</strong>
    - [x] <strong>時計回りが表</strong>（左手系）。<strong>裏はカリングで捨てられる</strong>
    - [x] <strong>2×2 のクワッド単位</strong>。<strong>小さい・細い三角形は効率が悪い</strong>

## 参考

- Juan Pineda, "A Parallel Algorithm for Polygon Rasterization"（SIGGRAPH 1988）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 6, 7）
- Microsoft, "Rasterization Rules"（Microsoft Learn）

## 関連ページ

- [描画の流れ（入門）](index.md)
- [クリップと画面への写し](clip-viewport.md)
- [ピクセルの色](pixel-shader.md)
- [深度・ブレンド](output-merger.md)
- [メッシュとテクスチャ](../mesh-textures.md)
