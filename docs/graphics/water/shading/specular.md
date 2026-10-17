---
title: スペキュラ（太陽の反射）
tags:
  - 描画
---

# スペキュラ（太陽の反射）

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

| 点 | 説明 |
| --- | --- |
| **高い `shininess`** | **水面は滑らかなので鋭いハイライト**（例：256 以上） |
| **GGX を使う** | **PBR の規約と揃える**（[PBR](../../../3d/pbr.md)）。**粗さ（roughness）を小さく** |
| **HDR で出す** | **太陽の反射は非常に明るい**。**ブルームで光る**（[ブルーム](../../postprocess/index.md)） |
| **ちらつき対策** | **細かい法線は距離でぼかす**（**粗さを距離で上げる**）。**さもないと遠くがチカチカする** |

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

- [水の質感](index.md)
- [水面の波](../waves/index.md)
