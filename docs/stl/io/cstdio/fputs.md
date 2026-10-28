---
title: std::fputs
summary: "ファイルに文字列を書く（改行は付かない）。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

文字列をそのままファイルに書き込みます。`puts` と違い、末尾に改行を自動で付けません。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fputs {#fputs}

```cpp
int fputs(const char* str, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 書く文字列（終端文字は書かれない） |
| `stream` | FILE* | 書き込み先 |

- 戻り値: 成功なら負でない値、失敗なら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::fputs("hi\n", stdout);
}
```

```text title="実行結果"
hi
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ログ 1 行を書く |

## よくあるミス

??? failure "改行が付くと思う"
    `fputs` は改行を付けません。自分で `\n` を書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`puts`](puts.md) | 標準出力に改行つき |
| [`fprintf`](fprintf.md) | 書式つき |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルに文字列を書く（改行は付かない）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fputs](https://cpprefjp.github.io/reference/cstdio/fputs.html)
- [cppreference: std::fputs](https://en.cppreference.com/w/cpp/io/c/fputs)
