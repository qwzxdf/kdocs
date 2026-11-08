---
title: Synchronization and Debugging
tags:
  - 描画最適化
---

# Synchronization and Debugging

GPU Driven は <strong>「GPU が書いたものを GPU が読む」</strong>処理の連続です。D3D12 はリソースの状態遷移・フェンス・メモリの寿命をアプリが管理するのでここを間違えると描画が欠ける・たまに壊れる・デバイスが消えるといった、再現しにくい不具合になります。このページではフレームごとのバリアの全体像・フレーム リングとフェンス・デバッグ レイヤーと GPU ベース検証・PIX・統計の読み戻し・典型的な事故とチェックリストを実コードで説明します。

!!! tip "ポイント"
    - <strong>GPU が書く → GPU が読む</strong>の<strong>間には必ずバリア</strong>。UAV 書き込み → INDIRECT_ARGUMENT は状態遷移。
    - フレーム リング：フレーム数ぶんのアップロード領域・フェンス値。GPU が使い終わってから再利用。
    - デバッグ レイヤー ＋ GPU ベース検証を開発中は常に ON。状態の食い違いをメッセージで教えてくれる。
    - PIXでバッファの中身（カリング結果・カウンタ）を直接見る。
    - 統計は数フレーム遅れて読み戻す（即座に待たない）。
    - 典型的な事故をチェックリストにして、順に潰す。

