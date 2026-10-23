---
title: std::current_exception
summary: "いま処理中の例外を、exception_ptr として取り出す。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::current_exception

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

`catch (...)` で捕まえた例外は、型が分かりません。そのまま保存して、あとで投げ直したい。`std::current_exception()` は、<strong>いま処理中の例外を `exception_ptr` として取り出し</strong>ます。

!!! tip "ポイント"
    - `catch` の中で呼ぶと、処理中の例外を `exception_ptr` で返す
    - 例外の処理中でないときは、空の `exception_ptr`
    - `catch (...)` で捕まえた例外を保存するのに使う
    - 投げ直すのは `rethrow_exception`

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::current_exception {#current_exception}

<span class="ver ver-11">C++11</span>

```cpp
std::exception_ptr current_exception() noexcept;
```

`catch` ブロックの中で呼ぶと、処理中の例外を指す `std::exception_ptr` を返します。例外を処理していない状況で呼ぶと、空の `exception_ptr` を返します。

型が分からない `catch (...)` でも、これを使えば、例外を失わずに保存できます。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::println("処理中でないとき: 空 = {}", !std::current_exception());
  try {
    throw std::runtime_error("boom");
  } catch (...) {
    std::exception_ptr p = std::current_exception();
    std::println("catch の中: 空でない = {}", static_cast<bool>(p));
  }
}
```

```text title="実行結果"
処理中でないとき: 空 = true
catch の中: 空でない = true
```

## ゲームでの使いどころ

`catch (...)` で捕まえた例外を保存します。

```cpp
try { Work(); } catch (...) { error = std::current_exception(); }
```

## よくあるミス

??? failure "`catch` の外で呼んで、空が返る"
    `catch` の中で呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を保持する型 |
| [`rethrow_exception`](rethrow_exception.md) | 投げ直す |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `current_exception()` は処理中の例外を `exception_ptr` で返す
    - [x] 処理中でなければ空
    - [x] `catch (...)` の中で使う

## 関連ページ

- [cpprefjp: std::current_exception](https://cpprefjp.github.io/reference/exception/current_exception.html)
- [cppreference: std::current_exception](https://en.cppreference.com/w/cpp/error/current_exception)
