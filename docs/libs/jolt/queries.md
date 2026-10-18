---
title: クエリ（レイキャストなど）
tags:
  - 外部ライブラリ
  - 物理演算
---

# クエリ（レイキャストなど）

**クエリ**は、**物理の世界に、問い合わせる**操作です。<strong>「この線上に、何がある？」（レイキャスト）</strong>、<strong>「この球を動かしたら、何に当たる？」（形状キャスト）</strong>、<strong>「この範囲に、何がある？」（重なり判定）</strong>など。**物体を動かさず**に、**当たりの情報だけ**を得られます。**射撃（ヒットスキャン）・視線が通るか・地面の高さ・ピッキング**などに使います（[ピッキングとレイキャスト](../../3d/picking-raycast.md)）。このページは、**主なクエリの種類**、**書き方**、**レイヤーによる絞り込み**、**結果の読み方**をまとめます。

!!! tip "ポイント"
    - クエリは <strong>`physics_system.GetNarrowPhaseQuery()`</strong>（正確な判定）と <strong>`GetBroadPhaseQuery()`</strong>（大まかな範囲の判定）から呼ぶ。
    - <strong>`CastRay`</strong> は<strong>線（レイ）が、最初に当たる物体</strong>を調べる。<strong>`RRayCast(始点, 向き)` の「向き」は、長さを持つ方向ベクトル</strong>（<strong>終点 − 始点</strong>）。
    - 結果は <strong>`mFraction`（0〜1：レイのどの位置で当たったか）</strong>と <strong>`mBodyID`</strong>。<strong>当たった点 ＝ 始点 ＋ 向き × `mFraction`</strong>。
    - <strong>形状キャスト（`CastShape`）</strong>は<strong>球・カプセルなどを、動かしてみて、当たるか</strong>を調べる（<strong>太い線</strong>）。
    - <strong>レイヤーのフィルター</strong>で、<strong>どの物体を対象にするか</strong>を絞る。<strong>自分自身は、除外</strong>する。
    - <strong>複数の当たりを、すべて</strong>知りたいなら<strong>コレクター（`CastRayCollector`）</strong>。
    - <strong>クエリは `Update` の外で</strong>呼ぶ（スレッド安全だが、<strong>`Update` と同時に、物体が変わる</strong>ため）。

## クエリの種類

| クエリ | 問い | 用途 |
| --- | --- | --- |
| **`CastRay`** | **この線の上に、何があるか** | **射撃・視線・地面の高さ・マウスのピッキング** |
| **`CastShape`** | **この形を動かしたら、何に当たるか** | **キャラクターの移動の予測・太い光線・スイープ** |
| **`CollideShape`** | **この形は、今、何と重なっているか** | **近接攻撃の判定・範囲ダメージ・エリアの内外** |
| **`CollidePoint`** | **この点は、どの物体の中にあるか** | **点の内外判定** |
| **`CollideAABox` / `CollideSphere`**（ブロードフェーズ） | **この範囲に、どの物体がいるか**（**大まかに**） | **周囲の物体の列挙・爆発の範囲** |

```cpp
const NarrowPhaseQuery& query = physics_system.GetNarrowPhaseQuery();
const BroadPhaseQuery& broad_query = physics_system.GetBroadPhaseQuery();
```

## レイキャスト（CastRay）

### 最初の 1 つだけ（最も簡単）

```cpp
RRayCast ray(origin, direction * max_distance);

RayCastResult hit;
bool did_hit = query.CastRay(ray, hit,
                             SpecifiedBroadPhaseLayerFilter(BroadPhaseLayers::MOVING),
                             SpecifiedObjectLayerFilter(Layers::ENEMY),
                             IgnoreSingleBodyFilter(shooter_id));

if (did_hit) {
  RVec3 hit_point = ray.GetPointOnRay(hit.mFraction);
  BodyID hit_body = hit.mBodyID;
}
```

