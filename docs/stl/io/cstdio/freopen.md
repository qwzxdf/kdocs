---
title: std::freopen
summary: "開いているファイル（stdout など）を、別のファイルに付け替える。"
order: 900
tags:
  - 入出力・文字列
---

# std::freopen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`stdout` の出力先を、ファイルに切り替えたいことがあります（ログ出力の保存など）。`freopen("log.txt", "w", stdout)` で、以降の `printf` の出力がファイルへ向かいます。元に戻すのは難しいので、必要な場面は限られます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::freopen {#freopen}

```cpp
std::FILE* freopen(const char* filename, const char* mode, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | const char* | 新しいファイル名 |
| `mode` | const char* | 開くモード（`"w"` など） |
| `stream` | FILE* | 付け替えるストリーム（`stdout` など） |

- 戻り値: 成功なら `stream`、失敗なら `nullptr`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  if (std::freopen("out.txt", "w", stdout) != nullptr) {
    std::printf("このメッセージはファイルへ\n");
  }
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 標準出力をファイルに保存する |

## よくあるミス

??? failure "元に戻せない"
    付け替えると、元の出力先には戻せません。一時的な切り替えには `rdbuf` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | ファイルを開く |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 開いているファイル（stdout など）を、別のファイルに付け替える
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::freopen](https://cpprefjp.github.io/reference/cstdio/freopen.html)
- [cppreference: std::freopen](https://en.cppreference.com/w/cpp/io/c/freopen)
