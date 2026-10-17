---
title: レイヤー
tags:
  - 外部ライブラリ
  - 物理演算
---

# レイヤー

Jolt の**レイヤー**は、<strong>「どの種類の物体どうしを、衝突させるか」</strong>を決める仕組みです。**プレイヤーと弾は当たる、弾どうしは当たらない、地面と敵は当たる**のように、**物体を分類**して、**組み合わせを、ルールとして書きます**。**不要な組み合わせの判定を省く**ので、**速くもなります**。Jolt では、**2 種類のレイヤー**（**オブジェクト レイヤー**と**ブロードフェーズ レイヤー**）と、**3 つの設定クラス**を用意する必要があり、**最初の関門**になります。このページは、**仕組み**と、**コピーして使える定番のコード**をまとめます。

!!! tip "ポイント"
    - <strong>オブジェクト レイヤー（`ObjectLayer`）</strong>＝ <strong>物体に付ける「種類」</strong>（動かない・動く・弾・プレイヤー ...）。<strong>自分で定義</strong>する。
    - <strong>ブロードフェーズ レイヤー（`BroadPhaseLayer`）</strong>＝ <strong>空間分割の、大まかなグループ</strong>。<strong>少数（2〜3 個）</strong>で、<strong>性能のため</strong>。
    - <strong>3 つのクラス</strong>を実装する：<strong>① `BroadPhaseLayerInterface`（種類 → グループ）</strong>、<strong>② `ObjectVsBroadPhaseLayerFilter`（種類 × グループ）</strong>、<strong>③ `ObjectLayerPairFilter`（種類 × 種類）</strong>。
    - 衝突のルールは<strong>表（マトリクス）で考える</strong>。<strong>対称</strong>にする（A と B が当たるなら、B と A も当たる）。
    - <strong>動かない物体（`NON_MOVING`）どうしは、衝突させない</strong>のが、基本。
    - <strong>物体の作成時に、`ObjectLayer` を渡す</strong>。<strong>あとから、変更もできる</strong>。

## なぜレイヤーが必要か

**物体が 1000 個**あれば、**全部の組み合わせ**（約 50 万）を判定すると、**重すぎます**。**レイヤーで、「当たらない組み合わせ」を、最初から除外**します。

```text
弾 ↔ 弾       ：当たらない（判定しない）
弾 ↔ 敵       ：当たる
プレイヤー ↔ 敵 ：当たる
地面 ↔ 地面    ：当たらない（どちらも動かない）
```

**ゲームの設計**として、「**何が何と当たるか**」を決めるのも、レイヤーの役割です（**味方の弾は、味方に当たらない**など）。

## 2 種類のレイヤー

### オブジェクト レイヤー（ObjectLayer）

<strong>物体に付ける「種類」</strong>です。**自由に定義できます**（`uint16_t`、最大 65535 種類）。

```cpp
namespace Layers {
static constexpr ObjectLayer NON_MOVING = 0;
static constexpr ObjectLayer MOVING = 1;
static constexpr ObjectLayer NUM_LAYERS = 2;
}
```

**ゲームに合わせて、増やします**。

```cpp
namespace Layers {
static constexpr ObjectLayer STATIC = 0;
static constexpr ObjectLayer PLAYER = 1;
static constexpr ObjectLayer ENEMY = 2;
static constexpr ObjectLayer PLAYER_BULLET = 3;
static constexpr ObjectLayer ENEMY_BULLET = 4;
static constexpr ObjectLayer TRIGGER = 5;
static constexpr ObjectLayer NUM_LAYERS = 6;
}
```

### ブロードフェーズ レイヤー（BroadPhaseLayer）

**ブロードフェーズ**（衝突判定の**最初の絞り込み**）が、**物体を、空間分割の木に入れる**とき、<strong>「動かない物体」と「動く物体」</strong>を、**別の木**にします。**木ごとに、更新の頻度が違う**（動かない木は、ほぼ更新不要）ので、**速くなります**。

```cpp
namespace BroadPhaseLayers {
static constexpr BroadPhaseLayer NON_MOVING(0);
static constexpr BroadPhaseLayer MOVING(1);
static constexpr uint NUM_LAYERS(2);
}
```

| | オブジェクト レイヤー | ブロードフェーズ レイヤー |
| --- | --- | --- |
| **役割** | **ゲームの、衝突ルール**（種類の分類） | **性能のための、大まかなグループ** |
| **数** | **多くてよい**（種類に応じて） | **少数**（**2〜3 個**が、普通） |
| **型** | `ObjectLayer`（`uint16_t`） | `BroadPhaseLayer`（`uint8_t`） |
| **付ける対象** | <strong>物体（Body）</strong> | **オブジェクト レイヤーから、自動で決まる** |

