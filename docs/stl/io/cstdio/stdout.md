---
title: std::stdout
summary: "標準出力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stdout

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

プログラムが起動した時点で開いている、標準出力です。`fprintf(stdout, ...)` は `printf(...)` と同じです。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::stdout {#stdout}

```cpp
extern std::FILE* stdout;
```

- 戻り値: 標準出力の `FILE*`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::fputs("out\n", stdout);
}
```

```text title="実行結果"
out
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンソールへの出力 |

## よくあるミス

??? failure "閉じる"
    `stdout` を `fclose` で閉じないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stdin`](stdin.md) | 標準入力 |
| [`stderr`](stderr.md) | 標準エラー出力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力を表す FILE*
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::stdout](https://cpprefjp.github.io/reference/cstdio/stdout.html)
- [cppreference: std::stdout](https://en.cppreference.com/w/cpp/io/c/stdout)
