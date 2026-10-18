import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

PELZER = '''Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004（草の板ポリ、風、クロス ブレンド）'''
SOUSA = '''Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）'''
WOHLLAIB = '''Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021'''
BOULANGER = '''Boulanger, Pattanaik, Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009'''
WIHLIDAL = '''Wihlidal, "Optimizing the Graphics Pipeline with Compute", Game Developers Conference 2016（フラスタム、背面、オクルージョンの、GPU カリング）'''
HAAR = '''Haar, Aaltonen, "GPU-Driven Rendering Pipelines", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
CARUCCI = '''Carucci, "Inside Geometry Instancing", GPU Gems 2, Chapter 3, 2005'''
BRUCKS = '''Brucks, "Octahedral Impostors", 2018（8 面体のマッピングを使った、インポスターの作り方）'''
DECORET = '''Décoret, Durand, Sillion, Dorsey, "Billboard Clouds for Extreme Model Simplification", ACM Transactions on Graphics (SIGGRAPH 2003)'''
CASTANO = '''Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正する）'''
WYMAN = '''Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017'''
BARRE = '''Barré-Brisebois, Bouchard, "Approximating Translucency for a Fast, Cheap and Convincing Subsurface Scattering Look", Game Developers Conference 2011'''
WEBER = '''Weber, Penn, "Creation and Rendering of Realistic Trees", SIGGRAPH 1995'''
PRUSINKIEWICZ = '''Prusinkiewicz, Lindenmayer, "The Algorithmic Beauty of Plants", Springer, 1990（L システム）'''
D3D11_INDIRECT = '''Microsoft Learn, "ID3D11DeviceContext::DrawIndexedInstancedIndirect"'''
D3D11_COPYCOUNT = '''Microsoft Learn, "ID3D11DeviceContext::CopyStructureCount"'''

# ---------------------------------------------------------------- grass shape
pg.Dedup("terrain/vegetation/grass-shape.md")
pg.Add("terrain/vegetation/grass-shape.md", '''
## 草 1 本を、どう作るか

草は、**数が多い**（1 平方メートルに、数百本）ので、**1 本あたりの、三角形の数が、すべてを決めます**。1 本を、3 枚の三角形で作ると、100 万本で、300 万三角形です。

| 方式 | 三角形 / 本 | 見た目 | 風の表現 |
| --- | --- | --- | --- |
| クロス板（十字に交差した 2 枚、絵を貼る） | 4 | 密集した草むらに見える。横から見ると、板 | 先端を、揺らせる |
| 房（3〜5 本の葉を、扇形に） | 6〜10 | 近景でも、まずまず | 房全体が、揺れる |
| 1 本ずつの葉（細い帯） | 3〜14 | 近景で、1 本ずつ、見える | **1 本ごとに、曲がる** |
| ビルボード | 2 | 遠景用 | 動かない |

## 葉 1 本の、メッシュ

1 本の葉は、**根元から先端へ向かう、細い帯**です。帯を、数段に分けて、**根元は太く、先端は細く**します。

```text
先端   ▲        ← 頂点 1 つ（三角形）
      ╱ ╲
     ╱───╲      ← セグメント 3（幅 小）
    │     │
    │─────│     ← セグメント 2
    │     │
    │─────│     ← セグメント 1
    │     │
根元 └─────┘     ← セグメント 0（幅 大）
```

| セグメント数 | 頂点数 | 三角形 | 用途 |
| --- | --- | --- | --- |
| 1 | 3 | 1 | 遠景（三角形 1 枚の、葉） |
| 3 | 7 | 5 | 中景 |
| 5 | 11 | 9 | 近景 |
| 7 | 15 | 13 | 最近景（曲がりが、なめらか） |

距離に応じて、**セグメント数が、違うメッシュに、切り替えます**。遠景では、三角形 1 枚でも、画面上では、細い線にしか見えません。

### 頂点の位置の、決め方

頂点は、**根元から、先端への高さ `t`（0〜1）**と、**左右（−1、+1）**で決まります。

```hlsl
// 葉の頂点を、シェーダーの中で、組み立てる（頂点バッファを持たない方法）。
// vertex_id から、段（level）と、左右（side）を取り出す。
static const int kSegments = 5;

float3 BladeVertex(uint vertex_id, float width, float height, float bend) {
  uint level = vertex_id / 2;                 // 0 〜 kSegments
  float side = (vertex_id & 1) ? 1.0 : -1.0;
  float t = float(level) / kSegments;

  // 幅: 根元で太く、先端で細く
  float w = width * (1.0 - t * t);
  // 曲がり: 先端ほど、前へ倒れる（二次曲線）
  float forward = bend * t * t * height;
  float up = height * (t - 0.5 * bend * bend * t * t * t);   // 曲がった分だけ、少し低くなる

  return float3(side * w * 0.5, up, forward);
}
```

**曲がりを、2 次以上の曲線**（`t²`）にすると、**根元は、まっすぐ立ち、先端だけが、しなる**、草らしい形になります。

## 頂点シェーダーで、組み立てる

草を、**頂点バッファのメッシュにしない**方法も、あります。**インスタンスごとの、パラメーター（位置、向き、高さ、曲がり）から、頂点シェーダーが、直接、頂点を計算**します。

| 項目 | 内容 |
| --- | --- |
| 頂点バッファ | **不要**（`SV_VertexID` だけ使う）。インデックス バッファも、規則的なので、定数で組める |
| インスタンス | 位置、向き、高さ、曲がり、色の、ばらつき |
| 利点 | **LOD ごとに、頂点数が違う**メッシュを、頂点バッファの切り替えなしで、`DrawInstanced(頂点数, インスタンス数)` で描ける |

```cpp
// 頂点バッファなしで描く。頂点数は、段数から決まる。
context->IASetInputLayout(nullptr);
context->IASetVertexBuffers(0, 0, nullptr, nullptr, nullptr);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLESTRIP);   // 帯は、ストリップで表現できる
const UINT vertices_per_blade = (kSegments + 1) * 2 + 1;                   // 先端は、1 つ追加
context->DrawInstanced(vertices_per_blade, instance_count, 0, 0);
```

三角形ストリップは、**帯**（左右の頂点を、交互に並べる）と、相性が良いです。

## 向きと、カメラ

葉は、**ただの帯**なので、**横から見ると、細い線**になります（帯の幅の方向と、視線が、垂直のとき、厚みがゼロ）。見えなくなる問題の対策を、示します。

| 問題 | 対策 |
| --- | --- |
| 帯を、真横から見ると、消える | **カメラの向きに、少しだけ、帯を回す**（ビルボード的に、幅の向きを、視線に垂直に近づける）。ただし、全部を向けると、不自然 |
| 帯の裏面が、描かれない | カリングを、無効にして、**両面**を描く。裏面の法線は、反転する |
| 近づくと、帯が、細すぎる | 幅に、**最小値**を持たせる。遠くでは、幅を、**少し太く**する（細すぎると、エイリアシングで消える） |

```hlsl
// 視線に応じて、帯の幅を、少しだけ、広げる（真横から見ても、消えないように）。
float3 view_dir = normalize(camera_position - world_pos);
float side_on = 1.0 - abs(dot(view_dir, blade_normal));   // 真横から見るほど 1
world_pos += blade_right * side * side_on * thicken_amount;
```

## 色

草の色の、**ばらつき**と、**根元の暗さ**が、見た目の、半分を決めます。

| 要素 | 内容 |
| --- | --- |
| 根元の色 | 暗く、地形のテクスチャの色に、合わせる。**境目が消える**（地形との、馴染み） |
| 先端の色 | 明るい。**高さ `t` で、補間** |
| 本ごとの、ばらつき | 位置から、決定的な乱数で、色相と明度を、少しずらす |
| 地面の色を、拾う | 草の根元の位置で、**地形のカラー マップ**を読み、草の色に、混ぜる |

