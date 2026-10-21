---
title: std::chrono::high_resolution_clock
summary: "最も細かい時計（実体は環境しだい）。使わず steady_clock を使う。"
order: 5
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::high_resolution_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::chrono::high_resolution_clock` は、**その環境で一番細かい（精度の高い）時計**を表す名前です。ただし、実体は環境によって違い、GCC / Clang(libstdc++) では `system_clock`、MSVC では `steady_clock` の別名です。**巻き戻る環境がある**ので、使わずに [`steady_clock`](steady_clock.md) を使います。

!!! tip "ポイント"
    - **使わない。** 計測は [`steady_clock`](steady_clock.md)、日時は [`system_clock`](system_clock.md)。
    - 環境によって巻き戻る可能性がある（`is_steady` が `false`）。
    - 古いコードや、サンプルでよく出てくるので、読めるようにしておく。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### high_resolution_clock {#high_resolution_clock}

```cpp
struct high_resolution_clock;   // 実体は system_clock か steady_clock の別名
```

- 戻り値: `now()` で今の時点
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  // 環境によって結果が変わる
  std::println("steady？ {}", std::chrono::high_resolution_clock::is_steady);
}
```

```text title="実行結果"
（GCC では false、MSVC では true）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| サンプルコードにあるので読めるように | `steady_clock` に置き換えて読む |

## よくあるミス

??? failure "計測に使って、時刻の変更で壊れる"
    `high_resolution_clock` は巻き戻ることがあります。`steady_clock` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`steady_clock`](steady_clock.md) | 計測用。こちらを使う |
| [`system_clock`](system_clock.md) | 日時用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最も細かい時計の名前
    - [x] 実体は環境しだい
    - [x] 使わない。`steady_clock` を使う

## 関連ページ

- [cpprefjp: std::chrono::high_resolution_clock](https://cpprefjp.github.io/reference/chrono/high_resolution_clock.html)
- [cppreference: std::chrono::high_resolution_clock](https://en.cppreference.com/w/cpp/chrono/high_resolution_clock)
