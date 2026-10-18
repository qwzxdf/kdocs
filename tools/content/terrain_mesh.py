import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）'''
FORSYTH = '''Forsyth, "Linear-Speed Vertex Cache Optimisation", 2006（頂点キャッシュに合わせた、インデックスの並べ替え）'''
STRUGAR = '''Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009'''
ULRICH = '''Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes'''
ERICSON = '''Ericson, "Real-Time Collision Detection", Morgan Kaufmann, 2004（レイと三角形、グリッドの走査）'''
AMANATIDES = '''Amanatides, Woo, "A Fast Voxel Traversal Algorithm for Ray Tracing", Eurographics 1987（グリッドを 1 マスずつ進む DDA）'''
STAVA = '''Št'ava, Beneš, Brisbin, Křivánek, "Interactive Terrain Modeling Using Hydraulic Erosion", Symposium on Computer Animation 2008'''
GALIN = '''Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)'''
MIKKELSEN = '''Mikkelsen, "Bump Mapping Unparametrized Surfaces on the GPU", Journal of Graphics, GPU, and Game Tools, Vol. 15, No. 1, 2010（高さの微分から、法線を作る）'''
TOKSVIG = '''Toksvig, "Mipmapping Normal Maps", Journal of Graphics Tools, Vol. 10, No. 3, 2005（法線マップのミップと、粗さへの反映）'''
D3D11_RS = '''Microsoft Learn, "D3D11_RASTERIZER_DESC"（`FrontCounterClockwise`）'''
JOLT = '''Jolt Physics, "HeightFieldShape" ドキュメント（物理エンジンでの、高さ場の扱い）'''

# 座標系の記述を、サイトの決まり（右手系・Y-up・反時計回りが表）に、そろえる
text, crlf = pg.Load("terrain/heightmap-mesh/grid-mesh.md")
text = text.replace("時計回りが表（左手系）", "反時計回りが表（右手系）")
text = text.replace("時計回りが表です（左手系・Y 上・+Z 前方で、上から見て時計回り。", "反時計回りが表です（右手系・Y 上で、上から見て反時計回り。")
pg.Save("terrain/heightmap-mesh/grid-mesh.md", text, crlf)

