---
title: std::move_only_function
summary: "ムーブだけできる関数を保持する（std::function のコピー不要版）。"
order: 45
tags:
  - ユーティリティ
---

# std::move_only_function

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-23">C++23</span>
`#include <functional>`
</div>

`std::move_only_function` は、**コピーできない（ムーブだけできる）関数オブジェクトを保持できる**、`std::function` の仲間です。`unique_ptr` や `packaged_task` をキャプチャしたラムダ式は、コピーできないので `std::function` には入りません。そのようなものをキューに積んで実行する、ジョブシステムで使います。

!!! tip "ポイント"
    - `std::function` はコピー可能なものしか入らない。こちらはムーブだけでよい。
    - 自身もコピーできない（ムーブのみ）。
    - `const` / `noexcept` 付きの呼び出しシグネチャを書ける（`void() const`）。

!!! info "このページを読む前に"
    [`std::function`](function.md) を先に読んでください。

## 関数の詳しい説明

### std::move_only_function {#move_only_function}

```cpp
template <class... Sig>
class move_only_function;   // Sig は R(Args...) の形
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能オブジェクト | 保持する関数（ムーブだけでよい） |

- 戻り値: `operator()` で保持した関数を呼ぶ
- 計算量: 呼び出しは O(1)

```cpp
#include <functional>
#include <memory>
#include <print>

int main() {
  auto value = std::make_unique<int>(42);

  // unique_ptr をキャプチャしたラムダはコピーできない → std::function には入らない
  std::move_only_function<void()> job = [v = std::move(value)] { std::println("{}", *v); };
  job();
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドプールのジョブキュー | `std::queue<std::move_only_function<void()>>` |

## よくあるミス

??? failure "コピーしようとする"
    コピーできません。`std::move` で移します。

??? failure "呼び出し中に自分を破棄する"
    実行中のオブジェクトを破棄すると未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::function`](function.md) | コピーできる関数だけ |
| [`std::packaged_task`](../concurrency/packaged_task.md) | future とセットの関数 |

## コンパイラ対応

C++23 の機能です。GCC 12 / MSVC 19.32 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ムーブだけできる関数を保持
    - [x] `std::function` はコピー必須
    - [x] C++23

## 関連ページ

- [cpprefjp: std::move_only_function](https://cpprefjp.github.io/reference/functional/move_only_function.html)
- [cppreference: std::move_only_function](https://en.cppreference.com/w/cpp/utility/functional/move_only_function)