```hlsl
float3 root_color = terrain_albedo.SampleLevel(g_linear_clamp, terrain_uv, 0).rgb * 0.5;  // 地面の色を、暗くして
float3 tip_color = lerp(root_color, float3(0.55, 0.75, 0.25), 0.8);                        // 先端は、明るい緑
float3 color = lerp(root_color, tip_color, t) * (0.9 + 0.2 * instance_random);             // 1 本ずつの、ばらつき
```

## 近年の、実装例

Wohllaib（2021）は、『Ghost of Tsushima』の草を、**1 本ずつの葉を、計算シェーダーで、曲線として、生成**し、描画する方法を、紹介しています。数百万本の草を、**GPU 上で、LOD ごとに、頂点数を変えて**、描いています。

| 項目 | 内容 |
| --- | --- |
| 葉の形 | ベジェ曲線（曲がった線）に、沿って、帯を作る |
| LOD | 距離に応じて、**頂点数を、減らす**。遠くは、少ない頂点で、細く |
| 風 | 葉の曲線の、制御点を、風で動かす |
| 地形との馴染み | 草の色を、地形の色から取り、根元で、境目を消す |

詳細は、GDC の発表を参照してください。ここでは、**「1 本ずつの葉を、曲線として扱い、LOD で、頂点数を変える」**という、考え方を、押さえてください。

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/grass-shape.md", [PELZER, WOHLLAIB, BOULANGER, SOUSA])

