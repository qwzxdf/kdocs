---
title: std::right
summary: "出力を、幅の中で右寄せにする（既定）。"
order: 900
tags:
  - 入出力・文字列
---

# std::right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`setw` で幅を決めたとき、文字を右に寄せて、左側を埋めます。数値の列を揃えるのに使います。

!!! tip "ポイント"
    - 既定は右寄せ。
    - `left` のあとで戻すときに使う。
    - `setw` は 1 回の出力ごとに必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::right {#right}

```cpp
std::ios_base& right(std::ios_base& str);
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
  std::cout << std::right << std::setw(5) << 42 << '\n';
}
```

```text title="実行結果"
   42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`left` のまま戻し忘れる"
    表示が左寄せのままになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`left`](left.md) | 左寄せ |
| [`setw`](setw.md) | 幅を設定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力を、幅の中で右寄せにする（既定）
    - [x] 既定は右寄せ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::right](https://cpprefjp.github.io/reference/ios/right.html)
- [cppreference: std::right](https://en.cppreference.com/w/cpp/io/manip/right)
