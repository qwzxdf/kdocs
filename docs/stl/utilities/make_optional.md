---
title: std::make_optional
summary: "値から optional を作る（型を書かなくてよい）。"
order: 900
tags:
  - ユーティリティ
---

# std::make_optional

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <optional>`
</div>

`std::optional<int>{42}` のように、型を書くのは面倒です。`make_optional(42)` なら、型を推論して `optional<int>` を作ってくれます。`make_pair` や `make_tuple` の `optional` 版です。型を指定して、コンストラクターの引数だけを渡し、その場でオブジェクトを作る形もあります。C++17 以降は、`std::optional o{42};` と型の推論が効くので、出番はほとんどありません。

!!! tip "ポイント"
    - 値を渡すと型を推論する（`make_optional(42)` は `optional<int>`）。
    - 型を指定して引数を渡すと、その場でオブジェクトを作る。
    - C++17 の CTAD（`std::optional o{42};`）でも同じことが書ける。

!!! info "このページを読む前に"
    [`std::optional`](optional.md) を先に読んでください。

## 関数の詳しい説明

### std::make_optional {#make_optional}

```cpp
template <class T> constexpr optional<decay_t<T>> make_optional(T&& value);
template <class T, class... Args> constexpr optional<T> make_optional(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | T | 中に入れる値 |
| `args...` | 引数 | `T` のコンストラクタに渡す引数 |

- 戻り値: 作った `optional`
- 計算量: 定数 + 中身の構築


## 実際に動かしてみる

```cpp
#include <optional>
#include <print>
#include <string>

int main() {
  auto a = std::make_optional(42);
  auto b = std::make_optional<std::string>(3, 'a');
  std::println("{} {}", *a, *b);
}
```

```text title="実行結果"
42 aaa
```

## ゲームでの使いどころ

新しいコードでは、`std::optional o{42};` と書けば、型の推論が働くので、`make_optional` は不要です。古いコードや、他人のコードを読むときに出会う関数です。

型を指定してコンストラクター引数を渡す形は、コピーを避けて、その場でオブジェクトを作りたいときに使えます。`make_optional<Enemy>(hp, speed)` と書くと、`optional<Enemy>` の中で `Enemy` が直接作られます。

関数の戻り値で「見つかった」を返すときは、`return value;` と値を返すだけで、暗黙に `optional` になります。

## よくあるミス

??? failure "参照を渡したつもりでコピーされる"
    `make_optional(x)` は `x` をコピーまたはムーブします。参照のまま保持するわけではありません。

??? failure "型の推論で意図しない型になる"
    `make_optional("abc")` は、`optional<const char*>` になり、`optional<std::string>` にはなりません。文字列にしたいなら型を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`optional`](optional.md) | optional の本体 |
| [`nullopt`](nullopt.md) | 値がない状態 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値から optional を作る
    - [x] 型を指定して引数でも作れる
    - [x] CTAD でも同じ

## 関連ページ

- [cpprefjp: std::make_optional](https://cpprefjp.github.io/reference/optional/make_optional.html)
- [cppreference: std::make_optional](https://en.cppreference.com/w/cpp/utility/optional/make_optional)
