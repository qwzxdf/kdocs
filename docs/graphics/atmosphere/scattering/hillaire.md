---
title: Hillaire 2020: Four LUTs
tags:
  - 描画
---

# Hillaire 2020: Four LUTs

<strong>Hillaire の手法は、4 つの小さな LUT（透過率・多重散乱・空の景色・空気遠近法）に分けて計算する</strong>ことで、動的な大気をリアルタイムで扱えます。パラメータを変えてもすぐに反映されます。このページでは 4 つの LUTを説明します。

!!! tip "ポイント"
    - 透過率 LUT：高さと角度から、透過率。
    - 多重散乱 LUT：多重散乱の近似。
    - スカイビュー LUT：視線の方向ごとの空の色。
    - 空気遠近法 LUT：カメラからの距離ごとの散乱。
    - 動的に更新できる（時刻・天候）。

!!! info "このページを読む前に"
    - [Atmospheric Scattering](index.md)（このセクション全体の地図と、読む順番）

## Hillaire 2020：4 つの LUT
<strong>Hillaire（2020, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"）</strong>は、軽い LUT を毎フレーム更新する方式です。大気の組成（霧の濃さ・時間帯）を動的に変えられるのが強みで、Unreal Engine の SkyAtmosphereなどに使われています。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="Hillaire の 4 つの LUT">
<text x="20" y="24" class="fig-title">Hillaire 2020：4 つの LUT</text>
<rect x="30" y="60" width="160" height="70" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/>
<text x="110" y="88" text-anchor="middle" style="font-size:13px">透過率 LUT</text><text x="110" y="108" text-anchor="middle" style="font-size:11px">256×64（2D）</text>
<rect x="210" y="60" width="160" height="70" rx="6" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/>
<text x="290" y="88" text-anchor="middle" style="font-size:13px">多重散乱 LUT</text><text x="290" y="108" text-anchor="middle" style="font-size:11px">32×32（2D）</text>
<rect x="390" y="60" width="160" height="70" rx="6" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="470" y="88" text-anchor="middle" style="font-size:13px">スカイビュー LUT</text><text x="470" y="108" text-anchor="middle" style="font-size:11px">192×108（2D）</text>
<rect x="570" y="60" width="180" height="70" rx="6" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d"/>
<text x="660" y="88" text-anchor="middle" style="font-size:13px">空気遠近法 LUT</text><text x="660" y="108" text-anchor="middle" style="font-size:11px">32×32×32（3D）</text>
<text x="110" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="110" y="176" text-anchor="middle" style="font-size:11px">太陽までの透過率</text>
<text x="290" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="290" y="176" text-anchor="middle" style="font-size:11px">多重散乱の寄与</text>
<text x="470" y="160" text-anchor="middle" style="font-size:11px">視線の向き →</text><text x="470" y="176" text-anchor="middle" style="font-size:11px">空の色（全天）</text>
<text x="660" y="160" text-anchor="middle" style="font-size:11px">カメラ前方の froxel →</text><text x="660" y="176" text-anchor="middle" style="font-size:11px">散乱光と透過率</text>
<text x="390" y="230" text-anchor="middle" style="font-size:13px">毎フレーム、順に更新：透過率 → 多重散乱 → スカイビュー → 空気遠近法</text>
</svg>

| LUT | 内容 |
| --- | --- |
| 透過率 LUT | (高さ, 太陽の天頂角) → 大気の外までの透過率（ほぼ固定。大気の組成が変わると更新） |
| 多重散乱 LUT | (高さ, 太陽の天頂角) → 多重散乱の寄与（近似） |
| スカイビュー LUT | カメラ位置での全方向の空の色（緯度経度で圧縮。地平線付近を細かく取る） |
| 空気遠近法 LUT | カメラ前方の froxel（視錐台の 3D 格子）ごとの散乱光と透過率。物体への霞に使う（[Aerial Perspective and Fog](../aerial-fog/index.md)） |

### スカイビュー LUT の工夫

