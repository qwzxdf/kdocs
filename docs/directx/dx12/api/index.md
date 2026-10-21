# API リファレンス

DirectX 12 の API をインターフェースや構造体ごとに引ける辞書です。手順を追って読む解説は上のページ（[DirectX 12 Guide](../index.md)）にあります。ここでは、メソッドや値を 1 つずつシグネチャ、引数、戻り値、落とし穴まで書きます。

コード ブロックの中の名前（`CreateCommittedResource` など）は、ここに載っているものならクリックでこのページの該当の節へ飛べます。

| ページ | 内容 |
| --- | --- |
| [ID3D12Device](id3d12device.md) | リソース、キュー、フェンス、ディスクリプタ、PSO を作るメソッド |
| [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) | バリア、クリア、描画の設定、描画、コピー、計測を記録するメソッド |
| [ID3D12CommandQueue](id3d12commandqueue.md) | 記録したリストを GPU に渡す。Signal と Wait |
| [ID3D12CommandAllocator](id3d12commandallocator.md) | 命令を置くメモリ。Reset のタイミング |
| [ID3D12Fence](id3d12fence.md) | CPU と GPU の同期。数字を進めて待つ |
| [ID3D12Resource](id3d12resource.md) | バッファとテクスチャ。Map、Unmap、GPU アドレス |
| [ID3D12DescriptorHeap](id3d12descriptorheap.md) | ディスクリプタの置き場と、先頭のハンドル |
| [ID3DBlob](id3dblob.md) | シェーダーのバイト列とエラー メッセージの入れ物 |
| [ID3D12Heap](id3d12heap.md) | リソースを置く GPU メモリのかたまり |
| [ID3D12PipelineState](id3d12pipelinestate.md) | シェーダーと固定機能をまとめた描画の設定 |
| [ID3D12RootSignature](id3d12rootsignature.md) | シェーダーの引数の型 |
| [ID3D12QueryHeap](id3d12queryheap.md) | タイムスタンプや統計の置き場 |
| [ID3D12PipelineLibrary](id3d12pipelinelibrary.md) | PSO のキャッシュ |
| [ID3D12Object](id3d12object.md) | 全インターフェース共通の SetName など |
| [IDXGIFactory](idxgifactory.md) | アダプターの列挙とスワップ チェーンの作成 |
| [IDXGIAdapter](idxgiadapter.md) | GPU の情報 |
| [IDXGISwapChain](idxgiswapchain.md) | バック バッファと Present |
| [D3D12SerializeRootSignature](d3d12serializerootsignature.md) | ルート シグネチャの記述をバイト列にする自由関数 |
| [Resource Structs](resource-structs.md) | `D3D12_HEAP_PROPERTIES`、`D3D12_RESOURCE_DESC` など |
| [View and Descriptor Structs](view-structs.md) | ビューとディスクリプタの `Desc` |
| [Pipeline State Structs](pipeline-structs.md) | PSO の `Desc` |
| [Root Signature Structs](root-signature-structs.md) | ルート シグネチャの `Desc` |
| [Copy and Barrier Structs](copy-barrier-structs.md) | コピーとバリアの構造体 |
| [Heap and Resource Enums](enum-heap-resource.md) | ヒープとリソースの列挙型と `Flags` |
| [Resource State Enums](enum-resource-state.md) | リソース状態とバリアの `Flags` |
| [Queue and Command Enums](enum-queue-command.md) | キューとコマンドの列挙型と `Flags` |
