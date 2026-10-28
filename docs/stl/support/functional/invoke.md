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

関数、ラムダ、関数オブジェクト、メンバー関数ポインター、メンバー変数ポインターは、呼び方がそれぞれ違います（`f(x)`、`(obj.*pmf)(x)`、`obj.*pmd` など）。汎用のテンプレートでは、これらを全部同じ書き方で呼びたい。`std::invoke(f, 引数...)` は、<strong>呼び出し可能なものを、種類によらず同じ書き方で呼びます</strong>。

!!! tip "ポイント"
    - `std::invoke(f, args...)` は `f` の種類に合わせた書き方で呼ぶ
    - メンバー関数ポインターは、第 2 引数にオブジェクトを渡す
    - メンバー変数ポインターもアクセスできる
    - 汎用のコールバックを呼ぶテンプレートで使う

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::invoke {#invoke}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... Args>
constexpr std::invoke_result_t<F, Args...> invoke(F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能なもの | 関数、ラムダ、メンバーへのポインターなど |
| `args...` | 値 | 渡す引数（メンバーなら先頭がオブジェクト） |

`f` が通常の関数・ラムダ・関数オブジェクトなら `f(args...)` を呼びます。メンバー関数ポインターなら `(args0.*f)(args1...)` を、メンバー変数ポインターなら `args0.*f` を実行します。`args0` がポインターや `reference_wrapper` のときも、自動で `*` を付けて扱います。

汎用のコールバックを受け取る自作のテンプレートで、`f(args...)` と書く代わりに `std::invoke` を使うと、メンバー関数ポインターも渡せるようになります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

struct Player {
  int hp = 100;
  int Heal(int amount) { return hp += amount; }
};

int Add(int a, int b) { return a + b; }

int main() {
  Player p;
  std::println("関数          : {}", std::invoke(Add, 2, 3));
  std::println("メンバー関数  : {}", std::invoke(&Player::Heal, p, 20));
  std::println("メンバー変数  : {}", std::invoke(&Player::hp, p));
}
```

```text title="実行結果"
関数          : 5
メンバー関数  : 120
メンバー変数  : 120
```

## ゲームでの使いどころ

汎用のコールバックを呼ぶテンプレートで使います。

```cpp
template <class F, class... Args>
auto Call(F&& f, Args&&... args) {
  return std::invoke(std::forward<F>(f), std::forward<Args>(args)...);
}
```

## よくあるミス

??? failure "メンバー関数に `f(obj, ...)` と書いてコンパイルエラーになる"
    `std::invoke` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke_r`](invoke_r.md) | 戻り値の型を指定 |
| [`mem_fn`](mem_fn.md) | メンバーを関数オブジェクトにする |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::invoke` は呼び出し可能なものを種類によらず呼ぶ
    - [x] メンバーポインターも呼べる
    - [x] 汎用のテンプレートで使う

## 関連ページ

- [cpprefjp: std::invoke](https://cpprefjp.github.io/reference/functional/invoke.html)
- [cppreference: std::invoke](https://en.cppreference.com/w/cpp/utility/functional/invoke)
