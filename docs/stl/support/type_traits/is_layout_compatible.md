---
title: std::is_layout_compatible
summary: "2 つの型のメモリ配置が互換かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_layout_compatible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

メンバの型と並びが同じで、一方を他方として読み替えても安全かを判定します。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_layout_compatible {#is_layout_compatible}

```cpp
template <class T, class U>
struct is_layout_compatible;
template <class T, class U>
inline constexpr bool is_layout_compatible_v = is_layout_compatible<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `U` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct L1 {
  int a;
};
struct L2 {
  int b;
};
struct A {
  int x;
  int y;
};

int main() {
  std::println("{}", std::is_layout_compatible_v<L1, L2>);
  std::println("{}", std::is_layout_compatible_v<L1, A>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "値と型を取り違える"
    `is_layout_compatible` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの型のメモリ配置が互換かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_layout_compatible](https://cpprefjp.github.io/reference/type_traits/is_layout_compatible.html)
- [cppreference: std::is_layout_compatible](https://en.cppreference.com/w/cpp/types/is_layout_compatible)
