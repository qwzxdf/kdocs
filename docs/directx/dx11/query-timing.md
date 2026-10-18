---
title: GPU Queries and Timing
tags:
  - DirectX
---

# GPU Queries and Timing

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

「このパスは、何ミリ秒、かかっているか」を、知るには、CPU の時計では、足りません。D3D11 の命令は、CPU が積んで、<strong>GPU が、あとで、実行する</strong>ので、CPU 側で、`Draw` の前後の、時間を、測っても、命令を、積む時間しか、測れません。GPU 自身に、時刻を、記録させる、<strong>クエリ</strong>（Query）が、必要です。

!!! tip "ポイント"
    - GPU の時間は、<strong>タイムスタンプ クエリ</strong>で、測る。開始と終了の、2 つの、タイムスタンプと、周波数（`DISJOINT`）が、1 組。
    - 結果は、GPU が、実行を、終えてから、取り出せる。<strong>数フレーム、遅れて、読む</strong>（すぐ読むと、CPU が、GPU を、待って、止まる）。
    - `Disjoint` が `TRUE` のフレーム（クロックが、変わった）の、結果は、捨てる。
    - ほかのクエリ: オクルージョン（見えたピクセル数）、パイプライン統計（頂点・ピクセルの数）、イベント（完了の確認）。
    - 本格的な計測は、グラフィックス デバッガー（PIX、RenderDoc、Nsight）。

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
| `TIMESTAMP_DISJOINT` | 周波数（1 秒あたりの、チック数）と、途切れた（`Disjoint`）かどうか。`Begin` と `End` で、囲む |
| `TIMESTAMP` | ある瞬間の、GPU の、時刻（チック数）。`End` だけ（`Begin` は不要） |

### 測る

```cpp
context->Begin(timer.disjoint.Get());                       // 計測の、開始
context->End(timer.start.Get());                            // 時刻 1: この時点の、GPU の時刻を、記録
RunPass();                                                  // 測りたい処理
context->End(timer.end.Get());                              // 時刻 2
context->End(timer.disjoint.Get());                         // 計測の、終了
```

`Begin(disjoint)` と `End(disjoint)` の間で、`End(timestamp)` を、呼びます。タイムスタンプは、`Begin` が、要らず、`End` で、GPU が、その命令に、到達した、時刻を、書きます。

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

`GetData` の、最後の引数は、フラグで、`0` は、結果が、まだなら、`S_FALSE` を、返して、<strong>待たずに</strong>、戻ります。`D3D11_ASYNC_GETDATA_DONOTFLUSH` を、付けると、命令の、フラッシュも、しません。

## 遅れて読む（リング）

クエリの結果は、GPU が、そのフレームを、実行し終わるまで、揃いません。<strong>すぐに、読もうとすると</strong>、`S_FALSE` が、返り続け、待つと、CPU が、止まります。<strong>数フレーム前の、クエリ</strong>を、読むのが、標準です。

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

複数の、パスを、測るときは、パスごとに、`start` と `end` の、ペアを、作ります（`disjoint` は、フレームに 1 つで、足ります）。

## オクルージョン クエリ

「描いた物の、ピクセルが、深度テストを、何個、通ったか」を、数えます。0 なら、完全に、隠れています。

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

結果は、1〜数フレーム、遅れるので、「前のフレームで、隠れていた物は、描かない」運用に、なります（[Occlusion Culling](../../rendering/culling.md)）。

## パイプライン統計

```cpp
desc.Query = D3D11_QUERY_PIPELINE_STATISTICS;
// 結果: D3D11_QUERY_DATA_PIPELINE_STATISTICS（IAVertices、VSInvocations、PSInvocations、CSInvocations など）
```

頂点シェーダー・ピクセル シェーダーの、呼び出し回数が、分かります。オーバードロー（ピクセル シェーダーの回数 ÷ 画面の画素数）の、見積もりに、使えます。

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

`CopyResource` の後、結果の準備を、確認するときなどに、使います。<strong>CPU が、GPU を、待つ</strong>ので、毎フレームの使用は、避けます。

## 速さを、測る、別の方法

| 方法 | 内容 |
| --- | --- |
| タイムスタンプ クエリ（このページ） | コードに、埋め込み、各パスの、ミリ秒を、画面に、表示する |
| PIX（Windows） | 1 フレームを、撮って、各ドロー コールの、時間を、見る。GPU カウンター |
| RenderDoc | 1 フレームを、撮って、各段の、入出力を、見る。無料 |
| NVIDIA Nsight、AMD Radeon GPU Profiler | ベンダー固有の、詳細な、カウンター |

製品の、ゲームでは、タイムスタンプ クエリを、デバッグ表示に、組み込んでおくと、どのパスが、重いかを、すぐに、確認できます（[Tools](../../rendering/tools.md)）。

## よくあるミス

??? failure "測った時間が、異常に、短い（CPU の時間）"
    CPU の `QueryPerformanceCounter` で、`Draw` の前後を、測っている。GPU は、まだ、実行していない。GPU タイムスタンプで、測る。

??? failure "クエリを、読むたびに、フレームが、止まる"
    すぐに読んで、GPU の、完了を、待っている。数フレーム前の、クエリを、読む（リング）。

??? failure "時間が、負、または、巨大な値になる"
    `Disjoint` が `TRUE` のフレームの、結果を、使っている。捨てる。

??? failure "`GetData` が、いつまでも、`S_FALSE`"
    `End` を、呼んでいない。`Begin`/`End` の、ペアが、崩れている。または、GPU が、まだ、そのフレームを、実行していない（遅れて読む）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU の時間は、GPU に、測らせる。CPU の時計では、測れない
    - [x] `TIMESTAMP_DISJOINT`（周波数）+ `TIMESTAMP` 2 つ（開始・終了）
    - [x] 結果は、数フレーム遅れて、`GetData(…, 0)` で、待たずに、読む
    - [x] `Disjoint` が `TRUE` なら、捨てる
    - [x] ほかに、オクルージョン、パイプライン統計、イベント
    - [x] 本格的には、PIX・RenderDoc

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Debug Layer](debug-layer.md)
- [Tools](../../rendering/tools.md)
- [Occlusion Culling](../../rendering/culling.md)
- [Microsoft Learn: ID3D11Query](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nn-d3d11-id3d11query)
