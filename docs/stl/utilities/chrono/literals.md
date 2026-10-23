---
title: std::chrono_literals
summary: "16ms、2s のように、単位つきの時間を書けるリテラル。"
order: 8
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono_literals

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-14">C++14</span>
`#include <chrono>`
</div>

`sleep_for(16)` と書いたとき、これがミリ秒なのか、マイクロ秒なのか、コードを読んだだけでは分かりません。単位を取り違えて、思ったより何千倍も待ってしまうバグもあります。`std::chrono_literals` を使うと、`16ms`、`2s`、`1.5min` のように、数値の後ろに単位を付けて `duration` を書けます。`using namespace std::chrono_literals;` と書くと使えます。

!!! tip "ポイント"
    - `ns`（ナノ秒）、`us`（マイクロ秒）、`ms`（ミリ秒）、`s`（秒）、`min`（分）、`h`（時）が使える。
    - 整数リテラルは整数の `duration`（`2s` は `seconds`）、小数は `double` の `duration`（`1.5s`）。
    - 日付用に `y`（年）、`d`（日）もある（C++20）。

!!! info "このページを読む前に"
    [`std::chrono::duration`](duration.md) が分かると読みやすいです。リテラルは、`duration` を短く書く書き方です。

## 関数の詳しい説明

### ms, s, min, h など {#literals}

```cpp
namespace std::chrono_literals {
constexpr chrono::milliseconds operator""ms(unsigned long long);
constexpr chrono::duration<double, milli> operator""ms(long double);
// ns, us, ms, s, min, h も同じ形
}
```

- 戻り値: 対応する `duration`
- 計算量: コンパイル時

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;

  auto frame = 16ms;     // milliseconds
  auto timeout = 2s;     // seconds
  auto fine = 1.5s;      // duration<double>（小数の秒）

  std::println("{} {}", frame + timeout, fine);
}
```

```text title="実行結果"
2016ms 1.5s
```

## しくみ

`16ms` は、`operator""ms(16)` という関数を呼びます。この関数が `std::chrono::milliseconds(16)` を返します。整数のリテラルは、整数の `duration`（`2s` は `seconds`）になり、小数のリテラルは `double` の `duration`（`1.5s` は `duration<double>`）になります。

使える単位は、`ns`（ナノ秒）、`us`（マイクロ秒）、`ms`（ミリ秒）、`s`（秒）、`min`（分）、`h`（時）です。C++20 では、日付用の `d`（日）と `y`（年）も加わりました。

`using namespace std::chrono_literals;` は、関数の中や、自分の名前空間の中に書きます。ヘッダーファイルの先頭の、グローバルな場所には書かないようにします。

## ゲームでの使いどころ

待ち時間の指定に使います。`std::this_thread::sleep_for(16ms)` と書くと、単位が一目で分かります。タイムアウトの判定は `now - start > 5s` と読みやすくなります。

ゲームの設定値に使うと、単位の取り違えが減ります。`constexpr auto kCooldown = 500ms;` とすれば、クールダウンの長さが明確です。

デルタタイムを秒の `float` で受けたいときは、`duration<float>` に代入します。`std::chrono::duration<float> dt = 16ms;` で `0.016` 秒です。

## よくあるミス

??? failure "`using namespace` をヘッダーの先頭に書く"
    ヘッダーに書くと、そのヘッダーを読み込むすべてのファイルに影響します。名前の衝突が起きることがあるので、関数の中か `.cpp` の中に書きます。

??? failure "`1.5s` を整数の `duration` だと思う"
    `1.5s` は `double` の `duration` です。`seconds` 型の変数には、そのまま代入できません。`duration_cast<seconds>` を使うか、`duration<double>` で受けます。

??? failure "`min` が `std::min` と衝突する"
    `using namespace std;` と一緒に使うと、`min` が名前の衝突を起こす場面があります。`std::chrono_literals` だけを `using` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | リテラルが作る型 |
| `std::chrono::milliseconds` | リテラルを使わずに書く場合の型名 |
| [`duration_cast`](duration_cast.md) | 単位を変換する |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `16ms`、`2s` のように、数値の後ろに単位を付ける。
    - [x] `using namespace std::chrono_literals;` は、ヘッダーの先頭に書かない。
    - [x] 小数のリテラルは `double` の `duration`。

## 関連ページ

- [cpprefjp: std::chrono_literals](https://cpprefjp.github.io/reference/chrono/duration/op_ms.html)
- [cppreference: std::literals::chrono_literals](https://en.cppreference.com/w/cpp/chrono/duration/operator%22%22ms)
