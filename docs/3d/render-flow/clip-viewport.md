---
title: クリップと画面への写し
tags:
  - 3Dゲーム
  - 描画
---

# クリップと画面への写し

**頂点シェーダーが終わると、頂点はクリップ座標になっています**。**ここから先は、GPU が自動でやる工程**です。**頂点を三角形にまとめ**、**画面の外にはみ出た部分を切り落とし**（クリップ）、**遠近法のための割り算をして**（透視除算）、**画面のピクセル座標に写します**（ビューポート変換）。このページでは、**この 4 つの自動工程**を**図で順に**説明します。

!!! tip "ポイント"
    - 頂点シェーダーの後、GPU が自動で<strong>① 三角形に組み立て → ② クリップ → ③ 透視除算 → ④ ビューポート変換</strong>を行う。
    - <strong>クリップ</strong> ＝ <strong>視錐台の外を切り捨てる</strong>。<strong>-w ≤ x, y ≤ w</strong>、<strong>0 ≤ z ≤ w</strong>（D3D）。
    - <strong>透視除算</strong> ＝ <strong>x, y, z を w で割る</strong>。<strong>これで遠近法</strong>。結果は<strong>NDC（正規化デバイス座標）</strong>。
    - <strong>ビューポート変換</strong> ＝ <strong>NDC をピクセル座標に写す</strong>。<strong>Y の向きが反転する</strong>。
    - <strong>深度（z）</strong>はここで<strong>0〜1 の値</strong>になる。

## 全体の流れ

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="クリップから画面まで"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">クリップ座標 → NDC → ピクセル座標</text>
<g font-size="12">
<rect x="20" y="60" width="160" height="90" rx="8" fill="#9664e6" fill-opacity="0.18" stroke="#9664e6" stroke-width="2"/>
<text x="100" y="86" text-anchor="middle" style="font-weight:700">クリップ座標</text><text x="100" y="108" text-anchor="middle">(x, y, z, w)</text><text x="100" y="128" text-anchor="middle" style="font-size:11px">4 要素</text>
<rect x="310" y="60" width="160" height="90" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="390" y="86" text-anchor="middle" style="font-weight:700">NDC</text><text x="390" y="108" text-anchor="middle">(x/w, y/w, z/w)</text><text x="390" y="128" text-anchor="middle" style="font-size:11px">x, y: -1〜1　z: 0〜1</text>
<rect x="600" y="60" width="160" height="90" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/>
<text x="680" y="86" text-anchor="middle" style="font-weight:700">ピクセル座標</text><text x="680" y="108" text-anchor="middle">(px, py, 深度)</text><text x="680" y="128" text-anchor="middle" style="font-size:11px">例：0〜800</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="182" y1="105" x2="308" y2="105" marker-end="url(#rfa)"/><line x1="472" y1="105" x2="598" y2="105" marker-end="url(#rfa)"/></g>
<text x="245" y="92" text-anchor="middle" style="font-size:12px">クリップ → w で割る</text>
<text x="535" y="92" text-anchor="middle" style="font-size:12px">ビューポート変換</text>
</svg>

## ① 三角形に組み立てる

**頂点が 1 個ずつ変換された後、GPU は「入力アセンブラで指定された形（トポロジー）」に従って、頂点を三角形にまとめます**。