# ---------------------------------------------------------------- instancing
pg.Dedup("terrain/vegetation/instancing.md")
pg.Add("terrain/vegetation/instancing.md", '''
## なぜ、普通に描くと、遅いのか

草を 1 本ずつ、`DrawIndexed` で描くと、**ドローコールが、数十万回**になります。ドローコール 1 回ごとに、CPU が、状態の設定と、ドライバーの処理を行うので、**1 回あたり数マイクロ秒**でも、積もると、フレームを、使い切ります。

| 方式 | ドローコール | CPU の負荷 |
| --- | --- | --- |
| 1 本ずつ描く | 数十万 | 非常に高い |
| 区画ごとに、まとめる | 数百 | 中程度（メッシュの結合が要る） |
| インスタンシング | **1〜数回** | 低い |
| GPU 駆動（間接描画） | **1 回**（インスタンス数も、GPU が決める） | 最小 |

インスタンシングの、基本的な考え方は、Carucci（2005）が、整理しています。

## インスタンスのデータ

```cpp
// 1 本の草のデータ（32 バイト）。位置・向き・大きさ・色。
struct GrassInstance {
  float3 position;      // 12 バイト
  float rotation;       // 4: Y 軸の回転（ラジアン）
  float scale;          // 4
  float height;         // 4
  float color_variation;// 4
  float bend;           // 4
};
static_assert(sizeof(GrassInstance) == 32);
```

インスタンスは、**構造化バッファ（StructuredBuffer）**に、並べます。頂点シェーダーが、`SV_InstanceID` で、自分の番号を受け取って、バッファから読みます。

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = UINT(sizeof(GrassInstance) * max_instances);
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 描画で読み、カリングで書く
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
desc.StructureByteStride = sizeof(GrassInstance);
device->CreateBuffer(&desc, nullptr, &instance_buffer);

D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_UNKNOWN;
srv.ViewDimension = D3D11_SRV_DIMENSION_BUFFER;
srv.Buffer.NumElements = max_instances;
device->CreateShaderResourceView(instance_buffer.Get(), &srv, &instance_srv);
```

## 間接描画（GPU 駆動）

**カリングを GPU で行う**と、「何個、描くか」が、CPU には、分かりません（GPU が、計算してから、決まる）。CPU に読み戻すと、**GPU の処理を、待つことになり、遅くなります**。そこで、**描画の引数を、GPU が書き、そのまま、描画に使う**のが、間接描画です。

### 全体の流れ

```text
① 全インスタンス（StructuredBuffer）
        ↓  計算シェーダー（カリング）
② 見えるインスタンスだけを、AppendStructuredBuffer に詰める
        ↓  CopyStructureCount（個数を、引数バッファへコピー）
③ 引数バッファ [IndexCount, InstanceCount, ...]
        ↓  DrawIndexedInstancedIndirect
④ 見えるものだけを描く
```

### 引数バッファ

```cpp
// DrawIndexedInstancedIndirect の引数（5 個の UINT）
struct DrawArgs {
  UINT index_count_per_instance;
  UINT instance_count;            // ← GPU が書く
  UINT start_index_location;
  INT base_vertex_location;
  UINT start_instance_location;
};

D3D11_BUFFER_DESC args_desc = {};
args_desc.ByteWidth = sizeof(DrawArgs);
args_desc.Usage = D3D11_USAGE_DEFAULT;
args_desc.MiscFlags = D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS;      // 間接描画の引数として使う
DrawArgs init = {blade_index_count, 0, 0, 0, 0};
D3D11_SUBRESOURCE_DATA data = {&init};
device->CreateBuffer(&args_desc, &data, &args_buffer);
```

### 見えたものを、詰めるバッファ

```cpp
D3D11_BUFFER_DESC vis_desc = {};
vis_desc.ByteWidth = UINT(sizeof(GrassInstance) * max_instances);
vis_desc.Usage = D3D11_USAGE_DEFAULT;
vis_desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
vis_desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
vis_desc.StructureByteStride = sizeof(GrassInstance);
device->CreateBuffer(&vis_desc, nullptr, &visible_buffer);

D3D11_UNORDERED_ACCESS_VIEW_DESC uav = {};
uav.Format = DXGI_FORMAT_UNKNOWN;
uav.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
uav.Buffer.NumElements = max_instances;
uav.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_APPEND;                  // Append バッファ（カウンター付き）
device->CreateUnorderedAccessView(visible_buffer.Get(), &uav, &visible_uav);
```

### 毎フレームの処理

```cpp
// ① カウンターを 0 に戻して、カリングを実行する
const UINT zero = 0;
context->CSSetShader(cull_cs.Get(), nullptr, 0);
context->CSSetShaderResources(0, 1, instance_srv.GetAddressOf());
context->CSSetUnorderedAccessViews(0, 1, visible_uav.GetAddressOf(), &zero);   // 初期カウント 0
context->Dispatch((instance_count + 63) / 64, 1, 1);

// UAV を外す（SRV として読むため）
ID3D11UnorderedAccessView* null_uav = nullptr;
context->CSSetUnorderedAccessViews(0, 1, &null_uav, nullptr);

// ② カウンターの値（見えた個数）を、引数バッファの instance_count へコピーする
context->CopyStructureCount(args_buffer.Get(), offsetof(DrawArgs, instance_count), visible_uav.Get());

// ③ 見えたものを、間接描画する
context->VSSetShaderResources(0, 1, visible_srv.GetAddressOf());
context->DrawIndexedInstancedIndirect(args_buffer.Get(), 0);
```

この流れでは、**CPU は、見えた個数を、一度も読みません**。GPU が、自分で決めた個数を、そのまま描画に、使います。

## 描画のシェーダー

```hlsl
struct GrassInstance {
  float3 position; float rotation;
  float scale; float height; float color_variation; float bend;
};
StructuredBuffer<GrassInstance> g_instances : register(t0);

cbuffer FrameCB : register(b0) { float4x4 view_proj; float3 camera_position; float time; };

struct VSOut {
  float4 position : SV_Position;
  float3 color : COLOR;
};

VSOut main(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  GrassInstance inst = g_instances[instance_id];
  float3 local = BladeVertex(vertex_id, 0.05 * inst.scale, inst.height, inst.bend);

  // Y 軸の回転
  float s = sin(inst.rotation), c = cos(inst.rotation);
  float3 rotated = float3(local.x * c + local.z * s, local.y, -local.x * s + local.z * c);

  VSOut o;
  o.position = mul(float4(inst.position + rotated, 1.0), view_proj);
  o.color = lerp(float3(0.1, 0.2, 0.05), float3(0.5, 0.75, 0.2), local.y / inst.height)
          * (0.9 + 0.2 * inst.color_variation);
  return o;
}
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| 順序 | Append バッファの、並びは、**スレッドの実行順**で決まる（毎フレーム、順序が変わる）。**順序に依存する処理**（半透明の、ソート）には、使えない |
| ドローコールを減らしすぎない | 種類（草・花・低木）が、違うメッシュは、別のドローコール。1 種類につき 1 回 |
| インスタンスの総数 | 数百万本を超えると、全部の、カリングが、重い。**区画ごとに、まとめて、粗いカリングを先に行う**（[Vegetation Culling](culling.md)） |
| `SV_InstanceID` の限界 | インスタンスの数が、65,535 を超えても、問題ない（32 ビット）。ただし、1 回の `Dispatch` の、スレッド グループ数に、上限（65,535）がある。数が、多いなら、複数回に分ける |
| デバッグ | 間接描画は、中身が見えにくい。**ステージング バッファに、コピーして、読み戻す**デバッグ用の経路を、用意しておく |

## 間接描画を、使わない方法

DirectX 11 が使えない環境（古い GPU）や、シンプルな実装では、**CPU でカリングして、見えるものだけを、インスタンス バッファに書く**方法も、あります。

```cpp
// CPU 側で、見えるインスタンスだけを集めて、毎フレーム、書き込む（草が、数万本までなら、十分）。
visible.clear();
for (const GrassInstance& g : all) if (IsVisible(g)) visible.push_back(g);
D3D11_MAPPED_SUBRESOURCE m;
context->Map(dynamic_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &m);
memcpy(m.pData, visible.data(), visible.size() * sizeof(GrassInstance));
context->Unmap(dynamic_buffer.Get(), 0);
context->DrawIndexedInstanced(index_count, UINT(visible.size()), 0, 0, 0);
```

| 方式 | 向く規模 | 長所 | 短所 |
| --- | --- | --- | --- |
| CPU でカリング | 数万本まで | 実装が簡単 | CPU の負荷が、本数に比例する。毎フレーム、転送する |
| GPU でカリング ＋ 間接描画 | 数十万〜数百万本 | CPU の負荷が、ほぼゼロ | 実装が複雑。デバッグが難しい |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/instancing.md", [CARUCCI, HAAR, WIHLIDAL, D3D11_INDIRECT, D3D11_COPYCOUNT])

# ---------------------------------------------------------------- culling
pg.Dedup("terrain/vegetation/culling.md")
pg.Add("terrain/vegetation/culling.md", '''
## カリングを、段階にする

草の本数は、**数十万〜数百万**です。**全インスタンスを、1 本ずつ**調べると、調べるだけで、重くなります。**大きな単位で、先に捨て、残りだけを、細かく調べる**、段階的なカリングにします。

| 段階 | 単位 | 方法 | 捨てる量 |
| --- | --- | --- | --- |
| ① 区画（タイル） | 数十メートル四方 | 視錐台、距離。区画の AABB で判定 | 画面外の、ほとんど |
| ② 区画の内部 | 区画内の全インスタンス | 計算シェーダーで、1 本ずつ、距離・視錐台 | 残りの、無駄な分 |
| ③ オクルージョン | 区画、またはインスタンス | Hi-Z バッファで、山や建物の、裏を、捨てる | 遮られた分 |

**区画ごとに、草のインスタンスを、事前に、並べておく**と、①で捨てた区画の、インスタンスには、触れずに済みます。

```cpp
struct GrassTile {
  BoundingBox bounds;           // 草の高さまで含めた AABB
  uint32_t first_instance;      // 全インスタンス バッファの中の、この区画の開始位置
  uint32_t instance_count;
};

// ① 区画のカリング（CPU）。見える区画の、インスタンス範囲を、集める。
std::vector<uint2> ranges;
for (const GrassTile& t : tiles) {
  if (DistanceToAabb(camera.position, t.bounds) > max_distance) continue;
  if (!Visible(camera.frustum, t.bounds)) continue;
  ranges.push_back({t.first_instance, t.instance_count});
}
// ② この範囲だけを、計算シェーダーで、1 本ずつ調べる。
```

## 距離カリングと、フェード

遠くの草は、**小さくて、見えません**。ただし、**ある距離で、いきなり消すと、境目が、目立ちます**。

| 方法 | 内容 |
| --- | --- |
| 距離で、一斉に消す | 簡単。**境目が、はっきり見える** |
| 草の高さを、縮めて、消す | 距離で、スケールを 0 に近づけて、**地面に、沈むように**消す |
| 密度を、間引く（確率的な消し方） | 距離が遠いほど、**一部の草だけ**描く。草 1 本ごとの、乱数との比較で、決める |
| 面積を、補う | 間引いた分、残った草を、**太く**する（草原の、密度の印象を、保つ） |

```hlsl
// 距離に応じて、草の描画する確率を下げる。草 1 本ごとに、決まった乱数を使うので、フレームで、ちらつかない。
float DistanceKeepProbability(float dist, float fade_start, float fade_end) {
  return 1.0 - smoothstep(fade_start, fade_end, dist);
}

[numthreads(64, 1, 1)]
void CullGrass(uint3 id : SV_DispatchThreadID) {
  if (id.x >= instance_count) return;
  GrassInstance g = g_all_instances[id.x];

  float dist = distance(g.position, camera_position);
  if (dist > fade_end) return;                                  // 遠すぎる

  // 1 本ごとに、固定の乱数（0〜1）。確率より小さい物だけ、描く。
  float keep = DistanceKeepProbability(dist, fade_start, fade_end);
  if (g.color_variation > keep) return;                         // 乱数の代わりに、固定の値を使う

  // 間引いた分だけ、残りを太くする（面積の保存）
  g.scale *= 1.0 / max(sqrt(keep), 0.3);

  if (!SphereInFrustum(g.position + float3(0, g.height * 0.5, 0), g.height)) return;

  g_visible.Append(g);
}
```

「**1 本ごとの固定の乱数**」を使うことが、重要です。フレームごとに、乱数を引き直すと、**毎フレーム、違う草が消えて、ちらつきます**。

## 視錐台カリング

計算シェーダー内で、草の**球**（位置 + 高さの半分を、中心）が、視錐台の 6 平面の、内側にあるかを調べます。

```hlsl
cbuffer CullCB : register(b0) {
  float4 frustum_planes[6];       // xyz = 法線（内向き）、w = 距離
  float3 camera_position;
  float fade_start, fade_end;
  uint instance_count;
};

bool SphereInFrustum(float3 center, float radius) {
  [unroll] for (int i = 0; i < 6; ++i) {
    if (dot(frustum_planes[i].xyz, center) + frustum_planes[i].w < -radius) return false;
  }
  return true;
}
```

平面は、**カメラの、視錐台の行列から、CPU で、1 回だけ計算**して、定数バッファで、渡します。

## オクルージョン カリング（Hi-Z）

山、建物、崖の**裏側の草**は、見えないのに、描いています。**深度バッファの、ミップマップ（Hi-Z、各ミップが、4 画素の最も遠い深度）**を使って、「草の周りの球が、完全に、手前の物に、隠れているか」を、判定します。

| 手順 | 内容 |
| --- | --- |
| ① 前のフレームの、深度から、Hi-Z を作る | 深度のミップを、**最大値（遠い方）**で、縮める |
| ② 草の球を、画面に投影する | 球が覆う、画面上の範囲（矩形）と、球の最も近い深度を求める |
| ③ 範囲の大きさに合う、Hi-Z のミップを、読む | 矩形全体が、1 画素に収まるミップ |
| ④ 比較 | 球の最も近い深度が、Hi-Z の深度**より遠い**なら、隠れている |

```hlsl
Texture2D<float> g_hiz : register(t1);        // 前のフレームの深度の、Hi-Z（ミップつき）

bool OccludedByHiZ(float3 center, float radius) {
  // 球を、画面に投影した、矩形を求める（簡略化: 中心と半径から）
  float4 clip = mul(float4(center, 1), view_proj);
  float2 ndc = clip.xy / clip.w;
  float2 uv = ndc * float2(0.5, -0.5) + 0.5;
  float screen_radius = radius * proj_scale / clip.w;       // 画面上の半径（UV 単位）

  // 矩形の大きさに合う、ミップを選ぶ
  float2 size_px = screen_radius * 2.0 * hiz_size;
  float mip = ceil(log2(max(size_px.x, size_px.y)));

  // 矩形の四隅の深度の、最大（最も遠い）を取る
  float2 corner = screen_radius;
  float d = max(max(g_hiz.SampleLevel(g_point, uv + float2(-corner.x, -corner.y), mip),
                    g_hiz.SampleLevel(g_point, uv + float2( corner.x, -corner.y), mip)),
                max(g_hiz.SampleLevel(g_point, uv + float2(-corner.x,  corner.y), mip),
                    g_hiz.SampleLevel(g_point, uv + float2( corner.x,  corner.y), mip)));

  // 球の最も近い点の、深度（クリップ空間の z/w）
  float nearest = (clip.z - radius) / (clip.w - radius);
  return nearest > d;     // 球の方が遠い → 隠れている（深度は、遠いほど大きい通常の設定）
}
```

| 注意点 | 内容 |
| --- | --- |
| 前のフレームの深度 | 今のフレームの深度は、まだ、無い。**1 フレーム前の深度**を使うので、**カメラが速く動くと、わずかに、取りこぼす**。球を、少し大きめに取る |
| 草は、小さい | 草 1 本の、オクルージョンは、効果が小さい。**区画の AABB に、行う**のが、現実的 |
| 逆 Z | 深度の方向を、逆にしている場合（遠いほど、小さい）は、比較の向きと、ミップの縮め方（最小値）を、逆にする |

地形が、山岳地帯の場合、**山の裏の、草の区画を、まとめて捨てる**と、大きく減らせます。

## カリングの結果を、確かめる

| 方法 | 内容 |
| --- | --- |
| 見えた本数を、表示する | `CopyStructureCount` の値を、読み戻して（デバッグ時のみ）、画面に出す |
| カリングを、カメラから切り離す | 別のカメラ（デバッグ カメラ）で、見ながら、本来のカメラで、カリングする。**捨てすぎ**が、すぐ、分かる |
| 色で、区別する | 区画ごとに、色を変えて、描く。境目の、不自然なところが、見える |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/culling.md", [WIHLIDAL, HAAR, WOHLLAIB, "Hill, Collin, \"Practical, Dynamic Visibility for Games\", GPU Pro 2, 2011（Hi-Z によるオクルージョン カリング）"])

