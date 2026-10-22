---
title: std::ws
summary: "入力で、空白（スペース・改行・タブ）を読み飛ばす。"
order: 900
tags:
  - 入出力・文字列
---

# std::ws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <sstream>`
</div>

`getline` の前後などで、残っている空白や改行を捨てたいときに、`in >> std::ws` と書きます。

!!! tip "ポイント"
    - 連続する空白をすべて飛ばす。
    - `skipws` が有効でも、`getline` では飛ばされないので使う。
    - 文字は 1 つも消費しない（空白だけ）。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::ws {#ws}

```cpp
template <class CharT, class Traits>
std::basic_istream<CharT, Traits>& ws(std::basic_istream<CharT, Traits>& is);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `is` | istream& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <sstream>

int main() {
  std::istringstream in("   x");
  in >> std::ws;
  char c;
  in >> c;
  std::println("{}", c);
}
```

```text title="実行結果"
x
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "改行が残って `getline` が空を返す"
    `cin >> n` のあとの改行が残ります。`cin >> std::ws` か `ignore` で捨てます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`skipws`](skipws.md) | 既定の空白の読み飛ばし |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力で、空白（スペース・改行・タブ）を読み飛ばす
    - [x] 連続する空白をすべて飛ばす
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ws](https://cpprefjp.github.io/reference/ios/ws.html)
- [cppreference: std::ws](https://en.cppreference.com/w/cpp/io/manip/ws)
