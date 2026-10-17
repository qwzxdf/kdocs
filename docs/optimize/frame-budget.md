---
title: フレーム時間の設計
tags:
  - 最適化
---

# フレーム時間の設計

ゲームは、**1 秒に 60 回**（**1 フレーム ≒ 16.6 ミリ秒**）、更新と描画を終える必要があります。**平均が速くても、たまに遅いフレームがあると、カクつき**として見えます。このページは、**フレームの時間を、どう配分するか**（フレームバジェット）、**固定タイムステップ**、**スパイク（突然の遅いフレーム）を防ぐ方法**、**処理を分散させる考え方**をまとめます。

!!! tip "ポイント"
    - <strong>60 FPS ＝ 16.6 ms、30 FPS ＝ 33.3 ms、120 FPS ＝ 8.3 ms。</strong>この時間の中に、すべてを収める。
    - <strong>システムごとに、時間の予算（バジェット）</strong>を決める（更新 5 ms、描画 8 ms ...）。
    - 見るのは<strong>平均でなく、最悪のフレーム</strong>。<strong>1 フレームの遅れが、体感を壊す</strong>。
    - <strong>物理は固定タイムステップ</strong>、描画は可変。<strong>`dt` の上限</strong>を決める（長い停止のあとの暴走を防ぐ）。
    - <strong>重い処理は、複数フレームに分散</strong>する（毎フレーム少しずつ）。<strong>見えない・遠いものは、更新頻度を下げる</strong>。
    - <strong>毎フレームのヒープ確保、ファイル読み込み、シェーダーのコンパイル</strong>は、スパイクの定番。

## フレーム時間の目安

| 目標 | 1 フレームの時間 |
| --- | --- |
| 30 FPS | 33.3 ms |
| **60 FPS** | **16.6 ms** |
| 120 FPS | 8.3 ms |
| 144 FPS | 6.9 ms |

**FPS（1 秒あたりの枚数）で比べず、ミリ秒で考える**と、足し算ができます。「60 → 55 FPS」の落ち込みは 1.5 ms、「30 → 25 FPS」の落ち込みは 6.7 ms で、**FPS の差は、同じでも、時間の差は違います**。

## フレームバジェット

**フレームの時間を、システムごとに配分**します。

| システム | 予算の例（60 FPS） |
| --- | --- |
| 入力・ゲームロジック | 3 ms |
| 物理 | 3 ms |
| アニメーション | 1.5 ms |
| 描画（CPU：コマンドの作成） | 4 ms |
| 描画（GPU） | 13 ms（CPU と並行） |
| オーディオ・その他 | 1 ms |
| <strong>余裕（スパイク用）</strong> | **2〜3 ms** |

| ルール | 説明 |
| --- | --- |
| **余裕を残す** | 16.6 ms ぎりぎりでは、少しの遅れで、フレームを落とす。**80% くらい**を目標に |
| **CPU と GPU は別々に見る** | CPU が 8 ms でも、GPU が 20 ms なら、フレームは、20 ms かかる |
| **一番遅い方が、フレーム時間を決める** | CPU と GPU は並行して動く（パイプライン）。**遅い側**が、限界 |
| **予算を超えたら、すぐ分かるように** | 画面に、システムごとの時間を表示する |

### 測って表示する

```cpp
class FrameTimer {
 public:
  void Begin() { start_ = std::chrono::steady_clock::now(); }

  float EndMs() {
    auto end = std::chrono::steady_clock::now();
    return std::chrono::duration<float, std::milli>(end - start_).count();
  }

 private:
  std::chrono::steady_clock::time_point start_;
};
```

**フレームの時間を、折れ線グラフ**にして、**スパイクが見える**ようにします（[計測](measure.md)、[Dear ImGui](../libs/imgui/index.md)）。

## 平均より、最悪値

