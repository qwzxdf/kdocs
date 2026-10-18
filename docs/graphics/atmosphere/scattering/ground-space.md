---
title: Ground and Space Views
tags:
  - 描画
---

# Ground and Space Views

<strong>視点が地面にある時と、宇宙にある時で、大気の見え方は違います</strong>。<strong>地面からは空が、宇宙からは地球の縁が光る</strong>ように見えます。このページでは、視点の位置による違いを説明します。

!!! tip "ポイント"
    - 地面：空の色と、地平線の霞。
    - 宇宙：地球の縁（リム）の大気。
    - 視点の高さで、LUT の使い方が変わる。
    - 地面の反射（アルベド）も、空に影響する。

## 地面と宇宙
| 状況 | 扱い |
| --- | --- |
| 地面の反射 | 地面のアルベドで地平線付近が明るくなる。地面からの散乱を足す |
| 宇宙から見た地球 | 視点が大気の外のとき、大気の入口まで進めてから積分（惑星表面の光る縁） |
| 日食・月食 | 太陽の円盤が欠けるとき、直射光を減らす |
| 影の中の空気 | 山の影で空気中の光の筋が途切れる（[God Rays](../god-rays/index.md)） |

## カメラの、高さで、見え方が、変わる

大気の、見え方は、<strong>カメラが、どこにあるか</strong>で、<strong>まったく</strong>違います。

| カメラの位置 | 見え方 | 空の描き方 |
| --- | --- | --- |
| 地上（高度 0〜数 km） | 空は、頭の上に、広がる。地平線は、ほぼ、水平 | Sky-View LUT（[Hillaire 2020: Four LUTs](hillaire.md)） |
| 高い山、飛行機（高度 10 km 前後） | 地平線が、少し下がり、わずかに、曲がって見える | Sky-View LUT（高度が、LUT の、入力） |
| 宇宙（高度 100 km 以上） | 惑星が、球として、見える。大気は、青い、薄い縁 | 画面全体を、直接、積分（レイマーチ） |

## 地上から：Sky-View LUT

<strong>カメラが、大気の中</strong>にあるなら、<strong>空は、カメラの周りの、全方向</strong>に、広がります。Sky-View LUT に、全方向の色を、描いて、画面では、LUT を、引くだけです。空は、ゆるやかに変化するので、低解像度で、十分です。

## 宇宙から：球体を、レイマーチ

<strong>カメラが、大気の外</strong>にあるとき、<strong>画面の、ほとんどは、宇宙</strong>（黒）で、惑星の、円盤が、見えます。大気は、惑星の、縁に、青く、細く見えます。この場合、Sky-View LUT（カメラの周りの、全方向）は、不適切です。画面の、各画素から、視線を、大気に向けて、直接、積分します。

```hlsl
// 宇宙から見る: 画素ごとに、視線が、大気の球と、どう交わるかを、調べて、積分する。
float4 SpaceViewPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 ray_dir = ScreenToViewDir(uv);
  float3 origin = g_camera_position_from_planet_center;

  // 視線と、大気の上端の球との、交点
  float2 t_top = RaySphere(origin, ray_dir, g_top_radius);
  if (t_top.y < 0.0) return float4(0, 0, 0, 0);                        // 大気に、当たらない（宇宙が、見える）
```

視線が、<strong>大気の球と、交わらない</strong>なら、<strong>何も描きません</strong>（星空や、背景が、見える）。

```hlsl
  float t_enter = max(t_top.x, 0.0);                                   // 大気に、入る距離（カメラが、すでに中なら 0）

  // 視線が、地面（惑星の本体）に、当たるなら、そこまで。当たらなければ、大気を、突き抜ける。
  float2 t_ground = RaySphere(origin, ray_dir, g_bottom_radius);
  float t_exit = (t_ground.x > 0.0) ? t_ground.x : t_top.y;

  float3 start = origin + ray_dir * t_enter;
  float ray_length = t_exit - t_enter;
  float3 L = IntegrateScatteredLuminance(start, ray_dir, g_sun_dir, ray_length, /*steps*/ 32);
```

<strong>視線が、大気の中を、通る区間</strong>（入口から、出口、または地面まで）だけを、積分します。

```hlsl
  // 視線が、地面に当たる → 惑星の、表面の色を、大気越しに、足す。
  if (t_ground.x > 0.0) {
    float3 hit_pos = origin + ray_dir * t_ground.x;
    float3 ground_albedo = SampleGroundAlbedo(hit_pos);
    float3 ground_lit = ground_albedo * SunTransmittance(hit_pos, g_sun_dir) * g_sun_illuminance * saturate(dot(normalize(hit_pos), g_sun_dir)) / 3.14159265;
    float3 view_t = Transmittance(start, ray_dir, ray_length);
    L += ground_lit * view_t;                                          // 地面の色が、大気を通って、届く
  }
  return float4(L, 1.0);
}
```

<strong>惑星の、表面</strong>（<strong>地面、海、雲</strong>）の、色を、大気を通した、透過率を、掛けて、足します。昼側では、青い、大気を、通して、地面や海が、見え、夜側は、暗くなります。

## 地面の、色

宇宙から、<strong>惑星を、見る</strong>とき、<strong>地面の、色</strong>が、必要です。

| 方法 | 内容 |
| --- | --- |
| 単色（アルベド） | 簡単。地球なら、青緑〜茶色の、平均 |
| テクスチャ（惑星全体の、地図） | 大陸、海、雪、砂漠を、描く。球面への、マッピング（キューブマップ） |
| 昼夜で、変える | 夜側に、街の、光（夜景テクスチャ）を、足す |

## 地上から、宇宙への、連続的な、遷移

<strong>ゲームで、地上から、宇宙へ、上昇する</strong>とき、<strong>高度に応じて、2 つの、方式を、切り替え</strong>ます。切り替えの、境目が、目立たないように、なめらかな、遷移が、必要です。

| 高度 | 方式 |
| --- | --- |
| 〜50 km | Sky-View LUT（空は、頭上全体に、広がる） |
| 50〜150 km | 両方を、ブレンド（空が、薄くなり、地平線が、曲がって、見え始める） |
| 150 km〜 | 宇宙ビュー（画面全体を、直接、積分） |

<strong>Sky-View LUT は、高度が、高くなる</strong>と、<strong>地平線が、画像の、下へ寄る</strong>（地平線の角度が、大きくなる）ので、連続的に、動きます。宇宙ビューとの、境目では、同じ値になるはずですが、LUT の、解像度による、わずかな差が、あります。ブレンドで、目立たなくします。

## 大気の縁（リム）

宇宙から、惑星を見ると、<strong>縁に、青い、細い、帯</strong>が、見えます。<strong>大気を、横から</strong>（接線方向に）通る視線が、長い距離を、通り、散乱が、積もるためです。

```text
 宇宙から、惑星の縁を、見る:
       視線 ─────────→   （大気を、長く、通る）
            ╲
        ╭─────╲─────╮
        │ 大気 ╲    │   ← 縁の青い帯（散乱光が、積もる）
        │  惑星     │
```

<strong>視線が、大気を、通る長さ</strong>が、<strong>中心</strong>（真正面から、見る）より、縁で、非常に、長いので、縁が、明るく、青い、リングになります。積分で、自然に、出るので、特別な、処理は、不要です。

## よくあるミス

??? failure "宇宙から見た地球に、大気の縁が見えない"
    <strong>宇宙からの視点</strong>でも<strong>大気の積分</strong>を行う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 視点の高さで、積分の範囲が変わる

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Bruneton Precomputed Scattering](bruneton.md)
