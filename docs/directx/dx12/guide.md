---
title: DirectX 12 Guide
tags:
  - DirectX
---

# DirectX 12 Guide

DirectX 12 は、管理することが多い API です。デバイスを作り、コマンドを溜めるキューとリスト、GPU の終わりを待つフェンス、リソースの状態を切り替えるバリア、ディスクリプタのヒープ、ルート シグネチャ、PSO と、三角形 1 枚のために必要な部品が一気に出てきます。部品ごとのページを順に読むと、全体のつながりが見えにくくなります。

このページは、<strong>空のウィンドウから、回る立方体まで</strong>を 8 つの段階に分けて順に示します。各段階に「ゴール」があるので、どこで詰まっているのか分かります。

!!! tip "ポイント"
    - 最初から [デバッグ レイヤー](debug-layer.md) を有効にする。バリアの不足やヒープの使い間違いは、メッセージで教えてくれる
    - 描画の骨格は、コマンドを記録して、キューに投げて、フェンスで待つ。これが回れば、あとは部品の追加
    - リソースの状態（Present、RenderTarget など）をバリアで切り替えるのを忘れない
    - 段階 4 の三角形までが、最初の山。そこまでは飛ばさずに、順に作る

!!! info "このページを読む前に"
    - [DirectX 12](index.md)（このセクションの全体像）
    - [Git の基礎](../../vs/git.md)（段階ごとにコミットする）

## 8 つの段階 {#steps}

| 段階 | ゴール | 読むページ |
| --- | --- | --- |
| 1 | 空のウィンドウ | [Win32 Window and Message Loop](window.md) |
| 2 | デバイス、コマンド キュー、スワップ チェーンが作れる | [Device and Factory](factory-device.md)、[Command Queue](command-queue.md)、[Swap Chain](swap-chain.md) |
| 3 | 画面が単色で塗りつぶされる | [Descriptor Heap](descriptor-heap.md)、[Command Allocator](command-allocator.md)、[Command List](command-list.md)、[Resource Barrier](resource-barrier.md)、[Fence](fence.md) |
| 4 | 三角形が出る | [Heaps and Resources](heaps-resources.md)、[Upload Buffer](upload-buffer.md)、[Root Signature](root-signature.md)、[Shaders and DXC](shaders-dxc.md)、[PSO](pso.md)、[Vertex and Index Buffer Views](vertex-index-view.md)、[Viewport and Scissor](viewport-scissor.md)、[Drawing a Triangle (D3D12)](triangle.md) |
| 5 | 三角形が回る | [Constant Buffer (D3D12)](constant-buffer.md) |
| 6 | 複数フレームを重ねても壊れない | [Frame Resources](frame-resources.md) |
| 7 | 立方体が正しく描かれる | [Depth Buffer (D3D12)](depth-buffer.md) |
| 8 | テクスチャを貼る | [Texture Upload](texture-upload.md) |

## 段階 1：ウィンドウ {#step1}

DirectX と関係なく、Win32 のウィンドウとメッセージ ループを書きます。閉じるボタンで終了できれば、ゴールです。

## 段階 2：デバイスとスワップ チェーン {#step2}

DXGI のファクトリーでアダプター（GPU）を選び、`D3D12CreateDevice` でデバイスを作ります。コマンド キューを作り、そのキューに結びつけて、スワップ チェーンを作ります。DX12 では、スワップ チェーンの作成に<strong>コマンド キューが必要</strong>です。

デバッグ ビルドでは、デバイスを作る前に `ID3D12Debug` でデバッグ レイヤーを有効にします。デバイスを作った後だと、遅すぎて有効になりません。

ゴールは、エラーなしで起動して終了することです。

## 段階 3：画面を塗りつぶす {#step3}

ここで、DX12 の骨格を一通り作ります。

1. RTV 用のディスクリプタ ヒープを作り、バック バッファごとに RTV を作る
2. コマンド アロケーターとコマンド リストを作る
3. フェンスを作る（GPU の完了を待つ）

毎フレームの流れは次のとおりです。

```text
アロケーターとリストをリセットする
バリア：バック バッファを Present → RenderTarget にする
RTV を設定して、クリアする
バリア：バック バッファを RenderTarget → Present に戻す
リストを閉じて、キューに投げる（ExecuteCommandLists）
Present
フェンスで、GPU の完了を待つ
```

