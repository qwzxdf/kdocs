import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# ---------------------------------------------------------------- pipeline.md
pg.Add("../rendering/pipeline.md", '''
## 1 フレームの時間は、どう決まるか

60 FPS で動かすなら、1 フレームに使える時間は約 16.7 ms です（30 FPS なら 33.3 ms、120 FPS なら 8.3 ms）。この時間の中で、CPU の仕事と GPU の仕事が、<strong>重なって</strong>進みます。

```text
CPU:  [フレーム N の更新・命令の記録][フレーム N+1 の更新・命令の記録][フレーム N+2 …]
GPU:            [フレーム N−1 の描画]          [フレーム N の描画]        [フレーム N+1 …]
```

CPU は、フレーム N の命令を作っている間に、GPU は、1 つ前のフレーム N−1 を描いています（フレーム イン フライト。[Frame Resources](../directx/dx12/frame-resources.md)）。このため、1 フレームの時間は、おおよそ<strong>CPU と GPU の、遅いほう</strong>で決まります。

| CPU の時間 | GPU の時間 | フレーム時間 | 速くするには |
| --- | --- | --- | --- |
| 8 ms | 12 ms | 約 12 ms | GPU を減らす（CPU を、いくら減らしても、変わらない） |
| 14 ms | 6 ms | 約 14 ms | CPU を減らす（GPU を、いくら減らしても、変わらない） |
| 15 ms | 15 ms | 約 15 ms | 両方を、同時に減らさないと、速くならない |

<strong>どちらが遅いか分からないまま、片方だけを直す</strong>と、時間を、無駄にします。遅いほうを見分けるのが、最初の仕事です。

フレーム イン フライトを増やすと、CPU が、先に進めて、時間は安定しますが、入力から画面に出るまでの<strong>遅延</strong>が、1 フレームぶん、増えます。

## GPU の中の、ボトルネックの種類

GPU が遅いと分かったら、次は、<strong>GPU の中の、どこ</strong>が遅いかです。描画パイプラインの段ごとに、詰まる場所が違い、効く対策も違います。

| ボトルネック | 起きる場面 | 確かめる実験 | 効く対策 |
| --- | --- | --- | --- |
| 頂点処理 | 三角形が非常に多い。頂点シェーダーが重い | メッシュの LOD を下げる。ピクセル シェーダーを空にしても変わらない | LOD、カリング、メッシュレット |
| ピクセルの計算（ALU） | ピクセル シェーダーが長い。解像度が高い | シェーダーを短くすると速くなる。解像度を下げると速くなる | シェーダーの軽量化、低解像度 |
| テクスチャの読み込み | テクスチャ参照が多い。大きなテクスチャ | 全テクスチャを 1×1 にすると速くなる（下のコード） | 圧縮、ミップ、参照を減らす |
| メモリ帯域 | 大きなレンダー ターゲット、G バッファ、ポスト プロセス | レンダー ターゲットのフォーマットを小さくすると速くなる | フォーマット、パスの統合 |
| ブレンド・書き込み（ROP） | 半透明が多い。画面全体の重ね描き | ブレンドを無効にすると速くなる | 半透明の削減、縮小バッファ |

「テクスチャが原因か」を調べる、簡単な実験は、サンプラーで、<strong>最も小さいミップだけを読ませる</strong>ことです。

```cpp
// 実験: 全テクスチャを、最も小さいミップ（約 1×1）で読ませる。速くなれば、テクスチャの読み込みが重い。
D3D11_SAMPLER_DESC desc = normal_sampler_desc;
desc.MinLOD = 15.0f;                                          // ミップ 15 より細かい段を、使わない（実質 1×1）
device->CreateSamplerState(&desc, &debug_sampler);
// 描画の前に、全パスで debug_sampler を束ねて、フレーム時間を比べる。
```

実験は、<strong>1 つずつ</strong>変えて、効果を見ます。複数を同時に変えると、どれが効いたか分かりません。

## ドロー コール 1 回で、CPU が行うこと

「ドロー コールが多いと遅い」と言われるのは、CPU が、1 回ごとに、次のような仕事をするためです。

| 仕事 | 内容 |
| --- | --- |
| 状態の検証 | シェーダー、ステート、リソースの組み合わせが、正しいかを確認 |
| リソースの束縛 | ビューや定数バッファを、パイプラインにつなぐ |
| 命令の生成 | GPU が理解できる、命令の列に、変換して書き込む（ドライバー） |
| 同期の管理 | 読み書きの衝突の、整理（D3D11 はドライバーが、D3D12 はアプリが行う） |

1 回の命令は、数マイクロ秒から十数マイクロ秒（環境により大きく変わる）で、<strong>数千回、積み重なると、数十 ミリ秒</strong>になります。そのため、同じメッシュを、インスタンスでまとめる、状態を、変えない順に、並べるといった対策が効きます（[ドロー コールとバッチ](draw-calls.md)）。D3D12 は、この CPU の負荷が、小さく、複数のスレッドで、命令を、記録できます。

## CPU 時間を測る

CPU 側の時間は、`std::chrono` で測れます。ただし、<strong>GPU の時間は、別</strong>で、GPU タイムスタンプ（[GPU Queries and Timing](../directx/dx11/query-timing.md)）で測ります。

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

`RecordDrawCalls` の時間が、フレーム時間の大半を占めていれば、CPU が、ボトルネックです。命令の積み方（バッチ、インスタンス、GPU ドリブン）を、見直します。
''', before="## 関連ページ")

