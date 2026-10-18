---
title: Resource Barrier
tags:
  - DirectX
---

# Resource Barrier

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>リソース バリア</strong>はリソースの <strong>使い方（状態）を切り替える</strong>ときに GPU に伝える命令です。同じテクスチャを「描き込み先（RTV）」として、使った後、「読み取り（SRV）」として、使うとき GPU は書き込みの完了を待ちキャッシュを流し読み取り用にメモリの扱いを変える必要があります。D3D12 ではこれを <strong>アプリが、明示</strong>します。忘れると画面が乱れクラッシュし最もバグが、出やすい部分です。

!!! tip "ポイント"
    - 各リソースは常に <strong>ある状態</strong>（`RENDER_TARGET`、`PIXEL_SHADER_RESOURCE`、`COPY_DEST`…）にある。使い方を変える前に <strong>遷移バリア</strong>で状態を切り替える。
    - <strong>遷移バリア</strong>: 状態 A → B。<strong>UAV バリア</strong>: 同じ UAV への読み書きの順序づけ。<strong>エイリアシング バリア</strong>: メモリを共有するリソースの切り替え。
    - バック バッファは `PRESENT` ↔ `RENDER_TARGET`。
    - バリアは <strong>コマンド リストに記録</strong>する（GPU が実行時に、行う）。
    - まとめて 1 回の `ResourceBarrier` で複数を渡すと効率がよい。
    - デバッグ レイヤー（GPU ベース検証）が、バリアの間違いを教えてくれる。

## リソースの状態

リソースは作成時に <strong>初期状態</strong>を指定しその後、バリアで変えます。

| 状態（`D3D12_RESOURCE_STATE_*`） | 意味 |
| --- | --- |
| `COMMON` / `PRESENT` | 初期状態。画面表示（`PRESENT`）は `COMMON` と同じ値 |
| `RENDER_TARGET` | レンダー ターゲットとして、書き込む |
| `DEPTH_WRITE` | 深度を書き込む（深度テストと書き込み） |
| `DEPTH_READ` | 深度を読み取り専用で、テストする（読み取り専用の DSV） |
| `PIXEL_SHADER_RESOURCE` | ピクセル シェーダーで、読む（SRV） |
| `NON_PIXEL_SHADER_RESOURCE` | ピクセル以外（頂点、計算など）で読む |
| `UNORDERED_ACCESS` | UAV として読み書きする |
| `COPY_SOURCE` | コピー元 |
| `COPY_DEST` | コピー先 |
| `VERTEX_AND_CONSTANT_BUFFER` | 頂点バッファ、定数バッファとして読む |
| `INDEX_BUFFER` | インデックス バッファとして、読む |
| `INDIRECT_ARGUMENT` | 間接描画の引数 |
| `GENERIC_READ` | 読み取り用の状態の組み合わせ（アップロード ヒープの初期状態） |

状態は <strong>OR で組み合わせられる</strong>（読み取り系だけ）。`PIXEL_SHADER_RESOURCE | NON_PIXEL_SHADER_RESOURCE` は全シェーダーで読める状態です。書き込み系（`RENDER_TARGET`、`UNORDERED_ACCESS`、`COPY_DEST`）は <strong>単独</strong>です。

## 遷移バリア

```cpp
// レンダー ターゲットに描いたテクスチャを、次のパスで、読む前に、状態を、切り替える。
auto barrier = CD3DX12_RESOURCE_BARRIER::Transition(
    scene_texture.Get(),
    D3D12_RESOURCE_STATE_RENDER_TARGET,                      // 前の状態
    D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);             // 後の状態
command_list->ResourceBarrier(1, &barrier);
```

| 引数 | 内容 |
| --- | --- |
| リソース | 状態を変えるリソース |
| `StateBefore` | 今の状態（<strong>正確に</strong>、合っている必要） |
| `StateAfter` | 次の状態 |
| `Subresource` | サブリソース（ミップ・配列要素）。`D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES` で全部 |

`StateBefore` が実際の状態と違うとデバッグ レイヤーが、エラーを出します。リソースごとに「今の状態」を追跡する仕組み（自作）を持つのが、一般的です。

```cpp
// 簡単な、状態の追跡: リソースごとに、今の状態を、持って、遷移を、自動で、入れる。
struct TrackedResource {
  ComPtr<ID3D12Resource> resource;
  D3D12_RESOURCE_STATES state = D3D12_RESOURCE_STATE_COMMON;

  void TransitionTo(ID3D12GraphicsCommandList* list, D3D12_RESOURCE_STATES next) {
    if (state == next) return;                               // 同じなら、何もしない
    auto barrier = CD3DX12_RESOURCE_BARRIER::Transition(resource.Get(), state, next);
    list->ResourceBarrier(1, &barrier);
    state = next;
  }
};
```

## 典型的な遷移の流れ

| 場面 | 遷移 |
| --- | --- |
| バック バッファ | `PRESENT` → `RENDER_TARGET`（描く前）→ `PRESENT`（描いた後） |
| シーン色（描いて次のパスで、読む） | `RENDER_TARGET` → `PIXEL_SHADER_RESOURCE` |
| G バッファ | `RENDER_TARGET` → `PIXEL_SHADER_RESOURCE`（ライティング）→ `RENDER_TARGET`（次のフレーム） |
| 深度バッファ（描いて AO で、読む） | `DEPTH_WRITE` → `NON_PIXEL_SHADER_RESOURCE`（計算シェーダー）または `PIXEL_SHADER_RESOURCE` |
| アップロード（頂点バッファ） | `COPY_DEST`（コピー）→ `VERTEX_AND_CONSTANT_BUFFER` |
| 計算シェーダーの出力 | `UNORDERED_ACCESS` → `PIXEL_SHADER_RESOURCE`（次の描画で、読む） |
| アップロード ヒープ | 常に `GENERIC_READ`（遷移しない） |

