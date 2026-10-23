---
title: Shadow Map Raymarching
tags:
  - 描画
---

# Shadow Map Raymarching

<strong>視線に沿って進み各点で「太陽の光が届くか」をシャドウ マップで判定</strong>して、光の量を足し合わせるのが正確な方式です。太陽が画面外でも使えます。このページではシャドウ マップを使ったレイマーチを説明します。

!!! tip "ポイント"
    - 視線に沿ってシャドウ マップを参照。
    - 光が届く点だけ散乱を足す。
    - 太陽が画面外でも動く。
    - ステップ数が多いと重いので、ジッタ＋時間蓄積。

## シャドウ マップでレイマーチ
<strong>正確な方法</strong>は視線に沿ってサンプル点を歩き、各点が日向か日陰かをシャドウ マップで判定して、日向の点の寄与を足すことです。ボリューメトリック フォグ（[Volumetric Fog](../volumetric-fog/index.md)）と同じ原理です。

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
| ステップ数 | 16〜64 回。少ないとジッターのノイズが出る |
| ジッター | 開始位置をずらして縞を消す（ブルー ノイズ。時間蓄積で平均） |
| `phase` | 太陽の方を見ると光が強い（前方散乱） |
| 密度 | 一様な霧、または高さフォグ。ノイズで濃淡を付けると揺らぐ光の筋 |
| 範囲 | カメラ近くだけで十分（遠くは距離フォグ） |
| 半解像度で描く | ぼかし＋アップサンプリングで軽く |

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

この方式は単散乱の積分をステップで離散化したものです。視線上の位置 s における太陽光の寄与は、「その位置が日向か（シャドウ）」「その位置の霧の密度」「太陽と視線のなす角による散乱の強さ（位相関数）」の積です。これを視線に沿って足し合わせます（さらに厳密には、各サンプルからカメラまでの透過率も掛けますが、薄い霧では省略されることも多いです）。

<div class="formula">L = ∫ shadow(s) · density(s) · phase(θ) · T(s) ds　≈　Σ shadow_i · density_i · phase · Δs</div>

コードの `accumulated += shadow * height_density * phase * step_length` がこの和の 1 項です。`shadow` は 0 か 1（PCF を使えば 0〜1）の値で、シャドウ マップから得ます。

### シャドウ マップの参照

シャドウ マップの参照には通常の描画と同じカスケード シャドウ マップを使います。各サンプル点のワールド位置が、どのカスケードに入るかを調べ、そのカスケードの深度を引いて比べます（[Cascaded Shadow Maps (CSM)](../../shadows/cascaded.md)）。シャドウ マップの 1 テクセルの大きさは、画面のどの距離でも同じなので、遠くのサンプルではシャドウ マップの粗さがそのまま筋のにじみになります。近くのカスケードで見える範囲を、光の筋の最大距離として選ぶのが現実的です。

### ステップ数を減らす工夫

ステップが 16 回では筋の間隔がステップ幅に近い細い筋で縞（バンディング）が出ます。ジッター（画素ごとに開始位置をずらす）を入れて縞をノイズに変え、時間蓄積とぼかしで消すのが基本です。さらに、ステップの間隔を近くで細かく、遠くで粗くする（距離に対して二乗に増やす）と、同じステップ数で近くの品質が上がります。

## シャドウ マップで光の通り道を調べる

<strong>放射状ブラー</strong>（[Screen-Space Radial Blur](radial-blur.md)）は、画面の画像だけを使うので、影の正確さがありません。シャドウ マップを使うと視線に沿った各点が、太陽の光を受けているかが正確に、分かります。

## 考え方

<strong>カメラから各画素へ向かう視線</strong>を、細かく区切って、各点で 2 つのことを調べます。

| 調べること | 内容 |
| --- | --- |
| 光が届いているか | その点は、シャドウ マップで影の外か（太陽の光が、届く） |
| どれだけ散乱するか | 霧の密度 × 位相関数（太陽の方向への、前方散乱） |

光が届いている点の散乱光だけを、足し合わせると光の筋（光が通る、道筋）が現れます。

```text
視線 ●────●────●────●────●────●
カメラ   光   影   影   光   光       ← 各点で、影かどうかを、シャドウ マップで調べる
         ↑                          光の点だけ、散乱光を、足す
```

## 実装

```hlsl
// 視線に沿って、シャドウ マップを引きながら、散乱光を、積分する。
float3 GodRays(float3 camera, float3 world_pos, float2 screen_pos) {
  const int kSteps = 32;
  float3 ray = world_pos - camera;
  float ray_length = length(ray);
  float3 ray_dir = ray / ray_length;
  float step_len = ray_length / kSteps;
```

