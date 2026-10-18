---
title: Hardware Tessellation
tags:
  - 描画
---

# Hardware Tessellation

<strong>GPU のテッセレーションで、パッチを距離に応じて細かく分割</strong>できます。<strong>メッシュの管理が楽で細かさを連続的に変えられます</strong>。このページではテッセレーションによる地形の LODを説明します。

!!! tip "ポイント"
    - ハル・ドメイン シェーダーで、パッチを分割。
    - 距離に応じて分割数を決める。
    - 隣のパッチと境界の分割数を揃える。
    - 対応していない環境もある。

## ハードウェア テッセレーション
<strong>DX11 のテッセレーション</strong>は <strong>ハル シェーダー・ドメイン シェーダー</strong>でパッチ（四角形）を、GPU 内で細分します。地形ではパッチ（例：64×64 m）を渡し、距離に応じた細分数を決めます。

テッセレーションのステージの役割です。ハル シェーダーはパッチの 4 辺と内側の細分係数を決めます（距離から）。固定機能のテッセレータは係数に従ってパッチを細分します。ドメイン シェーダーは細分された点の位置を計算し、高さマップを読んで持ち上げます。

```hlsl
HullConstants ComputeConstants(InputPatch<ControlPoint, 4> patch) {
  HullConstants output;
  float3 center = (patch[0].position + patch[1].position + patch[2].position + patch[3].position) * 0.25;
  float distance_to_camera = distance(center, camera_position);
  float factor = clamp(max_tessellation * (1.0 - distance_to_camera / far_distance), 1.0, max_tessellation);
  output.edge[0] = output.edge[1] = output.edge[2] = output.edge[3] = factor;
  output.inside[0] = output.inside[1] = factor;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| 辺の係数を隣と揃える | 隣り合うパッチが共有する辺で同じ係数を使う（クラックを防ぐ）。辺の中心の距離から計算する |
| 係数は 1〜64 | 係数を上げすぎると小さな三角形が増えて遅い |
| カリング | ハル シェーダーで画面外のパッチは係数 0 にして捨てる |
| 利点 | メッシュの管理が不要。連続的に細かさが変わる |
| 欠点 | 三角形が小さすぎると非効率。GPU によってはテッセレーションが遅い |

<strong>近年はコンピュート シェーダーで四分木を選びメッシュ シェーダーで描く</strong>構成も<strong>増えています</strong>。

## DirectX 11 のテッセレーションの 3 つのステージ

DirectX 11 は頂点シェーダーとピクセル シェーダーの間に 3 つのステージを足しました。

```text
頂点シェーダー → ハル シェーダー → テッセレータ → ドメイン シェーダー → ピクセル シェーダー
                 （プログラム可能） （固定機能）    （プログラム可能）
