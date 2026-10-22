---
title: std::wcscpy
summary: "ワイド文字列をコピーする。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcscpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`strcpy` の `wchar_t` 版です。コピー先の大きさを確かめないので、あふれる危険があります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wcscpy {#wcscpy}

```cpp
wchar_t* wcscpy(wchar_t* dest, const wchar_t* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | wchar_t* | コピー先（十分な大きさ） |
| `src` | const wchar_t* | コピー元 |

- 戻り値: `dest`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  wchar_t dst[8];
  std::wcscpy(dst, L"abc");
  std::println("{}", std::wcslen(dst));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （古い C のコードの保守） |

## よくあるミス

??? failure "コピー先が小さい"
    あふれると未定義動作です。`std::wstring` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcpy`](../../memory/cstring/strcpy.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字列をコピーする
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcscpy](https://cpprefjp.github.io/reference/cwchar/wcscpy.html)
- [cppreference: std::wcscpy](https://en.cppreference.com/w/cpp/string/wide/wcscpy)
