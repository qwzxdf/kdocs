---
title: Light Shaft Meshes
tags:
  - 描画
---

# Light Shaft Meshes

**窓から差し込む光など、位置が決まっている光の筋は、半透明のメッシュ（光の柱）で作る**と、**最も軽く済みます**。このページでは、**メッシュによる光の柱**を説明します。

!!! tip "ポイント"
    - **加算ブレンドの、細長いメッシュ**を置く。
    - **縁と端を、フェードさせる**。
    - **カメラに近づくと、フェードで消す**。
    - **動かない光に、最適**。

## メッシュで光の柱を作る
<strong>固定された光の柱（窓から差す光、洞窟の天井の穴）</strong>は、**半透明メッシュ**で**作れます**。

光の柱を自然に見せる工夫です。形は、光が通る形の錐台や箱のメッシュにします。加算ブレンドで背景に足して光らせます。フレネル風の縁として、視線と面の角度で縁を薄くし、輪郭を消します。深度フェードで、床や壁との交差部を薄くし、ハードな線を消します。ノイズや流れとして、テクスチャを流し、ほこりの揺らぎを出します。カメラが近づくと、近すぎる柱は薄くしてフェードアウトさせます。

```hlsl
float edge_fade = pow(saturate(abs(dot(normal, view_dir))), 2.0);
float depth_fade = saturate((scene_depth - pixel_depth) / fade_distance);
float near_fade = saturate((pixel_depth - near_fade_start) / near_fade_range);
float dust = dust_texture.Sample(linear_wrap, uv + time * 0.02).r;
float alpha = edge_fade * depth_fade * near_fade * (0.7 + 0.3 * dust) * intensity;
return float4(light_color * alpha, 0);
```

### 作り方のコツ

メッシュの光の柱は、アーティストが作るので、見た目の自由度が最も高い方式です。作るときのコツを挙げます。

形は、窓の形をそのまま光の方向に押し出した<strong>錐台</strong>が基本です。太陽は平行光なので、実際には窓と同じ大きさの柱になるはずですが、少し広げる（先細りでなく先広がりにする）と、光の拡散を表せます。柱を何本かの平面で構成する場合は、カメラに向かって回転する<strong>ビルボード</strong>にすると、どの角度から見ても板に見えません。

強さは、柱の中心を明るく、縁を暗くします。上に書いたフレネル風の縁（`pow(dot(normal, view_dir), 2)`）がそれです。さらに、柱の長さ方向にも、光源側を明るく、遠い側を暗くするグラデーションを付けると、光が拡散して弱まる様子が出ます。

ほこりの粒は、ノイズ テクスチャをゆっくり流す（UV を時間でずらす）だけで、揺らぎとして見えます。粒の動きに速度の違う 2 枚を重ねると、より自然になります。

メッシュ方式の弱点は、動的な光に対応しにくいことです。太陽が動けば柱の向きも動かす必要があり、窓の前に人が立てば本来は影が出るはずですが、メッシュは対応しません。昼夜サイクルのあるゲームでは、時刻に合わせて柱の向きと色を動かす仕組みが必要になります。

## よくあるミス

??? failure "メッシュの縁が硬く、板に見える"
    **縁をフェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **加算メッシュで、手軽に光の柱**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Blend State](../../translucency/blending-sorting/blend-state.md)
