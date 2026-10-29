---
title: std::setiosflags
summary: "書式フラグを、まとめて設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setiosflags

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iomanip>`
</div>

`std::hex` や `std::showpos` のような操作子は、それぞれ 1 つの設定を変えます。ストリームの書式は、内部では 1 つの整数の中のビット（フラグ）で管理されていて、`setiosflags` は、そのビットを名前で直接立てる操作子です。複数の設定を 1 回の `<<` でまとめて変えられる一方、ビットの扱いを知らないと、思った通りに効かない落とし穴があります。

!!! tip "ポイント"
    - `setiosflags(std::ios::hex | std::ios::showbase)` のように、複数のフラグを `|` でつなげて立てる
    - 立てるだけで、**同じグループのほかのフラグは消さない**
    - 基数（`dec`・`hex`・`oct`）を変えるときは、先に `resetiosflags(std::ios::basefield)` が要る
    - 通常は、`hex` や `showpos` のような、専用の操作子のほうが安全

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::setiosflags {#setiosflags}

```cpp
/* 未規定 */ setiosflags(std::ios_base::fmtflags mask);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mask` | `ios_base::fmtflags` | 立てるフラグ。`|` で複数つなげられる |

`str.setf(mask)` を呼ぶのと同じです。`setf(mask)` は、`mask` に含まれるビットを立てて、それ以外のビットは変えません。

書式のフラグには、グループがあります。基数は `dec`・`oct`・`hex` のうちどれか 1 つ（`basefield`）、そろえ方は `left`・`right`・`internal` のうちどれか 1 つ（`adjustfield`）、浮動小数点の形式は `fixed`・`scientific` など（`floatfield`）です。同じグループの中で、複数のビットが立った状態は、定義されていません。`hex` の操作子は、内部で `setf(hex, basefield)` と書き、同じグループの古いビットを消してから立てています。`setiosflags` には、その消す処理がありません。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  // 10 進のビットが立ったままなので、hex を足しても 10 進のまま
  std::cout << std::setiosflags(std::ios::hex | std::ios::showbase) << 255 << '\n';

  // 基数のビットをまとめて消してから、hex を立てる
  std::cout << std::resetiosflags(std::ios::basefield)
            << std::setiosflags(std::ios::hex | std::ios::showbase) << 255 << '\n';

  // 設定は残り続ける
  std::cout << 4096 << '\n';

  // 元に戻す
  std::cout << std::resetiosflags(std::ios::basefield | std::ios::showbase)
            << std::setiosflags(std::ios::dec) << 255 << '\n';
}
```

```text title="実行結果"
255
0xff
0x1000
255
```

1 行目は、ストリームの最初の状態が `dec` なので、`hex` を足しても `dec` と `hex` の両方が立ち、10 進で出力されます（`showbase` だけは立っても、10 進には付く接頭辞がないので効きません）。2 行目は、`basefield` をいったんすべて消したので、`hex` だけが立ち、`0xff` と出ます。3 行目は、設定が残っているので、続く出力も 16 進です。

## ゲームでの使いどころ

書式の設定を、変数に保存して、あとで戻したい場面で使います。`std::ios::fmtflags old = os.flags();` で今の設定を保存しておき、書式を変えて出力したあと、`os.flags(old)` で戻します。これは `setiosflags` の仕事ではありませんが、フラグを扱う基本の形で、ログ関数がストリームの状態を呼び出し元に残さない、ために使えます。

16 進ダンプの出力など、局所的に書式を変える場面では、`hex` などの専用の操作子を使うほうが、書き間違えにくく、読みやすいです。

## よくあるミス

??? failure "`setiosflags(std::ios::hex)` を使ったのに、10 進のまま出る"
    `dec` のビットが立ったままです。`resetiosflags(std::ios::basefield)` で基数のビットを消してから立てるか、`std::hex` を使います。

??? failure "設定が残って、あとの出力がすべて 16 進になった"
    フラグは変えるまで残ります。出力が終わったら、`resetiosflags` で消して、元の設定に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`resetiosflags`](resetiosflags.md) | 指定したフラグを消す |
| [`hex`](hex.md)・[`dec`](dec.md)・[`oct`](oct.md) | 基数の専用の操作子。同じグループの古いビットを消してくれる |
| [`showpos`](showpos.md)・[`showbase`](showbase.md) | 個別の設定を立てる操作子 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `setiosflags` は、指定したフラグを立てる。ほかのフラグは消さない
    - [x] 基数のように排他のグループは、先に `resetiosflags(basefield)` で消す
    - [x] 普通は、`hex` などの専用の操作子を使うほうが安全

## 関連ページ

- [cpprefjp: std::setiosflags](https://cpprefjp.github.io/reference/ios/setiosflags.html)
- [cppreference: std::setiosflags](https://en.cppreference.com/w/cpp/io/manip/setiosflags)
