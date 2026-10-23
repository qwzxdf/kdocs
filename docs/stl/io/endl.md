---
title: std::endl
summary: "改行を出して、バッファを書き出す（flush する）。"
order: 74
tags:
  - 入出力・文字列
---

# std::endl

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ostream>`
</div>

`std::endl` は、**改行を出して、同時に出力のバッファを書き出す（flush する）**マニピュレーターです。毎回 `flush` するので、大量に出すと**遅く**なります。ふつうは `"\n"` で足ります。デバッグ中にすぐ画面へ出したいときだけ使います。

!!! tip "ポイント"
    - **ふつうは `"\n"`**。`endl` は毎回 `flush` するので遅い。
    - `std::endl` ＝ `"\n"` ＋ `std::flush`。
    - 新しいコードは `std::println`（改行つき）。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::endl {#endl}

```cpp
std::ostream& endl(std::ostream& os);
```

- 改行して、**flush**（たまった出力をすぐ書き出す）します。flush は遅いので、ループの中で毎回使うと大量の出力が遅くなります

!!! note "実際は"
    普段は `'\n'` で改行し、すぐ出したいときだけ `std::flush` を使います。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << "a" << std::endl;   // 改行 + flush
  std::cout << "b" << '\n';          // 改行だけ
}
```

```text title="実行結果"
a
b
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クラッシュ直前のログを確実に出す | `std::cout << msg << std::endl;` |

## よくあるミス

??? failure "ループの中で endl を使う"
    1 行ごとに `flush` が走り、出力が数倍遅くなります。`"\n"` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::flush`](flush.md) | 改行なしでバッファを書き出す |
| [`std::println`](../utilities/print.md) | 改行つき出力 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 改行 + flush
    - [x] 普通は `"\n"`
    - [x] 大量出力では使わない

## 関連ページ

- [cpprefjp: std::endl](https://cpprefjp.github.io/reference/ostream/endl.html)
- [cppreference: std::endl](https://en.cppreference.com/w/cpp/io/manip/endl)
