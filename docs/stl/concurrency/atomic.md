---
title: std::atomic
tags:
  - 並行処理
---

# std::atomic

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <atomic>`
</div>

`std::atomic<T>` は、**複数のスレッドから同時に読み書きしても壊れない変数**です。`++` や代入が「途中で割り込まれない 1 回の操作」として行われるので、mutex を使わずにカウンタやフラグを共有できます。int、bool、ポインタのような小さな型に使います。

!!! tip "ポイント"
    - スレッド間で共有する **フラグ（bool）やカウンタ（int）は `std::atomic`**。
    - 使い方は普通の変数とほぼ同じ（`= true`、`++`、`load()`）。
    - 複数の値をまとめて矛盾なく更新したいなら、atomic では足りないので [`std::mutex`](mutex.md)。
    - メモリオーダー（`memory_order_relaxed` など）は、分からなければ指定しない（デフォルトが一番安全）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`operator=`](#assign) | <span class="rank rank-sometimes">たまに</span> | 書き込む |
| [`load`](#load) | <span class="rank rank-sometimes">たまに</span> | 読む |
| [`operator T`](#conversion) | <span class="rank rank-sometimes">たまに</span> | 普通の値として読む（暗黙の変換） |
| [`operator++`](#increment) | <span class="rank rank-sometimes">たまに</span> | 1 足す |
| [`fetch_add`](#fetch_add) | <span class="rank rank-sometimes">たまに</span> | 足して、足す前の値を返す |
| [`fetch_sub`](#fetch_sub) | <span class="rank rank-sometimes">たまに</span> | 引いて、引く前の値を返す |
| [`exchange`](#exchange) | <span class="rank rank-sometimes">たまに</span> | 書き込んで、前の値を返す |
| [`store`](#store) | <span class="rank rank-rare">知ってるだけ</span> | 書き込む（メモリオーダーを指定できる） |
| [`operator--`](#decrement) | <span class="rank rank-rare">知ってるだけ</span> | 1 引く |
| [`compare_exchange_strong`](#compare_exchange_strong) | <span class="rank rank-rare">知ってるだけ</span> | 期待した値のときだけ書き換える |
| [`compare_exchange_weak`](#compare_exchange_weak) | <span class="rank rank-rare">知ってるだけ</span> | 上の、ループで使う版 |
| [`fetch_or`](#fetch_or) | <span class="rank rank-rare">知ってるだけ</span> | ビット OR |
| [`fetch_and`](#fetch_and) | <span class="rank rank-rare">知ってるだけ</span> | ビット AND |
| [`fetch_xor`](#fetch_xor) | <span class="rank rank-rare">知ってるだけ</span> | ビット XOR |
| [`wait`](#wait) | <span class="rank rank-rare">知ってるだけ</span> | 値が変わるまで待つ <span class="ver ver-20">C++20</span> |
| [`notify_one`](#notify_one) | <span class="rank rank-rare">知ってるだけ</span> | 待っているスレッドを 1 つ起こす <span class="ver ver-20">C++20</span> |
| [`notify_all`](#notify_all) | <span class="rank rank-rare">知ってるだけ</span> | 待っているスレッドを全部起こす <span class="ver ver-20">C++20</span> |
| [`is_lock_free`](#is_lock_free) | <span class="rank rank-rare">知ってるだけ</span> | 内部で mutex を使っていないか |
| [`std::atomic_flag`](#atomic_flag) | <span class="rank rank-rare">知ってるだけ</span> | 一番単純なフラグ |

## よくある使い方

```cpp
#include <atomic>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> loaded_count = 0;
  std::atomic<bool> has_error = false;

  {
    std::vector<std::jthread> loaders;
    for (int i = 0; i < 8; ++i) {
      loaders.emplace_back([&, i] {
        if (i == 5) {
          has_error = true;  // 1 つ失敗したとする
          return;
        }
        ++loaded_count;      // 同時に足しても壊れない
      });
    }
  }
  std::println("読み込み {} 個 / エラー {}", loaded_count.load(), has_error.load());
}
```

```text title="実行結果"
読み込み 7 個 / エラー true
```

## 関数の詳しい説明

### operator= {#assign}

```cpp
T operator=(T desired) noexcept;
```

- 値を書き込みます。`flag = true;` と書けます

### load {#load}

```cpp
T load(std::memory_order order = std::memory_order_seq_cst) const noexcept;
```

- 値を読みます。`std::println` などに渡すときは `load()` で普通の値にします

### operator T {#conversion}

```cpp
operator T() const noexcept;
```

- `if (flag)` や `int n = counter;` のように、普通の変数として読めます（`load()` と同じ）

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<bool> ready;
  ready = true;
  if (ready) {  // operator T で読む
    std::println("ready = {}", ready.load());
  }
}
```