!!! info "このページを読む前に"
    - [GPU Driven Rendering](../gpu-driven.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](../../optimization/bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 1 フレームのバリア一覧

**GPU Driven の 1 フレーム**で、各リソースがどの状態を行き来するかを表にします。

- インスタンス バッファ: `SRV` → `COPY_DEST`（更新）→ `SRV`
- カウント バッファ: `INDIRECT_ARGUMENT` → `COPY_DEST`（ゼロ コピー）→ `UNORDERED_ACCESS`（カリング）→ `INDIRECT_ARGUMENT`（描画）
- コマンド バッファ: `INDIRECT_ARGUMENT` → `UNORDERED_ACCESS`（カリング）→ `INDIRECT_ARGUMENT`（描画）
- 可視フラグ バッファ: 常に `UNORDERED_ACCESS`（CS だけが読み書き）。同じバッファを連続する 2 つのディスパッチが触る間は、UAV バリア
- 深度バッファ: `DEPTH_WRITE`（描画）→ `NON_PIXEL_SHADER_RESOURCE`（Hi-Z 構築）→ `DEPTH_WRITE`（2 パス目の描画）
- Hi-Z テクスチャ: `NON_PIXEL_SHADER_RESOURCE` → `UNORDERED_ACCESS`（構築。ミップ間は UAV バリア）→ `NON_PIXEL_SHADER_RESOURCE`（判定）
- レンダー ターゲット: 通常どおり（`RENDER_TARGET` ↔ `PRESENT` など）

### 状態の追跡

手動で追跡すると間違えやすいので、リソースが自分の現在の状態を持つラッパーを作ります。

```cpp
class TrackedResource {                                       // リソースと、その「今の状態」をセットで持つ入れ物
 public:
  TrackedResource(ComPtr<ID3D12Resource> resource, D3D12_RESOURCE_STATES initial_state)
      : resource_(std::move(resource)), state_(initial_state) {}   // 作成時の状態を記録する

  void TransitionTo(ID3D12GraphicsCommandList* list, D3D12_RESOURCE_STATES new_state) {
    if (state_ == new_state) return;                          // すでにその状態なら、バリアを出さない
    D3D12_RESOURCE_BARRIER barrier =
        MakeTransitionBarrier(resource_.Get(), state_, new_state);   // 今の状態 → 新しい状態
    list->ResourceBarrier(1, &barrier);
    state_ = new_state;                                       // 記録を更新する
  }

  ID3D12Resource* Get() const { return resource_.Get(); }
  D3D12_RESOURCE_STATES state() const { return state_; }

 private:
  ComPtr<ID3D12Resource> resource_;
  D3D12_RESOURCE_STATES state_;                               // 今の状態(コマンド リストに積んだ順の想定)
};
```

`TrackedResource` は DX12 の「遷移バリアの `StateBefore` を呼ぶ側が正しく書く」という約束事を、ラッパーに預けるための道具です。`StateBefore` が実際の状態と違うとデバッグ レイヤーがエラーを出し、製品版では未定義の結果になります。ラッパーは今の状態を覚えているので、`TransitionTo(list, 新しい状態)` と書くだけで正しい遷移が出ます。同じ状態への遷移は何もしません。

- `state_` の保持: 「今、どの状態か」をソフトウェアで管理。遷移の元の状態を書き間違えない
- 同じ状態ならバリアを出さない: 無駄なバリアを避ける
- 注意: コマンド リストの記録順 ＝ 実行順を前提にした単純な追跡。複数のコマンド リストを並列に記録する場合は、状態の追跡を別途設計する（遷移の「最初の状態」を実行時に解決する方式）

### バリアをまとめる

`ResourceBarrier` は複数のバリアを 1 回の呼び出しにまとめられます。バリアごとに GPU がパイプラインを待つので、まとめるほうが速く済みます（[GPU プロファイラの読み方](../../optimization/tools.md)）。

```cpp
D3D12_RESOURCE_BARRIER barriers[2] = {
    MakeTransitionBarrier(a, before_a, after_a),              // リソース a の遷移
    MakeTransitionBarrier(b, before_b, after_b),              // リソース b の遷移
};
list->ResourceBarrier(_countof(barriers), barriers);          // まとめて 1 回で送る
```

## UAV バリアと状態遷移の違い

- <strong>状態遷移バリア（Transition）</strong>: リソースの「使い方」が変わるとき（UAV → INDIRECT_ARGUMENT など）
- UAV バリア: 同じ UAV 状態のまま前の書き込みを次の読み書きの前に完了させる（ディスパッチ同士の順序保証）

UAV で書いたバッファを別のディスパッチが UAV で読む場合は、UAV バリアです。UAV で書いたバッファを ExecuteIndirect が読む場合は、状態遷移（UAV → INDIRECT_ARGUMENT）です。

!!! note "Enhanced Barriers"
    新しい API「Enhanced Barriers」（`ID3D12GraphicsCommandList7::Barrier`、Agility SDK）は同期点・アクセス・レイアウトを細かく指定でき従来の状態遷移より柔軟で、無駄が少なくなります。新規に書くなら検討する価値がありますが、このパートは広く使われている従来のバリアで書いています。

## フレーム リングとフェンス

**CPU は GPU より先に進み**、数フレーム先のコマンドを積みます。GPU がまだ使っているリソース（アップロード バッファ・コマンド アロケータ）を CPU が上書きしないように、フェンスで同期します。

```cpp
void Renderer::WaitForFrame(uint32_t frame_index) {
  FrameResources& frame = frames_[frame_index];                // これから使うフレームの記録
  if (fence_->GetCompletedValue() < frame.fence_value) {       // GPU がそのフレームをまだ終えていないなら
    ThrowIfFailed(fence_->SetEventOnCompletion(frame.fence_value, fence_event_));   // 値に達したらイベントを立てる
    WaitForSingleObject(fence_event_, INFINITE);               // 立つまで待つ
  }
}

void Renderer::EndFrame() {
  const uint64_t signal_value = ++next_fence_value_;           // 新しいフェンス値
  ThrowIfFailed(command_queue_->Signal(fence_.Get(), signal_value));   // キューの最後に「ここまで終わったら signal_value」を積む
  frames_[frame_index_].fence_value = signal_value;            // このフレームの完了の目印として覚える

  frame_index_ = (frame_index_ + 1) % kFrameCount;             // 次のフレームの棚に進む
  WaitForFrame(frame_index_);                                  // その棚を使っていた古いフレームの完了を待つ

  bindless_heap_.CollectGarbage(fence_->GetCompletedValue());  // 完了済みの値までに解放予約された記述子を再利用に回す
}
```

`EndFrame` は 4 つの仕事をします。①フェンス値を 1 増やして、キューの最後にその値を `Signal` する命令を積みます。②その値をこのフレームの完了の目印として覚えます。③次のフレームの棚に進みます。④その棚を使っていた古いフレームが GPU で終わるまで待ちます。待ちが発生するのは CPU が GPU に `kFrameCount` フレーム以上先行したときだけです。3 フレームのリングなら GPU が 2 フレーム遅れている間は待たずに進めます。

- `fence_value`: そのフレームのコマンドが完了したときの値
- `WaitForFrame`: これから使うフレームの前回のコマンドが完了するまで待つ
- `SetEventOnCompletion`: 指定の値に達したら、イベントを立てる。`WaitForSingleObject` で待つ
- `CollectGarbage`: 遅延解放した記述子を完了済みのフェンス値で回収（[バインドレス](bindless.md)）
- フレーム数 `kFrameCount`: 2〜3。多いほど CPU/GPU が並列に動くが、入力の遅延が増える

### コマンド アロケータ

フレームごとにコマンド アロケータを持ちそのフレームの GPU 実行が終わってから `Reset` します。

```cpp
ThrowIfFailed(frames_[frame_index_].allocator->Reset());                                  // アロケータのメモリを再利用に戻す(GPU が使い終わっていること)
ThrowIfFailed(command_list_->Reset(frames_[frame_index_].allocator.Get(), nullptr));     // そのアロケータでコマンド リストの記録を始める
```

GPU がまだ実行しているアロケータを `Reset` すると、未定義動作です。`WaitForFrame` の後に呼びます。

## デバッグ レイヤーと GPU ベース検証

**開発中はデバッグ レイヤーを必ず有効にします**。状態遷移の誤り・リソースの不正な使用をメッセージで報告してくれます。

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug> debug_controller;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug_controller)))) {
  debug_controller->EnableDebugLayer();                        // API の使い方の誤りを報告させる(デバイス作成より前に呼ぶ)

  ComPtr<ID3D12Debug1> debug_controller1;
  if (SUCCEEDED(debug_controller.As(&debug_controller1))) {
    debug_controller1->SetEnableGPUBasedValidation(TRUE);      // シェーダー実行中のアクセスも検証する(非常に遅い)
  }
}
#endif
```

デバッグ レイヤーはデバイスを作る前に有効にします。後から有効にするとデバイスが作り直しになり既存のリソースが失われます。`SetBreakOnSeverity` を設定しておけばエラーの瞬間にデバッガーが止まるので、呼び出し履歴から原因の行がすぐ分かります。GPU ベース検証はシェーダーが読む記述子や状態まで追うので、数倍から数十倍遅くなります。普段は切っておき「デバイス消失の原因が分からない」ときだけ有効にします。

- デバッグ レイヤー: API の使い方の誤り（状態の食い違い・解放済みリソース・不正なパラメータ）を検出
- GPU ベース検証（GBV）: シェーダー実行中のリソース アクセスを検証（未初期化の記述子・状態の誤り・範囲外）。遅いので問題が出たときに有効化する
- `ID3D12InfoQueue`: エラーでブレークポイントをかける設定ができる

```cpp
ComPtr<ID3D12InfoQueue> info_queue;
if (SUCCEEDED(device_.As(&info_queue))) {
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);        // エラーが出た瞬間にデバッガーで止める
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);   // 破損級のメッセージでも止める
}
```

ExecuteIndirect 関連では、引数バッファの状態が `INDIRECT_ARGUMENT` でない・カウント バッファの状態が違うといったエラーを検出します。

### DRED（デバイス消失の原因追跡）

GPU がクラッシュ（デバイス消失）したとき DRED（Device Removed Extended Data）がどのコマンドで落ちたかを教えます。

```cpp
ComPtr<ID3D12DeviceRemovedExtendedDataSettings> dred_settings;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&dred_settings)))) {
  dred_settings->SetAutoBreadcrumbsEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);   // どのコマンドまで実行できたかの足跡(ブレッドクラム)を残す
  dred_settings->SetPageFaultEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);         // ページ フォルトしたアドレスと、近くのリソースを記録する
}
```

GPU Driven はシェーダーが GPU メモリを自由に読み書きするので、範囲外アクセスでデバイスが消えることがあります。DRED のページ フォルト情報が原因のリソースを絞るのに役立ちます。

## PIX でバッファを見る

**PIX for Windows**で、フレームをキャプチャし各ディスパッチ・ドローの前後のバッファの中身を確認できます。

- カウント バッファ: カリング後の個数が想定どおりか（0 ばかり・上限に張り付く）
- コマンド バッファ: `IndirectCommand` の中身（`instance_index`・`index_count`・`start_index`）が妥当か
- インスタンス バッファ: アップロードしたデータが化けていないか
- Hi-Z: ミップが正しく縮小されているか（画像として見る）
- ExecuteIndirect: PIX は間接描画の個々のコマンドに展開して、表示する
- GPU タイミング: カリング・Hi-Z・描画の各パスの時間

デバッグ用のマーカーを付けると、PIX のタイムラインが読みやすくなります。

```cpp
PIXBeginEvent(list, PIX_COLOR(0, 160, 0), L"GPU Culling");   // 緑色の「GPU Culling」という区間を始める
RecordCull(list, constants, address);                        // この区間の中身
PIXEndEvent(list);                                           // 区間を閉じる
```

## 統計の読み戻し

**カウント バッファをリードバック ヒープへコピー**して、CPU で読めば「実際に描いた数」が分かります。即座に待つと GPU/CPU の並列性を壊すので、数フレーム遅れて読みます。

```cpp
void Renderer::CreateReadback() {
  D3D12_HEAP_PROPERTIES heap_properties = MakeHeapProperties(D3D12_HEAP_TYPE_READBACK);   // GPU が書き、CPU が読むヒープ
  D3D12_RESOURCE_DESC desc = MakeBufferDesc(sizeof(uint32_t) * kBucketCount);             // バケットぶんのカウンタ
  for (FrameResources& frame : frames_) {                       // フレームごとに 1 つずつ
    ThrowIfFailed(device_->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                   D3D12_RESOURCE_STATE_COPY_DEST, nullptr,   // リードバックの初期状態はこれで固定
                                                   IID_PPV_ARGS(&frame.count_readback)));
  }
}

