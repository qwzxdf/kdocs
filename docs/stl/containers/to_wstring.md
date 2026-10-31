---
title: std::to_wstring
summary: "数値を wstring に変換する。"
order: 900
tags:
  - コンテナ
---

# std::to_wstring

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::to_string` の `wchar_t` 版が `std::to_wstring(x)` です。数値を `std::wstring` にします。Windows API に渡す文字列を、数値から組み立てるときに使います。

!!! tip "ポイント"
    - 整数や浮動小数点数を `std::wstring` に変換する
    - 浮動小数点数は `%f` の形式（小数点以下 6 桁）
    - 書式を指定したいなら `std::format(L"{:.2f}", x)`
    - ロケールの影響を受けることがある

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::to_wstring {#to_wstring}

<span class="ver ver-11">C++11</span>

```cpp
std::wstring to_wstring(int value);
std::wstring to_wstring(long value);
std::wstring to_wstring(long long value);
std::wstring to_wstring(unsigned value);
std::wstring to_wstring(double value);
// ほかの整数型、float、long double も
```

`to_string` と同じく、浮動小数点数は `1.500000` のように、小数点以下を 6 桁で出します。桁数を変えたいときは、`std::format` を使います。

結果は `std::wstring` で、`std::println` には直接渡せません。比較や連結に使い、画面に出すときは、UTF-8 に直すか、Windows API に渡します。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  const std::wstring a = std::to_wstring(42);
  const std::wstring b = std::to_wstring(-7);
  const std::wstring c = std::to_wstring(1.5);

  std::println("{}", a == L"42");
  std::println("{}", b == L"-7");
  std::println("{}", c == L"1.500000");
}
```

```text title="実行結果"
true
true
true
```

## ゲームでの使いどころ

Windows API のウィンドウ タイトルに、数値を入れるときに使います。

## よくあるミス

??? failure "浮動小数点数の桁数を指定できると思う"
    常に 6 桁です。`std::format` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::to_string` | `char` 版 |
| [`stol`](stol.md) | 文字列から整数へ |
| `std::format` | 書式を指定できる |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::to_wstring](https://cpprefjp.github.io/reference/string/to_wstring.html)
- [cppreference: std::to_wstring](https://en.cppreference.com/w/cpp/string/basic_string/to_wstring)
