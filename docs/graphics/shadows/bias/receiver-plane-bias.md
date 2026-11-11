---
title: Receiver Plane Bias
tags:
  - 描画
---

# Receiver Plane Bias

PCF は 1 画素の影を判定するためにシャドウ マップの周りの複数のテクセル（3×3 や 5×5）を読みます。このとき、すべてのサンプルに中心の画素の深度を使うと斜めの面では、隣のサンプルの本来の深度が中心と違うので、自分の面に自分の影が落ちる縞（シャドウ アクネ）が出ます。定数のバイアスで消そうとすると、広いカーネルほど大きくなって、影が物から浮いてしまいます。

<strong>受け手平面バイアス（Receiver Plane Depth Bias）は、画素の周りを 1 枚の平面とみなして、サンプルごとにその位置での平面の深度を計算して比べます</strong>。このページでは問題の見え方、勾配の求め方（導出と数字）、PCF への組み込み微分を使わない版、暴走の防ぎ方、他の方式との使い分けを説明します。

!!! tip "ポイント"
    - PCF の周辺サンプルは、斜めの面では中心とは別の深度にあります。中心の深度で比べると本来は光が当たる点が影と判定されます。
    - 面の傾き（光の座標 `(u, v)` に対する深度の勾配）を求めて、サンプルのずれに掛けて深度を補正します。
    - 勾配は光の座標の画面空間の微分（`ddx`・`ddy`）から、2×2 の連立方程式で解きます。
    - 広い PCF や PCSS で効果が大きく、バイアスを小さく保てるのでピーター パンニングも減ります。
    - 微分は物の縁（クアッドが別の面をまたぐ所）で乱れます。勾配に上限を設けます。

!!! info "このページを読む前に"
    - [Shadow Bias](index.md)（このセクション全体の地図と読む順番）
    - [PCF](../pcf.md)（周りのテクセルを読んで影の縁をなめらかにする方法）

## PCF とバイアスの問題 {#problem}

PCF は 1 画素をシャドウ マップの複数のテクセルで比較して、縁をなめらかにします。ところが、面が光に対して傾いていると PCF が読む隣のテクセルは、中心とは違う深度の点を指します。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="斜めの面と、PCF のサンプル位置。中心の深度で比べると端のサンプルが影と誤判定される"><defs><marker id="rpA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">斜めの面で、PCF のサンプルは深度が違う</text>
<line x1="60" y1="220" x2="640" y2="120" stroke="#4c8bf5" stroke-width="4"/><text x="640" y="110" text-anchor="end" style="font-size:12px;font-weight:600">受け手の面（斜め）</text>
<line x1="60" y1="260" x2="640" y2="260" stroke="currentColor" stroke-width="1.5"/><text x="640" y="254" text-anchor="end" style="font-size:12px">シャドウ マップ上のテクセル（u）</text>
<g stroke="#94a3b8" stroke-dasharray="4 4"><line x1="200" y1="260" x2="200" y2="196"/><line x1="350" y1="260" x2="350" y2="170"/><line x1="500" y1="260" x2="500" y2="144"/></g>
<g fill="#e5aa28"><circle cx="200" cy="196" r="5"/><circle cx="350" cy="170" r="6" fill="#e5484d"/><circle cx="500" cy="144" r="5"/></g>
<line x1="150" y1="170" x2="550" y2="170" stroke="#e5484d" stroke-dasharray="6 4" stroke-width="2"/><text x="560" y="174" style="font-size:12px;fill:#e5484d;font-weight:600">中心の深度（全サンプルに使うと…）</text>
<text x="200" y="186" text-anchor="middle" style="font-size:12px">本来より手前として扱われて</text><text x="200" y="206" text-anchor="middle" style="font-size:12px;fill:#e5484d">自己影になる</text>
<text x="500" y="136" text-anchor="middle" style="font-size:12px">本来より奥として扱われて</text><text x="500" y="124" text-anchor="middle" style="font-size:12px;fill:#e5484d">光が漏れる（ピーター パンニング）</text>
<g stroke="currentColor" stroke-width="2" marker-end="url(#rpA)"><line x1="350" y1="40" x2="350" y2="150"/></g><text x="360" y="58" style="font-size:12px">光</text></svg>

