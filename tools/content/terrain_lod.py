import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

STRUGAR = '''Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）'''
LOSASSO = '''Losasso, Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids", ACM Transactions on Graphics (SIGGRAPH 2004)'''
ASIRVATHAM = '''Asirvatham, Hoppe, "Terrain Rendering Using GPU-Based Geometry Clipmaps", GPU Gems 2, Chapter 2, 2005'''
ULRICH = '''Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes（チャンク LOD、スカート、ジオモーフ）'''
HOPPE98 = '''Hoppe, "Smooth View-Dependent Level-of-Detail Control and its Application to Terrain Rendering", IEEE Visualization 1998（ジオモーフの原型）'''
LINDSTROM = '''Lindstrom et al., "Real-Time, Continuous Level of Detail Rendering of Height Fields", SIGGRAPH 1996'''
ROAM = '''Duchaineau et al., "ROAM: Real-Time Optimally Adapting Meshes", IEEE Visualization 1997'''
CANTLAY = '''Cantlay, "DirectX 11 Terrain Tessellation", NVIDIA ホワイトペーパー, 2011'''
D3D11TESS = '''Microsoft Learn, "Tessellation Stages"（Direct3D 11 のハル・テッセレータ・ドメインの仕様）'''
WILLIAMS = '''Williams, "Pyramidal Parametrics", SIGGRAPH 1983（ミップマップの原典）'''

