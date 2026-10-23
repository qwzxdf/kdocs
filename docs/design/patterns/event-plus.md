---
title: イベントシステム＋（コンパイル時・低オーバーヘッド）
tags:
  - ゲームエンジン
---

# イベントシステム＋（コンパイル時・低オーバーヘッド）

[イベントシステム](event.md)の基本形は `std::function` のコールバックを `std::vector` に登録して、発行のたびに全員を呼ぶ形でした。手軽でたいていのゲームでは十分です。ところが、<strong>毎フレーム何千回も発行する</strong>（当たり判定、パーティクル、入力、ネットワーク）ようになると次の 3 つの見えないコストが効いてきます。このページは受け手がコンパイル時に決まる場合を中心にコストの少ない作り方をいくつか紹介します。

!!! tip "ポイント"
    - コストの正体は <strong>ヒープ確保</strong>（登録・コピー時）、<strong>間接呼び出し</strong>（インライン化できない）、キャッシュ ミス（バラバラに置かれた呼び出し先）の 3 つ。
    - 受け手がコンパイル時に分かるならテンプレートで直接呼び出しにできる。インライン化され実行時の登録も要らない。
    - 受け手を実行時に変えたいなら 確保しない `Delegate`（関数ポインタ + 対象のポインタ）と、固定容量の配列でヒープを避ける。
    - コールバックを呼ぶ代わりに イベントを型ごとの配列に溜めて、後で読む方法もある。呼び出しがなくなりキャッシュにも優しい。
    - どの方式にも 柔軟さと速さの引き換えがある。まず計測して、本当に重い所だけを置き換える。

!!! info "このページを読む前に"
    [イベントシステム](event.md)を先に読んでください。[`std::function`](../../stl/utilities/function.md)、[ラムダ式](../../basics/lambda.md)、[計算量](../../basics/big-o.md)、[キャッシュ効率](../../basics/cache.md)を使います。

## 基本形のコスト

基本形は受け手を `std::function` で持ちます。

```cpp
std::vector<std::function<void(const EnemyKilled&)>> listeners;
listeners.push_back([&](const EnemyKilled& e) { score.total += e.score; });   // ① 登録
for (auto& f : listeners) f(event);                                            // ② 発行
```

| コスト | どこで起きるか | 内容 |
| --- | --- | --- |
| ヒープ確保 | ① 登録 | ラムダのキャプチャが `std::function` の内部バッファ（実装により 16〜32 バイト程度）を超えると、ヒープに確保する。登録は起動時にまとめて行うのが普通なので、実行中のコストにはなりにくい |
| 間接呼び出し | ② 発行 | `std::function` の中身は、関数ポインタ経由の呼び出し。コンパイラは呼び出し先を知らないので、インライン化できない |
| キャッシュ ミス | ② 発行 | 受け手のオブジェクトとラムダのキャプチャが、メモリのあちこちに散らばる。1 回ごとに別のキャッシュ ラインを読む |
| 動的な管理 | ① 登録・解除 | `std::vector` の再確保、発行中の登録・解除に対する安全の確保 |

1 回の呼び出しは数ナノ秒程度で、<strong>1 フレームに数十回なら全く問題になりません</strong>。問題になるのは 毎フレーム、数千〜数万回の発行（弾の当たり判定、パーティクルの寿命、大量の AI）です。計測せずに置き換えるとコードだけ複雑になって、速くならないことがあるので[最適化](../../optimize/index.md)の考え方で、まず計測します。

## パターン 1：コンパイル時に決める（静的バス）

受け手が<strong>プログラムを書いた時点で決まっている</strong>（効果音、スコア、UI はいつもいる）なら実行時に登録する必要は、ありません。テンプレートで受け手の一覧を型として持ち発行の時に 直接、呼びます。

