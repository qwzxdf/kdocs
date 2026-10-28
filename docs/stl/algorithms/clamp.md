---
title: std::clamp
summary: "値を下限と上限の範囲内に収める（はみ出したら端の値にする）。"
order: 26
tags:
  - アルゴリズム
---

# std::clamp

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <algorithm>`
</div>

体力が 0 未満や最大値を超えないようにしたい、音量を 0〜1 に収めたい、カメラが範囲の外へ出ないようにしたい。ゲームには「値を範囲に収める」処理が山ほどあります。`std::min(std::max(x, lo), hi)` と書いても同じですが、入れ子になって読みにくくなります。`std::clamp` は、下限より小さければ下限、上限より大きければ上限、範囲内ならそのままの値を返す関数です。

!!! tip "ポイント"
    - HP、音量、カメラ位置、スティック入力など、**範囲に収めたい値は全部これ**。
    - 書き方は `std::clamp(値, 下限, 上限)`。3 つとも同じ型にする。
    - **下限 > 上限だと未定義動作**。

!!! info "このページを読む前に"
    [`std::min`](min.md) と [`std::max`](max.md) の組み合わせと同じ意味です。先にそちらを読んでおくと、`clamp` が何をしているかが分かります。

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

HP や音量、カメラ位置など、範囲に収めたい値のほとんどで使います。`hp = std::clamp(hp + heal, 0, max_hp)` と書けば、回復で最大値を超えず、ダメージで 0 を割りません。スティック入力の値を -1〜1 に収めたり、ズーム倍率に上限と下限を付けたりするのも同じ形です。

補間の `t` を 0〜1 に収める用途も定番です。`std::lerp(a, b, std::clamp(t, 0.0f, 1.0f))` と書くと、`t` が範囲外になっても行き過ぎません。

下限と上限を引数で受け取る関数を作るときは、`lo <= hi` を呼ぶ側が守るようにします。設定ファイルから読んだ値を渡すなら、読み込み時に確かめます。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| `lo > hi` | 未定義動作 |
| 戻り値の参照を一時的な値を渡したのに保存する | 未定義動作 |

## よくあるミス

??? failure "下限と上限を逆に渡す"
    `std::clamp(x, 10, 0)` は未定義動作です（`lo <= hi` が前提）。設定値などで逆転しうるときは、渡す前に `std::minmax` などで整えます。

??? failure "型が違う値を混ぜる"
    `std::clamp(f, 0, 1.0f)` のように、`float` と `int` を混ぜると、型が合わずコンパイルエラーになります。`0.0f` と `1.0f` のように、3 つとも同じ型にそろえます。

??? failure "戻り値が参照で、一時オブジェクトを受けてぶら下がる"
    `const auto& r = std::clamp(f(), lo, hi);` のように、一時的な値を渡して参照で受けると、行の終わりで消えた値を指します。`auto r = ...` と値で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::min`](min.md) | 上限だけを決める |
| [`std::max`](max.md) | 下限だけを決める |
| [`std::lerp`](../numeric/cmath/lerp.md) | 2 つの値の間を補間する。`t` の範囲を `clamp` で保証する |

## コンパイラ対応

C++17 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `clamp(値, 下限, 上限)` で範囲に収める。
    - [x] 下限が上限より大きいと未定義動作。
    - [x] 3 つとも同じ型にする。

## 関連ページ

- [cpprefjp: std::clamp](https://cpprefjp.github.io/reference/algorithm/clamp.html)
- [cppreference: std::clamp](https://en.cppreference.com/w/cpp/algorithm/clamp)
