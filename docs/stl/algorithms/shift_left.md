---
title: std::shift_left
summary: "範囲の要素を、前（左）へずらす。空いた後ろは放置する。"
order: 69
tags:
  - アルゴリズム
---

# std::shift_left

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

リングバッファのように、配列の要素を前へずらして、先頭の `n` 個を捨てたい。`std::shift_left(first, last, n)` は、要素を `n` 個ぶん前に動かします。後ろの `n` 個は、ムーブされた状態（値は不定）になります。

!!! tip "ポイント"
    - 要素を `n` 個ぶん、前（先頭側）へずらす
    - 先頭の `n` 個は捨てられる
    - 後ろの `n` 個は、使い終えた（ムーブ後の）状態。値に意味はない
    - 戻り値は、有効な範囲の終端

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::shift_left {#shift_left}

<span class="ver ver-20">C++20</span>

```cpp
template <class ForwardIt>
ForwardIt shift_left(ForwardIt first, ForwardIt last,
                     typename std::iterator_traits<ForwardIt>::difference_type n);
```

戻り値は、ずらした後の有効な要素の終端（`last - n`）です。`n` が 0 以下なら何もせず `last` を返し、範囲の長さ以上なら何もしないで `first` を返します。

後ろの `n` 個は、ムーブされたあとの状態で、使える値ではありません。`vector` なら、戻り値から `end()` までを `erase` します。

```cpp
v.erase(std::shift_left(v.begin(), v.end(), 2), v.end());
```

`std::rotate` は要素を捨てずに回転します。`shift_left` は、捨てるところが違います。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  // 先頭の 2 個を捨てて、前へ詰める
  const auto new_end = std::shift_left(v.begin(), v.end(), 2);
  v.erase(new_end, v.end());
  std::println("{}", v);
}
```

```text title="実行結果"
[3, 4, 5]
```

## ゲームでの使いどころ

履歴のバッファで、古い要素を捨てて、前へ詰めるときに使います。

## よくあるミス

??? failure "後ろの n 個の値を使う"
    使い終えた状態です。`erase` で消します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`shift_right`](shift_right.md) | 逆向き |
| [`rotate`](rotate.md) | 捨てずに回転 |
| [`remove`](remove.md) | 条件に合う要素を詰めて消す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::shift_left](https://cpprefjp.github.io/reference/algorithm/shift_left.html)
- [cppreference: std::shift_left](https://en.cppreference.com/w/cpp/algorithm/shift)
