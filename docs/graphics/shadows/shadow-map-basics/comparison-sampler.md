---
title: Comparison Samplers
tags:
  - 描画
---

# Comparison Samplers

シャドウ マップが描けても影はまだ見えません。画面の点が影の中かどうかはその点の「光から見た深度」とマップに保存された「光から最も近い物の深度」を比べて、初めて決まります。この比較を自分でテクスチャを 4 回読んで書くこともできますが、GPU には比較専用のサンプラー（比較サンプラー）があります。比較サンプラーは比較の結果を補間してくれるので、影の縁が少しなめらかになります。ところが「比較してから補間する」という順番を取り違えると、影が階段状になったり縁の位置がずれたりします。このページでは光の空間への変換、比較サンプラーの設定と順番の意味、3×3 の PCF を 9 回と `GatherCmp` 4 回で書く方法、カスケード配列、reversed-Z を HLSL と C++ の再現で説明します。

!!! tip "ポイント"
    - 画面の点を光のクリップ空間に変換し、NDC の `z` から少し引いた値をマップの深度と比べる。参照値がマップの値以下なら光が当たる（標準の Z、`LESS_EQUAL`）。
    - 比較サンプラー（`SampleCmpLevelZero`）は 4 テクセルを比較してから補間する。補間してから比較すると縁の位置が半テクセル以上ずれて、階段状になる。
    - 3×3 の PCF は `SampleCmp` 9 回でも `GatherCmp` 4 回と重み `[1−f, 1, 1, f] / 3` でも書ける。C++ の再現で両者の差は 1.2 × 10⁻⁷ だった。
    - 範囲外は光が当たる扱いにする。境界色は 1.0（最も遠い）。ただし、光の far を超えた点と near の手前も別に除く。
    - reversed-Z では、比較関数を `GREATER_EQUAL` にしてバイアスの向きも逆にする。

!!! info "このページを読む前に"
    - [Shadow Map Basics](index.md)（このセクション全体の地図と読む順番）
    - [MVP 変換](../../../3d/transforms-mvp.md)（ワールド・ビュー・射影の流れ）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文を読んで書いたものではありません。Reeves、Salesin、Cook の "Rendering Antialiased Shadows with Depth Maps"（1987、PCF の原典）と Microsoft の Direct3D 11 のドキュメント（`D3D11_SAMPLER_DESC`、`SampleCmp`、`GatherCmp`）は今回の執筆では読んでいません。`SampleCmp` と `GatherCmp` の動作（比較してから双線形補間、`GatherCmp` が 2×2 の比較結果を返す順序）は、このページが C++ で再現したものです。実機での動作は確認していません。

HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめました。C++ は MSVC で実行しました。バイアスなどの数値は説明のための値です。

## 光の空間への変換 {#transform}

ワールド座標の点を光のクリップ空間に変換します。

```hlsl
// シャドウ マップの比較: 光の空間への変換、比較サンプラー、3x3 の PCF（9 回 / GatherCmp 4 回）、カスケード配列、reversed-Z。
// 座標は左手系・Y-up、行ベクトル（v * M）。シャドウ マップは単一チャンネルの深度（D32_FLOAT など）、SRV は R32_FLOAT。
// 「足した」と書いた式や値はこのページが説明のために決めたもの。

Texture2D<float> g_shadow_map : register(t0);                // 単一のシャドウ マップ
Texture2DArray<float> g_shadow_array : register(t1);         // カスケード（スライスごと）
SamplerComparisonState g_shadow_cmp : register(s0);          // 比較サンプラー（LESS_EQUAL、線形、BORDER = 1.0）

cbuffer ShadowCB : register(b0) {
  float4x4 g_light_view_proj;     // ワールド → 光のクリップ空間（行ベクトル用）
  float2 g_map_size;              // シャドウ マップの幅・高さ（画素数）
  float2 g_texel_size;            // 1 / g_map_size
  float g_bias;                   // 深度バイアス（NDC の z 単位。足した値の例: 0.0005）
  float3 g_pad;
};

// ================= ① 光の空間への変換 =================

struct ShadowCoord {
  float2 uv;      // シャドウ マップの UV（0〜1、v は下向き）
  float depth;    // 比較する深度（バイアス込み）
  bool inside;    // マップの範囲内か
};

ShadowCoord ToShadowCoord(float3 world_pos) {
  ShadowCoord s;
  float4 clip = mul(float4(world_pos, 1.0), g_light_view_proj);
  float3 ndc = clip.xyz / clip.w;                              // 平行光源では w = 1。点光源・スポットでは必要
  s.uv = ndc.xy * float2(0.5, -0.5) + 0.5;                     // NDC の y は上向き、テクスチャの v は下向き
  s.depth = ndc.z - g_bias;                                    // 標準 Z（near = 0、far = 1）。奥にずらして自己影を防ぐ
  s.inside = all(s.uv >= 0.0) && all(s.uv <= 1.0) && ndc.z <= 1.0 && ndc.z >= 0.0;   // z の範囲外は far の外・near の手前
  return s;
}
```

