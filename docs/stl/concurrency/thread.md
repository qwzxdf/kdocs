---
title: std::thread
summary: "別のスレッドで、処理を動かす。"
order: 76
tags:
  - 並行処理
---

# std::thread

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
<span class="ver ver-20">C++20</span>
`#include <thread>`
</div>

`std::thread` は、**関数を別のスレッドで同時に動かす**ための型です。C++20 の `std::jthread` はその改良版で、<strong>消えるときに自動で終わりを待ち（join）</strong>、さらに「止まって」と伝える仕組み（`std::stop_token`）を持っています。新しく書くなら jthread を使います。

!!! tip "ポイント"
    - **`std::jthread` を使う**。`std::thread` は join 忘れでプログラムが落ちる。
    - 作った瞬間に動き始める。引数はコピーされて渡る（参照で渡すなら `std::ref`）。
    - 長く動くスレッドは `std::stop_token` を見て、止める合図が来たら抜けるように書く。
    - スレッドを作るのはそれなりに重い。細かい処理を毎フレーム作って捨てるのには向かない（スレッドプールを使う）。
    - 共有するデータは必ず守る（[並行処理の基本](../../basics/concurrency.md)）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 主な型・関数

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::jthread`](jthread.md) | <span class="rank rank-sometimes">たまに</span> | 自動で join するスレッド <span class="ver ver-20">C++20</span> |
| [`std::stop_token`](stop_token.md) | <span class="rank rank-sometimes">たまに</span> | 「止まって」の合図 <span class="ver ver-20">C++20</span> |
| [`std::this_thread::sleep_for`](this_thread/sleep_for.md) | <span class="rank rank-sometimes">たまに</span> | 今のスレッドを指定時間止める |
| [`std::thread`](#thread) | <span class="rank rank-rare">知ってるだけ</span> | 昔からあるスレッド（join を忘れると落ちる） |
| [`joinable`](#joinable) | <span class="rank rank-rare">知ってるだけ</span> | join できる状態か |
| [`detach`](#detach) | <span class="rank rank-rare">知ってるだけ</span> | 待たずに切り離す（使わない） |
| [`std::thread::hardware_concurrency`](#hardware_concurrency) | <span class="rank rank-rare">知ってるだけ</span> | 同時に動かせるスレッド数の目安 |

## よくある使い方

### 1. 重い処理を別スレッドで

```cpp
#include <atomic>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<bool> loaded = false;
  std::vector<int> stage;

  std::jthread loader([&] {
    stage.assign(1000, 1);  // 重い読み込みのつもり
    loaded = true;          // 終わったことを知らせる
  });

  // メインスレッドは待っている間も別のことができる（ここでは終わるまで待つ）
  loader.join();
  std::println("読み込み完了？ {} / {} マス", loaded.load(), stage.size());
}
```

```text title="実行結果"
読み込み完了？ true / 1000 マス
```

### 2. 止める合図で終わるスレッド

```cpp
#include <atomic>
#include <chrono>
#include <print>
#include <thread>

int main() {
  std::atomic<int> ticks = 0;
  {
    std::jthread worker([&ticks](std::stop_token stop) {  // 最初の引数で合図を受け取る
      while (!stop.stop_requested()) {
        ++ticks;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
      }
    });
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
  }  // jthread が消えるとき、自動で request_stop() → join() される
  std::println("止まった。動いていた？ {}", ticks.load() > 0);
}
```

```text title="実行結果"
止まった。動いていた？ true
```

## 関数の詳しい説明

### std::thread {#thread}

```cpp
template <class F, class... Args>
explicit thread(F&& f, Args&&... args);
```

- C++11 からあるスレッド。**join も detach もせずにデストラクタが呼ばれると `std::terminate`**（強制終了）

```cpp
#include <print>
#include <thread>

int main() {
  int result = 0;
  std::thread t([&result] { result = 42; });
  std::println("joinable？ {}", t.joinable());
  t.join();  // 忘れると落ちる
  std::println("{} / joinable？ {}", result, t.joinable());
}
```

```text title="実行結果"
joinable？ true
42 / joinable？ false
```

### joinable {#joinable}

```cpp
bool joinable() const noexcept;
```

- まだ join / detach していない、動いている（または動き終わった）スレッドを持っていれば `true`

### detach {#detach}

```cpp
void detach();
```

- スレッドを切り離し、終わりを待たなくなります。プログラムの終了時にまだ動いていると、消えた変数を触って落ちるなど危険なので、使いません

### std::thread::hardware_concurrency {#hardware_concurrency}

```cpp
static unsigned int hardware_concurrency() noexcept;
```

- 同時に動かせるスレッド数の目安（CPU の論理コア数）。分からなければ 0

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    std::atomic<bool> quit = false;
    std::thread t([&] {
      while (!quit) { /* ... */ }
    });
    quit = true;
    t.join();  // 忘れると落ちる
    ```

=== "今の書き方（C++20）"

    ```cpp
    std::jthread t([](std::stop_token stop) {
      while (!stop.stop_requested()) { /* ... */ }
    });  // 消えるときに自動で止めて待つ
    ```

### native_handle {#native_handle}

```cpp
native_handle_type native_handle();
```

- 計算量: 定数

OS 固有のハンドル（`pthread_t` や `HANDLE`）を返します。標準にない機能（優先度の設定など）を使うときの出口です。

### swap {#swap}

```cpp
void swap(thread& other) noexcept;
```

- 計算量: 定数

2 つの `thread` オブジェクトが管理するスレッドを入れ替えます。

### operator= {#op_assign}

```cpp
thread& operator=(thread&& other) noexcept;
```

- 計算量: 定数

ムーブ代入。コピーはできません。自分が実行中のスレッドを持っている（`joinable()` が真）状態で代入すると、`std::terminate` になります。

### get_id {#thread_get_id}

```cpp
std::thread::id get_id() const noexcept;
```

- 計算量: 定数

スレッドの ID。実行中でなければ（`joinable()` が偽なら）、どのスレッドも指さない既定の ID を返します。ログに出して、どのスレッドか確かめるのに使えます。

### join {#thread_join}

```cpp
void join();
```

- 計算量: スレッドの終了まで待つ

スレッドが終わるまで待ちます。`join` も `detach` もしないままスレッドオブジェクトを破棄すると、`std::terminate` が呼ばれます。2 回呼ぶとエラーです。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ロード | 裏でステージ・アセットを読み込む |
| 音声 | 音声のストリーミング再生 |
| ネットワーク | 受信を待ち続けるスレッド |
| 重い計算 | 経路探索、手続き型生成 |

毎フレームの細かい並列化には、スレッドを作り直すのではなく、あらかじめ作ったスレッドに仕事を渡す「スレッドプール（ジョブシステム）」を使います。

## よくあるミス

??? failure "引数を参照で渡したつもりがコピーされる"
    `std::jthread t(Fill, vec);` は vec のコピーが渡ります。参照で渡すなら `std::ref(vec)` にします（その間 vec が消えないように注意）。

??? failure "ラムダで参照キャプチャした変数が先に消える"
    スレッドが動いている間に、キャプチャしたローカル変数のスコープを抜けると壊れます。jthread をその変数より後に宣言すると、先に jthread が消えて待ってくれます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッドは jthread
    - [x] 長く動く処理は stop_token を見る
    - [x] 引数はコピーされる。参照は std::ref

## 関連ページ

- [並行処理の基本](../../basics/concurrency.md)
- [std::async](future.md)
- [cppreference: std::jthread](https://en.cppreference.com/w/cpp/thread/jthread)
