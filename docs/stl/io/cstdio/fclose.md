---
title: std::fclose
summary: "ファイルを閉じる。"
order: 900
tags:
  - 入出力・文字列
---

# std::fclose

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fopen` で開いたファイルは、使い終わったら必ず閉じます。閉じないと、バッファの内容が書き出されなかったり、ファイル記述子がリークしたりします。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fclose {#fclose}

```cpp
int fclose(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 閉じるファイル |

- 戻り値: 成功なら 0、失敗なら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::println("{}", std::fclose(f));
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルを閉じる（RAII で包むのが安全） |

## よくあるミス

??? failure "閉じたあとに使う"
    閉じたあとの `FILE*` を使うと未定義動作です。`unique_ptr` と `fclose` を組み合わせると、閉じ忘れを防げます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | 開く |
| [`std::ifstream`](../ifstream.md) | デストラクタで自動で閉じる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを閉じる
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fclose](https://cpprefjp.github.io/reference/cstdio/fclose.html)
- [cppreference: std::fclose](https://en.cppreference.com/w/cpp/io/c/fclose)
