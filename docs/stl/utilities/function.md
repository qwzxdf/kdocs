---
title: std::function
summary: "関数・ラムダ式を変数に入れて持つ。コールバックの保存に。"
order: 50
tags:
  - ユーティリティ
---

# std::function

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <functional>`
</div>

ボタンを押したときの処理、イベントが来たときの処理、ステートごとの更新処理。ゲームには、「あとで呼んでほしい処理」をデータとして持ちたい場面が多くあります。関数ポインターは、ラムダ式の中身（キャプチャ）を持てません。`std::function` は、呼び出せるものなら何でも入れておける変数です。普通の関数、ラムダ式、メンバー関数を呼ぶ関数オブジェクトなど、引数と戻り値の形が同じなら同じ型に入ります。

!!! tip "ポイント"
    - <strong>コールバック（あとで呼んでほしい処理）を保存するときに使う。</strong> `std::function<void()> on_click;`
    - 型は `std::function<戻り値(引数...)>`。
    - 空のまま呼ぶと例外になる。呼ぶ前に `if (f)` で確認する。
    - その場で渡してすぐ呼ぶだけなら、テンプレートや `auto` 引数のほうが速い。
    - ムーブだけできればいいなら C++23 の `std::move_only_function` もある。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) を先に読んでください。

## 宣言

```cpp
template <class R, class... Args>
class function<R(Args...)>;
```

| テンプレート引数 | 意味 | 例 |
| --- | --- | --- |
| `R(Args...)` | 「戻り値の型(引数の型...)」の形 | `void()`、`int(int, int)`、`bool(const Enemy&)` |

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [代入 / 作る](#assign) | <span class="rank rank-must">必須</span> | 関数・ラムダを入れる |
| [`operator()`](#call) | <span class="rank rank-must">必須</span> | 中の関数を呼ぶ |
| [`operator bool`](#bool) | <span class="rank rank-must">必須</span> | 何か入っているか |
| [`= nullptr`](#reset) | <span class="rank rank-sometimes">たまに</span> | 空にする |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 |
| [`target`](#target) | <span class="rank rank-rare">知ってるだけ</span> | 中に入っている関数を取り出す |

## よくある使い方

### 1. ボタンのコールバック

```cpp
#include <functional>
#include <print>
#include <string>
#include <utility>
#include <vector>

class Button {
 public:
  Button(std::string label, std::function<void()> on_click)
      : label_(std::move(label)), on_click_(std::move(on_click)) {}

  void Click() const {
    if (on_click_) {
      on_click_();
    }
  }

 private:
  std::string label_;
  std::function<void()> on_click_;
};

int main() {
  int volume = 5;
  std::vector<Button> buttons;
  buttons.emplace_back("+", [&volume] { ++volume; });
  buttons.emplace_back("-", [&volume] { --volume; });

  buttons[0].Click();
  buttons[0].Click();
  buttons[1].Click();
  std::println("音量 {}", volume);
}
```

```text title="実行結果"
音量 6
```

### 2. イベントの購読

```cpp
#include <functional>
#include <print>
#include <vector>

class DeathEvent {
 public:
  void Subscribe(std::function<void(int)> handler) { handlers_.push_back(std::move(handler)); }

  void Emit(int enemy_id) const {
    for (const auto& handler : handlers_) {
      handler(enemy_id);
    }
  }

 private:
  std::vector<std::function<void(int)>> handlers_;
};

