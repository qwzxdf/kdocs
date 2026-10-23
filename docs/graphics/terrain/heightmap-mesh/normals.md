---
title: Terrain Normals
tags:
  - 描画
---

# Terrain Normals

<strong>地形の陰影は法線で決まります</strong>。高さマップの隣り合う画素の差から、傾きを求めて法線にします。あらかじめ法線マップとして保存しておくと、実行時が軽くなります。このページでは地形の法線の求め方を説明します。

!!! tip "ポイント"
    - 法線 ＝ 隣の高さの差（中央差分）から求める。
    - 事前に法線マップを作っておくと軽い。
    - LOD で頂点が減っても、法線マップで細部を保てる。
    - 精度が足りないと、段々（バンディング）が出る。

!!! info "このページを読む前に"
    - [Heightmaps and Meshes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 法線
<strong>地形の法線</strong>は高さマップの勾配から求めます。隣のテクセルとの高さの差（中心差分）を使います。

<div class="formula">N = normalize( (h_left − h_right,　2·Δ,　h_down − h_up) )　（Δ：テクセル間のワールド距離）</div>

```hlsl
float3 TerrainNormal(float2 uv) {
  float2 texel = 1.0 / height_map_size;
  float hl = height_map.SampleLevel(linear_clamp, uv - float2(texel.x, 0), 0) * height_scale;
  float hr = height_map.SampleLevel(linear_clamp, uv + float2(texel.x, 0), 0) * height_scale;
  float hd = height_map.SampleLevel(linear_clamp, uv - float2(0, texel.y), 0) * height_scale;
  float hu = height_map.SampleLevel(linear_clamp, uv + float2(0, texel.y), 0) * height_scale;
  float texel_world = terrain_size / height_map_size.x;
  return normalize(float3(hl - hr, 2.0 * texel_world, hd - hu));
}
```

| 方式 | 内容 |
| --- | --- |
| 頂点で計算 | 頂点の数だけ。頂点が粗いと細かい起伏が出ない |
| ピクセルで計算 | ピクセルごとに高さマップから。細かく滑らか（頂点が粗くても見た目の凹凸は高さマップの解像度） |
| 法線マップを焼く | 事前に法線マップを作る。ピクセルで 1 回読むだけ（メモリは増える） |
| Sobel フィルタ | 8 近傍でより滑らか（ノイズの多い高さに有効） |

法線を計算する `Δ` は 高さのスケールと揃えます（テクセル間のワールド距離）。ここがずれると斜面が急すぎる・緩すぎる見た目になります。

## 中央差分の式を導く

高さを `h(x, z)` とする曲面の法線を、求めます。曲面 `y = h(x, z)` の x 方向の接線は `(1, ∂h/∂x, 0)`、z 方向の接線は `(0, ∂h/∂z, 1)` です。法線は 2 つの接線の外積です。

```text
n = (1, ∂h/∂x, 0) × (0, ∂h/∂z, 1)
  = (∂h/∂x × 1 − 0 × ∂h/∂z,  0 × 0 − 1 × 1,  1 × ∂h/∂z − ∂h/∂x × 0)
  = (∂h/∂x, −1, ∂h/∂z)
```

上向きが法線の向きなので符号を反転して、`n = (−∂h/∂x, 1, −∂h/∂z)` を正規化します。<strong>傾きが大きいほど法線は傾く</strong>ことが、読み取れます。

偏微分を隣の高さの差で近似します。画素の間隔（ワールドの距離）を `s` とすると

```text
∂h/∂x ≈ (h_右 − h_左) / (2 s)
∂h/∂z ≈ (h_上 − h_下) / (2 s)

n = normalize( −(h_右 − h_左) / (2 s),  1,  −(h_上 − h_下) / (2 s) )
  = normalize( h_左 − h_右,  2 s,  h_下 − h_上 )          ← 全体に 2s を掛けただけ
```

最後の形が上のコードの `float3(hl - hr, 2.0 * texel_world, hd - hu)` です。`2 s` を掛け忘れるまたは間違えると斜面が、実際より急にまたはなだらかに見えます。

| 間違い | 結果 |
| --- | --- |
| `s` を UV の 1 テクセル（0〜1 の値）にしてしまう | 傾きが、極端に急になる。地形がほぼ真っ平らな法線に見えるまたは逆 |
| 高さのスケール（`height_scale`）を掛け忘れる | 傾きが、実際より緩やかになる |
| 高さをメートルでなく 0〜1 のまま使う | 同上 |

高さも画素の間隔も同じ単位（メートル）で、計算することが肝心です。

## 差分の取り方

### 2 点（片側差分）、4 点（中央差分）、8 点（Sobel）

| 方式 | 読む画素 | 特徴 |
| --- | --- | --- |
| 前方差分 | 自分と右・上の 2 つ | 安い。画素の半分だけずれる（位置が、中心と合わない） |
| 中央差分 | 左・右・下・上の 4 つ | 標準。位置が中心に合う |
| Sobel | 周りの 8 つ | 細かいノイズを、ならす。やや重い |

```hlsl
// Sobel フィルタで、法線を求める。
float3 NormalSobel(float2 uv) {
  float2 t = 1.0 / height_map_size;
  float h00 = SampleH(uv + t * float2(-1, -1));
  float h10 = SampleH(uv + t * float2( 0, -1));
  float h20 = SampleH(uv + t * float2( 1, -1));
  float h01 = SampleH(uv + t * float2(-1,  0));
  float h21 = SampleH(uv + t * float2( 1,  0));
  float h02 = SampleH(uv + t * float2(-1,  1));
  float h12 = SampleH(uv + t * float2( 0,  1));
  float h22 = SampleH(uv + t * float2( 1,  1));

  // x 方向: 右の列 − 左の列（重み 1, 2, 1）。z 方向: 下の行 − 上の行。
  float dx = (h20 + 2.0 * h21 + h22) - (h00 + 2.0 * h01 + h02);
  float dz = (h02 + 2.0 * h12 + h22) - (h00 + 2.0 * h10 + h20);
  // Sobel は、重みの合計が 8 なので、距離は 8 s。
  return normalize(float3(-dx, 8.0 * texel_world, -dz));
}
```

Sobel は <strong>重みの合計が 8</strong>（中央差分は、2）なので `2 s` ではなく `8 s` を使います。

## 法線をどこで計算するか

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| 頂点で計算 | 頂点シェーダーで、高さマップを 4 回読んで法線を作り、補間して渡す | ピクセル シェーダーが、軽い | 頂点が粗い（遠景）と、細かい起伏が法線に反映されない |
| ピクセルで計算 | ピクセル シェーダーが、高さマップを 4 回（または 8 回）読む | 頂点が粗くても、細かい陰影が出る | ピクセルごとに、テクスチャの読み込みが増える |
| 法線マップを事前に作る | 高さマップから、法線マップ（`R8G8`、または `BC5`）を作っておく。ピクセルで 1 回読む | 最も速い。LOD が変わっても陰影が変わらない | メモリが、増える。高さを編集したら更新が必要 |

<strong>地形では法線マップを事前に作る</strong>方式が、一般的です。LOD で頂点が間引かれても、法線マップは同じ解像度なので、LOD の切り替えで陰影がポップしません。

### 法線マップの作り方（計算シェーダー）

```hlsl
Texture2D<float> g_height : register(t0);
RWTexture2D<float2> g_normal : register(u0);     // R16G16_SNORM、または R8G8_SNORM（xz だけ保存）

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  int2 p = int2(id.xy);
  float hl = g_height[clamp(p + int2(-1, 0), 0, size - 1)] * height_scale;
  float hr = g_height[clamp(p + int2( 1, 0), 0, size - 1)] * height_scale;
  float hd = g_height[clamp(p + int2(0, -1), 0, size - 1)] * height_scale;
  float hu = g_height[clamp(p + int2(0,  1), 0, size - 1)] * height_scale;
  float3 n = normalize(float3(hl - hr, 2.0 * texel_world, hd - hu));
  g_normal[id.xy] = n.xz;                         // y は、n.y = sqrt(1 − x² − z²) で、復元する
}
```

地形の法線は 常に上向き（y > 0）なので、x と z だけを保存して y を `sqrt(1 − x² − z²)` で、復元できます。2 チャンネルで済むのでメモリが、2/3 になります。

| 形式 | 精度 | メモリ（1 画素） |
| --- | --- | --- |
| `R8G8_SNORM` | 8 ビット。なだらかな斜面で段々（バンディング）が、見える | 2 バイト |
| `R16G16_SNORM` | 16 ビット。ほぼ問題ない | 4 バイト |
| `BC5_SNORM` | 圧縮（4:1）。色の成分ごとに独立して圧縮 | 1 バイト（平均） |

## 精度とバンディング

高さマップが <strong>8 ビット</strong>だと、高さが 256 段階しかなく、なだらかな斜面で 階段状になります。階段の段差の部分で法線が急に変わり、縞模様の陰影が出ます。

| 対策 | 内容 |
| --- | --- |
| 高さを 16 ビットにする | 根本的な解決。`R16_UNORM`（[Heightmap LOD (Mips)](../lod/height-mip.md)） |
| 高さにノイズを足す（ディザ） | 8 ビットのまま、見た目の縞をぼかす |
| 法線をバイリニアで補間する | 高さの、階段の角をならす |
| 法線マップの解像度を高さマップより低くする | 階段を、ならす（平均化） |

## 法線マップのミップマップ

法線マップを <strong>そのままミップマップにすると、問題</strong>があります。法線ベクトルを平均すると 長さが、1 より短くなります。

```text
平均した法線 = (n1 + n2 + n3 + n4) / 4          → 長さが、1 より短い
```

| 状況 | 平均した法線の長さ |
| --- | --- |
| 4 つが同じ向き（平らな場所） | 1.0 |
| 4 つがばらばら（ごつごつした場所） | 小さい（0.5 など） |

このことを使うと 平均した法線の長さが短いほど表面が、ごつごつしていると分かります。この長さを スペキュラーの粗さに、反映するのが Toksvig の方法（2005）です。遠くの岩場が光沢のちらつきなく、つや消しに見えるようになります。

```hlsl
// 平均した法線の長さから、粗さを補正する（Toksvig）。
float ToksvigRoughness(float3 averaged_normal, float roughness) {
  float len = length(averaged_normal);
  float ft = len / lerp(len, 1.0, roughness);       // 簡略化した式
  return sqrt(1.0 - ft * ft + roughness * roughness * ft * ft);   // 近似。実装によって異なる
}
```

実装は自分のライティング モデルの粗さの定義に合わせて、調整します。法線を `normalize` する前の長さを取っておくことが、重要です。

## 傾き（スロープ）の値

法線から <strong>地面の傾き</strong>がすぐに分かります。

```hlsl
float slope_cos = n.y;                         // 1 = 水平、0 = 垂直
float slope_deg = degrees(acos(saturate(n.y)));
```

スプラットの重み（岩、雪）の条件（[Splat Weights](../texturing/weights.md)）や、歩ける斜面の判定（登れる限界の角度）に、使います。

## よくあるミス

??? failure "地形の陰影に、段々の模様が出る"
    <strong>高さマップを 16bit</strong> にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣の高さの差で、法線を求める

## 参考

- Mikkelsen, "Bump Mapping Unparametrized Surfaces on the GPU", Journal of Graphics, GPU, and Game Tools, Vol. 15, No. 1, 2010（高さの微分から、法線を作る）
- Toksvig, "Mipmapping Normal Maps", Journal of Graphics Tools, Vol. 10, No. 3, 2005（法線マップのミップと、粗さへの反映）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Microsoft Learn, "DXGI_FORMAT"（`R16G16_SNORM`、`BC5_SNORM` などの形式）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Grid Mesh](grid-mesh.md)
