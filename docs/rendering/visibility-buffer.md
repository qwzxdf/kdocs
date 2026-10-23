---
title: Visibility Buffer
tags:
  - 最適化
  - 3Dゲーム
---

# Visibility Buffer

[Deferred](forward-deferred.md) は**ライティングを画面のピクセル数に比例**させましたが、代わりに G-Buffer（4 枚前後の画面サイズのテクスチャ）の書き込みと読み込みという、帯域幅の重い仕事が生まれました（[メモリ帯域幅](bandwidth.md)）。Visibility Buffer は、G-Buffer に材質の値を書く代わりに「どの物体の何番目の三角形か」という ID だけを書きます。材質の計算は後で ID から、頂点データを引き直して行うので、画面サイズの書き込みが 1 枚（32 ビット程度）で済みます。このページは何が改善するのか、仕組み、代償を説明します。

!!! tip "ポイント"
    - 目的：<strong>G-Buffer の帯域幅（4 枚 → 1 枚）</strong>と、<strong>小さな三角形でのピクセルシェーダーの無駄（quad overdraw）</strong>の削減。
    - 書くもの：インスタンス番号・三角形番号（例：32 ビット 1 枚）。材質の値は書かない。
    - 後のパス：ID から、三角形の頂点を読み重心座標を計算し、属性（UV・法線）を補間しテクスチャを引いて、ライティング。
    - 利点：書き込みの帯域が小さい・ジオメトリ パスが軽い（ピクセルシェーダーがほぼ空）・材質ごとにまとめて計算できる。
    - 代償：後のパスが複雑（頂点を自分で読み直す）。テクスチャのミップ選択（微分）を自分で計算。バインドレスがほぼ必須。
    - Nanite・Meshlet ベースのレンダラと相性が良い（[Mesh Shader](mesh-shaders.md)）。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## G-Buffer の何が重いのか

| 重い所 | 説明 |
| --- | --- |
| **書き込み** | 1080p・4 枚で約 33 MB / フレーム（60 FPS で約 2 GB/s） |
| 読み込み | ライティングで毎回、読む（Tiled なら 1 回） |
| オーバードロー | 後ろで隠れる物も G-Buffer に全部書く（[オーバードロー](overdraw.md)） |
| 小さな三角形 | ピクセルシェーダーが、2×2 ピクセル単位で動くため、小さな三角形ほど無駄（quad overdraw） |

## 仕組み

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="Visibility Buffer の流れ">
<defs><marker id="vb1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ID だけを書く → 後で、ID から、材質を計算する</text>
<rect x="20" y="50" width="170" height="80" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="105" y="84" text-anchor="middle" style="font-weight:700">① ID パス</text><text x="105" y="106" text-anchor="middle" style="font-size:12px">深度 ＋ 三角形 ID</text>
<line x1="196" y1="90" x2="246" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="254" y="50" width="170" height="80" rx="10" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="339" y="84" text-anchor="middle" style="font-weight:700">② 属性の復元</text><text x="339" y="106" text-anchor="middle" style="font-size:12px">頂点を読み、補間</text>
<line x1="430" y1="90" x2="480" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="488" y="50" width="150" height="80" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="563" y="84" text-anchor="middle" style="font-weight:700">③ 材質</text><text x="563" y="106" text-anchor="middle" style="font-size:12px">テクスチャを引く</text>
<line x1="644" y1="90" x2="690" y2="90" stroke="currentColor" stroke-width="3" marker-end="url(#vb1)"/>
<rect x="698" y="50" width="86" height="80" rx="10" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="741" y="96" text-anchor="middle" style="font-weight:700">④ 光</text>
<text x="20" y="176" style="font-weight:700">G-Buffer：</text><text x="110" y="176" style="font-size:12px">アルベド・法線・粗さ・深度 …（4 枚）を、画面全体に書く</text>
<text x="20" y="204" style="font-weight:700">Visibility：</text><text x="110" y="204" style="font-size:12px">ID（1 枚）だけ書く。残りは、ID から、後で計算</text>
<text x="20" y="240" style="font-size:12px">書き込みを減らす代わりに、②③ で、頂点バッファとテクスチャを、画面全体で読み直す</text>
</svg>

| 段階 | 内容 |
| --- | --- |
| **① ID パス** | ピクセルシェーダーは、`SV_PrimitiveID` とインスタンス番号を書くだけ（軽い）。深度も書く |
| ② 属性の復元 | ピクセルごとに三角形の 3 頂点を読み、ピクセルの位置から重心座標を計算し、UV・法線を補間 |
| ③ 材質 | 補間した UV でテクスチャを引く。UV の微分（ミップ選択）は重心座標の差から、自分で計算 |
| ④ ライティング | Deferred と同じ（Tiled / Clustered と、組み合わせられる） |

