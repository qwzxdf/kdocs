---
title: std::ferror
summary: "ファイルの読み書きでエラーが起きたかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::ferror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

読み込みが終わった理由が終端なのか、エラーなのかを区別するために使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ferror {#ferror}

```cpp
int ferror(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |

- 戻り値: エラーがあれば 0 以外
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("a", f);
  std::println("{}", std::ferror(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 読み込みの失敗の原因を調べる |

## よくあるミス

??? failure "終端とエラーを混同する"
    終端は `feof`、エラーは `ferror` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feof`](feof.md) | 終端かを調べる |
| [`perror`](perror.md) | エラーの内容を出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの読み書きでエラーが起きたかを調べる
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ferror](https://cpprefjp.github.io/reference/cstdio/ferror.html)
- [cppreference: std::ferror](https://en.cppreference.com/w/cpp/io/c/ferror)