`ToShadowCoord` は点を光の `ViewProjection` で変換し、`w` で割って NDC にします。平行光源（正射影）では `w` は 1 ですが、スポットライトや点光源（透視投影）では、割る必要があります。`uv` は `ndc.xy * (0.5, −0.5) + 0.5` です。NDC の y は上向きテクスチャの v は下向きなので、y だけ符号を反転します。これを忘れると影が上下に反転します。

`depth` は `ndc.z − g_bias` です。比較する深度を少しだけ奥にずらして、面が自分自身にできる影（自己影）を防ぎます。バイアスの大きさは NDC の `z` の単位です。このページの例の 0.0005 は深度範囲 100 m の正射影なら約 5 cm です。バイアスの詳しい決め方は [Shadow Bias](../bias/index.md) を見てください。

`inside` は `uv` が 0〜1 の範囲か `z` が 0〜1 の範囲かを調べます。`z` の範囲外も除く必要があります。光の far を超えた点がマップの奥の値と比べられて、影になってしまうのを防ぐためです。

## 比較サンプラー {#sampler}

比較サンプラーはサンプリングのときに「保存された深度」と「参照値」を比べる機能です。

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;   // 比較 + 線形補間（2×2）
desc.AddressU = desc.AddressV = desc.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;   // 範囲外は境界色
desc.BorderColor[0] = desc.BorderColor[1] = desc.BorderColor[2] = desc.BorderColor[3] = 1.0f;   // 範囲外の深度 = 1.0（最も遠い）→ 光が当たる
desc.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;                // 参照値 <= 保存値 → 1（光が当たる）
desc.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&desc, &shadow_sampler);
```

`Filter` は `COMPARISON_` で始まるものを選びます。`MIN_MAG_LINEAR_MIP_POINT` なら 4 テクセルの比較結果を双線形で補間します。`MIN_MAG_MIP_POINT` を選ぶと補間がなく 1 テクセルの比較結果（0 か 1）だけが返ります。`AddressU/V/W` を `BORDER` にして `BorderColor` を 1.0 にすると、範囲外は最も遠い深度の扱いになり光が当たります。`ComparisonFunc = LESS_EQUAL` は標準の Z（near が 0、far が 1）の設定です。reversed-Z（near が 1、far が 0）では `GREATER_EQUAL` にします。

HLSL では `SamplerComparisonState` 型で受け `SampleCmp` か `SampleCmpLevelZero` で読みます。

```hlsl

// ================= ② 比較サンプラー（ハードウェアの 2x2 PCF）=================