| トポロジー | 頂点の使い方 |
| --- | --- |
| **三角形リスト** | **3 個ずつで 1 枚**（0,1,2 / 3,4,5 / …）。**もっとも一般的** |
| **三角形ストリップ** | **前の三角形の 2 頂点を再利用**（0,1,2 / 1,2,3 / 2,3,4 …）。**頂点が少なくて済む** |
| **線・点** | **線分・点として描く**（デバッグ表示など） |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="トポロジー">
<text x="20" y="24" class="fig-title">三角形リスト（左）と三角形ストリップ（右）</text>
<g transform="translate(40,50)" stroke-width="2">
<polygon points="0,90 60,90 30,30" fill="#4c8bf5" fill-opacity="0.3" stroke="#4c8bf5"/><polygon points="80,90 140,90 110,30" fill="#2ea043" fill-opacity="0.3" stroke="#2ea043"/>
<text x="0" y="116" style="font-size:11px">0,1,2</text><text x="80" y="116" style="font-size:11px">3,4,5</text>
<text x="0" y="140" style="font-size:12px">独立した 2 枚（頂点 6 個）</text>
</g>
<g transform="translate(400,50)" stroke-width="2">
<polygon points="0,90 60,30 120,90" fill="#4c8bf5" fill-opacity="0.3" stroke="#4c8bf5"/><polygon points="60,30 120,90 180,30" fill="#2ea043" fill-opacity="0.3" stroke="#2ea043"/><polygon points="120,90 180,30 240,90" fill="#e5aa28" fill-opacity="0.3" stroke="#e5aa28"/>
<text x="0" y="116" style="font-size:11px">0</text><text x="60" y="22" style="font-size:11px">1</text><text x="122" y="108" style="font-size:11px">2</text><text x="182" y="22" style="font-size:11px">3</text><text x="242" y="108" style="font-size:11px">4</text>
<text x="0" y="140" style="font-size:12px">つながった 3 枚（頂点 5 個）</text>
</g>
</svg>

## ② クリップ（視錐台の外を切り捨てる）

**画面に映らない部分は、描く必要がありません**。**カメラの視野（視錐台）の外にある三角形を捨て、境界をまたぐ三角形は切り落とします**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="クリップ">
<text x="20" y="24" class="fig-title">クリップ：視野の外は捨てる、またぐものは切る</text>
<rect x="260" y="50" width="260" height="170" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4"/>
<text x="266" y="68" style="font-size:12px">画面（視野）</text>
<polygon points="320,100 420,100 370,170" fill="#2ea043" fill-opacity="0.35" stroke="#2ea043" stroke-width="2"/>
<text x="330" y="190" style="font-size:12px;fill:#2ea043">完全に内側 → そのまま</text>
<polygon points="60,100 150,70 110,160" fill="#e5484d" fill-opacity="0.35" stroke="#e5484d" stroke-width="2"/>
<text x="40" y="190" style="font-size:12px;fill:#e5484d">完全に外側 → 捨てる</text>
<polygon points="470,130 600,100 560,200" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<polygon points="470,130 520,118 520,170 540,168" fill="#e5aa28" fill-opacity="0.55" stroke="none"/>
<text x="540" y="238" text-anchor="middle" style="font-size:12px;fill:#e5aa28">またぐ → 内側だけ残す</text>
</svg>

**クリップ空間での内外判定**は**簡単な比較**です。**w を基準にして、頂点が箱の中にあるかを調べます**。

| 条件（D3D） | 意味 |
| --- | --- |
| **−w ≤ x ≤ w** | **左右が視野の内側** |
| **−w ≤ y ≤ w** | **上下が視野の内側** |
| **0 ≤ z ≤ w** | **近い面と遠い面の間** |

**頂点がすべて外側の同じ側にあれば、三角形ごと捨てる**（**カリング**）。**一部だけ外なら、境界で切って新しい頂点を作ります**（**三角形が 2 枚に分かれることもある**）。

**ハードウェアは、画面の左右上下の端のクリップを「広い余白（ガードバンド）」で省略**します。**少しはみ出た三角形は、切らずにそのまま通し、描くときに画面内だけ描く**ので、**軽くなります**。**近い面（z）でのクリップは、確実に行われます**。

!!! note "近い面より手前は描けない"
    **カメラにめり込んだ物は、近い面で切られて、断面が見えたり穴が空いたりします**。**近い面を小さくしすぎると深度の精度が落ちる**ので、**バランス**が必要です（[射影](../projection.md)）。

## ③ 透視除算（遠近法の割り算）

**クリップ座標の (x, y, z) を、すべて w で割ります**。**これだけで遠近法になります**。

<div class="formula">NDC = ( x/w, y/w, z/w )</div>

**w はカメラからの奥行き**（[頂点の工程](vertex-stage.md)）です。**遠い物ほど w が大きく、割った結果の x, y が 0（画面の中心）に近づきます**。

