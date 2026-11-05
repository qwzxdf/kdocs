---
title: Where to Apply Fog
tags:
  - 描画
---

# Where to Apply Fog

フォグは屋外の遠景をなじませる道具ですが、かける場所と順番を間違えると、すぐに破綻します。不透明な地面は霧に沈んでいるのに、パーティクルだけが霧の中で光って浮く。夜なのに霧が昼の色のまま白く光る。トーンマップの後に霧をかけて、明るい霧が出せない。どれもフォグの式が間違っているのではなく、「どの描画物にどの段階でどの合成方法でかけるか」の決め方の問題です。このページではフォグの 2 つの置き場所（物体ごと全画面）、半透明と加算の扱い空、区画ごとの設定、色の順序を HLSL と数字で説明します。

!!! tip "ポイント"
    - フォグは指数型 `T = exp(-σ d)`。色は `color × T + fog_color × (1 − T)`。ライティングの後、トーンマップの前にかける。
    - 不透明は物体ごとにかけても、全画面でかけてもよい。半透明は深度に書かれないので、全画面のフォグがかからない。自分のシェーダーでかける。
    - 加算ブレンドは霧の色を足さない。透過率 `T` を掛けるだけにする。足すと遠くの粒子が明るくなる（200 m で 2.6 倍）。
    - 頂点ごとのフォグは大きな三角形で誤差が大きい。10〜110 m にまたがる辺で、最大 0.17 ずれる。画素ごとの距離で計算する。
    - 空は普通は霧をかけない。地平線の近くだけ霧の色に寄せる。夜と屋内は色と σ を区画ごとに変える。

!!! info "このページを読む前に"
    - [Aerial Perspective and Fog](index.md)（このセクション全体の地図と読む順番）
    - [Fog Equation](fog-equation.md)（`T = exp(-σ d)` の式と霧の色の足し方）

## 読んだ資料 {#sources}

このページは特定の論文を読んで書いたものではありません。内容は一般的な実装の知識とこのページの実験（C++）です。Wronski の SIGGRAPH 2014 の発表（Volumetric Fog）と Hillaire の EGSR 2020 の論文は、別のページの執筆で一部を読みましたが、ここでは区画ごとの設定とボリューム フォグへの橋渡しに触れるだけです。Real-Time Rendering 第 4 版は、読んでいません。

HLSL は `fxc`（`ps_5_0` と `vs_5_0`）でコンパイルして確かめ C++ は MSVC で実行しました。σ、色、しきい値は説明のための値です。

## 描画物の種類ごとに見る {#overview}

霧は「光がカメラへ届く間に減る分と足される分」です。描画物の種類によって「減る分と足される分」の扱いが違います。まず、基本の部品を置きます。

```hlsl
```hlsl
// ================= 部品 =================

float Transmittance(float distance) {
  return exp(-g_sigma * distance);                       // 1 = 霧なし、0 = 霧に隠れる
}

// 霧の色を足しながら元の色を減らす。T が小さい（遠い）ほど霧の色に近づく。
float3 ApplyFog(float3 color, float distance) {
  float t = Transmittance(distance);
  return color * t + g_fog_color * (1.0 - t);
}
```
```

`Transmittance` は距離 `d` を進んだ後に元の光が残る割合です。`σ = 0.02` なら 50 m で 0.37、100 m で 0.135、200 m で 0.018 です。`ApplyFog` は元の色を `T` 倍に減らし、減った分を霧の色で埋めます。`T = 1` なら元の色のまま `T = 0` なら霧の色だけになります。

<svg class="fig flow" viewBox="0 0 660 194" role="img" aria-label="描画の順番とフォグ(青: 不透明、黄: 半透明、灰: ポスト)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">描画の順番とフォグ(青: 不透明、黄: 半透明、灰: ポスト)</text><rect x="10" y="34" width="140" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="80.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">不透明を描く</text><text x="80.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">(深度を書く)</text><rect x="180" y="34" width="140" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="250.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">ライティング</text><text x="250.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">(HDR)</text><rect x="350" y="34" width="140" height="50" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="420.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">フォグ(全画面)</text><text x="420.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">不透明だけ</text><rect x="10" y="114" width="140" height="50" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="80.0" y="136.0" text-anchor="middle" font-size="11" fill="currentColor">半透明を描く</text><text x="80.0" y="150.0" text-anchor="middle" font-size="11" fill="currentColor">各自でフォグ</text><rect x="180" y="114" width="140" height="50" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="250.0" y="143.0" text-anchor="middle" font-size="11" fill="currentColor">ブルーム</text><rect x="350" y="114" width="140" height="50" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="420.0" y="136.0" text-anchor="middle" font-size="11" fill="currentColor">トーンマップ</text><text x="420.0" y="150.0" text-anchor="middle" font-size="11" fill="currentColor">ガンマ</text><line x1="150" y1="59.0" x2="180" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="320" y1="59.0" x2="350" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="420.0" y1="84" x2="80.0" y2="114" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="150" y1="139.0" x2="180" y2="139.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="320" y1="139.0" x2="350" y2="139.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/></svg>