空の色は地平線付近で急に変わります。天頂角をそのまま格子にすると、地平線の解像度が足りません。非線形な割り当てで地平線付近を細かく取ります。

```hlsl
float SkyViewV(float view_zenith_cos, float horizon_cos) {
  float v;
  if (view_zenith_cos > horizon_cos) {
    float t = (view_zenith_cos - horizon_cos) / (1.0 - horizon_cos);
    v = 0.5 + 0.5 * sqrt(t);
  } else {
    float t = (horizon_cos - view_zenith_cos) / (horizon_cos + 1.0);
    v = 0.5 - 0.5 * sqrt(t);
  }
  return v;
}
```

平方根で割り当てることで、地平線の周り（v = 0.5）が細かくなります。

### 実行時の流れ

| 手順 | 内容 |
| --- | --- |
| ① LUT 更新 | 透過率・多重散乱・スカイビュー・空気遠近法をコンピュートで更新 |
| ② 空を描く | ピクセルの視線から、スカイビュー LUT を引く（1 回の表引き） |
| ③ 太陽の円盤 | 透過率 LUT で減衰させて足す |
| ④ 物体にかける | 空気遠近法 LUT で、物体の色を霞ませる（[Aerial Perspective and Fog](../aerial-fog/index.md)） |


原典は Hillaire の "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（Eurographics Symposium on Rendering 2020）です。この方式の特長は Bruneton の 4D テーブルを毎フレーム更新できる小さな LUT に分解したことです。LUT が小さいので大気の組成（ミーの密度、オゾンの量）をリアルタイムに変えて、天候の変化も表現できます。モバイルから高性能 PC まで、LUT の解像度を変えるだけで対応でき、Unreal Engine の Sky Atmosphere などに採用されています。

原典は Hillaire の "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（Eurographics Symposium on Rendering 2020）です。この方式の特長は Bruneton の 4D テーブルを毎フレーム更新できる小さな LUT に分解したことです。LUT が小さいので大気の組成（ミーの密度、オゾンの量）をリアルタイムに変えて、天候の変化も表現できます。モバイルから高性能 PC まで、LUT の解像度を変えるだけで対応でき、Unreal Engine の Sky Atmosphere などに採用されています。

LUT は小さいので毎フレーム更新しても軽く（0.1〜0.3 ms 程度）、時刻・天気・大気の濃さを動的に変えられます。

## 4 つの LUT の役割分担

Hillaire（2020）の方式は <strong>空の計算を 4 つの小さな LUT に分けて</strong>、毎フレーム、更新します。すべてがリアルタイムで動くので、時間帯の変化、天候の変化に即座に追従できます。

| LUT | 大きさ | 軸 | 内容 | 更新 |
| --- | --- | --- | --- | --- |
| 透過率 LUT | 256×64 | 高度、天頂角 | 大気の上端までの、透過率 | 大気の係数が変わったときのみ |
| 多重散乱 LUT | 32×32 | 高度、太陽の天頂角 | 多重散乱の、光（等方） | 大気の係数、または太陽の位置が変わったとき |
| Sky-View LUT | 192×108 | 緯度・経度（空の、方向） | カメラの位置から見た、空の色（全方向） | 毎フレーム |
| Aerial Perspective LUT | 32×32×32 | 画面 xy、距離 | カメラ前方の各点までの、散乱光と透過率 | 毎フレーム |

重い計算を小さな LUT に、集約し 画面の全画素では、LUT を読むだけにするという、設計です。

```text
 [透過率 LUT] ─┬─→ [多重散乱 LUT] ─┬─→ [Sky-View LUT] ───→ 空の、各画素は、LUT を引くだけ
              │                    └─→ [Aerial Perspective LUT] ──→ 物体の、各画素は、LUT を引くだけ
              └─ 太陽の透過率に、使う（Sky-View、Aerial Perspective でも）
```

## 1：透過率 LUT

<strong>高度と天頂角</strong>から 大気の上端までの、透過率を事前に計算します（詳細は、[Transmittance](transmittance.md)）。太陽の光が各点に届く割合を 1 回の、テクスチャ読み込みで得るための、基礎です。