# ---------------------------------------------------------------- CDLOD
pg.Dedup("terrain/lod/cdlod.md")
pg.Add("terrain/lod/cdlod.md", '''
## 論文が解こうとした問題

地形の LOD には、CDLOD より前から、いくつかの有名な方式がありました。論文は、それぞれの欠点を並べて、「GPU に仕事を任せる時代に合う、単純な方式」を提案しています。

| 方式 | 考え方 | 困るところ |
| --- | --- | --- |
| ROAM（1997） | 三角形を 1 枚ずつ、分割・統合する | CPU の仕事が重い。三角形ごとの管理は、GPU に向かない |
| Geomipmapping | 地形を正方形のブロックに分け、ブロックごとに間引く | 切り替えで、ポップが出る。隣と LOD が違うと、継ぎ目の専用インデックスが要る |
| チャンク LOD（Ulrich 2002） | 事前に作った、LOD つきのメッシュのかたまりを切り替える | メッシュをディスクに持つ。切り替えで、ポップが出る |
| クリップマップ（2004） | カメラの周りに、同じ頂点数の格子を重ねる | カメラ周りの層の更新が要る。遠くの視錐台カリングがしにくい |
| CDLOD（2009） | 四分木で範囲を選び、頂点を距離に応じて、連続的に動かす | — |

CDLOD の要点は、次の 5 つです。

1. **四分木のノードを選ぶ基準は、「カメラまでの距離の範囲」**。レベルごとに範囲を決めて、その範囲に入るノードを、そのレベルで描く
2. **すべてのノードは、同じ格子メッシュを、使い回す**。ノードごとに違うのは、位置・大きさ・レベルだけ（インスタンシング向き）
3. **高さは、頂点シェーダーで、テクスチャから読む**。ノードごとの頂点データは、持たない
4. **頂点を、距離に応じて、連続的に動かす（モーフィング）**。LOD の境目で、粗いレベルの形に、完全に一致させる
5. **だから、継ぎ目の専用インデックスも、スカートも要らない**

「選ぶのは、CPU の四分木。形を決めるのは、頂点シェーダー」という分担です。CPU は、数百個のノードを選ぶだけで、三角形は 1 枚も触りません。

## LOD の範囲を決める

レベル 0 が最も細かく、レベルが上がるほど粗くなります。カメラからの距離を、レベルごとに区切ります。

| レベル | 範囲（カメラからの距離）の例 | ノードの 1 辺 |
| --- | --- | --- |
| 0 | 0〜50 m | 64 m |
| 1 | 50〜100 m | 128 m |
| 2 | 100〜200 m | 256 m |
| 3 | 200〜400 m | 512 m |
| 4 | 400〜800 m | 1,024 m |

範囲を、<strong>前のレベルの 2 倍</strong>にすると、ノードの大きさ（1 辺が 2 倍）と、範囲の増え方が合います。そうすると、画面に映るノードの、見た目の大きさが、どのレベルでもほぼ同じになります。つまり、ノードごとの三角形数が、画面上で、ほぼ一定の密度になります。

距離は、**カメラからノードの AABB（軸に沿った箱）までの 3 次元の距離**で測ります。ノードの中心ではなく、箱の最も近い点を使います。高さの情報（最小・最大）が、箱に入っているので、山の上にいるときも、正しく測れます。

<strong>範囲の下限</strong>にも、条件があります。隣り合うノードのレベルが、**2 以上離れてはいけません**。1 つ違いなら、モーフィングで、境界を一致させられるからです。範囲を、ノードの大きさに比べて小さくしすぎると、この条件が破れます。論文のサンプルでは、範囲を、ノードの対角線の長さより十分に大きく取り、各レベルの範囲を、前の範囲の 2 倍前後にしています。

## ノードを選ぶアルゴリズム

根（地形全体）から再帰して、ノードを選びます。各ノードでは、次の 3 つを調べます。

1. ノードの AABB が、そのレベルの範囲の球と、交わらなければ、このノードは描かない（遠すぎる）
2. 視錐台と、交わらなければ、捨てる（画面の外）
3. ひとつ細かいレベルの範囲と、交わらなければ、このレベルで描く。交わるなら、4 つの子に分けて、子を調べる

```cpp
struct SelectedNode {
  const QuadNode* node;
  int level;
};

// level は、現在のノードのレベル（根が最大、葉が 0）。
void SelectNodes(const QuadNode& node, int level, const Camera& camera,
                 std::vector<SelectedNode>& out) {
  // ① このレベルの範囲の外なら、描かない（親が、粗いレベルで描いている）
  if (!node.bounds.IntersectsSphere(camera.position, lod_ranges[level])) {
    return;
  }
  // ② 画面の外なら捨てる
  if (!camera.frustum.Intersects(node.bounds)) {
    return;
  }
  // ③ 最も細かいレベル、または、ひとつ細かい範囲に入っていないなら、このノードで描く
  if (level == 0 ||
      !node.bounds.IntersectsSphere(camera.position, lod_ranges[level - 1])) {
    out.push_back({&node, level});
    return;
  }
  // ④ 範囲の内側にも入っている部分は、子に任せる。
  //    ノードの一部だけが近いとき、4 つの子はそれぞれ、別のレベルになる。
  for (const QuadNode& child : node.children) {
    SelectNodes(child, level - 1, camera, out);
  }
}
```

④ で、子に任せるとき、**親のノードが描く範囲のうち、細かい子が受け持たない部分は、粗いまま親が受け持つ**必要があります。実装では、子のうち「描かれなかった子」の領域に、親と同じ大きさの、粗いノードを追加する形にします（論文は、このとき 4 つの子の領域を、それぞれ、子のレベルで描く形で説明しています）。

## 格子メッシュ 1 枚を、使い回す

どのノードも、同じ頂点数の格子を使います。例として、32×32 マス（33×33 頂点）にします。<strong>偶数にするのは、モーフィングのため</strong>です。奇数番の頂点が、粗いレベルでは存在しない頂点になるので、偶数でないと、きれいに対応しません。

```cpp
constexpr int kGridCells = 32;
constexpr int kGridVerts = kGridCells + 1;

struct GridVertex { float x, z; };  // 0〜1 の範囲

// 頂点: 0〜1 を kGridCells 等分
std::vector<GridVertex> vertices;
for (int j = 0; j < kGridVerts; ++j) {
  for (int i = 0; i < kGridVerts; ++i) {
    vertices.push_back({float(i) / kGridCells, float(j) / kGridCells});
  }
}

// インデックス: 偶数マスと奇数マスで、対角線の向きを変える。
// こうすると、粗いレベルの三角形に、モーフィング後の形がぴったり一致する。
std::vector<uint16_t> indices;
for (int j = 0; j < kGridCells; ++j) {
  for (int i = 0; i < kGridCells; ++i) {
    uint16_t a = j * kGridVerts + i, b = a + 1;
    uint16_t c = (j + 1) * kGridVerts + i, d = c + 1;
    if (((i + j) & 1) == 0) {
      indices.insert(indices.end(), {a, c, d, a, d, b});
    } else {
      indices.insert(indices.end(), {a, c, b, b, c, d});
    }
  }
}
```

!!! note "対角線の向き"
    粗いレベルの 1 マスは、細かいレベルの 2×2 マスです。モーフィングで、奇数番の頂点が偶数番に重なったとき、細かい 4 マスの三角形のうち、いくつかは、つぶれて消えます。残る三角形が、粗い 1 マスの、2 枚の三角形になるように、4 マスの対角線を、市松模様に切り替えます。

## DirectX 11 で描く

ノードごとに変わる値は、**インスタンス データ**として、頂点バッファに積みます。1 回の `DrawIndexedInstanced` で、選ばれたすべてのノードを描けます。

```cpp
// ノードごとのデータ。インスタンス バッファに、ノードの数だけ並べる。
struct NodeInstance {
  float origin_x, origin_z;   // ノードの左下のワールド XZ
  float size;                 // ノードの 1 辺（メートル）
  float level;                // LOD レベル
  float morph_start, morph_end;  // モーフィングを始める距離、終える距離
  float pad[2];
};

// 入力レイアウト: 0 番スロット = 格子の頂点、1 番スロット = インスタンス
D3D11_INPUT_ELEMENT_DESC layout[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NODE", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 0, D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"MORPH", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 16, D3D11_INPUT_PER_INSTANCE_DATA, 1},
};

// 毎フレーム: 選ばれたノードを、インスタンス バッファに書く
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(instance_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
std::memcpy(mapped.pData, instances.data(), instances.size() * sizeof(NodeInstance));
context->Unmap(instance_buffer.Get(), 0);

UINT strides[2] = {sizeof(GridVertex), sizeof(NodeInstance)};
UINT offsets[2] = {0, 0};
ID3D11Buffer* buffers[2] = {grid_vb.Get(), instance_buffer.Get()};
context->IASetVertexBuffers(0, 2, buffers, strides, offsets);
context->IASetIndexBuffer(grid_ib.Get(), DXGI_FORMAT_R16_UINT, 0);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
context->DrawIndexedInstanced(static_cast<UINT>(indices.size()),
                              static_cast<UINT>(instances.size()), 0, 0, 0);
```

頂点シェーダーは、格子の位置（0〜1）を、ノードの位置・大きさで、ワールド座標へ変えます。そのあと、モーフィングして、高さを読みます。

```hlsl
cbuffer FrameCB : register(b0) {
  float4x4 view_proj;
  float3 camera_position;
  float grid_size;               // 32
  float2 heightmap_origin;       // 高さマップの左下（ワールド XZ）
  float2 heightmap_size;         // 高さマップが覆うワールドの大きさ
  float height_scale;
  float height_offset;
  float2 pad;
};

Texture2D<float> g_height : register(t0);   // R16_UNORM（線形補間ができる形式）
SamplerState g_linear_clamp : register(s0);

struct VSInput {
  float2 grid : POSITION;       // 0〜1
  float4 node : NODE;           // xy = 原点, z = 大きさ, w = レベル
  float4 morph : MORPH;         // x = 開始距離, y = 終了距離
};

float SampleHeight(float2 world_xz) {
  float2 uv = (world_xz - heightmap_origin) / heightmap_size;
  return g_height.SampleLevel(g_linear_clamp, uv, 0) * height_scale + height_offset;
}

float4 main(VSInput input) : SV_Position {
  // ① まず、モーフィングなしの XZ で、高さを読み、距離を測る
  float2 xz = input.node.xy + input.grid * input.node.z;
  float3 p = float3(xz.x, SampleHeight(xz), xz.y);
  float dist = distance(p, camera_position);

  // ② モーフ係数: 開始距離まで 0、終了距離で 1
  float morph = saturate((dist - input.morph.x) / (input.morph.y - input.morph.x));

  // ③ 奇数番の頂点を、ひとつ前の偶数番の位置へ寄せる
  float2 frac_part = frac(input.grid * (grid_size * 0.5)) * (2.0 / grid_size);
  float2 grid_morphed = input.grid - frac_part * morph;

  // ④ 寄せた XZ で、高さを読み直す
  xz = input.node.xy + grid_morphed * input.node.z;
  p = float3(xz.x, SampleHeight(xz), xz.y);
  return mul(float4(p, 1.0), view_proj);
}
```

### 速度が出る理由

| 項目 | 内容 |
| --- | --- |
| CPU の仕事 | 数百個のノードを選ぶだけ。頂点データには触らない |
| ドローコール | 1 回（インスタンシング）。または、レベルごとに数回 |
| 頂点データ | 格子 1 枚。全ノードで共有する |
| LOD の切り替え | 頂点シェーダーが連続的に動かすので、ポップが出ない |
| カリング | ノードごとに、視錐台カリングができる（クリップマップより細かく捨てられる） |

## 論文と、実装でずれやすい点

| 項目 | 論文の考え方 | 実装で気をつけること |
| --- | --- | --- |
| 距離 | カメラから、頂点（または AABB）までの 3 次元の距離 | XZ の 2 次元の距離だと、高い山で、LOD が合わない |
| モーフの範囲 | 各レベルの範囲の後ろ側で、0 から 1 へ | 範囲いっぱいで動かすと、細かさが落ちる。後ろの 3 割程度にする実装が多い |
| 高さの読み方 | 頂点シェーダーでの、テクスチャ読み | `R32_FLOAT` の線形補間は、環境で、使えないことがある。`R16_UNORM` が安全 |
| 法線 | 高さマップから計算（またはテクスチャ） | 頂点で出さず、ピクセル シェーダーで、高さマップの差分から出すと、モーフ中も滑らか |
| ノードの AABB | 高さの最小・最大を、四分木の各ノードに事前計算 | 高さを編集したら、AABB も更新する |

法線を高さマップから計算する方法は、[Terrain Normals](../heightmap-mesh/normals.md) を見てください。

''', before="## よくあるミス")
pg.Refs("terrain/lod/cdlod.md", [STRUGAR, LOSASSO, ULRICH, ROAM, "Microsoft Learn, \"ID3D11DeviceContext::DrawIndexedInstanced\"（インスタンシングの描画呼び出し）"])

