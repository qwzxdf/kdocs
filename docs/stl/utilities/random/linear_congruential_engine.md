---
title: std::linear_congruential_engine
summary: "線形合同法の乱数エンジンのテンプレート（`minstd_rand` の元）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::linear_congruential_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

乱数を作るいちばん単純な方法が、線形合同法です。前の値 `x` から、`x = (a * x + c) mod m` と計算して、次の値にします。かけ算と足し算と余りだけなので速く、状態は整数 1 つだけです。`std::linear_congruential_engine` は、この式の `a`、`c`、`m` をテンプレート引数にしたエンジンで、`std::minstd_rand0` と `std::minstd_rand` は、決まった数を当てはめた別名です。

!!! tip "ポイント"
    - `x_next = (a * x + c) mod m` を繰り返す。状態は 1 つの整数
    - `std::minstd_rand0`（a=16807）と `std::minstd_rand`（a=48271）は、c=0、m=2^31-1 の定番の組み合わせ
    - 品質は `mt19937` に劣る。低いビットの偏りや、短い周期に注意する
    - 自分でパラメータを選ぶなら、定評のある組み合わせから外れない

!!! info "このページを読む前に"
    [`std::minstd_rand`](minstd_rand.md) と [`std::mt19937`](mt19937.md) を先に読んでください。

## 関数の詳しい説明

### std::linear_congruential_engine {#linear_congruential_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class UIntType, UIntType a, UIntType c, UIntType m>
class linear_congruential_engine;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `UIntType` | 状態と出力の整数型。`m` が収まる大きさ |
| `a` | 乗数 |
| `c` | 増分 |
| `m` | 法（余りを取る数）。0 は 2^32 などの型の範囲を表す |

### パラメータの意味 {#params}

`a` は、前の値にかける数です。大きすぎても小さすぎてもよくなく、`m` との組み合わせで周期が決まります。`m` は、値の範囲で、出力は 0 から `m - 1` です。素数（2^31-1 は素数）にすると、周期を最大にしやすくなります。

`c` は、足す数です。`c` が 0 の場合を乗算合同法と呼び、`minstd_rand` 系がこれに当たります。`c` が 0 のとき、状態が 0 になると、以降ずっと 0 になるので、エンジンは、種が 0 なら 1 に読み替えます。そのため、`c` が 0 のとき `min()` は 1 になり、`c` が 0 でなければ `min()` は 0 です。

### 種と出力 {#seed}

既定の種は 1 です。`e.seed(n)` や、コンストラクターで指定します。最初の `operator()` は、種を `x` として、1 回計算した後の値を返します。種が 1 の `minstd_rand0` の最初の出力は 16807（`a * 1`）です。

### 品質の限界 {#quality}

線形合同法の乱数は、連続した出力を並べて、多次元の点にすると、規則正しい格子状に並ぶ傾向があります。`m` が 2 のべき乗のとき、下位のビットの周期が短く、偶数と奇数が交互に出るような偏りもあります。ゲームの見た目に影響する乱数（ダメージ、ドロップ）では、`mt19937` のほうが安心です。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>
#include <random>

int main() {
  // 小さなパラメータで、計算を目で追う: x = (5 * x + 3) mod 16
  using Tiny = std::linear_congruential_engine<std::uint_fast32_t, 5, 3, 16>;
  Tiny tiny;  // 種は 1
  const auto x1 = tiny();
  const auto x2 = tiny();
  const auto x3 = tiny();
  std::println("{} {} {}", x1, x2, x3);
  std::println("範囲: {} 〜 {}", Tiny::min(), Tiny::max());

  // c = 0 なら min() は 1
  using Mul = std::linear_congruential_engine<std::uint_fast32_t, 16807, 0, 2147483647>;
  std::println("c=0 の min(): {}", Mul::min());
  Mul e;
  std::println("最初の出力: {}", e());
}
```

```text title="実行結果"
8 11 10
範囲: 0 〜 15
c=0 の min(): 1
最初の出力: 16807
```

種 1 から、`(5 * 1 + 3) mod 16 = 8`、`(5 * 8 + 3) mod 16 = 11`、`(5 * 11 + 3) mod 16 = 10` と進んでいます。

## ゲームでの使いどころ

自分で組み立てることは、ほとんどありません。軽くて、再現性が必要な場面（リプレイの検証用の簡易な乱数など）に、`minstd_rand` を使います。

## よくあるミス

??? failure "m が 2 のべき乗で、下位ビットを使う"
    下位のビットの周期が短くなります。`% 2` で偶数と奇数を決めるような使い方は避けます。

??? failure "種を 0 にして、c = 0 で止まると思う"
    c = 0 のとき、種の 0 は 1 に読み替えられます。止まりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`minstd_rand0`](minstd_rand0.md) | a=16807 の定番の組み合わせ |
| [`minstd_rand`](minstd_rand.md) | a=48271 の改良版 |
| [`mersenne_twister_engine`](mersenne_twister_engine.md) | 品質のよい別方式 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::linear_congruential_engine](https://cpprefjp.github.io/reference/random/linear_congruential_engine.html)
- [cppreference: std::linear_congruential_engine](https://en.cppreference.com/w/cpp/numeric/random/linear_congruential_engine)