# ---------------------------------------------------------------- wind
pg.Dedup("terrain/vegetation/wind.md")
pg.Add("terrain/vegetation/wind.md", '''
## 風を、3 つの層で考える（Crysis の方法）

Sousa（2007）は、Crysis の植生の、揺れを、**3 つの層**に分けて、整理しました。

| 層 | 動く部分 | 動きの特徴 | 周波数 |
| --- | --- | --- | --- |
| 主な曲がり（main bending） | 木全体（幹の曲がり） | 大きく、ゆっくり。風の向きに、傾く | 低い |
| 枝の揺れ（branch bending） | 枝 | 中くらい。枝ごとに、位相が違う | 中くらい |
| 葉のはためき（leaf flutter） | 葉の端 | 小さく、速く。細かく震える | 高い |

3 つを足すと、**幹はゆっくり、枝は中くらい、葉は細かく**揺れる、自然な動きになります。**1 つの、サイン波だけでは、機械的**に見えます。

## それぞれの層の、頂点への情報

どの頂点が、どの層で動くかは、**頂点カラー**に、焼き込んでおきます（美術側で、調整できる）。

| 頂点カラー | 内容 |
| --- | --- |
| R | 主な曲がりの、強さ（根元 0、先端 1。**2 乗**して、使う） |
| G | 枝の、位相のずれ（枝ごとに、違う値を塗る） |
| B | 葉の、はためきの、強さ（葉の端が 1、枝に近いところが 0） |
| A | 枝の、揺れの、強さ |

```hlsl
float3 ApplyTreeWind(float3 world_pos, float3 vertex_color, float2 wind_dir, float wind_strength, float time) {
  // ① 主な曲がり: 木全体が、風の向きに、ゆっくり傾く。根元から先端へ、2 乗で強くなる。
  float main_phase = time * 0.7 + dot(world_pos.xz, wind_dir) * 0.05;
  float main_bend = (sin(main_phase) * 0.5 + 0.5 + 0.3) * wind_strength;
  float3 offset = float3(wind_dir.x, 0, wind_dir.y) * main_bend * vertex_color.r * vertex_color.r;

  // ② 枝: 枝ごとの位相で、上下左右に揺れる。
  float branch_phase = time * 2.0 + vertex_color.g * 6.2831;
  offset += float3(sin(branch_phase), 0.3 * sin(branch_phase * 1.3), cos(branch_phase * 0.9))
          * vertex_color.a * 0.1 * wind_strength;

  // ③ 葉: 速く、細かく震える。
  float leaf_phase = time * 12.0 + dot(world_pos, float3(1.7, 2.3, 3.1));
  offset += float3(sin(leaf_phase), sin(leaf_phase * 1.4 + 1.0), sin(leaf_phase * 0.8 + 2.0))
          * vertex_color.b * 0.02 * wind_strength;

  return world_pos + offset;
}
```

!!! warning "頂点をずらしたら、長さを保つ"
    枝や幹を、単純に、平行移動すると、**枝が、伸びて**見えます。根元からの、**長さを、保つ**ように、補正すると、自然に、見えます。曲がる量が小さいときは、気にならない程度です。

## 草の風

草は、**1 本が、小さい**ので、層は 1 つで十分です。ただし、**位置ごとに、位相をずらす**ことが、肝心です。そうしないと、**すべての草が、同時に、同じ動き**になり、不自然です。

```hlsl
float3 ApplyGrassWind(float3 world_pos, float height_t, float2 wind_dir, float strength, float time) {
  // 位置と時間から、位相を決める。風の向きに沿って、波が、渡っていく。
  float phase = dot(world_pos.xz, wind_dir) * 0.4 + time * 2.0;
  // 周波数の違う波を、足して、単調さを消す。
  float sway = sin(phase) + 0.5 * sin(phase * 2.3 + 1.7);
  // 根元は動かず、先端ほど大きく動く。
  float amount = height_t * height_t * strength * sway;
  return world_pos + float3(wind_dir.x, 0, wind_dir.y) * amount;
}
```

## 風のテクスチャ：突風を、作る

サイン波は、**規則的で、周期が見える**ので、風の、**ばらつき**（突風）を表すには、向きません。**風の強さを、ノイズのテクスチャに、描いて、それを、風の向きへ、スクロール**させます。

```hlsl
Texture2D<float> g_wind_noise : register(t2);    // タイル可能な、ノイズ（低周波）

float WindStrengthAt(float3 world_pos, float2 wind_dir, float time) {
  // ワールド座標で、ノイズを読む。時間とともに、風の向きへ、ずらす（流れる）。
  float2 uv = world_pos.xz * 0.02 - wind_dir * time * 0.1;
  float gust = g_wind_noise.SampleLevel(g_linear_wrap, uv, 0);
  return lerp(0.2, 1.0, gust);                   // 強い所は、突風。弱い所は、そよ風
}
```

| 要素 | 内容 |
| --- | --- |
| ノイズの周波数 | 低い（数十メートルの波長）。突風が、**大きなまとまり**で、草原を、渡る |
| スクロールの速さ | 風速に、比例。風の向きに、動かす |
| 大きさ | 風の強さに、掛ける。**ノイズの値が大きい所だけ、強く揺れる** |

草原の上を、**波が渡っていくように見える**ので、風の動きが、目で見えます。

## 風を、全体で共有する

風の向きと、強さは、**シーンの全体で、1 組**です（すべての植生が、同じ風を受ける）。

```cpp
struct WindCB {
  float2 direction;     // 風の向き（正規化済み）
  float strength;       // 風の強さ
  float time;           // 風用の時間（下の注意を参照）
  float gust_scale;     // 突風のノイズの、周波数
  float pad[3];
};
```

!!! warning "時間（`time`）を、float で、増やし続けない"
    ゲーム開始から、数時間たつと、`time` が、数万の大きさになり、**`sin(time * 12.0)` の、精度が落ちて**、動きが、カクカクします。時間は、**`fmod(time, 周期)`** で、**繰り返す範囲に、収めて**から、シェーダーへ渡します。サイン波の周期の、**公倍数**で、折り返すと、継ぎ目が、出ません。

```cpp
// 風用の時間: 数百秒で、折り返す。使うサイン波の周期が、この値で、割り切れるようにする。
wind.time = std::fmod(game_time, 1000.0f * 3.14159265f);
```

## ゲームの状況に、合わせる

| 要素 | 内容 |
| --- | --- |
| 天候 | 嵐で、風の強さを上げる。雨が降ると、草が、重くなる（揺れを小さく） |
| 爆発・ヘリコプター | 一時的な、**局所的な風**。位置と半径を、渡して、その範囲の、植生を、強く押す（[Trampled Grass](trample.md) の仕組みを、使える） |
| 屋内・洞窟 | 風を、止める。マスクで、強さを 0 に |
| 遠景 | 遠くの木は、揺れを、**弱める**（細かい動きは、見えない。計算の節約にもなる） |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/wind.md", [SOUSA, PELZER, WOHLLAIB])

# ---------------------------------------------------------------- trample
pg.Dedup("terrain/vegetation/trample.md")
pg.Add("terrain/vegetation/trample.md", '''
## 位置を、直接、渡す方法の、限界

上のコードは、**キャラクターの位置を、シェーダーに渡し、近くの草を、押す**方法です。1 体なら、うまく動きますが、**増えると、破綻**します。

| 状況 | 問題 |
| --- | --- |
| 敵が 20 体 | 20 個の位置を、全部の草が、ループで調べる。重い |
| 戦車、車 | 通った**跡**が、残らない（通り過ぎると、すぐ、元に戻る） |
| 爆発 | 瞬間の、局所的な、押しつぶし。履歴が、必要 |

そこで、**「踏まれた跡を、テクスチャに、描く」**方式に、します。草は、**その場所の、テクスチャの値を、読む**だけです。物の数に、関係なく、**草が 1 回読むだけ**です。

## インタラクション マップ

カメラの周りの、**数十メートル四方**を、覆う、**小さなテクスチャ**（256×256 など）を、用意します。

| チャンネル | 内容 |
| --- | --- |
| R | 倒れる量（0 = 立っている、1 = 完全に、倒れている） |
| G, B | 倒れる向き（x, z）。物から、遠ざかる向き |

```text
        ← 50 m →
   ┌───────────────┐
   │   ·  ·  ·     │  カメラの周りの、窓（256×256 画素）
   │  ·  ●→→ ·     │  ● = キャラクター。通った所に、押した向きが、描かれる
   │   ·  ·  ·     │
   └───────────────┘
```

### 物を、マップに描く

毎フレーム、**動く物の位置に、円（ブラシ）を、描き込み**ます。

```hlsl
// ブラシを描く（ピクセル シェーダー。物の位置を中心にした、四角形を描く）。
float4 BrushPS(float2 uv : TEXCOORD0, float2 center_uv, float radius_uv, float2 push_dir) : SV_Target {
  float d = distance(uv, center_uv) / radius_uv;
  float strength = saturate(1.0 - d);                 // 中心が 1、縁が 0
  strength *= strength;                                // 縁を、なだらかに
  // R = 倒れる量, GB = 向き（物の中心から、外へ）
  float2 away = normalize(uv - center_uv + 1e-5);
  return float4(strength, away * strength, 0);
}
```

ブレンド ステートは、**最大値（`D3D11_BLEND_OP_MAX`）**にします。複数の物が、重なっても、**強い方が、残ります**。

```cpp
D3D11_BLEND_DESC blend = {};
blend.RenderTarget[0].BlendEnable = TRUE;
blend.RenderTarget[0].SrcBlend = D3D11_BLEND_ONE;
blend.RenderTarget[0].DestBlend = D3D11_BLEND_ONE;
blend.RenderTarget[0].BlendOp = D3D11_BLEND_OP_MAX;          // 強い方を残す
blend.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_ONE;
blend.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_ONE;
blend.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_MAX;
blend.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend, &max_blend);
```

## 時間とともに、戻す

毎フレーム、マップ全体を、**少しずつ、薄めます**。そうすると、踏まれた草が、**ゆっくり、立ち上がります**。

```hlsl
// 全画面の描画: 前のフレームの結果を、少しだけ薄めて、コピーする。
float4 DecayPS(float2 uv : TEXCOORD0) : SV_Target {
  float4 prev = g_prev_map.SampleLevel(g_point_clamp, uv, 0);
  float recover = decay_per_second * dt;       // 例: 0.5 / 秒 → 約 2 秒で、元に戻る
  prev.r = max(prev.r - recover, 0.0);
  prev.gb *= (prev.r > 0.0) ? 1.0 : 0.0;       // 立ち上がったら、向きも消す
  return prev;
}
```

| パラメーター | 目安 | 効果 |
| --- | --- | --- |
| 回復の速さ | 0.2〜1 / 秒 | 小さいと、**長く、跡が残る**（雪、泥、深い草） |
| ブラシの大きさ | 物の、足元の半径 | 大きいほど、広く、倒れる |
| ブラシの強さ | 0.5〜1 | 物の、重さ |

## カメラについていく窓

マップは、**カメラの周りだけ**を覆います。カメラが動くと、窓が動きます。窓が動くとき、**マップの内容も、ずらす**必要があります。

### 毎フレーム、全体をコピーする方法

**カメラが、1 画素分動いたら、マップ全体を、ずらして、コピー**します。単純ですが、毎回、全体を、書き込むので、無駄です。

### 円環バッファ（トロイダル）

**ずらす代わりに、読み書きの位置を、ずらします**。テクスチャの `WRAP`（繰り返し）のアドレッシングを使うと、**窓の端を、超えた座標が、反対側に戻る**ので、内容を、コピーせずに済みます（[Geometry Clipmaps](../lod/clipmap.md) と、同じ発想）。

```hlsl
// ワールド座標から、マップの UV を求める。WRAP で、窓の外へ出ても、反対側から、読まれる。
float2 InteractionUV(float3 world_pos) {
  return world_pos.xz / map_world_size;
}
// 窓の外（遠すぎる）の草は、読んでも、意味がない。範囲の外は、「踏まれていない」にする。
float inside = step(distance(world_pos.xz, camera_position.xz), map_world_size * 0.5);
```

窓が、動いて、**新しく範囲に入った帯**だけは、**クリア**します（前の位置の、古い内容が、残っているため）。

## 草の側で読む

```hlsl
float3 ApplyTrample(float3 world_pos, float height_t) {
  float4 m = g_interaction.SampleLevel(g_linear_wrap, InteractionUV(world_pos), 0);
  float bend = m.r;                              // 倒れる量
  float2 dir = m.gb;                             // 倒れる向き

  // 先端ほど、大きく動く（根元は、動かない）
  float k = height_t * height_t;
  world_pos.xz += dir * bend * k * 0.6;          // 向きへ、押される
  world_pos.y -= bend * k * 0.5;                  // 倒れた分、低くなる
  return world_pos;
}
```

風（[Wind](wind.md)）と、足し合わせます。**踏まれた草には、風の揺れを、弱めます**（倒れた草は、風で、揺れにくい）。

```hlsl
float3 pos = ApplyGrassWind(world_pos, height_t, wind_dir, strength, time);
pos = ApplyTrample(pos, height_t);
```

## 水や雪との、共有

同じ仕組みは、**波紋のブラシ**（[Water Interaction](../../water/interaction/index.md)）、**雪の足跡**、**砂の跡**にも、使えます。**1 つの、インタラクション マップに、複数の用途を、まとめる**ことも、できます。

| 用途 | 使うチャンネル |
| --- | --- |
| 草の倒れ | R, G, B |
| 雪・砂の足跡の深さ | A |
| 水の波紋 | 別のマップ（高さを、波動方程式で、更新する） |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/trample.md", [WOHLLAIB, SOUSA, PELZER, "Microsoft Learn, \"D3D11_BLEND_OP\"（`D3D11_BLEND_OP_MAX`）"])

