---
title: イベントシステム（オブザーバー）
tags:
  - ゲームエンジン
---

# イベントシステム（オブザーバー）

**イベントシステム**は、<strong>「何かが起きた」ことをそれに興味のある相手へまとめて知らせる仕組み</strong>です。たとえば敵が倒されたとき、スコア、実績、サウンド、エフェクト、クエストなど、いろいろな場所が反応したくなります。敵のコードがそれら全部を直接呼ぶと、敵がゲーム中のあらゆるものを知っている状態になってしまいます。イベントシステムを使うと、敵は「倒された」と**発行**するだけで、反応したい側が自分で**購読**しておけます（オブザーバーパターン、Pub/Sub）。

!!! tip "ポイント"
    - 発行側は「起きたこと」を知らせるだけ。誰が聞いているかは知らない。
    - 購読は `std::function` のコールバックを登録するのが手軽。
    - **購読した側が先に消えると、消えたものを呼んでしまう**。購読を解除する仕組み（ID やトークン）を用意する。
    - 発行の最中に購読・解除・別のイベント発行が起きると壊れやすい。キューに溜めてフレームの最後に配る方法が安全。

!!! info "このページを読む前に"
    [`std::function`](../../stl/utilities/function.md) と [ラムダ式](../../basics/lambda.md) を使います。

## 基本

```cpp
#include <functional>
#include <print>
#include <utility>
#include <vector>

struct EnemyKilled {
  int enemy_id;
  int score;
};

class EnemyKilledEvent {
 public:
  using Handler = std::function<void(const EnemyKilled&)>;

  void Subscribe(Handler handler) { handlers_.push_back(std::move(handler)); }

  void Publish(const EnemyKilled& e) const {
    for (const auto& handler : handlers_) {
      handler(e);
    }
  }

 private:
  std::vector<Handler> handlers_;
};

int main() {
  EnemyKilledEvent on_killed;
  int total_score = 0;
  int kill_count = 0;

  // 反応したい側が自分で購読する
  on_killed.Subscribe([&](const EnemyKilled& e) { total_score += e.score; });
  on_killed.Subscribe([&](const EnemyKilled&) { ++kill_count; });
  on_killed.Subscribe([](const EnemyKilled& e) { std::println("爆発エフェクト（敵 {}）", e.enemy_id); });

  // 敵の側は「倒された」と知らせるだけ
  on_killed.Publish({1, 100});
  on_killed.Publish({2, 250});

  std::println("スコア {} / 撃破 {}", total_score, kill_count);
}
```

```text title="実行結果"
爆発エフェクト（敵 1）
爆発エフェクト（敵 2）
スコア 350 / 撃破 2
```

<div class="anim" data-type="graph" data-label="イベント：通知する側は、受け取る側を知らない">
n ev イベント通知 0 1 hit
n ui 画面UI 2 0
n snd 効果音 2 1
n ach 実績 2 2
# まず、受け取りたい相手が登録（購読）する
---
n ev イベント通知 0 1
n ui 画面UI 2 0
n snd 効果音 2 1
n ach 実績 2 2
l ev ui new 購読
l ev snd new 購読
l ev ach new 購読
# 3 つが購読した
---
n ev イベント通知 0 1 hit
n ui 画面UI 2 0 hit
n snd 効果音 2 1 hit
n ach 実績 2 2 hit
l ev ui hit 通知
l ev snd hit 通知
l ev ach hit 通知
# イベントが起きると、購読した全員に届く
---
n ev イベント通知 0 1
n ui 画面UI 2 0
n snd 効果音 2 1 gone
n ach 実績 2 2
l ev ui
l ev snd gone 解除
l ev ach
# 効果音が購読を解除した
---
n ev イベント通知 0 1 hit
n ui 画面UI 2 0 hit
n snd 効果音 2 1 dim
n ach 実績 2 2 hit
l ev ui hit 通知
l ev ach hit 通知
# 次のイベントは、解除した相手には届かない
</div>

## 詳しく

### 購読の解除

購読した UI が先に消えたのにイベントが来ると、消えた UI の関数が呼ばれてクラッシュします。購読したときに ID を返して、消えるときに解除できるようにします。

