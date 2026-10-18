---
title: GPU Queries and Timing
tags:
  - DirectX
---

# GPU Queries and Timing

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

「このパスは何ミリ秒、かかっているか」を知るには CPU の時計では、足りません。D3D11 の命令は CPU が積んで、<strong>GPU があとで実行する</strong>ので、CPU 側で `Draw` の前後の時間を測っても命令を積む時間しか測れません。GPU 自身に時刻を記録させる <strong>クエリ</strong>（Query）が必要です。

!!! tip "ポイント"
    - GPU の時間は <strong>タイムスタンプ クエリ</strong>で測る。開始と終了の 2 つのタイムスタンプと周波数（`DISJOINT`）が 1 組。
    - 結果は GPU が実行を終えてから取り出せる。<strong>数フレーム、遅れて読む</strong>（すぐ読むと CPU が、GPU を待って止まる）。
    - `Disjoint` が `TRUE` のフレーム（クロックが、変わった）の結果は捨てる。
    - ほかのクエリ: オクルージョン（見えたピクセル数）、パイプライン統計（頂点・ピクセルの数）、イベント（完了の確認）。
    - 本格的な計測はグラフィックス デバッガー（PIX、RenderDoc、Nsight）。

## タイムスタンプ クエリ

```cpp
struct GpuTimer {
  Microsoft::WRL::ComPtr<ID3D11Query> disjoint;
  Microsoft::WRL::ComPtr<ID3D11Query> start;
  Microsoft::WRL::ComPtr<ID3D11Query> end;
};

GpuTimer CreateGpuTimer(ID3D11Device* device) {
  GpuTimer timer;
  D3D11_QUERY_DESC desc = {};
  desc.Query = D3D11_QUERY_TIMESTAMP_DISJOINT;              // クロックの周波数と、途切れの有無
  device->CreateQuery(&desc, &timer.disjoint);
  desc.Query = D3D11_QUERY_TIMESTAMP;                       // ある瞬間の、GPU の時刻
  device->CreateQuery(&desc, &timer.start);
  device->CreateQuery(&desc, &timer.end);
  return timer;
}
```

| クエリ | 内容 |
| --- | --- |
| `TIMESTAMP_DISJOINT` | 周波数（1 秒あたりのチック数）と途切れた（`Disjoint`）かどうか。`Begin` と `End` で囲む |
| `TIMESTAMP` | ある瞬間の GPU の時刻（チック数）。`End` だけ（`Begin` は不要） |

### 測る

```cpp
context->Begin(timer.disjoint.Get());                       // 計測の、開始
context->End(timer.start.Get());                            // 時刻 1: この時点の、GPU の時刻を、記録
RunPass();                                                  // 測りたい処理
context->End(timer.end.Get());                              // 時刻 2
context->End(timer.disjoint.Get());                         // 計測の、終了
```

`Begin(disjoint)` と `End(disjoint)` の間で `End(timestamp)` を呼びます。タイムスタンプは `Begin` が要らず `End` で、GPU がその命令に到達した時刻を書きます。

### 結果を読む

```cpp
// 数フレーム後に、読む。S_OK が返れば、結果が、揃っている。
D3D11_QUERY_DATA_TIMESTAMP_DISJOINT disjoint_data;
UINT64 t0, t1;
if (context->GetData(timer.disjoint.Get(), &disjoint_data, sizeof(disjoint_data), 0) == S_OK &&
    !disjoint_data.Disjoint &&
    context->GetData(timer.start.Get(), &t0, sizeof(t0), 0) == S_OK &&
    context->GetData(timer.end.Get(), &t1, sizeof(t1), 0) == S_OK) {
  double milliseconds = double(t1 - t0) / double(disjoint_data.Frequency) * 1000.0;
}
```

`GetData` の最後の引数はフラグで `0` は結果が、まだなら `S_FALSE` を返して <strong>待たずに</strong>、戻ります。`D3D11_ASYNC_GETDATA_DONOTFLUSH` を付けると命令のフラッシュもしません。

## 遅れて読む（リング）

クエリの結果は GPU がそのフレームを実行し終わるまで揃いません。<strong>すぐに読もうとすると</strong>、`S_FALSE` が返り続け待つと CPU が、止まります。<strong>数フレーム前のクエリ</strong>を読むのが、標準です。

```cpp
constexpr int kFrames = 4;                                  // 4 フレーム前まで、持つ
GpuTimer timers[kFrames];

void BeginFrame(int frame) {
  GpuTimer& t = timers[frame % kFrames];
  context->Begin(t.disjoint.Get());
  context->End(t.start.Get());
}

void EndFrame(int frame) {
  GpuTimer& t = timers[frame % kFrames];
  context->End(t.end.Get());
  context->End(t.disjoint.Get());
}

void ReadResults(int frame) {                               // 3 フレーム前の結果を読む
  GpuTimer& t = timers[(frame + 1) % kFrames];
  ...                                                       // 上の GetData
}
```