# ---------------------------------------------------------------- morphing
pg.Dedup("terrain/lod/morphing.md")
import re  # noqa: E402
text, crlf = pg.Load("terrain/lod/morphing.md")
text = text.replace("**間引かれる側の頂点を両隣の頂点の中点へ寄せます**", "**間引かれる側の頂点を、粗い LOD に存在する頂点（偶数番）へ寄せます**")
pg.Save("terrain/lod/morphing.md", text, crlf)
pg.Add("terrain/lod/morphing.md", '''
## なぜ、ポップが起きるのか

LOD を切り替えると、頂点の数が変わり、形がわずかに変わります。細かいレベルでは、2 つの頂点の間に、**途中の頂点**があり、そこが山の頂上や谷の底に当たっていることがあります。粗いレベルに切り替わった瞬間、その頂点は無くなり、**頂上が、一瞬で低くなります**。これが、ポップです。

モーフィング（ジオモーフィング）は、<strong>切り替える前に、途中の頂点を、少しずつ粗いレベルの形に近づけておく</strong>手法です。切り替わる時点で、細かい形と粗い形が、すでに一致しているので、切り替えは、見た目では起きません。原型は、Hoppe の 1998 年の論文です。

## 頂点を寄せる 2 つの方法

粗いレベルで消える頂点（奇数番の頂点）を、どう動かすかには、2 つの流儀があります。

| 方式 | 動かすもの | 切り替え前の状態 | 特徴 |
| --- | --- | --- | --- |
| XZ を寄せる（CDLOD のサンプル） | 奇数番の頂点の XZ を、隣の偶数番の位置へ | 奇数番の頂点が、偶数番に重なって、三角形がつぶれる | 頂点シェーダーが単純。高さは、寄せた位置で読み直す |
| 高さだけを補間する（チャンク LOD など） | XZ は動かさず、高さを、両隣の高さの平均へ | 奇数番の頂点が、粗い辺の上に乗る | 見た目が、滑らかに変わる。XZ が滑らない |

どちらも、**最後に、粗いレベルの形と一致する**点は同じです。

### XZ を寄せる方式の動き

1 次元で、頂点が 5 個（0〜4）ある辺を考えます。粗いレベルでは、0・2・4 だけが残ります。

| モーフ係数 | 頂点 1 の位置 | 頂点 3 の位置 |
| --- | --- | --- |
| 0 | 1 | 3 |
| 0.5 | 0.5 | 2.5 |
| 1 | 0（頂点 0 と重なる） | 2（頂点 2 と重なる） |

頂点 1 は、頂点 0 の方へ、頂点 3 は、頂点 2 の方へ動きます。モーフ係数が 1 のとき、頂点 1 と 0 は同じ位置なので、その間の三角形は、面積が 0 になります。残った三角形が、粗いレベルのメッシュです。

### 高さだけを補間する方式

```hlsl
// 奇数番の頂点の高さを、両隣の偶数番の高さの平均へ近づける。
// grid_step は、1 マスの XZ の大きさ。
float MorphHeight(float2 world_xz, float2 grid, float morph, float grid_step) {
  float2 odd = step(0.25, frac(grid * (kGridSize * 0.5)));   // 奇数番なら 1
  float2 dir = odd * grid_step;                               // 両隣へのずれ
  float h = SampleHeight(world_xz);
  // x 方向だけが奇数番の頂点: 左右の平均。z 方向も同様。
  float h_coarse = 0.5 * (SampleHeight(world_xz - float2(dir.x, 0)) +
                          SampleHeight(world_xz + float2(dir.x, 0)));
  if (dir.x > 0 && dir.y > 0) {
    // 両方が奇数番の頂点（マスの中心）: 対角の平均
    h_coarse = 0.5 * (SampleHeight(world_xz - dir) + SampleHeight(world_xz + dir));
  } else if (dir.y > 0) {
    h_coarse = 0.5 * (SampleHeight(world_xz - float2(0, dir.y)) +
                      SampleHeight(world_xz + float2(0, dir.y)));
  }
  return lerp(h, h_coarse, morph);
}
```

XZ の位置が、変わりません。山の斜面の、模様が、滑って見える問題が出ません。そのかわり、高さを何度も読むので、頂点シェーダーのテクスチャ読み出しが、3 倍ほどに増えます。

## モーフの範囲の決め方

モーフ係数を、LOD の範囲のどこで動かすかで、見た目が変わります。

| 範囲 | 効果 |
| --- | --- |
| 範囲の全体で動かす | 切り替えは、完璧になめらか。ただし、近づくほど、細かさが、早く失われる |
| 範囲の後ろの 3 割 | 前の 7 割は、細かいまま。見た目が保たれる。多くの実装が、この形 |
| 範囲の後ろの 1 割 | 範囲がせまいと、画面上で、モーフ中の動きが、目立つ |

```cpp
// level ごとに、モーフを始める距離と、終える距離を決める。
// ranges[level] は、そのレベルを使う距離の上限。
void ComputeMorphRanges(const float* ranges, int level_count, float morph_ratio,
                        std::vector<float2>& out) {
  constexpr float kStartRatio = 0.7f;  // 範囲の後ろの 3 割で動かす
  for (int level = 0; level < level_count; ++level) {
    float prev = level == 0 ? 0.0f : ranges[level - 1];
    float end = ranges[level];
    float start = prev + (end - prev) * kStartRatio;
    out.push_back({start, end});
  }
}
```

!!! warning "モーフ中の頂点が、隣のレベルの範囲に入る"
    モーフの終わり（`end`）は、そのレベルの範囲の上限と、**ぴったり一致させます**。一致していないと、粗いレベルの境界で、細かいレベルの頂点が、まだ完全には寄っておらず、継ぎ目に、隙間が出ます（[Cracks and Seams](cracks.md)）。

## 動く地形との相性

地形が、プレイ中に変形する（掘る、爆発で凹む）ゲームでは、モーフィングの結果が、フレームごとに変わります。**頂点シェーダーで、毎フレーム、高さを読み直す**CDLOD 方式なら、高さマップを書き換えるだけで、そのまま反映されます。モーフ用のデータを、事前に焼き込む方式（チャンク LOD など）は、変形のたびに、作り直しが必要になります。

''', before="## よくあるミス")
pg.Refs("terrain/lod/morphing.md", [STRUGAR, HOPPE98, ULRICH, LOSASSO])

