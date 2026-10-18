---
title: Vegetation Lighting
tags:
  - 描画
---

# Vegetation Lighting

<strong>葉は薄く、光が透けるので、普通の面のライティングでは、暗く見えます</strong>。<strong>裏側からの光を足す（透過）</strong>ことで、自然な明るさになります。このページでは、植生のライティングを説明します。

!!! tip "ポイント"
    - 葉の裏から当たった光を、表側に透過させる。
    - 法線を、地面や球の向きに寄せて、均一にする。
    - 影は、アルファ テストで、切り抜く。
    - 環境光（AO）で、根元を暗くする。

## ライティング
| 要素 | 内容 |
| --- | --- |
| 法線 | 草の法線を地形の法線に寄せると草原が面として一様に照らされ、ごちゃつかない |
| 透過光 | 葉は光を通す。太陽が背後にあると明るい |
| AO | 根元を暗く（高さで）。木の内側も暗く |
| 影 | 草は影を落とさない・受けるだけにして、軽くする |

## 草の、ライティングが、難しい理由

草の 1 本は、<strong>薄い帯</strong>です。帯に、通常の、ライティングを行うと、次の問題が出ます。

| 問題 | 原因 |
| --- | --- |
| 草原が、ごちゃごちゃして見える | 帯 1 本ずつの、法線が、バラバラ。隣り合う草の、明るさが、まちまち |
| 逆光で、真っ黒 | 帯の、表が、光源と反対を向く。実際の葉は、光を通す |
| 影が、重い | 草 1 本ずつが、影を落とす・受ける。数百万本の影は、計算できない |
| 草と地面が、別物に見える | 草の色、明るさと、地面の色、明るさが、合っていない |

## ① 法線を、地面に合わせる

草原を、<strong>1 枚の、面</strong>のように、照らすのが、きれいに見せる、最大のコツです。草の法線を、<strong>地形の法線</strong>（または、真上）に、寄せます。

```hlsl
// 草の法線を、地形の法線と、真上へ寄せて、草原全体を、1 つの面のように、照らす。
float3 GrassNormal(float3 blade_normal, float3 terrain_normal, float height_t) {
  // 根元は、地面の法線。先端は、少し、帯の法線を混ぜる。
  float3 n = lerp(terrain_normal, blade_normal, 0.3 * height_t);
  return normalize(n);
}
```

| 寄せ方 | 効果 |
| --- | --- |
| 地形の法線にする | 草原が、地形の起伏と、一体の陰影になる（斜面は、暗く、日向は、明るい） |
| 真上（0, 1, 0）に寄せる | 草が、どこでも、上から照らされた様子になる。地形の、陰影を、無視する |
| 帯の法線を、少し混ぜる | 1 本ごとの、細かい、明暗の違いが、少し出る |

<strong>どの程度寄せるか</strong>は、見た目で決めます。完全に、地形の法線だと、平板に、見えます。

## ② 透過光

葉は、薄いので、<strong>裏から当たった光が、透けて、表に出てきます</strong>。太陽を背にして、草を見ると、<strong>明るく透けて見える</strong>のは、このためです。

簡単な、近似は、<strong>視線と光の向きから、透過を求める</strong>ものです（Barré-Brisebois と Bouchard、2011 の考え方を、簡略にしたもの）。

```hlsl
// 透過光: 光が、葉の裏から当たり、視線の方向へ、抜けてくる分。
float3 FoliageTranslucency(float3 normal, float3 view_dir, float3 light_dir, float3 light_color,
                           float3 albedo, float thickness) {
  // 光の向きを、法線で少し曲げる（葉の中での、屈折・散乱の近似）
  float3 h = normalize(light_dir + normal * 0.3);
  // 視線の方向と、曲げた光の向きが、逆向きに近い（光が、こちらへ抜けてくる）ほど、強い。
  float t = pow(saturate(dot(view_dir, -h)), 4.0);
  // 薄い葉ほど、透ける
  return albedo * light_color * t * (1.0 - thickness);
}
```