## 方法 1: 物体ごとにかける {#per-object}

各物体のピクセル シェーダーの最後で、ライティング済みの色に霧をかけます。

```hlsl
```hlsl
// ================= 方法 1: 物体ごと（フォワード、不透明）=================

struct PSInput {
  float4 position : SV_Position;
  float3 world_position : TEXCOORD0;
  float3 world_normal : NORMAL;
  float2 uv : TEXCOORD1;
};

float4 ForwardOpaquePS(PSInput input) : SV_Target {
  float3 albedo = g_albedo_tex.Sample(g_linear_clamp, input.uv).rgb;
  float3 lit = albedo * max(dot(normalize(input.world_normal), float3(0, 1, 0)), 0.0);   // 簡易ライティング（説明用）
  float d = length(input.world_position - g_camera_position);   // 画素ごとの距離（頂点で計算して補間しない）
  return float4(ApplyFog(lit, d), 1.0);                         // ライティングの後、出力の直前
}
```
```

`d` は画素のワールド位置とカメラの距離で、画素ごとに計算します。**頂点で計算して補間してはいけません**（理由は後の「頂点ごとのフォグ」で数字を出します）。長所は半透明の物にも同じ関数をそのまま使えることです。短所はすべてのマテリアルのシェーダーにこの 1 行を入れる必要があることで、入れ忘れた物だけ霧がかからず浮いて見えます。

## 方法 2: 全画面のポスト プロセス {#post}

ライティングが終わった HDR の画像と深度から、画素ごとの距離を復元して全画素にかけます。ディファード レンダリングの標準的な形です。

```hlsl
```hlsl
// ================= 方法 2: 全画面のポスト（ディファード）=================

// 深度からワールド位置を復元する。uv は 0〜1（上が 0）、深度は 0〜1。
float3 ReconstructWorldPosition(float2 uv, float depth) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 world = mul(float4(ndc, depth, 1.0), g_inv_view_proj);
  return world.xyz / world.w;                            // 同次座標を割る
}

float4 FogPostPS(float4 pos : SV_Position) : SV_Target {
  float2 uv = pos.xy / g_screen_size;
  float3 scene = g_scene_color.Load(int3(pos.xy, 0)).rgb;
  float depth = g_scene_depth.Load(int3(pos.xy, 0));
  float3 world = ReconstructWorldPosition(uv, depth);
  float3 to_pixel = world - g_camera_position;
  float d = length(to_pixel);

  if (depth >= 1.0) {                                    // 空（far plane のまま）。距離は無限扱い
    float3 dir = normalize(to_pixel);
    // 地平線に近いほど霧の色へ。sin(仰角) 0.33（仰角約 19°）で 0。係数 3 は足した値。
    float horizon = saturate(1.0 - abs(dir.y) * 3.0);
    return float4(lerp(scene, g_fog_color, horizon * g_fog_sky_strength), 1.0);
  }
  return float4(ApplyFog(scene, d), 1.0);
}
```
```

`ReconstructWorldPosition` は画面の UV と深度から NDC を作り逆ビュー射影行列を掛けて、`w` で割ります。`w` で割るのを忘れると遠い画素ほど位置がずれて、霧の濃さが場所によって変わります。上下は画面の UV が上から下、NDC の y が下から上なので、`1.0 - uv.y * 2.0` で反転します。

長所はマテリアルのシェーダーを変えなくてよいことです。短所は深度に書かれない物（半透明）に霧がかからないことです。次の節で扱います。

## 半透明と加算 {#transparent}

半透明は不透明の深度に書かれないので、全画面のフォグがかかりません。自分のシェーダーでかけます。ただし、ブレンドの種類でかけ方が違います。

```hlsl
```hlsl
// ================= 半透明 =================

Texture2D<float4> g_particle_tex : register(t3);