# ---------------------------------------------------------------- clipmap
pg.Dedup("terrain/lod/clipmap.md")
pg.Add("terrain/lod/clipmap.md", '''
## 論文の考え方

Losasso と Hoppe の方式は、**「見える範囲の、地形を、画面の解像度で必要な分だけ、持つ」**という発想から来ています。画面に映る範囲は、近くが細かく、遠くが粗くてよいので、同じ頂点数の格子を、**倍々の大きさで、入れ子**にします。

| 層 | 格子の間隔 | 覆う範囲 |
| --- | --- | --- |
| レベル 0 | 1 m | 255 m 四方（中心はカメラ） |
| レベル 1 | 2 m | 510 m 四方 |
| レベル 2 | 4 m | 1,020 m 四方 |
| レベル 3 | 8 m | 2,040 m 四方 |
| … | 倍々 | 倍々 |

どの層も、255 × 255 頂点（とは限りません。2 のべき乗に近い、同じ頂点数）です。層の数を 1 つ増やすたびに、覆う範囲は 2 倍になりますが、三角形の数は、層 1 つ分しか増えません。**10 層あれば、約 260 km 四方を、数十万個ほどの三角形で覆えます。**

### 論文の、もう 1 つの柱：データの供給

クリップマップは、描画の仕組みだけでなく、**巨大な高さデータの置き方**も提案しています。高さのデータは、全部でテラバイト級になることもあり、メモリに載りません。そこで、**層ごとに、カメラの周りだけを、メモリ上の正方形の窓として持つ**ようにします。

| 項目 | 内容 |
| --- | --- |
| メモリ上の窓 | 層ごとに、正方形の高さデータ（例：255×255）を持つ |
| カメラが動くと | 窓を動かして、新しく視界に入る帯の部分だけを、ディスクから読む |
| 窓の置き方 | **円環バッファ**（トロイダル アドレッシング）。窓の端を超えたら、反対側から使い直す |
| 圧縮 | 層をまたぐ高さの違い（残差）だけを、圧縮して持つ |

円環バッファは、窓全体を、ずらしてコピーせず、**書き込み位置だけをずらす**やり方です。テクスチャでは、`WRAP` の アドレッシング モードで、端を超えた座標が、反対側に戻るので、実現が簡単です。

```hlsl
// 層ごとの高さテクスチャを、円環バッファとして読む。
// clip_origin: この層の窓の左下が、ワールドのどのセルにあたるか（整数のセル）
float SampleClipHeight(Texture2D<float> tex, float2 world_xz, float cell_size) {
  float2 cell = world_xz / cell_size;
  // WRAP サンプラーなので、窓の外へ出ても、反対側から読まれる。
  float2 uv = cell / kClipSize;
  return tex.SampleLevel(g_linear_wrap, uv, 0);
}
```

窓を動かすときは、**新しく見える帯の部分だけ**を、`UpdateSubresource` や、ステージング テクスチャのコピーで書き換えます。窓を動かす単位は、**その層の格子の間隔の倍数（できれば 2 倍の間隔）**に揃えます。そうしないと、層の格子が、カメラの動きに合わせてなめらかに動いて、地形が泳いで見えます。

## 論文を、GPU で動かす（Asirvatham と Hoppe）

2004 年の論文は、CPU でメッシュを組み立てる方式でした。翌年の GPU Gems 2 で、**GPU の頂点シェーダーで動く形**に作り直されています。

| 項目 | 2004（原型） | 2005（GPU 版） |
| --- | --- | --- |
| 高さの置き場所 | CPU のメモリ上の頂点バッファ | **頂点テクスチャ**（頂点シェーダーで読む） |
| メッシュ | 毎フレーム、CPU で作る | **静的な頂点バッファ**を、使い回す |
| 層の形 | 正方形のリング | 同じ形の**ブロック**に分割して、描き分ける |
| 視錐台カリング | 層ごと | ブロックごと |
| 法線 | 頂点に持つ | 別の**法線マップ**として、層ごとに持つ |

### 層を、同じブロックに分ける

層の格子は、カメラの周りに、**輪（リング）**の形で置かれます。内側の層が、その輪の穴を埋めています。これを、同じ形の小さな正方形（ブロック）に分けて、**ブロック 1 種類のメッシュ**を、位置だけ変えて並べます。

| 部品 | 数（1 層あたり） | 役割 |
| --- | --- | --- |
| ブロック（m×m） | 12 個 | 輪の本体 |
| 輪の内側の縁（インテリア トリム） | 4 個 | 層の内側のずれを調整する細い帯 |
| 継ぎ目（フィックスアップ） | 1 個 | 隣の層との、隙間を埋める細い帯 |
| 縮退三角形のリング | 1 個 | 内側と外側の、頂点数の違いを吸収する |

細かい仕組みは多いですが、ここでは「**1 種類のブロックを、決まった配置で並べるだけで、輪ができる**」と覚えてください。実際の配置は、論文と、実装の例（Asirvatham の記事）を、見ながら作ります。

!!! note "そのまま使うなら、まず「1 層 = 正方形 1 枚の格子」から"
    初めて作るときは、論文のブロック分割を、そのまま真似なくてかまいません。層ごとに、同じ頂点数の、正方形の格子（穴あき）を 1 枚用意して、`DrawIndexedInstanced` で、層の数だけ描く形から始めると、仕組みが追いやすくなります。

## 層の間の、つなぎ目をどうするか

内側の層と外側の層は、格子の間隔が 2 倍違います。この境目に、**頂点がずれた隙間**ができます。論文では、**境界の近くで、頂点の高さを、外側の層の高さと、少しずつ補間する（トランジション領域）**ことで、隙間を消します。

```hlsl
// 層の端に近づくほど、高さを、外側の粗い層の高さへ寄せる。
float BlendHeight(float2 world_xz, float fine_h, float coarse_h, float2 clip_center,
                  float half_extent, float blend_width) {
  float2 d = abs(world_xz - clip_center);
  float edge_dist = max(d.x, d.y);   // 正方形の中心からの距離（最大値ノルム）
  float t = saturate((edge_dist - (half_extent - blend_width)) / blend_width);
  return lerp(fine_h, coarse_h, t);
}
```

これは、CDLOD のモーフィングと同じ考え方です。違うのは、<strong>寄せる基準が、カメラまでの距離ではなく、層の端までの距離</strong>であることです。

## クリップマップと CDLOD を、どう選ぶか

| 観点 | クリップマップ | CDLOD |
| --- | --- | --- |
| 三角形の数 | **ほぼ一定**（層の数 × 1 層ぶん） | カメラの位置や、地形の起伏で、変わる |
| 描く範囲の選び方 | カメラ中心の入れ子。**カメラが動くたび、窓を動かす** | 四分木で、必要な部分だけを選ぶ |
| 視錐台カリング | ブロック単位でできる。ただし、**後ろ側の層も、一部が、残る** | ノード単位で、細かく捨てられる |
| 高さデータの置き方 | 窓（円環バッファ）。**超巨大な地形で強い** | 通常のテクスチャで、よい。巨大地形は、別途ストリーミング |
| 実装の複雑さ | 継ぎ目の処理（ブロック、トリム）が、複雑 | 四分木とモーフィングだけ。単純 |
| 向く用途 | 海面（FFT 海）、巨大な地球規模の地形、フライト シミュレーター | 一般的なゲームの地形（数 km〜数十 km） |

水面は、クリップマップが、よく使われます。カメラの周りだけ細かく、遠くは粗くてよいという性質が、そのまま合うからです（[Water Waves](../../water/waves/index.md)）。

''', before="## よくあるミス")
pg.Refs("terrain/lod/clipmap.md", [LOSASSO, ASIRVATHAM, STRUGAR, "Tanner, Migdal, Jones, \"The Clipmap: A Virtual Mipmap\", SIGGRAPH 1998（クリップマップという名前と、窓として持つ考え方の原点。地形ではなくテクスチャの話）"])

