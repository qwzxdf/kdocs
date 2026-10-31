---
title: std::sub_match
summary: "一致したグループ 1 つぶんを表すクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::sub_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`(\d+)-(\d+)` というパターンで `"10-20"` を検索すると、全体の `10-20` と、グループ 1 の `10`、グループ 2 の `20` の、3 つの部分が一致として得られます。その 1 つぶんを表すのが `sub_match` です。文字列の中の範囲（始まりと終わりのイテレータ）を持ち、`str()` で文字列として取り出せます。

`std::smatch` の `m[1]` のように添字で取り出したものが、この `sub_match` です。

!!! tip "ポイント"
    - `first` と `second` が範囲の始まりと終わり。`pair` の派生クラス
    - `matched` が真なら、そのグループは一致している。`(a)|(b)` の一致しなかった側は偽
    - `str()` で `std::string`、`length()` で長さが得られる
    - 文字列そのもののコピーではなく、元の文字列への参照。元の文字列が消えると使えない

!!! info "このページを読む前に"
    [`std::match_results`](match_results.md) を先に読んでください。

## 関数の詳しい説明

### std::sub_match {#sub_match}

```cpp
template <class BidirIt>
class sub_match : public std::pair<BidirIt, BidirIt> {
 public:
  bool matched;
  difference_type length() const;
  string_type str() const;
  operator string_type() const;
  int compare(const sub_match& s) const;
};
```

### matched {#matched}

そのグループが一致に参加したかを表す `bool` です。`(a)|(b)` で `"b"` を検索したとき、グループ 1 は一致しておらず、`matched` は `false` で、グループ 2 は `true` です。一致しなかったグループの `str()` は空文字列になります。

### length と str {#length}

`length()` は、一致した部分の長さです。`str()` は、その部分を新しい `std::string` として返します。コピーが発生するので、長い文字列を繰り返し取り出すと遅くなります。コピーを避けたいなら、`first` と `second` を使って、`std::string_view` を作ります。

### compare {#compare}

`sub_match` どうし、あるいは文字列との比較を行います。`m[1] == "10"` のように、`==` で文字列と比べることもできます。

### 型の別名 {#aliases}

`sub_match` は、文字列の種類ごとに別名が用意されています。`std::ssub_match` は `std::string` 用、`std::csub_match` は `const char*` 用、`std::wssub_match` と `std::wcsub_match` は `wchar_t` 用です。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::string s = "abc123";
  std::smatch m;
  const std::regex re(R"(([a-z]+)(\d+))");
  std::regex_search(s, m, re);

  const auto& sub = m[2];
  std::println("matched={} length={} str={}", sub.matched, sub.length(), sub.str());

  // 一致しなかったグループ
  const std::string t = "b";
  std::smatch m2;
  std::regex_search(t, m2, std::regex("(a)|(b)"));
  std::println("グループ 1: {}  グループ 2: {}", m2[1].matched, m2[2].matched);

  // 文字列と直接比べられる
  std::println("グループ 2 == \"b\": {}", m2[2] == "b");
}
```

```text title="実行結果"
matched=true length=3 str=123
グループ 1: false  グループ 2: true
グループ 2 == "b": true
```

## ゲームでの使いどころ

コマンド `move 10 20` から数値を取り出すときなど、グループごとの値を取る場面で `m[1].str()` と書きます。数値に変換するなら、`std::stoi(m[1].str())` や `std::from_chars` を使います。

## よくあるミス

??? failure "元の文字列より長く sub_match を持つ"
    `sub_match` は元の文字列を指す参照のようなものです。元の `std::string` が破棄されると、ぶら下がります。必要なら、`str()` でコピーして持ちます。

??? failure "matched を見ずに str() を使う"
    一致しなかったグループの `str()` は空文字列で、エラーにはなりません。「空文字列に一致した」のか「一致しなかった」のかを区別したいなら、`matched` を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::match_results`](match_results.md) | `sub_match` の集まり |
| [`std::ssub_match`](ssub_match.md) | `std::string` 用の別名 |
| [`std::csub_match`](csub_match.md) | `const char*` 用の別名 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `sub_match` は、一致した 1 つぶんの範囲。`matched`、`length()`、`str()` を持つ
    - [x] 一致しなかったグループは `matched` が `false`
    - [x] 元の文字列が消えると使えない

## 関連ページ

- [cpprefjp: sub_match](https://cpprefjp.github.io/reference/regex/sub_match.html)
- [cppreference: std::sub_match](https://en.cppreference.com/w/cpp/regex/sub_match)
