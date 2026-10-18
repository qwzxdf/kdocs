---
title: Underwater God Rays
tags:
  - 描画
---

# Underwater God Rays

<strong>水中では、水面から差し込む光が、筋になって見えます</strong>。<strong>波の形で、筋が揺れる</strong>のが特徴です。このページでは、水中の光の筋を説明します。

!!! tip "ポイント"
    - シャドウ マップを使った、レイマーチで作る。
    - 波の形で、筋が揺れる。
    - 水が濁っているほど、筋が見える。
    - 画面空間のぼかしで、安く作る方法もある。

## 光の筋（ゴッド レイ）
<strong>水中に差し込む光の柱</strong>です。<strong>水中の粒子が光を散らして見える</strong>ことで生じます。

光の筋の方式は 3 つです。レイマーチ（ボリューム）は、視線に沿って進み、光が当たる点を数える方法で、シャドウ マップで光が届くかを判定します。ポストプロセスの放射ぼかしは、画面上で光源から放射状にぼかす安い方法です。ビルボード（メッシュ）は、光の筋の形をした半透明メッシュを加算で描きます。

<strong>レイマーチの基本形</strong>です。

```hlsl
float3 ray_origin = camera_position;
float3 ray_dir = normalize(world_position - camera_position);
float ray_length = distance_to_pixel;

float step_length = ray_length / kStepCount;
float jitter = InterleavedGradientNoise(input.position.xy);
float3 accumulated = 0;

for (int i = 0; i < kStepCount; ++i) {
  float3 sample_position = ray_origin + ray_dir * (i + jitter) * step_length;
  float shadow = SampleShadowMap(sample_position);
  float caustics = SampleCaustics(sample_position);
  float transmittance = exp(-density * (i + jitter) * step_length);
  accumulated += sun_color * shadow * caustics * transmittance * step_length;
}
```

| 点 | 説明 |
| --- | --- |
| ジッター | 開始位置をずらしてノイズ化し、少ない段数でも縞が出ない |
| シャドウ マップ | 水面を通った光の柱は、物の影で切れる |
| コースティクス | 光の筋が波の形で揺れる（水面のうねりに応じて明暗） |
| 透過率 | 遠くほど減衰 |

## 水中の、光の筋

水の中では、<strong>水面から、差し込む太陽光が、筋になって、見えます</strong>。水中に、<strong>細かい粒子</strong>（プランクトン、泥）があり、光の通り道で、光が、散乱して、光の通り道だけが、明るくなるためです（空気中の、ゴッド レイと、同じ原理、[God Rays](../../atmosphere/god-rays/index.md)）。

水中では、<strong>波が、光を、集めたり、散らしたり</strong>する（コースティクスの、3 次元版）ので、<strong>光の筋が、揺れ動き</strong>ます。

## 方法 1：放射状の、ブラー（画面空間）

<strong>太陽の画面上の位置</strong>から、<strong>画素に向かって、何回か、読んで、足す</strong>方法です（[Screen-Space Radial Blur](../../atmosphere/god-rays/radial-blur.md)）。水中では、太陽は、水面の向こうなので、水面の、明るさ（波を通った、太陽光）を、光の源とします。

```hlsl
// 水中で、画面の上方（太陽の方向）へ向かって、放射状に読んで、足す。
float2 sun_screen = ProjectToScreen(camera_position - sun_dir * 1000.0);   // 太陽の画面上の位置
float2 delta = (uv - sun_screen) / kSamples * density;
float2 sample_uv = uv;
float illum = 0.0, weight = 1.0;
for (int i = 0; i < kSamples; ++i) {
  sample_uv -= delta;
  illum += g_light_mask.Sample(g_linear_clamp, sample_uv).r * weight;     // 明るい（光が、通っている）部分
  weight *= decay;
}
float3 god_rays = illum / kSamples * sun_color_underwater * intensity;
```

| 項目 | 内容 |
| --- | --- |
| 軽い | 画面全体の、後処理。数回〜数十回の読み込み |
| 光の源 | 水面の、明るさ（波を通った、太陽光）、または、水面の、見え方を、マスクにする |
| 弱点 | 遮蔽物（岩、船）が、光を遮る、正確な影が、出ない。太陽が、画面の外にあると、使えない |

## 方法 2：シャドウ マップを使った、レイマーチ

