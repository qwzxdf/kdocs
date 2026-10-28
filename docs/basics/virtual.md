---
title: 継承と仮想関数
tags:
  - 基礎
---

# 継承と仮想関数

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
</div>

**継承**は、**あるクラス（基底クラス）の性質を受け継いだ新しいクラス（派生クラス）を作る仕組み**です。**仮想関数**（`virtual`）を使うと、基底クラスのポインタや参照から呼んだときに、**実際のオブジェクトの種類に合った関数**が呼ばれます（ポリモーフィズム）。「敵もプレイヤーもアイテムも `GameObject` として同じ vector に入れて、`Update()` を呼ぶとそれぞれの処理が動く」という書き方ができるのは、この仕組みのおかげです。

!!! tip "ポイント"
    - 基底クラスに `virtual void Update();`、派生クラスで `void Update() override;`。
    - **基底クラスのデストラクタは `virtual`** にする（付けないと派生クラスの片付けが呼ばれない）。
    - 派生クラスを入れるときは `std::vector<std::unique_ptr<Base>>`（値で入れると切り落とされる）。
    - 継承を深くしすぎない。ゲームでは「継承よりコンポーネント（組み合わせ）」が主流（[コンポーネント指向](../engine/component.md)）。

!!! info "このページを読む前に"
    [ポインタ](pointer.md) と [`std::unique_ptr`](../stl/utilities/unique_ptr.md) を先に読むと分かりやすいです。

## 基本

<svg class="fig flow" viewBox="0 0 1005 112" role="img" aria-label="仮想関数：オブジェクトの持つ vptr から、vtable を引いて、実際の関数を呼ぶ"><defs><marker id="fl27768" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">仮想関数：オブジェクトの持つ vptr から、vtable を引いて、実際の関数を呼ぶ</text><line x1="119.0" y1="64.0" x2="177.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27768)"/><text x="148.0" y="58.0" text-anchor="middle" style="font-size:12px">指す</text><line x1="463.0" y1="64.0" x2="521.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27768)"/><text x="492.0" y="58.0" text-anchor="middle" style="font-size:12px">vptr</text><line x1="767.0" y1="64.0" x2="825.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl27768)"/><text x="796.0" y="58.0" text-anchor="middle" style="font-size:12px">表を引く</text><rect x="28.0" y="44.0" width="88" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="72.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Enemy* e</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="180.0" y="44.0" width="280" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="320.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Goblin オブジェクト （vptr を持つ）</text><circle cx="182.0" cy="46.0" r="10" fill="#2ea043"/><text x="182.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="524.0" y="44.0" width="240" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="644.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Goblin の vtable （関数の表）</text><circle cx="526.0" cy="46.0" r="10" fill="#e5a828"/><text x="526.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="828.0" y="44.0" width="149" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="902.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Goblin::Attack()</text><circle cx="830.0" cy="46.0" r="10" fill="#e5484d"/><text x="830.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

```cpp
#include <memory>
#include <print>
#include <vector>

class GameObject {
 public:
  virtual ~GameObject() = default;  // 基底クラスのデストラクタは virtual
  virtual void Update() = 0;        // = 0 は「派生クラスで必ず書く」（純粋仮想関数）
  virtual void Draw() const { std::println("  （共通の描画）"); }
};

class Player : public GameObject {
 public:
  void Update() override { std::println("プレイヤー: 入力を見て動く"); }
};

class Enemy : public GameObject {
 public:
  void Update() override { std::println("敵: プレイヤーを追う"); }
  void Draw() const override { std::println("  敵の描画"); }
};

int main() {
  std::vector<std::unique_ptr<GameObject>> objects;
  objects.push_back(std::make_unique<Player>());
  objects.push_back(std::make_unique<Enemy>());

  for (const auto& obj : objects) {
    obj->Update();  // 実際の種類に合った Update が呼ばれる
    obj->Draw();
  }
}
```

```text title="実行結果"
プレイヤー: 入力を見て動く
  （共通の描画）
敵: プレイヤーを追う
  敵の描画
```

## 詳しく

### キーワードのまとめ

| 書き方 | 意味 |
| --- | --- |
| `class Derived : public Base` | Base を継承する（ほぼ必ず `public`） |
| `virtual void F();` | 派生クラスで上書きできる関数 |
| `virtual void F() = 0;` | 純粋仮想関数。派生クラスで必ず書く。これがあるクラスは直接作れない（抽象クラス） |
| `void F() override;` | 基底クラスの仮想関数を上書きする（書き間違いをコンパイラが見つけてくれる） |
| `void F() final;` / `class X final` | これ以上上書き・継承させない |
| `virtual ~Base() = default;` | 仮想デストラクタ |
| `protected:` | 自分と派生クラスからだけ使える |

### override を必ず付ける理由

```cpp
class Base {
 public:
  virtual ~Base() = default;
  virtual void Update(float dt) {}
};

class Bad : public Base {
 public:
  void Update(double dt) {}  // 引数の型が違うので、上書きではなく別の関数になってしまう
};

class Good : public Base {
 public:
  // void Update(double dt) override {}  // コンパイルエラーで間違いに気づける
  void Update(float dt) override {}
};
```

### 仮想デストラクタが必要な理由

```cpp
#include <memory>
#include <print>

class Base {
 public:
  virtual ~Base() { std::println("Base の片付け"); }
};

class Boss : public Base {
 public:
  ~Boss() override { std::println("Boss の片付け（エフェクトの解放など）"); }
};

int main() {
  std::unique_ptr<Base> p = std::make_unique<Boss>();
}  // virtual なので Boss → Base の順に両方呼ばれる
```