int main() {
  int score = 0;
  DeathEvent on_death;
  on_death.Subscribe([&score](int) { score += 100; });
  on_death.Subscribe([](int id) { std::println("敵 {} が倒れた", id); });

  on_death.Emit(7);
  std::println("スコア {}", score);
}
```

```text title="実行結果"
敵 7 が倒れた
スコア 100
```

## 関数の詳しい説明

### 代入 / 作る {#assign}

```cpp
template <class F>
function(F&& f);
template <class F>
function& operator=(F&& f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出せるもの | 普通の関数、ラムダ式、関数オブジェクトなど。引数と戻り値の型が合う必要がある |

<div class="anim" data-label="f = other">
f1 # f は f1 を持っている
xf1 # 今の関数を破棄する
+f2 # 新しい関数を持つ
</div>

```cpp
#include <functional>
#include <print>

int Double(int x) { return x * 2; }

struct Triple {
  int operator()(int x) const { return x * 3; }
};

int main() {
  std::function<int(int)> f = Double;  // 普通の関数
  std::println("{}", f(5));
  f = [](int x) { return x * x; };  // ラムダ式
  std::println("{}", f(5));
  f = Triple{};  // 関数オブジェクト
  std::println("{}", f(3));
}
```

```text title="実行結果"
10
25
9
```

### operator() {#call}

```cpp
R operator()(Args... args) const;
```

- 中に入っている関数を呼びます
- **空のときに呼ぶと `std::bad_function_call` 例外**

### operator bool {#bool}

```cpp
explicit operator bool() const noexcept;
```

- 何か入っていれば `true`

```cpp
#include <functional>
#include <print>

int main() {
  std::function<void()> callback;
  std::println("入っている？ {}", static_cast<bool>(callback));
  callback = [] { std::println("呼ばれた"); };
  if (callback) {
    callback();
  }
}
```

```text title="実行結果"
入っている？ false
呼ばれた
```

### = nullptr {#reset}

```cpp
function& operator=(std::nullptr_t) noexcept;
```

- 中身を消して空にします

<div class="anim" data-label="f = nullptr">
f1 # f は f1 を持っている
xf1 # 関数を破棄する
_ # 空。呼ぶと std::bad_function_call
</div>

```cpp
#include <functional>
#include <print>

int main() {
  std::function<void()> f = [] {};
  f = nullptr;
  std::println("{}", static_cast<bool>(f));
}
```

```text title="実行結果"
false
```

### swap {#swap}

```cpp
void swap(function& other) noexcept;
```

- 中身を交換します

### target {#target}

```cpp
template <class T>
T* target() noexcept;
```

- 中に入っている関数が `T` 型なら、そのポインタを返します（違えば `nullptr`）。ほぼ使いません

## フラグ・オプション

フラグはありません。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    typedef void (*Callback)(void* user_data);  // 関数ポインタ + void*
    void SetCallback(Callback cb, void* user_data);
    ```

=== "今の書き方"

    ```cpp
    void SetCallback(std::function<void()> cb);  // ラムダで状態ごと渡せる
    ```

### target_type {#target_type}

```cpp
const std::type_info& target_type() const noexcept;
```

- 計算量: 定数

中に入っている呼び出し可能なものの型情報（`typeid`）。空なら `typeid(void)`。

### operator= {#op_assign}

```cpp
function& operator=(function&& other);
function& operator=(const function& other);
template <class F> function& operator=(F&& f);
function& operator=(std::nullptr_t) noexcept;
```

- 計算量: 中身による

ほかの `function`・関数・ラムダなどを代入します。`nullptr` を代入すると空になります。

## ゲームでの使いどころ

コールバックの保存が基本です。`std::function<void()> on_click;` というメンバーを持たせ、UI のボタンを押したときに `on_click()` を呼びます。ボタンを作る側が、押したときの処理をラムダ式で渡します。

イベントの購読では、`vector<std::function<void(const Event&)>>` に登録して、イベントが起きたら全部を呼びます。

ただし、`std::function` は呼び出すたびに少しコストがかかり、中身が大きいとヒープを使います。毎フレーム何千回も呼ぶ処理には向きません。その場で渡してすぐ呼ぶだけなら、テンプレートや `auto` の引数のほうが速くなります。

## パフォーマンス

- 呼び出しは仮想関数のような間接呼び出しになるので、普通の関数呼び出しより少し遅いです。
- ラムダが大きな値をキャプチャしていると、**ヒープ確保**が起きることがあります（小さければ中に直接入る）。
- 毎フレーム何万回も呼ぶ処理には向きません。その場合はテンプレートで受け取るか、仮想関数や switch を使います。

```cpp
// その場で呼ぶだけならテンプレート（auto 引数）のほうが速い
void ForEachEnemy(auto&& func) {
  for (auto& e : enemies_) {
    func(e);
  }
}
```

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空のまま呼ぶ | `std::bad_function_call` 例外 |
| 参照でキャプチャした変数が消えたあとに呼ぶ | 未定義動作 |

## よくあるミス

??? failure "参照キャプチャした変数が先に消える"
    ```cpp
    std::function<void()> MakeCallback() {
      int count = 0;
      return [&count] { ++count; };  // count は関数を抜けると消える
    }
    ```

    保存するコールバックでは、値でキャプチャする（`[count]`）か、寿命の長いものだけを参照します。

??? failure "unique_ptr をキャプチャして入らない"
    `std::function` はコピーできる必要があるので、`unique_ptr` をムーブキャプチャしたラムダは入りません。C++23 の `std::move_only_function` を使います。

## 類似

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| `std::move_only_function` | コピー不可だが、unique_ptr をキャプチャできる <span class="ver ver-23">C++23</span> | ムーブだけでいいコールバック |
| `std::function_ref` | 持たずに借りるだけ（C++26） | 引数でその場で呼ぶだけ |
| 関数ポインタ | 状態（キャプチャ）を持てない。速い | C の API |
| テンプレート / `auto` 引数 | 呼び出しが速い。保存できない | その場で呼ぶだけ |
| 仮想関数 | クラスの継承で切り替える | 振る舞いが型ごとに決まっている |

## コンパイラ対応

C++11 からある機能です。`std::move_only_function` は C++23（GCC 12 / MSVC 17.2 以降。libc++ は未対応）です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「あとで呼ぶ処理」を変数に入れて持つ。
    - [x] 空のまま呼ぶと例外。呼ぶ前に `if (f)` で確認する。
    - [x] 毎フレーム大量に呼ぶ処理には、テンプレートのほうが速い。

## 関連ページ

- [cpprefjp: std::function](https://cpprefjp.github.io/reference/functional/function.html)
- [cppreference: std::function](https://en.cppreference.com/w/cpp/utility/functional/function)