## UAV バリア

同じ UAV に複数の `Dispatch` が続けて、書き込み・読み込みをするとき <strong>前の `Dispatch` の書き込みが終わるのを待たせる</strong>ために、UAV バリアを入れます。状態は `UNORDERED_ACCESS` のまま変わりません。

```cpp
// 計算シェーダー A が、書いた UAV を、計算シェーダー B が、読む前に。
auto uav_barrier = CD3DX12_RESOURCE_BARRIER::UAV(uav_resource.Get());
command_list->ResourceBarrier(1, &uav_barrier);
command_list->Dispatch(...);                                 // B
```

UAV バリアが無いと B が A の書き込み途中の値を読みます。FFT の段ごとの `Dispatch`、ヒストグラムの集計などで必須です（[Compute Shader](compute-shader.md)）。

## エイリアシング バリア

同じメモリを複数のリソースで、共有（エイリアス）して使い回すときリソース A から B へ切り替える合図です。メモリを節約する上級の技術（一時バッファを同じメモリに重ねる）で使います。

```cpp
auto aliasing = CD3DX12_RESOURCE_BARRIER::Aliasing(resource_a.Get(), resource_b.Get());
command_list->ResourceBarrier(1, &aliasing);
```

## まとめて渡す

```cpp
// 複数のバリアを、1 回の ResourceBarrier で、渡す（効率がよい）。
D3D12_RESOURCE_BARRIER barriers[] = {
    CD3DX12_RESOURCE_BARRIER::Transition(gbuffer_albedo.Get(), D3D12_RESOURCE_STATE_RENDER_TARGET,
                                         D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
    CD3DX12_RESOURCE_BARRIER::Transition(gbuffer_normal.Get(), D3D12_RESOURCE_STATE_RENDER_TARGET,
                                         D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
    CD3DX12_RESOURCE_BARRIER::Transition(depth.Get(), D3D12_RESOURCE_STATE_DEPTH_WRITE,
                                         D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
};
command_list->ResourceBarrier(ARRAYSIZE(barriers), barriers);
```

バリアは GPU に <strong>パイプラインの待ち（フラッシュ）</strong>を起こすことが、あります。1 つずつ何度も呼ぶよりまとめて、渡す方が GPU の待ちが減ります。<strong>不要なバリアを入れすぎる</strong>のも性能を落とします。

## 分割バリア

遷移の「開始」と「終了」を分けて、記録する `BEGIN_ONLY` / `END_ONLY` があります。開始から終了の間に他の仕事を挟むと GPU が遷移を裏で進められます。上級の最適化です。

## 拡張バリア

新しいバリア API（Enhanced Barriers、`ID3D12Device10`、`ID3D12GraphicsCommandList7`）は状態の代わりに <strong>「どの段が、どのアクセスを終えたか」</strong>で、記述します。より細かく制御できますが対応した環境が、必要です。

## 暗黙の状態遷移

特定の場面では状態が <strong>自動で、遷移</strong>します。

| 場面 | 内容 |
| --- | --- |
| `COMMON` からコピー・読み取り | `COMMON` のリソースは、コピー（`COPY_SOURCE`/`DEST`）や読み取りで暗黙に遷移（昇格）し実行後、`COMMON` に戻る（decay） |
| アップロード・リードバック ヒープ | 状態が、固定（`GENERIC_READ`、`COPY_DEST`）で遷移できない |

この暗黙の遷移に頼ると状態の追跡が、複雑になるので <strong>明示的に</strong>、遷移させるのが安全です。

## よくあるミス

??? failure "画面が乱れる、テクスチャがちらつくときどきクラッシュ"
    バリアが足りない（書いた後、読む前に遷移していない）、または `StateBefore` が実際の状態と違う。GPU ベース検証とデバッグ レイヤーで、検出する。

??? failure "計算シェーダーの連続した `Dispatch` で結果が不安定"
    UAV バリアを入れていない。前の `Dispatch` の書き込みが終わる前に次が、読んでいる。

??? failure "アップロード バッファを `COPY_DEST` に遷移しようとしてエラー"
    アップロード ヒープのリソースは `GENERIC_READ` で固定。遷移できない。コピー先は DEFAULT ヒープのリソース。

??? failure "バリアを入れすぎて遅い"
    1 つずつ毎回、遷移している。まとめて 1 回で渡す。状態の追跡で同じ状態への遷移を省く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バリア ＝ リソースの使い方（状態）を切り替える合図
    - [x] 遷移バリア: `Transition(resource, 前, 後)`。前の状態は正確に
    - [x] UAV バリア: 連続する、計算シェーダーの書き込みと読み込みの順序づけ
    - [x] バック バッファは、`PRESENT` ↔ `RENDER_TARGET`
    - [x] まとめて渡す。リソースの状態は追跡する
    - [x] GPU ベース検証で、バリアの間違いを見つける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Compute Shader](compute-shader.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: リソース バリア](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12)
