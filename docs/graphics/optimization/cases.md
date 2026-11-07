---
title: Optimization Case Studies
tags:
  - 最適化
  - 3Dゲーム
---

# Optimization Case Studies

「フレームが重い」と言われたとき最初にやることは手法を選ぶことではありません。どこが重いかを決めることです。CPU が重いのにシェーダーを直しても速くなりません。ピクセルが重いのにドロー コールを減らしても同じです。このページでは症状から原因の種類を絞る手順を示し、3 つの事例で「切り分け → 計測 → 原因 → 直す → 測り直す」を、コード付きで追います。事例のコードは HLSL をコンパイルして確かめ数字は C++ で実際に数えて出しています。

!!! tip "ポイント"
    - 解像度を下げて速くなるなら GPU のピクセル側、変わらないなら CPU か頂点側が原因である。
    - 直したあとの効果は見積もりでなく測り直した数字で確かめる。
    - ドロー コールの削減は「種類ごとにまとめる」と「見えない物を先に捨てる」の 2 段で効く。
    - ライトの数が増えたときは、画素が回すライトの数を減らす（クラスター）。
    - 半透明の重ね書きは解像度と枚数の両方を減らすと積で効く。

!!! info "このページを読む前に"
    - [Optimization](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 読んだ資料について {#sources}

このページは論文の解説ではなく、手法の使い分けをまとめた実践のページです。論文や発表は引いていません。数字は 2 種類に分かれます。「C++ で数えた」と書いたものは、このページのコードで出した値です。「例」と書いたミリ秒の値は考え方を示すための仮の値で、実測ではありません。

## 切り分けから始める {#triage}

最初の実験は解像度を半分にすることです。フレーム時間が大きく減れば GPU のピクセル処理（シェーダー、帯域、ブレンド）が原因です。変わらなければ CPU か頂点処理が原因です。ここから先はプロファイラーで確かめます。

CPU が原因ならドロー コールの数とそのたびに積んでいるステートの変更を見ます。GPU のピクセル側ならオーバードローの可視化とシェーダーの命令数を見ます。VRAM が足りないならテクスチャの大きさと数を見ます。

<svg class="fig flow" viewBox="0 0 680 184" role="img" aria-label="解像度を下げる切り分け"><defs><marker id="cs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">解像度を半分にして、フレーム時間を測る</text><rect x="260" y="30" width="160" height="40" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="340.0" y="54.0" text-anchor="middle" font-size="11" fill="currentColor">解像度を半分にする</text><line x1="300" y1="70" x2="150" y2="110" stroke="#94a3b8" marker-end="url(#cs-a)"/><line x1="380" y1="70" x2="530" y2="110" stroke="#94a3b8" marker-end="url(#cs-a)"/><text x="200" y="92" text-anchor="middle" font-size="10" fill="currentColor">速くなった</text><text x="480" y="92" text-anchor="middle" font-size="10" fill="currentColor">変わらない</text><rect x="30" y="110" width="240" height="62" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="150.0" y="131.0" text-anchor="middle" font-size="11" fill="currentColor">GPU のピクセル側</text><text x="150.0" y="145.0" text-anchor="middle" font-size="11" fill="currentColor">シェーダー・帯域・ブレンド</text><text x="150.0" y="159.0" text-anchor="middle" font-size="11" fill="currentColor">(事例 2, 3)</text><rect x="410" y="110" width="240" height="62" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="530.0" y="131.0" text-anchor="middle" font-size="11" fill="currentColor">CPU か頂点側</text><text x="530.0" y="145.0" text-anchor="middle" font-size="11" fill="currentColor">ドロー コール・頂点・カリング</text><text x="530.0" y="159.0" text-anchor="middle" font-size="11" fill="currentColor">(事例 1)</text></svg>

## 症状から探す {#symptoms}

| 症状 | ボトルネック | 効く手法 | ページ |
| --- | --- | --- | --- |
| 解像度を下げても速くならない | CPU | バッチ・インスタンシング・GPU Driven | [ドロー コール](../draw-call/draw-calls.md) |
| 解像度を下げると速くなる | GPU（ピクセル） | 低解像度・TAA・シェーダーの軽量化 | [低解像度](low-res-effects.md) |
| ライトを増やすと極端に重い | GPU（ライティング） | Deferred・Tiled・Clustered | [Deferred](../lighting/forward-deferred.md) |
| G-Buffer の書き込みが重い | 帯域幅 | フォーマット・Visibility Buffer | [帯域幅](bandwidth.md) |
| 三角形が多い | GPU（頂点） | LOD・カリング・Meshlet | [LOD](../draw-call/lod.md) |
| 半透明で重くなる | GPU（ピクセル・帯域） | 縮小バッファ・枚数削減 | [粒子](../translucency/particles-cost.md) |
| 影を付けると重い | CPU・GPU（頂点） | カスケード・影用カリング・キャッシュ | [影](../shadows/cost.md) |
| VRAM が足りない | VRAM | 圧縮・ストリーミング | [テクスチャ](texture-streaming.md) |
| ポストプロセスが重い | 帯域幅 | パスをまとめる・縮小 | [ポストの重さ](../postprocess/cost.md) |
| フレーム時間が不安定 | 全体 | 動的解像度・予算の設計 | [予算](../../optimize/frame-budget.md) |

## 事例 1：森でドロー コールが 8,000 回 {#case-forest}

### 症状と切り分け {#forest-triage}

森の場面で 24 ms（約 40 FPS）。ほかの場面は 12 ms です。解像度を半分にしても 24 ms のままなので、CPU が原因です。プロファイラーで見ると描画命令の記録に 14 ms かかっています（例）。ドロー コールは約 8,000 回で、内訳は木が 3,000、草が 4,000、岩が 1,000 です。

原因は木や草を 1 本ずつ描いていることです。1 回のドローごとに定数バッファの更新とステートの設定が走りドライバーの仕事が積み上がります。

### 直し方 1：種類ごとにまとめる {#forest-instancing}

木 5 種類、草 3 種類、岩 4 種類なら種類ごとにインスタンス描画にまとめて、12 回に減ります。C++ で数えた量は次のとおりです。

結果は末尾の「数字を出した C++」の実行結果にあります。要点は次のとおりです。

1 本ずつなら定数バッファが 256 バイト境界で 8,000 本分、1.95 MiB です。インスタンス バッファなら 1 本 64 バイトの行列で 0.49 MiB です。転送量が 4 分の 1 になるうえドロー コールが 8,000 回から 12 回になります。

### 直し方 2：見えない物を先に捨てる {#forest-culling}

まとめたあとも画面に映らない物まで描くと頂点処理が無駄になります。C++ で 400 m 四方に散らばった 8,000 本のうちファー 150 m・画角 60 度の視錐台に入る数を数えると、1,241 本（15.5 %）です。残りの 84.5 % は描く必要がありません。

視錐台カリングをコンピュート シェーダーで行い残った物の番号を種類ごとに並べます。

```hlsl
// 事例 1: 森のドロー コールを減らす。
// 8,000 本の木・草・岩を、種類ごとに 1 回のインスタンス描画にまとめ、
// 視錐台に入った物だけを GPU で選び出す（コンピュート シェーダー）。

// ---- 入力: シーンの全インスタンス ----
struct InstanceData {
  float4x4 world;        // 物体 → ワールド（行ベクトル用。mul(v, world)）
  float4 bounding;       // xyz = ワールドの中心 [m]、w = 境界球の半径 [m]
  uint type;             // メッシュの種類（0 = 木 A、1 = 木 B、…）
  uint3 pad;             // 16 バイト境界にそろえる。足した処理
};
StructuredBuffer<InstanceData> g_instances : register(t0);

// ---- 出力: 種類ごとの、見える物の添字の並び ----
// g_visible[type * g_max_per_type + k] に、g_instances の添字を入れる。
RWStructuredBuffer<uint> g_visible : register(u0);
// 間接描画の引数バッファ。種類ごとに 5 個の uint（20 バイト）が並ぶ:
//   [0] IndexCountPerInstance  [1] InstanceCount  [2] StartIndexLocation  [3] BaseVertexLocation  [4] StartInstanceLocation
// このシェーダーが書くのは [1] の InstanceCount だけ。ほかは CPU がメッシュごとに、あらかじめ入れておく。
RWByteAddressBuffer g_args : register(u1);

cbuffer CullCB : register(b0) {
  float4 g_planes[6];    // 視錐台の 6 平面。xyz = 内向きの法線、w = 平面方程式の定数 d（dot(n, p) + d >= 0 が内側）
  float3 g_camera_pos;   // カメラのワールド位置 [m]
  float g_max_distance;  // これより遠い物は描かない [m]（一例: 150）
  uint g_instance_count; // 全インスタンス数
  uint g_max_per_type;   // 種類ごとの上限
  float2 g_pad;
};

// 境界球が、6 平面のすべての内側にあるか調べる（球と錐台の標準的な判定）。
bool SphereInFrustum(float3 center, float radius) {
  [unroll] for (int i = 0; i < 6; ++i) {
    // 球の中心から平面までの符号つき距離。-radius より小さければ、完全に外側にある。
    float dist = dot(g_planes[i].xyz, center) + g_planes[i].w;
    if (dist < -radius) return false;
  }
  return true;
}
```

インスタンスは位置と半径（境界球）を持ちます。球が 6 つの平面すべての内側にあるか調べるのが、視錐台カリングの標準的な方法です。符号つき距離が `-radius` より小さければ、球は完全に外側にあります。

```hlsl
[numthreads(64, 1, 1)]    // 1 グループ 64 スレッド。1 スレッド = 1 インスタンス
void main(uint3 id : SV_DispatchThreadID) {
  uint i = id.x;                              // このスレッドが見るインスタンスの番号
  if (i >= g_instance_count) return;          // 端数のスレッドは何もしない

  InstanceData inst = g_instances[i];

  // 1. 距離カリング。境界球の手前の端までが最大距離を超えたら捨てる。
  float dist = distance(inst.bounding.xyz, g_camera_pos);
  if (dist - inst.bounding.w > g_max_distance) return;

  // 2. 視錐台カリング。
  if (!SphereInFrustum(inst.bounding.xyz, inst.bounding.w)) return;

  // 3. 生き残った物を、種類ごとの並びに追加する。
  //    種類ごとの InstanceCount（引数バッファの type * 20 + 4 バイト目）を 1 つ進めて、書き込み位置を得る。
  uint slot;
  g_args.InterlockedAdd(inst.type * 20 + 4, 1, slot);   // slot = 加算前の値 = この物の位置
  if (slot < g_max_per_type) {                        // 上限を超えたぶんは捨てる（溢れても壊れない）
    g_visible[inst.type * g_max_per_type + slot] = i;
  }
}
```

`InterlockedAdd` で種類ごとの `InstanceCount` を 1 つ増やし、加算前の値を書き込み位置にします。この値が間接描画の引数にそのまま使われます。上限を超えたぶんを捨てるのは、バッファの外に書かないためです。見える物が上限を超えると遠くの木が消えるので、上限は余裕をもって決めます。

次が CPU 側のコードです。`DrawIndexedInstancedIndirect` に引数バッファの位置を渡すだけで、CPU は何本描くかを知りません。

```cpp
// 事例 1 の CPU 側（Direct3D 11）。GPU カリングの結果を、間接描画に渡す。
// 作るもの: 引数バッファ（種類ごとに 20 バイト）、見える物の添字バッファ。
#include <d3d11.h>
#include <wrl/client.h>

#include <array>
#include <cstdint>

using Microsoft::WRL::ComPtr;

constexpr UINT kTypeCount = 12;          // 木 5 + 草 3 + 岩 4
constexpr UINT kMaxPerType = 4096;       // 種類ごとの、見える物の上限

// 間接描画の引数 1 つぶん（D3D11_DRAW_INDEXED_INSTANCED_INDIRECT_ARGS と同じ並び）。
struct DrawArgs {
  UINT index_count;       // 1 インスタンスのインデックス数（メッシュで決まる）
  UINT instance_count;    // 描くインスタンス数 ← GPU のカリングが書く
  UINT start_index;       // インデックス バッファの先頭
  INT base_vertex;        // 頂点バッファの先頭
  UINT start_instance;    // インスタンス ID の開始値
};

struct CullResources {
  ComPtr<ID3D11Buffer> args;                    // 引数バッファ
  ComPtr<ID3D11UnorderedAccessView> args_uav;   // カリング シェーダーが InstanceCount を書く入口
  ComPtr<ID3D11Buffer> visible;                 // 見える物の添字の並び（種類ごとに kMaxPerType 個）
  ComPtr<ID3D11UnorderedAccessView> visible_uav;
  ComPtr<ID3D11ShaderResourceView> visible_srv; // 頂点シェーダーが読む入口
  std::array<DrawArgs, kTypeCount> template_args;   // 毎フレーム書き戻す元（instance_count = 0）
};

HRESULT CreateCullResources(ID3D11Device* device, const std::array<UINT, kTypeCount>& index_counts,
                            CullResources* out) {
  // ---- 引数バッファ ----
  // DRAWINDIRECT_ARGS: DrawIndexedInstancedIndirect の引数に使える。
  // ALLOW_RAW_VIEWS: ByteAddressBuffer として UAV を作れる（シェーダーの RWByteAddressBuffer）。
  D3D11_BUFFER_DESC args_desc = {};
  args_desc.ByteWidth = sizeof(DrawArgs) * kTypeCount;
  args_desc.Usage = D3D11_USAGE_DEFAULT;
  args_desc.BindFlags = D3D11_BIND_UNORDERED_ACCESS;                       // CS が書く
  args_desc.MiscFlags = D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS | D3D11_RESOURCE_MISC_BUFFER_ALLOW_RAW_VIEWS;
  HRESULT hr = device->CreateBuffer(&args_desc, nullptr, &out->args);
  if (FAILED(hr)) return hr;

  D3D11_UNORDERED_ACCESS_VIEW_DESC args_uav = {};
  args_uav.Format = DXGI_FORMAT_R32_TYPELESS;                              // RAW ビューの決まり
  args_uav.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
  args_uav.Buffer.NumElements = args_desc.ByteWidth / 4;                   // 4 バイトの要素数
  args_uav.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_RAW;
  hr = device->CreateUnorderedAccessView(out->args.Get(), &args_uav, &out->args_uav);
  if (FAILED(hr)) return hr;

  // 毎フレーム書き戻す元の引数。InstanceCount は 0（GPU が数える）、ほかは固定。
  for (UINT t = 0; t < kTypeCount; ++t) {
    out->template_args[t] = {index_counts[t], 0, 0, 0, 0};
  }

  // ---- 見える物の添字バッファ（StructuredBuffer<uint>）----
  D3D11_BUFFER_DESC vis_desc = {};
  vis_desc.ByteWidth = sizeof(UINT) * kTypeCount * kMaxPerType;
  vis_desc.Usage = D3D11_USAGE_DEFAULT;
  vis_desc.BindFlags = D3D11_BIND_UNORDERED_ACCESS | D3D11_BIND_SHADER_RESOURCE;   // CS が書き、VS が読む
  vis_desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
  vis_desc.StructureByteStride = sizeof(UINT);
  hr = device->CreateBuffer(&vis_desc, nullptr, &out->visible);
  if (FAILED(hr)) return hr;
  hr = device->CreateUnorderedAccessView(out->visible.Get(), nullptr, &out->visible_uav);   // 既定のビューでよい
  if (FAILED(hr)) return hr;
  return device->CreateShaderResourceView(out->visible.Get(), nullptr, &out->visible_srv);
}

// 毎フレーム: カウンターを 0 に戻す → カリング → 種類ごとに間接描画。
void CullAndDraw(ID3D11DeviceContext* context, CullResources& r, ID3D11ComputeShader* cull_cs,
                 UINT instance_count) {
  // 1. 引数バッファを初期値（InstanceCount = 0）に戻す。GPU が足し込むので、必ず戻す。
  context->UpdateSubresource(r.args.Get(), 0, nullptr, r.template_args.data(), 0, 0);

  // 2. カリングを動かす。1 グループ 64 スレッド = 64 インスタンス。切り上げで割る。
  ID3D11UnorderedAccessView* uavs[2] = {r.visible_uav.Get(), r.args_uav.Get()};
  UINT initial[2] = {0, 0};                                // 追加カウンターは使わないので 0
  context->CSSetShader(cull_cs, nullptr, 0);
  context->CSSetUnorderedAccessViews(0, 2, uavs, initial);
  context->Dispatch((instance_count + 63) / 64, 1, 1);

  // 3. UAV を外す。同じリソースを、UAV と描画の入力として同時に束縛できない。
  ID3D11UnorderedAccessView* null_uavs[2] = {};
  context->CSSetUnorderedAccessViews(0, 2, null_uavs, initial);

  // 4. 種類ごとに 1 回ずつ描く。InstanceCount は GPU が決めたので、CPU は個数を知らない。
  //    引数バッファの中の、その種類の開始位置（20 バイトずつ）を渡す。
  for (UINT t = 0; t < kTypeCount; ++t) {
    // （ここで、その種類のメッシュと、visible_srv の頂点シェーダーへの束縛を済ませておく）
    context->DrawIndexedInstancedIndirect(r.args.Get(), sizeof(DrawArgs) * t);
  }
}
```

このコードは MSVC で `/c`（コンパイルのみ）で確かめました。実行はしていません。カウンターを毎フレーム戻すことを忘れると、`InstanceCount` が溜まり続けて描画数が増えていきます。

### 結果と次の一手 {#forest-result}

描画命令の記録が 14 ms から 1 ms 程度になりフレームが 11 ms になる、という見積もりです（例）。次は距離で LOD を切り替える（[LOD](../draw-call/lod.md)）か Hi-Z で手前の物に隠れた物を捨てる（[Culling](../draw-call/culling.md)）ことを考えます。

## 事例 2：ライトを 200 個にしたら極端に重い {#case-lights}

### 症状と切り分け {#lights-triage}

ライトを 20 個から 200 個に増やすと GPU が 18 ms から 55 ms になりました（例）。解像度を下げると速くなるので、GPU のピクセル処理です。ライティングのパスが重くフォワード描画で、各ピクセルが全 200 個のライトをループしています。

### 数で見る {#lights-numbers}

1080p は 207 万画素で、全ライトを回すと 200 × 207 万 ＝ 4.15 億回のライト評価です。多くのライトはその画素に届きません。ライトの半径が 8 m ならほとんどの画素にとって、200 個のうち数個〜数十個しか影響しません。

そこで、画面を 16 × 9 のタイルに分け奥行きを 24 層に分けて、クラスター（小さな箱）にします。C++ でライト 200 個（半径 8 m）をランダムに置いて数えた結果です。

クラスターあたりのライト数は平均 23.8 個、最大 48 個でした。全クラスターの平均で見積もると、画素が回す回数は 4.94 千万回で、全ライトを回す場合の約 8 分の 1 です。クラスターの割り当て自体は 3,456 クラスター × 200 ライト ＝ 約 69 万回の比較で、画素のループに比べて無視できます。

この数字は全クラスターを同じ重みで平均した目安です。実際には、画面に映る面の奥行きに偏りがあり画素が属するクラスターの分布は一様ではありません。

### 直し方：クラスターに先に集める {#lights-fix}

```hlsl
// 事例 2: ライト 200 個のクラスタード ライティング。
// 画面を 16 x 9 のタイルに分け、奥行きを 24 層に分けて、クラスター（小さな箱）ごとに
// 「影響するライトの番号」を先に集める。シェーディングでは自分のクラスターのライトだけを回す。

struct Light {
  float3 position_view;   // ビュー空間の位置 [m]（カメラが原点、+z が前）
  float radius;           // 影響半径 [m]
  float3 color;           // 色 × 強さ（線形）
  float pad;
};
StructuredBuffer<Light> g_lights : register(t0);

// クラスターごとの、ライトの数と番号。1 クラスターに最大 kMaxPerCluster 個。
static const uint kMaxPerCluster = 64;
RWStructuredBuffer<uint> g_cluster_indices : register(u0);   // [cluster * kMaxPerCluster + k]
RWStructuredBuffer<uint> g_cluster_counts : register(u1);    // [cluster]

cbuffer ClusterCB : register(b0) {
  uint3 g_grid;           // タイル数 x, y と奥行きの層数 z（例: 16, 9, 24）
  uint g_light_count;     // ライトの数（例: 200）
  float2 g_tan_half_fov;  // (tan(水平画角/2), tan(垂直画角/2))
  float g_near;           // ニア [m]
  float g_far;            // ファー [m]
};

// 奥行きの層の境界。指数的に刻む。近くは細かく、遠くは粗く（遠近法で画素に映る大きさが変わるため）。
//   z(k) = near * (far / near)^(k / 層数)
float SliceDepth(uint k) {
  return g_near * pow(max(g_far / g_near, 1.0), (float)k / g_grid.z);   // far > near なので max は保険
}

// 球と箱（AABB）が重なるか。箱の最も近い点までの距離の 2 乗が、半径の 2 乗以下なら重なる。
bool SphereIntersectsAabb(float3 center, float radius, float3 box_min, float3 box_max) {
  float3 closest = clamp(center, box_min, box_max);   // 箱の中で球の中心にいちばん近い点
  float3 d = center - closest;
  return dot(d, d) <= radius * radius;
}
```

奥行きの層は指数で刻みます。近くを細かく遠くを粗くするのは、遠近法で遠いほど 1 画素に映る範囲が広くなるからです。

```hlsl
[numthreads(4, 4, 4)]      // 1 グループ = 4 x 4 x 4 クラスター
void main(uint3 id : SV_DispatchThreadID) {
  if (any(id >= g_grid)) return;                               // 端数

  // このクラスターの奥行きの範囲 [z0, z1]。
  float z0 = SliceDepth(id.z);
  float z1 = SliceDepth(id.z + 1);

  // タイルの NDC の範囲 [-1, 1]。y は上が +1。
  float2 ndc_min = float2(id.xy) / float2(g_grid.xy) * 2.0 - 1.0;
  float2 ndc_max = float2(id.xy + 1) / float2(g_grid.xy) * 2.0 - 1.0;

  // ビュー空間の箱を作る。タイルの横幅と縦幅は奥ほど広い。手前の面と奥の面の両方の四隅を使い、
  // 全部を含む最小の箱（AABB）にする。
  float3 corners[4];
  corners[0] = float3(ndc_min.x * g_tan_half_fov.x, ndc_min.y * g_tan_half_fov.y, 1.0);
  corners[1] = float3(ndc_max.x * g_tan_half_fov.x, ndc_min.y * g_tan_half_fov.y, 1.0);
  corners[2] = float3(ndc_min.x * g_tan_half_fov.x, ndc_max.y * g_tan_half_fov.y, 1.0);
  corners[3] = float3(ndc_max.x * g_tan_half_fov.x, ndc_max.y * g_tan_half_fov.y, 1.0);
  float3 box_min = float3(1e9, 1e9, z0);
  float3 box_max = float3(-1e9, -1e9, z1);
  [unroll] for (int c = 0; c < 4; ++c) {
    float3 near_pt = corners[c] * z0;       // 手前の面の四隅（方向 × 奥行き。corners の z は 1）
    float3 far_pt = corners[c] * z1;        // 奥の面の四隅
    box_min.xy = min(box_min.xy, min(near_pt.xy, far_pt.xy));
    box_max.xy = max(box_max.xy, max(near_pt.xy, far_pt.xy));
  }

  // クラスターの通し番号（x が最も速く動く）。
  uint cluster = id.x + g_grid.x * (id.y + g_grid.y * id.z);

  // 全ライトを調べる。ここは 1 クラスターにつき 200 回。クラスター数は 16 x 9 x 24 = 3,456 個。
  uint count = 0;
  for (uint i = 0; i < g_light_count; ++i) {
    Light light = g_lights[i];
    if (SphereIntersectsAabb(light.position_view, light.radius, box_min, box_max)) {
      if (count < kMaxPerCluster) {                            // 溢れたぶんは捨てる（そのクラスターのライトが欠ける）
        g_cluster_indices[cluster * kMaxPerCluster + count] = i;
      }
      ++count;
    }
  }
  g_cluster_counts[cluster] = min(count, kMaxPerCluster);
}
```

クラスターごとにビュー空間の箱を作りライトの球と重なるかを調べます。箱は手前の面と奥の面の四隅から作る最小の箱です。球と箱の判定は箱の中で球の中心に最も近い点までの距離の 2 乗が、半径の 2 乗以下かどうかです。

ライトの数が上限（64）を超えると、そのクラスターのライトが欠けます。画面でライトが突然消えるので、上限は多めに取ります。

<svg class="fig flow" viewBox="0 0 680 162" role="img" aria-label="クラスターの分け方"><defs><marker id="cs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">クラスター: 画面のタイル x 奥行きの層(指数刻み)</text><rect x="20" y="40" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="20" y="70" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="20" y="100" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="60" y="40" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="60" y="70" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="60" y="100" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="100" y="40" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="100" y="70" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="100" y="100" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="140" y="40" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="140" y="70" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="140" y="100" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="180" y="40" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="180" y="70" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="180" y="100" width="40" height="30" fill="none" stroke="#94a3b8"/><rect x="100" y="70" width="40" height="30" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="120" y="126" text-anchor="middle" font-size="10" fill="currentColor">タイル</text><line x1="280.0" y1="50" x2="280.0" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="295.8" y1="50" x2="295.8" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="311.7" y1="50" x2="311.7" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="327.5" y1="50" x2="327.5" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="343.3" y1="50" x2="343.3" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="359.2" y1="50" x2="359.2" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="375.0" y1="50" x2="375.0" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="390.8" y1="50" x2="390.8" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="406.7" y1="50" x2="406.7" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="422.5" y1="50" x2="422.5" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="438.3" y1="50" x2="438.3" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="454.2" y1="50" x2="454.2" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="470.0" y1="50" x2="470.0" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="485.8" y1="50" x2="485.8" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="501.7" y1="50" x2="501.7" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="517.5" y1="50" x2="517.5" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="533.3" y1="50" x2="533.3" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="549.2" y1="50" x2="549.2" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="565.0" y1="50" x2="565.0" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="580.8" y1="50" x2="580.8" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="596.7" y1="50" x2="596.7" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="612.5" y1="50" x2="612.5" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="628.3" y1="50" x2="628.3" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="644.2" y1="50" x2="644.2" y2="90" stroke="#94a3b8" stroke-width="0.8"/><line x1="660.0" y1="50" x2="660.0" y2="90" stroke="#94a3b8" stroke-width="0.8"/><text x="280" y="108" text-anchor="middle" font-size="10" fill="currentColor">0.1 m</text><text x="660" y="108" text-anchor="middle" font-size="10" fill="currentColor">100 m</text><text x="470.0" y="126" text-anchor="middle" font-size="10" fill="currentColor">奥行き 24 層(近くが細かい)</text><text x="10" y="150" text-anchor="start" font-size="10" fill="currentColor">黄: 画素が属する 1 クラスター。ライトの球が箱と重なる分だけ、画素が回す</text></svg>

次がシェーディング側です。画素は自分のクラスターを探し、そのライトだけを回します。

```hlsl
// 事例 2 の続き: シェーディング側。画素が自分のクラスターを探して、そのライトだけを回す。
struct Light {
  float3 position_view;   // ビュー空間の位置 [m]
  float radius;           // 影響半径 [m]
  float3 color;           // 色 × 強さ
  float pad;
};
StructuredBuffer<Light> g_lights : register(t0);
StructuredBuffer<uint> g_cluster_indices : register(t1);    // [cluster * 64 + k]
StructuredBuffer<uint> g_cluster_counts : register(t2);     // [cluster]
Texture2D<float4> g_gbuffer_normal : register(t3);          // xyz = ビュー空間の法線
Texture2D<float4> g_gbuffer_albedo : register(t4);
Texture2D<float> g_depth : register(t5);

cbuffer ShadeCB : register(b0) {
  uint3 g_grid;            // 16, 9, 24
  uint g_pad0;
  float2 g_screen_size;    // (1920, 1080)
  float2 g_tan_half_fov;
  float g_near;
  float g_far;
  float2 g_pad1;
};

static const uint kMaxPerCluster = 64;

float LinearDepth(float z) {
  return g_near * g_far / (g_far - z * (g_far - g_near));   // 0〜1 の深度を、距離 [m] に直す
}

float4 main(float4 pos : SV_Position) : SV_Target {
  int2 p = int2(pos.xy);
  float depth = g_depth.Load(int3(p, 0));
  float view_z = LinearDepth(depth);                          // この画素の面のカメラからの距離 [m]

  // 画素の位置から、ビュー空間の位置を作る。
  float2 ndc = float2(pos.x / g_screen_size.x, 1.0 - pos.y / g_screen_size.y) * 2.0 - 1.0;   // y は上が +
  float3 position = float3(ndc * g_tan_half_fov * view_z, view_z);

  // 自分のクラスターを探す。タイルは画面を等分、奥行きの層は指数の刻みを逆にたどる。
  uint2 tile = uint2(pos.xy / g_screen_size * float2(g_grid.xy));
  uint slice = (uint)(log(view_z / g_near) / log(g_far / g_near) * g_grid.z);
  slice = min(slice, g_grid.z - 1);                           // ファー面ちょうどで溢れないように
  uint cluster = tile.x + g_grid.x * (tile.y + g_grid.y * slice);

  float3 n = normalize(g_gbuffer_normal.Load(int3(p, 0)).xyz);
  float3 albedo = g_gbuffer_albedo.Load(int3(p, 0)).rgb;

  // 自分のクラスターのライトだけを回す（全ライトを回さない）。
  float3 lighting = 0;
  uint count = g_cluster_counts[cluster];
  for (uint k = 0; k < count; ++k) {
    Light light = g_lights[g_cluster_indices[cluster * kMaxPerCluster + k]];
    float3 to_light = light.position_view - position;
    float dist = length(to_light);
    float falloff = saturate(1.0 - dist / light.radius);      // 半径で 0 になる単純な減衰（一例）
    falloff *= falloff;                                       // 2 乗にして、縁をなめらかにする
    float n_dot_l = saturate(dot(n, to_light / max(dist, 1e-4)));
    lighting += light.color * (falloff * n_dot_l);
  }
  return float4(albedo * lighting / 3.14159265, 1.0);          // ランバート拡散（ρ/π）
}
```

画素から奥行きの層を求めるには指数の刻みを逆にたどります。`log(view_z / near) / log(far / near) × 層数` を切り捨てます。ファー面ちょうどで層の数を超えないよう `min` で抑えています。

### 結果と次の一手 {#lights-result}

ライティングのパスが 40 ms から 6 ms 程度になるという見積もりです（例。評価回数が約 8 分の 1 になるという C++ の数字と同じ桁です）。次の壁は G バッファの帯域です（[帯域幅](bandwidth.md)）。

## 事例 3：魔法のエフェクトで 60 FPS が 35 FPS に {#case-smoke}

### 症状と切り分け {#smoke-triage}

魔法の煙を出すとフレームが 9 ms から 28 ms になりました（例）。解像度を下げると大きく速くなるので、GPU のピクセル処理か帯域です。オーバードローの可視化で煙の部分が真っ赤（10 重ね以上）でした。1 枚が画面の 3 分の 2 を覆っています。

### 数で見る {#smoke-numbers}

画面の 2/3 を覆う板をフル解像度で 10 枚重ねると、1080p でブレンドされる画素数は 207 万 × 2/3 × 10 ＝ 1,380 万です。RGBA16F のブレンドは読み 8 バイトと書き 8 バイトで 16 バイトなので、1 フレームのメモリ転送は 211 MiB です。60 fps なら 12.4 GiB/s になります。

半分の解像度（画素数は 4 分の 1）で、板を 5 枚に減らすとブレンドする画素は 173 万で、8 分の 1 です。転送は 26.4 MiB（60 fps で 1.54 GiB/s）に減ります。解像度と枚数の両方を減らしたので、効果が積になります。

なお、以前のこのページは「20 M ピクセル以上」と書いていましたが、計算すると 13.8 M でした。この版で直しています。

### 直し方：縮小バッファに描いて、深度に合わせて拡大する {#smoke-fix}

半分の解像度の煙をそのまま拡大すると、手前の物の輪郭で煙がにじみます。輪郭の画素が低解像度では煙のある側と平均されるためです。対策は 2 つです。縮小時の深度に最大値（最も奥）を使うことと拡大時に深度が合う画素だけを混ぜることです。

```hlsl

// ---- 縮小用: フル解像度の深度から、半分の解像度の深度を作る ----
// 2 x 2 の 4 画素のうち、最も奥（最大）の深度を選ぶ。煙の深度テストを「遠い方」に合わせると、
// 手前の物の輪郭の内側に煙がはみ出さない（逆に最小を選ぶと、輪郭の外で煙が消える）。
float DownsampleDepth(float4 pos : SV_Position) : SV_Target {
  int2 p = int2(pos.xy) * 2;                                  // 低解像度の画素 → フル解像度の左上
  float d0 = g_depth_full.Load(int3(p + int2(0, 0), 0));
  float d1 = g_depth_full.Load(int3(p + int2(1, 0), 0));
  float d2 = g_depth_full.Load(int3(p + int2(0, 1), 0));
  float d3 = g_depth_full.Load(int3(p + int2(1, 1), 0));
  return max(max(d0, d1), max(d2, d3));                       // 値が大きいほど奥（標準の深度）
}
```

2×2 のうち最も奥の深度を選ぶと手前の物の輪郭の内側に煙がはみ出しません。最小を選ぶと逆に輪郭の外で煙が消えます。

```hlsl
// 事例 3: 煙を半分の解像度に描いて、フル解像度に合成する。
// 縮小した深度で、煙を描くときの深度テストをする。合成は「深度に合った」拡大で縁のにじみを防ぐ。

Texture2D<float4> g_smoke_low : register(t0);       // 半分の解像度の煙（プリマルチプライド アルファ）
Texture2D<float> g_depth_full : register(t1);       // フル解像度の深度
Texture2D<float> g_depth_low : register(t2);        // 半分の解像度の深度（縮小時に、4 画素の最大 = 最も奥を選んだもの）
SamplerState g_point_clamp : register(s0);

cbuffer CompositeCB : register(b0) {
  float2 g_full_size;     // フル解像度の画面サイズ [px]
  float2 g_inv_low_size;  // 1 / 半分の解像度のサイズ
  float g_depth_threshold; // 深度が「同じ面」とみなせる差（線形化後 [m]）。一例: 0.5
  float g_near;
  float g_far;
  float g_pad;
};

float LinearDepth(float z) {
  return g_near * g_far / (g_far - z * (g_far - g_near));   // 0〜1 の深度を、カメラからの距離 [m] へ
}

// 出力はプリマルチプライドの煙。ブレンド ステートは（ソース = ONE、デスト = INV_SRC_ALPHA）。
float4 main(float4 pos : SV_Position) : SV_Target {
  int2 full_pixel = int2(pos.xy);                           // フル解像度の画素
  float2 low_uv = pos.xy / g_full_size;                     // 同じ位置の、低解像度の UV
  int2 low_base = int2(low_uv / g_inv_low_size - 0.5);      // バイリニアの左上の画素

  float full_depth = LinearDepth(g_depth_full.Load(int3(full_pixel, 0)));

  // 低解像度の 2 x 2 の 4 画素のうち、この画素と同じ面（深度が近い）にあるものだけを混ぜる。
  // 全部が違う面なら、いちばん深度が近い 1 画素を使う（にじまずに縁が割れる方を選ぶ）。
  float4 sum = 0;
  float weight_sum = 0;
  float best_diff = 1e9;
  float4 best_color = 0;
  [unroll] for (int j = 0; j < 2; ++j) {
    [unroll] for (int i = 0; i < 2; ++i) {
      int2 p = low_base + int2(i, j);
      float4 color = g_smoke_low.Load(int3(p, 0));
      float low_depth = LinearDepth(g_depth_low.Load(int3(p, 0)));
      float diff = abs(low_depth - full_depth);              // この画素の面と、低解像度の画素の面の距離 [m]

      // バイリニアの重み（画素の中心との距離で決まる、通常の拡大の重み）。
      float2 frac_pos = low_uv / g_inv_low_size - 0.5 - low_base;
      float wx = (i == 0) ? 1.0 - frac_pos.x : frac_pos.x;
      float wy = (j == 0) ? 1.0 - frac_pos.y : frac_pos.y;
      float w = wx * wy;

      if (diff < g_depth_threshold) {                        // 同じ面なら使う
        sum += color * w;
        weight_sum += w;
      }
      if (diff < best_diff) { best_diff = diff; best_color = color; }   // 保険: いちばん近い画素
    }
  }
  // 1 つも同じ面がなければ、いちばん近い 1 画素。重みがあれば正規化して返す。
  return (weight_sum > 1e-4) ? sum / weight_sum : best_color;
}
```

低解像度の 4 画素のうちフル解像度の画素と深度の差が小さいものだけをバイリニアの重みで混ぜます。4 つとも別の面ならいちばん近い 1 画素を使います。深度のしきい値は線形化した距離で決めます。0.5 m は一例です。

### 結果と次の一手 {#smoke-result}

煙のコストが約 8 分の 1 になりフレームは 11 ms 程度になるという見積もりです（例）。次に、見た目の差を確認します。縁にまだにじみが残るならしきい値を小さくするか縁だけをフル解像度で描く方法を考えます（[パーティクル](../translucency/particles-cost.md)）。

<svg class="fig flow" viewBox="0 0 700 216" role="img" aria-label="3 事例の前と後"><defs><marker id="cs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">3 事例の前と後(C++ で数えた値、対数軸)</text><text x="182" y="58" text-anchor="end" font-size="11" fill="currentColor">ドロー コール</text><rect x="190" y="34" width="164.8" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="360.7971327841043" y="47" text-anchor="start" font-size="10" fill="currentColor">8,000 回</text><rect x="190" y="56" width="45.6" height="18" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="241.5654303886775" y="69" text-anchor="start" font-size="10" fill="currentColor">12 回</text><text x="182" y="112" text-anchor="end" font-size="11" fill="currentColor">ライト評価(1080p)</text><rect x="190" y="88" width="363.9" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="559.8598814931474" y="101" text-anchor="start" font-size="10" fill="currentColor">414,700,000 回</text><rect x="190" y="110" width="324.8" height="18" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="520.846248954554" y="123" text-anchor="start" font-size="10" fill="currentColor">49,400,000 回</text><text x="182" y="166" text-anchor="end" font-size="11" fill="currentColor">ブレンドする画素</text><rect x="190" y="142" width="301.5" height="18" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="497.46156142583" y="155" text-anchor="start" font-size="10" fill="currentColor">13,800,000 画素</text><rect x="190" y="164" width="263.4" height="18" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="459.3841687987713" y="177" text-anchor="start" font-size="10" fill="currentColor">1,730,000 画素</text><text x="190" y="206" text-anchor="start" font-size="10" fill="currentColor">青: 前、黄: 後。軸は 1 〜 10^9</text></svg>

## 数字を出した C++ {#cpp}

事例 1〜3 の数字を出した C++ です。視錐台の判定、ライトのクラスター分けブレンドの転送量を数えます。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。乱数の種を固定しているので同じ数字が出ます。

```cpp
// 最適化の 3 つの事例の数字を、実際に数えて出す。
//  事例 1: 8,000 本のインスタンスを視錐台で選ぶと何本残るか、ドロー コールとバッファの量
//  事例 2: ライト 200 個を、クラスターに分けると 1 クラスターに何個残るか
//  事例 3: 半透明の重ね書きのピクセル数とメモリ転送
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>

namespace {
constexpr double kPi = 3.14159265358979323846;
constexpr double kMiB = 1024.0 * 1024.0;

struct V3 { double x, y, z; };

// ---- 事例 1 ----
// カメラは原点で +z を向く。ビュー空間の位置が (x, y, z) の球が、視錐台の中にあるか。
// 平面は 左・右・下・上・近・遠 の 6 枚。
bool InFrustum(V3 c, double r, double tan_h, double tan_v, double near_z, double far_z) {
  if (c.z + r < near_z || c.z - r > far_z) return false;     // 近い・遠い平面
  // 左右の平面: 法線 (1, 0, tan_h) / |.|。x = ±z * tan_h の面の外にあるか。
  const double nh = std::sqrt(1.0 + tan_h * tan_h);
  if (c.x * 1.0 + c.z * tan_h < -r * nh) return false;       // 左の平面の外側
  if (-c.x * 1.0 + c.z * tan_h < -r * nh) return false;      // 右の平面の外側
  const double nv = std::sqrt(1.0 + tan_v * tan_v);
  if (c.y * 1.0 + c.z * tan_v < -r * nv) return false;       // 下の平面の外側
  if (-c.y * 1.0 + c.z * tan_v < -r * nv) return false;      // 上の平面の外側
  return true;
}

// ---- 事例 2 ----
struct Light { V3 p; double r; };

// 球と箱の重なり。
bool SphereAabb(V3 c, double r, V3 lo, V3 hi) {
  const V3 q = {std::clamp(c.x, lo.x, hi.x), std::clamp(c.y, lo.y, hi.y), std::clamp(c.z, lo.z, hi.z)};
  const double dx = c.x - q.x, dy = c.y - q.y, dz = c.z - q.z;
  return dx * dx + dy * dy + dz * dz <= r * r;
}
}  // namespace

int main() {
  std::mt19937_64 rng(2026);
  std::uniform_real_distribution<double> u(0.0, 1.0);

  // ===== 事例 1 =====
  std::printf("== 事例 1: 森（木 3,000 + 草 4,000 + 岩 1,000）==\n");
  const int counts_by_type[3] = {3000, 4000, 1000};
  const double kFovY = 60.0 * kPi / 180.0, kAspect = 16.0 / 9.0;
  const double tan_v = std::tan(kFovY * 0.5), tan_h = tan_v * kAspect;
  int visible = 0, total = 0;
  for (int type = 0; type < 3; ++type) {
    for (int i = 0; i < counts_by_type[type]; ++i, ++total) {
      // 森は 400 m x 400 m に一様に散らばり、カメラは中心にいて +z を向く（z 方向の前後に広がる）。
      const V3 c = {(u(rng) - 0.5) * 400.0, 1.0 + 3.0 * u(rng), (u(rng) - 0.5) * 400.0};
      const double radius = (type == 0) ? 4.0 : (type == 1) ? 0.5 : 1.5;   // 境界球の半径 [m]
      if (InFrustum(c, radius, tan_h, tan_v, 0.1, 150.0)) ++visible;
    }
  }
  std::printf("全 %d 本のうち、視錐台（ファー 150 m）に入る数: %d (%.1f %%)\n", total, visible,
              100.0 * visible / total);
  std::printf("ドロー コール: 1 本ずつ %d 回 → 種類ごとの間接描画 12 回\n", total);
  // 1 回のドローごとに定数バッファを書くと、256 バイト境界（D3D12 の定数バッファの最小単位）に置かれる。
  std::printf("定数バッファ（1 本ずつ）: %.2f MiB / フレーム、インスタンス バッファ（64 B / 本）: %.2f MiB\n",
              total * 256.0 / kMiB, total * 64.0 / kMiB);

  // ===== 事例 2 =====
  std::printf("\n== 事例 2: ライト 200 個（半径 8 m）、1080p ==\n");
  const int kLights = 200;
  const int gx = 16, gy = 9, gz = 24;
  const double near_z = 0.1, far_z = 100.0;
  std::vector<Light> lights;
  for (int i = 0; i < kLights; ++i) {
    // ビュー空間の視錐台の中（z 1〜60 m）にランダムに置く。
    const double z = 1.0 + 59.0 * u(rng);
    lights.push_back({{(u(rng) * 2 - 1) * tan_h * z, (u(rng) * 2 - 1) * tan_v * z, z}, 8.0});
  }
  const double pixels = 1920.0 * 1080.0;
  std::printf("1 画素が全ライトを回す: %.1f M 回 / フレーム（200 x %.2f M 画素）\n",
              kLights * pixels / 1e6, pixels / 1e6);

  // 各クラスターに入るライトの数を数える。
  std::array<int, 64> histogram{};
  long long sum_per_cluster = 0;
  int max_per_cluster = 0;
  const int clusters = gx * gy * gz;
  for (int z = 0; z < gz; ++z) {
    const double z0 = near_z * std::pow(far_z / near_z, double(z) / gz);
    const double z1 = near_z * std::pow(far_z / near_z, double(z + 1) / gz);
    for (int y = 0; y < gy; ++y) {
      for (int x = 0; x < gx; ++x) {
        const double nx0 = double(x) / gx * 2 - 1, nx1 = double(x + 1) / gx * 2 - 1;
        const double ny0 = double(y) / gy * 2 - 1, ny1 = double(y + 1) / gy * 2 - 1;
        // 手前と奥の四隅から作る最小の箱（シェーダーと同じ作り方）。
        V3 lo = {1e9, 1e9, z0}, hi = {-1e9, -1e9, z1};
        for (double zz : {z0, z1}) {
          for (double nx : {nx0, nx1}) {
            for (double ny : {ny0, ny1}) {
              lo.x = std::min(lo.x, nx * tan_h * zz); hi.x = std::max(hi.x, nx * tan_h * zz);
              lo.y = std::min(lo.y, ny * tan_v * zz); hi.y = std::max(hi.y, ny * tan_v * zz);
            }
          }
        }
        int n = 0;
        for (const Light& l : lights) n += SphereAabb(l.p, l.r, lo, hi);
        sum_per_cluster += n;
        max_per_cluster = std::max(max_per_cluster, n);
        ++histogram[std::min(n, 63)];
      }
    }
  }
  std::printf("クラスター数 %d、1 クラスターあたりのライト数: 平均 %.2f、最大 %d\n", clusters,
              double(sum_per_cluster) / clusters, max_per_cluster);
  std::printf("画素が回す回数の目安（全クラスターの平均）: %.1f M 回 / フレーム（%.0f 倍少ない）\n",
              double(sum_per_cluster) / clusters * pixels / 1e6,
              double(kLights) / (double(sum_per_cluster) / clusters));
  std::printf("クラスターの割り当て（CS）の比較回数: %d x %d = %d 回\n", clusters, kLights, clusters * kLights);

  // ===== 事例 3 =====
  std::printf("\n== 事例 3: 煙（画面の 2/3 を覆う板を重ねる）、1080p、RGBA16F のブレンド ==\n");
  const double coverage = 2.0 / 3.0;
  auto blended = [&](double scale, int layers) { return coverage * pixels * scale * scale * layers; };
  const double before = blended(1.0, 10), after = blended(0.5, 5);
  std::printf("フル解像度 10 枚: %.1f M 画素をブレンド\n", before / 1e6);
  std::printf("半分の解像度 5 枚: %.2f M 画素をブレンド（%.1f 分の 1）\n", after / 1e6, before / after);
  // ブレンドは読み 8 B + 書き 8 B = 16 B / 画素。
  std::printf("ブレンドのメモリ転送: %.0f MiB → %.1f MiB / フレーム、60 fps で %.1f → %.2f GiB/s\n",
              before * 16 / kMiB, after * 16 / kMiB, before * 16 * 60 / (kMiB * 1024),
              after * 16 * 60 / (kMiB * 1024));
  return 0;
}
```

```text title="実行結果（事例 1）"
== 事例 1: 森（木 3,000 + 草 4,000 + 岩 1,000）==
全 8000 本のうち、視錐台（ファー 150 m）に入る数: 1241 (15.5 %)
ドロー コール: 1 本ずつ 8000 回 → 種類ごとの間接描画 12 回
定数バッファ（1 本ずつ）: 1.95 MiB / フレーム、インスタンス バッファ（64 B / 本）: 0.49 MiB
```

```text title="実行結果（事例 2）"
== 事例 2: ライト 200 個（半径 8 m）、1080p ==
1 画素が全ライトを回す: 414.7 M 回 / フレーム（200 x 2.07 M 画素）
クラスター数 3456、1 クラスターあたりのライト数: 平均 23.80、最大 48
画素が回す回数の目安（全クラスターの平均）: 49.4 M 回 / フレーム（8 倍少ない）
クラスターの割り当て（CS）の比較回数: 3456 x 200 = 691200 回
```

```text title="実行結果（事例 3）"
== 事例 3: 煙（画面の 2/3 を覆う板を重ねる）、1080p、RGBA16F のブレンド ==
フル解像度 10 枚: 13.8 M 画素をブレンド
半分の解像度 5 枚: 1.73 M 画素をブレンド（8.0 分の 1）
ブレンドのメモリ転送: 211 MiB → 26.4 MiB / フレーム、60 fps で 12.4 → 1.54 GiB/s
```

## 共通する流れ {#flow}

3 つの事例に共通するのは切り分け計測、原因、直す測り直すの順です。勘で直さず数字で確かめます。

1. 切り分け: 解像度を変えて、CPU と GPU のどちらかを決める。
2. 計測: プロファイラーで、重い所を特定する。
3. 原因: その所がなぜ重いのかを言葉にする（全部のライトを回している、など）。
4. 直す: 原因に対応する手法を 1 つだけ入れる。
5. 測り直す: 見積もりでなく、実際のフレーム時間で効果を確かめる。見た目も確認する。

## 全体のよくあるミス

??? failure "ボトルネックを調べずにシェーダーを直す"
    CPU 側が遅いのにシェーダーを最適化しても、速くなりません。まず、CPU と GPU のどちらが遅いかを解像度の変更やプロファイラーで確かめます。

??? failure "全オブジェクトを毎フレーム 1 つずつ CPU でカリングする"
    オブジェクトが数万になると、判定自体で CPU が重くなります。空間分割で階層的に判定するか事例 1 のように GPU で行います。

??? failure "GPU カリングで、見える物がちらつく"
    引数バッファのカウンターを毎フレーム 0 に戻していない、または種類ごとの上限が小さすぎる。上限を超えたぶんは捨てられるので、遠くの物が消える。

??? failure "クラスターのライトが、画面で急に消える"
    1 クラスターのライト数が上限（64）を超えている。上限を増やすかライトの半径を小さくする。

??? failure "縮小した煙が、手前の物の輪郭でにじむ"
    縮小した深度に最小を使っている。最大（最も奥）にして拡大時に深度が合う画素だけを混ぜる。

??? failure "最適化のつもりで、見た目が壊れる"
    カリングを強くしすぎて、画面の端で物が消える LOD の切り替えが目立つなどです。見た目も必ず確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 解像度を下げて速くなるなら GPU のピクセル、ならないなら CPU か頂点。
    - [x] ドロー コールは、種類ごとにまとめて見えない物を先に捨てる。
    - [x] ライトはクラスターに先に集めて、画素は自分のクラスターだけを回す。
    - [x] 半透明は縮小と枚数削減の積で効く。縁は深度で守る。
    - [x] 効果は測り直して確かめる。

## 関連ページ

- [Optimization](index.md)
- [何が重いのか](bottlenecks.md)
- [Profiling Tools](tools.md)
- [Draw Calls](../draw-call/draw-calls.md)
- [Tiled and Clustered](../lighting/light-culling.md)
- [Low-Resolution Effects](low-res-effects.md)
