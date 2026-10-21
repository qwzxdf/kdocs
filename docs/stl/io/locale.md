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
