---
title: std::getenv
summary: "環境変数の値を取得する。"
order: 7
group: <cstdlib> の関数
tags:
  - 数値
---

# std::getenv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::getenv("名前")` は、**環境変数の値を文字列で返す**関数です。無ければ `nullptr` を返します。ツールやビルドスクリプトが設定した値（`ASSET_ROOT` など）を読むときに使います。Windows では `_dupenv_s` が推奨されます。

!!! tip "ポイント"
    - 無ければ `nullptr`。使う前に必ず確認する。
    - 返った文字列は書き換えない（コピーして使う）。
    - MSVC は `getenv` で警告が出る（`_dupenv_s` を使う）。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::getenv {#getenv}

```cpp
char* getenv(const char* name);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `name` | `const char*` | 環境変数の名前 |

- 戻り値: 値の文字列（無ければ `nullptr`）
- 計算量: O(1)

```cpp
#include <cstdlib>
#include <print>

int main() {
  const char* v = std::getenv("KDOCS_UNSET_VARIABLE_XYZ");
  std::println("{}", v == nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 環境変数でアセットの場所を切り替える | `std::getenv("ASSET_ROOT")` |

## よくあるミス

??? failure "nullptr を確認しない"
    無いときに使うとクラッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::filesystem::current_path`](../../io/filesystem/current_path.md) | 作業フォルダ |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 環境変数を読む
    - [x] 無ければ nullptr
    - [x] MSVC は警告

## 関連ページ

- [cpprefjp: std::getenv](https://cpprefjp.github.io/reference/cstdlib/getenv.html)
- [cppreference: std::getenv](https://en.cppreference.com/w/cpp/utility/program/getenv)
