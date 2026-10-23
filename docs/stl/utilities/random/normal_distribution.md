---
title: std::normal_distribution
summary: "正規分布（釣り鐘型）。平均の近くが出やすい。"
order: 14
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::normal_distribution

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

弾の着弾点にばらつきを持たせたい、敵のステータスに個体差を付けたい。一様な乱数だと、範囲の端も真ん中も同じ確率で出るので、不自然に見えます。`std::normal_distribution` は、平均の近くが出やすく、離れるほど出にくい乱数（正規分布、釣り鐘型）を出します。平均 ± 標準偏差の範囲に、約 68% が入ります。

!!! tip "ポイント"
    - `normal_distribution<float> hp(100.0f, 15.0f);` は、平均 100、ばらつき 15。
    - 値の範囲に**制限はない**（平均から大きく離れた値もまれに出る）。範囲を限るなら `std::clamp`。
    - 2 次元・3 次元のばらつきは、軸ごとに作る。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::normal_distribution {#normal}

```cpp
template <class RealType = double>
class normal_distribution {
 public:
  explicit normal_distribution(RealType mean = 0.0, RealType stddev = 1.0);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mean` | 浮動小数点 | 平均（一番出やすい値） |
| `stddev` | 浮動小数点 | 標準偏差（ばらつきの大きさ） |

- 平均の近くが出やすく、離れるほど出にくい乱数です。平均 ± 標準偏差の範囲に約 68% が入ります

!!! note "実際は"
    弾のばらつき、ステータスの個体差など、「だいたいこのくらい、たまに外れる」ものに使います。範囲の外の値も出るので、`std::clamp` で収めます。

```cpp
#include <print>
#include <random>

int main() {
  std::normal_distribution<double> d(100.0, 15.0);
  std::println("平均 {} / ばらつき {}", d.mean(), d.stddev());
}
```

```text title="実行結果"
平均 100 / ばらつき 15
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

射撃のばらつきに使います。狙った点を平均にして、ばらつきを標準偏差に決めると、中心付近に当たりやすく、まれに大きく外れる、自然な散らばりになります。x と y を別々に作ります。

敵の HP やステータスの個体差にも向いています。`normal_distribution<float> hp(100.0f, 15.0f);` なら、平均 100 で、だいたい 85〜115 に収まります。

値の範囲に制限はなく、平均から大きく離れた値もまれに出ます。範囲を限るなら、`std::clamp` を通します。

## よくあるミス

??? failure "範囲を限りたいのに、そのまま使う"
    正規分布は無限に広がります。`std::clamp` で範囲に収めます。

??? failure "標準偏差に分散を渡す"
    2 つ目の引数は**標準偏差**（分散ではありません）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 範囲内で均等 |
| [`lognormal_distribution`](lognormal_distribution.md) | 対数が正規分布 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 平均の近くが出やすい分布
    - [x] 2 つ目は標準偏差
    - [x] 範囲を限るなら `clamp`

## 関連ページ

- [cpprefjp: std::normal_distribution](https://cpprefjp.github.io/reference/random/normal_distribution.html)
- [cppreference: std::normal_distribution](https://en.cppreference.com/w/cpp/numeric/random/normal_distribution)
