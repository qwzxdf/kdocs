---
title: Using the Sky for Lighting
tags:
  - 描画
---

# Using the Sky for Lighting

昼の日陰が真っ黒にならないのは、青い空が全体を照らしているからです。太陽だけを光源にすると影の中は何も見えなくなります。空は「見える背景」であると同時にシーン全体を包む大きな光源です。ただし空の光は全方向からの光を法線ごとに足し合わせる積分になります。画素ごとに毎回積分すると重すぎるので、あらかじめ少数の係数に圧縮しておきます。その代表が球面調和関数（SH）です。このページでは半球ライトという最小の方法から始めて、キューブマップを 9 係数の SH に投影する計算シェーダー、係数から法線ごとの環境光を求める式、鏡面の環境マップ、空が変わったときの更新までを HLSL と数字で説明します。

!!! tip "ポイント"
    - 空の拡散の光は法線ごとの放射照度 E(n) で表せる。毎画素の積分は重いので SH9（9 係数 × RGB）に圧縮して、画素シェーダーでは式を 1 つ評価するだけにする。
    - 半球ライト（上は空の色、下は地面の色）は最も軽い。ただし法線が真横を向く面では厳密な値より約 15 % 暗くなる。
    - SH9 は滑らかな空なら誤差が 1 % 前後に収まる。太陽のような強い点光源を入れると、背面が明るくなったり負の値が出たりする。太陽は環境マップに入れず平行光源として別に足す。
    - キューブマップの 1 画素の立体角は、面の端ほど小さい。中心を 1 とすると角では約 0.19 になる。立体角を掛けずに足すと係数がずれる。
    - 拡散は SH、鏡面は粗さごとにぼかしたミップつきのキューブマップで引く。空が変わったら SH は毎フレーム、鏡面は数フレームに分けて更新する。

!!! info "このページを読む前に"
    - [Sky Models](index.md)（このセクション全体の地図と読む順番）
    - [Spherical Harmonics (SH)](../../gi/theory/spherical-harmonics.md)（SH の基底と、球面関数の展開。このページは放射照度に絞って使う）

## 読んだ資料 {#sources}

- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）。4 ページ全部を読みました。式 (3) の基底、(10) の投影、(12)(13) の放射照度の式と定数 c1〜c5 は、この論文の値です。
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）。第 7 節の性能の途中まで読みました。空の LUT の更新の話に使います。表 2 の詳細と結論は読んでいません。
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0"（SIGGRAPH 2014）。太陽と EV の節だけを読みました。このページでは太陽を別に足す話の裏づけに使います。
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）は、読んでいません。鏡面の事前積分は [Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md) に任せて、このページでは名前だけ出します。

数字はこのページの HLSL を `fxc`（`cs_5_0` と `ps_5_0`）でコンパイルして確かめ、C++ の実験を MSVC で実行して出したものです。空の色や地面の反射率は「一例」で、実際のゲームの値ではありません。

## 空は何を照らすか {#what}

空が地上を照らす光は 3 つに分けて考えると整理できます。太陽の直接光は 1 方向からの強い光で、影を作ります。空の光は全方向からくる弱い光で、影の中まで届きます。地面からの反射光は照らされた地面が下から物を照らす光です。

昼の日陰が青っぽく見えるのは、青い空の光が当たっているからです。このページが扱うのは後ろの 2 つ空と地面からくる「全方向の光」です。太陽は直接光として別に扱います。

<svg class="fig flow" viewBox="0 0 660 280" role="img" aria-label="空のライティングの流れ"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">空のライティングの流れ(青: 拡散の環境光、黄: 鏡面と太陽)</text><rect x="10" y="40" width="120" height="54" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="70.0" y="64.0" text-anchor="middle" font-size="11" fill="currentColor">空を描く</text><text x="70.0" y="78.0" text-anchor="middle" font-size="11" fill="currentColor">(大気 LUT)</text><rect x="170" y="40" width="130" height="54" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="235.0" y="64.0" text-anchor="middle" font-size="11" fill="currentColor">小さなキューブマップ</text><text x="235.0" y="78.0" text-anchor="middle" font-size="11" fill="currentColor">32×32×6(太陽なし)</text><rect x="340" y="40" width="130" height="54" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="405.0" y="64.0" text-anchor="middle" font-size="11" fill="currentColor">ProjectFaceCS</text><text x="405.0" y="78.0" text-anchor="middle" font-size="11" fill="currentColor">96 グループの部分和</text><rect x="510" y="40" width="130" height="54" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="575.0" y="64.0" text-anchor="middle" font-size="11" fill="currentColor">SumPartialsCS</text><text x="575.0" y="78.0" text-anchor="middle" font-size="11" fill="currentColor">9 係数(RGB)</text><line x1="130" y1="67" x2="170" y2="67" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="300" y1="67" x2="340" y2="67" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="470" y1="67" x2="510" y2="67" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><rect x="510" y="124" width="130" height="54" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="575.0" y="148.0" text-anchor="middle" font-size="11" fill="currentColor">定数バッファ</text><text x="575.0" y="162.0" text-anchor="middle" font-size="11" fill="currentColor">9 個の float4</text><line x1="575" y1="94" x2="575" y2="124" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><rect x="510" y="208" width="130" height="54" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="575.0" y="232.0" text-anchor="middle" font-size="11" fill="currentColor">画素シェーダー</text><text x="575.0" y="246.0" text-anchor="middle" font-size="11" fill="currentColor">IrradianceFromSH</text><line x1="575" y1="178" x2="575" y2="208" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><rect x="170" y="124" width="130" height="54" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="235.0" y="148.0" text-anchor="middle" font-size="11" fill="currentColor">鏡面用キューブマップ</text><text x="235.0" y="162.0" text-anchor="middle" font-size="11" fill="currentColor">128×128×6 + ミップ</text><line x1="235" y1="94" x2="235" y2="124" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><rect x="170" y="208" width="130" height="54" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="235.0" y="232.0" text-anchor="middle" font-size="11" fill="currentColor">SampleSpecularEnv</text><text x="235.0" y="246.0" text-anchor="middle" font-size="11" fill="currentColor">反射ベクトルで引く</text><line x1="235" y1="178" x2="235" y2="208" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="300" y1="235" x2="510" y2="235" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><rect x="340" y="124" width="130" height="54" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="405.0" y="148.0" text-anchor="middle" font-size="11" fill="currentColor">太陽 = 平行光源</text><text x="405.0" y="162.0" text-anchor="middle" font-size="11" fill="currentColor">(環境マップに入れない)</text><line x1="470" y1="151" x2="510" y2="225" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/></svg>

## 環境光をどう表すか {#represent}

物の表面に届く環境光は法線 n を中心とした半球の上で、あらゆる方向からの放射輝度 L(ω) に n との角度の余弦を掛けて足したものです。これを放射照度 E(n) と呼びます。

`E(n) = ∫ L(ω) · max(0, n·ω) dω`

拡散反射の見た目はアルベドを π で割って、E を掛けたものです。つまり、シェーダーで必要なのは法線 n を入れると E(n) が返る関数です。これを毎画素で積分すると方向のサンプルが数百から数千いります。そこで、この関数を安く近似する方法が 3 つあります。

1. **半球ライト**: n の上下だけで、空の色と地面の色を補間します。係数は 2 色だけです。
2. **SH9**: 空の光を 9 個の係数（RGB で 27 個の数）に圧縮し、法線の式を 1 つ評価します。
3. **ぼかしたキューブマップ**: 余弦で畳み込んだキューブマップを、法線で引きます。表現力は最も高くメモリは最も多くいります。

