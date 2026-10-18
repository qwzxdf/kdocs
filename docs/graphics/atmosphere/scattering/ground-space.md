---
title: Ground and Space Views
tags:
  - 描画
---

# Ground and Space Views

<strong>視点が地面にある時と宇宙にある時で、大気の見え方は違います</strong>。<strong>地面からは空が宇宙からは地球の縁が光る</strong>ように見えます。このページでは視点の位置による違いを説明します。

!!! tip "ポイント"
    - 地面：空の色と地平線の霞。
    - 宇宙：地球の縁（リム）の大気。
    - 視点の高さで LUT の使い方が変わる。
    - 地面の反射（アルベド）も、空に影響する。

## 地面と宇宙
| 状況 | 扱い |
| --- | --- |
| 地面の反射 | 地面のアルベドで地平線付近が明るくなる。地面からの散乱を足す |
| 宇宙から見た地球 | 視点が大気の外のとき、大気の入口まで進めてから積分（惑星表面の光る縁） |
| 日食・月食 | 太陽の円盤が欠けるとき、直射光を減らす |
| 影の中の空気 | 山の影で空気中の光の筋が途切れる（[God Rays](../god-rays/index.md)） |

## カメラの高さで見え方が変わる

大気の見え方は <strong>カメラがどこにあるか</strong>で、<strong>まったく</strong>違います。

| カメラの位置 | 見え方 | 空の描き方 |
| --- | --- | --- |
| 地上（高度 0〜数 km） | 空は、頭の上に広がる。地平線はほぼ水平 | Sky-View LUT（[Hillaire 2020: Four LUTs](hillaire.md)） |
| 高い山、飛行機（高度 10 km 前後） | 地平線が、少し下がりわずかに曲がって見える | Sky-View LUT（高度が、LUT の入力） |
| 宇宙（高度 100 km 以上） | 惑星が、球として見える。大気は青い薄い縁 | 画面全体を直接、積分（レイマーチ） |

## 地上から：Sky-View LUT

<strong>カメラが大気の中</strong>にあるなら <strong>空は、カメラの周りの全方向</strong>に広がります。Sky-View LUT に、全方向の色を描いて画面では LUT を、引くだけです。空はゆるやかに変化するので低解像度で、十分です。

## 宇宙から：球体をレイマーチ

<strong>カメラが大気の外</strong>にあるとき、<strong>画面のほとんどは宇宙</strong>（黒）で惑星の円盤が、見えます。大気は惑星の縁に青く細く見えます。この場合、Sky-View LUT（カメラの周りの、全方向）は不適切です。画面の各画素から視線を大気に向けて直接、積分します。

```hlsl
// 宇宙から見る: 画素ごとに、視線が、大気の球と、どう交わるかを、調べて、積分する。
float4 SpaceViewPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 ray_dir = ScreenToViewDir(uv);
  float3 origin = g_camera_position_from_planet_center;

  // 視線と、大気の上端の球との、交点
  float2 t_top = RaySphere(origin, ray_dir, g_top_radius);
  if (t_top.y < 0.0) return float4(0, 0, 0, 0);                        // 大気に、当たらない（宇宙が、見える）
```

視線が <strong>大気の球と交わらない</strong>なら、<strong>何も描きません</strong>（星空や背景が、見える）。

```hlsl
  float t_enter = max(t_top.x, 0.0);                                   // 大気に、入る距離（カメラが、すでに中なら 0）

  // 視線が、地面（惑星の本体）に、当たるなら、そこまで。当たらなければ、大気を、突き抜ける。
  float2 t_ground = RaySphere(origin, ray_dir, g_bottom_radius);
  float t_exit = (t_ground.x > 0.0) ? t_ground.x : t_top.y;

  float3 start = origin + ray_dir * t_enter;
  float ray_length = t_exit - t_enter;
  float3 L = IntegrateScatteredLuminance(start, ray_dir, g_sun_dir, ray_length, /*steps*/ 32);
```

<strong>視線が大気の中を通る区間</strong>（入口から出口、または地面まで）だけを積分します。

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

<strong>惑星の表面</strong>（<strong>地面、海、雲</strong>）の色を大気を通した透過率を掛けて、足します。昼側では青い大気を通して地面や海が見え夜側は、暗くなります。

## 地面の色

宇宙から <strong>惑星を見る</strong>とき <strong>地面の色</strong>が、必要です。

| 方法 | 内容 |
| --- | --- |
| 単色（アルベド） | 簡単。地球なら青緑〜茶色の平均 |
| テクスチャ（惑星全体の地図） | 大陸、海、雪、砂漠を描く。球面へのマッピング（キューブマップ） |
| 昼夜で変える | 夜側に街の、光（夜景テクスチャ）を足す |

## 地上から宇宙への連続的な遷移

<strong>ゲームで地上から宇宙へ上昇する</strong>とき、<strong>高度に応じて 2 つの方式を、切り替え</strong>ます。切り替えの境目が目立たないように、なめらかな遷移が必要です。

| 高度 | 方式 |
| --- | --- |
| 〜50 km | Sky-View LUT（空は、頭上全体に広がる） |
| 50〜150 km | 両方を、ブレンド（空が薄くなり地平線が、曲がって見え始める） |
| 150 km〜 | 宇宙ビュー（画面全体を直接、積分） |

<strong>Sky-View LUT は高度が、高くなる</strong>と <strong>地平線が画像の、下へ寄る</strong>（地平線の角度が大きくなる）ので、連続的に動きます。宇宙ビューとの境目では同じ値になるはずですが、LUT の解像度によるわずかな差が、あります。ブレンドで目立たなくします。

## 大気の縁（リム）

宇宙から惑星を見ると <strong>縁に青い細い帯</strong>が、見えます。<strong>大気を横から</strong>（接線方向に）通る視線が、長い距離を通り散乱が積もるためです。

```text
 宇宙から、惑星の縁を、見る:
       視線 ─────────→   （大気を、長く、通る）
            ╲
        ╭─────╲─────╮
        │ 大気 ╲    │   ← 縁の青い帯（散乱光が、積もる）
        │  惑星     │
```

<strong>視線が大気を通る長さ</strong>が <strong>中心</strong>（真正面から、見る）より縁で非常に長いので縁が明るく青い、リングになります。積分で自然に出るので特別な処理は、不要です。

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
