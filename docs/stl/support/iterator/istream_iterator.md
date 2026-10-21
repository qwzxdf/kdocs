---
title: std::istream_iterator
summary: "入力ストリームから、値を 1 つずつ読むイテレータ。"
order: 15
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::istream_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::istream_iterator<T>` は、**入力ストリームから `T` 型の値を 1 つずつ読み出すイテレータ**です。`std::vector<int> v((istream_iterator<int>(in)), istream_iterator<int>());` のように、ストリームの全部を `vector` に読み込めます。C++20 以降は [`views::istream`](../../algorithms/views/istream_view.md) もあります。

!!! tip "ポイント"
    - 終端は、引数なしで作ったイテレータ。
    - ストリームが失敗する（型が違う・終わり）と終端になる。
    - ranges 版は `views::istream<T>(in)`。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::istream_iterator {#istream_iterator}

```cpp
template <class T>
class istream_iterator;
```

- ストリームから `>>` で値を読むイテレータ。ファイルの数値を全部 vector に読むのに使えます

```cpp
#include <iterator>
#include <print>
#include <sstream>
#include <vector>

int main() {
  std::istringstream in("10 20 30");
  std::vector<int> values(std::istream_iterator<int>(in), std::istream_iterator<int>{});
  std::vector<int> v = {1, 2, 3};
  auto r = v.rbegin();
  std::println("{} / {} {}", values, *r, *std::prev(r.base()));
}
```

```text title="実行結果"
[10, 20, 30] / 3 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの数値を全部 vector に読み込む | `istream_iterator<int>(in)` |

## よくあるミス

??? failure "最も困惑する構文 (vexing parse)"
    関数宣言と解釈されることがあります。引数を二重のかっこで包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::istream`](../../algorithms/views/istream_view.md) | ranges 版 |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値を 1 つずつ読むイテレータ
    - [x] 終端は引数なしで作る
    - [x] ranges 版もある

## 関連ページ

- [cpprefjp: std::istream_iterator](https://cpprefjp.github.io/reference/iterator/istream_iterator.html)
- [cppreference: std::istream_iterator](https://en.cppreference.com/w/cpp/iterator/istream_iterator)
