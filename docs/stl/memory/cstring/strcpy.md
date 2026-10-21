---
title: strcpy
summary: "C 文字列をコピーする（大きさを確認しない・危険）。"
order: 11
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strcpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strcpy` は、**C 文字列を別のバッファへコピーする**関数ですが、**コピー先の大きさを確認しません**。バッファより長い文字列を渡すと範囲外に書き込む（バッファオーバーフロー）ので、**新しく書くコードでは使いません**。

!!! tip "ポイント"
    - 代わりに `snprintf` や、`std::string` を使う。
    - MSVC では `strcpy_s` を使うよう警告が出る。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strcpy {#strcpy}

```cpp
char* strcpy(char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | コピー先（`src` の長さ + 1 以上の大きさが必要） |
| `src` | `const char*` | コピー元の C 文字列 |

- 戻り値: `dest`
- <strong>コピー先の大きさを一切チェックしません。</strong> `src` が長いと、`dest` の後ろを壊します（バッファオーバーフロー）。セキュリティの穴の原因として有名です。**使ってはいけません**（MSVC は警告 C4996 を出します）
- `std::string` に入れるか、`snprintf` で大きさを指定します。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char dst[8];
  std::strcpy(dst, "abc");
  std::println("{}", dst);
}
```

```text title="実行結果"
abc
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解用 | 使わず、`snprintf(dst, sizeof(dst), "%s", src)` |

## よくあるミス

??? failure "コピー先が小さい"
    範囲外書き込みで、クラッシュや脆弱性になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strncpy`](strncpy.md) | 長さを指定するが、終端の問題がある |
| [`snprintf`](snprintf.md) | 安全な選択 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 使わない
    - [x] 大きさを確認しない
    - [x] 代わりに snprintf / std::string

## 関連ページ

- [cpprefjp: strcpy](https://cpprefjp.github.io/reference/cstring/strcpy.html)
- [cppreference: strcpy](https://en.cppreference.com/w/cpp/string/byte/strcpy)
