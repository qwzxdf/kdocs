---
title: std::fsetpos
summary: "`fgetpos` で保存した位置に、読み書き位置を戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::fsetpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetpos` で保存した位置をそのまま復元します。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fsetpos {#fsetpos}

```cpp
int fsetpos(std::FILE* stream, const std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |
| `pos` | const fpos_t* | `fgetpos` で得た位置 |

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
| 使いどころ | あとで戻る位置を復元する |

## よくあるミス

??? failure "別のファイルの位置を使う"
    位置は、同じファイルのものを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetpos`](fgetpos.md) | 位置を保存する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fgetpos` で保存した位置に読み書き位置を戻す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fsetpos](https://cpprefjp.github.io/reference/cstdio/fsetpos.html)
- [cppreference: std::fsetpos](https://en.cppreference.com/w/cpp/io/c/fsetpos)
