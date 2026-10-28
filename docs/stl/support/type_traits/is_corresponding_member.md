---
title: std::is_corresponding_member
summary: "2 つのメンバが、2 つの構造体の対応する位置にあるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_corresponding_member

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

先頭部分が同じ並びの 2 つの構造体で、「このメンバとこのメンバは対応しているか」を判定します。一方のメンバを他方のメンバのように読み書きしてよいかの根拠になります。

!!! tip "ポイント"
    - メンバへのポインタを 2 つ渡す。
    - `constexpr` の関数。
    - ほとんど使わない。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_corresponding_member {#is_corresponding_member}

```cpp
template <class S1, class S2, class M1, class M2>
constexpr bool is_corresponding_member(M1 S1::* m1, M2 S2::* m2) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m1, m2` | メンバへのポインタ | 比べる 2 つのメンバ |

- 戻り値: 対応していれば `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct P1 {
  int a;
  char b;
};
struct P2 {
  int c;
  char d;
};

int main() {
  std::println("{}", std::is_corresponding_member(&P1::a, &P2::c));
  std::println("{}", std::is_corresponding_member(&P1::a, &P2::d));
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 共通の先頭部分を持つ構造体の扱い |

## よくあるミス

??? failure "標準レイアウトでない型に使う"
    標準レイアウトの型だけが対象です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_layout_compatible`](is_layout_compatible.md) | 全体のレイアウトが互換か |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのメンバが 2 つの構造体の対応する位置にあるかを調べる
    - [x] メンバへのポインタを 2 つ渡す
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_corresponding_member](https://cpprefjp.github.io/reference/type_traits/is_corresponding_member.html)
- [cppreference: std::is_corresponding_member](https://en.cppreference.com/w/cpp/types/is_corresponding_member)