| 点 | 説明 |
| --- | --- |
| **`RRayCast(origin, direction)`** | **始点**と、<strong>方向ベクトル（長さ付き）</strong>。**終点 ＝ `origin + direction`** |
| **`direction * max_distance`** | **方向（正規化済み）× 最大の距離<strong>で、</strong>届く距離**を決める |
| **`RayCastResult`** | **最初に当たった 1 つ**の結果 |
| **`hit.mFraction`** | **レイの何割の位置**で当たったか（**0 で始点、1 で終点**） |
| **`ray.GetPointOnRay(fraction)`** | **当たった点**（`origin + direction * fraction`） |
| **`hit.mBodyID`** | **当たった物体** |
| **`hit.mSubShapeID2`** | **複合形状の、どの部品に当たったか** |

**距離を知りたい**場合は、**`hit.mFraction * max_distance`** です。

### 当たった面の法線

<strong>法線（当たった面の向き）</strong>が欲しいときは、**物体のロック**を取って、**形に問い合わせます**。

```cpp
BodyLockRead lock(physics_system.GetBodyLockInterface(), hit.mBodyID);
if (lock.Succeeded()) {
  const Body& body = lock.GetBody();
  Vec3 normal = body.GetWorldSpaceSurfaceNormal(hit.mSubShapeID2, hit_point);
}
```

**弾痕の向き・反射**に使います。

### 全部の当たりを集める（コレクター）

**最初の 1 つだけでなく、レイ上の全部**（貫通する弾）を知りたいときは、**コレクター**を使います。

```cpp
AllHitCollisionCollector<CastRayCollector> collector;
RayCastSettings settings;
query.CastRay(ray, settings, collector, bp_filter, obj_filter, body_filter);

collector.Sort();
for (const RayCastResult& r : collector.mHits) {
  ...
}
```

| コレクター | 動き |
| --- | --- |
| **`ClosestHitCollisionCollector`** | **最も近い 1 つだけ** |
| **`AllHitCollisionCollector`** | **すべての当たり**を溜める（`Sort()` で、近い順に） |
| **`AnyHitCollisionCollector`** | **1 つでも当たれば、すぐ終了**（**視線が通るか**だけ知りたいとき。**最速**） |

### 視線が通るか（遮蔽の判定）

```cpp
bool CanSee(RVec3 from, RVec3 to) {
  RRayCast ray(from, to - from);
  AnyHitCollisionCollector<CastRayCollector> collector;
  query.CastRay(ray, RayCastSettings(), collector, bp_filter, obj_filter, body_filter);
  return !collector.HadHit();
}
```

**敵がプレイヤーを見えるか**（壁に遮られていないか）に使います。**`AnyHit` なので、速い**です。

## 形状キャスト（CastShape）

**形（球・カプセル）を、動かしてみて**、**最初に何に当たるか**を調べます。**太さのある光線**です。

```cpp
ShapeRefC sphere = new SphereShape(0.3f);
RShapeCast shape_cast = RShapeCast::sFromWorldTransform(
    sphere, Vec3::sReplicate(1.0f), RMat44::sTranslation(start), end - start);

ShapeCastSettings settings;
ClosestHitCollisionCollector<CastShapeCollector> collector;
query.CastShape(shape_cast, settings, start, collector, bp_filter, obj_filter, body_filter);

if (collector.HadHit()) {
  float fraction = collector.mHit.mFraction;
}
```

| 用途 | 説明 |
| --- | --- |
| **キャラクターが、前に進めるか** | **カプセルを、進行方向にキャスト** |
| **カメラの壁抜け防止** | **球を、注視点からカメラへ**キャスト（[カメラ](../../3d/camera.md)） |
| **太い弾・ビーム** | **球・カプセルを飛ばす** |
| **段差の検出** | **足元に向けて、キャスト** |

**細いレイ（`CastRay`）では、すり抜ける**ような**隙間・段差**にも、**形状キャスト**は、**正しく**反応します。

## 重なり判定（CollideShape・CollidePoint）

**動かさず、今の位置で、何と重なっているか**を調べます。

```cpp
ShapeRefC sphere = new SphereShape(radius);
AllHitCollisionCollector<CollideShapeCollector> collector;
CollideShapeSettings settings;

query.CollideShape(sphere, Vec3::sReplicate(1.0f), RMat44::sTranslation(center), settings,
                   center, collector, bp_filter, obj_filter, body_filter);

for (const CollideShapeResult& r : collector.mHits) {
  BodyID id = r.mBodyID2;
}
```

