---
title: std::unreachable
summary: "「ここには絶対に来ない」とコンパイラに伝える。"
order: 7
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::unreachable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <utility>`
</div>

`switch` のすべての場合を列挙したのに、コンパイラは「その他の場合」もあるかもしれないと考え、警告を出したり、不要な分岐のコードを作ったりします。`std::unreachable()` は、<strong>「ここには決して来ない」とコンパイラに約束する</strong>関数です。

!!! tip "ポイント"
    - `std::unreachable()` を呼ぶと、その経路は到達しないと仮定される
    - 実際に呼ばれると未定義動作
    - `switch` の `default` や、`if` の最後の `else` に書く
    - C++23 で追加

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unreachable {#unreachable}

<span class="ver ver-23">C++23</span>

```cpp
[[noreturn]] void unreachable();
```

コンパイラは、この関数に到達する経路は存在しない、と仮定して最適化します。そのため、不要な比較や分岐が省かれ、コードが速く小さくなることがあります。

約束を破って実際に呼ばれると、未定義動作です。Debug ビルドでは、`assert(false)` と書くほうが安全です。約束が確実に守られる場所（列挙子をすべて網羅した `switch` の `default` など）にだけ書きます。

## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

enum class Color { kRed, kGreen };

int ToValue(Color c) {
  switch (c) {
    case Color::kRed:   return 1;
    case Color::kGreen: return 2;
  }
  std::unreachable();   // 列挙子はすべて上で網羅した
}

int main() {
  std::println("kGreen = {}", ToValue(Color::kGreen));
}
```

```text title="実行結果"
kGreen = 2
```

## ゲームでの使いどころ

列挙型の `switch` の後ろに書いて、コンパイラの警告「戻り値がない」を消しつつ、最適化に役立てます。

## よくあるミス

??? failure "到達しうる経路に書いて、未定義動作になる"
    確実に到達しない所だけに書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abort`](../numeric/cstdlib/abort.md) | 確実に止めるなら |
| [`byte`](byte.md) | バイトを表す型 |

## コンパイラ対応

C++23 から使えます。GCC 12 以降、Clang 15 以降、Visual Studio 2022 17.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::unreachable()` はここに来ないとの約束
    - [x] 来ると未定義動作
    - [x] 網羅した `switch` の後ろに書く

## 関連ページ

- [cpprefjp: std::unreachable](https://cpprefjp.github.io/reference/utility/unreachable.html)
- [cppreference: std::unreachable](https://en.cppreference.com/w/cpp/utility/unreachable)
