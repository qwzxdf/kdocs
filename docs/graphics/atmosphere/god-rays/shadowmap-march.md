---
title: Shadow Map Raymarching
tags:
  - 描画
---

# Shadow Map Raymarching

**視線に沿って進み、各点で「太陽の光が届くか」をシャドウ マップで判定**して、**光の量を足し合わせる**のが**正確な方式**です。**太陽が画面外でも使えます**。このページでは、**シャドウ マップを使ったレイマーチ**を説明します。

!!! tip "ポイント"
    - **視線に沿って、シャドウ マップを参照**。
    - **光が届く点だけ、散乱を足す**。
    - **太陽が画面外でも、動く**。
    - **ステップ数が多いと重いので、ジッタ＋時間蓄積**。

## シャドウ マップでレイマーチ
**正確な方法**は**視線に沿ってサンプル点を歩き、各点が日向か日陰かをシャドウ マップで判定して、日向の点の寄与を足す**ことです。**ボリューメトリック フォグ（[Volumetric Fog](../volumetric-fog/index.md)）と同じ原理**です。

```hlsl
float3 VolumetricGodRays(float3 camera_pos, float3 pixel_world_pos, float2 pixel_coord) {
  float3 ray = pixel_world_pos - camera_pos;
  float ray_length = min(length(ray), kMaxDistance);
  float3 ray_dir = normalize(ray);

  float step_length = ray_length / kStepCount;
  float jitter = InterleavedGradientNoise(pixel_coord);
  float cos_theta = dot(ray_dir, -sun_direction);
  float phase = HenyeyGreenstein(cos_theta, 0.7);

  float3 accumulated = 0;
  for (int i = 0; i < kStepCount; ++i) {
    float3 p = camera_pos + ray_dir * (i + jitter) * step_length;
    float shadow = SampleCascadeShadow(p);
    float height_density = fog_density * exp(-height_falloff * (p.y - fog_base));
    accumulated += shadow * height_density * phase * step_length;
  }
  return accumulated * sun_color;
}
```

| 点 | 説明 |
| --- | --- |
| **ステップ数** | **16〜64 回**。**少ないとジッターのノイズ**が出る |
| **ジッター** | **開始位置をずらして縞を消す**（ブルー ノイズ。**時間蓄積で平均**） |
| **`phase`** | **太陽の方を見ると光が強い**（前方散乱） |
| **密度** | **一様な霧、または高さフォグ**。**ノイズで濃淡**を付けると、**揺らぐ光の筋** |
| **範囲** | **カメラ近くだけ**で十分（**遠くは距離フォグ**） |
| **半解像度で描く** | **ぼかし＋アップサンプリング**で**軽く** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="レイマーチの光の筋">
<text x="20" y="24" class="fig-title">視線上の各点が、日向か日陰かを数える</text>
<polygon points="260,70 400,70 420,190 240,190" fill="#555" fill-opacity="0.35" stroke="#555"/>
<text x="290" y="150" style="font-size:12px">影の領域</text>
<circle cx="80" cy="200" r="6" fill="#e5484d"/><text x="50" y="224" style="font-size:12px">カメラ</text>
<line x1="80" y1="200" x2="700" y2="90" stroke="currentColor" stroke-width="2"/>
<g><circle cx="160" cy="186" r="4" fill="#e5aa28"/><circle cx="240" cy="172" r="4" fill="#e5aa28"/><circle cx="320" cy="158" r="4" fill="#555"/><circle cx="400" cy="144" r="4" fill="#555"/><circle cx="480" cy="130" r="4" fill="#e5aa28"/><circle cx="560" cy="116" r="4" fill="#e5aa28"/><circle cx="640" cy="102" r="4" fill="#e5aa28"/></g>
<text x="440" y="210" style="font-size:12px;fill:#e5aa28">黄 ＝ 日向（光が足される）</text>
<text x="440" y="228" style="font-size:12px">灰 ＝ 日陰（足されない）</text>
</svg>

### 式の意味

この方式は、単散乱の積分を、ステップで離散化したものです。視線上の位置 s における太陽光の寄与は、「その位置が日向か（シャドウ）」「その位置の霧の密度」「太陽と視線のなす角による散乱の強さ（位相関数）」の積です。これを、視線に沿って足し合わせます（さらに厳密には、各サンプルからカメラまでの透過率も掛けますが、薄い霧では省略されることも多いです）。

<div class="formula">L = ∫ shadow(s) · density(s) · phase(θ) · T(s) ds　≈　Σ shadow_i · density_i · phase · Δs</div>

コードの `accumulated += shadow * height_density * phase * step_length` が、この和の 1 項です。`shadow` は 0 か 1（PCF を使えば 0〜1）の値で、シャドウ マップから得ます。

### シャドウ マップの参照

シャドウ マップの参照には、通常の描画と同じカスケード シャドウ マップを使います。各サンプル点のワールド位置が、どのカスケードに入るかを調べ、そのカスケードの深度を引いて比べます（[Cascaded Shadow Maps (CSM)](../../shadows/cascaded.md)）。シャドウ マップの 1 テクセルの大きさは、画面のどの距離でも同じなので、遠くのサンプルでは、シャドウ マップの粗さがそのまま筋のにじみになります。近くのカスケードで見える範囲を、光の筋の最大距離として選ぶのが現実的です。

### ステップ数を減らす工夫

ステップが 16 回では、筋の間隔がステップ幅に近い細い筋で縞（バンディング）が出ます。ジッター（画素ごとに開始位置をずらす）を入れて縞をノイズに変え、時間蓄積とぼかしで消すのが基本です。さらに、ステップの間隔を、近くで細かく、遠くで粗くする（距離に対して二乗に増やす）と、同じステップ数で近くの品質が上がります。

## よくあるミス

??? failure "光の筋に縞（バンディング）が出る"
    **ジッタ**＋ **時間蓄積**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **視線に沿って、影を判定して足す**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [ボリュームを使う](volume.md)
