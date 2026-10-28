---
title: std::ref
summary: "値を参照のまま、関数やスレッドに渡す（reference_wrapper を作る）。"
order: 7
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::ref

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

`std::ref` は、**値を参照として、`std::thread` や `std::bind` などに渡す**ための関数です。これらは引数を**コピー**するので、参照で渡したいときは `std::ref(x)` で包みます。`std::cref` は `const` 参照版です。

!!! tip "ポイント"
    - `std::thread t(f, std::ref(x));` で、参照渡し。
    - 包んだ値は `reference_wrapper` になる。
    - 元の値より長く保持しない（ダングリング）。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::ref {#ref}

```cpp
template <class T>
std::reference_wrapper<T> ref(T& t) noexcept;
```

- 値渡しされる場所（スレッドの引数、`std::bind`、コンテナ）に**参照として**渡したいときに使います

```cpp
#include <functional>
#include <print>
#include <thread>
#include <vector>

void Fill(std::vector<int>& v) { v.assign(3, 7); }

int main() {
  std::vector<int> data;
  std::jthread(Fill, std::ref(data)).join();  // ref が無いとコピーが渡ってコンパイルエラー
  std::println("{}", data);
}
```

```text title="実行結果"
[7, 7, 7]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドに結果の書き込み先を渡す | `std::thread t(Work, std::ref(result));` |

## よくあるミス

??? failure "ref を付けずに参照を渡したつもり"
    コピーが渡されて、書き込みが元に反映されません。

??? failure "元の変数より長生きさせる"
    ぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reference_wrapper`](reference_wrapper.md) | 包む型 |
| [`std::jthread`](../../concurrency/jthread.md) | スレッドに渡す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値を参照のまま渡す
    - [x] thread / bind はコピーする
    - [x] 元より長生きさせない

## 関連ページ

- [cpprefjp: std::ref](https://cpprefjp.github.io/reference/functional/ref.html)
- [cppreference: std::ref](https://en.cppreference.com/w/cpp/utility/functional/ref)
