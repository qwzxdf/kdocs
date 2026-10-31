---
title: std::this_thread::get_id
summary: "今のスレッドの ID を取得する。"
order: 78
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::get_id

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

ログに「どのスレッドから出力したか」を残したい。あるいは、「この関数は、メイン スレッドからしか呼べない」と検査したい。`std::this_thread::get_id()` は、呼び出したスレッドの ID を返します。スレッド ID は、`std::thread::id` 型で、比較と出力ができます。

!!! tip "ポイント"
    - 現在のスレッドの `std::thread::id` を返す
    - `==` で比べられる。順序の比較もできる
    - 整数ではない。数値としての意味は規定されていない
    - 別のスレッドの ID は `t.get_id()`

!!! info "このページを読む前に"
    [`std::thread`](../thread.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::get_id {#get_id}

<span class="ver ver-11">C++11</span>

```cpp
std::thread::id get_id() noexcept;
```

`std::thread::id` は、コピーでき、`==`、`<`、ハッシュ、`<<` による出力ができます。`std::format` で出すこともできます（C++23）。

スレッド ID は、スレッドが終了すると、別のスレッドに再利用されることがあります。ID を長期間覚えておいて、スレッドの同一性の判定に使うのは危険です。

「どのスレッドか」を、メイン スレッドの ID を保存しておいて比べる使い方が一般的です。

```cpp
const auto main_id = std::this_thread::get_id();   // main の冒頭で保存
void RequireMainThread() { assert(std::this_thread::get_id() == main_id); }
```

## 実際に動かしてみる

```cpp
#include <print>
#include <thread>

int main() {
  const auto main_id = std::this_thread::get_id();
  std::println("自分は main: {}", std::this_thread::get_id() == main_id);

  std::thread::id other;
  std::thread t([&] { other = std::this_thread::get_id(); });
  const auto t_id = t.get_id();
  t.join();

  std::println("別スレッドの ID は違う: {}", other != main_id);
  std::println("t.get_id() と一致: {}", other == t_id);
}
```

```text title="実行結果"
自分は main: true
別スレッドの ID は違う: true
t.get_id() と一致: true
```

## ゲームでの使いどころ

描画やファイル操作を「メイン スレッド限定」にする関数で、呼び出し元のスレッドを検査するのに使います。

## よくあるミス

??? failure "ID を整数として扱う"
    数値の意味は規定されていません。比較と出力だけにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`yield`](yield.md) | CPU を譲る |
| [`sleep_for`](sleep_for.md) | 一定時間眠る |
| [`thread`](../thread.md) | スレッド本体 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::this_thread::get_id](https://cpprefjp.github.io/reference/thread/this_thread/get_id.html)
- [cppreference: std::this_thread::get_id](https://en.cppreference.com/w/cpp/get_id)
