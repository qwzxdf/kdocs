---
title: std::uniform_int_distribution
summary: "範囲内の整数を、同じ確率で出す（両端を含む）。"
order: 10
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::uniform_int_distribution

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

サイコロを振る、ドロップするアイテムを選ぶ、配列からランダムに 1 つ選ぶ。ゲームでは整数の乱数をいちばん多く使います。`rand() % 6 + 1` と書くと動きますが、剰余の計算で値に偏りが出ます。`std::uniform_int_distribution` は、範囲内のどの整数も同じ確率で返す部品で、偏りの心配がありません。

!!! tip "ポイント"
    - 範囲は `[a, b]` で、両端を含む。`(1, 6)` なら 1 から 6。
    - 配列の添え字には `(0, size - 1)` を渡す。`size` は含めない。
    - `rand() % n` は偏るので使わない。

!!! info "このページを読む前に"
    [`std::mt19937`](mt19937.md) の乱数エンジンの使い方を先に読んでください。

## 関数の詳しい説明

### std::uniform_int_distribution {#uniform_int}

```cpp
template <class IntType = int>
class uniform_int_distribution {
 public:
  explicit uniform_int_distribution(IntType a, IntType b = std::numeric_limits<IntType>::max());
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 整数 | 最小値（**含む**） |
| `b` | 整数 | 最大値（**含む**） |

`a` は下限、`b` は上限で、どちらも出る可能性があります。`uniform_int_distribution<int> dice(1, 6)` なら、1、2、3、4、5、6 が同じ確率で出ます。

`vector` の要素をランダムに選ぶときは、`uniform_int_distribution<size_t> pick(0, v.size() - 1)` と書きます。`v.size()` を上限に渡すと、範囲外の添え字が出ます。`v` が空だと、`v.size() - 1` が大きな値になるので、空でないことを先に確かめます。

`a > b` は未定義動作です。型に `char` や `bool` は使えません。`int`、`long`、`unsigned` などを指定します。

- `a` 〜 `b` の整数が同じ確率で出ます。`a > b` は未定義動作

```cpp
#include <print>
#include <random>

int main() {
  std::mt19937 rng(42);
  std::uniform_int_distribution<int> dice(1, 6);

  bool ok = true;
  for (int i = 0; i < 1000; ++i) {
    int v = dice(rng);
    ok = ok && v >= 1 && v <= 6;   // 1〜6 に収まる（6 を含む）
  }
  std::println("全部 1〜6 の範囲？ {} / {} 〜 {}", ok, dice.min(), dice.max());
}
```

```text title="実行結果"
全部 1〜6 の範囲？ true / 1 〜 6
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

サイコロとドロップ判定の定番です。`dice(rng)` で 1〜6 を出し、敵のダメージの幅や、宝箱の中身の抽選を決めます。

配列からランダムに 1 つ選ぶ処理にも使います。敵の出現位置の候補リストから選ぶ、BGM の曲目をシャッフルせずに 1 つ選ぶ、といった場面です。`v[pick(rng)]` と書きます。

重みのある抽選（レアなアイテムほど出にくい）は、`uniform_int_distribution` を累積の重みと組み合わせるか、`std::discrete_distribution` を使います。

## よくあるミス

??? failure "上限を含めない書き方をする"
    `uniform_int_distribution<int> pick(0, v.size())` と書くと、`v.size()` が出ることがあり、範囲外のアクセスになります。添え字には `(0, v.size() - 1)` です。

??? failure "`rand() % n` で作る"
    `rand()` の最大値が `n` の倍数でないと、小さい値が少し出やすくなります。品質も低いので、標準の分布を使います。

??? failure "符号付きと符号なしを混ぜて範囲を作る"
    `uniform_int_distribution<int> pick(0, v.size() - 1)` は、`size_t` から `int` への変換で警告が出ます。`v.size()` が大きい場合は、桁あふれもします。型は `size_t` で指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 小数版。上限を含まない |
| [`discrete_distribution`](discrete_distribution.md) | 重み付きの抽選 |
| [`shuffle`](../../algorithms/shuffle.md) | 並びをかき混ぜる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `[a, b]` で、両端を含む。
    - [x] 配列の添え字には `(0, size - 1)`。
    - [x] `rand() % n` は使わない。

## 関連ページ

- [cpprefjp: std::uniform_int_distribution](https://cpprefjp.github.io/reference/random/uniform_int_distribution.html)
- [cppreference: std::uniform_int_distribution](https://en.cppreference.com/w/cpp/numeric/random/uniform_int_distribution)
