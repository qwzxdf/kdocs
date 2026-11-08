---
title: Compute Culling and Command Generation
tags:
  - 描画最適化
---

# Compute Culling and Command Generation

GPU Driven の心臓部です。**コンピュート シェーダーが全インスタンスを 1 つずつ判定**し、見えるものだけを `ExecuteIndirect` が読む形式の「描画コマンド」としてバッファに書き出します。このページでは視錐台の平面の求め方（行ベクトル・左手系・D3D の深度範囲）・境界球の判定・原子的な追加（ストリーム コンパクション）・PSO バケット・カウンタのリセット・ディスパッチ・バリアを実コードで示します。

!!! tip "ポイント"
    - <strong>1 スレッド ＝ 1 インスタンス</strong>。<strong>64 スレッド</strong>のグループでディスパッチ。
    - 視錐台の 6 平面はビュー射影行列の列の和・差からCPU で作る（行ベクトル・D3D の z は 0〜w）。
    - 判定は境界球 vs 6 平面。ワールド行列のスケールを半径に反映。
    - 見えたら`InterlockedAdd` で出力位置を確保して、コマンドを書く（ストリーム コンパクション）。
    - カウンタは毎フレーム 0 にリセット。PSO バケットごとにカウンタと領域を分ける。
    - 書き込み後は UAV → INDIRECT_ARGUMENT のバリアを忘れない。

