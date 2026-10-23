---
title: std::is_pointer_interconvertible_with_class
summary: "メンバへのポインタが、クラスの先頭のメンバを指すかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pointer_interconvertible_with_class

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

標準レイアウトのクラスの先頭のメンバは、そのクラスのオブジェクトと同じアドレスにあります。`is_pointer_interconvertible_with_class(&S::m)` は、メンバ `m` がそのような先頭のメンバか（ポインタを相互に変換してよいか）を、コンパイル時に調べます。

!!! tip "ポイント"
    - `constexpr` の関数。
    - 先頭のメンバなら `true`。
    - ほとんど使わない。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_pointer_interconvertible_with_class {#is_pointer_interconvertible_with_class}

```cpp
template <class S, class M>
constexpr bool is_pointer_interconvertible_with_class(M S::* mp) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mp` | メンバへのポインタ | 調べるメンバ |

- 戻り値: 先頭のメンバなら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct S {
  int m;
  int n;
};

int main() {
  std::println("{}", std::is_pointer_interconvertible_with_class(&S::m));
  std::println("{}", std::is_pointer_interconvertible_with_class(&S::n));
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | C のライブラリとの境界で、構造体の先頭を相互変換する |

## よくあるミス

??? failure "標準レイアウトでない型に使う"
    標準レイアウトでないと、結果は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_pointer_interconvertible_base_of`](is_pointer_interconvertible_base_of.md) | 基底クラスとの変換 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メンバへのポインタが、クラスの先頭のメンバを指すかを調べる
    - [x] `constexpr` の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_pointer_interconvertible_with_class](https://cpprefjp.github.io/reference/type_traits/is_pointer_interconvertible_with_class.html)
- [cppreference: std::is_pointer_interconvertible_with_class](https://en.cppreference.com/w/cpp/types/is_pointer_interconvertible_with_class)
