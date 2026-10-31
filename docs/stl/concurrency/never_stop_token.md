---
title: std::never_stop_token
summary: "停止が絶対に要求されない stop_token。"
order: 900
tags:
  - 並行処理
---

# std::never_stop_token

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <stop_token>`
</div>

`std::stop_token` を受け取る関数を、停止を考えない場面でも使いたい。そのために本物の `stop_source` を作るのは無駄です。`std::never_stop_token` は、<strong>絶対に停止しない</strong>ことが型で分かる `stop_token` 風の型で、停止の判定が、常に偽になるように最適化されます。C++26 の機能です。

!!! tip "ポイント"
    - `stop_possible()` が常に `false`、`stop_requested()` が常に `false`
    - `stop_token` と同じ使い方ができるが、型が別
    - テンプレートの引数に使うと、停止の分岐がコンパイル時に消える
    - C++26。手元の MSVC は未対応

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::never_stop_token {#never_stop_token}

<span class="ver ver-26">C++26</span>

```cpp
class never_stop_token {
 public:
  static constexpr bool stop_requested() noexcept { return false; }
  static constexpr bool stop_possible() noexcept { return false; }
  template <class> struct callback_type { callback_type(never_stop_token, auto&&) noexcept {} };
};
```

`stoppable_token` コンセプトを満たします。停止の判定が `constexpr` で常に偽なので、テンプレートが、停止に関するコードを丸ごと取り除けます。

`std::stop_token` を受け取るテンプレート関数に、停止を考えない呼び出し側が、`never_stop_token{}` を渡す、という使い方をします。

```cpp
template <std::stoppable_token Token>
void Work(Token token) {
  while (!token.stop_requested()) { /* ... */ }
}
Work(std::never_stop_token{});   // 停止の判定が消える
```

C++26 の機能で、手元の MSVC（Visual Studio 2026）では、まだ使えません。

## 使い方の形

```cpp
#include <stop_token>

// 停止の要求を見るテンプレート
template <std::stoppable_token Token>
int CountUntilStop(Token token, int limit) {
  int n = 0;
  while (!token.stop_requested() && n < limit) ++n;
  return n;
}

// C++26 の環境では、停止しないトークンを渡せる:
//   CountUntilStop(std::never_stop_token{}, 100);
// 通常の stop_token は:
//   CountUntilStop(std::stop_source{}.get_token(), 100);
```

手元の MSVC では `never_stop_token` を使えないので、動かさずに、使い方の形だけを示します。

## ゲームでの使いどころ

停止を考えない呼び出し側と、停止を考える呼び出し側で、同じテンプレート関数を使い回します。

## よくあるミス

??? failure "C++23 以前の環境で使う"
    未対応です。`stop_source` のトークンで代用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stop_token`](stop_token.md) | 通常のトークン |
| [`nostopstate`](nostopstate.md) | 状態を持たない `stop_source` |
| [`stop_source`](stop_source.md) | 要求を出す側 |

## コンパイラ対応

C++26 から使えます。手元の MSVC では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::never_stop_token](https://cpprefjp.github.io/reference/stop_token/never_stop_token.html)
- [cppreference: std::never_stop_token](https://en.cppreference.com/w/cpp/thread/never_stop_token)
