---
title: Vegetation Lighting
tags:
  - 描画
---

# Vegetation Lighting

<strong>葉は薄く光が透けるので普通の面のライティングでは、暗く見えます</strong>。裏側からの光を足す（透過）ことで、自然な明るさになります。このページでは植生のライティングを説明します。

!!! tip "ポイント"
    - 葉の裏から当たった光を表側に透過させる。
    - 法線を地面や球の向きに寄せて、均一にする。
    - 影はアルファ テストで、切り抜く。
    - 環境光（AO）で、根元を暗くする。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と、読む順番）

## ライティング
| 要素 | 内容 |
| --- | --- |
| 法線 | 草の法線を地形の法線に寄せると草原が面として一様に照らされ、ごちゃつかない |
| 透過光 | 葉は光を通す。太陽が背後にあると明るい |
| AO | 根元を暗く（高さで）。木の内側も暗く |
| 影 | 草は影を落とさない・受けるだけにして、軽くする |

## 草のライティングが難しい理由

草の 1 本は <strong>薄い帯</strong>です。帯に通常のライティングを行うと、次の問題が出ます。

| 問題 | 原因 |
| --- | --- |
| 草原がごちゃごちゃして見える | 帯 1 本ずつの法線がバラバラ。隣り合う草の明るさがまちまち |
| 逆光で真っ黒 | 帯の表が光源と反対を向く。実際の葉は、光を通す |
| 影が重い | 草 1 本ずつが、影を落とす・受ける。数百万本の影は計算できない |
| 草と地面が別物に見える | 草の色、明るさと地面の色、明るさが合っていない |

## ① 法線を地面に合わせる

草原を <strong>1 枚の面</strong>のように、照らすのがきれいに見せる最大のコツです。草の法線を 地形の法線（または、真上）に寄せます。

```hlsl
// 草の法線を地形の法線と、真上へ寄せて、草原全体を 1 つの面のように、照らす。
float3 GrassNormal(float3 blade_normal, float3 terrain_normal, float height_t) {
  // 根元は、地面の法線。先端は、少し、帯の法線を混ぜる。
  float3 n = lerp(terrain_normal, blade_normal, 0.3 * height_t);
  return normalize(n);
}
```

| 寄せ方 | 効果 |
| --- | --- |
| 地形の法線にする | 草原が地形の起伏と一体の陰影になる（斜面は暗く日向は、明るい） |
| 真上（0, 1, 0）に寄せる | 草がどこでも上から照らされた様子になる。地形の陰影を無視する |
| 帯の法線を少し混ぜる | 1 本ごとの細かい、明暗の違いが少し出る |

どの程度寄せるかは見た目で決めます。完全に地形の法線だと平板に見えます。

## ② 透過光

葉は薄いので <strong>裏から当たった光が透けて、表に出てきます</strong>。太陽を背にして草を見ると 明るく透けて見えるのは、このためです。

簡単な近似は 視線と光の向きから、透過を求めるものです（Barré-Brisebois と Bouchard、2011 の考え方を簡略にしたもの）。

```hlsl
// 透過光: 光が葉の裏から当たり、視線の方向へ抜けてくる分。
float3 FoliageTranslucency(float3 normal, float3 view_dir, float3 light_dir, float3 light_color,
                           float3 albedo, float thickness) {
  // 光の向きを法線で少し曲げる（葉の中での、屈折・散乱の近似）
  float3 h = normalize(light_dir + normal * 0.3);
  // 視線の方向と、曲げた光の向きが、逆向きに近い（光がこちらへ抜けてくる）ほど、強い。
  float t = pow(saturate(dot(view_dir, -h)), 4.0);
  // 薄い葉ほど、透ける
  return albedo * light_color * t * (1.0 - thickness);
}
```

| パラメーター | 内容 |
| --- | --- |
| `thickness` | 葉の厚さ（0 = 薄い、1 = 厚い）。テクスチャで与える |
| 指数（`pow` の 4.0） | 大きいほど、太陽の方向を見たときだけ強く光る |
| `albedo` | 透けた光の色は葉の色（緑や黄色）になる。白い光は透けない |

全体の明るさに足し込みます。

```hlsl
float3 lit = diffuse_lighting + FoliageTranslucency(n, v, l, light_color, albedo, thickness);
```

## ③ 環境光・AO

草の根元は <strong>周りの草に挟まれて、暗い</strong>はずです。草 1 本ずつの AO は計算できないので、高さ `t` で近似します。

```hlsl
// 根元ほど暗くする（周りの草に遮られている）
float ao = lerp(0.3, 1.0, saturate(height_t * 1.5));
float3 ambient = ambient_light * albedo * ao;
```

| 要素 | 内容 |
| --- | --- |
| 根元の暗さ | 0.2〜0.4（草の密度が高いほど、暗い） |
| 先端の明るさ | 1.0 |
| 地面の色との馴染み | 根元の色を地形の色に合わせる（[Grass Shape](grass-shape.md)） |

環境光が 空の色（上は青、下は地面の色）なら 草の裏側（下向きの面）に地面の色を足すとより自然です。

## ④ 影

| 影 | 内容 |
| --- | --- |
| 草が受ける影 | 木、建物、岩の影を草が受ける。普通に、シャドウ マップを引く（影の中の草は、暗くなる） |
| 草が落とす影 | 落とさないことが多い。草 1 本ずつをシャドウ マップに描くと、数百万本が重い |
| 草の影を代わりに表現する | 地面のテクスチャに暗い色を焼くまたは AO の模様を描く |
| 木が落とす影 | 木の葉は、アルファ テストで影も切り抜く（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |

<strong>草の影は省略する</strong>ことが一般的な選択です。そのかわり 地面のライティングに草の影の印象を足す（地形の色を草が生えている場所で少し暗くする）と、自然に見えます。

## ⑤ スペキュラー

草の光沢は <strong>葉の表面のワックス質</strong>や、細い葉の方向性から来ます。

| 方針 | 内容 |
| --- | --- |
| 弱いスペキュラー | 粗さを高く（0.7〜0.9）。控えめなつや |
| 遠くの草は切る | 小さい、ハイライトはちらつく（エイリアシング）。遠景ではスペキュラーを 0 にする |
| 地形のスペキュラーに合わせる | 草が生えた地面のスペキュラーとそろえる |

## 草と地形の境目を消す

草のライティングは <strong>地形のライティングと、連続している</strong>必要があります。ずれていると 草が地面から浮いて見えます。

| 項目 | 合わせる |
| --- | --- |
| 色 | 草の根元の色 = 地形のテクスチャの色 |
| 明るさ | 草の法線 ≒ 地形の法線（根元で） |
| 影 | 同じシャドウ マップを同じ精度で引く |
| 霧・大気 | 草にも地形と同じ、距離の霧をかける（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |

## よくあるミス

??? failure "逆光の葉が真っ暗"
    <strong>透過のライティング</strong>を足す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 透過と法線の調整で、自然な明るさ

## 参考

- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）
- Barré-Brisebois, Bouchard, "Approximating Translucency for a Fast, Cheap and Convincing Subsurface Scattering Look", Game Developers Conference 2011
- Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021
- Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004（草の板ポリ、風、クロス ブレンド）
- Boulanger, Pattanaik, Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009

## 関連ページ

- [Vegetation](index.md)
- [Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)