このページは 1 と 2 を詳しく扱い 3 は鏡面の節で触れます。

## 半球ライト {#hemisphere}

最も簡単で効果が大きい方法です。法線が上を向く面には空の色を下を向く面には地面の色を間は線形に補間します。

```hlsl
// ================= ① 半球ライト =================

// 法線の上下で空の色と地面の色を補間する最小の環境光。
float3 HemisphereAmbient(float3 normal, float3 sky_color, float3 ground_color) {
  float up = normal.y * 0.5 + 0.5;                       // 0（真下）〜 1（真上）
  return lerp(ground_color, sky_color, up);
}
```

`normal.y * 0.5 + 0.5` は法線の y 成分（−1〜1）を補間の重み（0〜1）に直しています。真上を向く面は 1 になって空の色、真横は 0.5 で両者の平均、真下は 0 で地面の色になります。物の上面が空の色、下面が地面の色になるので立体感が出ます。

空の色と地面の色は空のキューブマップから決められます。真上を向く面の放射照度 E(上) を π で割ったものが空の色、真下を向く面の E(下) を π で割ったものが地面の色です。こうして決めると半球ライトは真上と真下では厳密な値と完全に一致します。ずれるのはその間です。このあと C++ で数字を出します。

## SH9 {#sh}

SH は球面上の関数を直交する基底関数の和で表す方法です。基底は次数 l = 0, 1, 2, … と各次数の中の番号 m（−l〜l）で区別します。次数 l までを使うと基底は (l + 1)² 個です。l = 2 までなら 9 個で、これが SH9（3 次の SH）です。球面関数 L の係数は `L_lm = ∫ L(ω) Y_lm(ω) dω` で求めます。

### 基底となぜ 9 個で足りるのか {#basis}

Ramamoorthi と Hanrahan（2001）は、放射照度が環境光 L と余弦のローブ（max(0, cosθ) の関数）の「畳み込み」であることに注目しました。畳み込みを SH で行うと次数ごとに単純な掛け算になります。余弦のローブの係数 Â_l は l = 0 で π、l = 1 で 2π/3、l = 2 で π/4 です。奇数の l ≥ 3 はゼロで、偶数の l ≥ 4 は急に小さくなります。

余弦のローブの二乗の積分（エネルギー）を計算すると、全体を 1 としたとき l = 0 だけで 37.5 %、l ≤ 1 で 87.5 %、l ≤ 2 で 99.2 % になります（このページの計算。`k_l = Â_l · sqrt((2l+1)/4π)` を二乗して足しました）。3 次まででほぼ全部が入るので、9 個の係数で十分、というのが論文の主張です。

基底関数は次の 9 つです（論文の式 3）。順番は 00、1−1、10、11、2−2、2−1、20、21、22 です。

```hlsl
// 実数球面調和の基底（論文の式 3）。順番: 00, 1-1, 10, 11, 2-2, 2-1, 20, 21, 22。
void ShBasis(float3 d, out float basis[9]) {
  basis[0] = 0.282095;
  basis[1] = 0.488603 * d.y;                             // Y_1-1 ∝ y
  basis[2] = 0.488603 * d.z;                             // Y_10 ∝ z
  basis[3] = 0.488603 * d.x;                             // Y_11 ∝ x
  basis[4] = 1.092548 * d.x * d.y;                       // Y_2-2 ∝ xy
  basis[5] = 1.092548 * d.y * d.z;                       // Y_2-1 ∝ yz
  basis[6] = 0.315392 * (3.0 * d.z * d.z - 1.0);         // Y_20
  basis[7] = 1.092548 * d.x * d.z;                       // Y_21 ∝ xz
  basis[8] = 0.546274 * (d.x * d.x - d.y * d.y);         // Y_22
}
```

右側のコメントにある `∝ y` などはその基底が方向のどの成分に比例するかです。l = 1 の 3 つは方向 d の x・y・z そのものに比例します。つまり、「上が明るく下が暗い」という大まかな偏りを表します。l = 2 の 5 つは x と y の積などの 2 次の項で、少し細かい偏りを表します。l = 0 は定数で全体の平均の明るさです。

### キューブマップを SH に投影する {#project}

係数は空のキューブマップの全画素について、`放射輝度 × 基底 × 立体角` を足して求めます（論文の式 10 を離散化したもの）。まず、キューブの面の画素から方向を作る関数を用意します。

```hlsl
// キューブの面 f、面内の座標 (u, v) ∈ [-1, 1] から、方向（正規化前）を作る。D3D のキューブの向きの規約。
float3 CubeDirection(uint face, float2 uv) {
  float3 d;
  if (face == 0) d = float3(1.0, -uv.y, -uv.x);          // +X
  else if (face == 1) d = float3(-1.0, -uv.y, uv.x);     // -X
  else if (face == 2) d = float3(uv.x, 1.0, uv.y);       // +Y
  else if (face == 3) d = float3(uv.x, -1.0, -uv.y);     // -Y
  else if (face == 4) d = float3(uv.x, -uv.y, 1.0);      // +Z
  else d = float3(-uv.x, -uv.y, -1.0);                   // -Z
  return d;
}
```

面の番号 0〜5 は+X、−X、+Y、−Y、+Z、−Z の順です。uv は面の中の画素の位置を [−1, 1] に直したもので、この規約は Direct3D のキューブマップの向きに合わせています。**使うキューブマップの向きの規約が違うならここを合わせます。** 規約が食い違うと SH の上下や左右が反転します。症状は「空の青い側が下から当たる」ように見えることです。

次に、画素 1 つの立体角を求めます。立方体の面を球に投影すると面の端ほど 1 画素が覆う角度が小さくなります。立方体の面は中心から距離 1 の平面で、面の座標 (u, v) の画素は中心から `sqrt(u² + v² + 1)` の距離にあります。1 画素の面積は `(2/N)²`、方向に対して斜めになる分の余弦が `1 / sqrt(u² + v² + 1)`、距離の二乗の分が `1 / (u² + v² + 1)` なので、立体角は次の式になります。

`dΩ = (2/N)² / (u² + v² + 1)^(3/2)`

面の中心では 1、辺の中央（u = 1, v = 0）では `2^(-3/2) = 0.354`、角（u = v = 1）では `3^(-3/2) = 0.192` です。**立体角を掛け忘れると面の端が過大に数えられます。** 全画素の立体角の和が 4π になることは、実験で確かめます。

計算シェーダーでは 1 つのグループ（8 × 8 画素）が、自分の担当する画素の寄与を足し合わせグループごとの部分和を作ります。

