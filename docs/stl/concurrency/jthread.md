---
title: std::jthread
summary: "スコープを抜けると自動で join する、止める合図つきのスレッド。"
order: 71
tags:
  - 並行処理
---

# std::jthread

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-20">C++20</span>
`#include <thread>`
</div>

`std::jthread` は、**`std::thread` の改良版**です。デストラクターで自動的に `join` するので、`join` の呼び忘れによるクラッシュがありません。さらに、**「止まって」の合図（`stop_token`）**を受け取って、安全に終わらせる仕組みを持っています。新しく書くコードでは、`std::thread` ではなくこちらを使います。

!!! tip "ポイント"
    - **`std::thread` の代わりに `std::jthread` を使う。** デストラクターで自動 join。
    - 関数の第 1 引数に `std::stop_token` を取ると、停止の合図を受け取れる。
    - `request_stop()` で止める合図を出す。デストラクターも、合図を出してから join する。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

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

## 実際に動かしてみる

```cpp
#include <print>
#include <thread>

int main() {
  {
    std::jthread worker([] { std::println("worker"); });
  }  // ここで自動的に join される
  std::println("done");
}
```

```text title="実行結果"
worker
done
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロード用・AI 用のバックグラウンドスレッド | `std::jthread worker([](std::stop_token st) { while (!st.stop_requested()) {...} });` |
| ゲームの終了時に、すべてのスレッドを安全に止める | デストラクターで自動 |

## よくあるミス

??? failure "スレッドに渡した関数が stop_token を見ない"
    `request_stop` は合図を出すだけです。関数のループで `stop_requested()` を確認しないと止まりません。

??? failure "参照を渡したつもりがコピー"
    スレッドの引数はコピーされます。参照で渡すなら `std::ref(x)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::thread`](thread.md) | 従来のスレッド。join を忘れると落ちる |
| [`std::stop_token`](stop_token.md) | 止める合図 |
| [`std::async`](async.md) | 結果を受け取るなら |

## コンパイラ対応

C++20 の機能です。GCC 10 / Clang 18 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `thread` の代わりに `jthread`
    - [x] 自動で join
    - [x] `stop_token` で止める

## 関連ページ

- [cpprefjp: std::jthread](https://cpprefjp.github.io/reference/thread/jthread.html)
- [cppreference: std::jthread](https://en.cppreference.com/w/cpp/thread/jthread)
