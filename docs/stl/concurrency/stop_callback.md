---
title: std::stop_callback
summary: "「止まって」の合図が来たときに、実行する処理を登録する。"
order: 74
tags:
  - 並行処理
---

# std::stop_callback

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <stop_token>`
</div>

`std::stop_callback` は、**`stop_token` に合図が来たときに、自動で実行される関数を登録する**クラスです。ブロック中のスレッドを起こして終了させる、といった「合図が来たらこうする」処理を書けます。スコープを抜けると登録が解除されます。

!!! tip "ポイント"
    - `std::stop_callback cb(token, 関数);` と作る。
    - 合図が来たスレッドで実行される（`request_stop()` を呼んだスレッド）。
    - 登録は、`stop_callback` が生きている間だけ有効。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::stop_callback {#stop_callback}

```cpp
template <class Callback>
class stop_callback {
 public:
  template <class C>
  explicit stop_callback(const stop_token& st, C&& cb);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `st` | `stop_token` | 監視する合図 |
| `cb` | 関数 | 合図が来たときに呼ばれる |

- 戻り値: （クラス）。破棄すると登録が解除される
- 計算量: O(1)

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source source;

  std::stop_callback cb(source.get_token(), [] { std::println("停止の合図を受け取った"); });
  source.request_stop();  // この呼び出しの中でコールバックが実行される
}
```

```text title="実行結果"
停止の合図を受け取った
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 条件変数で待っているスレッドを、停止の合図で起こす | コールバックの中で `notify_all()` |

## よくあるミス

??? failure "コールバックを変数に入れずに作る"
    名前のない一時オブジェクトだと、その行で登録が解除されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stop_token`](stop_token.md) | 合図を受け取る |
| [`std::condition_variable`](condition_variable.md) | 待っているスレッドを起こす |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合図が来たときに実行する関数を登録する
    - [x] 合図を出したスレッドで実行される
    - [x] 変数に入れて生かしておく

## 関連ページ

- [cpprefjp: std::stop_callback](https://cpprefjp.github.io/reference/stop_token/stop_callback.html)
- [cppreference: std::stop_callback](https://en.cppreference.com/w/cpp/thread/stop_callback)
