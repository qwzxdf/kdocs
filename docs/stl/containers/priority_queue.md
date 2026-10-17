---
title: std::priority_queue
tags:
  - コンテナ
---

# std::priority_queue

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <queue>`
</div>

`std::priority_queue` は、**いつでも「一番大きいもの」をすぐ取り出せる入れ物**です。入れた順番に関係なく、取り出すときは常に優先度が一番高い要素が出てきます。中は「ヒープ」というデータ構造で、追加と取り出しが O(log n) で済みます。

!!! tip "ポイント"
    - **A\* やダイクストラの経路探索、「次に処理すべきもの」を取り出す処理**に使う。
    - 使う関数は `push` / `top` / `pop` / `empty` の 4 つだけ。
    - デフォルトは**大きい順**。小さい順にしたいなら `std::greater<>` を指定する（経路探索はこっち）。
    - 中身を回したり、途中の要素を消したりはできない。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md)、[ラムダ式](../../basics/lambda.md)（比較関数で使う）が分かると読みやすいです。

## 宣言

```cpp
template <class T, class Container = std::vector<T>,
          class Compare = std::less<typename Container::value_type>>
class priority_queue;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `Container` | 中で使う入れ物 | **小さい順にしたいとき、3 つ目を書くために書く**（`std::vector<T>` のまま） |
| `Compare` | 優先度の比較 | 小さい順・自作の順にしたいとき |

!!! warning "`std::less` なのに大きい順"
    `Compare` が `std::less`（`<`）のとき、**一番大きいものが `top()` に来ます**。直感と逆なので注意します。小さいものを先に取り出すなら `std::greater<>` です。

## 関数一覧


| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push`](#push) | <span class="rank rank-must">必須</span> | 追加 | O(log n) |
| [`top`](#top) | <span class="rank rank-must">必須</span> | 一番優先度の高い要素を見る | O(1) |
| [`pop`](#pop) | <span class="rank rank-must">必須</span> | 一番優先度の高い要素を消す | O(log n) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空か | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して追加 | O(log n) |
| [`push_range`](#push_range) | <span class="rank rank-rare">知ってるだけ</span> | まとめて追加 <span class="ver ver-23">C++23</span> | O(m log n) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 交換 | O(1) |

## よくある使い方

### 1. 大きい順に取り出す

```cpp
#include <print>
#include <queue>

int main() {
  std::priority_queue<int> q;
  for (int x : {30, 10, 50, 20, 40}) {
    q.push(x);
  }

  while (!q.empty()) {
    std::print("{} ", q.top());
    q.pop();
  }
  std::println("");
}
```

```text title="実行結果"
50 40 30 20 10 
```

### 2. 小さい順に取り出す（経路探索の形）

```cpp
#include <functional>
#include <print>
#include <queue>
#include <utility>
#include <vector>

int main() {
  // (コスト, マス番号) を、コストの小さい順に取り出す
  using Node = std::pair<int, int>;
  std::priority_queue<Node, std::vector<Node>, std::greater<>> open;

  open.push({7, 3});
  open.push({2, 8});
  open.push({5, 1});

  while (!open.empty()) {
    auto [cost, cell] = open.top();
    open.pop();
    std::println("コスト {} のマス {}", cost, cell);
  }
}
```

```text title="実行結果"
コスト 2 のマス 8
コスト 5 のマス 1
コスト 7 のマス 3
```

`std::pair` は `first` → `second` の順に比べられるので、コストを `first` に置くとそのまま使えます。

### 3. 自作の順番で並べる

```cpp
#include <print>
#include <queue>
#include <string>
#include <vector>

struct Task {
  std::string name;
  int priority;
};

