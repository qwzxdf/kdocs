---
title: DX12 and Vulkan Mapping
tags:
  - DirectX
---

# DX12 and Vulkan Mapping

DX12 を読んだあとで Vulkan の資料を開くと、知らない言葉ばかりで戸惑います。ところが、中でやっていることは驚くほど近いです。どちらも「アプリが GPU を明示的に管理する」API だからです。名前が違うだけで、役割が対応している部品がほとんどです。

このページは、DX12 の用語が Vulkan のどれに当たるかを引く、対応表です。Vulkan の使い方そのものは扱いません。

!!! tip "ポイント"
    - 大きな構造は同じ。デバイス、キュー、コマンドの記録と投入、同期、リソースの状態管理
    - 名前が一番違うのは、同期（フェンス / セマフォ）と、リソースのバインド（ルート シグネチャ / ディスクリプタ セット）
    - Vulkan のほうが、メモリの確保と画像のレイアウト遷移を細かく扱う
    - シェーダーは SPIR-V 形式。HLSL は DXC で SPIR-V に変換して使える
    - 座標の違い（Y の向き、深度の範囲）に注意

!!! info "このページを読む前に"
    - [DirectX 12 Guide](dx12/guide.md)
    - [Device and Factory](dx12/factory-device.md)

## オブジェクトの対応 {#objects}

| DX12 | Vulkan | 一言 |
| --- | --- | --- |
| `IDXGIFactory` | `VkInstance` | API の入口。アダプターを列挙する |
| `IDXGIAdapter` | `VkPhysicalDevice` | 物理的な GPU |
| `ID3D12Device` | `VkDevice` | 論理デバイス。リソースを作る窓口 |
| `ID3D12CommandQueue` | `VkQueue` | コマンドを GPU に投げる先 |
| `ID3D12CommandAllocator` | `VkCommandPool` | コマンドを置くメモリ |
| `ID3D12GraphicsCommandList` | `VkCommandBuffer` | コマンドの記録先 |
| `IDXGISwapChain3` | `VkSwapchainKHR` | 画面に出す画像の列 |
| `ID3D12Resource` | `VkBuffer` / `VkImage` | バッファとテクスチャ |
| `ID3D12Heap` | `VkDeviceMemory` | GPU のメモリの塊 |
| ディスクリプタ ヒープ / テーブル | `VkDescriptorPool` / `VkDescriptorSet` | リソースの参照の置き場 |
| ルート シグネチャ | `VkPipelineLayout` | シェーダーに渡すリソースの形 |
| PSO | `VkPipeline` | パイプラインの状態の塊 |
| `ID3D12Fence` | `VkFence` / `VkSemaphore` | 同期（詳しくは下） |
| リソース バリア | `vkCmdPipelineBarrier` | 状態の切り替えと同期 |
| デバッグ レイヤー | Validation Layer | API の誤用を検出する |

名前が違っても、組み立ての順序は同じです。「デバイスを作る → キューを取る → アロケーターとリストを作る → 記録する → 投げる → 待つ」の流れは、そのまま対応します。

## 同期の違い {#sync}

DX12 の `ID3D12Fence` は、1 つの種類で CPU と GPU の同期、キュー同士の同期の両方を担います。値が増えていく単調増加の数字を GPU が書き、CPU やほかのキューが「この値になるまで待つ」という形です。

Vulkan は、用途ごとに名前が分かれます。

- `VkFence`：GPU から CPU へ「終わった」を伝える。CPU が待つ
- `VkSemaphore`：キュー同士の順序付け。GPU の中で完結する
- `VkEvent`：コマンド バッファの中での細かい同期

Vulkan 1.2 以降の<strong>タイムライン セマフォ</strong>は、数字が増えていく仕組みで、DX12 のフェンスと同じ考え方です。新しい Vulkan のコードでは、これを使うと、DX12 から移りやすくなります。

## リソースのバインド {#binding}

