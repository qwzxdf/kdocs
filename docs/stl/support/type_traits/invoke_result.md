---
title: std::invoke_result
summary: "関数を呼んだときの、戻り値の型を調べる。"
order: 20
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::invoke_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

テンプレートの中で、「渡された関数を呼んだら、何型の値が返ってくるか」を知りたいことがあります。ジョブを投げて結果を受け取る `future` や、結果をためるコンテナの要素の型を決めたいときです。`std::invoke_result_t<F, Args...>` は、`F` を `Args...` で呼んだときの戻り値の型を返します。関数・ラムダ・メンバー関数ポインターを、まとめて同じ書き方で扱えます。

!!! tip "ポイント"
    - `invoke_result_t<F, Args...>` は、`std::invoke(f, args...)` の戻り値の型
    - 関数・関数オブジェクト・ラムダ・メンバー関数ポインター・データメンバーポインターのどれでも使える
    - 呼べない組み合わせだと、`invoke_result_t` は定義されない（SFINAE で外れる）
    - C++17 で追加。古い `std::result_of` は C++20 で削除された

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::invoke_result {#invoke_result}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... ArgTypes>
struct invoke_result;   // ::type が戻り値の型

template <class F, class... ArgTypes>
using invoke_result_t = typename invoke_result<F, ArgTypes...>::type;
```

| 引数 | 意味 |
| --- | --- |
| `F` | 呼び出すものの型。関数ポインター、ラムダの型、メンバー関数ポインターなど |
| `ArgTypes...` | 呼び出すときの引数の型。値のカテゴリー（左辺値・右辺値）も含めて渡す |

#### 引数の型の渡し方

`ArgTypes` には、呼び出すときの引数の「式の型」を渡します。左辺値の `int` 変数を渡すなら `int&`、右辺値なら `int` です。この違いで、オーバーロードの選び方が変わり、戻り値の型が変わる関数もあります。

#### メンバー関数ポインター

メンバー関数ポインターを呼ぶときは、最初の引数に、オブジェクトを渡します。`invoke_result_t<decltype(&Player::Speed), const Player&, int>` のように、`const Player&` を先頭に書きます。

#### 呼べないとき

呼べない組み合わせ（引数の数や型が合わない）では、`invoke_result<F, Args...>` は `type` を持ちません。`invoke_result_t` を直接使うとコンパイル エラーですが、テンプレートの制約の中では、その候補が静かに外れるので、オーバーロードを選り分ける道具に使えます。呼べるかどうかを `bool` で知りたいだけなら、[`is_invocable`](is_invocable.md) を使います。

#### result_of との関係

C++11 の `std::result_of<F(Args...)>` は、書き方が分かりにくく、C++20 で削除されました。`invoke_result_t<F, Args...>` に置き換えます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <type_traits>
#include <vector>

int Damage(int attack, int defense) { return attack - defense; }

struct Player {
  double Speed(int level) const { return level * 1.5; }
};

// 関数を 2 回呼んで、結果を vector にためる。要素の型は戻り値の型に合わせる
template <class F, class... Args>
std::vector<std::invoke_result_t<F, Args...>> RunTwice(F f, Args... args) {
  return {f(args...), f(args...)};
}

int main() {
  auto twice = [](int x) { return x * 2.0; };

  std::println("関数: {}", std::is_same_v<std::invoke_result_t<decltype(&Damage), int, int>, int>);
  std::println("ラムダ: {}", std::is_same_v<std::invoke_result_t<decltype(twice), int>, double>);
  std::println("メンバー関数: {}",
               std::is_same_v<std::invoke_result_t<decltype(&Player::Speed), const Player&, int>, double>);
  std::println("戻り値がない関数: {}", std::is_void_v<std::invoke_result_t<void (*)()>>);

  std::vector<int> results = RunTwice(Damage, 10, 3);
  std::println("RunTwice の結果: {}", results);
}
```

```text title="実行結果"
関数: true
ラムダ: true
メンバー関数: true
戻り値がない関数: true
RunTwice の結果: [7, 7]
```

## ゲームでの使いどころ

ジョブを投げて結果を受け取る `future` の型や、結果をためるコンテナの要素の型を、渡された関数から決めるときに使います。`std::async` や `std::packaged_task` の内部でも使われています。

## よくあるミス

??? failure "呼べない組み合わせで invoke_result_t を直接書く"
    コンパイル エラーになります。呼べるかを先に知りたいなら `is_invocable` を使います。

??? failure "引数に値のカテゴリーを付け忘れる"
    オーバーロードが左辺値と右辺値で分かれている関数では、`int` と `int&` で結果が変わります。

??? failure "result_of を使う"
    C++20 で削除されました。`invoke_result` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_invocable`](is_invocable.md) | 呼べるかを `bool` で返す |
| [`invoke`](../functional/invoke.md) | 実際に呼ぶ関数 |
| [`std::function`](../../utilities/function.md) | 呼び出せるものを保持する型 |

## コンパイラ対応

C++17 から使えます。`std::invoke_result_t` は、C++17 で追加された短縮形です。

## 関連ページ

- [cpprefjp: std::invoke_result](https://cpprefjp.github.io/reference/type_traits/invoke_result.html)
- [cppreference: std::invoke_result](https://en.cppreference.com/w/cpp/types/invoke_result)
