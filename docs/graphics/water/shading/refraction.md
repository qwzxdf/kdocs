---
title: Water Refraction Distortion
tags:
  - 描画
---

# Water Refraction Distortion

<strong>水の中の景色は、水面で曲がって見えます</strong>。<strong>法線に応じて、既に描いた画面をずらして読む</strong>ことで、安く表現できます。このページでは、水の屈折の歪みと、水面より手前の物の扱いを説明します。

!!! tip "ポイント"
    - 画面のコピーを、法線でずらして読む。
    - 水面より手前の物は、ずらさない（深度で判定）。
    - 歪みが強すぎると、不自然。
    - 水深が浅いほど、歪みを弱める。

## 屈折の歪み
<strong>水面の法線は波で傾く</strong>ので、<strong>水中の物は歪んで見えます</strong>。法線の XZ 成分で背景を読む UV をずらします。

```hlsl
float2 distortion = wave_normal.xz * distortion_strength;
float2 refract_uv = screen_uv + distortion;

float scene_depth_at_uv = LinearizeDepth(depth_texture.Sample(point_clamp, refract_uv).r);
if (scene_depth_at_uv < surface_depth) {
  refract_uv = screen_uv;
}

float3 scene_color = scene_copy.Sample(linear_clamp, refract_uv).rgb;
```

| 点 | 説明 |
| --- | --- |
| `distortion_strength` | 0.02 程度。大きすぎると不自然 |
| 深度の再確認 | ずらした先が水面より手前（水の外にある物）なら、ずらさない。手前の物が水の中に引きずられて見える失敗を防ぐ |
| 距離で弱める | 遠くの水は歪みを減らす（ちらつき防止） |
| 水深で強める | 深いほど、歪みが大きい（浅い所はほとんど歪まない） |

## なぜ、水の中の物は、ずれて見えるのか

光が、空気から水へ入るとき、<strong>境界で、曲がります</strong>（屈折）。<strong>スネルの法則</strong>で、曲がる角度が決まります。

```text
n₁ sinθ₁ = n₂ sinθ₂            n₁ = 1.0（空気）、n₂ = 1.33（水）
```

水の中の、物体から来た光は、水面で、曲がって、目に届きます。<strong>目は、光が、曲がらず、まっすぐ来た、と思い込む</strong>ので、<strong>水の中の物は、実際より、浅い所に、見えます</strong>。ストローが、水面で、折れて見えるのも、同じ理由です。

## 正確な屈折ベクトル

水面の、法線 `N` と、視線 `V` から、<strong>屈折した、光の向き</strong>を計算するのが、HLSL の組み込み関数 `refract` です。

```hlsl
// refract(入射方向（目から、水面へ向かう向き）, 法線, 屈折率の比 = n1 / n2)
float3 refracted_dir = refract(-view_dir, wave_normal, 1.0 / 1.33);
```

この向きに、光が、水の中を進みます。<strong>屈折した向きに、水の中を、一定の距離だけ進んだ点</strong>が、目に、見えている点です。

```hlsl
// 水面の点 P から、屈折した向きに、水の深さぶん進んだ点（水中の、見える位置）。
float3 refracted_pos = world_pos + refracted_dir * (water_depth / max(-refracted_dir.y, 0.05));
// この点を、画面に投影して、そこの、シーンの色を、読む。
float4 clip = mul(float4(refracted_pos, 1), view_proj);
float2 refract_uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
```

これが、<strong>屈折の、幾何学的に、正しい</strong>方法です。<strong>水深</strong>（底までの距離）が、必要なので、深度バッファを読みます（[Color by Water Depth](depth-color.md)）。

## 画面のコピーを、歪ませる（簡易な方法）

幾何学的な方法は、<strong>水深と、屈折ベクトル</strong>が必要で、計算が、増えます。<strong>多くのゲームでは、もっと、簡単な方法</strong>を、使います（Sousa、2005）。

1. 水面を描く前に、画面（シーンの色）を、テクスチャにコピーする
2. 水面の、ピクセルで、波の法線に応じて、UV を、ずらして、そのコピーを読む

```cpp
// 水面を描く前に、シーンの色を、コピーする。
context->CopyResource(scene_copy_tex.Get(), scene_color_tex.Get());
// 水の描画では、scene_copy を SRV として、読む（書き込み先の scene_color とは、別のテクスチャ）。
```

