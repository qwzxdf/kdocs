---
title: std::chrono::steady_clock
summary: "巻き戻らない時計。時間の計測に使う。"
order: 3
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::steady_clock

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

フレーム間の時間（デルタタイム）や、処理にかかった時間を測りたいとき、`time()` や `system_clock` を使うと、PC の時刻が変わった瞬間に計測値が負になったり、極端に大きくなったりします。`std::chrono::steady_clock` は、時間が巻き戻らないことが保証されている時計で、「経過した時間」を測るために作られています。

!!! tip "ポイント"
    - 経過時間の計測には必ず `steady_clock` を使う。`system_clock` は時刻の変更で巻き戻る。
    - 2 つの `now()` の差が `duration`（経過時間）になる。
    - 「今何時か」は分からない。基準になる時刻が定まっていない。

!!! info "このページを読む前に"
    [`std::chrono::duration`](duration.md) と [`time_point`](time_point.md) の関係を先に読んでください。時刻の差が時間の長さになる、という関係が前提です。

## 関数の詳しい説明

### steady_clock::now {#steady_clock}

```cpp
struct steady_clock {
  using time_point = std::chrono::time_point<steady_clock>;
  static constexpr bool is_steady = true;
  static time_point now() noexcept;
};
```

`now()` は、いまの時点を `time_point` で返します。この値そのものには意味がなく、基準（エポック）は実装次第です。PC の起動時刻かもしれませんし、別の値かもしれません。差を取ったときにだけ意味が出ます。

2 つの時点を引くと、`duration` が得られます。`end - start` の型は `steady_clock::duration` で、実装が決めた単位（Windows ではナノ秒、Linux でもナノ秒が多い）を持ちます。ミリ秒や秒として読みたいときは、`duration_cast` で変換するか、`duration<float>` に代入して小数の秒にします。

精度は実装によります。Windows の MSVC では `QueryPerformanceCounter` を使っており、100 ナノ秒程度の精度があります。

- 戻り値: 今の時点（`time_point`）
- 計算量: O(1)（1 回あたり数十ナノ秒）

```cpp
#include <chrono>
#include <print>

int main() {
  using Clock = std::chrono::steady_clock;

  auto start = Clock::now();
  auto end = Clock::now();
  std::println("巻き戻らない: {} / is_steady: {}", end >= start, Clock::is_steady);
}
```

```text title="実行結果"
巻き戻らない: true / is_steady: true
```

### フレーム時間の測り方 {#frame_time}

```cpp
// 毎フレームの先頭で
auto now = Clock::now();
std::chrono::duration<float> dt = now - last;   // 秒（小数）
last = now;
```

- 戻り値: 前のフレームからの経過時間（秒、小数）
- 計算量: O(1)

## しくみ

`system_clock` は「世の中の時刻」に合わせた時計です。NTP による調整、夏時間の切り替え、ユーザーが時計を変更する操作で、時間が巻き戻ることがあります。ゲームのフレーム時間を `system_clock` で測っていると、時計が巻き戻った瞬間に、デルタタイムが負の数になり、キャラクターが後ろへ動いたり、計算が壊れたりします。

`steady_clock` は、そのような補正を受けない、単調に増える時計です。ただし、スリープ中に止まるかは実装次第で、Linux の `CLOCK_MONOTONIC` はスリープ中に止まり、Windows の `QueryPerformanceCounter` は進み続けます。

`high_resolution_clock` という時計もありますが、実装によっては `system_clock` の別名で、巻き戻る可能性があります。計測には `steady_clock` を選ぶのが安全です。

### is_steady {#is_steady}

```cpp
static constexpr bool is_steady;
```

- 計算量: コンパイル時

巻き戻らず、一定の速さで進む時計なら `true`。`steady_clock` は常に `true` です。

## ゲームでの使いどころ

ゲームループのデルタタイムの計測が、代表的な使いどころです。

```cpp
auto prev = std::chrono::steady_clock::now();
while (running) {
  auto now = std::chrono::steady_clock::now();
  std::chrono::duration<float> dt = now - prev;  // 小数の秒
  prev = now;
  Update(dt.count());
}
```

処理時間の計測にも使います。重そうな処理の前後で `now()` を取り、差をログに出します。プロファイラーを使うほどではない簡単な計測や、リリースビルドで一時的に数字を見たいときに便利です。

タイムアウトの判定にも使います。「5 秒たったらロード失敗」のような場面で、開始時刻を覚えておき、`now() - start > 5s` を調べます。

## よくあるミス

??? failure "経過時間を `system_clock` で測る"
    時計の変更で巻き戻ると、差が負になります。デルタタイムで位置を更新していると、キャラクターが後ろへ戻ります。計測には `steady_clock` を使います。

??? failure "`time_point` の値そのものを表示して意味を考える"
    `steady_clock::now().time_since_epoch().count()` を表示しても、基準が不定なので意味のある時刻にはなりません。差を取ったときに意味が出ます。

??? failure "最初のフレームのデルタタイムが極端に大きい"
    ゲームループの前に `prev` を取り忘れると、最初のフレームの `dt` が不正な値になります。ループに入る直前に `prev = now()` を設定します。ウィンドウを動かしたあとにも、`dt` が極端に大きくなるので、上限（たとえば 0.1 秒）で切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 世の中の時刻。ログの日時など。巻き戻る可能性がある |
| [`high_resolution_clock`](high_resolution_clock.md) | 最も細かい時計。実装によっては `system_clock` の別名なので、計測には勧めない |
| [`duration_cast`](duration_cast.md) | 時間の長さの単位を変える |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 経過時間の計測は `steady_clock`。
    - [x] 差を取ってはじめて意味が出る。
    - [x] デルタタイムは上限を決めて使う。

## 関連ページ

- [cpprefjp: std::chrono::steady_clock](https://cpprefjp.github.io/reference/chrono/steady_clock.html)
- [cppreference: std::chrono::steady_clock](https://en.cppreference.com/w/cpp/chrono/steady_clock)
