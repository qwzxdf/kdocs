---
title: Gaussian Blur
tags:
  - 描画
---

# Gaussian Blur

**ガウスぼかし**は、**画像処理でもっとも基本的なぼかし**で、**ブルームをはじめ、DOF・SSAO のぼかしなど**、**あらゆる所**で**使われます**。**中心が重く、離れるほど滑らかに軽くなる重み**で**周りを平均**するので、**自然でムラのないぼかし**になります。このページでは、**ガウス関数・分離可能性（横 → 縦の 2 パス）・バイリニアを使ったタップ数の半減・重みの作り方・カーネル サイズの決め方**を説明します。

!!! tip "ポイント"
    - ガウスぼかし ＝ <strong>ガウス関数（釣り鐘）の重みで周りの画素を平均する</strong>。
    - <strong>分離可能</strong>：<strong>2D の (2R+1)² タップを横 1D → 縦 1D の 2 パス（2×(2R+1) タップ）</strong>にできる。
    - <strong>バイリニア補間を利用</strong>すると、<strong>2 タップを 1 回の読み込みにまとめられ、タップ数が約半分</strong>になる。
    - <strong>σ（標準偏差）</strong>が<strong>ぼかしの強さ</strong>。<strong>カーネルの半径は 3σ 程度</strong>で十分。
    - <strong>重みは合計 1 に正規化</strong>（<strong>明るさを保つ</strong>）。
    - <strong>ブルームでは、縮小した画像にかける</strong>ので、<strong>小さなカーネル（5〜9 タップ）で済む</strong>。

## The Gaussian Function {#ガウス関数}

<div class="formula">G(x) = (1 / (σ√(2π))) · exp( −x² / (2σ²) )</div>

**中心が最大で離れるほど急速に小さくなる**釣り鐘形です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="ガウス関数">
<text x="20" y="26" class="fig-title">ガウスの重み：σ が大きいほど、広く平らになる</text>
<line x1="80" y1="200" x2="700" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="390" y1="50" x2="390" y2="200" stroke="currentColor" stroke-opacity="0.3" stroke-dasharray="4 4"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="80,198 150,196 220,185 280,150 330,100 370,66 390,60 410,66 450,100 500,150 560,185 630,196 700,198"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,199 150,198 220,196 280,190 330,178 370,168 390,166 410,168 450,178 500,190 560,196 630,198 700,199"/>
<text x="470" y="80" style="font-size:12px;fill:#2563eb">σ 小：中心に集中（弱いぼかし）</text>
<text x="470" y="150" style="font-size:12px;fill:#e5484d">σ 大：広く平ら（強いぼかし）</text>
<text x="390" y="224" text-anchor="middle" style="font-size:12px">中心からの距離 →</text>
</svg>

## Separability {#分離可能性}

**2D のガウスは、横の 1D ガウス × 縦の 1D ガウス**に**分解できます**。**そこで、「横方向にぼかす」→「縦方向にぼかす」の 2 パス**に**分ける**と、**タップ数が大幅に減ります**。

タップ数の比較です。2D のまま直接ぼかすと、(2R+1)² 回で、R=8 なら 289 回です。分離（横→縦）すれば 2 × (2R+1) 回で、R=8 なら 34 回です。分離できる性質のおかげで、約 8.5 倍も減ります。

<!-- fig:gaussian-separable:begin -->

