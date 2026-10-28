---
title: std::mdspan
summary: "1 次元の配列を 2 次元・3 次元として見る窓（コピーしない）。タイルマップや画像に。"
order: 14
tags:
  - コンテナ
---

# std::mdspan

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

タイルマップを 1 本の `vector` で持っていると、`tiles[y * width + x]` と、毎回添え字を計算することになります。幅を取り違えるミスもよく起きます。`std::mdspan` は、1 本に並んだ配列を多次元配列として見せる窓です。`grid[y, x]` と書けば、添え字の計算は、裏でやってくれます。`std::span` の多次元版で、中身は持たず、先頭のポインターと各次元の大きさだけを持ちます。

!!! tip "ポイント"
    - <strong>2 次元マップ・画像・行列を 1 本の vector で持つときに使う。</strong> 添字計算を書かなくて済む。
    - 書き方は `std::mdspan grid(v.data(), height, width);` → `grid[y, x]`。
    - 借りているだけなので、元の vector が再確保されると壊れる。
    - コンパイラ対応がまだ新しいので、使えなければ添字計算を手で書く。

!!! info "このページを読む前に"
    [`std::span`](span.md) と、[vector で 2 次元マップを持つ方法](vector.md#2-次元のマップは-1-本の-vector-で持つ) を先に読んでおくと分かりやすいです。

## 宣言

```cpp
template <class T, class Extents, class LayoutPolicy = std::layout_right,
          class AccessorPolicy = std::default_accessor<T>>
class mdspan;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 推論に任せることが多い |
| `Extents` | 各次元の大きさ（`std::extents` / `std::dextents`） | 推論に任せることが多い |
| `LayoutPolicy` | メモリ上の並べ方 | 列優先にしたいときだけ |
| `AccessorPolicy` | 要素の読み方 | しない |

### 作り方

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `std::mdspan grid(v.data(), h, w);` | <span class="rank rank-must">必須</span> | 高さ h × 幅 w の 2 次元として見る（大きさは実行時） |
| `std::mdspan<int, std::extents<std::size_t, 8, 8>> board(arr.data());` | <span class="rank rank-sometimes">たまに</span> | 大きさをコンパイル時に固定 |
| `std::mdspan<float, std::dextents<std::size_t, 3>> vol(p, d, h, w);` | <span class="rank rank-rare">知ってるだけ</span> | 3 次元 |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`operator[]`](#operator) | <span class="rank rank-must">必須</span> | 多次元の添字でアクセス <span class="ver ver-23">C++23</span> | O(1) |
| [`extent`](#extent) | <span class="rank rank-must">必須</span> | r 番目の次元の大きさ | O(1) |
| [`rank`](#rank) | <span class="rank rank-sometimes">たまに</span> | 次元数 | O(1) |
| [`size`](#size) | <span class="rank rank-sometimes">たまに</span> | 全要素数 | O(1) |
| [`data_handle`](#data_handle) | <span class="rank rank-sometimes">たまに</span> | 先頭のポインタ | O(1) |
| [`empty`](#empty) | <span class="rank rank-rare">知ってるだけ</span> | 要素数が 0 か | O(1) |
| [`stride`](#stride) | <span class="rank rank-rare">知ってるだけ</span> | r 番目の次元で 1 つ進むと何要素進むか | O(1) |
| [`extents`](#extents) | <span class="rank rank-rare">知ってるだけ</span> | 大きさの情報をまとめて取得 | O(1) |
| [`mapping`](#mapping) | <span class="rank rank-rare">知ってるだけ</span> | 添字 → 位置の変換ルールを取得 | O(1) |

`begin` / `end` は**ありません**。範囲 for で直接は回せないので、次元ごとに for を書きます。

## よくある使い方

### 1. 2 次元マップ

```cpp
#include <mdspan>
#include <print>
#include <vector>

int main() {
  constexpr std::size_t kWidth = 4;
  constexpr std::size_t kHeight = 3;
  std::vector<int> tiles(kWidth * kHeight, 0);

  // 高さ × 幅 の 2 次元として見る
  std::mdspan grid(tiles.data(), kHeight, kWidth);
  grid[1, 2] = 7;  // y = 1, x = 2

  for (std::size_t y = 0; y < grid.extent(0); ++y) {
    for (std::size_t x = 0; x < grid.extent(1); ++x) {
      std::print("{} ", grid[y, x]);
    }
    std::println("");
  }
  std::println("元の配列の添字 6: {}", tiles[6]);
}
```

```text title="実行結果"
0 0 0 0 
0 0 7 0 
0 0 0 0 
元の配列の添字 6: 7
```

`grid[1, 2]` は `tiles[1 * 4 + 2]` と同じ場所です。

## 関数の詳しい説明

### operator[] <span class="ver ver-23">C++23</span> {#operator data-toc-label="operator[]"}

```cpp
template <class... OtherIndexTypes>
constexpr reference operator[](OtherIndexTypes... indices) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `indices` | 整数を次元の数だけ | 各次元の添字。`grid[y, x]` のようにカンマで並べる |

- 戻り値: 要素の参照
- 範囲外は未定義動作

```cpp
#include <mdspan>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(6, 0);
  std::mdspan m(v.data(), 2, 3);  // 2 行 3 列
  m[1, 2] = 5;
  std::println("{}", v);  // 1 * 3 + 2 = 添字 5
}
```

```text title="実行結果"
[0, 0, 0, 0, 0, 5]
```

### extent {#extent}

```cpp
constexpr index_type extent(rank_type r) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `rank_type` | 何番目の次元か（0 始まり） |

- 戻り値: その次元の大きさ

```cpp
#include <mdspan>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(12);
  std::mdspan grid(v.data(), 3, 4);  // 高さ 3、幅 4
  std::println("高さ {} / 幅 {}", grid.extent(0), grid.extent(1));
}
```

```text title="実行結果"
高さ 3 / 幅 4
```

!!! note "実際は"
    ループの上限に使います。`grid.extent(0)` が y 方向、`grid.extent(1)` が x 方向です（作ったときの順番）。

### rank {#rank}

```cpp
static constexpr rank_type rank() noexcept;
```

- 次元数（2 次元なら 2）

### size {#size}

```cpp
constexpr size_type size() const noexcept;
```

- 全要素数（各次元の大きさの積）

```cpp
#include <mdspan>
#include <print>
#include <vector>

