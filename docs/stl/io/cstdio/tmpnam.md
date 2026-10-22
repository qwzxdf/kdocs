---
title: std::tmpnam
summary: "一時ファイルに使える名前を作る（非推奨）。"
order: 900
tags:
  - 入出力・文字列
---

# std::tmpnam

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

一時ファイルの名前を作りますが、名前を作ってから開くまでの間に、他のプロセスが同じ名前を使う危険があります（競合）。`tmpfile` を使うほうが安全です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::tmpnam {#tmpnam}

```cpp
char* tmpnam(char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | char* | 名前を入れる配列（`L_tmpnam` 以上の大きさ）。`nullptr` なら内部の静的領域 |

- 戻り値: 名前（失敗したら `nullptr`）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char name[L_tmpnam];
  std::println("{}", std::tmpnam(name) != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （古い C のコードの保守） |

## よくあるミス

??? failure "名前だけ作って後で開く"
    競合の危険があります。`tmpfile` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tmpfile`](tmpfile.md) | 安全な一時ファイル |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一時ファイルに使える名前を作る（非推奨）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::tmpnam](https://cpprefjp.github.io/reference/cstdio/tmpnam.html)
- [cppreference: std::tmpnam](https://en.cppreference.com/w/cpp/io/c/tmpnam)
