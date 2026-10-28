---
title: std::bad_weak_ptr
summary: "期限切れの weak_ptr から shared_ptr を作ろうとしたときの例外。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_weak_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_weak_ptr` は、<strong>期限切れの `weak_ptr` から `shared_ptr` を作ったことを表す例外</strong>。

!!! tip "ポイント"
    - 期限切れの `weak_ptr` を `shared_ptr` のコンストラクターに渡すと投げられる
    - `lock()` なら空の `shared_ptr` が返る（例外にならない）
    - `<memory>` で宣言される
    - `lock()` を使えば、起こらない

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_weak_ptr {#bad_weak_ptr}

```cpp
class bad_weak_ptr : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

指す先がすでに破棄された `std::weak_ptr` から、`std::shared_ptr` のコンストラクターで作ろうとすると、投げられます。`weak_ptr::lock()` なら、例外を投げず、空の `shared_ptr` を返します。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  std::weak_ptr<int> weak;                 // 何も指していない
  try {
    std::shared_ptr<int> strong(weak);
  } catch (const std::bad_weak_ptr&) {
    std::println("bad_weak_ptr を捕まえた");
  }
  std::println("lock なら安全: {}", weak.lock() == nullptr);
}
```

```text title="実行結果"
bad_weak_ptr を捕まえた
lock なら安全: true
```

## ゲームでの使いどころ

キャラクターが消えたかもしれない参照を安全に使います。

```cpp
if (auto target = weak_target.lock()) {
  Attack(*target);   // まだ生きている
}
```

## よくあるミス

??? failure "捕まえずに放置して、プログラムが終了する"
    例外を投げうる機能を使うときは、`try` / `catch` で受けるか、事前に条件を確かめます。

??? failure "`catch (std::exception)` と値で捕まえる"
    `const` 参照で捕まえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | すべての標準例外の基底 |
| [`weak_ptr`](../../utilities/weak_ptr.md) | 所有しない弱い参照 |

## コンパイラ対応

C++11 から使えます。`<memory>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 期限切れの `weak_ptr` を `shared_ptr` のコンストラクターに渡すと投げられる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_weak_ptr](https://cpprefjp.github.io/reference/memory/bad_weak_ptr.html)
- [cppreference: std::bad_weak_ptr](https://en.cppreference.com/w/cpp/memory/bad_weak_ptr)
