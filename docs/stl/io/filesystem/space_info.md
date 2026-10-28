---
title: std::filesystem::space_info
summary: "ディスクの容量と空き容量を持つ構造体。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::space_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ディスクの空きを調べると、「全体で何バイト」「空きは何バイト」「自分が使えるのは何バイト」の 3 つの数字が欲しくなります。`std::filesystem::space_info` は、この 3 つをまとめて持つ小さな構造体です。[`space`](space.md) の戻り値として受け取ります。

!!! tip "ポイント"
    - メンバーは `capacity`、`free`、`available` の 3 つ。どれも `std::uintmax_t` のバイト数
    - 自分で作ることはほとんどない。`space` が返す値を読むための型
    - `capacity >= free >= available` が成り立つのがふつう
    - 値が `static_cast<std::uintmax_t>(-1)` のときは、取得できなかったという意味

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### space_info {#space_info}

<span class="ver ver-17">C++17</span>

```cpp
struct space_info {
  std::uintmax_t capacity;
  std::uintmax_t free;
  std::uintmax_t available;
};
```

| メンバー | 意味 |
| --- | --- |
| `capacity` | ボリュームの総容量（バイト） |
| `free` | ボリューム全体の空き（バイト） |
| `available` | 現在のプロセスが使える空き（バイト） |

`capacity` は、ボリュームの大きさです。500 GB の SSD なら、パーティションの大きさに近い値になります。`free` は、使われていない領域の合計で、管理者だけが使える予約領域も含みます。

`available` が実際に書き込める量です。ユーザーごとの容量制限があるときや、ファイルシステムが一部を予約しているときは、`free` より小さくなります。ゲームの保存判定は、この値で行います。

3 つとも<strong>バイト単位の符号なし整数</strong>なので、引き算で「使用中の量」を求めるときは、`capacity - free` の順に書きます。逆にすると、符号なしの引き算で巨大な値になります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::space_info info = fs::space(".");

  // 使用中の量は、capacity から free を引いて求める
  std::uintmax_t used = info.capacity - info.free;
  std::println("使用中 + 空き == 全体: {}", used + info.free == info.capacity);

  // 単位を GiB に直して表示する形（値はマシンによる）
  double gib = static_cast<double>(info.available) / (1024.0 * 1024.0 * 1024.0);
  std::println("使える空きが 0 GiB より大きい: {}", gib > 0.0);
}
```

```text title="実行結果"
使用中 + 空き == 全体: true
使える空きが 0 GiB より大きい: true
```

## ゲームでの使いどころ

設定画面や起動時のログに、ディスクの空きを表示するときに使います。バイト数のままでは読みにくいので、GiB や MiB に直して、小数 1 桁ほどで出します。

セーブ前の容量チェックでは、`available` を見ます。「使用中の量」を出したい（キャッシュ フォルダーの上限を、ボリュームの何割までにするか決めたい）ときは、`capacity - free` を使います。

## よくあるミス

??? failure "符号なしの引き算で、巨大な値になる"
    `info.free - info.capacity` のように大きいほうを後ろに書くと、マイナスにならず、2 の 64 乗に近い値になります。引く順番を確かめます。

??? failure "取得できなかった値を、そのまま容量として使う"
    ネットワーク ドライブなどでは、`-1` を `uintmax_t` にした最大値が入ることがあります。`available` が `static_cast<std::uintmax_t>(-1)` のときは、「不明」として扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`space`](space.md) | この構造体を返す関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `capacity`、`free`、`available` の 3 つ
    - [x] 保存の判定は `available`
    - [x] 全部バイト単位の符号なし整数

## 関連ページ

- [cpprefjp: std::filesystem::space_info](https://cpprefjp.github.io/reference/filesystem/space_info.html)
- [cppreference: std::filesystem::space_info](https://en.cppreference.com/w/cpp/filesystem/space_info)
