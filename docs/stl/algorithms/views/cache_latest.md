---
title: views::cache_latest
summary: "直前に計算した要素を覚えておく view。"
order: 900
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# views::cache_latest

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <ranges>`
</div>

`views::transform` のように、要素を変換するビューは、同じ要素を複数回読むたびに、変換を毎回行います。変換が重いと、その無駄が目立ちます。`std::views::cache_latest` は、直前に読んだ要素の変換結果を 1 つだけ覚えて、同じ位置を再び読むときに、再利用するビューです。

!!! tip "ポイント"
    - 直前の 1 要素の結果を、キャッシュする
    - `transform` のあとに置いて、重い変換を重複して行わないようにする
    - `filter` と `transform` の組み合わせで、変換が 2 回走る問題を防ぐ
    - C++26

!!! info "このページを読む前に"
    [`views::transform`](transform.md) を先に読んでください。

## 関数の詳しい説明

### std::views::cache_latest {#cache_latest}

<span class="ver ver-26">C++26</span>

```cpp
inline constexpr /* 未規定 */ cache_latest = /* 未規定 */;
// v | std::views::transform(f) | std::views::cache_latest
```

典型的な問題は、`v | transform(f) | filter(p)` で、`filter` が `p` の判定のために 1 回、ループが値を使うためにもう 1 回、`transform` の結果を読み、`f` が 2 回呼ばれることです。

間に `cache_latest` を入れると、直前の 1 要素の結果が保持されて、`f` の呼び出しが 1 要素につき 1 回になります。

代償は、要素の参照を返せず、値のキャッシュを持つので、イテレーターの `operator*` が非 const になる、といった制約です。使える範囲の種類は、入力イテレーターの範囲になります。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
auto expensive = [](int x) { return HeavyCompute(x); };

// cache_latest なし: filter が 2 回読むので、expensive が 2 回呼ばれる
auto a = v | std::views::transform(expensive)
           | std::views::filter([](int y) { return y > 10; });

// cache_latest あり: 1 要素に 1 回だけ
auto b = v | std::views::transform(expensive)
           | std::views::cache_latest
           | std::views::filter([](int y) { return y > 10; });
```

## ゲームでの使いどころ

重い変換（物理の計算、パス検索）を含むパイプラインで、変換が重複して呼ばれるのを防ぎます。

## よくあるミス

??? failure "常に付ける"
    要素の参照を返せなくなり、余計な制約がつきます。重い変換のときだけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`transform`](transform.md) | 要素を変換する |
| [`filter`](filter.md) | 条件で絞る |
| `std::ranges::to` | 結果を具体化する |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: views::cache_latest](https://cpprefjp.github.io/reference/ranges/cache_latest_view.html)
- [cppreference: views::cache_latest](https://en.cppreference.com/w/cpp/ranges/cache_latest_view)