// 戻り値は 0（影）〜 1（光）。比較してから 2x2 を双線形に補間する。
float ShadowHw2x2(float3 world_pos) {
  ShadowCoord s = ToShadowCoord(world_pos);
  if (!s.inside) return 1.0;                                   // 範囲外は光が当たる扱い（BORDER = 1.0 でも同じだが、z の外は別に必要）
  return g_shadow_map.SampleCmpLevelZero(g_shadow_cmp, s.uv, s.depth);
}
```

`SampleCmp` は画面の微分でミップを選ぶので、分岐の中では使えません。`SampleCmpLevelZero` はミップ 0 を使うので、分岐の中でも使えます。シャドウ マップはミップを持たない（深度の平均には意味がない）ので、こちらが標準です。

### 比較してから補間する {#order}

比較サンプラーの動作は次の順番です。

1. 参照値 `ref` の座標の周りの 4 テクセルを取る。
2. 各テクセルについて `ref <= 保存値` を調べ 1 か 0 にする。
3. この 4 つの結果を座標の小数位置で、双線形に補間する。

C++ で再現して補間してから比較する順番と並べました。左の 2 テクセルが遮蔽物（深度 0.3）、右の 2 テクセルが背景（0.9）で、受け手の深度が 0.6 のときテクセル中心の間を歩いた結果です。

<svg class="fig flow" viewBox="0 0 640 250" role="img" aria-label="段の縁を歩いたときの、光の割合"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">段の縁を歩いたときの、光の割合</text><line x1="60" y1="200" x2="600" y2="200" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="200" stroke="#94a3b8"/><line x1="60" y1="192.7" x2="600" y2="192.7" stroke="#94a3b8" stroke-dasharray="4 3"/><text x="54" y="196.72727272727272" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="124.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="51.27272727272728" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="60.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="195.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">0.25</text><text x="330.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">0.5</text><text x="465.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">0.75</text><text x="600.0" y="216" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="330.0" y="234" text-anchor="middle" font-size="11" fill="currentColor">テクセル中心の間の位置 t</text><polyline points="60.0,192.7 127.5,174.5 195.0,156.4 262.5,138.2 330.0,120.0 397.5,101.8 465.0,83.6 532.5,65.5 600.0,47.3" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">比較してから補間</text><polyline points="60.0,192.7 127.5,192.7 195.0,192.7 262.5,192.7 330.0,47.3 397.5,47.3 465.0,47.3 532.5,47.3 600.0,47.3" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">補間してから比較</text></svg>

比較してから補間する場合は 0 から 1 まで直線的に変わります。補間してから比較する場合は中間の深度（0.3 と 0.9 の混ぜ物）を先に作ってしまうため、位置 0.5 で突然 0 から 1 に変わる階段になります。存在しない中間の深度と比べているので、縁の位置が実際の位置からずれる原因にもなります。**だから、比較サンプラーを使い手動で比較する場合も補間の前に比較する**ことが必要です。

### 手動の比較 {#manual}

比較サンプラーが使えない場合（VSM や ESM のように深度そのものを使う場合）は、通常のサンプラーで深度を読んで、手で比較します。

```hlsl
// ================= ⑥ 手動の比較（比較サンプラーなし）=================

SamplerState g_point_clamp : register(s1);

// 補間なし。比較サンプラーが使えない場合（深度を VSM に使うなど）の例。縁は階段状になる。
float ShadowManual(float3 world_pos) {
  ShadowCoord s = ToShadowCoord(world_pos);
  if (!s.inside) return 1.0;
  float stored = g_shadow_map.SampleLevel(g_point_clamp, s.uv, 0);
  return s.depth <= stored ? 1.0 : 0.0;
}
```

点サンプリングで読むので補間がなく、縁は階段状になります。なめらかにしたいなら自分で 4 点を比較して補間します。[VSM, ESM and MSM](../vsm/index.md) で扱う方式は、比較ではなく統計を使います。

## 3×3 の PCF {#pcf}

2×2 の補間だけでは縁のなめらかさは 1 テクセル分です。もっと広くぼかすには複数回サンプリングして平均します。この方法を PCF（Percentage Closer Filtering）と呼びます。

### SampleCmp を 9 回 {#nine}

1 テクセルずつずらした位置で `SampleCmp` を 9 回呼んで、平均します。

```hlsl
// ================= ③ 3x3 の PCF（9 回）=================

