---
title: std::oct
summary: "整数を 8 進数で出力・入力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::oct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

Unix のファイル権限は、`0644` のように 8 進数で表します。`std::cout << 420` では `420` と出るところを、`644` と表示したい。整数を 8 進数にする操作子が `std::oct` です。

!!! tip "ポイント"
    - `std::cout << std::oct << 420` で `644` と出る
    - 戻すには `std::dec`。設定は残り続ける
    - `std::showbase` を併用すると、先頭に `0` が付く
    - 入力にも効く。`0` で始まる文字列を 8 進数として読む

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::oct {#oct}

```cpp
std::ios_base& oct(std::ios_base& str);
```

ストリームの基数を 8 進数にします。[`hex`](hex.md) の 8 進数版で、残り続ける性質も同じです。

`showbase` と併用すると、8 進数の印として、先頭に `0` が付きます（`0644`）。ただし値が 0 のときは、`0` だけです。

ゲームで 8 進数を使う場面は少ないのですが、ファイルの権限（`std::filesystem::perms` の値は 8 進数で定義されています）を表示するときは、`std::cout << std::oct << static_cast<unsigned>(perms)` と書くと、`chmod` と同じ見た目で確認できます。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::oct << 420 << '\n';              // 644
  std::cout << std::showbase << 420 << '\n';         // 0644
  std::cout << std::noshowbase << std::dec << 420 << '\n';   // 420
}
```

```text title="実行結果"
644
0644
420
```

## ゲームでの使いどころ

ファイルの権限の確認や、古い形式のデータの解析で使います。ゲーム本体で使うことは、あまりありません。

## よくあるミス

??? failure "戻し忘れて、数値の表示が崩れる"
    `std::dec` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`dec`](dec.md) | 10 進数にする |
| [`setbase`](setbase.md) | 基数を数値で指定する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数を 8 進数にする
    - [x] 戻すまで続く
    - [x] 権限の表示に使う

## 関連ページ

- [cpprefjp: std::oct](https://cpprefjp.github.io/reference/ios/oct.html)
- [cppreference: std::oct](https://en.cppreference.com/w/cpp/io/manip/oct)
