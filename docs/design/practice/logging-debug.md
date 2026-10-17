---
title: ログとデバッグ支援の設計
tags:
  - 設計
  - 実践
---

# ログとデバッグ支援の設計

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

バグが起きたとき、<strong>「何が起きたのか」を知る手がかり</strong>があるかどうかで、直す時間が大きく変わります。その手がかりが**ログ**（記録）と、**デバッグ支援の仕組み**（assert、デバッグ描画、デバッグ メニューなど）です。ゲームは、**自分の PC では動くのに、友達の PC では落ちる**、**1 時間遊ぶと、たまにおかしくなる**、といった「再現しにくいバグ」が多いので、**あとから見られる記録**が特に役立ちます。「`println` を、あちこちに書いては消す」のではなく、**最初から、ログとデバッグ支援を設計に入れておく**と、開発がずっと楽になります。

!!! tip "ポイント"
    - `println` を直接書かず、<strong>ログ関数（レベル付き）</strong>を作る。`Info`、`Warning`、`Error`、`Debug` のように、**重要度**で分ける。
    - ログは、**画面・ファイル・デバッガー**など、**出力先を切り替えられる**ようにする。
    - 製品版では、**デバッグ ログを出さない**（ビルド設定で消す）。
    - **assert** は「あり得ない状態」を、すぐに検出する。**エラー処理**とは別（ユーザーの入力ミスなどは、assert ではなくエラー処理）。
    - **デバッグ描画**（当たり判定の形、AI の視線）と、**デバッグ メニュー**（[Dear ImGui](../../libs/imgui/index.md)）が、あると、バグ探しが速い。
    - ログには、**時刻・種類・場所・メッセージ**を入れる。**どこで・何が**が分かるようにする。

## ログの設計

### ログ レベル

| レベル | 使いどころ | 例 |
| --- | --- | --- |
| **Fatal / Critical** | 続行できない致命的エラー | 「必須のファイルが無い」 |
| **Error** | 失敗した（続行はできる） | 「テクスチャの読み込みに失敗：boss.png」 |
| **Warning** | おかしいが、動いている | 「HP が負になった。0 に補正した」 |
| **Info** | 大事な出来事 | 「ステージ 3 を開始」「セーブ完了」 |
| **Debug** | 開発中だけ見たい詳しい情報 | 「敵 #12 の状態が Idle → Chase」 |
| **Trace** | 毎フレーム出るような、最も細かい情報 | 「Update: dt=0.016」 |

出力するレベルを**設定で切り替える**ようにします（普通は、開発では `Debug` 以上、製品版では `Info` か `Warning` 以上）。

### 最小のログ関数

```cpp
#include <format>
#include <print>
#include <source_location>
#include <string_view>

enum class LogLevel { kDebug, kInfo, kWarning, kError };

class Logger {
 public:
  static void SetMinLevel(LogLevel level) { min_level_ = level; }

  template <class... Args>
  static void Write(LogLevel level, std::format_string<Args...> fmt, Args&&... args) {
    if (level < min_level_) {
      return;                                         // 設定より軽いレベルは出さない
    }
    std::println("[{}] {}", Name(level), std::format(fmt, std::forward<Args>(args)...));
  }

 private:
  static constexpr std::string_view Name(LogLevel l) {
    switch (l) {
      case LogLevel::kDebug: return "DEBUG";
      case LogLevel::kInfo: return "INFO";
      case LogLevel::kWarning: return "WARN";
      case LogLevel::kError: return "ERROR";
    }
    return "?";
  }
  inline static LogLevel min_level_ = LogLevel::kDebug;
};

// 使いやすいマクロ（場所の情報を足す）
#define LOG_INFO(...)  Logger::Write(LogLevel::kInfo, __VA_ARGS__)
#define LOG_ERROR(...) Logger::Write(LogLevel::kError, __VA_ARGS__)
```

```cpp
LOG_INFO("ステージ {} を開始", stage_id);
LOG_ERROR("テクスチャの読み込みに失敗: {}", path);
```

`std::format` の書式が使えるので、型安全で、`printf` のような書式ミスがありません（[format](../../stl/utilities/format.md)）。

