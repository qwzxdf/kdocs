---
title: std::try_lock
summary: "複数のミューテックスを、待たずにまとめてロックしようとする。"
order: 900
tags:
  - 並行処理
---

# std::try_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

複数のミューテックスを、待たずにまとめてロックしたい。`std::try_lock(m1, m2, ...)` は、先頭から順にロックを試みます。全部取れれば `-1` を返します。1 つでも取れなければ、すでに取ったものを全部戻して、取れなかった最初の番号を返します。

!!! tip "ポイント"
    - 全部取れたら `-1`、取れなければ最初に失敗した番号（0 始まり）
    - 失敗したら、すでに取ったロックは自動で解放される
    - 待たない。`std::lock` との違い
    - 引数は、ロックできるもの（`mutex` や `unique_lock`）

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::try_lock {#try_lock}

<span class="ver ver-11">C++11</span>

```cpp
template <class L1, class L2, class... Ln>
int try_lock(L1& l1, L2& l2, Ln&... ln);
```

戻り値の `-1` は、「全部のロックに成功した」を表します。0 以上の値は、その番号のロックが取れなかったことを表します。

`std::lock` は、取れるまで待ちます。`std::try_lock` は、待たずに結果を返します。取れなければ、ほかの仕事を先にして、あとでまた試す、といった処理に向いています。

途中で例外が出たときも、取ったロックは解放されます。

成功したあと、ロックの解放は呼び出し側の責任です。`unique_lock(m, std::adopt_lock)` に引き渡すのが定番です。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex a;
  std::mutex b;

  // 両方空いている: 成功は -1
  std::println("全部取れた: {}", std::try_lock(a, b));
  a.unlock();
  b.unlock();

  // b を別のスレッドが持っている
  b.lock();
  int result = 0;
  std::thread t([&] { result = std::try_lock(a, b); });
  t.join();
  std::println("失敗した番号: {}", result);  // 1 (b)

  // a は戻されている: 取れる
  std::println("a は取れる: {}", a.try_lock());
  a.unlock();
  b.unlock();
}
```

```text title="実行結果"
全部取れた: -1
失敗した番号: 1
a は取れる: true
```

## ゲームでの使いどころ

複数の資源が全部空いているときだけ処理を進める、待たない設計に使います。

## よくあるミス

??? failure "-1 を失敗と思う"
    `-1` は成功です。

??? failure "成功後に unlock を忘れる"
    呼び出し側で解放します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lock`](lock.md) | 待って全部取る |
| [`try_to_lock`](try_to_lock.md) | 1 つを試す |
| [`scoped_lock`](scoped_lock.md) | 待ってまとめて取る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::try_lock](https://cpprefjp.github.io/reference/mutex/try_lock.html)
- [cppreference: std::try_lock](https://en.cppreference.com/w/cpp/thread/try_lock)
