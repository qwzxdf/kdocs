---
title: std::thread / std::jthread
tags:
  - 並行処理
---

# std::thread / std::jthread

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
| [`std::jthread`](#jthread) | <span class="rank rank-sometimes">たまに</span> | 自動で join するスレッド <span class="ver ver-20">C++20</span> |
| [`join`](#join) | <span class="rank rank-sometimes">たまに</span> | スレッドが終わるまで待つ |
| [`std::stop_token`](#stop_token) | <span class="rank rank-sometimes">たまに</span> | 「止まって」の合図を受け取る <span class="ver ver-20">C++20</span> |
| [`request_stop`](#request_stop) | <span class="rank rank-sometimes">たまに</span> | 「止まって」と伝える <span class="ver ver-20">C++20</span> |
| [`std::this_thread::sleep_for`](#sleep_for) | <span class="rank rank-sometimes">たまに</span> | 今のスレッドを指定時間止める |
| [`std::thread`](#thread) | <span class="rank rank-rare">知ってるだけ</span> | 昔からあるスレッド（join を忘れると落ちる） |
| [`joinable`](#joinable) | <span class="rank rank-rare">知ってるだけ</span> | join できる状態か |
| [`detach`](#detach) | <span class="rank rank-rare">知ってるだけ</span> | 待たずに切り離す（使わない） |
| [`std::thread::hardware_concurrency`](#hardware_concurrency) | <span class="rank rank-rare">知ってるだけ</span> | 同時に動かせるスレッド数の目安 |
| [`std::this_thread::get_id`](#get_id) | <span class="rank rank-rare">知ってるだけ</span> | 今のスレッドの ID |
| [`std::this_thread::yield`](#yield) | <span class="rank rank-rare">知ってるだけ</span> | 他のスレッドに順番を譲る |

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

### std::jthread {#jthread}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
explicit jthread(F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出せるもの | スレッドで動かす関数・ラムダ。最初の引数を `std::stop_token` にすると合図を受け取れる |
| `args` | 何個でも | `f` に渡す引数（**コピーされる**） |

- 作った瞬間に別のスレッドで動き始めます
- デストラクタで `request_stop()` してから `join()` します

### join {#join}

```cpp
void join();
```

- スレッドが終わるまで、呼んだスレッドを止めて待ちます。1 回しか呼べません

### std::stop_token {#stop_token}

<span class="ver ver-20">C++20</span>

```cpp
class stop_token {
 public:
  bool stop_requested() const noexcept;
};
```

- `stop_requested()` が `true` になったら、スレッドの処理を終わらせます。jthread の関数の最初の引数にすると自動で渡されます

### request_stop {#request_stop}

<span class="ver ver-20">C++20</span>

```cpp
bool request_stop() noexcept;
```

- 「止まって」と伝えます。スレッドが止まるかどうかは、stop_token を見ているかどうか次第です

### std::this_thread::sleep_for {#sleep_for}

```cpp
template <class Rep, class Period>
void sleep_for(const std::chrono::duration<Rep, Period>& d);
```

- 今のスレッドを指定時間止めます。指定より長く止まることがあります

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

### std::this_thread::get_id {#get_id}

```cpp
std::thread::id get_id() noexcept;
```

- 今のスレッドの ID。「メインスレッドから呼ばれているか」のチェックに使えます

### std::this_thread::yield {#yield}

```cpp
void yield() noexcept;
```

- 他のスレッドに順番を譲ります。待ちのループで CPU を使い切らないようにするのに使いますが、普通は条件変数などで待ちます

```cpp
#include <print>
#include <thread>

int main() {
  auto main_id = std::this_thread::get_id();
  std::jthread t([main_id] {
    std::this_thread::yield();
    std::println("メインスレッド？ {}", std::this_thread::get_id() == main_id);
  });
  t.join();
  std::println("コア数は 1 以上？ {}", std::thread::hardware_concurrency() >= 1);
}
```

```text title="実行結果"
メインスレッド？ false
コア数は 1 以上？ true
```

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
