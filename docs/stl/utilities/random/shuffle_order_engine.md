---
title: std::shuffle_order_engine
summary: "別のエンジンの出力の順番を入れ替えるアダプタ（`knuth_b` の元）。"
order: 900
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::shuffle_order_engine

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

線形合同法のようなエンジンは、連続した出力の間に規則性が残ります。その規則性を壊すために、出力をいったん表に溜めておき、乱数で選んだ位置の値を返す方法が、Knuth（クヌース）の考えたシャッフルです。`std::shuffle_order_engine<Engine, k>` は、これを実装したアダプタで、`std::knuth_b` が `<minstd_rand0, 256>` の別名です。

!!! tip "ポイント"
    - 元のエンジンの出力を `k` 個溜め、そこから選んで返す。返した場所には、新しい出力を補充する
    - 選ぶ位置は、直前に返した値から決まる
    - 出力の値の範囲や、分布は変わらない。順番だけが変わる
    - `k` が大きいほど、順番が崩れるが、状態が大きくなる

!!! info "このページを読む前に"
    [`std::knuth_b`](knuth_b.md) と [`std::linear_congruential_engine`](linear_congruential_engine.md) を先に読んでください。

## 関数の詳しい説明

### std::shuffle_order_engine {#shuffle_order_engine}

<span class="ver ver-11">C++11</span>

```cpp
template <class Engine, size_t k>
class shuffle_order_engine;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Engine` | 元になるエンジン |
| `k` | 溜めておく表の大きさ。1 以上 |

動きは、次のとおりです。

1. 初期化のとき、元のエンジンから `k` 個を取って、表に入れる。もう 1 個を取って、「直前の出力」とする
2. 出力するとき、「直前の出力」から添字を決める（`直前の出力 × k / 値の範囲` の整数部分）
3. 表のその位置の値を、返す値にする
4. 表のその位置に、元のエンジンから新しい値を入れる。返した値が、次の「直前の出力」になる

値の範囲（`min()` と `max()`）と、各値の出る確率の分布は、元のエンジンと同じです。順番だけが入れ替わります。

`k` は、静的な定数の `table_size` として取れます。`knuth_b` の `table_size` は 256 です。

## 実際に動かしてみる

```cpp
#include <print>
#include <random>

int main() {
  // knuth_b と同じ組み合わせ
  using E = std::shuffle_order_engine<std::minstd_rand0, 256>;
  E e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）

  std::println("表の大きさ: {}", E::table_size);
  std::println("範囲は元と同じ: {}",
               E::min() == std::minstd_rand0::min() && E::max() == std::minstd_rand0::max());
}
```

```text title="実行結果"
1112339016
表の大きさ: 256
範囲は元と同じ: true
```

## ゲームでの使いどころ

使う場面はほとんどありません。`knuth_b` として、歴史的な理由で存在しています。

## よくあるミス

??? failure "質が上がると思う"
    順番は崩れますが、元のエンジンの周期や分布の品質は上がりません。品質が要るなら `mt19937` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`knuth_b`](knuth_b.md) | `<minstd_rand0, 256>` の別名 |
| [`discard_block_engine`](discard_block_engine.md) | 出力を間引く |
| [`std::shuffle`](../../algorithms/shuffle.md) | 要素の並びをシャッフルするアルゴリズム。別物 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::shuffle_order_engine](https://cpprefjp.github.io/reference/random/shuffle_order_engine.html)
- [cppreference: std::shuffle_order_engine](https://en.cppreference.com/w/cpp/numeric/random/shuffle_order_engine)