int main() {
  std::vector<float> voxels(2 * 3 * 4);
  std::mdspan vol(voxels.data(), 2, 3, 4);
  std::println("{} 次元 / {} 要素", vol.rank(), vol.size());
}
```

```text title="実行結果"
3 次元 / 24 要素
```

### data_handle {#data_handle}

```cpp
constexpr const data_handle_type& data_handle() const noexcept;
```

- 先頭のポインタ（作るときに渡したもの）

### empty {#empty}

```cpp
constexpr bool empty() const noexcept;
```

- どれかの次元の大きさが 0 なら `true`

### stride {#stride}

```cpp
constexpr index_type stride(rank_type r) const;
```

- r 番目の添字を 1 増やすと、元の配列で何要素ぶん進むか

```cpp
#include <mdspan>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(12);
  std::mdspan grid(v.data(), 3, 4);
  // y を 1 増やすと 4 要素進む、x を 1 増やすと 1 要素進む
  std::println("{} {}", grid.stride(0), grid.stride(1));
}
```

```text title="実行結果"
4 1
```

### extents {#extents}

```cpp
constexpr const extents_type& extents() const noexcept;
```

- 各次元の大きさをまとめた `std::extents` を返します。別の mdspan を同じ大きさで作るときに使います

### mapping {#mapping}

```cpp
constexpr const mapping_type& mapping() const noexcept;
```

- 「添字 → 元の配列の位置」の変換ルールを返します。`mapping()(y, x)` で元の配列の添字が計算できます

## フラグ・オプション

`LayoutPolicy` で「どの順番でメモリに並んでいるか」を指定します。

| 値 | 重要度 | 並び方 | 使う場面 |
| --- | --- | --- | --- |
| `std::layout_right`（省略時） | <span class="rank rank-must">必須</span> | **行優先**。一番右の添字が連続（C の配列と同じ） | 普通はこれ |
| `std::layout_left` | <span class="rank rank-sometimes">たまに</span> | **列優先**。一番左の添字が連続 | 列優先で並んだ行列（一部の数学ライブラリ、OpenGL の行列など） |
| `std::layout_stride` | <span class="rank rank-rare">知ってるだけ</span> | 各次元の間隔を自由に指定 | 大きい画像の一部分を切り出して見る |

<div class="mem">
<div class="mem-step"><span class="mem-label">layout_right（2×3）</span><span class="mem-cells"><span>0,0</span><span>0,1</span><span>0,2</span><span class="move">1,0</span><span class="move">1,1</span><span class="move">1,2</span></span><span class="mem-note">行ごとに並ぶ</span></div>
<div class="mem-step"><span class="mem-label">layout_left（2×3）</span><span class="mem-cells"><span>0,0</span><span class="move">1,0</span><span>0,1</span><span class="move">1,1</span><span>0,2</span><span class="move">1,2</span></span><span class="mem-note">列ごとに並ぶ</span></div>
</div>

### accessor {#accessor}

```cpp
const accessor_type& accessor() const noexcept;
```

- 計算量: 定数

要素へのアクセス方法（アクセサ）への参照。

### is_unique {#is_unique}

```cpp
constexpr bool is_unique() const;
```

- 計算量: 定数

異なる添字が異なる要素を指すなら `true`。重なりがないことを示します。

### is_exhaustive {#is_exhaustive}

```cpp
constexpr bool is_exhaustive() const;
```

- 計算量: 定数

すき間なく、全部の要素が連続して並ぶなら `true`。

### is_strided {#is_strided}

```cpp
constexpr bool is_strided() const;
```

- 計算量: 定数

各次元に一定のストライド（飛び幅）があれば `true`。

### swap {#swap}

```cpp
friend constexpr void swap(mdspan& x, mdspan& y) noexcept;
```

- 計算量: 定数

2 つの `mdspan` を入れ替えます。

### operator= {#op_assign}

```cpp
mdspan& operator=(const mdspan&) = default;
```

- 計算量: 定数

コピー代入。`mdspan` は軽い view なので、コピーはポインタなどのコピーです。

### rank_dynamic {#rank_dynamic}

```cpp
static constexpr rank_type rank_dynamic() noexcept;
```

- 計算量: 定数

動的な（実行時に決まる）次元の数。

### static_extent {#static_extent}

```cpp
static constexpr size_t static_extent(rank_type r) noexcept;
```

- 計算量: 定数

r 番目の次元の、コンパイル時の大きさ（動的なら `dynamic_extent`）。

## ゲームでの使いどころ

2 次元のタイルマップや画像、行列を 1 本の `vector` で持つときに使います。`std::mdspan grid(tiles.data(), height, width);` と作れば、`grid[y, x]` で読み書きできます。

3 次元のボクセル（ブロックの世界）にも使えます。`grid[z, y, x]` と書けます。並べ方（行優先か列優先か）は、レイアウト（`layout_right`、`layout_left`）で選べます。

借りているだけなので、元の `vector` が再確保されると壊れます。`[y, x]` という複数の添え字は C++23 の機能で、対応するコンパイラーが限られます。

## パフォーマンス

- 添字計算をしているだけなので、手で `y * width + x` と書くのと同じ速さです。
- 回すときは**一番右の添字を内側のループ**にすると、メモリを順番に読むので速くなります（`layout_right` の場合）。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 範囲外の添字 | 未定義動作 |
| 元の配列が再確保・破棄されたあとに使う | 未定義動作 |

## よくあるミス

??? failure "x と y の順番を逆にする"
    `std::mdspan grid(p, kHeight, kWidth)` と作ったら、`grid[y, x]` の順で書きます。`grid[x, y]` にすると範囲外になったり、縦横が入れ替わったりします。

??? failure "`grid[y][x]` と書く"
    mdspan は `grid[y, x]`（カンマ区切り）です。`grid[y][x]` はコンパイルエラーになります。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::span`](span.md) | 1 次元 | 普通の配列を借りる |
| `vector<vector<T>>` | 行ごとにメモリがバラバラ | 行ごとに長さが違うとき |
| 添字計算を手書き | `v[y * w + x]` | mdspan が使えないとき |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::mdspan` <span class="ver ver-23">C++23</span> | VS 2022 17.9〜 | 16〜 | 17〜 |
| 多次元の `operator[]`（`a[i, j]`） <span class="ver ver-23">C++23</span> | VS 2022 17.9〜 | 13〜（言語機能） | 15〜（言語機能） |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 本の配列を `grid[y, x]` で見られる
    - [x] 作るのは `std::mdspan grid(v.data(), height, width)`
    - [x] 借りているだけ。元の配列が伸びると壊れる

## 関連ページ

- [cpprefjp: std::mdspan](https://cpprefjp.github.io/reference/mdspan/mdspan.html)
- [cppreference: std::mdspan](https://en.cppreference.com/w/cpp/container/mdspan)
