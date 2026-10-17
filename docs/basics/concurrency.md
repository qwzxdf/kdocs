---
title: 並行処理の基本
tags:
  - 基礎
  - 並行処理
---

# 並行処理の基本

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
</div>

**並行処理**（マルチスレッド）は、**複数の処理を同時に進める**ことです。今の CPU には複数のコア（計算する部品）があるので、重い処理を別のスレッドに任せると、ゲームが止まらずに済みます。たとえば「ロード画面のアニメーションを動かしながら、裏でステージを読み込む」がそうです。ただし、**2 つのスレッドが同じデータを同時に触ると壊れる**（データ競争）ので、守り方を知っておく必要があります。

!!! tip "ポイント"
    - スレッドは [`std::jthread`](../stl/concurrency/thread.md) で作る（終わるのを自動で待ってくれる）。
    - **同じデータを複数のスレッドが触るなら、必ず守る**：[`std::mutex`](../stl/concurrency/mutex.md) でロックするか、[`std::atomic`](../stl/concurrency/atomic.md) を使う。
    - 「結果を 1 つ返すだけ」の処理なら [`std::async`](../stl/concurrency/future.md) が一番簡単。
    - ゲームの描画やゲームロジックは、基本的にメインスレッド 1 本で書く。別スレッドに出すのは**ロード・音声・重い計算**など切り離しやすいものだけ。
    - バグが再現しにくく難しいので、必要になるまで使わなくていい。

## 基本

### スレッドを作る

```cpp
#include <print>
#include <thread>

void LoadStage(int stage) {
  std::println("ステージ {} を読み込み中...", stage);
}

int main() {
  std::jthread loader(LoadStage, 3);  // 別のスレッドで LoadStage(3) が動き始める
  // ここでメインスレッドは別のことができる
}  // loader が消えるときに、終わるのを待つ（join）
```

```text title="実行結果"
ステージ 3 を読み込み中...
```

### データ競争（Data Race）

```cpp
int counter = 0;
// スレッド A: ++counter;   スレッド B: ++counter;
```

`++counter` は「読む → 1 足す → 書く」の 3 段階なので、2 つのスレッドが同時に行うと、片方の結果が上書きされて消えることがあります。これは**未定義動作**で、たまにしか起きないので見つけにくいバグになります。

<div class="mem">
<div class="mem-step"><span class="mem-label">スレッド A</span><span class="mem-note">counter を読む（0）→ 1 にする → 書く（1）</span></div>
<div class="mem-step"><span class="mem-label">スレッド B</span><span class="mem-note">　　counter を読む（0）→ 1 にする → 書く（1）</span></div>
<div class="mem-step"><span class="mem-label">結果</span><span class="mem-note">2 回足したのに 1 になる</span></div>
</div>

### 守り方

```cpp
#include <atomic>
#include <mutex>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> atomic_counter = 0;  // 方法 1: atomic（単純な数値ならこれ）

  int counter = 0;                      // 方法 2: mutex で守る
  std::mutex mutex;

  {
    std::vector<std::jthread> workers;
    for (int t = 0; t < 4; ++t) {
      workers.emplace_back([&] {
        for (int i = 0; i < 1000; ++i) {
          ++atomic_counter;
          std::lock_guard lock(mutex);  // この行から } まで、他のスレッドは入れない
          ++counter;
        }
      });
    }
  }  // 全員の終わりを待つ

  std::println("{} {}", atomic_counter.load(), counter);
}
```

```text title="実行結果"
4000 4000
```

## 詳しく

### 道具の使い分け

| やりたいこと | 道具 |
| --- | --- |
| 別のスレッドで処理を動かす | [`std::jthread`](../stl/concurrency/thread.md) |
| 処理を投げて、結果をあとで受け取る | [`std::async` / `std::future`](../stl/concurrency/future.md) |
| 1 つの数値・フラグを共有する | [`std::atomic`](../stl/concurrency/atomic.md) |
| 複数のデータをまとめて守る | [`std::mutex` + `std::lock_guard`](../stl/concurrency/mutex.md) |
| 「データが来るまで待つ」 | [`std::condition_variable`](../stl/concurrency/condition_variable.md) |
| 同時に動く数を制限する・全員がそろうのを待つ | [セマフォ・ラッチ・バリア](../stl/concurrency/semaphore.md) |
| スレッドに「止まって」と伝える | [`std::stop_token`](../stl/concurrency/thread.md#stop_token)（jthread と一緒に使う） |

### 気をつけること

| 問題 | 内容 | 防ぎ方 |
| --- | --- | --- |
| データ競争 | 同じデータを同時に書く | mutex / atomic |
| デッドロック | A を持って B を待つスレッドと、B を持って A を待つスレッドが永遠に待つ | 複数のロックは `std::scoped_lock` で一度に取る |
| 共有しすぎ | ロックだらけで結局 1 本ずつしか動かない | 共有するデータを減らす。各スレッドに自分の分を持たせ、最後にまとめる |
| UI・描画 API を別スレッドから呼ぶ | 多くのライブラリはメインスレッドからしか呼べない | 結果だけ受け取り、メインスレッドで反映する |

### ゲームでのよくある形

```text
メインスレッド:  入力 → 更新 → 描画 → 入力 → 更新 → 描画 → ...
ロードスレッド:     [ステージ読み込み..................] → 完了フラグ（atomic）
メインスレッド:  完了フラグを毎フレーム確認 → 読み込み済みならシーンを切り替える
```

## よくあるミス

??? failure "守らずに共有する"
    「たぶん大丈夫」で共有した変数が、数時間に 1 回だけ壊れる、というバグになります。共有するものは必ず守ります。

??? failure "std::thread の join を忘れる"
    `std::thread` は、join も detach もせずに消えるとプログラムが強制終了します。`std::jthread` を使えば自動で join されます。

??? failure "スレッドの中からメインの描画やエンジンの関数を呼ぶ"
    多くのグラフィック・ウィンドウの API はメインスレッド専用です。読み込んだデータだけを渡し、GPU への登録などはメインスレッドで行います。

## 理解度チェック

!!! question "Q1. ロード用のスレッドが「読み込み完了」を知らせるのに、普通の bool を使うとどうなる？"
    <div class="spoiler" markdown>

    **答え:** 片方が書き、もう片方が読むのでデータ競争（未定義動作）になります。最適化で「値が変わらない」とみなされ、いつまでも完了に気づかないこともあります。`std::atomic<bool>` を使います。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッドは jthread、結果を受け取るなら async
    - [x] 共有するデータは mutex か atomic で必ず守る
    - [x] ゲームのロジックと描画はメインスレッド。重い処理だけ外に出す

## 関連ページ

- [std::thread / std::jthread](../stl/concurrency/thread.md)
- [std::mutex](../stl/concurrency/mutex.md)
- [std::atomic](../stl/concurrency/atomic.md)
