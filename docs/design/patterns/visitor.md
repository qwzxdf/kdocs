---
title: ビジター
tags:
  - 設計
---

# ビジター

**ビジター**（Visitor）は、**データの構造（クラスの種類）を変えずに、そのデータに対する新しい処理を、あとから足せる**ようにするパターンです。たとえば、ゲームの「式の木」（`1 + 2 * x` のようなスクリプトの数式）や、シーンの階層、AI のビヘイビア ツリーのような、**いろいろな種類のノードが並んだデータ**に、「画面に出す」「保存する」「評価する」など、**処理を何種類も足していきたい**とき、各ノードのクラスに関数を足し続けると、クラスが肥大化します。ビジターは、**処理のほうを別のオブジェクト（ビジター）として切り出す**ことで、それを避けます。

!!! tip "ポイント"
    - <strong>「データの種類が固定で、処理が増えていく」</strong>ときに向いている。逆（種類が増えていく）なら、普通の `virtual` 関数のほうが向く。
    - C++17 以降は、**`std::variant` + `std::visit`** で、簡単に書ける。**ほとんどの場合、これで十分**。
    - 古典的な書き方（`Accept` と `Visit`）は、**二重ディスパッチ**を使う。仮想関数が 2 回呼ばれる。
    - 処理ごとに、ビジターを 1 つ作る（`PrintVisitor`、`EvalVisitor`、`SaveVisitor`）。
    - 向いているのは、**木構造・AST・コマンドの種類・イベントの種類**など。

## 解く問題：種類が固定で、処理が増える

| データ（種類は、あまり増えない） | 画面に出す | 計算する（評価） | 保存する | 最適化する | 型を調べる |
| --- | --- | --- | --- | --- | --- |
| **Number** | ○ | ○ | ○ | ○ | ○ |
| **Add** | ○ | ○ | ○ | ○ | ○ |
| **Multiply** | ○ | ○ | ○ | ○ | ○ |

横（処理）は、どんどん増えます。種類 × 処理の組み合わせが、すべて必要です。

### 悪い例：処理が増えるたびに、全クラスを直す

```cpp
class Expr {
 public:
  virtual ~Expr() = default;
  virtual int Eval() const = 0;
  virtual std::string ToString() const = 0;
  virtual void Save(Json& j) const = 0;     // 処理を足すたびに、全部のクラスに足す
  // virtual bool Optimize() ...
};

class Number : public Expr { /* Eval、ToString、Save をすべて実装 */ };
class Add : public Expr { /* 同じ */ };
class Multiply : public Expr { /* 同じ */ };
```

| 問題 | 説明 |
| --- | --- |
| **処理を足すたびに、全クラスを変更**する | `Number`、`Add`、`Multiply` すべてに、新しい関数を書く |
| **1 つのクラスに、無関係な処理が混ざる** | 評価、表示、保存が 1 つのクラスに集まって、肥大化する |
| **処理が散らばる** | 「保存」の処理が、すべてのクラスに分散して、全体が読めない |

## 良い例 1：std::variant + std::visit（C++17 以降・おすすめ）

データを `std::variant`（いくつかの型のどれか）にして、**処理を、型ごとの関数をまとめたもの（ビジター）として書き**ます。

```cpp
#include <memory>
#include <print>
#include <string>
#include <variant>

struct Number {
  int value;
};
struct Add;       // 前方宣言（中に、自分と同じ Expr を持つため）
struct Multiply;

using Expr = std::variant<Number, std::unique_ptr<Add>, std::unique_ptr<Multiply>>;

struct Add {
  Expr left, right;
};
struct Multiply {
  Expr left, right;
};

// ビジター 1：計算する
struct EvalVisitor {
  int operator()(const Number& n) const { return n.value; }
  int operator()(const std::unique_ptr<Add>& a) const {
    return std::visit(*this, a->left) + std::visit(*this, a->right);
  }
  int operator()(const std::unique_ptr<Multiply>& m) const {
    return std::visit(*this, m->left) * std::visit(*this, m->right);
  }
};

// ビジター 2：文字列にする（Eval とは別に、後から足せる）
struct PrintVisitor {
  std::string operator()(const Number& n) const { return std::to_string(n.value); }
  std::string operator()(const std::unique_ptr<Add>& a) const {
    return "(" + std::visit(*this, a->left) + " + " + std::visit(*this, a->right) + ")";
  }
  std::string operator()(const std::unique_ptr<Multiply>& m) const {
    return "(" + std::visit(*this, m->left) + " * " + std::visit(*this, m->right) + ")";
  }
};

int main() {
  // 1 + 2 * 3
  auto mul = std::make_unique<Multiply>(Multiply{Number{2}, Number{3}});
  auto add = std::make_unique<Add>(Add{Number{1}, std::move(mul)});
  Expr expr = std::move(add);

  std::println("{} = {}", std::visit(PrintVisitor{}, expr), std::visit(EvalVisitor{}, expr));
}
```

