---
title: std::out_of_range
summary: "範囲外の添字・キーにアクセスしたときの例外。"
order: 3
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::out_of_range

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <stdexcept>`
</div>

`std::out_of_range` は、**範囲外の添字やキーにアクセスした**ときに投げられる例外です。`vector::at(i)` や `map::at(key)` が、範囲外のときに投げます。`[]` は投げず、未定義動作になります。

!!! tip "ポイント"
    - `at()` は範囲を検査して `out_of_range` を投げる。`[]` は検査しない。
    - `logic_error` の派生クラス。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::out_of_range {#out_of_range}

```cpp
class out_of_range : public logic_error;
```

- 範囲外を表します。`vector::at`、`string::at`、`string::substr`、`map::at`、`stoi`（int に入らない）が投げます

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  try {
    v.at(10);   // at は範囲を検査する
  } catch (const std::out_of_range&) {
    std::println("範囲外");
  }
}
```

```text title="実行結果"
範囲外
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 範囲外アクセスをテストで検出する | `v.at(i)` |

## よくあるミス

??? failure "[] で範囲外を調べようとする"
    `[]` は例外を投げず、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invalid_argument`](invalid_argument.md) | 引数が不正 |
| [`std::vector`](../../containers/vector.md) | `at()` が投げる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲外アクセスの例外
    - [x] `at()` が投げる
    - [x] `[]` は投げない

## 関連ページ

- [cpprefjp: std::out_of_range](https://cpprefjp.github.io/reference/stdexcept/out_of_range.html)
- [cppreference: std::out_of_range](https://en.cppreference.com/w/cpp/error/out_of_range)