```hlsl
groupshared float3 g_reduce[64][9];                      // 8x8 スレッド × 9 係数

[numthreads(8, 8, 1)]
void ProjectFaceCS(uint3 gid : SV_GroupID, uint3 tid : SV_GroupThreadID, uint3 dtid : SV_DispatchThreadID,
                   uint gindex : SV_GroupIndex) {
  uint face = dtid.z;                                    // ディスパッチの z が面の番号（0〜5）
  float2 uv = (dtid.xy + 0.5) / g_face_size * 2.0 - 1.0; // 画素の中心を [-1, 1] に
  float3 d = CubeDirection(face, uv);
  float len2 = dot(d, d);
  d = normalize(d);

  // 1 画素の立体角: (2/N)² / (u² + v² + 1)^(3/2)。立方体の面の端ほど 1 画素が覆う角度が小さい。
  float texel = 2.0 / g_face_size;
  float d_omega = texel * texel / (len2 * sqrt(len2));

  float3 radiance = g_sky_cube.SampleLevel(g_linear_clamp, d, 0).rgb;
  float basis[9];
  ShBasis(d, basis);
  [unroll] for (int i = 0; i < 9; ++i) {
    g_reduce[gindex][i] = radiance * basis[i] * d_omega; // 論文の式 10: L(ω) Y_lm(ω) dω
  }
  GroupMemoryBarrierWithGroupSync();

  // グループ内で足す（二分木の縮約）。64 → 32 → ... → 1。
  [unroll] for (uint stride = 32; stride > 0; stride /= 2) {
    if (gindex < stride) {
      [unroll] for (int j = 0; j < 9; ++j) g_reduce[gindex][j] += g_reduce[gindex + stride][j];
    }
    GroupMemoryBarrierWithGroupSync();
  }

  if (gindex == 0) {
    uint group_index = face * g_groups_per_face + gid.y * (g_face_size / 8) + gid.x;
    [unroll] for (int k = 0; k < 9; ++k) g_partial[group_index * 9 + k] = float4(g_reduce[0][k], 0);
  }
}
```

`g_reduce` は 64 スレッド × 9 係数の `groupshared` 配列です。各スレッドが自分の画素の `放射輝度 × 基底 × dΩ` を 9 個書き込みます。その後は二分木の縮約です。stride を 32、16、8、4、2、1 と半分にしながら前半のスレッドが、stride だけ離れたスレッドの値を足します。`GroupMemoryBarrierWithGroupSync()` を各段階の後に置いて書き込みの完了を待ちます。これを省くと足す前の値を読むスレッドが出て、結果が実行のたびに変わります。

最後に、グループの代表（`gindex == 0`）が部分和を `g_partial` に書きます。面ごとグループごとに 9 個の `float4` の場所を決めます（w は使いません）。

```hlsl
// ================= ③ 部分和を足す =================

RWStructuredBuffer<float4> g_sh_out : register(u1);     // 9 係数（rgb）

[numthreads(9, 1, 1)]                                    // 1 スレッド = 1 係数
void SumPartialsCS(uint3 tid : SV_GroupThreadID) {
  uint count = g_groups_per_face * 6;                    // 全グループ数
  float3 sum = 0;
  for (uint g = 0; g < count; ++g) sum += g_partial[g * 9 + tid.x].rgb;
  g_sh_out[tid.x] = float4(sum, 0);                      // 放射輝度 L の SH 係数 L_lm
}
```

2 つ目の計算シェーダーは 1 グループ 9 スレッドで、スレッドが 1 つの係数を担当し、全グループの部分和を足します。32 × 32 の面ならグループは面ごとに 16 個、全体で 96 個です。部分和のバッファは 96 × 9 個の `float4` で、約 13.5 KB です。足すグループ数が 96 なので、1 スレッドのループは 96 回で済みます。

### 放射照度を評価する {#irradiance}

係数 `L_lm` を持っていれば法線 n の放射照度は、論文の式 13 の展開形で求まります。

```hlsl
// ================= ④ 放射照度 =================

// 論文の式 13（展開形）。L_lm を sh[0..8] に持つ（順番は ShBasis と同じ）。
// E(n) = c1 L22 (x²-y²) + c3 L20 z² + c4 L00 - c5 L20 + 2c1 (L2-2 xy + L21 xz + L2-1 yz) + 2c2 (L11 x + L1-1 y + L10 z)
float3 IrradianceFromSH(float3 sh[9], float3 n) {
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  return c1 * sh[8] * (n.x * n.x - n.y * n.y)            // L22
       + c3 * sh[6] * n.z * n.z                          // L20 の z² 項
       + c4 * sh[0]                                       // L00（定数項）
       - c5 * sh[6]                                       // L20 の定数項
       + 2.0 * c1 * (sh[4] * n.x * n.y + sh[7] * n.x * n.z + sh[5] * n.y * n.z)   // L2-2, L21, L2-1
       + 2.0 * c2 * (sh[3] * n.x + sh[1] * n.y + sh[2] * n.z);                    // L11, L1-1, L10
}
```

c1〜c5 は `Â_l` と基底の係数を掛け合わせた定数です。このページの C++ で `c1 = Â2 · 0.546274`、`c2 = Â1 · 0.488603 / 2`、`c3 = Â2 · 3 · 0.315392`、`c4 = Â0 · 0.282095`、`c5 = Â2 · 0.315392` を計算し論文の 6 桁の値と一致することを確かめました（c4 だけ最後の桁が 1 違いますが、丸めの差です）。式の中身は l = 2 の項（`c1`、`c3`、`c5` の行）、l = 0 の項（`c4`）、l = 1 の項（`c2` の行）の順に並んでいます。

関数の引数 `sh[9]` は `float3` の配列で、RGB を同時に計算します。**戻り値が負になることがあります。** SH で空を近似すると、暗い側の法線でわずかに負になる場合があるため、画素シェーダーでは `max(…, 0)` で切ります。

論文は同じ計算を行列の形でも書いています（式 11・12）。法線を `(x, y, z, 1)` の 4 次元ベクトルにして、4 × 4 の対称行列 M で `nᵗ M n` を求める形です。

```hlsl
// 論文の式 11・12: E(n) = nᵗ M n（M は 4x4 対称行列、色ごと）。係数から M を組み立てておけば、評価は行列とベクトルの積だけ。
float4x4 IrradianceMatrix(float3 sh[9], int channel) {
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  float L00 = sh[0][channel], L1m1 = sh[1][channel], L10 = sh[2][channel], L11 = sh[3][channel];
  float L2m2 = sh[4][channel], L2m1 = sh[5][channel], L20 = sh[6][channel], L21 = sh[7][channel], L22 = sh[8][channel];
  return float4x4(c1 * L22,  c1 * L2m2, c1 * L21,  c2 * L11,
                  c1 * L2m2, -c1 * L22, c1 * L2m1, c2 * L1m1,
                  c1 * L21,  c1 * L2m1, c3 * L20,  c2 * L10,
                  c2 * L11,  c2 * L1m1, c2 * L10,  c4 * L00 - c5 * L20);
}

float EvaluateMatrix(float4x4 m, float3 n) {
  float4 nt = float4(n, 1.0);
  return dot(nt, mul(m, nt));                            // nᵗ M n
}
```

行列を色（RGB）ごとに 1 個ずつあらかじめ組み立てておけば、画素シェーダーは行列とベクトルの積だけを評価します。利点は式が単純なことです。欠点は `float4x4` を 3 個（48 個の float）送るので、9 個の `float4`（36 個の float）で済む展開形より定数が増えることです。結果はどちらも同じです。

### 画素シェーダーでの使い方 {#use}

SH の環境光と太陽の直接光を画素シェーダーで足します。

