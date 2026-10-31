---
title: std::once_flag
summary: "call_once で「1 回だけ実行」を管理するための旗。"
order: 900
tags:
  - 並行処理
---

# std::once_flag

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

スレッドが複数あっても、初期化処理を 1 回だけ実行したい。`std::once_flag` は、その「実行済みか」を覚えておく印で、`std::call_once` と組み合わせて使います。

!!! tip "ポイント"
    - `call_once(flag, f)` で、`flag` ごとに `f` が 1 回だけ実行される
    - コピーもムーブもできない
    - 複数のスレッドが同時に呼んでも、1 つだけが実行し、他は終わるまで待つ
    - `static` 変数のローカル初期化も、同じ保証がある

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::once_flag {#once_flag}

<span class="ver ver-11">C++11</span>

```cpp
struct once_flag {
  constexpr once_flag() noexcept;
  once_flag(const once_flag&) = delete;
  once_flag& operator=(const once_flag&) = delete;
};
```

`once_flag` は、メンバー関数を持たない、状態だけの型です。`call_once` が内部の状態を読み書きします。

クラスのメンバーにして、そのオブジェクトごとに 1 回だけ初期化する使い方が便利です。グローバルや `static` にすれば、プログラム全体で 1 回です。

`f` が例外を投げた場合は、実行済みとは見なされません。次の `call_once` が、また実行します。

関数内の `static` 変数の初期化は、C++11 から、スレッド安全に 1 回だけ行われます。単純な遅延初期化なら、それで足ります。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <thread>
#include <vector>

std::once_flag g_flag;
int g_init_count = 0;

void Init() { ++g_init_count; }

int main() {
  std::vector<std::thread> threads;
  for (int i = 0; i < 4; ++i) {
    threads.emplace_back([] { std::call_once(g_flag, Init); });
  }
  for (auto& t : threads) t.join();

  std::println("初期化された回数: {}", g_init_count);
}
```

```text title="実行結果"
初期化された回数: 1
```

## ゲームでの使いどころ

遅延初期化するシングルトンや、最初に使われたときに作るリソースに使います。

## よくあるミス

??? failure "once_flag をコピーする"
    コピーできません。参照かポインターで渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`call_once`](call_once.md) | 実行する関数 |
| [`mutex`](mutex.md) | 毎回ロックする普通の方法 |
| `static` 変数 | 関数内の簡単な遅延初期化 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::once_flag](https://cpprefjp.github.io/reference/mutex/once_flag.html)
- [cppreference: std::once_flag](https://en.cppreference.com/w/cpp/thread/once_flag)
