---
title: std::resetiosflags
summary: "書式フラグを、まとめて解除する。"
order: 900
tags:
  - 入出力・文字列
---

# std::resetiosflags

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`setiosflags` で設定したフラグを指定して解除します。

!!! tip "ポイント"
    - フラグは `|` でつなぐ。
    - 指定したフラグだけが解除される。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::resetiosflags {#resetiosflags}

```cpp
/* 実装定義 */ resetiosflags(std::ios_base::fmtflags mask);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mask` | fmtflags | 解除するフラグ |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::showpos << std::resetiosflags(std::ios::showpos) << 5 << '\n';
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "設定していないフラグを解除する"
    何も起こりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setiosflags`](setiosflags.md) | フラグを設定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式フラグをまとめて解除する
    - [x] フラグは `|` でつなぐ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::resetiosflags](https://cpprefjp.github.io/reference/ios/resetiosflags.html)
- [cppreference: std::resetiosflags](https://en.cppreference.com/w/cpp/io/manip/resetiosflags)
