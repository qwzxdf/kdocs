---
title: std::tmpfile
summary: "自動で消える一時ファイルを作る。"
order: 900
tags:
  - 入出力・文字列
---

# std::tmpfile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

プログラムが終了するか、`fclose` で閉じると自動で消える、一時ファイルを作ります。名前は不要で、`"wb+"` で開かれます。中間データの一時保存に使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::tmpfile {#tmpfile}

```cpp
std::FILE* tmpfile();
```

- 戻り値: 成功なら `FILE*`、失敗なら `nullptr`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("x", f);
  std::rewind(f);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
x
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大きな中間データを一時的に置く |

## よくあるミス

??? failure "閉じ忘れる"
    閉じるまでファイルが残ります。`fclose` を忘れないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tmpnam`](tmpnam.md) | 名前だけを作る（非推奨） |
| [`fopen`](fopen.md) | 名前つきで開く |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自動で消える一時ファイルを作る
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::tmpfile](https://cpprefjp.github.io/reference/cstdio/tmpfile.html)
- [cppreference: std::tmpfile](https://en.cppreference.com/w/cpp/io/c/tmpfile)