```text title="実行結果"
(1 + (2 * 3)) = 7
```

| 利点 | 説明 |
| --- | --- |
| **処理を足しても、データの型を変えない** | `SaveVisitor` を足すだけ。`Number` や `Add` は触らない |
| **処理が 1 か所にまとまる** | 「評価」のコードが、`EvalVisitor` 1 つに集まる |
| **`virtual` 関数が要らない** | `std::variant` が、どの型かを覚えている |
| **処理の漏れを、コンパイラが見つけてくれる** | 型を足したのに、`operator()` を書き忘れると、コンパイル エラー |

### ラムダで、その場でビジターを書く

型が少なければ、ラムダを重ねる書き方（**overloaded パターン**）が便利です。

```cpp
template <class... Ts>
struct Overloaded : Ts... {
  using Ts::operator()...;
};
template <class... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;   // C++17 の推論ガイド（C++20 では不要なことが多い）

std::variant<int, float, std::string> v = 3.5f;

std::visit(Overloaded{
    [](int i) { std::println("整数 {}", i); },
    [](float f) { std::println("小数 {}", f); },
    [](const std::string& s) { std::println("文字列 {}", s); },
}, v);
```

```text title="実行結果"
小数 3.5
```

詳しくは [`std::variant`](../../stl/utilities/variant.md#visit) を見てください。

## 良い例 2：古典的なビジター（virtual、二重ディスパッチ）

継承を使う場合の書き方です。データのクラスが `Accept` を持ち、ビジターが型ごとの `Visit` を持ちます。<strong>「どのデータ」と「どのビジター」の両方で、呼ぶ関数が決まる</strong>（二重ディスパッチ）のが特徴です。

```cpp
class Number;
class Add;

// ビジターのインターフェース：型ごとに Visit を持つ
class ExprVisitor {
 public:
  virtual ~ExprVisitor() = default;
  virtual void Visit(const Number& n) = 0;
  virtual void Visit(const Add& a) = 0;
};

// データ：Accept だけを持つ
class Expr {
 public:
  virtual ~Expr() = default;
  virtual void Accept(ExprVisitor& visitor) const = 0;
};

class Number : public Expr {
 public:
  explicit Number(int v) : value(v) {}
  void Accept(ExprVisitor& visitor) const override { visitor.Visit(*this); }  // 自分の型で呼び返す
  int value;
};

class Add : public Expr {
 public:
  Add(std::unique_ptr<Expr> l, std::unique_ptr<Expr> r) : left(std::move(l)), right(std::move(r)) {}
  void Accept(ExprVisitor& visitor) const override { visitor.Visit(*this); }
  std::unique_ptr<Expr> left, right;
};
```

<svg class="fig flow" viewBox="0 0 424 280" role="img" aria-label="二重ディスパッチ：Accept と Visit が行き来する"><defs><marker id="fl65752" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">二重ディスパッチ：Accept と Visit が行き来する</text><line x1="113.0" y1="148.0" x2="171.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl65752)"/><text x="142.0" y="142.0" text-anchor="middle" style="font-size:12px">Accept</text><line x1="253.0" y1="148.0" x2="311.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl65752)"/><text x="282.0" y="142.0" text-anchor="middle" style="font-size:12px">Visit(Add)</text><line x1="315.8" y1="125.0" x2="251.2" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl65752)"/><text x="283.5" y="100.0" text-anchor="middle" style="font-size:12px">Accept</text><line x1="315.8" y1="171.0" x2="251.2" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl65752)"/><text x="283.5" y="184.0" text-anchor="middle" style="font-size:12px">Accept</text><rect x="28.0" y="128.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="69.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">呼び出し</text><circle cx="30.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="30.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="174.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="212.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Add</text><circle cx="176.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="176.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="314.0" y="128.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="355.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ビジター</text><circle cx="316.0" cy="130.0" r="10" fill="#4c8bf5"/><text x="316.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="174.0" y="44.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="212.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">左</text><circle cx="176.0" cy="46.0" r="10" fill="#2ea043"/><text x="176.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="174.0" y="212.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="212.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">右</text><circle cx="176.0" cy="214.0" r="10" fill="#2ea043"/><text x="176.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>

