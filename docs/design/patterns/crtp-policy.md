---
title: CRTP とポリシーベース設計
tags:
  - 設計
---

# CRTP とポリシーベース設計

<div class="page-badges" markdown>
<span class="perf perf-4">◎ 速い</span>
</div>

**静的ポリモーフィズム**は、「同じ呼び方で、違う動きをさせる」（多態）を、コンパイル時に決める方法です。普通の多態（`virtual` 関数）は、実行時に「どの関数を呼ぶか」を探す（仮想呼び出し）ので、少しだけ遅く、インライン展開もできません。毎フレーム何万回も呼ぶ小さな処理では、この差が効くことがあります。静的ポリモーフィズムは、テンプレートを使って、呼ぶ関数をコンパイル時に確定させるので、仮想呼び出しのコストがなく、インライン展開もできます。代表的な書き方が CRTP（シーアールティーピー、Curiously Recurring Template Pattern）とポリシーベース設計です。

!!! tip "ポイント"
    - **まずは普通の `virtual`**。速さが問題になった場所（計測で分かった所）だけ、静的な方法にする。
    - **CRTP**: 派生クラスを、基底クラスのテンプレート引数に渡す（`class A : public Base<A>`）。基底から派生の関数を、`static_cast` で呼べる。
    - ポリシーベース: クラスの振る舞いの一部を、テンプレート引数（ポリシー）で差し替える（`Pool<Enemy, MallocAllocator>`）。
    - 代償は、型ごとにコードが生成される（コード サイズ）、異なる型をまとめて 1 つの配列に入れられない、エラーメッセージが難しいこと。
    - C++20 の concepts と `std::variant`（+ `std::visit`）で、同じことをより簡単に書けることが多い。

## 動的ポリモーフィズムとの違い

<svg class="fig flow" viewBox="0 0 573 196" role="img" aria-label="virtual は実行時に探し、テンプレートはコンパイル時に決まる"><defs><marker id="fl25039" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">virtual は実行時に探し、テンプレートはコンパイル時に決まる</text><line x1="180.0" y1="64.0" x2="238.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl25039)"/><text x="209.0" y="58.0" text-anchor="middle" style="font-size:12px">実行時</text><line x1="366.0" y1="64.0" x2="424.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl25039)"/><line x1="180.0" y1="148.0" x2="424.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl25039)"/><text x="302.0" y="142.0" text-anchor="middle" style="font-size:12px">コンパイル時に決まる</text><rect x="28.0" y="44.0" width="149" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="102.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Shape* s-&gt;Area()</text><rect x="241.0" y="44.0" width="122" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="302.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">vtable を引く</text><rect x="427.0" y="44.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="486.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Circle::Area</text><rect x="28.0" y="128.0" width="149" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="102.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Circle c Area(c)</text><rect x="427.0" y="128.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="486.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Circle::Area</text></svg>

| 項目 | 動的（`virtual`） | 静的（CRTP・テンプレート） |
| --- | --- | --- |
| 呼ぶ関数が決まるとき | **実行時** | コンパイル時 |
| 呼び出しのコスト | 仮想呼び出し（ポインタをたどる） | 直接呼べる・インライン化できる |
| 異なる型を、1 つの配列に入れる | できる（`vector<unique_ptr<Shape>>`） | できない（型ごとに別の配列） |
| 実行時に型を切り替える | できる | できない |
| コード サイズ | 小さい | 型ごとにコードが増える |
| ヘッダ | 実装を `.cpp` に隠せる | テンプレートなので、ヘッダに実装が出る |

## CRTP

### 形

```cpp
// 基底クラス：テンプレート引数に、派生クラスを受け取る
template <class Derived>
class Shape {
 public:
  double Area() const {
    return static_cast<const Derived*>(this)->AreaImpl();  // 派生の関数を、コンパイル時に呼ぶ
  }

  void Print() const {
    std::println("面積: {}", Area());
  }
};

// 派生クラス：自分自身を、基底のテンプレート引数に渡す
class Circle : public Shape<Circle> {
 public:
  explicit Circle(double r) : r_(r) {}
  double AreaImpl() const { return 3.14159 * r_ * r_; }

 private:
  double r_;
};

class Square : public Shape<Square> {
 public:
  explicit Square(double s) : s_(s) {}
  double AreaImpl() const { return s_ * s_; }

 private:
  double s_;
};

// どの型でも、共通の呼び方で使える（テンプレート）
template <class T>
void Report(const Shape<T>& shape) {
  shape.Print();
}
```