```hlsl
// ================= 画素シェーダー（確認用）=================

cbuffer ShCB : register(b2) {
  float4 g_sh[9];
  float3 g_sun_dir;
  float g_pad4;
  float3 g_sun_illuminance;                              // 太陽の照度（平行光源として別に足す）
  float g_pad5;
};

float4 SkyLightPS(float4 pos : SV_Position, float3 normal : NORMAL, float3 albedo_in : TEXCOORD0) : SV_Target {
  float3 n = normalize(normal);
  float3 sh[9];
  [unroll] for (int i = 0; i < 9; ++i) sh[i] = g_sh[i].rgb;

  float3 ambient = max(IrradianceFromSH(sh, n), 0.0);              // 空の拡散の環境光
  float3 sun = g_sun_illuminance * saturate(dot(n, g_sun_dir));    // 太陽は平行光源として別に足す
  float4x4 m = IrradianceMatrix(sh, 1);                             // 行列形式の確認（緑）
  float check = EvaluateMatrix(m, n);                               // 展開形と同じ値になるはず
  float3 spec = SampleSpecularEnv(reflect(-n, n), 0.5);             // 呼び出しの確認（意味は薄い）
  float3 result = albedo_in / 3.14159265 * (ambient + sun);
  return float4(result + spec * 0.0 + check * 0.0, 1.0);
}
```

太陽は `g_sun_illuminance * saturate(dot(n, g_sun_dir))` で平行光源として別に足します。**太陽を空のキューブマップに含めて SH にすると、二重に数えるうえに SH が大きく壊れます**（次の節で数字を出します）。最後の行の `albedo_in / 3.14159265` はランバート反射の `albedo / π` です。

## 数字で確かめる {#experiment}

HLSL と同じ基底、同じキューブの面の規約で C++ に同じ計算を書き厳密な値と比べました。最初に準備の部分です。空の色を決める関数 `Sky` と基底 `Basis` を置きます。

```cpp
struct V3 { double x, y, z; };
static V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
static V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
static double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static V3 Norm(V3 a) { double l = std::sqrt(Dot(a, a)); return {a.x / l, a.y / l, a.z / l}; }
constexpr double kPi = std::numbers::pi;

// 論文の式 3 の基底。順番は HLSL の ShBasis と同じ。
static std::array<double, 9> Basis(V3 d) {
  return {0.282095, 0.488603 * d.y, 0.488603 * d.z, 0.488603 * d.x, 1.092548 * d.x * d.y,
          1.092548 * d.y * d.z, 0.315392 * (3 * d.z * d.z - 1), 1.092548 * d.x * d.z,
          0.546274 * (d.x * d.x - d.y * d.y)};
}

// 空の放射輝度（相対値）。y が上。上は青、地平線は明るく白っぽい下は暗い地面。
static V3 Sky(V3 d) {
  if (d.y >= 0) {
    double t = std::pow(1.0 - d.y, 3.0);                 // 地平線に近いほど 1
    return V3{0.20, 0.40, 0.90} * (1.0 - t) + V3{0.80, 0.85, 0.95} * t;
  }
  return {0.12, 0.10, 0.08};                             // 地面の反射（一例）
}

using Sh = std::array<V3, 9>;
```

`Sky` は上が青、地平線が明るい白っぽい色、下が暗い地面、という単純な空です（値は一例）。`pow(1.0 - d.y, 3.0)` で地平線に近いほど白くなります。次に、基準の値を出す 2 つの投影です。1 つは球面を (θ, φ) の細かい格子で直接積分するもの（基準）、もう 1 つは HLSL と同じ手順で、キューブの面から投影するものです。

```cpp
// 球面を (θ, φ) の格子で積分して、SH9 の係数を求める（基準値）。
static Sh ProjectGrid(const std::function<V3(V3)>& f, int n_theta = 400) {
  Sh sh{};  // 9 係数（各 RGB）。0 で初期化
  int n_phi = n_theta * 2;                               // φ は θ の 2 倍の分割（格子の縦横比をそろえる）
  double dt = kPi / n_theta, dp = 2 * kPi / n_phi;       // 1 マスの θ 幅・φ 幅 [rad]
  for (int i = 0; i < n_theta; ++i) {
    double th = (i + 0.5) * dt;                          // マスの中心の θ（真上 = 0）
    for (int j = 0; j < n_phi; ++j) {
      double ph = (j + 0.5) * dp;                        // マスの中心の φ
      V3 d{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};   // y が上
      double w = std::sin(th) * dt * dp;                 // マスの立体角 = sin θ dθ dφ [sr]
      auto b = Basis(d);                                 // 9 個の基底の値
      V3 L = f(d);                                       // この方向の放射輝度
      for (int k = 0; k < 9; ++k) sh[k] = sh[k] + L * (b[k] * w);   // 式 10: L · Y_lm · dΩ を足す
    }
  }
  return sh;
}

// HLSL の CubeDirection と同じ規約。
static V3 CubeDir(int face, double u, double v) {
  switch (face) {
    case 0: return {1, -v, -u};                          // +X
    case 1: return {-1, -v, u};                          // -X
    case 2: return {u, 1, v};                            // +Y
    case 3: return {u, -1, -v};                          // -Y
    case 4: return {u, -v, 1};                           // +Z
    default: return {-u, -v, -1};                        // -Z
  }
}

// キューブマップの N x N の面から投影する（HLSL の ProjectFaceCS と同じ計算）。
static Sh ProjectCube(const std::function<V3(V3)>& f, int n, double* total_omega = nullptr) {
  Sh sh{};                                               // 9 係数の合計
  double total = 0;                                      // 立体角の総和（4π になるはず）
  for (int face = 0; face < 6; ++face)
    for (int y = 0; y < n; ++y)
      for (int x = 0; x < n; ++x) {
        double u = (x + 0.5) / n * 2 - 1, v = (y + 0.5) / n * 2 - 1;   // 画素の中心を [-1, 1] に
        V3 d = CubeDir(face, u, v);                      // 正規化前の方向
        double len2 = Dot(d, d);                         // u² + v² + 1
        double texel = 2.0 / n;                          // 面の幅 2 を n 分割した 1 画素の幅
        double d_omega = texel * texel / (len2 * std::sqrt(len2));   // 立体角 = (2/N)² / (u²+v²+1)^(3/2)
        d = Norm(d);                                     // 基底に入れる方向は単位ベクトル
        total += d_omega;                                // 検算用の総和
        auto b = Basis(d);
        V3 L = f(d);                                     // 空の色（キューブマップの代わりに関数で与える）
        for (int k = 0; k < 9; ++k) sh[k] = sh[k] + L * (b[k] * d_omega);   // HLSL の g_reduce に入れる値と同じ
      }
  if (total_omega) *total_omega = total;                 // 呼び出し側が総和を見たいときだけ返す
  return sh;
}
```

`ProjectGrid` はθ を 400 分割、φ を 800 分割して `sin θ dθ dφ` を立体角にします。`ProjectCube` は HLSL の `CubeDirection` と立体角の式をそのまま使っています。次に、放射照度の評価です。