std::array<uint32_t, kBucketCount> Renderer::ReadCounts(uint32_t frame_index) {
  std::array<uint32_t, kBucketCount> counts = {};               // 結果
  void* mapped = nullptr;
  D3D12_RANGE read_range = {0, sizeof(counts)};                 // CPU が読む範囲
  ThrowIfFailed(frames_[frame_index].count_readback->Map(0, &read_range, &mapped));
  std::memcpy(counts.data(), mapped, sizeof(counts));           // GPU が書いた値をコピーして取り出す
  D3D12_RANGE written_range = {0, 0};                           // CPU は何も書いていない、という宣言
  frames_[frame_index].count_readback->Unmap(0, &written_range);
  return counts;
}
```

読み戻しは描画と同じフレームで待たずに数フレーム遅れで読むのが基本です。`RecordReadbackCounts`（[ExecuteIndirect](execute-indirect.md)）でコピーを積みそのフレームのフェンスが完了した後に `ReadCounts` で `Map` します。同じフレームで待つと GPU の完了まで CPU が止まり CPU と GPU の並列実行が失われます。

- リードバック ヒープ: GPU が書き CPU が読むヒープ。初期状態は `COPY_DEST`
- フレームごとに持つ: フェンス完了後に読むので、フレームごとに別バッファ
- `Map` の範囲: 読む範囲を指定。`Unmap` では書いていない（空の範囲）
- 読むタイミング: `WaitForFrame` の後（そのフレームが完了した後）。`kFrameCount - 1` フレーム前の結果

## 典型的な事故

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| **描画がたまに欠ける** | UAV → INDIRECT_ARGUMENT の遷移がない | 遷移を入れる。デバッグ レイヤーで確認 |
| フレームごとにカウントが増え続ける | カウンタをリセットしていない | 毎フレーム、ゼロ コピー |
| 何も描かれない | カウント 0・バケットの PSO が違う・コマンド シグネチャの不一致 | PIX でカウント・コマンドの中身を確認 |
| 特定のオブジェクトだけ消える | 境界球が小さい・平面の符号が逆・D3D の近平面の式 | カリングを一時的に無効にして比較 |
| デバイス消失（DXGI_ERROR_DEVICE_REMOVED） | シェーダーの範囲外アクセス・未初期化の記述子・アロケータの早すぎる Reset | DRED・GPU ベース検証 |
| テクスチャが違う物になる | 記述子の再利用が早すぎる・`NonUniformResourceIndex` の欠落 | 遅延解放・非一様インデックス |
| 1 フレーム遅れで物が出る・消える | 可視フラグの更新順序・フェンスの待ち | 2 パスの流れを見直す |
| GPU 時間が長い | ミップごとのバリア・過剰な UAV バリア・原子操作の競合 | PIX のタイムライン・SPD・ウェーブ集約 |
| 入力が遅れて感じる | `kFrameCount` が大きい | 2 に減らす・待ちの設計 |

## 開発の進め方

1. **① まずカリング無しで**: 全インスタンスを ExecuteIndirect で描く（コマンド生成だけ確認）
2. ② 視錐台カリングを追加: PIX でカウントを確認。意図的にカメラを動かして検証
3. ③ バインドレス: テクスチャが正しく引かれるか
4. ④ バケット: PSO ごとに分けて描画
5. ⑤ Hi-Z・2 パス: Hi-Z の画像をデバッグ表示。カリングされた数を統計表示
6. ⑥ メッシュレット: 対応 GPU で。フォールバック経路を残す
7. 常時: デバッグ レイヤーを ON。PIX でフレームを時々キャプチャ

最初から全部を作ると不具合の原因を特定できません。段階的に毎回「描けている」ことを確認します。

## チェックリスト

- ☐: **`IndirectCommand` のサイズが `ByteStride` と一致**し、HLSL の構造体と並びが同じ
- ☐: カウンタを毎フレームリセットしている
- ☐: カリング書き込み後、UAV → INDIRECT_ARGUMENT の遷移がある
- ☐: バケットごとの領域・カウンタが重ならない。上限超えは書かない
- ☐: ExecuteIndirect の後、必要なルート引数を再設定している
- ☐: バインドレスで `NonUniformResourceIndex` を付けている
- ☐: 記述子・リソースの解放はフェンス完了後
- ☐: アップロード バッファはフレーム数ぶんある
- ☐: デバッグ レイヤーでエラー・警告が 0
- ☐: メッシュ シェーダー非対応 GPU へのフォールバックがある

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU が書き GPU が読む間にはバリア。UAV → INDIRECT_ARGUMENT は状態遷移、ディスパッチ同士は UAV バリア
    - [x] フレーム リング ＋ フェンスで、GPU が使い終わってから CPU が再利用
    - [x] 開発中はデバッグ レイヤー・GPU ベース検証・DRED を ON
    - [x] PIX で、カウント・コマンド・Hi-Z の中身を直接見る
    - [x] 段階的に作り典型的な事故のチェックリストで潰す

## 参考

- Microsoft, "Using Resource Barriers to Synchronize Resource States in Direct3D 12"
- Microsoft, "Using D3D12 Debug Layer and GPU-Based Validation"
- Microsoft, "Use DRED to diagnose GPU faults"
- Microsoft, "PIX on Windows"
- Microsoft, "Enhanced Barriers"（DirectX-Specs）

## 関連ページ

- [GPU Driven (D3D12)](index.md)
- [シーン データ](scene-data.md)
- [カリング](culling.md)
- [ExecuteIndirect](execute-indirect.md)
- [Hi-Z と 2 パス](hiz-two-pass.md)
- [プロファイリング ツール](../../optimization/tools.md)