<svg class="fig illust motion" data-fig="gaussian-separable" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gaussian-separable" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">分離可能なガウス: 2 次元のぼかしを、横 1 回 + 縦 1 回に分けると、同じ結果で、読み込みが半径に比例するだけになる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">12×12 画素に光源を 1 つ。半径 4(9×9 = 81 タップ)の 2 次元ガウスと、横 9 + 縦 9 の 2 回を、比べる</text>
<rect x="30" y="100" width="208.0" height="208.0" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 入力</text>
<rect x="32.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="151.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fff4b8"/></rect>
<rect x="100.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="32.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="49.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="66.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="83.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="100.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="117.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="134.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="151.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="168.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="185.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="202.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="219.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="335" y="100" width="208.0" height="208.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">② 横にぼかす(9 タップ)</text>
<rect x="337.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#0f172a;#353a41"/></rect>
<rect x="388.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#83826f"/></rect>
<rect x="405.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#dcd4a3"/></rect>
<rect x="422.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#0f172a;#fff4b8"/></rect>
<rect x="439.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#0f172a;#fff4b8"/></rect>
<rect x="456.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#fff4b8"/></rect>
<rect x="473.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#0f172a;#dcd4a3"/></rect>
<rect x="490.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#0f172a;#83826f"/></rect>
<rect x="507.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#353a41"/></rect>
<rect x="524.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#535652"/></rect>
<rect x="354.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#9b987d"/></rect>
<rect x="371.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#0f172a;#d2ca9d"/></rect>
<rect x="388.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#0f172a;#e4dca8"/></rect>
<rect x="405.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#d2ca9d"/></rect>
<rect x="422.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#0f172a;#9b987d"/></rect>
<rect x="439.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#0f172a;#535652"/></rect>
<rect x="456.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#232936"/></rect>
<rect x="473.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="337.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="354.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="371.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="388.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="405.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="422.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="439.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="456.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="473.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="490.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="507.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="524.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="640" y="100" width="208.0" height="208.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">③ さらに縦にぼかす(9 タップ)</text>
<rect x="642.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="659.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="676.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="693.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="710.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="727.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="744.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="761.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="778.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="795.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="812.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="829.0" y="102.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="659.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="676.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="693.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#0f172a;#11192b"/></rect>
<rect x="710.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#0f172a;#141b2d"/></rect>
<rect x="727.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#181f2f"/></rect>
<rect x="744.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#192030"/></rect>
<rect x="761.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#181f2f"/></rect>
<rect x="778.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#141b2d"/></rect>
<rect x="795.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#11192b"/></rect>
<rect x="812.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="829.0" y="119.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="659.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="676.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#0f172a;#11192b"/></rect>
<rect x="693.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#0f172a;#161d2e"/></rect>
<rect x="710.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#212835"/></rect>
<rect x="727.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#2e343d"/></rect>
<rect x="744.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#343940"/></rect>
<rect x="761.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#2e343d"/></rect>
<rect x="778.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#212835"/></rect>
<rect x="795.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#161d2e"/></rect>
<rect x="812.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#11192b"/></rect>
<rect x="829.0" y="136.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="659.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="676.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#0f172a;#141b2d"/></rect>
<rect x="693.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#212835"/></rect>
<rect x="710.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#3c4044"/></rect>
<rect x="727.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#585b55"/></rect>
<rect x="744.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#65665d"/></rect>
<rect x="761.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#585b55"/></rect>
<rect x="778.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#3c4044"/></rect>
<rect x="795.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#212835"/></rect>
<rect x="812.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#141b2d"/></rect>
<rect x="829.0" y="153.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#0f172a;#10182b"/></rect>
<rect x="659.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#0f172a;#11192b"/></rect>
<rect x="676.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#1c2331"/></rect>
<rect x="693.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#33383f"/></rect>
<rect x="710.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#5b5d57"/></rect>
<rect x="727.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#83816e"/></rect>
<rect x="744.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#929078"/></rect>
<rect x="761.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#82806e"/></rect>
<rect x="778.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#585b55"/></rect>
<rect x="795.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#2e343d"/></rect>
<rect x="812.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#181f2f"/></rect>
<rect x="829.0" y="170.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#0f172a;#131a2c"/></rect>
<rect x="659.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#18202f"/></rect>
<rect x="676.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#292f39"/></rect>
<rect x="693.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#45484a"/></rect>
<rect x="710.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#6f6f63"/></rect>
<rect x="727.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#96937a"/></rect>
<rect x="744.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#a4a182"/></rect>
<rect x="761.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#929078"/></rect>
<rect x="778.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#65665d"/></rect>
<rect x="795.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#343940"/></rect>
<rect x="812.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#192030"/></rect>
<rect x="829.0" y="187.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#0f172a;#18202f"/></rect>
<rect x="659.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#272d38"/></rect>
<rect x="676.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#3e4346"/></rect>
<rect x="693.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#575a55"/></rect>
<rect x="710.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#737365"/></rect>
<rect x="727.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#8d8b75"/></rect>
<rect x="744.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#96937a"/></rect>
<rect x="761.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#83816e"/></rect>
<rect x="778.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#585b55"/></rect>
<rect x="795.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#2e343d"/></rect>
<rect x="812.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#181f2f"/></rect>
<rect x="829.0" y="204.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#0f172a;#1f2634"/></rect>
<rect x="659.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#383c42"/></rect>
<rect x="676.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#555854"/></rect>
<rect x="693.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#696a5f"/></rect>
<rect x="710.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#717164"/></rect>
<rect x="727.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#737365"/></rect>
<rect x="744.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#6f6f63"/></rect>
<rect x="761.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#5b5d57"/></rect>
<rect x="778.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#3c4044"/></rect>
<rect x="795.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#212835"/></rect>
<rect x="812.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#0f172a;#141b2d"/></rect>
<rect x="829.0" y="221.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#232936"/></rect>
<rect x="659.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#3f4347"/></rect>
<rect x="676.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#5f6159"/></rect>
<rect x="693.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#6f6f63"/></rect>
<rect x="710.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#696a5f"/></rect>
<rect x="727.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#575a55"/></rect>
<rect x="744.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#45484a"/></rect>
<rect x="761.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#33383f"/></rect>
<rect x="778.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#212835"/></rect>
<rect x="795.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#0f172a;#161d2e"/></rect>
<rect x="812.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#0f172a;#11192b"/></rect>
<rect x="829.0" y="238.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#0f172a;#1f2634"/></rect>
<rect x="659.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#383c42"/></rect>
<rect x="676.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#535552"/></rect>
<rect x="693.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#5f6159"/></rect>
<rect x="710.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#555854"/></rect>
<rect x="727.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#3e4346"/></rect>
<rect x="744.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#292f39"/></rect>
<rect x="761.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#1c2331"/></rect>
<rect x="778.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#0f172a;#141b2d"/></rect>
<rect x="795.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#0f172a;#11192b"/></rect>
<rect x="812.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="829.0" y="255.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#0f172a;#18202f"/></rect>
<rect x="659.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#272d38"/></rect>
<rect x="676.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#383c42"/></rect>
<rect x="693.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#3f4347"/></rect>
<rect x="710.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#383c42"/></rect>
<rect x="727.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#272d38"/></rect>
<rect x="744.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#18202f"/></rect>
<rect x="761.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#0f172a;#11192b"/></rect>
<rect x="778.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="795.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="812.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="829.0" y="272.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="642.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#0f172a;#131a2c"/></rect>
<rect x="659.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#0f172a;#18202f"/></rect>
<rect x="676.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#0f172a;#1f2634"/></rect>
<rect x="693.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#0f172a;#232936"/></rect>
<rect x="710.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#0f172a;#1f2634"/></rect>
<rect x="727.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#0f172a;#18202f"/></rect>
<rect x="744.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#0f172a;#131a2c"/></rect>
<rect x="761.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#0f172a;#10182b"/></rect>
<rect x="778.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="795.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="812.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="829.0" y="289.0" width="17.3" height="17.3" fill="#0f172a"/>
<rect x="30" y="340" width="900" height="130" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="330" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">読み込みの数</text>
<text x="50" y="394" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">2 次元のまま(9×9)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;1.0000" values="0;0;1;1"/></text>
<rect x="300" y="380" width="1" height="22" fill="#e5484d" opacity="0.85"><animate attributeName="width" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4889;0.5422;1.0000" values="1;1;300;300"/></rect>
<text x="610.0" y="397" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">11,664 回(1 画素あたり 81)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5420;0.5422;1.0000" values="0;0;1;1"/></text>
<text x="50" y="424" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">分離(9 + 9)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;1.0000" values="0;0;1;1"/></text>
<rect x="300" y="410" width="1" height="22" fill="#2ea043" opacity="0.85"><animate attributeName="width" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4889;0.5422;1.0000" values="1;1;66.67;66.67"/></rect>
<text x="376.66666666666663" y="427" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">2,592 回(1 画素あたり 18)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5420;0.5422;1.0000" values="0;0;1;1"/></text>
<text x="50" y="458" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">結果の最大の差: 1e-16(同じ結果)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5954;0.5956;1.0000" values="0;0;1;1"/><rect x="660" y="346" width="270" height="130" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="676" y="370" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">半径 32 のぼかしなら</text>
<text x="676" y="393" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">2 次元: 4225 タップ</text>
<text x="676" y="415" text-anchor="start" style="font-size:13px;font-weight:700;fill:#166534">分離: 130 タップ(32 倍少ない)</text>
<text x="676" y="437" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">半径に比例なので、大きなぼかしも安い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ガウス関数は、横と縦に、分けて掛け算できる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">横にぼかして、その結果を縦にぼかす<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">結果は 2 次元のぼかしと、完全に同じ。読み込みは、9 × 9 = 81 から 18 に<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gaussian-separable:end -->

