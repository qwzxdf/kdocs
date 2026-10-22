---
title: std::aligned_union
summary: "複数の型のどれでも入れられる、生のメモリ領域の型。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::aligned_union

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

いくつかの型のどれか 1 つを入れられる領域（`union` のようなもの）が欲しいが、`union` は非トリビアルな型を入れにくい、ということがあります。`aligned_union<MinLen, Types...>` は、すべての型を入れられる大きさと境界の領域を表します。C++23 で非推奨になりました。

!!! tip "ポイント"
    - C++23 で非推奨。
    - `::type` が領域の型、`alignment_value` が境界。
    - `variant` を使うほうが安全。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::aligned_union {#aligned_union}

```cpp
template <size_t Len, class... Types>
struct aligned_union {
  static constexpr size_t alignment_value = /* 最大のアライメント */;
  using type = /* 領域の型 */;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Len` | size_t | 最低限の大きさ |
| `Types...` | 型 | 入れたい型の一覧 |

- 戻り値: 領域の型と境界
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::aligned_union<0, int, double>::alignment_value);
  std::println("{}", sizeof(std::aligned_union_t<0, int, double>));
}
```

```text title="実行結果"
8
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 複数の型のどれかを入れる領域を用意する |

## よくあるミス

??? failure "新しいコードで使う"
    非推奨です。`std::variant` か、`alignas` の `std::byte` 配列を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`aligned_storage`](aligned_storage.md) | 1 つの型の領域 |

## コンパイラ対応

C++11 から使えます。C++23 で非推奨になりました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の型のどれでも入れられる、生のメモリ領域の型
    - [x] C++23 で非推奨
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::aligned_union](https://cpprefjp.github.io/reference/type_traits/aligned_union.html)
- [cppreference: std::aligned_union](https://en.cppreference.com/w/cpp/types/aligned_union)
