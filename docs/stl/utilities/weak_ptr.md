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

敵がプレイヤーを追いかけているとき、プレイヤーがやられて消えたら、敵はもう追いかけられません。敵が `shared_ptr` でプレイヤーを持っていると、敵が持っている限りプレイヤーが消えず、「消えたことに気づけない」問題が起きます。`std::weak_ptr` は、`shared_ptr` が持っているものを、持ち主にならずに見るためのポインターです。使いたいときに `lock()` で一時的に `shared_ptr` に変えて、相手が消えていれば空が返ります。

!!! tip "ポイント"
    - **「相手が消えているかもしれない」参照**に使う（ターゲット、親への参照、キャッシュ）。
    - 使う直前に `lock()`。`if (auto p = w.lock()) { ... }` が定番の形。
    - **お互いを `shared_ptr` で持ち合う循環参照を防ぐ**ために、片方を `weak_ptr` にする。

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) の参照カウントの仕組みを先に読んでください。`weak_ptr` は、そのカウントに数えられない見張り役です。

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

### use_count {#use_count}

```cpp
long use_count() const noexcept;
```

- 計算量: 定数

管理しているオブジェクトを共有している `shared_ptr` の数。期限切れなら 0。

### reset {#reset}

```cpp
void reset() noexcept;
```

- 計算量: 定数

何も指さない状態にします。

### swap {#swap}

```cpp
void swap(weak_ptr& r) noexcept;
```

- 計算量: 定数

2 つの `weak_ptr` を入れ替えます。

### owner_before {#owner_before}

```cpp
template <class Y>
bool owner_before(const weak_ptr<Y>& other) const noexcept;
```

- 計算量: 定数

持ち主（制御ブロック）の順序で比べます。`weak_ptr` をキーにした `map` で使います。

### owner_hash <span class="ver ver-26">C++26</span> {#owner_hash data-toc-label="owner_hash"}

```cpp
std::size_t owner_hash() const noexcept;
```

- 計算量: 定数

持ち主（制御ブロック）に対するハッシュ値。

### owner_equal <span class="ver ver-26">C++26</span> {#owner_equal data-toc-label="owner_equal"}

```cpp
template <class Y>
bool owner_equal(const weak_ptr<Y>& other) const noexcept;
```

- 計算量: 定数

同じ持ち主かどうか。

### operator= {#op_assign}

```cpp
weak_ptr& operator=(const weak_ptr& r) noexcept;
weak_ptr& operator=(const shared_ptr<T>& r) noexcept;
```

- 計算量: 定数

`weak_ptr` または `shared_ptr` から代入します。参照カウントは増えません（弱い参照）。

## ゲームでの使いどころ

ターゲットの参照で使います。敵がプレイヤーを狙うとき、`weak_ptr<Player> target_;` として持ちます。毎フレーム `if (auto p = target_.lock())` と調べて、まだ生きていれば追いかけ、消えていれば目標を解除します。

親子の参照で、循環参照を避けるのにも使います。親が子を `shared_ptr` で持ち、子が親を `weak_ptr` で持つ形にすると、お互いが相手を生かし合うことがありません。

リソースのキャッシュにも使います。`unordered_map<string, weak_ptr<Texture>>` に登録しておくと、使っている間だけ共有され、誰も使わなくなったら解放されます。

## よくあるミス

??? failure "`lock()` を呼ばずに、`expired()` だけで判断して使う"
    `if (!w.expired()) { w.lock()->Foo(); }` と書くと、`expired()` と `lock()` の間に別のスレッドが解放する可能性があります。1 回の `lock()` で得た `shared_ptr` を使います。

??? failure "`lock()` で得た `shared_ptr` を長く持つ"
    `lock()` した `shared_ptr` を、メンバーとして保存すると、その時点で `weak_ptr` ではなく普通の持ち主になります。見張るだけにしたいなら、スコープの中で使い切ります。

??? failure "`make_shared` で作ったものが、`weak_ptr` のせいでメモリが解放されない"
    `make_shared` では、制御ブロックと本体が同じ領域にあるため、`weak_ptr` が残る間は、メモリそのものが解放されません。デストラクターは呼ばれます。

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
    - [x] 持ち主にならずに見る。使うときは `lock()`。
    - [x] 循環参照を防ぐために、片方を `weak_ptr` にする。
    - [x] `expired()` で判断せず、`lock()` の結果を使う。

## 関連ページ

- [cpprefjp: std::weak_ptr](https://cpprefjp.github.io/reference/memory/weak_ptr.html)
- [cppreference: std::weak_ptr](https://en.cppreference.com/w/cpp/memory/weak_ptr)
