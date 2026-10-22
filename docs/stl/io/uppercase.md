---
title: std::uppercase
summary: "16 進数や指数表記の英字を、大文字で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::uppercase

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`0xff` が `0XFF`、`1e5` が `1E5` になります。16 進数のダンプや、見やすさを優先した表示で使います。

!!! tip "ポイント"
    - `showbase` と組み合わせると `0XFF`。
    - `nouppercase` で解除する。
    - 指数表記の `e` も大文字になる。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::uppercase {#uppercase}

```cpp
std::ios_base& uppercase(std::ios_base& str);
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
  std::cout << std::uppercase << std::hex << std::showbase << 255 << '\n';
}
```

```text title="実行結果"
0XFF
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`showbase` を忘れる"
    `showbase` がないと、`FF` と出力されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`showbase`](showbase.md) | 接頭辞を付ける |
| [`hex`](hex.md) | 16 進数にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 16 進数や指数表記の英字を、大文字で出力する
    - [x] `showbase` と組み合わせると `0XFF`
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::uppercase](https://cpprefjp.github.io/reference/ios/uppercase.html)
- [cppreference: std::uppercase](https://en.cppreference.com/w/cpp/io/manip/uppercase)
