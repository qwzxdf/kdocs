---
title: std::istreambuf_iterator
summary: "ストリームバッファから、1 文字ずつ生で読むイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::istreambuf_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`istream_iterator<char>` は空白をスキップしてしまいます。`istreambuf_iterator` は、書式を無視して、バッファから 1 文字ずつそのまま読みます。ファイルの全体を `std::string` に読むときに使われます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::istreambuf_iterator {#istreambuf_iterator}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class istreambuf_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |

- 戻り値: `*it` で 1 文字
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("a b");
  std::string s{std::istreambuf_iterator<char>(in), {}};
  std::println("{}", s);
}
```

```text title="実行結果"
a b
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルを丸ごと文字列に読み込む |

## よくあるミス

??? failure "`istream_iterator<char>` で空白が消える"
    `istream_iterator` は空白を読み飛ばします。空白を残したいときは `istreambuf_iterator` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`istream_iterator`](istream_iterator.md) | 書式つきで読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームバッファから、1 文字ずつ生で読むイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::istreambuf_iterator](https://cpprefjp.github.io/reference/iterator/istreambuf_iterator.html)
- [cppreference: std::istreambuf_iterator](https://en.cppreference.com/w/cpp/iterator/istreambuf_iterator)