```text title="実行結果"
ready = true
```

### operator++ {#increment}

```cpp
T operator++() noexcept;     // ++x：足したあとの値を返す
T operator++(int) noexcept;  // x++：足す前の値を返す
```

- 1 足します。整数とポインタの atomic で使えます

### fetch_add {#fetch_add}

```cpp
T fetch_add(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- `arg` を足して、**足す前の値**を返します。連番の ID を配るのに便利です

### fetch_sub {#fetch_sub}

```cpp
T fetch_sub(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- `arg` を引いて、**引く前の値**を返します

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> next_id = 100;
  int a = next_id.fetch_add(1);  // 100 を受け取り、中身は 101 に
  int b = next_id.fetch_add(1);
  std::atomic<int> remaining = 3;
  int before = remaining.fetch_sub(1);
  ++remaining;
  std::println("{} {} / 引く前 {} → 今 {}", a, b, before, remaining.load());
}
```

```text title="実行結果"
100 101 / 引く前 3 → 今 3
```

### exchange {#exchange}

```cpp
T exchange(T desired, std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- 新しい値を書き込み、**前の値**を返します。「たまった件数を取り出して 0 に戻す」が 1 回でできます

### store {#store}

```cpp
void store(T desired, std::memory_order order = std::memory_order_seq_cst) noexcept;
```

- 書き込みます。`operator=` と同じですが、メモリオーダーを指定できます

### operator-- {#decrement}

```cpp
T operator--() noexcept;
```

- 1 引きます

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> pending = 5;
  int taken = pending.exchange(0);
  pending.store(2);
  --pending;
  std::println("取り出し {} / 今 {}", taken, pending.load());
}
```

```text title="実行結果"
取り出し 5 / 今 1
```

### compare_exchange_strong {#compare_exchange_strong}

```cpp
bool compare_exchange_strong(T& expected, T desired) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `expected` | `T&` | 「今この値のはず」。違っていたら、今の値が書き戻される |
| `desired` | `T` | 一致したときに書き込む値 |

- 今の値が `expected` と同じなら `desired` に書き換えて `true`。違えば何もせず `false`（CAS 操作）

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> state = 0;
  int expected = 1;
  bool changed = state.compare_exchange_strong(expected, 9);
  std::println("書き換えた？ {} / 今 {} / expected に入った値 {}", changed, state.load(), expected);
  changed = state.compare_exchange_strong(expected, 9);  // 今度は expected が 0 なので成功
  std::println("書き換えた？ {} / 今 {}", changed, state.load());
}
```

```text title="実行結果"
書き換えた？ false / 今 0 / expected に入った値 0
書き換えた？ true / 今 9
```

### compare_exchange_weak {#compare_exchange_weak}

```cpp
bool compare_exchange_weak(T& expected, T desired) noexcept;
```

- strong と同じですが、一致していても失敗することがあります（その分速い）。ループの中で使います

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> best_score = 500;
  int new_score = 800;
  // 「今より大きければ書き換える」を安全に行う
  int current = best_score.load();
  while (current < new_score && !best_score.compare_exchange_weak(current, new_score)) {
    // 失敗したら current に最新の値が入っているので、もう一度比べる
  }
  std::println("{}", best_score.load());
}
```

```text title="実行結果"
800
```

### fetch_or {#fetch_or}

```cpp
T fetch_or(T arg) noexcept;
```

- ビット OR を割り込まれずに行い、前の値を返します。ビットフラグを立てるのに使います

### fetch_and {#fetch_and}

```cpp
T fetch_and(T arg) noexcept;
```

- ビット AND。フラグを下ろすのに使います

### fetch_xor {#fetch_xor}

```cpp
T fetch_xor(T arg) noexcept;
```