| 用途 | 説明 |
| --- | --- |
| **近接攻撃の判定** | **剣の振りの範囲**と、重なっている敵 |
| **爆発の範囲ダメージ** | **球で、重なっている物体**を取る |
| **エリア内の敵の数** | **範囲に、何がいるか** |
| **スポーン位置の確認** | **その位置が、何かと重なっていないか** |

**範囲だけで十分**（形の正確さが、いらない）なら、**ブロードフェーズのクエリ**（`CollideAABox`・`CollideSphere`）が、**速い**です。

```cpp
AllHitCollisionCollector<CollideShapeBodyCollector> collector;
broad_query.CollideSphere(center, radius, collector, bp_filter, obj_filter);
```

**物体の境界ボックス**との重なりを返す**だけ**で、**形の正確な判定は、しません**。

## レイヤーとフィルター

**クエリの対象を、絞ります**。

| フィルター | 役割 |
| --- | --- |
| **`BroadPhaseLayerFilter`** | **どのブロードフェーズ レイヤーを、対象にするか** |
| **`ObjectLayerFilter`** | **どのオブジェクト レイヤーを、対象にするか** |
| **`BodyFilter`** | **特定の物体を、除外・指定**する |
| **`ShapeFilter`** | **複合形状の、特定の部品を、除外** |

### よく使うフィルター

```cpp
DefaultBroadPhaseLayerFilter bp_filter(object_vs_broadphase_filter, Layers::PLAYER_BULLET);
DefaultObjectLayerFilter obj_filter(object_pair_filter, Layers::PLAYER_BULLET);

IgnoreSingleBodyFilter body_filter(shooter_id);
```

| フィルター | 意味 |
| --- | --- |
| **`DefaultBroadPhaseLayerFilter` / `DefaultObjectLayerFilter`** | <strong>「このレイヤーの物体が、衝突する相手」</strong>だけを対象（**衝突のルールを、そのまま使う**） |
| **`SpecifiedObjectLayerFilter(layer)`** | **指定した 1 つのレイヤーだけ** |
| **`IgnoreSingleBodyFilter(id)`** | **指定した物体を、除外**（**撃った本人、自分自身**） |
| **`IgnoreMultipleBodiesFilter`** | **複数を除外** |

!!! warning "自分自身を、除外する"
    **プレイヤーの位置から、レイを飛ばす**と、**自分自身にすぐ当たります**。**`IgnoreSingleBodyFilter`** で、**自分を除外**します。**始点を、体の外に少しずらす**方法もあります。

## 結果の使い方

| 結果 | 使い方 |
| --- | --- |
| **`mBodyID`** | **`BodyInterface::GetUserData(id)`** で、**ゲームのエンティティ**を取得（[統合](integration.md)） |
| **当たった点** | **`ray.GetPointOnRay(fraction)`** → **着弾の効果・弾痕** |
| **法線** | **反射・弾痕の向き** |
| **距離** | **`fraction × 長さ`** → **ダメージの距離減衰** |

## 使いどころ

| 場面 | クエリ |
| --- | --- |
| **ヒットスキャンの射撃** | <strong>`CastRay`（最も近い 1 つ）</strong> |
| **貫通する弾** | <strong>`CastRay`（全部の当たり）</strong> |
| **敵の視線判定** | <strong>`CastRay`（`AnyHit`）</strong> |
| **地面の高さ・接地判定** | **足元から、真下へ `CastRay`** |
| **マウスのクリックで、物体を選ぶ** | **カメラからのレイ**（[ピッキング](../../3d/picking-raycast.md)） |
| **カメラの壁抜け防止** | **球の `CastShape`** |
| **近接攻撃・範囲攻撃** | **`CollideShape`** |
| **周囲の物体の列挙** | **ブロードフェーズの `CollideSphere`** |

## 性能

