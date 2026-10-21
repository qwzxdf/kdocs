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

`std::bad_alloc` は、**`new` などでメモリが確保できなかった**ときに投げられる例外です。メモリ不足の状態なので、受け取っても、できることは限られます（後片付けして終了、など）。

!!! tip "ポイント"
    - `new (std::nothrow)` なら、投げずに `nullptr`。
    - メモリ不足でログも出せないことがある。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_alloc {#bad_alloc}

```cpp
class bad_alloc : public exception;
```

- `new` や vector の確保でメモリが足りなかったときに投げられます

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  try {
    throw std::bad_alloc();   // 実際は new が失敗したときに投げられる
  } catch (const std::bad_alloc&) {
    std::println("メモリ確保失敗");
  }
}
```

```text title="実行結果"
メモリ確保失敗
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 巨大なアセットの読み込みで失敗した | `catch (const std::bad_alloc&)` で、読み込みを諦める |

## よくあるミス

??? failure "受け取って処理を続ける"
    状態が不安定なことがあります。安全に終了する設計にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nothrow`](../../memory/new_delete/nothrow.md) | 例外ではなく nullptr |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリ確保失敗の例外
    - [x] 受け取っても出来ることは少ない
    - [x] nothrow で例外なしにできる

## 関連ページ

- [cpprefjp: std::bad_alloc](https://cpprefjp.github.io/reference/stdexcept/bad_alloc.html)
- [cppreference: std::bad_alloc](https://en.cppreference.com/w/cpp/error/bad_alloc)
