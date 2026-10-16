---
title: ECS（エンティティ・コンポーネント・システム）
tags:
  - ゲームエンジン
---

# ECS（エンティティ・コンポーネント・システム）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

**ECS** は、ゲームの世界を**エンティティ（ただの番号）**、**コンポーネント（データだけ）**、**システム（処理だけ）**の 3 つに分けて作る設計です。[コンポーネント指向](component.md)では「オブジェクトが部品を持ち、部品が自分で Update する」のに対し、ECS では**同じ種類のコンポーネントを 1 本の配列にまとめて並べ**、システムがその配列をまとめて処理します。データがメモリ上に連続して並ぶので、何万体ものオブジェクトでも速く回せます。Unity DOTS、Bevy、Overwatch のエンジンなどがこの形で、C++ では **EnTT** や **flecs** というライブラリが有名です。

!!! tip "結論"
    - **エンティティ = ID 番号**、**コンポーネント = データだけの構造体**、**システム = 「この組み合わせを持つエンティティ全部に対する処理」**。
    - 同じ種類のコンポーネントは vector に詰めて持つ → キャッシュ効率が良く速い。
    - 「位置と速度を持つもの全部を動かす」のように、**組み合わせで処理対象が決まる**。
    - 自作は勉強にとても良いが、本格的に使うなら EnTT などのライブラリを使うのが現実的。
    - オブジェクトが数百程度なら、普通のコンポーネント指向でも十分速い。

!!! info "このページを読む前に"
    [コンポーネント指向](component.md)、[キャッシュ効率](../basics/cache.md)、[テンプレート](../basics/template.md)、[ハンドルと世代 ID](handle.md) を先に読むと分かりやすいです。

## 基本

### 3 つの役割

| 要素 | 中身 | 例 |
| --- | --- | --- |
| エンティティ | **ただの番号**（ID）。データも処理も持たない | `Entity player = 0;` |
| コンポーネント | **データだけ**の構造体。関数を持たない | `struct Position { float x, y; };` |
| システム | **処理だけ**。特定のコンポーネントの組み合わせを持つエンティティをまとめて処理する | `MovementSystem`：Position と Velocity を持つもの全部を動かす |

### メモリの並び方の違い

<div class="mem">
<div class="mem-step"><span class="mem-label">コンポーネント指向</span><span class="mem-cells"><span class="move">P</span><span class="free">　</span><span>V</span><span class="free">　</span><span class="move">P</span><span class="free">　</span><span class="free">　</span><span>V</span></span><span class="mem-note">オブジェクトごとに部品がヒープにバラバラ</span></div>
<div class="mem-step"><span class="mem-label">ECS の Position</span><span class="mem-cells"><span class="move">P</span><span class="move">P</span><span class="move">P</span><span class="move">P</span></span><span class="mem-note">同じ種類が 1 本に並ぶ</span></div>
<div class="mem-step"><span class="mem-label">ECS の Velocity</span><span class="mem-cells"><span>V</span><span>V</span><span>V</span><span>V</span></span><span class="mem-note">MovementSystem はこの 2 本を順番に読むだけ</span></div>
</div>

## 詳しく

### 最小の ECS を作る

ここでは仕組みを理解するために、**sparse set（疎集合）**という方式で小さな ECS を作ります（EnTT と同じ考え方）。

