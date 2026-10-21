---
title: DirectX 12 Guide
tags:
  - DirectX
---

# DirectX 12 Guide

<strong>DirectX 12（Direct3D 12、D3D12）</strong>は <strong>GPU をほぼ直接、操作する</strong>、低レベルな API です。メモリの管理、命令の並べ替え読み書きの衝突の整理といった仕事を <strong>アプリが自分で</strong>行います。そのぶんコードは大きく難しくなりますが、<strong>CPU の負荷が小さく</strong>、マルチスレッドで命令を作れレイトレーシング（DXR）、メッシュ シェーダー、バインドレス、GPU ドリブンのような新しい機能が、使えます。このセクションはウィンドウから三角形、テクスチャ、計算シェーダー、DXR まで 1 つずつ動かしながら、説明します。ほかの DirectX を知らなくても、読めます（[DirectX 11 Guide](../dx11/index.md) とは、別の系列です）。

## この API の考え方

D3D12 は <strong>「命令の記録」と「実行」を分けた</strong>、API です。

```text
CPU:  コマンド リスト に、命令を、記録する（Draw、Dispatch、バリア…）
        ↓ Close
      コマンド キュー に、コマンド リストを、投げる（ExecuteCommandLists）
        ↓
GPU:  キューの、命令を、順に、実行する
        ↓
CPU:  フェンス で、GPU の完了を、確認する（Signal / 待つ）
```

| 登場する物 | 役割 |
| --- | --- |
| [Device](factory-device.md) | GPU に物を作らせる |
| [Command Queue](command-queue.md) | GPU に仕事を渡す窓口（キュー） |
| [Command Allocator](command-allocator.md)・[Command List](command-list.md) | 命令を、記録するメモリと記録の窓口 |
| [Fence](fence.md) | CPU と GPU の同期（「ここまで終わった」の、目印） |
| [Descriptor Heap](descriptor-heap.md)・[Descriptor](descriptor.md) | リソースの、「見方」を並べた表 |
| [Resource Barrier](resource-barrier.md) | リソースの使い方の切り替え（読む → 書く）の、明示 |
| [Root Signature](root-signature.md)・[PSO](pso.md) | シェーダーの引数の型と、パイプライン全体の設定 |

## 読む順番

| 段階 | ページ |
| --- | --- |
| ① 土台 | [Device and Factory](factory-device.md) → [Command Queue](command-queue.md) → [Command Allocator](command-allocator.md) → [Command List](command-list.md) → [Fence](fence.md) → [Swap Chain](swap-chain.md) |
| ② リソース | [Descriptor Heap](descriptor-heap.md) → [Descriptor](descriptor.md) → [Resource Barrier](resource-barrier.md) → [Heaps and Resources](heaps-resources.md) → [Upload Buffer](upload-buffer.md) |
| ③ パイプライン | [Shaders and DXC](shaders-dxc.md) → [Root Signature](root-signature.md) → [PSO](pso.md) → [Vertex and Index Buffer Views](vertex-index-view.md) → [Drawing a Triangle](triangle.md) |
| ④ 動かす・貼る・立体に | [Constant Buffer](constant-buffer.md) → [Texture Upload](texture-upload.md) → [Depth Buffer](depth-buffer.md) → [Viewport and Scissor](viewport-scissor.md) |
| ⑤ 実用 | [Frame Resources](frame-resources.md) → [Compute Shader](compute-shader.md) → [GPU Queries and Timing](query-timing.md) → [Debug Layer](debug-layer.md) → [DXR Host Setup](dxr-host.md) |

## このセクションの前提

| 項目 | 内容 |
| --- | --- |
| 言語 | C++23。Google C++ Style |
| ヘルパー | `d3dx12.h`（`CD3DX12_*`）。`Microsoft::WRL::ComPtr` |
| シェーダー | HLSL。SM 6.0 以上（`dxc`）。SM 5.1 の `fxc` でも動く |
| 座標系 | 右手系・Y が上・前は −Z。行ベクトル。三角形は反時計回りが表 |
| 必要な環境 | Windows 10 以降、D3D12 対応の GPU（機能レベル 11.0 以上） |
| ウィンドウ | [Win32 Window and Message Loop](../dx11/window.md) と同じ。このセクションでは省く |

## アプリが自分で行う仕事

D3D12 では次の仕事をアプリが自分で、行います。

| 仕事 | 内容 | ページ |
| --- | --- | --- |
| 命令の記録と投入 | コマンド リストに記録してキューに投げる | [Command List](command-list.md) |
| GPU の完了待ち | フェンスで、同期する | [Fence](fence.md) |
| リソースの状態管理 | バリアで状態を切り替える | [Resource Barrier](resource-barrier.md) |
| ビューの管理 | ディスクリプタ ヒープに自分で、並べる | [Descriptor Heap](descriptor-heap.md) |
| パイプラインの一括設定 | PSO にまとめて事前に作る | [PSO](pso.md) |
| メモリの置き場所 | ヒープの種類を選んで、アップロードする | [Heaps and Resources](heaps-resources.md) |

この仕事の多さが D3D12 が「難しい」と言われる理由ですが <strong>1 つずつ役割を、理解すれば</strong>、やっていることは単純です。

## 用語について

このセクションに出てくる API の名前や用語は、1 つずつ専用のページを持っています。文章の中の最初の 1 回はそのページへのリンクになります。

## 関連ページ

- [DirectX 11 Guide](../dx11/index.md)
- [DirectX の概念](../concepts/index.md)
- [DX11 と DX12 の対応表](../compare.md)
- [GPU Driven（D3D12 詳細）](../../rendering/gpu-driven-dx12/index.md)
- [DirectX 12 での初期化まとめ（ImGui）](../../libs/imgui/dx12.md)
