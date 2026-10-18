---
title: Sun Inscatter
tags:
  - 描画
---

# Sun Inscatter

**太陽の方向を見ると、フォグが明るく黄色っぽく霞みます**。**視線と太陽の方向が近いほど、フォグの色を太陽の色に寄せる**と、**自然**です。このページでは、**太陽方向のにじみ**を説明します。

!!! tip "ポイント"
    - **視線と太陽の内積で、フォグの色を変える**。
    - **太陽側は、暖色・明るい**。
    - **反対側は、空の青**。
    - **ミー散乱の前方散乱に対応**。

## Glow Toward the Sun {#太陽方向のにじみ}
**太陽の方向を見ると霧が明るく・暖色に光ります**（**前方散乱**）。**フォグの色を視線と太陽の角度で変えます**。

```hlsl
float sun_amount = saturate(dot(view_dir, sun_dir));
float3 fog_color_dir = lerp(fog_color, sun_fog_color, pow(sun_amount, 8.0));
```

コードの要点です。`pow(.., 8)` は、太陽のすぐ周りだけが効くように、角度の広がりを絞ります。より正確には、ミー散乱の位相関数である Henyey-Greenstein 関数を使います（[Atmospheric Scattering](../scattering/index.md)）。夕方は、太陽側が赤橙に、反対側が青紫になります。

### Formulation with the Phase Function {#位相関数による定式化}

空気中の粒子（エアロゾル、水滴）による散乱はミー散乱と呼ばれ、強い<strong>前方散乱</strong>が特徴です。光が進んできた方向のまま散らされやすいので、太陽の方向を見たとき、散乱光が最も強くなります。この角度による強さの変化を表す関数が位相関数で、ゲームでは Henyey-Greenstein 関数がよく使われます。

<div class="formula">HG(cosθ, g) = (1 − g²) / (4π · (1 + g² − 2 g cosθ)^(3/2))</div>

g は非対称パラメータ（−1〜1）で、0 なら等方（どの方向にも均等）、1 に近づくほど前方散乱が強くなります。大気中のミー散乱では、g が 0.76 前後の値がよく使われます。θ は、視線と太陽方向のなす角で、cosθ は `dot(view_dir, sun_dir)` です。上の `pow(sun_amount, 8)` は、この関数を単純化した近似と見なせます。

HG 関数を使うと、太陽の方向がどのくらい強く光るかと、広がり方を、g で調整できます。これにフォグの色の計算を組み込むと、次のようになります。

```hlsl
float phase = HenyeyGreenstein(dot(view_dir, sun_dir), 0.76);
float3 fog_color_dir = ambient_fog_color + sun_color * phase * sun_inscatter_scale;
```

空の色（青い環境光）に、太陽の項を<strong>足す</strong>形です。足すことで、太陽側だけが明るく暖色に染まり、反対側は青いままになります。

## Common Mistakes {#よくあるミス}

??? failure "太陽の方向でも、フォグが青いまま"
    **太陽方向の色**を**足す**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **太陽の方向で、フォグの色を変える**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Aerial Perspective and Fog](index.md)
- [Phase Functions](../scattering/phase-function.md)
