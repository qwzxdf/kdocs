---
title: DirectX 12 Guide
tags:
  - DirectX
---

# DirectX 12 Guide

ゲームを作っていると「描く命令を出した順に GPU が実行している」と考えがちです。ところが実際の GPU は CPU とは別の速さで動いていて、命令を出した瞬間に絵が描かれるわけではありません。DirectX 11 まではこの違いをドライバーが隠してくれていました。メモリの置き場所を決めるのも命令の順番を整えるのもドライバーの仕事でした。

DirectX 12（Direct3D 12、D3D12）はその仕事をアプリに返した API です。コードは増えて難しくなりますが、そのぶんドライバーが裏で何をしているか分からない、という状態がなくなります。命令を複数のスレッドで作れるので、CPU の負荷も下げられます。レイトレーシング（DXR）、メッシュ シェーダー、バインドレスのような新しい機能もこの API でだけ使えます。

このセクションはウィンドウに三角形を出すところから始めて、テクスチャ、計算シェーダー、DXR まで 1 つずつ動かしながら説明します。DirectX 11 を知らなくても読めます（[DirectX 11 Guide](../dx11/index.md) は、別の系列です）。

!!! info "このセクションを読む前に"
    C++ のポインターと参照（[ポインタ](../../basics/pointer.md)、[参照と const 参照](../../basics/reference.md)）、スマート ポインター（[所有権](../../basics/ownership.md)）が分かれば読めます。Win32 のウィンドウの作り方は[Win32 Window and Message Loop](window.md) にまとめています。

## この API の考え方

D3D12 の中心にあるのは、「命令を記録すること」と「実行すること」を分けて考える見方です。CPU は `Draw` などの命令をコマンド リストという入れ物に書き込むだけです。書き終えたリストをコマンド キューに渡して初めて、GPU が実行を始めます。CPU は渡したあとすぐ次の仕事に進めます。

```text
CPU:  コマンド リストに、命令を記録する（Draw、Dispatch、バリア…）
        ↓ Close
      コマンド キューに、リストを渡す（ExecuteCommandLists）
        ↓
GPU:  キューの命令を、順に実行する
        ↓
CPU:  フェンスで、GPU が終わったかを確認する
```

この流れに次の物が登場します。それぞれ専用のページがあります。

- GPU に物を作らせる窓口が[Device](factory-device.md) です。
- 仕事を渡す窓口が [Command Queue](command-queue.md)、命令を書き込む窓口が [Command List](command-list.md)、その置き場が [Command Allocator](command-allocator.md) です。
- CPU が GPU の終了を知る仕組みが、[Fence](fence.md) です。
- リソースの「見方」を並べた表が [Descriptor Heap](descriptor-heap.md) と [Descriptor](descriptor.md) で、リソースの使い方の切り替えを GPU に伝えるのが [Resource Barrier](resource-barrier.md) です。
- シェーダーの引数の型が [Root Signature](root-signature.md)、パイプライン全体の設定が [PSO](pso.md) です。

この仕事の多さが D3D12 が難しいと言われる理由です。ただ、1 つずつ役割が分かればやっていることは単純です。

## 読む順番

| 段階 | ページ |
| --- | --- |
| ① 土台 | [Helper Functions](util.md) → [Win32 Window and Message Loop](window.md) → [Device and Factory](factory-device.md) → [Command Queue](command-queue.md) → [Command Allocator](command-allocator.md) → [Command List](command-list.md) → [Fence](fence.md) → [Swap Chain](swap-chain.md) |
| ② リソース | [Descriptor Heap](descriptor-heap.md) → [Descriptor](descriptor.md) → [Resource Barrier](resource-barrier.md) → [Heaps and Resources](heaps-resources.md) → [Upload Buffer](upload-buffer.md) |
| ③ パイプライン | [Shaders and DXC](shaders-dxc.md) → [Root Signature](root-signature.md) → [PSO](pso.md) → [Vertex and Index Buffer Views](vertex-index-view.md) → [Drawing a Triangle](triangle.md) |
| ④ 動かす・貼る・立体に | [Constant Buffer](constant-buffer.md) → [Texture Upload](texture-upload.md) → [Depth Buffer](depth-buffer.md) → [Viewport and Scissor](viewport-scissor.md) |
| ⑤ 実用 | [Frame Resources](frame-resources.md) → [Compute Shader](compute-shader.md) → [GPU Queries and Timing](query-timing.md) → [Debug Layer](debug-layer.md) → [DXR Host Setup](dxr-host.md) |

関数やインターフェースを 1 つずつ引きたいときは、[API リファレンス](api/index.md) があります。コードの中の名前からその解説へ飛べます。

## このセクションの前提

- 言語は C++23 で Google C++ Style です。`Microsoft::WRL::ComPtr` を使います。
- **`d3dx12.h` は使いません。** 構造体は素の `D3D12_*` を書き毎回同じになる組み立てだけを[Helper Functions](util.md) の小さな関数にまとめています。
- シェーダーは HLSL で、シェーダー モデル 6.0 以上（コンパイラーは `dxc`）です。
- 座標系は左手系で Y が上、前は +Z です。行ベクトルを使い三角形は時計回りが表です。
- Windows 10 以降と D3D12 に対応した GPU（機能レベル 11.0 以上）が必要です。

## アプリが自分で行う仕事

D3D12 でアプリが受け持つ仕事を一覧にします。

| 仕事 | 内容 | ページ |
| --- | --- | --- |
| 命令の記録と投入 | コマンド リストに記録して、キューに渡す | [Command List](command-list.md) |
| GPU の完了待ち | フェンスで同期する | [Fence](fence.md) |
| リソースの状態管理 | バリアで状態を切り替える | [Resource Barrier](resource-barrier.md) |
| ビューの管理 | ディスクリプタ ヒープに自分で並べる | [Descriptor Heap](descriptor-heap.md) |
| パイプラインの一括設定 | PSO にまとめて、事前に作る | [PSO](pso.md) |
| メモリの置き場所 | ヒープの種類を選んで、アップロードする | [Heaps and Resources](heaps-resources.md) |

## 関連ページ

- [API リファレンス](api/index.md)
- [DirectX 11 Guide](../dx11/index.md)
- [DirectX の概念](../concepts/index.md)
- [DX11 と DX12 の対応表](../compare.md)
- [GPU Driven（D3D12 詳細）](../../rendering/gpu-driven-dx12/index.md)
- [DirectX 12 での初期化まとめ（ImGui）](../../libs/imgui/dx12.md)
