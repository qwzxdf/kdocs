---
title: レイヤー
tags:
  - 外部ライブラリ
  - 物理演算
---

# レイヤー

Jolt の**レイヤー**は 「どの種類の物体どうしを衝突させるか」を決める仕組みです。プレイヤーと弾は当たる弾どうしは当たらない、地面と敵は当たるのように物体を分類して、組み合わせをルールとして書きます。不要な組み合わせの判定を省くので、速くもなります。Jolt では2 種類のレイヤー（オブジェクト レイヤーとブロードフェーズ レイヤー）と、3 つの設定クラスを用意する必要があり最初の関門になります。このページは仕組みとコピーして使える定番のコードをまとめます。

!!! tip "ポイント"
    - <strong>オブジェクト レイヤー（`ObjectLayer`）</strong>＝ <strong>物体に付ける「種類」</strong>（動かない・動く・弾・プレイヤー ...）。自分で定義する。
    - ブロードフェーズ レイヤー（`BroadPhaseLayer`）＝ 空間分割の大まかなグループ。少数（2〜3 個）で 性能のため。
    - 3 つのクラスを実装する：① `BroadPhaseLayerInterface`（種類 → グループ）、② `ObjectVsBroadPhaseLayerFilter`（種類 × グループ）、③ `ObjectLayerPairFilter`（種類 × 種類）。
    - 衝突のルールは表（マトリクス）で考える。対称にする（A と B が当たるなら B と A も当たる）。
    - 動かない物体（`NON_MOVING`）どうしは、衝突させないのが基本。
    - 物体の作成時に `ObjectLayer` を渡す。あとから変更もできる。

!!! info "このページを読む前に"
    - [Jolt Physics](index.md)（このセクション全体の地図と、読む順番）
    - [物理演算の全体像](overview.md)（Jolt の全体像）

## なぜレイヤーが必要か

**物体が 1000 個**あれば、全部の組み合わせ（約 50 万）を判定すると、重すぎます。レイヤーで「当たらない組み合わせ」を最初から除外します。

```text
弾 ↔ 弾       ：当たらない（判定しない）
弾 ↔ 敵       ：当たる
プレイヤー ↔ 敵 ：当たる
地面 ↔ 地面    ：当たらない（どちらも動かない）
```

ゲームの設計として「何が何と当たるか」を決めるのもレイヤーの役割です（味方の弾は、味方に当たらないなど）。

## 2 種類のレイヤー

### オブジェクト レイヤー（ObjectLayer）

<strong>物体に付ける「種類」</strong>です。自由に定義できます（`uint16_t`、最大 65535 種類）。

```cpp
namespace Layers {
static constexpr ObjectLayer NON_MOVING = 0;
static constexpr ObjectLayer MOVING = 1;
static constexpr ObjectLayer NUM_LAYERS = 2;
}
```

ゲームに合わせて増やします。

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

ブロードフェーズ（衝突判定の最初の絞り込み）が物体を空間分割の木に入れるとき 「動かない物体」と「動く物体」を別の木にします。木ごとに更新の頻度が違う（動かない木は、ほぼ更新不要）ので速くなります。

```cpp
namespace BroadPhaseLayers {
static constexpr BroadPhaseLayer NON_MOVING(0);
static constexpr BroadPhaseLayer MOVING(1);
static constexpr uint NUM_LAYERS(2);
}
```

| | オブジェクト レイヤー | ブロードフェーズ レイヤー |
| --- | --- | --- |
| 役割 | ゲームの衝突ルール（種類の分類） | 性能のための、大まかなグループ |
| 数 | 多くてよい（種類に応じて） | 少数（2〜3 個が普通） |
| 型 | `ObjectLayer`（`uint16_t`） | `BroadPhaseLayer`（`uint8_t`） |
| 付ける対象 | 物体（Body） | オブジェクト レイヤーから、自動で決まる |

