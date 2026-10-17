---
title: 背面法の輪郭線
tags:
  - 描画
---

# 背面法の輪郭線

<strong>背面法（Inverted Hull Method）</strong>は、**輪郭線を作る、もっとも古典的で簡単な方法**です。**同じモデルを「もう 1 回」描き、頂点を法線方向に少し膨らませ、表面（前面）を捨てて裏面だけを黒く描く**と**元のモデルの輪郭の外側に、黒い縁**が**できます**。**シェーダーだけで実現でき、線の太さや色を物体や部位ごとにアーティストが制御できる**ので、**多くのアニメ調ゲーム**で**使われます**。このページでは、<strong>仕組み・実装・画面上の太さを一定にする方法・線の途切れ（角）の対策・太さの調整（頂点カラー）</strong>を説明します。

!!! tip "ポイント"
    - 背面法 ＝ <strong>モデルを、法線方向に膨らませて、裏面だけを黒く描く</strong>。<strong>はみ出た裏面が輪郭線に見える</strong>。
    - <strong>実装が簡単</strong>。<strong>1 パス追加するだけ</strong>。
    - <strong>前面をカリング</strong>（<strong>`CULL_FRONT`</strong>）して、<strong>裏面だけ</strong>描く。
    - <strong>画面上の太さを一定</strong>にするには、<strong>クリップ空間で膨らませる</strong>（<strong>距離に応じて、補正</strong>）。
    - <strong>角（平らな面の境）で、法線が割れて、線が途切れる</strong> → <strong>スムーズ法線を別に持つ</strong>。
    - <strong>線の太さは、頂点カラーで部位ごとに調整</strong>できる。

## 仕組み

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="背面法の仕組み">
<text x="20" y="26" class="fig-title">膨らませた裏面が、輪郭線として見える</text>
<g transform="translate(50,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">① 元のモデル</text>
<circle cx="80" cy="80" r="56" fill="#f5deb3" stroke="#334155" stroke-width="2"/>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">② 膨らませた裏面（黒）</text>
<circle cx="80" cy="80" r="66" fill="#111827"/>
<text x="0" y="170" style="font-size:12px">前面は描かず、裏面だけ描く</text>
</g>
<g transform="translate(540,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">③ 重ねる</text>
<circle cx="80" cy="80" r="66" fill="#111827"/><circle cx="80" cy="80" r="56" fill="#f5deb3"/>
<text x="0" y="170" style="font-size:12px">元のモデルが上に来て、縁だけ黒く残る</text>
</g>
</svg>

| 手順 | 内容 |
| --- | --- |
| **① 元のモデルを描く** | **通常のシェーディング** |
| **② 同じモデルをもう一度描く** | **頂点を法線方向に膨らませる・前面をカリング・黒で塗る** |
| **③ 結果** | **元のモデルが手前にあり、膨らんだ裏面が縁として見える** |

## 実装