### 出力先を切り替える（シンク）

| 出力先 | 用途 |
| --- | --- |
| **コンソール** | 開発中。色分けすると見やすい |
| **ファイル** | **製品版・テスト プレイ**。後から見られる（`log.txt`） |
| **デバッガーの出力ウィンドウ** | Visual Studio で、実行中に見る（`OutputDebugStringA`） |
| **画面の中**（ゲーム内のコンソール） | ゲームを遊びながら見る（[Dear ImGui](../../libs/imgui/index.md) のログ ウィンドウ） |
| **ネットワーク** | 遠隔の PC のログを集める（オンライン ゲーム） |

出力先を**インターフェース**（`ILogSink`）にして、複数を同時に使えるようにすると、あとから足せます（[インターフェース設計](../foundations/interface-design.md)）。

### ログに何を入れるか

| 項目 | 説明 |
| --- | --- |
| **時刻**（またはフレーム番号） | いつ起きたか。順番が分かる |
| **レベル** | 重要度 |
| **場所**（ファイル名・行・関数名） | `std::source_location` で自動取得（[source_location](../../stl/support/source_location.md)） |
| **メッセージ** | 何が起きたか。**値も入れる**（「失敗」だけでなく「何を、なぜ」） |
| **スレッド ID** | マルチスレッドのとき、どのスレッドか |

```text
[12:03:41.250] [ERROR] [texture.cpp:42] テクスチャの読み込みに失敗: assets/boss.png (ファイルが見つかりません)
```

### ログのルール

| ルール | 理由 |
| --- | --- |
| **ログだけで、状況が分かる書き方にする** | 「失敗」ではなく、「何を（パス）、なぜ（原因）」 |
| **毎フレーム出るログは、Trace レベルにする** | 画面が埋まる。ファイルも巨大になる。速度も落ちる |
| **ログの出し過ぎ・出さなさ過ぎを避ける** | 出しすぎると、大事なものが埋もれる。足りないと、原因が分からない |
| **個人情報・パスワードを出さない** | ログは、人に送られることがある |
| **ログ出力の失敗で、ゲームを落とさない** | ファイルに書けなくても、続行する |
| **製品版でも、Error / Warning はファイルに残す** | 遊んだ人の不具合報告に、ログを添えてもらえる |

## assert（「あり得ない」を検出する）

**assert** は、「**ここは、絶対にこうなっているはず**」という**前提**を書いて、破られたらすぐに止める仕組みです。プログラムの**バグ**（作り手のミス）を見つけるためのものです。

```cpp
#include <cassert>

void Heal(Player* player, int amount) {
  assert(player != nullptr);        // 呼ぶ側の間違い（バグ）
  assert(amount >= 0);              // 負の回復は、設計上あり得ない
  player->hp = std::min(player->hp + amount, player->max_hp);
}
```

| 項目 | assert | エラー処理（`if` + 戻り値・例外） |
| --- | --- | --- |
| 対象 | **プログラマーのミス**（あり得ないはずの状態） | **起こり得る失敗**（ファイルが無い、入力ミス） |
| Release | **無効になる**（何もしない） | 常に有効 |
| 失敗したとき | プログラムを止める（デバッガーで原因が見える） | 呼び出し元に伝えて、処理を続ける |
| 例 | 引数が `nullptr` でないはず | ファイルが開けなかった |

!!! warning "assert の中に、副作用のあるコードを書かない"
    `assert(Load() == true);` のように、**処理本体を assert の中に書く**と、Release で `Load()` が呼ばれなくなります。処理は外で行い、**結果だけを assert**します。

自作の assert（メッセージ付き、Release でもログに出す）を作るチームも多いです。`static_assert`（コンパイル時のチェック）も使います（`static_assert(sizeof(Header) == 16);`）。

## デバッグ支援の仕組み