②③ のパスは材質ごとにピクセルをまとめて処理できる（タイル分類）ので同じシェーダーが連続して動き、効率が上がります。

## 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| **書き込み帯域** | 4 枚 → 1 枚（約 4 分の 1） |
| ジオメトリ パスの軽さ | ピクセルシェーダーがほぼ空。大量の三角形・小さな三角形に強い |
| 材質計算の 1 回化 | 最終的に見えるピクセルだけ、材質を計算（隠れた面の材質計算はゼロ） |
| 材質の自由度 | 材質ごとのバリエーションを後のパスで分類して処理 |

## 代償

| 代償 | 説明 |
| --- | --- |
| **実装が複雑** | 頂点の再読み込み・重心座標・微分の自前計算 |
| テクスチャの読み込み | バインドレス（番号でテクスチャを参照）が事実上、必要（DX11 では難しい） |
| 頂点の読み直し | ピクセルごとに 3 頂点を読む（キャッシュに乗るので通常は軽い） |
| MSAA との相性 | サンプルごとの ID が必要（TAA 前提の設計が多い） |
| 透明・アルファテスト | ID パスでアルファ テストのテクスチャ参照が必要 |

## 他の方式との使い分け

| 方式 | 向く場面 |
| --- | --- |
| <strong>Forward（Forward+）</strong> | 透明・MSAA・モバイル。材質が単純 |
| Deferred | ライトが多い・DX11・実装が比較的簡単 |
| Visibility Buffer | 三角形が多い・G-Buffer の帯域が、ボトルネック。GPU Driven / Meshlet と併用 |

「G-Buffer の帯域が、ボトルネックと測れた」ときに検討します（[何が重いのか](bottlenecks.md)）。

## Visibility Buffer を実装する

G バッファは「マテリアルの値」を全部、書きます。Visibility Buffer は、<strong>「どの三角形か」だけ</strong>を書きマテリアルの値は、後のパスで、1 回だけ計算します。

### ① 可視性のパス：三角形の ID だけを書く

```hlsl
// 1 つのレンダー ターゲット（R32_UINT）に、「どの描画の、どの三角形か」を、詰めて書く。
cbuffer DrawCB : register(b1) {
  uint g_draw_id;                                   // この描画（インスタンス）の番号。0〜255
};

uint PSVisibility(float4 pos : SV_Position, uint primitive_id : SV_PrimitiveID) : SV_Target {
  return (g_draw_id << 24) | (primitive_id & 0x00FFFFFF);        // 上位 8 ビット: 描画の番号、下位 24 ビット: 三角形の番号
}
```

ピクセル シェーダーはテクスチャを読まず色の計算もしません。1 ピクセルあたり 4 バイトを書くだけで、G バッファ（数枚 × 4〜8 バイト）より帯域が、大きく減ります。深度も同時に書きます（[Multiple Render Targets](../directx/dx11/mrt.md)）。

### ② シェーディングのパス：三角形から、全部を復元する

画面の全ピクセルについて三角形の番号から、頂点を読み そのピクセルの位置での重心座標を求め属性（UV、法線）を補間してマテリアルを評価します。

