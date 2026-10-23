---
title: std::declval
summary: "式の中でだけ使う、「その型の値があるとみなす」ための関数（decltype 専用）。"
order: 74
tags:
  - ユーティリティ
---

# std::declval

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::declval<T>()` は、**「型 T の値がここにあるものとして」扱うための、`decltype` の中だけで使う関数**です。`T` に既定コンストラクターがなくても、そのメンバ関数の戻り値の型などを調べられます。実際には呼ばれず、**評価される場所で使うとコンパイルエラー**になります。

!!! tip "ポイント"
    - `decltype(std::declval<T>().size())` で、`T::size()` の戻り値の型が分かる。
    - `decltype` や `sizeof`、コンセプトの `requires` の中だけで使う。
    - 実行時には呼べない。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::declval {#declval}

```cpp
template <class T>
add_rvalue_reference_t<T> declval() noexcept;
```

- 戻り値: （`T&&` 型。評価はされない）
- 計算量: コンパイル時

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  // std::string を作らずに、size() の戻り値の型を調べる
  using Size = decltype(std::declval<std::string>().size());
  std::println("{}", std::is_same_v<Size, std::size_t>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、メンバ関数の戻り値型を調べる | `decltype(std::declval<T>().Update())` |

## よくあるミス

??? failure "実行時の式で使う"
    コンパイルエラーになります。`decltype` の中だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke_result`](../support/type_traits/invoke_result.md) | 関数の戻り値型を調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値があるとみなす（decltype 用）
    - [x] 実行時には使えない
    - [x] テンプレートの部品

## 関連ページ

- [cpprefjp: std::declval](https://cpprefjp.github.io/reference/utility/declval.html)
- [cppreference: std::declval](https://en.cppreference.com/w/cpp/utility/declval)
