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

`transform` の関数が重い処理で、同じ要素に対して何度も呼ばれると無駄です。`views::cache_latest` は、いま見ている要素の計算結果を 1 つだけ覚えておき、同じ要素を読むときは再計算しません。

!!! tip "ポイント"
    - 直前の 1 要素だけを覚える。
    - `transform` や `filter` と組み合わせて、同じ要素の関数呼び出しが何度も起きるのを防ぐ。
    - `const` では使えない（内部に状態をもつため）。

!!! info "このページを読む前に"
    [`views`](../views.md) を先に読んでください。

## 関数の詳しい説明

### views::cache_latest {#cache_latest}

```cpp
constexpr auto views::cache_latest();  // パイプで使う
```

- 戻り値: `cache_latest_view`
- 計算量: begin / end は定数

### std::ranges::cache_latest_view {#cache_latest_view}

```cpp
template <input_range V>
class cache_latest_view;
```

- 戻り値: `views::cache_latest` が作る view の型

ふつうは `views::cache_latest` で書くので、型の名前を自分で書くことは少なく、`auto` で受けます。


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  int calls = 0;
  auto heavy = [&](int x) { ++calls; return x * x; };
  auto r = v | std::views::transform(heavy) | std::views::cache_latest
             | std::views::filter([](int x) { return x % 2 == 0; });
  int sum = 0;
  for (int x : r) sum += x;
  std::println("{} {}", sum, calls);
}
```

```text title="実行結果"
20 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 重い変換の結果を 1 度だけ計算する | `v | views::transform(heavy) | views::cache_latest | views::filter(pred)` |

## よくあるミス

??? failure "const な範囲に使う"
    内部に状態を持つため、`const` の view としては使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::transform`](transform.md) | 各要素を変換する |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 直前の要素の結果を覚える
    - [x] 同じ要素の再計算を避ける
    - [x] C++26

## 関連ページ

- [cpprefjp: views::cache_latest](https://cpprefjp.github.io/reference/ranges/cache_latest_view.html)
- [cppreference: views::cache_latest](https://en.cppreference.com/w/cpp/ranges/cache_latest_view)
