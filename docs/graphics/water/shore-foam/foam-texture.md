---
title: 泡テクスチャと合成
tags:
  - 描画
---

# 泡テクスチャと合成

**マスクが決まったら、泡テクスチャで見た目を付け、水面に合成します**。**テクスチャを流して、泡が動くように見せる**のが**コツ**です。このページでは、**泡テクスチャの使い方と、合成**を説明します。

!!! tip "ポイント"
    - **泡テクスチャ ＝ ノイズ状の白いパターン**。
    - **マスク × テクスチャ ＝ 泡の濃さ**。
    - **テクスチャを流して、動きを付ける**。
    - **水の色の上に、白を乗せる**。

## 泡テクスチャ
**マスクだけでは、べったりした白**になります。**泡の模様（粒の集まり）のテクスチャ**を**乗せます**。

```hlsl
float2 foam_uv1 = input.world_position.xz * 0.2 + time * float2(0.02, 0.01);
float2 foam_uv2 = input.world_position.xz * 0.47 - time * float2(0.015, 0.03);
float foam_pattern = foam_texture.Sample(linear_wrap, foam_uv1).r
                   * foam_texture.Sample(linear_wrap, foam_uv2).r;

float foam = saturate(mask * 2.0 - (1.0 - foam_pattern * 2.0));
```

| 点 | 説明 |
| --- | --- |
| **2 枚を掛ける** | **スケールの違う 2 枚を掛けて、繰り返しを隠す** |
| **`mask * 2 − (1 − pattern)`** | **マスクが強いほど、模様の隙間まで埋まる<strong>（</strong>マスクが弱いと模様の濃い所だけ残る<strong>）。</strong>端が自然に崩れる** |
| **ワールド座標の UV** | **水面が動いても泡が水面に貼りつく** |
| **ゆっくり流す** | **泡は水の流れに乗る** |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="マスクと模様の合成">
<text x="20" y="24" class="fig-title">マスクの強さで、模様の見え方が変わる</text>
<defs>
<pattern id="foamdots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="3" fill="#ffffff"/><circle cx="11" cy="9" r="2" fill="#ffffff"/></pattern>
</defs>
<rect x="40" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="290" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="540" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="40" y="50" width="200" height="120" fill="url(#foamdots)" opacity="0.18"/>
<rect x="290" y="50" width="200" height="120" fill="url(#foamdots)" opacity="0.6"/>
<rect x="540" y="50" width="200" height="120" fill="#ffffff" opacity="0.9"/>
<text x="140" y="190" text-anchor="middle" style="font-size:12px">マスク弱：模様の濃い所だけ</text>
<text x="390" y="190" text-anchor="middle" style="font-size:12px">マスク中：まだら</text>
<text x="640" y="190" text-anchor="middle" style="font-size:12px">マスク強：ほぼ真っ白</text>
</svg>

## 泡の合成
**泡は水面の色の上に白く乗せます**。**泡の部分は水中が見えず（不透明）、光沢も無く**なります。

```hlsl
float3 foam_color = float3(0.95, 0.97, 1.0) * (ambient + diffuse_light);
float3 color = lerp(water_color, foam_color, foam);

float roughness = lerp(water_roughness, 0.9, foam);
float transparency = 1.0 - foam;
```

| 点 | 説明 |
| --- | --- |
| **泡の色** | **白だが光に照らされた色**（**暗い所で光らない**ように、**ライティングを掛ける**） |
| **粗さを上げる** | **泡は荒れた面**。**水の鋭いスペキュラを消す** |
| **屈折を弱める** | **泡の下は見えない**。**水中の色（屈折）の寄与を減らす** |

## よくあるミス

??? failure "泡が、水面に貼り付いたシールのように見える"
    **テクスチャを流す**・**2 層重ねる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **マスク × テクスチャで、泡の濃さ**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [岸辺の泡](index.md)
- [泡を残す](foam-history.md)
