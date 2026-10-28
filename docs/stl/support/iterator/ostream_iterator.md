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

コンテナの中身を、区切り文字つきで出力したい。`for` ループで書くと、最後の区切り文字の扱いが面倒です。`std::ostream_iterator` は、<strong>代入するたびに、ストリームに値と区切り文字を書き込む</strong>出力イテレーターで、`std::copy` の出力先に渡せます。

!!! tip "ポイント"
    - `std::ostream_iterator<T>(stream, 区切り)` で作る
    - 代入すると、値と区切りがストリームに書かれる
    - `std::copy` の出力先として使う
    - 最後にも区切り文字が付く

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ostream_iterator {#ostream_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class T>
class ostream_iterator {
 public:
  ostream_iterator(std::ostream& stream, const char* delimiter = nullptr);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | 出力ストリーム | 書き込み先 |
| `delimiter` | `const char*` | 値の後ろに付ける区切り。省略可 |

`*it = value` は、`stream << value << delimiter` に置き換えられます。最後の要素の後ろにも区切りが付くので、末尾の区切りが邪魔なら、`for` で書くか、最後の 1 つだけ別に出力します。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iostream>
#include <iterator>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3};
  std::copy(v.begin(), v.end(), std::ostream_iterator<int>(std::cout, ", "));
  std::cout << "\n";
}
```

```text title="実行結果"
1, 2, 3, 
```

## ゲームでの使いどころ

デバッグ出力で、コンテナの中身を 1 行に出します。C++23 なら `std::println("{}", v)` のほうが短く書けます。

## よくあるミス

??? failure "最後の区切りが余計に付く"
    最後だけ別に出力します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`istream_iterator`](istream_iterator.md) | 入力版 |
| [`ostreambuf_iterator`](ostreambuf_iterator.md) | 1 文字ずつ書く |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ostream_iterator<T>(s, 区切り)` は値と区切りを書き込む出力イテレーター
    - [x] `std::copy` の出力先に使う
    - [x] 最後にも区切りが付く

## 関連ページ

- [cpprefjp: std::ostream_iterator](https://cpprefjp.github.io/reference/iterator/ostream_iterator.html)
- [cppreference: std::ostream_iterator](https://en.cppreference.com/w/cpp/iterator/ostream_iterator)