# ---------------------------------------------------------------- grid mesh
pg.Dedup("terrain/heightmap-mesh/grid-mesh.md")
pg.Add("terrain/heightmap-mesh/grid-mesh.md", '''
## 格子の作り方を、決める 4 つのこと

| 決めること | 選び方 |
| --- | --- |
| ① 1 枚の格子の頂点数 | 65×65、129×129、257×257 など、`2^n + 1`。LOD で半分に間引けるので、偶数のマス数にする |
| ② インデックスの幅 | 16 ビット（頂点が 65,536 個まで、つまり 256×256 頂点まで）か、32 ビット |
| ③ 三角形の貼り方 | 全マスで同じ対角線か、市松（交互）か |
| ④ 頂点の形式 | `float2`（x, z）か、`uint16×2`（格子の整数座標）か |

### ① 頂点数と三角形の数

N×N 頂点の格子は、`(N − 1)²` 個のマスで、`2 × (N − 1)²` 枚の三角形になります。

| 頂点数 | マス数 | 三角形 | 16 ビット index |
| --- | --- | --- | --- |
| 33×33 | 32×32 | 2,048 | 使える |
| 65×65 | 64×64 | 8,192 | 使える |
| 129×129 | 128×128 | 32,768 | 使える |
| 257×257 | 256×256 | 131,072 | 頂点が 66,049 個で、16 ビットでは足りない |

16 ビットのインデックスは、**メモリの帯域が半分**で済み、頂点バッファも小さくできます。**1 枚の格子は、129×129 までに、とどめる**と、扱いやすいです。それ以上の広さは、同じ格子を、位置を変えて、何枚も描きます（[Chunking](chunks.md)）。

### ② 頂点は、(x, z) だけでよい

高さは、頂点シェーダーが、高さマップから読みます。頂点バッファには、**0〜1 の格子上の位置**（x, z）だけを持ちます。

```cpp
struct GridVertex { float x, z; };   // 0〜1

std::vector<GridVertex> BuildGridVertices(uint32_t n) {
  std::vector<GridVertex> v;
  v.reserve(n * n);
  for (uint32_t z = 0; z < n; ++z) {
    for (uint32_t x = 0; x < n; ++x) {
      v.push_back({float(x) / (n - 1), float(z) / (n - 1)});
    }
  }
  return v;
}
```

さらに小さくするなら、座標を `uint16` 2 つ（0〜n−1 の整数）にして、シェーダーで `/ (n - 1)` します。129×129 頂点なら、頂点バッファが、約 66 KB から 33 KB に、減ります。1 つの格子を、数百回、使い回すので、**頂点バッファ自体の大きさは、ほとんど問題になりません**。大切なのは、**インデックスと、頂点シェーダーの、軽さ**です。

### ③ 三角形の貼り方

1 つのマス（四角形）を、2 枚の三角形に分けるとき、**対角線の向きが 2 通り**あります。

| 方式 | 見た目 | 使いどころ |
| --- | --- | --- |
| 全マス、同じ向き | 斜面の、同じ方向に、筋が出ることがある | 簡単 |
| 市松（交互） | 筋が、目立ちにくい | **モーフィング（CDLOD）を使うなら、必須**（[CDLOD](../lod/cdlod.md)） |
| 高さに応じて、向きを選ぶ | 谷や尾根の形に、沿って、貼る。見た目は最も自然 | 頂点ごとの判断が、要る。実行時に決めにくい |

市松の貼り方では、**2×2 マスごとに、対角線が、交差する形**になります。粗い LOD に落とすと、粗い 1 マスの、2 枚の三角形に、きれいにまとまります。

```cpp
std::vector<uint16_t> BuildCheckerIndices(uint32_t n) {
  std::vector<uint16_t> idx;
  idx.reserve((n - 1) * (n - 1) * 6);
  for (uint32_t z = 0; z + 1 < n; ++z) {
    for (uint32_t x = 0; x + 1 < n; ++x) {
      const uint16_t a = z * n + x;        // 左上
      const uint16_t b = a + 1;            // 右上
      const uint16_t c = a + n;            // 左下
      const uint16_t d = c + 1;            // 右下
      // 上から見て反時計回りが表。マスの位置で、対角線の向きを変える。
      if (((x + z) & 1) == 0) {
        idx.insert(idx.end(), {a, c, d, a, d, b});
      } else {
        idx.insert(idx.end(), {a, c, b, b, c, d});
      }
    }
  }
  return idx;
}
```

### ④ 表裏の向き（ワインディング）

地形は、**上から見たとき、反時計回りの三角形が表**です（右手系・Y 上）。Direct3D 11 の既定は、**時計回りが表**なので、ラスタライザー ステートで、反転します。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_BACK;
rs.FrontCounterClockwise = TRUE;      // 反時計回りを表にする（このサイトの決まり）
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &rasterizer_state);
```

向きが逆だと、地形が、**裏返しになって、地面の上の面が、消えます**（裏面カリング）。地形が、まるごと見えないときは、最初に、この設定を疑います。

## 三角形ストリップと、リスト

| 方式 | インデックス数（N×N 頂点） | 特徴 |
| --- | --- | --- |
| 三角形リスト | `6 × (N−1)²` | 簡単。LOD やモーフィングと、相性がよい |
| 三角形ストリップ | 約 `2 × N × (N−1)` ＋ 切れ目 | インデックスは、約 1/3。行ごとに、リスタート値（`0xFFFF`）で、つなぐ |

ストリップは、インデックスの数が減りますが、**現代の GPU の頂点キャッシュは、リストでも、十分に効く**ので、差は、小さくなりました。**市松の対角線は、ストリップでは、表現しにくい**ので、リストを使うのが、無難です。

## 頂点キャッシュに合わせる

GPU は、**直前に処理した頂点の結果を、数十個だけ、キャッシュ**しています。同じ頂点を、続けて使うほど、処理が減ります。

格子を、**行ごとに、順番に**並べると、1 行ぶんの頂点数がキャッシュの大きさを超えて、**上の行の頂点が、キャッシュから出てしまいます**。

| 並べ方 | 頂点の再利用 |
| --- | --- |
| 行ごとの順（上のコード） | 頂点が、ほぼ 2 回、使われる。キャッシュが小さいと、再計算が増える |
| 小さなブロック（例：8×8）ごとの順 | ブロック内で、頂点を、使い回せる。キャッシュに、収まりやすい |
| 最適化ツール（Forsyth のアルゴリズムなど）で並べ替え | インデックスを、キャッシュに最適な順に並べ替える。地形の格子のような、規則的なメッシュでは、効果は、限定的 |

格子メッシュは、規則的なので、**元の並びでも、十分に効率が良い**ことが、多いです。数百万頂点を、描くのでなければ、頂点キャッシュの最適化は、後回しで、かまいません。

## DirectX 11 で、格子を作る

```cpp
// 頂点バッファ（変更しないので IMMUTABLE）
D3D11_BUFFER_DESC vb_desc = {};
vb_desc.ByteWidth = UINT(vertices.size() * sizeof(GridVertex));
vb_desc.Usage = D3D11_USAGE_IMMUTABLE;
vb_desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;
D3D11_SUBRESOURCE_DATA vb_data = {vertices.data()};
device->CreateBuffer(&vb_desc, &vb_data, &grid_vb);

// インデックス バッファ（16 ビット）
D3D11_BUFFER_DESC ib_desc = {};
ib_desc.ByteWidth = UINT(indices.size() * sizeof(uint16_t));
ib_desc.Usage = D3D11_USAGE_IMMUTABLE;
ib_desc.BindFlags = D3D11_BIND_INDEX_BUFFER;
D3D11_SUBRESOURCE_DATA ib_data = {indices.data()};
device->CreateBuffer(&ib_desc, &ib_data, &grid_ib);
```

```hlsl
// 頂点シェーダー: 格子の位置を、ワールドに直し、高さマップから、高さを読む。
Texture2D<float> g_height : register(t0);
SamplerState g_linear_clamp : register(s0);

cbuffer ChunkCB : register(b1) {
  float2 chunk_origin;     // このチャンクの、左下のワールド XZ
  float chunk_size;        // チャンクの 1 辺（メートル）
  float height_scale;
  float2 height_uv_origin; // 高さマップ上の、このチャンクの範囲
  float2 height_uv_size;
  float height_offset;
};

float4 main(float2 grid : POSITION) : SV_Position {
  float2 xz = chunk_origin + grid * chunk_size;
  float2 uv = height_uv_origin + grid * height_uv_size;
  float y = g_height.SampleLevel(g_linear_clamp, uv, 0) * height_scale + height_offset;
  return mul(float4(xz.x, y, xz.y, 1.0), view_proj);
}
```

高さマップの端の画素の中心が、チャンクの端の頂点に、合うように、`height_uv_origin` と `height_uv_size` を、**半画素分、内側に**寄せます。そうしないと、隣のチャンクと、**高さが、半画素分ずれて、継ぎ目が出ます**。

## 格子の解像度と、高さマップの解像度

格子の頂点の間隔と、高さマップの画素の間隔を、**同じ**にするのが、標準です（頂点 1 つに、画素 1 つ）。

| 関係 | 内容 |
| --- | --- |
| 頂点の方が粗い | 高さマップの、細かい凹凸が、メッシュに、反映されない（LOD の遠景では、これが、普通） |
| 頂点の方が細かい | 高さマップを、補間して使う。余計な頂点が、増えるだけ |
| 同じ | 1 頂点 = 1 画素。無駄がない |

遠景で、頂点の方が粗くなる場合は、**ミップを選んで読む**ことで、ちらつきを防ぎます（[Heightmap LOD (Mips)](../lod/height-mip.md)）。

''', before="## よくあるミス")
pg.Refs("terrain/heightmap-mesh/grid-mesh.md", [RTR, STRUGAR, FORSYTH, D3D11_RS])

