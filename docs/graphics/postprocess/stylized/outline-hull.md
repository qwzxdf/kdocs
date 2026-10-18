---
title: Inverted Hull Outlines
tags:
  - 描画
---

# Inverted Hull Outlines

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

背面法の手順は 3 段階です。元のモデルを通常のシェーディングで描きます。同じモデルをもう一度描き、頂点を法線方向に膨らませ、前面をカリングして黒で塗ります。結果として、元のモデルが手前にあり、膨らんだ裏面が縁として見えます。

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

<svg class="fig illust motion" data-fig="outline-hull-width" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-outline-hull-width" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">反転ハル法:裏面を外へ膨らませ、輪郭線にする</text>
<circle cx="190" cy="200" r="80" fill="#0b0b0b"><animate attributeName="r" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.1481;0.3333;0.4444;0.5556;0.6296;1.0000" values="80;80;80;94;94;84;84;84"/></circle>
<circle cx="190" cy="200" r="80" fill="#f59e0b" stroke="none"/>
<text x="190" y="80" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">膨らませる幅を変える</text>
<text x="70" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">幅 0:輪郭線は見えない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="1;1;0;0"/></text>
<text x="70" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">幅を広げると、線が太くなる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;0.4441;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">広すぎ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;0.5553;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">適度な幅（細め）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5553;0.5556;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="570" y="80" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">遠ざかると…</text>
<text x="440" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">ワールドの幅を固定</text>
<circle cx="520" cy="150" r="47" fill="#0b0b0b"><animate attributeName="r" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6296;0.8519;1.0000" values="47;47;18.8;18.8"/></circle>
<circle cx="520" cy="150" r="40" fill="#f59e0b"><animate attributeName="r" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6296;0.8519;1.0000" values="40;40;16;16"/></circle>
<text x="440" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">距離で補正（画面で一定）</text>
<circle cx="520" cy="290" r="47" fill="#0b0b0b"><animate attributeName="r" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6296;0.8519;1.0000" values="47;47;23;23"/></circle>
<circle cx="520" cy="290" r="40" fill="#f59e0b"><animate attributeName="r" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6296;0.8519;1.0000" values="40;40;16;16"/></circle>
<text x="440" y="372" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">上は遠くで線が細くなる。下は画面で一定<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

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

角のあるモデルでは、法線が頂点ごとに分かれていて、膨らませると角で線が途切れます。対策は、スムーズ法線を別に持つことです。同じ位置の頂点の法線を平均した滑らかな法線を、輪郭用に頂点（UV2 や頂点カラー）に保存します。DCC ツールやインポート時に計算して、モデル作成時に焼きます。スキニングでも崩れないよう、スムーズ法線を接線空間で保存する方法もあります。

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

頂点カラーによる制御です。部位ごとの太さは、頂点カラーの R に係数を入れて決めます。線を消したい部分（目・口の中・内側の線）は、係数を 0 にします。遠くで細くするために、距離のフェードも使えます。

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

- [Outlines and Toon](index.md)
- [Screen-Space Edge Detection](outline-edge.md)
- [Cel Shading](cel-shading.md)
- [スキニングとアニメーション](../../../3d/skinning-animation.md)
