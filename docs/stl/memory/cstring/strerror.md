---
title: std::strerror
summary: "エラー番号（errno）を、説明の文字列にする。"
order: 900
tags:
  - メモリ
---

# std::strerror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cerrno>`
</div>

`errno` の数値だけでは原因が分かりません。`strerror(errno)` で、「No such file or directory」のような説明が得られます。文字列は処理系が決め、静的な領域にあるので、スレッドで使うときは `strerror_s` などを使います。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strerror {#strerror}

```cpp
char* strerror(int errnum);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `errnum` | int | エラー番号（`errno` の値） |

- 戻り値: 説明の文字列（静的な領域。書き換え禁止）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cerrno>
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strerror(ENOENT) != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルを開けなかった理由をログに出す |

## よくあるミス

??? failure "戻り値を保存して使い回す"
    次の呼び出しで上書きされることがあります。すぐコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`errno`](../../io/cerrno.md) | エラー番号 |
| [`std::error_code`](../../support/error_code.md) | C++ のエラー表現 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エラー番号（errno）を説明の文字列にする
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strerror](https://cpprefjp.github.io/reference/cstring/strerror.html)
- [cppreference: std::strerror](https://en.cppreference.com/w/cpp/string/byte/strerror)
