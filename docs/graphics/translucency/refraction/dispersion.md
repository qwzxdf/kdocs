---
title: Dispersion
tags:
  - 描画
---

# Dispersion

**光の波長ごとに屈折率が違うため、ガラスの縁で、色が分かれて見える**ことがあります。**赤・緑・青で、ずらす量を変える**と、**この効果を作れます**。このページでは、**分散の表現**を説明します。

!!! tip "ポイント"
    - **波長ごとに屈折率が違う ＝ 分散**。
    - **R・G・B で、ずらす量を変えて、3 回読む**。
    - **宝石・プリズムなど、強い分散の物体に効果的**。
    - **やりすぎない**（普通のガラスは、ほぼ目立たない）。

## 色収差（分散）
**波長ごとに屈折率が少し違う**ので、**ガラスの縁で、色がずれて見えます**（**プリズムの虹**）。**R・G・B で、屈折の強さを少しずつ変えて、3 回サンプル**します。

```hlsl
float3 background;
background.r = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.00).r;
background.g = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.03).g;
background.b = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.06).b;
```

**わずか（数%）の差**で**十分**です。**宝石・水晶・厚いガラス**で**効果的**です。

### 分散の原理

物質の屈折率は、光の波長によってわずかに違います。たとえばガラスでは、青い光（波長が短い）のほうが、赤い光より少し大きく曲がります。ふつうの窓ガラスでは差が小さく気づきませんが、プリズムやダイヤモンド、水滴の縁では、この差が白い光を虹色に分けて見せます。これが分散です。

### 実装の考え方

RGB の 3 チャンネルで、屈折率を少しずつ変えて、背景を 3 回読みます。赤は屈折率が小さいので歪みが小さく、緑は中間、青は歪みが大きい、というようにします。それぞれのチャンネルの結果だけを取り出して合成すれば、縁に虹色の色ずれが出ます。

```hlsl
float3 DispersedRefraction(float2 uv, float2 offset, float spread) {
  float r = scene_color_copy.Sample(linear_clamp, uv + offset * (1.0 - spread)).r;
  float g = scene_color_copy.Sample(linear_clamp, uv + offset).g;
  float b = scene_color_copy.Sample(linear_clamp, uv + offset * (1.0 + spread)).b;
  return float3(r, g, b);
}
```

`spread` は 0.02〜0.1 程度の小さな値です。多くのサンプルで波長を細かく分けるほど、虹が滑らかになります（[Chromatic Aberration](../../postprocess/lens-effects/chromatic-aberration.md) の多サンプル版と同じ方法です）。ダイヤモンドのような強い分散を見せたいときは、サンプルを 8 個以上に増やし、各サンプルに波長に応じた色の重みを付けます。コストは屈折の読み込みの回数倍になるので、宝石のように、分散が主役の物にだけ使うのが現実的です。

## よくあるミス

??? failure "すべてのガラスに強い色収差を付けて、安っぽくなる"
    **宝石など、分散が目立つ物だけに使う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **R・G・B で、ずらす量を変える**
    - [x] **控えめに使う**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Refraction](index.md)
- [色収差（レンズ）](../../postprocess/lens-effects/index.md)
