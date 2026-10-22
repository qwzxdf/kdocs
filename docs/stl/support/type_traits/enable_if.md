---
title: std::enable_if
summary: "条件が真のときだけ、型を存在させる（SFINAE のための道具）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::enable_if

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

同じ名前の関数を、整数用と小数用で書き分けたいとき、テンプレートの条件で「この型のときだけ有効」と決めたくなります。`enable_if<条件, T>` は、条件が真のときだけ `::type` を持ち、偽だと型がなくなるため、その関数が候補から外れます（SFINAE）。C++20 では `requires` やコンセプトが読みやすいです。

!!! tip "ポイント"
    - `enable_if_t<条件, T>`: 条件が真なら `T`、偽ならコンパイルエラー（候補から外れる）。
    - 関数テンプレートの追加の引数に、`std::enable_if_t<条件, int> = 0` と書くのが定番。
    - C++20 以降は `requires` を優先する。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::enable_if {#enable_if}

```cpp
template <bool B, class T = void>
struct enable_if {};  // B が false のとき ::type はない
template <class T>
struct enable_if<true, T> { using type = T; };
template <bool B, class T = void>
using enable_if_t = typename enable_if<B, T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B` | bool | 条件 |
| `T` | 型 | 条件が真のときの型（既定は `void`） |

- 戻り値: 条件が真なら `T`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

template <class T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
std::string Describe(T) {
  return "integer";
}
template <class T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
std::string Describe(T) {
  return "float";
}

int main() {
  std::println("{} {}", Describe(1), Describe(1.0f));
}
```

```text title="実行結果"
integer float
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 型ごとに関数を書き分ける |

## よくあるミス

??? failure "両方の条件が重なる"
    条件が重なると、候補が複数になり、曖昧でコンパイルエラーになります。条件は排他的にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conditional`](conditional.md) | 条件で型を選ぶ |
| [`concepts`](../concepts/same_as.md) | C++20 の書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件が真のときだけ、型を存在させる（SFINAE のための道具）
    - [x] `enable_if_t<条件, T>`: 条件が真なら `T`、偽ならコンパイルエラー（候補から外れる）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::enable_if](https://cpprefjp.github.io/reference/type_traits/enable_if.html)
- [cppreference: std::enable_if](https://en.cppreference.com/w/cpp/types/enable_if)