更新の頻度は 低く（大気の係数が変わらない限り 1 回で済む）。

## 2：多重散乱 LUT

<strong>高度と太陽の天頂角</strong>から 多重散乱の、光の量を事前に計算します（詳細は、[Multiple Scattering](multiple-scattering.md)）。32×32 の小さな LUT で、透過率 LUT を使って各点で、64 方向を積分します。

## 3：Sky-View LUT

<strong>カメラの位置</strong>から見た 空の、全方向の色を 1 枚の小さな画像に描きます。空はゆるやかに変化するので 192×108 という、小さな解像度で十分です。

### 空の方向を画像に割り当てる

方向（視線の向き）を 画像の、座標に割り当てます。地平線の近くは色が急に変わるので、非線形な割り当てで地平線の近くを細かく取ります。

```hlsl
// Sky-View LUT の uv から、視線の方向（緯度 = 地平線からの角度、経度 = 太陽との、方位角の差）を求める。
void UvToSkyViewParams(float2 uv, float view_height, out float view_zenith_cos, out float light_view_cos) {
  // 地平線までの、角度。地平線の、すぐ上と、すぐ下を細かく取る。
  float v_horizon = sqrt(view_height * view_height - g_bottom_radius * g_bottom_radius) / view_height;
  float beta = asin(g_bottom_radius / view_height);                    // 地平線の、俯角
  float zenith_horizon_angle = 3.14159265 - beta;                      // 天頂角の、地平線の値
```

まず、カメラの高度から 地平線の、天頂角（地平線がどこに見えるか）を求めます。カメラが高いほど地平線は下がり（天頂角が大きく）ます。

```hlsl
  float coord;
  if (uv.y < 0.5) {
    // 上半分: 地平線より、上（空）。地平線に近いほど、細かい（二乗で、詰める）
    coord = 1.0 - 2.0 * uv.y;
    coord *= coord;
    view_zenith_cos = cos(zenith_horizon_angle * (1.0 - coord) ...);
  } else {
    // 下半分: 地平線より、下（地面の方向）。同様に地平線の近くを細かく
    coord = uv.y * 2.0 - 1.0;
    coord *= coord;
    // ...
  }
```

画像の上下で 地平線の上と下を分け、それぞれ地平線に向かって `coord²` で、サンプルを詰めます。地平線の近くは色の変化が急（空と地面、霞）なのでここに解像度を集めるのが、肝心です。

```hlsl
  // 横方向は、太陽との方位角の差（0 〜 π）。二乗で、詰める。
  float light_view_angle_cos = ...;      // 太陽と、視線の、水平方向での、角度の cos
  light_view_cos = light_view_angle_cos;
}
```

横軸は 太陽との方位角の差にします。太陽のすぐ近く（ミー散乱が強い、明るい輪）を細かく取るためです。

```hlsl
// Sky-View LUT を描く: 各画素について、視線の方向に 1 回散乱 + 多重散乱を積分する。
float4 SkyViewPS(float2 uv : TEXCOORD0) : SV_Target {
  float view_height = length(g_camera_position_from_planet_center);
  float view_zenith_cos, light_view_cos;
  UvToSkyViewParams(uv, view_height, view_zenith_cos, light_view_cos);

  float3 ray_dir = ...;                         // 求めた角度から、視線の向きを復元
  float3 sun_dir = ...;
  float3 L = IntegrateScatteredLuminance(float3(0, view_height, 0), ray_dir, sun_dir, /*steps*/ 30);
  return float4(L, 1.0);
}
```

積分は 1 回散乱のループ（[Single-Scattering Integral](single-scattering.md)）に多重散乱 LUT（[Multiple Scattering](multiple-scattering.md)）を足した、ものです。LUT の画素数が少ない（192×108 = 約 2 万）ので積分の、ステップ数を多く（30〜）しても、軽いです。

### 空を描く

画面の各画素は 視線の方向から、LUT の uv を求めて 1 回読むだけです。