典型的にはブロードフェーズ レイヤー ＝ 「動かない」と「動く」の 2 つにします。

## 3 つの設定クラス

Jolt には**次の 3 つを実装して、`PhysicsSystem::Init` に渡す**必要があります。

### 1. BroadPhaseLayerInterface（種類 → グループ）

オブジェクト レイヤーをブロードフェーズ レイヤーに対応づけます。

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

「このオブジェクト レイヤーの物体は、このブロードフェーズ レイヤーの木と判定するか」を返します。

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
| `STATIC` は `MOVING` の木とだけ判定 | 動かない物体どうしは、判定しない |
| それ以外はすべての木と判定 | `true` を返す |

### 3. ObjectLayerPairFilter（種類 × 種類）

「この 2 つのオブジェクト レイヤーの物体は、衝突するか」を返します。ゲームの衝突ルールそのものです。

```cpp
class ObjectLayerPairFilterImpl : public ObjectLayerPairFilter {
 public:
  bool ShouldCollide(ObjectLayer a, ObjectLayer b) const override {
    return kCollisionMatrix[a][b];
  }
};
```

## 衝突マトリクスで考える

**表にして考える**とミスが減ります。

| | STATIC | PLAYER | ENEMY | PLAYER_BULLET | ENEMY_BULLET | TRIGGER |
| --- | --- | --- | --- | --- | --- | --- |
| STATIC | ✕ | ○ | ○ | ○ | ○ | ✕ |
| PLAYER | ○ | ○ | ○ | ✕ | ○ | ○ |
| ENEMY | ○ | ○ | ○ | ○ | ✕ | ✕ |
| PLAYER_BULLET | ○ | ✕ | ○ | ✕ | ✕ | ✕ |
| ENEMY_BULLET | ○ | ○ | ✕ | ✕ | ✕ | ✕ |
| TRIGGER | ✕ | ○ | ✕ | ✕ | ✕ | ✕ |

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
| 対称にする | `[a][b]` と `[b][a]` を同じ値に（Jolt は、対称を前提） |
| 動かない物体どうしは `false` | 無駄な判定を避ける |
| 自分の弾は自分に当たらない | プレイヤーの弾 × プレイヤー ＝ `false` |
| トリガー（センサー） | 反応させたい相手とだけ `true` |
| ビット マスクで書く方法も | 各レイヤーが「衝突する相手」のビットを持つ（`1 << layer`）。マトリクスよりコンパクト |

!!! note "ビット マスク版"
    `uint32_t mask[NUM_LAYERS]` に当たる相手のビットを立て、`ShouldCollide(a, b)` は `(mask[a] & (1u << b)) != 0` と書く方法もあります。レイヤーが 32 個以内のときに便利です。

## 物体にレイヤーを付ける

```cpp
BodyCreationSettings settings(shape, position, rotation, EMotionType::Dynamic, Layers::ENEMY);
BodyID id = bodies.CreateAndAddBody(settings, EActivation::Activate);

bodies.SetObjectLayer(id, Layers::ENEMY_BULLET);
```

| 操作 | 説明 |
| --- | --- |
| **作成時に渡す** | `BodyCreationSettings` の最後の引数が `ObjectLayer` |
| あとから変更 | `SetObjectLayer`。ブロードフェーズ レイヤーも自動で更新 |
| 用途 | ダメージを受けている間は、無敵（レイヤー変更）、ゴースト化 |

## レイヤーとクエリ（レイキャスト）

**レイキャストなどのクエリ**にもレイヤーで絞り込みができます（[クエリ](queries.md)）。

```cpp
DefaultBroadPhaseLayerFilter bp_filter(object_vs_broadphase_filter, Layers::PLAYER_BULLET);
DefaultObjectLayerFilter obj_filter(object_pair_filter, Layers::PLAYER_BULLET);
```

「PLAYER_BULLET が衝突する相手」だけをレイキャストの対象にできます。衝突のルールをそのまま使い回すので、一貫します。

