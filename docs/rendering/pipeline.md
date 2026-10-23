---
title: 描画のしくみ
tags:
  - 最適化
  - 3Dゲーム
---

# 描画のしくみ

ゲームの 1 フレームは**CPU が「何を描くか」の命令を作り GPU がそれを実際に描く**という、2 人のやり取りで成り立っています。どちらかが遅いとフレーム全体が遅くなります。たとえば、CPU が 5 ms で命令を作っても、GPU が描くのに 20 ms かかるならフレームは 20 ms です。このページでは最適化の前提になる描画の流れと用語を説明します。

!!! tip "ポイント"
    - フレーム時間は<strong>CPU と GPU の遅いほう</strong>で決まる。
    - 流れは<strong>命令の作成 → 頂点 → ラスタライズ → ピクセル → 書き込み</strong>。
    - まずどちらが遅いかを見分ける。詳しくは[何が重いのか](bottlenecks.md)。

## 描画の流れ

<svg class="fig flow" viewBox="0 0 1309 196" role="img" aria-label="CPU が描画命令を作り、GPU が処理する"><defs><marker id="fl12852" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">CPU が描画命令を作り、GPU が処理する</text><line x1="150.0" y1="87.0" x2="150.0" y2="125.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="275.0" y1="148.0" x2="333.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><text x="304.0" y="142.0" text-anchor="middle" style="font-size:12px">送る</text><line x1="494.0" y1="148.0" x2="552.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="802.0" y1="148.0" x2="860.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><line x1="1096.0" y1="148.0" x2="1154.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl12852)"/><rect x="79.5" y="44.0" width="141" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="150.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">CPU ゲームの更新</text><circle cx="81.5" cy="46.0" r="10" fill="#4c8bf5"/><text x="81.5" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="28.0" y="128.0" width="244" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="150.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">描画命令を作る （ドローコール）</text><circle cx="30.0" cy="130.0" r="10" fill="#2ea043"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="336.0" y="128.0" width="155" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="413.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GPU 頂点シェーダー</text><circle cx="338.0" cy="130.0" r="10" fill="#e5a828"/><text x="338.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="555.0" y="128.0" width="244" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="677.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ラスタライズ （ピクセルに分解）</text><circle cx="557.0" cy="130.0" r="10" fill="#e5484d"/><text x="557.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text><rect x="863.0" y="128.0" width="230" height="40" rx="9" fill="rgba(150,100,230,0.22)" stroke="#9664e6" stroke-width="2"/><text x="978.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ピクセルシェーダー （色付け）</text><circle cx="865.0" cy="130.0" r="10" fill="#9664e6"/><text x="865.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">5</text><rect x="1157.0" y="128.0" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="1219.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面に書き込む</text><circle cx="1159.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="1159.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">6</text></svg>

| 用語 | 意味 |
| --- | --- |
| **ドロー コール** | 「この形をこの設定で描いて」という GPU への 1 回の描画命令 |
| 頂点シェーダー | 頂点（三角形の角）の位置を計算するプログラム |
| ピクセル シェーダー | 画面の 1 点（ピクセル）の色を計算するプログラム |
| オーバードロー | 同じピクセルに何度も描くこと（手前に隠れて見えないものまで描く） |
| フィルレート | 1 秒に描けるピクセル数。GPU の限界の 1 つ |
| メモリ帯域 | GPU がテクスチャなどを読み書きできる速さ |

## CPU と GPU、どちらが遅いか

| 症状 | 原因の候補 | 確かめ方 |
| --- | --- | --- |
| **解像度を下げると速くなる** | GPU 側（ピクセルが多い。フィルレート、シェーダーが重い） | 解像度を半分にして、フレーム時間を比べる |
| 解像度を下げても変わらない | CPU 側（ドロー コール、ゲームの更新） | 同上 |
| オブジェクトの数を減らすと速くなる | CPU 側（ドロー コール）か、GPU 側（頂点数） | |
| GPU プロファイラーで、GPU が 100% 近い | GPU 側 | RenderDoc、PIX、NVIDIA Nsight |
| CPU プロファイラーで、描画の関数が上位 | CPU 側 | Visual Studio のプロファイラー |

## 1 フレームの時間はどう決まるか

60 FPS で動かすなら 1 フレームに使える時間は約 16.7 ms です（30 FPS なら 33.3 ms、120 FPS なら 8.3 ms）。この時間の中で CPU の仕事と GPU の仕事が、<strong>重なって</strong>進みます。

```text
CPU:  [フレーム N の更新・命令の記録][フレーム N+1 の更新・命令の記録][フレーム N+2 …]
GPU:            [フレーム N−1 の描画]          [フレーム N の描画]        [フレーム N+1 …]
```

CPU はフレーム N の命令を作っている間に GPU は、1 つ前のフレーム N−1 を描いています（フレーム イン フライト。[Frame Resources](../directx/dx12/frame-resources.md)）。このため 1 フレームの時間はおおよそCPU と GPU の遅いほうで決まります。

