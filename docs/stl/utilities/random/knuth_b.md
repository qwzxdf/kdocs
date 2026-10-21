---
title: std::knuth_b
summary: "内部で並べ替えを使う乱数エンジン。"
order: 6
group: 乱数エンジン
tags:
  - ユーティリティ
---

# std::knuth_b

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::knuth_b` は、**内部に 256 個の値の表を持ち、出る順番をかき混ぜる**乱数エンジンです（Knuth が示した方法）。`minstd_rand0` の出力をかき混ぜるので、`minstd_rand0` よりは質が良くなります。使い道は少なく、知っておくだけで十分です。

!!! tip "ポイント"
    - `std::shuffle_order_engine<minstd_rand0, 256>` の別名。
    - `mt19937` のほうが定番で、品質も上。
    - 標準で定義されているが、実際にはほとんど使われない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::knuth_b {#knuth_b}

```cpp
using knuth_b = std::shuffle_order_engine<std::minstd_rand0, 256>;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `seed` | 整数 | 種 | `1` |

- 戻り値: `operator()` で整数を返す
- 計算量: O(1)

```cpp
#include <print>
#include <random>

int main() {
  std::println("{} 〜 {}", std::knuth_b::min(), std::knuth_b::max());
}
```

```text title="実行結果"
1 〜 2147483646
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゲームではほぼ出番なし | `mt19937` を使う |

## よくあるミス

??? failure "mt19937 より良いと思い込む"
    品質は `mt19937` のほうが上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mt19937`](mt19937.md) | 定番 |
| [`std::minstd_rand`](minstd_rand.md) | 元になっているエンジン |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力をかき混ぜるエンジン
    - [x] 使い道は少ない
    - [x] `mt19937` を使う

## 関連ページ

- [cpprefjp: std::knuth_b](https://cpprefjp.github.io/reference/random/shuffle_order_engine.html)
- [cppreference: std::shuffle_order_engine](https://en.cppreference.com/w/cpp/numeric/random/shuffle_order_engine)
