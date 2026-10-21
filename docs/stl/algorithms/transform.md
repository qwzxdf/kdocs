---
title: std::ranges::transform
summary: "範囲の全要素を変換して、別の場所（または同じ場所）に書き出す。"
order: 41
tags:
  - アルゴリズム
---

# std::ranges::transform

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::transform` は、**範囲の全要素に関数を適用して、結果を書き出す**アルゴリズムです。「全員のダメージを 2 倍にする」「座標を画面の座標に変える」のような、1 対 1 の変換に使います。2 つの範囲から 1 つ作る版もあります。

!!! tip "ポイント"
    - 結果を**別の場所**に書くなら、出力先のイテレータを渡す。同じ範囲に書き戻せば、その場で変換になる。
    - 出力先の大きさが足りないと範囲外に書き込む。`std::back_inserter` が安全。
    - 結果を新しい `vector` にしたいだけなら、[`views::transform`](views/transform.md) と [`ranges::to`](ranges_to.md) の組み合わせが短い。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::transform {#transform}

```cpp
template <input_range R, weakly_incrementable O, class F, class Proj = identity>
constexpr unary_transform_result<borrowed_iterator_t<R>, O> transform(R&& r, O result, F op, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 元 |
| `result` | 出力イテレータ | 書き込み先（元と同じでも OK） |
| `op` | 関数 | 要素を受け取って、書き込む値を返す |

<div class="anim" data-label="std::ranges::transform(v, v.begin(), double_it)">
1 2 3 4 # v
>2 >4 >6 >8 # 1 つずつ変換して書く
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<float> speeds = {1.0f, 2.0f, 3.0f};
  // その場で全部 1.5 倍にする（書き込み先 = 元）
  std::ranges::transform(speeds, speeds.begin(), [](float s) { return s * 1.5f; });
  std::println("{}", speeds);
}
```

```text title="実行結果"
[1.5, 3, 4.5]
```

!!! note "実際は"
    その場で書き換えるなら、範囲 for で `for (auto& s : speeds) s *= 1.5f;` と書くほうが読みやすいことも多いです。


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `op` | <span class="rank rank-must">必須</span> | ラムダ式など | 要素 1 つを受け取り、変換した値を返す |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | `op` に渡す前に、メンバを取り出す |
| 2 範囲版 | <span class="rank rank-sometimes">たまに</span> | `transform(a, b, out, op)` | 2 つの範囲から 1 つずつ取って変換する |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 全員のダメージを倍率で補正する | `transform(damages, damages.begin(), 2倍)` |
| ワールド座標をスクリーン座標に直す | `transform(points, back_inserter(out), 変換)` |
| 2 つのベクトル配列を足し合わせる | `transform(a, b, out.begin(), 足し算)` |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 出力先の大きさが足りない | 範囲外への書き込み（未定義動作） |

## よくあるミス

??? failure "for_each の代わりに使って、結果を捨てる"
    `transform` は結果を**書き出す**ためのものです。副作用だけを起こしたいなら [`for_each`](for_each.md) か範囲 for を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::transform`](views/transform.md) | コピーせず、遅延して変換して「見る」 |
| [`std::ranges::for_each`](for_each.md) | 各要素に処理を実行する（結果は書き出さない） |
| [`std::transform_reduce`](transform_reduce.md) | 変換して、合計などにまとめる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全要素を変換して書き出す
    - [x] 同じ範囲に書き戻せばその場で変換
    - [x] 出力先は十分な大きさか `back_inserter`

## 関連ページ

- [cpprefjp: std::ranges::transform](https://cpprefjp.github.io/reference/algorithm/ranges_transform.html)
- [cppreference: std::ranges::transform](https://en.cppreference.com/w/cpp/algorithm/ranges/transform)
