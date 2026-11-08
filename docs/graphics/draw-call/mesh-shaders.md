---
title: Mesh Shader and Meshlet
tags:
  - 最適化
  - 3Dゲーム
---

# Mesh Shader and Meshlet

[GPU Driven](gpu-driven.md)でカリングを GPU に任せても、カリングの単位が「物体」や「サブメッシュ」のままだと困る場面が残ります。建物や地形のような大きな物体は画面に映るのが一部だけでも見えない部分の頂点を全部処理してしまいます。メッシュをあらかじめ小さな「塊」（Meshlet）に分けておけば、塊ごとに「見える・見えない」を決められます。Mesh Shader はこの塊をそのまま処理するための新しいシェーダー段です。

このページでは Meshlet とは何か何が改善するのか従来のパイプラインと何が違うのかを、数字で追いながら説明します。使える環境（DX12 Ultimate）と DX11 での代わりの方法も書きます。D3D12 で通して動かす実装は [Meshlets and Mesh Shaders（D3D12）](gpu-driven-dx12/meshlets.md) にあります。

!!! tip "ポイント"
    - <strong>Meshlet</strong> はメッシュを約 64 頂点・約 124 三角形の小さな塊に分割したものです。ビルド時に作ります。
    - 目的はカリングの単位を細かくすることです。見えない塊は頂点処理をまるごと省けます。
    - 塊ごとのカリング情報は境界球と法線の円錐（Normal Cone）です。円錐を使うと裏向きの塊をまとめて除外できます。
    - Mesh Shader パイプラインは、Task（Amplification）Shader が塊ごとにカリングし、Mesh Shader が頂点と三角形を出力し、ピクセルシェーダーに渡ります。入力アセンブラ・頂点シェーダー・ジオメトリ シェーダーを置き換えます。
    - DX12 Ultimate（Mesh Shader 対応）の機能で、DX11 では使えません。DX11 でも Meshlet 単位のコンピュート カリングはできます。
    - 応用として連続 LOD（Nanite 風）やマイクロポリゴンがあります。