int main() {
  // true を返すと「a のほうが優先度が低い」という意味になる
  auto lower = [](const Task& a, const Task& b) { return a.priority < b.priority; };
  std::priority_queue<Task, std::vector<Task>, decltype(lower)> tasks(lower);

  tasks.push({"BGM 更新", 1});
  tasks.push({"当たり判定", 10});
  tasks.push({"UI 更新", 5});

  while (!tasks.empty()) {
    std::println("{}", tasks.top().name);
    tasks.pop();
  }
}
```

```text title="実行結果"
当たり判定
UI 更新
BGM 更新
```

## 関数の詳しい説明

### push {#push}

```cpp
void push(const T& value);
void push(T&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` / `T&&` | 追加する値 |

- 計算量: O(log n)（中の vector の末尾に足して、正しい位置まで上げる）

<div class="anim" data-label="pq.push(7)">
9 5 3 # 最大が先頭（ヒープ）
9 5 3 +7 # まず末尾に入れる
9 >7 3 >5 # 親（5）より大きいので上へ
</div>

```cpp
#include <print>
#include <queue>

int main() {
  std::priority_queue<int> q;
  q.push(3);
  q.push(9);
  q.push(5);
  std::println("一番大きいのは {}", q.top());
}
```

```text title="実行結果"
一番大きいのは 9
```

### top {#top}

```cpp
const T& top() const;
```

- 戻り値: 一番優先度の高い要素の **const 参照**（書き換えられない）
- 計算量: O(1)
- **空のとき未定義動作**

<div class="anim" data-label="pq.top()">
9 7 3 5 # pq
*9 7 3 5 # 一番大きい要素
</div>

### pop {#pop}

```cpp
void pop();
```

- 一番優先度の高い要素を消します。戻り値は**なし**。値が欲しいなら先に `top()` で取る
- 計算量: O(log n)
- **空のとき未定義動作**

<div class="anim" data-label="pq.pop()">
9 7 3 5 # 先頭が最大
x9 7 3 5 # 先頭（最大）を取り出す
>5 7 3 _ # 最後の要素を先頭へ
>7 >5 3 _ # 子より小さいので下へ。次の最大が先頭に
</div>

```cpp
#include <print>
#include <queue>

int main() {
  std::priority_queue<int> q;
  for (int x : {30, 10, 50}) {
    q.push(x);
  }
  while (!q.empty()) {
    int best = q.top();  // 先に取る
    q.pop();             // それから消す
    std::println("{}", best);
  }
}
```

```text title="実行結果"
50
30
10
```

### empty {#empty}

```cpp
bool empty() const;
```

- 空なら `true`。`top` / `pop` の前に必ず確認します

### size {#size}

```cpp
size_type size() const;
```

- 要素数

```cpp
#include <print>
#include <queue>

int main() {
  std::priority_queue<int> q;
  std::println("{} {}", q.empty(), q.size());
  q.push(1);
  q.push(2);
  std::println("{} {}", q.empty(), q.size());
}
```

```text title="実行結果"
true 0
false 2
```

### emplace {#emplace}

```cpp
template <class... Args>
void emplace(Args&&... args);
```

- 要素のコンストラクタ引数を渡して、その場で作って追加します

```cpp
#include <functional>
#include <print>
#include <queue>
#include <utility>
#include <vector>

int main() {
  using Node = std::pair<int, int>;  // (コスト, マス)
  std::priority_queue<Node, std::vector<Node>, std::greater<>> open;
  open.emplace(7, 3);  // Node(7, 3) をその場で作る
  open.emplace(2, 8);
  std::println("{}", open.top());
}
```

```text title="実行結果"
(2, 8)
```

### push_range <span class="ver ver-23">C++23</span> {#push_range data-toc-label="push_range"}

```cpp
template <container-compatible-range<T> R>
void push_range(R&& rg);
```

- 範囲の要素をまとめて追加します

### swap {#swap}

```cpp
void swap(priority_queue& other) noexcept;
```

- 中身を交換します

## フラグ・オプション

`Compare` で取り出す順番が決まります。

| 指定 | 重要度 | 取り出す順 | 使う場面 |
| --- | --- | --- | --- |
| `std::less<T>`（省略時） | <span class="rank rank-must">必須</span> | **大きい順** | スコアの高い順、優先度の高い順 |
| `std::greater<>` | <span class="rank rank-must">必須</span> | **小さい順** | 経路探索（コストの小さい順）、時刻の早い順 |
| ラムダ式 | <span class="rank rank-sometimes">たまに</span> | 自由 | 構造体のメンバで比べる |

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `top`, `empty`, `size` | O(1) |
| `push`, `pop` | O(log n) |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 経路探索 | A\*、ダイクストラの「次に調べるマス」 |
| イベントのスケジューリング | 発生時刻の早い順に処理 |
| AI の行動選択 | 評価値の高い行動から試す |
| 上位 N 件 | 小さい順の priority_queue に N 個だけ残す |

## パフォーマンス

- 中身は vector なので、メモリ確保は vector と同じく少なめです。
- 「優先度を後から変える」ことはできません。A\* では、同じマスを新しいコストでもう一度 `push` し、取り出したときに古いものを捨てる方法が定番です。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空で `top` / `pop` | 未定義動作 |
| 比較関数が矛盾している | 未定義動作 |

## よくあるミス

??? failure "小さい順のつもりで大きい順になっている"
    `std::priority_queue<int>` は大きい順です。経路探索で小さいコストから取り出したいなら `std::greater<>` を指定します。

??? failure "pop の戻り値を使おうとする"
    ```cpp
    int x = q.pop();  // コンパイルエラー: pop は何も返さない

    int x2 = q.top();  // OK: 先に取ってから
    q.pop();
    ```

??? failure "中身を回そうとする"
    `begin()` / `end()` が無いので範囲 for は使えません。全部見たいなら、コピーを作って `pop` しながら見るか、vector と `std::ranges::sort` で代用します。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    std::priority_queue<int, std::vector<int>, std::greater<>> q;
    q.push(5);
    q.push(1);
    q.push(3);
    std::println("{}", q.top());
    ```

    <div class="spoiler" markdown>

    **答え:** `1`。`std::greater<>` なので小さいものが先頭に来ます。

    </div>

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::queue`](queue.md) | 入れた順に出てくる | 先入れ先出し |
| [`std::set`](set.md) / `multiset` | 全要素が並んでいて、途中も消せる | 優先度を後から変えたい、中身を見たい |
| vector + `std::ranges::sort` | 一度に全部並べる | 全部入れ終わってから順番に処理する |

## コンパイラ対応

C++98 からある機能です。`push_range` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `push` / `top` / `pop` / `empty` の 4 つだけ
    - [x] デフォルトは大きい順。小さい順は `std::greater<>`
    - [x] `pop` は値を返さない。先に `top`
    - [x] 経路探索の定番

## 関連ページ

- [cpprefjp: std::priority_queue](https://cpprefjp.github.io/reference/queue/priority_queue.html)
- [cppreference: std::priority_queue](https://en.cppreference.com/w/cpp/container/priority_queue)
