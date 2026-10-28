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

一時ファイルの名前だけを、先に決めたい。`std::tmpnam` は、<strong>ほかのファイルとぶつからない名前</strong>を作る関数ですが、名前を作ってから実際にファイルを作るまでの間に、他のプロセスが同じ名前を作ってしまう危険があり、現在は使うことが勧められません。

!!! tip "ポイント"
    - `tmpnam(バッファー)` で、使われていない名前を作る。失敗は `nullptr`
    - 名前の確認とファイルの作成が別なので、競合する（TOCTOU）
    - MSVC や GCC は、警告を出す。新しいコードでは使わない
    - 代わりに `tmpfile`、または `temp_directory_path` に自分で名前を付ける

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::tmpnam {#tmpnam}

```cpp
char* tmpnam(char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `char*` | 名前を入れるバッファー（`L_tmpnam` バイト以上）。`nullptr` なら、内部の静的な領域に入れる |

使われていない名前を返します。返された名前は、作成した時点では未使用ですが、そのファイルをこちらが作るまでに、別のプロセスが同じ名前で作成できます。この隙を突くと、他者に自分の一時ファイルを乗っ取られる脆弱性になります。

`filename` に `nullptr` を渡すと、内部の領域に名前を入れ、その場所を返します。2 回目の呼び出しで上書きされ、複数のスレッドから呼ぶと壊れます。

GCC は、リンク時に「`tmpnam` は危険」と警告し、MSVC は警告 C4996 を出します。代わりに、[`tmpfile`](tmpfile.md)（名前を出さず、競合なしで開く）や、`std::filesystem::temp_directory_path()` の下に、プロセス番号や乱数で自分の名前を作る方法を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char name[L_tmpnam];
  char* r = std::tmpnam(name);
  std::println("名前が作れた: {}", r != nullptr);
  std::println("空ではない: {}", name[0] != '\0');
}
```

```text title="実行結果"
名前が作れた: true
空ではない: true
```

## ゲームでの使いどころ

新しいコードでは使いません。古い C のコードに出てきたときは、`tmpfile` か、`mkstemp`（POSIX）、`std::filesystem` を使った書き方に置き換えます。

## よくあるミス

??? failure "名前を作ってから、あとでファイルを作って、競合する"
    確認と作成の間に隙があります。`tmpfile` のように、作成と同時に開く方法を使います。

??? failure "`nullptr` を渡して、複数のスレッドから呼ぶ"
    内部の領域が共有され、壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tmpfile`](tmpfile.md) | 競合のない一時ファイルを開く |
| [`temp_directory_path`](../filesystem/temp_directory_path.md) | 一時フォルダーの場所 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 使われていない名前を作る
    - [x] 競合に弱く、非推奨
    - [x] 代わりに `tmpfile`

## 関連ページ

- [cpprefjp: std::tmpnam](https://cpprefjp.github.io/reference/cstdio/tmpnam.html)
- [cppreference: std::tmpnam](https://en.cppreference.com/w/cpp/io/c/tmpnam)