```hlsl
float3 SampleSkyView(float3 view_dir) {
  float2 uv = SkyViewDirToUv(view_dir);       // 先ほどの、割り当ての、逆変換
  return g_sky_view_lut.SampleLevel(g_linear_clamp, uv, 0).rgb;
}
```

画面全体の空がテクスチャ 1 回の読み込みになるので、安いです。

## 4：Aerial Perspective LUT

<strong>空気遠近法</strong>（遠くの物が霞んで、青みを帯びる）を 物体に適用するための LUT です。カメラの前方の空間を 32×32×32 の、3D テクスチャに分割し（froxel と、同じ発想）、各セルにカメラからそのセルまでの、散乱光と透過率を保存します。

| 軸 | 内容 |
| --- | --- |
| x、y | 画面上の位置（カメラから見た、方向） |
| z | カメラからの距離（0 〜 32 km、非線形に分割、近くを細かく） |
| RGB | カメラからそのセルまでの、散乱光（空気が足す色） |
| A | 透過率（カメラから、そのセルまでの平均的な透過率） |

```hlsl
// Aerial Perspective LUT を 1 スライス（距離）ずつ、描く。各スライスは、カメラから、その距離までを積分する。
float4 AerialPerspectivePS(float2 uv, uint slice) {
  float distance_m = SliceToDistance(slice);                         // スライス → 距離（近くを細かく）
  float3 ray_dir = ScreenToViewDir(uv);
  float3 scattered; float3 transmittance;
  IntegrateScatteredLuminance(g_camera_position, ray_dir, g_sun_dir, distance_m, scattered, transmittance);
  float mean_t = dot(transmittance, float3(1, 1, 1)) / 3.0;           // 透過率の RGB の、平均
  return float4(scattered, 1.0 - mean_t);
}
```

### 物体に適用する

物体を描くとき その画素の深度から、カメラまでの距離を求め LUT の、対応するセルを読んで散乱光を足し、透過率を掛けます。

```hlsl
// 物体の色に空気遠近法を適用する（ピクセル シェーダーの、最後）。
float3 ApplyAerialPerspective(float3 scene_color, float2 screen_uv, float distance_m) {
  float slice = DistanceToSlice(distance_m);                          // 距離 → スライス（連続値）
  float4 ap = g_aerial_perspective_lut.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
  float3 inscatter = ap.rgb;                                          // 空気が足す光
  float transmittance = 1.0 - ap.a;                                   // 物体の光が届く割合
  return scene_color * transmittance + inscatter;
}
```

この 1 行で どんな物体にも、空気遠近法がかかります。物体ごとに大気の積分を行う必要がありません。距離に応じた霞と青みが物理的な、正しい値で自然に付きます。

## 全体の更新の流れ

```text
起動時 / 大気の係数が、変わったとき:
  ① 透過率 LUT を、計算
  ② 多重散乱 LUT を、計算（①を使う）

毎フレーム:
  ③ Sky-View LUT を、計算（①②を使う）
  ④ Aerial Perspective LUT を、計算（①②を使う）
  ⑤ 空を描く（③を引く）
  ⑥ 各物体の、描画で、空気遠近法を、適用（④を引く）
```

| LUT | コスト（目安） |
| --- | --- |
| 透過率 | 起動時のみ（0.1 ms 未満） |
| 多重散乱 | 太陽が動くたび（0.05 ms 程度） |
| Sky-View | 毎フレーム 0.05〜0.1 ms |
| Aerial Perspective | 毎フレーム 0.1〜0.2 ms |

<strong>合計で毎フレーム、0.3 ms 未満</strong>と 軽く、時間帯の変化にもリアルタイムに追従できます。

## DirectX 11 で組む

4 つの LUT はすべて計算シェーダーで書く、小さなテクスチャです。

### LUT のテクスチャ

