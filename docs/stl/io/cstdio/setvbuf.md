---
title: std::setvbuf
summary: "ファイルのバッファの方式（全部・行・なし）と大きさを設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setvbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`setbuf` より細かく、バッファの方式（`_IOFBF` 全バッファ、`_IOLBF` 行バッファ、`_IONBF` なし）と大きさを指定します。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::setvbuf {#setvbuf}

```cpp
int setvbuf(std::FILE* stream, char* buffer, int mode, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |
| `buffer` | char* | バッファ（`nullptr` なら自動） |
| `mode` | int | `_IOFBF`・`_IOLBF`・`_IONBF` |
| `size` | size_t | バッファの大きさ |

- 戻り値: 成功なら 0
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  static char buf[1024];
  std::println("{}", std::setvbuf(stdout, buf, _IOFBF, sizeof buf));
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大量出力の前にバッファを大きくする |

## よくあるミス

??? failure "ローカル配列を渡す"
    バッファは、ファイルが閉じられるまで生きている必要があります。`static` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setbuf`](setbuf.md) | 簡易版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルのバッファの方式（全部・行・なし）と大きさを設定する
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::setvbuf](https://cpprefjp.github.io/reference/cstdio/setvbuf.html)
- [cppreference: std::setvbuf](https://en.cppreference.com/w/cpp/io/c/setvbuf)
