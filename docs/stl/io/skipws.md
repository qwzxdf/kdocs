---
title: std::skipws
summary: "入力で、先頭の空白を読み飛ばす（既定でオン）。"
order: 900
tags:
  - 入出力・文字列
---

# std::skipws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <sstream>`
</div>

`cin >> x` が、先頭の空白や改行を飛ばしてくれるのは、`skipws` が既定でオンだからです。`noskipws` で解除すると、空白も 1 文字として読めます。

!!! tip "ポイント"
    - 既定でオン。
    - `std::noskipws` で空白も読む。
    - 文字単位で読みたいときに `noskipws` を使う。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::skipws {#skipws}

```cpp
std::ios_base& skipws(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | ios_base& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <sstream>

int main() {
  std::istringstream in(" x");
  in >> std::noskipws;
  char c;
  in >> c;
  std::println("{}", c == ' ');
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`noskipws` を戻し忘れる"
    設定が残り、後続の整数の入力が失敗します。`skipws` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ws`](ws.md) | 空白を読み飛ばす |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力で、先頭の空白を読み飛ばす（既定でオン）
    - [x] 既定でオン
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::skipws](https://cpprefjp.github.io/reference/ios/skipws.html)
- [cppreference: std::skipws](https://en.cppreference.com/w/cpp/io/manip/skipws)
