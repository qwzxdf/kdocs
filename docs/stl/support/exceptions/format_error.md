---
title: std::format_error
summary: "`std::format` の書式が不正なときの例外。"
order: 16
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::format_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format_error` は、**`std::vformat` などで、実行時に与えた書式の文字列が不正だった**ときに投げられる例外です。コンパイル時に決まる書式（`std::format("{}", x)`）は、コンパイル時にエラーになるので、この例外は出ません。

!!! tip "ポイント"
    - 実行時の書式（`vformat`）で出る。
    - `"{"` のように閉じていない書式、引数の数の不一致などが原因。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::format_error {#format_error}

```cpp
class format_error : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <format>
#include <print>

int main() {
  try {
    std::string s = std::vformat("{", std::make_format_args());  // 閉じていない
    (void)s;
  } catch (const std::format_error&) {
    std::println("書式が不正");
  }
}
```

```text title="実行結果"
書式が不正
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 翻訳テキストの書式が壊れていたときに、落ちずにログを出す | `catch (const std::format_error&)` |

## よくあるミス

??? failure "ユーザー入力を書式にする"
    意図しない展開や例外が起きます。入力は引数に渡し、書式にはしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::vformat`](../../utilities/vformat.md) | 実行時の書式 |
| [`std::format`](../../utilities/format.md) | コンパイル時に検査される |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式が不正なときの例外
    - [x] 実行時の書式で起きる
    - [x] ユーザー入力は書式にしない

## 関連ページ

- [cpprefjp: std::format_error](https://cpprefjp.github.io/reference/format/format_error.html)
- [cppreference: std::format_error](https://en.cppreference.com/w/cpp/utility/format/format_error)