<strong>水中の、各画素について</strong>、<strong>視線に沿って、少しずつ進み</strong>、各点が、太陽光を、受けているか（影の中か）を、調べて、足し合わせます。水面の波による、光の、変調も、含められます（[Shadow Map Raymarching](../../atmosphere/god-rays/shadowmap-march.md)）。

```hlsl
// 視線に沿って進み、各点で、太陽光が届いているかを、シャドウ マップと、コースティクスで調べる。
float3 pos = camera_position;
float step = ray_length / kSteps;
float3 in_scatter = 0;
for (int i = 0; i < kSteps; ++i) {
  pos += view_dir * step;
  float lit = SampleShadowMap(pos);                              // 太陽光が、届いているか（0〜1）
  float caustic = SampleCaustic(pos);                            // 波が作る、光の濃淡
  float depth_below = surface_y - pos.y;
  float3 sun = sun_color * exp(-g_absorption * depth_below);     // 水面から、この点までの、吸収
  float3 T = exp(-g_absorption * (distance(pos, camera_position)));     // この点から、カメラまでの、吸収
  in_scatter += sun * lit * caustic * T * g_scatter * step;
}
```

| 項目 | 内容 |
| --- | --- |
| 精度 | 岩や船の影で、光の筋が、遮られる。正確 |
| 波の影響 | コースティクスを、掛けると、光の筋が、波で、揺れる |
| 重い | 画素ごとに、数十回の、ステップ。低解像度で計算して、アップサンプルする |
| 吸収 | 水面からの深さと、カメラまでの距離の、両方で、減衰を掛ける |

## 方法 3：光の筋の、メッシュ

水面から、水中に向かって、<strong>細長い、半透明の、板（またはメッシュ）</strong>を、置く方法です（[Light Shaft Meshes](../../atmosphere/god-rays/mesh-shafts.md)）。

| 項目 | 内容 |
| --- | --- |
| 形 | 太陽の向きに沿った、細長い板。上は、明るく、下に向かって、消える |
| 動き | 波に合わせて、ゆっくり、揺らす（位置と、明るさ） |
| 軽い | 板を、数十枚描くだけ |
| 弱点 | 影や、遮蔽物と、連動しない。見た目が、決まった形に |

<strong>加算ブレンド</strong>で、描きます。板が、重なる所が、<strong>明るくなります</strong>。

## 水中らしさを、出す工夫

| 工夫 | 内容 |
| --- | --- |
| 波で、揺らす | 光の筋の、強さを、コースティクスの、模様で、変調する（水面の、揺れが、筋の揺れになる） |
| 深さで、消す | 光は、深くなるほど、吸収されて、消える。浅い所だけ、明るい筋 |
| 青緑に、着色 | 水中の、太陽光の、色（赤が、吸収された、青緑）で、描く |
| 粒子 | 光の筋の中に、細かい粒子（マリン スノー）を、漂わせると、光の筋が、立体的に見える（[Other Underwater Elements](other.md)） |

## 太陽の位置による、見え方

| 太陽の位置 | 見え方 |
| --- | --- |
| 真上（正午） | 光の筋が、真下へ、まっすぐ。ほぼ、垂直 |
| 低い（朝夕） | 光の筋が、斜め。筋が、長く、屈折で、曲がる |
| 水面の向こう側を、見る | 筋が、カメラに向かって来る。まぶしい（光が、強い） |
| 曇り、夜 | 光の筋が、無い |

太陽が、<strong>水面で屈折</strong>するので、水中での、光の向きは、<strong>空気中の向きと、違います</strong>（スネルの法則、[Refraction](../shading/refraction.md)）。水中の光の向きは、`refract(−sun_dir, (0,1,0), 1/1.33)` で、求めます。太陽が、水平線に近くても、水中では、真下に、近づく向きに、曲がります（最大でも、約 48.6°）。

## よくあるミス

??? failure "光の筋が、揺れずに固定されて見える"
    <strong>水面の波を、光の筋に反映</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波に応じて揺れる光の筋

## 参考

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Wronski, "Volumetric Fog and Lighting", SIGGRAPH 2014（ボリューム ライティング）

## 関連ページ

- [Underwater Rendering](index.md)
- [God Rays](../../atmosphere/god-rays/index.md)
