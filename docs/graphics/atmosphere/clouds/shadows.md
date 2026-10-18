---
title: Cloud Shadows
tags:
  - 描画
---

# Cloud Shadows

<strong>雲は、地上に影を落とします</strong>。<strong>雲の密度を、太陽方向に積分した「影マップ」</strong>を作り、地面の明るさに反映します。このページでは、雲の影を説明します。

!!! tip "ポイント"
    - 雲の透過率を、太陽方向のマップに記録。
    - 地面のシェーディングで、そのマップを参照。
    - 雲が動くと、影も動く。
    - 低解像度で十分。

## 影
<strong>雲は地面や他の雲に影を落とします</strong>。

| 影の種類 | 内容 |
| --- | --- |
| <strong>雲の影（地面へ）</strong> | 地面の位置から太陽方向へ雲を積分して、日が差す量を減らす。または雲の影用のマップ（光方向の透過率）を事前に作る |
| 雲の自己影 | <strong>光のマーチ（上記）</strong> |
| 山の影が雲に | シャドウ マップを雲のサンプルで引く |
| 光の筋 | 雲の隙間から差す光（[God Rays](../god-rays/index.md)） |

### 雲の影マップの作り方

雲の影マップは、太陽方向から見た、雲の透過率の 2D テクスチャです。次の手順で作ります。

太陽の方向を軸にした正射影で、カメラの周囲の地面を覆う範囲を決めます。範囲内の各テクセルについて、そのテクセルから太陽に向かって雲の層を貫く線を引き、雲の層の入口から出口まで密度を積分して、光学的厚さを求めます。その透過率 `exp(−光学的厚さ)` を、テクスチャに保存します。

地面のシェーディングでは、ピクセルのワールド位置を同じ正射影で変換し、このテクスチャを引いて、太陽光に掛けます。雲の影の動きはゆっくりで、形も柔らかいので、解像度は 512×512 程度の低解像度で十分です。更新も、毎フレームでなく、数フレームに 1 回、もしくは雲の更新と一緒に少しずつ行えば、コストが小さく済みます。

この透過率は、通常のシャドウ マップ（地面の物体が落とす影）と<strong>掛け合わせて</strong>使います。それぞれ独立した遮蔽なので、確率の積と同じです。また、ボリューメトリック フォグ（[Volumetric Fog](../volumetric-fog/index.md)）の光の注入にも、同じ透過率を使うと、雲の影の下で霧が暗くなり、雲の隙間から差す光の筋が出る、つながった画面になります。

## 雲の、影

<strong>雲は、光を、遮る</strong>ので、<strong>地面に、雲の影</strong>が、落ちます。雲の影が、地面を、ゆっくり、流れていく様子は、風景に、生命感と、スケール感を、与えます。雲の、影を、地面に、落とすには、地面の各点が、太陽の方向に、雲を、どれだけ、通るかを、知る必要が、あります。

## 方法 1：雲の、影マップ

<strong>太陽の方向から</strong>、<strong>雲の殻</strong>を、見下ろして、各位置での、雲の、光学的な厚さ（密度の積分）を、テクスチャ（雲の影マップ）に、描きます。地面の、各点は、このマップを、引くだけで、雲の影の、濃さが、分かります。

```text
        太陽
         ↓ ↓ ↓          ← 太陽の方向に、投影した、正射影
     ░░▓▓▓░░░▓▓░░       ← 雲の層（上から見た、厚さ）
   ──────────────────── 地面
   ↓ ↓ ↓ ↓              ← 影マップを、地面の各点で、引く
```

### 影マップを、描く

```hlsl
// 計算シェーダー: 影マップの各画素について、太陽の方向に、雲の殻を、通る、光学的な厚さを求める。
[numthreads(8, 8, 1)]
void CloudShadowMapCS(uint3 id : SV_DispatchThreadID) {
  // 画素に対応する、地面（または、雲の底の下）の、位置を、太陽の向きに、垂直な平面上の、座標から、求める。
  float3 plane_pos = ShadowMapToWorld(id.xy);                       // 影マップの画素 → ワールド位置（太陽に、垂直な平面）
  // この位置から、太陽へ向かって、雲の殻を、通過する区間を、求める。
  float2 range = CloudLayerIntersect(plane_pos, g_sun_dir);
  float optical_depth = 0.0;
  const int kSteps = 16;
  float step_len = (range.y - range.x) / kSteps;
  for (int i = 0; i < kSteps; ++i) {
    float3 p = plane_pos + g_sun_dir * (range.x + (i + 0.5) * step_len);
    optical_depth += CloudDensityCheap(p) * g_extinction * step_len;   // 安い密度（細部は、不要）
  }
  g_cloud_shadow_map[id.xy] = exp(-optical_depth);                     // 透過率（1 = 影なし、0 = 完全な影）
}
```

