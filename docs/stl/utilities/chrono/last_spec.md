---
title: std::chrono::last_spec
summary: "「最後」を表す定数 `std::chrono::last` の型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::last_spec

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`March / last` や `Friday[last]` の `last` は、整数でも文字列でもなく、`std::chrono::last_spec` という、空の型の定数です。「最後」という意味だけを表し、演算子の `/` や `[]` と組み合わせて、最終日や最終週を指す型を作ります。

自分で `last_spec` の変数を作ることは、ありません。`std::chrono::last` を書くだけです。

!!! tip "ポイント"
    - `last_spec` は空の型。`std::chrono::last` がその定数
    - `month / last` は `month_day_last`、`weekday[last]` は `weekday_last`
    - 年と組み合わせると、`year_month_day_last` などになる
    - 値を持たないので、比較や計算はできない

!!! info "このページを読む前に"
    [`month_day_last`](month_day_last.md) と [`weekday_last`](weekday_last.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::last_spec {#last_spec}

<span class="ver ver-20">C++20</span>

```cpp
struct last_spec {
  explicit last_spec() = default;
};
inline constexpr last_spec last{};
```

コンストラクターが `explicit` なので、`last_spec x = {};` とは書けません。`last` を使います。

`last` と組み合わせられるのは、次の 3 通りです。

| 書き方 | 結果の型 | 意味 |
| --- | --- | --- |
| `March / last` | `month_day_last` | 3 月の最終日 |
| `Friday[last]` | `weekday_last` | 最後の金曜日 |
| `2026y / March / last` | `year_month_day_last` | 2026 年 3 月の最終日 |

名前が `last` なので、変数名などに使うと、`std::chrono` の名前空間を `using` したときに、紛らわしくなります。`using namespace std::chrono;` のコードで `last` という変数を作ると、同じ名前の定数と衝突するかもしれません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  using namespace std::chrono;

  // last と組み合わせた結果の型を確かめる
  static_assert(std::is_same_v<decltype(March / last), month_day_last>);
  static_assert(std::is_same_v<decltype(Friday[last]), weekday_last>);
  static_assert(std::is_same_v<decltype(2026y / March / last), year_month_day_last>);

  const year_month_day_last end = 2026y / March / last;
  std::println("2026 年 3 月の最終日: {}", static_cast<unsigned>(end.day()));
}
```

```text title="実行結果"
2026 年 3 月の最終日: 31
```

`static_assert` が通ることで、`last` の組み合わせが、それぞれの型になることが確かめられます。

## ゲームでの使いどころ

最終日や最終週を指す設計値を書くときに、`last` を使います。自分で型を意識することはありません。

## よくあるミス

??? failure "last を変数名に使って衝突する"
    `using namespace std::chrono;` の下で `auto last = ...;` と書くと、名前が紛らわしくなります。変数名を変えるか、`using` を限定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_day_last`](month_day_last.md) | `month / last` の型 |
| [`weekday_last`](weekday_last.md) | `weekday[last]` の型 |
| [`year_month_day_last`](year_month_day_last.md) | 年を含む最終日 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: last_spec](https://cpprefjp.github.io/reference/chrono/last_spec.html)
- [cppreference: std::chrono::last_spec](https://en.cppreference.com/w/cpp/chrono/last_spec)