`Shape<Circle>` の中で `static_cast<const Circle*>(this)->AreaImpl()` と書かれているので、**呼ぶ関数は `Circle::AreaImpl` と、コンパイル時に分かります**。仮想関数のテーブルは不要です。

### CRTP の使いどころ

| 使い方 | 説明 |
| --- | --- |
| 共通の機能を、型ごとに足す（Mixin） | 基底が、派生クラスの関数を使って、共通の機能を作る（`operator!=` を `operator==` から作る、など） |
| コピー不可・シングルトンなどの共通部品 | `class A : public NonCopyable<A>`（型ごとに別の基底になる） |
| インスタンス カウンター | 型ごとの数を数える `Counter<Enemy>`（型ごとに別の `static` 変数になる） |
| 速さが重要な、型ごとの処理 | 毎フレーム何万回も呼ぶ、小さな関数（物理の形状、ベクトル演算） |

```cpp
// 型ごとのインスタンスを数える Mixin
template <class T>
class InstanceCounter {
 public:
  InstanceCounter() { ++count_; }
  InstanceCounter(const InstanceCounter&) { ++count_; }
  ~InstanceCounter() { --count_; }
  static int count() { return count_; }

 private:
  inline static int count_ = 0;  // T ごとに別の変数
};

class Enemy : public InstanceCounter<Enemy> {};
class Bullet : public InstanceCounter<Bullet> {};
// Enemy::count() と Bullet::count() は、別の数になる
```

## ポリシーベース設計

クラスの**振る舞いの一部を、小さな部品（ポリシー）として、テンプレート引数で渡す**設計です。実行時にではなく、コンパイル時に組み合わせを決めます。

```cpp
// ポリシー 1：確保の仕方
struct HeapAllocate {
  static void* Allocate(std::size_t n) { return ::operator new(n); }
  static void Free(void* p) { ::operator delete(p); }
};

// ポリシー 2：確保の仕方（静的な領域）
struct PoolAllocate {
  static void* Allocate(std::size_t n) { /* プールから取る */ }
  static void Free(void* p) { /* プールに返す */ }
};

// ポリシー：ログの出し方
struct NoLog { static void Log(const char*) {} };                    // 何もしない（Release）
struct ConsoleLog { static void Log(const char* m) { std::puts(m); } };  // 画面に出す（Debug）

// 部品を組み合わせて作るクラス
template <class T, class AllocPolicy, class LogPolicy>
class ObjectFactory {
 public:
  T* Create() {
    LogPolicy::Log("create");
    return new (AllocPolicy::Allocate(sizeof(T))) T();
  }
};

// 使うとき：組み合わせを、型で選ぶ
ObjectFactory<Enemy, PoolAllocate, NoLog> release_factory;       // 製品版
ObjectFactory<Enemy, HeapAllocate, ConsoleLog> debug_factory;    // デバッグ版
```

| 項目 | 説明 |
| --- | --- |
| 利点 | 実行時のコストがない（`NoLog::Log` は空で、完全に消える）。組み合わせが自由 |
| 欠点 | 組み合わせの型が増える。長いテンプレート引数になる |
| 標準ライブラリでの例 | `std::vector<T, Allocator>` のアロケータ、`std::unordered_map<K, V, Hash, KeyEqual>` のハッシュと比較、`std::unique_ptr<T, Deleter>` の削除の仕方 |

標準ライブラリは、ポリシーベースの考え方でできています（[std::allocator](../../stl/memory/allocator.md)、[std::hash](../../stl/utilities/hash.md)）。

## concepts と variant による、もっと簡単な方法

C++20 以降は、CRTP を使わなくても、次の方法で同じことができます。

### concepts（型の条件）

```cpp
template <class T>
concept HasArea = requires(const T& s) {
  { s.Area() } -> std::convertible_to<double>;
};

template <HasArea T>
void Report(const T& shape) {          // Area() を持つ型なら、何でも受け取れる
  std::println("面積: {}", shape.Area());
}
```

