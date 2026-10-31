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

文字列を別の配列にコピーしたい。`std::strcpy(dst, src)` は、`src` の終端までを `dst` にコピーします。ただしコピー先の大きさを確かめないので、`src` が長いとバッファ オーバーランを起こします。セキュリティ上の事故の定番の原因で、新しいコードでは使いません。

!!! tip "ポイント"
    - 終端の `'\0'` までコピーする
    - コピー先の大きさを調べない。`strlen(src) + 1` 要素が要る
    - 領域が重なると未定義動作
    - MSVC は警告（C4996）を出す。`std::string` か `snprintf` に置き換える

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strcpy {#strcpy}

```cpp
char* strcpy(char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | コピー先 |
| `src` | `const char*` | コピー元 |

戻り値は `dest` です。

コピー先が小さいと、配列の外を上書きします。スタックの他の変数や戻りアドレスを壊すので、攻撃に悪用されます。入力が外から来る場合は、特に危険です。

安全に書くなら、`std::string` に代入するか、大きさを渡せる `snprintf(dst, sizeof(dst), "%s", src)` を使います。`strncpy` は、終端を付けないことがあり、別の落とし穴があります。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char dst[8];
  std::strcpy(dst, "abc");  // "abc" は終端を含めて 4 バイト。8 に収まる
  std::println("{}", dst);
  std::println("長さ: {}", std::strlen(dst));
}
```

```text title="実行結果"
abc
長さ: 3
```

## ゲームでの使いどころ

古い C のコードを読むときに出会います。新しく書くなら、`std::string` を使います。

## よくあるミス

??? failure "コピー先が小さい"
    `char name[4]` に 10 文字をコピーすると、領域の外を壊します。

??? failure "終端の分を数え忘れる"
    3 文字をコピーするには 4 要素が要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strncpy`](strncpy.md) | 長さを指定する。終端が付かないことがある |
| `std::string` | 大きさを自動で管理する |
| [`snprintf`](snprintf.md) | 大きさを指定して書き込める |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strcpy](https://cpprefjp.github.io/reference/cstring/strcpy.html)
- [cppreference: strcpy](https://en.cppreference.com/w/cpp/string/byte/strcpy)
