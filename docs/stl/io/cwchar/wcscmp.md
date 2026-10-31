---
title: std::wcscmp
summary: "2 つのワイド文字列を比べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcscmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

パスワードの照合や、アイテム名の一致の判定のように、2 つの文字列が同じかどうか、あるいはどちらが先に並ぶかを知りたい場面があります。`wchar_t` の文字列に対して、これを行うのが `wcscmp` です。`char` 版の `strcmp` と同じ働きで、先頭から 1 要素ずつ比べ、違う所が見つかった時点で結果を返します。

!!! tip "ポイント"
    - 戻り値は、`lhs < rhs` なら負、等しければ 0、`lhs > rhs` なら正。大きさは決まっていない
    - 一致の判定は `== 0`。`!wcscmp(a, b)` とも書く
    - 要素の値（UTF-16 の符号値）で比べる。辞書順や、言語ごとの並びではない
    - 言語に合わせた並べ替えは `wcscoll`（ロケールに従う）か、`std::collate`

!!! info "このページを読む前に"
    [`<cwchar>`](../cwchar.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::wcscmp {#wcscmp}

```cpp
int wcscmp(const wchar_t* lhs, const wchar_t* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs` | `const wchar_t*` | 比べる 1 つ目の文字列 |
| `rhs` | `const wchar_t*` | 比べる 2 つ目の文字列 |

先頭から順に、`wchar_t` の値を比べます。違う要素が見つかれば、その差の符号で結果が決まります。片方が先に終端に達したら、短いほうが小さいとされます。

戻り値の大きさには意味がありません。`-1`、`0`、`1` とは限らず、`-32` や `98` が返る環境もあります。符号だけを見て、`< 0`、`== 0`、`> 0` と比べます。

比べるのは文字の符号値なので、UTF-16 では、サロゲート ペアを含む文字列の並びが、実際の文字の並びと一致しないことがあります。日本語を五十音順に並べるような用途には、そのままでは向きません。

どちらかが終端のない配列だと、配列の外まで読んで、クラッシュします。`nullptr` を渡すのも未定義動作です。

C++ の `std::wstring` では、`==` や `<` で比べるので、`wcscmp` は不要です。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("同じ: {}", std::wcscmp(L"Hero", L"Hero") == 0);
  std::println("Hero < Mage: {}", std::wcscmp(L"Hero", L"Mage") < 0);
  std::println("Mage > Hero: {}", std::wcscmp(L"Mage", L"Hero") > 0);
  std::println("短いほうが小さい: {}", std::wcscmp(L"He", L"Hero") < 0);
}
```

```text title="実行結果"
同じ: true
Hero < Mage: true
Mage > Hero: true
短いほうが小さい: true
```

## ゲームでの使いどころ

Windows API から受け取った `wchar_t` の文字列が、特定の名前と一致するかを調べるときに使います。自分のコードでは `std::wstring` に入れて `==` で比べます。

## よくあるミス

??? failure "戻り値を 1 や -1 と比べる"
    `wcscmp(a, b) == -1` は、環境によって成り立ちません。`< 0` と書きます。

??? failure "ポインタどうしの == で比べる"
    `if (a == b)` は、文字列の中身ではなく、アドレスの比較です。中身を比べるには `wcscmp` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| `wcsncmp` | 先頭の n 要素だけ比べる |
| `wcscoll` | ロケールの並び順で比べる |
| `strcmp` | `char` 版 |
| [`std::wstring`](../../containers/string.md) | `==` と `<` で比べられる。普段はこちら |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcscmp` は、2 つのワイド文字列を要素の値で比べる
    - [x] 戻り値は符号だけを見る。一致は `== 0`
    - [x] C++ では `std::wstring` の `==` で足りる

## 関連ページ

- [cpprefjp: wcscmp](https://cpprefjp.github.io/reference/cwchar/wcscmp.html)
- [cppreference: wcscmp](https://en.cppreference.com/w/cpp/string/wide/wcscmp)
