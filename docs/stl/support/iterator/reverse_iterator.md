---
title: std::reverse_iterator
summary: "逆向きに進むイテレータ（rbegin / rend が返す型）。"
order: 14
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::reverse_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

双方向のイテレーターがあれば、逆順に走査できます。`std::reverse_iterator` は、<strong>元のイテレーターを包んで、`++` で後ろに進む（元の向きでは前へ戻る）</strong>イテレーターアダプターです。`rbegin()` / `rend()` が返す型です。

!!! tip "ポイント"
    - `rbegin()` / `rend()` が返す型
    - `++` で元のイテレーターを戻す
    - `base()` で元のイテレーターに変換できる
    - 参照すると、元の 1 つ手前の要素になる

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::reverse_iterator {#reverse_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class It>
class reverse_iterator {
 public:
  explicit reverse_iterator(It it);
  It base() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | 双方向イテレーター | 包む元のイテレーター |

`reverse_iterator(it)` を参照（`*`）すると、`it` の 1 つ手前の要素になります。この「1 つずれ」のおかげで、`rbegin()` が `end()` から作られても、最後の要素を指せます。

`base()` で元のイテレーターに戻すとき、位置が 1 つずれます。`std::find` などで見つけた逆順のイテレーターを、`erase` に渡すときは、`std::next(it).base()` のように補正が必要です。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::reverse_iterator<std::vector<int>::iterator> r(v.end());
  std::println("逆順の先頭 = {}", *r);
  std::println("base() は元の位置: {}", r.base() == v.end());
}
```

```text title="実行結果"
逆順の先頭 = 3
base() は元の位置: true
```

## ゲームでの使いどころ

逆順にループします。

```cpp
for (auto it = v.rbegin(); it != v.rend(); ++it) Use(*it);
```

範囲 for では、`std::views::reverse`（C++20）が簡単です。

## よくあるミス

??? failure "`base()` で戻すと 1 つずれる"
    `erase` に渡す前に、位置を補正します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_reverse_iterator`](make_reverse_iterator.md) | 作成用の補助関数 |
| [`rbegin`](rbegin.md) | 逆順の先頭 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `reverse_iterator` は逆順に走査するアダプター
    - [x] 参照すると元の 1 つ手前の要素
    - [x] `base()` は 1 つずれる

## 関連ページ

- [cpprefjp: std::reverse_iterator](https://cpprefjp.github.io/reference/iterator/reverse_iterator.html)
- [cppreference: std::reverse_iterator](https://en.cppreference.com/w/cpp/iterator/reverse_iterator)
