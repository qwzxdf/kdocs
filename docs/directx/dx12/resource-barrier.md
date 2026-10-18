---
title: Resource Barrier
tags:
  - DirectX
---

# Resource Barrier

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>リソース バリア</strong>は、リソースの、<strong>使い方（状態）を、切り替える</strong>ときに、GPU に、伝える、命令です。同じテクスチャを、「描き込み先（RTV）」として、使った後、「読み取り（SRV）」として、使うとき、GPU は、書き込みの、完了を、待ち、キャッシュを、流し、読み取り用に、メモリの、扱いを、変える必要が、あります。D3D12 では、これを、<strong>アプリが、明示</strong>します。忘れると、画面が、乱れ、クラッシュし、最も、バグが、出やすい、部分です。

!!! tip "ポイント"
    - 各リソースは、常に、<strong>ある状態</strong>（`RENDER_TARGET`、`PIXEL_SHADER_RESOURCE`、`COPY_DEST`…）に、ある。使い方を、変える前に、<strong>遷移バリア</strong>で、状態を、切り替える。
    - <strong>遷移バリア</strong>: 状態 A → B。<strong>UAV バリア</strong>: 同じ UAV への、読み書きの、順序づけ。<strong>エイリアシング バリア</strong>: メモリを、共有する、リソースの、切り替え。
    - バック バッファは、`PRESENT` ↔ `RENDER_TARGET`。
    - バリアは、<strong>コマンド リストに、記録</strong>する（GPU が、実行時に、行う）。
    - まとめて、1 回の `ResourceBarrier` で、複数を、渡すと、効率がよい。
    - デバッグ レイヤー（GPU ベース検証）が、バリアの、間違いを、教えてくれる。

## リソースの、状態

リソースは、作成時に、<strong>初期状態</strong>を、指定し、その後、バリアで、変えます。

| 状態（`D3D12_RESOURCE_STATE_*`） | 意味 |
| --- | --- |
| `COMMON` / `PRESENT` | 初期状態。画面表示（`PRESENT`）は、`COMMON` と、同じ値 |
| `RENDER_TARGET` | レンダー ターゲットとして、書き込む |
| `DEPTH_WRITE` | 深度を、書き込む（深度テストと、書き込み） |
| `DEPTH_READ` | 深度を、読み取り専用で、テストする（読み取り専用の DSV） |
| `PIXEL_SHADER_RESOURCE` | ピクセル シェーダーで、読む（SRV） |
| `NON_PIXEL_SHADER_RESOURCE` | ピクセル以外（頂点、計算など）で、読む |
| `UNORDERED_ACCESS` | UAV として、読み書きする |
| `COPY_SOURCE` | コピー元 |
| `COPY_DEST` | コピー先 |
| `VERTEX_AND_CONSTANT_BUFFER` | 頂点バッファ、定数バッファとして、読む |
| `INDEX_BUFFER` | インデックス バッファとして、読む |
| `INDIRECT_ARGUMENT` | 間接描画の、引数 |
| `GENERIC_READ` | 読み取り用の、状態の、組み合わせ（アップロード ヒープの、初期状態） |

状態は、<strong>OR で、組み合わせられる</strong>（読み取り系だけ）。`PIXEL_SHADER_RESOURCE | NON_PIXEL_SHADER_RESOURCE` は、全シェーダーで、読める状態です。書き込み系（`RENDER_TARGET`、`UNORDERED_ACCESS`、`COPY_DEST`）は、<strong>単独</strong>です。

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
| リソース | 状態を、変える、リソース |
| `StateBefore` | 今の状態（<strong>正確に</strong>、合っている必要） |
| `StateAfter` | 次の状態 |
| `Subresource` | サブリソース（ミップ・配列要素）。`D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES` で、全部 |

`StateBefore` が、実際の状態と、違うと、デバッグ レイヤーが、エラーを、出します。リソースごとに、「今の状態」を、追跡する、仕組み（自作）を、持つのが、一般的です。

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

## 典型的な、遷移の、流れ

| 場面 | 遷移 |
| --- | --- |
| バック バッファ | `PRESENT` → `RENDER_TARGET`（描く前）→ `PRESENT`（描いた後） |
| シーン色（描いて、次のパスで、読む） | `RENDER_TARGET` → `PIXEL_SHADER_RESOURCE` |
| G バッファ | `RENDER_TARGET` → `PIXEL_SHADER_RESOURCE`（ライティング）→ `RENDER_TARGET`（次のフレーム） |
| 深度バッファ（描いて、AO で、読む） | `DEPTH_WRITE` → `NON_PIXEL_SHADER_RESOURCE`（計算シェーダー）または `PIXEL_SHADER_RESOURCE` |
| アップロード（頂点バッファ） | `COPY_DEST`（コピー）→ `VERTEX_AND_CONSTANT_BUFFER` |
| 計算シェーダーの出力 | `UNORDERED_ACCESS` → `PIXEL_SHADER_RESOURCE`（次の、描画で、読む） |
| アップロード ヒープ | 常に `GENERIC_READ`（遷移しない） |