## Implementation (Horizontal and Vertical) {#実装横方向と縦方向}

```hlsl
Texture2D src : register(t0);
SamplerState linear_clamp : register(s0);

cbuffer BlurConstants : register(b0) {
  float2 direction;
  float2 texel_size;
};

static const int kRadius = 4;
static const float kWeights[kRadius + 1] = { 0.2270270, 0.1945946, 0.1216216, 0.0540541, 0.0162162 };

float4 BlurMain(float4 position : SV_POSITION, float2 uv : TEXCOORD0) : SV_Target {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * kWeights[0];
  for (int i = 1; i <= kRadius; ++i) {
    float2 offset = direction * texel_size * i;
    sum += src.SampleLevel(linear_clamp, uv + offset, 0).rgb * kWeights[i];
    sum += src.SampleLevel(linear_clamp, uv - offset, 0).rgb * kWeights[i];
  }
  return float4(sum, 1.0);
}
```

コードの要点です。`direction` は、横なら (1, 0)、縦なら (0, 1) で、同じシェーダーを 2 回使います。`kWeights` は σ ≒ 2 の 9 タップ（中心 + 片側 4）で、合計は 1 です。中心だけ 1 回、左右は対称に足します。重みが左右対称だからです。

## Halving the Taps with Bilinear {#バイリニアでタップ数を半分に}

