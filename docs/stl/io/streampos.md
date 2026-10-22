---
title: std::streampos
summary: "ストリーム上の位置を表す型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streampos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`tellg()` が返し、`seekg(pos)` に渡す型です。`fpos<mbstate_t>` の別名で、マルチバイト文字の状態も含められます。整数と見なして計算するのは移植性がありません。

!!! tip "ポイント"
    - 入出力の位置・大きさを表す型。
    - `<ios>` で定義される。
    - ふつうは `auto` で受ける。

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streampos {#streampos}

```cpp
using streampos = fpos<mbstate_t>;
```

- 戻り値: なし（型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <fstream>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("abc");
  in.get();
  std::streampos pos = in.tellg();
  std::println("{}", static_cast<long long>(pos));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの途中に戻る | `auto pos = in.tellg(); ... in.seekg(pos);` |

## よくあるミス

??? failure "`int` で受ける"
    大きなファイルで桁あふれします。`auto` か、この型で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ios_base`](ios_base.md) | ストリームの土台 |
| [`ifstream`](ifstream.md) | ファイル入力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリーム上の位置を表す型
    - [x] tellg / seekg で使う
    - [x] auto で受けるのが安全

## 関連ページ

- [cpprefjp: std::streampos](https://cpprefjp.github.io/reference/ios/streampos.html)
- [cppreference: std::streampos](https://en.cppreference.com/w/cpp/io/streampos)
