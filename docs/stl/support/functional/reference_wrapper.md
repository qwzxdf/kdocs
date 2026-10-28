---
title: std::reference_wrapper
summary: "参照を、コピー・代入できる値として持つ入れ物。"
order: 20
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::reference_wrapper

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

`std::reference_wrapper<T>` は、**参照をコピーや代入のできる値として持つ**入れ物です。通常の参照 `T&` は、コンテナに入れたり、代入し直したりできません。`reference_wrapper` なら、`std::vector<std::reference_wrapper<Enemy>>` のように参照の一覧を作れます。[`std::ref`](ref.md) が作ります。

!!! tip "ポイント"
    - `std::vector<T&>` は書けないが、`std::vector<std::reference_wrapper<T>>` は書ける。
    - `.get()` で参照を取り出す（`T&` へ暗黙に変換もされる）。
    - 元のオブジェクトより長く持たない。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::reference_wrapper {#reference_wrapper}

```cpp
template <class T>
class reference_wrapper {
 public:
  reference_wrapper(T& ref) noexcept;
  T& get() const noexcept;
  operator T&() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ref` | `T&` | 参照する対象 |

- 戻り値: `get()` で元の参照
- 計算量: O(1)

```cpp
#include <functional>
#include <print>
#include <vector>

int main() {
  int a = 1;
  int b = 2;
  std::vector<std::reference_wrapper<int>> refs = {a, b};  // 参照の一覧

  refs[0].get() = 10;  // 元の a が書き換わる
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
10 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 別のコンテナにある要素への参照を並べ替え用の一覧に集める | `std::vector<std::reference_wrapper<Enemy>>` |

## よくあるミス

??? failure "元の値より長生きさせる"
    ぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ref`](ref.md) | reference_wrapper を作る |
| ポインター | `nullptr` にできる。`reference_wrapper` は常に何かを指す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 参照をコピー・代入できる値にする
    - [x] `.get()` で取り出す
    - [x] 元より長生きさせない

## 関連ページ

- [cpprefjp: std::reference_wrapper](https://cpprefjp.github.io/reference/functional/reference_wrapper.html)
- [cppreference: std::reference_wrapper](https://en.cppreference.com/w/cpp/utility/functional/reference_wrapper)
