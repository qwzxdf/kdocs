---
title: std::stoi
summary: "文字列を int に変換する（失敗すると例外）。"
order: 61
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stoi

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stoi` は、**文字列を `int` に変換する**関数です。数字として読めなければ `std::invalid_argument`、範囲外なら `std::out_of_range` の例外を投げます。仲間に `stol`、`stoll`、`stoul` などがあります。例外を使いたくない場面では、[`std::from_chars`](../io/from_chars.md) を使います。

!!! tip "ポイント"
    - 数字の前の空白は読み飛ばされ、数字の後ろの文字は無視される。
    - 変換できないと**例外**。
    - 失敗を例外にしたくないなら `from_chars`。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stoi {#stoi}

```cpp
int stoi(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 変換する文字列。先頭の空白は飛ばされる |
| `pos` | `std::size_t*` | 変換に使った文字数を受け取る（要らなければ省略） |
| `base` | `int` | 進数（2〜36）。`16` なら 16 進数、`0` なら `0x` などから自動判定 |

- 戻り値: 変換した `int`
- 例外: 数字で始まらなければ `std::invalid_argument`、int に入らなければ `std::out_of_range`

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stoi("1500"));
  std::println("{}", std::stoi("ff", nullptr, 16));

  std::size_t used = 0;
  int value = std::stoi("42px", &used);
  std::println("{} ({} 文字使った)", value, used);
}
```

```text title="実行結果"
1500
255
42 (2 文字使った)
```

!!! note "実際は"
    例外を使わないなら `std::from_chars`（`<charconv>`）のほうが速く、失敗をエラーコードで返してくれます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの数値の読み込み | `int gold = std::stoi(text);` |

## よくあるミス

??? failure "例外を握りつぶさない"
    `try` / `catch` で `invalid_argument` と `out_of_range` を受けます。

??? failure ""12abc" が 12 になる"
    後ろの文字は無視されます。全体が数値か確かめるなら `from_chars` の `ptr`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../io/from_chars.md) | 例外なし・高速 |
| [`stof`](stof.md) | float に変換 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → int
    - [x] 失敗は例外
    - [x] 例外なしなら from_chars

## 関連ページ

- [cpprefjp: std::stoi](https://cpprefjp.github.io/reference/string/stoi.html)
- [cppreference: std::stoi](https://en.cppreference.com/w/cpp/string/basic_string/stoi)
