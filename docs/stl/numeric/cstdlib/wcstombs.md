---
title: std::wcstombs
summary: "wchar_t の文字列をマルチバイト文字列に変換する。"
order: 900
tags:
  - 数値
---

# std::wcstombs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`wchar_t` の文字列を、ロケールのマルチバイト文字列にまとめて変換します。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::wcstombs {#wcstombs}

```cpp
std::size_t wcstombs(char* dst, const wchar_t* src, std::size_t len);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dst` | char* | 変換結果の書き込み先（`nullptr` で長さだけ調べる） |
| `src` | const wchar_t* | 変換元の文字列 |
| `len` | size_t | 書き込む最大のバイト数 |

- 戻り値: 書き込んだバイト数。不正なら `(size_t)-1`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char buf[8];
  std::size_t n = std::wcstombs(buf, L"abc", 8);
  std::println("{}", n);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 文字コードの変換（ただし新しいコードは UTF-8 に統一する） |

## よくあるミス

??? failure "ロケールを設定せずに使う"
    既定は `"C"` ロケールで、ASCII しか変換できません。`std::setlocale` で設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../../encoding/index.md) | 変換の考え方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] wchar_t の文字列をマルチバイト文字列に変換する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcstombs](https://cpprefjp.github.io/reference/cstdlib/wcstombs.html)
- [cppreference: std::wcstombs](https://en.cppreference.com/w/cpp/c/wcstombs)