<strong>太陽の方向</strong>に、<strong>雲の殻を、貫く、光線</strong>を、画素ごとに、飛ばし、密度を積分して、透過率（光が、地面まで、届く割合）を、書き込みます。安い密度（基本の形だけ）で、十分です（影は、ぼんやりしている）。解像度は、256×256 〜 1024×1024 で、広い範囲を、覆います。雲は、ゆっくり、動くので、数フレームに、1 回、更新すれば、十分です。

### 地面で、引く

```hlsl
// 地面（または、物体）の、ライティングで、雲の影を、太陽の光に、掛ける。
float CloudShadow(float3 world_pos) {
  // ワールド位置を、影マップの座標へ（太陽の向きに、垂直な平面に、投影）。
  float2 uv = WorldToCloudShadowUv(world_pos);
  return g_cloud_shadow_map.SampleLevel(g_linear_clamp, uv, 0);
}
float3 sun = g_sun_color * CloudShadow(world_pos) * ShadowMapShadow(world_pos);   // 雲の影 × 通常のシャドウ マップ
```

<strong>太陽の直接光</strong>に、<strong>雲の影の透過率</strong>を、掛けます。通常の、シャドウ マップ（[Shadows](../../shadows/index.md)）と、掛け合わせて、使います。雲の下では、太陽の光が、弱まり、地面が、暗くなります。

## 方法 2：天気マップを、直接、引く

<strong>雲の影の、簡易な、近似</strong>です。<strong>雲は、薄い層</strong>なので、天気マップ（[Cloud Density Model](density-model.md)）の、カバレッジを、そのまま、影の濃さに、使います。

```hlsl
// 天気マップの、カバレッジを、太陽の方向に、ずらして、影として使う。
float2 shadow_uv = (world_pos.xz + g_sun_dir.xz * (g_cloud_height / max(g_sun_dir.y, 0.1))) * g_weather_scale;
float coverage = g_weather_map.SampleLevel(g_linear_wrap, shadow_uv, 0).r;
float shadow = 1.0 - coverage * g_cloud_shadow_strength;
```

<strong>雲の、高さだけ</strong>、<strong>太陽の方向に、位置を、ずらして</strong>、天気マップを、読む（雲の層が、地面の、上空にあるため、影は、太陽と、反対の、向きに、ずれる）。計算は、1 回の、テクスチャ読み込みで、非常に、軽いです。雲の、厚みの、細かい、濃淡は、出ません。

| 方式 | 精度 | コスト |
| --- | --- | --- |
| 影マップ（雲の殻を、積分） | 高（雲の、実際の、密度を、反映） | 中（数フレームに、1 回の、更新） |
| 天気マップを、引く | 低（カバレッジだけ） | 最小 |

## 雲の影を、ボリュームにも

<strong>霧や、大気</strong>（[Volumetric Fog](../volumetric-fog/index.md)）の、<strong>ライティング</strong>でも、雲の影を、使います。光の筋（[God Rays](../god-rays/index.md)）が、雲の隙間から、差し込む様子が、出ます。

```hlsl
// ボリューム フォグの、太陽の光の注入で、雲の影も、掛ける。
float3 sun_in_cell = g_sun_color * shadow_map_visibility * CloudShadow(cell_world_pos);
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 雲の、動き | 雲が、風で、動くと、影マップも、変わる。更新を、間引くと、影が、カクカクする。前の、影マップと、補間 |
| 太陽の、角度が、浅い（朝夕） | 影が、非常に、長く伸びる。影マップの、範囲が、足りなくなる。範囲を、広げる、カスケード化 |
| 影の、濃さ | 雲の影は、柔らかく、薄い。濃すぎると、不自然（暗すぎる）。透過率の、下限を、設ける（0.3 など） |
| ボリュームと、地面の、整合 | 雲の影を、地面にも、霧にも、同じ影マップで、適用して、ずれが、ないように |

## よくあるミス

??? failure "雲の影が地上に落ちない"
    <strong>雲の影マップ</strong>を作り、<strong>地面で参照</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 雲の透過率を、影マップにして使う

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Cascaded Shadow Maps (CSM)](../../shadows/cascaded.md)