```cpp
#include <functional>
#include <print>
#include <unordered_map>
#include <utility>

template <class Event>
class Signal {
 public:
  using Handler = std::function<void(const Event&)>;

  int Subscribe(Handler handler) {
    int id = next_id_++;
    handlers_.emplace(id, std::move(handler));
    return id;
  }
  void Unsubscribe(int id) { handlers_.erase(id); }

  void Publish(const Event& e) const {
    for (const auto& [id, handler] : handlers_) {
      handler(e);
    }
  }

 private:
  int next_id_ = 0;
  std::unordered_map<int, Handler> handlers_;
};

struct ScoreChanged {
  int score;
};

int main() {
  Signal<ScoreChanged> on_score;
  int id = on_score.Subscribe([](const ScoreChanged& e) { std::println("UI: {}", e.score); });
  on_score.Publish({100});
  on_score.Unsubscribe(id);  // UI が閉じられた
  on_score.Publish({200});   // もう呼ばれない
  std::println("おわり");
}
```

```text title="実行結果"
UI: 100
おわり
```

さらに一歩進めると、「購読オブジェクトが消えたら自動で解除される」ようにできます（デストラクタで `Unsubscribe` を呼ぶクラスを作る。RAII）。

### すぐ配るか、溜めて配るか

| 方式 | 動き | 長所 | 短所 |
| --- | --- | --- | --- |
| 即時（上の例） | Publish したその場で全員を呼ぶ | 簡単。結果がすぐ反映される | 呼ばれた側がさらに Publish すると、処理が入れ子になって追いにくい |
| キュー | Publish はキューに入れるだけ。フレームの決まったタイミングでまとめて配る | 順番が安定。発行中の購読・解除でも壊れにくい | 反映が少し遅れる |

```cpp
#include <functional>
#include <print>
#include <queue>
#include <string>
#include <utility>

class EventQueue {
 public:
  void Push(std::string event) { queue_.push(std::move(event)); }

  void Dispatch(const std::function<void(const std::string&)>& handler) {
    std::size_t count = queue_.size();  // 今あるぶんだけ配る
    for (std::size_t i = 0; i < count; ++i) {
      handler(queue_.front());
      queue_.pop();
    }
  }

 private:
  std::queue<std::string> queue_;
};

int main() {
  EventQueue events;
  events.Push("ドアが開いた");
  events.Push("敵が出現");
  // フレームの最後にまとめて処理
  events.Dispatch([](const std::string& e) { std::println("処理: {}", e); });
}
```

```text title="実行結果"
処理: ドアが開いた
処理: 敵が出現
```

### イベントの種類が多いとき

| 方法 | 特徴 |
| --- | --- |
| イベントの種類ごとに `Signal<T>` を作る | 型安全。どこで何が発行されるか分かりやすい |
| `std::variant` で 1 つの型にまとめる | 1 本のキューに全部入れられる。`std::visit` で処理（[variant](../../stl/utilities/variant.md)） |
| 型をキーにしたマップ（`type_index` → ハンドラの一覧） | 何でも登録できる汎用のイベントバス |

## ゲームでの例

| イベント | 反応する側 |
| --- | --- |
| 敵が倒された | スコア、実績、ドロップ、サウンド、クエストの進行 |
| プレイヤーがダメージを受けた | HP バー、画面の揺れ、効果音、コントローラーの振動 |
| アイテムを拾った | インベントリ、UI の通知 |
| ステージをクリアした | セーブ、リザルト画面への切り替え |

## よくあるミス

??? failure "購読を解除し忘れる"
    消えたオブジェクトをキャプチャしたラムダが呼ばれ、未定義動作になります。

??? failure "ハンドラの中で同じイベントを購読・解除する"
    `handlers_` を回している最中に追加・削除すると、ループが壊れます。キュー方式にするか、解除を「予約」してあとで消します。

??? failure "何でもイベントにする"
    処理の流れがイベントでつながりすぎると、「何が起きたらどこが動くのか」が追えなくなります。直接呼べば済むものは直接呼びます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 発行側は知らせるだけ、反応したい側が購読する
    - [x] 購読は解除できるようにする
    - [x] 発行中に購読・解除するならキュー方式

## 関連ページ

- [イベントシステム＋（コンパイル時・低オーバーヘッド）](event-plus.md)
- [std::function](../../stl/utilities/function.md)
- [std::queue](../../stl/containers/queue.md)
- [Game Programming Patterns: Observer](https://gameprogrammingpatterns.com/observer.html)
