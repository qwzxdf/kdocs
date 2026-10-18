---
title: Underwater God Rays
tags:
  - 描画
---

# Underwater God Rays

**水中の光の筋は、水面の波で揺れながら、差し込みます**。**波の高さを反映したレイマーチ**で、**表現できます**。このページでは、**水中のゴッド レイ**を説明します。

!!! tip "ポイント"
    - **水面の波の形が、筋の揺れになる**。
    - **水が濁っているほど、筋が見える**。
    - **深さとともに、弱まる**。
    - **詳細は、[Underwater God Rays](../../water/underwater/god-rays.md)**。

## 水中の光の筋
**水中の光の筋**は、**同じ原理**で**コースティクスで揺らぎが付く**のが**特徴**です（[Underwater Rendering](../../water/underwater/index.md)）。

### 水中で光の筋が出る理由

水中には、プランクトンや砂粒などの微粒子が浮かんでいるので、水中でも光が散乱されます。水面を通り抜けた太陽光は、波の形に応じて屈折し、水中のあちこちへ集光したり、散らされたりします。結果として、水中には、揺らめく光の筋が生まれます。水は、空気より強く光を吸収するので、赤い光から先に消え、深くなるほど青緑色になり、暗くなります。

### 実装の考え方

陸上の光の筋と同じく、シャドウ マップのレイマーチやボリューメトリック フォグで、視線に沿って日向かどうかを判定します。水中の特徴は、<strong>水面の波が、光の筋の形を決める</strong>ことです。波によって太陽光が不均一に水中へ入るので、光の強さは、水面の形で変調されます。具体的には、水面の波の法線から屈折を計算して、水底への光の集まり方（コースティクス）を求め、これを光の筋の強さに掛けます（[Caustics](../../water/underwater/caustics.md)）。コースティクスのテクスチャをスクロールさせながら、霧の密度に掛けると、水面の揺れに連動して揺らめく光の筋になります。

水中のボリュームの密度は、深くなるほど濃くする（光が吸収されるので）か、色を青緑に変えます。水の濁りも密度で表すと、きれいな海と濁った湖で、光の筋の見え方を変えられます。詳しくは、水の章の[Underwater God Rays](../../water/underwater/god-rays.md)を参照してください。

## よくあるミス

??? failure "水中の光の筋が、揺れない"
    **波を反映**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **波で揺れる筋を、水中に差す**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Underwater God Rays](../../water/underwater/god-rays.md)