```cpp
static const double c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;   // 定数: 論文の値。Â_l と基底の係数の積（[1] で確かめる）

// 論文の式 13（HLSL の IrradianceFromSH）。
static V3 IrrSh(const Sh& s, V3 n) {
  V3 r = s[8] * (c1 * (n.x * n.x - n.y * n.y));          // L22 の項
  r = r + s[6] * (c3 * n.z * n.z) + s[0] * c4 + s[6] * (-c5);   // L20 の z² 項 + 定数項 L00 - L20 の定数項
  r = r + (s[4] * (n.x * n.y) + s[7] * (n.x * n.z) + s[5] * (n.y * n.z)) * (2 * c1);   // l = 2 の交差項
  r = r + (s[3] * n.x + s[1] * n.y + s[2] * n.z) * (2 * c2);   // l = 1 の項
  return r;
}

// 厳密な放射照度 E(n) = ∫ L(ω) max(0, n·ω) dω を、格子で直接積分する。
static V3 IrrExact(const std::function<V3(V3)>& f, V3 n, int n_theta = 400) {
  V3 e{0, 0, 0};                                         // 放射照度の合計
  int n_phi = n_theta * 2;                               // ProjectGrid と同じ格子
  double dt = kPi / n_theta, dp = 2 * kPi / n_phi;
  for (int i = 0; i < n_theta; ++i) {
    double th = (i + 0.5) * dt;
    for (int j = 0; j < n_phi; ++j) {
      double ph = (j + 0.5) * dp;
      V3 d{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};   // 光の来る方向
      double c = std::max(0.0, Dot(n, d));               // 余弦。裏側の光は 0
      if (c > 0) e = e + f(d) * (c * std::sin(th) * dt * dp);   // L · cos · dΩ
    }
  }
  return e;                                              // 単位は L と同じ × sr
}

static V3 Hemisphere(V3 n, V3 sky, V3 ground) {
  double up = n.y * 0.5 + 0.5;                           // HLSL の HemisphereAmbient と同じ重み
  return ground * (1 - up) + sky * up;                   // 下の色と上の色の線形補間
}
```

`IrrSh` は HLSL の `IrradianceFromSH` と同じです。`IrrExact` は `max(0, n·ω)` をそのまま格子で積分する厳密な値です。`Hemisphere` は半球ライトです。これらを `main` で呼んで比べます。

```cpp
int main() {
  // ---- 1. 定数 c1〜c5 は Â_l と基底の係数から出る ----
  const double A0 = kPi, A1 = 2 * kPi / 3, A2 = kPi / 4;  // A0 = π, A1 = 2π/3, A2 = π/4。余弦ローブの係数 Â_l（論文）
  std::printf("[1] constants (from A_l)   paper\n");
  std::printf("c1 = A2*0.546274      = %.6f   %.6f\n", A2 * 0.546274, c1);  // c1 = Â2 × 基底 22 の係数。右の値が論文の値
  std::printf("c2 = A1*0.488603/2    = %.6f   %.6f\n", A1 * 0.488603 / 2, c2);  // c2 は Â1 × 基底 1 の係数の半分（式の側に 2 が付く）
  std::printf("c3 = A2*3*0.315392    = %.6f   %.6f\n", A2 * 3 * 0.315392, c3);  // c3 は Â2 × 3 × 基底 20 の係数（z² の係数）
  std::printf("c4 = A0*0.282095      = %.6f   %.6f\n", A0 * 0.282095, c4);  // c4 は Â0 × 基底 00 の係数。平均の明るさ
  std::printf("c5 = A2*0.315392      = %.6f   %.6f\n", A2 * 0.315392, c5);  // c5 は Â2 × 基底 20 の係数（定数項から引く）
  std::printf("A0 : A1 : A2 = 1 : %.4f : %.4f\n\n", A1 / A0, A2 / A0);  // Â の比。l が上がるほど小さい

  // ---- 2. キューブマップの面の大きさと立体角・精度 ----
  std::printf("[2] cube face size vs L00 and max coefficient error (reference: 400x800 grid)\n");
  Sh ref = ProjectGrid(Sky);  // 基準: 400x800 の格子で積分した係数
  std::printf("grid L00 (rgb) = %.5f %.5f %.5f\n", ref[0].x, ref[0].y, ref[0].z);
  for (int n : {4, 8, 16, 32, 64}) {  // キューブの 1 面の画素数を変える
    double total;
    Sh s = ProjectCube(Sky, n, &total);  // HLSL と同じ手順で投影し、立体角の総和も受け取る
    double max_err = 0;  // 9 係数の RGB のうち、基準との差の最大
    for (int k = 0; k < 9; ++k)
      max_err = std::max({max_err, std::fabs(s[k].x - ref[k].x), std::fabs(s[k].y - ref[k].y), std::fabs(s[k].z - ref[k].z)});
    std::printf("N=%2d  sum(domega)=%.5f (4pi=%.5f)  max|dL_lm|=%.5f\n", n, total, 4 * kPi, max_err);  // 総和が 4π に近づくか。係数の誤差が N とともに減るか
  }
  std::printf("\n");

  // ---- 3. SH9 の放射照度 vs 厳密 ----
  Sh sh = ProjectCube(Sky, 32);  // 以降は N = 32 の投影を使う（本番の設定の想定）
  std::printf("[3] irradiance: SH9 vs exact (sky, N=32)\n");
  struct N { const char* name; V3 n; } normals[] = {  // 確かめる 6 つの法線（上・下・横 2 つ・斜め 2 つ）
      {"up    ", {0, 1, 0}}, {"down  ", {0, -1, 0}}, {"+x    ", {1, 0, 0}},
      {"-z    ", {0, 0, -1}}, {"45deg ", Norm({1, 1, 0})}, {"-45deg", Norm({1, -1, 0})}};
  double sum_rel = 0, worst = 0;
  int cnt = 0;
  for (auto& q : normals) {
    V3 e = IrrExact(Sky, q.n), a = IrrSh(sh, q.n);
    double rel = std::fabs(a.y - e.y) / e.y;             // 緑で比べる
    std::printf("%s exact G=%.4f  SH9 G=%.4f  rel.err=%.2f%%\n", q.name, e.y, a.y, rel * 100);
  }
  // 法線をたくさん取って、平均と最悪を求める（基準はその色の最大値）
  double emax = 0;  // 誤差の基準にする、放射照度の最大値
  for (int i = 0; i < 40; ++i) for (int j = 0; j < 80; ++j) {  // 40 x 80 = 3200 個の法線で全体を見る
    double th = (i + 0.5) / 40 * kPi, ph = (j + 0.5) / 80 * 2 * kPi;
    V3 n{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
    emax = std::max(emax, IrrExact(Sky, n, 100).y);  // 最大値を探すだけの 1 周目（格子は粗く 100）
  }
  for (int i = 0; i < 40; ++i) for (int j = 0; j < 80; ++j) {
    double th = (i + 0.5) / 40 * kPi, ph = (j + 0.5) / 80 * 2 * kPi;
    V3 n{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
    double e = IrrExact(Sky, n, 100).y, a = IrrSh(sh, n).y;
    double rel = std::fabs(a - e) / emax;  // 誤差を最大値で割る（小さい E で相対誤差が大きく出るのを避ける）
    sum_rel += rel; worst = std::max(worst, rel); ++cnt;  // 平均と最悪を更新
  }
  std::printf("over %d normals: mean err = %.3f%% of max, worst = %.3f%% of max\n\n", cnt, sum_rel / cnt * 100, worst * 100);

  // ---- 4. 半球ライト vs 厳密 ----
  std::printf("[4] hemisphere light (sky color = zenith, ground color = ground) vs exact\n");
  V3 sky_c = IrrExact(Sky, {0, 1, 0}) * (1.0 / kPi), ground_c = IrrExact(Sky, {0, -1, 0}) * (1.0 / kPi);  // 半球ライトの色。真上・真下の E/π と一致させる
  std::printf("sky_c (E_up/pi) G=%.4f  ground_c (E_down/pi) G=%.4f\n", sky_c.y, ground_c.y);
  for (auto& q : normals) {
    V3 e = IrrExact(Sky, q.n) * (1.0 / kPi);  // 厳密な E/π
    V3 h = Hemisphere(q.n, sky_c, ground_c);  // 半球ライト
    V3 s = IrrSh(sh, q.n) * (1.0 / kPi);  // SH9 の E/π
    std::printf("%s exact/pi G=%.4f  SH9 G=%.4f  hemi G=%.4f\n", q.name, e.y, s.y, h.y);
  }
  std::printf("\n");

  // ---- 5. 太陽を入れると SH が壊れる ----
  std::printf("[5] adding the sun as a delta light (E_sun = 1.0 on a surface facing it)\n");
  V3 sun_dir = Norm({0.3, 0.8, 0.5});  // 太陽の向き（一例）
  auto bs = Basis(sun_dir);  // 太陽方向の基底の値
  Sh sun{};  // 太陽だけを SH にしたもの
  for (int k = 0; k < 9; ++k) sun[k] = V3{1, 1, 1} * bs[k];  // 平行光源の L_lm = E * Y_lm(s)
  for (auto& q : {std::make_pair("n = s    ", sun_dir), std::make_pair("n = -s   ", sun_dir * -1.0),
                  std::make_pair("n perp s", Norm(V3{-0.8, 0.3, 0}))}) {
    double truth = std::max(0.0, Dot(q.second, sun_dir));  // 厳密: 太陽から見て表側だけ明るい
    double est = IrrSh(sun, q.second).y;  // SH9 で近似した値
    std::printf("%s true E = %.4f   SH9 E = %.4f\n", q.first, truth, est);
  }
  // 太陽の SH で負の値が出る法線の割合
  int neg = 0, tot = 0;  // 負の値が出た法線の数と、全法線の数
  for (int i = 0; i < 90; ++i) for (int j = 0; j < 180; ++j) {
    double th = (i + 0.5) / 90 * kPi, ph = (j + 0.5) / 180 * 2 * kPi;
    V3 n{std::sin(th) * std::cos(ph), std::cos(th), std::sin(th) * std::sin(ph)};
    if (IrrSh(sun, n).y < 0) ++neg;  // 1 つでも負なら数える
    ++tot;
  }
  std::printf("normals with negative SH9 irradiance: %.1f%%\n", 100.0 * neg / tot);

  // ---- 6. 法線を上から下へ回したときの曲線（図用）----
  std::printf("\n[6] normal rotated from up (0 deg) to down (180 deg) in the x-y plane, G channel, value = E/pi\n");
  for (int deg = 0; deg <= 180; deg += 15) {  // 15° ごとに回す
    double a = deg * kPi / 180;  // 回転角 [rad]
    V3 n{std::sin(a), std::cos(a), 0};  // x-y 平面で、真上から真下へ回す法線
    std::printf("%3d exact=%.4f sh9=%.4f hemi=%.4f\n", deg, IrrExact(Sky, n).y / kPi, IrrSh(sh, n).y / kPi, Hemisphere(n, sky_c, ground_c).y);
  }

  // ---- 7. 太陽の SH9 を太陽の向きから離していったときの曲線（図用）----
  std::printf("\n[7] sun SH9 vs true, normal rotated away from the sun direction\n");
  V3 ref_axis = Norm({-0.8, 0.3, 0});                    // 太陽と直交する向き（[5] と同じ）
  for (int deg = 0; deg <= 180; deg += 15) {
    double a = deg * kPi / 180;
    V3 n = Norm(sun_dir * std::cos(a) + ref_axis * std::sin(a));  // 太陽の向きから、直交する向きへ回していく
    std::printf("%3d true=%.4f sh9=%.4f\n", deg, std::max(0.0, Dot(n, sun_dir)), IrrSh(sun, n).y);
  }

  // ---- 8. キューブの面の端での 1 画素の立体角（中心を 1 として）----
  std::printf("\n[8] solid angle of a cube texel relative to the face center: corner = %.4f, edge middle = %.4f\n",
              std::pow(3.0, -1.5), std::pow(2.0, -1.5));
  return 0;
}
```

