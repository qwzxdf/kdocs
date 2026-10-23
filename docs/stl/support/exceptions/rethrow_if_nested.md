---
title: std::rethrow_if_nested
summary: "包まれた例外があれば、それを取り出して投げ直す。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::rethrow_if_nested

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

入れ子になった例外の、内側の例外を取り出したい。`std::rethrow_if_nested(e)` は、<strong>`e` が内側の例外を持っていれば、それを投げ直します</strong>。持っていなければ何もしません。

!!! tip "ポイント"
    - `e` が内側の例外を持てば、それを投げる
    - 持たなければ何もしない
    - 再帰的に呼んで、原因の連鎖をたどる
    - `throw_with_nested` で作った例外に使う

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rethrow_if_nested {#rethrow_if_nested}

<span class="ver ver-11">C++11</span>

```cpp
template <class E>
void rethrow_if_nested(const E& e);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | 例外オブジェクト | 内側を調べる例外 |

`e` が `nested_exception` を継承していて、内側の例外が空でなければ、その内側の例外を投げます。そうでなければ、何も起きずに戻ります。

`catch` を再帰的に書いて、外側から内側へ、すべての原因をたどる処理に使います（上のコードの `Print` 関数）。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

void Load() {
  try {
    throw std::runtime_error("ファイルがない");
  } catch (...) {
    std::throw_with_nested(std::runtime_error("読み込みに失敗"));   // 元の例外を内側に入れて投げる
  }
}

void Print(const std::exception& e) {
  std::println("{}", e.what());
  try {
    std::rethrow_if_nested(e);                // 内側があれば投げ直す
  } catch (const std::exception& inner) {
    Print(inner);
  }
}

int main() {
  try {
    Load();
  } catch (const std::exception& e) {
    Print(e);
  }
}
```

```text title="実行結果"
読み込みに失敗
ファイルがない
```

## ゲームでの使いどころ

ログ出力で、原因の連鎖を、外側から内側へ出力します。（上のコードの `Print` 関数）

## よくあるミス

??? failure "投げ直された例外を捕まえず、終了する"
    `try` / `catch` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nested_exception`](nested_exception.md) | 内側を持つ基底 |
| [`throw_with_nested`](throw_with_nested.md) | 入れ子にして投げる |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rethrow_if_nested(e)` は内側の例外があれば投げ直す
    - [x] なければ何もしない
    - [x] 再帰で原因をたどる

## 関連ページ

- [cpprefjp: std::rethrow_if_nested](https://cpprefjp.github.io/reference/exception/rethrow_if_nested.html)
- [cppreference: std::rethrow_if_nested](https://en.cppreference.com/w/cpp/error/rethrow_if_nested)
