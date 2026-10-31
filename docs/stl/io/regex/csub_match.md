---
title: std::csub_match
summary: "C 文字列用の sub_match。"
order: 900
tags:
  - 入出力・文字列
---

# std::csub_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`const char*` の C 文字列を検索対象にしたとき、結果のグループ 1 つぶんは `std::csub_match` で表されます。`sub_match<const char*>` の別名で、`first` と `second` は、イテレータではなく、`const char*` のポインタです。

!!! tip "ポイント"
    - `sub_match<const char*>` の別名
    - `std::cmatch` の要素。`first` と `second` が `const char*`
    - ポインタの差で、一致の位置と長さが求まる
    - `std::string` を検索するなら `std::ssub_match`

!!! info "このページを読む前に"
    [`std::sub_match`](sub_match.md) を先に読んでください。

## 関数の詳しい説明

### std::csub_match {#csub_match}

```cpp
using csub_match = sub_match<const char*>;
```

`sub_match` の機能は、そのまま使えます。`matched`、`length()`、`str()`、`compare()` です。違いは、`first` と `second` が `const char*` であることだけで、元の C 文字列のどの位置かが、ポインタで分かります。

C 文字列のリテラル（`"abc123"`）を検索すると、結果は文字列リテラルの領域を指します。リテラルは、プログラムの終了まで有効なので、ぶら下がりの心配はありません。配列に入れた文字列を検索するときは、配列が生きている間だけ有効です。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const char* s = "abc123";
  std::cmatch m;
  std::regex_search(s, m, std::regex("(\\d+)"));

  std::csub_match sm = m[1];
  std::println("str={} length={}", sm.str(), sm.length());
  std::println("先頭から {} バイト目", sm.first - s);
}
```

```text title="実行結果"
str=123 length=3
先頭から 3 バイト目
```

`first - s` で、ポインタの差から位置が分かります。

## ゲームでの使いどころ

コマンドライン引数や、C の API が返した `const char*` を、`std::string` にコピーせずに検索したいときに使います。

## よくあるミス

??? failure "一時的なバッファの寿命を忘れる"
    ローカル配列に入れた文字列を検索し、その配列が消えたあとに `csub_match` を使うと、ぶら下がります。必要なら `str()` でコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sub_match`](sub_match.md) | 元のテンプレート |
| [`ssub_match`](ssub_match.md) | `std::string` 用 |
| [`std::cmatch`](cmatch.md) | `csub_match` の集まり |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `csub_match` は、`const char*` の検索結果の、グループ 1 つぶんの型
    - [x] `first` と `second` は `const char*`
    - [x] 元の配列が生きている間だけ有効

## 関連ページ

- [cpprefjp: csub_match](https://cpprefjp.github.io/reference/regex/csub_match.html)
- [cppreference: std::csub_match](https://en.cppreference.com/w/cpp/regex/sub_match)
