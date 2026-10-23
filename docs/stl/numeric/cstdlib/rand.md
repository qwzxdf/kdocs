---
title: std::rand
summary: "乱数を作る古い関数（品質が低いので使わない）。"
order: 4
group: <cstdlib> の関数
tags:
  - 数値
---

# std::rand

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

敵の出現位置をランダムにしたい、ダイスを振りたい。最も手軽な乱数は `std::rand` です。短く書けますが、品質が低く、癖があります。簡単な試作ではよくても、ゲームの本番には向きません。

!!! tip "ポイント"
    - `std::rand()` は 0 〜 `RAND_MAX` の整数を返す
    - `RAND_MAX` は環境で違う（Windows の MSVC では 32767）
    - `rand() % n` は偏りが出る。範囲が大きいほど悪化
    - 新しいコードでは `<random>` の `std::mt19937` と分布クラス

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rand {#rand}

```cpp
int rand();
```

戻り値は 0 以上 `RAND_MAX` 以下の疑似乱数です。`RAND_MAX` は最低でも 32767 で、MSVC では 32767 ちょうどです。つまり 15 ビットしかなく、1 から 100000 の乱数を作るには足りません。

`rand() % 6 + 1` でダイスを作ると、`RAND_MAX + 1` が 6 の倍数でないため、わずかに偏ります。範囲が広くなるほど偏りが大きくなります。また、環境によっては下位ビットの周期が短く、`% 2` で交互の値が出る実装もありました。

スレッドセーフでもありません。複数のスレッドから呼ぶと、結果が崩れる可能性があります。

そうした欠点がすべて解消されているのが、`<random>` の乱数エンジン（`std::mt19937`）と分布クラス（`std::uniform_int_distribution`）です。ゲームの本番ではこちらを使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::srand(1);                                      // 種を固定して再現性を持たせる
  const int a = std::rand();
  std::srand(1);
  const int b = std::rand();
  std::println("0 以上 RAND_MAX 以下: {}", a >= 0 && a <= RAND_MAX);
  std::println("同じ種なら同じ値: {}", a == b);
}
```

```text title="実行結果"
0 以上 RAND_MAX 以下: true
同じ種なら同じ値: true
```

## ゲームでの使いどころ

試作の段階で、手早くランダムな値が欲しいときに使います。本番では `<random>` に置き換えます。

```cpp
#include <random>

std::mt19937 rng(std::random_device{}());               // 乱数エンジン
std::uniform_int_distribution<int> dice(1, 6);          // 1〜6 を等確率で
const int roll = dice(rng);
```

## よくあるミス

??? failure "`rand() % n` で偏りを知らずに使う"
    `std::uniform_int_distribution` を使います。

??? failure "`srand` を呼ばず、毎回同じ並びになる"
    起動時に 1 回 `srand` を呼びます。

??? failure "複数のスレッドから呼んで結果が崩れる"
    スレッドごとに別の乱数エンジンを持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`srand`](srand.md) | 種を決める |
| [`mt19937`](../../utilities/random/mt19937.md) | 品質の高い乱数エンジン |
| [`uniform_int_distribution`](../../utilities/random/uniform_int_distribution.md) | 偏りのない整数の乱数 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rand()` は 0 〜 `RAND_MAX` の疑似乱数
    - [x] `RAND_MAX` は小さく、`% n` は偏る
    - [x] 本番では `<random>` を使う

## 関連ページ

- [cpprefjp: std::rand](https://cpprefjp.github.io/reference/cstdlib/rand.html)
- [cppreference: std::rand](https://en.cppreference.com/w/cpp/numeric/math/rand)