```cpp
#include <print>
#include <tuple>

struct EnemyKilled {
  int enemy_id;
  int score;
};
struct ItemPicked {
  int item_id;
};

// 受け手: 受けたいイベントの On だけを書く。基底クラスも、登録も要らない。
struct ScoreBoard {
  int total = 0;
  void On(const EnemyKilled& e) { total += e.score; }
};

struct Audio {
  void On(const EnemyKilled&) { std::println("効果音: 敵を倒した"); }
  void On(const ItemPicked&) { std::println("効果音: アイテム"); }
};

// 受け手の型の並びを、テンプレートで持つ。
template <typename... Handlers>
class StaticBus {
 public:
  explicit StaticBus(Handlers&... handlers) : handlers_(handlers...) {}

  template <typename Event>
  void Publish(const Event& e) {
    // 全受け手に対して、Dispatch を展開する（実行時のループではなく、コンパイル時の展開）。
    std::apply([&](auto&... h) { (Dispatch(h, e), ...); }, handlers_);
  }

 private:
  template <typename Handler, typename Event>
  static void Dispatch(Handler& handler, const Event& e) {
    if constexpr (requires { handler.On(e); }) {   // この Event を受けられる受け手だけ呼ぶ
      handler.On(e);
    }
  }

  std::tuple<Handlers&...> handlers_;
};

int main() {
  ScoreBoard score;
  Audio audio;
  StaticBus bus(score, audio);

  bus.Publish(EnemyKilled{1, 100});
  bus.Publish(ItemPicked{7});
  bus.Publish(EnemyKilled{2, 50});
  std::println("合計: {}", score.total);
}
```

```text title="実行結果"
効果音: 敵を倒した
効果音: アイテム
効果音: 敵を倒した
合計: 150
```

数行ずつ見ていきます。

```cpp
template <typename... Handlers>
class StaticBus {
 public:
  explicit StaticBus(Handlers&... handlers) : handlers_(handlers...) {}
```

受け手の型を `Handlers...`（任意の個数）として受け取り参照のまま `std::tuple` に持ちます。受け手はバスの外に実体がありバスはそれを指すだけです。`StaticBus bus(score, audio);` と書くと型は自動で `StaticBus<ScoreBoard, Audio>` と決まります。

```cpp
  template <typename Event>
  void Publish(const Event& e) {
    std::apply([&](auto&... h) { (Dispatch(h, e), ...); }, handlers_);
  }
```

`std::apply` でタプルの全要素を 1 つずつ取り出し、畳み込み式 `(Dispatch(h, e), ...)` で全員に対する呼び出しを並べます。これは実行時のループではなく、コンパイル時に受け手の数だけ呼び出しが展開されるので、コンパイラは全部の呼び出し先を知っていて、インライン化できます。

```cpp
    if constexpr (requires { handler.On(e); }) {
      handler.On(e);
    }
```

`if constexpr` と `requires` で「この受け手が、この `Event` を受けられるか」をコンパイル時に調べます。受けられない受け手には呼び出しコードが、生成されません。`ScoreBoard` は `ItemPicked` の `On` を持たないので、`Publish(ItemPicked)` では何も呼ばれません。

| 利点 | 欠点 |
| --- | --- |
| 呼び出しが直接になりインライン化される（最速） | 受け手は、コンパイル時に決まる。実行時に増減できない |
| 登録・ヒープ確保が不要 | 受け手を増やすとバスの型が、変わる（テンプレートがヘッダーに広がる） |
| 受け手がイベントを受けているかをコンパイルで検査 | コンパイル時間が、増える |

常にいる受け手（効果音、スコア、画面表示）に向いています。プレイヤーが増減する物、一時的な物（敵ごとパーティクルごと）には、向きません（パターン 2 以降）。

## パターン 2：確保しない Delegate

実行時に登録・解除したいが `std::function` の確保を避けたいときは、<strong>関数ポインタと対象のポインタだけ</strong>を持つ小さな型を自作します。

```cpp
#include <array>
#include <cstddef>
#include <print>

// 戻り値と引数の型だけで決まる、「呼べる物」。ヒープを使わず、2 つのポインタ（16 バイト）だけ。
template <typename Signature>
class Delegate;

template <typename R, typename... Args>
class Delegate<R(Args...)> {
 public:
  Delegate() = default;

  // メンバー関数を、対象のオブジェクトと、結びつける。Method は、コンパイル時の定数。
  template <auto Method, typename T>
  static Delegate Bind(T* instance) {
    Delegate d;
    d.instance_ = instance;
    d.call_ = [](void* self, Args... args) -> R {
      return (static_cast<T*>(self)->*Method)(args...);   // 呼び出し先が、関数ポインタに、焼き込まれる
    };
    return d;
  }

  R operator()(Args... args) const { return call_(instance_, args...); }
  explicit operator bool() const { return call_ != nullptr; }

 private:
  void* instance_ = nullptr;
  R (*call_)(void*, Args...) = nullptr;
};
```

