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

ファイルの権限（`0755` など）の表示に使われる、8 進数で出力します。

!!! tip "ポイント"
    - `dec` で 10 進数に戻す。
    - `showbase` を付けると先頭に `0` が付く。
    - 入力にも効く。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::oct {#oct}

```cpp
std::ios_base& oct(std::ios_base& str);
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
  std::cout << std::oct << 8 << '\n';
}
```

```text title="実行結果"
10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "戻し忘れる"
    `dec` で戻さないと、後続の整数も 8 進数で出力されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数 |
| [`dec`](dec.md) | 10 進数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数を 8 進数で出力・入力する
    - [x] `dec` で 10 進数に戻す
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::oct](https://cpprefjp.github.io/reference/ios/oct.html)
- [cppreference: std::oct](https://en.cppreference.com/w/cpp/io/manip/oct)
