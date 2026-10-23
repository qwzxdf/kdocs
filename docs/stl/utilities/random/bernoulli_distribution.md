---
title: std::bernoulli_distribution
summary: "確率 p で true、そうでなければ false を出す。"
order: 12
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::bernoulli_distribution

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

「30% の確率で会心の一撃」「5% でレアドロップ」。ゲームでは、確率で成功か失敗かを決める判定が、あちこちに出てきます。`uniform_real_distribution` で 0 から 1 の値を作って `< 0.3f` と比べる書き方もありますが、何をしているのかが、少し読み取りにくくなります。`std::bernoulli_distribution` は、確率 `p` で `true`、`1 - p` で `false` を出す分布です。意図がそのまま名前に出ます。

!!! tip "ポイント"
    - `bernoulli_distribution crit(0.3);` は 30% で `true`。
    - `p` は 0.0〜1.0。範囲外は未定義。
    - 複数回の試行の合計は [`binomial_distribution`](binomial_distribution.md)。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) の乱数エンジンの使い方を先に読んでください。分布は、エンジンの出力を目的の形に変える部品です。

## 関数の詳しい説明

### std::bernoulli_distribution {#bernoulli}

```cpp
class bernoulli_distribution {
 public:
  explicit bernoulli_distribution(double p = 0.5);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `double` | true が出る確率（0.0〜1.0） |

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(3);
  std::bernoulli_distribution always(1.0);
  std::bernoulli_distribution never(0.0);
  std::println("{} {}", always(rng), never(rng));
}
```

```text title="実行結果"
true false
```

!!! note "実際は"
    「30% で会心」「5% でレアドロップ」のような判定は、`uniform_real(0,1) < 0.3f` と書くより、こちらのほうが意図がはっきりします。

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

## しくみ

`bernoulli_distribution(p)` の `p` は、`true` が出る確率で、0.0 から 1.0 の範囲で指定します。範囲外は未定義です。`p` を省略すると 0.5 です。

使い方は、他の分布と同じです。`std::bernoulli_distribution crit(0.3); bool hit = crit(rng);` と書きます。分布オブジェクトは軽く、使う場所で作っても構いません。

何回か試した合計を知りたいときは、`binomial_distribution` を使います。「10 回挑戦して何回成功するか」を一度に決められます。

## ゲームでの使いどころ

会心やクリティカルの判定が代表的です。`std::bernoulli_distribution crit(0.3);` と作り、攻撃のたびに `crit(rng)` で判定します。

レアドロップの判定にも使います。ただし、確率が低いドロップを何回も引かないと出ない、という体験を避けたいゲームでは、「天井」を設けて、一定回数で必ず出るようにします。この場合の確率は、毎回変わるので、`p` を引くたびに作り直します。

敵の行動のランダム化（待機するか攻撃するか）や、パーティクルを出すかどうかの判定にも使えます。

## よくあるミス

??? failure "確率を百分率で渡す"
    `bernoulli_distribution(30)` は、`p` が 30 で範囲外の未定義動作です。確率は 0.0 から 1.0 で渡します。30% は `0.3` です。

??? failure "毎回エンジンを作り直す"
    判定のたびに `mt19937` を作ると、遅く、乱数の質も落ちます。エンジンは 1 つ作って使い回します。

??? failure "`p` が 0 や 1 のときの扱いを忘れる"
    `p = 0.0` なら常に `false`、`p = 1.0` なら常に `true` です。これらは正しい指定ですが、確率の設定値を外部から読み込むときに、範囲外の値が混ざっていないかを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 0〜1 の値を作って比べる書き方。意図は読み取りにくい |
| [`binomial_distribution`](binomial_distribution.md) | 複数回の試行の合計 |
| [`discrete_distribution`](discrete_distribution.md) | 3 つ以上の選択肢を重みで選ぶ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 確率 `p` で `true` を返す。`p` は 0.0〜1.0。
    - [x] 会心やドロップの判定に使う。
    - [x] エンジンは使い回す。

## 関連ページ

- [cpprefjp: std::bernoulli_distribution](https://cpprefjp.github.io/reference/random/bernoulli_distribution.html)
- [cppreference: std::bernoulli_distribution](https://en.cppreference.com/w/cpp/numeric/random/bernoulli_distribution)