```cpp
#include <cstdint>
#include <memory>
#include <print>
#include <string>
#include <typeindex>
#include <typeinfo>
#include <unordered_map>
#include <utility>
#include <vector>

using Entity = std::uint32_t;

// 型を消した基底クラス（どの型のプールもまとめて持てるように）
class IPool {
 public:
  virtual ~IPool() = default;
  virtual void Remove(Entity e) = 0;
};

// 1 種類のコンポーネントを、隙間なく vector に並べて持つ
template <class T>
class Pool : public IPool {
 public:
  T& Add(Entity e, T value) {
    index_[e] = dense_.size();
    entities_.push_back(e);
    dense_.push_back(std::move(value));
    return dense_.back();
  }

  bool Has(Entity e) const { return index_.contains(e); }
  T& Get(Entity e) { return dense_[index_.at(e)]; }

  // 消すときは最後の要素を穴に持ってきて、隙間を作らない
  void Remove(Entity e) override {
    auto it = index_.find(e);
    if (it == index_.end()) {
      return;
    }
    std::size_t hole = it->second;
    std::size_t last = dense_.size() - 1;
    if (hole != last) {
      dense_[hole] = std::move(dense_[last]);
      entities_[hole] = entities_[last];
      index_[entities_[hole]] = hole;
    }
    dense_.pop_back();
    entities_.pop_back();
    index_.erase(e);
  }

  const std::vector<Entity>& entities() const { return entities_; }

 private:
  std::vector<T> dense_;                       // コンポーネント本体（連続）
  std::vector<Entity> entities_;               // dense_[i] の持ち主
  std::unordered_map<Entity, std::size_t> index_;  // エンティティ → dense_ の添字
};

class Registry {
 public:
  Entity Create() { return next_++; }

  void Destroy(Entity e) {
    for (auto& [type, pool] : pools_) {
      pool->Remove(e);
    }
  }

  template <class T>
  T& Add(Entity e, T value = {}) {
    return GetPool<T>().Add(e, std::move(value));
  }

  template <class T>
  bool Has(Entity e) {
    return GetPool<T>().Has(e);
  }

  template <class T>
  T& Get(Entity e) {
    return GetPool<T>().Get(e);
  }

  // A と Rest... を全部持つエンティティに func を呼ぶ
  template <class A, class... Rest, class Func>
  void Each(Func func) {
    for (Entity e : GetPool<A>().entities()) {
      if ((Has<Rest>(e) && ...)) {
        func(e, Get<A>(e), Get<Rest>(e)...);
      }
    }
  }

 private:
  template <class T>
  Pool<T>& GetPool() {
    auto& slot = pools_[std::type_index(typeid(T))];
    if (!slot) {
      slot = std::make_unique<Pool<T>>();
    }
    return static_cast<Pool<T>&>(*slot);
  }

  Entity next_ = 0;
  std::unordered_map<std::type_index, std::unique_ptr<IPool>> pools_;
};

// --- コンポーネント（データだけ） ---
struct Position {
  float x;
  float y;
};
struct Velocity {
  float x;
  float y;
};
struct Name {
  std::string value;
};

// --- システム（処理だけ） ---
void MovementSystem(Registry& registry, float dt) {
  registry.Each<Position, Velocity>([dt](Entity, Position& p, Velocity& v) {
    p.x += v.x * dt;
    p.y += v.y * dt;
  });
}

void PrintSystem(Registry& registry) {
  registry.Each<Name, Position>([](Entity, Name& n, Position& p) {
    std::println("{}: ({}, {})", n.value, p.x, p.y);
  });
}

int main() {
  Registry registry;

  Entity player = registry.Create();
  registry.Add(player, Name{"プレイヤー"});
  registry.Add(player, Position{0, 0});
  registry.Add(player, Velocity{10, 0});

  Entity tree = registry.Create();  // 動かない（Velocity が無い）
  registry.Add(tree, Name{"木"});
  registry.Add(tree, Position{5, 5});

  Entity bullet = registry.Create();
  registry.Add(bullet, Name{"弾"});
  registry.Add(bullet, Position{0, 0});
  registry.Add(bullet, Velocity{0, 100});

  MovementSystem(registry, 0.5f);
  registry.Destroy(bullet);  // 弾が消えた
  MovementSystem(registry, 0.5f);
  PrintSystem(registry);
}
```

```text title="実行結果"
プレイヤー: (10, 0)
木: (5, 5)
```

### 仕組みのポイント

