---
title: std::is_invocable_r
summary: "指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_invocable_r

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

`is_invocable` に、戻り値が `R` へ暗黙に変換できる条件を足したものです。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_invocable_r {#is_invocable_r}

```cpp
template <class R, class F, class Args...>
struct is_invocable_r;
template <class R, class F, class Args...>
inline constexpr bool is_invocable_r_v = is_invocable_r<R, F, Args...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 調べる型 |
| `F` | 型 | 調べる型 |
| `Args...` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("{}", std::is_invocable_r_v<double, int (*)(int), int>);
  std::println("{}", std::is_invocable_r_v<std::string, int (*)(int), int>);
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
    `is_invocable_r` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_invocable_r](https://cpprefjp.github.io/reference/type_traits/is_invocable_r.html)
- [cppreference: std::is_invocable_r](https://en.cppreference.com/w/cpp/types/is_invocable_r)
