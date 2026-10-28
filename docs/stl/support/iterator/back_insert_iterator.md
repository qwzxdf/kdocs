---
title: std::back_insert_iterator
summary: "代入するたびに、コンテナの末尾へ push_back するイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::back_insert_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::copy` は、コピー先に十分な領域があることを前提にします。空のコンテナにコピーすると、範囲外に書き込みます。`std::back_insert_iterator` は、<strong>代入するたびに`push_back` で末尾に追加する</strong>イテレーターです。コンテナが自動で広がります。

!!! tip "ポイント"
    - `std::back_inserter(c)` で作る（`back_insert_iterator` を直接書かなくてよい）
    - 代入すると、コンテナに`push_back` で末尾に追加する
    - `std::copy` や `std::transform` の出力先に渡せる
    - コンテナの大きさを事前に決めなくてよい

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::back_insert_iterator {#back_insert_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class Container>
class back_insert_iterator {
 public:
  explicit back_insert_iterator(Container& c);
  back_insert_iterator& operator=(const typename Container::value_type& value);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ | 追加先 |

出力イテレーターとして振る舞い、`*it = value` や `++it` は、追加の動作に置き換えられています。通常は、`std::back_inserter(c)` のように、補助関数で作ります。

コピー元の要素数が分からないとき、結果を詰める場所を先に確保しなくて済むのが利点です。`reserve` を併用すると、余計な再確保が減ります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> src = {1, 2, 3};
  std::vector<int> dst;
  std::copy(src.begin(), src.end(), std::back_inserter(dst));
  for (int x : dst) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
1 2 3 
```

## ゲームでの使いどころ

条件に合う要素だけを、別のコンテナに集めます。

```cpp
std::copy_if(src.begin(), src.end(), std::back_inserter(result), [](int x) { return x > 0; });
```

## よくあるミス

??? failure "出力先の領域がなく、範囲外に書き込む"
    挿入用のイテレーターを使います。

??? failure "`std::vector` に `front_inserter` を使う"
    `push_front` が必要です。`deque` / `list` で使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inserter`](inserter.md) | 任意の位置に挿入 |
| [`front_inserter`](front_inserter.md) | 先頭に追加 |

## コンパイラ対応

C++98 から使えます。`<iterator>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `back_insert_iterator` は`push_back` で末尾に追加する出力イテレーター
    - [x] `std::back_inserter(c)` で作る
    - [x] `std::copy` の出力先に使える

## 関連ページ

- [cpprefjp: std::back_insert_iterator](https://cpprefjp.github.io/reference/iterator/back_insert_iterator.html)
- [cppreference: std::back_insert_iterator](https://en.cppreference.com/w/cpp/iterator/back_insert_iterator)
