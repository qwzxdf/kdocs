---
title: std::showpos
summary: "正の数の出力に、`+` を付ける。"
order: 900
tags:
  - 入出力・文字列
---

# std::showpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

ふつうは、正の数の前には何も付きません。`showpos` を設定すると、`+5` のように `+` が付きます。ダメージの増減表示（+10 / -3）などで便利です。

!!! tip "ポイント"
    - `noshowpos` で解除する。
    - 0 にも `+0` が付く。
    - 整数にも小数にも効く。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showpos {#showpos}

```cpp
std::ios_base& showpos(std::ios_base& str);
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
  std::cout << std::showpos << 5 << '\n';
}
```

```text title="実行結果"
+5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "設定が残り続ける"
    他の出力にも `+` が付き続けます。必要なら `noshowpos` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setw`](setw.md) | 幅を設定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正の数の出力に、`+` を付ける
    - [x] `noshowpos` で解除する
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::showpos](https://cpprefjp.github.io/reference/ios/showpos.html)
- [cppreference: std::showpos](https://en.cppreference.com/w/cpp/io/manip/showpos)
