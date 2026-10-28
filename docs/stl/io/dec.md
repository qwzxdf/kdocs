---
title: std::dec
summary: "整数を 10 進数で出力・入力する（既定）。"
order: 900
tags:
  - 入出力・文字列
---

# std::dec

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`hex` で 16 進数にした出力を、元の 10 進数に戻したい。ストリームの基数は、設定が残り続けるので、いったん変えたら、戻す操作が必要です。それが `std::dec` です。

<strong>整数の入出力を 10 進数にする</strong>操作子で、ストリームの既定の状態です。

!!! tip "ポイント"
    - ストリームの既定は 10 進数。`dec` は、`hex` や `oct` から戻すために使う
    - 入力にも効く。`std::cin >> std::hex >> x` で、16 進数の文字列を読み取れる
    - 設定は、次に変えるまで残る
    - `std::cout << std::dec` は、現在の基数に関係なく 10 進数にする

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::dec {#dec}

```cpp
std::ios_base& dec(std::ios_base& str);
```

ストリームの書式フラグのうち、基数のグループ（`basefield`）を 10 進数にします。出力だけでなく、入力にも効くので、`std::cin >> std::dec >> n` は、`0x` で始まる入力も 10 進数として読もうとします（`0` で止まります）。

基数を指定せず、入力から自動で判定させたい場合は、`std::cin >> std::setbase(0) >> n` とします。`0x` なら 16 進数、`0` で始まれば 8 進数、そうでなければ 10 進数として読みます。

`hex` を使う関数の後始末として、`dec` を呼ぶのが定番です。ストリームの状態を一時的に変えて、元に戻す処理は、保存と復元（`std::ios::fmtflags f = os.flags(); ... os.flags(f);`）でも書けます。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\n';   // ff
  std::cout << 255 << '\n';               // hex が残っているので ff
  std::cout << std::dec << 255 << '\n';   // 255 に戻る

  int n = 0;
  std::cin >> std::dec >> n;
  std::cout << "入力なし: " << std::cin.fail() << '\n';
}
```

```text title="実行結果"
ff
ff
255
入力なし: 1
```

## ゲームでの使いどころ

16 進数や 8 進数で出したあとに、元の表示へ戻すときに使います。ログ関数やデバッグ出力の関数の最後に `std::dec` を流して、呼び出し側の出力に影響しないようにします。

## よくあるミス

??? failure "`hex` の後に戻さず、数値の表示が崩れる"
    戻す操作を忘れずに入れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`oct`](oct.md) | 8 進数にする |
| [`setbase`](setbase.md) | 基数を数値で指定する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数を 10 進数にする
    - [x] 既定の状態に戻す
    - [x] 入力にも効く

## 関連ページ

- [cpprefjp: std::dec](https://cpprefjp.github.io/reference/ios/dec.html)
- [cppreference: std::dec](https://en.cppreference.com/w/cpp/io/manip/dec)
