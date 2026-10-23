---
title: std::atoi
summary: "文字列を整数に変換する（失敗を検出できない古い関数）。"
order: 2
group: <cstdlib> の関数
tags:
  - 数値
---

# std::atoi

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::atoi` は、**文字列を `int` に変換する**C 由来の関数です。失敗しても `0` を返すだけで、エラーが分かりません。新しいコードでは、[`std::from_chars`](../../io/from_chars.md) を使います。

!!! tip "ポイント"
    - 数字でない文字列は 0 になる。0 との区別がつかない。
    - 範囲外の値は未定義動作。
    - 新しいコードでは `from_chars`。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::atoi {#atoi}

```cpp
int atoi(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |

- 戻り値: 変換した整数（失敗は 0）
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{} {}", std::atoi("42"), std::atoi("abc"));
}
```

```text title="実行結果"
42 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `from_chars` に置き換える |

## よくあるミス

??? failure "失敗が分からない"
    `"0"` と `"abc"` の結果が同じ 0 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../../io/from_chars.md) | 失敗を検出できる |
| [`strtol`](strtol.md) | 終了位置が分かる |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → 整数。失敗が分からない
    - [x] 新しいコードは from_chars
    - [x] 範囲外は未定義

## 関連ページ

- [cpprefjp: std::atoi](https://cpprefjp.github.io/reference/cstdlib/atoi.html)
- [cppreference: std::atoi](https://en.cppreference.com/w/cpp/numeric/math/atoi)