# ---------------------------------------------------------------- lighting
pg.Dedup("terrain/vegetation/lighting.md")
pg.Add("terrain/vegetation/lighting.md", '''
## 草の、ライティングが、難しい理由

草の 1 本は、**薄い帯**です。帯に、通常の、ライティングを行うと、次の問題が出ます。

| 問題 | 原因 |
| --- | --- |
| 草原が、**ごちゃごちゃ**して見える | 帯 1 本ずつの、法線が、バラバラ。隣り合う草の、明るさが、まちまち |
| 逆光で、**真っ黒** | 帯の、表が、光源と反対を向く。実際の葉は、光を通す |
| 影が、**重い** | 草 1 本ずつが、影を落とす・受ける。数百万本の影は、計算できない |
| 草と地面が、**別物**に見える | 草の色、明るさと、地面の色、明るさが、合っていない |

## ① 法線を、地面に合わせる

草原を、**1 枚の、面**のように、照らすのが、きれいに見せる、最大のコツです。草の法線を、**地形の法線**（または、真上）に、**寄せます**。

```hlsl
// 草の法線を、地形の法線と、真上へ寄せて、草原全体を、1 つの面のように、照らす。
float3 GrassNormal(float3 blade_normal, float3 terrain_normal, float height_t) {
  // 根元は、地面の法線。先端は、少し、帯の法線を混ぜる。
  float3 n = lerp(terrain_normal, blade_normal, 0.3 * height_t);
  return normalize(n);
}
```

| 寄せ方 | 効果 |
| --- | --- |
| 地形の法線にする | 草原が、地形の起伏と、**一体の陰影**になる（斜面は、暗く、日向は、明るい） |
| 真上（0, 1, 0）に寄せる | 草が、どこでも、上から照らされた様子になる。地形の、陰影を、無視する |
| 帯の法線を、少し混ぜる | 1 本ごとの、細かい、明暗の違いが、少し出る |

**どの程度寄せるか**は、見た目で決めます。完全に、地形の法線だと、平板に、見えます。

## ② 透過光

葉は、薄いので、**裏から当たった光が、透けて、表に出てきます**。太陽を背にして、草を見ると、**明るく透けて見える**のは、このためです。

簡単な、近似は、**視線と光の向きから、透過を求める**ものです（Barré-Brisebois と Bouchard、2011 の考え方を、簡略にしたもの）。

```hlsl
// 透過光: 光が、葉の裏から当たり、視線の方向へ、抜けてくる分。
float3 FoliageTranslucency(float3 normal, float3 view_dir, float3 light_dir, float3 light_color,
                           float3 albedo, float thickness) {
  // 光の向きを、法線で少し曲げる（葉の中での、屈折・散乱の近似）
  float3 h = normalize(light_dir + normal * 0.3);
  // 視線の方向と、曲げた光の向きが、逆向きに近い（光が、こちらへ抜けてくる）ほど、強い。
  float t = pow(saturate(dot(view_dir, -h)), 4.0);
  // 薄い葉ほど、透ける
  return albedo * light_color * t * (1.0 - thickness);
}
```

| パラメーター | 内容 |
| --- | --- |
| `thickness` | 葉の厚さ（0 = 非常に薄い、1 = 厚い）。テクスチャで、与える |
| 指数（`pow` の 4.0） | 大きいほど、太陽の方向を、見たときだけ、強く光る |
| `albedo` | 透けた光の色は、葉の色（緑や黄色）になる。白い光は、透けない |

全体の明るさに、足し込みます。

```hlsl
float3 lit = diffuse_lighting + FoliageTranslucency(n, v, l, light_color, albedo, thickness);
```

## ③ 環境光・AO

草の根元は、**周りの草に、挟まれて、暗い**はずです。草 1 本ずつの、AO は、計算できないので、**高さ `t` で、近似**します。

```hlsl
// 根元ほど暗くする（周りの草に遮られている）
float ao = lerp(0.3, 1.0, saturate(height_t * 1.5));
float3 ambient = ambient_light * albedo * ao;
```

| 要素 | 内容 |
| --- | --- |
| 根元の暗さ | 0.2〜0.4（草の密度が高いほど、暗い） |
| 先端の明るさ | 1.0 |
| 地面の色との馴染み | 根元の色を、地形の色に合わせる（[Grass Shape](grass-shape.md)） |

環境光が、**空の色**（上は青、下は地面の色）なら、**草の裏側（下向きの面）**に、地面の色を足すと、より自然です。

## ④ 影

| 影 | 内容 |
| --- | --- |
| 草が、受ける影 | 木、建物、岩の影を、草が、受ける。**普通に、シャドウ マップを、引く**（影の中の草は、暗くなる） |
| 草が、落とす影 | **落とさない**ことが、多い。草 1 本ずつを、シャドウ マップに描くと、数百万本が、重い |
| 草の影を、代わりに、表現する | 地面のテクスチャに、**暗い**色を焼く、または、AO の模様を描く |
| 木が、落とす影 | 木の葉は、**アルファ テスト**で、影も、切り抜く（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |

**草の影は、省略する**ことが、一般的な選択です。そのかわり、**地面のライティングに、草の影の、印象を足す**（地形の色を、草が、生えている場所で、少し暗くする）と、自然に見えます。

## ⑤ スペキュラー

草の、光沢は、**葉の表面の、ワックス質**や、**細い葉の、方向性**から来ます。

| 方針 | 内容 |
| --- | --- |
| 弱いスペキュラー | 粗さを高く（0.7〜0.9）。控えめな、つや |
| 遠くの草は、切る | 小さい、ハイライトは、**ちらつく**（エイリアシング）。遠景では、スペキュラーを、0 にする |
| 地形のスペキュラーに合わせる | 草が、生えた地面の、スペキュラーと、そろえる |

## 草と地形の、境目を、消す

草のライティングは、**地形のライティングと、連続している**必要があります。ずれていると、**草が、地面から、浮いて見えます**。

| 項目 | 合わせる |
| --- | --- |
| 色 | 草の根元の色 = 地形のテクスチャの色 |
| 明るさ | 草の法線 ≒ 地形の法線（根元で） |
| 影 | 同じシャドウ マップを、同じ精度で、引く |
| 霧・大気 | 草にも、地形と同じ、距離の霧を、かける（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)） |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/lighting.md", [SOUSA, BARRE, WOHLLAIB, PELZER, BOULANGER])

# ---------------------------------------------------------------- translucency
pg.Dedup("terrain/vegetation/translucency.md")
pg.Add("terrain/vegetation/translucency.md", '''
## 半透明が、使えない理由

草や木の葉は、**輪郭が、細かい**ので、**テクスチャの、アルファ（透明度）**で、形を切り抜きます。ここで、**半透明のブレンド**を使うと、次の問題が起きます。

| 問題 | 内容 |
| --- | --- |
| ソートが要る | 半透明は、**奥から手前の順**に描かないと、正しく、混ざらない。数百万本を、ソートできない |
| 深度を書かない | 半透明は、深度バッファに、書かない。**隣の草との、前後関係**が、おかしくなる |
| 重い | 画素ごとの、ブレンドは、メモリ帯域を使う。草は、画面全体に、重なる |

そこで、**アルファ テスト（切り抜き）**を使います。**アルファが、しきい値より小さい画素は、捨てる**だけで、深度も、書けて、ソートも要りません。

```hlsl
float alpha = g_albedo.Sample(g_linear_wrap, input.uv).a;
clip(alpha - 0.5);                // アルファが 0.5 未満の画素は、捨てる
```

## アルファ テストの、問題

### ① 縁が、ギザギザになる

アルファ テストは、**画素ごとに、残すか捨てるかを決める**ので、縁が、**ジャギー**になります。**MSAA の、効果も、出ません**（シェーダー内の、`clip` は、1 画素ごとの結果で、サブサンプルごとには、決まらない）。

| 対策 | 内容 |
| --- | --- |
| Alpha to Coverage | アルファの値を、**MSAA の、カバレッジ（サブサンプルの、何個を、描くか）に変換**する。縁が、なめらか（[Alpha to Coverage](../../translucency/alpha-test/alpha-to-coverage.md)） |
| TAA | 時間方向に、平均する。ジャギーが、ならされる（[TAA](../../postprocess/antialiasing/taa.md)） |
| ハッシュ アルファ | 画素ごとに、**ランダムな**しきい値で、判定する。**時間方向に、平均すると**、半透明に、見える（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)、Wyman と McGuire、2017） |

