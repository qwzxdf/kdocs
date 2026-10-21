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

`std::bad_variant_access` は、**`std::variant` が今持っていない型を、`std::get<T>` で取り出そうとした**ときに投げられる例外です。例外を避けるなら、[`std::get_if`](../../utilities/get_if.md) か [`std::visit`](../../utilities/visit.md) を使います。

!!! tip "ポイント"
    - `std::get<T>(v)` は違う型だと例外。`get_if` はポインターで安全に確認できる。
    - 値を持たない特別な状態（`valueless_by_exception`）でも `visit` が投げる。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_variant_access {#bad_variant_access}

```cpp
class bad_variant_access : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 1;
  try {
    std::get<float>(v);
  } catch (const std::bad_variant_access&) {
    std::println("違う型が入っている");
  }
}
```

```text title="実行結果"
違う型が入っている
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 状態の取り違えを、デバッグで検出する | `std::get<Moving>(state)` |

## よくあるミス

??? failure "例外を使わない方針なのに get を使う"
    `get_if` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant`](../../utilities/variant.md) | 本体 |
| [`std::get_if`](../../utilities/get_if.md) | 例外を投げない取り出し |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 違う型を get すると投げる
    - [x] `get_if` は投げない
    - [x] visit は全型を処理

## 関連ページ

- [cpprefjp: std::bad_variant_access](https://cpprefjp.github.io/reference/variant/bad_variant_access.html)
- [cppreference: std::bad_variant_access](https://en.cppreference.com/w/cpp/utility/variant/bad_variant_access)