`Bind<&Audio::OnKilled>(&audio)` のように メンバー関数を型として渡す（`template <auto Method>`）ので、呼び出し用の関数はそのメンバー関数を直接呼ぶ小さな関数として、コンパイル時に作られます。`std::function` と違い ヒープ確保も仮想関数もありません。

次に、イベントの型ごとに 固定容量の受け手の配列を持つチャンネルを作ります。

```cpp
// イベント 1 種類ぶんの、受け手の一覧。固定容量なので、登録でヒープを使わない。
template <typename Event, std::size_t Capacity = 8>
class Channel {
 public:
  using Handler = Delegate<void(const Event&)>;

  bool Subscribe(Handler handler) {
    if (count_ == Capacity) return false;                    // 満杯: 失敗を返す（確保しない）
    handlers_[count_++] = handler;
    return true;
  }

  void Publish(const Event& e) const {
    for (std::size_t i = 0; i < count_; ++i) handlers_[i](e);   // 連続した配列を、順に呼ぶ
  }

 private:
  std::array<Handler, Capacity> handlers_{};
  std::size_t count_ = 0;
};

struct EnemyKilled {
  int score;
};

struct Audio {
  void OnKilled(const EnemyKilled& e) { std::println("効果音（スコア {}）", e.score); }
};
struct Ui {
  void OnKilled(const EnemyKilled& e) { std::println("UI: +{}", e.score); }
};

int main() {
  Audio audio;
  Ui ui;
  Channel<EnemyKilled> killed;
  killed.Subscribe(Delegate<void(const EnemyKilled&)>::Bind<&Audio::OnKilled>(&audio));
  killed.Subscribe(Delegate<void(const EnemyKilled&)>::Bind<&Ui::OnKilled>(&ui));
  killed.Publish(EnemyKilled{100});
}
```

```text title="実行結果"
効果音（スコア 100）
UI: +100
```

| 利点 | 欠点 |
| --- | --- |
| 登録・発行でヒープを使わない。受け手の一覧が連続した配列 | 容量が固定（足りないと登録に失敗） |
| 実行時に登録できる | 呼び出しは、関数ポインタ経由の間接呼び出し（インライン化は、できない） |
| `std::function` より小さい（16 バイト） | ラムダをそのまま登録できない（キャプチャを持てない）。対象はメンバー関数か普通の関数 |

注意点として `Delegate` は対象のオブジェクトを ポインタで、覚えるだけで寿命を管理しません。受け手が先に消える前に必ず解除します（解除の仕組みは、下の「解除の扱い」）。

## パターン 3：イベントを溜めて、後でまとめて読む

コールバックを呼ぶ代わりに <strong>イベントをデータとして、配列に溜め</strong>、フレームの決まった所で まとめて処理する方法です。発行の瞬間に他のコードが呼ばれないので、発行側が速く、再帰（イベントの最中に別のイベント）の心配もありません。

### 型の決まったリング バッファ

