---
title: std::giga
summary: "SI 接頭辞「giga」（10 億倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::giga

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

長さ・時間・容量などの単位に「giga」をつけたいとき、`1/1` のような分数を自分で書くのはミスのもとです。`std::giga` は、SI 接頭辞 giga（10 億倍）をそのまま表す `ratio` の別名です。`std::chrono::duration` の単位の指定にも使います。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000000, 1>`。
    - `::num` と `::den` で分子と分母を取り出す。
    - `duration<double, std::milli>` のように単位として使う。

!!! info "このページを読む前に"
    [`std::ratio`](../ratio.md) を先に読んでください。

## 関数の詳しい説明

### std::giga {#giga}

```cpp
using giga = ratio<1000000000, 1>;  // 実装により intmax_t に収まらない場合は定義されない（yotta など）
```

- 戻り値: 10 億倍を表す `ratio`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  std::println("{} {}", std::giga::num, std::giga::den);
}
```

```text title="実行結果"
1000000000 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ミリ秒の duration を作る | `std::chrono::duration<int, std::milli>` |

## よくあるミス

??? failure "接頭辞の向きを取り違える"
    `giga` は 10 億倍です。「小さい単位」か「大きい単位」かを、倍率で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数の型 |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間の長さ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SI 接頭辞 giga = 10 億倍
    - [x] ratio の別名
    - [x] duration の単位に使う

## 関連ページ

- [cpprefjp: std::giga](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::giga](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
