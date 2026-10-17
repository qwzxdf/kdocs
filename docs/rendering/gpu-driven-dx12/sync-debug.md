---
title: 同期とデバッグ
tags:
  - 描画最適化
---

# 同期とデバッグ

GPU Driven は、<strong>「GPU が書いたものを、GPU が読む」</strong>処理の連続です。**D3D12 は、リソースの状態遷移・フェンス・メモリの寿命をアプリが管理**するので**ここを間違えると描画が欠ける・たまに壊れる・デバイスが消える**といった、**再現しにくい不具合**になります。このページでは、**フレームごとのバリアの全体像・フレーム リングとフェンス・デバッグ レイヤーと GPU ベース検証・PIX・統計の読み戻し・典型的な事故とチェックリスト**を、**実コード**で説明します。

!!! tip "ポイント"
    - <strong>GPU が書く → GPU が読む</strong>の<strong>間には必ずバリア</strong>。<strong>UAV 書き込み → INDIRECT_ARGUMENT</strong> は<strong>状態遷移</strong>。
    - <strong>フレーム リング</strong>：<strong>フレーム数ぶんのアップロード領域・フェンス値</strong>。<strong>GPU が使い終わってから再利用</strong>。
    - <strong>デバッグ レイヤー ＋ GPU ベース検証</strong>を<strong>開発中は常に ON</strong>。<strong>状態の食い違いをメッセージで教えてくれる</strong>。
    - <strong>PIX</strong>で<strong>バッファの中身（カリング結果・カウンタ）</strong>を<strong>直接見る</strong>。
    - <strong>統計は数フレーム遅れて読み戻す</strong>（<strong>即座に待たない</strong>）。
    - <strong>典型的な事故をチェックリストにして</strong>、<strong>順に潰す</strong>。

## 1 フレームのバリア一覧

**GPU Driven の 1 フレーム**で、**各リソースがどの状態を行き来するか**を、**表にします**。

| リソース | 状態の遷移 |
| --- | --- |
| **インスタンス バッファ** | `SRV` → `COPY_DEST`（更新）→ `SRV` |
| **カウント バッファ** | `INDIRECT_ARGUMENT` → `COPY_DEST`（ゼロ コピー）→ `UNORDERED_ACCESS`（カリング）→ `INDIRECT_ARGUMENT`（描画） |
| **コマンド バッファ** | `INDIRECT_ARGUMENT` → `UNORDERED_ACCESS`（カリング）→ `INDIRECT_ARGUMENT`（描画） |
| **可視フラグ バッファ** | **常に `UNORDERED_ACCESS`**（CS だけが読み書き）。**同じバッファを連続する 2 つのディスパッチが触る間は、UAV バリア** |
| **深度バッファ** | `DEPTH_WRITE`（描画）→ `NON_PIXEL_SHADER_RESOURCE`（Hi-Z 構築）→ `DEPTH_WRITE`（2 パス目の描画） |
| **Hi-Z テクスチャ** | `NON_PIXEL_SHADER_RESOURCE` → `UNORDERED_ACCESS`（構築。ミップ間は UAV バリア）→ `NON_PIXEL_SHADER_RESOURCE`（判定） |
| **レンダー ターゲット** | 通常どおり（`RENDER_TARGET` ↔ `PRESENT` など） |

### 状態の追跡

**手動で追跡**すると**間違えやすい**ので、**リソースが自分の現在の状態を持つ**ラッパーを作ります。

```cpp
class TrackedResource {
 public:
  TrackedResource(ComPtr<ID3D12Resource> resource, D3D12_RESOURCE_STATES initial_state)
      : resource_(std::move(resource)), state_(initial_state) {}

  void TransitionTo(ID3D12GraphicsCommandList* list, D3D12_RESOURCE_STATES new_state) {
    if (state_ == new_state) return;
    CD3DX12_RESOURCE_BARRIER barrier =
        CD3DX12_RESOURCE_BARRIER::Transition(resource_.Get(), state_, new_state);
    list->ResourceBarrier(1, &barrier);
    state_ = new_state;
  }

  ID3D12Resource* Get() const { return resource_.Get(); }
  D3D12_RESOURCE_STATES state() const { return state_; }

 private:
  ComPtr<ID3D12Resource> resource_;
  D3D12_RESOURCE_STATES state_;
};
```

| 点 | 説明 |
| --- | --- |
| **`state_` の保持** | <strong>「今、どの状態か」</strong>を**ソフトウェアで管理**。**遷移の元の状態を書き間違えない** |
| **同じ状態なら、バリアを出さない** | **無駄なバリアを避ける** |
| **注意** | **コマンド リストの記録順 ＝ 実行順**を**前提**にした**単純な追跡**。**複数のコマンド リストを並列に記録**する場合は、**状態の追跡を別途設計**する（**遷移の「最初の状態」を実行時に解決する方式**） |

