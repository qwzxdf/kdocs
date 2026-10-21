---
title: errno
summary: "C 由来の関数が失敗した理由を入れる、グローバルなエラー番号。"
order: 97
tags:
  - 入出力・文字列
---

# errno

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cerrno>`
</div>

`errno` は、**C 由来の関数が失敗したときに、その理由の番号が入る**変数（実際はマクロ）です。`std::strtol` の範囲外は `ERANGE` になります。使う前に `errno = 0;` にして、呼んだ直後に確認します。スレッドごとに別の値を持ちます。C++ の新しい関数は、`std::error_code` を返す形が主流です。

!!! tip "ポイント"
    - 呼ぶ前に `errno = 0;` にしておく。
    - 成功しても `errno` が書き換わらないことがある。失敗が分かるときだけ見る。
    - 説明文は `std::strerror(errno)`。

## 関数の詳しい説明

### errno {#cerrno}

```cpp
#define errno /* スレッドごとの int の左辺値 */
#define ERANGE /* 値が範囲外 */
```

- 戻り値: 直前の失敗のエラー番号
- 計算量: O(1)

```cpp
#include <cerrno>
#include <cstdlib>
#include <print>

int main() {
  errno = 0;
  std::strtol("999999999999999999999", nullptr, 10);   // 範囲外
  std::println("{}", errno == ERANGE);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI の失敗理由を調べる | `if (errno == ENOENT)` |

## よくあるミス

??? failure "呼ぶ前に 0 にしない"
    以前の失敗の値が残っていて、誤判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::error_code`](../support/error_code.md) | C++ のエラー表現 |
| [`std::strtol`](../numeric/cstdlib/strtol.md) | errno を使う関数 |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 関数の失敗理由の番号
    - [x] 呼ぶ前に 0 にする
    - [x] スレッドごとの値

## 関連ページ

- [cpprefjp: errno](https://cpprefjp.github.io/reference/cerrno/errno.html)
- [cppreference: errno](https://en.cppreference.com/w/cpp/error/errno)
