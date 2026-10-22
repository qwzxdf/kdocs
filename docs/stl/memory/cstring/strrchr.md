---
title: std::strrchr
summary: "文字列の中から、指定した文字が最後に現れる位置を探す。"
order: 900
tags:
  - メモリ
---

# std::strrchr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

ファイルパスから拡張子や最後のフォルダ区切りを探すとき、先頭から探す `strchr` では最初の位置しか分かりません。`strrchr` は**最後に現れる**位置を返します。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strrchr {#strrchr}

```cpp
const char* strrchr(const char* str, int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 探す文字列 |
| `ch` | int | 探す文字（`'\0'` も探せる） |

- 戻り値: 見つかった位置のポインタ。なければ `nullptr`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* path = "a/b/c.txt";
  const char* name = std::strrchr(path, '/') + 1;
  std::println("{}", name);
}
```

```text title="実行結果"
c.txt
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | パスからファイル名を取り出す |

## よくあるミス

??? failure "見つからないのに +1 する"
    戻り値が `nullptr` のときに `+ 1` すると、不正なポインタになります。必ず `nullptr` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strchr`](strchr.md) | 最初に現れる位置 |
| [`std::filesystem::path`](../../io/filesystem/path.md) | パスの扱いはこちら |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列の中から、指定した文字が最後に現れる位置を探す
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strrchr](https://cpprefjp.github.io/reference/cstring/strrchr.html)
- [cppreference: std::strrchr](https://en.cppreference.com/w/cpp/string/byte/strrchr)
