---
title: std::mbtowc
summary: "マルチバイト文字 1 文字を wchar_t に変換する。"
order: 900
tags:
  - 数値
---

# std::mbtowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

ロケールのマルチバイト文字を、ワイド文字（`wchar_t`）1 文字に変換します。内部の状態を使うので、スレッドセーフではありません。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::mbtowc {#mbtowc}

```cpp
int mbtowc(wchar_t* pwc, const char* s, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pwc` | wchar_t* | 変換結果の書き込み先 |
| `s` | const char* | 変換元のバイト列 |
| `n` | size_t | 調べる最大のバイト数 |

- 戻り値: 使ったバイト数。不正なら -1
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  wchar_t w = 0;
  int n = std::mbtowc(&w, "A", 1);
  std::println("{} {}", n, static_cast<int>(w));
}
```

```text title="実行結果"
1 65
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
    - [x] マルチバイト文字 1 文字を wchar_t に変換する
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::mbtowc](https://cpprefjp.github.io/reference/cstdlib/mbtowc.html)
- [cppreference: std::mbtowc](https://en.cppreference.com/w/cpp/c/mbtowc)
