---
title: std::scanf
summary: "標準入力から、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::scanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`scanf("%d", &n)` のように、書式に合わせて標準入力から値を読みます。読み込めた個数が戻ります。入力の失敗の扱いが難しく、新しいコードでは `std::cin` が安全です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::scanf {#scanf}

```cpp
int scanf(const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | const char* | 書式文字列 |
| `...` | ポインタ | 読み込んだ値を入れる場所 |

- 戻り値: 読み込めた個数。入力が終わったら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  int n = 0;
  int count = std::scanf("%d", &n);
  std::println("{} {}", count, n);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （競技プログラミングや、古い C のコード） |

## よくあるミス

??? failure "`&` を忘れる"
    変数のアドレス（`&n`）を渡さないと、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cin`](../cin.md) | C++ の入力 |
| [`sscanf`](sscanf.md) | 文字列から読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力から、書式を指定して読み込む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::scanf](https://cpprefjp.github.io/reference/cstdio/scanf.html)
- [cppreference: std::scanf](https://en.cppreference.com/w/cpp/io/c/scanf)
