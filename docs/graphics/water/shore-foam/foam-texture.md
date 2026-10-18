---
title: Foam Textures and Compositing
tags:
  - 描画
---

# Foam Textures and Compositing

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

合成のコードの要点です。泡の色は白ですが、光に照らされた色にします（暗い所で光らないよう、ライティングを掛けます）。泡は荒れた面なので、粗さを上げ、水の鋭いスペキュラを消します。泡の下は見えないので、屈折を弱め、水中の色の寄与を減らします。

## 泡の量から、泡の見た目へ

履歴や、ヤコビアンから得られるのは、**泡の量**（0〜1 のマスク）です。これを、**泡らしい、模様**に変えるのが、**泡のテクスチャ**の役目です。

## しきい値で、切り出す

**泡の量が、多い場所ほど、泡のテクスチャが、濃く出る**ように、**テクスチャの値と、泡の量を、比較**します。

```hlsl
// 泡のテクスチャ（白黒のノイズ状の模様）を、泡の量でしきい値処理する。
float foam_pattern = g_foam_tex.Sample(g_linear_wrap, world_uv * foam_scale).r;
// 泡の量が多いほど、小さい値のところまで、泡になる（しきい値が、下がる）。
float foam = smoothstep(1.0 - foam_amount, 1.0 - foam_amount + foam_softness, foam_pattern);
```

| 泡の量 | 見え方 |
| --- | --- |
| 0.1 | まばらな、小さな泡の点 |
| 0.5 | 網目状の、泡の層 |
| 0.9 | ほぼ一面の、泡（切れ目が、わずか） |

**しきい値で、切る**ことで、泡の**縁が、くっきり**し、量の変化に、応じて、**泡の面積が、なめらかに、増減**します。単純に、泡の量を、アルファとして掛けると、**ぼんやりした、白いもや**になります。

## 2 つのスケールを、重ねる

1 つの、スケールだけだと、**繰り返しが、目立ち**ます。**大きさの違う、2 枚**を、**逆向きに、ゆっくり、動かして**、混ぜます。

```hlsl
float p1 = g_foam_tex.Sample(g_linear_wrap, world_uv * 0.5 + time * float2( 0.01, 0.005)).r;
float p2 = g_foam_tex.Sample(g_linear_wrap, world_uv * 1.7 + time * float2(-0.007, 0.011)).r;
float foam_pattern = p1 * p2 * 2.0;          // 掛けて 2 倍。平均の明るさが、保たれる
```

## 泡の、色と、ライティング

泡は、**白く、不透明に近い**ですが、**水の中に、浮いている**ため、**水の色が、少し、混ざります**。

| 要素 | 内容 |
| --- | --- |
| 色 | 白〜薄いグレー。**水の色を、少し混ぜる**（水の中の、泡は、青みがかる） |
| 拡散反射 | **ランバート**。泡は、粗い表面なので、**反射が、拡散**する |
| スペキュラー | **ほぼ無し**（粗さが、高い）。水のスペキュラーを、**泡の量で、打ち消す** |
| 水の反射の、打ち消し | 泡のある所は、水面の**鏡面反射が、弱まる**（泡が、水面を覆うため） |

```hlsl
// 泡の量で、水の反射と、スペキュラーを弱めて、泡の拡散色に、置き換える。
float3 water_shaded = water_color + reflection + specular;
float3 foam_shaded = foam_color * (ambient + sun_color * saturate(dot(N, L)));
float3 color = lerp(water_shaded, foam_shaded, foam * foam_opacity);
```

## 泡の厚みと、凹凸

泡の、**模様の濃淡**は、**泡の厚み**として、解釈できます。厚い所は、**盛り上がって**います。この、**凹凸**を、**法線**に反映すると、泡が、**立体的**に見えます。

```hlsl
// 泡のテクスチャの、勾配から、法線を作る（簡易）。
float h = foam_pattern;
float2 gradient = float2(ddx(h), ddy(h)) * foam_normal_strength;       // 画面の微分
float3 foam_normal = normalize(float3(-gradient.x, 1.0, -gradient.y));
N = normalize(lerp(N, foam_normal, foam));
```

## 泡が、水面を、覆っているときの、透明度

泡は、**完全に不透明ではありません**。薄い泡の層は、**下の、水が、透けて見える**ことがあります。**泡の、アルファ**は、**泡のテクスチャの、値**から決めます。

```hlsl
float foam_alpha = saturate(foam * foam_opacity);
// 下の水の色と、泡の色を、アルファでブレンドする。
```

## 泡の、縁の、扱い

**岸に、打ち寄せる、泡**は、岸の、陸の部分で、**切れ目**が、できます。陸と水の、**境目**では、泡を、**陸の方へ、はみ出さない**ようにします（[Shore Foam: Depth Difference](shore-depth.md)）。

## 低解像度の、履歴と、高解像度の、模様の、組み合わせ

| 層 | 解像度 | 内容 |
| --- | --- | --- |
| 泡の履歴（量） | 低（512×512） | **どこに、どれだけ**、泡があるか |
| 泡のテクスチャ（模様） | 高（1024×1024、タイル） | 泡の**形** |
| しきい値処理 | ピクセル | 履歴の値で、模様を、**切り出す** |

**低解像度の履歴**を、高解像度の、泡の模様で、**切り出す**ことで、**少ない、メモリと、計算**で、**細かい泡**が、表現できます。

## よくあるミス

??? failure "泡が、水面に貼り付いたシールのように見える"
    **テクスチャを流す**・**2 層重ねる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **マスク × テクスチャで、泡の濃さ**

## 参考

- Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Vlachos, "Water Flow in Portal 2", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games（フロー マップと、2 位相の繰り返し）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Shore Foam](index.md)
- [Persistent Foam](foam-history.md)
