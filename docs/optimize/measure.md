---
title: 計測（プロファイリング）
tags:
  - 最適化
---

# 計測（プロファイリング）

最適化で一番大切なのは、<strong>「どこが遅いのか」を、数字で知る</strong>ことです。人間の勘は、よく外れます。「この関数が重そう」と思っていた場所が、実は全体の 1% で、本当の原因は別の場所にあった、ということは、普通に起きます。計測（プロファイリング）は、プログラムの時間やメモリの使われ方を測って、ボトルネック（一番足を引っ張っている場所）を見つける作業です。

!!! tip "ポイント"
    - <strong>Release ビルド</strong>（最適化あり）で測る。Debug の結果は、製品の速さとは別物。
    - まず<strong>フレーム時間</strong>を画面に出す。平均ではなく、最悪のフレームを見る。
    - 次に、プロファイラーで「どの関数が、全体の何 % か」を見る。上位から直す。
    - 細かい区間は、自作のタイマーで測る（`ScopedTimer`）。
    - 測る条件をそろえる（同じステージ、同じ場所、同じ PC）。1 回の結果で判断せず、数回測る。

!!! info "このページを読む前に"
    - [optimize/index.md](index.md)（このセクション全体の地図と、読む順番）

## 測るもの

| 測るもの | 単位 | 何が分かるか |
| --- | --- | --- |
| **フレーム時間** | ミリ秒 | 1 フレームにかかる時間。60 FPS なら 16.6 ms 以内 |
| 関数ごとの時間 | ミリ秒・% | どの関数が重いか |
| CPU と GPU の時間 | ミリ秒 | CPU が遅いのか、GPU が遅いのか（[描画の最適化](../rendering/index.md)） |
| メモリ使用量 | MB | 増え続けていないか（リーク）。大きすぎないか |
| メモリ確保の回数 | 回 | 毎フレームの確保が多くないか |
| ロード時間 | 秒 | どのファイルの読み込みが遅いか |

## 1. フレーム時間を表示する

最初にやることです。**画面の隅に、フレーム時間（ミリ秒）とグラフ**を出します。

```cpp
#include <chrono>

class FrameTimer {
 public:
  // 毎フレームの最初に呼ぶ。直前のフレームの時間（ミリ秒）を返す
  double Tick() {
    auto now = std::chrono::steady_clock::now();
    double ms = std::chrono::duration<double, std::milli>(now - last_).count();
    last_ = now;
    return ms;
  }

 private:
  std::chrono::steady_clock::time_point last_ = std::chrono::steady_clock::now();
};
```

| 見方 | 説明 |
| --- | --- |
| 平均だけを見ない | 平均 5 ms でも、たまに 50 ms のフレームがあると、カクつく |
| 最大・95 パーセンタイル | 悪い方から 5% のフレームの時間。滑らかさの指標 |
| グラフ（折れ線） | 重いフレームが、山として見える。[Dear ImGui](../libs/imgui/index.md) の `PlotLines` が便利 |
| 目標 | 60 FPS = 16.6 ms、30 FPS = 33.3 ms、144 FPS = 6.9 ms |

## 2. プロファイラーを使う

**プロファイラー**は、プログラムを実行しながら、「どの関数が、どれだけの時間を使ったか」を記録する道具です。

### Visual Studio のパフォーマンス プロファイラー

1. Release 構成でビルドする（デバッグ情報付きがおすすめ：リンカー → デバッグ情報の生成 → 「はい」）
2. メニュー「デバッグ → パフォーマンス プロファイラー」（Alt + F2）
3. CPU 使用率 にチェックを入れて「開始」
4. ゲームを、遅い場面で数十秒遊んで、終了する
5. レポートで、「ホット パス」（時間を使っている関数の流れ）を見る

| 見る項目 | 意味 |
| --- | --- |
| 自己 CPU | その関数自身が使った時間（中で呼んだ関数を除く）。ここが大きい関数が、直す候補 |
| 合計 CPU | その関数と、中で呼んだ関数の合計。呼び出しの流れを見るのに使う |
| ホット パス | 時間を一番使っている、呼び出しの経路 |
| 呼び出し元 / 呼び出し先 | 関数をクリックして、誰が呼んでいるか、何を呼んでいるかをたどる |

### ほかのプロファイラー

