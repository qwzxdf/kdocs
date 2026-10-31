---
title: std::bad_any_cast
summary: "any_cast で、入っている型と違う型を取り出したときの例外。"
order: 900
tags:
  - ユーティリティ
---

# std::bad_any_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <any>`
</div>

`std::any_cast<T>(a)` で、`any` が持っている型と違う型を指定すると、失敗します。そのとき投げられる例外が `std::bad_any_cast` です。`std::bad_cast` の派生クラスで、`catch (const std::bad_cast&)` でも捕まえられます。

!!! tip "ポイント"
    - 値を取り出す形の `any_cast` が、型の不一致のときに投げる
    - ポインタを返す形では、例外ではなく `nullptr` を返す
    - `what()` のメッセージは、実装ごとに違う
    - 型が確実でないなら、ポインタ版で調べる

!!! info "このページを読む前に"
    [`std::any_cast`](any_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_any_cast {#bad_any_cast}

<span class="ver ver-17">C++17</span>

```cpp
class bad_any_cast : public std::bad_cast {
 public:
  const char* what() const noexcept override;
};
```

`any` が空のとき、または入っている型と違う型を指定したときに、`any_cast` が投げます。例外のオブジェクトは、原因（どの型を期待し、何が入っていたか）を持ちません。メッセージ以外の情報がないので、ログに残したいときは、`any::type()` で入っている型の名前を調べます。

```cpp
std::println("入っている型: {}", a.type().name());
```

型の名前は、実装により分かりにくい形（MSVC では `int`、GCC では `i` など）で出ます。

## 実際に動かしてみる

```cpp
#include <any>
#include <print>
#include <string>
#include <typeinfo>

int main() {
  std::any a = 42;

  try {
    std::string s = std::any_cast<std::string>(a);
  } catch (const std::bad_any_cast&) {
    std::println("bad_any_cast を捕まえた");
  }

  // 親クラスの bad_cast でも捕まえられる
  try {
    std::any_cast<double>(a);
  } catch (const std::bad_cast&) {
    std::println("bad_cast としても捕まえられる");
  }

  // 空の any でも投げる
  std::any empty;
  try {
    std::any_cast<int>(empty);
  } catch (const std::bad_any_cast&) {
    std::println("空でも失敗する");
  }
}
```

```text title="実行結果"
bad_any_cast を捕まえた
bad_cast としても捕まえられる
空でも失敗する
```

## ゲームでの使いどころ

イベント システムで、`any` の型を取り違えたときに、例外ではなくログを出して無視する、といった処理を `catch` で書きます。

## よくあるミス

??? failure "例外を使わずに済む場面で catch に頼る"
    型が複数ありうるなら、ポインタ版の `any_cast<T>(&a)` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::any_cast`](any_cast.md) | これを投げる関数 |
| `std::bad_cast` | 親クラス |
| `std::bad_variant_access` | `variant` の同様の例外 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::bad_any_cast](https://cpprefjp.github.io/reference/any/bad_any_cast.html)
- [cppreference: std::bad_any_cast](https://en.cppreference.com/w/cpp/utility/bad_any_cast)
