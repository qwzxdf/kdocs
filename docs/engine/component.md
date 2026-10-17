---
title: コンポーネント指向
tags:
  - ゲームエンジン
---

# コンポーネント指向

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

**コンポーネント指向**は、**ゲームオブジェクトを「機能の部品（コンポーネント）の組み合わせ」で作る設計**です。「動く」「描かれる」「当たり判定がある」「HP がある」といった機能をそれぞれ小さなクラスにしておき、オブジェクトに必要な部品だけを取り付けます。Unity の `GameObject` + `MonoBehaviour`、Unreal の `Actor` + `ActorComponent` がこの形です。継承でキャラクターの種類を作る方法の弱点を解決するために広まりました。

!!! tip "ポイント"
    - <strong>継承は「〜は〜の一種」、コンポーネントは「〜は〜を持っている」。</strong> ゲームのオブジェクトは後者で考えたほうが組み合わせやすい。
    - 基本形は `GameObject` が `std::vector<std::unique_ptr<Component>>` を持ち、毎フレーム全部の `Update` を呼ぶ。
    - コンポーネント同士は `GetComponent<T>()` で探して連携する。
    - オブジェクトが何万個にもなるなら、データの並びを最適化した [ECS](../design/patterns/ecs.md) を検討する。

!!! info "このページを読む前に"
    [継承と仮想関数](../basics/virtual.md)、[テンプレート](../basics/template.md)、[`std::unique_ptr`](../stl/utilities/unique_ptr.md) を使います。

## 基本

### 継承だけで作ると困ること

<svg class="fig flow" viewBox="0 0 640 448" role="img" aria-label="継承の木：機能が増えると、枝が増えていく"><defs><marker id="fl24499" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">継承の木：機能が増えると、枝が増えていく</text><line x1="124.1" y1="209.0" x2="197.9" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><line x1="101.8" y1="255.0" x2="220.2" y2="377.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><line x1="283.4" y1="125.0" x2="351.1" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><line x1="283.4" y1="171.0" x2="351.1" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><line x1="433.0" y1="210.6" x2="508.9" y2="171.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><line x1="433.0" y1="253.4" x2="508.9" y2="293.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl24499)"/><rect x="28.0" y="212.0" width="103" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="79.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GameObject</text><rect x="195.0" y="128.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="242.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Character</text><rect x="204.5" y="380.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="242.5" y="400.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Item</text><rect x="354.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="392.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Player</text><rect x="354.0" y="212.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="392.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Enemy</text><rect x="494.0" y="128.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="553.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">WalkingEnemy</text><rect x="497.5" y="296.0" width="111" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="553.0" y="316.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FlyingEnemy</text></svg>

ここで「**空を飛ぶアイテム**」や「**プレイヤーが操作できる敵**」を作ろうとすると、どこに入れればいいか分かりません。機能を継承の木に固定してしまうので、組み合わせが増えるとクラスが爆発します。

### コンポーネントで作る

| オブジェクト | 付けるコンポーネント |
| --- | --- |
| プレイヤー | Transform、Sprite、PlayerInput、Health、Collider |
| 歩く敵 | Transform、Sprite、WalkAI、Health、Collider |
| 飛ぶ敵 | Transform、Sprite、FlyAI、Health、Collider |
| 空を飛ぶアイテム | Transform、Sprite、FlyAI、Pickup、Collider |

「飛ぶ」機能（FlyAI）は、敵にもアイテムにも付けられます。

## 詳しく

### 最小の実装 {#minimal}

<p class="ng">※ 仕組みを分かりやすくするために、あえて<strong>非推奨の実装</strong>にしています（コンポーネントを個別に <code>new</code> して、ポインタで持ちます）。非推奨の理由は、<a href="#slow">「遅さの原因と対策」</a>の項目を見てください。</p>

