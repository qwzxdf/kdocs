---
title: std::regex_iterator
summary: "文字列から、正規表現に一致する部分を、順に取り出すイテレータ。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`regex_search` は、最初の一致を 1 つ見つけて終わります。文字列の中の一致を全部取り出したいときに、`suffix()` を次の探し始めにして、自分でループを書くこともできますが、それを自動でやってくれるのが `regex_iterator` です。進めるたびに、次の一致が見つかり、一致がなくなると終端と等しくなります。

!!! tip "ポイント"
    - 範囲 `for` や `std::distance` で、全部の一致を順に取り出せる
    - `*it` が、その時点の一致（`match_results`）
    - 終端は、引数なしで作った `regex_iterator`
    - 空の一致に当たると、1 文字進んで続ける。無限ループにはならない

!!! info "このページを読む前に"
    [`std::match_results`](match_results.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_iterator {#regex_iterator}

```cpp
template <class BidirIt, class CharT = typename std::iterator_traits<BidirIt>::value_type,
          class Traits = std::regex_traits<CharT>>
class regex_iterator;
```

`std::sregex_iterator` が `std::string` 用、`std::cregex_iterator` が `const char*` 用、`std::wsregex_iterator` と `std::wcregex_iterator` が `wchar_t` 用の別名です。

### コンストラクター {#ctor}

```cpp
regex_iterator(BidirIt a, BidirIt b, const regex_type& re,
               match_flag_type m = match_default);
regex_iterator();
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a`, `b` | `BidirIt` | 検索する範囲 |
| `re` | `const regex_type&` | パターン |
| `m` | `match_flag_type` | 検索の動作 |

最初の一致を見つけた状態で作られます。一致がなければ、終端と等しくなります。引数なしで作ったものが、終端として使えます。

`re` は、イテレータが生きている間、保持される必要があります。一時オブジェクトの `std::regex` を渡すと、削除されたコンストラクターに当たってコンパイルできません。

### 進める {#advance}

`++it` で、次の一致に進みます。一致が空文字列だった場合は、`match_not_null` と `match_continuous` を使って、同じ位置から空でない一致を探し、なければ 1 文字進めて探します。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <regex>
#include <string>

int main() {
  const std::string s = "a1b22c333";
  const std::regex re(R"(\d+)");

  // 1. 一致の個数を数える
  std::sregex_iterator begin(s.begin(), s.end(), re);
  std::sregex_iterator end;
  std::println("一致の個数: {}", std::distance(begin, end));

  // 2. 順に取り出す
  for (std::sregex_iterator it(s.begin(), s.end(), re); it != end; ++it) {
    std::println("{} (位置 {})", it->str(), it->position());
  }
}
```

```text title="実行結果"
一致の個数: 3
1 (位置 1)
22 (位置 3)
333 (位置 6)
```

`it->str()` で一致した文字列、`it->position()` で位置が得られます。`it` は `match_results` へのポインタのように振る舞います。

## ゲームでの使いどころ

テキストの中から、`{name}` の形のプレースホルダーを全部探して、変数の値に置き換えるような処理で使えます。置き換えだけなら `regex_replace` が楽ですが、置き換える中身を計算したいときは、このイテレータで回します。

## よくあるミス

??? failure "regex の一時オブジェクトを渡す"
    `sregex_iterator(s.begin(), s.end(), std::regex("\\d+"))` は、一時オブジェクトを禁止するために、コンパイルできません。変数に入れます。

??? failure "検索対象の文字列を、イテレータより先に破棄する"
    イテレータは文字列を指しています。文字列が消えると、使えません。

??? failure "distance のあとで、同じイテレータを使う"
    `std::distance(begin, end)` は `begin` をコピーして進めるので、元の `begin` は動きません。ただ、入力イテレータの扱いに近いので、2 回回すときは、作り直すほうが安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::sregex_iterator`](../sregex_iterator.md) | `std::string` 用の別名 |
| [`std::cregex_iterator`](cregex_iterator.md) | `const char*` 用の別名 |
| [`regex_token_iterator`](regex_token_iterator.md) | 一致や、一致と一致の間を、取り出す |
| [`std::regex_search`](../regex_search.md) | 最初の一致だけを探す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regex_iterator` は、文字列中の一致を、順に取り出す
    - [x] 終端は、引数なしで作ったもの
    - [x] `regex` は変数に入れる。一時オブジェクトは不可

## 関連ページ

- [cpprefjp: regex_iterator](https://cpprefjp.github.io/reference/regex/regex_iterator.html)
- [cppreference: std::regex_iterator](https://en.cppreference.com/w/cpp/regex/regex_iterator)