- ビット XOR。フラグを反転させるのに使います

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<unsigned> flags = 0;
  flags.fetch_or(0b0101);   // ビット 0 と 2 を立てる
  flags.fetch_and(~0b0001u);  // ビット 0 を下ろす
  flags.fetch_xor(0b1000);  // ビット 3 を反転
  std::println("{:04b}", flags.load());
}
```

```text title="実行結果"
1100
```

### wait {#wait}

<span class="ver ver-20">C++20</span>

```cpp
void wait(T old, std::memory_order order = std::memory_order_seq_cst) const noexcept;
```

- 値が `old` から変わって通知されるまで、CPU を使わずに待ちます

### notify_one {#notify_one}

<span class="ver ver-20">C++20</span>

```cpp
void notify_one() noexcept;
```

- `wait` しているスレッドを 1 つ起こします。値を変えてから呼びます

### notify_all {#notify_all}

<span class="ver ver-20">C++20</span>

```cpp
void notify_all() noexcept;
```

- `wait` しているスレッドを全部起こします

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  std::atomic<bool> ready = false;
  std::jthread worker([&] {
    ready.wait(false);  // true になるまで眠って待つ
    std::println("スタート");
  });
  ready = true;
  ready.notify_one();
}
```

```text title="実行結果"
スタート
```

### is_lock_free {#is_lock_free}

```cpp
bool is_lock_free() const noexcept;
```

- 内部で mutex を使わずに実現できているか。int や bool、ポインタなら普通は `true`。大きな構造体を atomic にすると `false`（遅い）になります

### std::atomic_flag {#atomic_flag}

```cpp
class atomic_flag {
 public:
  bool test_and_set() noexcept;
  void clear() noexcept;
  bool test() const noexcept;  // C++20
};
```

- 一番単純な bool の atomic。スピンロックを自作するときに使います

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> x;
  std::atomic_flag f;
  bool was_set = f.test_and_set();
  std::println("{} {} {}", x.is_lock_free(), was_set, f.test());
}
```

```text title="実行結果"
true false true
```

## フラグ・オプション（メモリオーダー）

各操作には「メモリオーダー」を指定できます。**分からなければ指定しない**（デフォルトの `seq_cst` が一番安全）でかまいません。

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `memory_order_seq_cst`（省略時） | <span class="rank rank-sometimes">たまに</span> | 一番厳しい。すべてのスレッドから見て操作の順番がそろう |
| `memory_order_relaxed` | <span class="rank rank-rare">知ってるだけ</span> | その変数の値が壊れないことだけ保証。順番は保証しない（単純なカウンタ向け） |
| `memory_order_acquire` | <span class="rank rank-rare">知ってるだけ</span> | 読み込み用。これより後の読み書きが前に来ない |
| `memory_order_release` | <span class="rank rank-rare">知ってるだけ</span> | 書き込み用。これより前の読み書きが後に来ない（acquire と組で使う） |
| `memory_order_acq_rel` | <span class="rank rank-rare">知ってるだけ</span> | acquire と release の両方（読んで書く操作用） |
| `memory_order_consume` | <span class="rank rank-rare">知ってるだけ</span> | 使わない（C++26 で非推奨） |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 「読み込み完了」のフラグ | `std::atomic<bool> loaded` |
| 進捗の表示 | `std::atomic<int> loaded_count`（ロード画面のバー） |
| 連番の ID を配る | `fetch_add` |
| 終了の合図 | `std::atomic<bool> quit`（jthread なら stop_token） |

## よくあるミス

??? failure "atomic 同士の組み合わせで矛盾する"
    `if (count > 0) { --count; }` は、比べてから引くまでの間に別のスレッドが割り込めます。1 つの操作（`fetch_sub` や `compare_exchange`）で書くか、mutex を使います。

??? failure "大きな構造体を atomic にする"
    `std::atomic<BigStruct>` は内部で mutex を使うことになり、速くありません。mutex で守るほうが分かりやすいです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 共有するフラグ・カウンタは atomic
    - [x] 複数の値をまとめて守るなら mutex
    - [x] メモリオーダーは指定しなくていい

## 関連ページ

- [std::mutex](mutex.md)
- [並行処理の基本](../../basics/concurrency.md)
- [cppreference: std::atomic](https://en.cppreference.com/w/cpp/atomic/atomic)
