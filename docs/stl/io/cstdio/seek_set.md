---
title: SEEK_SET
summary: "`fseek` の基準：ファイルの先頭。"
order: 900
tags:
  - 入出力・文字列
---

# SEEK_SET

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fseek` に位置を伝えるとき、「何バイト動かすか」だけでは足りません。先頭から数えるのか、今の位置から数えるのか。その基準を選ぶ 3 つの定数のうち、先頭を基準にするのが `SEEK_SET` です。

!!! tip "ポイント"
    - `fseek(f, n, SEEK_SET)` で、先頭から `n` バイトの位置へ移る
    - `n` は 0 以上。負の値は失敗する
    - `fseek(f, 0, SEEK_SET)` は先頭へ戻る。`rewind` と似ている
    - 値そのものは環境定義。名前で使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### SEEK_SET {#SEEK_SET}

```cpp
#define SEEK_SET /* 整数定数 */
```

`fseek` の第 3 引数 `origin` に渡し、位置の基準を「ファイルの先頭」にします。`offset` が、先頭からのバイト数です。

パックファイルの目次に「アセット A は 先頭から 1024 バイト目」と記録してあるなら、読み込むときに `fseek(f, 1024, SEEK_SET)` で飛びます。位置が絶対的な値で表されるので、ほとんどの場面で、これを使います。

テキスト モードで開いたファイルでは、`SEEK_SET` と共に使える `offset` は、`ftell` が返した値と 0 だけです。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fseek(f, 3, SEEK_SET);       // 先頭から 3 バイト目へ
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fseek(f, 0, SEEK_SET);       // 先頭へ戻る
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
D
A
```

## ゲームでの使いどころ

パックファイルから、目次で指定された位置のアセットを読み込むときに使います。アセットの位置は絶対的な値なので、基準は先頭です。

## よくあるミス

??? failure "負の `offset` を渡して失敗する"
    先頭より前には行けません。末尾からの相対位置なら `SEEK_END` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`SEEK_CUR`](seek_cur.md) | 今の位置を基準にする |
| [`SEEK_END`](seek_end.md) | 末尾を基準にする |
| [`fseek`](fseek.md) | これらを受け取る関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭を基準にする
    - [x] 絶対的な位置へ飛ぶ
    - [x] `offset` は 0 以上

## 関連ページ

- [cpprefjp: SEEK_SET](https://cpprefjp.github.io/reference/cstdio/seek_set.html)
- [cppreference: SEEK_SET](https://en.cppreference.com/w/cpp/io/c/SEEK_SET)