**隣り合う 2 画素をちょうど良い位置の 1 回のバイリニア読み込みで**まとめられます。**2 画素の重み w1, w2 と、位置 o1, o2 に対して**：

<div class="formula">
新しい重み = w1 + w2<br>
新しい位置 = (o1·w1 + o2·w2) / (w1 + w2)
</div>

バイリニアを利用すると、タップ数をさらに減らせます。元の 9 タップは、位置が 0、±1、±2、±3、±4 で、重みが 0.227、0.195、0.122、0.054、0.016 です。これを、バイリニア補間の特性を使って、隣り合う 2 つのタップを 1 回の読み込みにまとめると、位置が 0、±1.385、±3.231 の 5 タップになり、重みが 0.227、0.316、0.070 になります。ハードウェアが 2 画素を重み付きで混ぜてくれるので、読み込み回数が約半分になります。

```hlsl
static const float kOffsets[3] = { 0.0, 1.3846153846, 3.2307692308 };
static const float kLinearWeights[3] = { 0.2270270270, 0.3162162162, 0.0702702703 };

float4 BlurLinear(float4 position : SV_POSITION, float2 uv : TEXCOORD0) : SV_Target {
  float3 sum = src.SampleLevel(linear_clamp, uv, 0).rgb * kLinearWeights[0];
  for (int i = 1; i < 3; ++i) {
    float2 offset = direction * texel_size * kOffsets[i];
    sum += src.SampleLevel(linear_clamp, uv + offset, 0).rgb * kLinearWeights[i];
    sum += src.SampleLevel(linear_clamp, uv - offset, 0).rgb * kLinearWeights[i];
  }
  return float4(sum, 1.0);
}
```