```text title="実行結果"
[1] constants (from A_l)   paper
c1 = A2*0.546274      = 0.429043   0.429043
c2 = A1*0.488603/2    = 0.511664   0.511664
c3 = A2*3*0.315392    = 0.743125   0.743125
c4 = A0*0.282095      = 0.886228   0.886227
c5 = A2*0.315392      = 0.247708   0.247708
A0 : A1 : A2 = 1 : 0.6667 : 0.2500
```

```text title="実行結果（続き）"
[2] cube face size vs L00 and max coefficient error (reference: 400x800 grid)
grid L00 (rgb) = 0.83305 1.08562 1.75917
N= 4  sum(domega)=12.75821 (4pi=12.56637)  max|dL_lm|=0.04616
N= 8  sum(domega)=12.61449 (4pi=12.56637)  max|dL_lm|=0.01112
N=16  sum(domega)=12.57840 (4pi=12.56637)  max|dL_lm|=0.00275
N=32  sum(domega)=12.56938 (4pi=12.56637)  max|dL_lm|=0.00068
N=64  sum(domega)=12.56712 (4pi=12.56637)  max|dL_lm|=0.00016
```

```text title="実行結果（続き）"
[3] irradiance: SH9 vs exact (sky, N=32)
up     exact G=1.3980  SH9 G=1.4162  rel.err=1.30%
down   exact G=0.3142  SH9 G=0.3315  rel.err=5.51%
+x     exact G=1.0024  SH9 G=1.0061  rel.err=0.37%
-z     exact G=1.0024  SH9 G=1.0061  rel.err=0.37%
45deg  exact G=1.3284  SH9 G=1.3235  rel.err=0.37%
-45deg exact G=0.5620  SH9 G=0.5565  rel.err=0.99%
over 3200 normals: mean err = 0.372% of max, worst = 1.268% of max
```

```text title="実行結果（続き）"
[4] hemisphere light (sky color = zenith, ground color = ground) vs exact
sky_c (E_up/pi) G=0.4450  ground_c (E_down/pi) G=0.1000
up     exact/pi G=0.4450  SH9 G=0.4508  hemi G=0.4450
down   exact/pi G=0.1000  SH9 G=0.1055  hemi G=0.1000
+x     exact/pi G=0.3191  SH9 G=0.3203  hemi G=0.2725
-z     exact/pi G=0.3191  SH9 G=0.3203  hemi G=0.2725
45deg  exact/pi G=0.4229  SH9 G=0.4213  hemi G=0.3945
-45deg exact/pi G=0.1789  SH9 G=0.1771  hemi G=0.1505
```

```text title="実行結果（続き）"
[5] adding the sun as a delta light (E_sun = 1.0 on a surface facing it)
n = s     true E = 1.0000   SH9 E = 1.0625
n = -s    true E = 0.0000   SH9 E = 0.0625
n perp s true E = 0.0000   SH9 E = 0.0938
normals with negative SH9 irradiance: 29.7%
```

