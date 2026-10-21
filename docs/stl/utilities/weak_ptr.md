---
title: std::weak_ptr
summary: "shared_ptr の持ち物を、持ち主にならずに見る。相手が消えたかを確かめられる。"
order: 50
tags:
  - ユーティリティ
---

# std::weak_ptr

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::weak_ptr` は、**`shared_ptr` が持っているものを、持ち主にならずに「見る」ためのポインタ**です。参照カウントを増やさないので、相手が消えるのを邪魔しません。使いたいときは `lock()` で一時的に `shared_ptr` に変えます。相手が消えていれば、`lock()` は空の `shared_ptr` を返します。

!!! tip "ポイント"
    - **「相手が消えているかもしれない」参照**に使う（ターゲット、親への参照、キャッシュ）。
    - 使う直前に `lock()`。`if (auto p = w.lock()) { ... }` が定番の形。
    - **お互いを `shared_ptr` で持ち合う循環参照を防ぐ**ために、片方を `weak_ptr` にする。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) を先に読んでください。

## 宣言

```cpp
template <class T>
class weak_ptr;
```

## 関数の詳しい説明

### weak_ptr を作る {#weak}

```cpp
weak_ptr(const shared_ptr<T>& r) noexcept;
```

- shared_ptr から作ります。参照カウントは増えません（相手が消えるのを邪魔しない）
- weak_ptr から直接 `->` で中身は使えません。`lock()` で shared_ptr に戻してから使います

### lock {#lock}

```cpp
std::shared_ptr<T> lock() const noexcept;
```

- 戻り値: 相手がまだ生きていれば、それを指す shared_ptr。消えていれば空の shared_ptr
- 取り出した shared_ptr を持っている間は、相手が消えないことが保証されます

### expired {#expired}

```cpp
bool expired() const noexcept;
```

- 相手がもう消えていれば `true`

```cpp
#include <memory>
#include <print>

int main() {
  auto p = std::make_shared<int>(1);
  std::weak_ptr<int> w = p;
  std::println("{}", w.expired());
  p.reset();
  std::println("{}", w.expired());
}
```

```text title="実行結果"
false
true
```

!!! note "実際は"
    `expired()` で確認してから `lock()` すると、その間に消える可能性があります（マルチスレッドのとき）。使うなら最初から `if (auto p = w.lock())` で書きます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 敵の「ターゲット」への参照（ターゲットが倒れていたら消える） | `std::weak_ptr<Enemy> target;` |
| 子から親への参照（循環参照の防止） | `std::weak_ptr<Node> parent;` |
| キャッシュ（誰も使わなくなったら捨てる） | `weak_ptr` のキャッシュ表 |

## よくあるミス

??? failure "expired() で確認してから lock() する"
    確認から `lock()` の間に消える可能性があります（マルチスレッド）。最初から `if (auto p = w.lock())` と書きます。

??? failure "lock() の結果を保存しない"
    `lock()` した `shared_ptr` を持っている間は、相手が消えません。長く保持すると、消えるはずのものが残ります。短いスコープで使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::shared_ptr`](shared_ptr.md) | 持ち主になる |
| [`std::unique_ptr`](unique_ptr.md) | 持ち主は 1 人。参照はただのポインタか参照 |
| 生ポインタ | 消えたかどうかを知る方法がない |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 持ち主にならずに見る
    - [x] 使う直前に `lock()`
    - [x] 循環参照を防ぐ

## 関連ページ

- [cpprefjp: std::weak_ptr](https://cpprefjp.github.io/reference/memory/weak_ptr.html)
- [cppreference: std::weak_ptr](https://en.cppreference.com/w/cpp/memory/weak_ptr)