バリアを抜くと、デバッグ レイヤーが「リソースの状態が違う」と教えてくれます。ゴールは、単色の画面です。

最初は、フレームごとに GPU の完了を待ってよいです（遅いですが、単純です）。段階 6 で、待たずに重ねる形にします。

## 段階 4：三角形 {#step4}

必要な部品が一気に増える、最初の山です。

1. 頂点データをアップロード ヒープ上のバッファに書く（[Upload Buffer](upload-buffer.md)）。頂点バッファ ビューで、GPU に場所と大きさを教える
2. ルート シグネチャを作る（今は、パラメーターなしの空でよい）
3. HLSL をコンパイルする（DXC）
4. PSO を作る。シェーダー、入力レイアウト、ラスタライザー、ブレンド、ルート シグネチャ、レンダー ターゲットの形式を 1 つにまとめる
5. コマンド リストに PSO、ルート シグネチャ、ビューポート、シザー矩形、頂点バッファ、トポロジを設定して `DrawInstanced`

DX12 の PSO は、ほとんどのステートをまとめて作るので、作成時に設定を間違えるとエラーになります。このサイトの規約は、反時計回りが表なので、ラスタライザーの `FrontCounterClockwise` を `TRUE` にします。

ビューポートとシザー矩形は、コマンド リストを `Reset` するたびに設定し直します。忘れると、何も描かれません。

## 段階 5：回す {#step5}

回転行列を定数バッファで渡します。定数バッファは、256 バイトの境界に合わせた大きさで作り、アップロード ヒープに置いて、毎フレーム `memcpy` で更新します。ルート シグネチャにルート定数バッファ ビュー（CBV）のパラメーターを追加します。

行列は SimpleMath で作ります。行ベクトル方式で、`world * view * proj` と、左から右に掛けます。HLSL の `cbuffer` には `row_major float4x4` と書いて、メモリの並びを合わせます。

## 段階 6：フレームを重ねる {#step6}

段階 3 では、フレームごとに GPU を待っていました。待つ間、CPU は何もしないので、非効率です。バック バッファの数（2〜3）に合わせて、<strong>フレームごとのアロケーター、定数バッファ、フェンス値を持ち</strong>、GPU が使い終わったフレームのものだけを再利用します。

自分の番のフレームの完了だけを待てばよく、1 フレーム先まで CPU が進めます。詳しくは [Frame Resources](frame-resources.md) にあります。

## 段階 7：立方体と深度 {#step7}

深度バッファは、`D32_FLOAT` のテクスチャで、DSV 用のヒープに DSV を作ります。PSO に深度ステートと DSV の形式を指定し、描画の前に `ClearDepthStencilView` で 1.0 に戻します。

PSO の `DSVFormat` を設定し忘れると、PSO の作成は成功しても、実際の描画で深度が働きません。

立方体の頂点とインデックスは、8 頂点 36 インデックスで書けます。面の巻き順は、外から見て反時計回りです。

## 段階 8：テクスチャ {#step8}

テクスチャは、デフォルト ヒープに置き、アップロード ヒープ経由でコピーします。SRV 用のヒープを作り、SRV を作って、ルート シグネチャのディスクリプタ テーブルから参照します。サンプラーは、静的サンプラーにすると、ヒープを作る手間を省けます。詳しくは [Texture Upload](texture-upload.md) にあります。

## この先 {#next}

立方体にテクスチャが貼れたら、DX12 の基本の部品が一巡したことになります。次は、必要なものを選びます。

- コンピュート シェーダー：[Compute Shader (D3D12)](compute-shader.md)
- 時間の計測：[GPU Queries and Timing (D3D12)](query-timing.md)
- 環境を作る補助関数：[Helper Functions](util.md)

## これだけ覚える {#summary}

- 段階 4 の三角形までが、最初の山。その前の段階を飛ばさない
- 状態の切り替えは、バリア。デバッグ レイヤーが教えてくれる
- ビューポートとシザー矩形は、リセットのたびに設定し直す

## 関連ページ

- [DirectX 12](index.md)
- [Drawing a Triangle (D3D12)](triangle.md)
- [GPU デバッグの流れ](../../vs/gpu-debug.md)
