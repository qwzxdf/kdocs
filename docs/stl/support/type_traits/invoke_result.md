---
title: std::invoke_result
summary: "関数を呼んだときの、戻り値の型を調べる。"
order: 20
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::invoke_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::invoke_result_t<F, Args...>` は、**関数 F を引数 Args... で呼んだときの、戻り値の型**を返します。テンプレートで、渡された関数の戻り値の型に合わせたコンテナや `future` を作るときに使います。

!!! tip "ポイント"
    - `std::invoke_result_t<decltype(f), int>` の形。
    - `std::async` や `std::packaged_task` の戻り値型を決めるのに使われている。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::invoke_result_t {#invoke_result}

```cpp
template <class F, class... Args>
using invoke_result_t = /* F(Args...) の戻り値の型 */;
```

- 関数を呼んだときの戻り値の型

```cpp
#include <cstdint>
#include <print>
#include <string>
#include <type_traits>

enum class Layer : std::uint8_t { kGround, kAir };

int main() {
  std::println("{}", std::is_same_v<std::remove_cvref_t<const std::string&>, std::string>);
  std::println("{}", std::is_same_v<std::underlying_type_t<Layer>, std::uint8_t>);
  std::println("{}", std::is_same_v<std::common_type_t<int, double>, double>);
  std::println("{}", std::is_same_v<std::conditional_t<(sizeof(void*) == 8), long long, int>,
                                    long long>);
  std::println("{}", std::is_same_v<std::make_unsigned_t<int>, unsigned int>);
  auto twice = [](int x) { return x * 2.0; };
  std::println("{}", std::is_same_v<std::invoke_result_t<decltype(twice), int>, double>);
  std::println("{}", std::is_same_v<std::decay_t<const int[3]>, const int*>);
}
```

```text title="実行結果（64 ビット環境）"
true
true
true
true
true
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ジョブの戻り値型に合わせた future を作る | `std::future<std::invoke_result_t<F>>` |

## よくあるミス

??? failure "古い result_of を使う"
    C++20 で削除されました。`invoke_result` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke`](../functional/invoke.md) | 実際に呼ぶ関数 |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 戻り値の型を調べる
    - [x] `result_of` の後継
    - [x] future の型に使う

## 関連ページ

- [cpprefjp: std::invoke_result](https://cpprefjp.github.io/reference/type_traits/invoke_result.html)
- [cppreference: std::invoke_result](https://en.cppreference.com/w/cpp/types/invoke_result)
