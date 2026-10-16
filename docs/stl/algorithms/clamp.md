---
title: std::clamp
tags:
  - アルゴリズム
---

# std::clamp

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <algorithm>`
</div>

`std::clamp` は、**値を「下限〜上限」の範囲に収める**関数です。下限より小さければ下限を、上限より大きければ上限を、範囲内ならそのままの値を返します。`std::min(std::max(x, lo), hi)` と同じ意味ですが、ずっと読みやすく書けます。

!!! tip "結論"
    - HP、音量、カメラ位置、スティック入力など、**範囲に収めたい値は全部これ**。
    - 書き方は `std::clamp(値, 下限, 上限)`。3 つとも同じ型にする。
    - **下限 > 上限だと未定義動作**。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::clamp`](#clamp) | <span class="rank rank-often">よく使う</span> | 値を範囲に収める | O(1) |
| [`std::ranges::clamp`](#ranges-clamp) | <span class="rank rank-rare">知ってるだけ</span> | プロジェクション付き版 <span class="ver ver-20">C++20</span> | O(1) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>

int main() {
  int hp = 130;
  hp = std::clamp(hp, 0, 100);
  std::println("HP {}", hp);

  float volume = -0.2f;
  volume = std::clamp(volume, 0.0f, 1.0f);
  std::println("音量 {}", volume);

  float camera_x = 50.0f;
  std::println("カメラ {}", std::clamp(camera_x, 0.0f, 640.0f));
}
```

```text title="実行結果"
HP 100
音量 0
カメラ 50
```

## 関数の詳しい説明

### std::clamp {#clamp}

```cpp
template <class T>
constexpr const T& clamp(const T& v, const T& lo, const T& hi);
template <class T, class Compare>
constexpr const T& clamp(const T& v, const T& lo, const T& hi, Compare comp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `v` | `const T&` | 収めたい値 |
| `lo` | `const T&` | 下限 |
| `hi` | `const T&` | 上限。**`lo <= hi` である必要がある** |
| `comp` | 比較関数 | 大小の決め方（ほぼ使わない） |

- 戻り値: `v < lo` なら `lo`、`hi < v` なら `hi`、それ以外は `v`。**参照**を返す
- 計算量: O(1)

```cpp
#include <algorithm>
#include <print>

int main() {
  for (int x : {-5, 3, 12}) {
    std::println("{} → {}", x, std::clamp(x, 0, 10));
  }
}
```

```text title="実行結果"
-5 → 0
3 → 3
12 → 10
```

!!! note "実際は"
    参照を返すので、`const int& r = std::clamp(x + 1, 0, 10);` のように一時的な値を渡して参照で受けると壊れます。普通に `int r = ...` で受ければ問題ありません。

### std::ranges::clamp <span class="ver ver-20">C++20</span> {#ranges-clamp data-toc-label="std::ranges::clamp"}

```cpp
template <class T, class Proj = identity, class Comp = ranges::less>
constexpr const T& clamp(const T& v, const T& lo, const T& hi, Comp comp = {}, Proj proj = {});
```

- プロジェクションを指定できる版です。普段は `std::clamp` で足ります

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    if (hp < 0) hp = 0;
    if (hp > 100) hp = 100;

    hp = std::min(std::max(hp, 0), 100);
    ```

=== "今の書き方（C++17）"

    ```cpp
    hp = std::clamp(hp, 0, 100);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ステータス | `std::clamp(hp, 0, max_hp)` |
| 音量・明るさ | `std::clamp(volume, 0.0f, 1.0f)` |
| カメラ | マップの端からはみ出さないように位置を収める |
| 入力 | スティックの値を -1〜1 に収める |
| 色 | 0〜255 に収める |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `lo > hi` | 未定義動作 |
| 戻り値の参照を、一時的な値を渡したのに保存する | 未定義動作 |

## よくあるミス

??? failure "引数の順番を間違える"
    `std::clamp(0, hp, 100)` だと「0 を hp〜100 に収める」になってしまいます。最初の引数が「収めたい値」です。

??? failure "マップが画面より小さくて lo > hi になる"
    カメラの位置を `std::clamp(x, 0.0f, map_width - screen_width)` で収めると、マップが画面より狭いときに上限がマイナスになり、未定義動作になります。先に上限を `std::max(0.0f, ...)` しておきます。

## 理解度チェック

!!! question "Q1. `std::clamp(15, 0, 10)` と `std::clamp(-3, 0, 10)` は？"
    <div class="spoiler" markdown>

    **答え:** `10` と `0`。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::min` / `std::max`](min_max.md) | 片側だけ制限する |

## コンパイラ対応

C++17 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::clamp(値, 下限, 上限)`
    - [x] 下限 > 上限にしない

## 関連ページ

- [cpprefjp: std::clamp](https://cpprefjp.github.io/reference/algorithm/clamp.html)
- [cppreference: std::clamp](https://en.cppreference.com/w/cpp/algorithm/clamp)
