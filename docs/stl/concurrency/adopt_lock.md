---
title: std::adopt_lock
summary: "「すでにロック済みのミューテックスを引き取る」と伝える目印。"
order: 900
tags:
  - 並行処理
---

# std::adopt_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::lock_guard` は、構築のときにミューテックスをロックして、破棄のときにアンロックします。すでに自分でロックしてある場合は、構築で二重にロックしてしまいます。`std::adopt_lock` は、「このミューテックスは、すでにロックしてある。所有権だけを引き継いでほしい」と伝える印です。

!!! tip "ポイント"
    - `lock_guard(m, std::adopt_lock)` は、ロック済みのミューテックスの面倒を見る
    - 破棄のときにアンロックする
    - `std::lock` で複数のミューテックスを同時にロックしたあと、`lock_guard` に引き渡すのが定番
    - 実際にロックしていないのに渡すと、未定義動作

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::adopt_lock {#adopt_lock}

<span class="ver ver-11">C++11</span>

```cpp
struct adopt_lock_t { explicit adopt_lock_t() = default; };
inline constexpr std::adopt_lock_t adopt_lock{};
```

`lock_guard`、`unique_lock`、`scoped_lock` の、コンストラクターに渡します。

```cpp
std::lock(a, b);                                 // 2 つを同時にロック（デッドロックしない）
std::lock_guard<std::mutex> ga(a, std::adopt_lock);
std::lock_guard<std::mutex> gb(b, std::adopt_lock);
```

C++17 以降は、`std::scoped_lock lock(a, b);` の 1 行で同じことができるので、`adopt_lock` を使う機会は減りました。

呼び出し側が、現在のスレッドで、ミューテックスを確実にロックしている責任を持ちます。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex m;

  m.lock();  // 先に自分でロックしてある
  {
    std::lock_guard<std::mutex> guard(m, std::adopt_lock);  // 所有権だけ引き継ぐ
    std::println("ロック中");
  }  // ここでアンロックされる

  // アンロックされたので、また取れる
  std::println("取れた: {}", m.try_lock());
  m.unlock();
}
```

```text title="実行結果"
ロック中
取れた: true
```

## ゲームでの使いどころ

複数のミューテックスを同時にロックしたあと、スコープを抜けるときに自動で解放するために使います。C++17 以降は `scoped_lock` です。

## よくあるミス

??? failure "ロックしていないのに渡す"
    未定義動作です。

??? failure "二重にアンロックする"
    `adopt_lock` で渡したあとは、自分で `unlock` しません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`defer_lock`](defer_lock.md) | ロックを遅らせる印 |
| [`lock`](lock.md) | 複数を同時にロック |
| [`scoped_lock`](scoped_lock.md) | 複数を一度に守る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::adopt_lock](https://cpprefjp.github.io/reference/mutex/defer_lock.html)
- [cppreference: std::adopt_lock](https://en.cppreference.com/w/cpp/thread/lock_tag)
