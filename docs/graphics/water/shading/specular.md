---
title: Specular (Sun Glint)
tags:
  - 描画
---

# Specular (Sun Glint)

**水面に映る太陽のきらめきが、水らしさを決める大きな要素**です。**法線の細かい凹凸で、きらきらと散らばる反射**になります。このページでは、**スペキュラの計算と、きらめきの出し方**を説明します。

!!! tip "ポイント"
    - **GGX などで、太陽の反射を計算**する。
    - **法線の細かい凹凸で、反射が散らばる**。
    - **粗さを、波の大きさに合わせる**。
    - **遠くは、ちらつくので、粗さを上げる**。

## スペキュラ（太陽の反射）
**太陽が水面に映ると細かい波ごとに小さな反射が散らばって見えます**（**グリント**）。**法線マップの細かい法線**で、**Blinn–Phong・GGX のスペキュラ**を**計算**します。

```hlsl
float3 half_vector = normalize(light_dir + view_dir);
float n_dot_h = saturate(dot(normal, half_vector));
float specular = pow(n_dot_h, shininess) * sun_intensity;
```

コードの要点です。水面は滑らかなので、`shininess` を高くして（例：256 以上）鋭いハイライトにします。GGX を使うと PBR の規約と揃い、粗さ（roughness）を小さくします（[PBR](../../../3d/pbr.md)）。太陽の反射は非常に明るいので、HDR で出して、ブルームで光らせます（[ブルーム](../../postprocess/index.md)）。細かい法線は、距離でぼかして（粗さを距離で上げる）、遠くのチカチカを防ぎます。

## よくあるミス

??? failure "遠くの水面で、反射がちらつく"
    **距離に応じて粗さを上げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **法線の凹凸で、太陽が散らばって映る**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Shading](index.md)
- [Water Waves](../waves/index.md)
