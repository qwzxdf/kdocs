---
title: GPU Driven (D3D12)
tags:
  - 描画最適化
---

# GPU Driven (D3D12)

[GPU Driven Rendering](../gpu-driven.md)のページでは、<strong>「カリングと描画引数の生成を GPU に任せる」</strong>という考え方を説明しました。このパートではそれを Direct3D 12 の実コードで組み立てます。バッファの作り方・ルート シグネチャ・コンピュート シェーダーによるカリング・`ExecuteIndirect`・Hi-Z オクルージョン・メッシュレット・バリアまでコピーして動かせる粒度で、なぜそう書くのかとともに解説します。

## このパートの前提

- API は Direct3D 12（Windows 10 以降）です。HLSL は dxc（DirectX Shader Compiler）でコンパイルします。
- ヘルパーは `Microsoft::WRL::ComPtr` とこのサイトの [dx12_util.h](../../../directx/dx12/util.md)（`MakeHeapProperties`、`MakeBufferDesc`、`MakeTransitionBarrier`、`OffsetHandle` など）です。`d3dx12.h` と `CD3DX12_*` は使いません。構造体は素の `D3D12_*` を埋めます。
- シェーダー モデルは基本 6.0 以上です。バインドレス（`ResourceDescriptorHeap`）は 6.6、メッシュ シェーダーは 6.5 が必要です。
- 座標系はこのサイトの標準で、左手系・Y 上・+Z 前方・行ベクトルです。
- コーディング規約は Google C++ Style です。メンバー変数は末尾に `_` を付け関数は大文字始まりにします。

!!! note "D3D11 の章との関係"
    このサイトの描画の解説は主に D3D11 を前提にしています。GPU Driven は D3D12 の機能（`ExecuteIndirect`・明示的バリア・バインドレス）が本領を発揮するのでこのパートだけ D3D12 で書きます。

## 全体の流れ

<svg class="fig illust" viewBox="0 0 780 330" role="img" aria-label="GPU Driven のフレーム構成">
<text x="20" y="24" class="fig-title">1 フレームの流れ（CPU が積むのは数回の呼び出し）</text>
<rect x="30" y="50" width="170" height="44" rx="6" fill="rgba(76,139,245,0.18)" stroke="currentColor" stroke-width="2"/><text x="42" y="77" style="font-size:13px">① インスタンス更新</text>
<rect x="30" y="120" width="170" height="44" rx="6" fill="rgba(76,139,245,0.18)" stroke="currentColor" stroke-width="2"/><text x="42" y="147" style="font-size:13px">② カウンタをリセット</text>
<rect x="30" y="190" width="170" height="44" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="42" y="217" style="font-size:13px">③ カリング（CS）</text>
<rect x="30" y="260" width="170" height="44" rx="6" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="42" y="287" style="font-size:13px">④ UAV → 引数 バリア</text>
<rect x="300" y="50" width="200" height="44" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="312" y="77" style="font-size:13px">⑤ ExecuteIndirect（深度）</text>
<rect x="300" y="120" width="200" height="44" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="312" y="147" style="font-size:13px">⑥ Hi-Z 構築（CS）</text>
<rect x="300" y="190" width="200" height="44" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="312" y="217" style="font-size:13px">⑦ 2 パス目のカリング（CS）</text>
<rect x="300" y="260" width="200" height="44" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="312" y="287" style="font-size:13px">⑧ ExecuteIndirect（本描画）</text>
<g stroke="currentColor" stroke-width="2" fill="none"><line x1="115" y1="94" x2="115" y2="120"/><line x1="115" y1="164" x2="115" y2="190"/><line x1="115" y1="234" x2="115" y2="260"/><line x1="200" y1="282" x2="300" y2="72"/><line x1="400" y1="94" x2="400" y2="120"/><line x1="400" y1="164" x2="400" y2="190"/><line x1="400" y1="234" x2="400" y2="260"/></g>
<text x="540" y="76" style="font-size:12px">CPU：コマンドを積むだけ</text><text x="540" y="96" style="font-size:12px">GPU：何を描くかを自分で決める</text>
<text x="520" y="150" style="font-size:12px">① 〜 ④：1 パス目（前フレーム可視）</text>
<text x="520" y="220" style="font-size:12px">⑥ 〜 ⑧：2 パス目（新しい Hi-Z）</text>
</svg>

