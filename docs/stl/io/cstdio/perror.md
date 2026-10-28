---
title: std::perror
summary: "`errno` の内容を、説明つきで標準エラー出力に出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::perror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイル操作の失敗の原因を人が読める文字列で出したいとき、`perror("ファイル名")` と書くと、`ファイル名: No such file or directory` のように標準エラー出力に出ます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::perror {#perror}

```cpp
void perror(const char* s);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | const char* | 先頭に付ける説明（`nullptr` や空文字列なら付けない） |

- 戻り値: なし
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("not_exist.txt", "r");
  if (f == nullptr) {
    std::perror("open failed");
  }
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルを開けなかった理由をログに出す |

## よくあるミス

??? failure "成功時の `errno` を見る"
    `errno` は成功しても 0 に戻されません。失敗を確かめた直後に呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strerror`](../../memory/cstring/strerror.md) | 文字列として取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `errno` の内容を説明つきで標準エラー出力に出す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::perror](https://cpprefjp.github.io/reference/cstdio/perror.html)
- [cppreference: std::perror](https://en.cppreference.com/w/cpp/io/c/perror)
