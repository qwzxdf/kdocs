---
title: std::stack
tags:
  - コンテナ
---

# std::stack

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <stack>`
</div>

`std::stack`（スタック）は、**最後に入れたものから順番に取り出す入れ物**です（後入れ先出し、LIFO）。お皿を積み重ねて、上から取っていくイメージです。中身は [`std::deque`](deque.md) で、「上に積む」「上から取る」以外の操作を取り除いたものです。

!!! tip "ポイント"
    - <strong>「直前の状態に戻る」ものに使う。</strong> アンドゥ、画面遷移の「戻る」、深さ優先探索。
    - 使う関数は `push` / `top` / `pop` / `empty` の 4 つだけ。
    - 実は `std::vector` の `push_back` / `back` / `pop_back` でも同じことができる。中身を見たいなら vector で書く。

## 宣言

```cpp
template <class T, class Container = std::deque<T>>
class stack;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `T` | 要素の型 | 必ず |
| `Container` | 中で使う入れ物 | `std::vector<T>` にすると少し速い（任意） |

<div class="mem">
<div class="mem-step"><span class="mem-label">push(D)</span><span class="mem-cells"><span>A</span><span>B</span><span>C</span><span class="new">D</span></span><span class="mem-note">上（右端）に積む</span></div>
<div class="mem-step"><span class="mem-label">pop()</span><span class="mem-cells"><span>A</span><span>B</span><span>C</span><span class="gone">D</span></span><span class="mem-note">上（top）から取る。最後に入れた D が出ていく</span></div>
</div>

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push`](#push) | <span class="rank rank-must">必須</span> | 上に積む | O(1) |
| [`top`](#top) | <span class="rank rank-must">必須</span> | 一番上を見る（書き換えも可） | O(1) |
| [`pop`](#pop) | <span class="rank rank-must">必須</span> | 一番上を消す（値は返さない） | O(1) |
| [`empty`](#empty) | <span class="rank rank-must">必須</span> | 空か | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して積む | O(1) |
| [`push_range`](#push_range) | <span class="rank rank-rare">知ってるだけ</span> | まとめて積む <span class="ver ver-23">C++23</span> | O(m) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 交換 | O(1) |

## よくある使い方

### 1. 画面遷移の「戻る」

```cpp
#include <print>
#include <stack>
#include <string>

int main() {
  std::stack<std::string> scenes;
  scenes.push("タイトル");
  scenes.push("メニュー");
  scenes.push("設定");
  std::println("今: {}", scenes.top());

  scenes.pop();  // 戻るボタン
  std::println("今: {}", scenes.top());
}
```

```text title="実行結果"
今: 設定
今: メニュー
```

### 2. アンドゥ

```cpp
#include <print>
#include <stack>

int main() {
  int x = 0;
  std::stack<int> history;  // 変更前の値を積んでいく

  for (int next : {5, 8, 2}) {
    history.push(x);
    x = next;
  }
  std::println("今: {}", x);

  // 2 回アンドゥ
  for (int i = 0; i < 2 && !history.empty(); ++i) {
    x = history.top();
    history.pop();
  }
  std::println("アンドゥ後: {}", x);
}
```

```text title="実行結果"
今: 2
アンドゥ後: 5
```

## 関数の詳しい説明

### push {#push}

```cpp
void push(const T& value);
void push(T&& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const T&` / `T&&` | 一番上に積む値 |

- 計算量: O(1)

<div class="anim" data-label="s.push(4)">
1 2 3 # 底 1 … 上 3
1 2 3 +4 # 上に積む
</div>

### top {#top}

```cpp
reference top();
const_reference top() const;
```

- 戻り値: 一番上（最後に積んだ要素）の参照。書き換えもできる
- **空のとき未定義動作**

<div class="anim" data-label="s.top()">
1 2 3 # s
1 2 *3 # 一番上の要素
</div>

### pop {#pop}

```cpp
void pop();
```

- 一番上を消します。戻り値は**なし**。値が欲しいなら先に `top()` で取る
- **空のとき未定義動作**

<div class="anim" data-label="s.pop()">
1 2 3 4 # 底 1 … 上 4
1 2 3 x4 # 上から取る（後に入ったものが先）
1 2 3 # 完了
</div>

```cpp
#include <print>
#include <stack>

int main() {
  std::stack<int> s;
  s.push(1);
  s.push(2);
  s.top() = 20;  // 一番上を書き換える
  std::println("一番上: {}", s.top());
  s.pop();
  std::println("一番上: {}", s.top());
}
```

```text title="実行結果"
一番上: 20
一番上: 1
```

### empty {#empty}

```cpp
bool empty() const;
```

- 空なら `true`。`top` / `pop` の前に確認します

### size {#size}

```cpp
size_type size() const;
```

- 要素数

```cpp
#include <print>
#include <stack>
#include <string>

int main() {
  std::stack<std::string> menus;
  menus.push("ポーズ");
  menus.push("設定");
  std::println("{} 枚開いている", menus.size());
  while (!menus.empty()) {
    std::println("閉じる: {}", menus.top());
    menus.pop();
  }
}
```

```text title="実行結果"
2 枚開いている
閉じる: 設定
閉じる: ポーズ
```

### emplace {#emplace}

```cpp
template <class... Args>
decltype(auto) emplace(Args&&... args);
```

- 要素のコンストラクタ引数を渡して、その場で作って積みます

### push_range <span class="ver ver-23">C++23</span> {#push_range data-toc-label="push_range"}

```cpp
template <container-compatible-range<T> R>
void push_range(R&& rg);
```

- 範囲の要素を順番に積みます（最後の要素が一番上になる）

### swap {#swap}

```cpp
void swap(stack& other) noexcept;
```

- 中身を交換します

## フラグ・オプション

フラグはありません。

## 計算量まとめ

すべての操作が O(1) です。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 画面・シーンの管理 | ポーズメニューを上に積む、閉じたら下の画面に戻る |
| アンドゥ | エディタやパズルの「一手戻す」 |
| 深さ優先探索 | 迷路生成、塗りつぶし |
| 状態の入れ子 | ステートマシンの「割り込み状態」 |

## パフォーマンス

デフォルトでは deque を使っていますが、`std::stack<T, std::vector<T>>` にすると、メモリが 1 本に並ぶぶん少し速くなります。

## よくあるミス

??? failure "空なのに top を呼ぶ"
    ```cpp
    scenes.pop();
    std::println("{}", scenes.top());  // 最後の 1 個を消した後だと未定義動作

    if (!scenes.empty()) {
      std::println("{}", scenes.top());  // OK
    }
    ```

??? failure "中身を全部表示しようとする"
    stack は一番上しか見られません。デバッグ表示などで中身も見たいなら、最初から `std::vector` を使って `push_back` / `back` / `pop_back` で書きます。

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::queue`](queue.md) | 先に入れたものから出る | 来た順に処理する |
| [`std::vector`](vector.md) | `push_back` / `back` / `pop_back` で同じことができる | 中身も見たいとき |

## コンパイラ対応

C++98 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最後に入れたものから出る（LIFO）
    - [x] `push` / `top` / `pop` / `empty` の 4 つだけ
    - [x] 中身を見たいなら vector で代用する

## 関連ページ

- [cpprefjp: std::stack](https://cpprefjp.github.io/reference/stack/stack.html)
- [cppreference: std::stack](https://en.cppreference.com/w/cpp/container/stack)
