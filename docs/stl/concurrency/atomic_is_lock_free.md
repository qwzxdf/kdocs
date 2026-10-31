---
title: std::atomic_is_lock_free
summary: "atomic の操作が、ロックなしで行えるかを調べる。"
order: 900
tags:
  - 並行処理
---

# std::atomic_is_lock_free

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`std::atomic<T>` は、`T` のサイズによっては、CPU の命令だけでは実現できず、内部でロックを使います。ロックを使うと、遅くなるうえ、割り込みやシグナルのハンドラーの中で使えなくなります。`atomic_is_lock_free(&a)` は、この `atomic` がロックを使わずに動くかを調べる関数です。

!!! tip "ポイント"
    - `true` なら、ロックなしで動く（CPU の原子命令のみ）
    - `int`、ポインターなどの小さな型は、ほぼ必ず `true`
    - 大きな構造体は `false` になりやすい
    - メンバー関数 `a.is_lock_free()` と同じ。静的な版は `is_always_lock_free`

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_is_lock_free {#atomic_is_lock_free}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
bool atomic_is_lock_free(const std::atomic<T>* obj) noexcept;
```

結果は、型と環境で決まります。アライメントによって、同じ型でも変わる実装があります。

コンパイル時に分かる版が、`std::atomic<T>::is_always_lock_free`（C++17）です。常にロックなしなら `true` で、`static_assert` に使えます。

ロックを使う `atomic` は、機能としては正しく動きますが、性能の期待が外れます。16 バイトを超える構造体を `atomic` にすると、大抵は内部でミューテックスを使います。割り込みハンドラーやリアルタイム処理に使うときは、事前にこの関数で確かめます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

struct Small { int a; };
struct Big { char data[64]; };

int main() {
  std::atomic<int> i{0};
  std::atomic<Big> big{};

  std::println("int: {}", std::atomic_is_lock_free(&i));
  std::println("64 バイトの構造体: {}", std::atomic_is_lock_free(&big));

  // コンパイル時に調べる
  static_assert(std::atomic<int>::is_always_lock_free);
  static_assert(std::atomic<Small>::is_always_lock_free);
}
```

```text title="実行結果"
int: true
64 バイトの構造体: false
```

## ゲームでの使いどころ

性能が重要な共有データに `atomic` を使うとき、`static_assert(is_always_lock_free)` で、ロックなしであることを保証します。

## よくあるミス

??? failure "大きな構造体を atomic にして速いと思う"
    内部でロックを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic`](atomic.md) | 本体 |
| `is_always_lock_free` | コンパイル時の判定 |
| [`atomic_flag`](atomic_flag.md) | 常にロックなしが保証される |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_is_lock_free](https://cpprefjp.github.io/reference/atomic/atomic_is_lock_free.html)
- [cppreference: std::atomic_is_lock_free](https://en.cppreference.com/w/cpp/atomic/atomic_is_lock_free)
