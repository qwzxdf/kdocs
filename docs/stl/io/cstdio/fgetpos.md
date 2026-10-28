---
title: std::fgetpos
summary: "ファイルの現在位置を、保存する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`ftell` と違い、大きなファイルでも使え、特殊な状態も保存できます。保存した位置は、`fsetpos` で復元します。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetpos {#fgetpos}

```cpp
int fgetpos(std::FILE* stream, std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |
| `pos` | fpos_t* | 位置の保存先 |

- 戻り値: 成功なら 0
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("abc", f);
  std::rewind(f);
  std::fpos_t pos;
  std::fgetpos(f, &pos);
  std::fgetc(f);
  std::fsetpos(f, &pos);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | あとで戻るために位置を覚える |

## よくあるミス

??? failure "保存した値を数値として扱う"
    `fpos_t` の中身は実装依存です。計算には使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fsetpos`](fsetpos.md) | 位置を復元する |
| [`ftell`](ftell.md) | 数値で位置を取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの現在位置を保存する
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fgetpos](https://cpprefjp.github.io/reference/cstdio/fgetpos.html)
- [cppreference: std::fgetpos](https://en.cppreference.com/w/cpp/io/c/fgetpos)