// アルファブレンド（SrcAlpha, InvSrcAlpha）: 色にだけ霧をかける。アルファはそのまま。
// 霧の色を足すのは背景が霧に隠れる分をこの粒子が「霧の色で覆う」ため。
float4 AlphaBlendedPS(PSInput input) : SV_Target {
  float4 tex = g_particle_tex.Sample(g_linear_clamp, input.uv);
  float d = length(input.world_position - g_camera_position);
  return float4(ApplyFog(tex.rgb, d), tex.a);
}

// 加算ブレンド（One, One）: 霧の色を足してはいけない。背景にはすでに霧がかかっている。
// 光の分は霧の中を通る間に減る（T を掛ける）だけ。
float4 AdditivePS(PSInput input) : SV_Target {
  float4 tex = g_particle_tex.Sample(g_linear_clamp, input.uv);
  float d = length(input.world_position - g_camera_position);
  return float4(tex.rgb * Transmittance(d), tex.a);
}

// 乗算ブレンド（Zero, SrcColor）: 暗くする物。遠いほど霧の分だけ「何もしない」（白 1.0）に寄せる。
float4 MultiplyPS(PSInput input) : SV_Target {
  float3 shade = g_particle_tex.Sample(g_linear_clamp, input.uv).rgb;
  float d = length(input.world_position - g_camera_position);
  return float4(lerp(float3(1, 1, 1), shade, Transmittance(d)), 1.0);
}
```
```

**アルファ ブレンド**（`SrcAlpha, InvSrcAlpha`）の物は、色に `ApplyFog` をかけアルファはそのままにします。遠い煙が霧の色に溶けるように見えます。

**加算ブレンド**（`One, One`）の物は霧の色を足してはいけません。背景にはすでに霧がかかっています。加算は背景に光を足すだけなので、足すべき光は「粒子の光が霧の中を進む間に減った分」、つまり `color × T` だけです。霧の色まで足すと霧の色が二重に加わります。

C++ で数えると HDR で 20 の炎の粒子（霧の色 0.6）は、10 m で 16.375（正解）に対して 16.483（誤り）で、1.007 倍です。50 m で 1.052 倍、100 m で 1.192 倍、200 m で 2.608 倍と遠いほど誤りの明るさが目立ちます。**遠くの炎が霧の中で白く光る**症状として現れます。

**乗算ブレンド**（`Zero, SrcColor`）は影や汚れで背景を暗くする物です。霧が濃い所では背景が霧に覆われているので、暗くする効果が弱くなります。`lerp(1, shade, T)` で遠いほど 1（何もしない）に寄せます。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="頂点ごとのフォグの最大誤差(σ=0.02、辺の距離範囲ごと)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">頂点ごとのフォグの最大誤差(σ=0.02、辺の距離範囲ごと)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">0.2</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">0.4</text><rect x="104.5" y="188.6" width="43.0" height="1.4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="126.0" y="184.6125" text-anchor="middle" font-size="10" fill="currentColor">0.0037</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">10〜20 m</text><rect x="239.5" y="166.1" width="43.0" height="23.9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="261.0" y="162.075" text-anchor="middle" font-size="10" fill="currentColor">0.0638</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">10〜60 m</text><rect x="374.5" y="127.0" width="43.0" height="63.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="396.0" y="123.03750000000001" text-anchor="middle" font-size="10" fill="currentColor">0.1679</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">10〜110 m</text><rect x="509.5" y="64.2" width="43.0" height="125.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="531.0" y="60.1875" text-anchor="middle" font-size="10" fill="currentColor">0.3355</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">10〜210 m</text></svg>

## 空にかけるか {#sky}

空は深度が最大（far plane）のままの画素です。距離が無限なので普通に `ApplyFog` をかけると、`T = 0` になり空が全部、霧の色になって消えます。