<strong>カメラからその画素の物体まで</strong>の視線を、32 区間に分けます。物体より奥は積分しません（物体で視線が、止まる）。

```hlsl
  // ステップの開始位置を、ノイズで、ずらす（縞を、細かいノイズに、変える）。
  float jitter = InterleavedGradientNoise(screen_pos);
  float3 sum = 0.0;
  float cos_theta = dot(ray_dir, g_sun_dir);
  float phase = HenyeyGreenstein(cos_theta, 0.7);               // 太陽の方向への、前方散乱
```

開始位置をノイズでずらす（ジッター）と、縞（バンディング）が細かいノイズに変わり、TAA でなめらかにならされます（[Cloud Temporal Reprojection](../clouds/temporal.md)）。位相関数は視線に沿って一定なので、ループの外で 1 回です。

```hlsl
  for (int i = 0; i < kSteps; ++i) {
    float3 p = camera + ray_dir * ((i + jitter) * step_len);
    float shadow = SampleShadowMap(p);                          // 1 = 光が届く、0 = 影
    sum += shadow;
  }
```

各点のワールド位置を シャドウ マップの座標へ、変換して影かどうかを調べます（[Comparison Samplers](../../shadows/shadow-map-basics/comparison-sampler.md)）。光が届く点（`shadow = 1`）だけが足されるので影に入った区間は、足されません。

```hlsl
  // 平均を取り、散乱の量（霧の密度 × 距離）と、位相関数、太陽の色を、掛ける。
  float scatter_amount = 1.0 - exp(-g_fog_density * ray_length);     // 霧の、全体の、厚み
  return (sum / kSteps) * scatter_amount * phase * g_sun_color;
}
```

光が届いた区間の割合（`sum / kSteps`）に、霧の厚みと位相関数、太陽の色を掛けます。光が多く届く（影が少ない）視線ほど、明るい筋になります。

## シャドウ マップの読み方

<strong>視線に沿った各点</strong>は 空間の、あらゆる場所にあるのでシャドウ マップ（カスケード）の、どの範囲に入るかを判定して適切な、カスケードを引きます（[CSM](../../shadows/cascaded.md)）。遠い点はカスケードの外になることがあり、影なし（光が届く）とみなします。

```hlsl
float SampleShadowMap(float3 world_pos) {
  // どのカスケードに入るかを調べ、そのカスケードの、シャドウ マップを、比較サンプラーで引く。
  int cascade = SelectCascade(world_pos);
  if (cascade < 0) return 1.0;                                   // 範囲の外 → 影なし
  float4 shadow_coord = mul(float4(world_pos, 1.0), g_cascade_matrix[cascade]);
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, float3(shadow_coord.xy, cascade), shadow_coord.z);
}
```

## 計算量と最適化

<strong>画面の全画素</strong>に対して 32 ステップの、ループを回すと非常に重いです（1080p で、約 6,600 万回のシャドウ マップ読み込み）。

| 最適化 | 内容 |
| --- | --- |
| 低解像度（半分、1/4）で計算 | 画素数が、1/4〜1/16。アップサンプル（深度を考慮した、バイラテラル）で元の解像度へ |
| ステップ数を減らす + ジッター + TAA | 16 ステップでも、ノイズ + 時間方向の平均で、なめらかに |
| 近い範囲のみ | カメラの、近くだけ（数十メートル）をレイマーチ。遠くは簡易な霧 |
| ボリューム テクスチャ（froxel）に、まとめる | 画素ごとにレイマーチする代わりに、3D グリッドに 1 回だけ計算（[Volumetric Fog](../volumetric-fog/index.md)） |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 影の形が正確に、光の筋に反映される（木漏れ日、窓の形） |
| 長所 | 太陽が画面の外でも、動く |
| 長所 | 霧の密度を場所で、変えられる（霧の濃淡が光に反映） |
| 短所 | 重い（画素 × ステップ） |
| 短所 | ノイズ（ステップが、少ないとき） |
| 短所 | シャドウ マップの、解像度に依存する（遠くは粗い） |

## よくあるミス

??? failure "光の筋に縞（バンディング）が出る"
    <strong>ジッタ</strong>＋ 時間蓄積を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 視線に沿って、影を判定して足す

## 参考

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014（Interleaved Gradient Noise）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Volume-Based God Rays](volume.md)