### ② 遠くで、葉が、痩せて見える

テクスチャの**ミップマップ**で、アルファを、**平均して縮める**と、**遠くのミップで、アルファの値が、小さくなります**。しきい値（0.5）を、下回る画素が、増えて、**葉が、スカスカになります**。

| 距離 | ミップ | アルファの平均 | 0.5 以上の画素の割合 |
| --- | --- | --- | --- |
| 近い | 0 | 元のまま | 元の割合（たとえば、60%） |
| 中くらい | 2 | ぼける | 40% |
| 遠い | 4 | さらに、ぼける | 10% |

葉の、**見た目の面積が、距離で、小さくなる**のです。

**対策：ミップごとに、アルファを、補正**します（Castaño、2010）。

| 手順 | 内容 |
| --- | --- |
| ① ミップ 0 で、**しきい値以上の画素の割合**（カバレッジ）を求める | たとえば、60% |
| ② 各ミップで、**カバレッジが、同じ 60%** になるように、アルファに、**スケール**を掛ける | ミップ 4 で、元の 60% を、保つ |
| ③ スケールを、ミップごとに、保存する | ミップ作成の、前処理で、行う |

```cpp
// ミップごとに、アルファを、補正して、カバレッジを保つ（前処理の例）。
float ComputeCoverage(const std::vector<float>& alpha, float threshold, float scale) {
  size_t covered = 0;
  for (float a : alpha) if (a * scale > threshold) ++covered;
  return float(covered) / float(alpha.size());
}

// 二分探索で、カバレッジが、目標（ミップ 0 の値）に、一致する scale を探す。
float FindAlphaScale(const std::vector<float>& mip_alpha, float threshold, float target_coverage) {
  float lo = 0.0f, hi = 8.0f;
  for (int i = 0; i < 20; ++i) {
    const float mid = 0.5f * (lo + hi);
    if (ComputeCoverage(mip_alpha, threshold, mid) < target_coverage) lo = mid; else hi = mid;
  }
  return 0.5f * (lo + hi);
}

// 全ミップに、適用する。
for (int level = 1; level < mip_count; ++level) {
  const float scale = FindAlphaScale(mips[level].alpha, 0.5f, coverage_at_mip0);
  for (float& a : mips[level].alpha) a = std::min(a * scale, 1.0f);
}
```

