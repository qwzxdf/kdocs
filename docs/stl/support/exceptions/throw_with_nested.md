---
title: std::throw_with_nested
summary: "いま処理中の例外を包んだ上で、新しい例外を投げる。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::throw_with_nested

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

`catch` で捕まえた例外を、新しい説明つきの例外に包んで、上位に投げ直したい。`std::throw_with_nested(e)` は、<strong>いま処理中の例外を内側に入れて、`e` を投げます</strong>。

!!! tip "ポイント"
    - `catch` の中で、処理中の例外を内側に入れて、新しい例外を投げる
    - 外側は `e` の型としても捕まえられる
    - 内側は `rethrow_if_nested` で取り出す
    - エラーの原因の連鎖を残せる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::throw_with_nested {#throw_with_nested}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
[[noreturn]] void throw_with_nested(T&& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 例外オブジェクト | 外側として投げる例外 |

`catch` の中で呼びます。いま処理中の例外が内側に保存され、`e`（新しい例外）が外側として投げられます。外側の型は、`e` の型と `nested_exception` の両方を継承した型になるので、`catch (const E&)` で受けられます。

受け取った側は、`std::rethrow_if_nested` で内側の例外にたどれます。

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

低水準の失敗を、高水準の説明に言い換えつつ、原因を残します。（上のコードの `Load` 関数）

## よくあるミス

??? failure "`catch` の外で呼んで、内側が空になる"
    `catch` の中で呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nested_exception`](nested_exception.md) | 内側を持つ基底 |
| [`rethrow_if_nested`](rethrow_if_nested.md) | 内側を取り出す |

## コンパイラ対応

C++11 から使えます。`<exception>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `throw_with_nested(e)` は処理中の例外を内側に入れて `e` を投げる
    - [x] `catch` の中で呼ぶ
    - [x] `rethrow_if_nested` で内側をたどる

## 関連ページ

- [cpprefjp: std::throw_with_nested](https://cpprefjp.github.io/reference/exception/throw_with_nested.html)
- [cppreference: std::throw_with_nested](https://en.cppreference.com/w/cpp/error/throw_with_nested)
