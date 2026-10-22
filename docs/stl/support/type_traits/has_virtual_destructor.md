---
title: std::has_virtual_destructor
summary: "型が仮想デストラクタを持つかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::has_virtual_destructor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

基底クラスのポインタ経由で `delete` するとき、デストラクタが `virtual` でないと、派生クラスの後始末が走りません。それを判定します。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_virtual_destructor {#has_virtual_destructor}

```cpp
template <class T>
struct has_virtual_destructor;
template <class T>
inline constexpr bool has_virtual_destructor_v = has_virtual_destructor<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct A {
  int x;
};
struct VB {
  virtual ~VB() = default;
};

int main() {
  std::println("{}", std::has_virtual_destructor_v<VB>);
  std::println("{}", std::has_virtual_destructor_v<A>);
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
    `has_virtual_destructor` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型が仮想デストラクタを持つかを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::has_virtual_destructor](https://cpprefjp.github.io/reference/type_traits/has_virtual_destructor.html)
- [cppreference: std::has_virtual_destructor](https://en.cppreference.com/w/cpp/types/has_virtual_destructor)