中心の深度を全サンプルの比較に使うと斜めの面の片側では、本来の深度より手前の値と比べて、影と判定されます（アクネ）。もう片側では奥の値と比べて光が漏れます。

数字で確かめます。シャドウ マップが 2048 × 2048 で、5×5 の PCF なら中心から最大 2 テクセル、`2 / 2048 ≒ 0.001` だけ離れたテクセルを読みます。面の深度勾配が `dz/du = 0.8` ならその 2 テクセル先の深度は、中心より `0.8 × 0.001 ≒ 0.00078` ずれます。24 ビットの深度の 1 段階は `2⁻²⁴ ≒ 6 × 10⁻⁸` なので、ずれは約 1 万 3 千段階です。この差を定数バイアスで覆うには `0.00078` 以上が要って、光の方向に傾いた面ほどさらに大きくなります。バイアスが大きいと影が物から浮きます。

## 平面の深度を使う {#plane}

受け手平面バイアス（Isidoro、GDC 2006）は画素の周りを平面とみなします。PCF で読む各サンプルの位置 `(du, dv)` で、平面の深度を計算してその深度で比べます。

<div class="formula">z′ = z + (dz/du) · du + (dz/dv) · dv</div>

必要なのは勾配 `(dz/du, dz/dv)` です。画素のシャドウ座標 `(u, v, z)` は画面上の位置 `(x, y)` の関数です。`(u, v, z)` の画面空間の微分 `ddx`、`ddy` は連鎖律から次の関係を満たします。

```text
∂z/∂x = (dz/du)·(∂u/∂x) + (dz/dv)·(∂v/∂x)
∂z/∂y = (dz/du)·(∂u/∂y) + (dz/dv)·(∂v/∂y)
```

未知数は `dz/du` と `dz/dv` の 2 つで、式も 2 つなので解けます。行列で書くと次のとおりです。

```text
[ ∂u/∂x  ∂v/∂x ] [dz/du]   [ ∂z/∂x ]
[ ∂u/∂y  ∂v/∂y ] [dz/dv] = [ ∂z/∂y ]
```

クラメルの公式で解きます。行列式は `det = ∂u/∂x · ∂v/∂y − ∂v/∂x · ∂u/∂y` です。

Python で確かめました。平面 `z = z0 + 0.8u − 0.5v` と画面から `(u, v)` への写像を仮定して `ddx`、`ddy` を計算し上の式で解いたところ `dz/du = 0.8`、`dz/dv = −0.5` が復元できました。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="必要な定数バイアスは、面の傾きとカーネルの大きさに比例して大きくなる。平面バイアスなら小さな定数で済む"><text x="14" y="22" class="fig-title">必要な定数バイアス（2048 のシャドウ マップ、深度勾配 0.8）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/><line x1="60" y1="200" x2="60" y2="40" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(229,72,77,0.25)" stroke="#e5484d" stroke-width="2"><rect x="100" y="162" width="90" height="38"/><rect x="250" y="130" width="90" height="70"/><rect x="400" y="62" width="90" height="138"/></g>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="560" y="196" width="90" height="4"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="145" y="156">約 0.0004</text><text x="295" y="124">約 0.0008</text><text x="445" y="56">約 0.0016</text><text x="605" y="190">0.0001 など</text>
<text x="145" y="220">3×3（±1）</text><text x="295" y="220">5×5（±2）</text><text x="445" y="220">9×9（±4）</text><text x="605" y="220">平面バイアス</text></g>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">定数バイアスは、カーネルが広いほど大きくなる（赤）。平面バイアスは、量子化ぶんの小さな定数で済む（青）</text></svg>

## PCF に組み込む {#pcf}

まず、勾配を求める関数です。画面の微分を受け取って勾配を返します。

