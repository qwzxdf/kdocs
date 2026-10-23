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

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

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

### EDOM {#EDOM}

```cpp
#define EDOM /* 実装定義の整数 */
```

- 戻り値: `errno` の値：数学関数の引数が、定義域の外
- 計算量: なし

`errno` が `EDOM` のとき、数学関数の引数が、定義域の外ことを表します。`std::errc` の対応する値（`std::errc::argument_out_of_domain`）と比べるほうが、移植性があります。

### ERANGE {#ERANGE}

```cpp
#define ERANGE /* 実装定義の整数 */
```

- 戻り値: `errno` の値：結果が、表せる範囲の外
- 計算量: なし

`errno` が `ERANGE` のとき、結果が、表せる範囲の外ことを表します。`std::errc` の対応する値（`std::errc::result_out_of_range`）と比べるほうが、移植性があります。

### EILSEQ {#EILSEQ}

```cpp
#define EILSEQ /* 実装定義の整数 */
```

- 戻り値: `errno` の値：不正なマルチバイト列
- 計算量: なし

`errno` が `EILSEQ` のとき、不正なマルチバイト列ことを表します。`std::errc` の対応する値（`std::errc::illegal_byte_sequence`）と比べるほうが、移植性があります。

### ENOENT {#ENOENT}

```cpp
#define ENOENT /* 実装定義の整数 */
```

- 戻り値: `errno` の値：ファイルやフォルダがない
- 計算量: なし

`errno` が `ENOENT` のとき、ファイルやフォルダがないことを表します。`std::errc` の対応する値（`std::errc::no_such_file_or_directory`）と比べるほうが、移植性があります。

### EACCES {#EACCES}

```cpp
#define EACCES /* 実装定義の整数 */
```

- 戻り値: `errno` の値：アクセス権がない
- 計算量: なし

`errno` が `EACCES` のとき、アクセス権がないことを表します。`std::errc` の対応する値（`std::errc::permission_denied`）と比べるほうが、移植性があります。

### EEXIST {#EEXIST}

```cpp
#define EEXIST /* 実装定義の整数 */
```

- 戻り値: `errno` の値：すでに存在する
- 計算量: なし

`errno` が `EEXIST` のとき、すでに存在することを表します。`std::errc` の対応する値（`std::errc::file_exists`）と比べるほうが、移植性があります。

### EINVAL {#EINVAL}

```cpp
#define EINVAL /* 実装定義の整数 */
```

- 戻り値: `errno` の値：引数が不正
- 計算量: なし

`errno` が `EINVAL` のとき、引数が不正ことを表します。`std::errc` の対応する値（`std::errc::invalid_argument`）と比べるほうが、移植性があります。

### ENOMEM {#ENOMEM}

```cpp
#define ENOMEM /* 実装定義の整数 */
```

- 戻り値: `errno` の値：メモリ不足
- 計算量: なし

`errno` が `ENOMEM` のとき、メモリ不足ことを表します。`std::errc` の対応する値（`std::errc::not_enough_memory`）と比べるほうが、移植性があります。

### ENOSPC {#ENOSPC}

```cpp
#define ENOSPC /* 実装定義の整数 */
```

- 戻り値: `errno` の値：デバイスに空きがない
- 計算量: なし

`errno` が `ENOSPC` のとき、デバイスに空きがないことを表します。`std::errc` の対応する値（`std::errc::no_space_on_device`）と比べるほうが、移植性があります。

### EINTR {#EINTR}

```cpp
#define EINTR /* 実装定義の整数 */
```

- 戻り値: `errno` の値：システムコールがシグナルで中断された
- 計算量: なし

`errno` が `EINTR` のとき、システムコールがシグナルで中断されたことを表します。`std::errc` の対応する値（`std::errc::interrupted`）と比べるほうが、移植性があります。

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
