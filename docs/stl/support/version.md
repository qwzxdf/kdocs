---
title: <version>（機能テストマクロ）
summary: "「この標準ライブラリの機能が使えるか」を、`#if` で調べるためのマクロ。"
order: 40
tags:
  - 型・言語サポート
---

# <version>（機能テストマクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <version>`
</div>

`<version>` は、**標準ライブラリの機能が使えるかを、`#if` で調べるためのマクロ（機能テストマクロ）**を定義するヘッダーです。`__cpp_lib_print`、`__cpp_lib_expected` のように、機能ごとのマクロがあり、使えるなら日付に見える数字（導入された年月）が入っています。コンパイラの違いを吸収するコードを書くときに使います。

!!! tip "ポイント"
    - `#if defined(__cpp_lib_print)` で、`<print>` が使えるかを調べる。
    - 値は `YYYYMM` 形式の数字（導入された規格の年月）。
    - 言語機能のマクロは `__cpp_xxx`（`__cpp_concepts` など）。

## 関数の詳しい説明

### <version> {#version}

```cpp
#define __cpp_lib_print 202207L   // 例
```

- 戻り値: マクロ（未対応なら未定義）
- 計算量: コンパイル時

```cpp
#include <print>
#include <version>

int main() {
#if defined(__cpp_lib_print)
  std::println("std::print が使える");
#else
  std::puts("std::print は使えない");
#endif
}
```

```text title="実行結果"
std::print が使える（対応した環境の場合）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コンパイラが古いときに、代わりの実装へ切り替える | `#if defined(__cpp_lib_flat_map)` |

## よくあるミス

??? failure "マクロの値で新旧を比べる"
    日付なので、`>= 202207L` のように比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| `__cplusplus` | 規格の版全体を表す |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 機能が使えるかを #if で調べる
    - [x] マクロ名は `__cpp_lib_機能名`
    - [x] 値は導入年月

## 関連ページ

- [cpprefjp: <version>（機能テストマクロ）](https://cpprefjp.github.io/reference/version.html)
- [cppreference: <version>（機能テストマクロ）](https://en.cppreference.com/w/cpp/utility/feature_test)
