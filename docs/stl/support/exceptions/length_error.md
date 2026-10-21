---
title: std::length_error
summary: "許される最大の長さを超えたときの例外。"
order: 13
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::length_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <stdexcept>`
</div>

`std::length_error` は、**コンテナなどが許される最大の長さ（`max_size()`）を超える大きさを求められた**ときに投げられる例外です。`vector::reserve` に巨大な値を渡したときなどに起きます。入力の大きさをそのまま確保に使うコードの検査に役立ちます。

!!! tip "ポイント"
    - `logic_error` の派生クラス。
    - 大きすぎる値は、確保の前に自分で上限を確認する。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::length_error {#length_error}

```cpp
class length_error : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <print>
#include <stdexcept>
#include <vector>

int main() {
  std::vector<int> v;
  try {
    v.reserve(v.max_size() + 1);
  } catch (const std::length_error&) {
    std::println("大きすぎる");
  }
}
```

```text title="実行結果"
大きすぎる
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み込んだデータの大きさが異常でないか | 確保する前に上限を確認する |

## よくあるミス

??? failure "bad_alloc と取り違える"
    `length_error` は「大きさが上限を超えた」、`bad_alloc` は「メモリが足りなかった」です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bad_alloc`](bad_alloc.md) | メモリ不足 |
| [`logic_error`](logic_error.md) | 親 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大の長さを超えた
    - [x] reserve などが投げる
    - [x] メモリ不足とは別

## 関連ページ

- [cpprefjp: std::length_error](https://cpprefjp.github.io/reference/stdexcept/length_error.html)
- [cppreference: std::length_error](https://en.cppreference.com/w/cpp/error/length_error)