<!-- fig:layer-matrix:begin -->

<svg class="fig illust motion" data-fig="layer-matrix" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-layer-matrix" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイヤーの組み合わせで、「何と何をぶつけるか」を先に決める</text>
<text x="238" y="157.0" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">床（NON_MOVING）</text>
<text x="301.0" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">床（NON_MOVING）</text>
<text x="238" y="223.0" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">キャラ（MOVING）</text>
<text x="411.0" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">キャラ（MOVING）</text>
<text x="238" y="289.0" text-anchor="end" style="font-size:13px;font-weight:700;fill:#1f2937">破片（DEBRIS）</text>
<text x="521.0" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">破片（DEBRIS）</text>
<rect x="250" y="120.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="360" y="120.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="470" y="120.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="250" y="186.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="360" y="186.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="470" y="186.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="250" y="252.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="360" y="252.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="470" y="252.0" width="106" height="62.0" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/><rect x="250" y="120.0" width="106" height="62.0" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="303.0" y="159.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">通り抜け</text>
<rect x="360" y="120.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="413.0" y="159.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
<rect x="470" y="120.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="523.0" y="159.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;1.0000" values="0;0;1;1"/><rect x="250" y="186.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="303.0" y="225.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
<rect x="360" y="186.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="413.0" y="225.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
<rect x="470" y="186.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="523.0" y="225.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/><rect x="250" y="252.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="303.0" y="291.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
<rect x="360" y="252.0" width="106" height="62.0" fill="#bbf7d0" stroke="#94a3b8" stroke-width="1.5"/>
<text x="413.0" y="291.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">ぶつかる</text>
<rect x="470" y="252.0" width="106" height="62.0" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
<text x="523.0" y="291.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">通り抜け</text>
</g>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 つのレイヤーの、行 × 列の組み合わせを調べる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">床: 床どうしは調べない。キャラと破片とは、ぶつかる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.2756;0.2759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">キャラ: 全部とぶつかる<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;0.4825;0.4828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="340" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">破片: キャラとは通り抜け、破片どうしも通り抜け(数が多いので、計算を減らす)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:layer-matrix:end -->

## よくあるミス

??? failure "3 つのクラスのうち 1 つを実装し忘れる"
    **`PhysicsSystem::Init` の引数が 3 つ**必要です。全部作ります。

??? failure "`GetBroadPhaseLayer` の対応表がレイヤーを足したのに更新されていない"
    新しいレイヤーの分をコンストラクタに足します（`NUM_LAYERS` も）。

??? failure "衝突マトリクスが非対称で片方からしか当たらない"
    `[a][b]` と `[b][a]` を同じにします。

??? failure "動かない物体どうしを `true` にして、重くなる"
    `STATIC × STATIC` は `false`。

??? failure "ブロードフェーズ レイヤーをオブジェクト レイヤーと同じ数だけ作って、遅くなる"
    ブロードフェーズは少数（2〜3）で十分です。

??? failure "弾が味方に当たる"
    衝突マトリクスの `PLAYER_BULLET × PLAYER` を `false` に。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>オブジェクト レイヤー ＝ 物体の種類</strong>（衝突ルールの単位）。ブロードフェーズ レイヤー ＝ 性能用の大まかなグループ（2〜3 個）
    - [x] 3 つのクラス：`BroadPhaseLayerInterface`（種類 → グループ）、`ObjectVsBroadPhaseLayerFilter`（種類 × グループ）、`ObjectLayerPairFilter`（種類 × 種類）
    - [x] 衝突マトリクスで設計。対称に。動かない物体どうしは判定しない
    - [x] 物体の作成時に `ObjectLayer` を渡す。`SetObjectLayer` であとから変更
    - [x] クエリ（レイキャスト）にも同じレイヤーのルールを使える

## 関連ページ

- [Jolt Physics](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)
- [クエリ（レイキャストなど）](queries.md)
