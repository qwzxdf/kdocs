---
title: std::function_ref
summary: "呼び出せるものを借りて参照するだけの、軽い関数ラッパー。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::function_ref

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <functional>`
</div>

関数の引数でコールバックを受けるとき、`std::function` だと、中の関数オブジェクトをコピーして保持するので、コピーのコストや、ヒープ確保が気になります。呼び出している間だけ使えれば十分なら、持ち主にならず、借りるだけの `std::function_ref` が軽く済みます。

!!! tip "ポイント"
    - 呼び出せるものを、コピーせずに参照するだけ（持ち主にならない）
    - ヒープ確保が起きず、サイズはポインター 2 つ分
    - 借りているものが消えると、呼び出しは未定義動作
    - 関数の引数に使う。メンバー変数に保存するのは危険

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::function_ref {#function_ref}

<span class="ver ver-26">C++26</span>

```cpp
template <class... Signature>
class function_ref;

// Signature の例: R(Args...)、R(Args...) const、R(Args...) noexcept
```

| 引数 | 意味 |
| --- | --- |
| `R(Args...)` | 呼び出しの形（戻り値と引数）。`const` や `noexcept` を付けられる |

`std::function` との違いは、持ち主にならないことです。`std::function` は、渡された関数オブジェクトを自分の中にコピー（またはムーブ）して保存します。`function_ref` は、元の関数オブジェクトへのポインターと、呼び出し用の関数ポインターを持つだけです。コピーも、ヒープ確保もありません。

ラムダを直接渡すと、一時オブジェクトが関数の呼び出しの間だけ生きるので、安全に使えます。

```cpp
void Each(std::function_ref<void(int)> f);
Each([&](int x) { sum += x; });   // 安全。呼び出しの間だけ使う
```

一方、`function_ref` を変数やメンバーに保存して、あとで呼ぶと、元のラムダが消えているかもしれません。一時オブジェクトから作った `function_ref` を保存するのは、典型的なミスです。

呼び出しは、間接呼び出し 1 回で済みます。`std::function` が内部でする、仮想関数に近い呼び出しと、同じ程度のコストです。

関数ポインターを渡すと、関数ポインターそのものを格納します（関数ポインターは、小さいので問題ありません）。

## 使い方の形

```cpp
#include <functional>
#include <print>

// 呼び出している間だけ使うコールバック
void ForEachEnemy(int count, std::function_ref<void(int)> f) {
  for (int i = 0; i < count; ++i) f(i);
}

int main() {
  int damage_total = 0;
  ForEachEnemy(3, [&](int id) { damage_total += (id + 1) * 10; });
  std::println("合計ダメージ: {}", damage_total);

  // 通常の関数も渡せる
  ForEachEnemy(2, [](int id) { std::println("敵 {}", id); });
}
```


## ゲームでの使いどころ

「全部の敵に対して、これを実行する」のような、呼び出している間だけ使うコールバックの引数に使います。`std::function` よりも軽くなります。

## よくあるミス

??? failure "function_ref を保存して、あとで呼ぶ"
    元のラムダが消えたあとに呼ぶと、未定義動作です。保存するなら `std::function` か `std::move_only_function` を使います。

??? failure "一時オブジェクトから作って、変数に入れる"
    `std::function_ref<void()> f = []{ ... };` のように変数に入れると、一時オブジェクトがすぐ消えます。引数で受けるときだけ安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copyable_function`](copyable_function.md) | 持ち主になるコピー可能な版 |
| [`std::function`](../../utilities/function.md) | 持ち主になる従来の版 |
| [`ref`](ref.md) | 参照ラッパー |

## コンパイラ対応

C++26 です。手元の MSVC（Visual Studio 2026）では、まだ `std::function_ref` が無く、コンパイルできませんでした。そのため、このページのサンプルは動かして確かめていません。使えるようになったら、実行結果を確かめて書き足します。

## 関連ページ

- [cpprefjp: std::function_ref](https://cpprefjp.github.io/reference/functional/function_ref.html)
- [cppreference: std::function_ref](https://en.cppreference.com/w/cpp/utility/functional/function_ref)
