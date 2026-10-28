---
title: std::fgetpos
summary: "ファイルの現在位置を、保存する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルの途中で、あとで戻ってきたい位置を記録しておきたい。`ftell` は `long` で位置を返すので、巨大なファイルや、テキスト モードの特殊な状態では、足りないことがあります。`std::fgetpos` は、<strong>位置の情報を、ライブラリが決めた型（`fpos_t`）にそのまま保存する</strong>関数です。

!!! tip "ポイント"
    - `fgetpos(ファイル, &pos)` で、今の位置を `fpos_t` に保存する
    - 保存した位置に戻るのは `fsetpos`
    - `fpos_t` の中身は不透明。数値として表示したり、計算したりしない
    - 戻り値は、成功なら 0、失敗なら 0 以外

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetpos {#fgetpos}

```cpp
int fgetpos(std::FILE* stream, std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を調べるファイル |
| `pos` | `fpos_t*` | 位置の保存先 |

`fpos_t` には、位置だけでなく、マルチバイト文字の解析途中の状態など、ファイルを同じ状態で再開するための情報が入ります。そのため、`ftell` の `long` より、確実に元の状態へ戻れます。

型の中身は規格が決めていないので、整数のように表示したり、足し算したりできません。保存して、`fsetpos` に渡すためだけの値です。

Windows の MSVC では `fpos_t` が 64 ビットなので、2 GB を超えるファイルでも使えます。`long` が 32 ビットの環境で、大きなファイルの位置を保存する、簡単な方法の 1 つです。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("ab.txt", "w");
  std::fputs("0123456789", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ab.txt", "r");
  std::fgetc(f);
  std::fgetc(f);                       // 2 文字進める

  std::fpos_t mark;
  std::fgetpos(f, &mark);              // ここ（3 文字目の手前）を記録する
  std::println("記録した位置から: {}", static_cast<char>(std::fgetc(f)));

  std::fsetpos(f, &mark);              // 記録した位置に戻る
  std::println("戻って読み直し: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
記録した位置から: 2
戻って読み直し: 2
```

## ゲームでの使いどころ

パーサーが、先の内容を見て、うまくいかなければ元の位置からやり直す（バックトラック）ときに使います。`fgetpos` で位置を保存し、試して失敗したら `fsetpos` で戻ります。

位置が数値で扱えて足りるなら、`ftell` と `fseek` のほうが簡単です。

## よくあるミス

??? failure "`fpos_t` を整数として表示・計算しようとする"
    中身は不透明です。保存して `fsetpos` に渡すだけにします。

??? failure "別のファイルの `fpos_t` を使い回す"
    その `fpos_t` は、取得したファイルでのみ有効です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fsetpos`](fsetpos.md) | 保存した位置に戻る |
| [`ftell`](ftell.md) | 位置を `long` で返す |
| [`fseek`](fseek.md) | 数値で位置を動かす |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 位置を `fpos_t` に保存する
    - [x] 戻るのは `fsetpos`
    - [x] 中身は数値として扱わない

## 関連ページ

- [cpprefjp: std::fgetpos](https://cpprefjp.github.io/reference/cstdio/fgetpos.html)
- [cppreference: std::fgetpos](https://en.cppreference.com/w/cpp/io/c/fgetpos)