### バリアをまとめる

**`ResourceBarrier`** は、**複数のバリアを、1 回の呼び出しにまとめられます**。**バリアごとに GPU がパイプラインを待つ**ので、**まとめるほうが効率的**です（[GPU プロファイラの読み方](../tools.md)）。

```cpp
CD3DX12_RESOURCE_BARRIER barriers[2] = {
    CD3DX12_RESOURCE_BARRIER::Transition(a, before_a, after_a),
    CD3DX12_RESOURCE_BARRIER::Transition(b, before_b, after_b),
};
list->ResourceBarrier(_countof(barriers), barriers);
```

## UAV バリアと状態遷移の違い

| 種類 | 用途 |
| --- | --- |
| <strong>状態遷移バリア（Transition）</strong> | **リソースの「使い方」が変わる**とき（UAV → INDIRECT_ARGUMENT など） |
| **UAV バリア** | **同じ UAV 状態のまま、前の書き込みを次の読み書きの前に完了させる**（**ディスパッチ同士の順序保証**） |

**UAV で書いたバッファを、別のディスパッチが UAV で読む**場合は、**UAV バリア**です。**UAV で書いたバッファを、ExecuteIndirect が読む**場合は、<strong>状態遷移（UAV → INDIRECT_ARGUMENT）</strong>です。

!!! note "Enhanced Barriers"
    <strong>新しい API「Enhanced Barriers」</strong>（**`ID3D12GraphicsCommandList7::Barrier`**、Agility SDK）は、**同期点・アクセス・レイアウトを細かく指定**でき、**従来の状態遷移より、柔軟で効率的**です。**新規に書くなら、検討する価値があります**が、**このパートは広く使われている従来のバリア**で書いています。

## フレーム リングとフェンス

**CPU は GPU より先に進み**、**数フレーム先のコマンドを積みます**。**GPU がまだ使っているリソース**（**アップロード バッファ・コマンド アロケータ**）を、**CPU が上書き**しないように、**フェンス**で**同期**します。

```cpp
void Renderer::WaitForFrame(uint32_t frame_index) {
  FrameResources& frame = frames_[frame_index];
  if (fence_->GetCompletedValue() < frame.fence_value) {
    ThrowIfFailed(fence_->SetEventOnCompletion(frame.fence_value, fence_event_));
    WaitForSingleObject(fence_event_, INFINITE);
  }
}

void Renderer::EndFrame() {
  const uint64_t signal_value = ++next_fence_value_;
  ThrowIfFailed(command_queue_->Signal(fence_.Get(), signal_value));
  frames_[frame_index_].fence_value = signal_value;

  frame_index_ = (frame_index_ + 1) % kFrameCount;
  WaitForFrame(frame_index_);

  bindless_heap_.CollectGarbage(fence_->GetCompletedValue());
}
```

| 点 | 説明 |
| --- | --- |
| **`fence_value`** | **そのフレームのコマンドが、完了したときの値** |
| **`WaitForFrame`** | **これから使うフレームの、前回のコマンドが完了するまで待つ** |
| **`SetEventOnCompletion`** | **指定の値に達したら、イベントを立てる**。**`WaitForSingleObject` で待つ** |
| **`CollectGarbage`** | **遅延解放した記述子**を**完了済みのフェンス値**で**回収**（[ビンドレス](bindless.md)） |
| **フレーム数 `kFrameCount`** | **2〜3**。**多いほど CPU/GPU が並列**に動くが、**入力の遅延が増える** |

### コマンド アロケータ

**フレームごとにコマンド アロケータを持ち**、**そのフレームの GPU 実行が終わってから `Reset`** します。

```cpp
ThrowIfFailed(frames_[frame_index_].allocator->Reset());
ThrowIfFailed(command_list_->Reset(frames_[frame_index_].allocator.Get(), nullptr));
```

**GPU がまだ実行している**アロケータを **`Reset` すると、未定義動作**です。**`WaitForFrame` の後**に**呼びます**。

## デバッグ レイヤーと GPU ベース検証