!!! info "このページを読む前に"
    - [GPU Driven Rendering](../gpu-driven.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](../../optimization/bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 視錐台の平面（C++）

**ビュー射影行列 `VP`**（行ベクトル規約：`clip = p * VP`）から、6 平面を作ります。クリップ空間の条件は D3D では次のとおりです。

- x: `-w ≤ x ≤ w`
- y: `-w ≤ y ≤ w`
- z: `0 ≤ z ≤ w`（OpenGL の `-w ≤ z` ではない）

`clip.x = dot(p, 列0)`、`clip.y = dot(p, 列1)`、`clip.z = dot(p, 列2)`、`clip.w = dot(p, 列3)` なので平面（`n·p + d ≥ 0` で内側）は列の和・差で得られます。

- 左: `列3 + 列0`
- 右: `列3 − 列0`
- 下: `列3 + 列1`
- 上: `列3 − 列1`
- 近: `列2`（`z ≥ 0`）
- 遠: `列3 − 列2`（`w − z ≥ 0`）

```cpp
// ビュー射影行列(行ベクトル規約: clip = p * VP)から、視錐台の 6 平面を取り出す。
// 平面は (nx, ny, nz, d)。dot(n, p) + d >= 0 が内側。
std::array<DirectX::XMFLOAT4, 6> ExtractFrustumPlanes(DirectX::FXMMATRIX view_projection) {
  DirectX::XMFLOAT4X4 m;                                       // 要素を m.m[行][列] で読むための、格納用の行列
  DirectX::XMStoreFloat4x4(&m, view_projection);               // XMMATRIX(SIMD レジスタ)をメモリに書き出す

  // 行ベクトル規約では、clip の各成分は「p と列ベクトルの内積」になるので、列を取り出す。
  auto column = [&m](int c) {                                  // c 番目の列 = 各行の c 番目の要素を集めたもの
    return DirectX::XMVectorSet(m.m[0][c], m.m[1][c], m.m[2][c], m.m[3][c]);
  };
  DirectX::XMVECTOR c0 = column(0);                            // clip.x を作る列
  DirectX::XMVECTOR c1 = column(1);                            // clip.y を作る列
  DirectX::XMVECTOR c2 = column(2);                            // clip.z を作る列
  DirectX::XMVECTOR c3 = column(3);                            // clip.w を作る列

  DirectX::XMVECTOR raw[6] = {                                 // 正規化する前の平面(列の和と差)
      DirectX::XMVectorAdd(c3, c0), DirectX::XMVectorSubtract(c3, c0),   // 左: w + x >= 0 / 右: w - x >= 0
      DirectX::XMVectorAdd(c3, c1), DirectX::XMVectorSubtract(c3, c1),   // 下: w + y >= 0 / 上: w - y >= 0
      c2,                           DirectX::XMVectorSubtract(c3, c2)};  // 近: z >= 0(D3D) / 遠: w - z >= 0

  std::array<DirectX::XMFLOAT4, 6> planes;                     // 結果
  for (int i = 0; i < 6; ++i) {
    DirectX::XMVECTOR length = DirectX::XMVector3Length(raw[i]);  // 法線(xyz)の長さ。w は含めない
    DirectX::XMStoreFloat4(&planes[i], DirectX::XMVectorDivide(raw[i], length));  // 4 成分すべてを割って、距離をワールドの単位にする
  }
  return planes;
}
```

行ベクトル規約では `clip.x` は `p` と列 0 の内積です。だから視錐台の平面は行ではなく列の和と差になります。左の平面なら `w + x >= 0` を変形して `列3 + 列0` です。取り出した 6 本のベクトルは法線の長さがばらばらです。そのまま球の半径と比べると距離の単位がそろわないので、`xyz` の長さで 4 成分すべてを割ります。

- 列を取り出す: `m.m[行][列]`。列ベクトルは各行の同じ列を集める
- 正規化: 法線 `(x, y, z)` の長さで、4 成分全部を割る。符号付き距離がワールド単位になる（球の半径と比べるため）
- 内側が正: `dot(plane.xyz, p) + plane.w ≥ 0` が内側
- 近平面が `c2`: D3D の `z ≥ 0`。OpenGL 用の `c3 + c2` と違うので注意

## 定数バッファ

```cpp
struct CullConstants {                       // カリング シェーダーに渡す定数(C++ 側)
  DirectX::XMFLOAT4 frustum_planes[6];       // 視錐台の 6 平面。16 バイト × 6 = 96 バイト
  uint32_t instance_count;                   // 判定するインスタンスの数(範囲外のスレッドを捨てるのに使う)
  uint32_t reserved[3];                      // 16 バイト境界までの詰め物。96 + 4 + 12 = 112
};
static_assert(sizeof(CullConstants) == 112);  // HLSL の cbuffer と大きさがずれると、後ろの値が壊れる
```

```hlsl
cbuffer CullConstants : register(b0) {       // 定数バッファ。C++ の CullConstants と並びを一致させる
  float4 frustum_planes[6];                  // 視錐台の 6 平面(法線は正規化済み)
  uint instance_count;                       // インスタンスの総数
  uint3 reserved;                            // 詰め物(C++ 側の reserved[3] に対応)
};
```

**定数バッファは毎フレーム値が変わる**ので、[アップロード リング](scene-data.md)に書き GPU 仮想アドレスをルート CBV に渡します（256 バイト境界に揃える）。

## カリング シェーダー

```hlsl
#define PLANE_COUNT 6                        // 視錐台の平面の数
#define MAX_COMMANDS_PER_BUCKET 65536        // PSO バケット 1 個が書ける、コマンドの最大数

StructuredBuffer<Instance> instances : register(t0);          // 全インスタンス(読み取り)
StructuredBuffer<MeshInfo> meshes : register(t1);             // メッシュ表(読み取り)
RWStructuredBuffer<IndirectCommand> commands : register(u0);  // 描画コマンドの出力先(バケットごとの領域)
RWByteAddressBuffer command_counts : register(u1);            // バケットごとの個数(4 バイト × バケット数)

bool SphereInFrustum(float3 center, float radius) {
  [unroll] for (int i = 0; i < PLANE_COUNT; ++i) {            // 6 平面ぶんを展開して並べる
    float distance = dot(frustum_planes[i].xyz, center) + frustum_planes[i].w;  // 球の中心から平面までの符号付き距離(内側が正)
    if (distance < -radius) return false;                     // 半径より深く外側にあれば、球全体が外にある
  }
  return true;                                                // どの平面の外側にも完全には出ていない
}

float MaxScale(float4x4 world) {
  float sx = length(world[0].xyz);                            // X 軸の方向ベクトルの長さ = X のスケール
  float sy = length(world[1].xyz);                            // Y のスケール
  float sz = length(world[2].xyz);                            // Z のスケール
  return max(sx, max(sy, sz));                                // 最大の軸に合わせて半径を伸ばす(安全側)
}

[numthreads(64, 1, 1)]                                        // 1 グループ 64 スレッド
void CullMain(uint3 id : SV_DispatchThreadID) {
  uint instance_index = id.x;                                 // 1 スレッド = 1 インスタンス
  if (instance_index >= instance_count) return;               // 切り上げで余ったスレッドは何もしない

  Instance instance = instances[instance_index];              // このスレッドが担当するインスタンス
  MeshInfo mesh = meshes[instance.mesh_index];                // そのメッシュの情報(境界球や描画の範囲)

  float3 center = mul(float4(mesh.bounds_center, 1.0), instance.world).xyz;  // メッシュ空間の球の中心をワールドへ(行ベクトル: p * W)
  float radius = mesh.bounds_radius * MaxScale(instance.world);              // 拡大を半径に反映する

  if (!SphereInFrustum(center, radius)) return;               // 視錐台の外なら、コマンドを作らない

  uint slot;                                                  // このバケットの何番目に書くか
  command_counts.InterlockedAdd(mesh.pso_bucket * 4, 1, slot);  // 個数を +1 し、加算前の値を slot に受け取る
  if (slot >= MAX_COMMANDS_PER_BUCKET) return;                // 領域を超える分は書かない(バッファの外を壊さない)

  IndirectCommand command;                                    // 書き出す描画コマンド
  command.instance_index = instance_index;                    // 頂点シェーダーが行列を引くための番号(ルート定数になる)
  command.index_count = mesh.index_count;                     // 描くインデックス数
  command.instance_count = 1;                                 // 1 コマンド = 1 インスタンス
  command.start_index = mesh.start_index;                     // 巨大なインデックス バッファの先頭位置
  command.base_vertex = mesh.base_vertex;                     // 巨大な頂点バッファの先頭位置
  command.start_instance = 0;                                 // 使わない(番号はルート定数で渡す)
  commands[mesh.pso_bucket * MAX_COMMANDS_PER_BUCKET + slot] = command;  // バケットの領域の slot 番目へ
}
```

流れを順に追うと①番号が範囲外なら戻る②インスタンスとメッシュ情報を読む、③境界球をワールドに移す④視錐台の外なら戻る⑤バケットのカウンタを増やして書く位置を決める、⑥コマンドを書くの 6 段階です。④の `return` が多くのスレッドをここで終わらせるので、見えない物のコストは③までの読み込みと計算だけで済みます。⑤の `InterlockedAdd` がスレッド同士が出力位置を奪い合わないための鍵です。

- **`SV_DispatchThreadID`**: グループ番号 × 64 ＋ グループ内番号。インスタンス番号にそのまま使える
- `mul(float4(p, 1), world)`: 行ベクトル規約（`p * W`）。このサイトの標準
- `MaxScale`: ワールド行列の 3 軸の長さの最大値。境界球の半径に掛ける（非一様スケールでも安全側）
- `distance < -radius`: 球が平面の外側に完全にはみ出すなら不可視
- `InterlockedAdd(..., 1, slot)`: カウンタを 1 増やし、増やす前の値を `slot` に受け取る。スレッド間で衝突しない出力位置が得られる
- **`mesh.pso_bucket * 4`: バケットごとの 4 バイトのカウンタ**（`ByteAddressBuffer` のバイト オフセット）
- `slot >= MAX`: 領域を超えた分は書かない（バッファ オーバーランを防ぐ）。カウンタは超えた値のままだが、ExecuteIndirect の最大数で切り詰められる
- `instance_count = 1`: 1 コマンド ＝ 1 インスタンス。同じメッシュを束ねる最適化は後述

### スレッドの順序は不定

`InterlockedAdd` で出力位置を取るのでコマンドが書かれる順序は、実行のたびに変わります。不透明の描画では順序は問題ない（深度テストで解決）が半透明（ソートが必要）には使えません（別の方法：キー付きソート）。

## 同じメッシュをまとめる（インスタンシング）

**同じメッシュの物体が多数ある**場合、1 インスタンスごとに 1 コマンドを出すとコマンド数が増えます。メッシュごとに見えるインスタンスを並べ `InstanceCount` を大きくして 1 コマンドにまとめる手もあります。

| 方式 | 内容 | 向き |
| --- | --- | --- |
| 1 インスタンス = 1 コマンド（本ページ） | 単純。ルート定数にインスタンス番号 | メッシュの種類が多い・実装を単純にしたい |
| メッシュ単位でまとめる | 見えるインスタンス番号の「リスト」をメッシュごとに作り、`InstanceCount` ＝ 個数 | 同じメッシュが大量（木・草・岩） |

まとめる方式は 2 段階（メッシュごとのカウント → プレフィックス和でオフセット → インスタンス番号を書く）になり、やや複雑です。まず単純な形を作りボトルネックならに進むのが現実的です。

## カウンタのリセットとディスパッチ

**毎フレーム**、カウンタを 0 に戻します。ゼロで埋めた小さなバッファから、コピーするのが簡単です。

```cpp
constexpr uint32_t kBucketCount = 4;              // PSO バケットの数(例)
constexpr uint32_t kMaxCommandsPerBucket = 65536; // シェーダーの MAX_COMMANDS_PER_BUCKET と同じ値にする

void Renderer::CreateCullBuffers() {
  // コマンド バッファ: 全バケットぶんの領域。GPU が書くので UAV を許可する。
  command_buffer_ = CreateDefaultBuffer(
      device_.Get(), sizeof(IndirectCommand) * kBucketCount * kMaxCommandsPerBucket,
      D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS, D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT);  // 毎フレームの最後の状態に合わせる
  // カウンタ バッファ: バケットごとに 4 バイト。
  count_buffer_ = CreateDefaultBuffer(device_.Get(), sizeof(uint32_t) * kBucketCount,
                                      D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS,
                                      D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT);

  std::array<uint32_t, kBucketCount> zeros = {};            // 全部 0 の配列(カウンタのリセット用)
  zero_buffer_ = CreateUploadBuffer(device_.Get(), sizeof(zeros));  // CPU から書ける小さなバッファ
  void* mapped = nullptr;
  D3D12_RANGE read_range = {0, 0};                          // CPU はこの範囲を読まない、という宣言
  ThrowIfFailed(zero_buffer_->Map(0, &read_range, &mapped));  // CPU から書けるようにアドレスを得る
  std::memcpy(mapped, zeros.data(), sizeof(zeros));         // ゼロを書き込む
  zero_buffer_->Unmap(0, nullptr);                          // 書き込み終わり
}
```

```cpp
void Renderer::RecordCull(ID3D12GraphicsCommandList* list, const CullConstants& constants,
                          D3D12_GPU_VIRTUAL_ADDRESS constants_address) {
  // ① カウンタ バッファを、コピーの書き込み先の状態にする。
  D3D12_RESOURCE_BARRIER to_copy = MakeTransitionBarrier(
      count_buffer_.Get(), D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT, D3D12_RESOURCE_STATE_COPY_DEST);
  list->ResourceBarrier(1, &to_copy);
  list->CopyBufferRegion(count_buffer_.Get(), 0, zero_buffer_.Get(), 0,
                         sizeof(uint32_t) * kBucketCount);   // ゼロをコピーして、カウンタを 0 に戻す

  // ② 2 つのバッファを、シェーダーが書ける状態にする。
  D3D12_RESOURCE_BARRIER to_uav[2] = {
      MakeTransitionBarrier(count_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
                            D3D12_RESOURCE_STATE_UNORDERED_ACCESS),
      MakeTransitionBarrier(command_buffer_.Get(), D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT,
                            D3D12_RESOURCE_STATE_UNORDERED_ACCESS),
  };
  list->ResourceBarrier(2, to_uav);

  // ③ パイプラインとルート パラメーターを設定する。
  list->SetPipelineState(cull_pso_.Get());                  // カリングのコンピュート PSO
  list->SetComputeRootSignature(cull_root_signature_.Get());  // 対応するルート シグネチャ
  list->SetComputeRootConstantBufferView(kCullRootConstants, constants_address);  // 定数(視錐台など)
  list->SetComputeRootShaderResourceView(kCullRootInstances,
                                         instance_buffer_->GetGPUVirtualAddress());  // t0: インスタンス
  list->SetComputeRootShaderResourceView(kCullRootMeshes, mesh_buffer_->GetGPUVirtualAddress());  // t1: メッシュ表
  list->SetComputeRootUnorderedAccessView(kCullRootCommands,
                                          command_buffer_->GetGPUVirtualAddress());  // u0: コマンドの出力先
  list->SetComputeRootUnorderedAccessView(kCullRootCounts,
                                          count_buffer_->GetGPUVirtualAddress());    // u1: バケットごとのカウンタ

  // ④ 実行。1 スレッド = 1 インスタンスなので、64 で割って切り上げた数のグループを起動する。
  uint32_t group_count = (constants.instance_count + 63) / 64;
  list->Dispatch(group_count, 1, 1);

  // ⑤ 書き込みが終わるのを待って、ExecuteIndirect が読める状態に戻す。
  D3D12_RESOURCE_BARRIER to_indirect[2] = {
      MakeTransitionBarrier(count_buffer_.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                            D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT),
      MakeTransitionBarrier(command_buffer_.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                            D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT),
  };
  list->ResourceBarrier(2, to_indirect);
}
```

`CreateCullBuffers` は起動時に 1 回だけ呼びます。コマンド バッファは `kBucketCount × kMaxCommandsPerBucket` 個ぶん（ここでは 4 × 65,536）を確保するので、バケットの数を増やすとメモリが比例して増えます。ゼロの入ったアップロード バッファは、毎フレームのカウンタのリセットで使い回します。`RecordCull` は 5 つの段階でバリアは 3 回です。カウンタを COPY_DEST にして 0 を書き 2 つのバッファを UAV にして、ディスパッチし最後に両方を INDIRECT_ARGUMENT へ戻します。

- 初期状態 `INDIRECT_ARGUMENT`: 毎フレームの最後が `INDIRECT_ARGUMENT`なので、最初もそれに揃える（遷移の連鎖が簡単）
- コマンド バッファはクリア不要: カウンタ以降の領域は読まれない（ExecuteIndirect は、カウント分だけ読む）
- カウンタ バッファのコピー: `COPY_DEST` に遷移 → ゼロをコピー → `UNORDERED_ACCESS` に遷移
- `SetComputeRootConstantBufferView`: GPU 仮想アドレスをそのまま渡す。ヒープ設定が不要
- `(count + 63) / 64`: 切り上げ除算。範囲外のスレッドはシェーダー先頭で `return`
- 終了時の遷移: UAV → `INDIRECT_ARGUMENT`。これを忘れると ExecuteIndirect が、書き込み途中の値を読む

!!! note "ClearUnorderedAccessViewUint という手もある"
    `ClearUnorderedAccessViewUint` でも0 を書けますが、シェーダー可視ヒープ上の GPU ハンドルと CPU ハンドル（非シェーダー可視でもよい）の両方が必要です。今回のようにルート UAV（記述子なし）で扱う構成では、コピー方式が簡単です。

## 負荷の見積もり

- **スレッド数**: インスタンス数（10 万個で約 1,600 グループ）
- メモリ読み出し: 1 インスタンス 80 バイト ＋ メッシュ情報 32 バイト。10 万個で約 11 MB
- GPU 時間の目安: 数十〜百数十マイクロ秒（10 万インスタンス・現代の GPU）
- 原子操作の競合: 全スレッドが同じカウンタを叩く。バケットを分けると緩和。ウェーブ単位で集約する最適化もある（`WaveActiveCountBits` ＋ 代表レーンの 1 回の `InterlockedAdd`）

### ウェーブ単位の集約

ウェーブ内の「見える」スレッド数をまとめて、1 回だけ `InterlockedAdd` する最適化です。

```hlsl
bool visible = SphereInFrustum(center, radius);                 // このスレッドの結果(見える = true)
uint wave_visible_count = WaveActiveCountBits(visible);         // ウェーブ内で「見える」スレッドの数
uint wave_offset = 0;                                           // ウェーブ全体の書き込み開始位置
if (WaveIsFirstLane() && wave_visible_count > 0) {              // 先頭のレーンだけが、まとめて 1 回だけ加算する
  command_counts.InterlockedAdd(bucket * 4, wave_visible_count, wave_offset);  // 個数をまとめて予約し、加算前の値を受け取る
}
wave_offset = WaveReadLaneFirst(wave_offset);                   // 先頭レーンの値を、ウェーブの全スレッドに配る
uint slot = wave_offset + WavePrefixCountBits(visible);         // 自分より前の「見える」スレッドの数だけ、後ろに書く
```

`WaveActiveCountBits` はウェーブ内の `true` の数を返し、`WavePrefixCountBits` は自分より前の `true` の数を返します。たとえば 32 レーンのうち 10 レーンが見えるなら原子操作は 32 回から 1 回に減ります。先頭レーンが 10 個ぶんをまとめて予約し、各レーンが「自分より前の見えるレーンの数」を足して、重ならない位置に書きます。

複数バケットが混ざる場合はバケットごとに同様の処理が必要で、複雑になります。まず単純な `InterlockedAdd` で動かしボトルネックなら導入します。

<!-- fig:prefix-compact:begin -->

<svg class="fig illust motion" data-fig="prefix-compact" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-prefix-compact" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">カリング結果の詰め直し: 見える物の番号を隙間なく並べる</text>
<text x="148" y="121" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">物体の番号</text>
<text x="148" y="186" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">見える? (1 = 見える)</text>
<text x="148" y="251" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">手前までの合計(出力位置)</text>
<rect x="160" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="187.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">0</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="160" y="160" width="54" height="40" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="187.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="160" y="225" width="54" height="40" fill="#dcfce7" stroke="#94a3b8" stroke-width="1.5"/>
<text x="187.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#2ea043">0</text>
</g>
<rect x="218" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="245.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">1</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="218" y="160" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="245.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="218" y="225" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="245.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">1</text>
</g>
<rect x="276" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="303.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">2</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="276" y="160" width="54" height="40" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="303.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="276" y="225" width="54" height="40" fill="#dcfce7" stroke="#94a3b8" stroke-width="1.5"/>
<text x="303.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#2ea043">1</text>
</g>
<rect x="334" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="361.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">3</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="334" y="160" width="54" height="40" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="361.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="334" y="225" width="54" height="40" fill="#dcfce7" stroke="#94a3b8" stroke-width="1.5"/>
<text x="361.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#2ea043">2</text>
</g>
<rect x="392" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="419.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">4</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="392" y="160" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="419.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="392" y="225" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="419.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">3</text>
</g>
<rect x="450" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="477.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">5</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="450" y="160" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="477.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="450" y="225" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="477.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">3</text>
</g>
<rect x="508" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="535.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">6</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="508" y="160" width="54" height="40" fill="#2563eb" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="535.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="508" y="225" width="54" height="40" fill="#dcfce7" stroke="#94a3b8" stroke-width="1.5"/>
<text x="535.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#2ea043">3</text>
</g>
<rect x="566" y="95" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="593.0" y="121" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">7</text>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="0;0;1;1"/><rect x="566" y="160" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" opacity="0.85"/>
<text x="593.0" y="186" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;1.0000" values="0;0;1;1"/><rect x="566" y="225" width="54" height="40" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="593.0" y="251" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#64748b">4</text>
</g>
<text x="148" y="316" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28">出力（描く物の一覧）</text>
<rect x="160" y="290" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.4543;0.4545;1.0000" values="0;0;1;1"/><rect x="160" y="290" width="54" height="40" fill="#e5aa28" opacity="0.85"/>
<text x="187.0" y="316" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">0</text>
</g>
<rect x="218" y="290" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.5270;0.5273;1.0000" values="0;0;1;1"/><rect x="218" y="290" width="54" height="40" fill="#e5aa28" opacity="0.85"/>
<text x="245.0" y="316" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">2</text>
</g>
<rect x="276" y="290" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><rect x="276" y="290" width="54" height="40" fill="#e5aa28" opacity="0.85"/>
<text x="303.0" y="316" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">3</text>
</g>
<rect x="334" y="290" width="54" height="40" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.6725;0.6727;1.0000" values="0;0;1;1"/><rect x="334" y="290" width="54" height="40" fill="#e5aa28" opacity="0.85"/>
<text x="361.0" y="316" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#ffffff">6</text>
</g>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">GPU が 8 個の物体を同時に調べる<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">見える物は 1、隠れた物は 0<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.0604;0.0606;0.2422;0.2424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">手前までの 1 の合計を計算する(プレフィックス サム)。これが出力位置<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.2422;0.2424;0.4543;0.4545;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">見える物だけが、自分の出力位置に番号を書き込む。描画命令の数は 4 つ<animate attributeName="opacity" dur="16.5s" repeatCount="indefinite" keyTimes="0.0000;0.4543;0.4545;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:prefix-compact:end -->

## よくあるミス

??? failure "近平面を OpenGL の式（c3 + c2）で作って、手前の物が消える／近くの物が残る"
    **D3D の `z ≥ 0` は列 2 そのもの**。遠平面は `c3 − c2`。

??? failure "平面を正規化せず半径と比べて、判定が距離でずれる"
    法線の長さで4 成分を割る。

??? failure "ワールド行列のスケールを無視して、拡大された物が端で消える"
    境界球の半径に `MaxScale`を掛ける。

??? failure "カウンタをリセットせずフレームごとにコマンドが積み上がる"
    毎フレーム、ゼロ コピー（または Clear）をする。

??? failure "UAV → INDIRECT_ARGUMENT のバリアを忘れて、描画がたまに欠ける・壊れる"
    書き込み後は必ず遷移。デバッグ レイヤーが警告する。

??? failure "バケットの上限を超えて、他のバケットの領域を壊す"
    `slot >= MAX` で書かない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>1 スレッド ＝ 1 インスタンス</strong>。境界球と視錐台 6 平面で判定
    - [x] 平面は `VP` の列の和・差で作り正規化する。D3D の近平面は列 2
    - [x] `InterlockedAdd` で出力位置を確保（ストリーム コンパクション）。順序は不定
    - [x] PSO バケットごとにカウンタ・領域を分ける。上限超えは書かない
    - [x] カウンタのリセット → ディスパッチ → UAV → INDIRECT_ARGUMENT のバリア

## 参考

- Gribb, Hartmann, "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix"（2001）
- Microsoft, "Compute Shader Overview"（HLSL）
- Wihlidal, "Optimizing the Graphics Pipeline with Compute"（GDC 2016）

## 関連ページ

- [GPU Driven (D3D12)](index.md)
- [シーン データ](scene-data.md)
- [ExecuteIndirect](execute-indirect.md)
- [Hi-Z と 2 パス](hiz-two-pass.md)
- [視錐台カリング](../culling.md)