継承が**いりません**（`Area()` を持つだけでよい）。エラーメッセージも分かりやすくなります（[インターフェース設計](../foundations/interface-design.md)）。

### std::variant + std::visit（閉じた型の集合）

```cpp
using Shape = std::variant<Circle, Square>;       // 型が決まっているなら、これで十分

double TotalArea(const std::vector<Shape>& shapes) {
  double sum = 0;
  for (const Shape& s : shapes) {
    sum += std::visit([](const auto& shape) { return shape.Area(); }, s);  // 仮想関数なし
  }
  return sum;
}
```

型が決まっていて、1 つの配列にまとめたいときは、`variant` が向いています。仮想関数のポインタをたどらず、データがまとまって並ぶので、速くなることも多いです（[variant](../../stl/utilities/variant.md)、[ビジター](visitor.md)）。

## どれを使うか

| 状況 | 選ぶもの |
| --- | --- |
| 実行時に型を切り替える・あとから型を足す（プラグイン） | **`virtual`**（抽象クラス） |
| 型の種類が決まっていて、1 つの配列にまとめたい | `std::variant` + `std::visit` |
| 関数やクラスを、いろいろな型で使い回したい（型の条件を書く） | テンプレート + concepts |
| 派生クラスの関数を、基底から呼びたい・共通の機能を足したい | CRTP |
| 振る舞いの一部を、コンパイル時に組み合わせたい | ポリシー |
| 速さが気になる（ただし計測してから） | 静的な方法 |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 数学ライブラリ（`Vec2`、`Vec3`、`Vec4` の共通演算） | CRTP で、共通の演算子を基底にまとめる |
| コンポーネントの共通機能（型 ID の自動付与） | CRTP（`Component<Position>` が、型ごとの ID を持つ） |
| メモリ アロケータの選択 | ポリシー（`Pool<T, Alloc>`） |
| 毎フレーム何万回も呼ぶ処理 | `virtual` を避け、テンプレート・`variant` にする |
| デバッグ機能の ON/OFF | ポリシー（`NoLog` で、Release では完全に消す） |

## よくあるミス

??? failure "速さの計測をせずに、全部をテンプレートにする"
    仮想呼び出しの差は、ほとんどの場所では小さく、**コードが読みにくくなる損のほうが大きい**です。計測して、本当に遅い場所だけ使います。

??? failure "CRTP で、派生クラスの型を間違える"
    `class Square : public Shape<Circle>` のように、別の型を渡しても、コンパイルが通ってしまうことがあります。`static_cast` の先が間違い、未定義動作になります。基底のコンストラクタを `private` にして、`friend Derived;` にすると、間違いを防げます。

??? failure "CRTP の基底を、型をまたいで 1 つの配列に入れようとする"
    `Shape<Circle>` と `Shape<Square>` は、別の型です。`std::vector<Shape<???>>` は作れません。まとめたいなら `virtual` か `variant` です。

??? failure "テンプレートの実装を `.cpp` に書く"
    テンプレートは、使う側で展開されるので、ヘッダに実装を書く必要があります（またはヘッダの下で `.inl` を include）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 速さが必要と**計測で分かってから**、静的な多態にする。普通は `virtual` でよい
    - [x] CRTP ＝ `class A : public Base<A>`。基底から `static_cast<A*>(this)` で派生を呼ぶ
    - [x] ポリシー ＝ 振る舞いの部品を、テンプレート引数で差し替える（標準のアロケータ、ハッシュ、デリータ）
    - [x] C++20 では、まず concepts と `std::variant` を検討する
    - [x] 代償は、コード サイズ、ヘッダの実装、異なる型を混ぜられないこと

## 関連ページ

- [インターフェース設計（concepts）](../foundations/interface-design.md)
- [ビジター](visitor.md)
- [std::variant](../../stl/utilities/variant.md)
- [テンプレート（基礎）](../../basics/template.md)
- [継承と仮想関数（基礎）](../../basics/virtual.md)
- [パフォーマンス設計](../practice/performance-design.md)
- [コンパイラの最適化](../../optimize/compiler.md)
- [メモリとキャッシュ（最適化）](../../optimize/memory-cache.md)
