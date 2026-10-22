---
title: std::invoke_r
summary: "呼び出しの結果を、指定した戻り値の型に変換して返す。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::invoke_r

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <functional>`
</div>

コールバックの戻り値を、決まった型として受け取りたいことがあります。`std::invoke` の結果を毎回 `static_cast` で包むかわりに、`invoke_r<R>` は戻り値を `R` へ暗黙変換して返します。`R` が `void` なら、結果を捨てます。

!!! tip "ポイント"
    - `invoke` と同じく、関数・メンバ関数・メンバ変数を同じ書き方で呼べる。
    - 戻り値の型を指定できる（`void` なら結果を捨てる）。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::invoke_r {#invoke_r}

```cpp
template <class R, class F, class... Args>
constexpr R invoke_r(F&& f, Args&&... args) noexcept(/* 呼び出しが noexcept なら */);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | テンプレート引数 | 戻り値の型 |
| `f` | 呼び出せるもの | 関数・ラムダ・メンバ関数ポインタなど |
| `args...` | 引数 | `f` に渡す引数 |

- 戻り値: `f(args...)` の結果を `R` に変換した値
- 計算量: 呼ぶ関数に依存


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  auto f = [](int a, int b) { return a + b; };
  double d = std::invoke_r<double>(f, 1, 2);
  std::println("{}", d);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コールバックの結果を `double` で受ける | `std::invoke_r<double>(callback, arg);` |

## よくあるミス

??? failure "変換できない型を指定する"
    戻り値が `R` に暗黙変換できないとコンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke`](invoke.md) | 戻り値の型はそのまま |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `invoke` の戻り値の型を指定する版
    - [x] `void` なら結果を捨てる
    - [x] 暗黙変換できる型だけ

## 関連ページ

- [cpprefjp: std::invoke_r](https://cpprefjp.github.io/reference/functional/invoke_r.html)
- [cppreference: std::invoke_r](https://en.cppreference.com/w/cpp/utility/functional/invoke)
