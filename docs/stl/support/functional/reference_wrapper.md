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

参照は、コンテナの要素にしたり、再代入したりできません。`std::vector<int&>` は作れません。`std::reference_wrapper<T>` は、<strong>参照のように振る舞うが、コピーも再代入もできるオブジェクト</strong>です。

!!! tip "ポイント"
    - `std::reference_wrapper<T>` は `T` への参照を保持するコピー可能なオブジェクト
    - `std::vector<std::reference_wrapper<T>>` のように、参照をコンテナに入れられる
    - `.get()` で参照を取り出し、`T&` に暗黙に変換できる
    - `std::ref` / `std::cref` で作る

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::reference_wrapper {#reference_wrapper}

<span class="ver ver-11">C++11</span>

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
| `ref` | `T&` | 保持する参照 |

内部ではポインターを持っていますが、参照のように使えます。コピーするとポインターがコピーされ、同じオブジェクトを指します。代入すると、指す先が変わります（通常の参照にはできない動作です）。

用途は、元のオブジェクトを並べ替える・分類するのに、コピーしたくない場合です。`vector<reference_wrapper<Enemy>>` を並べ替えても、元の `Enemy` の並びは変わりません。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  int a = 3, b = 1, c = 2;
  std::vector<std::reference_wrapper<int>> refs = {a, b, c};
  std::sort(refs.begin(), refs.end());           // 並べ替えても a, b, c の位置は変わらない
  refs[0].get() = 100;                           // 最小の b が書き換わる
  std::println("a={}, b={}, c={}", a, b, c);
}
```

```text title="実行結果"
a=3, b=100, c=2
```

## ゲームでの使いどころ

元のデータを動かさず、並べ替えた「ビュー」を作ります。

```cpp
std::vector<std::reference_wrapper<Enemy>> sorted(enemies.begin(), enemies.end());
std::sort(sorted.begin(), sorted.end(), ByDistance);
```

## よくあるミス

??? failure "参照先が先に破棄される"
    元のコンテナが生きている間だけ使います。

??? failure "一時オブジェクトの参照を持つ"
    禁止されています（コンパイルエラー）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ref`](ref.md) | 作成用の補助関数 |
| [`cref`](cref.md) | `const` 版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `reference_wrapper<T>` はコピー・再代入できる参照
    - [x] コンテナに参照を入れられる
    - [x] `.get()` か暗黙の変換で参照を取る

## 関連ページ

- [cpprefjp: std::reference_wrapper](https://cpprefjp.github.io/reference/functional/reference_wrapper.html)
- [cppreference: std::reference_wrapper](https://en.cppreference.com/w/cpp/utility/functional/reference_wrapper)