```cpp
auto MakeLut = [&](UINT w, UINT h, UINT d, DXGI_FORMAT fmt, Microsoft::WRL::ComPtr<ID3D11ShaderResourceView>& srv,
                   Microsoft::WRL::ComPtr<ID3D11UnorderedAccessView>& uav) {
  Microsoft::WRL::ComPtr<ID3D11Resource> res;
  if (d == 1) {
    D3D11_TEXTURE2D_DESC desc = {w, h, 1, 1, fmt, {1, 0}, D3D11_USAGE_DEFAULT,
                                 D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS, 0, 0};
    Microsoft::WRL::ComPtr<ID3D11Texture2D> t;
    device->CreateTexture2D(&desc, nullptr, &t);
    t.As(&res);
  } else {
    D3D11_TEXTURE3D_DESC desc = {w, h, d, 1, fmt, D3D11_USAGE_DEFAULT,
                                 D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS, 0, 0};
    Microsoft::WRL::ComPtr<ID3D11Texture3D> t;
    device->CreateTexture3D(&desc, nullptr, &t);
    t.As(&res);
  }
  device->CreateShaderResourceView(res.Get(), nullptr, &srv);
  device->CreateUnorderedAccessView(res.Get(), nullptr, &uav);
};
MakeLut(256, 64, 1, DXGI_FORMAT_R16G16B16A16_FLOAT, transmittance_srv, transmittance_uav);      // 透過率
MakeLut(32, 32, 1, DXGI_FORMAT_R16G16B16A16_FLOAT, multiscatter_srv, multiscatter_uav);         // 多重散乱
MakeLut(192, 108, 1, DXGI_FORMAT_R11G11B10_FLOAT, skyview_srv, skyview_uav);                    // Sky-View
MakeLut(32, 32, 32, DXGI_FORMAT_R16G16B16A16_FLOAT, aerial_srv, aerial_uav);                    // Aerial Perspective（3D）
```

4 つともサイズが小さいので、毎フレーム、書き直しても軽く済みます。Aerial Perspective だけが、3D テクスチャ（画面の 32×32 に、奥行き 32 段）です。

### 更新の順序

```cpp
// 透過率と多重散乱は、大気のパラメータが変わったときだけ（普通は、起動時の 1 回）。
if (atmosphere_changed) {
  Dispatch(transmittance_cs, {}, {transmittance_uav}, 256 / 8, 64 / 8, 1);
  Dispatch(multiscatter_cs, {transmittance_srv}, {multiscatter_uav}, 32, 32, 1);     // 1 グループ = 1 テクセル（内部で、並列に積分）
}
// Sky-View と Aerial Perspective は、毎フレーム（太陽の向きや、カメラの高さが、変わるため）。
Dispatch(skyview_cs, {transmittance_srv, multiscatter_srv}, {skyview_uav}, 192 / 8, 108 / 8, 1);
Dispatch(aerial_cs, {transmittance_srv, multiscatter_srv}, {aerial_uav}, 32 / 8, 32 / 8, 32);
```

`Dispatch(...)` は仮の関数で「入力 SRV を束ね、出力 UAV を束ね `Dispatch` を呼び、終わったら束縛を外す」をまとめたものです（[D3D11 Pass Recipes](../../../directx/dx11/pass-recipes.md)）。後のパスが前の LUT を読むので、各 `Dispatch` のあとで UAV を `nullptr` で、外します。毎フレーム更新するのは 2 枚だけなので、大気の計算が軽くなります。

## 宇宙から地上まで

この方式は <strong>カメラが地上でも、空の高いところでも宇宙でも</strong>、同じ仕組みで、動きます。カメラの高度が LUT の入力になっているためです（Sky-View LUT の、地平線の計算が高度から決まる）。宇宙から惑星を見るとき（大気の、青い縁）には Sky-View LUT は使わず、画面全体を直接、積分する専用のパスを使います（[Ground and Space Views](ground-space.md)）。

## よくあるミス

??? failure "LUT の解像度が低く、空にバンディング"
    <strong>解像度を上げる</strong>・非線形のマッピングを使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 4 つの小さな LUT で、動的な大気

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Multiple Scattering](multiple-scattering.md)
- [Aerial Perspective and Fog](../aerial-fog/index.md)