| 部品 | 役割 |
| --- | --- |
| `Pool<T>` | 1 種類のコンポーネントを `dense_`（隙間の無い vector）に並べる |
| `index_` | 「エンティティ → 何番目に入っているか」の表。`Has` / `Get` に使う |
| `Remove` | 最後の要素を穴に移して詰める（[swap して pop_back](../stl/containers/vector.md#順番がどうでもいいならswap-して-pop_back)）。O(1) |
| `Registry` | 型ごとのプールをまとめて持つ。`std::type_index` で型からプールを探す |
| `Each<A, B>` | A のプールを順に回し、B も持っているものだけ処理する |

本物のライブラリでは、`index_` の `unordered_map` を「エンティティ番号を添字にした vector」（sparse 配列）にして、さらに速くしています。

### エンティティの再利用と世代

上の実装は ID を増やし続けるだけですが、実際には消したエンティティの番号を再利用します。そのとき、古い番号を覚えていた人が**別の新しいエンティティを触ってしまう**問題が起きるので、「世代（generation）」を番号に含めます。詳しくは [ハンドルと世代 ID](handle.md) を見てください。

### 2 つの主な方式

| 方式 | 仕組み | 得意 | 代表 |
| --- | --- | --- | --- |
| Sparse set | コンポーネントの種類ごとに配列 | コンポーネントの追加・削除が速い | EnTT |
| Archetype | 「持っているコンポーネントの組み合わせ」ごとに配列 | 複数のコンポーネントをまとめて回すのがとても速い | Unity DOTS、flecs、Bevy |

### システムの書き方のコツ

| コツ | 理由 |
| --- | --- |
| システムは「どのコンポーネントを読み、どれを書くか」をはっきりさせる | 並列化しやすくなる。依存関係が見える |
| システムの実行順は決めておく（入力 → AI → 移動 → 当たり判定 → 描画） | コンポーネント指向のような「取り付け順で動きが変わる」問題が起きない |
| 処理中にエンティティを消さない | 「消す印」コンポーネントを付けて、最後にまとめて消す |
| タグ（データの無い空の構造体）で分類する | `struct EnemyTag {};` を付けたものだけを処理する、など |

## EnTT を使う場合

```cpp
#include <entt/entt.hpp>  // https://github.com/skypjack/entt

struct Position {
  float x, y;
};
struct Velocity {
  float x, y;
};

void Update(entt::registry& registry, float dt) {
  auto view = registry.view<Position, Velocity>();
  view.each([dt](Position& p, const Velocity& v) {
    p.x += v.x * dt;
    p.y += v.y * dt;
  });
}

void Spawn(entt::registry& registry) {
  entt::entity e = registry.create();
  registry.emplace<Position>(e, 0.0f, 0.0f);
  registry.emplace<Velocity>(e, 1.0f, 0.0f);
}
```

| 主なライブラリ | 特徴 |
| --- | --- |
| EnTT | ヘッダだけで使える。sparse set。とても速く、情報も多い |
| flecs | C / C++。archetype。クエリやリレーションなど機能が豊富 |

## コンポーネント指向との比較

| | コンポーネント指向 | ECS |
| --- | --- | --- |
| 考え方 | オブジェクトが部品を持ち、部品が自分で動く | データ（コンポーネント）と処理（システム）を分ける |
| メモリ | 部品がバラバラ | 種類ごとに連続 |
| 速さ | 数百〜数千まで | 数万〜数十万でも速い |
| 書きやすさ | 直感的。1 つのオブジェクトを中心に考える | 慣れが必要。「全体に対する処理」で考える |
| 向いているゲーム | アドベンチャー、パズル、普通のアクション | 弾幕、RTS、大量の NPC、シミュレーション |

## よくあるミス

??? failure "コンポーネントに処理（関数）を書く"
    ECS ではコンポーネントはデータだけにします。処理はシステムに書きます。コンポーネントに `Update` を持たせると、コンポーネント指向に戻ってしまいます。

??? failure "システムの中でエンティティを追加・削除する"
    回している配列が変わると壊れます（swap による詰め直しが起きるため）。コマンドを溜めておき、システムが終わったあとに実行します。

??? failure "コンポーネントのポインタを保存する"
    プールの vector は伸びたり詰めたりするので、ポインタや参照はすぐ無効になります。保存するのはエンティティ ID だけにします。

## 理解度チェック

!!! question "Q1. 「HP が 0 以下のエンティティを全部消す」システムを、上の Registry で書くと？"
    <div class="spoiler" markdown>

    **答え:** 回しながら消すと壊れるので、先に集めてから消します。

    ```cpp
    struct Health {
      int hp;
    };

    void DeathSystem(Registry& registry) {
      std::vector<Entity> dead;
      registry.Each<Health>([&](Entity e, Health& h) {
        if (h.hp <= 0) {
          dead.push_back(e);
        }
      });
      for (Entity e : dead) {
        registry.Destroy(e);
      }
    }
    ```

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] エンティティは番号、コンポーネントはデータ、システムは処理
    - [x] 同じ種類のコンポーネントを連続して並べるので速い
    - [x] 保存するのはエンティティ ID だけ
    - [x] 本格的に使うなら EnTT / flecs

## 関連ページ

- [コンポーネント指向](component.md)
- [ハンドルと世代 ID](handle.md)
- [キャッシュ効率](../basics/cache.md)
- [EnTT](https://github.com/skypjack/entt)
- [flecs](https://github.com/SanderMertens/flecs)
