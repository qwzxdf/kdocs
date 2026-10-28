---
title: std::defaultfloat
summary: "浮動小数点数の出力を、既定の形式に戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::defaultfloat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`fixed` や `scientific` を設定したあと、既定の形式（値に応じて自動で選ぶ）に戻すときに使います。

!!! tip "ポイント"
    - `fixed`・`scientific`・`hexfloat` を解除する。
    - 桁数（`setprecision`）は変わらない。
    - 設定はストリームに残る。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::defaultfloat {#defaultfloat}

```cpp
std::ios_base& defaultfloat(std::ios_base& str);
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
  std::cout << std::fixed << 1.5 << ' ' << std::defaultfloat << 1.5 << '\n';
}
```

```text title="実行結果"
1.500000 1.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "`setprecision` もリセットされると思う"
    桁数は別の設定です。戻したいなら `setprecision(6)` も指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 固定小数点 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点数の出力を既定の形式に戻す
    - [x] `fixed`・`scientific`・`hexfloat` を解除する
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::defaultfloat](https://cpprefjp.github.io/reference/ios/defaultfloat.html)
- [cppreference: std::defaultfloat](https://en.cppreference.com/w/cpp/io/manip/defaultfloat)