```hlsl
Texture2D<float> g_shadow_map : register(t0);
SamplerComparisonState g_shadow_sampler : register(s0);

cbuffer ShadowConstants : register(b0) {
  float4x4 g_world_to_light;     // ワールド → ライトのクリップ空間
  float g_shadow_texel_size;     // 1 テクセルの UV の大きさ（1 / 解像度）
  float g_small_bias;            // 量子化誤差ぶんの小さな定数バイアス。例: 1e-4
  float g_max_slope;             // 勾配の上限。例: 10
  float _pad;
};

// シャドウ座標 (u, v, z) の画面微分から、深度の勾配 (dz/du, dz/dv) を求める。
float2 ReceiverPlaneDepthGradient(float3 coord_ddx, float3 coord_ddy) {
  float det = coord_ddx.x * coord_ddy.y - coord_ddx.y * coord_ddy.x;
  // 行列式が 0 に近いと、面が光と平行（退化）。符号を保って、0 割りを避ける（足した処理）
  float safe_det = (abs(det) < 1e-12) ? 1e-12 : det;
  float2 grad;
  grad.x = (coord_ddy.y * coord_ddx.z - coord_ddx.y * coord_ddy.z) / safe_det;   // dz/du
  grad.y = (coord_ddx.x * coord_ddy.z - coord_ddy.x * coord_ddx.z) / safe_det;   // dz/dv
  return clamp(grad, -g_max_slope, g_max_slope);          // 暴走の防止（後の節）
}
```

次に、PCF の各サンプルで平面の深度を使って比べます。

```hlsl
// 戻り値: 0 = 完全に影、1 = 光が当たる（PCF の平均）
float ShadowPcfReceiverPlane(float3 coord) {
  // ① 勾配は、ループの外で、全画素が同じように求める（ddx/ddy は分岐の中で使わない）
  float2 dz_duv = ReceiverPlaneDepthGradient(ddx(coord), ddy(coord));

  // ② 5×5 の各サンプルで、平面に沿った深度と比べる
  float sum = 0.0;
  const int kRadius = 2;
  [unroll] for (int y = -kRadius; y <= kRadius; ++y) {
    [unroll] for (int x = -kRadius; x <= kRadius; ++x) {
      float2 offset = float2(x, y) * g_shadow_texel_size;   // シャドウ マップ上のずれ（UV）
      float z_at_sample = coord.z + dot(dz_duv, offset);     // 平面に沿った、そのサンプルでの深度
      sum += g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy + offset, z_at_sample - g_small_bias);
    }
  }
  return sum / float((2 * kRadius + 1) * (2 * kRadius + 1));
}

float4 ReceiverPlanePS(float3 world_pos : TEXCOORD0) : SV_Target {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float3 coord = float3(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5, ndc.z);   // (u, v, z)
  float lit = ShadowPcfReceiverPlane(coord);
  return float4(lit, lit, lit, 1.0);
}
```

`dz_duv` は UV を 1 動かしたときの深度の変化です。`z_at_sample` は中心の深度に勾配とずれの内積を足したものです。`g_small_bias` は量子化誤差を覆うためのごく小さな定数で、勾配に比例する大きな定数ではありません。これがバイアスを小さく保てる理由です。

`ddx`、`ddy` は分岐の中では使えません（隣のピクセルとの差を取るため、全ピクセルが同じ命令を実行する必要があります）。①をループの外に置いているのは、そのためです。

## 微分を使わない版（法線から求める） {#normal}

画面の微分は物の縁で乱れます。面の法線が分かっていれば微分を使わずに勾配を解析的に求められます。平行光（正射影）ならライトの空間で、面の法線を `n = (nx, ny, nz)` としたとき深度の勾配は `dz/dx = −nx / nz`、`dz/dy = −ny / nz` です。これを UV の単位に直します。

```hlsl
cbuffer LightOrthoConstants : register(b1) {
  float3x3 g_world_to_light_rot;   // ワールドの方向 → ライト空間の方向（回転だけ）
  float g_ortho_extent_xy;         // 正射影の横幅・縦幅（メートル）
  float g_ortho_depth_range;       // 正射影の奥行き（メートル）。z を 0..1 にしている範囲
  float3 _pad3;
};

// 足した処理: 平行光なら、面の法線から勾配を直接求められる（微分を使わない）
float2 ReceiverPlaneGradientFromNormal(float3 world_normal) {
  float3 n = normalize(mul(world_normal, g_world_to_light_rot));   // ライト空間の法線
  float nz = max(abs(n.z), 0.05);                                  // 光と平行に近い面の暴走を防ぐ
  // ライト空間の勾配（メートル / メートル）
  float2 dz_dxy = -n.xy / (n.z >= 0.0 ? nz : -nz);
  // UV の 1 単位 = ortho_extent メートル、深度 1 単位 = ortho_depth_range メートル
  return dz_dxy * (g_ortho_extent_xy / g_ortho_depth_range);
}
```