<svg class="fig" viewBox="0 0 560 220" role="img" aria-label="フレーム時間のスパイク"><line x1="40" y1="180" x2="540" y2="180" stroke="currentColor" stroke-width="2"/><line x1="40" y1="130" x2="540" y2="130" stroke="currentColor" stroke-dasharray="5 4"/><text x="548" y="134" style="font-size:11px">16.6 ms</text><rect x="60" y="150" width="40" height="30" fill="#4c8bf5"/><rect x="126" y="147" width="40" height="33" fill="#4c8bf5"/><rect x="192" y="150" width="40" height="30" fill="#4c8bf5"/><rect x="258" y="147" width="40" height="33" fill="#4c8bf5"/><rect x="324" y="45" width="40" height="135" fill="#e5484d"/><rect x="390" y="150" width="40" height="30" fill="#4c8bf5"/><rect x="456" y="147" width="40" height="33" fill="#4c8bf5"/><text x="62" y="198">10 ms</text><text x="128" y="198">11 ms</text><text x="194" y="198">10 ms</text><text x="260" y="198">11 ms</text><text x="326" y="198">45 ms</text><text x="392" y="198">10 ms</text><text x="458" y="198">11 ms</text><text x="40" y="20" class="fig-title">平均 12 ms（60 FPS に収まる）でも、45 ms の 1 フレームが、カクつきとして見える</text></svg>

| 指標 | 意味 |
| --- | --- |
| **平均フレーム時間** | 全体の傾向 |
| <strong>最悪（最大）</strong> | スパイクの大きさ |
| <strong>99 パーセンタイル（1% ロー）</strong> | **遅い方から 1% のフレーム**の時間。カクつきの指標として、よく使う |

**目標は、最悪値を、予算内に収める**ことです。

## スパイクの原因

| 原因 | 対策 |
| --- | --- |
| **ヒープ確保・解放** | **毎フレームの確保をやめる**（[毎フレームのヒープ確保を避ける](frame-allocation.md)） |
| **ファイル読み込み** | **非同期ロード**、先読み（[ロード時間](loading.md)） |
| **シェーダー・パイプラインのコンパイル** | 事前にコンパイル、**起動時に作る**、キャッシュ |
| **ガベージコレクション相当**（大量の一括解放） | まとめて解放せず、分散する |
| **ログ・ファイル書き込み** | バッファに貯めて、別スレッドで書く |
| **ロックの待ち** | ロックを短く、ロックしない設計（[マルチスレッド化](multithreading.md)） |
| **OS・ほかのプロセス** | 計測で見分ける。電源設定、バックグラウンド処理 |
| **ページフォールト**（初めて触るメモリ） | 起動時に、一度触っておく |
| <strong>垂直同期（VSync）</strong> | 16.6 ms に、待たされる。**計測するときは、切る** |
| **初回の描画・初回の使用** | ウォームアップ（最初に、1 回、ダミーで動かす） |

## 固定タイムステップ

<strong>物理・ゲームロジックは、一定の `dt`（例：1/60 秒）</strong>で動かすと、**挙動が、フレームレートに依存しません**。描画は、速さに合わせます。

```cpp
constexpr float kFixedDt = 1.0f / 60.0f;
constexpr float kMaxFrameTime = 0.25f;

float accumulator = 0.0f;
auto previous = Clock::now();

while (running) {
  auto now = Clock::now();
  float frame_time = std::chrono::duration<float>(now - previous).count();
  previous = now;

  frame_time = std::min(frame_time, kMaxFrameTime);
  accumulator += frame_time;

  while (accumulator >= kFixedDt) {
    FixedUpdate(kFixedDt);
    accumulator -= kFixedDt;
  }

  float alpha = accumulator / kFixedDt;
  Render(alpha);
}
```

| 要素 | 説明 |
| --- | --- |
| **`accumulator`** | 溜まった時間。`kFixedDt` ごとに、1 回更新 |
| <strong>`kMaxFrameTime`（上限）</strong> | <strong>長い停止（デバッガーで止めた、ウィンドウを動かした）のあとに、何十回も更新して、さらに遅くなる「死のスパイラル」</strong>を防ぐ |
| <strong>`alpha`（補間）</strong> | 描画を、前の更新と今の更新の間で補間して、滑らかにする |

### 死のスパイラル

更新が重くて、1 回の更新が `kFixedDt` より長くかかると、**溜まる時間が増え、さらに更新が増え、永遠に追いつけません**。対策は、<strong>上限（`kMaxFrameTime`）</strong>と、**1 フレームの最大更新回数**を決めることです。

