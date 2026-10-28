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

`variant` の値を取り出すとき、`std::get<Moving>(state)` は、違う型が入っていると例外を投げます。ゲームのステートマシンでは、「いま移動中なら処理する、そうでなければ何もしない」という書き方が多く、例外は不便です。`std::get_if<T>(&v)` は、`variant` が `T` を持っていればそれへのポインターを違えば `nullptr` を返します。`if` の条件に書けるので、読みやすくなります。

!!! tip "ポイント"
    - 引数は**ポインター**（`&v`）。`std::get` は参照を渡す。
    - `if (auto* p = std::get_if<Moving>(&state)) { ... }` が定番の形。
    - `std::get` と違って、型が違っても例外を投げない。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) の持ち方と、[`std::get`](get.md) の例外を先に読んでください。`get_if` は、例外を使わない版です。

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

ステートの判定で使います。`variant<Idle, Moving, Attacking> state;` があるとき、`if (auto* m = std::get_if<Moving>(&state)) { m->Update(dt); }` と書きます。ポインターが取れた場合だけ、中身が使えます。

複数の型を順に調べるときは、`else if` で並べます。型が多い場合は、`std::visit` で全部を扱うほうが、書き忘れがなくなります。

`variant` が `const` のときは、`const T*` が返ります。書き換えたいときは、`const` でない `variant` に対して呼びます。

## よくあるミス

??? failure "引数にポインターではなく参照を渡す"
    `std::get_if<T>(v)` は、コンパイルエラーです。`get_if` はポインターを受け取るので、`&v` と書きます。`get` は参照を受けます。

??? failure "戻り値のヌルを確かめずに使う"
    違う型が入っていると `nullptr` です。そのまま `->` で使うと、未定義動作でクラッシュします。必ず `if` で確かめます。

??? failure "戻り値のポインターを長く持つ"
    `variant` に別の型を代入すると、中身が破棄されて、持っていたポインターがぶら下がります。取ったポインターは、その場で使い切ります。

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
    - [x] `get_if<T>(&v)` で、違う型なら `nullptr`。
    - [x] 引数はポインター（`&v`）。
    - [x] 使う前に `nullptr` を確かめる。

## 関連ページ

- [cpprefjp: std::get_if](https://cpprefjp.github.io/reference/variant/get_if.html)
- [cppreference: std::get_if](https://en.cppreference.com/w/cpp/utility/variant/get_if)
