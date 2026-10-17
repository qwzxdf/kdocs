---
title: Water Reflection
tags:
  - 描画
---

# Water Reflection

**水面には、空や周囲の景色が映ります**。**空は、環境マップで安く**、**周囲の物は、SSR や平面反射**で映します。このページでは、**水の反射の手法と、使い分け**を説明します。

!!! tip "ポイント"
    - **空は、環境マップ（キューブマップ）**。
    - **周囲の物は、SSR・平面反射**。
    - **法線で反射方向をずらして、波の歪みを出す**。
    - **フォールバックの順：SSR → 平面反射 → 環境マップ**。

## 反射
**反射はフレネルの F で重みを付けて合成**します。**反射の取り方は、状況で選びます**。

| 方式 | 内容 |
| --- | --- |
| <strong>環境マップ（キューブ）</strong> | **安い**。**空や遠景だけ**。**近くの物は映らない** |
| **平面反射** | **水面は平らなので鏡像用にもう一度描く**。**正確だが重い**（[平面反射](../../reflections/index.md)） |
| **SSR** | **画面内の物を映す**。**画面外は環境マップに落とす** |
| **レイトレ反射** | **最も正確**。**重い** |

**波で法線が傾く**ので**反射ベクトルを法線から作り**、**平面反射なら、法線の XZ で UV をずらして歪ませます**。

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);
float3 reflection = environment.SampleLevel(linear_clamp, reflect_dir, 0).rgb;
```

## よくあるミス

??? failure "水面の反射が、画面の端で途切れる"
    **環境マップへフォールバック**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空は環境マップ、周囲は SSR か平面反射**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Shading](index.md)
- [Reflections](../../reflections/index.md)
- [Planar Reflections](../../reflections/planar.md)