```text title="実行結果（続き）"
[6] normal rotated from up (0 deg) to down (180 deg) in the x-y plane, G channel, value = E/pi
  0 exact=0.4450 sh9=0.4508 hemi=0.4450
 15 exact=0.4445 sh9=0.4477 hemi=0.4391
 30 exact=0.4384 sh9=0.4382 hemi=0.4219
 45 exact=0.4229 sh9=0.4213 hemi=0.3945
 60 exact=0.3969 sh9=0.3961 hemi=0.3588
 75 exact=0.3616 sh9=0.3621 hemi=0.3172
 90 exact=0.3191 sh9=0.3203 hemi=0.2725
105 exact=0.2723 sh9=0.2728 hemi=0.2279
120 exact=0.2244 sh9=0.2234 hemi=0.1863
135 exact=0.1789 sh9=0.1771 hemi=0.1505
150 exact=0.1397 sh9=0.1392 hemi=0.1231
165 exact=0.1113 sh9=0.1142 hemi=0.1059
180 exact=0.1000 sh9=0.1055 hemi=0.1000
```

```text title="実行結果（続き）"
[7] sun SH9 vs true, normal rotated away from the sun direction
  0 true=1.0000 sh9=1.0625
 15 true=0.9659 sh9=1.0141
 30 true=0.8660 sh9=0.8783
 45 true=0.7071 sh9=0.6817
 60 true=0.5000 sh9=0.4609
 75 true=0.2588 sh9=0.2546
 90 true=0.0000 sh9=0.0938
105 true=0.0000 sh9=-0.0043
120 true=0.0000 sh9=-0.0391
135 true=0.0000 sh9=-0.0254
150 true=0.0000 sh9=0.0123
165 true=0.0000 sh9=0.0481
180 true=0.0000 sh9=0.0625
```

```text title="実行結果（続き）"
[8] solid angle of a cube texel relative to the face center: corner = 0.1925, edge middle = 0.3536
```

### キューブマップの大きさ {#res}

[2] はキューブの 1 面の画素数 N を変えて、基準の係数（格子で積分したもの）からのずれを見ています。立体角の総和は N = 4 で 12.758（4π ＝ 12.566 より 1.5 % 大きい）、N = 32 で 12.569 です。係数の最大誤差は N = 4 で 0.046、N = 8 で 0.011、N = 16 で 0.0028、N = 32 で 0.0007、N = 64 で 0.00016 と N が 2 倍になるたびに約 4 分の 1 になります。この空は滑らかなので N = 8 でも誤差は L00（約 1）の 1 % 程度です。だから、投影用のキューブマップは 32 × 32 程度の小さいもので足ります。投影のために画面用の大きなキューブマップを読むと無駄に重くなります。

### SH9 の精度 {#accuracy}

[3] は 6 方向の法線で SH9 と厳密な放射照度を比べています。真上は厳密 1.3980 に対して SH9 は 1.4162（1.3 % 過大）、真横と斜めは 0.4〜1.0 % の差です。いちばん大きいのは真下の 5.5 % ですがこれは、真下の E が小さい（0.314）ので、相対値が大きく出ています。3200 個の法線で E の最大値に対する誤差を見ると、平均 0.37 %、最悪 1.27 % です。

論文は実際の環境マップ（屋外・屋内の写真）で、誤差が平均 3 % 未満、最悪でも 9 % 前後と書いています。この空の誤差がそれより小さいのは、滑らかな空と地面だけの単純な環境だからです。**街灯や窓のように強い光源が環境マップに含まれると、誤差は大きくなります。** 空だけなら SH9 で十分です。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="法線を真上から真下へ回したときの E/π(緑)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">法線を真上から真下へ回したときの E/π(緑)</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="180.0" text-anchor="end" font-size="10" fill="currentColor">0.1</text><text x="54" y="146.0" text-anchor="end" font-size="10" fill="currentColor">0.2</text><text x="54" y="112.0" text-anchor="end" font-size="10" fill="currentColor">0.3</text><text x="54" y="78.0" text-anchor="end" font-size="10" fill="currentColor">0.4</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0°</text><text x="150.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">30°</text><text x="240.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">60°</text><text x="330.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">90°</text><text x="420.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">120°</text><text x="510.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">150°</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">180°</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">法線の角度(0° = 真上、180° = 真下)</text><polyline points="60.0,58.7 105.0,58.9 150.0,60.9 195.0,66.2 240.0,75.1 285.0,87.1 330.0,101.5 375.0,117.4 420.0,133.7 465.0,149.2 510.0,162.5 555.0,172.2 600.0,176.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">厳密</text><polyline points="60.0,56.7 105.0,57.8 150.0,61.0 195.0,66.8 240.0,75.3 285.0,86.9 330.0,101.1 375.0,117.2 420.0,134.0 465.0,149.8 510.0,162.7 555.0,171.2 600.0,174.1" fill="none" stroke="#4c8bf5" stroke-width="2.4" stroke-dasharray="6 3"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4" stroke-dasharray="6 3"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">SH9</text><polyline points="60.0,58.7 105.0,60.7 150.0,66.6 195.0,75.9 240.0,88.0 285.0,102.2 330.0,117.3 375.0,132.5 420.0,146.7 465.0,158.8 510.0,168.1 555.0,174.0 600.0,176.0" fill="none" stroke="#e5aa28" stroke-width="2.4"/><line x1="470" y1="80" x2="496" y2="80" stroke="#e5aa28" stroke-width="2.4"/><text x="502" y="84" text-anchor="start" font-size="11" fill="currentColor">半球ライト</text></svg>

### 半球ライトとの差 {#hemi-diff}

[4] と [6] は半球ライトと SH9、厳密な値を比べています。図の横軸は法線を真上（0°）から真下（180°）まで回した角度です。SH9 の曲線は厳密な曲線にほぼ重なっています。半球ライトは両端では一致して、間では低く出ます。真横（90°）で厳密 0.3191 に対して半球ライトは 0.2725 で、14.6 % 暗くなります。45° では 6.7 %、135° では 15.9 % 暗くなります。

原因は半球ライトが `n.y` について線形に補間していることです。厳密な放射照度は空全体を余弦で重みづけた積分なので、真横を向く面にも上の半球の明るい空が、かなり当たります。線形補間はこの「横向きの面が空を拾う分」を数えません。定数 2 色で済むのでモバイルなどの軽さを優先する場面では十分です。一方 SH9 は 9 個の `float4` だけで、この誤差が 1 % 前後に収まります。方向ごとに色が違う空（夕焼けで片側だけ赤いなど）は、半球ライトでは表せないので SH9 のほうが向いています。

## 太陽を環境マップに入れてはいけない {#sun}

太陽の円盤は空の他の部分より桁違いに明るい光です。Lagarde らの数字（[Day-Night Cycle](day-night.md) 参照）では、太陽の輝度は約 1.6 × 10⁹ cd/m² です。これを環境マップに含めると SH9 の係数は、太陽に引っ張られます。

