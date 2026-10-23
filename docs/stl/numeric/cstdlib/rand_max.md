---
title: RAND_MAX
summary: "rand() が返す最大値のマクロ。"
order: 900
tags:
  - 数値
---

# RAND_MAX

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`std::rand` が返す値の範囲は 0 以上 `RAND_MAX` 以下です。0〜1 の乱数が欲しいとき、`rand()` を何で割ればよいかを教えてくれるのが `RAND_MAX` です。

!!! tip "ポイント"
    - `RAND_MAX` は `rand()` が返す最大値
    - 最低でも 32767。MSVC では 32767 ちょうど
    - 0〜1 の乱数は `rand() / static_cast<double>(RAND_MAX)`
    - 値が小さいので、細かい乱数には不向き。`<random>` を使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### RAND_MAX {#rand_max}

```cpp
#define RAND_MAX /* 32767 以上 */
```

`RAND_MAX` は `std::rand` の戻り値の上限で、少なくとも 32767 です。MSVC は 32767（15 ビット）、GCC（glibc）は 2147483647（31 ビット）で、環境によって大きく違います。

0 以上 1 以下の小数にするには、`static_cast<double>(std::rand()) / RAND_MAX` と書きます。整数同士で割ると 0 になるので、必ず `double` にキャストしてから割ります。

範囲が 15 ビットしかない環境では、1 万より細かい刻みの乱数を作れません。また `rand() % n` は偏りが出ます。品質と範囲の両方が必要なゲームでは、`<random>` の `std::mt19937` を使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("RAND_MAX は 32767 以上: {}", RAND_MAX >= 32767);
  std::srand(1);
  const double ratio = static_cast<double>(std::rand()) / RAND_MAX;
  std::println("0〜1 の範囲に収まる: {}", ratio >= 0.0 && ratio <= 1.0);
}
```

```text title="実行結果"
RAND_MAX は 32767 以上: true
0〜1 の範囲に収まる: true
```

## ゲームでの使いどころ

`rand` の値を 0〜1 に直すときに使います。

```cpp
const float chance = static_cast<float>(std::rand()) / RAND_MAX;
if (chance < 0.3f) { /* 30% の確率 */ }
```

品質と細かさが要るなら `std::uniform_real_distribution<float>(0.0f, 1.0f)` を使います。

## よくあるミス

??? failure "整数どうしで割って、常に 0 になる"
    `double` にキャストしてから割ります。

??? failure "環境の違いを知らず、MSVC で粗い乱数になる"
    `<random>` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rand`](rand.md) | 乱数を返す |
| [`srand`](srand.md) | 種を決める |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `RAND_MAX` は `rand()` の最大値
    - [x] MSVC は 32767、glibc は 2147483647
    - [x] 0〜1 の乱数にするには `double` にキャストして割る

## 関連ページ

- [cpprefjp: RAND_MAX](https://cpprefjp.github.io/reference/cstdlib/RAND_MAX.html)
- [cppreference: RAND_MAX](https://en.cppreference.com/w/cpp/c/RAND_MAX)
