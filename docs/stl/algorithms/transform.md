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

全員のダメージを 2 倍にする、ワールド座標を画面の座標に変える。範囲の全要素を 1 対 1 で変換する処理は、`for` で回して、結果を別の配列へ書き込む形になりがちです。`std::ranges::transform` は、変換の関数を渡すだけで、全要素を変換して書き出す関数です。同じ範囲に書き戻せば、その場での変換になります。

!!! tip "ポイント"
    - 結果を**別の場所**に書くなら、出力先のイテレータを渡す。同じ範囲に書き戻せば、その場で変換になる。
    - 出力先の大きさが足りないと範囲外に書き込む。`std::back_inserter` が安全。
    - 結果を新しい `vector` にしたいだけなら、[`views::transform`](views/transform.md) と [`ranges::to`](ranges_to.md) の組み合わせが短い。

!!! info "このページを読む前に"
    [`ranges` とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

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

パラメーターの一括変換に使います。全員のダメージを 2 倍にする、全部の座標に行列を掛ける、全部の色を暗くする、といった処理が 1 行で書けます。

変換先が別の `vector` なら、`std::back_inserter` を出力先に渡すと、必要な数だけ自動で増えていきます。先に `reserve` しておけば、確保の回数も減ります。

結果を新しい `vector` にしたいだけなら、`views::transform` と `ranges::to` の組み合わせのほうが短く書けます。毎フレーム同じ変換を繰り返す場合は、ビューのまま使うと、コピーを減らせます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 出力先の大きさが足りない | 範囲外への書き込み（未定義動作） |

## よくあるミス

??? failure "出力先の大きさが足りない"
    `transform(src, dst.begin(), f)` で `dst` が小さいと、範囲外に書き込んで未定義動作になります。大きさをそろえるか、`std::back_inserter(dst)` を渡して自動で増やします。

??? failure "変換の関数に副作用を持たせる"
    `transform` の関数は、要素を変換するための純粋な関数として書くのが原則です。カウンターを増やすなど、状態を変える処理を入れたいなら、`for_each` を使います。

??? failure "入力と出力が一部重なる"
    入力の範囲と出力の範囲が、ずれて重なっていると、読む前に書き換えてしまいます。まったく同じ範囲か、重ならない範囲にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::transform`](views/transform.md) | 遅延評価で変換する。結果を保存しないなら、これが軽い |
| [`for_each`](for_each.md) | 副作用のある処理を全要素に行う |
| [`copy`](copy.md) | 変換せずに写す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全要素を 1 対 1 で変換して書き出す。
    - [x] 出力先の大きさに注意。`back_inserter` が安全。
    - [x] 副作用のある処理は `for_each`。

## 関連ページ

- [cpprefjp: std::ranges::transform](https://cpprefjp.github.io/reference/algorithm/ranges_transform.html)
- [cppreference: std::ranges::transform](https://en.cppreference.com/w/cpp/algorithm/ranges/transform)