| CPU の時間 | GPU の時間 | フレーム時間 | 速くするには |
| --- | --- | --- | --- |
| 8 ms | 12 ms | 約 12 ms | GPU を減らす（CPU を、いくら減らしても変わらない） |
| 14 ms | 6 ms | 約 14 ms | CPU を減らす（GPU を、いくら減らしても変わらない） |
| 15 ms | 15 ms | 約 15 ms | 両方を同時に減らさないと、速くならない |

どちらが遅いか分からないまま片方だけを直すと時間を無駄にします。遅いほうを見分けるのが最初の仕事です。

フレーム イン フライトを増やすと CPU が、先に進めて時間は安定しますが、入力から画面に出るまでの遅延が、1 フレームぶん増えます。

## GPU の中のボトルネックの種類

GPU が遅いと分かったら次は <strong>GPU の中のどこ</strong>が遅いかです。描画パイプラインの段ごとに詰まる場所が違い効く対策も違います。

| ボトルネック | 起きる場面 | 確かめる実験 | 効く対策 |
| --- | --- | --- | --- |
| 頂点処理 | 三角形が非常に多い。頂点シェーダーが重い | メッシュの LOD を下げる。ピクセル シェーダーを空にしても変わらない | LOD、カリング、メッシュレット |
| ピクセルの計算（ALU） | ピクセル シェーダーが長い。解像度が高い | シェーダーを短くすると速くなる。解像度を下げると速くなる | シェーダーの軽量化、低解像度 |
| テクスチャの読み込み | テクスチャ参照が多い。大きなテクスチャ | 全テクスチャを 1×1 にすると速くなる（下のコード） | 圧縮、ミップ、参照を減らす |
| メモリ帯域 | 大きなレンダー ターゲット、G バッファ、ポスト プロセス | レンダー ターゲットのフォーマットを小さくすると速くなる | フォーマット、パスの統合 |
| ブレンド・書き込み（ROP） | 半透明が多い。画面全体の重ね描き | ブレンドを無効にすると速くなる | 半透明の削減、縮小バッファ |

「テクスチャが原因か」を調べる簡単な実験は、サンプラーで 最も小さいミップだけを読ませることです。

```cpp
// 実験: 全テクスチャを、最も小さいミップ（約 1×1）で読ませる。速くなれば、テクスチャの読み込みが重い。
D3D11_SAMPLER_DESC desc = normal_sampler_desc;
desc.MinLOD = 15.0f;                                          // ミップ 15 より細かい段を、使わない（実質 1×1）
device->CreateSamplerState(&desc, &debug_sampler);
// 描画の前に、全パスで debug_sampler を束ねて、フレーム時間を比べる。
```

実験は 1 つずつ変えて効果を見ます。複数を同時に変えるとどれが効いたか分かりません。

## ドロー コール 1 回で、CPU が行うこと

「ドロー コールが多いと遅い」と言われるのは、CPU が 1 回ごとに次のような仕事をするためです。

| 仕事 | 内容 |
| --- | --- |
| 状態の検証 | シェーダー、ステート、リソースの組み合わせが正しいかを確認 |
| リソースの束縛 | ビューや定数バッファをパイプラインにつなぐ |
| 命令の生成 | GPU が理解できる命令の列に変換して書き込む（ドライバー） |
| 同期の管理 | 読み書きの衝突の整理（D3D11 はドライバーが、D3D12 はアプリが行う） |

1 回の命令は数マイクロ秒から十数マイクロ秒（環境により大きく変わる）で、<strong>数千回、積み重なると数十 ミリ秒</strong>になります。そのため、同じメッシュをインスタンスでまとめる状態を変えない順に並べるといった対策が効きます（[ドロー コールとバッチ](draw-calls.md)）。D3D12 はこの CPU の負荷が小さく、複数のスレッドで命令を記録できます。

## CPU 時間を測る

CPU 側の時間は `std::chrono` で測れます。ただし、<strong>GPU の時間は別</strong>で GPU タイムスタンプ（[GPU Queries and Timing](../directx/dx11/query-timing.md)）で測ります。

```cpp
#include <chrono>

using Clock = std::chrono::steady_clock;

// CPU 側の、ある範囲の時間（ミリ秒）を測る。命令を積む時間で、GPU の実行時間では、ない。
class ScopedTimer {
 public:
  explicit ScopedTimer(double* out_ms) : out_ms_(out_ms), start_(Clock::now()) {}
  ~ScopedTimer() { *out_ms_ = std::chrono::duration<double, std::milli>(Clock::now() - start_).count(); }

 private:
  double* out_ms_;
  Clock::time_point start_;
};

void RenderScene() {
  double record_ms = 0.0;
  {
    ScopedTimer timer(&record_ms);
    RecordDrawCalls();                                        // 命令を積む（CPU の仕事）
  }
  // record_ms が、CPU 側の「描画の準備」の時間。
}
```

`RecordDrawCalls` の時間がフレーム時間の大半を占めていれば、CPU がボトルネックです。命令の積み方（バッチ、インスタンス、GPU ドリブン）を見直します。

## 関連ページ

- [描画の流れ（入門）：図で最初から追う](../3d/render-flow/index.md)
- [描画最適化](index.md)
- [何が重いのか](bottlenecks.md)
- [計測（プロファイリング）](../optimize/measure.md)
- [フレーム時間の設計](../optimize/frame-budget.md)

