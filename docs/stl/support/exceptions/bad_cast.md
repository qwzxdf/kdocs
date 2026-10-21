---
title: std::bad_cast
summary: "参照の `dynamic_cast` が失敗したときの例外。"
order: 15
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <typeinfo>`
</div>

`std::bad_cast` は、**参照に対する `dynamic_cast` が失敗した**ときに投げられる例外です。ポインターへの `dynamic_cast` は失敗すると `nullptr` を返しますが、参照にはヌルがないので、例外になります。

!!! tip "ポイント"
    - ポインターは `nullptr`、参照は `bad_cast` 例外。
    - 例外を避けたいなら、ポインターにキャストして `nullptr` を確認する。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_cast {#bad_cast}

```cpp
class bad_cast : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: （例外クラス）。`what()` でメッセージ
- 計算量: O(1)

```cpp
#include <print>
#include <typeinfo>

struct Base {
  virtual ~Base() = default;
};
struct Derived : Base {};
struct Other : Base {};

int main() {
  Derived d;
  Base& b = d;
  try {
    Other& o = dynamic_cast<Other&>(b);
    (void)o;
  } catch (const std::bad_cast&) {
    std::println("キャスト失敗");
  }
}
```

```text title="実行結果"
キャスト失敗
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| エンティティの型を確かめて変換する | `dynamic_cast<Boss*>(entity)` を使い、`nullptr` を確認する |

## よくあるミス

??? failure "ポインターのつもりで例外を期待する"
    ポインターのキャストは例外を投げません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`typeid`](../typeid.md) | 型を調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 参照の dynamic_cast 失敗
    - [x] ポインターは nullptr
    - [x] ポインターのほうが扱いやすい

## 関連ページ

- [cpprefjp: std::bad_cast](https://cpprefjp.github.io/reference/typeinfo/bad_cast.html)
- [cppreference: std::bad_cast](https://en.cppreference.com/w/cpp/types/bad_cast)