```cpp
#include <array>
#include <cstddef>
#include <print>
#include <variant>

struct EnemyKilled {
  int enemy_id;
  int score;
};
struct ItemPicked {
  int item_id;
};

// 起こりうるイベントを、全部、列挙する。型が決まっているので、仮想関数もヒープも、要らない。
using GameEvent = std::variant<EnemyKilled, ItemPicked>;

template <std::size_t Capacity>
class EventQueue {
 public:
  bool Push(const GameEvent& e) {
    if (size_ == Capacity) return false;                     // 満杯
    buffer_[(head_ + size_) % Capacity] = e;
    ++size_;
    return true;
  }

  // 溜まった全イベントを、古い順に、visitor へ渡す。
  template <typename Visitor>
  void Drain(Visitor&& visitor) {
    while (size_ > 0) {
      std::visit(visitor, buffer_[head_]);
      head_ = (head_ + 1) % Capacity;
      --size_;
    }
  }

 private:
  std::array<GameEvent, Capacity> buffer_;
  std::size_t head_ = 0;
  std::size_t size_ = 0;
};

struct Handler {
  void operator()(const EnemyKilled& e) { std::println("敵 {} を倒した（+{}）", e.enemy_id, e.score); }
  void operator()(const ItemPicked& e) { std::println("アイテム {} を拾った", e.item_id); }
};

int main() {
  EventQueue<16> queue;
  queue.Push(EnemyKilled{1, 100});
  queue.Push(ItemPicked{7});
  queue.Push(EnemyKilled{2, 50});

  Handler handler;
  queue.Drain(handler);              // フレームの決まった所で、まとめて配る
}
```

```text title="実行結果"
敵 1 を倒した（+100）
アイテム 7 を拾った
敵 2 を倒した（+50）
```

`std::variant<EnemyKilled, ItemPicked>` がイベントの全種類を型として持ち `std::visit` が、実際に入っている型に応じて `Handler` の対応する `operator()` を呼びます。仮想関数ではなく型の番号による分岐で、コンパイラが全部の呼び先を知っています。バッファは固定長の配列でヒープを使いません。

| 利点 | 欠点 |
| --- | --- |
| 発行が配列への書き込みだけ（速い再帰しない） | イベントの全種類を、1 か所で列挙する必要（新しい種類を足すと全体が、再コンパイル） |
| 処理をフレームの決まった所に集められる（順序が分かる） | 発行から処理まで、遅れる（同じフレームの後半か次のフレーム） |
| ヒープなし連続したメモリ | `variant` の大きさは、最大のイベントにそろう（大きなイベントがあると、無駄が出る） |

### 型ごとの配列（イベント チャンネル）

イベントの種類ごとに 別の配列を持つ方式もあります。`variant` の大きさの無駄がなくなり受け手は、自分が興味のある種類の配列だけを読みます。

```cpp
#include <print>
#include <span>
#include <vector>

// 1 フレームぶんの、イベントを溜める。フレームの境目で、読み側と書き側を、入れ替える。
template <typename Event>
class Events {
 public:
  void Send(const Event& e) { write_.push_back(e); }         // このフレームに起きたこと

  void EndFrame() {                                          // フレームの境目
    read_.swap(write_);                                      // 溜めたものを、読む側へ
    write_.clear();                                          // 書く側は、空に戻す（容量は、残る）
  }

  std::span<const Event> Read() const { return read_; }      // 前のフレームに起きたこと

 private:
  std::vector<Event> write_;
  std::vector<Event> read_;
};

struct EnemyKilled {
  int enemy_id;
  int score;
};

int main() {
  Events<EnemyKilled> killed;

  // フレーム 1: 起きたことを送る。
  killed.Send({1, 100});
  killed.Send({2, 50});
  killed.EndFrame();

  // フレーム 2: 前のフレームに起きたことを、まとめて読む。
  int total = 0;
  for (const EnemyKilled& e : killed.Read()) total += e.score;
  std::println("前のフレームの合計: {}", total);
}
```

```text title="実行結果"
前のフレームの合計: 150
```

2 つの `std::vector`（書き側と読み側）をフレームの境目で入れ替える（ダブル バッファ）ので、書いている最中の配列を読むことが、ありません。`clear` は要素を消すだけでメモリは残るので、2 フレーム目以降は再確保もほとんど起きません。受け手は `Read()` の連続した配列をただループするだけで、呼び出しも登録もありません。ECS のイベント（Bevy の `Events`、EnTT のディスパッチャーに近い形）は、この考え方です（[ECS](ecs.md)）。

## 解除の扱い

静的バスはそもそも解除が要りません（受け手は、コンパイル時に固定）。`Delegate` や動的な登録で受け手が消えうる場合は、<strong>世代つきの ID</strong>で安全に解除します。

```cpp
struct Subscription {
  std::uint32_t index;        // 受け手の配列の位置
  std::uint32_t generation;   // 世代（その位置が、再利用されるたびに増える）
};
```

