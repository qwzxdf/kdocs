---
title: std::ignore
summary: "tie や構造化束縛的な代入で、「この値は使わない」と書くための印。"
order: 58
tags:
  - ユーティリティ
---

# std::ignore

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::tie` で戻り値を受け取るとき、2 つ目の値はいらない、ということがあります。使わない変数をわざわざ宣言するのは無駄です。`std::ignore` は、`std::tie` の中で「この要素は受け取らない」ことを表す印で、何を代入しても捨てられます。

!!! tip "ポイント"
    - `std::tie(x, std::ignore) = pair;` で、2 つ目を捨てる
    - 何を代入しても、何も起きない
    - 構造化束縛では使えない。代わりに、使わない変数の名前を `_` などにする
    - 関数の戻り値を捨てる意図を示すときにも使われる（`std::ignore = f();`）

!!! info "このページを読む前に"
    [`std::tie`](tie.md) を先に読んでください。

## 関数の詳しい説明

### std::ignore {#ignore}

<span class="ver ver-11">C++11</span>

```cpp
inline constexpr /* 未規定の型 */ ignore;
```

`std::ignore` は、どんな値を代入されても受け付けて、何もしないオブジェクトです。`tie` の中の要素として、受け取らない場所に置きます。

```cpp
bool inserted;
std::tie(std::ignore, inserted) = set.insert(value);   // 位置は不要、成功したかだけ欲しい
```

`std::set::insert` が返す `pair<iterator, bool>` の、`iterator` を捨てて、`bool` だけを取る典型例です。

関数の戻り値を意図的に無視するのにも使えます。`[[nodiscard]]` の関数の結果を捨てるとき、`std::ignore = f();` と書くと、意図が明確になります。`(void)f();` と同じ効果です。

構造化束縛 `auto [a, b] = f();` では、使いません。すべての名前に変数が作られます。

## 実際に動かしてみる

```cpp
#include <print>
#include <set>
#include <tuple>

int main() {
  std::set<int> s;

  bool inserted = false;
  std::tie(std::ignore, inserted) = s.insert(10);
  std::println("1 回目: {}", inserted);

  std::tie(std::ignore, inserted) = s.insert(10);
  std::println("2 回目: {}", inserted);

  // 3 つ組から、真ん中だけを取る
  int mid = 0;
  std::tie(std::ignore, mid, std::ignore) = std::make_tuple(1, 2, 3);
  std::println("mid = {}", mid);
}
```

```text title="実行結果"
1 回目: true
2 回目: false
mid = 2
```

## ゲームでの使いどころ

`set` や `map` への挿入結果のうち、成功したかどうかだけを見たい、といった場面で使います。

## よくあるミス

??? failure "構造化束縛で使おうとする"
    `auto [std::ignore, x] = ...` は書けません。使わない名前を付けるか、`tie` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tie`](tie.md) | これを受け取る側 |
| [`std::make_tuple`](make_tuple.md) | 値の `tuple` を作る |
| `[[maybe_unused]]` | 使わない変数の警告を抑える |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::ignore](https://cpprefjp.github.io/reference/tuple/ignore.html)
- [cppreference: std::ignore](https://en.cppreference.com/w/cpp/utility/tuple/ignore)