複数のパスを測るときはパスごとに `start` と `end` のペアを作ります（`disjoint` は、フレームに 1 つで足ります）。

## オクルージョン クエリ

「描いた物のピクセルが深度テストを何個、通ったか」を数えます。0 なら完全に隠れています。

```cpp
D3D11_QUERY_DESC desc = {};
desc.Query = D3D11_QUERY_OCCLUSION;                         // 通ったピクセル数を数える（OCCLUSION_PREDICATE は、0 か否かだけ）
device->CreateQuery(&desc, &occlusion_query);

context->Begin(occlusion_query.Get());
DrawBoundingBox();                                          // 物の、バウンディング ボックスを、描く（色は、書かない）
context->End(occlusion_query.Get());

UINT64 pixels = 0;
if (context->GetData(occlusion_query.Get(), &pixels, sizeof(pixels), 0) == S_OK && pixels == 0) {
  // 完全に隠れている → 次のフレームで、その物を、描かない
}
```

結果は 1〜数フレーム、遅れるので「前のフレームで隠れていた物は、描かない」運用になります（[Occlusion Culling](../../rendering/culling.md)）。

## パイプライン統計

```cpp
desc.Query = D3D11_QUERY_PIPELINE_STATISTICS;
// 結果: D3D11_QUERY_DATA_PIPELINE_STATISTICS（IAVertices、VSInvocations、PSInvocations、CSInvocations など）
```

頂点シェーダー・ピクセル シェーダーの呼び出し回数が分かります。オーバードロー（ピクセル シェーダーの回数 ÷ 画面の画素数）の見積もりに使えます。

## イベント クエリ（GPU の完了を待つ）

```cpp
desc.Query = D3D11_QUERY_EVENT;
device->CreateQuery(&desc, &event_query);

context->End(event_query.Get());                            // ここまでの命令が、完了したら、シグナル
BOOL done = FALSE;
while (context->GetData(event_query.Get(), &done, sizeof(done), 0) != S_OK || !done) {
  // GPU の完了を待つ（スピンするので、実際には、別の仕事をする）
}
```

`CopyResource` の後、結果の準備を確認するときなどに使います。<strong>CPU が GPU を待つ</strong>ので、毎フレームの使用は避けます。

## 速さを測る別の方法

| 方法 | 内容 |
| --- | --- |
| タイムスタンプ クエリ（このページ） | コードに埋め込み各パスのミリ秒を画面に、表示する |
| PIX（Windows） | 1 フレームを撮って、各ドロー コールの時間を見る。GPU カウンター |
| RenderDoc | 1 フレームを撮って各段の入出力を見る。無料 |
| NVIDIA Nsight、AMD Radeon GPU Profiler | ベンダー固有の詳細な、カウンター |

製品のゲームではタイムスタンプ クエリをデバッグ表示に組み込んでおくとどのパスが重いかをすぐに確認できます（[Tools](../../rendering/tools.md)）。

## よくあるミス

??? failure "測った時間が異常に短い（CPU の時間）"
    CPU の `QueryPerformanceCounter` で `Draw` の前後を測っている。GPU はまだ実行していない。GPU タイムスタンプで測る。

??? failure "クエリを読むたびにフレームが止まる"
    すぐに読んで GPU の完了を待っている。数フレーム前のクエリを読む（リング）。

??? failure "時間が負、または巨大な値になる"
    `Disjoint` が `TRUE` のフレームの結果を使っている。捨てる。

??? failure "`GetData` が、いつまでも `S_FALSE`"
    `End` を呼んでいない。`Begin`/`End` のペアが崩れている。または、GPU がまだそのフレームを実行していない（遅れて読む）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU の時間は、GPU に測らせる。CPU の時計では測れない
    - [x] `TIMESTAMP_DISJOINT`（周波数）+ `TIMESTAMP` 2 つ（開始・終了）
    - [x] 結果は数フレーム遅れて `GetData(…, 0)` で、待たずに読む
    - [x] `Disjoint` が `TRUE` なら捨てる
    - [x] ほかにオクルージョン、パイプライン統計、イベント
    - [x] 本格的には PIX・RenderDoc

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Debug Layer](debug-layer.md)
- [Tools](../../rendering/tools.md)
- [Occlusion Culling](../../rendering/culling.md)
- [Microsoft Learn: ID3D11Query](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nn-d3d11-id3d11query)