// 1 テクセルずつずらした 9 点の SampleCmp を平均する。各 SampleCmp が 2x2 なので、見る範囲は 4x4 テクセル。
float ShadowPcf3x3_Nine(float3 world_pos) {
  ShadowCoord s = ToShadowCoord(world_pos);
  if (!s.inside) return 1.0;
  float sum = 0;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      sum += g_shadow_map.SampleCmpLevelZero(g_shadow_cmp, s.uv + float2(x, y) * g_texel_size, s.depth);
    }
  }
  return sum / 9.0;
}
```

各 `SampleCmp` が 2×2 の範囲を見るので、全体の範囲は 4×4 テクセルになります。このページの C++ の計算（正射影の幅 50 m、マップ 2048）では 1 テクセルが 2.44 cm なので、2×2 の範囲が 4.9 cm、4×4 の範囲が 9.8 cm です。

### GatherCmp を 4 回 {#gather}

`GatherCmp` は 2×2 の比較結果を補間せずに 4 つ返します。4 回呼べば 4×4 の比較結果が取れて、重みを自分で掛けられます。

```hlsl
// ================= ④ 3x3 の PCF（GatherCmp 4 回）=================

// GatherCmp は 2x2 の比較結果を 4 つ返す（補間はしない）。これを 4 回使って 4x4 テクセルの比較結果を取り
// 3x3 の箱型 × 双線形 と同じ重みを手で掛ける。重みは軸ごとに [1-f, 1, 1, f] / 3（f = テクセル内の小数位置）。
float ShadowPcf3x3_Gather(float3 world_pos) {
  ShadowCoord s = ToShadowCoord(world_pos);
  if (!s.inside) return 1.0;
  float2 t = s.uv * g_map_size - 0.5;                          // テクセル中心を整数にした座標
  float2 base = floor(t);                                      // 4x4 の中の 2 番目のテクセル（添字 1）
  float2 f = t - base;                                         // 小数位置
  float2 center_uv = (base + 1.0) * g_texel_size;              // 4x4 の中心（テクセルの角）
  // 4 つの 2x2: 左上・右上・左下・右下。各 GatherCmp は (x, y, z, w) = (左下, 右下, 右上, 左上) を返す
  float4 g00 = g_shadow_map.GatherCmp(g_shadow_cmp, center_uv + float2(-1, -1) * g_texel_size, s.depth);
  float4 g10 = g_shadow_map.GatherCmp(g_shadow_cmp, center_uv + float2(+1, -1) * g_texel_size, s.depth);
  float4 g01 = g_shadow_map.GatherCmp(g_shadow_cmp, center_uv + float2(-1, +1) * g_texel_size, s.depth);
  float4 g11 = g_shadow_map.GatherCmp(g_shadow_cmp, center_uv + float2(+1, +1) * g_texel_size, s.depth);
  // 4x4 の比較結果 c[行][列]（行 0 が上）
  float c[4][4] = {
    { g00.w, g00.z, g10.w, g10.z },
    { g00.x, g00.y, g10.x, g10.y },
    { g01.w, g01.z, g11.w, g11.z },
    { g01.x, g01.y, g11.x, g11.y } };
  float wx[4] = { 1.0 - f.x, 1.0, 1.0, f.x };
  float wy[4] = { 1.0 - f.y, 1.0, 1.0, f.y };
  float sum = 0;
  [unroll] for (int j = 0; j < 4; ++j) {
    [unroll] for (int i = 0; i < 4; ++i) {
      sum += c[j][i] * wx[i] * wy[j];
    }
  }
  return sum / 9.0;                                            // 重みの合計は 3 × 3 = 9
}
```

重みは `SampleCmp` 9 回の結果と一致するように導きます。座標の小数位置を `f` とすると、各 `SampleCmp` は片側のテクセルに `1−f`、反対側に `f` の重みを与えます。これを −1、0、+1 の 3 つのずらしで 3 分の 1 ずつ足すと 4 つのテクセルの重みは、軸ごとに `[1−f, 1, 1, f] / 3` になります。2 次元では軸ごとの重みの積を 9 で割ります（`3 × 3`）。

`GatherCmp` が返す 4 つの値の順序は `(x, y, z, w)` が `(左下, 右下, 右上, 左上)` だとして書いています。C++ で `SampleCmp` と `GatherCmp` を同じ約束で再現し、ランダムなマップ、ランダムな位置の 20,000 点で、9 回の結果と 4 回の結果を比べました。最大の差は 1.19 × 10⁻⁷ で、浮動小数点の誤差の範囲です。ただし、これは再現の中の一致で GPU の実機での順序は確認していません。

読み込みの数で比べます。9 回版は 9 回の `sample_c`、4 回版は 4 回の `gather4_c` です。`fxc` の命令数はフル版の関数単体で、9 回版が 46、4 回版が 56 でした。読み込みは 4 回に減るが重みの計算が増えて、命令数は増えます。メモリ待ちが支配的なら 4 回版が有利になり演算が支配的なら 9 回版が有利になります。実機では測っていません。

大きな範囲では差が広がります。5×5 の箱型は `SampleCmp` 25 回、`GatherCmp` 9 回で 7×7 は 49 回と 16 回です。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="N×N の箱型 PCF の読み込み回数"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">N×N の箱型 PCF の読み込み回数</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">25</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">50</text><rect x="81.5" y="187.0" width="43.0" height="3.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="103.0" y="183.0" text-anchor="middle" font-size="10" fill="currentColor">1</text><rect x="127.5" y="187.0" width="43.0" height="3.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="149.0" y="183.0" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">1</text><rect x="216.5" y="163.0" width="43.0" height="27.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="238.0" y="159.0" text-anchor="middle" font-size="10" fill="currentColor">9</text><rect x="262.5" y="178.0" width="43.0" height="12.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="284.0" y="174.0" text-anchor="middle" font-size="10" fill="currentColor">4</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">3</text><rect x="351.5" y="115.0" width="43.0" height="75.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="373.0" y="111.0" text-anchor="middle" font-size="10" fill="currentColor">25</text><rect x="397.5" y="163.0" width="43.0" height="27.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="419.0" y="159.0" text-anchor="middle" font-size="10" fill="currentColor">9</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">5</text><rect x="486.5" y="43.0" width="43.0" height="147.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="508.0" y="39.0" text-anchor="middle" font-size="10" fill="currentColor">49</text><rect x="532.5" y="142.0" width="43.0" height="48.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="554.0" y="138.0" text-anchor="middle" font-size="10" fill="currentColor">16</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">7</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">SampleCmp</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">GatherCmp</text></svg>

## カスケード（配列） {#cascade}

カスケード シャドウ マップは `Texture2DArray` に入れて、スライス番号を指定して読みます。

```hlsl
// ================= ⑤ カスケード（配列）=================

