---
title: std::queue
summary: "先に入れたものを先に取り出す（先入れ先出し）。順番待ち・メッセージの受け渡しに。"
order: 10
tags:
  - コンテナ
---

# std::queue

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <queue>`
</div>

受け取ったイベントを、来た順に処理したい。マスを近い順に調べる幅優先探索をしたい。「先に入れたものを、先に取り出す」入れ物が必要です。`std::queue`（キュー）は、レジの行列のように、後ろに並んで前から出ていく入れ物です（先入れ先出し、FIFO）。中身は `std::deque` で、そこから「後ろに入れる」「前から出す」以外の操作を取り除いています。

!!! tip "ポイント"
    - <strong>「来た順に処理する」ものに使う。</strong> イベント、コマンド、幅優先探索。
    - 使う関数は `push` / `front` / `pop` / `empty` の 4 つだけ。
    - 中身を回したり、途中を見たりはできない。必要なら [`std::deque`](deque.md) を直接使う。

!!! info "このページを読む前に"
    [`std::deque`](deque.md) を知っていると、中身のイメージがつかみやすいです。

## 宣言

```cpp
template <class T, class Container = std::deque<T>>
class queue;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `Container` | 中で使う入れ物（`std::deque` か `std::list`） | しない |

<div class="mem">
<div class="mem-step"><span class="mem-label">push(D)</span><span class="mem-cells"><span class="move">A</span><span>B</span><span>C</span><span class="new">D</span></span><span class="mem-note">後ろに並ぶ</span></div>
<div class="mem-step"><span class="mem-label">pop()</span><span class="mem-cells"><span class="gone">A</span><span>B</span><span>C</span><span>D</span></span><span class="mem-note">前（front）から出ていく</span></div>
</div>

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push`](#push) | <span class="rank rank-must">必須</span> | 末尾に追加 | O(1) |
| [`front`](#front) | <span class="rank rank-must">必須</span> | 次に出てくる要素（先頭）を見る | O(1) |
| [`pop`](#pop) | <span class="rank rank-must">必須</span> | 先頭を消す（値は返さない） | O(1) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空か | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して末尾に追加 | O(1) |
| [`back`](#back) | <span class="rank rank-rare">知ってるだけ</span> | 最後に入れた要素を見る | O(1) |
| [`push_range`](#push_range) | <span class="rank rank-rare">知ってるだけ</span> | まとめて追加 <span class="ver ver-23">C++23</span> | O(m) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 交換 | O(1) |

## よくある使い方

### 1. イベントを来た順に処理する

```cpp
#include <print>
#include <queue>
#include <string>

int main() {
  std::queue<std::string> events;
  events.push("ドアが開いた");
  events.push("敵が出現");
  events.push("BGM 変更");

  // 1 フレームで溜まったイベントを全部処理する
  while (!events.empty()) {
    std::println("処理: {}", events.front());
    events.pop();
  }
}
```

```text title="実行結果"
処理: ドアが開いた
処理: 敵が出現
処理: BGM 変更
```

### 2. 幅優先探索で近い順にマスを調べる

```cpp
#include <array>
#include <print>
#include <queue>
#include <utility>

