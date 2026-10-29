---
title: std::resetiosflags
summary: "書式フラグを、まとめて解除する。"
order: 900
tags:
  - 入出力・文字列
---

# std::resetiosflags

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iomanip>`
</div>

16 進で出力したあと、10 進に戻したい。右そろえにしたあと、元に戻したい。書式の設定を戻すには、「立っているビットを消す」操作が要ります。`std::resetiosflags` は、指定したフラグを一度にまとめて消す操作子です。特に、`setiosflags` で基数を変えるときの下ごしらえとして使います。

!!! tip "ポイント"
    - `resetiosflags(std::ios::basefield)` のように、グループごとまとめて消せる
    - 消すだけで、立てはしない。続けて `setiosflags` か、専用の操作子で立てる
    - 基数は `basefield`、そろえ方は `adjustfield`、浮動小数点は `floatfield` というグループがある
    - 全部を元に戻すなら、保存した `flags()` を戻すほうが簡単

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::resetiosflags {#resetiosflags}

```cpp
/* 未規定 */ resetiosflags(std::ios_base::fmtflags mask);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mask` | `ios_base::fmtflags` | 消すフラグ。`|` で複数つなげられる |

`str.setf(std::ios_base::fmtflags(0), mask)` を呼びます。これは、`mask` に含まれるビットを、すべて 0 にする、という意味です。立てているビットだけでなく、指定した範囲全体が消えるので、グループ名（`basefield` など）を渡すと、そのグループの中で立っていたものが、何であっても消えます。

主なグループは、次のとおりです。

| グループ | 含まれるフラグ | 意味 |
| --- | --- | --- |
| `basefield` | `dec`・`oct`・`hex` | 整数の基数 |
| `adjustfield` | `left`・`right`・`internal` | 幅に足りないときのそろえ方 |
| `floatfield` | `fixed`・`scientific` | 浮動小数点の形式（両方で `hexfloat`） |

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\n';

  // 基数を消すと、どのビットも立たない。整数は 10 進で出る
  std::cout << std::resetiosflags(std::ios::basefield) << 255 << '\n';

  std::cout << std::left << std::setw(6) << "ab" << "|\n";

  // そろえ方を消すと、既定の右そろえに戻る
  std::cout << std::resetiosflags(std::ios::adjustfield) << std::setw(6) << "ab" << "|\n";
}
```

```text title="実行結果"
ff
255
ab    |
    ab|
```

`basefield` を消すと、`dec`・`oct`・`hex` のどれも立たない状態になり、整数は 10 進で出ます。`adjustfield` を消すと、`left` が消えて、既定の右そろえに戻ります。

## ゲームでの使いどころ

ログ関数の中で、書式を一時的に変えるときです。関数に入るところで `auto old = os.flags();` と保存し、出るところで `os.flags(old)` と戻すのが、いちばん確実で、`resetiosflags` を使うよりも漏れが出ません。`resetiosflags` が活きるのは、1 つの出力式の中で、特定のグループだけ戻したいときです。

## よくあるミス

??? failure "`resetiosflags(std::ios::hex)` で、10 進に戻らない"
    `hex` のビットだけを消すと、どのビットも立たず、結果は 10 進に見えます。ただし、それは `dec` が立ったわけではありません。意図を明確にするなら、`resetiosflags(std::ios::basefield) << std::setiosflags(std::ios::dec)` と、続けて書きます。

??? failure "`resetiosflags(0)` を呼んで、何も起きない"
    `mask` が 0 だと、消すビットがありません。グループ名か、消したいフラグを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setiosflags`](setiosflags.md) | 指定したフラグを立てる |
| [`dec`](dec.md) | 基数を 10 進にする専用の操作子。古いビットも消してくれる |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `resetiosflags` は、指定したフラグを、まとめて消す
    - [x] グループ名（`basefield`・`adjustfield`・`floatfield`）で、そのグループ全体を消せる
    - [x] 全部を戻したいときは、`flags()` で保存した値を、あとで戻す

## 関連ページ

- [cpprefjp: std::resetiosflags](https://cpprefjp.github.io/reference/ios/resetiosflags.html)
- [cppreference: std::resetiosflags](https://en.cppreference.com/w/cpp/io/manip/resetiosflags)
