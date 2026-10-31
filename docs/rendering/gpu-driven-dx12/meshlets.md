---
title: メッシュレットとメッシュ シェーダー
tags:
  - 描画最適化
---

# メッシュレットとメッシュ シェーダー

ここまでは、インスタンス（1 つの物体）を単位にカリングしてきました。ところが、建物や地形や高ポリのキャラのような巨大なメッシュは、一部しか見えていないことが多く、物体全体を描くのは無駄です。そこで、メッシュを数十〜百数十個の三角形の小さな塊（クラスタ）に分割しておき、塊ごとにカリングします。この塊がメッシュレットです。

D3D12 では、メッシュレットを処理するための専用のシェーダー段が用意されています。増幅シェーダー（Amplification Shader、AS）と、メッシュ シェーダー（Mesh Shader、MS）です。前者が「どの塊を描くか」を決め、後者が「その塊の頂点と三角形を出す」係を受け持ちます。このページでは、メッシュレットのデータ、AS と MS の書き方、そして両者がどう連携して動くのか（コードが何を実行していて、それがどういう意味か）を実際の数字を追いながら説明します。

!!! tip "ポイント"
    - メッシュレットは、最大 64 頂点・124 三角形ほどの小さな塊で、境界球と背面コーンを持つ。
    - AS はグループ内のスレッドが 1 つずつメッシュレットを判定し、生き残りの番号を「ペイロード」に集めて `DispatchMesh` で MS に渡す。
    - MS は 1 グループが 1 メッシュレットを処理する。頂点と三角形をスレッドで手分けして出力する。
    - `DispatchMesh` で起動される MS グループの `SV_GroupID` は、その AS グループの中での通し番号。ペイロードの添字に使う。
    - PSO は、パイプライン ステート ストリームで作る。入力アセンブラと頂点シェーダーは使わない。
    - `ExecuteIndirect` の引数に `DISPATCH_MESH` を使えば、カリング CS が書いたコマンドで AS を起動できる。

!!! info "このページを読む前に"
    カリングの考え方は [カリング（コンピュート）](culling.md)、コマンドの書き方は [ExecuteIndirect](execute-indirect.md)、マテリアルの引き方は [バインドレス](bindless.md) で説明しています。原理の側は [メッシュ シェーダー](../mesh-shaders.md) にあります。

## メッシュレットとは

メッシュレットは、メッシュの三角形を頂点の再利用を最大にしながら小さなグループにまとめたものです。サイズの上限は、GPU のメッシュ シェーダーの出力の上限と効率から決まります。

| 項目 | 内容 |
| --- | --- |
| 頂点 | 最大 64 個。メッシュ全体の頂点バッファへの添字の配列として持つ |
| 三角形 | 最大 124 個。メッシュレット内の頂点番号（0〜63）の 3 つ組 |
| カリング情報 | 境界球と背面コーン（軸と角度） |

上限を 64 頂点・124 三角形にするのは、NVIDIA の GPU で効率がよいサイズだからです。AMD などでは、もう少し大きくしても動きますが、まずはこの値で始めて、実機で測って調整します。124 は 4 の倍数で、meshoptimizer が三角形数に 4 の倍数を要求するためです。

### データ構造

```cpp
struct MeshletData {
  uint32_t vertex_offset;
  uint32_t triangle_offset;
  uint32_t vertex_count;
  uint32_t triangle_count;
};

struct MeshletBounds {
  DirectX::XMFLOAT3 center;
  float radius;
  DirectX::XMFLOAT3 cone_axis;
  float cone_cutoff;
};
```

`MeshletData` は、メッシュレットの中身が共有の配列のどこにあるかを指します。`vertex_offset` は「メッシュレットの頂点インデックス配列」の中の開始位置、`triangle_offset` は「三角形配列」の中の開始位置で、それぞれの個数が `vertex_count` と `triangle_count` です。メッシュレットごとに頂点を持つのではなく、全メッシュレットで 1 本の配列を共有して、添字だけを持つ作りです。

`MeshletBounds` は、カリング用の情報です。`center` と `radius` が境界球で、視錐台との判定に使います。`cone_axis` と `cone_cutoff` が背面コーンで、メッシュレットの全三角形がカメラに背を向けているかを判定します。コーンの軸は、メッシュレットの法線の平均的な向きです。

### meshoptimizer で作る

メッシュレットは、ビルド時に作ります。`meshoptimizer` の `meshopt_buildMeshlets` と `meshopt_computeMeshletBounds` が標準的です。

