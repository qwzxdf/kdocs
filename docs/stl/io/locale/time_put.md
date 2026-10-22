---
title: std::time_put
summary: "日時を、書式に従って文字列に書き出すファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_put

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`put_time` が内部で使っているのが `time_put` です。ロケールの規則（曜日・月の名前など）に従って、`tm` を `strftime` 風の書式で出力します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::time_put {#time_put}

```cpp
template <class CharT, class OutIt = ostreambuf_iterator<CharT>>
class time_put {
 public:
  OutIt put(OutIt out, std::ios_base& str, CharT fill, const std::tm* t, const CharT* fmt_first, const CharT* fmt_last) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き出し先 |
| `t` | const tm* | 書く日時 |
| `fmt_first, fmt_last` | ポインタ | 書式の範囲 |

- 戻り値: 書き終えた後の出力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::tm t{};
  t.tm_year = 124;
  t.tm_mon = 0;
  t.tm_mday = 1;
  std::ostringstream os;
  const std::string fmt = "%Y-%m-%d";
  std::use_facet<std::time_put<char>>(std::locale::classic()).put(std::ostreambuf_iterator<char>(os), os, ' ', &t, fmt.data(), fmt.data() + fmt.size());
  std::println("{}", os.str());
}
```

```text title="実行結果"
2024-01-01
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロケールに従った日時の出力 |

## よくあるミス

??? failure "直接使う"
    ふつうは `std::put_time` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_time`](../put_time.md) | ストリームに書く |
| [`time_get`](time_get.md) | 読み込み側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日時を、書式に従って文字列に書き出すファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::time_put](https://cpprefjp.github.io/reference/locale/time_put.html)
- [cppreference: std::time_put](https://en.cppreference.com/w/cpp/locale/time_put)
