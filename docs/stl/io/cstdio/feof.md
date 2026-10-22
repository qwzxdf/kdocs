---
title: std::feof
summary: "ファイルの終端に達したかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::feof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetc` などで、終端を**越えて読もうとした**とき、終端の状態が立ちます。ループ条件に `feof` だけを使うと、最後に 1 回余分に読むことになるので、読み込みの戻り値で判定します。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::feof {#feof}

```cpp
int feof(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |

- 戻り値: 終端なら 0 以外
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
  std::fgetc(f);  // 終端を越えて読む
  std::println("{}", std::feof(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 読み込みが終端で終わったか、エラーで終わったかを区別する |

## よくあるミス

??? failure "`while (!feof(f))` でループする"
    最後の読み込みの直後は、まだ終端の状態が立たないので、1 回余分にループします。`while (fgets(...))` のように、戻り値で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ferror`](ferror.md) | エラーかを調べる |
| [`clearerr`](clearerr.md) | 状態をクリアする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの終端に達したかを調べる
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::feof](https://cpprefjp.github.io/reference/cstdio/feof.html)
- [cppreference: std::feof](https://en.cppreference.com/w/cpp/io/c/feof)