```cpp
constexpr size_t kMaxVertices = 64;
constexpr size_t kMaxTriangles = 124;
constexpr float kConeWeight = 0.5f;

void BuildMeshlets(const std::vector<DirectX::XMFLOAT3>& positions,
                   const std::vector<uint32_t>& indices, std::vector<MeshletData>* meshlets,
                   std::vector<MeshletBounds>* bounds, std::vector<uint32_t>* meshlet_vertices,
                   std::vector<uint32_t>* meshlet_triangles) {
  size_t max_meshlets = meshopt_buildMeshletsBound(indices.size(), kMaxVertices, kMaxTriangles);
  std::vector<meshopt_Meshlet> local_meshlets(max_meshlets);
  std::vector<unsigned int> local_vertices(max_meshlets * kMaxVertices);
  std::vector<unsigned char> local_triangles(max_meshlets * kMaxTriangles * 3);

  size_t count = meshopt_buildMeshlets(
      local_meshlets.data(), local_vertices.data(), local_triangles.data(), indices.data(),
      indices.size(), &positions[0].x, positions.size(), sizeof(DirectX::XMFLOAT3), kMaxVertices,
      kMaxTriangles, kConeWeight);
```

`meshopt_buildMeshletsBound` で、最大でいくつのメッシュレットができるかを先に見積もり、出力用の配列を確保します。`meshopt_buildMeshlets` が、三角形を近いもの同士でまとめて、メッシュレットの配列、頂点インデックスの配列、三角形の配列（1 バイト 3 個で 1 三角形）を埋めます。

`kConeWeight` は、背面コーンのカリング効率をどれだけ重視して分割するかです（0〜1）。大きくすると、法線のそろった塊ができて背面カリングの効果が上がり、代わりに頂点の再利用がやや落ちます。

```cpp
  for (size_t i = 0; i < count; ++i) {
    const meshopt_Meshlet& m = local_meshlets[i];

    MeshletData data;
    data.vertex_offset = static_cast<uint32_t>(meshlet_vertices->size());
    data.triangle_offset = static_cast<uint32_t>(meshlet_triangles->size());
    data.vertex_count = m.vertex_count;
    data.triangle_count = m.triangle_count;
    meshlets->push_back(data);

    for (unsigned int v = 0; v < m.vertex_count; ++v) {
      meshlet_vertices->push_back(local_vertices[m.vertex_offset + v]);
    }
    for (unsigned int t = 0; t < m.triangle_count; ++t) {
      const unsigned char* tri = &local_triangles[m.triangle_offset + t * 3];
      meshlet_triangles->push_back(static_cast<uint32_t>(tri[0]) |
                                   (static_cast<uint32_t>(tri[1]) << 8) |
                                   (static_cast<uint32_t>(tri[2]) << 16));
    }
```

ここで、メッシュレット固有の配列を全メッシュレット共通の配列へ連結します。三角形は、3 つの頂点番号（それぞれ 0〜63 なので 1 バイトに収まる）を `a | b << 8 | c << 16` で 1 つの `uint` に詰めます。こうしておくと、MS が `uint` を 1 回読むだけで 1 三角形を取り出せます。

```cpp
    meshopt_Bounds b = meshopt_computeMeshletBounds(
        &local_vertices[m.vertex_offset], &local_triangles[m.triangle_offset], m.triangle_count,
        &positions[0].x, positions.size(), sizeof(DirectX::XMFLOAT3));
    MeshletBounds bound;
    bound.center = {b.center[0], b.center[1], b.center[2]};
    bound.radius = b.radius;
    bound.cone_axis = {b.cone_axis[0], b.cone_axis[1], b.cone_axis[2]};
    bound.cone_cutoff = b.cone_cutoff;
    bounds->push_back(bound);
  }
}
```

`meshopt_computeMeshletBounds` が、境界球とコーンを計算します。`cone_cutoff` は、コーンの開きに対応する値（角度の cos に近い量）で、背面の判定式にそのまま使います。

## GPU に置くデータ

メッシュレットの情報は、GPU に常駐させます。AS と MS から読むので、構造化バッファにして SRV にします。

| バッファ | 内容 | レジスタ |
| --- | --- | --- |
| メッシュレット境界 | `MeshletBounds` の配列 | `t4` |
| メッシュレット | `MeshletData` の配列 | `t5` |
| メッシュレット頂点インデックス | メッシュレットごとの頂点インデックス（`uint` の配列） | `t6` |
| メッシュレット三角形 | 詰めた三角形（`uint` の配列） | `t7` |
| 頂点 | 従来と同じ頂点バッファ（構造化バッファとして読む） | `t8` |

`MeshInfo` には、そのメッシュのメッシュレットの開始番号と個数を足します。

