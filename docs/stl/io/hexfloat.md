---
title: std::hexfloat
summary: "浮動小数点数を、16 進の指数表記で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::hexfloat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

10 進数への変換で丸めが入らない、正確な表現です。浮動小数点の値を一切の誤差なしでテキストに保存したいときに使います。

!!! tip "ポイント"
    - `0x1p+0`（1.0）のような形になる。
    - 読み込みは `std::hexfloat` を設定した入力。
    - `defaultfloat` で戻す。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::hexfloat {#hexfloat}

```cpp
std::ios_base& hexfloat(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | ios_base& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::hexfloat << 1.0 << '\n';
}
```

```text title="実行結果"
0x1p+0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "人が読むために使う"
    人には読みにくい表現です。正確さが必要なときだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 固定小数点 |
| [`defaultfloat`](defaultfloat.md) | 既定に戻す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点数を 16 進の指数表記で出力する
    - [x] `0x1p+0`（1.0）のような形になる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::hexfloat](https://cpprefjp.github.io/reference/ios/hexfloat.html)
- [cppreference: std::hexfloat](https://en.cppreference.com/w/cpp/io/manip/hexfloat)
