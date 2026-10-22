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

`weak_ptr` は、指している先がすでに解放されているかもしれません。`std::shared_ptr<T> s(w);` のように、`weak_ptr` から `shared_ptr` をコンストラクタで作ろうとして、先が解放済みだと `bad_weak_ptr` が投げられます。

!!! tip "ポイント"
    - `weak_ptr::lock()` は例外を投げず、空の `shared_ptr` を返す。
    - コンストラクタで作ろうとしたときだけ例外になる。
    - `std::exception` から派生。

!!! info "このページを読む前に"
    [`std::shared_ptr`](../../utilities/shared_ptr.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_weak_ptr {#bad_weak_ptr}

```cpp
class bad_weak_ptr : public exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: `what()` はエラーを表す文字列
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  std::weak_ptr<int> w;
  try {
    std::shared_ptr<int> s(w);
  } catch (const std::bad_weak_ptr&) {
    std::println("期限切れ");
  }
}
```

```text title="実行結果"
期限切れ
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 期限切れの確認 | `if (auto s = w.lock()) { ... }`（例外を使わない） |

## よくあるミス

??? failure "コンストラクタで直接作る"
    `shared_ptr<T> s(w);` は期限切れで例外です。普通は `lock()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weak_ptr`](../../utilities/weak_ptr.md) | 弱い参照 |
| [`shared_ptr`](../../utilities/shared_ptr.md) | 共有所有 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 期限切れの weak_ptr から shared_ptr を作ると投げる
    - [x] lock() は投げない
    - [x] <memory>

## 関連ページ

- [cpprefjp: std::bad_weak_ptr](https://cpprefjp.github.io/reference/memory/bad_weak_ptr.html)
- [cppreference: std::bad_weak_ptr](https://en.cppreference.com/w/cpp/memory/bad_weak_ptr)