cbuffer CascadeCB : register(b1) {
  float4x4 g_cascade_view_proj[4];
  float4 g_cascade_far;           // 各カスケードの手前側の境界（視点からの距離 [m]）
};

float ShadowCascade(float3 world_pos, float view_depth) {
  int slice = 3;                                               // 見つからなければ最後のカスケード
  [unroll] for (int i = 2; i >= 0; --i) {
    if (view_depth < g_cascade_far[i]) slice = i;              // 最も手前（細かい）カスケードを選ぶ
  }
  float4 clip = mul(float4(world_pos, 1.0), g_cascade_view_proj[slice]);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;
  return g_shadow_array.SampleCmpLevelZero(g_shadow_cmp, float3(uv, slice), ndc.z - g_bias);
}
```

`float3(uv, slice)` でスライスを指定します。スライスは視点からの距離で選びます。手前から順に境界より近い最初のカスケードを選びます。選び方と境界のぼかしは [Cascaded Shadow Maps](../cascaded.md) を見てください。

## reversed-Z {#reversed}

reversed-Z では near が 1、far が 0 になります。比較関数を `GREATER_EQUAL` にしバイアスは近づける向き（`+`）にします。

```hlsl
// 比較の向きだけを変えた reversed-Z 版（near = 1、far = 0）。サンプラーの ComparisonFunc は GREATER_EQUAL にする。
float ShadowHw2x2Reversed(float3 world_pos) {
  float4 clip = mul(float4(world_pos, 1.0), g_light_view_proj);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_cmp, uv, ndc.z + g_bias);   // reversed-Z ではバイアスの向きも逆（近づける）
}
```

比較関数を取り違えると全部が影になるか全く影が出なくなります。reversed-Z の投影行列の作り方は、[投影](../../../3d/projection.md) を見てください。

## テクスチャの形式と注意点 {#notes}

シャドウ マップの書き込みは `D32_FLOAT` や `D24_UNORM_S8_UINT`、`D16_UNORM` の深度バッファです。シェーダーから読むには `R32_TYPELESS` のテクスチャに DSV を `D32_FLOAT`、SRV を `R32_FLOAT` で作ります。

深度の精度は C++ で出しました。深度範囲 100 m の正射影で、16 ビットは約 1.53 mm、24 ビットは約 5.96 µm、float32 の [0.5, 1) は約 5.96 µm の刻みです。刻みがバイアスより小さければ、足ります。ミップは作りません。

## 数字を出した C++ {#experiment}

```cpp
// 比較サンプラーと PCF の数字を確かめる。GPU の動作（SampleCmp、GatherCmp）を C++ で再現する。
//   [1] 比較してから補間（SampleCmp）と補間してから比較の違い
//   [2] 3x3 PCF: SampleCmp 9 回と GatherCmp 4 回 + 重み が同じ値になるか
//   [3] 影の縁の幅と深度の精度（ワールド単位）
//   [4] 読み込みの数
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

