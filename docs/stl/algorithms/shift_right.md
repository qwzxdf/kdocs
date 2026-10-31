---
title: std::shift_right
summary: "範囲の要素を、後ろ（右）へずらす。空いた前は放置する。"
order: 70
tags:
  - アルゴリズム
---

# std::shift_right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`shift_left` の逆で、要素を後ろへずらします。`std::shift_right(first, last, n)` は、要素を `n` 個ぶん後ろへ動かし、先頭の `n` 個を、ムーブ後の状態にします。先頭に空きを作って、新しい要素を入れるときに使います。

!!! tip "ポイント"
    - 要素を `n` 個ぶん、後ろへずらす
    - 後ろの `n` 個は捨てられる
    - 先頭の `n` 個は、ムーブ後の状態。値に意味はない
    - 戻り値は、有効な範囲の先頭（`first + n`）

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::shift_right {#shift_right}

<span class="ver ver-20">C++20</span>

```cpp
template <class ForwardIt>
ForwardIt shift_right(ForwardIt first, ForwardIt last,
                      typename std::iterator_traits<ForwardIt>::difference_type n);
```

戻り値は `first + n` で、ずらした要素の先頭です。先頭の `n` 個の空きに、新しい値を代入して使います。

後ろにはみ出る `n` 個は、捨てられます。捨てたくなければ、先に `resize` で長さを増やしておきます。

双方向イテレータ以上があれば、効率の良い実装（後ろから順にムーブ）になります。前方イテレータだけでは、遅い実装になります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  // 2 個ぶん後ろへずらして、先頭に空きを作る
  const auto start = std::shift_right(v.begin(), v.end(), 2);
  std::fill(v.begin(), start, 0);  // 空きに新しい値を入れる
  std::println("{}", v);
}
```

```text title="実行結果"
[0, 0, 1, 2, 3]
```

## ゲームでの使いどころ

最新の値を先頭に入れ、古い値を押し出す履歴のバッファに使います。

## よくあるミス

??? failure "先頭の n 個を、元の値のままと思う"
    ムーブ後の状態です。上書きします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`shift_left`](shift_left.md) | 前へずらす |
| [`rotate`](rotate.md) | 捨てずに回転 |
| [`move_backward`](move_backward.md) | 後ろから順にムーブ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::shift_right](https://cpprefjp.github.io/reference/algorithm/shift_right.html)
- [cppreference: std::shift_right](https://en.cppreference.com/w/cpp/algorithm/shift)