# ---------------------------------------------------------------- cracks
pg.Dedup("terrain/lod/cracks.md")
pg.Add("terrain/lod/cracks.md", '''
## 隙間が生まれる、仕組み

LOD の違うタイルが、辺を共有して隣り合っているとします。細かい側には、辺の途中に頂点があり、粗い側には、その頂点がありません。

```text
  細かい側        境界        粗い側
   ●───●───●   ←  辺  →   ●───────●
       ↑                      （途中の頂点が無い）
   この頂点は、高さが、粗い辺から、ずれている
```

細かい側の「途中の頂点」は、地形の高さを読んで、持ち上がったり、下がったりしています。粗い側の辺は、両端の頂点を、**まっすぐ結んだだけ**です。両者の高さが違えば、その間に、**三角形 1 枚分の隙間**ができます。画面では、背景（空）が、**1 画素ぐらいの線**として見えます。

この現象を、T 字型の接合部（**T ジャンクション**）と呼ぶこともあります。3 本の辺が T の字に出会うからです。T ジャンクションでは、浮動小数点の丸め誤差も加わるので、頂点の高さが、同じになるように作っても、隙間が出ることがあります。

## 対策を、1 つずつ見る

### ① スカート（垂れ幕）

タイルの縁から、下向きに、**壁（スカート）**を足します。隙間は、壁の裏に隠れます。

```cpp
// 格子の周囲に、スカートの頂点を足す。
// 縁の頂点を複製して、高さだけを下げる。
struct SkirtVertex { float x, z; float skirt; };  // skirt = 0（地面）or 1（下げる）

void AddSkirt(std::vector<SkirtVertex>& vertices, std::vector<uint16_t>& indices,
              int n /* 辺の頂点数 */) {
  // 縁の頂点を並べ直して、skirt=1 の複製を作り、縁と複製の間に三角形を張る
  // （実装は、4 辺について同じ）
}
```

```hlsl
// 頂点シェーダー: skirt が 1 の頂点は、高さを一定量下げる。
float skirt_depth = node_size * 0.05;   // ノードの大きさに比例させる
float h = SampleHeight(xz) - input.skirt * skirt_depth;
```

| 長所 | 短所 |
| --- | --- |
| 実装が簡単。どの LOD の組み合わせでも使える | 壁が、ひび割れのように、見えることがある（特に、急な斜面と、強い光） |
| 事前処理が要らない | 壁の分だけ、三角形が増える |
| チャンク LOD（Ulrich 2002）が提案した、定番の方法 | 影やデプスの計算に、壁が映る |

壁が見えてしまう場合は、**壁の法線を、隣の地面の法線と同じにする**、**壁のテクスチャを、地面と同じ座標から引く**と、目立たなくなります。

### ② 境界の頂点を寄せる（ステッチング）

隣が粗いときだけ、細かい側の**境界の頂点を、粗い側の辺の上へ動かします**。動かす先は、「粗い辺が通る高さ」です。

```hlsl
// 境界の、奇数番の頂点: 粗い側の辺（両隣の偶数番を結ぶ線）の高さに合わせる。
// edge_flags: 4 辺のうち、隣が粗い辺のビット
float StitchHeight(float2 grid, float h, float2 xz, float step, uint edge_flags) {
  if ((edge_flags & 1) && grid.x == 0.0 && IsOdd(grid.y)) {
    h = 0.5 * (SampleHeight(xz - float2(0, step)) + SampleHeight(xz + float2(0, step)));
  }
  // ほかの 3 辺も同様
  return h;
}
```

| 長所 | 短所 |
| --- | --- |
| 隙間がなく、壁も見えない | 隣の LOD が、変わるたびに、**どの辺が粗いかの情報**を、ノードごとに更新する必要がある |
| 追加の三角形がない | ポップは、残る（寄せる量が、急に変わる）→ モーフィングへ進む |

### ③ 境界専用のインデックス（geomipmapping の方式）

隣が粗いときは、**細かい側の境界の三角形の貼り方**を変えます。奇数番の頂点を使わずに、偶数番の頂点だけで、三角形を作ります。

| 隣のレベル | 必要なインデックス |
| --- | --- |
| 同じ、または細かい | 通常のインデックス |
| 粗い（辺ごとに、4 辺） | 4 辺それぞれの、粗い／細かいの組み合わせ（2⁴ = 16 通り） |

LOD の組み合わせごとに、インデックス バッファを用意する必要があります。頂点の位置は変えないので、見た目は、1 画素の隙間もありません。

| 長所 | 短所 |
| --- | --- |
| 頂点シェーダーが、単純 | 16 種類のインデックス バッファを管理する |
| 継ぎ目に、余計な負荷がない | インスタンシングが、種類ごとに分かれる |

### ④ モーフィング（CDLOD の方式）

細かい側の境界頂点を、**距離に応じて、連続的に、粗い側の位置へ寄せます**。粗いレベルの範囲に入る時点で、すべての奇数番の頂点が、偶数番に重なっているので、境界の隙間は、**自動的に、なくなります**。

CDLOD は、この仕組みで、継ぎ目の専用処理が、いっさい要りません。ただし、**隣のノードのレベルが 2 以上違わない**ことが、前提です。違うと、モーフィングで、片方しか寄らず、隙間が出ます（[Geomorphing](morphing.md)）。

### ⑤ 共通の関数で高さを決める

境界の頂点の高さを、**両側のノードが、同じ関数で決める**方法です。たとえば、「境界上の高さは、粗い側の補間で決める」と決めれば、細かい側も、その値を使えば、隙間はできません。クリップマップの層の境界で、使われる考え方です。

## 方式の選び方

| 状況 | おすすめ |
| --- | --- |
| まず動かしたい | スカート |
| 四分木の LOD を、新しく作る | モーフィング（CDLOD） |
| 古い GPU を含む、チャンク LOD | スカート ＋ チャンクごとのモーフィング |
| 高さを、頂点で読まない（CPU でメッシュを作る） | 境界のステッチング、または専用インデックス |
| 水面・クリップマップ | トランジション領域（層の端で補間） |

## 隙間を、見つける

見た目だけでは、1 画素の隙間は、見逃します。次の方法で、見つけます。

- 背景色を、**目立つ色（赤・マゼンタ）**にして、地形を表示する。隙間が、点線のように赤く光る
- ワイヤーフレームで、境界を拡大する
- 地形に近づいて、**境界を、斜めから**見る

''', before="## よくあるミス")
pg.Refs("terrain/lod/cracks.md", [ULRICH, STRUGAR, LOSASSO, LINDSTROM, ROAM])