int main() {
  constexpr int kW = 5;
  constexpr int kH = 3;
  std::array<std::array<int, kW>, kH> dist{};
  for (auto& row : dist) {
    row.fill(-1);
  }

  std::queue<std::pair<int, int>> q;
  q.push({0, 0});
  dist[0][0] = 0;

  constexpr std::array<std::pair<int, int>, 4> kDirs = {
      {{1, 0}, {-1, 0}, {0, 1}, {0, -1}}};
  while (!q.empty()) {
    auto [x, y] = q.front();
    q.pop();
    for (auto [dx, dy] : kDirs) {
      int nx = x + dx;
      int ny = y + dy;
      if (nx < 0 || ny < 0 || nx >= kW || ny >= kH || dist[ny][nx] != -1) {
        continue;
      }
      dist[ny][nx] = dist[y][x] + 1;
      q.push({nx, ny});
    }
  }

  for (const auto& row : dist) {
    std::println("{}", row);
  }
}
```

```text title="実行結果"
[0, 1, 2, 3, 4]
[1, 2, 3, 4, 5]
[2, 3, 4, 5, 6]
```

## 関数の詳しい説明

### push {#push}

```cpp
void push(const T& value);
void push(T&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` / `T&&` | 末尾（列の最後）に並べる値 |

- 計算量: O(1)

<div class="anim" data-label="q.push(4)">
1 2 3 # 先頭 1 … 末尾 3
1 2 3 +4 # 後ろに入る
</div>

### front {#front}

```cpp
reference front();
const_reference front() const;
```

- 戻り値: 先頭（次に出てくる要素）の参照
- **空のとき未定義動作**

<div class="anim" data-label="q.front()">
1 2 3 # q
*1 2 3 # 次に出るもの
</div>

### pop {#pop}

```cpp
void pop();
```

- 先頭を消します。戻り値は**なし**。値が欲しいなら先に `front()` で取る
- **空のとき未定義動作**

<div class="anim" data-label="q.pop()">
1 2 3 4 # 先頭 1 … 末尾 4
x1 2 3 4 # 先頭から出る（先に入ったものが先）
2 3 4 # 完了
</div>

```cpp
#include <print>
#include <queue>

int main() {
  std::queue<int> q;
  q.push(1);
  q.push(2);
  q.push(3);
  int first = q.front();
  q.pop();
  std::println("出た: {} / 次: {}", first, q.front());
}
```

```text title="実行結果"
出た: 1 / 次: 2
```

### empty {#empty}

```cpp
bool empty() const;
```

- 空なら `true`。`front` / `pop` の前に確認します

### size {#size}

```cpp
size_type size() const;
```

- 要素数

```cpp
#include <print>
#include <queue>
#include <string>

int main() {
  std::queue<std::string> events;
  events.push("a");
  events.push("b");
  events.push("c");

  // このフレームでは「今あるぶん」だけ処理する
  std::size_t count = events.size();
  for (std::size_t i = 0; i < count; ++i) {
    std::println("処理: {}", events.front());
    events.pop();
    if (i == 0) {
      events.push("d");  // 処理中に増えたものは次のフレームへ
    }
  }
  std::println("残り: {} 個", events.size());
}
```

```text title="実行結果"
処理: a
処理: b
処理: c
残り: 1 個
```

### emplace {#emplace}

```cpp
template <class... Args>
decltype(auto) emplace(Args&&... args);
```

- 要素のコンストラクタ引数を渡して、末尾にその場で作ります

### back {#back}

```cpp
reference back();
```

- 最後に入れた要素の参照。空のとき未定義動作

<div class="anim" data-label="q.back()">
1 2 3 # q
1 2 *3 # 最後に入れたもの
</div>

```cpp
#include <print>
#include <queue>
#include <string>

int main() {
  std::queue<std::string> q;
  q.emplace(3, 'x');  // std::string(3, 'x')
  q.push("last");
  std::println("先頭 {} / 末尾 {}", q.front(), q.back());
}
```

```text title="実行結果"
先頭 xxx / 末尾 last
```

### push_range <span class="ver ver-23">C++23</span> {#push_range data-toc-label="push_range"}

```cpp
template <container-compatible-range<T> R>
void push_range(R&& rg);
```

- 範囲の要素をまとめて末尾に追加します

### swap {#swap}

```cpp
void swap(queue& other) noexcept;
```

- 中身を交換します

## フラグ・オプション

フラグはありません。

## 計算量まとめ

すべての操作が O(1) です。

### operator== {#op_eq}

```cpp
bool operator==(const queue& a, const queue& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const queue& a, const queue& b);
```

- 計算量: O(要素数)

要素を先頭から順に比べる、辞書順の三方比較。`<`・`>`・`<=`・`>=` も使えるようになります。

## ゲームでの使いどころ

イベントやコマンドを来た順に処理するのに使います。入力から受け取ったイベントを `push` し、ゲームループで `front` と `pop` で取り出して処理します。

幅優先探索（BFS）でも使います。スタート地点を入れて、取り出したマスの隣を順に入れていくと、近いマスから順に調べられます。迷路の最短経路や、敵からの距離の計算に使われます。

使う関数は、`push`、`front`、`pop`、`empty` の 4 つだけです。中身を回したり、途中を見たりはできません。必要なら `deque` を直接使います。

## パフォーマンス

- 中身は deque なので、追加・取り出しはどちらも O(1) です。
- 毎フレーム大量に出し入れするなら、`std::vector` を 2 本用意して「今フレーム用」と「次フレーム用」を `swap` する方法もよく使われます（再確保が起きにくい）。

## よくあるミス

??? failure "ループ中に push したものも同じフレームで処理してしまう"
    イベント処理の中で新しいイベントを `push` すると、`while (!q.empty())` が終わらなくなることがあります。「今あるぶんだけ処理する」なら、最初に `size()` を覚えてその回数だけ回します。

??? failure "pop の戻り値を使おうとする"
    `pop` は何も返しません。`front` で取ってから `pop` します。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::stack`](stack.md) | 後に入れたものから出る（後入れ先出し） | アンドゥ、深さ優先探索 |
| [`std::priority_queue`](priority_queue.md) | 優先度の高いものから出る | 経路探索、スケジューリング |
| [`std::deque`](deque.md) | 中身を見る・回すこともできる | queue の機能では足りないとき |

## コンパイラ対応

C++98 からある機能です。`push_range` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先に入れたものから出る（FIFO）
    - [x] `push` / `front` / `pop` / `empty` の 4 つだけ
    - [x] `pop` は値を返さない

## 関連ページ

- [cpprefjp: std::queue](https://cpprefjp.github.io/reference/queue/queue.html)
- [cppreference: std::queue](https://en.cppreference.com/w/cpp/container/queue)
