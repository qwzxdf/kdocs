---
title: std::bad_alloc
summary: "メモリ確保に失敗したときの例外。"
order: 6
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_alloc

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <new>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_alloc` は、<strong>メモリの確保に失敗したことを表す例外</strong>。

!!! tip "ポイント"
    - メモリの確保に失敗したときに `new` が投げる
    - `new (std::nothrow) T` なら例外を投げず `nullptr` を返す
    - 捕まえて続行できる場面は少ない
    - `std::vector` の拡張などでも投げられる

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_alloc {#bad_alloc}

```cpp
class bad_alloc : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

メモリの確保（`new`、`std::vector` の拡張など）に失敗すると投げられます。確保したい量が大きすぎる、空きがないときです。

ゲームでは、この例外を捕まえて続行することは、まれです。確保に失敗した状態では、ほとんど何もできないためです。ログを出して終了する（またはシーンを破棄してメモリを空ける）のが一般的です。

`new (std::nothrow)` を使うと、例外を投げず、`nullptr` を返します。組み込み機器やコンソールで、例外を無効にした環境では、こちらを使います。

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  try {
    void* p = ::operator new(static_cast<std::size_t>(-1) / 2);   // 巨大すぎる確保
    ::operator delete(p);
  } catch (const std::bad_alloc&) {
    std::println("bad_alloc を捕まえた");
  }
}
```

```text title="実行結果"
bad_alloc を捕まえた
```

## ゲームでの使いどころ

メモリ不足でも落ちずに、保存してから終了するといった処理に使います。

```cpp
try {
  LoadLevel(path);
} catch (const std::bad_alloc&) {
  ShowError("メモリが足りません");
  UnloadAssets();
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

## コンパイラ対応

C++98 から使えます。`<new>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリの確保に失敗したときに `new` が投げる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_alloc](https://cpprefjp.github.io/reference/stdexcept/bad_alloc.html)
- [cppreference: std::bad_alloc](https://en.cppreference.com/w/cpp/error/bad_alloc)
