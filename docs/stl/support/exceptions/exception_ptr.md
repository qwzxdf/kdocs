---
title: std::exception_ptr
summary: "例外を保存して、別の場所・スレッドで投げ直す。"
order: 8
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::exception_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <exception>`
</div>

例外は、投げられたスレッドの中で捕まえるのが普通です。ですが、別のスレッドで起きた例外を、メイン スレッドに運んで投げ直したい場面があります。`std::exception_ptr` は、<strong>例外を保持して、持ち運べる型</strong>です。

!!! tip "ポイント"
    - 例外を保持して持ち運べる型
    - `current_exception()` で作り、`rethrow_exception()` で投げ直す
    - 別スレッドの例外を運ぶのに使われる
    - 空かどうかは `if (ptr)` で確かめる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exception_ptr {#exception_ptr}

<span class="ver ver-11">C++11</span>

```cpp
using exception_ptr = /* 実装定義 */;
```

`std::current_exception()` で、`catch` の中の例外を `exception_ptr` に保存し、あとで `std::rethrow_exception()` で投げ直せます。

`std::future` や `std::promise` が、別スレッドの例外を呼び出し側に運ぶ仕組みも、内部でこれを使っています。

`exception_ptr` はコピーでき、コピーしても同じ例外オブジェクトを共有します。空の `exception_ptr` は、`nullptr` と比べて判定できます。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::exception_ptr saved;
  try {
    throw std::runtime_error("読み込み失敗");
  } catch (...) {
    saved = std::current_exception();      // 例外を保存する
  }

  try {
    std::rethrow_exception(saved);         // あとで投げ直す
  } catch (const std::runtime_error& e) {
    std::println("再び捕まえた: {}", e.what());
  }
}
```

```text title="実行結果"
再び捕まえた: 読み込み失敗
```

## ゲームでの使いどころ

ワーカー スレッドの失敗を、メイン スレッドに運びます。

```cpp
std::exception_ptr error;
std::thread worker([&] {
  try { LoadAssets(); } catch (...) { error = std::current_exception(); }
});
worker.join();
if (error) std::rethrow_exception(error);   // メイン スレッドで投げ直す
```

## よくあるミス

??? failure "保存した例外を、スレッドをまたいで同時に触る"
    `exception_ptr` 自体のコピーは安全ですが、指す先の例外オブジェクトを書き換えないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_exception`](current_exception.md) | 今の例外を取る |
| [`rethrow_exception`](rethrow_exception.md) | 投げ直す |
| [`make_exception_ptr`](make_exception_ptr.md) | 例外から作る |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `exception_ptr` は例外を保持して持ち運ぶ型
    - [x] `current_exception` で作り、`rethrow_exception` で投げ直す
    - [x] 別スレッドの例外を運ぶのに使う

## 関連ページ

- [cpprefjp: std::exception_ptr](https://cpprefjp.github.io/reference/stdexcept/exception_ptr.html)
- [cppreference: std::exception_ptr](https://en.cppreference.com/w/cpp/error/exception_ptr)
