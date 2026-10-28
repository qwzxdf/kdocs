---
title: std::left
summary: "出力を、幅の中で左寄せにする。"
order: 900
tags:
  - 入出力・文字列
---

# std::left

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`setw` で幅を決めたとき、文字を左に寄せて、右側を埋めます。表の左揃えの列に使います。

!!! tip "ポイント"
    - `setw` は次の 1 回の出力にだけ効く。
    - `left` の設定はストリームに残る。
    - `right` で戻す。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::left {#left}

```cpp
std::ios_base& left(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | ios_base& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::left << std::setw(5) << 42 << "|\n";
}
```

```text title="実行結果"
42   |
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "`setw` が次の出力でリセットされる"
    `setw` は 1 回の出力ごとに必要です。`left` は残ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`right`](right.md) | 右寄せ |
| [`setw`](setw.md) | 幅を設定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力を幅の中で左寄せにする
    - [x] `setw` は次の 1 回の出力にだけ効く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::left](https://cpprefjp.github.io/reference/ios/left.html)
- [cppreference: std::left](https://en.cppreference.com/w/cpp/io/manip/left)
