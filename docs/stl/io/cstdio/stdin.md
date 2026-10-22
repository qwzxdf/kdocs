---
title: std::stdin
summary: "標準入力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stdin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

プログラムが起動した時点で開いている、標準入力です。`fgets(buf, n, stdin)` のように使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::stdin {#stdin}

```cpp
extern std::FILE* stdin;
```

- 戻り値: 標準入力の `FILE*`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("{}", stdin != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンソールからの入力 |

## よくあるミス

??? failure "閉じる"
    `stdin` を `fclose` で閉じないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stdout`](stdout.md) | 標準出力 |
| [`std::cin`](../cin.md) | C++ の標準入力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力を表す FILE*
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::stdin](https://cpprefjp.github.io/reference/cstdio/stdin.html)
- [cppreference: std::stdin](https://en.cppreference.com/w/cpp/io/c/stdin)
