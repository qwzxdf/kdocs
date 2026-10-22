---
title: std::bad_any_cast
summary: "any_cast で、入っている型と違う型を取り出したときの例外。"
order: 900
tags:
  - ユーティリティ
---

# std::bad_any_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any` は、何でも入れられる代わりに、取り出すときに型を間違えると失敗します。参照やコピーで取り出す `any_cast<T>(a)` は、型が違うと `bad_any_cast` を投げます。ポインタ版の `any_cast<T>(&a)` は、投げずに `nullptr` を返します。

!!! tip "ポイント"
    - `std::exception` から派生。
    - 参照・値の `any_cast` が型違いのときに投げる。
    - 投げたくないなら、ポインタ版（`any_cast<T>(&a)`）で `nullptr` を確かめる。

!!! info "このページを読む前に"
    [`std::any`](any.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_any_cast {#bad_any_cast}

```cpp
class bad_any_cast : public bad_cast {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: `what()` はエラーを表す文字列
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <any>
#include <print>
#include <string>

int main() {
  std::any a = std::string("hello");
  try {
    int x = std::any_cast<int>(a);
    std::println("{}", x);
  } catch (const std::bad_any_cast&) {
    std::println("型が違う");
  }
}
```

```text title="実行結果"
型が違う
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 型が違うかもしれない取り出し | `if (auto* p = std::any_cast<int>(&a)) { ... }` |

## よくあるミス

??? failure "空の any から取り出す"
    空の `any` からの取り出しも `bad_any_cast` です。`has_value()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::any`](any.md) | any の本体 |
| [`bad_variant_access`](../support/exceptions/bad_variant_access.md) | variant の類似の例外 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] any_cast の型違いで投げる例外
    - [x] ポインタ版は投げない
    - [x] has_value() で空を確かめる

## 関連ページ

- [cpprefjp: std::bad_any_cast](https://cpprefjp.github.io/reference/any/bad_any_cast.html)
- [cppreference: std::bad_any_cast](https://en.cppreference.com/w/cpp/utility/bad_any_cast)