## UAV バリア

同じ UAV に、複数の、`Dispatch` が、続けて、書き込み・読み込みをするとき、<strong>前の、`Dispatch` の、書き込みが、終わるのを、待たせる</strong>ために、UAV バリアを、入れます。状態は、`UNORDERED_ACCESS` の、まま、変わりません。

```cpp
// 計算シェーダー A が、書いた UAV を、計算シェーダー B が、読む前に。
auto uav_barrier = CD3DX12_RESOURCE_BARRIER::UAV(uav_resource.Get());
command_list->ResourceBarrier(1, &uav_barrier);
command_list->Dispatch(...);                                 // B
```

UAV バリアが、無いと、B が、A の、書き込み途中の、値を、読みます。FFT の、段ごとの、`Dispatch`、ヒストグラムの、集計などで、必須です（[Compute Shader](compute-shader.md)）。

## エイリアシング バリア

同じ、メモリを、複数の、リソースで、共有（エイリアス）して、使い回すとき、リソース A から B へ、切り替える、合図です。メモリを、節約する、上級の、技術（一時バッファを、同じ、メモリに、重ねる）で、使います。

```cpp
auto aliasing = CD3DX12_RESOURCE_BARRIER::Aliasing(resource_a.Get(), resource_b.Get());
command_list->ResourceBarrier(1, &aliasing);
```

## まとめて、渡す

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

バリアは、GPU に、<strong>パイプラインの、待ち（フラッシュ）</strong>を、起こすことが、あります。1 つずつ、何度も、呼ぶより、まとめて、渡す方が、GPU の、待ちが、減ります。<strong>不要な、バリアを、入れすぎる</strong>のも、性能を、落とします。

## 分割バリア

遷移の「開始」と「終了」を、分けて、記録する、`BEGIN_ONLY` / `END_ONLY` が、あります。開始から、終了の間に、他の、仕事を、挟むと、GPU が、遷移を、裏で、進められます。上級の、最適化です。

## 拡張バリア

新しい、バリア API（Enhanced Barriers、`ID3D12Device10`、`ID3D12GraphicsCommandList7`）は、状態の、代わりに、<strong>「どの段が、どのアクセスを、終えたか」</strong>で、記述します。より細かく、制御できますが、対応した、環境が、必要です。

## 暗黙の状態遷移

特定の、場面では、状態が、<strong>自動で、遷移</strong>します。

| 場面 | 内容 |
| --- | --- |
| `COMMON` から、コピー・読み取り | `COMMON` のリソースは、コピー（`COPY_SOURCE`/`DEST`）や、読み取りで、暗黙に、遷移（昇格）し、実行後、`COMMON` に戻る（decay） |
| アップロード・リードバック ヒープ | 状態が、固定（`GENERIC_READ`、`COPY_DEST`）で、遷移できない |

この暗黙の遷移に、頼ると、状態の追跡が、複雑になるので、<strong>明示的に</strong>、遷移させるのが、安全です。

## よくあるミス

??? failure "画面が、乱れる、テクスチャが、ちらつく、ときどきクラッシュ"
    バリアが、足りない（書いた後、読む前に、遷移していない）、または、`StateBefore` が、実際の状態と、違う。GPU ベース検証と、デバッグ レイヤーで、検出する。

??? failure "計算シェーダーの、連続した、`Dispatch` で、結果が、不安定"
    UAV バリアを、入れていない。前の `Dispatch` の、書き込みが、終わる前に、次が、読んでいる。

??? failure "アップロード バッファを、`COPY_DEST` に、遷移しようとして、エラー"
    アップロード ヒープの、リソースは、`GENERIC_READ` で、固定。遷移できない。コピー先は、DEFAULT ヒープの、リソース。

??? failure "バリアを、入れすぎて、遅い"
    1 つずつ、毎回、遷移している。まとめて、1 回で、渡す。状態の、追跡で、同じ状態への、遷移を、省く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バリア ＝ リソースの、使い方（状態）を、切り替える、合図
    - [x] 遷移バリア: `Transition(resource, 前, 後)`。前の状態は、正確に
    - [x] UAV バリア: 連続する、計算シェーダーの、書き込みと、読み込みの、順序づけ
    - [x] バック バッファは、`PRESENT` ↔ `RENDER_TARGET`
    - [x] まとめて渡す。リソースの状態は、追跡する
    - [x] GPU ベース検証で、バリアの、間違いを、見つける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Compute Shader](compute-shader.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: リソース バリア](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12)