**典型的には、ブロードフェーズ レイヤー ＝ 「動かない」と「動く」の 2 つ**にします。

## 3 つの設定クラス

Jolt には、**次の 3 つを実装して、`PhysicsSystem::Init` に渡す**必要があります。

### 1. BroadPhaseLayerInterface（種類 → グループ）

**オブジェクト レイヤーを、ブロードフェーズ レイヤーに、対応づけます**。

```cpp
class BPLayerInterfaceImpl final : public BroadPhaseLayerInterface {
 public:
  BPLayerInterfaceImpl() {
    mObjectToBroadPhase[Layers::STATIC] = BroadPhaseLayers::NON_MOVING;
    mObjectToBroadPhase[Layers::PLAYER] = BroadPhaseLayers::MOVING;
    mObjectToBroadPhase[Layers::ENEMY] = BroadPhaseLayers::MOVING;
    mObjectToBroadPhase[Layers::PLAYER_BULLET] = BroadPhaseLayers::MOVING;
    mObjectToBroadPhase[Layers::ENEMY_BULLET] = BroadPhaseLayers::MOVING;
    mObjectToBroadPhase[Layers::TRIGGER] = BroadPhaseLayers::NON_MOVING;
  }

  uint GetNumBroadPhaseLayers() const override { return BroadPhaseLayers::NUM_LAYERS; }

  BroadPhaseLayer GetBroadPhaseLayer(ObjectLayer layer) const override {
    JPH_ASSERT(layer < Layers::NUM_LAYERS);
    return mObjectToBroadPhase[layer];
  }

#if defined(JPH_EXTERNAL_PROFILE) || defined(JPH_PROFILE_ENABLED)
  const char* GetBroadPhaseLayerName(BroadPhaseLayer layer) const override {
    switch ((BroadPhaseLayer::Type)layer) {
      case (BroadPhaseLayer::Type)BroadPhaseLayers::NON_MOVING: return "NON_MOVING";
      case (BroadPhaseLayer::Type)BroadPhaseLayers::MOVING: return "MOVING";
      default: JPH_ASSERT(false); return "INVALID";
    }
  }
#endif

 private:
  BroadPhaseLayer mObjectToBroadPhase[Layers::NUM_LAYERS];
};
```

### 2. ObjectVsBroadPhaseLayerFilter（種類 × グループ）

<strong>「このオブジェクト レイヤーの物体は、このブロードフェーズ レイヤーの木と、判定するか」</strong>を返します。

```cpp
class ObjectVsBroadPhaseLayerFilterImpl : public ObjectVsBroadPhaseLayerFilter {
 public:
  bool ShouldCollide(ObjectLayer layer1, BroadPhaseLayer layer2) const override {
    switch (layer1) {
      case Layers::STATIC:
        return layer2 == BroadPhaseLayers::MOVING;
      default:
        return true;
    }
  }
};
```

| 点 | 説明 |
| --- | --- |
| **`STATIC` は、`MOVING` の木とだけ判定** | **動かない物体どうしは、判定しない** |
| **それ以外は、すべての木と判定** | `true` を返す |

### 3. ObjectLayerPairFilter（種類 × 種類）

<strong>「この 2 つのオブジェクト レイヤーの物体は、衝突するか」</strong>を返します。**ゲームの衝突ルールそのもの**です。

```cpp
class ObjectLayerPairFilterImpl : public ObjectLayerPairFilter {
 public:
  bool ShouldCollide(ObjectLayer a, ObjectLayer b) const override {
    return kCollisionMatrix[a][b];
  }
};
```

## 衝突マトリクスで考える

**表にして考える**と、**ミスが減ります**。

| | STATIC | PLAYER | ENEMY | PLAYER_BULLET | ENEMY_BULLET | TRIGGER |
| --- | --- | --- | --- | --- | --- | --- |
| **STATIC** | ✕ | ○ | ○ | ○ | ○ | ✕ |
| **PLAYER** | ○ | ○ | ○ | ✕ | ○ | ○ |
| **ENEMY** | ○ | ○ | ○ | ○ | ✕ | ✕ |
| **PLAYER_BULLET** | ○ | ✕ | ○ | ✕ | ✕ | ✕ |
| **ENEMY_BULLET** | ○ | ○ | ✕ | ✕ | ✕ | ✕ |
| **TRIGGER** | ✕ | ○ | ✕ | ✕ | ✕ | ✕ |