| 点 | 説明 |
| --- | --- |
| **`AnyHit` は最速** | **1 つ見つかれば、すぐ終了** |
| **範囲・レイヤーを絞る** | **対象が少ないほど速い** |
| **毎フレームの大量のクエリ** | **数百本までは軽い**。**数千本以上**は、**まとめて**・**頻度を下げる**（[フレーム時間の設計](../../optimize/frame-budget.md)） |
| **結果を溜める** | **コレクターの、確保**を**使い回す**（[毎フレームのヒープ確保を避ける](../../optimize/frame-allocation.md)） |

<!-- fig:raycast-hit:begin -->

<svg class="fig illust motion" data-fig="raycast-hit" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-raycast-hit" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイキャスト: 線を伸ばし、最初に当たった物を返す</text>
<rect x="250" y="200" width="80" height="80" fill="#2563eb" opacity="0.85"/>
<text x="290.0" y="245.0" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#ffffff">B1</text>
<rect x="430" y="150" width="90" height="80" fill="#2ea043" opacity="0.85"/>
<text x="475.0" y="195.0" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#ffffff">B2</text>
<circle cx="90.0" cy="300.0" r="8" fill="#1f2937"/>
<text x="90.0" y="326.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">レイの始点</text>
<line x1="90.0" y1="300.0" x2="90.0" y2="300.0" stroke="#e5484d" stroke-width="3.5"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.3704;1.0000" values="90;90;250;250"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.3704;1.0000" values="300;300;260;260"/></line>
<line x1="250.0" y1="260.0" x2="633.2798000813858" y2="164.18004997965355" stroke="#e5484d" stroke-width="2" stroke-dasharray="5 5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/></line>
<circle cx="250.0" cy="260.0" r="9" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000" values="0;0;1;1"/></circle>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">始点と向きから、直線を伸ばす<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">線を伸ばしていく<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最初に B1 に当たった。距離 165<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="360" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">B2 も線の先にあるが、手前の B1 に遮られる。通常は、最初の 1 つだけ返す<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:raycast-hit:end -->

## よくあるミス

??? failure "`RRayCast` の第 2 引数に、正規化した方向を、そのまま渡して、短すぎる"
    <strong>第 2 引数は、「長さのある、方向ベクトル」</strong>です。**`direction * max_distance`** にします。

??? failure "自分自身に、レイが当たる"
    **`IgnoreSingleBodyFilter`** で、除外します。

??? failure "レイキャストが、何にも当たらない"
    **レイヤーのフィルター**が、**対象を除外**していないか、**`NarrowPhaseQuery`** に、物体が追加されて（`OptimizeBroadPhase` の後）いるか、確認します。

??? failure "`mFraction` を、そのまま距離として使う"
    **0〜1 の割合**です。**距離 ＝ `mFraction` × レイの長さ**。

??? failure "`Update` の最中に、クエリを呼んで、不整合になる"
    **`Update` の外**で呼びます。

??? failure "細い隙間を、`CastRay` で判定して、すり抜ける"
    <strong>`CastShape`（太さのある形）</strong>を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] クエリは <strong>`GetNarrowPhaseQuery()`</strong>。<strong>`CastRay`（線）・`CastShape`（太い線）・`CollideShape`（重なり）</strong>
    - [x] <strong>`RRayCast(始点, 方向 × 距離)`</strong>。<strong>結果の `mFraction` は 0〜1 の割合</strong>（<strong>当たった点 ＝ `GetPointOnRay(fraction)`</strong>）
    - [x] <strong>コレクター</strong>：<strong>`Closest`（最も近い 1 つ）・`All`（全部）・`Any`（1 つでも。最速）</strong>
    - [x] <strong>フィルターで、レイヤーと物体を絞る</strong>。<strong>自分自身を、除外</strong>
    - [x] <strong>`mBodyID` → `GetUserData`</strong> で、<strong>ゲームのエンティティ</strong>へ
    - [x] <strong>`Update` の外で呼ぶ</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [レイヤー](layers.md)
- [形（Shape）](shapes.md)
- [ECS・ゲームとの連携](integration.md)
- [ピッキングとレイキャスト](../../3d/picking-raycast.md)
- [3D の衝突判定](../../3d/collision-3d.md)
