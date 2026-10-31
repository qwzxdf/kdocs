---
title: std::atomic_init
summary: "atomic を初期化する（まだ他のスレッドが触っていないとき）。"
order: 900
tags:
  - 並行処理
---

# std::atomic_init

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`std::atomic<int> a;` と書いただけの `atomic` は、C++20 より前は初期化されませんでした。値を入れるには、構築のときに渡すか、`atomic_init` で初期化します。`atomic_init(&a, v)` は、まだ他のスレッドから見えていない `atomic` に、初期値を入れる関数です。

!!! tip "ポイント"
    - 初期化専用。他のスレッドが触る前に呼ぶ
    - C++20 で `atomic` の既定の構築が値初期化になり、`atomic_init` は非推奨になった
    - メモリ順序はない。単純な代入と同じ
    - 通常は `std::atomic<int> a{0};` と書く

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_init {#atomic_init}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
void atomic_init(std::atomic<T>* obj, typename std::atomic<T>::value_type desired) noexcept;
```

`obj` を、スレッド安全な操作を使わずに初期化します。他のスレッドが同時に触っていると、データ競合です。

C++11 から C++17 では、`std::atomic<int> a;` は初期化されない `atomic` でした（C の `_Atomic` との互換のため）。そのため、`atomic_init` で値を入れる必要がありました。C++20 からは、既定の構築が値初期化になったので、この関数は不要になり、非推奨です。

新しいコードでは、宣言で初期化します。

```cpp
std::atomic<int> a{0};
```

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a;       // C++20 以降は 0 で初期化される
  std::atomic_init(&a, 7);  // 古い書き方（C++20 では非推奨）
  std::println("{}", a.load());

  std::atomic<int> b{7};    // 新しい書き方
  std::println("{}", b.load());
}
```

```text title="実行結果"
7
7
```

## ゲームでの使いどころ

古いコードの読解用です。新しく書くなら、宣言と同時に初期化します。

## よくあるミス

??? failure "他のスレッドが触る状態で呼ぶ"
    データ競合になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic`](atomic.md) | 本体 |
| `atomic::store` | 共有後に値を入れる |

## コンパイラ対応

C++11 から使えます。C++20 で非推奨です。手元の MSVC は警告（C4996）を出すことがあります。

## 関連ページ

- [cpprefjp: std::atomic_init](https://cpprefjp.github.io/reference/atomic/atomic_init.html)
- [cppreference: std::atomic_init](https://en.cppreference.com/w/cpp/atomic/atomic_init)
