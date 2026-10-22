---
title: std::index_sequence_for
summary: "型のパックの個数ぶんの index_sequence を作る。"
order: 900
tags:
  - ユーティリティ
---

# std::index_sequence_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

可変長テンプレート引数 `Ts...` と同じ個数の番号列がほしいとき、`index_sequence_for<Ts...>` と書けば `make_index_sequence<sizeof...(Ts)>` と同じものが作れます。

!!! tip "ポイント"
    - `index_sequence_for<Ts...>` は `make_index_sequence<sizeof...(Ts)>`。
    - 型のパックと番号を並べて展開したいときに使う。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::index_sequence_for {#index_sequence_for}

```cpp
template <class... T>
using index_sequence_for = make_index_sequence<sizeof...(T)>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T...` | 型のパック | 個数を数える型 |

- 戻り値: `index_sequence<0, ..., sizeof...(T)-1>`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

int main() {
  using Seq = std::index_sequence_for<int, double, char>;
  std::println("{}", Seq::size());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 引数の型ごとに番号を振る | `std::index_sequence_for<Args...>{}` |

## よくあるミス

??? failure "パックが空"
    パックが空なら空の列になります。展開側がそれに耐えるように書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_index_sequence`](make_index_sequence.md) | 個数を直接指定 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型パックの個数ぶんの番号列
    - [x] sizeof... を書かずに済む
    - [x] 展開に使う

## 関連ページ

- [cpprefjp: std::index_sequence_for](https://cpprefjp.github.io/reference/utility/index_sequence_for.html)
- [cppreference: std::index_sequence_for](https://en.cppreference.com/w/cpp/utility/integer_sequence)