```hlsl
struct MeshInfo {
  float3 bounds_center;
  float bounds_radius;
  float3 aabb_min;
  uint meshlet_offset;  // このメッシュのメッシュレットの、全体の中での開始番号
  float3 aabb_max;
  uint meshlet_count;   // このメッシュのメッシュレットの個数
  uint pso_bucket;
  uint3 reserved;
};
```

## AS と MS は何をしているのか

コードを読む前に全体の動きをつかみます。ここを理解しておくと、後のコードが全部つながります。

従来のパイプラインでは、頂点シェーダーが 1 頂点ずつ、入力アセンブラが読んだ順に動きました。メッシュ シェーダーのパイプラインは、これを 2 段の「スレッド グループの発射」に置き換えます。

1. CPU（または `ExecuteIndirect`）が `DispatchMesh(x, y, z)` で、AS のグループを `x × y × z` 個起動します。コンピュート シェーダーの `Dispatch` と同じ形です。
2. AS の 1 グループの中で、スレッドがそれぞれ 1 つのメッシュレットを調べ、見えるものだけを選びます。
3. AS のグループがシェーダーの中から `DispatchMesh(n, 1, 1, payload)` を呼び、MS のグループを `n` 個起動します。`n` はそのグループで生き残った数なので、見えなければ 0 個で、何も起動しません。
4. MS の各グループが 1 つのメッシュレットを担当し、頂点と三角形を出力します。出力された三角形は、そのままラスタライザーへ渡ります。

つまり AS は、「動的に MS の仕事量を決めるスレッド グループ」です。CPU は AS を何グループ起動するかしか知らず、その中の何個が MS に進むかは、GPU が実行中に決めます。

AS から MS へは、メモリを経由せず「ペイロード」という小さなデータを渡します。上限は 16 KB です。このページでは、生き残ったメッシュレットの番号の配列と、インスタンス番号を載せます。

<svg class="fig flow" viewBox="0 0 780 260" role="img" aria-label="増幅シェーダーとメッシュ シェーダーの連携">
<defs><marker id="mx" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" style="font-weight:700">AS が選び、MS が出力する</text>
<rect x="20" y="50" width="150" height="56" rx="6" fill="rgba(229,170,40,0.28)" stroke="currentColor" stroke-width="2"/>
<text x="32" y="76" style="font-size:13px">ExecuteIndirect</text><text x="32" y="94" style="font-size:12px">DISPATCH_MESH</text>
<rect x="230" y="50" width="190" height="56" rx="6" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/>
<text x="242" y="76" style="font-size:13px">AS グループ</text><text x="242" y="94" style="font-size:12px">32 スレッドが 32 メッシュレットを判定</text>
<rect x="480" y="30" width="130" height="40" rx="6" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="492" y="55" style="font-size:12px">MS グループ 0</text>
<rect x="480" y="80" width="130" height="40" rx="6" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="492" y="105" style="font-size:12px">MS グループ 1</text>
<rect x="480" y="130" width="130" height="40" rx="6" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="492" y="155" style="font-size:12px">MS グループ n-1</text>
<rect x="650" y="70" width="110" height="56" rx="6" fill="rgba(229,170,40,0.28)" stroke="currentColor" stroke-width="2"/><text x="662" y="96" style="font-size:12px">ラスタライザー</text><text x="662" y="114" style="font-size:12px">→ PS</text>
<g stroke="currentColor" stroke-width="2" fill="none" marker-end="url(#mx)">
<line x1="170" y1="78" x2="226" y2="78"/><line x1="420" y1="70" x2="476" y2="52"/><line x1="420" y1="80" x2="476" y2="100"/><line x1="420" y1="90" x2="476" y2="148"/>
<line x1="610" y1="52" x2="646" y2="88"/><line x1="610" y1="100" x2="646" y2="98"/><line x1="610" y1="150" x2="646" y2="108"/></g>
<text x="440" y="200" style="font-size:12px">DispatchMesh(n, 1, 1, payload)：生き残った n 個だけ起動する（n = 0 なら何も起きない）</text>
<text x="440" y="222" style="font-size:12px">payload：生き残ったメッシュレットの番号の配列とインスタンス番号</text>
</svg>

## 増幅シェーダー（カリング）

では、AS のコードです。グループ内のスレッド（ここでは 32 個）がそれぞれ 1 つのメッシュレットを判定し、生き残った番号をペイロードに集めます。

```hlsl
#define AS_GROUP_SIZE 32

struct Payload {
  uint meshlet_indices[AS_GROUP_SIZE];
  uint instance_index;
};

groupshared Payload s_payload;
groupshared uint s_visible_count;

StructuredBuffer<MeshletBounds> meshlet_bounds : register(t4);
```