# ---------------------------------------------------------------- chunks
pg.Dedup("terrain/heightmap-mesh/chunks.md")
pg.Add("terrain/heightmap-mesh/chunks.md", '''
## チャンクの大きさを、どう決めるか

チャンクは、**小さすぎても、大きすぎても、困ります**。

| 大きさ | 利点 | 欠点 |
| --- | --- | --- |
| 小さい（17×17 頂点など） | カリングが細かい。見えない部分を、無駄に描かない | チャンクの数が、爆発する。ドローコールと、CPU のカリングの仕事が増える |
| 大きい（513×513 頂点など） | チャンクの数が、少ない | 画面に、少しだけ入っている、巨大なチャンクを、丸ごと描く。LOD の細かさが、粗い |
| 中くらい（65×65〜129×129） | 両方の、ちょうど中間 | — |

目安は、**1 つのチャンクが、画面上で、数百〜数千三角形程度**になる大きさです。それより、小さいチャンクを、大量に、個別のドローコールにするのは、割に合いません。

### 数の見積もり

世界を 16 km × 16 km、チャンクを 64 m 四方にすると、

```text
チャンクの総数 = (16000 / 64)² = 250² = 62,500 個
```

カメラの周りの、視錐台に入るのは、数百〜1,000 個ほどです。**62,500 個を、毎フレーム、全部調べるのは、無駄**です。四分木などで、**大きい範囲を、まとめて捨てる**ようにします（[CDLOD](../lod/cdlod.md) の四分木）。

## チャンクが持つもの

```cpp
struct TerrainChunk {
  int grid_x, grid_z;            // チャンクの格子上の位置
  float min_height, max_height;  // 高さの最小・最大（AABB のため）
  BoundingBox bounds;            // ワールド座標の AABB
  int lod_level;                 // いまの LOD
  bool loaded;                   // 高さデータが、メモリに、あるか
};

BoundingBox ChunkBounds(const TerrainChunk& c, float chunk_size) {
  const float x0 = c.grid_x * chunk_size, z0 = c.grid_z * chunk_size;
  return {{x0, c.min_height, z0}, {x0 + chunk_size, c.max_height, z0 + chunk_size}};
}
```

**高さの最小・最大は、チャンクごとに、事前に求めておく**必要があります。山の中のチャンクと、谷のチャンクでは、AABB の縦の長さが、まるで違います。最小と最大が、不正確だと、**カリングで、見えるはずの山が、消える**ことがあります。

## 視錐台カリング

```cpp
// AABB と 6 枚の平面の、判定（p 頂点テスト）。
bool Visible(const Frustum& f, const BoundingBox& box) {
  for (const Plane& pl : f.planes) {
    // 平面の法線の向きに、最も進んだ頂点（positive vertex）を選ぶ
    const float3 p = {pl.n.x >= 0 ? box.max.x : box.min.x,
                      pl.n.y >= 0 ? box.max.y : box.min.y,
                      pl.n.z >= 0 ? box.max.z : box.min.z};
    if (Dot(pl.n, p) + pl.d < 0) return false;   // 完全に外側
  }
  return true;
}

void CullChunks(const std::vector<TerrainChunk>& all, const Frustum& f,
                std::vector<const TerrainChunk*>& visible) {
  for (const TerrainChunk& c : all) {
    if (c.loaded && Visible(f, c.bounds)) visible.push_back(&c);
  }
}
```

p 頂点テストは、AABB の 8 頂点を調べず、**平面ごとに、1 つの頂点だけ**で、判定できます。**視錐台の、少し外側に、はみ出た AABB が、「見える」と判定される**ことはありますが、描いても、画面に出ないだけで、問題はありません。

## 描画：インスタンスで、まとめる

見えるチャンクは、**同じ格子メッシュ**を、位置だけ変えて、描きます。

| 方法 | ドローコール | 特徴 |
| --- | --- | --- |
| 1 チャンク = 1 ドローコール | チャンクの数 | 簡単。数百個なら、問題ない |
| インスタンシング | 1 回（または、LOD ごと） | チャンクの位置などを、インスタンス バッファへ。CPU の仕事が、最小 |

```cpp
// 見えるチャンクの情報を、インスタンス バッファに詰めて、1 回で描く。
struct ChunkInstance { float2 origin; float size; float level; float2 uv_origin; float2 uv_size; };

std::vector<ChunkInstance> instances;
for (const TerrainChunk* c : visible) {
  instances.push_back({ChunkOrigin(*c), chunk_size, float(c->lod_level),
                       ChunkUvOrigin(*c), ChunkUvSize(*c)});
}
UploadToInstanceBuffer(context, instance_buffer, instances);
context->DrawIndexedInstanced(index_count, UINT(instances.size()), 0, 0, 0);
```

**LOD ごとに、頂点数の違う格子**を、使うなら、LOD ごとに、1 回ずつ描きます。

## 高さデータの、持ち方

チャンクごとに、高さを、どこへ置くか。2 つの方法があります。

| 方法 | 内容 | 特徴 |
| --- | --- | --- |
| 全体で 1 枚の巨大なテクスチャ | 世界全体の高さマップを、1 枚に持つ | 単純。**巨大な地形では、メモリに収まらない** |
| チャンクごとに、別のテクスチャ | チャンクごとに、小さな高さマップを持つ | ストリーミングが、簡単。ドローコールごとに、テクスチャを切り替える必要がある |
| テクスチャ配列 | 同じ大きさの、チャンクの高さを、配列のスライスにする | **1 回のドローコールで、全チャンクを描ける**。スライスの番号を、インスタンスに持たせる |
| アトラス（大きな 1 枚に、並べる） | カメラの周りの、チャンクだけを、窓として持つ | クリップマップと、似た発想（[Geometry Clipmaps](../lod/clipmap.md)） |

**テクスチャ配列**は、インスタンシングと、相性が良く、よく使われる方法です。

```hlsl
Texture2DArray<float> g_height_array : register(t0);

struct VSInput {
  float2 grid : POSITION;
  float4 chunk : CHUNK;         // xy = 原点, z = 大きさ, w = スライス番号
};

float height = g_height_array.SampleLevel(g_linear_clamp, float3(uv, input.chunk.w), 0);
```

## ストリーミング

世界が、メモリより大きいとき、**プレイヤーの周りの、チャンクだけを、メモリに置く**必要があります。

| 範囲 | 状態 |
| --- | --- |
| 描画範囲 | 高さデータが、メモリに、読み込み済み |
| 先読み範囲（描画範囲の、少し外） | これから使うので、**非同期で、読み込み中** |
| それ以外 | メモリから、解放 |

```cpp
// プレイヤーの周りの、チャンクの範囲を、計算して、読み込み・解放する。
void UpdateStreaming(const float3& player, int load_radius, int unload_radius) {
  const int px = int(player.x / chunk_size), pz = int(player.z / chunk_size);
  for (TerrainChunk& c : chunks) {
    const int d = std::max(std::abs(c.grid_x - px), std::abs(c.grid_z - pz));
    if (d <= load_radius && !c.loaded && !c.loading) RequestLoadAsync(c);
    if (d > unload_radius && c.loaded) Unload(c);        // load より大きい半径で解放（ヒステリシス）
  }
}
```

**読み込む半径より、少し大きい半径で、解放する**（ヒステリシス）と、境界の近くを、行き来したときに、**読み込みと解放が、毎フレーム繰り返されません**。

## チャンクの継ぎ目

| 継ぎ目の原因 | 対策 |
| --- | --- |
| 隣り合う、チャンクの境界の高さが、違う | 境界の画素を、**両側のチャンクで、同じ値**にする（共有する） |
| 隣り合うチャンクの、LOD が違う | モーフィング、スカートなど（[Cracks and Seams](../lod/cracks.md)） |
| 高さマップの、半画素のずれ | UV の範囲を、半画素分、内側へ寄せる |
| 法線が、境界で、不連続 | 隣のチャンクの、高さを読んで、法線を計算する（または、法線マップを、共有する） |

境界の画素は、**両方のチャンクに、同じ値を、重複して保存**します（`N×N` でなく、`(N+1)×(N+1)` 画素）。そうすると、隣のチャンクを、読み込まなくても、境界が合います。

''', before="## よくあるミス")
pg.Refs("terrain/heightmap-mesh/chunks.md", [ULRICH, STRUGAR, RTR, "Gribb, Hartmann, \"Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix\", 2001（視錐台の平面を、行列から取り出す）"])

