---
title: typeid
summary: "式や型の「実際の型」を、実行時に調べる演算子。"
order: 10
group: 実行時の型情報（<typeinfo>）
tags:
  - 型・言語サポート
---

# typeid

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <typeinfo>`
</div>

`typeid` は、**式や型の型情報（`std::type_info`）を返す演算子**です。仮想関数を持つクラスのポインター・参照に使うと、**実際の（派生クラスの）型**が分かります。ただし、ゲームでは仮想関数やコンポーネントの ID で型を区別するのが普通で、`typeid` は主にデバッグに使います。

!!! tip "ポイント"
    - `typeid(*p) == typeid(Derived)` で、実際の型が分かる（基底クラスに仮想関数が必要）。
    - `typeid(x).name()` は実装依存の文字列（デバッグ表示用）。
    - RTTI を無効にするプロジェクトでは使えない。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### typeid {#typeid}

```cpp
const std::type_info& typeid(式または型);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `式 / 型` | 式または型 | 調べたいもの |

- 戻り値: `std::type_info` への参照
- 計算量: O(1)

```cpp
#include <print>
#include <typeinfo>

struct Base {
  virtual ~Base() = default;
};
struct Derived : Base {};

int main() {
  Derived d;
  Base& b = d;
  std::println("{} {}", typeid(b) == typeid(Derived), typeid(b) == typeid(Base));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグ時に、実際の型の名前を表示する | `typeid(*p).name()` |

## よくあるミス

??? failure "RTTI を切った環境で使う"
    `/GR-` や `-fno-rtti` では使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::type_info`](type_info.md) | 戻り値の型 |
| `dynamic_cast` | 型を調べて安全に変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実際の型を調べる
    - [x] 仮想関数が必要
    - [x] デバッグ向け

## 関連ページ

- [cpprefjp: typeid](https://cpprefjp.github.io/reference/typeinfo/type_info.html)
- [cppreference: typeid](https://en.cppreference.com/w/cpp/language/typeid)