`Payload` が、AS から MS へ渡す荷物の形です。`meshlet_indices` は、このグループで見えると判定されたメッシュレットの番号を詰める配列で、最大でスレッド数と同じ 32 個です。`instance_index` は、どのインスタンスの描画かを MS に伝えます。

`groupshared` で宣言しているのは、ペイロードをグループ内のスレッドが共同で書き込むためです。`DispatchMesh` に渡せるペイロードは、groupshared 変数でなければなりません。

```hlsl
bool MeshletVisible(MeshletBounds bounds, float4x4 world, float3 camera_position) {
  float3 center = mul(float4(bounds.center, 1.0), world).xyz;
  float radius = bounds.radius * MaxScale(world);
  if (!SphereInFrustum(center, radius)) return false;

  float3 axis = normalize(mul(bounds.cone_axis, (float3x3)world));
  float3 to_meshlet = center - camera_position;
  float distance_to_meshlet = length(to_meshlet);
  if (dot(to_meshlet, axis) >= bounds.cone_cutoff * distance_to_meshlet + radius) return false;

  return true;
}
```

`MeshletVisible` は、1 つのメッシュレットが見えるかを返します。前半は、これまでのカリングと同じ視錐台との判定です。メッシュレットの境界球をインスタンスのワールド行列で動かし、半径にはスケールの最大値（`MaxScale`）を掛けて、視錐台の 6 面と比べます。

後半が背面コーンの判定です。`to_meshlet` は、カメラから塊の中心へ向かうベクトルで、`axis` は塊の法線の平均の向きです。`dot(to_meshlet, axis)` が大きいほど、カメラから見て、法線が奥を向いていることになります。メッシュレットのすべての三角形が背を向けている条件は、「`dot(to_meshlet, axis) >= cone_cutoff × 距離 + 半径`」です。半径を足すのは、境界球の端にあるメッシュレットでも判定を安全側に倒すためです。この式は meshoptimizer の公式のものです。

軸の変換に `(float3x3)world` を使っているのは、向きだけを回すためで、平行移動を含めないためです。ワールド行列に非一様スケールがあるときは、法線と同じく、逆転置行列で変換します。

```hlsl
[numthreads(AS_GROUP_SIZE, 1, 1)]
void ASMain(uint group_thread_id : SV_GroupThreadID, uint group_id : SV_GroupID) {
  uint instance_index = draw_instance_index;
  Instance instance = instances[instance_index];
  MeshInfo mesh = meshes[instance.mesh_index];

  if (group_thread_id == 0) s_visible_count = 0;
  GroupMemoryBarrierWithGroupSync();
```

`[numthreads(32, 1, 1)]` は、AS の 1 グループが 32 スレッドであることを表します。AS のスレッド数の上限は 128 です。

`group_id` は、このグループが 1 つのインスタンスの中で何番目か（0, 1, 2, ...）を表します。1 つのインスタンスに 1000 個のメッシュレットがあれば、`ceil(1000 / 32) = 32` グループを起動して、`group_id` で担当する範囲を分けます。

`instance_index` は、`ExecuteIndirect` がコマンドごとに書いたルート定数 `draw_instance_index` から取ります。ここで、カウンターの `s_visible_count` を 0 にして、`GroupMemoryBarrierWithGroupSync` で全スレッドがそろうのを待ちます。0 にする前に他のスレッドが加算を始めてしまうのを防ぐためです。

```hlsl
  uint local_index = group_id * AS_GROUP_SIZE + group_thread_id;
  if (local_index < mesh.meshlet_count) {
    uint meshlet_index = mesh.meshlet_offset + local_index;
    if (MeshletVisible(meshlet_bounds[meshlet_index], instance.world, camera_position)) {
      uint slot;
      InterlockedAdd(s_visible_count, 1, slot);
      s_payload.meshlet_indices[slot] = meshlet_index;
    }
  }
```

各スレッドは、自分の担当のメッシュレットを 1 つ決めます。`local_index` はそのメッシュの中での番号で、`mesh.meshlet_offset` を足すと、全体の配列での番号になります。`local_index < mesh.meshlet_count` の条件は、最後のグループで、メッシュレットの数に満たないスレッドが範囲外を読まないようにするためです。

見えると判定したスレッドは、`InterlockedAdd` でカウンターを 1 つ進め、進める前の値（`slot`）を自分の書き込み位置にします。複数のスレッドが同時に呼んでも、`slot` が重ならないのが `InterlockedAdd` の性質です。見えるものだけが、配列の先頭から隙間なく詰まります。

ウェーブ命令（`WavePrefixCountBits`）で書き込み位置を決める方法もありますが、グループが複数のウェーブにまたがる GPU（ウェーブが 32 より小さい場合）では結果が狂うので、このページでは使いません。