微分を使わないので物の縁でも安定します。代わりに正射影の平行光（太陽）でしか使えず法線の精度（法線マップの有無）に依存します。透視射影（スポットライト）では深度が非線形で、勾配が一定でないのでこの式は使えません。

## 暴走を防ぐ {#clamp}

光とほぼ平行な面では `det` が 0 に近づいて、勾配が極端な値になります。上限を設けます。

```text
grad = clamp(grad, -g_max_slope, g_max_slope);   // ReceiverPlaneDepthGradient の最後の行と同じ
```

画面の微分は 2×2 のクアッド（隣り合う 4 画素）で計算されます。クアッドの画素が別の面にまたがる（物の縁）と微分が乱れて、勾配が壊れます。縁ではこの方式の効果が弱まります。勾配の上限を設けてあとは `g_small_bias` を少し大きめに取って補います。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`ReceiverPlanePS` と法線から勾配を求める関数をコンパイルして、エラーが出ないことを確かめました。勾配の解の式は Python で平面を仮定して、復元できることを確かめました。法線版の式は一般的な考え方から自分で導いたもので、描画では確認していません。

## 長所と短所 {#pros-cons}

長所は PCF を広く取っても、斜めの面で自己影が出ないことです。バイアスを小さく保てるのでピーター パンニングも少なくなります。平面に沿った補正なのでカスケードごとの調整も少なく済みます。

短所は画面の微分に依存することです。分岐の中や物の縁で不安定になります。平面を仮定するので曲面や角では仮定が崩れます。光とほぼ平行な面では数値が暴走するので、クランプが必要です。微分と逆行列の分だけ計算も増えます。

## 他の方式との使い分け {#choice}

- 2×2 の PCF（比較サンプラー、ハードウェア）は傾き依存バイアス（[Slope-Scale Bias](slope-scale-bias.md)）で十分です。
- 3×3〜5×5 の PCF（ソフトな縁）は、受け手平面バイアスが効きます。
- PCSS（広い範囲で読む）は受け手平面バイアスがほぼ必須です（[PCSS](../pcss.md)）。
- VSM や ESM（フィルタ可能なシャドウ マップ）は、別の問題（光漏れ）があるので、この方式は使いません。

## よくあるミス {#mistakes}

??? failure "広い PCF にすると、斜めの面に縞模様の自己影が出る"
    原因は全サンプルに中心の深度を使っていることです。受け手平面バイアスでサンプルごとに深度を補正します。定数バイアスを大きくして消すと影が浮くので避けます。

??? failure "平らな面の端で、勾配が壊れて影がおかしい"
    原因は物の縁で画面の微分が乱れて、勾配が極端な値になることです。勾配に上限を設けます。ポリゴンの縁に注意します。法線から勾配を求める版も縁で安定します。

??? failure "分岐の中でコンパイルエラーやおかしな値になる"
    原因は `ddx`・`ddy` を分岐の中で使っていることです。微分は全ピクセルが同じ命令を実行する場所で呼びます。ループや分岐の外で先に勾配を求めておきます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] PCF の周辺サンプルは、斜めの面で深度が違います。中心の深度で比べるとアクネが出ます。
    - [x] 勾配は `ddx`・`ddy` の 2×2 の連立方程式で解きます。サンプルの深度は `z + dot(勾配, ずれ)` です。
    - [x] 定数バイアスは量子化誤差ぶんだけの小さな値にします。
    - [x] 微分は縁で乱れるので、勾配に上限を設けます。

## 参考 {#references}

読んだ資料はありません。勾配の導出は連鎖律とクラメルの公式から自分で書きました。

- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（受け手平面の深度バイアスなど。このページでは読んでいません）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches

## 関連ページ

- [Shadow Bias](index.md)
- [Normal Offset](normal-offset.md)
- [PCF](../pcf.md)