| 道具 | 特徴 |
| --- | --- |
| Tracy | ゲーム向け。フレームごとの時間の流れが、タイムラインで見える。コードに `ZoneScoped` を書く。無料 |
| Superluminal | 見やすく、使いやすい。有料（学生向けの無料枠あり） |
| RenderDoc | 描画（GPU）の、1 フレームを分解して見る。無料（[描画の最適化](../rendering/index.md)） |
| PIX（Microsoft） | DirectX 用の、GPU・CPU の解析。無料 |
| Intel VTune / AMD uProf | CPU の命令レベルの解析（キャッシュミスなど） |

## 3. 自作のタイマーで区間を測る

プロファイラーで「`Update` が重い」と分かったら、その中を、さらに細かく測ります。

```cpp
#include <chrono>
#include <print>

// スコープの時間を測って、破棄されるときに表示する（RAII）
class ScopedTimer {
 public:
  explicit ScopedTimer(const char* name)
      : name_(name), start_(std::chrono::steady_clock::now()) {}
  ~ScopedTimer() {
    double ms = std::chrono::duration<double, std::milli>(
                    std::chrono::steady_clock::now() - start_).count();
    std::println("{}: {:.3f} ms", name_, ms);
  }

 private:
  const char* name_;
  std::chrono::steady_clock::time_point start_;
};

void Update() {
  {
    ScopedTimer t("AI");
    UpdateAI();
  }
  {
    ScopedTimer t("Physics");
    UpdatePhysics();
  }
}
```

- 結果を `println` で毎フレーム出すと、それ自体が遅く、見にくいです。**数フレームぶんを平均して、画面に出す**とよいです
- `std::chrono::steady_clock` を使います（`system_clock` は時計が巻き戻ることがある）

## 4. ベンチマーク（小さな処理の速さ比べ）

「`vector` と `list`、どちらが速いか」のような、**小さな処理の比較**には、ベンチマークを書きます。

| ライブラリ | 特徴 |
| --- | --- |
| Google Benchmark | 一番有名。繰り返し回数を自動で決めて、統計を出す。vcpkg: `benchmark` |
| nanobench | ヘッダ 1 つ。簡単 |
| Compiler Explorer の Quick Bench（quick-bench.com） | ブラウザで、2 つの書き方を比べられる |

### ベンチマークの注意

| 落とし穴 | 対策 |
| --- | --- |
| 結果を使わないと、コンパイラが処理を消す | 結果を `benchmark::DoNotOptimize()` などで「使った」ことにする |
| 1 回だけ測る | 数百〜数万回くり返して、平均とばらつきを見る |
| Debug で測る | Release で測る |
| キャッシュが温まっている（2 回目以降が速い） | 実際のゲームに近い状態（データの量・順番）で測る |
| 小さいデータだけで測る | 実際に使う大きさで測る。大きさで勝者が変わることがある |
| 他のアプリが動いている | ブラウザなどを閉じて、電源設定を高パフォーマンスにする |

## 5. メモリを測る

| 道具 | 何が分かるか |
| --- | --- |
| <strong>Visual Studio の「診断ツール」</strong>（デバッグ中に表示） | メモリ使用量の推移、スナップショットの比較 |
| 「メモリ使用量」プロファイラー（Alt + F2） | どのクラスが、どれだけメモリを使っているか |
| 自作のカウンター | `new` をフックして、確保の回数とバイト数を数える（[std::allocator](../stl/memory/allocator.md)） |
| AddressSanitizer | メモリのバグ（リークではなく、範囲外・解放後使用） |
| CRT のリーク検出（`_CrtDumpMemoryLeaks()`） | 終了時に、解放されていないメモリを報告（Debug） |

詳しくは [メモリ使用量](memory-usage.md) を見てください。

## 結果の読み方

| 状況 | 考えること |
| --- | --- |
| **1 つの関数が、全体の 50% 以上** | そこを直せば、大きく効く。アルゴリズム・メモリ・確保を疑う |
| 同じくらいの関数が、たくさん並ぶ（平らな分布） | 1 か所を直しても効かない。設計全体（データの並び、処理の回数）を見直す |
| 標準ライブラリの関数が上位（`vector::push_back`、`operator new`） | 使い方が悪い（確保が多い、コピーが多い）。呼んでいる側を直す |
| CPU 時間は小さいのに、フレームが遅い | GPU 待ちか、スレッドの待ち（ロック）か、vsync。GPU プロファイラーも見る |
| たまに重いフレームがある | 確保（`vector` の再確保）、ロード、ガベージ的な処理。時間の履歴を見る |

## ゲームでの使いどころ

