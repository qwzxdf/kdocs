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

<!-- fig:raster-sweep:begin -->

<svg class="fig illust motion" data-fig="raster-sweep" viewBox="0 0 780 450" role="img"><rect x="0" y="0" width="780" height="450" rx="14" fill="#ffffff"/>
<defs><marker id="arr-raster-sweep" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ラスタライズ:ピクセルの中心が三角形の内側かを、1 つずつ調べる</text>
<rect x="20" y="56" width="560" height="336" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="48" y1="56" x2="48" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="76" y1="56" x2="76" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="104" y1="56" x2="104" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="132" y1="56" x2="132" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="160" y1="56" x2="160" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="188" y1="56" x2="188" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="216" y1="56" x2="216" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="244" y1="56" x2="244" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="272" y1="56" x2="272" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="300" y1="56" x2="300" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="328" y1="56" x2="328" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="356" y1="56" x2="356" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="384" y1="56" x2="384" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="412" y1="56" x2="412" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="440" y1="56" x2="440" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="468" y1="56" x2="468" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="496" y1="56" x2="496" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="524" y1="56" x2="524" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="552" y1="56" x2="552" y2="392" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="84" x2="580" y2="84" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="112" x2="580" y2="112" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="140" x2="580" y2="140" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="168" x2="580" y2="168" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="196" x2="580" y2="196" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="224" x2="580" y2="224" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="252" x2="580" y2="252" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="280" x2="580" y2="280" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="308" x2="580" y2="308" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="336" x2="580" y2="336" stroke="#e2e8f0" stroke-width="1"/>
<line x1="20" y1="364" x2="580" y2="364" stroke="#e2e8f0" stroke-width="1"/>
<rect x="245" y="113" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1841;0.1845;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="113" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1865;0.1868;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="141" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2286;0.2290;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="141" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2310;0.2314;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="141" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2333;0.2337;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="141" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2357;0.2360;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2755;0.2759;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2778;0.2782;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2802;0.2805;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2825;0.2829;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="329" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2849;0.2852;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="357" y="169" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2872;0.2876;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="189" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3200;0.3204;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3223;0.3227;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3247;0.3250;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3270;0.3274;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3294;0.3297;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="329" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3321;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="357" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3341;0.3344;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="385" y="197" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3364;0.3368;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="189" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3668;0.3672;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3692;0.3695;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3719;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3739;0.3742;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3762;0.3766;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="329" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3786;0.3789;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="357" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3809;0.3813;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="385" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3832;0.3836;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="413" y="225" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3856;0.3859;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="161" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4114;0.4117;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="189" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4137;0.4141;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4160;0.4164;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4184;0.4187;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4207;0.4211;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4231;0.4234;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="329" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4254;0.4258;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="357" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4277;0.4281;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="385" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4301;0.4305;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="413" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4324;0.4328;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="441" y="253" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4348;0.4351;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="133" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4559;0.4562;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="161" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4582;0.4586;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="189" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4605;0.4609;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="217" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4629;0.4632;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="245" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4652;0.4656;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="273" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4676;0.4679;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="301" y="281" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4699;0.4703;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="133" y="309" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5027;0.5031;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="161" y="309" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5050;0.5054;1.0000" values="0;0;0.75;0.75"/></rect>
<rect x="189" y="309" width="26" height="26" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5074;0.5077;1.0000" values="0;0;0.75;0.75"/></rect>
<polygon points="109.6,341.6 482.0,263.2 260.8,100.8" fill="none" stroke="#e5484d" stroke-width="3"/>
<circle cx="34.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="286.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="314.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="70.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="286.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="314.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="98.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="126.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1841;0.1845;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="126.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1865;0.1868;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="126.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="154.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2286;0.2290;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="154.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2310;0.2314;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="154.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2333;0.2337;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="154.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2357;0.2360;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="154.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2755;0.2759;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2778;0.2782;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2802;0.2805;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2825;0.2829;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2849;0.2852;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="370.0" cy="182.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2872;0.2876;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="398.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="182.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3200;0.3204;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="230.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3223;0.3227;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3247;0.3250;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3270;0.3274;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3294;0.3297;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3321;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="370.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3341;0.3344;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="398.0" cy="210.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3364;0.3368;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="426.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="210.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3668;0.3672;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="230.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3692;0.3695;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3715;0.3719;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3739;0.3742;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3762;0.3766;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3786;0.3789;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="370.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3809;0.3813;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="398.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3832;0.3836;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="426.0" cy="238.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3856;0.3859;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="454.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="238.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4114;0.4117;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="202.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4137;0.4141;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="230.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4160;0.4164;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4184;0.4187;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4207;0.4211;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4231;0.4234;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4254;0.4258;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="370.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4277;0.4281;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="398.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4301;0.4305;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="426.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4324;0.4328;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="454.0" cy="266.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4348;0.4351;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="482.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="266.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4559;0.4562;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="174.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4582;0.4586;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="202.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4605;0.4609;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="230.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4629;0.4632;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="258.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4652;0.4656;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="286.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4676;0.4679;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="314.0" cy="294.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4699;0.4703;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="342.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="294.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="322.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5027;0.5031;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="174.0" cy="322.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5050;0.5054;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="202.0" cy="322.0" r="3" fill="#94a3b8"><animate attributeName="fill" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5074;0.5077;1.0000" values="#94a3b8;#94a3b8;#ffffff;#ffffff"/></circle>
<circle cx="230.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="286.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="314.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="322.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="286.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="314.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="350.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="62.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="90.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="118.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="146.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="174.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="202.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="230.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="258.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="286.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="314.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="342.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="370.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="398.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="426.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="454.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="482.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="510.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="538.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="566.0" cy="378.0" r="3" fill="#94a3b8"/>
<circle cx="34.0" cy="70.0" r="9" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="cx" dur="11.1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.0744;0.0768;0.0791;0.0814;0.0838;0.0861;0.0885;0.0908;0.0932;0.0955;0.0978;0.1002;0.1025;0.1049;0.1072;0.1095;0.1119;0.1142;0.1166;0.1189;0.1213;0.1236;0.1259;0.1283;0.1306;0.1330;0.1353;0.1377;0.1400;0.1423;0.1447;0.1470;0.1494;0.1517;0.1541;0.1564;0.1587;0.1611;0.1634;0.1658;0.1681;0.1705;0.1728;0.1751;0.1775;0.1798;0.1822;0.1845;0.1868;0.1892;0.1915;0.1939;0.1962;0.1986;0.2009;0.2032;0.2056;0.2079;0.2103;0.2126;0.2150;0.2173;0.2196;0.2220;0.2243;0.2267;0.2290;0.2314;0.2337;0.2360;0.2384;0.2407;0.2431;0.2454;0.2477;0.2501;0.2524;0.2548;0.2571;0.2595;0.2618;0.2641;0.2665;0.2688;0.2712;0.2735;0.2759;0.2782;0.2805;0.2829;0.2852;0.2876;0.2899;0.2923;0.2946;0.2969;0.2993;0.3016;0.3040;0.3063;0.3086;0.3110;0.3133;0.3157;0.3180;0.3204;0.3227;0.3250;0.3274;0.3297;0.3321;0.3344;0.3368;0.3391;0.3414;0.3438;0.3461;0.3485;0.3508;0.3532;0.3555;0.3578;0.3602;0.3625;0.3649;0.3672;0.3695;0.3719;0.3742;0.3766;0.3789;0.3813;0.3836;0.3859;0.3883;0.3906;0.3930;0.3953;0.3977;0.4000;0.4023;0.4047;0.4070;0.4094;0.4117;0.4141;0.4164;0.4187;0.4211;0.4234;0.4258;0.4281;0.4305;0.4328;0.4351;0.4375;0.4398;0.4422;0.4445;0.4468;0.4492;0.4515;0.4539;0.4562;0.4586;0.4609;0.4632;0.4656;0.4679;0.4703;0.4726;0.4750;0.4773;0.4796;0.4820;0.4843;0.4867;0.4890;0.4914;0.4937;0.4960;0.4984;0.5007;0.5031;0.5054;0.5077;0.5101;0.5124;0.5148;0.5171;0.5195;0.5218;0.5241;0.5265;0.5288;0.5312;0.5335;0.5359;0.5382;0.5405;0.5429;0.5452;0.5476;0.5499;0.5523;0.5546;0.5569;0.5593;0.5616;0.5640;0.5663;0.5686;0.5710;0.5733;0.5757;0.5780;0.5804;0.5827;0.5850;0.5874;0.5897;0.5921;0.5944;0.5968;0.5991;0.6014;0.6038;0.6061;0.6085;0.6108;0.6132;0.6155;0.6178;0.6202;0.6225;0.6249;0.6272;0.6295;0.6319" values="34;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566;34;62;90;118;146;174;202;230;258;286;314;342;370;398;426;454;482;510;538;566"/><animate attributeName="cy" dur="11.1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.0744;0.0768;0.0791;0.0814;0.0838;0.0861;0.0885;0.0908;0.0932;0.0955;0.0978;0.1002;0.1025;0.1049;0.1072;0.1095;0.1119;0.1142;0.1166;0.1189;0.1213;0.1236;0.1259;0.1283;0.1306;0.1330;0.1353;0.1377;0.1400;0.1423;0.1447;0.1470;0.1494;0.1517;0.1541;0.1564;0.1587;0.1611;0.1634;0.1658;0.1681;0.1705;0.1728;0.1751;0.1775;0.1798;0.1822;0.1845;0.1868;0.1892;0.1915;0.1939;0.1962;0.1986;0.2009;0.2032;0.2056;0.2079;0.2103;0.2126;0.2150;0.2173;0.2196;0.2220;0.2243;0.2267;0.2290;0.2314;0.2337;0.2360;0.2384;0.2407;0.2431;0.2454;0.2477;0.2501;0.2524;0.2548;0.2571;0.2595;0.2618;0.2641;0.2665;0.2688;0.2712;0.2735;0.2759;0.2782;0.2805;0.2829;0.2852;0.2876;0.2899;0.2923;0.2946;0.2969;0.2993;0.3016;0.3040;0.3063;0.3086;0.3110;0.3133;0.3157;0.3180;0.3204;0.3227;0.3250;0.3274;0.3297;0.3321;0.3344;0.3368;0.3391;0.3414;0.3438;0.3461;0.3485;0.3508;0.3532;0.3555;0.3578;0.3602;0.3625;0.3649;0.3672;0.3695;0.3719;0.3742;0.3766;0.3789;0.3813;0.3836;0.3859;0.3883;0.3906;0.3930;0.3953;0.3977;0.4000;0.4023;0.4047;0.4070;0.4094;0.4117;0.4141;0.4164;0.4187;0.4211;0.4234;0.4258;0.4281;0.4305;0.4328;0.4351;0.4375;0.4398;0.4422;0.4445;0.4468;0.4492;0.4515;0.4539;0.4562;0.4586;0.4609;0.4632;0.4656;0.4679;0.4703;0.4726;0.4750;0.4773;0.4796;0.4820;0.4843;0.4867;0.4890;0.4914;0.4937;0.4960;0.4984;0.5007;0.5031;0.5054;0.5077;0.5101;0.5124;0.5148;0.5171;0.5195;0.5218;0.5241;0.5265;0.5288;0.5312;0.5335;0.5359;0.5382;0.5405;0.5429;0.5452;0.5476;0.5499;0.5523;0.5546;0.5569;0.5593;0.5616;0.5640;0.5663;0.5686;0.5710;0.5733;0.5757;0.5780;0.5804;0.5827;0.5850;0.5874;0.5897;0.5921;0.5944;0.5968;0.5991;0.6014;0.6038;0.6061;0.6085;0.6108;0.6132;0.6155;0.6178;0.6202;0.6225;0.6249;0.6272;0.6295;0.6319" values="70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;70;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;98;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;126;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;154;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;182;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;210;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;238;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;266;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;294;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;322;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;350;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378;378"/><animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.0717;0.0721;0.6339;0.6342;1.0000" values="0;0;1;1;0;0"/></circle>
<text x="620" y="80" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">調べたピクセル</text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;1.0000" values="1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">20<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">40<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.2099;0.2103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">60<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2099;0.2103;0.2568;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">80<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2568;0.2571;0.3036;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">100<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3036;0.3040;0.3505;0.3508;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">120<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3505;0.3508;0.3973;0.3977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">140<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3973;0.3977;0.4441;0.4445;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">160<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4445;0.4910;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">180<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4910;0.4914;0.5378;0.5382;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">200<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5378;0.5382;0.5847;0.5850;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">220<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5847;0.5850;0.6315;0.6319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="112" text-anchor="start" style="font-size:30px;font-weight:700;fill:#1f2937" opacity="0">240<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.6315;0.6319;1.0000" values="0;0;1;1"/></text>
<text x="620" y="160" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">内側（塗る）</text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;1.0000" values="1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">0<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">0<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.2099;0.2103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2099;0.2103;0.2568;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2568;0.2571;0.3036;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3036;0.3040;0.3505;0.3508;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">20<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3505;0.3508;0.3973;0.3977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">29<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3973;0.3977;0.4441;0.4445;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">40<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4445;0.4910;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">47<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4910;0.4914;0.5378;0.5382;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">50<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5378;0.5382;0.5847;0.5850;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">50<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5847;0.5850;0.6315;0.6319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="192" text-anchor="start" style="font-size:30px;font-weight:700;fill:#2563eb" opacity="0">50<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.6315;0.6319;1.0000" values="0;0;1;1"/></text>
<text x="620" y="232" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">外側（塗らない）</text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="1">0<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;1.0000" values="1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">20<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1162;0.1166;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">40<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.2099;0.2103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">58<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2099;0.2103;0.2568;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">74<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.2568;0.2571;0.3036;0.3040;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">88<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3036;0.3040;0.3505;0.3508;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">100<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3505;0.3508;0.3973;0.3977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">111<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.3973;0.3977;0.4441;0.4445;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">120<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4445;0.4910;0.4914;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">133<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.4910;0.4914;0.5378;0.5382;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">150<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5378;0.5382;0.5847;0.5850;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">170<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.5847;0.5850;0.6315;0.6319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="620" y="264" text-anchor="start" style="font-size:30px;font-weight:700;fill:#64748b" opacity="0">190<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.6315;0.6319;1.0000" values="0;0;1;1"/></text>
<text x="20" y="420" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">白い点 = ピクセルの中心。内側なら青く塗り、外側なら塗らない<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.6429;0.6432;1.0000" values="1;1;0;0"/></text>
<text x="20" y="420" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">内側の 50 個が、このあとピクセルシェーダーで色を計算される<animate attributeName="opacity" dur="11.1s" repeatCount="indefinite" keyTimes="0.0000;0.6429;0.6432;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:raster-sweep:end -->

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