# ---------------------------------------------------------------- editing
pg.Dedup("terrain/heightmap-mesh/editing.md")
pg.Add("terrain/heightmap-mesh/editing.md", '''
## ブラシの考え方

高さマップの編集は、**ブラシの範囲の画素に、ブラシの形の、重みを掛けて、高さを、変える**操作です。

| ブラシ | 高さの変え方 |
| --- | --- |
| 盛る（Raise） | `h += strength × falloff` |
| 削る（Lower） | `h -= strength × falloff` |
| 平らにする（Flatten） | `h = lerp(h, target, strength × falloff)`（`target` は、クリックした場所の高さ） |
| ならす（Smooth） | `h = lerp(h, 周りの平均, strength × falloff)` |
| 設定した高さにする（Set Height） | `h = lerp(h, 指定の高さ, falloff)` |
| ノイズ | `h += noise(p) × strength × falloff` |
| 段丘（Terrace） | 高さを、階段状に丸める |

`falloff` は、ブラシの中心から、縁へ向かって、1 から 0 へ、減る重みです。

```hlsl
// 中心 1、縁 0 の、なめらかな重み。
float Falloff(float dist, float radius, float hardness) {
  float t = saturate(dist / radius);
  // hardness が 1 に近いほど、縁が鋭い
  return 1.0 - smoothstep(hardness, 1.0, t);
}
```

## 計算シェーダーで、ブラシを適用する

CPU で、高さマップを書き換えて、毎フレーム、GPU に転送するのは、重いです。**ブラシも、GPU の計算シェーダーで、適用**します。

```hlsl
RWTexture2D<float> g_height : register(u0);          // R32_FLOAT（編集中は精度が必要）

cbuffer BrushCB : register(b0) {
  float2 brush_center;     // ブラシの中心（高さマップの画素座標）
  float brush_radius;      // 画素
  float brush_strength;    // 1 回に変える量（メートル）
  float hardness;
  int mode;                // 0=盛る 1=削る 2=ならす 3=平らにする
  float flatten_target;
  float dt;
};

[numthreads(8, 8, 1)]
void main(uint3 id : SV_DispatchThreadID) {
  float2 p = float2(id.xy);
  float d = distance(p, brush_center);
  if (d > brush_radius) return;                       // ブラシの外は、何もしない

  float w = Falloff(d, brush_radius, hardness) * brush_strength * dt;
  float h = g_height[id.xy];

  if (mode == 0) h += w;
  else if (mode == 1) h -= w;
  else if (mode == 3) h = lerp(h, flatten_target, saturate(w));
  else {
    // ならす: 周りの 8 画素の平均へ寄せる
    float sum = 0.0;
    for (int j = -1; j <= 1; ++j)
      for (int i = -1; i <= 1; ++i) sum += g_height[id.xy + int2(i, j)];
    h = lerp(h, sum / 9.0, saturate(w));
  }
  g_height[id.xy] = h;
}
```

```cpp
// ブラシの範囲を覆う、最小のスレッド グループだけを、ディスパッチする。
const int r = int(brush_radius) + 1;
const int x0 = std::max(0, int(center.x) - r), y0 = std::max(0, int(center.y) - r);
// シェーダー側は、id にオフセットを足して使う（ここでは、省略）
context->Dispatch((2 * r + 7) / 8, (2 * r + 7) / 8, 1);
```

!!! warning "「ならす」は、読み書きが同じテクスチャだと、結果が、順序に依存する"
    「ならす」ブラシは、**周りの画素を読んで、自分に書く**ので、同じテクスチャへ書くと、**すでに書き換えた画素を、読むことがあります**（順序が決まっていない）。ならしを、正確にやるときは、**ピンポン（別のテクスチャに、書き出して、コピーして戻す）**にします。

## 編集した範囲だけを、更新する

高さを書き換えたら、**それに依存する、すべてのデータ**を、更新する必要があります。ただし、**編集した範囲だけ**でかまいません。

| 依存するデータ | 更新方法 |
| --- | --- |
| ミップ | 編集した範囲の、ミップだけ、作り直す（[Heightmap LOD (Mips)](../lod/height-mip.md)） |
| 法線マップ | 編集範囲 + 1 画素の外側を、再計算する（法線は、隣の高さに依存するため） |
| チャンクの AABB | 編集範囲に、触れたチャンクの、最小・最大を、再計算する |
| 四分木のノード（CDLOD） | 影響する、ノードの最小・最大を、根まで、更新する |
| 物理の高さ場 | 当たり判定の、高さデータを、更新する |
| 配置（植生） | 高さが変わった範囲の、草・木を、置き直す |

```cpp
// 編集した範囲（ダーティ矩形）を、記録して、まとめて更新する。
struct DirtyRect { int x0, y0, x1, y1; };

void MarkDirty(DirtyRect& d, int x0, int y0, int x1, int y1) {
  d.x0 = std::min(d.x0, x0); d.y0 = std::min(d.y0, y0);
  d.x1 = std::max(d.x1, x1); d.y1 = std::max(d.y1, y1);
}

// フレームの終わりに、1 回だけ、まとめて更新する。
if (dirty.x1 >= dirty.x0) {
  const DirtyRect r = {dirty.x0 - 1, dirty.y0 - 1, dirty.x1 + 1, dirty.y1 + 1};  // 法線のため、1 画素広げる
  RecomputeNormals(r);
  RebuildMips(r);
  UpdateChunkBounds(r);
  UpdatePhysicsHeights(r);
  dirty = EmptyRect();
}
```

編集中は、**ブラシを動かすたびに、全部更新する必要はなく**、フレームの最後に、1 回まとめれば、十分です。

## 精度

| 項目 | 内容 |
| --- | --- |
| 編集中の形式 | `R32_FLOAT`。ブラシの 1 回の変化量は、非常に小さい（0.01 m 以下）。16 ビットだと、**変化が、丸められて、消える** |
| 保存の形式 | `R16_UNORM`。編集が終わったら、変換する |
| 誤差の蓄積 | 何度も、ならすと、**高さが、少しずつ、変化する**。保存前に、不要な、ならしを、しない |

## 元に戻す（アンドゥ）

地形の編集は、**数十回〜数百回のブラシ**を、繰り返します。アンドゥは、必須です。ただし、**高さマップ全体を、毎回コピーすると、メモリが足りません**。

| 方法 | 内容 |
| --- | --- |
| タイルの差分 | 編集で、変わったタイル（64×64 画素など）だけを、**変更前の値で保存**する。アンドゥは、保存したタイルを、書き戻す |
| ストローク単位 | マウスを押してから離すまでを、1 回の操作として、まとめる（細かい、1 フレームごとの変更では、ない） |
| 圧縮 | 差分は、変わっていない部分が多い。**圧縮して保存**する |

```cpp
struct UndoEntry {
  struct Tile { int tx, ty; std::vector<float> before; };
  std::vector<Tile> tiles;                  // 変更された、タイルの、変更前の値
};

// ブラシで、タイルに、初めて触れる前に、そのタイルの内容を、保存する。
void SaveTileBeforeEdit(UndoEntry& e, const HeightMap& h, int tx, int ty) {
  for (const auto& t : e.tiles) if (t.tx == tx && t.ty == ty) return;   // すでに、保存済み
  e.tiles.push_back({tx, ty, h.CopyTile(tx, ty)});
}
```

## ゲーム中の変形（ランタイム）

爆発の穴、掘削、建物の整地など、**ゲーム中に、地形を、変形させる**場合も、同じ仕組みです。ただし、次の点が、違います。

| 項目 | 内容 |
| --- | --- |
| 速さ | 1 フレームの中で、終わらせる（ブラシの適用は、軽い） |
| 同期 | 物理（当たり判定）と、見た目が、**同じ高さデータ**を、見ていること |
| ネットワーク | 変形の、**コマンド（位置・半径・強さ）**を、送る。高さマップは、送らない（決定的に、同じ結果にする） |
| 保存 | セーブ データには、**元の地形からの、差分**（編集コマンドの列、または、変更タイル）を、保存する |

''', before="## よくあるミス")
pg.Refs("terrain/heightmap-mesh/editing.md", [STAVA, GALIN, RTR, JOLT])