```hlsl
  s_payload.instance_index = instance_index;
  GroupMemoryBarrierWithGroupSync();

  DispatchMesh(s_visible_count, 1, 1, s_payload);
}
```

全スレッドが判定を終えたら、再び `GroupMemoryBarrierWithGroupSync` で待ち、`DispatchMesh` を呼びます。ここで、`s_visible_count` 個の MS グループが起動します。

`DispatchMesh` には決まりがあります。グループ内の全スレッドが同じ値で、一様に呼ぶ必要があります。分岐の中や、スレッドごとに違う値で呼ぶと、動作は未定義です。呼んだ後にこのシェーダーの中の処理は終わりになります。`s_visible_count` が 0 なら、MS は 1 つも起動しません。

## メッシュ シェーダー

MS は、1 グループが 1 つのメッシュレットを担当して、頂点と三角形を出力します。

```hlsl
#define MS_GROUP_SIZE 128
#define MAX_VERTICES 64
#define MAX_TRIANGLES 124

StructuredBuffer<MeshletData> meshlets : register(t5);
StructuredBuffer<uint> meshlet_vertices : register(t6);
StructuredBuffer<uint> meshlet_triangles : register(t7);
StructuredBuffer<Vertex> vertices : register(t8);

struct MsVertex {
  float4 position : SV_Position;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};
```

`MsVertex` は、MS が 1 頂点ごとに出力するデータで、頂点シェーダーの出力と同じ役割です。`SV_Position` を必ず含めます。

```hlsl
[outputtopology("triangle")]
[numthreads(MS_GROUP_SIZE, 1, 1)]
void MSMain(uint group_thread_id : SV_GroupThreadID, uint group_id : SV_GroupID,
            in payload Payload payload, out vertices MsVertex out_vertices[MAX_VERTICES],
            out indices uint3 out_triangles[MAX_TRIANGLES]) {
```

シグネチャが MS の特徴を全部表しています。

`[outputtopology("triangle")]` は、出力が三角形のリストであることを宣言します（もう 1 つの選択肢は `"line"`）。

`in payload Payload payload` が、AS から受け取ったペイロードです。同じ AS グループから起動された MS グループは、全部が同じペイロードを読みます。

`out vertices MsVertex out_vertices[MAX_VERTICES]` と `out indices uint3 out_triangles[MAX_TRIANGLES]` が、出力先の配列です。頂点の配列と、三角形（頂点番号の 3 つ組）の配列で、サイズが上限になります。MS の出力は、頂点も三角形も最大 256 までです。このページでは、64 と 124 にしています。

`group_id` の意味に注意してください。AS の `DispatchMesh(n, ...)` が起動した n 個の MS グループのうち、何番目かを表します。MS 全体の通し番号ではなく、その AS グループの内側の番号です。だから、`payload.meshlet_indices[group_id]` で、このグループが担当するメッシュレットを取り出せるのです。

```hlsl
  uint meshlet_index = payload.meshlet_indices[group_id];
  Instance instance = instances[payload.instance_index];
  MeshletData meshlet = meshlets[meshlet_index];

  SetMeshOutputCounts(meshlet.vertex_count, meshlet.triangle_count);
```

ペイロードから担当のメッシュレット番号を取り出し、`meshlets[...]` で頂点数と三角形数を読みます。

`SetMeshOutputCounts(頂点数, 三角形数)` は、このグループが実際に出力する個数の宣言です。出力の配列は上限サイズで宣言していますが、実際に使うのは、この宣言した個数だけです。出力を書き込む前に全スレッドが同じ値で 1 回呼びます。呼ばずに出力を書くと、何も描かれません。

```hlsl
  for (uint v = group_thread_id; v < meshlet.vertex_count; v += MS_GROUP_SIZE) {
    uint vertex_index = meshlet_vertices[meshlet.vertex_offset + v];
    Vertex vertex = vertices[vertex_index];

    float4 world_position = mul(float4(vertex.position, 1.0), instance.world);
    MsVertex output;
    output.position = mul(world_position, view_projection);
    output.normal = mul(vertex.normal, (float3x3)instance.world);
    output.uv = vertex.uv;
    out_vertices[v] = output;
  }
```

頂点の変換です。スレッドが 128 個あり、頂点は最大 64 個なので、スレッド `t` が頂点 `t` を担当します。`v += MS_GROUP_SIZE` のループは、メッシュレットの頂点がスレッド数より多い場合にも動くための、定番の書き方です。