| 手順 | 担当 | 内容 | 解説ページ |
| --- | --- | --- | --- |
| **① インスタンス更新** | CPU → GPU | 動いた物の行列だけをアップロード | [シーン データ](scene-data.md) |
| ② カウンタのリセット | GPU | 出力の個数を 0 に | [カリング](culling.md) |
| ③ カリング | GPU（CS） | 見える物だけ描画コマンドを書く | [カリング](culling.md) |
| ④ バリア | GPU | UAV → INDIRECT_ARGUMENT | [カリング](culling.md) |
| ⑤ 描画（深度） | GPU | `ExecuteIndirect` | [ExecuteIndirect](execute-indirect.md) |
| ⑥ Hi-Z 構築 | GPU（CS） | 深度から、最大深度のミップ チェーン | [Hi-Z と 2 パス](hiz-two-pass.md) |
| ⑦ 2 パス目のカリング | GPU（CS） | 新しい Hi-Z で、1 パス目で漏れた物を判定 | [Hi-Z と 2 パス](hiz-two-pass.md) |
| ⑧ 本描画 | GPU | `ExecuteIndirect` | [ExecuteIndirect](execute-indirect.md) |

## このパートで使うデータ構造

**C++ と HLSL で、同じ形の構造体**を使います。サイズと整列は `static_assert`で固定します（ずれると描画が壊れデバッグしづらい）。

```cpp
struct alignas(16) InstanceData {          // 配置された物体 1 個(GPU に常駐する)
  DirectX::XMFLOAT4X4 world;               // モデル → ワールドの行列。64 バイト
  uint32_t mesh_index;                     // どのメッシュか(MeshInfo の配列の添字)
  uint32_t material_index;                 // どのマテリアルか(バインドレスで引く)
  uint32_t flags;                          // 予備のビット(影を落とすか、など)
  uint32_t reserved;                       // 16 バイト境界にそろえる詰め物
};
static_assert(sizeof(InstanceData) == 80); // 64 + 16。HLSL の構造体と大きさが違うと、2 つ目以降が壊れる

struct MeshInfo {                          // メッシュの種類 1 つ
  DirectX::XMFLOAT3 bounds_center;         // 境界球の中心(メッシュ空間)
  float bounds_radius;                     // 境界球の半径
  uint32_t index_count;                    // 描くインデックス数
  uint32_t start_index;                    // 巨大なインデックス バッファの中の先頭
  int32_t base_vertex;                     // 巨大な頂点バッファの中の先頭(インデックスに足される)
  uint32_t pso_bucket;                     // どの PSO のグループか
};
static_assert(sizeof(MeshInfo) == 32);

struct IndirectCommand {                   // ExecuteIndirect が読む、1 回ぶんの描画
  uint32_t instance_index;                 // ルート定数に書かれるインスタンス番号(4 バイト)
  D3D12_DRAW_INDEXED_ARGUMENTS draw;       // DrawIndexedInstanced の引数 5 つ(20 バイト)
};
static_assert(sizeof(IndirectCommand) == 24);   // コマンド シグネチャの ByteStride と一致させる
```

