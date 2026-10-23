---
title: std::bad_optional_access
summary: "空の optional から `value()` で取り出したときの例外。"
order: 10
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_optional_access

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_optional_access` は、<strong>値を持たない `std::optional` から値を取り出したことを表す例外</strong>。

!!! tip "ポイント"
    - 値のない `optional` の `value()` が投げる
    - `*opt` は例外ではなく未定義動作になる
    - `has_value()` か `value_or(既定値)` で避けられる
    - `<optional>` で宣言される

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_optional_access {#bad_optional_access}

```cpp
class bad_optional_access : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

値が入っていない `std::optional` に対して、`value()` を呼ぶと投げられます。`*opt` や `opt->` は、例外を投げず、未定義動作になるので、事前に `has_value()` で確かめます。

## 実際に動かしてみる

```cpp
#include <optional>
#include <print>

int main() {
  std::optional<int> hp;               // 値なし
  try {
    int v = hp.value();
    (void)v;
  } catch (const std::bad_optional_access&) {
    std::println("bad_optional_access を捕まえた");
  }
  std::println("value_or なら安全: {}", hp.value_or(100));
}
```

```text title="実行結果"
bad_optional_access を捕まえた
value_or なら安全: 100
```

## ゲームでの使いどころ

値が入っていないかもしれない `optional` を、既定値つきで取り出します。

```cpp
const int hp = saved_hp.value_or(100);   // 例外を使わずに済む
```

## よくあるミス

??? failure "捕まえずに放置して、プログラムが終了する"
    例外を投げうる機能を使うときは、`try` / `catch` で受けるか、事前に条件を確かめます。

??? failure "`catch (std::exception)` と値で捕まえる"
    `const` 参照で捕まえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | すべての標準例外の基底 |
| [`optional`](../../utilities/optional.md) | 値があるかもしれない型 |

## コンパイラ対応

C++17 から使えます。`<optional>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値のない `optional` の `value()` が投げる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_optional_access](https://cpprefjp.github.io/reference/optional/bad_optional_access.html)
- [cppreference: std::bad_optional_access](https://en.cppreference.com/w/cpp/utility/bad_optional_access)