| パラメーター | 内容 |
| --- | --- |
| `thickness` | 葉の厚さ（0 = 非常に薄い、1 = 厚い）。テクスチャで、与える |
| 指数（`pow` の 4.0） | 大きいほど、太陽の方向を、見たときだけ、強く光る |
| `albedo` | 透けた光の色は、葉の色（緑や黄色）になる。白い光は、透けない |

全体の明るさに、足し込みます。

```hlsl
float3 lit = diffuse_lighting + FoliageTranslucency(n, v, l, light_color, albedo, thickness);
```

## ③ 環境光・AO

草の根元は、<strong>周りの草に、挟まれて、暗い</strong>はずです。草 1 本ずつの、AO は、計算できないので、<strong>高さ `t` で、近似</strong>します。

```hlsl
// 根元ほど暗くする（周りの草に遮られている）
float ao = lerp(0.3, 1.0, saturate(height_t * 1.5));
float3 ambient = ambient_light * albedo * ao;
```

| 要素 | 内容 |
| --- | --- |
| 根元の暗さ | 0.2〜0.4（草の密度が高いほど、暗い） |
| 先端の明るさ | 1.0 |
| 地面の色との馴染み | 根元の色を、地形の色に合わせる（[Grass Shape](grass-shape.md)） |

環境光が、<strong>空の色</strong>（上は青、下は地面の色）なら、<strong>草の裏側（下向きの面）</strong>に、地面の色を足すと、より自然です。

## ④ 影

| 影 | 内容 |
| --- | --- |
| 草が、受ける影 | 木、建物、岩の影を、草が、受ける。普通に、シャドウ マップを、引く（影の中の草は、暗くなる） |
| 草が、落とす影 | 落とさないことが、多い。草 1 本ずつを、シャドウ マップに描くと、数百万本が、重い |
| 草の影を、代わりに、表現する | 地面のテクスチャに、暗い色を焼く、または、AO の模様を描く |
| 木が、落とす影 | 木の葉は、アルファ テストで、影も、切り抜く（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |

<strong>草の影は、省略する</strong>ことが、一般的な選択です。そのかわり、<strong>地面のライティングに、草の影の、印象を足す</strong>（地形の色を、草が、生えている場所で、少し暗くする）と、自然に見えます。

## ⑤ スペキュラー

草の、光沢は、<strong>葉の表面の、ワックス質</strong>や、<strong>細い葉の、方向性</strong>から来ます。

| 方針 | 内容 |
| --- | --- |
| 弱いスペキュラー | 粗さを高く（0.7〜0.9）。控えめな、つや |
| 遠くの草は、切る | 小さい、ハイライトは、ちらつく（エイリアシング）。遠景では、スペキュラーを、0 にする |
| 地形のスペキュラーに合わせる | 草が、生えた地面の、スペキュラーと、そろえる |

## 草と地形の、境目を、消す

草のライティングは、<strong>地形のライティングと、連続している</strong>必要があります。ずれていると、<strong>草が、地面から、浮いて見えます</strong>。

| 項目 | 合わせる |
| --- | --- |
| 色 | 草の根元の色 = 地形のテクスチャの色 |
| 明るさ | 草の法線 ≒ 地形の法線（根元で） |
| 影 | 同じシャドウ マップを、同じ精度で、引く |
| 霧・大気 | 草にも、地形と同じ、距離の霧を、かける（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |

## よくあるミス

??? failure "逆光の葉が、真っ暗"
    <strong>透過のライティング</strong>を足す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 透過と、法線の調整で、自然な明るさ

## 参考

- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Barré-Brisebois, Bouchard, "Approximating Translucency for a Fast, Cheap and Convincing Subsurface Scattering Look", Game Developers Conference 2011
- Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021
- Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004（草の板ポリ、風、クロス ブレンド）
- Boulanger, Pattanaik, Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009

## 関連ページ

- [Vegetation](index.md)
- [Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)