```cpp
constexpr bool kCollisionMatrix[Layers::NUM_LAYERS][Layers::NUM_LAYERS] = {
    //  STATIC PLAYER ENEMY  P_BUL  E_BUL  TRIGGER
    {   false, true,  true,  true,  true,  false },
    {   true,  true,  true,  false, true,  true  },
    {   true,  true,  true,  true,  false, false },
    {   true,  false, true,  false, false, false },
    {   true,  true,  false, false, false, false },
    {   false, true,  false, false, false, false },
};
```

| 設計のコツ | 説明 |
| --- | --- |
| **対称にする** | **`[a][b]` と `[b][a]` を、同じ値に**（Jolt は、対称を前提） |
| **動かない物体どうしは、`false`** | **無駄な判定**を避ける |
| **自分の弾は、自分に当たらない** | **プレイヤーの弾 × プレイヤー ＝ `false`** |
| <strong>トリガー（センサー）</strong> | **反応させたい相手とだけ `true`** |
| **ビット マスクで書く方法も** | **各レイヤーが、「衝突する相手」のビットを持つ**（`1 << layer`）。**マトリクスより、コンパクト** |

!!! note "ビット マスク版"
    `uint32_t mask[NUM_LAYERS]` に、**当たる相手のビットを立て**、`ShouldCollide(a, b)` は `(mask[a] & (1u << b)) != 0` と書く方法もあります。**レイヤーが、32 個以内**のときに、便利です。

## 物体にレイヤーを付ける

```cpp
BodyCreationSettings settings(shape, position, rotation, EMotionType::Dynamic, Layers::ENEMY);
BodyID id = bodies.CreateAndAddBody(settings, EActivation::Activate);

bodies.SetObjectLayer(id, Layers::ENEMY_BULLET);
```

| 操作 | 説明 |
| --- | --- |
| **作成時に、渡す** | `BodyCreationSettings` の**最後の引数**が `ObjectLayer` |
| **あとから変更** | **`SetObjectLayer`**。**ブロードフェーズ レイヤーも、自動で更新** |
| **用途** | <strong>ダメージを受けている間は、無敵（レイヤー変更）</strong>、**ゴースト化** |

## レイヤーと、クエリ（レイキャスト）

**レイキャストなどのクエリ**にも、**レイヤーで絞り込み**ができます（[クエリ](queries.md)）。

```cpp
DefaultBroadPhaseLayerFilter bp_filter(object_vs_broadphase_filter, Layers::PLAYER_BULLET);
DefaultObjectLayerFilter obj_filter(object_pair_filter, Layers::PLAYER_BULLET);
```

<strong>「PLAYER_BULLET が衝突する相手」だけ</strong>を、レイキャストの対象にできます。**衝突のルールを、そのまま使い回す**ので、**一貫**します。

## よくあるミス

??? failure "3 つのクラスのうち、1 つを実装し忘れる"
    **`PhysicsSystem::Init` の引数が 3 つ**必要です。**全部作ります**。

??? failure "`GetBroadPhaseLayer` の対応表が、レイヤーを足したのに、更新されていない"
    **新しいレイヤーの分**を、**コンストラクタに足します**（`NUM_LAYERS` も）。

??? failure "衝突マトリクスが、非対称で、片方からしか当たらない"
    **`[a][b]` と `[b][a]` を、同じ**にします。

??? failure "動かない物体どうしを、`true` にして、重くなる"
    **`STATIC × STATIC` は `false`**。

??? failure "ブロードフェーズ レイヤーを、オブジェクト レイヤーと同じ数だけ作って、遅くなる"
    <strong>ブロードフェーズは、少数（2〜3）</strong>で十分です。

??? failure "弾が、味方に当たる"
    **衝突マトリクスの、`PLAYER_BULLET × PLAYER` を `false`** に。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>オブジェクト レイヤー ＝ 物体の種類</strong>（衝突ルールの単位）。<strong>ブロードフェーズ レイヤー ＝ 性能用の大まかなグループ（2〜3 個）</strong>
    - [x] <strong>3 つのクラス</strong>：<strong>`BroadPhaseLayerInterface`</strong>（種類 → グループ）、<strong>`ObjectVsBroadPhaseLayerFilter`</strong>（種類 × グループ）、<strong>`ObjectLayerPairFilter`</strong>（種類 × 種類）
    - [x] <strong>衝突マトリクスで設計</strong>。<strong>対称に</strong>。<strong>動かない物体どうしは、判定しない</strong>
    - [x] <strong>物体の作成時に、`ObjectLayer` を渡す</strong>。<strong>`SetObjectLayer` で、あとから変更</strong>
    - [x] <strong>クエリ（レイキャスト）にも、同じレイヤーのルール</strong>を使える

## 関連ページ

- [Jolt Physics](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)
- [クエリ（レイキャストなど）](queries.md)
