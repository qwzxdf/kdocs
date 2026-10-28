---
title: std::bind_back
summary: "関数の末尾の引数をあらかじめ決めた、新しい関数を作る。"
order: 10
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bind_back

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <functional>`
</div>

`std::bind_front` が先頭の引数を固定するのに対して、`std::bind_back(f, 引数...)` は、<strong>最後の引数を固定した関数オブジェクト</strong>を作ります。

!!! tip "ポイント"
    - `std::bind_back(f, a)` は、`f(残り..., a)` を呼ぶ関数オブジェクトを返す
    - `bind_front` の後ろ版
    - 範囲アダプターのパイプで使う関数を、簡単に作れる
    - C++23 で追加

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bind_back {#bind_back}

<span class="ver ver-23">C++23</span>

```cpp
template <class F, class... Args>
constexpr /* 関数オブジェクト */ bind_back(F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能なもの | 関数、ラムダなど |
| `args...` | 値 | 末尾に固定する引数 |

返る関数オブジェクトを呼ぶと、渡した引数に続けて、固定した引数が `f` に転送されます。

用途は、後ろの引数が決まっていて、前の引数を後から渡す場面です。たとえば、`Damage(attack, defense)` で防御力を固定して、攻撃力を後から渡す、といった使い方です。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Damage(int attack, int defense) { return attack - defense; }

int main() {
  auto against_armor = std::bind_back(Damage, 10);   // defense を 10 に固定
  std::println("攻撃 30: {}", against_armor(30));
  std::println("攻撃 15: {}", against_armor(15));
}
```

```text title="実行結果"
攻撃 30: 20
攻撃 15: 5
```

## ゲームでの使いどころ

末尾の引数を固定して、コールバックや範囲アダプターに渡します。

## よくあるミス

??? failure "C++20 のコンパイラで使えない"
    C++23 の機能です。ラムダ式で代用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_front`](bind_front.md) | 先頭の引数を固定 |
| [`bind`](bind.md) | 古い汎用の束縛 |

## コンパイラ対応

C++23 から使えます。GCC 13 以降、Clang 19 以降、Visual Studio 2022 17.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bind_back(f, a)` は末尾の引数を固定する
    - [x] `bind_front` の後ろ版
    - [x] C++23

## 関連ページ

- [cpprefjp: std::bind_back](https://cpprefjp.github.io/reference/functional/bind_back.html)
- [cppreference: std::bind_back](https://en.cppreference.com/w/cpp/utility/functional/bind_back)
