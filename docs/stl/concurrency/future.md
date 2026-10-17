---
title: std::async / std::future
tags:
  - 並行処理
---

# std::async / std::future

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::async` は、**関数を別のスレッドで実行して、その結果を「あとで受け取る引換券」（`std::future`）を返す**関数です。スレッドを自分で作って、結果を共有変数に書いて、mutex で守って……という手間を省けます。「重い計算を投げておいて、終わったら結果を受け取る」だけなら、これが一番簡単です。

!!! tip "ポイント"
    - 結果を 1 つ返す処理なら `auto f = std::async(std::launch::async, 関数, 引数...);` → `f.get()` で受け取る。
    - **必ず `std::launch::async` を指定**する（省略すると、別スレッドで動かないことがある）。
    - `get()` は終わるまで待つ。待ちたくないなら `wait_for(0s)` で終わったか確かめる。
    - 別スレッドで投げた例外は、`get()` したときに呼び出し側で投げ直される。
    - `std::async` の戻り値を受け取らずに捨てると、その場で終わるまで待ってしまう。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数一覧

| 関数・型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::async`](#async) | <span class="rank rank-sometimes">たまに</span> | 関数を非同期に実行して future を返す |
| [`get`](#get) | <span class="rank rank-sometimes">たまに</span> | 結果を受け取る（終わるまで待つ） |
| [`wait_for`](#wait_for) | <span class="rank rank-sometimes">たまに</span> | 指定時間だけ待って、終わったか調べる |
| [`valid`](#valid) | <span class="rank rank-rare">知ってるだけ</span> | まだ結果を受け取れるか |
| [`wait`](#wait) | <span class="rank rank-rare">知ってるだけ</span> | 終わるまで待つ（結果は受け取らない） |
| [`std::promise`](#promise) | <span class="rank rank-rare">知ってるだけ</span> | 結果を書き込む側を自分で持つ |
| [`std::shared_future`](#shared_future) | <span class="rank rank-rare">知ってるだけ</span> | 複数の場所から結果を受け取れる future |
| [`std::packaged_task`](#packaged_task) | <span class="rank rank-rare">知ってるだけ</span> | 関数と future をセットにしたもの（自作のスレッドプール用） |

## よくある使い方

### 1. 重い計算を投げて、あとで受け取る

```cpp
#include <future>
#include <print>
#include <vector>

long long HeavySum(int n) {
  long long sum = 0;
  for (int i = 1; i <= n; ++i) {
    sum += i;
  }
  return sum;
}

int main() {
  // 2 つの計算を同時に投げる
  std::future<long long> a = std::async(std::launch::async, HeavySum, 1000000);
  std::future<long long> b = std::async(std::launch::async, HeavySum, 2000000);

  // ここで別のことができる

  std::println("{} {}", a.get(), b.get());  // 終わるまで待って受け取る
}
```

```text title="実行結果"
500000500000 2000001000000
```

### 2. ロード画面：終わったか毎フレーム確かめる

```cpp
#include <chrono>
#include <future>
#include <print>
#include <string>
#include <thread>

std::string LoadStage() {
  std::this_thread::sleep_for(std::chrono::milliseconds(30));  // 重い読み込みのつもり
  return "stage1";
}

int main() {
  using namespace std::chrono_literals;
  auto loading = std::async(std::launch::async, LoadStage);

  int frames = 0;
  while (loading.wait_for(0s) != std::future_status::ready) {  // 待たずに確認
    ++frames;  // ロード中のアニメーションを描く
    std::this_thread::sleep_for(5ms);
  }
  std::println("読み込み完了: {} / 待っている間も描けた？ {}", loading.get(), frames > 0);
}
```

```text title="実行結果"
読み込み完了: stage1 / 待っている間も描けた？ true
```

## 関数の詳しい説明

### std::async {#async}

```cpp
template <class F, class... Args>
std::future</* F の戻り値 */> async(std::launch policy, F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `policy` | `std::launch` | 実行の仕方（[フラグ](#フラグオプション)）。**`std::launch::async` を指定する** |
| `f` | 呼び出せるもの | 実行する関数 |
| `args` | 何個でも | `f` に渡す引数（コピーされる） |

- 戻り値: 結果を受け取るための `std::future`

### get {#get}

```cpp
T get();
```

- 結果を受け取ります。まだ終わっていなければ終わるまで待ちます
- **1 回しか呼べません**（2 回目は未定義動作 / 例外）。呼んだあと `valid()` は false になります
- 関数の中で例外が投げられていたら、ここで投げ直されます

```cpp
#include <future>
#include <print>
#include <stdexcept>

int main() {
  auto f = std::async(std::launch::async, [] () -> int {
    throw std::runtime_error("ファイルが無い");
  });
  try {
    f.get();
  } catch (const std::exception& e) {
    std::println("受け取った例外: {}", e.what());
  }
}
```

```text title="実行結果"
受け取った例外: ファイルが無い
```

### wait_for {#wait_for}

```cpp
template <class Rep, class Period>
std::future_status wait_for(const std::chrono::duration<Rep, Period>& timeout) const;
```

- 最大 `timeout` だけ待って、状態を返します。`0s` を渡すと待たずに「今終わっているか」だけ調べられます

| 戻り値 | 意味 |
| --- | --- |
| `std::future_status::ready` | 終わっている（`get()` してすぐ受け取れる） |
| `std::future_status::timeout` | まだ終わっていない |
| `std::future_status::deferred` | `std::launch::deferred` で、まだ始まってもいない |

### valid {#valid}

```cpp
bool valid() const noexcept;
```

- まだ結果を受け取れる状態か。`get()` したあとや、何も入っていない future では `false`

### wait {#wait}

```cpp
void wait() const;
```

- 終わるまで待ちます（結果は受け取らない）

```cpp
#include <future>
#include <print>

int main() {
  std::future<int> f = std::async(std::launch::async, [] { return 7; });
  f.wait();
  bool before = f.valid();
  int value = f.get();
  std::println("valid {} / 値 {} / valid {}", before, value, f.valid());
}
```

```text title="実行結果"
valid true / 値 7 / valid false
```

### std::promise {#promise}

```cpp
template <class T>
class promise {
 public:
  std::future<T> get_future();
  void set_value(T value);
  void set_exception(std::exception_ptr p);
};
```

- 「結果を書く側」を自分で持ちます。async で表せない形（スレッドの途中で結果を渡す、など）で使います

### std::shared_future {#shared_future}

```cpp
template <class T>
class shared_future;
```

- コピーでき、複数の場所から `get()` できる future。`future.share()` で作ります

### std::packaged_task {#packaged_task}

```cpp
template <class R, class... Args>
class packaged_task<R(Args...)>;
```

- 関数と、その結果を受け取る future をセットにしたもの。仕事をキューに入れて、別のスレッドで実行する仕組み（スレッドプール）を自作するときに使います

```cpp
#include <future>
#include <print>
#include <thread>
#include <utility>

int main() {
  std::promise<int> promise;
  std::shared_future<int> result = promise.get_future().share();
  std::jthread worker([&promise] { promise.set_value(42); });
  std::println("{} {}", result.get(), result.get());  // shared_future は何度でも get できる

  std::packaged_task<int(int)> task([](int x) { return x * 2; });
  std::future<int> f = task.get_future();
  std::jthread runner(std::move(task), 21);
  std::println("{}", f.get());
}
```

```text title="実行結果"
42 42
42
```

## フラグ・オプション

`std::launch`（実行の仕方）です。

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::launch::async` | <span class="rank rank-sometimes">たまに</span> | 必ず別のスレッドで、すぐ実行する |
| `std::launch::deferred` | <span class="rank rank-rare">知ってるだけ</span> | `get()` / `wait()` されたときに、呼んだスレッドで実行する（遅延実行） |
| `async \| deferred`（省略時） | <span class="rank rank-rare">知ってるだけ</span> | 実装が好きなほうを選ぶ。別スレッドで動く保証が無いので使わない |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ロード | ステージ・アセットの読み込みを投げて、`wait_for(0s)` で毎フレーム確認 |
| 重い計算 | 経路探索、ダンジョン生成、AI の先読み |
| 並列化 | 大きな計算を 4 つに分けて投げ、全部 `get()` して合わせる |

## よくあるミス

??? failure "launch::async を付けない"
    省略すると deferred が選ばれることがあり、`get()` するまで何も起きません（並列にならない）。

??? failure "戻り値を捨てる"
    ```cpp
    std::async(std::launch::async, Save);  // 戻り値の future がすぐ消える → 終わるまで待ってしまう
    ```

    future のデストラクタが終わりを待つので、非同期になりません。変数に受けておきます。

??? failure "get を 2 回呼ぶ"
    future の結果は 1 回しか取り出せません。何度も使うなら変数に保存するか、shared_future にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::async(std::launch::async, f)` で投げて、`get()` で受け取る
    - [x] 待ちたくないなら `wait_for(0s)` で確認
    - [x] 戻り値は必ず変数に受ける

## 関連ページ

- [std::jthread](thread.md)
- [並行処理の基本](../../basics/concurrency.md)
- [cppreference: std::async](https://en.cppreference.com/w/cpp/thread/async)