| 仕組み | 説明 |
| --- | --- |
| **デバッグ描画** | 当たり判定の形、AI の視線・経路、物理の接触点を、線で画面に出す。**見えるだけでバグが分かる** |
| **デバッグ メニュー**（[ImGui](../../libs/imgui/index.md)） | 実行中に、パラメータを変える・ステージを飛ぶ・無敵にする・敵を出す |
| **フレーム時間のグラフ** | 重いフレームが、すぐ見える |
| **オブジェクトのインスペクター** | 選んだ敵の状態（HP、状態、位置）を、ウィンドウに出す |
| **チート・デバッグ コマンド** | コンソールに `spawn boss` と打って、敵を出す。テストが速くなる |
| **一時停止・コマ送り** | 1 フレームずつ進めて、動きを確認する |
| <strong>再現用の記録（リプレイ・シード）</strong> | 乱数のシードと入力を記録して、バグを**再現**できるようにする |
| **クラッシュ ダンプ** | 落ちたときの状態を、ファイルに残す（Windows の Minidump） |

### デバッグ用のコードを、製品版から消す

```cpp
#ifdef _DEBUG
  DrawColliders();          // デバッグ描画：Debug ビルドでだけ有効
#endif

// または、自作のマクロ
#if defined(ENABLE_DEBUG_UI)
  ImGui::ShowDemoWindow();
#endif
```

| 方法 | 説明 |
| --- | --- |
| **`_DEBUG`**（MSVC の Debug ビルドで自動定義） | Debug だけ有効 |
| **自作のマクロ**（`ENABLE_DEBUG_UI`） | Release でも、開発用ビルドで有効にできる（「Development」構成） |
| **`NullDebugDraw`**（何もしないクラス） | `IDebugDraw` を差し替える（[インターフェース設計](../foundations/interface-design.md)）。`#ifdef` が散らばらない |

「Debug（遅い）」と「Release（製品）」の間に、<strong>「Development」（速いが、デバッグ機能あり）</strong>という構成を作るチームも多いです。Debug は遅すぎて、ゲームとして遊べないことがあるためです。

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| リソースの読み込み失敗 | Error ログに、**パスと原因**。代わりのリソース（ピンクのテクスチャ）で続行する |
| 状態の遷移（ステートマシン） | Debug ログに「Idle → Chase」。バグ追跡に役立つ |
| ネットワーク | 送受信のメッセージを Trace で記録 |
| テスト プレイ | ログと、直近のフレームの入力をファイルに残して、報告に添付 |
| 当たり判定がおかしい | デバッグ描画で、判定の形を表示 |
| 落ちるバグ | assert と、ダンプ ファイル。Visual Studio で、ダンプを開いて、落ちた行を見る（[デバッグ](../../vs/debugging.md)） |

## よくあるミス

??? failure "`println` を、あちこちに直接書く"
    出力先も、レベルも切り替えられず、製品版に残ります。ログ関数を通します。

??? failure "毎フレーム、ログを大量に出す"
    ファイルが巨大になり、遅くもなります。毎フレームのものは Trace にして、普段は出しません。

??? failure "assert で、ユーザーの間違いを扱う"
    ファイルが無い、入力が不正、のような**起こり得ること**を assert にすると、Release で無視されて、おかしな動きになります。エラー処理にします（[エラー処理の方針](../foundations/error-handling.md)）。

??? failure "ログに、必要な情報が足りない"
    「読み込みに失敗」だけでは、どのファイルか分かりません。**何を、なぜ**を書きます。

??? failure "ログを、製品版で一切残さない"
    プレイヤーから不具合の報告があっても、手がかりがありません。Error / Warning は、ファイルに残します（個人情報は除く）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `println` を直接書かず、**レベル付きのログ関数**を通す。出力先は切り替えられるように
    - [x] ログには、**時刻・レベル・場所・何が・なぜ**を入れる
    - [x] assert は「あり得ないはず」の検出。起こり得る失敗は、エラー処理
    - [x] デバッグ描画・デバッグ メニュー・コンソールを、最初から設計に入れる
    - [x] 製品版では、デバッグ機能とデバッグ ログを消し、Error / Warning は残す

## 関連ページ

- [エラー処理の方針](../foundations/error-handling.md)
- [デバッグのやり方（Visual Studio）](../../vs/debugging.md)
- [Dear ImGui](../../libs/imgui/index.md)
- [std::format](../../stl/utilities/format.md)
- [source_location](../../stl/support/source_location.md)
