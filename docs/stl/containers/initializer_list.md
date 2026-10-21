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

`std::initializer_list<T>` は、**`{1, 2, 3}` のように波かっこで書いた値の並びを受け取るための型**です。`std::vector<int> v = {1, 2, 3};` や `std::max({a, b, c})` が書けるのは、これのおかげです。要素は一時的な配列に置かれ、`initializer_list` はそれを指す軽い窓です。

!!! tip "ポイント"
    - 自分の関数やクラスで `{1, 2, 3}` を受けたいときに使う。
    - **要素は一時的なもの**。`initializer_list` を保存すると、中身が消えている。
    - 要素は `const`（書き換えられない）。コピーは作られない（`move` もできない）。

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

| 場面 | 書き方 |
| --- | --- |
| 可変個の値を受ける関数（`max({a, b, c})`） | `void Add(std::initializer_list<Item> items)` |
| コンテナを `{ ... }` で初期化できる自作クラス | `Party(std::initializer_list<Member> members)` |

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
