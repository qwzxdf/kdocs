---
title: std::front_inserter
summary: "代入するたびに、コンテナの先頭に push_front するイテレータ。"
order: 11
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::front_inserter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::deque` や `std::list` の先頭に、要素を次々に追加したい。`std::front_inserter(c)` は、<strong>`push_front` で追加するイテレーターを作る補助関数</strong>です。

!!! tip "ポイント"
    - `std::front_inserter(c)` は `front_insert_iterator` を作る
    - 代入するたびに `c.push_front(value)` が呼ばれる
    - `deque` / `list` / `forward_list` で使える（`vector` は不可）
    - 追加は先頭から。結果は逆順に並ぶ

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::front_inserter {#front_inserter}

<span class="ver ver-98">C++98</span>

```cpp
template <class Container>
front_insert_iterator<Container> front_inserter(Container& c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ | 追加先（`push_front` を持つこと） |

`vector` は `push_front` を持たないので使えません。先頭に追加するので、`{1, 2, 3}` をコピーすると、`{3, 2, 1}` の順になります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> src = {1, 2, 3};
  std::deque<int> dst;
  std::copy(src.begin(), src.end(), std::front_inserter(dst));
  for (int x : dst) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
3 2 1 
```

## ゲームでの使いどころ

順序を逆にしながら、コピーしたいときに使えます。

## よくあるミス

??? failure "`vector` に使ってコンパイルエラーになる"
    `push_front` を持つコンテナを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`back_insert_iterator`](back_insert_iterator.md) | 末尾に追加 |
| [`inserter`](inserter.md) | 位置を指定して追加 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `front_inserter(c)` は `push_front` で追加するイテレーター
    - [x] `vector` では使えない
    - [x] 結果は逆順になる

## 関連ページ

- [cpprefjp: std::front_inserter](https://cpprefjp.github.io/reference/iterator/front_inserter.html)
- [cppreference: std::front_inserter](https://en.cppreference.com/w/cpp/iterator/front_inserter)
