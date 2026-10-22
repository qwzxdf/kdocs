---
title: std::clearerr
summary: "ファイルのエラー状態と終端状態をクリアする。"
order: 900
tags:
  - 入出力・文字列
---

# std::clearerr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルを最後まで読むと終端の状態（`feof`）が立ち、それ以降は読めません。`clearerr` で状態を戻すと、読み込みを再開できます（ファイルが後から伸びる場合など）。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::clearerr {#clearerr}

```cpp
void clearerr(std::FILE* stream);
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
  std::fgetc(f);
  std::fgetc(f);  // 終端に達する
  std::clearerr(f);
  std::println("{}", std::feof(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 追記されるログファイルを読み続ける |

## よくあるミス

??? failure "クリアしたのに読めると思う"
    状態をクリアしても、読む位置が末尾なら、読み込みは終端のままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feof`](feof.md) | 終端かを調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルのエラー状態と終端状態をクリアする
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::clearerr](https://cpprefjp.github.io/reference/cstdio/clearerr.html)
- [cppreference: std::clearerr](https://en.cppreference.com/w/cpp/io/c/clearerr)
