---
title: std::ref
summary: "値を参照のまま、関数やスレッドに渡す（reference_wrapper を作る）。"
order: 7
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::ref

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

`std::thread` や `std::bind` に引数を渡すと、既定ではコピーされます。変数そのものを渡したいときは、参照を渡したつもりでも、コピーが渡されます。`std::ref(x)` は、<strong>`x` を参照として持ち運べる`reference_wrapper`</strong>を返します。

!!! tip "ポイント"
    - `std::ref(x)` は `x` への参照を包んだ `std::reference_wrapper` を返す
    - `std::thread` や `std::bind` に、参照渡しをするために使う
    - `std::cref(x)` は `const` 参照版
    - 参照先が先に破棄されないよう、寿命に注意する

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ref {#ref}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
std::reference_wrapper<T> ref(T& t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 左辺値 | 参照を持たせたい変数 |

`std::reference_wrapper<T>` は、コピーできる参照のようなオブジェクトです。`T&` に暗黙に変換できます。

`std::thread` にスレッド関数の引数として値を渡すと、コピーされます。関数が参照 `int&` を受け取る場合、そのままだとコンパイルエラーになります。`std::ref(x)` で包むと、`x` そのものが渡されます。

参照先の寿命は、呼び出し側で保証します。スレッドが動いている間に、変数が破棄されると、ぶら下がり参照になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <thread>

void AddOne(int& value) { ++value; }

int main() {
  int count = 0;
  std::thread t(AddOne, std::ref(count));   // count そのものを渡す
  t.join();
  std::println("count = {}", count);
}
```

```text title="実行結果"
count = 1
```

## ゲームでの使いどころ

スレッドや `bind` の引数に、変数の参照を渡します。

```cpp
std::thread worker(Process, std::ref(shared_state), std::cref(config));
```

## よくあるミス

??? failure "`std::ref` を使わず、コピーが更新されて元が変わらない"
    `std::ref` で包みます。

??? failure "参照先が先に破棄される"
    スレッドを `join` してから変数を破棄します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reference_wrapper`](reference_wrapper.md) | ラッパーの型 |
| [`cref`](cref.md) | `const` 参照版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ref(x)` は参照を持ち運べるラッパー
    - [x] `thread` / `bind` で参照渡しに使う
    - [x] 参照先の寿命に注意

## 関連ページ

- [cpprefjp: std::ref](https://cpprefjp.github.io/reference/functional/ref.html)
- [cppreference: std::ref](https://en.cppreference.com/w/cpp/utility/functional/ref)
