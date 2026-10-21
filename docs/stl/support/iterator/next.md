---
title: std::next
summary: "イテレータを n 個進めた位置を返す（元は変えない）。"
order: 1
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::next

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

`std::next(it, n)` は、**イテレータを n 個進めた位置を返す**関数です。`it` 自身は変わりません（`std::advance` は変わる）。`list` のようにランダムアクセスできない範囲でも使えます。

!!! tip "ポイント"
    - `n` を省略すると 1 つ進める。
    - 範囲の終わりを超えて進むと未定義動作。
    - `it + n` が書けない `list` などで便利。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::next {#next}

```cpp
template <class InputIt>
InputIt next(InputIt it, std::iter_difference_t<InputIt> n = 1);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレータ | 元の位置（変わらない） |
| `n` | 整数 | 何個先か（省略すると 1） |

- n 個先のイテレータを**新しく返します**。list など `+ n` できないイテレータにも使えます（その場合 O(n)）

<div class="anim" data-label="std::next(it, 2)">
*a b c d # it は a を指す
a b *c d # 2 つ先を返す。it 自体は動かない
</div>

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("{} {}", *std::next(v.begin()), *std::next(v.begin(), 2));
}
```

```text title="実行結果"
2 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 番目の要素を指す | `std::next(v.begin())` |

## よくあるミス

??? failure "end() を超えて進む"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`prev`](prev.md) | 戻る |
| [`advance`](advance.md) | イテレータそのものを進める |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 進めた位置を返す
    - [x] 元は変えない
    - [x] list にも使える

## 関連ページ

- [cpprefjp: std::next](https://cpprefjp.github.io/reference/iterator/next.html)
- [cppreference: std::next](https://en.cppreference.com/w/cpp/iterator/next)
