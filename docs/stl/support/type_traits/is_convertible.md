---
title: std::is_convertible
summary: "型 `From` から `To` へ暗黙に変換できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_convertible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`To x = from;` と書けるかを判定します。`explicit` のコンストラクタ経由の変換は含みません。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_convertible {#is_convertible}

```cpp
template <class From, class To>
struct is_convertible;
template <class From, class To>
inline constexpr bool is_convertible_v = is_convertible<From, To>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `From` | 型 | 調べる型 |
| `To` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_convertible_v<int, double>);
  std::println("{}", std::is_convertible_v<int*, int>);
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
    `is_convertible` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型 `From` から `To` へ暗黙に変換できるかを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_convertible](https://cpprefjp.github.io/reference/type_traits/is_convertible.html)
- [cppreference: std::is_convertible](https://en.cppreference.com/w/cpp/types/is_convertible)
