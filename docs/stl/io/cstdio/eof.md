---
title: EOF
summary: "ファイルの終端またはエラーを表す定数（負の整数）。"
order: 900
tags:
  - 入出力・文字列
---

# EOF

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetc` などが、終端やエラーを知らせるときに返す値です。負の整数（ふつう `-1`）で、通常の文字（0〜255）と区別できます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### EOF {#eof}

```cpp
#define EOF (-1)  // 値は実装定義（負の整数）
```

- 戻り値: 負の整数の定数
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("{}", EOF < 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `fgetc` の結果の判定 |

## よくあるミス

??? failure "`char` に入れる"
    `char` に入れると、`0xFF` の文字と `EOF` が区別できません。`int` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 1 文字を読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの終端またはエラーを表す定数（負の整数）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: EOF](https://cpprefjp.github.io/reference/cstdio/eof.html)
- [cppreference: EOF](https://en.cppreference.com/w/cpp/io/c/EOF)
