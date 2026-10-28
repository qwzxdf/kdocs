---
title: std::uniform_real_distribution
summary: "範囲内の小数を、同じ確率で出す（上限は含まない）。"
order: 11
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::uniform_real_distribution

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

ランダムな角度、ランダムな位置、「0 から 1 の間の確率」。ゲームの乱数は整数だけではありません。`rand()` で小数を作ろうとして `rand() / RAND_MAX` と書くと、偏りが出ることもあります。`std::uniform_real_distribution` は、指定した範囲の小数をどの値も同じ確率で返してくれる部品です。乱数エンジンと組み合わせて使います。

!!! tip "ポイント"
    - 範囲は `[a, b)`。下限は含み、上限は含まない。
    - 確率の判定（成功か失敗か）だけなら、`bernoulli_distribution` のほうが意図が伝わる。
    - エンジン（`mt19937`）は 1 つ作って使い回す。分布は軽いので、使う場所で作ってもよい。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) の乱数エンジンの使い方を先に読んでください。分布は、エンジンが出した生の乱数を必要な範囲と形に変える部品です。

## 関数の詳しい説明

### std::uniform_real_distribution {#uniform_real}

```cpp
template <class RealType = double>
class uniform_real_distribution {
 public:
  explicit uniform_real_distribution(RealType a, RealType b = 1.0);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 浮動小数点 | 最小値（含む） |
| `b` | 浮動小数点 | 最大値（**含まない**） |

`a` は下限で、この値は出る可能性があります。`b` は上限で、この値は出ません。`uniform_real_distribution<float> angle(0.0f, 360.0f)` なら、0 度以上 360 度未満です。360 度が出ないのは、0 度と同じ向きだからです。

`b` を省略すると 1.0 になります。`uniform_real_distribution<float> p;` は 0 以上 1 未満の値を返します。`a < b` でなければなりません。`a == b` や `a > b` は未定義動作です。

型の引数は、`float` か `double` を指定します。ゲームの座標が `float` なら、`float` にそろえます。`double` で作って `float` に代入しても動きますが、無駄な変換になります。

分布オブジェクトは `operator()` にエンジンを渡して呼びます。`angle(rng)` のように書きます。

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(7);
  std::uniform_real_distribution<float> angle(0.0f, 360.0f);
  float a = angle(rng);
  std::println("0 以上 360 未満？ {}", a >= 0.0f && a < 360.0f);
}
```

```text title="実行結果"
0 以上 360 未満？ true
```

### operator() {#op_call}

```cpp
template <class Generator>
result_type operator()(Generator& g);
```

- 計算量: 定数（アルゴリズムによる）

乱数エンジン `g` から乱数を取って、この分布に従う値を 1 つ返します。

### reset {#reset}

```cpp
void reset();
```

- 計算量: 定数

分布の内部状態を初期化します。直前の呼び出しで持ち越している値（正規分布の「余り」の値）を捨てます。

### param {#param}

```cpp
param_type param() const;
void param(const param_type& p);
```

- 計算量: 定数

分布のパラメータ一式を取り出す、または設定します。

### min {#min}

```cpp
result_type min() const;
```

- 計算量: 定数

この分布が返しうる最小値。

### max {#max}

```cpp
result_type max() const;
```

- 計算量: 定数

この分布が返しうる最大値。

## ゲームでの使いどころ

パーティクルの初速や方向をばらつかせるのに使います。`uniform_real_distribution<float> speed(2.0f, 5.0f)` で速さを `angle(0.0f, 6.2832f)` で向きを決めて、毎フレーム数十個のパーティクルを生み出します。

敵の出現位置をランダムにするときも使います。画面の幅 `W` と高さ `H` の範囲で `x` と `y` を作れば、画面内のランダムな位置が決まります。

確率の判定にも使えます。`dist(rng) < 0.3f` と書くと 30% の確率です。ただしこの用途は、`bernoulli_distribution` を使うほうが読みやすくなります。

## よくあるミス

??? failure "上限が含まれると思う"
    `[a, b)` なので、上限の `b` は出ません。反対に、整数の `uniform_int_distribution` は `[a, b]` で上限を含みます。同じ名前でも仕様が違うので、混同しやすい点です。

??? failure "毎回エンジンを作り直す"
    関数の中で `std::mt19937 rng(std::random_device{}());` を毎回作ると、遅く、しかも似た乱数が出ることがあります。エンジンはクラスのメンバーなどに 1 つだけ持ち、使い回します。

??? failure "`rand() / RAND_MAX` で小数を作る"
    `rand()` の品質は低く、`RAND_MAX` が小さい環境（Windows では 32767）では、小数の細かさも足りません。標準の分布を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_int_distribution`](uniform_int_distribution.md) | 整数版。上限を含む |
| [`normal_distribution`](normal_distribution.md) | 正規分布。真ん中に集まりやすい値が欲しいとき |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 成功か失敗かの判定 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `[a, b)` で、上限は出ない。
    - [x] 確率の判定は `bernoulli_distribution` が読みやすい。
    - [x] エンジンは使い回す。

## 関連ページ

- [cpprefjp: std::uniform_real_distribution](https://cpprefjp.github.io/reference/random/uniform_real_distribution.html)
- [cppreference: std::uniform_real_distribution](https://en.cppreference.com/w/cpp/numeric/random/uniform_real_distribution)
