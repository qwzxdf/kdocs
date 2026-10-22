---
title: std::is_move_constructible
summary: "ムーブして構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

他のオブジェクトからムーブして作れるかを判定します。ムーブコンストラクタを `delete` した型は `false` です。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_move_constructible {#is_move_constructible}

```cpp
template <class T>
struct is_move_constructible;
template <class T>
inline constexpr bool is_move_constructible_v = is_move_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct NoMove {
  NoMove() = default;
  NoMove(NoMove&&) = delete;
};

int main() {
  std::println("{}", std::is_move_constructible_v<std::string>);
  std::println("{}", std::is_move_constructible_v<NoMove>);
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
    `is_move_constructible` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_constructible`](is_copy_constructible.md) | コピーして作れる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ムーブして構築できる型かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_move_constructible.html)
- [cppreference: std::is_move_constructible](https://en.cppreference.com/w/cpp/types/is_move_constructible)