`meshlet_vertices[meshlet.vertex_offset + v]` が、メッシュレットの `v` 番目の頂点の、メッシュ全体での頂点番号です。それで `vertices[...]` を引き、頂点シェーダーと同じ変換（ワールド → ビュー射影）をして、`out_vertices[v]` に書きます。1 頂点は、このグループで 1 回しか変換されません。三角形が頂点を共有しても、変換し直しにならないのが、メッシュレットの利点です。

```hlsl
  for (uint t = group_thread_id; t < meshlet.triangle_count; t += MS_GROUP_SIZE) {
    uint packed = meshlet_triangles[meshlet.triangle_offset + t];
    out_triangles[t] = uint3(packed & 0xFF, (packed >> 8) & 0xFF, (packed >> 16) & 0xFF);
  }
}
```

三角形の出力も同じ形です。詰めておいた `uint` を 3 つの頂点番号に分けて、`out_triangles[t]` に書きます。この番号は、メッシュレット内の `out_vertices` の添字（0〜63）であって、メッシュ全体の頂点番号ではありません。

ピクセル シェーダーは、従来のものがそのまま使えます。`MsVertex` が、ピクセル シェーダーの入力になります。マテリアル番号は、[バインドレス](bindless.md) と同じく、ルート定数 `draw_material_index` から読みます。

### 1 回の描画を数字で追う

ここまでの流れを数字で追います。建物のインスタンスにメッシュレットが 1000 個あるとします。

| 段階 | 起こること |
| --- | --- |
| コマンド | カリング CS が書いたコマンドが `ThreadGroupCountX = ceil(1000 / 32) = 32` を持つ |
| AS の起動 | AS のグループが 32 個起動する。グループ 5 は、メッシュレット 160〜191 を担当する |
| AS のグループ 5 | 32 スレッドが 32 個を判定。視錐台と背面コーンを通ったのが 5 個だったとする |
| `DispatchMesh` | `s_visible_count = 5`。MS のグループが 5 個起動する。ペイロードに 5 個の番号が入る |
| MS のグループ 2 | `group_id = 2`。`payload.meshlet_indices[2]` のメッシュレット（頂点 60 個、三角形 110 個）を担当する |
| MS の 128 スレッド | スレッド 0〜59 が頂点を変換し、スレッド 0〜109 が三角形を書く。残りのスレッドは待つだけ |
| ラスタライザー | 5 グループ分の三角形がそのまま描かれる |

建物の裏側のメッシュレットは、AS の段で除外されるので、MS が起動することも、頂点が変換されることもありません。これが、メッシュ シェーダーを使う理由です。

## PSO の作成（メッシュ シェーダー）

メッシュ シェーダーの PSO は、`D3D12_GRAPHICS_PIPELINE_STATE_DESC` では作れません。シェーダーの種類が増えたので、「パイプライン ステート ストリーム」という、サブオブジェクトを並べる形で作ります。

ストリームの 1 要素は、「種類（`D3D12_PIPELINE_STATE_SUBOBJECT_TYPE`）の直後にその種類のデータ」が来る構造で、ポインター境界に置く決まりです。この組み立てを小さなテンプレートで書きます。

```cpp
template <D3D12_PIPELINE_STATE_SUBOBJECT_TYPE Type, typename T>
struct alignas(void*) PsoSubobject {
  D3D12_PIPELINE_STATE_SUBOBJECT_TYPE type = Type;
  T data = {};
};

struct MeshPipelineStateStream {
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_ROOT_SIGNATURE, ID3D12RootSignature*> root_signature;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_AS, D3D12_SHADER_BYTECODE> amplification_shader;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_MS, D3D12_SHADER_BYTECODE> mesh_shader;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_PS, D3D12_SHADER_BYTECODE> pixel_shader;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_BLEND, D3D12_BLEND_DESC> blend;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_SAMPLE_MASK, UINT> sample_mask;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_RASTERIZER, D3D12_RASTERIZER_DESC> rasterizer;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_DEPTH_STENCIL, D3D12_DEPTH_STENCIL_DESC> depth_stencil;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_RENDER_TARGET_FORMATS, D3D12_RT_FORMAT_ARRAY> rtv_formats;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_DEPTH_STENCIL_FORMAT, DXGI_FORMAT> dsv_format;
  PsoSubobject<D3D12_PIPELINE_STATE_SUBOBJECT_TYPE_SAMPLE_DESC, DXGI_SAMPLE_DESC> sample_desc;
};
```

`alignas(void*)` は、サブオブジェクトがポインター境界に並ぶようにするためです。種類（4 バイト）の直後にデータが来ると、データのサイズによってはずれが生じます。ずれたストリームは、PSO の作成に失敗します。

