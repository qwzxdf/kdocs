---
title: std::async
summary: "関数を別スレッドで実行して、結果を future で受け取る。"
order: 90
tags:
  - 並行処理
---

# std::async

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

重い計算やファイルの読み込みをゲームのメインループを止めずに裏で行いたい。`std::thread` を自分で作って `join` し、結果を受け渡す仕組みを作るのは、手間がかかります。`std::async` は、関数を別のスレッドで実行して、その結果を `std::future` で受け取れるようにする関数です。「重い処理を投げて、あとで結果を受け取る」を簡単に書けます。

!!! tip "ポイント"
    - `auto f = std::async(std::launch::async, 関数, 引数...);` で、必ず別スレッドで実行する。
    - 結果は `f.get()` で受け取る（終わるまで待つ）。
    - **戻り値の `future` を受け取らないと、その行で終わるまで待たされる**（デストラクターが待つ）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::async {#async}

```cpp
template <class F, class... Args>
std::future</* F の戻り値 */> async(std::launch policy, F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `policy` | `std::launch` | 実行の仕方（[フラグ](#flags)）。**`std::launch::async` を指定する** |
| `f` | 呼び出せるもの | 実行する関数 |
| `args` | 何個でも | `f` に渡す引数（コピーされる） |

- 戻り値: 結果を受け取るための `std::future`

## 実際に動かしてみる

```cpp
#include <future>
#include <print>

int main() {
  auto f = std::async(std::launch::async, [] { return 6 * 7; });
  std::println("{}", f.get());   // 結果を受け取る（終わるまで待つ）
}
```

```text title="実行結果"
42
```

## フラグ・オプション {#flags}

`std::launch` は、`async` が仕事をいつ、どのスレッドで動かすかを決めるビットマスクです。値は 2 つで、`|` で組み合わせられます。

### std::launch::async

呼んだ時点で、新しいスレッドで実行を始めます。「裏で動かしたい」という普通の期待どおりに動くのはこの指定だけなので、迷ったらこれを渡します。`f.get()` や `f.wait()` を呼ぶと、そのスレッドが終わるのを待ちます。

### std::launch::deferred

スレッドを作らず、`get()` か `wait()` が呼ばれた時点で、**呼んだスレッドの上で**実行します。呼ばれなければ、関数は一度も実行されません。ロード処理に付けると「裏で読み込んでいるはず」が実際には動いていない、という事故になります。

### 指定なし（async と deferred の両方）

`std::launch::async | std::launch::deferred` が既定の動きで、どちらで動かすかは実装が決めます。スレッドが足りないときに deferred になりうるので、`wait_for(0ms)` で終わりを見張る使い方では、永遠に `future_status::deferred` が返ります。

## ゲームでの使いどころ

ロード処理を裏で走らせるのが代表例です。`auto f = std::async(std::launch::async, LoadLevel, path);` で投げ、毎フレーム `f.wait_for(0ms)` で終わったかを確かめます。終わったら `f.get()` で結果を受け取り、画面を切り替えます。

AI の経路探索のような、重い計算にも使えます。1 フレームで終わらない計算を裏に回して、結果が出たら反映します。

戻り値の `future` を受け取らないと、その行で終わるまで待たされます。`future` のデストラクターが完了を待つためです。必ず変数で受けます。

## よくあるミス

??? failure "future を受け取らずに捨てる"
    `std::async(...)` の戻り値を捨てると、一時オブジェクトのデストラクターで終わるまで待ちます。同期呼び出しと変わらなくなります。

??? failure "launch ポリシーを省略する"
    省略すると、実装が「遅延実行（`get()` で初めて実行）」を選ぶことがあります。`std::launch::async` を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::future`](future.md) | 結果を受け取る側 |
| [`std::jthread`](jthread.md) | 結果は不要で、実行だけしたい |
| [`std::promise`](promise.md) | 結果を自分で渡す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 関数を別スレッドで実行して future で結果を受け取る
    - [x] `std::launch::async` を明示
    - [x] future を捨てると待たされる

## 関連ページ

- [cpprefjp: std::async](https://cpprefjp.github.io/reference/future/async.html)
- [cppreference: std::async](https://en.cppreference.com/w/cpp/thread/async)