**9 タップが 5 回の読み込み**で**済みます**（**約 55 %**）。**ただし、精度（FP16 のフォーマット）やフィルタ可能なフォーマットが条件**です。

## σ and Kernel Size {#σ-とカーネル-サイズ}

σ とカーネルの大きさの目安です。半径 R は約 3σ にします（それ以降はほぼ 0 です）。σ は、ぼかしたい広さ（画素）を 2〜3 で割った値にします。重みの合計は 1 に正規化して、明るさが変わらないようにします。

**重みを作る**簡単な方法（C++）：

```cpp
std::vector<float> GaussianWeights(int radius, float sigma) {
  std::vector<float> w(radius + 1);
  float sum = 0.0f;
  for (int i = 0; i <= radius; ++i) {
    w[i] = std::exp(-(i * i) / (2.0f * sigma * sigma));
    sum += (i == 0) ? w[i] : 2.0f * w[i];
  }
  for (float& v : w) v /= sum;
  return w;
}
```

## Using It for Bloom {#ブルームでの使い方}

<strong>ブルームでは縮小した画像（1/2〜1/64）に、小さなカーネル（5〜9 タップ）</strong>で**ぼかします**。**元の解像度では、広い範囲**になるので**ガウスの半径が小さくても、十分なにじみ**になります。

| 段 | 解像度 | カーネル |
| --- | --- | --- |
| **1/2** | **960×540** | **9 タップ** |
| **1/8** | **240×135** | **5〜9 タップ** |
| **1/32** | **60×34** | **5 タップ** |

**縮小とぼかしを同時に行う方式**が<strong>[Dual Filter](dual-filter.md)</strong> です。

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **分離 ＋ バイリニアで読み込み** | **タップ数を最小に** |
| **共有メモリで読み込みを再利用**（コンピュート） | **隣接スレッドが同じ画素を何度も読むのを避ける** |
| **縮小した画像にかける** | **カーネルを小さくできる**（[ダウンサンプル](downsample.md)） |
| **ガンマ・HDR に注意** | **リニアな HDR 値でぼかす**（ガンマ空間でぼかすと暗くなる） |
| **端の処理** | **`clamp` で端を延ばす**（**黒が混ざらないように**） |

## Common Mistakes {#よくあるミス}

??? failure "ぼかしたら、画面全体が暗く（明るく）なった"
    **重みの合計が 1 でない**。**正規化**する。

??? failure "横と縦で、ぼかし具合が違う"
    **横・縦の `texel_size` が、幅・高さの逆数になっているか**を確認。**非正方形ピクセル**にも注意。

??? failure "画面の端が黒くにじむ"
    <strong>サンプラーを `clamp`（端を延ばす）</strong>にする。**`border`（黒）は使わない**。

??? failure "ガンマ空間（LDR）でぼかして、暗くなる"
    **リニアでぼかす**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] ガウス ＝ <strong>釣り鐘の重みで周りを平均</strong>。<strong>σ が強さ、半径は 3σ</strong>
    - [x] <strong>分離</strong>（横 → 縦の 2 パス）で<strong>タップ数が大幅に減る</strong>
    - [x] <strong>バイリニア利用</strong>で<strong>さらに約半分</strong>
    - [x] <strong>重みの合計は 1</strong>。<strong>端は clamp</strong>
    - [x] ブルームでは<strong>縮小した画像に、小さなカーネル</strong>

## References {#参考}

- Rákos, "Efficient Gaussian blur with linear sampling"（2010）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Gonzalez & Woods, "Digital Image Processing"

## Related Pages {#関連ページ}

- [Bloom](index.md)
- [Downsampling and the Mip Chain](downsample.md)
- [Dual Filter](dual-filter.md)
- [SSAO のぼかし](../../ao/filtering/index.md)