DX12 は、ルート シグネチャに「何番目のスロットに何が入るか」を宣言し、ディスクリプタ ヒープの中の範囲をディスクリプタ テーブルとして渡します。ルート定数は、シグネチャの中に直接書き込める小さい値です。

Vulkan は、ディスクリプタ セット レイアウトで「1 つのセットの形」を宣言し、複数のセットをパイプライン レイアウトにまとめます。実行時には、ディスクリプタ プールからセットを確保して、リソースを書き込み、`vkCmdBindDescriptorSets` で結びつけます。DX12 のルート定数に当たるのが、プッシュ定数（push constants）です。

どちらも、「シェーダーが見る世界の形を先に宣言し、実行時に中身を差し込む」考え方です。

## リソースの状態とレイアウト {#state}

DX12 は、リソースごとの状態（`RENDER_TARGET`、`PIXEL_SHADER_RESOURCE` など）をバリアで切り替えます。

Vulkan のバッファはアクセスの同期だけですが、画像には、さらに<strong>レイアウト</strong>（`COLOR_ATTACHMENT_OPTIMAL`、`SHADER_READ_ONLY_OPTIMAL` など）があり、バリアでこれを切り替えます。メモリ上の並び方を用途に合わせて変えるという意味です。DX12 は状態にこの意味が含まれていて、1 つの概念で済みます。

## メモリ {#memory}

DX12 のヒープの種類（Default / Upload / Readback）は、Vulkan では「メモリ タイプ」のフラグで表されます。

| DX12 | Vulkan |
| --- | --- |
| Default ヒープ | `DEVICE_LOCAL`（GPU が速く読む） |
| Upload ヒープ | `HOST_VISIBLE` + `HOST_COHERENT`（CPU が書ける） |
| Readback ヒープ | `HOST_VISIBLE` + `HOST_CACHED`（CPU が読める） |

Vulkan は、メモリの確保が回数に上限があるため、大きな塊を確保して、リソースを切り出すのが前提です。VMA（Vulkan Memory Allocator）というライブラリがその仕事を代行します。

## シェーダー {#shaders}

DX12 は DXIL、Vulkan は SPIR-V が、コンパイル後の形式です。HLSL で書いたシェーダーは、DXC に `-spirv` を付けるだけで、Vulkan 用の SPIR-V に変換できます。同じ HLSL を両方の API で使いたい場合に便利です。

ただし、リソースの番号の振り方（`register` と `[[vk::binding]]`）や、いくつかの組み込み関数に違いがあります。

## 座標系の違い {#coords}

| 項目 | DX12 | Vulkan |
| --- | --- | --- |
| NDC の Y | 上が +1 | 下が +1（Y が下向き） |
| NDC の深度 | 0 〜 1 | 0 〜 1 |
| テクスチャの原点 | 左上 | 左上 |

Vulkan は、NDC の Y が下向きなので、DX と同じ行列を使うと、画面が上下逆になります。ビューポートの高さに負の値を指定する（Vulkan 1.1 以降）か、投影行列で Y を反転して合わせます。深度の範囲は、OpenGL と違って、0〜1 で DX と同じです。

## 描画の枠組み {#render-pass}

DX12 にも、`BeginRenderPass` はありますが、多くのコードは `OMSetRenderTargets` で済ませています。Vulkan は、もともと「レンダー パス」でレンダー ターゲットの使い方を宣言する形でした。今は、Vulkan 1.3 の動的レンダリング（`vkCmdBeginRendering`）で、DX12 の書き方に近くなっています。

## これだけ覚える {#summary}

- 部品の役割は、ほぼ 1 対 1 で対応する。デバイス、キュー、リスト、PSO、バリア
- 違いが大きいのは、同期、バインド、画像のレイアウト、メモリの確保
- 座標系は、Vulkan の Y が下向き。HLSL は DXC で SPIR-V に変換できる

## 関連ページ

- [DX11 and DX12 Mapping](compare.md)
- [DirectX 12 Guide](dx12/guide.md)
- [Root Signature](dx12/root-signature.md)
