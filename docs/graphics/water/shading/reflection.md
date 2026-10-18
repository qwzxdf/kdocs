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

反射の取り方は 4 つあります。環境マップ（キューブ）は安く、空や遠景だけを映し、近くの物は映りません。平面反射は、水面が平らなので鏡像用にもう一度描く方法で、正確ですが重くなります。SSR は画面内の物を映し、画面外は環境マップに落とします。レイトレ反射は最も正確ですが、重くなります。

**波で法線が傾く**ので**反射ベクトルを法線から作り**、**平面反射なら、法線の XZ で UV をずらして歪ませます**。

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);
float3 reflection = environment.SampleLevel(linear_clamp, reflect_dir, 0).rgb;
```

### 組み合わせ方

実際のゲームでは、これらを重ねます。基本は環境マップで、空と遠景を安定して映します。その上に SSR を足して、近くの岸辺や船、橋の映り込みを出します。SSR が当たらなかった画素（画面外や画面端）は、環境マップにフェードで戻します（[SSR Fallback and Compositing](../../reflections/ssr-fallback.md)）。湖や池のように水面が完全に平らな場合は、平面反射が品質で勝ります。波のある海は、法線が場所ごとに違い、反射方向がバラバラになるので、平面反射の鏡像を、波の法線の XZ 成分で歪ませて使います。

反射の強さは、フレネルで決まります（[Water Fresnel](fresnel.md)）。真上から見るとほとんど反射せず、斜めから見るほど鏡に近づくので、反射の質が目立つのは遠くの水面です。遠くの水面は法線が細かく揺れてちらつきやすいため、距離に応じて法線を平らにする（粗さを上げる）処理を入れます。

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
