---
title: std::setiosflags
summary: "書式フラグを、まとめて設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setiosflags

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`showpos | uppercase` のように、複数のフラグを 1 回で設定できます。`resetiosflags` で解除します。

!!! tip "ポイント"
    - フラグは `|` でつなぐ。
    - 追加であり、他のフラグは変わらない。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::setiosflags {#setiosflags}

```cpp
/* 実装定義 */ setiosflags(std::ios_base::fmtflags mask);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mask` | fmtflags | 設定するフラグ |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setiosflags(std::ios::showpos) << 5 << '\n';
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

??? failure "`basefield` のフラグを足す"
    `ios::hex` を足しても `dec` が残って効かないことがあります。`std::hex` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`resetiosflags`](resetiosflags.md) | フラグを解除 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式フラグを、まとめて設定する
    - [x] フラグは `|` でつなぐ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::setiosflags](https://cpprefjp.github.io/reference/ios/setiosflags.html)
- [cppreference: std::setiosflags](https://en.cppreference.com/w/cpp/io/manip/setiosflags)
