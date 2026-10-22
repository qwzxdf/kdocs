---
title: std::streamoff
summary: "ストリーム上の位置の差（オフセット）を表す符号付き整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streamoff

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`seekg(off, dir)` の `off` のように、ストリームの位置を相対的に動かす量を表す型です。

!!! tip "ポイント"
    - 入出力の位置・大きさを表す型。
    - `<ios>` で定義される。
    - ふつうは `auto` で受ける。

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streamoff {#streamoff}

```cpp
using streamoff = /* 実装定義の整数型 */;
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
  std::streamoff off = 1;
  in.seekg(off, std::ios::cur);
  std::println("{}", static_cast<char>(in.get()));
}
```

```text title="実行結果"
c
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
    - [x] ストリーム上の位置の差（オフセット）を表す符号付き整数型
    - [x] tellg / seekg で使う
    - [x] auto で受けるのが安全

## 関連ページ

- [cpprefjp: std::streamoff](https://cpprefjp.github.io/reference/ios/streamoff.html)
- [cppreference: std::streamoff](https://en.cppreference.com/w/cpp/io/streamoff)