ミップを作る、**ツールの段階**で、行います。実行時の、シェーダーでは、普通に、ミップを読むだけです。

### ③ 距離で、シェーダー側で補う

ツールで、作り直せない、既存のテクスチャには、**シェーダーで、距離に応じて、しきい値を、下げる**方法も、あります。

```hlsl
// ミップが進むほど、しきい値を下げる（簡易な補正）。
float mip = g_albedo.CalculateLevelOfDetail(g_linear_wrap, input.uv);
float threshold = lerp(0.5, 0.25, saturate(mip / 4.0));
clip(alpha - threshold);
```

簡単ですが、**ミップごとの、アルファの分布が、画像によって違う**ので、前処理の補正（②）より、精度が劣ります。

## 薄い、植生（草）の、アルファ

草は、**形を、ジオメトリ（細い三角形の帯）**で、表現するなら、**アルファが、要りません**。三角形の縁が、そのまま、草の形になるので、アルファ テストの、問題がなくなります。

| 方式 | アルファ | 縁 |
| --- | --- | --- |
| クロス板 ＋ 草の絵 | **要る**（アルファで切り抜く） | アルファ テスト。ミップの補正が必要 |
| 1 本ずつの、細い帯 | 要らない | **ジオメトリの縁**。MSAA で、なめらか。ただし、遠くで、細すぎて、消える |

細い帯の、**遠くでの、細さ**（1 画素より細いと、消える）には、**幅の、下限**を設けます（[Grass Shape](grass-shape.md)）。

## 木の葉

木の葉は、**カード（板に、葉の絵）**で、表現します。アルファ テストで、**葉の形を、切り抜きます**。

| 項目 | 内容 |
| --- | --- |
| 葉の描画 | アルファ テスト ＋ Alpha to Coverage |
| 影 | アルファ テストで、**影も、切り抜く**（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)） |
| 遠景（インポスター） | 木全体を、1 枚の絵（板）に。アルファ テスト、またはディザで、フェード（[Trees](trees.md)） |
| LOD の、切り替え | ディザ フェード（市松の、ディザ パターンで、2 つの LOD を、混ぜる） |

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/translucency.md", [CASTANO, WYMAN, SOUSA, "Microsoft Learn, \"D3D11_BLEND_DESC\"（`AlphaToCoverageEnable`）"])

