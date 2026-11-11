---
title: Terrain Normals
tags:
  - 描画
---

# Terrain Normals

地形に陰影を付けるには各点で面がどちらを向いているかを知る必要があります。高さマップが持っているのは高さだけで、向きは入っていません。そこで隣り合う画素の高さの差から傾きを求めて、法線を作ります。この計算を毎フレームやるのか事前に法線マップへ焼いておくのかで、見た目と速さが変わります。

<strong>地形の法線は高さの差分から作る</strong>のが基本です。このページでは式の導き方、差分の取り方、計算する場所の選び方、法線マップの形式と精度、ミップマップで起きる問題までを順に説明します。

!!! tip "ポイント"
    - 法線は隣の高さの差（中央差分）を `(−∂h/∂x, 1, −∂h/∂z)` に入れて正規化したものです。
    - 高さと画素の間隔は同じ単位（メートル）にそろえます。ここがずれると斜面が急すぎたり緩すぎたりします。
    - 事前に法線マップへ焼くとピクセル シェーダーは 1 回読むだけで済みます。LOD で頂点が減っても陰影はポップしません。
    - 地形の法線は上向きなので、x と z だけを保存して y は `sqrt(1 − x² − z²)` で復元できます。
    - 高さが 8 ビットだと緩い斜面に階段状の縞が出ます。16 ビットにして直します。