```

| ステージ | 役割 | 地形では |
| --- | --- | --- |
| ハル シェーダー | パッチの制御点を受け取りどれだけ細かく割るか（テッセレーション係数）を決める | カメラの距離や、画面上の大きさから係数を決める |
| テッセレータ（固定機能） | 係数に従って、パッチの内側に新しい点と三角形を作る（プログラムは書けない） | — |
| ドメイン シェーダー | 新しい点の位置をパッチの座標（0〜1）から計算する | 高さマップを読んで、頂点を持ち上げる |

地形では <strong>パッチ 1 枚が地形の正方形ブロック</strong>になります。<strong>制御点は 4 つ（四隅）</strong>で、トポロジーは `D3D11_PRIMITIVE_TOPOLOGY_4_CONTROL_POINT_PATCHLIST` です。

```cpp
// パッチの描画: 頂点の代わりに、4 つの制御点のパッチを渡す。
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_4_CONTROL_POINT_PATCHLIST);
context->IASetVertexBuffers(0, 1, patch_vb.GetAddressOf(), &stride, &offset);
context->Draw(patch_count * 4, 0);   // パッチ 1 枚 = 4 点
```

## ハル シェーダー：係数を決める

ハル シェーダーは 2 つの関数でできています。

| 関数 | 呼ばれ方 | 役割 |
| --- | --- | --- |
| 制御点の関数 | 制御点ごとに 1 回 | 制御点をそのまま（または加工して）出力する |
| パッチ定数関数 | パッチごとに 1 回 | テッセレーション係数を決める（`SV_TessFactor`、`SV_InsideTessFactor`） |

四角形のパッチでは <strong>辺の係数が 4 つ内側の係数が 2 つ</strong>です。

```hlsl
struct HullConstants {
  float edge[4]   : SV_TessFactor;        // 辺ごとの分割数（左・下・右・上）
  float inside[2] : SV_InsideTessFactor;  // 内側の分割数（横・縦）
};
```

ハル シェーダーがパッチごとに GPU へ伝える分割数です。四角形パッチなので 4 辺（左・下・右・上）それぞれの分割数と内側の横・縦の、分割数を持ちます。

```hlsl
// 辺の中点と、カメラの距離から、その辺の分割数を決める。
float EdgeFactor(float3 p0, float3 p1) {
  float3 mid = 0.5 * (p0 + p1);
  float dist = distance(mid, camera_position);
  // 距離が 2 倍になったら、係数を半分に（画面上の三角形の大きさを、一定にしたい）
  return clamp(kFactorAtOneMeter / dist, 1.0, 64.0);
}
```

辺の分割数を辺の中点とカメラの距離から、決めます。距離が 2 倍になれば係数を半分にして、画面上の三角形の大きさが一定になるようにします。1〜64 に制限するのはハードウェアの上限（64）と下限（1 = 分割しない）に、合わせるためです。

```hlsl
HullConstants ComputeConstants(InputPatch<ControlPoint, 4> patch) {
  HullConstants c;
  // 辺の係数は、辺の両端の点だけから決める。隣のパッチも、同じ両端から計算するので、
  // 共有する辺では、必ず同じ値になる（隙間が出ない）。
  c.edge[0] = EdgeFactor(patch[0].position, patch[2].position);  // 左
  c.edge[1] = EdgeFactor(patch[0].position, patch[1].position);  // 下
  c.edge[2] = EdgeFactor(patch[1].position, patch[3].position);  // 右
  c.edge[3] = EdgeFactor(patch[2].position, patch[3].position);  // 上
  // 内側は、4 辺の平均（または最大）にする
  c.inside[0] = 0.5 * (c.edge[1] + c.edge[3]);
  c.inside[1] = 0.5 * (c.edge[0] + c.edge[2]);
  return c;
}
```

辺の係数は <strong>辺の両端の点だけ</strong>から、決めます。隣り合うパッチは共有する辺を同じ両端から、計算するので必ず同じ値になり隙間（ひび割れ）が、出ません。内側の係数は向かい合う 2 辺の平均にします。

```hlsl
[domain("quad")]
[partitioning("fractional_odd")]
[outputtopology("triangle_cw")]
[outputcontrolpoints(4)]
[patchconstantfunc("ComputeConstants")]
ControlPoint main(InputPatch<ControlPoint, 4> patch, uint i : SV_OutputControlPointID) {
  return patch[i];
}
```

!!! warning "辺の係数は、辺の両端だけから計算する"
    パッチの中心の距離から、4 辺とも同じ係数にすると隣のパッチとの境界で、<strong>左のパッチの右辺と右のパッチの左辺の係数が、食い違います</strong>。すると、境界の頂点が合わず隙間（クラック）が出ます。辺の係数は <strong>その辺の 2 つの端点だけ</strong>から計算します。同じ辺を隣のパッチが同じ順序の 2 点で計算する必要があります（両端を座標の大きさの順に並べるなどして、計算の順序をそろえます）。

### 分割方式（`partitioning`）

| 値 | 動き | 向く場面 |
| --- | --- | --- |
| `integer` | 係数を整数に丸める。係数が変わる瞬間に頂点が急に増える | 簡単。ポップが出る |
| `fractional_odd` | 係数が連続的に変わると、新しい頂点が既存の頂点の位置から、滑らかに生えてくる | 地形に向く。ポップが出ない |
| `fractional_even` | 同上。偶数の分割から始まる | 偶数の分割が必要なとき |
| `pow2` | 係数を 2 のべき乗に丸める | 地形の四分木の LOD に合わせる |

`fractional_odd` が地形では標準です。距離が動くと頂点の位置が連続的に動くので、CDLOD のモーフィングと同じ効果を固定機能がやってくれます。

## ドメイン シェーダー：頂点を作る

テッセレータが作った点の座標（`SV_DomainLocation`、パッチの中の 0〜1）を受け取って、ワールド座標と高さを計算します。

```hlsl
Texture2D<float> g_height : register(t0);
SamplerState g_linear_clamp : register(s0);

