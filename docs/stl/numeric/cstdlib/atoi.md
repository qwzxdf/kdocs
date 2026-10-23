---
title: std::atoi
summary: "文字列を整数に変換する（失敗を検出できない古い関数）。"
order: 2
group: <cstdlib> の関数
tags:
  - 数値
---

# std::atoi

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

設定ファイルから読んだ文字列 "120" を、数値の 120 にしたい。古くから C 言語で使われてきたのが `std::atoi` です。短く書けますが、<strong>失敗しても失敗したと教えてくれない</strong>という大きな欠点があります。

!!! tip "ポイント"
    - `std::atoi("123")` は 123
    - 数字でない文字列は 0 を返す。本当の 0 と区別できない
    - 範囲を超える値は未定義動作
    - 新しいコードでは `std::from_chars` か `std::stoi` を使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atoi {#atoi}

```cpp
int atoi(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 数値を表す、null で終わる文字列 |

戻り値は、文字列の先頭から読み取れた整数です。先頭の空白は飛ばされ、符号（`+`、`-`）と数字が読まれます。数字でない文字に出会うと、そこで読むのを止めて、それまでの値を返します。`"12abc"` は 12、`"abc"` は 0 です。

欠点は、失敗を検出できないことです。`"abc"` の 0 と、`"0"` の 0 は区別できません。さらに、値が `int` の範囲を超えると、未定義動作です（エラーを返すわけでもありません）。

文字列の途中で読み取りを終えた位置も分かりません。入力を検査したい場合は、`std::strtol`（読み終えた位置を返す）、`std::from_chars`（例外も確保もなく速い）、`std::stoi`（失敗で例外）のいずれかを使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("atoi(\"123\")   = {}", std::atoi("123"));
  std::println("atoi(\"12abc\") = {}", std::atoi("12abc"));   // 数字でない所で止まる
  std::println("atoi(\"abc\")   = {}", std::atoi("abc"));     // 失敗しても 0
  std::println("atoi(\"-45\")   = {}", std::atoi("-45"));
}
```

```text title="実行結果"
atoi("123")   = 123
atoi("12abc") = 12
atoi("abc")   = 0
atoi("-45")   = -45
```

## ゲームでの使いどころ

ごく簡単なツールや、入力が必ず正しいと分かっている場面で使います。ユーザーの入力や外部のファイルから読む数値には向きません。

```cpp
// 失敗を検出したい場合は from_chars を使う
int value = 0;
auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), value);
if (ec != std::errc{}) { /* 変換に失敗 */ }
```

## よくあるミス

??? failure "失敗した 0 と本当の 0 を区別できない"
    `std::from_chars` か `std::strtol` を使います。

??? failure "範囲外の値で未定義動作になる"
    範囲を検査できる関数に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtol`](strtol.md) | 失敗と読み終えた位置が分かる |
| [`stoi`](../../containers/stoi.md) | `std::string` から。失敗で例外 |
| [`from_chars`](../../io/from_chars.md) | 例外なし・確保なし。最も速い |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atoi(str)` は文字列を `int` に変える
    - [x] 失敗しても 0 を返し、区別できない
    - [x] 新しいコードでは `from_chars` を使う

## 関連ページ

- [cpprefjp: std::atoi](https://cpprefjp.github.io/reference/cstdlib/atoi.html)
- [cppreference: std::atoi](https://en.cppreference.com/w/cpp/numeric/math/atoi)
