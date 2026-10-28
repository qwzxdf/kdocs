---
title: std::basic_const_iterator
summary: "要素を const として見せるイテレータのアダプタ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::basic_const_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <iterator>`
</div>

読み取り専用でしか使わないイテレータを「書き換えない」型で保証したいことがあります。`basic_const_iterator<It>` は、`*it` が必ず const 参照になるように包みます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::basic_const_iterator {#basic_const_iterator}

```cpp
template <input_iterator It>
class basic_const_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | 元のイテレータ |

- 戻り値: `*it` が const になるイテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::basic_const_iterator<std::vector<int>::iterator> it(v.begin());
  std::println("{}", std::is_const_v<std::remove_reference_t<decltype(*it)>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 読み取り専用で関数に渡す |

## よくあるミス

??? failure "書き換えるつもりで包む"
    包むと `*it = x` はできなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_const_iterator`](make_const_iterator.md) | 作る関数 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素を const として見せるイテレータのアダプタ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::basic_const_iterator](https://cpprefjp.github.io/reference/iterator/basic_const_iterator.html)
- [cppreference: std::basic_const_iterator](https://en.cppreference.com/w/cpp/iterator/basic_const_iterator)