!!! info "このページを読む前に"
    - [Heightmaps and Meshes](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 高さから法線を導く {#derive}

高さを `h(x, z)` とする曲面 `y = h(x, z)` を考えます。x 方向の接線は `(1, ∂h/∂x, 0)`、z 方向の接線は `(0, ∂h/∂z, 1)` です。法線は 2 つの接線の外積になります。

```text
n = (1, ∂h/∂x, 0) × (0, ∂h/∂z, 1)
  = (∂h/∂x × 1 − 0 × ∂h/∂z,  0 × 0 − 1 × 1,  1 × ∂h/∂z − ∂h/∂x × 0)
  = (∂h/∂x, −1, ∂h/∂z)
```

法線は上向き（y が正）にしたいので、符号を反転して `n = (−∂h/∂x, 1, −∂h/∂z)` を正規化します。傾きが大きいほど x と z の成分が大きくなって、法線が横へ倒れます。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="高さマップの断面で、左右の高さの差から接線と法線を作る"><defs><marker id="tnA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">中央差分: 左と右の高さの差が、傾きになる</text>
<path d="M30,210 L150,200 L270,170 L390,120 L510,100 L630,96 L700,98" fill="none" stroke="#4c8bf5" stroke-width="3"/>
<line x1="270" y1="170" x2="270" y2="224" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="390" y1="120" x2="390" y2="224" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="330" y1="145" x2="330" y2="224" stroke="#94a3b8" stroke-dasharray="4 4"/>
<circle cx="270" cy="170" r="5" fill="#e5aa28"/><circle cx="390" cy="120" r="5" fill="#e5aa28"/><circle cx="330" cy="145" r="6" fill="#e5484d"/>
<text x="270" y="242" text-anchor="middle" style="font-size:12px">h_左</text><text x="390" y="242" text-anchor="middle" style="font-size:12px">h_右</text><text x="330" y="242" text-anchor="middle" style="font-size:12px">この画素</text>
<line x1="270" y1="196" x2="390" y2="196" stroke="currentColor" stroke-width="1.5" marker-end="url(#tnA)"/><text x="330" y="190" text-anchor="middle" style="font-size:12px">2 s（ワールドの距離）</text>
<line x1="296" y1="160" x2="364" y2="130" stroke="#e5aa28" stroke-width="3"/><text x="372" y="168" text-anchor="start" style="font-size:12px;fill:#b7791f">接線</text>
<line x1="330" y1="145" x2="296" y2="70" stroke="#e5484d" stroke-width="3" marker-end="url(#tnA)"/><text x="288" y="62" text-anchor="end" style="font-size:12px;font-weight:600">法線</text>
<text x="470" y="150" style="font-size:12px">傾き ≒ (h_右 − h_左) / 2 s</text><text x="470" y="170" style="font-size:12px">法線 ∝ (h_左 − h_右, 2 s)</text></svg>

偏微分は隣の高さの差で近似します。画素の間隔（ワールドの距離）を `s` とすると、次のようになります。

```text
∂h/∂x ≈ (h_右 − h_左) / (2 s)
∂h/∂z ≈ (h_上 − h_下) / (2 s)

n = normalize( −(h_右 − h_左) / (2 s),  1,  −(h_上 − h_下) / (2 s) )
  = normalize( h_左 − h_右,  2 s,  h_下 − h_上 )          ← 全体に 2s を掛けただけ
```

最後の形が次のコードの `float3(hl - hr, 2.0 * texel_world, hd - hu)` です。`2 s` を掛け忘れたり間違えたりすると、斜面が実際より急に見えたりなだらかに見えたりします。数字で確かめます。メートル単位で隣の高さの差が左右で 1 m、`s` が 2 m なら傾きは `1 / (2 × 2) = 0.25` です。法線は `normalize(−1, 4, 0)` で鉛直から約 14° 傾きます。`s` を UV の 1 テクセル（たとえば 1/1024）にしてしまうと `normalize(−1, 0.002, 0)` となって、ほぼ真横を向きます。

高さも画素の間隔も同じ単位（メートル）にそろえます。これが唯一の注意点です。

## 差分の取り方 {#difference}

### 前方差分（2 点）

自分と右・上の 2 画素だけを読みます。読む回数は最小ですが差分の中心が画素の中心から半画素ずれます。地形全体が半画素ずれた陰影になって、段差の位置が高さと合いません。実用ではほぼ使いません。

### 中央差分（4 点）

左・右・下・上の 4 画素を読みます。差分の中心が画素の中心に合います。標準の方式で上の導出がそのまま使えます。

```hlsl
// 共通の宣言（以下のコードで使う）
Texture2D<float> g_height : register(t0);        // 高さ。0..1 に正規化（R16_UNORM が望ましい）
SamplerState g_linear_clamp : register(s0);

cbuffer TerrainConstants : register(b0) {
  float2 g_height_map_size;   // 高さマップの幅・高さ（テクセル数）
  float g_height_scale;       // 高さ 1.0 に対応するメートル。例: 200
  float g_texel_world;        // 隣り合うテクセルの間隔（メートル）。terrain_size / 幅
};

float SampleHeight(float2 uv) {
  // 補間つきで読んで、メートルに直す。単位をそろえる要の 1 行
  return g_height.SampleLevel(g_linear_clamp, uv, 0) * g_height_scale;
}

float3 NormalCentral(float2 uv) {
  float2 texel = 1.0 / g_height_map_size;         // UV での 1 テクセル
  float hl = SampleHeight(uv - float2(texel.x, 0));
  float hr = SampleHeight(uv + float2(texel.x, 0));
  float hd = SampleHeight(uv - float2(0, texel.y));
  float hu = SampleHeight(uv + float2(0, texel.y));
  // y 成分の 2 s は、差分を取った 2 画素ぶんの距離（メートル）
  return normalize(float3(hl - hr, 2.0 * g_texel_world, hd - hu));
}
```

`SampleLevel` のミップ レベルは 0 に固定します。高さマップにミップがあっても、法線の計算は最も細かい高さで行います。

### Sobel（8 点）

周りの 8 画素を読みます。重みを 1、2、1 にして斜めの画素も使うので、細かいノイズが平均化されます。実測の地形データのようにノイズが多い高さに向いています。重みの合計が 8 なので y 成分は `2 s` ではなく `8 s` を使います。

```hlsl
float3 NormalSobel(float2 uv) {
  float2 t = 1.0 / g_height_map_size;
  float h00 = SampleHeight(uv + t * float2(-1, -1));
  float h10 = SampleHeight(uv + t * float2( 0, -1));
  float h20 = SampleHeight(uv + t * float2( 1, -1));
  float h01 = SampleHeight(uv + t * float2(-1,  0));
  float h21 = SampleHeight(uv + t * float2( 1,  0));
  float h02 = SampleHeight(uv + t * float2(-1,  1));
  float h12 = SampleHeight(uv + t * float2( 0,  1));
  float h22 = SampleHeight(uv + t * float2( 1,  1));

  // x 方向: 右の列 − 左の列（重み 1, 2, 1）。z 方向: 上の行 − 下の行
  float dx = (h20 + 2.0 * h21 + h22) - (h00 + 2.0 * h01 + h02);
  float dz = (h02 + 2.0 * h12 + h22) - (h00 + 2.0 * h10 + h20);
  // 係数の総和が 8（中央差分は 2）。y 成分に 8 s を使うのはこのため
  return normalize(float3(-dx, 8.0 * g_texel_world, -dz));
}
```

Sobel はなめらかになる代わりに本当の細かい起伏もなだらかにします。岩のような鋭い地形では中央差分の方が輪郭が残ります。

## 法線をどこで計算するか {#where}

### 頂点シェーダーで計算する

頂点ごとに高さを 4 回読んで、法線を作り補間してピクセル シェーダーへ渡します。ピクセル シェーダーは軽くなりますが、頂点が粗い遠景では頂点の間にある細かい起伏が法線に入りません。LOD が変わると頂点の数が変わるので、陰影がポップします。

### ピクセル シェーダーで計算する

ピクセルごとに高さを 4 回（Sobel なら 8 回）読みます。頂点が粗くても見た目の凹凸が高さマップの解像度で出ます。ただし、全ピクセルでテクスチャ読み出しが増えるので、画面を広く覆う地形ではコストが目立ちます。

### 法線マップに焼く

高さマップから法線マップを事前に作っておきピクセル シェーダーで 1 回だけ読みます。計算は最初の 1 回で済みます。LOD が変わっても法線マップの解像度は同じなので、陰影が変わりません。代償はメモリと高さを編集するたびに更新が必要なことです。

地形では焼く方式が一般的です。編集可能な地形（ブラシで盛る削る）では、変えた範囲だけ計算シェーダーで焼き直します。

## 法線マップを焼く {#bake}

高さマップの全画素に対して計算シェーダーで法線を求めて保存します。

```hlsl
RWTexture2D<float2> g_normal_out : register(u0);   // R16G16_SNORM。x と z だけを保存する

cbuffer BakeConstants : register(b1) {
  uint2 g_size;              // 高さマップのテクセル数
  uint2 _pad;
};

[numthreads(8, 8, 1)]
void BakeNormalCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_size)) return;                // 足した: 8 の倍数でないサイズの端

  int2 p = int2(id.xy);
  int2 max_p = int2(g_size) - 1;
  // 端の画素は、外側を端の値で埋める（clamp）。境界で法線が傾くのを防ぐ
  float hl = g_height[clamp(p + int2(-1, 0), 0, max_p)] * g_height_scale;
  float hr = g_height[clamp(p + int2( 1, 0), 0, max_p)] * g_height_scale;
  float hd = g_height[clamp(p + int2(0, -1), 0, max_p)] * g_height_scale;
  float hu = g_height[clamp(p + int2(0,  1), 0, max_p)] * g_height_scale;

  float3 n = normalize(float3(hl - hr, 2.0 * g_texel_world, hd - hu));
  // 地形の法線は常に上向き（y > 0）。y は読むときに sqrt(1 - x² - z²) で復元する
  g_normal_out[id.xy] = n.xz;
}
```

`g_height[...]` はサンプラーを使わない直接の読み出しで、補間されません。計算の中心は画素の中心なので、これで正確です。

地形タイルをまたぐ継ぎ目では隣のタイルの端の高さを読めないと継ぎ目に筋が出ます。隣のタイルの 1 画素分を余白として一緒に持つかタイルの境界を含めた範囲で焼きます（[Chunks](chunks.md) 参照）。

### 保存する形式

`x` と `z` だけを持てば法線の長さが 1 であることから、`y = sqrt(1 − x² − z²)` で戻せます。2 チャンネルで済むので 3 チャンネルの 2/3 のメモリです。形式ごとのメモリは 4096 × 4096 の場合、次のとおりです。

- `R8G8_SNORM`: 1 画素 2 バイトで、32 MiB です。8 ビットなのでなだらかな斜面でバンディングが見えます。
- `R16G16_SNORM`: 1 画素 4 バイトで、64 MiB です。ほぼ問題ありません。
- `BC5_SNORM`: 圧縮（4:1）で 1 画素 1 バイト、16 MiB です。2 チャンネルを独立に圧縮するので、法線に向いています。

## 精度とバンディング {#precision}

高さマップが 8 ビットだと高さは 256 段階です。高さの範囲が 1000 m なら 1 段の差が約 3.9 m になります。間隔 10 m の画素で斜面の傾きが 5 %（10 m で 0.5 m 上がる）の場所を考えます。高さは約 8 画素ごとに 3.9 m ずつ跳ねて、その間は平らです。平らな所の法線は真上で段の角では傾きが `3.9 / 20 ≒ 0.2` と急に大きくなります。8 画素ごとの縞模様の陰影になります。

対処は 4 つあります。

1. 高さを 16 ビットにします。根本的な解決です。`R16_UNORM` で 65536 段階になり同じ 1000 m でも 1 段が約 0.015 m です（[Heightmap LOD (Mips)](../lod/height-mip.md)）。
2. 高さにノイズ（ディザ）を足します。8 ビットのまま縞をぼかせます。
3. 高さを補間してから差分を取ります。階段の角が少しなだらかになります。
4. 法線マップの解像度を高さより低くします。平均化で階段がならされます。

## 法線マップのミップマップ {#mip}

法線マップをそのまま縮小すると、問題が起きます。単位ベクトルの平均は向きがそろっていないと長さが 1 より短くなるからです。

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="4 つの法線を平均すると、そろっているときは長さ 1、ばらばらのときは短くなる"><defs><marker id="tnB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">平均した法線の長さが、ごつごつ具合を表す</text>
<rect x="20" y="40" width="330" height="170" rx="10" fill="rgba(148,163,184,0.12)" stroke="#94a3b8"/><rect x="370" y="40" width="330" height="170" rx="10" fill="rgba(148,163,184,0.12)" stroke="#94a3b8"/>
<text x="185" y="62" text-anchor="middle" style="font-size:13px;font-weight:600">平らな場所</text><text x="535" y="62" text-anchor="middle" style="font-size:13px;font-weight:600">ごつごつした場所</text>
<g stroke="#4c8bf5" stroke-width="2.5" marker-end="url(#tnB)"><line x1="120" y1="180" x2="120" y2="110"/><line x1="150" y1="180" x2="150" y2="110"/><line x1="180" y1="180" x2="180" y2="110"/><line x1="210" y1="180" x2="210" y2="110"/></g>
<line x1="165" y1="190" x2="165" y2="100" stroke="#e5484d" stroke-width="3.5" marker-end="url(#tnB)"/><text x="260" y="140" style="font-size:12px">平均の長さ ≒ 1.0</text>
<g stroke="#4c8bf5" stroke-width="2.5" marker-end="url(#tnB)"><line x1="450" y1="180" x2="410" y2="118"/><line x1="480" y1="180" x2="470" y2="108"/><line x1="510" y1="180" x2="560" y2="120"/><line x1="540" y1="180" x2="500" y2="112"/></g>
<line x1="490" y1="190" x2="490" y2="150" stroke="#e5484d" stroke-width="3.5" marker-end="url(#tnB)"/><text x="590" y="150" style="font-size:12px">平均の長さ ≒ 0.5</text>
<text x="360" y="224" text-anchor="middle" style="font-size:12px">短いほど、ミップの 1 画素の中で向きがばらついている（＝粗い面）</text></svg>

平均が短いことはミップの 1 画素の中で法線の向きがばらついていることを意味します。この長さを使って遠くの岩場のスペキュラーをちらつきなく「つや消し」に近づけるのが Toksvig の方法（2005）です。ミップを作るときは平均したベクトルを正規化せず長さをそのまま持っておきます。

```hlsl
Texture2D<float4> g_normal_mip_src : register(t1);       // 1 つ上のミップ（正規化しない法線 xyz）
RWTexture2D<float4> g_normal_mip_dst : register(u1);     // R16G16B16A16_FLOAT

[numthreads(8, 8, 1)]
void NormalMipCS(uint3 id : SV_DispatchThreadID) {
  // 2×2 の法線を、正規化せずに平均する。長さが 1 より短くなるのが目的
  uint2 s = id.xy * 2;
  float3 sum = g_normal_mip_src[s].xyz + g_normal_mip_src[s + uint2(1, 0)].xyz
             + g_normal_mip_src[s + uint2(0, 1)].xyz + g_normal_mip_src[s + uint2(1, 1)].xyz;
  g_normal_mip_dst[id.xy] = float4(sum * 0.25, 0);
}

// Toksvig の補正: 平均の長さ ‖N‖ が短いほど、スペキュラーの鋭さ（指数）を弱める。
// ft = ‖N‖ / (‖N‖ + s (1 − ‖N‖))、補正後の指数 = ft × s（s は元の指数）
float ToksvigSpecularPower(float3 averaged_normal, float specular_power) {
  float len = length(averaged_normal);
  float ft = len / (len + specular_power * (1.0 - len));
  return ft * specular_power;
}
```

`len` が 1 に近ければ `ft` も 1 に近くて、指数はほぼ変わりません。`len` が 0.5 で元の指数が 64 なら `ft = 0.5 / (0.5 + 64 × 0.5) ≒ 0.015` で、指数は約 1 になります。ほぼ鏡面ではなく広いハイライトになります。実装は自分のライティング モデルの粗さの定義に合わせて、指数を粗さに置き換えます。この式は記憶から書いたもので、原論文は未読です。

## 実行時に使う {#runtime}

法線マップを読んで y を復元して、ライティングに使います。

```hlsl
Texture2D<float2> g_normal_map : register(t2);   // R16G16_SNORM（x, z）

float3 LoadTerrainNormal(float2 uv) {
  float2 xz = g_normal_map.Sample(g_linear_clamp, uv);
  // 補間で長さが少しずれても、y の根号が負にならないようにする（足した）
  float y = sqrt(saturate(1.0 - dot(xz, xz)));
  return float3(xz.x, y, xz.y);
}

float4 TerrainPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 n = LoadTerrainNormal(uv);
  float3 light_dir = normalize(float3(0.4, 0.8, 0.3));   // 太陽の向き（光の来る向き）
  float lambert = saturate(dot(n, light_dir));
  // 傾きの余弦（1 = 水平、0 = 垂直）。岩や雪の判定に使える
  float slope_cos = n.y;
  float slope_deg = degrees(acos(saturate(n.y)));
  float rock = smoothstep(35.0, 50.0, slope_deg);        // 35° から岩が見え始め、50° で全面岩
  float3 grass = float3(0.25, 0.45, 0.15);
  float3 stone = float3(0.4, 0.38, 0.35);
  return float4(lerp(grass, stone, rock) * lambert, 1.0);
}
```

傾きは `n.y` から直接分かります。スプラットの重み（[Splat Weights](../texturing/weights.md)）に岩や雪の条件として使えます。ナビゲーションの「歩ける斜面」の判定にも使えます。

## よくあるミス {#mistakes}

??? failure "地形の陰影が急すぎるまたは平らに見える"
    原因は高さと画素の間隔の単位がそろっていないことです。UV の 1 テクセルや 0〜1 の高さをそのまま使うと傾きが 1000 倍近くずれることがあります。高さは `g_height_scale` でメートルに直して、間隔 `g_texel_world` もメートルで渡します。

??? failure "地形の陰影に段々の模様が出る"
    原因は高さマップが 8 ビットで、高さの段差が法線に出ていることです。高さマップを `R16_UNORM` にします。直せないときは高さにディザを足すか法線マップの解像度を下げます。

??? failure "タイルの境目に筋が出る"
    原因はタイルの端の画素が、隣のタイルの高さを知らずに法線を作っていることです。端の画素を clamp すると、そこだけ傾きが半分になります。隣のタイルの 1 画素を余白として持って焼きます。

??? failure "遠くの岩場でハイライトがちらつく"
    原因は法線マップのミップで平均を正規化して、ごつごつ具合の情報を捨てていることです。正規化前の長さを持っておいて、Toksvig の補正で粗さを上げます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 法線は `normalize(h_左 − h_右, 2 s, h_下 − h_上)` です。高さと `s` はメートルにそろえます。
    - [x] 地形では法線マップに焼いて、`x` と `z` だけを保存します。`y` は復元します。
    - [x] 高さは 16 ビットにします。8 ビットだと縞が出ます。
    - [x] ミップでは法線を正規化せずに平均して、長さを粗さの補正に使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。数式は導出して HLSL は `fxc`（`cs_5_0` と `ps_5_0`）でコンパイルして確かめました。GPU で実行はしていません。Toksvig の式は記憶から書いたものです。

- Mikkelsen, "Bump Mapping Unparametrized Surfaces on the GPU", Journal of Graphics, GPU, and Game Tools, Vol. 15, No. 1, 2010（高さの微分から法線を作る）
- Toksvig, "Mipmapping Normal Maps", Journal of Graphics Tools, Vol. 10, No. 3, 2005（法線マップのミップと、粗さへの反映）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Microsoft Learn, "DXGI_FORMAT"（`R16G16_SNORM`、`BC5_SNORM` などの形式）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Grid Mesh](grid-mesh.md)
- [Chunks](chunks.md)