struct Map {
  int w, h;
  std::vector<float> d;
  float At(int x, int y) const {                                 // 範囲外は境界色 1.0（最も遠い = 光が当たる）
    if (x < 0 || y < 0 || x >= w || y >= h) return 1.0f;
    return d[y * w + x];
  }
};

// SampleCmpLevelZero（LESS_EQUAL、線形）の再現: 4 テクセルを比較してから、小数位置で双線形に補間する。
static float SampleCmp(const Map& m, double u, double v, float ref) {
  double tx = u * m.w - 0.5, ty = v * m.h - 0.5;                 // テクセル中心が整数になる座標
  int x0 = (int)std::floor(tx), y0 = (int)std::floor(ty);
  double fx = tx - x0, fy = ty - y0;
  auto c = [&](int x, int y) { return ref <= m.At(x, y) ? 1.0 : 0.0; };   // 比較: 参照値 <= 保存値 なら光
  return (float)((c(x0, y0) * (1 - fx) + c(x0 + 1, y0) * fx) * (1 - fy) + (c(x0, y0 + 1) * (1 - fx) + c(x0 + 1, y0 + 1) * fx) * fy);
}

// GatherCmp の再現: 2x2 の比較結果を (左下, 右下, 右上, 左上) = (x, y, z, w) の順で返す（補間なし）。
static std::array<float, 4> GatherCmp(const Map& m, double u, double v, float ref) {
  int x0 = (int)std::floor(u * m.w - 0.5), y0 = (int)std::floor(v * m.h - 0.5);
  auto c = [&](int x, int y) { return ref <= m.At(x, y) ? 1.0f : 0.0f; };
  return {c(x0, y0 + 1), c(x0 + 1, y0 + 1), c(x0 + 1, y0), c(x0, y0)};
}

// HLSL の ShadowPcf3x3_Nine と同じ。
static float PcfNine(const Map& m, double u, double v, float ref) {
  float sum = 0;
  for (int y = -1; y <= 1; ++y)
    for (int x = -1; x <= 1; ++x) sum += SampleCmp(m, u + x / (double)m.w, v + y / (double)m.h, ref);
  return sum / 9;
}