**開発中はデバッグ レイヤーを必ず有効にします**。**状態遷移の誤り・リソースの不正な使用**を、**メッセージで報告**してくれます。

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug> debug_controller;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug_controller)))) {
  debug_controller->EnableDebugLayer();

  ComPtr<ID3D12Debug1> debug_controller1;
  if (SUCCEEDED(debug_controller.As(&debug_controller1))) {
    debug_controller1->SetEnableGPUBasedValidation(TRUE);
  }
}
#endif
```

| 機能 | 内容 |
| --- | --- |
| **デバッグ レイヤー** | **API の使い方の誤り**（状態の食い違い・解放済みリソース・不正なパラメータ）を**検出** |
| <strong>GPU ベース検証（GBV）</strong> | **シェーダー実行中のリソース アクセス**を**検証**（**未初期化の記述子・状態の誤り・範囲外**）。**非常に遅い**ので**問題が出たときに有効化**する |
| **`ID3D12InfoQueue`** | **エラーでブレークポイント**を**かける**設定ができる |

```cpp
ComPtr<ID3D12InfoQueue> info_queue;
if (SUCCEEDED(device_.As(&info_queue))) {
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
}
```

**ExecuteIndirect 関連**では、**引数バッファの状態が `INDIRECT_ARGUMENT` でない**・**カウント バッファの状態が違う**といった**エラー**を**検出**します。

### DRED（デバイス消失の原因追跡）

<strong>GPU がクラッシュ（デバイス消失）</strong>したとき、**DRED**（Device Removed Extended Data）が、**どのコマンドで落ちたか**を**教えます**。

```cpp
ComPtr<ID3D12DeviceRemovedExtendedDataSettings> dred_settings;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&dred_settings)))) {
  dred_settings->SetAutoBreadcrumbsEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);
  dred_settings->SetPageFaultEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);
}
```

**GPU Driven は、シェーダーが GPU メモリを自由に読み書きする**ので、**範囲外アクセスでデバイスが消える**ことがあります。**DRED のページ フォルト情報**が、**原因のリソース**を**絞る**のに**役立ちます**。

## PIX でバッファを見る

**PIX for Windows**で、**フレームをキャプチャ**し、**各ディスパッチ・ドローの前後**の**バッファの中身**を**確認**できます。

| 見るもの | 確認すること |
| --- | --- |
| **カウント バッファ** | **カリング後の個数**が**想定どおりか**（0 ばかり・上限に張り付く） |
| **コマンド バッファ** | **`IndirectCommand` の中身**（`instance_index`・`index_count`・`start_index`）が**妥当か** |
| **インスタンス バッファ** | **アップロードしたデータ**が、**化けていないか** |
| **Hi-Z** | **ミップが正しく縮小されているか**（画像として見る） |
| **ExecuteIndirect** | **PIX は間接描画の個々のコマンドに展開**して、**表示**する |
| **GPU タイミング** | **カリング・Hi-Z・描画**の**各パスの時間** |

**デバッグ用のマーカー**を**付ける**と、**PIX のタイムラインが読みやすく**なります。

```cpp
PIXBeginEvent(list, PIX_COLOR(0, 160, 0), L"GPU Culling");
RecordCull(list, constants, address);
PIXEndEvent(list);
```

## 統計の読み戻し

**カウント バッファをリードバック ヒープへコピー**して、**CPU で読めば**、<strong>「実際に描いた数」</strong>が**分かります**。**即座に待つと、GPU/CPU の並列性を壊す**ので、**数フレーム遅れて読みます**。

```cpp
void Renderer::CreateReadback() {
  CD3DX12_HEAP_PROPERTIES heap_properties(D3D12_HEAP_TYPE_READBACK);
  CD3DX12_RESOURCE_DESC desc =
      CD3DX12_RESOURCE_DESC::Buffer(sizeof(uint32_t) * kBucketCount);
  for (FrameResources& frame : frames_) {
    ThrowIfFailed(device_->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                   D3D12_RESOURCE_STATE_COPY_DEST, nullptr,
                                                   IID_PPV_ARGS(&frame.count_readback)));
  }
}

