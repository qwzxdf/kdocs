---
title: std::ostream_iterator
summary: "代入するたびに、出力ストリームへ値を書き出すイテレータ。"
order: 16
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::ostream_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iterator>`
</div>

`std::ostream_iterator<T>` は、**代入するたびに、出力ストリームへ値を書き出すイテレータ**です。`std::copy` の出力先に渡すと、範囲の中身を区切り文字つきで画面やファイルへ出せます。現代では [`std::println`](../../utilities/print.md) が range を出せるので、そちらが簡単です。

!!! tip "ポイント"
    - `std::ostream_iterator<int>(std::cout, ", ")` のように、区切り文字を指定する。
    - 最後の要素のあとにも区切りが付く。
    - 新しいコードでは `std::println("{}", v)`。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::ostream_iterator {#ostream_iterator}

```cpp
template <class T, class CharT = char>
class ostream_iterator {
 public:
  ostream_iterator(std::ostream& os, const CharT* delim = nullptr);
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `os` | 出力ストリーム | 書き出し先 |  |
| `delim` | 文字列 | 要素の後ろに付ける区切り | なし |

- 戻り値: （イテレータ）。`*it = value;` で書き出す
- 計算量: O(要素数)

```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::copy(v.begin(), v.end(), std::ostream_iterator<int>(std::cout, ", "));
  std::cout << "\n";
}
```

```text title="実行結果"
1, 2, 3, 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグで配列の中身を出力する（古い書き方） | `std::copy(v.begin(), v.end(), ostream_iterator<int>(cout, " "))` |

## よくあるミス

??? failure "最後に区切りが付く"
    末尾のカンマが気になるなら、`println("{}", v)` のほうが整います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../../utilities/print.md) | 範囲をそのまま出せる |
| [`istream_iterator`](istream_iterator.md) | 入力側 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 代入で書き出すイテレータ
    - [x] 区切り文字を指定できる
    - [x] 新しいコードは println

## 関連ページ

- [cpprefjp: std::ostream_iterator](https://cpprefjp.github.io/reference/iterator/ostream_iterator.html)
- [cppreference: std::ostream_iterator](https://en.cppreference.com/w/cpp/iterator/ostream_iterator)