```cpp
ComPtr<ID3D12PipelineState> Renderer::CreateMeshPso(ID3DBlob* as, ID3DBlob* ms, ID3DBlob* ps) {
  MeshPipelineStateStream stream;
  stream.root_signature.data = mesh_root_signature_.Get();
  stream.amplification_shader.data = {as->GetBufferPointer(), as->GetBufferSize()};
  stream.mesh_shader.data = {ms->GetBufferPointer(), ms->GetBufferSize()};
  stream.pixel_shader.data = {ps->GetBufferPointer(), ps->GetBufferSize()};
  stream.blend.data = MakeDefaultBlendDesc();
  stream.sample_mask.data = UINT_MAX;

  stream.rasterizer.data = MakeDefaultRasterizerDesc();
  stream.rasterizer.data.FrontCounterClockwise = FALSE;  // このサイトでは時計回りが表

  stream.depth_stencil.data = MakeDefaultDepthStencilDesc();
  stream.rtv_formats.data.NumRenderTargets = 1;
  stream.rtv_formats.data.RTFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM;
  stream.dsv_format.data = DXGI_FORMAT_D32_FLOAT;
  stream.sample_desc.data = {1, 0};

  D3D12_PIPELINE_STATE_STREAM_DESC stream_desc = {sizeof(stream), &stream};
  ComPtr<ID3D12PipelineState> pso;
  ThrowIfFailed(device2_->CreatePipelineState(&stream_desc, IID_PPV_ARGS(&pso)));
  return pso;
}
```

`MakeDefaultBlendDesc` などは [Helper Functions](../../directx/dx12/util.md) の関数です。

メッシュ シェーダーの PSO には、頂点シェーダーも入力レイアウトも、プリミティブ トポロジーの指定もありません。入力アセンブラ（IA）を使わないので、IA に関する設定がすべて要らなくなります。ルート シグネチャにも、`ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` は付けません。

ストリーム版の `CreatePipelineState` は、`ID3D12Device2` のメソッドです。`device_.As(&device2_)` で取得します。コマンド リストも、`DispatchMesh` を持つ `ID3D12GraphicsCommandList6` が必要です。

### 対応の確認

```cpp
D3D12_FEATURE_DATA_D3D12_OPTIONS7 options7 = {};
bool supports_mesh_shader =
    SUCCEEDED(device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS7, &options7,
                                          sizeof(options7))) &&
    options7.MeshShaderTier != D3D12_MESH_SHADER_TIER_NOT_SUPPORTED;
```

メッシュ シェーダーは Shader Model 6.5 の機能です（`as_6_5`、`ms_6_5` でコンパイルします）。対応していない GPU には、従来の頂点シェーダーの経路（[ExecuteIndirect](execute-indirect.md)）をフォールバックとして用意します。

## ExecuteIndirect で DispatchMesh

インスタンスごとに AS を起動するコマンドは、カリング CS が書き、`ExecuteIndirect` で実行します。普通のドローとの違いは、コマンドの最後の引数が `DISPATCH_MESH` になることだけです。

```cpp
struct MeshIndirectCommand {
  uint32_t instance_index;
  uint32_t material_index;
  D3D12_DISPATCH_MESH_ARGUMENTS dispatch;
};
static_assert(sizeof(MeshIndirectCommand) == 20);

ComPtr<ID3D12CommandSignature> Renderer::CreateMeshCommandSignature() {
  D3D12_INDIRECT_ARGUMENT_DESC arguments[2] = {};
  arguments[0].Type = D3D12_INDIRECT_ARGUMENT_TYPE_CONSTANT;
  arguments[0].Constant.RootParameterIndex = kRootMeshDraw;
  arguments[0].Constant.DestOffsetIn32BitValues = 0;
  arguments[0].Constant.Num32BitValuesToSet = 2;  // instance_index, material_index
  arguments[1].Type = D3D12_INDIRECT_ARGUMENT_TYPE_DISPATCH_MESH;

  D3D12_COMMAND_SIGNATURE_DESC desc = {};
  desc.ByteStride = sizeof(MeshIndirectCommand);
  desc.NumArgumentDescs = 2;
  desc.pArgumentDescs = arguments;

  ComPtr<ID3D12CommandSignature> signature;
  ThrowIfFailed(device_->CreateCommandSignature(&desc, mesh_root_signature_.Get(),
                                                IID_PPV_ARGS(&signature)));
  return signature;
}
```

コマンドの先頭の 8 バイトがルート定数（インスタンス番号とマテリアル番号）になり、続く 12 バイト（`ThreadGroupCountX/Y/Z`）が `DispatchMesh` の引数です。カリング CS が、コマンドを書くときにグループ数を計算します。

