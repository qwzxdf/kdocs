---
title: std::once_flag
summary: "call_once で「1 回だけ実行」を管理するための旗。"
order: 900
tags:
  - 並行処理
---

# std::once_flag

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

初期化処理を「最初に必要になったときに 1 回だけ」行いたいとき、複数のスレッドが同時に来ても 1 回だけ実行されるようにするには、`once_flag` と `call_once` を組み合わせます。`once_flag` は、「もう実行したか」を覚えておく旗です。

!!! tip "ポイント"
    - `std::call_once(flag, 関数)` に渡して使う。
    - コピー・ムーブできない。
    - スレッドセーフな遅延初期化に使う。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::once_flag {#once_flag}

```cpp
struct once_flag {
  constexpr once_flag() noexcept;
  once_flag(const once_flag&) = delete;
  once_flag& operator=(const once_flag&) = delete;
};
```

- 戻り値: なし（旗）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::once_flag flag;
  for (int i = 0; i < 3; ++i) {
    std::call_once(flag, [] { std::println("once"); });
  }
}
```

```text title="実行結果"
once
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 最初に使うときだけ設定ファイルを読む | `std::call_once(flag, LoadConfig);` |

## よくあるミス

??? failure "旗を毎回新しく作る"
    `once_flag` を関数の中のローカル変数にすると、毎回新しい旗になり、毎回実行されます。`static` かメンバにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`call_once`](call_once.md) | 1 回だけ実行する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「1 回だけ」の旗
    - [x] call_once と組み合わせる
    - [x] static かメンバにする

## 関連ページ

- [cpprefjp: std::once_flag](https://cpprefjp.github.io/reference/mutex/once_flag.html)
- [cppreference: std::once_flag](https://en.cppreference.com/w/cpp/thread/once_flag)