| 項目 | 古典的（virtual） | `std::variant` + `std::visit` |
| --- | --- | --- |
| コードの量 | 多い（`Accept` と `Visit` を、全クラスに） | **少ない** |
| 型の足しやすさ | ビジターの全部に `Visit` を足す | `variant` に型を足し、全ビジターの `operator()` を足す |
| 処理の足しやすさ | ビジターを 1 つ足すだけ | ビジターを 1 つ足すだけ |
| 型が閉じているか | 開いている（継承で増やせる） | **閉じている**（`variant` に書いた型だけ） |
| 速さ | 仮想呼び出し × 2 | 速い（データが連続し、仮想関数なし） |

## 使うか迷ったら

| 状況 | 選ぶもの |
| --- | --- |
| 種類は固定。処理が増える | **ビジター**（`variant` + `visit`） |
| 種類が増える。処理は固定 | 普通の **`virtual` 関数**（クラスごとに実装） |
| 種類も処理も増える | 設計を見直す（コンポーネントや、データ駆動に） |
| 処理が 1〜2 個で、増えない | ビジターは大げさ。普通の関数でよい |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| スクリプト・式の木 | 評価、表示、最適化、保存を、ビジターで分ける |
| **イベントの種類**（`variant<Damage, Heal, Death>`） | イベントを、種類ごとに処理する（[イベントシステム](event.md)） |
| **コマンド**の種類 | 実行、保存、取り消しを、ビジターで足す（[コマンド](command.md)） |
| **AI のビヘイビア ツリー** | ノードの評価、デバッグ表示、保存 |
| **シーン グラフ** | 描画、当たり判定、シリアライズを、同じ木に別々に適用する |
| ネットワークの**パケットの種類** | 受け取った種類ごとに処理する |

## よくあるミス

??? failure "型が増え続けるのに、ビジターを使う"
    新しい種類のデータを足すたびに、**全部のビジター**に `Visit` を足す必要があります。種類が増えるなら、普通の `virtual` 関数のほうが楽です。

??? failure "`std::visit` で、型の処理が漏れる"
    すべての型を処理する `operator()` を書く必要があります。1 つでも欠けると、コンパイルエラーです（これは利点です）。「それ以外」は、`auto` を引数にしたもの（`[](const auto&) {}`）で受けます。

??? failure "ビジターが状態を持ちすぎる"
    ビジターのメンバに、たくさんの状態を持たせると、使い回しにくくなります。**1 回の処理ごとに、新しく作る**ようにします。

??? failure "二重ディスパッチを、`dynamic_cast` で代用する"
    `if (auto* n = dynamic_cast<Number*>(e))` を並べると、種類が増えるたびに書き換えが必要で、漏れも検出できません。ビジターか `variant` にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 種類が固定で、処理が増えるときに向く
    - [x] C++17 以降は、`std::variant` + `std::visit` で簡単に書ける
    - [x] 処理を、データのクラスから切り離して、ビジターに 1 か所にまとめる
    - [x] 種類が増えるなら、普通の `virtual` 関数のほうが向いている
    - [x] 古典的な書き方は、`Accept` と `Visit` の二重ディスパッチ

## 関連ページ

- [std::variant](../../stl/utilities/variant.md)
- [CRTP とポリシーベース設計](crtp-policy.md)
- [イベントシステム](event.md)
- [コマンドパターン](command.md)
- [継承と仮想関数（基礎）](../../basics/virtual.md)