[domain("quad")]
DSOutput main(HullConstants constants, float2 uv : SV_DomainLocation,
              const OutputPatch<ControlPoint, 4> patch) {
  // パッチの四隅を、バイリニアに補間して、XZ を作る
  float3 bottom = lerp(patch[0].position, patch[1].position, uv.x);
  float3 top = lerp(patch[2].position, patch[3].position, uv.x);
  float3 p = lerp(bottom, top, uv.y);

  // 高さマップから高さを読む。ドメイン シェーダーは、画面の微分が使えないので、SampleLevel。
  float2 tex_uv = (p.xz - heightmap_origin) / heightmap_size;
  p.y = g_height.SampleLevel(g_linear_clamp, tex_uv, mip_level) * height_scale + height_offset;

  DSOutput output;
  output.position = mul(float4(p, 1.0), view_proj);
  output.world_position = p;
  output.tex_uv = tex_uv;
  return output;
}
```

## 係数の決め方：距離と画面上の大きさ

距離だけで係数を決めると <strong>画角（FOV）や画面の解像度が変わったとき</strong>に、三角形の見た目の大きさが変わります。より正確には <strong>辺が画面上で何画素になるか</strong>から、係数を決めます。

```hlsl
// 辺の、画面上の長さ（画素）を測って、1 つの三角形の辺が、目標の画素数になるように割る。
float EdgeFactorScreen(float3 p0, float3 p1, float target_pixels) {
  float4 c0 = mul(float4(p0, 1), view_proj);
  float4 c1 = mul(float4(p1, 1), view_proj);
  float2 s0 = c0.xy / c0.w * 0.5 * screen_size;   // 画素座標
  float2 s1 = c1.xy / c1.w * 0.5 * screen_size;
  return clamp(length(s0 - s1) / target_pixels, 1.0, 64.0);
}
```

目標は 8 画素前後です。<strong>小さすぎる三角形（1〜2 画素）は、GPU が苦手です</strong>（2×2 のクアッドのため、ピクセル シェーダーが無駄に走る）。

NVIDIA の資料（Cantlay、2011）はこの考え方を地形で実装した標準的な参考です。<strong>パッチごとに高さマップを事前に調べて、平らな場所は係数を下げる</strong>といった工夫も紹介されています。

## カリング

ハル シェーダーでパッチが画面の外にあると分かったら、<strong>係数を 0 にする</strong>とそのパッチは、破棄されます。

```hlsl
// 視錐台の 6 枚の平面と、パッチの AABB（高さの最大・最小も使う）を比べる。
bool Visible(float3 aabb_min, float3 aabb_max) {
  for (int i = 0; i < 6; ++i) {
    float3 p = float3(frustum_planes[i].x > 0 ? aabb_max.x : aabb_min.x,
                      frustum_planes[i].y > 0 ? aabb_max.y : aabb_min.y,
                      frustum_planes[i].z > 0 ? aabb_max.z : aabb_min.z);
    if (dot(frustum_planes[i].xyz, p) + frustum_planes[i].w < 0) return false;
  }
  return true;
}

// ComputeConstants の最後で:
if (!Visible(patch_min, patch_max)) {
  c.edge[0] = c.edge[1] = c.edge[2] = c.edge[3] = 0;
  c.inside[0] = c.inside[1] = 0;
}
```

## テッセレーションの長所と短所

| 観点 | 内容 |
| --- | --- |
| 長所 | CPU に四分木が要らない。パッチの配置は固定の格子でよい。LOD が連続的 |
| 長所 | パッチの数が少なく、頂点バッファが小さい（1 パッチ = 4 点） |
| 短所 | 固定機能のテッセレータが、GPU によって速度がまちまち |
| 短所 | 小さい三角形が多くなると、急に遅くなる |
| 短所 | 新しい形式（メッシュ シェーダー）が、同じことをより柔軟にできる |
| 短所 | DX11 以降の GPU が必要（モバイルや古い環境では使えない） |

最近はテッセレーションの代わりに <strong>四分木でノードを選び同じ格子をインスタンスで描く</strong>（CDLOD 型）が、より一般的です。ただし、<strong>パッチ 1 枚から高さマップで変位させる</strong>形は、ディスプレースメント マッピング（岩や壁の凹凸）とそのまま同じなので、地形以外でも使い道があります。

## よくあるミス

??? failure "パッチの境目に隙間が見える"
    <strong>境界の分割数を隣と揃える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU で、距離に応じて分割

## 参考

- Cantlay, "DirectX 11 Terrain Tessellation", NVIDIA ホワイトペーパー, 2011
- Microsoft Learn, "Tessellation Stages"（Direct3D 11 のハル・テッセレータ・ドメインの仕様）
- Vlachos, Peters, Boyd, Mitchell, "Curved PN Triangles", Symposium on Interactive 3D Graphics 2001（テッセレーションで曲面にする考え方の源流）
- Moreton, "Watertight Tessellation Using Forward Differencing", Graphics Hardware 2001（辺の細分を、辺の両端だけで決める隙間の出ない方式）
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）

## 関連ページ

- [Terrain LOD](index.md)
- [CDLOD](cdlod.md)
