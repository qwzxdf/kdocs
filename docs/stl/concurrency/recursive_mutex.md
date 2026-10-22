---
title: std::recursive_mutex
summary: "同じスレッドなら何度でもロックできる鍵。"
order: 83
tags:
  - 並行処理
---

# std::recursive_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::recursive_mutex` は、**同じスレッドが何度でも続けてロックできる**鍵です。普通の `mutex` は、自分でかけた鍵をもう一度かけようとすると固まりますが、`recursive_mutex` なら、かけた回数だけ開ければ使えます。再帰する関数がロックを取る、といった場面で使えますが、設計を見直すほうが良いサインでもあります。

!!! tip "ポイント"
    - **できるだけ使わない。** ロックのかけ方を整理して、普通の `mutex` で済ませるのが良い。
    - ロックした回数と同じ回数だけ `unlock` が必要（`lock_guard` なら自動）。
    - 普通の `mutex` より少し遅い。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::recursive_mutex {#recursive_mutex}

```cpp
class recursive_mutex;
```

- 同じスレッドなら何度ロックしてもいい mutex（ロックした回数だけ unlock が必要）。必要になるのは設計がこじれているときが多いので、使わずに済むようにします

### lock {#lock}

```cpp
void lock();
```

- 計算量: 待つ時間による

ロックします。すでに自分が持っていれば、回数を増やして成功します。

### try_lock {#try_lock}

```cpp
bool try_lock() noexcept;
```

- 計算量: 定数

待たずに、ロックを試みます。

### unlock {#unlock}

```cpp
void unlock();
```

- 計算量: 定数

ロックの回数を 1 減らします。0 になったら、本当に解除します。

### native_handle {#native_handle}

```cpp
native_handle_type native_handle();
```

- 計算量: 定数

OS 固有のハンドル（`pthread_t` や `HANDLE`）を返します。標準にない機能（優先度の設定など）を使うときの出口です。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::recursive_mutex m;
  std::lock_guard a(m);
  std::lock_guard b(m);  // 同じスレッドなら、もう一度ロックできる
  std::println("OK");
}
```

```text title="実行結果"
OK
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 再帰する関数の中でロックを取る | ロックを関数の入口に集め、内部関数は鍵を取らない形に直す方が良い |

## よくあるミス

??? failure "設計の問題を隠す"
    「呼び出し元がすでに鍵をかけているかも」という状況は、関数の分け方の問題です。`recursive_mutex` に頼らず、「鍵を取る関数」と「取らない内部関数」に分けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mutex`](mutex.md) | 普通の鍵 |
| [`std::timed_mutex`](timed_mutex.md) | 時間つきで待てる鍵 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じスレッドなら何度でもロックできる
    - [x] 使わない設計が望ましい
    - [x] 遅い

## 関連ページ

- [cpprefjp: std::recursive_mutex](https://cpprefjp.github.io/reference/mutex/recursive_mutex.html)
- [cppreference: std::recursive_mutex](https://en.cppreference.com/w/cpp/thread/recursive_mutex)