<svg class="fig illust motion" data-fig="perspective-divide" viewBox="0 0 780 260" role="img" aria-label="透視除算">
<text x="20" y="24" class="fig-title">遠いほど、画面の中心に寄って小さくなる（透視除算）</text>
<rect x="60" y="50" width="300" height="180" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<line x1="210" y1="50" x2="210" y2="230" stroke="currentColor" stroke-opacity="0.2"/><line x1="60" y1="140" x2="360" y2="140" stroke="currentColor" stroke-opacity="0.2"/>
<rect x="90" y="80" width="100" height="100" fill="#4c8bf5" fill-opacity="0.35" stroke="#4c8bf5" stroke-width="2"/>
<text x="140" y="200" text-anchor="middle" style="font-size:12px">近い（w = 2）：大きい</text>
<rect x="240" y="100" width="40" height="40" fill="#e5484d" fill-opacity="0.45" stroke="#e5484d" stroke-width="2"/>
<text x="260" y="160" text-anchor="middle" style="font-size:12px">遠い（w = 10）：小さい</text>
<g font-size="13">
<text x="410" y="80" style="font-weight:700">同じ大きさの箱（幅 2）</text>
<text x="410" y="108">近い箱：x = 2 → 2 / 2 = <tspan font-weight="700">1.0</tspan></text>
<text x="410" y="132">遠い箱：x = 2 → 2 / 10 = <tspan font-weight="700">0.2</tspan></text>
<text x="410" y="170">w が大きいほど、割った結果が小さくなる</text>
<text x="410" y="194">→ 画面上で小さく、中心に寄る</text>
</g>
<circle cx="260" cy="120" r="5" fill="#e5484d"><animate attributeName="cx" values="260;250;260;270;260" dur="4s" repeatCount="indefinite"/></circle>
</svg>

**z / w は、深度**（0〜1）になります。**この値は遠いほど 1 に近い**ですが、**直線的には増えません**（近くに細かく割り当てる）。<strong>深度の詳細は[深度とカリング](../depth-culling.md)</strong>で扱います。

| NDC | 範囲（D3D） |
| --- | --- |
| **x** | <strong>−1（左端）〜 1（右端）</strong> |
| **y** | <strong>−1（下端）〜 1（上端）</strong> |
| **z** | <strong>0（近い面）〜 1（遠い面）</strong> |

## ④ ビューポート変換（ピクセルへ写す）

**NDC を実際の画面のピクセル座標に写します**。**画面（描画先）の大きさに合わせて拡大し、原点を左上に移します**。

<div class="formula">
px = (x_ndc × 0.5 + 0.5) × 幅<br>
py = (0.5 − y_ndc × 0.5) × 高さ
</div>

**Y の符号が逆になる**ことに注意してください。**NDC は上が +1**、<strong>ピクセル座標は上が 0（下に行くほど増える）</strong>です。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="NDC からピクセル座標"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">NDC（左）とピクセル座標（右）：Y の向きが逆</text>
<g transform="translate(60,50)">
<rect x="0" y="0" width="200" height="200" fill="none" stroke="currentColor"/>
<line x1="100" y1="0" x2="100" y2="200" stroke="currentColor" stroke-opacity="0.25"/><line x1="0" y1="100" x2="200" y2="100" stroke="currentColor" stroke-opacity="0.25"/>
<text x="-4" y="-6" style="font-size:11px">(-1, 1)</text><text x="150" y="-6" style="font-size:11px">(1, 1)</text>
<text x="-4" y="218" style="font-size:11px">(-1, -1)</text><text x="150" y="218" style="font-size:11px">(1, -1)</text>
<circle cx="130" cy="80" r="5" fill="#e5484d"/><text x="138" y="76" style="font-size:11px">(0.3, 0.1)</text>
<text x="100" y="244" text-anchor="middle" style="font-size:12px">上が +1</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="290" y1="150" x2="410" y2="150" marker-end="url(#rfa)"/></g>
<text x="350" y="138" text-anchor="middle" style="font-size:12px">幅 800 × 高さ 800</text>
<g transform="translate(450,50)">
<rect x="0" y="0" width="200" height="200" fill="none" stroke="currentColor"/>
<text x="-4" y="-6" style="font-size:11px">(0, 0)</text><text x="150" y="-6" style="font-size:11px">(800, 0)</text>
<text x="-4" y="218" style="font-size:11px">(0, 800)</text><text x="140" y="218" style="font-size:11px">(800, 800)</text>
<circle cx="130" cy="90" r="5" fill="#e5484d"/><text x="138" y="108" style="font-size:11px">(520, 360)</text>
<text x="100" y="244" text-anchor="middle" style="font-size:12px">上が 0、下に行くほど増える</text>
</g>
</svg>