# ---------------------------------------------------------------- tools.md
pg.Add("../rendering/tools.md", '''
## RenderDoc の使い方

RenderDoc は、1 フレームを撮って、描画の中身を、細かく見る道具です（無料）。

| 手順 | 操作 |
| --- | --- |
| ① 起動して、実行ファイルを指定 | `Launch Application` に、実行ファイルのパスを入れて、`Launch` |
| ② 1 フレームを撮る | ゲームの画面で `F12`（または `Print Screen`）。撮ったフレームが、一覧に出る |
| ③ イベントを見る | `Event Browser` に、ドロー コールとクリアが、順に並ぶ。マーカー（下）で、パスごとにまとまる |
| ④ 1 つの描画を調べる | イベントを選び、`Pipeline State` で、シェーダー、ステート、束縛を見る。`Texture Viewer` で、レンダー ターゲットと入力テクスチャを見る |
| ⑤ オーバードローを見る | `Texture Viewer` の `Overlay` で `Quad Overdraw (Draw)`（1 回の描画の重なり）や `Quad Overdraw (Pass)`（パス全体） |
| ⑥ ピクセルの履歴 | ピクセルを右クリックして `Pixel History`。そのピクセルに、どの描画が、書いたかが分かる |
| ⑦ シェーダーのデバッグ | ピクセルの履歴から、`Debug this Pixel` で、シェーダーを 1 行ずつ追う |

「何も映らない」「色がおかしい」といった、見た目の問題には、特に役立ちます。入力のテクスチャが、真っ黒だった、ビューポートが 0 だった、といった原因が、すぐ見つかります。

## PIX で、GPU の時間を見る

PIX（Windows、無料）は、DirectX の描画の、時間を、詳しく見ます。

| 機能 | 内容 |
| --- | --- |
| `GPU Capture` | 1 フレームを撮って、各ドロー コールの GPU 時間を、一覧にする |
| `Timing Capture` | CPU と GPU の、時間線。どこで、CPU が、GPU を待っているかが分かる |
| 占有率・カウンター | ベンダーのカウンター（ウェーブの占有率、キャッシュの当たり率）が、見られる環境がある |

<strong>デバッグ情報つきのシェーダー</strong>（`-Zi`）と、<strong>マーカー</strong>があると、見やすくなります。

## コードに、マーカーを入れる

マーカーを入れると、RenderDoc や PIX で、パスの名前が、見えます。

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

D3D12 では、WinPixEventRuntime の `PIXBeginEvent(command_list, color, name)` と `PIXEndEvent(command_list)` を使います（[Debug Layer](../directx/dx12/debug-layer.md)）。

## オーバードローを、自作で見える化する

エンジンの中に、デバッグ表示として、組み込めます。<strong>全ての物を、「1 回描くと、少しだけ足す」</strong>シェーダーで描き、色に変えます。

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

青なら 1〜2 重ね、緑・黄が、3〜5 重ね、赤なら 8 重ね以上、という見え方になります。赤い所（煙、草むら、UI の重ね）を、優先して減らします（[Overdraw](overdraw.md)）。

## フレーム時間を、グラフと数字で見る

平均だけを見ると、突発的な遅さ（スパイク）を、見逃します。<strong>最悪の値</strong>（99 パーセンタイルなど）も、あわせて表示します。

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

平均が 12 ms でも、99 パーセンタイルが 30 ms なら、ときどきカクつきます。<strong>平均ではなく、スパイクの原因</strong>（アセットの読み込み、シェーダーのコンパイル、ガベージ）を、探します（[フレーム時間の設計](../optimize/frame-budget.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- async-compute.md
pg.Add("../rendering/async-compute.md", '''
## D3D12 での実装

コンピュート キューを作って、グラフィックス キューと、フェンスでつなぎます（[Command Queue](../directx/dx12/command-queue.md)、[Fence](../directx/dx12/fence.md)）。

```cpp
// コンピュート キュー（描画と並列に走る）。
D3D12_COMMAND_QUEUE_DESC desc = {};
desc.Type = D3D12_COMMAND_LIST_TYPE_COMPUTE;
device->CreateCommandQueue(&desc, IID_PPV_ARGS(&compute_queue));
// コマンド アロケーターと、コマンド リストも、COMPUTE の種類で作る。
```

流れの例です。<strong>深度を描き終えたら、AO の計算を、コンピュート キューで始め</strong>、同時に、グラフィックス キューで、影を描きます。ライティングは、AO の完了を待ちます。

```cpp
// ① グラフィックス: 深度プリパス。
graphics_queue->ExecuteCommandLists(1, depth_prepass_list);
graphics_queue->Signal(fence.Get(), ++depth_done);            // 深度が、できた目印

// ② コンピュート: 深度を待って、AO を計算（GPU 同士の待ち。CPU は止まらない）。
compute_queue->Wait(fence.Get(), depth_done);
compute_queue->ExecuteCommandLists(1, ao_list);
compute_queue->Signal(fence.Get(), ++ao_done);                // AO が、できた目印

// ③ グラフィックス: AO と並列に、影マップを描く。
graphics_queue->ExecuteCommandLists(1, shadow_list);

// ④ グラフィックス: ライティングは、AO の完了を待ってから。
graphics_queue->Wait(fence.Get(), ao_done);
graphics_queue->ExecuteCommandLists(1, lighting_list);
```

②の `Wait` は、<strong>GPU 側の待ち</strong>で、CPU は止まりません。③の影マップは、AO と<strong>並列</strong>に、実行されます。

## リソースの扱い

コンピュート キューは、グラフィックス キューと、<strong>別のキュー</strong>なので、リソースの状態の扱いに、注意が要ります。

| 注意 | 内容 |
| --- | --- |
| 状態の遷移は、リストを実行するキューで | コンピュート キューは、描画用の状態（`RENDER_TARGET` など）への遷移が、できない |
| 深度を、読む前に | 深度を、`NON_PIXEL_SHADER_RESOURCE` へ遷移するバリアを、<strong>グラフィックス キューの、リストの最後に</strong>入れて、`Signal` する |
| 結果の、受け渡し | AO の出力は、`UNORDERED_ACCESS` で書き、ライティングで読む前に、`PIXEL_SHADER_RESOURCE` へ遷移（グラフィックス キュー側） |
| 同時に、触らない | 2 つのキューが、同じリソースを、同時に読み書きしない |

## 効果が出る場面と、出ない場面

| 状況 | 結果 |
| --- | --- |
| 影マップ（ALU が空く）と AO（ALU を使う） | 重なって、全体が速くなりやすい |
| 帯域を、使い切る処理どうし | 並列にしても、帯域を、奪い合って、速くならない |
| 1 つの処理が、GPU 全体を、使い切っている | 並列にする余地がない。順番に走るだけ |
| 同期（`Wait`）が、多すぎる | 待ちが、増えて、かえって遅くなる |

効果は、GPU の世代や、処理の内容で、大きく変わります。<strong>必ず、PIX の、タイミング キャプチャで、2 つのキューが、実際に重なって走っているか</strong>を確認し、フレーム時間を、導入前後で比べます。重なっていなければ、効果は、ありません（[調査ツール](tools.md)）。
''', before="## よくあるミス")

# ---------------------------------------------------------------- cases.md
pg.Add("../rendering/cases.md", '''
## 事例で、流れを追う

症状から、原因を特定し、直して、効果を確かめるまでの流れを、3 つの場面で見ます。数字は、考え方を示すための例（目安）です。

### 事例 1：森で、ドロー コールが 8,000 回

| 手順 | 内容 |
| --- | --- |
| 症状 | 森の場面で、24 ms（約 40 FPS）。他の場面は、12 ms |
| 切り分け | 解像度を半分にしても、24 ms のまま → <strong>CPU が原因</strong> |
| 計測 | プロファイラーで、描画の記録が、14 ms を占める。ドロー コールは約 8,000 回（木 3,000、草 4,000、岩 1,000） |
| 原因 | 木や草を、1 本ずつ、描いている |
| 直し方 | 同じメッシュを、インスタンスで、まとめる。木 5 種類 + 草 3 種類 + 岩 4 種類 = 12 回に |
| 結果 | 描画の記録が、14 ms → 1 ms。フレームは 11 ms に |
| 次の一手 | 視錐台と距離で、カリングして、見えない木を、インスタンスから、外す（[カリング](culling.md)） |

### 事例 2：ライトを 200 個にしたら、極端に重い

| 手順 | 内容 |
| --- | --- |
| 症状 | ライトを 20 個から 200 個に増やすと、GPU が、18 ms から 55 ms に |
| 切り分け | 解像度を、下げると速くなる → <strong>GPU のピクセル処理</strong> |
| 計測 | ライティングのパスが、重い。フォワード描画で、各ピクセルが、全 200 個のライトを、ループしている |
| 原因 | 全ピクセルが、画面全体の、全ライトを、計算している |
| 直し方 | ディファードにして、<strong>クラスタード方式</strong>で、各ピクセルに、影響するライトだけを、渡す |
| 結果 | ライティングが、40 ms → 6 ms |
| 次の一手 | G バッファの、帯域が、次の壁になる。フォーマットを軽くする（[帯域幅](bandwidth.md)） |

### 事例 3：魔法のエフェクトで、60 FPS が 35 FPS に

| 手順 | 内容 |
| --- | --- |
| 症状 | 魔法の煙を出すと、フレームが、9 ms から 28 ms に |
| 切り分け | 解像度を、下げると、大きく速くなる → GPU のピクセル処理か、帯域 |
| 計測 | オーバードローの可視化で、煙の部分が、真っ赤（10 重ね以上）。1 枚が、画面の 3 分の 2 を覆っている |
| 原因 | 大きな半透明の板を、フル解像度で、10 枚以上、重ねている。1080p で、20 M ピクセル以上、ブレンド（読み書き）している |
| 直し方 | 煙を、半分の解像度の、縮小バッファに描いて、最後に合成。板の数を、10 枚から 5 枚に |
| 結果 | 煙のコストが、約 1/8 に。フレームは 11 ms に |
| 次の一手 | 見た目の差を、確認する。縁がにじむなら、深度を考慮した拡大（[パーティクル](particles.md)） |

3 つに共通するのは、<strong>① 切り分け → ② 計測 → ③ 原因 → ④ 直す → ⑤ 測り直す</strong>の順です。勘で直さず、数字で確かめます。
''', before="## 全体のよくあるミス")
print("ok")
