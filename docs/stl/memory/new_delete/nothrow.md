---
title: std::nothrow
summary: "new が失敗したとき、例外ではなく nullptr を返させる指定。"
order: 4
group: new / delete まわり
tags:
  - メモリ
---

# std::nothrow

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <new>`
</div>

`std::nothrow` は、**`new` が失敗したときに、例外ではなく `nullptr` を返させる**ための印です。`new (std::nothrow) T` のように書きます。例外を使わない方針のコードで使います。

!!! tip "ポイント"
    - `new (std::nothrow) T;` → 失敗すると `nullptr`。
    - 戻り値を必ず `nullptr` と比べる。
    - コンストラクターの中の例外は、別（`nothrow` でも飛ぶ）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::nothrow {#nothrow}

```cpp
T* p = new (std::nothrow) T(args...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `std::nothrow` | `std::nothrow_t` | 失敗したとき、例外ではなく `nullptr` を返す印 |

- 戻り値: 成功なら `T*`、失敗なら `nullptr`
- 例外を使わないプロジェクトで使われます。**`nullptr` かどうかを必ず確認**します（確認しないと、結局クラッシュします）

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  int* p = new (std::nothrow) int(7);  // 失敗しても例外を投げない
  std::println("{}", p != nullptr);
  delete p;
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 例外を切っているプロジェクトでのメモリ確保 | `auto* p = new (std::nothrow) Big;` |

## よくあるミス

??? failure "nullptr を調べない"
    失敗すると `nullptr` で、使うとクラッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`new`](new.md) | 通常の new |
| [`malloc`](../malloc.md) | 失敗すると nullptr |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 失敗したら nullptr を返す new
    - [x] 戻り値を必ず確認
    - [x] 例外を使わない方針向け

## 関連ページ

- [cpprefjp: std::nothrow](https://cpprefjp.github.io/reference/new/new.html)
- [cppreference: std::nothrow](https://en.cppreference.com/w/cpp/memory/new/nothrow)