std::array<uint32_t, kBucketCount> Renderer::ReadCounts(uint32_t frame_index) {
  std::array<uint32_t, kBucketCount> counts = {};
  void* mapped = nullptr;
  CD3DX12_RANGE read_range(0, sizeof(counts));
  ThrowIfFailed(frames_[frame_index].count_readback->Map(0, &read_range, &mapped));
  std::memcpy(counts.data(), mapped, sizeof(counts));
  CD3DX12_RANGE written_range(0, 0);
  frames_[frame_index].count_readback->Unmap(0, &written_range);
  return counts;
}
```

| 点 | 説明 |
| --- | --- |
| **リードバック ヒープ** | **GPU が書き、CPU が読む**ヒープ。**初期状態は `COPY_DEST`** |
| **フレームごとに持つ** | **フェンス完了後に読む**ので、**フレームごとに別バッファ** |
| **`Map` の範囲** | **読む範囲を指定**。<strong>`Unmap` では、書いていない（空の範囲）</strong> |
| **読むタイミング** | <strong>`WaitForFrame` の後（そのフレームが完了した後）</strong>。**`kFrameCount - 1` フレーム前の結果** |

## 典型的な事故

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| **描画がたまに欠ける** | **UAV → INDIRECT_ARGUMENT の遷移がない** | **遷移を入れる**。**デバッグ レイヤーで確認** |
| **フレームごとにカウントが増え続ける** | **カウンタをリセットしていない** | **毎フレーム、ゼロ コピー** |
| **何も描かれない** | **カウント 0**・**バケットの PSO が違う**・**コマンド シグネチャの不一致** | **PIX でカウント・コマンドの中身を確認** |
| **特定のオブジェクトだけ消える** | **境界球が小さい**・**平面の符号が逆**・**D3D の近平面の式** | **カリングを一時的に無効にして比較** |
| <strong>デバイス消失（DXGI_ERROR_DEVICE_REMOVED）</strong> | **シェーダーの範囲外アクセス**・**未初期化の記述子**・**アロケータの早すぎる Reset** | **DRED・GPU ベース検証** |
| **テクスチャが違う物になる** | **記述子の再利用が早すぎる**・**`NonUniformResourceIndex` の欠落** | **遅延解放**・**非一様インデックス** |
| **1 フレーム遅れで物が出る・消える** | **可視フラグの更新順序**・**フェンスの待ち** | **2 パスの流れを見直す** |
| **GPU 時間が長い** | **ミップごとのバリア**・**過剰な UAV バリア**・**原子操作の競合** | **PIX のタイムライン**・**SPD・ウェーブ集約** |
| **入力が遅れて感じる** | **`kFrameCount` が大きい** | **2 に減らす・待ちの設計** |

## 開発の進め方

| 順序 | 内容 |
| --- | --- |
| **① まずカリング無しで** | **全インスタンスを、ExecuteIndirect で描く**（**コマンド生成だけ**確認） |
| **② 視錐台カリングを追加** | **PIX でカウントを確認**。**意図的にカメラを動かして検証** |
| **③ ビンドレス** | **テクスチャが正しく引かれるか** |
| **④ バケット** | **PSO ごとに分けて、描画** |
| **⑤ Hi-Z・2 パス** | **Hi-Z の画像をデバッグ表示**。**カリングされた数を統計表示** |
| **⑥ メッシュレット** | **対応 GPU で**。**フォールバック経路を残す** |
| **常時** | **デバッグ レイヤーを ON**。**PIX でフレームを時々キャプチャ** |

**最初から全部を作る**と**不具合の原因を特定できません**。**段階的に毎回「描けている」ことを確認**します。

## チェックリスト

| 確認 | 内容 |
| --- | --- |
| ☐ | **`IndirectCommand` のサイズが `ByteStride` と一致**し、**HLSL の構造体と並びが同じ** |
| ☐ | **カウンタを毎フレームリセット**している |
| ☐ | **カリング書き込み後、UAV → INDIRECT_ARGUMENT** の**遷移**がある |
| ☐ | **バケットごとの領域・カウンタ**が**重ならない**。**上限超えは書かない** |
| ☐ | **ExecuteIndirect の後、必要なルート引数を再設定**している |
| ☐ | **ビンドレスで、`NonUniformResourceIndex` を付けている** |
| ☐ | **記述子・リソースの解放は、フェンス完了後** |
| ☐ | **アップロード バッファは、フレーム数ぶん**ある |
| ☐ | **デバッグ レイヤーでエラー・警告が 0** |
| ☐ | **メッシュ シェーダー非対応 GPU へのフォールバック**がある |

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>GPU が書き、GPU が読む</strong>間には<strong>バリア</strong>。<strong>UAV → INDIRECT_ARGUMENT は状態遷移</strong>、<strong>ディスパッチ同士は UAV バリア</strong>
    - [x] <strong>フレーム リング ＋ フェンス</strong>で、<strong>GPU が使い終わってから、CPU が再利用</strong>
    - [x] <strong>開発中は、デバッグ レイヤー・GPU ベース検証・DRED を ON</strong>
    - [x] <strong>PIX で、カウント・コマンド・Hi-Z の中身</strong>を<strong>直接見る</strong>
    - [x] <strong>段階的に作り</strong>、<strong>典型的な事故のチェックリスト</strong>で<strong>潰す</strong>

## 参考

- Microsoft, "Using Resource Barriers to Synchronize Resource States in Direct3D 12"
- Microsoft, "Using D3D12 Debug Layer and GPU-Based Validation"
- Microsoft, "Use DRED to diagnose GPU faults"
- Microsoft, "PIX on Windows"
- Microsoft, "Enhanced Barriers"（DirectX-Specs）

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [シーン データ](scene-data.md)
- [カリング](culling.md)
- [ExecuteIndirect](execute-indirect.md)
- [Hi-Z と 2 パス](hiz-two-pass.md)
- [プロファイリング ツール](../tools.md)
