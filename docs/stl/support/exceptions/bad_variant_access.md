---
title: std::bad_variant_access
summary: "variant が持っていない型を `get` で取り出したときの例外。"
order: 11
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_variant_access

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_variant_access` は、<strong>保持していない型を `std::variant` から取り出したことを表す例外</strong>。

!!! tip "ポイント"
    - 違う型を `get` すると投げられる
    - `std::get_if` なら `nullptr` を返す
    - `std::holds_alternative` で型を確かめられる
    - `<variant>` で宣言される

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_variant_access {#bad_variant_access}

```cpp
class bad_variant_access : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

`std::variant` に、別の型の値が入っているとき、`std::get<T>(v)` で違う型を取り出そうとすると、投げられます。`std::get_if` は、例外を投げず、`nullptr` を返します。

## 実際に動かしてみる

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 10;     // int を保持
  try {
    float f = std::get<float>(v);      // float ではない
    (void)f;
  } catch (const std::bad_variant_access&) {
    std::println("bad_variant_access を捕まえた");
  }
  std::println("get_if なら安全: {}", std::get_if<float>(&v) == nullptr);
}
```

```text title="実行結果"
bad_variant_access を捕まえた
get_if なら安全: true
```

## ゲームでの使いどころ

型を確かめてから取り出します。

```cpp
if (const int* p = std::get_if<int>(&v)) { /* int を保持していた */ }
```

すべての型を網羅する処理は、`std::visit` を使うほうが安全です。

## よくあるミス

??? failure "捕まえずに放置して、プログラムが終了する"
    例外を投げうる機能を使うときは、`try` / `catch` で受けるか、事前に条件を確かめます。

??? failure "`catch (std::exception)` と値で捕まえる"
    `const` 参照で捕まえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | すべての標準例外の基底 |
| [`variant`](../../utilities/variant.md) | 複数の型のうち 1 つを持つ型 |

## コンパイラ対応

C++17 から使えます。`<variant>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 違う型を `get` すると投げられる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_variant_access](https://cpprefjp.github.io/reference/variant/bad_variant_access.html)
- [cppreference: std::bad_variant_access](https://en.cppreference.com/w/cpp/utility/variant/bad_variant_access)
