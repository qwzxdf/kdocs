---
title: std::wfstream
summary: "`wchar_t` のファイルストリーム。"
order: 900
tags:
  - 入出力・文字列
---

# std::wfstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <fstream>`
</div>

`std::wfstream` は、`fstream` の `wchar_t` 版です。ファイルを `wchar_t` の単位で読み書きします。文字コードの変換が絡むので、新しいコードでは UTF-8 のバイト列を `ifstream`・`ofstream` で扱うほうが一般的です。

!!! tip "ポイント"
    - `fstream` の `wchar_t` 版。
    - `wstring` を扱う。
    - ゲームでは UTF-8 の `string` を使うことが多い。

!!! info "このページを読む前に"
    [`std::fstream`](fstream.md) を先に読んでください。

## 関数の詳しい説明

### std::wfstream {#wfstream}

```cpp
using wfstream = basic_fstream<wchar_t>;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <fstream>
#include <print>

int main() {
  std::wfstream fs;
  std::println("{}", fs.is_open());
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Windows API と文字列をやり取りする | `std::wfstream` |

## よくあるミス

??? failure "文字コードを考えない"
    `wchar_t` は Windows では UTF-16、Linux では UTF-32 です。環境で意味が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fstream`](fstream.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wchar_t` のファイルストリーム
    - [x] fstream の wchar_t 版
    - [x] UTF-8 の string が主流

## 関連ページ

- [cpprefjp: std::wfstream](https://cpprefjp.github.io/reference/fstream/wfstream.html)
- [cppreference: std::wfstream](https://en.cppreference.com/w/cpp/io/wfstream)
