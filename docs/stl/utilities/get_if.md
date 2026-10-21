---
title: std::get_if
summary: "variant から、その型の値へのポインターを取る（違う型ならヌル）。"
order: 57
tags:
  - ユーティリティ
---

# std::get_if

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::get_if<T>(&v)` は、**`variant` が型 `T` の値を持っていればそれへのポインター、違えば `nullptr`** を返す関数です。例外を投げないので、「その型なら処理する」を `if` で書けます。

!!! tip "ポイント"
    - 引数は**ポインター**（`&v`）。`std::get` は参照を渡す。
    - `if (auto* p = std::get_if<Moving>(&state)) { ... }` が定番の形。
    - `std::get` と違って、型が違っても例外を投げない。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::get_if {#get_if}

```cpp
template <class T, class... Types>
constexpr std::add_pointer_t<T> get_if(std::variant<Types...>* pv) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pv` | variant の**ポインタ** | `&v` を渡す |

- 今 `T` が入っていればそのポインタ、違えば `nullptr`。例外を使わずに安全に取り出せます

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 1.5f;
  if (auto* f = std::get_if<float>(&v)) {
    std::println("float {}", *f);
  }
  std::println("int？ {}", std::get_if<int>(&v) != nullptr);
}
```

```text title="実行結果"
float 1.5
int？ false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 今の状態が「攻撃中」ならその中身を使う | `if (auto* a = std::get_if<Attacking>(&state))` |

## よくあるミス

??? failure "&を付け忘れる"
    `std::get_if<T>(v)` は書けません。`std::get_if<T>(&v)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::get`](get.md) | 違う型なら例外 |
| [`std::visit`](visit.md) | すべての型を処理する |
| [`std::holds_alternative`](holds_alternative.md) | 調べるだけ |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] その型ならポインター、違えば `nullptr`
    - [x] 引数は `&v`
    - [x] 例外を投げない

## 関連ページ

- [cpprefjp: std::get_if](https://cpprefjp.github.io/reference/variant/get_if.html)
- [cppreference: std::get_if](https://en.cppreference.com/w/cpp/utility/variant/get_if)
