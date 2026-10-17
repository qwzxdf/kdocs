---
title: コースティクス
tags:
  - 描画
---

# コースティクス

**水面の波で光が集まり、水底にゆらゆら揺れる光の模様ができます**。**アニメーションするテクスチャを、光の方向から投影**する**のが手軽**です。このページでは、**コースティクスの作り方**を説明します。

!!! tip "ポイント"
    - **コースティクス ＝ 波で光が集まってできる模様**。
    - **テクスチャをアニメーションして、投影する**。
    - **水深に応じて、強さを変える**。
    - **本格的には、波の法線から光線を追う**。

## コースティクス
**コースティクス**は、**波打つ水面がレンズのように光を集め、底に明るい網目模様ができる**現象です。**波の凹凸の形で光が集まる所と散る所ができます**。

| 方式 | 内容 |
| --- | --- |
| **アニメする模様のテクスチャ** | **ループするコースティクス模様を、ライトの方向から底に投影**して**足す**。**安い・定番** |
| **シミュレーション** | **水面の法線から屈折を計算**し、**底に落ちる光の集まりを求める**（**重い・正確**） |
| **ヤコビアン風の近似** | **水面の法線のラプラシアン**（凸凹）から、**集光の強さを近似** |

### テクスチャを投影する

```hlsl
float3 light_space = mul(float4(world_position, 1), light_view_projection).xyz;
float2 caustics_uv = world_position.xz * caustics_scale;

float c1 = caustics_texture.Sample(linear_wrap, caustics_uv + time * float2(0.03, 0.02)).r;
float c2 = caustics_texture.Sample(linear_wrap, caustics_uv * 1.3 - time * float2(0.02, 0.03)).r;
float caustics = min(c1, c2);

float depth_fade = exp(-water_depth_at_point * caustics_falloff);
float3 lit = base_color + sun_color * caustics * depth_fade * n_dot_l;
```

| 点 | 説明 |
| --- | --- |
| **2 枚の `min`** | **向きの違う 2 枚の暗い方を取る**と、**明るい線が細く交差して、リアルな網目** |
| **水深で減衰** | **深い底ほど、光が届かず、弱い** |
| **`n_dot_l`** | **太陽に向いた面だけ**（**壁には弱く**） |
| **水面より上は出さない** | **水位より下の位置だけに投影** |
| **ワールド座標の UV** | **カメラが動いても底に貼りつく**（**真上から投影**が簡単） |

### 色収差で見栄えを上げる

**コースティクスを、RGB でわずかにずらして取る**と、**縁が虹色に光って**、**よりそれらしく**見えます。

```hlsl
float r = caustics_texture.Sample(linear_wrap, caustics_uv + float2(0.002, 0)).r;
float g = caustics_texture.Sample(linear_wrap, caustics_uv).r;
float b = caustics_texture.Sample(linear_wrap, caustics_uv - float2(0.002, 0)).r;
float3 caustics_rgb = float3(r, g, b);
```

## よくあるミス

??? failure "水底の模様が、動かない・単調"
    **2 枚を逆向きに流して重ねる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **揺れる模様を、光の方向から投影**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水中の表現](index.md)
- [光の筋](god-rays.md)
