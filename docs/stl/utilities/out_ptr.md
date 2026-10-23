---
title: std::out_ptr
summary: "C のAPI が「ポインターのポインター」で返すオブジェクトを、スマートポインターで受け取る。"
order: 76
tags:
  - ユーティリティ
---

# std::out_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <memory>`
</div>

`std::out_ptr(smart_ptr)` は、**C のAPI が `T**` の引数を通して返すオブジェクトを、そのまま `unique_ptr` や `shared_ptr` で受け取る**ための関数です。「`Create(&handle)` でハンドルが返ってくる」形の API で、生ポインターを経由せずに、すぐスマートポインターで持てます。呼び出しが終わると、自動で `reset` されます。

!!! tip "ポイント"
    - `Create(std::out_ptr(p));` の形で、出力引数に渡す。
    - 既存の値は解放される（`reset` と同じ）。
    - 解放の仕方が `delete` と違うときは、削除関数を持つ `unique_ptr` を使う。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::out_ptr {#out_ptr}

```cpp
template <class Smart, class... Args>
auto out_ptr(Smart& s, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | スマートポインター | 結果を受け取る先 |

- 戻り値: `T**` として使える包み
- 計算量: O(1)

```cpp
#include <memory>
#include <print>

// C 風の API: 新しい int を作って、ポインターのポインターで返す
void Create(int** out) {
  *out = new int(5);
}

int main() {
  std::unique_ptr<int> p;
  Create(std::out_ptr(p));  // 生ポインターを経由せずに、unique_ptr で受け取る
  std::println("{}", *p);
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| COM や C のライブラリが返すハンドルを、スマートポインターで持つ | `CreateX(std::out_ptr(handle))` |

## よくあるミス

??? failure "削除の方法が合わない"
    `unique_ptr` の削除関数が、API の解放関数と合っているか確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inout_ptr`](inout_ptr.md) | 既存の値を渡して、置き換えて返す |
| [`std::unique_ptr`](unique_ptr.md) | 受け取る先 |

## コンパイラ対応

C++23 の機能です。GCC 14 / MSVC 19.37 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C のAPI の出力引数を受け取る
    - [x] 呼び出し後に自動で reset
    - [x] C++23

## 関連ページ

- [cpprefjp: std::out_ptr](https://cpprefjp.github.io/reference/memory/out_ptr.html)
- [cppreference: std::out_ptr](https://en.cppreference.com/w/cpp/memory/out_ptr_t)