そこで、空はスキップするか地平線の近くだけを霧の色へ寄せます。上の `FogPostPS` の空の分岐は後者です。重みは `saturate(1 − |sin(仰角)| × 3)` で仰角 0° で 1、2° で 0.895、5° で 0.739、10° で 0.479、15° で 0.224、約 19.5°（`sin = 1/3`）以上で 0 です。係数 3 は霧が空に及ぶ高さを決める値で、足した値です。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="空の地平線ブレンドの重み"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">空の地平線ブレンドの重み</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="150.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">5</text><text x="240.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="330.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">15</text><text x="420.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="510.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">25</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">仰角(度)</text><polyline points="60.0,40.0 69.0,44.5 78.0,48.9 87.0,53.4 96.0,57.8 105.0,62.2 114.0,66.7 123.0,71.1 132.0,75.6 141.0,80.0 150.0,84.4 159.0,88.9 168.0,93.3 177.0,97.7 186.0,102.2 195.0,106.6 204.0,111.0 213.0,115.4 222.0,119.8 231.0,124.2 240.0,128.6 249.0,132.9 258.0,137.3 267.0,141.7 276.0,146.0 285.0,150.4 294.0,154.7 303.0,159.1 312.0,163.4 321.0,167.7 330.0,172.0 339.0,176.3 348.0,180.6 357.0,184.8 366.0,189.1 375.0,193.4 384.0,197.6 393.0,201.8 402.0,206.0 411.0,210.0 420.0,210.0 429.0,210.0 438.0,210.0 447.0,210.0 456.0,210.0 465.0,210.0 474.0,210.0 483.0,210.0 492.0,210.0 501.0,210.0 510.0,210.0 519.0,210.0 528.0,210.0 537.0,210.0 546.0,210.0 555.0,210.0 564.0,210.0 573.0,210.0 582.0,210.0 591.0,210.0 600.0,210.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">重み</text></svg>

地平線で空と遠景の霧が同じ色になれば、境目が自然につながります。色の合わせ方は [Matching Fog Color to the Sky](color-match.md) を見てください。濃霧のときは `g_fog_sky_strength` を 1 にして、空も霧の色にします。

## 区画ごとの設定（夜・屋内・洞窟） {#zones}

夜は霧の色を暗くします。昼の明るい霧の色のまま夜を迎えると、霧だけが光ります。屋内や洞窟はσ を小さくするか霧の色を変えます。外と中で設定が違う場合は区画（ゾーン）ごとに設定を持ち境で補間します。

```hlsl
```hlsl
// ================= 区画ごとの設定 =================

struct FogZone {
  float3 center;    // 区画の中心 [m]
  float radius;     // 影響する半径 [m]
  float3 color;
  float sigma;
};
StructuredBuffer<FogZone> g_zones : register(t4);
cbuffer ZoneCB : register(b1) { uint g_zone_count; float3 g_zone_pad; };

// カメラ位置の周りの区画を距離で重みづけして混ぜる。境で設定が急に変わらないよう重みは中心で 1、半径で 0。
void BlendZones(float3 camera, out float3 color, out float sigma) {
  float3 c = g_fog_color * 0.0001;                       // ゼロ割りを避ける最小の既定の重み（足した処理）
  float s = g_sigma * 0.0001, wsum = 0.0001;
  for (uint i = 0; i < g_zone_count; ++i) {
    FogZone z = g_zones[i];
    float w = saturate(1.0 - distance(camera, z.center) / z.radius);
    w = w * w * (3.0 - 2.0 * w);                         // smoothstep で境をなめらかに
    c += z.color * w;
    s += z.sigma * w;
    wsum += w;
  }
  color = c / wsum;
  sigma = s / wsum;
}
```
```

重みはカメラと区画の中心の距離から、`1 − 距離 / 半径` を作り `smoothstep` でなめらかにします。重みが 0 の区画は影響せず重みが 1 の中心では、その区画の設定だけが効きます。複数の区画が重なる所では重みで平均します。ゼロ割りを避けるためごく小さな既定の重みを足します（足した処理）。

**境で急に切り替えない**のが要点です。扉をくぐった瞬間に霧の色が変わると、画面全体が瞬間的に色づきます。補間の幅は扉やトンネルの長さに合わせて決めます。

点光源の周りだけ霧が光る表現はフォグの式の延長ではなく、体積を持つ霧の計算が要ります。[Volumetric Fog](../volumetric-fog/index.md) を見てください。

## 頂点ごとのフォグ（比較用） {#per-vertex}

昔は頂点シェーダーでフォグの係数を計算し、三角形の中は補間に任せていました。

```hlsl
```hlsl
// ================= 頂点ごとのフォグ（比較用。非推奨）=================

struct VSOut {
  float4 position : SV_Position;
  float fog_factor : TEXCOORD0;
};

cbuffer ObjectCB : register(b2) { float4x4 g_world_view_proj; };

VSOut PerVertexFogVS(float3 pos : POSITION) {
  VSOut o;
  o.position = mul(float4(pos, 1.0), g_world_view_proj);
  o.fog_factor = Transmittance(o.position.w);            // 頂点で T を計算し、三角形の中は補間に任せる
  return o;
}
```
```