```hlsl
// 法線の xz 成分で、UV をずらす。
float2 distortion = wave_normal.xz * distortion_strength;
float2 refract_uv = screen_uv + distortion;
float3 scene_color = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
```

波の法線が、<strong>傾いている方向に、ずれて</strong>見えるので、<strong>水面が、ゆらゆらして、水中の物が、揺らいで見えます</strong>。

### パラメーター

| パラメーター | 目安 | 内容 |
| --- | --- | --- |
| `distortion_strength` | 0.02〜0.05 | ずれの大きさ。大きいと、不自然に、歪む |
| 水深での、強さ | 浅いほど、弱める | 浅い所は、光が、水中を、通る距離が短く、ほとんど、ずれない |
| 距離での、強さ | 遠いほど、弱める | 遠くは、ちらつきを、防ぐ |

## 手前の物を、ずらさない

歪ませた UV で、シーンの色を、読むとき、<strong>水より手前にある物</strong>（水面から、突き出た杭、船、プレイヤーの足）を、<strong>読んでしまう</strong>ことがあります。杭の色が、水面に、にじみ出して見えます。

```hlsl
// ずらした先の深度が、水面より手前なら（水の外にある物）、ずらさない。
float2 refract_uv = screen_uv + distortion;
float scene_depth_at_uv = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
if (scene_depth_at_uv < surface_depth) {
  refract_uv = screen_uv;                    // ずらさず、元の位置を読む
}
float3 scene_color = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
```

| 状況 | 結果 |
| --- | --- |
| ずらした先が、水の中（底） | そのまま、歪ませた色を使う |
| ずらした先が、水より手前の物 | 歪ませず、元の位置の色を使う |

これでも、<strong>水面の境界で、わずかに、にじみ</strong>ます。さらに、<strong>水の外にある物の、マスク</strong>を、別のテクスチャで、持つ方法もありますが、簡易な方法では、この深度の、チェックだけで、十分なことが、多いです。

## 水深から、歪みを決める

<strong>浅い場所</strong>では、光が、水の中を、通る距離が、短く、<strong>屈折の影響が、小さい</strong>です。水深に比例して、歪みを強めます。

```hlsl
float depth_factor = saturate(water_depth / 2.0);       // 2 m で、最大
float2 distortion = wave_normal.xz * distortion_strength * depth_factor;
```

岸に、近づくほど、歪みが、小さくなり、<strong>水際で、屈折が、自然に、消えます</strong>。

## 色収差（分散）

水の屈折率は、<strong>波長で、少し違います</strong>（赤で 1.331、青で 1.337）。これを、再現すると、<strong>RGB を、わずかに、別々にずらして</strong>、読みます。

```hlsl
float3 scene_color;
scene_color.r = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 0.95).r;
scene_color.g = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 1.00).g;
scene_color.b = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 1.05).b;
```

水は、屈折率の差が、小さく、効果は、ごくわずかです。入れると、<strong>水面の縁が、わずかに、虹色</strong>に見えます。ガラス（[Dispersion](../../translucency/refraction/dispersion.md)）では、効果が、目立ちます。

## 画面の端

歪ませた UV が、<strong>画面の外</strong>を指すことがあります。画面の外の色は、無いので、<strong>サンプラーの、クランプ</strong>（`CLAMP`）で、端の色を、繰り返し、読みます。画面の端で、色が、伸びて見えることがあります。

| 対策 | 内容 |
| --- | --- |
| 歪みを、画面の端で、弱める | 端に近いほど、歪みを小さくする |
| 画面を、少し大きく描く | シーンを、画面より、少し広い範囲で、描く（コストが、増える） |
| 気にしない | 水面の歪みは、小さいので、多くの場合、目立たない |

## よくあるミス

??? failure "岸辺の物が、水面に引き込まれて歪む"
    <strong>深度を比べて、手前の物は除く</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 法線で画面をずらす
    - [x] 手前の物は除く

## 参考

- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005（画面のコピーを、ずらして使う屈折）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（フレネル、屈折、スネルの法則）
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（水の描画、平面反射と、屈折のコピー）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes

## 関連ページ

- [Water Shading](index.md)
- [Screen-Space Refraction](../../translucency/refraction/screen-space.md)
