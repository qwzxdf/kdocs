---
title: std::internal
summary: "符号や接頭辞を左に、数字を右に寄せる（間を埋める）。"
order: 900
tags:
  - 入出力・文字列
---

# std::internal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`setw` で幅を決めたとき、`-42` を `-00042` のように、符号と数字の間を埋めて表示できます。`left`・`right` は全体を寄せるのに対し、`internal` は符号と数字の間を埋めます。

!!! tip "ポイント"
    - `setfill('0')` と組み合わせて使う。
    - `left`・`right`・`internal` から 1 つを選ぶ。
    - 幅は `setw` で決める。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::internal {#internal}

```cpp
std::ios_base& internal(std::ios_base& str);
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
  std::cout << std::internal << std::setw(6) << std::setfill('0') << -42 << '\n';
}
```

```text title="実行結果"
-00042
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`setw` を忘れる"
    幅を指定しないと、埋める場所がありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`left`](left.md) | 左寄せ |
| [`right`](right.md) | 右寄せ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号や接頭辞を左に、数字を右に寄せる（間を埋める）
    - [x] `setfill('0')` と組み合わせて使う
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::internal](https://cpprefjp.github.io/reference/ios/internal.html)
- [cppreference: std::internal](https://en.cppreference.com/w/cpp/io/manip/internal)
