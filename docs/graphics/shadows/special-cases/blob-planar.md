---
title: Blob and Planar Projected Shadows
tags:
  - 描画
---

# Blob and Planar Projected Shadows

**シャドウ マップが重い・使えない環境（モバイル・遠くの小物）**では、**もっと安い影の技法**を使います。**ブロブ シャドウは、足元に丸い暗い円を置くだけ**、**平面投影シャドウは、物体を地面に押しつぶして黒く描く**方法です。**どちらも、柔らかさや正確さは劣りますが、非常に安い**です。このページでは、**ブロブ・平面投影の仕組みと使いどころ**を説明します。

!!! tip "ポイント"
    - **ブロブ ＝ 足元に、丸いぼかした影の板を置く**。
    - **平面投影 ＝ 物体を、光の向きで地面に投影した形で、黒く描く**。
    - **どちらも、非常に安い**が、**地面が平らな場合のみ**。
    - **モバイル・遠くの小さな物・キャラクターの補助の影**に**使う**。

<!-- fig:blob-planar:begin -->

<svg class="fig illust motion" data-fig="blob-planar" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-blob-planar" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">簡易な影:ブロブ（丸い影）と、平面投影</text>
<text x="190" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ブロブ:高さで、大きさと濃さを変える</text>
<rect x="40" y="310" width="300" height="14" fill="#d6c7a1"/>
<ellipse cx="190" cy="316" rx="34" ry="8" fill="#000000" fill-opacity="0.6"><animate attributeName="rx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="34;34;34;60;34;34;34"/><animate attributeName="fill-opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="0.6;0.6;0.6;0.18;0.6;0.6;0.6"/></ellipse>
<circle cx="190" cy="300" r="22" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cy" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.2500;0.4167;0.5833;0.7500;1.0000" values="300;300;300;140;300;300;300"/></circle>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">地面にいる:小さく濃い影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;1.0000" values="1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ジャンプ…<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;0.4163;0.4167;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高い:大きく薄い影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4163;0.4167;0.5830;0.5833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">着地:また小さく濃い<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5830;0.5833;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="570" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">平面投影:行列で、地面に押しつぶす</text>
<rect x="420" y="310" width="300" height="14" fill="#d6c7a1"/>
<polygon points="530,220 590,220 590,280 530,280" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<polygon points="0,0 0,0 0,0 0,0" fill="#000000" fill-opacity="0.5"><animate attributeName="points" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.3333;0.6667;0.9583;1.0000" values="0,0 0,0 0,0 0,0;0,0 0,0 0,0 0,0;542.35,310 696.36,310 696.36,316 542.35,316;542.35,310 696.36,310 696.36,316 542.35,316;415.45,310 575.88,310 575.88,316 415.45,316;415.45,310 575.88,310 575.88,316 415.45,316;415.45,310 575.88,310 575.88,316 415.45,316"/></polygon>
<circle cx="460" cy="110" r="12" fill="#e5aa28"><animate attributeName="cx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.3333;0.6667;0.9583;1.0000" values="460;460;460;670;670;670"/></circle>
<text x="420" y="360" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937" opacity="0">光の向きに沿って、物の頂点を地面へ投影した所が、影<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">どちらもシャドウ マップなしで描ける、安い影。地面が平らな場合に有効（段差や他の物には落ちない）。</text>
</svg>

<!-- fig:blob-planar:end -->

## ブロブ シャドウ（丸い影）
**足元に柔らかい丸い暗い画像**（**ブロブ**）を、**地面に貼る**だけの影です。**シャドウ マップなし**で、**最も安く**、<strong>「地面に接している」感じ</strong>を出せます。

ブロブ シャドウの特徴です。実装は、地面に丸いグラデーションの四角形（デカール）を、キャラクターの足元に置くだけです。高さに応じて薄く、大きくします（ジャンプ中は薄くぼける）。利点は非常に安いことで、モバイルや多数のキャラクターに向きます。欠点は、形が丸いだけで光の方向や物の形を反映しないことと、傾斜地で浮いて見えることです。

**ブロブ ＋ 本格的な影**を組み合わせ、**近くは本格、遠くはブロブ**のように<strong>切り替える（LOD）</strong>ことも一般的です。

## 平面投影シャドウ
**物体のジオメトリを、「地面の平面」に押し潰す**行列を**かけて**描き、**暗い単色**で塗ります。

<div class="formula">平面 n·x + d = 0 へ、光の方向 L に沿って投影する行列（4×4）</div>

```cpp
XMVECTOR plane = XMVectorSet(0, 1, 0, 0);
XMVECTOR light = XMVectorSet(light_dir.x, light_dir.y, light_dir.z, 0);
XMMATRIX shadow_matrix = XMMatrixShadow(plane, XMVectorNegate(light));
```

平面投影シャドウの特徴です。`XMMatrixShadow` は DirectXMath の関数で、平面と光の方向から投影行列を作ります。物体を `shadow_matrix` で変換して、黒（半透明）で描きます。平面と同じ高さになるので、Z ファイティングを避けるため、少しオフセットするか、ステンシルで二重描画を防ぎます。利点は、形が正確で、シャドウ マップが不要なことです。欠点は、平らな床のみで、他の物への影や自己影は不可なこと、ハード エッジになることです。

**古い手法**ですが**平らな床のゲーム**（スポーツ・シンプルな 3D）では今でも**有効**です。

## よくあるミス

??? failure "段差のある地面で、平面投影の影が空中に浮く"
    **平らな地面でのみ使う**、または**シャドウ マップに切り替え**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ブロブ・平面投影は、非常に安い影**
    - [x] **平らな地面向き**。**モバイル・遠景向き**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Special Cases](index.md)
- [Distance Field Shadows](../sdf-shadows.md)
- [Contact Shadows](../contact-shadows.md)
