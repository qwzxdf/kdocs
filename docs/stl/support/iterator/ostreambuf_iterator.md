---
title: std::ostreambuf_iterator
summary: "ストリームバッファへ、1 文字ずつ生で書くイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::ostreambuf_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`ostream_iterator` は区切り文字を付けて書式つきで出力します。`ostreambuf_iterator` は、書式なしで 1 文字ずつ書きます。速く、余計な処理がありません。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::ostreambuf_iterator {#ostreambuf_iterator}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class ostreambuf_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |

- 戻り値: 代入で 1 文字書く
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <sstream>

int main() {
  std::ostringstream out;
  std::ostreambuf_iterator<char> it(out);
  *it++ = 'h';
  *it++ = 'i';
  std::println("{}", out.str());
}
```

```text title="実行結果"
hi
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | アルゴリズムの結果を文字列ストリームへ出す |

## よくあるミス

??? failure "区切り文字を期待する"
    区切りは付きません。必要なら自分で書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ostream_iterator`](ostream_iterator.md) | 区切りつきで書く |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームバッファへ 1 文字ずつ生で書くイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ostreambuf_iterator](https://cpprefjp.github.io/reference/iterator/ostreambuf_iterator.html)
- [cppreference: std::ostreambuf_iterator](https://en.cppreference.com/w/cpp/iterator/ostreambuf_iterator)
