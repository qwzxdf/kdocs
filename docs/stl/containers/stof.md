---
title: std::stof
summary: "文字列を float に変換する（失敗すると例外）。"
order: 62
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stof

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stof` は、**文字列を `float` に変換する**関数です。[`stoi`](stoi.md) の小数版で、失敗すると例外を投げます。`double` なら [`stod`](stod.md) です。

!!! tip "ポイント"
    - `"0.25"` や `"1e3"` のような形式も読める。
    - 失敗は例外。
    - ロケールの影響を受ける（地域によって小数点が違う）。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stof {#stof}

```cpp
float stof(const std::string& str, std::size_t* pos = nullptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 変換する文字列 |
| `pos` | `std::size_t*` | 変換に使った文字数を受け取る |

- 例外: `stoi` と同じ

```cpp
#include <print>
#include <string>

int main() {
  float gravity = std::stof("9.8");
  std::println("{}", gravity * 2.0f);
}
```

```text title="実行結果"
19.6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの小数の読み込み | `float rate = std::stof("0.25");` |

## よくあるミス

??? failure "ロケールで小数点が「,」になる環境"
    `stof` は現在のロケールに従います。固定したいなら `from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../io/from_chars.md) | ロケールに依存しない |
| [`stod`](stod.md) | double |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → float
    - [x] 失敗は例外
    - [x] ロケールに依存する

## 関連ページ

- [cpprefjp: std::stof](https://cpprefjp.github.io/reference/string/stof.html)
- [cppreference: std::stof](https://en.cppreference.com/w/cpp/string/basic_string/stof)
