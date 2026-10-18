import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# ---------------------------------------------------------------- lod.md
pg.Add("../rendering/lod.md", '''
## LOD を、実装する

### どの LOD を使うか：画面上の大きさで決める

距離だけで決めると、大きな物と小さな物で、見え方が、そろいません。<strong>画面上で、その物が、何ピクセルに見えるか</strong>で決めます。

```cpp
// 物体の、画面上の直径（ピクセル）を求める。
float ProjectedSize(float bounding_radius, float distance, float screen_height_px, float fov_y) {
  const float world_per_screen = 2.0f * distance * std::tan(fov_y * 0.5f);   // 距離 distance で、画面の縦が覆う長さ
  return (bounding_radius * 2.0f) / world_per_screen * screen_height_px;
}

// しきい値（ピクセル）。画面で大きいほど、細かい LOD。
constexpr float kThresholds[3] = {200.0f, 80.0f, 30.0f};   // LOD0: 200px 以上、LOD1: 80px 以上、LOD2: 30px 以上、それ未満は LOD3

// ヒステリシスつき: 境目で、LOD が、行ったり来たりしない（ちらつかない）ように、少しだけ、余裕を持たせる。
int SelectLod(float projected_px, int current_lod) {
  for (int lod = 0; lod < 3; ++lod) {
    // 現在の LOD から、粗い側へ移るときは、しきい値より少し下で、細かい側へ戻るときは、少し上で。
    const float margin = (lod < current_lod) ? 1.1f : 0.9f;
    if (projected_px >= kThresholds[lod] * margin) return lod;
  }
  return 3;
}
```

しきい値の、前後に、10% の余裕（ヒステリシス）を持たせると、カメラが、境目で、止まっても、LOD が、切り替わり続けません。

### 切り替えを、ディザで、なじませる

LOD が、突然、切り替わると、形が、ポンと変わります（ポップ）。<strong>2 つの LOD を、同時に、ディザで、入れ替えながら</strong>描くと、目立たなくなります。

```hlsl
// 4×4 のベイヤー行列（0〜1）。ピクセルごとに、違うしきい値を作る。
float Bayer4(uint2 p) {
  static const float m[16] = {0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5};
  return (m[(p.x & 3) + 4 * (p.y & 3)] + 0.5) / 16.0;
}

// fade: この LOD の、濃さ（0〜1）。切り替え中、LOD A は 1→0、LOD B は 0→1 と変える。
void PSMain(float4 pos : SV_Position /* ... */) {
  clip(g_fade - Bayer4(uint2(pos.xy)));            // しきい値より、fade が小さいピクセルを、捨てる
  // 通常のシェーディング
}
```

切り替え中は、LOD A（`fade` が 1 から 0 へ）と LOD B（0 から 1 へ）の両方を描き、ピクセルごとに、一方だけが、残ります。TAA と組み合わせると、ディザが、平均されて、なめらかなフェードに見えます（[TAA・アップスケーラ・VRS](taa-upscaling.md)）。

### LOD の作り方：メッシュの簡略化

LOD は、手作業で作るのは、大変なので、<strong>自動で、三角形を、減らす</strong>ライブラリを使います。meshoptimizer が、広く使われています。

```cpp
#include <meshoptimizer.h>

// 元のメッシュから、三角形を、約 25% に減らした LOD を作る。
size_t target_index_count = (indices.size() / 3) / 4 * 3;          // 三角形の数を 1/4 に
float target_error = 0.01f;                                         // 許す誤差（メッシュの大きさに対する割合）
std::vector<uint32_t> lod_indices(indices.size());
size_t lod_index_count = meshopt_simplify(
    lod_indices.data(), indices.data(), indices.size(),
    &vertices[0].position.x, vertices.size(), sizeof(Vertex),
    target_index_count, target_error, 0, nullptr);
lod_indices.resize(lod_index_count);                                // 実際に、得られた個数
```

LOD ごとに、三角形を、およそ半分から 1/4 に減らして、3〜4 段作るのが一般的です。ビルド時に、作って、ファイルに保存します（[ベイク](../optimize/baking.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- visibility-buffer.md
pg.Add("../rendering/visibility-buffer.md", '''
## Visibility Buffer を、実装する

G バッファは、「マテリアルの値」を、全部、書きます。Visibility Buffer は、<strong>「どの三角形か」だけ</strong>を、書き、マテリアルの値は、<strong>後のパスで</strong>、1 回だけ、計算します。

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

ピクセル シェーダーは、テクスチャを、読まず、色の計算も、しません。<strong>1 ピクセルあたり、4 バイトを書くだけ</strong>で、G バッファ（数枚 × 4〜8 バイト）より、帯域が、大きく減ります。深度も、同時に、書きます（[Multiple Render Targets](../directx/dx11/mrt.md)）。

### ② シェーディングのパス：三角形から、全部を復元する

画面の、全ピクセルについて、三角形の番号から、頂点を読み、<strong>そのピクセルの位置での、重心座標</strong>を求め、属性（UV、法線）を、補間して、マテリアルを、評価します。

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

数行ずつ見ると、<strong>頂点の読み込みと、補間を、自分で行っている</strong>のが、G バッファ方式との違いです。ラスタライザーが、やってくれていた、属性の補間を、シェーダーで、再現しています。

### 注意：ミップの選択（微分）

ピクセル シェーダーでは、`Sample` が、隣のピクセルとの、UV の差（微分）から、ミップを、自動で選びます。シェーディングのパスは、<strong>全画面のパス</strong>で、隣のピクセルが、別の三角形のため、この微分が、使えません。

| 方法 | 内容 |
| --- | --- |
| 光線の差分（ray differentials） | 隣のピクセルの光線も、三角形と交差させて、UV の差を、求める。`SampleGrad` に渡す |
| 解析的な微分 | 重心座標の、画面空間の微分を、解析的に求める（高速。実装が複雑） |
| `SampleLevel` で、固定のミップ | 遠近で、品質が落ちる。簡易版 |

この微分の計算が、Visibility Buffer の、実装で、いちばん手間のかかる部分です。

### どんなときに、向くか

| 向く | 向かない |
| --- | --- |
| 三角形が、非常に多い（細かいメッシュ。Nanite のようなメッシュ シェーダー系） | 三角形が、少なく、ピクセルが、重い場面（G バッファで、足りる） |
| G バッファの帯域が、ボトルネック | マテリアルの種類が、多く、シェーダーの分岐が、重くなる（シェーディングのパスが、肥大する） |
| オーバードローで、G バッファの、書き込みが、無駄になる | 古い GPU（構造化バッファの、大量の読み込みが、重い） |
''', before="## よくあるミス")

# ---------------------------------------------------------------- low-res-effects.md
pg.Add("../rendering/low-res-effects.md", '''
## 深度を使って、境界をにじませずに、拡大する

縮小して描いた結果を、普通のバイリニアで、拡大すると、物体の<strong>輪郭が、にじみ</strong>ます。低解像度の 1 ピクセルが、手前の物と、奥の物の、両方に、またがっているためです。<strong>フル解像度の深度</strong>と<strong>低解像度の深度</strong>を、比べて、「近い深度の、サンプル」から、色を取ります。

```hlsl
Texture2D<float4> g_low_color : register(t0);       // 低解像度の結果（煙、AO、ブルームなど）
Texture2D<float> g_low_depth : register(t1);        // 低解像度の深度（縮小時に、最大か最小で作る）
Texture2D<float> g_full_depth : register(t2);       // フル解像度の深度
SamplerState g_point_clamp : register(s0);

cbuffer UpsampleCB : register(b0) {
  float2 g_low_size;                                // 低解像度の大きさ（ピクセル）
  float2 pad;
};

// 4 つの、近い低解像度ピクセルのうち、フル解像度の深度に、最も近い深度を持つものを、採る。
float4 PSUpsample(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  const float full_z = LinearizeDepth(g_full_depth.SampleLevel(g_point_clamp, uv, 0));
  const int2 base = int2(floor(uv * g_low_size - 0.5));       // 低解像度の、左上のピクセル

  float4 best_color = 0;
  float best_diff = 1e9;
  [unroll] for (int i = 0; i < 4; ++i) {
    const int2 q = clamp(base + int2(i & 1, i >> 1), 0, int2(g_low_size) - 1);
    const float low_z = LinearizeDepth(g_low_depth.Load(int3(q, 0)));
    const float diff = abs(low_z - full_z);                    // フル解像度の深度との、差
    if (diff < best_diff) {
      best_diff = diff;
      best_color = g_low_color.Load(int3(q, 0));               // 深度が、いちばん近いサンプルの色
    }
  }
  return best_color;
}
```

数行ずつ見ると、<strong>「このピクセルと、同じ物体にいる、低解像度のピクセル」を、深度で選んで、その色をそのまま使います</strong>。手前の物体のピクセルは、手前の、低解像度の色を、奥は奥の色を、使うので、輪郭が、にじみません。ただし、色を、混ぜずに、選ぶので、階段状に、見えることがあります。

| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| バイリニア | 4 つを、距離で混ぜる。最も、安い | 輪郭が、目立たない物（霧、ブルーム） |
| 最近深度（上のコード） | 深度が、近い 1 つを、選ぶ | 輪郭のある物の、前の煙 |
| 深度で重みづけ | 4 つを、深度の近さで、重みづけして混ぜる | 階段が気になるとき（少し重い） |
| 法線も使う | 深度に加えて、法線の近さも見る | AO など、面の向きで変わる物 |

## 縮小時の、深度の作り方

低解像度の深度は、フル解像度の深度から、<strong>縮小して作ります</strong>。平均は使わず、<strong>最大（遠い）か最小（近い）</strong>を、選びます。平均すると、手前と奥の間の、存在しない深度が、できて、境界で、おかしくなるためです。

```hlsl
// 2×2 のフル解像度の深度から、最大（最も遠い）を取って、低解像度の深度にする。
float DownsampleDepth(int2 p) {
  float d0 = g_full_depth.Load(int3(p * 2 + int2(0, 0), 0));
  float d1 = g_full_depth.Load(int3(p * 2 + int2(1, 0), 0));
  float d2 = g_full_depth.Load(int3(p * 2 + int2(0, 1), 0));
  float d3 = g_full_depth.Load(int3(p * 2 + int2(1, 1), 0));
  return max(max(d0, d1), max(d2, d3));                       // 通常の深度（0 が近い）なら max が、最も遠い
}
```

縮小する深度が、最大か最小かは、用途で選びます。煙（手前の物の後ろに、隠れるべき）は、<strong>最小（最も近い）</strong>を選ぶと、手前の物に、煙が、はみ出しにくくなります。
''', before="## よくあるミス")
print("ok")
