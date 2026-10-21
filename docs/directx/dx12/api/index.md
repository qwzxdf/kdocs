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
