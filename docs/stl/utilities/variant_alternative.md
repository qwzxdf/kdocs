---
title: std::variant_alternative
summary: "variant の N 番目の選択肢の型を取り出す。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_alternative

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`variant<int, double, std::string>` の「2 番目の型は何か」をテンプレートの中で知りたいことがあります。`variant_alternative_t<N, V>` が、N 番目の選択肢の型を教えてくれます。

!!! tip "ポイント"
    - 番号は 0 から。
    - `_t` 版で型がそのまま取れる。
    - 選択肢の数は [`variant_size`](variant.md) で調べる。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_alternative {#variant_alternative}

```cpp
template <size_t I, class V> struct variant_alternative;
template <size_t I, class V> using variant_alternative_t = typename variant_alternative<I, V>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | size_t | 選択肢の番号 |
| `V` | variant 型 | 調べる variant |

- 戻り値: I 番目の選択肢の型
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>
#include <variant>

int main() {
  using V = std::variant<int, double, std::string>;
  std::println("{}", std::is_same_v<std::variant_alternative_t<1, V>, double>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| variant の各選択肢の型でテンプレートを展開 | `std::variant_alternative_t<I, V>` |

## よくあるミス

??? failure "範囲外の番号"
    選択肢の数以上の番号を渡すと、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant`](variant.md) | variant の本体 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] N 番目の選択肢の型を取り出す
    - [x] `_t` 版を使う
    - [x] 番号は 0 から

## 関連ページ

- [cpprefjp: std::variant_alternative](https://cpprefjp.github.io/reference/variant/variant_alternative.html)
- [cppreference: std::variant_alternative](https://en.cppreference.com/w/cpp/utility/variant/variant_alternative)