霧の係数は距離の指数関数で距離は辺に沿って線形ですが、係数は線形ではありません。三角形の内側を線形に補間すると、真の値からずれます。C++ で距離が d0 から d1 まで変わる辺を数えました。`σ = 0.02` で 10〜20 m の辺は最大 0.0037、10〜60 m で 0.0638、10〜110 m で 0.1679、10〜210 m で 0.3355 のずれです。**大きな三角形（地面、壁）ほど霧が中途半端になります。** 画素ごとに距離を求めれば、避けられます。

## 色の順序 {#order}

霧はライティングの後、トーンマップの前にかけます。

トーンマップの後にかけると霧の色が 0〜1 に押し込まれます。C++ で Reinhard（`x / (1 + x)`）を使って、HDR で 8 の景色に HDR で 3 の霧を `T = 0.5` でかけました。霧 → トーンマップの順序は 0.8462、トーンマップ → 霧の順序は 0.8194 で、差は 3.2 % です。差は小さく見えますが**明るい霧（HDR で 3）は、トーンマップ後には 0.75 より明るくできません。** 朝焼けや太陽に照らされた霧のような 1 を超える明るい霧の表現が、できなくなります。ブルームも霧の後にかけたほうが自然です。霧の中の光のにじみになるからです。

```text
ライティング → 霧 → ブルームなどのポスト エフェクト → トーンマップ → ガンマ
```

## 数字を出した C++ {#experiment}

```cpp
```cpp
// フォグをかける場所と順番で、結果がどう変わるかを数える。
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr double kPi = 3.14159265358979323846;
static double Tonemap(double x) { return x / (1.0 + x); }   // Reinhard（一例）。0〜1 に押し込む

int main() {
  const double sigma = 0.02;                                 // 減衰係数 [1/m]。50 m で T = 0.37
  // ---- ① 加算ブレンドの粒子: 霧の色を足すと遠いほど明るくなる ----
  std::printf("[1] additive particle (HDR color 20, fog color 0.6), correct = c*T, wrong = c*T + fog*(1-T)\n");
  std::printf("dist[m]   T      correct   wrong    wrong/correct\n");
  for (double d : {10.0, 50.0, 100.0, 200.0}) {
    double T = std::exp(-sigma * d);
    double ok = 20 * T, ng = 20 * T + 0.6 * (1 - T);          // 背景には、すでに霧がかかっている
    std::printf("%6.0f   %.3f  %7.3f  %7.3f   %.3f\n", d, T, ok, ng, ng / ok);
  }

  // ---- ② トーンマップの前後 ----
  std::printf("\n[2] fog before / after tone mapping (scene HDR 8, fog color HDR 3, T = 0.5)\n");
  double scene = 8, fog = 3, T = 0.5;
  double before = Tonemap(scene * T + fog * (1 - T));        // 霧 → トーンマップ（正しい順序）
  double after = Tonemap(scene) * T + Tonemap(fog) * (1 - T);   // トーンマップ → 霧
  std::printf("fog -> tonemap : %.4f\n", before);
  std::printf("tonemap -> fog : %.4f\n", after);
  std::printf("difference     : %.4f (%.1f %% of the first)\n", before - after, 100 * (before - after) / before);
  std::printf("fog color 3.0 after tonemap alone = %.3f (cannot exceed 1.0)\n", Tonemap(fog));

  // ---- ③ 頂点ごとのフォグの誤差 ----
  std::printf("\n[3] per-vertex fog: triangle edge from depth d0 to d1, fog factor f = 1 - exp(-sigma d)\n");
  std::printf("d0..d1[m]   max |linear-interp f - true f|   at t\n");
  for (auto e : {std::pair{10.0, 20.0}, std::pair{10.0, 60.0}, std::pair{10.0, 110.0}, std::pair{10.0, 210.0}}) {
    double f0 = 1 - std::exp(-sigma * e.first), f1 = 1 - std::exp(-sigma * e.second);
    double worst = 0, wt = 0;
    for (int i = 0; i <= 1000; ++i) {
      double t = i / 1000.0;
      double d = e.first + (e.second - e.first) * t;         // 距離は辺に沿って線形（簡略化: 視線との角度の変化は無視）
      double err = std::fabs((f0 + (f1 - f0) * t) - (1 - std::exp(-sigma * d)));
      if (err > worst) { worst = err; wt = t; }
    }
    std::printf("%4.0f..%-4.0f   %.4f                              %.2f\n", e.first, e.second, worst, wt);
  }

  // ---- ④ 空の地平線ブレンド: 重み = saturate(1 - |sin(仰角)| * 3) ----
  std::printf("\n[4] sky horizon blend weight vs elevation\n");
  for (double deg : {0.0, 2.0, 5.0, 10.0, 15.0, 19.47, 30.0}) {
    double s = std::sin(deg * kPi / 180);
    double w = std::clamp(1.0 - std::fabs(s) * 3.0, 0.0, 1.0);
    std::printf("elevation %5.2f deg  sin=%.3f  weight=%.3f\n", deg, s, w);
  }
  return 0;
}
```
```