```hlsl
struct Instance {                          // C++ の InstanceData と同じ並び
  float4x4 world;                          // モデル → ワールド
  uint mesh_index;                         // メッシュの番号
  uint material_index;                     // マテリアルの番号
  uint flags;                              // 予備
  uint reserved;                           // 詰め物
};

struct MeshInfo {                          // C++ の MeshInfo と同じ並び
  float3 bounds_center;                    // 境界球の中心
  float bounds_radius;                     // 半径
  uint index_count;
  uint start_index;
  int base_vertex;                         // 符号付き(負の値もありうる)
  uint pso_bucket;
};

struct IndirectCommand {                   // 6 ワード = 24 バイト。ExecuteIndirect の 1 コマンドと同じ並び
  uint instance_index;                     // ルート定数になる
  uint index_count;                        // 以下の 5 つが DrawIndexedInstanced の引数
  uint instance_count;
  uint start_index;
  int base_vertex;
  uint start_instance;
};
```

| 構造体 | 役割 |
| --- | --- |
| `InstanceData` | 配置された 1 つの物体（ワールド行列・メッシュ番号・マテリアル番号）。シーンの全物体が並ぶ |
| `MeshInfo` | メッシュの種類ごとの情報（境界球・インデックスの範囲・PSO のバケット） |
| `IndirectCommand` | `ExecuteIndirect` が読む 1 回分の描画引数。先頭の 1 ワードがルート定数（インスタンス番号）、続く 20 バイトが `DrawIndexedInstanced` の引数 |

3 つの構造体は C++ と HLSL の両方に同じものを書きます。HLSL の `float4x4` は 64 バイト、`uint` と `int` は 4 バイトなので、ここで書いた並びなら両側の大きさが一致します。`float3` の直後に `float` を置くのは、16 バイトの境界をまたがないようにするためです。`float3` の次に `uint` や `int` を置くと HLSL のパッキング規則では詰められますが、C++ の `XMFLOAT3`（12 バイト）の直後には `uint32_t` が置かれて同じ位置になります。念のため各構造体の大きさを `static_assert` で固定しておきます。

`D3D12_DRAW_INDEXED_ARGUMENTS` は `IndexCountPerInstance`・`InstanceCount`・`StartIndexLocation`・`BaseVertexLocation`・`StartInstanceLocation`の20 バイトです。HLSL 側の`IndirectCommand`（6 ワード＝24 バイト）とフィールドの並び順が同じでなければなりません。

## 全メッシュを 1 つの巨大バッファに

**GPU Driven**ではメッシュごとに頂点バッファを切り替えません（切り替えは CPU の仕事になるため）。全メッシュの頂点を 1 つの頂点バッファ、全メッシュのインデックスを 1 つのインデックス バッファに詰め `MeshInfo` の `start_index`・`base_vertex`で範囲を指します。

| バッファ | 内容 |
| --- | --- |
| グローバル頂点バッファ | 全メッシュの頂点を連結 |
| グローバル インデックス バッファ | 全メッシュのインデックスを連結（`base_vertex` で頂点の位置を補正） |
| メッシュ情報バッファ | `MeshInfo` の配列 |
| インスタンス バッファ | `InstanceData` の配列（毎フレーム更新される部分あり） |

## 読む順序

1. [シーン データ](scene-data.md)：**バッファと記述子の作り方**
2. [バインドレス](bindless.md)：テクスチャを番号で引く
3. [カリング](culling.md)：コンピュート シェーダーで、コマンドを書く
4. [ExecuteIndirect](execute-indirect.md)：コマンド シグネチャと描画ループ
5. [Hi-Z と 2 パス](hiz-two-pass.md)：オクルージョン カリング
6. [メッシュレット](meshlets.md)：クラスタ単位のカリングとメッシュ シェーダー
7. [Synchronization and Debugging](sync-debug.md)：バリア・フェンス・よくある事故

## 関連ページ

- [GPU Driven Rendering](../gpu-driven.md)
- [Culling](../culling.md)
- [Hi-Z](../../optimization/hiz.md)
- [メッシュ シェーダー](../mesh-shaders.md)
- [ビジビリティ バッファ](../../lighting/visibility-buffer.md)