**前のページの例**で、<strong>NDC (0.3, 0.1)</strong> は次のようになります。

<div class="formula">
px = (0.3 × 0.5 + 0.5) × 800 = 520<br>
py = (0.5 − 0.1 × 0.5) × 800 = 360
</div>

**頂点 (3, 1, 10) は、画面の (520, 360) のピクセルに写ります**。

```cpp
D3D11_VIEWPORT viewport = {};
viewport.TopLeftX = 0;
viewport.TopLeftY = 0;
viewport.Width = 800;
viewport.Height = 800;
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;
context->RSSetViewports(1, &viewport);
```

| 項目 | 内容 |
| --- | --- |
| **`Width / Height`** | **描画先の大きさ**（**画面の一部だけに描く**こともできる） |
| **`MinDepth / MaxDepth`** | **深度の範囲**。**ふつう 0〜1** |
| **ビューポートを狭く** | **分割画面・ミニマップ・シャドウ マップの一部**に描ける |

## 深度の値

**ビューポート変換で深度 z/w が 0〜1 の値になります**。**この値が後の工程の「深度テスト」（隠れているかの判定）に使われます**（[深度・ブレンド](output-merger.md)）。

| 深度 | 意味 |
| --- | --- |
| **0** | <strong>近い面（カメラのすぐ前）</strong> |
| **1** | **遠い面** |
| **非線形** | **近くの精度が高く、遠くの精度が低い**。**近い面を遠ざけると精度が改善** |

## よくあるミス

??? failure "近い面を 0 にして、描画が壊れる"
    **近い面は 0 より大きい値**（0.1 など）。**0 だと w = 0 の頂点が出て割り算が壊れる**。

??? failure "近い面と遠い面の比が大きすぎて、遠くで奥行きがちらつく（Z ファイティング）"
    **近い面を可能な限り遠くに置く**。**リバース Z（深度を反転）や 32 ビット浮動小数の深度**も有効。

??? failure "画面の Y の向きを間違えて、上下が逆に映る"
    **NDC は上が +1、ピクセルは上が 0**。**ビューポート変換が自動で処理する**ので**自分で反転しない**。

??? failure "ビューポートの大きさが描画先と違い、画面の一部にしか描かれない"
    **リサイズ時にビューポートも更新**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点シェーダーの後は<strong>GPU が自動</strong>：<strong>組み立て → クリップ → 透視除算 → ビューポート変換</strong>
    - [x] <strong>クリップ</strong>は<strong>視野の外を捨てる</strong>。<strong>またぐ三角形は切る</strong>
    - [x] <strong>透視除算</strong> ＝ <strong>x, y, z を w で割る</strong>。<strong>遠近法のしくみ</strong>
    - [x] <strong>ビューポート変換</strong>で<strong>ピクセル座標へ</strong>。<strong>Y が反転</strong>
    - [x] <strong>深度 z/w</strong>は<strong>0〜1</strong>。<strong>後の深度テストに使われる</strong>

## 参考

- Microsoft, "Rasterizer Stage"（Microsoft Learn）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 5, 6）
- Scratchapixel, "The Perspective and Orthographic Projection Matrix"

## 関連ページ

- [描画の流れ（入門）](index.md)
- [頂点の工程](vertex-stage.md)
- [ラスタライズ](rasterize.md)
- [射影](../projection.md)
- [深度とカリング](../depth-culling.md)