// HLSL の ShadowPcf3x3_Gather と同じ。
static float PcfGather(const Map& m, double u, double v, float ref) {
  double tx = u * m.w - 0.5, ty = v * m.h - 0.5;
  double bx = std::floor(tx), by = std::floor(ty), fx = tx - bx, fy = ty - by;
  double cu = (bx + 1) / m.w, cv = (by + 1) / m.h;               // 4x4 の中心（テクセルの角）
  auto g00 = GatherCmp(m, cu - 1.0 / m.w, cv - 1.0 / m.h, ref), g10 = GatherCmp(m, cu + 1.0 / m.w, cv - 1.0 / m.h, ref);
  auto g01 = GatherCmp(m, cu - 1.0 / m.w, cv + 1.0 / m.h, ref), g11 = GatherCmp(m, cu + 1.0 / m.w, cv + 1.0 / m.h, ref);
  float c[4][4] = {{g00[3], g00[2], g10[3], g10[2]}, {g00[0], g00[1], g10[0], g10[1]},
                   {g01[3], g01[2], g11[3], g11[2]}, {g01[0], g01[1], g11[0], g11[1]}};
  double wx[4] = {1 - fx, 1, 1, fx}, wy[4] = {1 - fy, 1, 1, fy};
  double sum = 0;
  for (int j = 0; j < 4; ++j)
    for (int i = 0; i < 4; ++i) sum += c[j][i] * wx[i] * wy[j];
  return (float)(sum / 9);
}

