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

設定の読み込みやリソースの初期化を「最初に必要になったときに 1 回だけ」行いたい。複数のスレッドが同時に来ても、1 回だけ実行されなければ困ります。`std::call_once` と `std::once_flag` を組み合わせると、それが実現できます。`once_flag` は、「もう実行したか」を覚えておく旗です。コピーもムーブもできません。

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

シングルトンの遅延初期化に使います。リソースマネージャーを最初に使うときにだけ作る、といった場面です。複数のスレッドが同時に初めて呼んでも、初期化は 1 回だけです。

関数内の `static` 変数も、C++11 以降はスレッドセーフに 1 回だけ初期化されます。単純な場合は、`static` 変数のほうが簡単です。`once_flag` は、初期化の処理が複数の変数にまたがるときに使います。

## よくあるミス

??? failure "旗を毎回新しく作る"
    `once_flag` を関数の中のローカル変数にすると、毎回新しい旗になり、毎回実行されます。`static` かメンバにします。

??? failure "フラグをコピーしようとする"
    `once_flag` はコピーもムーブもできません。クラスのメンバーとして持つ場合、そのクラスもコピーできなくなります。

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
