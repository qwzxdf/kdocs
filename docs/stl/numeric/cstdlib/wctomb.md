---
title: std::wctomb
summary: "wchar_t 1 文字をマルチバイト文字に変換する。"
order: 900
tags:
  - 数値
---

# std::wctomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

ワイド文字（`wchar_t`）1 文字を、ロケールのマルチバイト文字に変換します。バッファは `MB_CUR_MAX` バイト以上必要です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::wctomb {#wctomb}

```cpp
int wctomb(char* s, wchar_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | char* | 変換結果の書き込み先（`MB_CUR_MAX` バイト以上） |
| `wc` | wchar_t | 変換するワイド文字 |

- 戻り値: 書き込んだバイト数。変換できなければ -1
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <climits>
#include <cstdlib>
#include <print>

int main() {
  char buf[MB_LEN_MAX];
  int n = std::wctomb(buf, L'A');
  std::println("{}", n);
}
```

```text title="実行結果"
1
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
    - [x] wchar_t 1 文字をマルチバイト文字に変換する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wctomb](https://cpprefjp.github.io/reference/cstdlib/wctomb.html)
- [cppreference: std::wctomb](https://en.cppreference.com/w/cpp/c/wctomb)
