---
title: std::rewind
summary: "ファイルの読み書き位置を、先頭に戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::rewind

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fseek(f, 0, SEEK_SET)` と同じですが、エラー状態もクリアします。書いたあとにすぐ読み返すときに使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::rewind {#rewind}

```cpp
void rewind(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |

- 戻り値: なし
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("a", f);
  std::rewind(f);
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
| 使いどころ | 書いたデータを読み返す |

## よくあるミス

??? failure "エラーを見落とす"
    `rewind` は成否を返しません。確かめたいなら `fseek` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fseek`](fseek.md) | 位置を動かす |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの読み書き位置を先頭に戻す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rewind](https://cpprefjp.github.io/reference/cstdio/rewind.html)
- [cppreference: std::rewind](https://en.cppreference.com/w/cpp/io/c/rewind)