```text title="実行結果"
Boss の片付け（エフェクトの解放など）
Base の片付け
```

`virtual` が無いと `Base` のデストラクタしか呼ばれず、未定義動作になります。

### スライシング（切り落とし）

```cpp
std::vector<GameObject> objects;  // 値で持つと…
objects.push_back(Enemy{});       // Enemy の部分が切り落とされて GameObject だけが残る
```

派生クラスを基底クラスの「値」に入れると、派生クラスの部分が失われます。必ずポインタ（`unique_ptr`）か参照で扱います。

### 派生クラスかどうか調べる（dynamic_cast）

```cpp
#include <memory>
#include <print>

struct GameObject {
  virtual ~GameObject() = default;
};
struct Enemy : GameObject {
  int hp = 50;
};

int main() {
  std::unique_ptr<GameObject> obj = std::make_unique<Enemy>();
  if (auto* enemy = dynamic_cast<Enemy*>(obj.get())) {  // Enemy なら非 nullptr
    std::println("敵だった。HP {}", enemy->hp);
  }
}
```

```text title="実行結果"
敵だった。HP 50
```

`dynamic_cast` を多用しているなら、設計を見直すサインです（仮想関数で解決できないか考える）。

### 仮想関数のコスト

- 仮想関数の呼び出しは、オブジェクトが持つ「仮想関数テーブル」を経由する**間接呼び出し**になります。普通の関数より少し遅く、インライン化もされにくいです。
- 何十万回も呼ぶ処理（パーティクル 1 個ずつなど）では、仮想関数よりも「種類ごとに vector を分けて普通の関数で回す」ほうが速くなります。

## ゲームでの例

| 場面 | 例 |
| --- | --- |
| シーン | `class Scene { virtual void Update(); virtual void Draw(); }` を継承した `TitleScene`、`GameScene` |
| コンポーネントの基底 | `class Component { virtual void Update(float dt); }` |
| ステート | `class State { virtual void Enter(); virtual void Update(); }` |
| AI の行動 | `class Action { virtual bool Execute(); }` |

<!-- fig:vtable-call:begin -->

<svg class="fig illust motion" data-fig="vtable-call" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vtable-call" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">仮想関数の呼び出し: オブジェクト → 表 → 関数 と 2 回たどる</text>
<rect x="50" y="120" width="170" height="90" fill="#ffffff" stroke="#2563eb" stroke-width="2.5"/>
<text x="135" y="110" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2563eb">Slime のオブジェクト</text>
<text x="135" y="150" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">vptr（表への矢印）</text>
<text x="135" y="190" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#64748b">hp = 30</text>
<rect x="310" y="120" width="170" height="90" fill="#ffffff" stroke="#2ea043" stroke-width="2.5"/>
<text x="395" y="110" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">Slime の vtable（表）</text>
<text x="395" y="150" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">Update → Slime::Update</text>
<text x="395" y="190" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">Draw → Slime::Draw</text>
<rect x="570" y="120" width="160" height="90" fill="#ffffff" stroke="#e5aa28" stroke-width="2.5"/>
<text x="650" y="110" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#e5aa28">実際のコード</text>
<text x="650" y="160" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">Slime::Update()</text>
<line x1="222" y1="150" x2="306" y2="150" stroke="#e5484d" stroke-width="3" marker-end="url(#arr-vtable-call)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/></line>
<line x1="482" y1="150" x2="566" y2="150" stroke="#e5484d" stroke-width="3" marker-end="url(#arr-vtable-call)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></line>
<text x="50" y="260" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">enemy-&gt;Update()  ← 型は Enemy* でも、中身は Slime</text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">Enemy* で Slime を指している<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">① オブジェクトの先頭の vptr を読む<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">② vtable の「Update」の欄を読む<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">③ そこに書かれた関数 Slime::Update を呼ぶ(実行時に決まる)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;0.7094;0.7097;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="330" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">普通の関数より、メモリを 2 回余計に読む。この差が仮想関数のコスト<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7094;0.7097;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:vtable-call:end -->

## よくあるミス

??? failure "基底クラスのデストラクタに virtual を付け忘れる"
    `unique_ptr<Base>` で派生クラスを持つなら必須です。

??? failure "override を付けずに、上書きしたつもりになる"
    引数の型や `const` が少し違うだけで別の関数になります。必ず `override` を付けます。

??? failure "継承を深くしすぎる"
    `GameObject → Character → Enemy → FlyingEnemy → FlyingFireEnemy` のように深くすると、「飛ぶけど火を吹かない敵」を作るのが難しくなります。機能を部品（コンポーネント）にして組み合わせる設計が主流です。

??? failure "コンストラクタの中で仮想関数を呼ぶ"
    基底クラスのコンストラクタの中では、派生クラスはまだできていないので、派生クラスの関数は呼ばれません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 上書きできる関数は `virtual`、上書きする側は `override`
    - [x] 基底クラスのデストラクタは `virtual`
    - [x] 派生クラスは unique_ptr で持つ（値で持つと切り落とされる）
    - [x] 継承は浅く。組み合わせはコンポーネントで

## 関連ページ

- [コンポーネント指向](../engine/component.md)
- [cppreference: virtual function specifier](https://en.cppreference.com/w/cpp/language/virtual)