int main() {
  // ---- [1] 比較してから補間 vs 補間してから比較 ----
  // 1 行のシャドウ マップ: 左の 2 テクセルが遮蔽物（深度 0.3）、右の 2 テクセルが背景（0.9）。受け手の深度 0.6 は遮蔽物の奥・背景の手前。
  std::printf("[1] step edge: occluder depth 0.3 | background 0.9, receiver depth 0.6\n");
  std::printf("position t (texel centers 1 -> 2)   compare-then-filter   filter-then-compare\n");
  Map row{4, 1, {0.3f, 0.3f, 0.9f, 0.9f}};
  for (double t = 0; t <= 1.0001; t += 0.125) {
    double u = (1.5 + t) / 4.0;                                  // 1 番目と 2 番目のテクセル中心の間
    float a = SampleCmp(row, u, 0.5, 0.6f);
    double interp = 0.3 * (1 - t) + 0.9 * t;                     // 先に深度を補間
    float b = 0.6 <= interp ? 1.0f : 0.0f;
    std::printf("t = %.3f                              %.3f                 %.0f\n", t, a, b);
  }

  // ---- [2] 9 回と GatherCmp 4 回が一致するか ----
  std::mt19937 rng(5);
  std::uniform_real_distribution<float> uni(0, 1);
  Map m{64, 64, std::vector<float>(64 * 64)};
  for (auto& v : m.d) v = uni(rng);                              // ランダムな深度のマップ（最悪ケースのつもり）
  double max_diff = 0;
  for (int i = 0; i < 20000; ++i) {
    double u = 0.1 + 0.8 * uni(rng), v = 0.1 + 0.8 * uni(rng);
    float ref = uni(rng);
    max_diff = std::max(max_diff, (double)std::fabs(PcfNine(m, u, v, ref) - PcfGather(m, u, v, ref)));
  }
  std::printf("\n[2] 3x3 PCF: max |SampleCmp x 9 - GatherCmp x 4 with weights| over 20000 random samples = %.2e\n", max_diff);

  // ---- [3] 縁の幅と深度の精度 ----
  double ortho_width = 50.0, depth_range = 100.0;
  int size = 2048;
  double texel = ortho_width / size;
  std::printf("\n[3] ortho width %.0f m, map %d, depth range %.0f m\n", ortho_width, size, depth_range);
  std::printf("texel = %.2f cm; 2x2 PCF edge ~ %.1f cm; 3x3 PCF (4x4 footprint) edge ~ %.1f cm\n", texel * 100, 2 * texel * 100, 4 * texel * 100);
  std::printf("depth step: 16-bit = %.2f mm, 24-bit = %.2f um, float32 in [0.5,1) = %.2f um\n", depth_range / 65536 * 1000,
              depth_range / 16777216.0 * 1e6, depth_range * std::pow(2.0, -24) * 1e6);
  std::printf("bias 0.0005 in NDC z = %.1f cm\n", 0.0005 * depth_range * 100);

  // ---- [4] 読み込みの数 ----
  std::printf("\n[4] fetches for an N x N box PCF on top of 2x2 bilinear comparisons\n");
  std::printf("N  SampleCmp calls  footprint(texels)  GatherCmp calls\n");
  for (int n : {1, 3, 5, 7}) {
    int footprint = n + 1;
    int gathers = ((footprint + 1) / 2) * ((footprint + 1) / 2);
    std::printf("%d  %-14d  %dx%-12d  %d\n", n, n * n, footprint, footprint, gathers);
  }
  return 0;
}
```

```text title="実行結果"
[1] step edge: occluder depth 0.3 | background 0.9, receiver depth 0.6
position t (texel centers 1 -> 2)   compare-then-filter   filter-then-compare
t = 0.000                              0.000                 0
t = 0.125                              0.125                 0
t = 0.250                              0.250                 0
t = 0.375                              0.375                 0
t = 0.500                              0.500                 1
t = 0.625                              0.625                 1
t = 0.750                              0.750                 1
t = 0.875                              0.875                 1
t = 1.000                              1.000                 1
```

```text title="実行結果（続き）"
[2] 3x3 PCF: max |SampleCmp x 9 - GatherCmp x 4 with weights| over 20000 random samples = 1.19e-07
```

```text title="実行結果（続き）"
[3] ortho width 50 m, map 2048, depth range 100 m
texel = 2.44 cm; 2x2 PCF edge ~ 4.9 cm; 3x3 PCF (4x4 footprint) edge ~ 9.8 cm
depth step: 16-bit = 1.53 mm, 24-bit = 5.96 um, float32 in [0.5,1) = 5.96 um
bias 0.0005 in NDC z = 5.0 cm
```

```text title="実行結果（続き）"
[4] fetches for an N x N box PCF on top of 2x2 bilinear comparisons
N  SampleCmp calls  footprint(texels)  GatherCmp calls
1  1               2x2             1
3  9               4x4             4
5  25              6x6             9
7  49              8x8             16
```

## よくあるミス {#mistakes}

??? failure "影が上下に反転する"
    NDC の y（上向き）とテクスチャの v（下向き）の違いを直していない。`ndc.xy * float2(0.5, −0.5) + 0.5` にする。

??? failure "影が全くない、または全部が影になる"
    比較関数が深度の向きと合っていない。標準の Z は `LESS_EQUAL`、reversed-Z は `GREATER_EQUAL`。

??? failure "通常のサンプラーで読んで、おかしい"
    比較サンプラーは `SamplerComparisonState` で受け `SampleCmp` で読む。

??? failure "光の far を超えた所が影になる"
    `z` の範囲を調べていない。`ndc.z > 1.0` と `ndc.z < 0.0` は光が当たる扱いにする。

??? failure "縁が階段状になる"
    補間してから比較している、または点サンプリングで読んでいる。比較サンプラーで比較してから補間する。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 光の空間の深度とマップの深度を比べる。参照値 <= 保存値 なら光（標準の Z）。
    - [x] 比較サンプラーは、比較してから補間する。補間してから比較しない。
    - [x] 3×3 の PCF は、`SampleCmp` 9 回、または `GatherCmp` 4 回と重み `[1−f, 1, 1, f] / 3`。
    - [x] 範囲外と `z` の範囲外は、光が当たる扱い。
    - [x] reversed-Z では、比較関数とバイアスの向きを逆にする。

## 参考 {#references}

- William T. Reeves, David H. Salesin, Robert L. Cook, "Rendering Antialiased Shadows with Depth Maps", Proceedings of SIGGRAPH 1987, pp. 283–291. 読んでいない。PCF の原典として挙げる。
- Microsoft Learn, "D3D11_SAMPLER_DESC", "SampleCmp", "GatherCmp". 読んでいない。API の名前の出典として挙げる。
- このページの比較サンプラーの再現と 3×3 の重みの導出は、説明のために書いたもの。実機での動作は未確認。

## 関連ページ {#related}

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [PCF](../pcf.md)
- [Shadow Bias](../bias/index.md)
- [Cascaded Shadow Maps](../cascaded.md)
