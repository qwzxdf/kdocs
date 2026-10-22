---
title: std::is_within_lifetime
summary: "ポインタが指すオブジェクトが、いま寿命の中にあるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_within_lifetime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <type_traits>`
</div>

`union` のどのメンバが有効かは、実行時に決まります。`constexpr` の中で「いま有効なメンバか」を調べたいときに、`is_within_lifetime(&u.i)` が使えます。定数式の中でだけ使える関数です。

!!! tip "ポイント"
    - 定数式（`constexpr`）の中で使う。
    - `union` の有効なメンバの判定に使う。
    - C++26 の機能。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_within_lifetime {#is_within_lifetime}

```cpp
template <class T>
constexpr bool is_within_lifetime(const T* p) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | const T* | 調べたいオブジェクトのポインタ |

- 戻り値: 寿命の中なら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <type_traits>

int main() {
  union U {
    int i;
    char c;
  };

  constexpr bool Check() {
    U u{.i = 1};
    return std::is_within_lifetime(&u.i);
  }
  static_assert(Check());
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `constexpr` の `union` で、有効なメンバを調べる |

## よくあるミス

??? failure "実行時に使う"
    定数式の中でだけ使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`launder`](../../memory/new_delete/launder.md) | 寿命を新しくしたオブジェクトを指す |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインタが指すオブジェクトが、いま寿命の中にあるかを調べる
    - [x] 定数式（`constexpr`）の中で使う
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_within_lifetime](https://cpprefjp.github.io/reference/type_traits/is_within_lifetime.html)
- [cppreference: std::is_within_lifetime](https://en.cppreference.com/w/cpp/types/is_within_lifetime)
