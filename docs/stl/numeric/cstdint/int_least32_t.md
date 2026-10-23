---
title: std::int_least32_t
summary: "32 ビット以上で、最も小さい符号付き整数。"
order: 900
tags:
  - 数値
---

# std::int_least32_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

固定幅の `std::int32_t` は、環境によっては定義されないことがあります。そこで標準は、「幅は決まらないが、条件を満たす型は必ず用意する」という別の型の組を用意しています。

`std::int_least32_t` は、<strong>少なくとも 32 ビットを持つ、最も小さい符号つき整数</strong>を表します。

!!! tip "ポイント"
    - 符号つき整数型。大きさは環境で変わりうる（32 ビット以上）
    - `<cstdint>` で定義され、環境が何であっても必ず用意される
    - `std::int32_t` と違って、幅が揃うことは保証されない。ファイルや通信のデータ形式には使わない
    - 普通のゲームでは、`int` か `std::int32_t` で足りる

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::int_least32_t {#int_least32_t}

<span class="ver ver-11">C++11</span>

```cpp
using int_least32_t = /* 符号つき整数型 */;
```

`std::int_least32_t` は型の別名で、実体は環境の整数型です。条件は「幅が少なくとも 32 ビット」です。範囲は、少なくとも −2,147,483,648 〜 2,147,483,647 です。

「最小」の基準も環境に任されています。ほとんどの環境では、`int_least32_t` は `int32_t` と同じ幅ですが、32ビットちょうどの型を持たない珍しい環境（バイトが 8 ビットでない DSP など）でも、この型は必ず用意されます。

そのため、移植性が最優先で、メモリも節約したい場合に向きます。ただし、PC・コンソール・スマホが対象のゲームでは、`intN_t`（ちょうど N ビット）が必ず定義されるので、`least` 系を使う理由はほぼありません。

ファイルや通信に使ってはいけません。環境ごとに大きさが違うと、同じファイルが別の環境で読めなくなるからです。データ形式には、幅が固定の `std::int32_t` を使います。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  // 大きさは環境で違うが、条件（少なくとも 32 ビット）は必ず満たす
  std::println("{}", sizeof(std::int_least32_t) * 8 >= 32);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

ゲームで使う場面はほとんどありません。ループの回数のように、桁の小さい値を速く扱いたいときに `int_fast` 系を使う例が、移植性の高いライブラリのコードで見られます。

```cpp
for (std::int_least32_t i = 0; i < count; ++i) {
  // 範囲が小さいと分かっていて、速さだけが欲しいカウンター
}
```

迷ったら `int` を使います。

## よくあるミス

??? failure "ファイルに書き出して、別の環境で読めなくなる"
    固定幅の `std::int32_t` を使います。

??? failure "`sizeof` が 4 バイトだと決めつける"
    「少なくとも」の幅です。環境によって大きくなりえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::int32_t`](int32_t.md) | ちょうどの幅 |
| [`<cstdint>`](../cstdint.md) | 整数型の一覧 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号つき整数で、幅は少なくとも 32 ビット
    - [x] 要件を満たす最も小さい型
    - [x] データ形式には使わない。普通は `int` で足りる

## 関連ページ

- [cpprefjp: std::int_least32_t](https://cpprefjp.github.io/reference/cstdint/int_least32_t.html)
- [cppreference: std::int_least32_t](https://en.cppreference.com/w/cpp/types/integer)
