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
`#include <random>`
</div>

`std::seed_seq` は、**複数の整数（種のもと）から、乱数エンジンの十分な量の種を作る**クラスです。`mt19937` は内部に 624 個の状態を持つので、32 ビットの種 1 つだと偏りが出ます。`seed_seq` を渡すと、状態が十分にばらけます。

!!! tip "ポイント"
    - `std::seed_seq seq{rd(), rd(), rd(), rd()};` のように、複数の値を渡す。
    - エンジンの引数にそのまま渡せる: `std::mt19937 rng(seq);`。
    - 同じ入力なら、同じ種が作られる（再現できる）。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::seed_seq {#seed_seq}

```cpp
class seed_seq {
 public:
  seed_seq(std::initializer_list<unsigned> values);
  std::size_t size() const noexcept;
  template <class RandomIt> void generate(RandomIt first, RandomIt last);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `values` | 整数のリスト | 種のもとにする値 |

- 戻り値: `generate` で、指定した範囲に種を書き出す
- 計算量: O(n)

```cpp
#include <print>
#include <random>

int main() {
  std::seed_seq seq{1, 2, 3};
  std::println("もとの値の数: {}", seq.size());

  std::mt19937 a(seq);
  std::seed_seq seq2{1, 2, 3};
  std::mt19937 b(seq2);
  std::println("同じ入力なら同じ列: {}", a() == b());
}
```

```text title="実行結果"
もとの値の数: 3
同じ入力なら同じ列: true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| リプレイ用に、複数の値（ステージ番号 + プレイヤー ID）から種を作る | `std::seed_seq{stage, player_id}` |
| エンジンの状態を十分にばらけさせる | `std::seed_seq{rd(), rd(), rd(), rd()}` |

## よくあるミス

??? failure "同じ seed_seq を使い回す"
    エンジンの引数に渡す `seed_seq` は、非 const の参照で渡されます。使い回すと、状態が進んで違う種になります。必要なら作り直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::random_device`](random_device.md) | OS の乱数。種のもとに使う |
| [`std::mt19937`](mt19937.md) | 受け取るエンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の値から種を作る
    - [x] `mt19937` の状態を十分にばらけさせる
    - [x] 同じ入力なら同じ種

## 関連ページ

- [cpprefjp: std::seed_seq](https://cpprefjp.github.io/reference/random/seed_seq.html)
- [cppreference: std::seed_seq](https://en.cppreference.com/w/cpp/numeric/random/seed_seq)
