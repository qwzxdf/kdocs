---
title: std::this_thread::sleep_for
summary: "今のスレッドを、指定した時間だけ止める。"
order: 75
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::sleep_for

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

`std::this_thread::sleep_for` は、**今のスレッドを指定した時間だけ止める**関数です。ワーカースレッドの待ち時間、リトライの間隔などに使います。**指定した時間より長く止まることがある**ので、正確なフレーム制御（60FPS の固定）には向きません。

!!! tip "ポイント"
    - `using namespace std::chrono_literals;` で `100ms` と書けて読みやすい。
    - 指定時間「以上」止まる。ぴったりにはならない。
    - 時刻で指定するなら [`sleep_until`](sleep_until.md)。

!!! info "このページを読む前に"
    [並行処理の基本](../../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::sleep_for {#sleep_for}

```cpp
template <class Rep, class Period>
void sleep_for(const std::chrono::duration<Rep, Period>& d);
```

- 今のスレッドを指定時間止めます。指定より長く止まることがあります

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <thread>

int main() {
  using namespace std::chrono_literals;
  auto start = std::chrono::steady_clock::now();
  std::this_thread::sleep_for(10ms);
  std::println("{}", std::chrono::steady_clock::now() - start >= 10ms);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロード完了までの待ちスレッドのポーリング間隔 | `std::this_thread::sleep_for(100ms);` |
| サーバーへの再接続の間隔 | リトライごとに `sleep_for` |

## よくあるミス

??? failure "メインスレッドで sleep_for してしまう"
    メインスレッド（描画・入力）を止めると、画面が固まります。待ちはワーカースレッドで行います。

??? failure "フレームレートの固定に使う"
    スリープの精度は OS しだいです。垂直同期（VSync）などで制御します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::this_thread::sleep_until`](sleep_until.md) | 時刻で指定 |
| [`std::this_thread::yield`](yield.md) | 順番を譲るだけ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今のスレッドを止める
    - [x] 指定時間「以上」止まる
    - [x] メインスレッドでは使わない

## 関連ページ

- [cpprefjp: std::this_thread::sleep_for](https://cpprefjp.github.io/reference/thread/this_thread/sleep_for.html)
- [cppreference: std::this_thread::sleep_for](https://en.cppreference.com/w/cpp/thread/sleep_for)
