---
title: std::replace_copy_if
summary: "条件に合う要素だけ置き換えながら、別の場所へコピーする。"
order: 900
tags:
  - アルゴリズム
---

# std::replace_copy_if

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <algorithm>`
</div>

元のデータは残したまま、「条件に合うものだけ別の値に置き換えた結果」がほしいことがあります。`replace_if` は元の列を書き換えてしまうので、コピーしながら置き換える `replace_copy_if` を使います。

!!! tip "ポイント"
    - 元の列は変わらない。出力先は別に用意する。
    - 条件は関数（ラムダ）で渡す。値で決めるなら [`replace_copy`](replace_copy.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::replace_copy_if {#replace_copy_if}

```cpp
template <class InputIt, class OutputIt, class Pred, class T>
OutputIt replace_copy_if(InputIt first, InputIt last, OutputIt d_first, Pred pred, const T& new_value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 元の範囲 |
| `d_first` | イテレータ | コピー先の先頭 |
| `pred` | 述語 | `true` を返した要素を置き換える |
| `new_value` | T | 置き換える値 |

- 戻り値: コピー先の最後の次のイテレータ
- 計算量: 線形（`last - first` 回、`pred` を呼ぶ）


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {3, -1, 4, -5, 9};
  std::vector<int> dst(src.size());
  // 負の値を 0 に置き換えてコピーする
  std::replace_copy_if(src.begin(), src.end(), dst.begin(),
                       [](int x) { return x < 0; }, 0);
  std::println("{}", src);
  std::println("{}", dst);
}
```

```text title="実行結果"
[3, -1, 4, -5, 9]
[3, 0, 4, 0, 9]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 負の値を 0 にした配列を作る | `std::replace_copy_if(src.begin(), src.end(), dst.begin(), [](int x){ return x < 0; }, 0);` |

## よくあるミス

??? failure "出力先の大きさが足りない"
    出力先に `dst.begin()` を渡すだけでは領域は増えません。あらかじめ同じ大きさにするか、`std::back_inserter(dst)` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`replace_copy`](replace_copy.md) | 値で比べる版 |
| [`replace_if`](replace.md) | その場で書き換える版 |
| [`copy_if`](copy.md) | 条件に合うものだけ取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件に合う要素を置き換えながらコピーする
    - [x] 元の列は変わらない
    - [x] 出力先は別に用意する

## 関連ページ

- [cpprefjp: std::replace_copy_if](https://cpprefjp.github.io/reference/algorithm/replace_copy_if.html)
- [cppreference: std::replace_copy_if](https://en.cppreference.com/w/cpp/algorithm/replace_copy)