| 場面 | 方法 |
| --- | --- |
| 開発中ずっと | フレーム時間とグラフを、画面の隅に出しておく（[ログとデバッグ支援](../design/practice/logging-debug.md)） |
| 遅いステージを調べる | Visual Studio の CPU プロファイラーで、その場面を数十秒測る |
| 毎フレームの内訳を見る | Tracy の `ZoneScoped` を、主要な関数に書く |
| コンテナの選び方で迷う | ベンチマークで、実際のデータ量で比べる |
| 製品版の前 | 実機（最低スペックの PC）で測る。開発 PC より遅い |

<!-- fig:amdahl-bars:begin -->

<svg class="fig illust motion" data-fig="amdahl-bars" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-amdahl-bars" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">全体の 50% を占める所を 2 倍速くするほうが、30% の所より効く</text>
<g opacity="1"><text x="70" y="92" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">今の状態（100）</text>
<rect x="70" y="100" width="270.0" height="44" fill="#2563eb" opacity="0.9"/>
<text x="205.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">A 50</text>
<rect x="340.0" y="100" width="162.0" height="44" fill="#2ea043" opacity="0.9"/>
<text x="421.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">B 30</text>
<rect x="502.0" y="100" width="108.0" height="44" fill="#e5aa28" opacity="0.9"/>
<text x="556.0" y="128" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">C 20</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="0;0;1;1"/><text x="70" y="122" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">B を 2 倍速く → 85</text>
<rect x="70" y="130" width="270.0" height="44" fill="#2563eb" opacity="0.9"/>
<text x="205.0" y="158" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">A 50</text>
<rect x="340.0" y="130" width="81.0" height="44" fill="#2ea043" opacity="0.9"/>
<text x="380.5" y="158" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">B 15</text>
<rect x="421.0" y="130" width="108.0" height="44" fill="#e5aa28" opacity="0.9"/>
<text x="475.0" y="158" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">C 20</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/><text x="70" y="212" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">A を 2 倍速く → 75</text>
<rect x="70" y="220" width="135.0" height="44" fill="#2563eb" opacity="0.9"/>
<text x="137.5" y="248" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">A 25</text>
<rect x="205.0" y="220" width="162.0" height="44" fill="#2ea043" opacity="0.9"/>
<text x="286.0" y="248" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">B 30</text>
<rect x="367.0" y="220" width="108.0" height="44" fill="#e5aa28" opacity="0.9"/>
<text x="421.0" y="248" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">C 20</text>
</g>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A 50、B 30、C 20(合計 100)の処理がある<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">B を半分にしても、全体は 85。15 しか減らない<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A を半分にすると、全体は 75。25 減る → 重い所から直す<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:amdahl-bars:end -->

## よくあるミス

??? failure "Debug ビルドで測る"
    最適化がなく、`vector` の範囲チェックなども入るので、何倍も遅くなります。しかも、**遅くなる割合が関数ごとに違う**ので、ボトルネックの場所すら変わります。必ず Release で測ります。

??? failure "平均 FPS だけを見る"
    平均が 60 でも、たまに 100 ms のフレームがあれば、カクつきます。最悪のフレームや、フレーム時間の履歴を見ます。

??? failure "測る処理が、測定自体で遅くなる"
    細かい区間を何千か所も測ると、タイマーの呼び出しが、処理より重くなります。大きな区間から測り、絞り込んでいきます。

??? failure "1 回の結果で、速くなったと判断する"
    PC の状態（温度、他のアプリ）で、結果はぶれます。数回測って、ばらつきを見ます。

??? failure "開発 PC だけで測る"
    プレイヤーの PC は、もっと遅いかもしれません。最低スペックの環境でも、確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Release で、同じ条件で、数回測る
    - [x] フレーム時間は画面に出し、<strong>最悪のフレーム</strong>を見る
    - [x] プロファイラーで、自己 CPU の大きい関数から直す
    - [x] 細かい区間は、`ScopedTimer`。小さな処理の比較は、ベンチマーク
    - [x] 直したら、また測って、速くなったか確認する

## 関連ページ

- [最適化の進め方](index.md)
- [ログとデバッグ支援の設計](../design/practice/logging-debug.md)
- [描画の最適化](../rendering/index.md)
- [メモリ使用量](memory-usage.md)
- [RAII](../design/patterns/raii.md)
- [パフォーマンス プロファイラー（Visual Studio）](../vs/profiler.md)
- [フレーム時間の設計](frame-budget.md)