```cpp
#include <memory>
#include <print>
#include <string>
#include <utility>
#include <vector>

class GameObject;

// すべてのコンポーネントの基底クラス
class Component {
 public:
  virtual ~Component() = default;
  virtual void Update(float dt) {}

  GameObject* owner() const { return owner_; }

 private:
  friend class GameObject;
  GameObject* owner_ = nullptr;
};

class GameObject {
 public:
  explicit GameObject(std::string name) : name_(std::move(name)) {}

  // コンポーネントを作って取り付ける
  template <class T, class... Args>
  T& AddComponent(Args&&... args) {
    auto component = std::make_unique<T>(std::forward<Args>(args)...);
    component->owner_ = this;
    T& ref = *component;
    components_.push_back(std::move(component));
    return ref;
  }

  // 指定した型のコンポーネントを探す（無ければ nullptr）
  template <class T>
  T* GetComponent() const {
    for (const auto& c : components_) {
      if (auto* found = dynamic_cast<T*>(c.get())) {
        return found;
      }
    }
    return nullptr;
  }

  void Update(float dt) {
    for (auto& c : components_) {
      c->Update(dt);
    }
  }

  const std::string& name() const { return name_; }

 private:
  std::string name_;
  std::vector<std::unique_ptr<Component>> components_;
};

// --- 具体的なコンポーネント ---

struct Transform : Component {
  float x = 0.0f;
  float y = 0.0f;
};

class Mover : public Component {
 public:
  explicit Mover(float vx) : vx_(vx) {}
  void Update(float dt) override {
    if (auto* t = owner()->GetComponent<Transform>()) {  // 同じオブジェクトの Transform を探す
      t->x += vx_ * dt;
    }
  }

 private:
  float vx_;
};

struct Health : Component {
  int hp = 100;
};

int main() {
  GameObject slime("スライム");
  slime.AddComponent<Transform>();
  slime.AddComponent<Mover>(30.0f);
  slime.AddComponent<Health>().hp = 20;

  GameObject sign("看板");  // 動かないし HP も無い
  sign.AddComponent<Transform>();

  for (int frame = 0; frame < 2; ++frame) {
    slime.Update(0.5f);
    sign.Update(0.5f);
  }

  std::println("{}: x = {} / HP {}", slime.name(), slime.GetComponent<Transform>()->x,
               slime.GetComponent<Health>()->hp);
  std::println("{} に HP はある？ {}", sign.name(), sign.GetComponent<Health>() != nullptr);
}
```

```text title="実行結果"
スライム: x = 30 / HP 20
看板 に HP はある？ false
```

### 設計のポイント

| ポイント | 理由 |
| --- | --- |
| コンポーネントは 1 つの役割だけ持つ | 組み合わせやすく、再利用しやすい |
| 毎フレーム `GetComponent` しない | 毎回の検索は遅い。`Start()` などで一度探してポインタを覚えておく |
| 持ち主（GameObject）が消えたらコンポーネントも消える | `unique_ptr` で持っているので自動 |
| コンポーネント同士の参照はポインタで覚える | 同じ GameObject の中なら寿命が同じなので安全 |
| 別のオブジェクトの参照は ID で覚える | 相手が先に消えるかもしれない（[所有権](../basics/ownership.md)） |

### ライフサイクル（呼ばれる順番）

エンジンによって名前は違いますが、だいたい次のような関数を用意します。

| 関数 | 呼ばれるとき | 使い道 |
| --- | --- | --- |
| `Awake` / コンストラクタ | 取り付けた直後 | 自分の初期化 |
| `Start` | 最初の Update の直前 | 他のコンポーネントを探して覚える |
| `Update(dt)` | 毎フレーム | 動き・ロジック |
| `FixedUpdate(dt)` | 固定タイムステップごと | 物理（[ゲームループ](game-loop.md)） |
| `Draw` | 描画のとき | 見た目 |
| `OnDestroy` / デストラクタ | 消えるとき | 後片付け |

### 遅さの原因と対策 {#slow}

この素朴な実装は、オブジェクトが数百〜数千くらいまでなら十分動きます。それ以上になると次の点が効いてきます。

| 原因 | 対策 |
| --- | --- |
| コンポーネント 1 個ごとにヒープ確保（メモリがバラバラ） | 種類ごとに vector にまとめて持つ → [ECS](../design/patterns/ecs.md) |
| 毎フレーム仮想関数を呼ぶ | 種類ごとにまとめて普通の関数で回す |
| `dynamic_cast` での検索 | 型ごとの ID を使う、ポインタを覚えておく |

## ゲームでの例

| 部品 | 役割 |
| --- | --- |
| `Transform` | 位置・回転・大きさ |
| `SpriteRenderer` | 画像を描く |
| `RigidBody` | 速度・重力 |
| `Collider` | 当たり判定の形 |
| `Health` | HP、ダメージ、死亡 |
| `PlayerInput` | 入力で動かす |
| `EnemyAI` | 行動を決める |
| `AudioSource` | 音を鳴らす |

## よくあるミス

??? failure "1 つのコンポーネントに何でも入れる"
    `PlayerComponent` に移動・攻撃・HP・アニメーションを全部入れると、継承で作るのと変わらなくなります。役割ごとに分けます。

??? failure "Update の中で GameObject を消す"
    ループで回している最中に vector から消すと壊れます。「消す予定」の印を付けておき、全員の Update が終わったあとにまとめて消します。

??? failure "コンポーネントの Update の順番に依存する"
    「Mover が先、Collider が後」のような順番に頼ると、取り付けた順で動きが変わります。順番が大事な処理は、種類ごとに決まった順で回す仕組み（システム）にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] オブジェクトは機能の部品の組み合わせで作る
    - [x] `AddComponent<T>()` / `GetComponent<T>()` が基本の操作
    - [x] 1 コンポーネント 1 役割
    - [x] 数が多いなら ECS へ

## 関連ページ

- [ECS](../design/patterns/ecs.md)
- [継承と仮想関数](../basics/virtual.md)
- [Game Programming Patterns: Component](https://gameprogrammingpatterns.com/component.html)
