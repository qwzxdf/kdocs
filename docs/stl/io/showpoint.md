---
title: std::showpoint
summary: "小数の出力に、小数点と末尾の 0 を必ず付ける。"
order: 900
tags:
  - 入出力・文字列
---

# std::showpoint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::cout << 1.0` は、既定では `1` と出力されます。`showpoint` を設定すると、`1.00000` のように、小数点と桁数ぶんの 0 が付きます。

!!! tip "ポイント"
    - 有効桁数（既定は 6）ぶんまで 0 が付く。
    - `noshowpoint` で解除する。
    - 桁数は `setprecision` で変える。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showpoint {#showpoint}

```cpp
std::ios_base& showpoint(std::ios_base& str);
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
  std::cout << std::showpoint << 1.0 << '\n';
}
```

```text title="実行結果"
1.00000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`fixed` と取り違える"
    `showpoint` は有効桁数ぶんの桁、`fixed` は小数点以下の桁数が基準です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 小数点以下の桁数で固定 |
| [`setprecision`](setprecision.md) | 桁数を設定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数の出力に、小数点と末尾の 0 を必ず付ける
    - [x] 有効桁数（既定は 6）ぶんまで 0 が付く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::showpoint](https://cpprefjp.github.io/reference/ios/showpoint.html)
- [cppreference: std::showpoint](https://en.cppreference.com/w/cpp/io/manip/showpoint)
