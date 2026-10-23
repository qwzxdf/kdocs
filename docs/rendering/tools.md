---
title: 調査ツール
tags:
  - 最適化
  - 3Dゲーム
---

# 調査ツール

描画の最適化は**測ってから**行います。勘で直してもボトルネックでない部分を最適化して、速くならないことがよくあります。このページでは描画を調べるための道具と見るべき項目を説明します。

!!! tip "ポイント"
    - まず<strong>CPU か GPU か</strong>を見分ける（解像度を変えて比べる）。
    - <strong>1 フレームを分解</strong>して、ドロー コールごとの時間を見る（RenderDoc・PIX）。
    - GPU の内部（占有率・メモリ待ち）は、ベンダーのツール（Nsight・RGP）。
    - オーバードローの可視化は、自作でも簡単に作れる。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## 道具の一覧

| 道具 | 何が分かるか |
| --- | --- |
| **RenderDoc**（無料） | 1 フレームをドロー コール 1 つずつに分解。何をどの順番で描いたか。テクスチャ、バッファの中身 |
| PIX（Microsoft・無料） | DirectX の CPU / GPU のタイミング。どの描画が重いか |
| NVIDIA Nsight / AMD Radeon GPU Profiler | GPU の内部（シェーダーの重さ、メモリ帯域）の詳細 |
| Visual Studio の「グラフィックス診断」 | フレームの キャプチャ（古い API 向け） |
| オーバードローの可視化 | 何回描かれたかを色で表示（自作のデバッグ表示で加算ブレンドで表示する） |

## 見るべき項目

| 見たいもの | 道具 | 見る場所 |
| --- | --- | --- |
| **フレーム全体の時間** | PIX・エンジンの統計 | CPU 時間と GPU 時間 |
| 重いドロー コール | PIX・RenderDoc | ドロー コールごとの GPU 時間 |
| ドロー コールの数 | RenderDoc | イベント一覧 |
| オーバードロー | RenderDoc のオーバーレイ・自作 | 加算ブレンドで重なりを色にする |
| 帯域幅 | Nsight・RGP | メモリ スループットの使用率 |
| シェーダーの重さ | Nsight・RGP・PIX | 占有率・ALU 使用率・テクスチャ待ち |
| VRAM 使用量 | PIX・タスク マネージャー | テクスチャ・バッファの合計 |

## 切り分けの手順

| 手順 | 内容 |
| --- | --- |
| **① CPU か GPU か** | 解像度を半分にして、フレーム時間が変わるか見る |
| ② GPU ならどのパスか | PIX などでパスごとの時間を見る（シャドウ・G-Buffer・ライティング・ポスト） |
| ③ そのパスの中で何か | 頂点・ピクセル・帯域のどれか。シェーダーを空にして速くなるかで確かめる |
| ④ 直してまた測る | 1 つずつ変えて、効果を確認する |

## RenderDoc の使い方

RenderDoc は 1 フレームを撮って、描画の中身を細かく見る道具です（無料）。

| 手順 | 操作 |
| --- | --- |
| ① 起動して実行ファイルを指定 | `Launch Application` に実行ファイルのパスを入れて `Launch` |
| ② 1 フレームを撮る | ゲームの画面で `F12`（または `Print Screen`）。撮ったフレームが一覧に出る |
| ③ イベントを見る | `Event Browser` にドロー コールとクリアが、順に並ぶ。マーカー（下）でパスごとにまとまる |
| ④ 1 つの描画を調べる | イベントを選び `Pipeline State` で、シェーダー、ステート、束縛を見る。`Texture Viewer` でレンダー ターゲットと入力テクスチャを見る |
| ⑤ オーバードローを見る | `Texture Viewer` の `Overlay` で `Quad Overdraw (Draw)`（1 回の描画の重なり）や `Quad Overdraw (Pass)`（パス全体） |
| ⑥ ピクセルの履歴 | ピクセルを右クリックして `Pixel History`。そのピクセルにどの描画が書いたかが分かる |
| ⑦ シェーダーのデバッグ | ピクセルの履歴から `Debug this Pixel` で、シェーダーを 1 行ずつ追う |

「何も映らない」「色がおかしい」といった、見た目の問題には特に役立ちます。入力のテクスチャが真っ黒だった、ビューポートが 0 だったといった原因が、すぐ見つかります。

## PIX で GPU の時間を見る

PIX（Windows、無料）は DirectX の描画の時間を詳しく見ます。

| 機能 | 内容 |
| --- | --- |
| `GPU Capture` | 1 フレームを撮って、各ドロー コールの GPU 時間を一覧にする |
| `Timing Capture` | CPU と GPU の時間線。どこで CPU が GPU を待っているかが分かる |
| 占有率・カウンター | ベンダーのカウンター（ウェーブの占有率、キャッシュの当たり率）が見られる環境がある |

<strong>デバッグ情報つきのシェーダー</strong>（`-Zi`）と マーカーがあると、見やすくなります。

## コードにマーカーを入れる

マーカーを入れると RenderDoc や PIX で、パスの名前が見えます。

