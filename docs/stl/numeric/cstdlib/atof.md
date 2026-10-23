---
title: std::atof
summary: "文字列を double に変換する。"
order: 900
tags:
  - 数値
---

# std::atof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

"0.75" のような小数の文字列を `double` にする、最も短い方法が `std::atof` です。`std::atoi` と同じく、失敗しても失敗とは教えてくれません。

!!! tip "ポイント"
    - `std::atof("3.14")` は 3.14
    - 数字でない文字列は 0.0 を返す。本当の 0 と区別できない
    - 範囲を超える値は未定義動作
    - 失敗を検査するなら `strtod` か `from_chars`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atof {#atof}

```cpp
double atof(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 数値を表す、null で終わる文字列 |

`std::strtod(str, nullptr)` と同じ変換を行います。先頭の空白を飛ばし、符号、数字、小数点、指数を読みます。読めなかった時点で止まり、そこまでの値を返します。

失敗を検出できません。`"abc"` も `"0"` も 0.0 を返します。範囲を超えた場合の動作は規格で決まっていません（`strtod` なら `ERANGE` が分かります）。

小数点はロケールに依存します。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("atof(\"3.14\")  = {}", std::atof("3.14"));
  std::println("atof(\"1e2\")   = {}", std::atof("1e2"));
  std::println("atof(\"abc\")   = {}", std::atof("abc"));    // 失敗しても 0
}
```

```text title="実行結果"
atof("3.14")  = 3.14
atof("1e2")   = 100
atof("abc")   = 0
```

## ゲームでの使いどころ

簡単なツールで、小数を読むだけなら使えます。ゲームの設定ファイルやユーザー入力には `strtod` か `from_chars` を使い、失敗を検出できるようにします。

## よくあるミス

??? failure "失敗を 0.0 と区別できない"
    `strtod` か `from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtod`](strtod.md) | 失敗と読み終えた位置が分かる |
| [`atoi`](atoi.md) | 整数版 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atof(str)` は文字列を `double` にする
    - [x] 失敗しても 0 を返し、区別できない
    - [x] 検査したいなら `strtod` か `from_chars`

## 関連ページ

- [cpprefjp: std::atof](https://cpprefjp.github.io/reference/cstdlib/atof.html)
- [cppreference: std::atof](https://en.cppreference.com/w/cpp/c/atof)