詳しくは、[ゲームループ](../engine/game-loop.md)にも書いてあります。

## 処理の分散

**重い処理を、1 フレームで全部やらず**、**複数フレームに分けて**、毎フレームの負荷を一定にします。

| 方法 | 説明 | 例 |
| --- | --- | --- |
| **時間スライス** | 1 フレームに、処理する量を決める | 経路探索を、1 フレーム 0.5 ms まで |
| **ラウンドロビン** | N 個を、毎フレーム 1/N ずつ更新 | 敵 100 体を、毎フレーム 10 体ずつ AI 更新 |
| **更新頻度を下げる** | 遠い・見えないものは、低頻度で | 遠い敵は、10 フレームに 1 回更新 |
| **キュー** | 要求を溜めて、予算の範囲で処理 | 爆発エフェクトの生成を、1 フレーム 3 個まで |
| <strong>非同期（別スレッド）</strong> | メインスレッドから外す | ロード、経路探索（[マルチスレッド化](multithreading.md)） |
| **キャッシュ** | 結果を覚えて、再計算しない | 経路、視線の判定結果 |

```cpp
void UpdateAi(std::span<Enemy> enemies, int frame_index) {
  constexpr int kGroups = 8;
  for (size_t i = 0; i < enemies.size(); ++i) {
    if (static_cast<int>(i % kGroups) == frame_index % kGroups) {
      enemies[i].ThinkSlow();
    }
    enemies[i].MoveFast();
  }
}
```

**遅い AI の思考**を、8 フレームに 1 回にして、**移動のような軽い処理**は、毎フレーム行う例です。

## 動的な調整

| 方法 | 説明 |
| --- | --- |
| **LOD** | 遠くは、簡単なモデル・簡単な計算 |
| **品質設定** | 影・エフェクトの量を、設定で変える |
| **動的解像度** | 重いとき、描画の解像度を下げて、フレームを守る |
| **負荷の監視** | フレーム時間が予算を超えたら、エフェクトを減らす |

## よくあるミス

??? failure "平均 FPS だけで、判断している"
    カクつきは、**最悪のフレーム**です。**フレーム時間のグラフ**と、**99 パーセンタイル**を見ます。

??? failure "`dt` に上限がなく、デバッガーで止めたあと、ゲームが暴走する"
    `dt` を `kMaxFrameTime` で制限します。

??? failure "VSync をつけたまま、速さを測る"
    VSync がフレーム時間を 16.6 ms にそろえるので、**速度が分かりません**。測るときは、切ります。

??? failure "更新が重くて、固定タイムステップが追いつかない（死のスパイラル）"
    更新の最大回数を決め、**更新自体を軽く**します。

??? failure "全部の敵を、毎フレーム、全力で更新している"
    時間スライス、更新頻度の低下で、**負荷を分散**します。

??? failure "予算ぎりぎりで作って、少しの遅れで、フレームを落とす"
    **2〜3 ms の余裕**を残します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>60 FPS ＝ 16.6 ms</strong>。<strong>ミリ秒で考えて、システムごとに予算</strong>を配分。<strong>余裕を残す</strong>
    - [x] 見るのは<strong>最悪値・99 パーセンタイル</strong>。<strong>1 フレームのスパイク</strong>が、カクつき
    - [x] スパイクの定番は<strong>ヒープ確保・ファイル読み込み・シェーダーのコンパイル</strong>
    - [x] <strong>固定タイムステップ + `dt` の上限</strong>で、暴走と死のスパイラルを防ぐ
    - [x] 重い処理は、<strong>複数フレームに分散</strong>。<strong>遠いものは、更新頻度を下げる</strong>

## 関連ページ

- [最適化の進め方](index.md)
- [計測（プロファイリング）](measure.md)
- [毎フレームのヒープ確保を避ける](frame-allocation.md)
- [ロード時間・起動時間](loading.md)
- [ゲームループ](../engine/game-loop.md)
- [プロファイラー（Visual Studio）](../vs/profiler.md)