# ---------------------------------------------------------------- height query
pg.Dedup("terrain/heightmap-mesh/height-query.md")
pg.Add("terrain/heightmap-mesh/height-query.md", '''
## 双線形補間は、描画のメッシュと、ずれる

上の `SampleHeight` は、4 点から、**双線形補間**で、高さを求めます。ところが、描画される地形は、**格子のマスを、2 枚の三角形に分けた、折れ曲がった面**です。双線形補間の面は、**曲がった面（双曲放物面）**で、三角形の平面とは、違います。

| 方式 | 面の形 | 描画との一致 |
| --- | --- | --- |
| 双線形補間 | 4 点を通る、曲面 | マスの中心で、ずれる |
| 三角形で補間（重心座標） | 2 枚の平面 | **描画のメッシュと、完全に一致** |

ずれは、わずかですが、**足が地面に、めり込んだり、浮いたり**します。特に、**急な斜面**や、**高さマップの解像度が、粗い**場合は、目立ちます。キャラクターの足や、物の接地には、**メッシュと同じ三角形で、補間**する必要があります。

## 三角形に合わせた補間

マスを、**どの対角線で、分けているか**で、計算が変わります（[Grid Mesh](grid-mesh.md)）。

```text
対角線 A（左上 − 右下）           対角線 B（右上 − 左下）
a───b                            a───b
│╲  │                            │  ╱│
│ ╲ │                            │ ╱ │
c───d                            c───d
```

```cpp
// 三角形に合わせた高さの補間。(fx, fz) は、マスの中の位置（0〜1）。
// h00 = 左上(a), h10 = 右上(b), h01 = 左下(c), h11 = 右下(d)
float InterpolateTriangle(float h00, float h10, float h01, float h11,
                          float fx, float fz, bool diagonal_a) {
  if (diagonal_a) {
    // 対角線 a−d。a, c, d の三角形（左下側）と、a, d, b の三角形（右上側）
    if (fx <= fz) {
      // 左下側: a, c, d
      return h00 + (h11 - h01) * fx + (h01 - h00) * fz;
    } else {
      // 右上側: a, d, b
      return h00 + (h10 - h00) * fx + (h11 - h10) * fz;
    }
  } else {
    // 対角線 b−c。a, c, b の三角形（左上側）と、b, c, d の三角形（右下側）
    if (fx + fz <= 1.0f) {
      // 左上側: a, c, b
      return h00 + (h10 - h00) * fx + (h01 - h00) * fz;
    } else {
      // 右下側: b, c, d
      return h11 + (h01 - h11) * (1.0f - fx) + (h10 - h11) * (1.0f - fz);
    }
  }
}

float SampleHeightMatchingMesh(const HeightMap& map, float world_x, float world_z) {
  const float u = (world_x - map.origin_x) / map.cell_size;
  const float v = (world_z - map.origin_z) / map.cell_size;
  const int x0 = std::clamp(int(std::floor(u)), 0, map.width - 2);
  const int z0 = std::clamp(int(std::floor(v)), 0, map.height - 2);
  const float fx = u - x0, fz = v - z0;
  const bool diagonal_a = ((x0 + z0) & 1) == 0;       // 市松の貼り方と、同じ規則
  return InterpolateTriangle(map.At(x0, z0), map.At(x0 + 1, z0),
                             map.At(x0, z0 + 1), map.At(x0 + 1, z0 + 1), fx, fz, diagonal_a);
}
```

!!! warning "対角線の規則は、メッシュと、まったく同じにする"
    `diagonal_a` の判定が、描画のメッシュの貼り方と、1 つでも違うと、ずれが、残ります。規則を、**1 か所の関数にまとめて**、メッシュ作りと、高さの補間の、両方から、使います。

## 法線も、同じ三角形から

高さと同じ三角形から、**面の法線**も、求められます。足を、斜面に合わせて傾ける、キャラクターを、斜面に沿って、滑らせるときに使います。

```cpp
float3 NormalAt(const HeightMap& map, float world_x, float world_z) {
  const float e = map.cell_size;
  // 中央差分（なめらかな法線）。三角形の面の法線が欲しいなら、三角形の 3 点から、外積で求める。
  const float hl = SampleHeightMatchingMesh(map, world_x - e, world_z);
  const float hr = SampleHeightMatchingMesh(map, world_x + e, world_z);
  const float hd = SampleHeightMatchingMesh(map, world_x, world_z - e);
  const float hu = SampleHeightMatchingMesh(map, world_x, world_z + e);
  return Normalize({hl - hr, 2.0f * e, hd - hu});
}
```

## レイと地形の交差

「画面をクリックした場所の、地面」「弾が、地面に当たる位置」を求めるには、**レイと、高さ場の交差**を調べます。

### ① 一定の歩幅で、進む（レイマーチ）

レイに沿って、少しずつ進み、**レイの高さが、地面の高さを下回った所**を、交点とします。

```cpp
bool RaycastTerrain(const HeightMap& map, float3 origin, float3 dir, float max_dist,
                    float step, float3& hit) {
  float t = 0.0f;
  float prev_diff = origin.y - SampleHeightMatchingMesh(map, origin.x, origin.z);
  while (t < max_dist) {
    t += step;
    const float3 p = origin + dir * t;
    const float diff = p.y - SampleHeightMatchingMesh(map, p.x, p.z);
    if (diff < 0.0f && prev_diff >= 0.0f) {
      // 地面の下に入った。直前の位置との間で、二分探索して、交点を絞り込む。
      float lo = t - step, hi = t;
      for (int i = 0; i < 8; ++i) {
        const float mid = 0.5f * (lo + hi);
        const float3 q = origin + dir * mid;
        if (q.y - SampleHeightMatchingMesh(map, q.x, q.z) < 0.0f) hi = mid; else lo = mid;
      }
      hit = origin + dir * hi;
      return true;
    }
    prev_diff = diff;
  }
  return false;
}
```

歩幅が大きいと、**細い尾根を、飛び越えて、取りこぼします**。小さいと、遅くなります。**歩幅は、格子の間隔の、半分以下**が、目安です。

### ② マスを、1 つずつ進む（DDA）

Amanatides と Woo（1987）の方法で、レイが通る、**マスだけを、1 つずつ**たどり、各マスで、レイと 2 枚の三角形の交差を調べます。取りこぼしがなく、長いレイでも、**調べるマスの数は、距離に比例**するだけです。

| 方式 | 取りこぼし | 速さ | 実装 |
| --- | --- | --- | --- |
| 一定の歩幅 | 出ることがある | 歩幅が、小さいと遅い | 簡単 |
| マスを 1 つずつ（DDA） | **ない** | 速い | やや複雑 |
| 四分木の最大高さで、枝刈り | ない | **長いレイで、特に速い** | 複雑（最大高さのミップが、必要） |

長距離（狙撃、視線チェック）では、**最大高さのミップ**（[Heightmap LOD (Mips)](../lod/height-mip.md)）で、「このブロックの上を、レイが、通過するか」を、先に判定して、**大きく飛ばす**と、速くなります。

## 物理エンジンの高さ場

物理エンジンも、地形の当たり判定に使える**高さ場（heightfield）の形状**を、持っています（PhysX、Jolt など）。

| 項目 | 内容 |
| --- | --- |
| データ | 高さの配列（描画の高さマップと、同じ値を渡す） |
| 三角形の分け方 | エンジンごとに、決まっている。**描画と合わせる**（合わせられなければ、わずかなずれを、許容する） |
| 更新 | 地形を変形したら、高さ場の、**該当範囲を、更新**する |
| 穴 | 洞窟の入口などの、穴は、**材質の ID に、穴を表す値**を持たせて、表現する（エンジンによる） |

物理エンジンが、独自の補間を使う場合、**自分で、同じ補間を、実装して、見た目を、合わせる**のが、無難です。

## 範囲外と、穴

| 場合 | 扱い |
| --- | --- |
| 地形の外 | `clamp` で、端の高さを、そのまま使う。または、「地面がない」を返す |
| 穴（洞窟の入口） | 穴の画素は、`NaN` や、特別な値で、表す。**高さの補間で、穴の境目が、混ざらない**ように、4 点のどれかが穴なら、その三角形は、穴として扱う |
| チャンクの境界 | 隣のチャンクを、読み込んでいない間は、境界の画素を、**両側が、同じ値で持つ**（[Chunking](chunks.md)） |

''', before="## よくあるミス")
pg.Refs("terrain/heightmap-mesh/height-query.md", [AMANATIDES, ERICSON, RTR, JOLT])

