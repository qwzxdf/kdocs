---
title: std::invoke
summary: "関数・メンバ関数・メンバ変数を、同じ書き方で呼び出す。"
order: 8
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::invoke

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::invoke` は、**関数、ラムダ、メンバ関数ポインター、メンバ変数ポインターを、すべて同じ書き方で呼び出す**関数です。`std::invoke(f, args...)` と書くと、`f` が何であっても呼べます。テンプレートで、渡された「呼べるもの」を呼ぶときに使います。

!!! tip "ポイント"
    - `std::invoke(&Enemy::Attack, enemy, 10)` のように、メンバ関数も呼べる。
    - `std::function` や `std::thread` の内部でも使われている。
    - 呼べるかの確認は `std::is_invocable`。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::invoke {#invoke}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... Args>
constexpr std::invoke_result_t<F, Args...> invoke(F&& f, Args&&... args);
```

- 普通の関数、ラムダ、**メンバ関数のポインタ**、**メンバ変数のポインタ**を、同じ書き方で呼びます。ranges のプロジェクション（`&Enemy::hp`）はこの仕組みで動いています

```cpp
#include <functional>
#include <print>

struct Enemy {
  int hp = 30;
  int Attack(int bonus) const { return 10 + bonus; }
};

int main() {
  Enemy e;
  std::println("{} {} {}", std::invoke(&Enemy::hp, e), std::invoke(&Enemy::Attack, e, 5),
               std::invoke(std::plus{}, 2, 3));
}
```

```text title="実行結果"
30 15 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 渡された「呼べるもの」を、型を気にせず呼ぶ（テンプレート） | `std::invoke(callback, args...)` |

## よくあるミス

??? failure "メンバ関数ポインターを f(obj) で呼ぼうとする"
    書き方が違います。`std::invoke(f, obj)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::apply`](../../utilities/apply.md) | tuple をばらして呼ぶ |
| [`mem_fn`](mem_fn.md) | メンバ関数ポインターを包む |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何でも同じ書き方で呼ぶ
    - [x] メンバ関数ポインターも呼べる
    - [x] テンプレートの部品

## 関連ページ

- [cpprefjp: std::invoke](https://cpprefjp.github.io/reference/functional/invoke.html)
- [cppreference: std::invoke](https://en.cppreference.com/w/cpp/utility/functional/invoke)