```cpp
// D3D11: ID3DUserDefinedAnnotation
Microsoft::WRL::ComPtr<ID3DUserDefinedAnnotation> annotation;
context.As(&annotation);

annotation->BeginEvent(L"Shadow Pass");
DrawShadowMaps();
annotation->EndEvent();

// 範囲を抜けると自動で閉じる、簡単な道具。
struct GpuMarker {
  ID3DUserDefinedAnnotation* annotation;
  GpuMarker(ID3DUserDefinedAnnotation* a, const wchar_t* name) : annotation(a) { annotation->BeginEvent(name); }
  ~GpuMarker() { annotation->EndEvent(); }
};
// 使い方: GpuMarker marker(annotation.Get(), L"G-Buffer Pass");
```

D3D12 では WinPixEventRuntime の `PIXBeginEvent(command_list, color, name)` と `PIXEndEvent(command_list)` を使います（[Debug Layer](../directx/dx12/debug-layer.md)）。

## オーバードローを自作で見える化する

エンジンの中にデバッグ表示として、組み込めます。<strong>全ての物を「1 回描くと少しだけ足す」</strong>シェーダーで描き色に変えます。

```hlsl
// ① 全オブジェクトを、このピクセル シェーダーで描く（加算ブレンド）。1 回の重なりで、1/8 だけ足す。
float PSOverdraw() : SV_Target {
  return 1.0 / 8.0;
}
```

```cpp
// レンダー ターゲット: R16_FLOAT。ブレンドは加算（ONE, ONE）。深度テストは無効（隠れた物も、数える）。
D3D11_BLEND_DESC blend = {};
blend.RenderTarget[0].BlendEnable = TRUE;
blend.RenderTarget[0].SrcBlend = D3D11_BLEND_ONE;
blend.RenderTarget[0].DestBlend = D3D11_BLEND_ONE;
blend.RenderTarget[0].BlendOp = D3D11_BLEND_OP_ADD;
blend.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_ONE;
blend.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_ONE;
blend.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_ADD;
blend.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_RED;
```

```hlsl
// ② フルスクリーン パスで、重なりの数を、色に変える（青 → 緑 → 黄 → 赤）。
Texture2D<float> g_overdraw : register(t0);

float4 PSHeat(float4 pos : SV_Position) : SV_Target {
  float layers = g_overdraw.Load(int3(pos.xy, 0)) * 8.0;         // 重なりの数（1/8 を、戻す）
  float t = saturate(layers / 8.0);                              // 8 重なりで、真っ赤
  float3 color = lerp(float3(0, 0, 1), float3(0, 1, 0), saturate(t * 2.0));
  color = lerp(color, float3(1, 0, 0), saturate(t * 2.0 - 1.0));
  return float4(color, 1.0);
}
```

青なら 1〜2 重ね緑・黄が、3〜5 重ね赤なら 8 重ね以上、という見え方になります。赤い所（煙、草むら UI の重ね）を優先して減らします（[Overdraw](overdraw.md)）。

## フレーム時間をグラフと数字で見る

平均だけを見ると突発的な遅さ（スパイク）を見逃します。<strong>最悪の値</strong>（99 パーセンタイルなど）もあわせて表示します。

```cpp
#include <algorithm>
#include <array>
#include <cstddef>

// 直近 N フレームの、フレーム時間（ms）を覚えて、平均と、最悪に近い値（99 パーセンタイル）を返す。
template <std::size_t N>
class FrameStats {
 public:
  void Add(float ms) {
    samples_[next_] = ms;
    next_ = (next_ + 1) % N;
    if (count_ < N) ++count_;
  }

  float Average() const {
    float sum = 0.0f;
    for (std::size_t i = 0; i < count_; ++i) sum += samples_[i];
    return count_ ? sum / count_ : 0.0f;
  }

  float Percentile(float p) const {                              // p: 0.99 など
    std::array<float, N> copy = samples_;
    std::size_t k = static_cast<std::size_t>(p * (count_ - 1));
    std::nth_element(copy.begin(), copy.begin() + k, copy.begin() + count_);
    return copy[k];
  }

 private:
  std::array<float, N> samples_{};
  std::size_t next_ = 0;
  std::size_t count_ = 0;
};
// 使い方: FrameStats<240> stats; stats.Add(frame_ms); 画面に Average() と Percentile(0.99f) を出す。
```

平均が 12 ms でも 99 パーセンタイルが 30 ms ならときどきカクつきます。平均ではなくスパイクの原因（アセットの読み込みシェーダーのコンパイル、ガベージ）を探します（[フレーム時間の設計](../optimize/frame-budget.md)）。

## よくあるミス

??? failure "プロファイラーを使わず勘で直す"
    ボトルネックでない所を直しても、速くなりません。

??? failure "デバッグ ビルドで測る"
    最適化が効いていないので、結果が当てになりません。リリース相当で測ります。

??? failure "平均だけを見て、スパイクを見逃す"
    フレームごとの時間のグラフで、突発的な遅さを探します（[フレーム時間の設計](../optimize/frame-budget.md)）。

??? failure "複数の変更を同時にして、どれが効いたか分からない"
    1 つずつ変えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>測ってから</strong>直す
    - [x] RenderDoc / PIX で 1 フレームを分解
    - [x] Nsight / RGP で GPU の内部を見る
    - [x] 切り分けはCPU/GPU → パス → 頂点/ピクセル/帯域
    - [x] 1 つずつ変えて、効果を確認

## 関連ページ

- [描画最適化](index.md)
- [何が重いのか](bottlenecks.md)
- [計測（プロファイリング）](../optimize/measure.md)
- [プロファイラー（Visual Studio）](../vs/profiler.md)

