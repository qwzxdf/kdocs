---
title: std::discrete_distribution
summary: "重みに比例した確率で、添字を選ぶ（ガチャ・ドロップ抽選）。"
order: 13
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::discrete_distribution

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::discrete_distribution` は、**重みのリストに比例した確率で、「何番目か」を選ぶ分布**です。ガチャの排出率、ドロップテーブル、敵の行動の抽選に使います。重みの合計が 100 でなくてもよく、比率だけが意味を持ちます。

!!! tip "ポイント"
    - 戻り値は**添字**（0 始まり）。名前や ID の配列と組み合わせて使う。
    - 重みの合計は何でもよい（`{70, 25, 5}` でも `{14, 5, 1}` でも同じ）。
    - 各確率は `probabilities()` で確かめられる。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::discrete_distribution {#discrete}

```cpp
template <class IntType = int>
class discrete_distribution {
 public:
  discrete_distribution(std::initializer_list<double> weights);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `weights` | 重みのリスト | i 番目が出る確率は「i 番目の重み ÷ 重みの合計」 |

- 戻り値: 選ばれた**添字**（0 始まり）

```cpp
#include <array>
#include <print>
#include <random>
#include <string>

int main() {
  std::array<std::string, 3> rarity = {"ノーマル", "レア", "スーパーレア"};
  std::discrete_distribution<int> gacha({70, 25, 5});  // 70%, 25%, 5%

  std::mt19937 rng(2024);
  std::array<int, 3> counts{};
  for (int i = 0; i < 10000; ++i) {
    ++counts[gacha(rng)];
  }
  std::println("ノーマルが一番多い？ {}", counts[0] > counts[1] && counts[1] > counts[2]);
}
```

```text title="実行結果"
ノーマルが一番多い？ true
```

```cpp
#include <print>
#include <random>

int main() {
  std::discrete_distribution<int> gacha({70, 25, 5});
  std::println("{}", gacha.probabilities());   // 重みから計算された確率
}
```

```text title="実行結果"
[0.7, 0.25, 0.05]
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

| 場面 | 書き方 |
| --- | --- |
| ガチャの排出率 | `discrete_distribution<int> gacha({70, 25, 5});` |
| ドロップテーブル | 重みを並べて、添字でアイテムを選ぶ |

## よくあるミス

??? failure "重みに負の数を入れる"
    重みは 0 以上です。全部 0 だとエラーになります。

??? failure "確率と重みを取り違える"
    重みは比率なので、合計を 1 にそろえる必要はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 2 択 |
| [`piecewise_constant_distribution`](piecewise_constant_distribution.md) | 区間ごとの重み（連続値） |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重みに比例して添字を選ぶ
    - [x] 重みの合計は何でもよい
    - [x] ガチャ・ドロップ抽選

## 関連ページ

- [cpprefjp: std::discrete_distribution](https://cpprefjp.github.io/reference/random/discrete_distribution.html)
- [cppreference: std::discrete_distribution](https://en.cppreference.com/w/cpp/numeric/random/discrete_distribution)
