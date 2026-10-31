---
title: std::seed_seq
summary: "複数の値から、エンジンの種を作る。"
order: 3
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::seed_seq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`mt19937` の状態は 624 個の 32 ビット整数ですが、種として 1 つの整数を渡すと、約 43 億通りの列しか作れません。もっと多様にしたいとき、複数の値を混ぜて、必要なだけの種を作るのが `std::seed_seq` です。`random_device` から取った数個の値を渡すのが、定番の使い方です。

!!! tip "ポイント"
    - 複数の整数を渡して作り、エンジンの種に渡す（`std::mt19937 e(seq);`）
    - 同じ入力からは、必ず同じ種が作られる。再現性がある
    - 入力の値が少なくても、状態全体を埋めるように混ぜる
    - `generate` で、任意の長さの種の列を取り出せる

!!! info "このページを読む前に"
    [`std::random_device`](random_device.md) と [`std::mt19937`](mt19937.md) を先に読んでください。

## 関数の詳しい説明

### std::seed_seq {#seed_seq}

<span class="ver ver-11">C++11</span>

```cpp
class seed_seq {
 public:
  seed_seq(std::initializer_list<std::uint_least32_t> values);
  template <class InputIt> seed_seq(InputIt begin, InputIt end);

  std::size_t size() const noexcept;
  template <class OutputIt> void param(OutputIt dest) const;
  template <class RandomIt> void generate(RandomIt begin, RandomIt end);
};
```

### コンストラクター {#ctor}

`seed_seq{1, 2, 3}` や、イテレータの範囲で作ります。渡された値は、内部に覚えられます。

### generate {#generate}

`[begin, end)` に、32 ビットの値を書き込みます。渡された値が 3 個でも、範囲が 624 個でも、全部が埋まります。内部では、入力の値を混ぜ合わせて、範囲の大きさに引き伸ばしています。同じ入力からは、同じ列が作られます。

エンジンのコンストラクターや `seed` に `seed_seq` を渡すと、エンジンが内部で `generate` を呼んで、状態を初期化します。

### size と param {#size}

`size()` は、渡された値の個数です。`param(dest)` で、その値を取り出せます。保存して、あとで同じ `seed_seq` を作り直すのに使います。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>
#include <vector>

int main() {
  std::seed_seq seq{1, 2, 3};
  std::println("もとの値の数: {}", seq.size());

  // 同じ入力なら、同じ種が作られる
  std::seed_seq a{1, 2, 3};
  std::seed_seq b{1, 2, 3};
  std::vector<std::uint32_t> va(4), vb(4);
  a.generate(va.begin(), va.end());
  b.generate(vb.begin(), vb.end());
  std::println("同じ入力なら同じ列: {}", va == vb);

  // エンジンの種に使う
  std::seed_seq s1{1, 2, 3};
  std::seed_seq s2{1, 2, 3};
  std::mt19937 e1(s1);
  std::mt19937 e2(s2);
  std::println("エンジンも同じ列: {}", e1() == e2());
}
```

```text title="実行結果"
もとの値の数: 3
同じ入力なら同じ列: true
エンジンも同じ列: true
```

## ゲームでの使いどころ

毎回違う乱数を使いたいとき、`random_device` から数個の値を取って、`seed_seq` に渡します。

```cpp
std::random_device rd;
std::seed_seq seq{rd(), rd(), rd(), rd()};
std::mt19937 rng(seq);
```

リプレイを再現したいときは、`seed_seq` に渡した値を保存しておきます。

## よくあるミス

??? failure "seed_seq を使い回す"
    エンジンの種に使うと、内部の状態が進む実装があります。2 つのエンジンの種に同じ `seed_seq` を使うなら、同じ値から 2 つ作ります。

??? failure "random_device の値を 1 つだけ渡す"
    32 ビットぶんの多様性しかありません。複数回呼んで渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`random_device`](random_device.md) | 種のもとになる、予測しにくい値 |
| [`mt19937`](mt19937.md) | 種を受け取るエンジン |
| [`std::chrono::steady_clock`](../chrono/steady_clock.md) | 時刻を種に使う（予測しやすい） |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::seed_seq](https://cpprefjp.github.io/reference/random/seed_seq.html)
- [cppreference: std::seed_seq](https://en.cppreference.com/w/cpp/numeric/random/seed_seq)