```hlsl
struct MeshIndirectCommand {
  uint instance_index;
  uint material_index;
  uint thread_group_count_x;
  uint thread_group_count_y;
  uint thread_group_count_z;
};

command.instance_index = instance_index;
command.material_index = instance.material_index;
command.thread_group_count_x = (mesh.meshlet_count + AS_GROUP_SIZE - 1) / AS_GROUP_SIZE;
command.thread_group_count_y = 1;
command.thread_group_count_z = 1;
```

AS の 1 グループが 32 個のメッシュレットを担当するので、グループ数は `ceil(meshlet_count / 32)` です。この値が AS の `SV_GroupID` の範囲（0 から グループ数 − 1）になります。

グループ数には上限があります。X、Y、Z の各次元は 65,535 以下、積の総数は 2^22 以下です。メッシュレットが多いメッシュは、Y にも分けて指定します。

描画のループは、メッシュ PSO をセットして `ExecuteIndirect` を呼ぶだけです。

```cpp
list->SetPipelineState(mesh_pso_.Get());
list->ExecuteIndirect(mesh_command_signature_.Get(), kMaxDraws, mesh_command_buffer_.Get(), 0,
                      mesh_count_buffer_.Get(), 0);
```

## 効果とトレードオフ

利点は、次の 4 つです。巨大メッシュの見えない部分をメッシュレット単位で除外できます。メッシュレット内の頂点を 1 回だけ変換して、複数の三角形で使い回せます。入力アセンブラのインデックス フェッチに縛られません。メッシュレット単位の LOD（クラスタ LOD、Nanite 風）の土台になります。

注意点もあります。メッシュ シェーダー対応の GPU が必要です（NVIDIA Turing 以降、AMD RDNA2 以降、Intel Arc など）。小さなメッシュでは、AS と MS の起動のオーバーヘッドのほうが大きくなることがあり、大きなメッシュで効果が出ます。ビルド時にメッシュレットを作る前処理が必要です。スキニングや頂点アニメーションは、MS で行うか、事前にコンピュートで計算しておくことになり、複雑になります。

## よくあるミス

??? failure "DispatchMesh をスレッドごとに別の値で、または分岐の中で呼ぶ"
    グループの全スレッドが同じ値で、`GroupMemoryBarrierWithGroupSync` のあとに一様に呼ぶ。

??? failure "WavePrefixCountBits で出力位置を決め、ウェーブが 32 より小さい GPU で壊れる"
    groupshared のカウンターと `InterlockedAdd` を使う。

??? failure "SetMeshOutputCounts を呼ばずに出力して、何も描かれない"
    全スレッドが出力を書く前に同じ値で呼ぶ。

??? failure "MS の group_id を全体の通し番号だと思って、メッシュレットを取り違える"
    `group_id` は、その AS グループが起動した MS の中での番号。ペイロードの添字にだけ使う。

??? failure "メッシュレットの頂点や三角形が上限（64 と 124）を超える"
    meshoptimizer に同じ上限を渡す。HLSL の配列サイズと一致させる。

??? failure "PSO の作成が失敗する（IA フラグや入力レイアウトを指定している）"
    メッシュ シェーダーの PSO は、IA に関する指定をしない。ストリーム版で作り、サブオブジェクトのずれに注意する。

??? failure "背面コーンの式を座標系に合わせず、見える面を消してしまう"
    コーンの軸をワールド空間へ変換してから判定する。視線は `center − camera`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メッシュレットは、最大 64 頂点・124 三角形ほどの塊で、境界球と背面コーンを持つ（meshoptimizer で作る）
    - [x] AS はメッシュレットを判定して、生き残りの番号をペイロードに詰め、`DispatchMesh` で MS を起動する
    - [x] MS の 1 グループが 1 メッシュレット。`SetMeshOutputCounts` のあと、頂点と三角形を出力する
    - [x] MS の `SV_GroupID` は、AS グループの中での番号で、ペイロードの添字に使う
    - [x] PSO はパイプライン ステート ストリームで作り、IA は使わない
    - [x] `ExecuteIndirect` の引数に `DISPATCH_MESH` を使えば、インスタンスごとに AS を起動できる

## 参考

- Microsoft, "Mesh Shader"（DirectX-Specs）
- Kapoulkine, "meshoptimizer"（meshopt_buildMeshlets）
- Haar, Aaltonen, "GPU-Driven Rendering Pipelines"（SIGGRAPH 2015、クラスタ カリング）
- Karis et al., "A Deep Dive into Nanite Virtualized Geometry"（SIGGRAPH 2021）

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [カリング（コンピュート）](culling.md)
- [ExecuteIndirect](execute-indirect.md)
- [バインドレス](bindless.md)
- [メッシュ シェーダー](../mesh-shaders.md)
- [LOD](../lod.md)