```hlsl
cbuffer OutlineParams : register(b2) {
  float outline_width;
  float3 outline_color;
};

VSOutput OutlineVS(VSInput input) {
  VSOutput output;
  float3 expanded = input.position + input.normal * outline_width;
  output.position = mul(mul(float4(expanded, 1.0), world), view_projection);
  return output;
}

float4 OutlinePS(VSOutput input) : SV_Target {
  return float4(outline_color, 1.0);
}
```

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.FillMode = D3D11_FILL_SOLID;
desc.CullMode = D3D11_CULL_FRONT;
device->CreateRasterizerState(&desc, outline_rasterizer.GetAddressOf());
```

| 点 | 説明 |
| --- | --- |
| **`position + normal × width`** | **法線方向に頂点を膨らませる** |
| **`CULL_FRONT`** | **前面を描かず、裏面だけ描く** |
| **色** | <strong>黒（または暗い色・物体の色の暗い版）</strong> |
| **深度** | **通常の深度テスト**。**元のモデルが手前にあるので、膨らんだ裏面は、縁だけ見える** |

<!-- fig:outline-hull-width:begin -->
<!-- fig:outline-hull-width:end -->

## 画面上の太さを一定にする

**ワールド空間で `normal × width` を足す**と、**カメラから遠いと線が細く見え、近いと太く見えます**（**遠近法**）。**画面上の太さを一定**にするには、**クリップ空間で膨らませます**。

```hlsl
VSOutput OutlineConstantWidthVS(VSInput input) {
  VSOutput output;
  float4 clip_position = mul(mul(float4(input.position, 1.0), world), view_projection);
  float3 clip_normal = mul(mul(input.normal, (float3x3)world), (float3x3)view_projection);
  float2 screen_normal = normalize(clip_normal.xy);
  float2 offset = screen_normal * outline_width_pixels * 2.0 / viewport_size;
  clip_position.xy += offset * clip_position.w;
  output.position = clip_position;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| **`clip_normal.xy`** | **法線の画面上の向き** |
| **`× clip_position.w`** | **透視除算の後に画面上で一定の幅になる** |
| **`outline_width_pixels`** | **画面上の画素単位の太さ** |
| **遠近感を残したい場合** | **ワールド空間版を使い、距離で太さを補正** |

## 線が途切れる問題（角）

**立方体のような、角のあるモデル**は、**角の頂点が面ごとに別の法線を持つ**ので、<strong>法線方向に膨らませると、頂点が面ごとに別の方向へ離れ、角に隙間（線の途切れ）</strong>ができます。

<svg class="fig illust" viewBox="0 0 780 210" role="img" aria-label="角の途切れ">
<text x="20" y="26" class="fig-title">角の頂点は、面ごとに法線が違うので、膨らませると割れる</text>
<g transform="translate(60,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">面の法線で膨らませる（割れる）</text>
<rect x="30" y="30" width="80" height="80" fill="#f5deb3" stroke="#334155" stroke-width="2"/>
<polyline fill="none" stroke="#111827" stroke-width="6" points="30,22 110,22 118,30 118,110 110,118 30,118 22,110 22,30 30,22" stroke-dasharray="80 8"/>
</g>
<g transform="translate(420,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">スムーズ法線で膨らませる（つながる）</text>
<rect x="30" y="30" width="80" height="80" fill="#f5deb3" stroke="#334155" stroke-width="2"/>
<rect x="22" y="22" width="96" height="96" rx="8" fill="none" stroke="#111827" stroke-width="6"/>
</g>
</svg>

| 対策 | 内容 |
| --- | --- |
| **スムーズ法線を別に持つ** | **同じ位置の頂点の法線を平均した、滑らかな法線を輪郭用に頂点（UV2・頂点カラー）に保存** |
| **モデル作成時に焼く** | **DCC ツール・インポート時に計算** |
| **接線空間に格納** | **スムーズ法線を接線空間で保存**（**スキニングでも崩れない**） |

```hlsl
float3 smooth_normal = input.smooth_normal;
float3 expanded = input.position + smooth_normal * outline_width;
```

## 太さの調整（頂点カラー）

**線の太さを部位ごとに変えたい**ことが**あります**（**顔は細く・体は太く**）。<strong>頂点カラー（またはテクスチャ）</strong>で**太さの係数を持ちます**。

```hlsl
float width_scale = input.color.r;
float3 expanded = input.position + smooth_normal * outline_width * width_scale;
```

| 用途 | 内容 |
| --- | --- |
| **部位ごとの太さ** | **頂点カラー R に係数** |
| **線を消したい部分** | **係数を 0**（**目・口の中・内側の線**） |
| **距離による細く** | <strong>遠くで細くする（距離のフェード）</strong> |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **簡単・安い** | **内側の線（モデルの内部の折り目）は出ない** |
| **太さ・色を物体や部位ごとに制御できる** | **角のあるモデルでスムーズ法線が必要** |
| **MSAA・TAA と相性が良い** | <strong>頂点数が 2 倍になる（描画が 2 回）</strong> |
| **ジオメトリに沿った綺麗な線** | **薄いオブジェクトで裏と表の線が干渉** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **スムーズ法線を事前に焼く** | **角で途切れない** |
| **クリップ空間で太さを一定** | **画面上の太さがそろう** |
| **頂点カラーで太さを制御** | **部位ごとの調整** |
| **画面空間エッジを併用** | **内側の線を足す**（[画面空間のエッジ検出](outline-edge.md)） |
| **色は元の色の暗い版** | **黒より柔らかい絵に** |
| **距離で線を細く・消す** | **遠くでうるさくならない** |

## よくあるミス

??? failure "立方体の角で、線が途切れる"
    **スムーズ法線**を使う。

??? failure "遠くのキャラの線が、太すぎる（または細すぎる）"
    **クリップ空間で膨らませる**、または**距離で補正**。

??? failure "前面も描いて、モデルが黒くなる"
    **`CULL_FRONT`** で、**裏面だけ**描く。

??? failure "スキニングしたキャラの輪郭が、動いて崩れる"
    **輪郭パスでも同じスキニングを適用**する（**スムーズ法線も同じ骨で変形**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 背面法 ＝ <strong>法線方向に膨らませた裏面を、黒く描く</strong>。<strong>前面はカリング</strong>
    - [x] <strong>簡単・安く</strong>、<strong>太さや色を制御できる</strong>
    - [x] <strong>クリップ空間で膨らませる</strong>と<strong>画面上の太さが一定</strong>
    - [x] <strong>角の途切れ</strong>は<strong>スムーズ法線</strong>で<strong>解決</strong>
    - [x] <strong>内側の線は出ない</strong> → <strong>画面空間エッジと併用</strong>

## 参考

- Raskar & Cohen, "Image Precision Silhouette Edges"（I3D 1999）
- Xu et al., "Guilty Gear Xrd's Art Style"（GDC 2015）
- Ohno et al., "Rendering the Outlines in 3D Game Characters"

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [画面空間のエッジ検出](outline-edge.md)
- [セル シェーディング](cel-shading.md)
- [スキニングとアニメーション](../../../3d/skinning-animation.md)