!!! info "このページを読む前に"
    - [Draw Call](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](../optimization/bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 従来の頂点処理の限界

従来は入力アセンブラが頂点バッファとインデックス バッファを順に読み頂点シェーダーを 1 頂点ずつ実行し、三角形に組み立ててラスタライザーへ渡します。この流れは固定で途中に「この塊は要らない」と言える場所がありません。困る点を 5 つ挙げます。

1. カリングの粒度が粗い。単位は物体かサブメッシュで一部だけ見える大きな物体は、全体の頂点を処理します。
2. 三角形ごとのカリングが遅い。三角形が見えないと分かるのは頂点シェーダーのあとなので、その頂点処理はすでに無駄になっています。
3. 入力の形式が固定される。頂点バッファとインデックスの形式に縛られ圧縮した形式や自由な並びを使いにくくなります。
4. ジオメトリ シェーダーが遅い。三角形を新しく作る処理は多くの GPU で効率が悪いと知られています。
5. 頂点の再利用がキャッシュ頼りになる。同じ頂点を複数の三角形が共有しても、再利用できるかはハードウェアのキャッシュ次第です。

## Meshlet（小さな塊）

Meshlet はメッシュを頂点数と三角形数の上限つきで小さく分けた塊です。

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="メッシュを、Meshlet に分割">
<text x="20" y="24" class="fig-title">1 つのメッシュを小さな塊（Meshlet）に分割。塊ごとに、見えるか判定する</text>
<g stroke="currentColor" stroke-width="2">
<polygon points="60,200 130,110 200,200" fill="rgba(76,139,245,0.35)"/>
<polygon points="130,110 200,200 270,110" fill="rgba(46,160,67,0.35)"/>
<polygon points="200,200 270,110 340,200" fill="rgba(229,170,40,0.4)"/>
<polygon points="270,110 340,200 400,100" fill="rgba(229,72,77,0.3)"/>
<polygon points="130,110 200,60 270,110" fill="rgba(150,100,230,0.35)"/>
<polygon points="270,110 330,60 400,100" fill="rgba(76,139,245,0.25)"/>
</g>
<text x="60" y="226" style="font-size:12px">それぞれの色が 1 つの Meshlet</text>
<text x="450" y="60" style="font-weight:700">1 つの Meshlet が、持つもの</text>
<text x="450" y="84" style="font-size:12px">・頂点：最大 64 個（目安）</text>
<text x="450" y="104" style="font-size:12px">・三角形：最大 124 個（目安）</text>
<text x="450" y="124" style="font-size:12px">・境界球（見えるか判定）</text>
<text x="450" y="144" style="font-size:12px">・法線の円錐（裏向きか判定）</text>
<text x="450" y="180" style="font-weight:700">ビルド時に作る（ベイク）</text>
<text x="450" y="204" style="font-size:12px">meshoptimizer などの、ライブラリで分割</text>
<text x="450" y="224" style="font-size:12px">→ 実行時は、塊の配列を読むだけ</text>
</svg>

大きさの目安は最大 64 頂点・124 から 126 三角形です。NVIDIA が推奨する値で、GPU のスレッド グループに収まる大きさになっています。このページと D3D12 側のページは、meshoptimizer が三角形数を 4 の倍数に求めるため、124 を使います。

作り方はビルド時に meshoptimizer の `meshopt_buildMeshlets` などで、近い三角形をまとめることです。Meshlet に持たせるのは、頂点インデックス、三角形のインデックス、境界球、法線の円錐です。塊の中の頂点は 0 から 63 の小さな番号（8 ビット）で参照するので、三角形 1 つの記録が 3 バイトで済みます。

### 数字で見積もる

1 つの Meshlet に必要な記録を数えます。頂点インデックスが 64 個 × 4 バイト = 256 バイト、詰めた三角形が 124 個 × 4 バイト = 496 バイトです（D3D12 側のページでは、3 バイトを 1 つの `uint` に詰めています）。

三角形が 100 万個あるメッシュなら 124 個ずつ詰めても最低 1,000,000 ÷ 124 ≒ 8,065 個の塊になります。実際は頂点の再利用や法線のそろい具合を優先して分けるので、上限いっぱいには詰まりません。1 万個前後と見ておくのが現実的です（これは見積もりで、測った値ではありません）。

AS が 1 グループで 32 個の塊を見るなら 1 万個の塊は 10,000 ÷ 32 ≒ 313 グループで判定できます。物体の判定が 1 回で済んでいたものを 313 グループに分ける代わりに、その一部しか見えないとき MS 以降の仕事が大きく減ります。

### Meshlet カリング

塊ごとに次の 4 つの判定ができます。

1. 視錐台。境界球が視錐台の外なら除外します。
2. オクルージョン。境界球が前のフレームの深度（Hi-Z）に隠れていれば除外します（[Hi-Z](../optimization/hiz.md)）。
3. 法線の円錐。塊の全三角形がカメラと反対を向いているならまとめて除外します。バックフェイス カリングの Meshlet 版です。
4. 距離と大きさ。遠すぎる塊、小さすぎる塊を除外します。

三角形を 1 つずつ見る前に数十から百余りの三角形を一度に除外できるので、頂点処理も三角形の組み立ても、まるごと省けます。

## Mesh Shader パイプライン

Mesh Shader は従来の「入力アセンブラ → 頂点シェーダー →（ジオメトリ シェーダー）」を置き換える、新しいパイプラインです。

<svg class="fig flow" viewBox="0 0 640 250" role="img" aria-label="従来のパイプラインと、Mesh Shader パイプライン">
<defs><marker id="msA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="14" y="22" class="fig-title">従来のパイプラインと、Mesh Shader パイプライン</text>
<text x="14" y="58" style="font-size:12px">従来</text>
<rect x="60" y="40" width="150" height="40" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="135" y="60" text-anchor="middle" dominant-baseline="central">入力アセンブラ</text>
<rect x="250" y="40" width="130" height="40" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="315" y="60" text-anchor="middle" dominant-baseline="central">頂点シェーダー</text>
<rect x="430" y="40" width="130" height="40" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="495" y="60" text-anchor="middle" dominant-baseline="central">ラスタライザー</text>
<text x="14" y="168" style="font-size:12px">Mesh</text>
<rect x="60" y="150" width="150" height="40" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="135" y="170" text-anchor="middle" dominant-baseline="central">Task（AS）</text>
<rect x="250" y="150" width="130" height="40" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="315" y="170" text-anchor="middle" dominant-baseline="central">Mesh（MS）</text>
<rect x="430" y="150" width="130" height="40" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="495" y="170" text-anchor="middle" dominant-baseline="central">ラスタライザー</text>
<g stroke="currentColor" stroke-width="2" fill="none" marker-end="url(#msA)">
<line x1="210" y1="60" x2="246" y2="60"/><line x1="380" y1="60" x2="426" y2="60"/>
<line x1="210" y1="170" x2="246" y2="170"/><line x1="380" y1="170" x2="426" y2="170"/>
</g>
<text x="60" y="108" style="font-size:12px">頂点を 1 個ずつ順に読む。途中で「要らない」と言えない</text>
<text x="60" y="218" style="font-size:12px">AS が塊を選び、MS が頂点と三角形を直接書く。入力アセンブラは通らない</text>
</svg>

- Task Shader（Amplification Shader）は、Meshlet ごとのカリングをします。見える Meshlet の数だけ Mesh Shader を起動します。起動する数を GPU が動的に決めます。
- Mesh Shader は 1 つの Meshlet をスレッド グループ全体で処理します。頂点の位置と三角形を自分で出力します。入力はメモリから自由に読めます。
- ラスタライザーとピクセル シェーダーは、従来と同じです。

Mesh Shader の最小の形は、次のとおりです。

```hlsl
[outputtopology("triangle")]                                   // 出力は三角形のリスト
[numthreads(128, 1, 1)]                                        // 1 グループ 128 スレッド
void MeshMain(uint gtid : SV_GroupThreadID, uint gid : SV_GroupID,   // グループ内の番号と、グループの番号
              out vertices VertexOut verts[64],                // 頂点の出力先(上限 64)
              out indices uint3 tris[124]) {                   // 三角形の出力先(上限 124)
  Meshlet m = meshlets[gid];                                   // このグループが担当する Meshlet
  SetMeshOutputCounts(m.vertex_count, m.triangle_count);       // 実際に出す頂点数・三角形数の宣言
  if (gtid < m.vertex_count) verts[gtid] = TransformVertex(m, gtid);   // スレッド 1 つが頂点 1 つを変換して書く
  if (gtid < m.triangle_count) tris[gtid] = LoadTriangle(m, gtid);     // スレッド 1 つが三角形 1 つを書く
}
```

`SetMeshOutputCounts` はこのグループが実際に出す頂点数と三角形数の宣言です。出力の配列は上限の大きさで宣言しますが、ラスタライザーに渡るのは宣言した個数までです。出力を書く前にグループの全スレッドが同じ値で呼ぶ必要があります。

出力の配列はグループ全体で 1 つの配列です。スレッドは番号を割り当てて分担して書きます。頂点シェーダーのように「1 頂点につき 1 回」ではなく、グループ全体で 1 つの塊を作るという見方に切り替えるのがこの段のコツです。

### AS と MS をつなげた動くコード

カリングする AS と頂点を出す MS を 1 つのファイルにまとめます。`dxc` で `as_6_5`、`ms_6_5`、`ps_6_5` のそれぞれにコンパイルして、エラーが出ないことを確かめました。GPU では動かしていません。視錐台の判定とライティングは説明のために足した簡単な実装です。

```hlsl
cbuffer FrameCB : register(b0) {
  float4x4 view_projection;   // ワールド → クリップ(行ベクトル: v * M)
  float4 frustum_planes[6];   // 視錐台の 6 平面(xyz = 内向き法線, w = 距離)
  float3 camera_position;     // ワールド空間のカメラ位置
  float pad0;                 // 16 バイト境界にそろえる詰め物
};

struct Meshlet {              // 1 メッシュレットの範囲
  uint vertex_offset;         // 頂点インデックス配列の開始位置
  uint triangle_offset;       // 詰めた三角形配列の開始位置
  uint vertex_count;          // 頂点数(最大 64)
  uint triangle_count;        // 三角形数(最大 124)
};

struct MeshletBounds {        // カリング用
  float3 center;              // 境界球の中心(ワールド空間とする)
  float radius;               // 境界球の半径
  float3 cone_axis;           // 法線の円錐の軸
  float cone_cutoff;          // 円錐の開き(cos に近い量)
};
```

定数バッファにはワールドからクリップへの行列、視錐台の 6 平面、カメラ位置を置きます。`Meshlet` は塊の範囲を指す 16 バイト、`MeshletBounds` は境界球と円錐を合わせた 32 バイトです。ここでは簡単にするため境界球の中心をワールド空間として扱います。インスタンスごとのワールド行列を掛ける方法は、[D3D12 のメッシュレットのページ](gpu-driven-dx12/meshlets.md)にあります。

```hlsl
struct Vertex {
  float3 position;            // メッシュ空間の位置
  float3 normal;              // 法線
  float2 uv;                  // テクスチャ座標
};

struct VertexOut {            // MS → PS
  float4 position : SV_Position;   // クリップ空間の位置(必須)
  float3 normal : NORMAL;          // 法線
  float2 uv : TEXCOORD0;           // テクスチャ座標
};

StructuredBuffer<Meshlet> meshlets : register(t0);          // 塊の範囲
StructuredBuffer<MeshletBounds> bounds : register(t1);      // 塊のカリング情報
StructuredBuffer<uint> meshlet_vertices : register(t2);     // 塊ごとの頂点インデックス
StructuredBuffer<uint> meshlet_triangles : register(t3);    // 詰めた三角形
StructuredBuffer<Vertex> vertices : register(t4);           // 頂点本体
```

頂点バッファは頂点バッファとしてではなく構造化バッファとして読みます。入力アセンブラを通らないので、頂点の並びをシェーダーの側が自由に決められます。

```hlsl
#define AS_GROUP_SIZE 32

struct Payload {
  uint meshlet_indices[AS_GROUP_SIZE];   // 生き残ったメッシュレットの番号
};

groupshared Payload s_payload;           // DispatchMesh に渡せるのは groupshared だけ
groupshared uint s_count;                // 生き残った数

bool Visible(MeshletBounds b) {
  for (int i = 0; i < 6; ++i) {                                       // 6 平面を順に
    if (dot(frustum_planes[i].xyz, b.center) + frustum_planes[i].w < -b.radius) return false;   // 球が平面の外側に完全に出ている
  }
  float3 to_meshlet = b.center - camera_position;                    // カメラから塊へ
  return dot(to_meshlet, b.cone_axis) < b.cone_cutoff * length(to_meshlet) + b.radius;   // 全面が背を向けているなら false
}
```

視錐台の判定は球の中心から各平面までの符号つき距離が `-radius` より小さければ、その平面の外側に完全に出ている、という考え方です。1 つでも外側に出ていれば `false` を返します。円錐の判定はカメラから塊へのベクトルと円錐の軸の内積を `cone_cutoff × 距離 + 半径` と比べます。式の意味は[D3D12 のページ](gpu-driven-dx12/meshlets.md)に詳しく書いています。

```hlsl
[numthreads(AS_GROUP_SIZE, 1, 1)]
void ASMain(uint gtid : SV_GroupThreadID, uint gid : SV_GroupID) {
  if (gtid == 0) s_count = 0;                                         // カウンターを 0 に
  GroupMemoryBarrierWithGroupSync();                                  // 全員がそろうのを待つ
  uint index = gid * AS_GROUP_SIZE + gtid;                            // 担当のメッシュレット
  uint total, stride;
  meshlets.GetDimensions(total, stride);                              // メッシュレットの総数
  if (index < total && Visible(bounds[index])) {                      // 範囲内で、見えるなら
    uint slot;
    InterlockedAdd(s_count, 1, slot);                                 // 位置を確保
    s_payload.meshlet_indices[slot] = index;                          // 番号を詰める
  }
  GroupMemoryBarrierWithGroupSync();                                  // 全員の書き込みを待つ
  DispatchMesh(s_count, 1, 1, s_payload);                             // 生き残った数だけ MS を起動
}
```

AS のスレッドは 1 つの塊を見て、見えるなら `InterlockedAdd` で確保した位置に番号を書きます。2 回目のバリアは全スレッドの書き込みが終わる前に `DispatchMesh` を呼ばないための待ちです。`s_count` が 0 なら MS は 1 つも起動しません。

```hlsl
#define MS_GROUP_SIZE 128

[outputtopology("triangle")]
[numthreads(MS_GROUP_SIZE, 1, 1)]
void MSMain(uint gtid : SV_GroupThreadID, uint gid : SV_GroupID,
            in payload Payload payload,
            out vertices VertexOut out_vertices[64],
            out indices uint3 out_triangles[124]) {
  Meshlet m = meshlets[payload.meshlet_indices[gid]];                 // 自分のメッシュレット
  SetMeshOutputCounts(m.vertex_count, m.triangle_count);              // 出す個数の宣言
  for (uint v = gtid; v < m.vertex_count; v += MS_GROUP_SIZE) {       // 頂点を手分けして
    Vertex vtx = vertices[meshlet_vertices[m.vertex_offset + v]];
    VertexOut o;
    o.position = mul(float4(vtx.position, 1.0), view_projection);    // モデル = ワールドとする(足した)
    o.normal = vtx.normal;
    o.uv = vtx.uv;
    out_vertices[v] = o;
  }
  for (uint t = gtid; t < m.triangle_count; t += MS_GROUP_SIZE) {     // 三角形を手分けして
    uint p = meshlet_triangles[m.triangle_offset + t];
    out_triangles[t] = uint3(p & 0xFF, (p >> 8) & 0xFF, (p >> 16) & 0xFF);
  }
}
```

MS の `gid` は AS が起動した MS グループの中での番号です。ペイロードの添字として使います。ループが `v += MS_GROUP_SIZE` なのは塊の頂点数がスレッド数（128）を超えても動くようにするためです。ここでは 64 頂点が上限なので、実際には 1 周で終わります。

```hlsl
float4 PSMain(VertexOut input) : SV_Target {
  float3 n = normalize(input.normal);                                 // 法線を正規化
  float l = saturate(dot(n, normalize(float3(0.3, 1.0, -0.4))));      // 固定の向きの光(一例)
  return float4(l.xxx * 0.8 + 0.2, 1.0);                              // 環境光 0.2 を足す
}
```

ピクセル シェーダーは従来のものがそのまま使えます。MS の出力 `VertexOut` が入力になります。

### 何が改善するのか

1. カリングが細かくなります。Meshlet 単位で頂点処理の前に除外できるので、頂点と三角形の処理が大きく減ります。
2. メモリの自由度が上がります。頂点データを圧縮や量子化した形式で持てます。
3. 入力アセンブラのボトルネックを避けられます。頂点バッファから頂点シェーダーへという固定の流れから離れます。
4. GPU Driven と自然に組み合わせられます。Task Shader がカリングをパイプラインの中で行います。
5. ジオメトリを動的に作る処理（テッセレーションや LOD の細かな制御）を柔軟に書けます。

### 数字で見る効果

効果の大きさを仮定を置いた数字で見ます。ある建物が 1,000 個の塊でできていて、カメラから見えるのが 50 個だけだったとします（これは説明のための仮定で、実際の割合はカメラの位置で変わります）。

<svg class="fig illust" viewBox="0 0 640 220" role="img" aria-label="頂点変換の回数の比較">
<text x="20" y="24" class="fig-title">頂点変換の最大回数(1,000 塊のうち 50 塊が見える場合)</text>
<g stroke="currentColor" stroke-width="1.5">
<rect x="180" y="50" width="400" height="34" fill="rgba(229,72,77,0.35)"/>
<rect x="180" y="110" width="20" height="34" fill="rgba(46,160,67,0.4)"/>
</g>
<text x="20" y="72" style="font-size:13px">塊で絞らない</text><text x="190" y="72" style="font-size:12px">64,000 回(1,000 × 64)</text>
<text x="20" y="132" style="font-size:13px">AS で絞る</text><text x="210" y="132" style="font-size:12px">3,200 回(50 × 64)</text>
<text x="20" y="180" style="font-size:12px">どちらも「1 塊の頂点が上限の 64 個」の最大値。差は 20 分の 1 になる。</text>
</svg>

1,000 × 64 = 64,000、50 × 64 = 3,200 で、頂点変換が最大 20 分の 1 になります。三角形の出力も同じ比です。ただし、AS が 1,000 個の塊を判定する仕事が増えます。判定 1 回は球と 6 平面の比較と円錐の内積だけで、頂点変換よりずっと軽い処理です。

## 使える環境

- DirectX 12 Ultimate（Feature Level 12_2）。Mesh Shader は Shader Model 6.5 以降です。
- Vulkan では `VK_EXT_mesh_shader` です。NVIDIA・AMD・Intel の新しい GPU で使えます。
- DirectX 11 では使えません。
- GPU は NVIDIA が Turing 以降、AMD が RDNA2 以降、Intel が Arc です。

!!! warning "DX11 では、Mesh Shader は使えない"
    このサイトの描画の例は DX11 ですが、Mesh Shader は DX12 Ultimate / Vulkan の機能です。DX11 でも Meshlet の考え方は活かせます（下記）。

### DX11 での代わりの方法

DX11 では Mesh Shader の代わりにコンピュート シェーダーで塊を選びます。

1. Meshlet 単位のコンピュート カリング。コンピュート シェーダーで Meshlet を判定し、生き残った Meshlet の三角形をインデックス バッファに書き出して、`DrawIndexedInstancedIndirect` で描きます。
2. クラスター単位のインダイレクト。Meshlet を描画の単位にして、インダイレクトの引数で描きます。
3. 三角形フィルタリング。コンピュートで見えない三角形を除外し、インデックス バッファを詰め直します。頂点処理の前に行います。

効果は Mesh Shader ほどではありません。それでも「頂点処理の前に塊ごとに除外する」という考え方は使えます。D3D11 での通して動く形は[GPU Driven Rendering](gpu-driven.md) にあります。

## 連続 LOD とマイクロポリゴン（Nanite 風）

Meshlet は細かい詳細度の制御の土台にもなります。

- クラスター階層（連続 LOD）。Meshlet を木の階層にして、画面上の大きさに合った詳細度の Meshlet だけを選びます。ポップのない滑らかな LOD になります。
- マイクロポリゴン。三角形が 1 ピクセル以下になります。ハードウェアのラスタライザーは小さな三角形が苦手なので（[Overdraw](../optimization/overdraw.md)）、コンピュートによるソフトウェア ラスタライズを併用します。
- Visibility Buffer。三角形の ID だけを書き材質の計算を後に回します（[Visibility Buffer](../lighting/visibility-buffer.md)）。

Unreal Engine 5 の Nanite は、これらの組み合わせ（クラスター階層・GPU Driven・ソフトウェア ラスタライズ・Visibility Buffer）です。数十億の三角形を画面のピクセル数に見合う量だけ描きます。このページは Nanite の解説論文を読んでいません。上の説明は一般に知られている構成の紹介です。

## 導入の判断

- 三角形が少ない（数十万）、または DX11 のときは Meshlet は要りません。普通のカリングと LOD で足ります。
- 三角形が多い高密度のメッシュなら Meshlet と GPU Driven（DX12 / Vulkan）が合います。
- 連続 LOD が欲しいならクラスター階層を使います。ビルド時の処理が大変です。

Meshlet の利点は高密度のメッシュで大きく出ます。普通のゲームの中程度のモデルでは従来のパイプラインで十分なことが多いです。

## 確かめたこと

- 上の HLSL を `dxc` で `as_6_5`、`ms_6_5`、`ps_6_5` にコンパイルしてエラーが出ないことを確かめました。
- GPU では動かしていません。描画結果も速さも測っていません。
- 20 分の 1 などの数字はこのページで置いた仮定（1,000 塊のうち 50 塊が見える）から計算した値で、実機で測った値ではありません。

## よくあるミス

??? failure "Mesh Shader を DX11 で使おうとする"
    DX11 には Mesh Shader の段がありません。DX12 Ultimate か Vulkan が必要です。DX11 ではコンピュートで塊を選ぶ方法に切り替えます。

??? failure "三角形が少ないのに、Meshlet 化して遅くなる"
    AS と MS を起動する分のオーバーヘッドが、除外できる頂点処理より大きくなります。数万三角形の小さなメッシュは従来のパイプラインのままにします。

??? failure "Meshlet の大きさを GPU に合わせずに効率が落ちる"
    頂点が少なすぎる塊はスレッド グループの大半が遊びます。ベンダーの推奨（64 頂点・124 から 126 三角形）を出発点にして、実機で測って調整します。

??? failure "法線の円錐が不正確で、見えるはずの物が消える"
    円錐の軸をワールド空間へ変換していない、半径を足していないといった原因で、見える塊を消します。判定は安全側（少し多めに残す）に倒します。

??? failure "Meshlet を実行時に毎回作る"
    分割はコストの高い処理で、毎フレーム行うと意味がありません。ビルド時に作り結果をファイルに保存します（[ベイク](../../optimize/baking.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Meshlet は、約 64 頂点・124 三角形の小さな塊</strong>です。ビルド時に分割します。
    - [x] 目的はカリングの単位を細かくすることです。塊ごとに頂点処理の前に除外します（境界球・法線の円錐・Hi-Z）。
    - [x] Mesh Shader は、Task Shader（カリング）から Mesh Shader（頂点・三角形の出力）へと進み、従来の頂点処理を置き換えます。
    - [x] DX12 Ultimate / Vulkan の機能で、DX11 では使えません（コンピュートで近いことができます）。
    - [x] 応用は連続 LOD・マイクロポリゴン・Visibility Buffer（Nanite 風）です。

## 参考資料

このページは次の資料を読まずに書きました。内容は一般に知られている説明と手元でコンパイルして確かめた HLSL に基づいています。

- Microsoft, "Mesh Shader"（DirectX-Specs）。未読。
- Arseny Kapoulkine, "meshoptimizer"（`meshopt_buildMeshlets`）。未読。
- Brian Karis, Rune Stubbe, Graham Wihlidal, "A Deep Dive into Nanite Virtualized Geometry"（SIGGRAPH 2021）。未読。

## 関連ページ

- [描画の最適化（詳細）](../optimization/index.md)
- [Culling](culling.md)
- [GPU Driven Rendering](gpu-driven.md)
- [Meshlets and Mesh Shaders（D3D12）](gpu-driven-dx12/meshlets.md)
- [Visibility Buffer](../lighting/visibility-buffer.md)
- [Hi-Z and Screen-Space Tracing](../optimization/hiz.md)
