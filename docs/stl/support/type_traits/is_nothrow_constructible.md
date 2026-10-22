---
title: std::is_nothrow_constructible
summary: "指定した引数で、例外を投げずに構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`noexcept` で構築できるかを判定します。例外安全な実装（`vector` の再確保でムーブを選ぶなど）の分岐に使われます。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_constructible {#is_nothrow_constructible}

```cpp
template <class T, class Args...>
struct is_nothrow_constructible;
template <class T, class Args...>
inline constexpr bool is_nothrow_constructible_v = is_nothrow_constructible<T, Args...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `Args...` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("{}", std::is_nothrow_constructible_v<int, int>);
  std::println("{}", std::is_nothrow_constructible_v<std::string, const char*>);
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
    `is_nothrow_constructible` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した引数で、例外を投げずに構築できる型かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_nothrow_constructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_constructible.html)
- [cppreference: std::is_nothrow_constructible](https://en.cppreference.com/w/cpp/types/is_nothrow_constructible)