# ---------------------------------------------------------------- normals
pg.Dedup("terrain/heightmap-mesh/normals.md")
pg.Add("terrain/heightmap-mesh/normals.md", '''
## 中央差分の式を、導く

高さを `h(x, z)` とする、曲面の法線を、求めます。曲面 `y = h(x, z)` の、x 方向の接線は `(1, ∂h/∂x, 0)`、z 方向の接線は `(0, ∂h/∂z, 1)` です。法線は、2 つの接線の外積です。

```text
n = (1, ∂h/∂x, 0) × (0, ∂h/∂z, 1)
  = (∂h/∂x × 1 − 0 × ∂h/∂z,  0 × 0 − 1 × 1,  1 × ∂h/∂z − ∂h/∂x × 0)
  = (∂h/∂x, −1, ∂h/∂z)
```

上向きが法線の向きなので、符号を反転して、`n = (−∂h/∂x, 1, −∂h/∂z)` を正規化します。**傾きが大きいほど、法線は、傾く**ことが、読み取れます。

**偏微分を、隣の高さの差で、近似**します。画素の間隔（ワールドの距離）を `s` とすると、

```text
∂h/∂x ≈ (h_右 − h_左) / (2 s)
∂h/∂z ≈ (h_上 − h_下) / (2 s)

n = normalize( −(h_右 − h_左) / (2 s),  1,  −(h_上 − h_下) / (2 s) )
  = normalize( h_左 − h_右,  2 s,  h_下 − h_上 )          ← 全体に 2s を掛けただけ
```

最後の形が、上のコードの `float3(hl - hr, 2.0 * texel_world, hd - hu)` です。**`2 s` を、掛け忘れる、または、間違えると、斜面が、実際より、急に、または、なだらかに見えます**。

| 間違い | 結果 |
| --- | --- |
| `s` を、UV の 1 テクセル（0〜1 の値）にしてしまう | 傾きが、極端に急になる。地形が、ほぼ真っ平らな法線に見える、または、逆 |
| 高さのスケール（`height_scale`）を、掛け忘れる | 傾きが、実際より、緩やかになる |
| 高さを、メートルでなく、0〜1 のまま使う | 同上 |

**高さも、画素の間隔も、同じ単位（メートル）で、計算する**ことが、肝心です。

## 差分の取り方

### 2 点（片側差分）、4 点（中央差分）、8 点（Sobel）

| 方式 | 読む画素 | 特徴 |
| --- | --- | --- |
| 前方差分 | 自分と、右・上の 2 つ | 安い。**画素の半分だけ、ずれる**（位置が、中心と合わない） |
| 中央差分 | 左・右・下・上の 4 つ | 標準。位置が、中心に合う |
| Sobel | 周りの 8 つ | **細かいノイズを、ならす**。やや重い |

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

Sobel は、**重みの合計が 8**（中央差分は、2）なので、`2 s` ではなく、`8 s` を使います。

## 法線を、どこで計算するか

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| 頂点で計算 | 頂点シェーダーで、高さマップを、4 回読んで、法線を作り、補間して渡す | ピクセル シェーダーが、軽い | **頂点が粗い（遠景）と、細かい起伏が、法線に、反映されない** |
| ピクセルで計算 | ピクセル シェーダーが、高さマップを、4 回（または 8 回）読む | **頂点が粗くても、細かい陰影が、出る** | ピクセルごとに、テクスチャの読み込みが、増える |
| 法線マップを事前に作る | 高さマップから、法線マップ（`R8G8`、または `BC5`）を作っておく。ピクセルで、1 回読む | **最も速い**。LOD が変わっても、陰影が、変わらない | メモリが、増える。高さを編集したら、更新が、必要 |

**地形では、法線マップを、事前に作る**方式が、一般的です。**LOD で頂点が間引かれても、法線マップは、同じ解像度**なので、**LOD の切り替えで、陰影が、ポップしません**。

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

地形の法線は、**常に、上向き（y > 0）**なので、x と z だけを保存して、y を、`sqrt(1 − x² − z²)` で、復元できます。2 チャンネルで済むので、メモリが、2/3 になります。

| 形式 | 精度 | メモリ（1 画素） |
| --- | --- | --- |
| `R8G8_SNORM` | 8 ビット。**なだらかな斜面で、段々（バンディング）が、見える** | 2 バイト |
| `R16G16_SNORM` | 16 ビット。ほぼ、問題ない | 4 バイト |
| `BC5_SNORM` | 圧縮（4:1）。色の成分ごとに、独立して、圧縮 | 1 バイト（平均） |

## 精度とバンディング

高さマップが、**8 ビット**だと、高さが 256 段階しかなく、なだらかな斜面で、**階段状**になります。階段の、段差の部分で、法線が、急に変わり、**縞模様の陰影**が出ます。

| 対策 | 内容 |
| --- | --- |
| 高さを、16 ビットにする | 根本的な解決。`R16_UNORM`（[Heightmap LOD (Mips)](../lod/height-mip.md)） |
| 高さに、ノイズを足す（ディザ） | 8 ビットのまま、見た目の縞を、ぼかす |
| 法線を、バイリニアで、補間する | 高さの、階段の角を、ならす |
| 法線マップの、解像度を、高さマップより低くする | 階段を、ならす（平均化） |

## 法線マップの、ミップマップ

法線マップを、**そのまま、ミップマップにすると、問題**があります。法線ベクトルを、平均すると、**長さが、1 より短く**なります。

```text
平均した法線 = (n1 + n2 + n3 + n4) / 4          → 長さが、1 より短い
```

| 状況 | 平均した法線の長さ |
| --- | --- |
| 4 つが、同じ向き（平らな場所） | 1.0 |
| 4 つが、ばらばら（ごつごつした場所） | 小さい（0.5 など） |

このことを使うと、**平均した法線の長さが短いほど、表面が、ごつごつしている**と分かります。この長さを、**スペキュラーの粗さに、反映する**のが、Toksvig の方法（2005）です。遠くの岩場が、**光沢の、ちらつきなく、つや消しに見える**ようになります。

```hlsl
// 平均した法線の長さから、粗さを補正する（Toksvig）。
float ToksvigRoughness(float3 averaged_normal, float roughness) {
  float len = length(averaged_normal);
  float ft = len / lerp(len, 1.0, roughness);       // 簡略化した式
  return sqrt(1.0 - ft * ft + roughness * roughness * ft * ft);   // 近似。実装によって異なる
}
```

実装は、自分のライティング モデルの粗さの定義に合わせて、調整します。**法線を、`normalize` する前の、長さを、取っておく**ことが、重要です。

## 傾き（スロープ）の値

法線から、**地面の傾き**が、すぐに分かります。

```hlsl
float slope_cos = n.y;                         // 1 = 水平、0 = 垂直
float slope_deg = degrees(acos(saturate(n.y)));
```

スプラットの重み（岩、雪）の条件（[Splat Weights](../texturing/weights.md)）や、**歩ける斜面の判定**（登れる限界の角度）に、使います。

''', before="## よくあるミス")
pg.Refs("terrain/heightmap-mesh/normals.md", [MIKKELSEN, TOKSVIG, RTR, "Microsoft Learn, \"DXGI_FORMAT\"（`R16G16_SNORM`、`BC5_SNORM` などの形式）"])

pg.Refs("terrain/heightmap-mesh/index.md", [STRUGAR, ULRICH, RTR, FORSYTH])
print("ok")