# ---------------------------------------------------------------- height mip
pg.Dedup("terrain/lod/height-mip.md")
pg.Add("terrain/lod/height-mip.md", '''
## なぜ、ミップが要るのか

遠くの地形を、粗い LOD で描くと、頂点が、数百メートルおきにしか、ありません。その頂点が、**細かい高さマップの、1 点だけ**を読むと、どうなるでしょうか。

高さマップが、1 m ごとに値を持つなら、数百メートル間隔の頂点は、その中の 1 点を、たまたま拾います。カメラが少し動いて、頂点の位置が、1 m 動くと、拾う値が変わります。**山の頂上を拾ったり、谷を拾ったりして、地形が、ちらちら揺れます。** これは、テクスチャの縮小で出る、エイリアシングと、同じ現象です。

ミップマップは、「大きい画像を、半分の大きさに平均して縮めたもの」を、積み重ねたものです（Williams、1983）。頂点の間隔に合ったミップを読めば、**その頂点が受け持つ範囲の、平均の高さ**が取れます。

## どのミップを読むか

頂点の間隔が、高さマップのテクセルの何個分かで、ミップが決まります。

```text
テクセル数 = 頂点の間隔(m) ÷ 高さマップの 1 テクセルの大きさ(m)
ミップ = log2(テクセル数)
```

| LOD | 頂点の間隔 | 高さマップが 1 m / テクセルのとき | 読むミップ |
| --- | --- | --- | --- |
| 0 | 2 m | 2 テクセル | 1 |
| 1 | 4 m | 4 テクセル | 2 |
| 2 | 8 m | 8 テクセル | 3 |
| 3 | 16 m | 16 テクセル | 4 |

LOD が 1 つ上がるごとに、ミップも 1 つ上がります。これは、CDLOD の場合、「レベル = ミップ + 定数」で済みます。

```hlsl
// LOD レベルから、読むミップを決める。
// level は、頂点を持つノードのレベル（0 が最も細かい）。
// base_mip は、レベル 0 の頂点の間隔に、合うミップ。
float HeightMip(float level, float base_mip) {
  return base_mip + level;
}

float SampleHeightLod(float2 world_xz, float level) {
  float2 uv = (world_xz - heightmap_origin) / heightmap_size;
  return g_height.SampleLevel(g_linear_clamp, uv, HeightMip(level, 0.0)) * height_scale + height_offset;
}
```

<strong>連続的な LOD（モーフィングつき）では、ミップも、連続的に変える</strong>と、切り替えのポップが、さらに目立たなくなります。トライリニア補間が、2 つのミップを自動で混ぜてくれるので、`SampleLevel` に、小数のミップ レベルを渡します。

```hlsl
// モーフ係数 morph（0〜1）を使って、ミップを、レベルの間で連続的に動かす。
float mip = level + morph;
float h = g_height.SampleLevel(g_linear_clamp, uv, mip);
```

## 平均だと、山が低くなる

ミップは、平均で作るのが普通です。しかし、**地形の山は、平均すると、低くなります**。幅の細い尾根は、まわりの谷と、平均されて、削られます。

| ミップ | 尾根の高さ（隣は谷 0 m） |
| --- | --- |
| 0（元の高さ） | 100 m |
| 1（2×2 の平均） | 50 m |
| 2（4×4 の平均） | 25 m |

そうすると、遠くの山が、近くで見たときより、**低く見えます**。カメラが近づくと、山がせり上がって、地形が膨らむ現象が起きます。

対策は、2 つあります。

| 方法 | 内容 |
| --- | --- |
| 最大値のミップも作る | 縮めるとき、4 つのテクセルの**最大値**を、取る。遠くの山を、少し高く見積もる |
| 平均と最大の間で混ぜる | `lerp(average, maximum, 0.5)` のように、中間を取る |

```cpp
// 高さマップのミップを、平均ではなく、最大値で作る例（CPU 側）。
void BuildMaxMip(const std::vector<float>& src, int src_size, std::vector<float>& dst) {
  const int dst_size = src_size / 2;
  dst.resize(static_cast<size_t>(dst_size) * dst_size);
  for (int y = 0; y < dst_size; ++y) {
    for (int x = 0; x < dst_size; ++x) {
      const float a = src[(2 * y) * src_size + 2 * x];
      const float b = src[(2 * y) * src_size + 2 * x + 1];
      const float c = src[(2 * y + 1) * src_size + 2 * x];
      const float d = src[(2 * y + 1) * src_size + 2 * x + 1];
      dst[y * dst_size + x] = std::max(std::max(a, b), std::max(c, d));
    }
  }
}
```

最大値のミップは、**カリングにも使えます**。四分木のノードの AABB の「最大の高さ」は、そのノードが覆う範囲の、最大値のミップを、引けば求まります。

## 最小・最大のミップを、AABB に使う

CDLOD では、ノードごとの AABB が、必要です。高さの最小値と最大値を、**ミップ（最小と最大の 2 本）**として持てば、四分木の各ノードの値が、ミップのテクセルに、1 対 1 で対応します。

| ノードのレベル | 対応するミップ | 内容 |
| --- | --- | --- |
| 葉 | ミップ k | 1 テクセル = 1 ノードの最小・最大 |
| 1 つ上 | ミップ k+1 | 1 テクセル = 4 ノードの最小・最大 |

```cpp
// 四分木のノードの AABB を、最小・最大ミップから作る。
Aabb NodeBounds(int level, int x, int z, const MinMaxMips& mips) {
  const int mip = level + mips.base_mip;
  const float min_y = mips.min[mip].At(x, z);
  const float max_y = mips.max[mip].At(x, z);
  const float size = node_size_at_level[level];
  return {{x * size, min_y, z * size}, {(x + 1) * size, max_y, (z + 1) * size}};
}
```

高さを編集したら、**その範囲のミップを作り直し**、影響する四分木のノードの AABB を、更新します。

## DirectX 11 での、ミップの作り方

高さマップをテクスチャとして作るとき、`MipLevels` を 0 にすると、すべてのミップの領域が確保されます。`GenerateMips` は、**平均**のミップを作ります（最大値のミップは、自分で作ります）。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = size;
desc.Height = size;
desc.MipLevels = 0;                     // 0 = 全ミップ
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16_UNORM;    // 高さは 16 ビット（線形補間ができる）
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;  // GenerateMips に必要
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;

device->CreateTexture2D(&desc, nullptr, &height_texture);
// 0 番のミップに、高さを書き込んだあと
context->GenerateMips(height_srv.Get());
```

16 ビットの高さは、0〜65535 を、`height_scale` で、メートルに直します。8 ビットだと、山の高さが 256 段階しかなく、階段が見えます。

!!! note "頂点シェーダーで、ミップを選ぶ"
    頂点シェーダーでは、画面の微分（`ddx`、`ddy`）が使えないので、`Sample` ではミップが自動では選ばれません。**必ず `SampleLevel` で、ミップを自分で指定します。** 指定を忘れて、ミップ 0 だけを読むと、遠くの地形が、ちらつきます。

''', before="## よくあるミス")
pg.Refs("terrain/lod/height-mip.md", [WILLIAMS, STRUGAR, LOSASSO, "Microsoft Learn, \"ID3D11DeviceContext::GenerateMips\""])