# ---------------------------------------------------------------- trees
pg.Dedup("terrain/vegetation/trees.md")
pg.Add("terrain/vegetation/trees.md", '''
## 木は、どう作られるか

木の 3D モデルは、**手で作る**場合と、**ルールから、自動生成する**場合があります。

| 方法 | 内容 |
| --- | --- |
| 手作り（DCC ツール） | アーティストが、幹、枝、葉を、モデリングする。品質は、高いが、手間がかかる |
| 木の専用ツール | 樹種ごとの、パラメーターから、木を生成する。**パラメーターを変えて、同じ種類の、別の木**を、たくさん作れる |
| 手続き的な生成（L システムなど） | ルール（枝分かれの規則）を、繰り返し適用して、枝を生やす |

自動生成の、基礎は、**L システム**（Prusinkiewicz と Lindenmayer、1990）と、**Weber と Penn の、パラメトリックな木**（1995）です。

### Weber と Penn の、考え方

1 本の木を、**少数のパラメーターで**記述します。

| パラメーター | 内容 |
| --- | --- |
| 枝の分かれる、数 | 幹から、何本の枝が出るか |
| 枝の長さ・太さの、減り方 | 先へ行くほど、短く、細く |
| 枝の、曲がり・ねじれ | 枝が、どのくらい、まっすぐでないか |
| 枝の、角度 | 幹から、どの角度で分かれるか |
| ランダムさ | 個体ごとの、ばらつき |

パラメーターを変えると、**松、オーク、柳**など、違う樹種が、生成できます。1 本の定義から、**ランダムなバリエーション**を、いくつも作れるので、**同じ木が並ぶ**問題が、軽減されます。

## 木を構成する、部品

| 部品 | 形 | 素材 |
| --- | --- | --- |
| 幹・太い枝 | メッシュ（円柱を、曲げたもの） | 不透明（木の皮のテクスチャ） |
| 細い枝 | メッシュ、または、板 | アルファ テスト |
| 葉 | **カード（板に、葉の房の絵）** | アルファ テスト、透過（[Foliage Translucency](translucency.md)） |

葉を、1 枚ずつ、3D モデルにすると、**数十万ポリゴン**になります。**葉の房を、1 枚の板に描いて、並べる**（カード）ことで、数千ポリゴンに、収めます。

## LOD

木は、1 本が、**数万ポリゴン**で、森では、数万本です。LOD が、**必須**です。

| LOD | 距離 | 内容 | 三角形（目安） |
| --- | --- | --- | --- |
| 0 | 〜30 m | 幹・枝の、完全なメッシュ ＋ 葉のカード | 20,000〜50,000 |
| 1 | 30〜80 m | 細い枝を減らす。葉のカードを、統合 | 5,000〜10,000 |
| 2 | 80〜200 m | 幹と、主な枝だけ。葉は、大きなカードに | 1,000〜3,000 |
| インポスター | 200 m〜 | **数方向から撮った絵**を、板に貼る | 2（板 1 枚） |
| ビルボード | 最遠 | 1 枚の絵（常に、カメラを向く） | 2 |

### LOD の切り替えを、隠す

LOD が、切り替わる瞬間に、**ポップ**が起きます。隠すには、**ディザ フェード**を使います。

```hlsl
// ディザ フェード: 2 つの LOD を、市松状のパターンで、混ぜて切り替える。
// fade が 0 → 1 に動くと、LOD A が、少しずつ、消えて、LOD B が現れる。
void ApplyDitherFade(float4 screen_pos, float fade) {
  // 4×4 のベイヤー行列（0〜15）から、しきい値を作る
  static const float bayer[16] = {
     0, 8, 2,10,  12, 4,14, 6,  3,11, 1, 9,  15, 7,13, 5};
  uint2 p = uint2(screen_pos.xy) & 3;
  float threshold = (bayer[p.y * 4 + p.x] + 0.5) / 16.0;
  clip(fade - threshold);        // fade が threshold 未満の画素は、捨てる（LOD A の側）
}
// LOD B には、逆（1 - fade）を渡す。
```

2 つの LOD を、**同時に、描く**期間が、必要です。コストは、増えますが、切り替えの、見た目が、大きく、改善します（[Dithered Transparency](../../translucency/alpha-test/dither.md)）。

## インポスター

**インポスター（imposter）**は、**3D の木を、事前に、複数の方向から撮影した絵**を、**板**に貼って、**木の代わり**に、描く手法です。

### 作り方

| 手順 | 内容 |
| --- | --- |
| ① 撮影 | 木を、**周りの、決まった方向**（例：8×8 = 64 方向）から、撮影する。**色、法線、深度**を、それぞれ、記録する |
| ② アトラス | 撮影した絵を、**1 枚の大きなテクスチャ**（アトラス）に、並べる |
| ③ 実行時 | カメラの向きに、最も近い撮影方向の、絵を、板に貼って描く |

### 方向の、決め方（8 面体マッピング）

撮影する方向を、**球面上に**、均等に並べたいとき、**8 面体（正八面体）マッピング**が、使われます。球面を、**正方形に展開**する方法で、格子状に、均等な方向を、取れます（Brucks、2018）。

```text
方向 (x, y, z) → 正方形上の座標 (u, v)      ← 8 面体マッピング（球面 ↔ 正方形）
 u, v を、N×N の格子に、離散化          → 撮影する方向の、番号
```

### 実行時：3 枚の絵を、混ぜる

カメラが、**撮影方向の、間**を向いているとき、1 枚の絵だけだと、**ポップ**が起きます（絵が、切り替わる瞬間）。そこで、**近い、3 つの方向の絵を、重みつきで、混ぜ**ます。

```hlsl
// インポスターの、ピクセル シェーダー（概略）。
float4 ImposterPS(float2 uv : TEXCOORD0, float3 view_dir_local : TEXCOORD1) : SV_Target {
  // ① カメラの向きを、8 面体マッピングの、座標に変える
  float2 grid = OctEncode(normalize(view_dir_local)) * (kGridSize - 1);
  float2 cell = floor(grid);
  float2 f = frac(grid);

  // ② 近い 3 つの方向（格子の三角形）を選ぶ。重みは、重心座標
  float2 c0 = cell, c1 = cell + float2(1, 0), c2 = cell + float2(0, 1), c3 = cell + float2(1, 1);
  bool upper = (f.x + f.y) > 1.0;
  float3 w = upper ? float3(1.0 - f.y, 1.0 - f.x, f.x + f.y - 1.0)
                   : float3(1.0 - f.x - f.y, f.x, f.y);
  float2 a = upper ? c3 : c0, b = upper ? c2 : c1, c = upper ? c1 : c2;

  // ③ 3 枚の、アトラスの絵を、読んで、混ぜる
  float4 col = SampleAtlas(a, uv) * w.x + SampleAtlas(b, uv) * w.y + SampleAtlas(c, uv) * w.z;
  clip(col.a - 0.5);
  return col;
}
```

| 項目 | 内容 |
| --- | --- |
| 方向の数 | 8×8（64 枚）が、一般的。多いほど、滑らかだが、アトラスが、大きい（例：2048×2048 に 64 枚 ＝ 1 枚 256×256） |
| 深度・法線 | 色だけでなく、**法線と深度**も、撮影しておくと、**ライティングと、地面との、接点（深度のオフセット）**が、正しくなる |
| 距離の、切り替え | LOD 2 から、インポスターへ、**ディザ フェード**で、切り替える |
| 向き | 地面に垂直な軸で、回転する（木は、地面に、立っているため）。真上から見る場合を、除いて、**縦の軸**だけで、回す、簡易版も、ある |

簡易版は、**横方向の、数方向（8 方向）だけ**を、撮影します。真上や真下から見ない、地上のゲームでは、十分です。

## ビルボード（最遠）

最も遠い木は、**カメラを、常に向いた、板 1 枚**に、します。**1 方向の絵**だけで、回転で、形が崩れないよう、**ほぼ、シルエットだけ**が、分かる程度です。

| 距離 | 見え方 |
| --- | --- |
| 500 m〜 | 数画素の、緑のかたまり。**詳細は、不要** |
| 1 km〜 | 木を 1 本ずつ、描かず、**森の、色の塊**として、地形のテクスチャに、含める |

## 影

| LOD | 影への、扱い |
| --- | --- |
| 近い木 | 完全なメッシュで、**影を落とす**。葉は、アルファ テストで切り抜く |
| 中くらい | **影用の、簡略な LOD**（描画より、粗い）を使う |
| 遠い木 | 影を落とさない。または、**インポスターで、影も、近似する** |

影の描画は、**カメラの描画と、別の距離で、LOD を、決めて**かまいません（影は、粗くても、気づかれにくい）。

''', before="## よくあるミス")
pg.Refs("terrain/vegetation/trees.md", [SOUSA, WEBER, PRUSINKIEWICZ, DECORET, BRUCKS])

pg.Refs("terrain/vegetation/index.md", [PELZER, SOUSA, WOHLLAIB, WIHLIDAL, CASTANO])
pg.Refs("terrain/index.md", ["Strugar, \"Continuous Distance-Dependent Level of Detail for Rendering Heightmaps\", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009", "Ebert, Musgrave, Peachey, Perlin, Worley, \"Texturing and Modeling: A Procedural Approach\", 3rd Edition, Morgan Kaufmann, 2002", SOUSA])
print("ok")
