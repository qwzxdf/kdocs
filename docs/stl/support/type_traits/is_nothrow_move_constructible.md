---
title: std::is_nothrow_move_constructible
summary: "ムーブが例外を投げない型かを調べる。"
order: 12
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::is_nothrow_move_constructible_v<T>` は、**型 T のムーブコンストラクターが例外を投げない（`noexcept`）か**を調べます。`vector` が再確保するときに、ムーブにするかコピーにするかの判断に使われます。自作のクラスのムーブに `noexcept` を付け忘れないための確認にも使えます。

!!! tip "ポイント"
    - `noexcept` でないと、`vector` の再確保でコピーになり、遅くなる。
    - `static_assert` で守る。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_nothrow_move_constructible_v {#is_nothrow_move_constructible}

- ムーブコンストラクタが `noexcept` か。false だと vector の再確保でコピーされてしまうので、自作のクラスの確認に使えます（[ムーブ](../../../basics/move.md#noexcept-を付ける理由)）

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Safe {
  Safe() = default;
  Safe(Safe&&) noexcept = default;
};
struct Throwy {
  Throwy() = default;
  Throwy(Throwy&&) {}   // noexcept が無い
};

int main() {
  std::println("{} {}", std::is_nothrow_move_constructible_v<Safe>, std::is_nothrow_move_constructible_v<Throwy>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作のクラスのムーブが noexcept かを守る | `static_assert(std::is_nothrow_move_constructible_v<Enemy>)` |

## よくあるミス

??? failure "ムーブコンストラクターに noexcept を付けない"
    `vector` の拡張でコピーになり、遅くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::move_if_noexcept`](../../utilities/move_if_noexcept.md) | 内部で使っている |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ムーブが noexcept か
    - [x] 付けないと vector でコピーになる
    - [x] static_assert で守る

## 関連ページ

- [cpprefjp: std::is_nothrow_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_move_constructible.html)
- [cppreference: std::is_nothrow_move_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_move_constructible)
