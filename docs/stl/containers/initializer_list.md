---
title: std::initializer_list
summary: "{1, 2, 3} という波かっこの並びを、関数やコンストラクタが受け取るための型。"
order: 25
tags:
  - コンテナ
---

# std::initializer_list

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <initializer_list>`
</div>

`std::vector<int> v = {1, 2, 3};` や `std::max({a, b, c})` のように、波かっこで値の並びを渡して書けるのは便利です。自分のクラスや関数でも、この書き方を受けたいと思ったとき、受け取る側の型が必要になります。`std::initializer_list<T>` は、波かっこで書いた値の並びを受け取るための型です。要素は一時的な配列に置かれ、`initializer_list` は、それを指すだけです。

!!! tip "ポイント"
    - 自分の関数やクラスで `{1, 2, 3}` を受けたいときに使う。
    - **要素は一時的なもの**。`initializer_list` を保存すると、中身が消えている。
    - 要素は `const`（書き換えられない）。コピーは作られない（`move` もできない）。

!!! info "このページを読む前に"
    波かっこによる初期化（`{1, 2, 3}`）の書き方が分かると読みやすいです。

## 宣言

```cpp
template <class T>
class initializer_list;
```

## 関数の詳しい説明

### begin, end {#begin_end}

```cpp
constexpr const T* begin() const noexcept;
constexpr const T* end() const noexcept;
```

- 戻り値: 最初の要素と、終わりの次を指すポインター
- 計算量: O(1)

### size {#size}

```cpp
constexpr size_t size() const noexcept;
```

- 戻り値: 要素数
- 計算量: O(1)

```cpp
#include <initializer_list>
#include <print>
#include <vector>

int Sum(std::initializer_list<int> values) {
  int total = 0;
  for (int v : values) {
    total += v;
  }
  return total;
}

int main() {
  std::println("合計 {}", Sum({1, 2, 3}));

  // 波かっこと丸かっこで意味が変わる
  std::vector<int> a{3, 4};   // 要素が 3 と 4 の 2 個
  std::vector<int> b(3, 4);   // 4 が 3 個
  std::println("{} {}", a.size(), b.size());
}
```

```text title="実行結果"
合計 6
2 3
```

## ゲームでの使いどころ

自作のコンテナ型やベクトル型に `MyList list = {1, 2, 3};` と書けるコンストラクターを用意するときに使います。`MyList(std::initializer_list<int> init)` を持たせるだけです。

可変個の引数を持つ関数にも向いています。`int Sum(std::initializer_list<int> values)` と書くと、`Sum({1, 2, 3})` のように呼べます。型がそろっている引数の並びを渡すだけなら、可変長テンプレートより簡単です。

要素は一時的な配列に置かれます。`initializer_list` をメンバー変数に保存すると、配列が消えたあとにぶら下がります。保存するなら、`vector` などにコピーします。

## よくあるミス

??? failure "initializer_list を保存する"
    `initializer_list` は一時的な配列を指すだけです。メンバに保存して後で使うと、中身が消えて未定義動作です。保存するなら `std::vector` にコピーします。

??? failure "丸かっこと波かっこの取り違え"
    `std::vector<int> v{3, 4}` は 2 要素、`v(3, 4)` は 4 が 3 個。波かっこは `initializer_list` のコンストラクタが優先されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::span`](span.md) | 既存の配列を指す窓。保存しても安全（元が生きていれば） |
| [`std::vector`](vector.md) | 中身を保存する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `{1, 2, 3}` を受けるための型
    - [x] 要素は一時的で const
    - [x] 保存せず、`vector` にコピーする

## 関連ページ

- [cpprefjp: std::initializer_list](https://cpprefjp.github.io/reference/initializer_list/initializer_list.html)
- [cppreference: std::initializer_list](https://en.cppreference.com/w/cpp/utility/initializer_list)