# ---------------------------------------------------------------- tessellation
pg.Dedup("terrain/lod/tessellation.md")
pg.Add("terrain/lod/tessellation.md", '''
## DirectX 11 のテッセレーションの、3 つのステージ

DirectX 11 は、頂点シェーダーとピクセル シェーダーの間に、3 つのステージを足しました。

```text
頂点シェーダー → ハル シェーダー → テッセレータ → ドメイン シェーダー → ピクセル シェーダー
                 （プログラム可能） （固定機能）    （プログラム可能）
```

| ステージ | 役割 | 地形では |
| --- | --- | --- |
| ハル シェーダー | パッチの制御点を受け取り、**どれだけ細かく割るか（テッセレーション係数）**を決める | カメラの距離や、画面上の大きさから、係数を決める |
| テッセレータ（固定機能） | 係数に従って、パッチの内側に、新しい点と三角形を作る（プログラムは書けない） | — |
| ドメイン シェーダー | 新しい点の位置を、パッチの座標（0〜1）から計算する | 高さマップを読んで、頂点を持ち上げる |

地形では、<strong>パッチ 1 枚が、地形の正方形ブロック</strong>になります。**制御点は 4 つ（四隅）**で、トポロジーは `D3D11_PRIMITIVE_TOPOLOGY_4_CONTROL_POINT_PATCHLIST` です。

```cpp
// パッチの描画: 頂点の代わりに、4 つの制御点のパッチを渡す。
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_4_CONTROL_POINT_PATCHLIST);
context->IASetVertexBuffers(0, 1, patch_vb.GetAddressOf(), &stride, &offset);
context->Draw(patch_count * 4, 0);   // パッチ 1 枚 = 4 点
```

## ハル シェーダー：係数を決める

ハル シェーダーは、2 つの関数でできています。

| 関数 | 呼ばれ方 | 役割 |
| --- | --- | --- |
| 制御点の関数 | 制御点ごとに 1 回 | 制御点を、そのまま（または加工して）出力する |
| パッチ定数関数 | パッチごとに 1 回 | **テッセレーション係数**を決める（`SV_TessFactor`、`SV_InsideTessFactor`） |

四角形のパッチでは、**辺の係数が 4 つ、内側の係数が 2 つ**です。

```hlsl
struct HullConstants {
  float edge[4]   : SV_TessFactor;        // 辺ごとの分割数（左・下・右・上）
  float inside[2] : SV_InsideTessFactor;  // 内側の分割数（横・縦）
};

// 辺の中点と、カメラの距離から、その辺の分割数を決める。
float EdgeFactor(float3 p0, float3 p1) {
  float3 mid = 0.5 * (p0 + p1);
  float dist = distance(mid, camera_position);
  // 距離が 2 倍になったら、係数を半分に（画面上の三角形の大きさを、一定にしたい）
  return clamp(kFactorAtOneMeter / dist, 1.0, 64.0);
}

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
    パッチの中心の距離から、4 辺とも同じ係数にすると、隣のパッチとの境界で、**左のパッチの右辺と、右のパッチの左辺の係数が、食い違います**。すると、境界の頂点が合わず、隙間（クラック）が出ます。辺の係数は、**その辺の、2 つの端点だけ**から計算します。**同じ辺を、隣のパッチが、同じ順序の 2 点で計算する必要があります**（両端を、座標の大きさの順に並べるなどして、計算の順序をそろえます）。

### 分割方式（`partitioning`）

| 値 | 動き | 向く場面 |
| --- | --- | --- |
| `integer` | 係数を整数に丸める。係数が変わる瞬間に、頂点が、急に増える | 簡単。ポップが出る |
| `fractional_odd` | 係数が連続的に変わると、新しい頂点が、**既存の頂点の位置から、滑らかに生えてくる** | 地形に向く。**ポップが出ない** |
| `fractional_even` | 同上。偶数の分割から始まる | 偶数の分割が必要なとき |
| `pow2` | 係数を 2 のべき乗に丸める | 地形の四分木の LOD に合わせる |

`fractional_odd` が、地形では標準です。距離が動くと、頂点の位置が、連続的に動くので、CDLOD のモーフィングと、同じ効果を、固定機能がやってくれます。

## ドメイン シェーダー：頂点を作る

テッセレータが作った点の座標（`SV_DomainLocation`、パッチの中の 0〜1）を受け取って、ワールド座標と、高さを計算します。

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

## 係数の決め方：距離と、画面上の大きさ

距離だけで係数を決めると、**画角（FOV）や画面の解像度が変わったとき**に、三角形の見た目の大きさが変わります。より正確には、**辺が画面上で何画素になるか**から、係数を決めます。

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

目標は、8 画素前後です。**小さすぎる三角形（1〜2 画素）は、GPU が苦手です**（2×2 のクアッドのため、ピクセル シェーダーが無駄に走る）。

NVIDIA の資料（Cantlay、2011）は、この考え方を、地形で実装した、標準的な参考です。**パッチごとに、高さマップを事前に調べて、平らな場所は、係数を下げる**といった工夫も紹介されています。

## カリング

ハル シェーダーで、パッチが、画面の外にあると分かったら、**係数を 0 にする**と、そのパッチは、破棄されます。

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

## テッセレーションの、長所と短所

| 観点 | 内容 |
| --- | --- |
| 長所 | CPU に四分木が要らない。**パッチの配置は、固定の格子**でよい。LOD が連続的 |
| 長所 | パッチの数が少なく、頂点バッファが小さい（1 パッチ = 4 点） |
| 短所 | 固定機能のテッセレータが、**GPU によって、速度がまちまち** |
| 短所 | **小さい三角形が多くなると、急に遅くなる** |
| 短所 | 新しい形式（メッシュ シェーダー）が、同じことを、より柔軟にできる |
| 短所 | DX11 以降の GPU が必要（モバイルや、古い環境では使えない） |

最近は、テッセレーションの代わりに、**四分木でノードを選び、同じ格子を、インスタンスで描く**（CDLOD 型）が、より一般的です。ただし、**パッチ 1 枚から、高さマップで変位させる**形は、**ディスプレースメント マッピング**（岩や壁の凹凸）と、そのまま同じなので、地形以外でも使い道があります。

''', before="## よくあるミス")
pg.Refs("terrain/lod/tessellation.md", [CANTLAY, D3D11TESS, "Vlachos, Peters, Boyd, Mitchell, \"Curved PN Triangles\", Symposium on Interactive 3D Graphics 2001（テッセレーションで曲面にする考え方の源流）", "Moreton, \"Watertight Tessellation Using Forward Differencing\", Graphics Hardware 2001（辺の細分を、辺の両端だけで決める、隙間の出ない方式）", STRUGAR])

# ---------------------------------------------------------------- index
pg.Refs("terrain/lod/index.md", [STRUGAR, LOSASSO, ASIRVATHAM, ULRICH, CANTLAY])
print("ok")
