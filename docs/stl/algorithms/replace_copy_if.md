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

`replace_copy` が「特定の値」を置き換えるのに対し、`std::replace_copy_if` は、「条件に合う要素」を置き換えます。たとえば、負の値を全部 0 にしたコピーを作る、のように使います。

!!! tip "ポイント"
    - 条件が真の要素を `new` に置き換えて、出力先に書く
    - 元の範囲は変わらない
    - 条件は述語（要素を受け取って `bool` を返す関数）
    - その場で置き換えるなら `replace_if`

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::replace_copy_if {#replace_copy_if}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt, class OutputIt, class UnaryPred, class T>
OutputIt replace_copy_if(InputIt first, InputIt last, OutputIt d_first,
                         UnaryPred pred, const T& new_value);
```

戻り値は、出力の最後の次の位置です。

述語は、副作用を持たないものにします。実装は、各要素に対して 1 回呼びますが、並列版では順序が不定です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {5, -3, 8, -1};
  std::vector<int> out(v.size());

  // 負の値を 0 にしたコピーを作る
  std::replace_copy_if(v.begin(), v.end(), out.begin(), [](int x) { return x < 0; }, 0);

  std::println("元: {}", v);
  std::println("結果: {}", out);
}
```

```text title="実行結果"
元: [5, -3, 8, -1]
結果: [5, 0, 8, 0]
```

## ゲームでの使いどころ

ダメージの計算で、負の値を 0 に切り詰めたコピーを作るときに使います。

## よくあるミス

??? failure "述語に副作用を持たせる"
    呼ばれる順序や回数が、保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`replace_copy`](replace_copy.md) | 特定の値を置き換える |
| [`replace`](replace.md) | その場で置き換える |
| [`clamp`](clamp.md) | 範囲に収める |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::replace_copy_if](https://cpprefjp.github.io/reference/algorithm/replace_copy_if.html)
- [cppreference: std::replace_copy_if](https://en.cppreference.com/w/cpp/algorithm/replace_copy)