```text title="実行結果"
[1] additive particle (HDR color 20, fog color 0.6), correct = c*T, wrong = c*T + fog*(1-T)
dist[m]   T      correct   wrong    wrong/correct
    10   0.819   16.375   16.483   1.007
    50   0.368    7.358    7.737   1.052
   100   0.135    2.707    3.226   1.192
   200   0.018    0.366    0.955   2.608
```

```text title="実行結果（続き）"
[2] fog before / after tone mapping (scene HDR 8, fog color HDR 3, T = 0.5)
fog -> tonemap : 0.8462
tonemap -> fog : 0.8194
difference     : 0.0267 (3.2 % of the first)
fog color 3.0 after tonemap alone = 0.750 (cannot exceed 1.0)
```

```text title="実行結果（続き）"
[3] per-vertex fog: triangle edge from depth d0 to d1, fog factor f = 1 - exp(-sigma d)
d0..d1[m]   max |linear-interp f - true f|   at t
  10..20     0.0037                              0.49
  10..60     0.0638                              0.46
  10..110    0.1679                              0.42
  10..210    0.3355                              0.35
```

```text title="実行結果（続き）"
[4] sky horizon blend weight vs elevation
elevation  0.00 deg  sin=0.000  weight=1.000
elevation  2.00 deg  sin=0.035  weight=0.895
elevation  5.00 deg  sin=0.087  weight=0.739
elevation 10.00 deg  sin=0.174  weight=0.479
elevation 15.00 deg  sin=0.259  weight=0.224
elevation 19.47 deg  sin=0.333  weight=0.000
elevation 30.00 deg  sin=0.500  weight=0.000
```

## よくあるミス {#mistakes}

??? failure "半透明の物だけ霧がかかっていない"
    全画面のフォグは深度に書かれない物にかからない。半透明のシェーダーに `ApplyFog` を入れる。

??? failure "遠くの炎やパーティクルが、霧の中で白く光る"
    加算ブレンドの物に霧の色を足している。`color × T` だけにする。

??? failure "空が全部、霧の色になる"
    空の画素（深度 1.0）に距離を無限として `ApplyFog` をかけている。空はスキップするか地平線の近くだけ寄せる。

??? failure "霧の中でも遠くの空が青いまま浮く"
    濃霧のとき空にも霧をかけていない。`g_fog_sky_strength` を上げる。

??? failure "大きな床や壁で、霧が中途半端に出る"
    頂点でフォグの係数を計算して補間している。画素ごとに距離を求める。

??? failure "明るい霧が出せない"
    トーンマップの後にかけている。霧はトーンマップの前、HDR の空間でかける。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] フォグはライティングの後、トーンマップの前にかける。
    - [x] 半透明は自分でかける。加算は `color × T` だけ（霧の色を足さない）。
    - [x] 距離は画素ごとに計算する（頂点で計算して補間しない）。
    - [x] 空は普通かけない。地平線の近くだけ霧の色へ寄せる。
    - [x] 夜と屋内は色と σ を区画ごとに持ち境をなめらかに補間する。

## 参考 {#references}

- Bart Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games. 一部だけ読んだ。区画ごとの設定の先にあるボリューム フォグの出典として挙げる。
- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Proc. EGSR 2020) 39(4), 2020. 一部だけ読んだ。空の描画の出典として挙げる。
- Tomasz Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018. 読んでいない。
- このページの HLSL（フォグの適用、区画の補間）と C++ の数字は説明のために書いたもの。

## 関連ページ {#related}

- [Aerial Perspective and Fog](index.md)
- [Fog Equation](fog-equation.md)
- [Height Fog](height-fog.md)
- [Matching Fog Color to the Sky](color-match.md)
- [Volumetric Fog](../volumetric-fog/index.md)