```hlsl
Texture2D<uint> g_visibility : register(t0);
StructuredBuffer<uint> g_indices : register(t1);          // 全メッシュのインデックス
StructuredBuffer<Vertex> g_vertices : register(t2);       // 全メッシュの頂点
StructuredBuffer<DrawInfo> g_draws : register(t3);        // 描画ごとの、ワールド行列、頂点・インデックスの開始位置、マテリアル番号

// カメラの、ピクセルを通る光線と、三角形の交点から、重心座標を求める（Möller–Trumbore 法）。
float3 Barycentrics(float3 ray_origin, float3 ray_dir, float3 p0, float3 p1, float3 p2) {
  float3 e1 = p1 - p0;
  float3 e2 = p2 - p0;
  float3 pvec = cross(ray_dir, e2);
  float inv_det = 1.0 / dot(e1, pvec);
  float3 tvec = ray_origin - p0;
  float u = dot(tvec, pvec) * inv_det;
  float3 qvec = cross(tvec, e1);
  float v = dot(ray_dir, qvec) * inv_det;
  return float3(1.0 - u - v, u, v);                       // 頂点 0・1・2 の重み
}

float4 PSShading(float4 pos : SV_Position) : SV_Target {
  uint packed = g_visibility.Load(int3(pos.xy, 0));
  if (packed == 0xFFFFFFFF) return SkyColor(pos.xy);       // 何も描かれていないピクセル（クリア値）

  uint draw_id = packed >> 24;
  uint triangle = packed & 0x00FFFFFF;
  DrawInfo draw = g_draws[draw_id];

  // 三角形の 3 頂点を、読む（インデックス → 頂点 → ワールド座標）。
  uint i0 = g_indices[draw.index_offset + triangle * 3 + 0];
  uint i1 = g_indices[draw.index_offset + triangle * 3 + 1];
  uint i2 = g_indices[draw.index_offset + triangle * 3 + 2];
  Vertex v0 = g_vertices[draw.vertex_offset + i0];
  Vertex v1 = g_vertices[draw.vertex_offset + i1];
  Vertex v2 = g_vertices[draw.vertex_offset + i2];
  float3 w0 = mul(float4(v0.position, 1), draw.world).xyz;
  float3 w1 = mul(float4(v1.position, 1), draw.world).xyz;
  float3 w2 = mul(float4(v2.position, 1), draw.world).xyz;

  // このピクセルを通る、カメラの光線。
  float3 ray_dir = normalize(PixelToWorldRay(pos.xy));
  float3 bary = Barycentrics(g_camera_position, ray_dir, w0, w1, w2);

  // 属性を、重心座標で補間して、マテリアルを評価し、ライティング。
  float2 uv = v0.uv * bary.x + v1.uv * bary.y + v2.uv * bary.z;
  float3 normal = normalize(v0.normal * bary.x + v1.normal * bary.y + v2.normal * bary.z);
  return ShadeMaterial(draw.material_id, uv, normal /* , ... */);
}
```

数行ずつ見ると 頂点の読み込みと補間を自分で行っているのが、G バッファ方式との違いです。ラスタライザーがやってくれていた、属性の補間をシェーダーで再現しています。

### 注意：ミップの選択（微分）

ピクセル シェーダーでは `Sample` が、隣のピクセルとの UV の差（微分）から、ミップを自動で選びます。シェーディングのパスは 全画面のパスで、隣のピクセルが別の三角形のため、この微分が使えません。

| 方法 | 内容 |
| --- | --- |
| 光線の差分（ray differentials） | 隣のピクセルの光線も、三角形と交差させて UV の差を求める。`SampleGrad` に渡す |
| 解析的な微分 | 重心座標の画面空間の微分を解析的に求める（高速。実装が複雑） |
| `SampleLevel` で固定のミップ | 遠近で、品質が落ちる。簡易版 |

この微分の計算が Visibility Buffer の実装で、いちばん手間のかかる部分です。

### どんなときに向くか

| 向く | 向かない |
| --- | --- |
| 三角形が多い（細かいメッシュ。Nanite のようなメッシュ シェーダー系） | 三角形が少なく、ピクセルが重い場面（G バッファで、足りる） |
| G バッファの帯域がボトルネック | マテリアルの種類が多く、シェーダーの分岐が重くなる（シェーディングのパスが、肥大する） |
| オーバードローで G バッファの書き込みが、無駄になる | 古い GPU（構造化バッファの大量の読み込みが、重い） |

## よくあるミス

??? failure "帯域が、ボトルネックでないのに導入する"
    **複雑さが見合いません**。測ってから。

??? failure "テクスチャのミップ選択が合わずちらつく"
    重心座標から UV の微分を正しく、計算します（勾配を手計算）。

??? failure "アルファ テストの物を ID パスで考慮していない"
    ID パスのピクセルシェーダーで、テクスチャを引いて `discard` します。

??? failure "DX11 で、バインドレスを前提に設計する"
    DX11 ではテクスチャ配列・アトラスで代用します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Visibility Buffer ＝ <strong>三角形の ID だけを書き、材質は後で ID から計算</strong>
    - [x] 改善：G-Buffer の書き込み帯域（4 枚 → 1 枚）・小さな三角形の無駄
    - [x] 代償：属性の復元・微分の自前計算・バインドレス。実装が複雑
    - [x] GPU Driven / Meshlet / 大量の三角形と、相性が良い（Nanite の方式）
    - [x] 帯域がボトルネックのときに検討

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [Forward と Deferred](forward-deferred.md)
- [メモリ帯域幅](bandwidth.md)
- [Mesh Shader と Meshlet](mesh-shaders.md)
- [オーバードロー](overdraw.md)
