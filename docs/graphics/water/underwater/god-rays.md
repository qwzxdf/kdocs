---
title: 水中の光の筋
tags:
  - 描画
---

# 水中の光の筋

**水中では、水面から差し込む光が、筋になって見えます**。**波の形で、筋が揺れる**のが**特徴**です。このページでは、**水中の光の筋**を説明します。

!!! tip "ポイント"
    - **シャドウ マップを使った、レイマーチ**で作る。
    - **波の形で、筋が揺れる**。
    - **水が濁っているほど、筋が見える**。
    - **画面空間のぼかしで、安く作る方法もある**。

## 光の筋（ゴッド レイ）
**水中に差し込む光の柱**です。**水中の粒子が光を散らして見える**ことで**生じます**。

| 方式 | 内容 |
| --- | --- |
| <strong>レイマーチ（ボリューム）</strong> | **視線に沿って進み、光が当たる点を数える**。**シャドウ マップで光が届くか判定** |
| **ポストプロセスの放射ぼかし** | **画面上で光源から放射状にぼかす**（安い） |
| <strong>ビルボード（メッシュ）</strong> | **光の筋の形をした半透明メッシュ**を、**加算で描く** |

**レイマーチの基本形**です。

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
| **ジッター** | **開始位置をずらしてノイズ化**し、**少ない段数でも縞が出ない** |
| **シャドウ マップ** | **水面を通った光の柱は、物の影で切れる** |
| **コースティクス** | **光の筋が波の形で揺れる**（水面のうねりに応じて明暗） |
| **透過率** | **遠くほど減衰** |

## よくあるミス

??? failure "光の筋が、揺れずに固定されて見える"
    **水面の波を、光の筋に反映**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **波に応じて揺れる光の筋**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水中の表現](index.md)
- [ゴッド レイ](../../atmosphere/god-rays/index.md)
