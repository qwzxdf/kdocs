---
title: std::ftell
summary: "ファイルの現在位置を返す。"
order: 900
tags:
  - 入出力・文字列
---

# std::ftell

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

いま、ファイルのどこを読み書きしているかを先頭からのバイト数で返します。`fseek` で戻る位置を覚えておくときに使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ftell {#ftell}

```cpp
long ftell(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |

- 戻り値: 現在位置（失敗したら `-1L`）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("abc", f);
  std::println("{}", std::ftell(f));
  std::fclose(f);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルの大きさを調べる（末尾に移動して `ftell`） |

## よくあるミス

??? failure "2GB を超えるファイル"
    `long` が 32 ビットの環境では、大きなファイルで使えません。`std::filesystem::file_size` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fseek`](fseek.md) | 位置を動かす |
| [`fgetpos`](fgetpos.md) | 位置を保存する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの現在位置を返す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ftell](https://cpprefjp.github.io/reference/cstdio/ftell.html)
- [cppreference: std::ftell](https://en.cppreference.com/w/cpp/io/c/ftell)
