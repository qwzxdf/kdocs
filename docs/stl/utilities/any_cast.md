---
title: std::any_cast
summary: "any に入っている値を、型を指定して取り出す。"
order: 60
tags:
  - ユーティリティ
---

# std::any_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any_cast<T>` は、**`std::any` に入っている値を型 `T` で取り出す**関数です。型が違うと `std::bad_any_cast` の例外になります。ポインターで渡すと、違う型のとき例外を投げず `nullptr` を返します。

!!! tip "ポイント"
    - `std::any_cast<int>(a)` は、違う型なら**例外**。
    - `std::any_cast<int>(&a)` は、違う型なら **`nullptr`**。例外を使わないならこちら。
    - `a.type()` で、今の型を調べられる。

!!! info "このページを読む前に"
    [`std::any`](any.md) を先に読んでください。

## 関数の詳しい説明

### std::any_cast {#any_cast}

```cpp
template <class T>
T any_cast(const any& operand);          // 失敗すると例外
template <class T>
const T* any_cast(const any* operand) noexcept;  // 失敗すると nullptr
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `operand` | `any` / `any*` | 取り出す元。ポインタを渡すとポインタ版になる |

- 型が**ぴったり**合わないと失敗します（`int` を入れて `long` で取り出すのも失敗）
- 参照版は失敗すると `std::bad_any_cast` 例外

```cpp
#include <any>
#include <print>

int main() {
  std::any a = 10;
  std::println("{}", std::any_cast<int>(a));
  try {
    std::any_cast<long>(a);
  } catch (const std::bad_any_cast&) {
    std::println("long では取り出せない");
  }
}
```

```text title="実行結果"
10
long では取り出せない
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エディタの設定値（型がバラバラ）を取り出す | `if (auto* v = std::any_cast<int>(&value))` |

## よくあるミス

??? failure "型を間違える"
    `int` で入れたものを `long` で取り出すと失敗です。入れた型と、まったく同じ型で取り出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::any`](any.md) | 本体 |
| [`std::variant`](variant.md) | 入る型が決まっている場合は、こちら |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型を指定して取り出す
    - [x] ポインター版は `nullptr` を返す
    - [x] 入れた型と同じ型で

## 関連ページ

- [cpprefjp: std::any_cast](https://cpprefjp.github.io/reference/any/any_cast.html)
- [cppreference: std::any_cast](https://en.cppreference.com/w/cpp/utility/any/any_cast)