解除するとその位置の世代を 1 つ上げて、空き位置にします。古い `Subscription`（世代が古い）で解除しようとしても、世代が合わず 別の受け手を誤って解除しません（[Handle](../../engine/handle.md)）。

## 方式の選び方

| 方式 | 受け手の決まり方 | 呼び出し | ヒープ | 柔軟さ | 向く場面 |
| --- | --- | --- | --- | --- | --- |
| `std::function` の配列（基本形） | 実行時 | 間接 | 登録時に確保しうる | 最大（ラムダ可） | 回数の少ない、通知（UI、シーン遷移） |
| 静的バス（パターン 1） | コンパイル時 | 直接（インライン化） | なし | 低（固定） | 常にいる受け手、頻繁なイベント |
| `Delegate` + 固定配列（パターン 2） | 実行時 | 間接 | なし | 中（容量固定） | 実行時に、登録するが確保を避けたい |
| リング バッファ + `variant`（パターン 3） | 実行時（受け手は、visitor） | 直接（visit） | なし | 中（種類は、コンパイル時） | 発行側を軽くしたい順序を制御したい |
| 型ごとの配列（イベント チャンネル） | 実行時（受け手は、ループ） | なし（データを読む） | 初回だけ | 高（種類を自由に追加） | 大量の、イベント（ECS、パーティクル） |

組み合わせて使うこともあります。たとえば、<strong>エンジンの中核</strong>（入力 → 物理 → 描画の毎フレームの流れ）は、静的バスか型ごとの配列で ゲームの上位の通知（実績、シーン遷移）は基本形の `std::function` で、というふうに 頻度で使い分けます。

## 計測のしかた

置き換える前に必ず計測します（[最適化](../../optimize/index.md)）。

1. <strong>どれだけ呼ばれているか</strong>を数える。発行回数 × 受け手の数が 1 フレームで数百を超えなければ、置き換えの効果は小さい。
2. プロファイラーでイベントの発行・配送のコードが、フレームの何 % を占めているかを見る。
3. 置き換えた後で 同じ条件で、もう一度、計測する。速くならなければ元に戻す。

## よくあるミス

??? failure "回数の少ない通知まで、静的バスにしてコンパイルが遅くなる"
    UI やシーン遷移のようなまれなイベントにテンプレートを使うとヘッダーが広がり、コンパイル時間が増えるだけで、速くならない。頻度の高い所だけにする。

??? failure "`Delegate` の対象が、先に消えて無効なポインターを呼ぶ"
    `Delegate` は対象の寿命を管理しない。受け手が消える前に必ず解除する（世代つきの ID）。

??? failure "リング バッファが満杯で、イベントを黙って失う"
    `Push` の戻り値（`false`）を見ていない。容量を見積もるか満杯になったら、ログを出す。

??? failure "溜めたイベントの処理中に新しいイベントを送って、無限に続く"
    イベントを処理している間に同じバッファに書き足している。ダブル バッファ（書き側と読み側を分ける）にして、書いたものは次のフレームに読む。

??? failure "`variant` の大きさが一部の大きなイベントに引きずられる"
    1 つだけとても大きなイベント（配列を持つ）があると全部が、その大きさ。大きなイベントは別の配列（型ごとのチャンネル）にするかデータ本体は、別に置いて ID だけをイベントに入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本形の `std::function` は、手軽で十分。毎フレーム数千回以上になって初めて、コストが見える
    - [x] 受け手が、コンパイル時に決まるなら静的バス（テンプレート、直接呼び出し）が最速
    - [x] 実行時の登録で、確保を避けるなら `Delegate` + 固定容量の配列
    - [x] イベントをデータとして溜める方式（リング バッファ + `variant`、型ごとの配列）は発行が軽く再帰もしない
    - [x] 解除は世代つきの ID で安全に
    - [x] 頻度で使い分ける。置き換える前に必ず計測する

## 関連ページ

- [イベントシステム（オブザーバー）](event.md)
- [CRTP とポリシー](crtp-policy.md)
- [データ指向設計](data-oriented.md)
- [ECS](ecs.md)
- [Handle](../../engine/handle.md)
- [キャッシュ効率](../../basics/cache.md)
