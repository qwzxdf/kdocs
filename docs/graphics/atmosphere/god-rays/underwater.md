---
title: Underwater God Rays
tags:
  - 描画
---

# Underwater God Rays

<strong>水中の光の筋は、水面の波で揺れながら、差し込みます</strong>。<strong>波の高さを反映したレイマーチ</strong>で、表現できます。このページでは、水中のゴッド レイを説明します。

!!! tip "ポイント"
    - 水面の波の形が、筋の揺れになる。
    - 水が濁っているほど、筋が見える。
    - 深さとともに、弱まる。
    - 詳細は、[Underwater God Rays](../../water/underwater/god-rays.md)。

## 水中の光の筋
<strong>水中の光の筋</strong>は、<strong>同じ原理</strong>でコースティクスで揺らぎが付くのが特徴です（[Underwater Rendering](../../water/underwater/index.md)）。

### 水中で光の筋が出る理由

水中には、プランクトンや砂粒などの微粒子が浮かんでいるので、水中でも光が散乱されます。水面を通り抜けた太陽光は、波の形に応じて屈折し、水中のあちこちへ集光したり、散らされたりします。結果として、水中には、揺らめく光の筋が生まれます。水は、空気より強く光を吸収するので、赤い光から先に消え、深くなるほど青緑色になり、暗くなります。

### 実装の考え方

陸上の光の筋と同じく、シャドウ マップのレイマーチやボリューメトリック フォグで、視線に沿って日向かどうかを判定します。水中の特徴は、<strong>水面の波が、光の筋の形を決める</strong>ことです。波によって太陽光が不均一に水中へ入るので、光の強さは、水面の形で変調されます。具体的には、水面の波の法線から屈折を計算して、水底への光の集まり方（コースティクス）を求め、これを光の筋の強さに掛けます（[Caustics](../../water/underwater/caustics.md)）。コースティクスのテクスチャをスクロールさせながら、霧の密度に掛けると、水面の揺れに連動して揺らめく光の筋になります。

水中のボリュームの密度は、深くなるほど濃くする（光が吸収されるので）か、色を青緑に変えます。水の濁りも密度で表すと、きれいな海と濁った湖で、光の筋の見え方を変えられます。詳しくは、水の章の[Underwater God Rays](../../water/underwater/god-rays.md)を参照してください。

## 水中の、光の筋

<strong>水中</strong>で、<strong>水面から、差し込む、太陽の光</strong>は、光の筋に、なります。水中の、細かい粒子（プランクトン、泥）が、光を、散乱して、光の通り道を、見せるためです。空気中の、ゴッド レイと、同じ原理ですが、水の、吸収（赤が、先に消える）と、波による、揺れが、加わります。

詳しい、実装は、<strong>水の、セクション</strong>で、扱っています（[Underwater God Rays](../../water/underwater/god-rays.md)）。ここでは、<strong>空気中との、違い</strong>を、整理します。

## 空気中との、違い

| 項目 | 空気中 | 水中 |
| --- | --- | --- |
| 光の、色 | 太陽の色（白、橙） | 青緑（赤が、吸収される） |
| 減衰 | ゆるやか（数 km） | 急（数十 m で、消える） |
| 光の筋の、揺れ | ほぼ、無し（霧の、ゆらぎ） | 波による、強い、揺れ（コースティクス） |
| 光の向き | 太陽の方向 | 水面で、屈折して、真下に、近づく（最大で、約 48.6°） |
| 見える、距離 | 長い | 短い（水の濁りで、数 m〜数十 m） |

## 色と、減衰

<strong>水中の、光の筋の色</strong>は、<strong>水面から、そこまでの、深さ</strong>に応じて、赤から、順に、吸収されます。浅い所は、明るい青緑、深くなるほど、暗い青です。

```hlsl
// 水中の光の筋: 水面からの深さと、カメラまでの距離の、両方で、減衰させる。
float3 UnderwaterSunColor(float depth_below_surface, float distance_to_camera) {
  float3 sun_at_depth = g_sun_color * exp(-g_absorption * depth_below_surface);       // 水面 → この点（太陽の光）
  float3 to_camera = exp(-g_absorption * distance_to_camera);                          // この点 → カメラ（散乱した光）
  return sun_at_depth * to_camera;
}
```

<strong>2 回の減衰</strong>（<strong>太陽 → 点</strong>、点 → カメラ）が、両方、効きます。どちらも、Beer の法則です。深く、遠い光の筋は、ほぼ見えません。

## 光の向き（屈折）

<strong>太陽の光</strong>は、<strong>水面で、屈折</strong>して、水中へ入ります。水中での、光の向きは、空気中と違います。

```hlsl
// 水中での、太陽の光の向き。水面の法線は、真上 (0, 1, 0) とする（波は、無視）。
float3 UnderwaterLightDir(float3 sun_dir) {
  // sun_dir は、光が来る向き（太陽へ向かう）。進む向きは、逆。
  return refract(-sun_dir, float3(0, 1, 0), 1.0 / 1.33);
}
```

<strong>太陽が、地平線に近い</strong>（斜めの、光）ほど、<strong>水中では、真下に近づく</strong>（スネルの法則）ので、光の筋は、常に、ほぼ、下向きです。

## 波による、揺れ

<strong>水面の、波</strong>は、<strong>レンズ</strong>のように、光を、集めたり、散らしたりします（コースティクス）。光の筋の、強さを、コースティクスの模様で、変調します（[Caustics](../../water/underwater/caustics.md)）。

```hlsl
// 光の筋の強さに、コースティクスの模様を、掛ける。波が、動くと、光の筋も、ゆらぐ。
float caustic = SampleCaustic(p);                                     // 水面の波が作る、光の濃淡
scatter *= caustic;
```

<strong>水面が、揺れる</strong>と、<strong>水中の、光の筋が、ゆらゆらと、揺れ動き</strong>ます。水中らしさを、強く与える、重要な、効果です。

## 手法の、選択

| 手法 | 水中での、使い方 |
| --- | --- |
| 放射状ブラー | 水面（明るい、窓）を、光源として、放射状に、ぼかす。簡単で、軽い |
| シャドウ マップ レイマーチ | 岩や、船の、影で、光の筋が、遮られる。波の、コースティクスで、変調。正確（重い） |
| 光の筋の、メッシュ | 水面から、下へ、板を置く。アーティスト制御。軽い |
| ボリューム フォグ | 水中を、ボリュームとして、扱い、吸収と散乱を、同時に、計算 |

## よくあるミス

??? failure "水中の光の筋が、揺れない"
    <strong>波を反映</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波で揺れる筋を、水中に差す

## 参考

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Underwater God Rays](../../water/underwater/god-rays.md)