[5] は太陽を平行光源（デルタ関数）として SH9 に入れた場合の誤差です。法線が太陽を向く面で厳密な E は 1.0 ですが、SH9 は 1.0625 になります。太陽と反対を向く面では厳密 0 に対して 0.0625、太陽と直交する面では厳密 0 に対して 0.0938 です。さらに、全方向の 29.7 % の法線で、SH9 の値は負になります。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="太陽の SH9 は、背面で 0 にならずに振動する"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">太陽の SH9 は、背面で 0 にならずに振動する</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><line x1="60" y1="185.7" x2="600" y2="185.7" stroke="#94a3b8" stroke-dasharray="4 3"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">-0.2</text><text x="54" y="189.71428571428572" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">0.5</text><text x="54" y="68.28571428571428" text-anchor="end" font-size="10" fill="currentColor">1</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0°</text><text x="150.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">30°</text><text x="240.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">60°</text><text x="330.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">90°</text><text x="420.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">120°</text><text x="510.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">150°</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">180°</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">法線と太陽の向きの角度</text><polyline points="60.0,64.3 105.0,68.4 150.0,80.6 195.0,99.9 240.0,125.0 285.0,154.3 330.0,185.7 375.0,185.7 420.0,185.7 465.0,185.7 510.0,185.7 555.0,185.7 600.0,185.7" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">厳密</text><polyline points="60.0,56.7 105.0,62.6 150.0,79.1 195.0,102.9 240.0,129.7 285.0,154.8 330.0,174.3 375.0,186.2 420.0,190.5 465.0,188.8 510.0,184.2 555.0,179.9 600.0,178.1" fill="none" stroke="#e5484d" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#e5484d" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">SH9</text></svg>

図は法線を太陽の向きから 180° まで回したときの値です。厳密な値は 90° で 0 になって、それ以降は 0 のままです。SH9 は 90° の手前で厳密な値より下がり 90° で +0.094、105°〜135° で負（最小 −0.039）になって、150° 以降は再び正になります。これは 9 個の滑らかな基底で、鋭い山を近似するときに必ず出る振動（リンギング）です。

**だから太陽は環境マップにも SH にも入れず平行光源として、シェーダーで足します。** 空のキューブマップを描くときは、太陽の円盤を描かない設定にします。大気散乱のシェーダー（[Hillaire 2020](../scattering/hillaire.md) など）には、太陽の円盤を足すかどうかのスイッチがあるものが多いので、環境光用のキューブマップを描くときは、それを切ります。

## 鏡面の環境光 {#specular}

光沢のある面（金属、水面）には空の細かい景色が映ります。拡散と違って法線ではなく反射ベクトルで環境マップを引き粗さに応じてぼかした（ミップの）高い層を選びます。

```hlsl
// ================= ⑤ 鏡面の環境光 =================

TextureCube<float4> g_specular_cube : register(t1);     // 粗さごとにぼかしたミップつきのキューブマップ
cbuffer SpecCB : register(b1) {
  float g_max_mip;                                       // 最も粗いミップの番号
  float3 g_pad3;
};

float3 SampleSpecularEnv(float3 reflect_dir, float roughness) {
  float mip = roughness * g_max_mip;                     // 粗さに比例してミップを選ぶ（簡易）。本番は split-sum の事前積分
  return g_specular_cube.SampleLevel(g_linear_clamp, reflect_dir, mip).rgb;
}
```

`roughness * g_max_mip` は粗さに比例してミップを選ぶ最も簡単な近似です。本来のミップは粗さに対して線形に並んでいないので、実際には粗さごとの GGX のローブで畳み込んだキューブマップ（split-sum の第 1 項）を使います。そのつくり方と視線による補正項（BRDF の LUT）は、[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md) で説明しています。この関数は名前の位置を示すだけの簡易版です。

## 空が変わったら更新する {#update}

時刻が進んで空の色が変わるか天候が変わると、環境光も更新します。更新の頻度は拡散と鏡面で分けます。

- **拡散（SH9）**: 投影元のキューブマップは 32 × 32 × 6 面で、6,144 画素です。計算シェーダーのグループは 96 個で、合計は 96 × 64 = 6,144 スレッドです。1 画素あたり 9 係数 × 3 色の積和ですから、GPU にはごく軽い仕事です。毎フレーム更新しても負担になりません。更新が遅れると夕焼けなのに環境光は昼の色、というずれが出ます。
- **鏡面（ミップつきのキューブマップ）**: 128 × 128 × 6 面で、ミップ込みの画素数は約 131,000（6 × 128² × 4/3 = 131,072）です。粗いミップほど畳み込みの計算が重いので、1 フレームに 1 面ずつ 6 フレームで 1 周するように更新を分割します。時刻の変化は遅いので数フレーム遅れても、見た目の差は目立ちません。

空そのものの LUT の更新については、Hillaire（2020）が参考になります。論文は LUT の更新を含めた全体の GPU 時間が、NVIDIA 1080 の 1280 × 720 で 0.31 ms だと書いています。空の描画自体は毎フレーム更新しても軽いという目安になります。ただし、空のキューブマップを 6 面描く追加のコストは、このページでは測っていません。

もう 1 つの方法は時刻ごとに環境マップを事前に焼いておいて、補間することです。時刻が固定の時間帯だけならこれが最も安く、天候が変わるなら向きません。

## よくあるミス {#mistakes}

??? failure "時間が変わっても、地上の明るさが変わらない"
    環境光の SH や環境マップを空に合わせて更新していない。空だけ変えて SH を作り直さないと夕焼けでも昼の色で照らされる。拡散用の SH は毎フレーム更新する。

??? failure "SH の結果で、上下や左右が反転する"
    キューブマップの向きの規約と `CubeDirection` が食い違っている。真上を向く面が暗く真下が明るい場合は、y の符号を疑う。+X の面と −X の面を入れ替えている場合は、左右が反転する。

??? failure "太陽の向きに環境光が強く出て、背面にも光が回る"
    太陽の円盤が空のキューブマップに入ったまま SH にしている。太陽は平行光源として別に足し、キューブマップを描くときには円盤を切る。

??? failure "キューブマップの端が明るすぎる"
    立体角 `dΩ` を掛けていない。面の端の画素は中心より小さい立体角を持つので、掛けないと端が過大に数えられる。

??? failure "並列のスレッドの結果が、実行のたびに変わる"
    `GroupMemoryBarrierWithGroupSync()` を縮約の各段階の後に置いていない。足す前の値を読むスレッドが出る。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 空の拡散の光は法線ごとの放射照度 E(n)。SH9 に圧縮して画素シェーダーで式を 1 つ評価する。
    - [x] 半球ライトは軽いが、真横の面で約 15 % 暗くなる。SH9 は誤差が 1 % 前後（滑らかな空の場合）。
    - [x] キューブマップの投影では、画素の立体角を掛ける。面の端は中心の約 0.19 倍。
    - [x] 太陽は SH に入れず平行光源として別に足す。入れると背面が明るくなり負の値が出る。
    - [x] 拡散は SH（毎フレーム）、鏡面はミップつきのキューブマップ（数フレームに分けて更新）。

## 参考 {#references}

- Ravi Ramamoorthi, Pat Hanrahan, "An Efficient Representation for Irradiance Environment Maps", Proceedings of SIGGRAPH 2001, pp. 497–500, 2001. 4 ページ全部を読んだ。式 (3)(10)(12)(13)、Â_l の値、定数 c1〜c5 を参照した。
- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Proc. EGSR 2020) 39(4), 2020. 第 7 節の性能の途中まで読んだ。
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014 Course: Physically Based Shading in Theory and Practice. 太陽と EV の節だけを読んだ。
- Brian Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice. 読んでいない。split-sum の存在を示すために挙げた。
- 半球ライトは一般的な手法で、出典は読んでいない。このページの誤差の数字は C++ で厳密な積分と比べたもの。

## 関連ページ {#related}

- [Sky Models](index.md)
- [Day-Night Cycle](day-night.md)
- [Hillaire 2020](../scattering/hillaire.md)
- [Spherical Harmonics (SH)](../../gi/theory/spherical-harmonics.md)
- [Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)
- [Reflection Probes](../../reflections/probes/index.md)
