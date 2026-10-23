---
title: std::locale
summary: "言語・地域ごとの書式（小数点、通貨、日付）の設定。"
order: 95
tags:
  - 入出力・文字列
---

# std::locale

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <locale>`
</div>

`std::locale` は、**言語や地域ごとの書式（小数点が「.」か「,」か、通貨、日付の形）の設定**を表すクラスです。ストリームに `imbue` すると、その設定で数値などが出力されます。`std::locale::classic()` は、地域に依存しない「C」ロケールです。ゲームでは、プログラムの動作が環境で変わらないよう、**数値の入出力は「C」ロケールに固定する**のが安全です。

!!! tip "ポイント"
    - 既定のロケールは、プログラム起動時は「C」。
    - ストリームの `imbue` で変更できる。
    - ファイルやネットワークのデータは、地域に依存しない形式（C ロケール）で読み書きする。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::locale {#locale}

```cpp
class locale {
 public:
  static const locale& classic();
  std::string name() const;
};
```

- 戻り値: （クラス）
- 計算量: O(1)

```cpp
#include <locale>
#include <print>

int main() {
  std::println("{}", std::locale::classic().name());
}
```

```text title="実行結果"
C
```

### name {#name}

```cpp
std::string name() const;
```

- 計算量: 定数

ロケールの名前（`"C"`・`"ja_JP.UTF-8"` など）。名前のないロケールは `"*"`。

### classic {#classic}

```cpp
static const locale& classic();
```

- 計算量: 定数

クラシックロケール（`"C"` ロケール）への参照。言語に依存しない、標準の振る舞いです。

### global {#global}

```cpp
static locale global(const locale& loc);
```

- 計算量: 定数

プログラム全体の既定のロケールを設定し、それまでのロケールを返します。これ以降に作るストリームは、このロケールを使います。

### combine {#combine}

```cpp
template <class Facet>
locale combine(const locale& other) const;
```

- 計算量: 定数

ほかのロケールから、`Facet`（部品）だけを取り込んだ、新しいロケールを作ります。

### operator() {#op_call}

```cpp
template <class CharT, class Traits, class Alloc>
bool operator()(const std::basic_string<CharT, Traits, Alloc>& s1, const std::basic_string<CharT, Traits, Alloc>& s2) const;
```

- 計算量: O(長さ)

ロケールの照合順（`collate`）で、2 つの文字列を比べます。`std::sort(v.begin(), v.end(), std::locale("ja_JP"))` のように、比較関数として渡せます。

### operator== {#op_eq}

```cpp
bool operator==(const locale& other) const;
```

- 計算量: 定数

同じロケールなら `true`。

### operator!= {#operator}

```cpp
bool operator!=(const locale& other) const;
```

- 計算量: 定数

違うロケールなら `true`（C++20 では `==` から自動で導かれる）。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小数の入出力を、環境に依存させない | `stream.imbue(std::locale::classic())` |

## よくあるミス

??? failure "環境のロケールで数値を保存する"
    ヨーロッパ設定の PC で「1,5」と書かれ、読み込みで壊れます。保存は C ロケールにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../utilities/format.md) | `L` 指定でロケールを使う（既定は使わない） |

## コンパイラ対応

C 由来の機能です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 地域ごとの書式の設定
    - [x] 保存は C ロケールで
    - [x] `classic()` が C ロケール

## 関連ページ

- [cpprefjp: std::locale](https://cpprefjp.github.io/reference/locale/locale.html)
- [cppreference: std::locale](https://en.cppreference.com/w/cpp/locale/locale)
