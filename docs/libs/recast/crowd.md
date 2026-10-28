---
title: 群衆と動的な障害物
tags:
  - 外部ライブラリ
  - AI
---

# 群衆と動的な障害物

経路探索だけでは、**多数のキャラがお互いにぶつからずに動く**ことや、ドアが開閉したり、物が置かれたりして、通れる場所が変わることには対応できません。Recast Navigation には、そのための DetourCrowd（群衆）と DetourTileCache（動的な障害物）があります。このページでは、これらの使い方とオフメッシュ リンク・エリアを説明します。

!!! tip "ポイント"
    - <strong>DetourCrowd</strong> ＝ <strong>経路の追従 ＋ お互いの回避</strong>を多数のエージェントでまとめて処理する。
    - 使い方はエージェントを追加 → 目標を設定 → 毎フレーム `update`。
    - DetourTileCache ＝ 障害物の追加・削除で該当するタイルだけを作り直す。
    - オフメッシュ リンク ＝ ジャンプ・はしご・ワープなど、ナビメッシュで表せない接続。
    - エリア ＝ 水・草・溶岩などの種類。通行コストを変えられる。

!!! info "このページを読む前に"
    - [Recast & Detour](index.md)（このセクション全体の地図と、読む順番）
    - [ナビメッシュとは](overview.md)（Recast & Detour の全体像）

## DetourCrowd

**1 体ずつ経路探索と移動を書く**代わりに、`dtCrowd` に任せると、次をまとめて処理してくれます。

| 機能 | 説明 |
| --- | --- |
| 経路の追従 | 目標へ向かう経路を求めて、そのとおりに進む |
| 経路の再探索 | 経路が不正になったとき・目標が動いたときに自動で再探索 |
| 近くのエージェントの回避 | 他のエージェントとぶつからないよう、速度を調整する |
| 壁の回避 | 壁に沿って動く |
| 分離 | エージェントどうしが重ならないよう、少し離れる |
| スライス探索の分散 | 重い探索を複数フレームに分けて処理 |

### 初期化

```cpp
dtCrowd* crowd = dtAllocCrowd();
crowd->init(max_agents, max_agent_radius, nav_mesh);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `maxAgents` | `int` | 同時に扱うエージェントの最大数 |
| `maxAgentRadius` | `float` | エージェントの最大の半径 |
| `nav` | `dtNavMesh*` | ナビメッシュ |

### エージェントの追加

```cpp
dtCrowdAgentParams params = {};
params.radius = 0.6f;
params.height = 2.0f;
params.maxAcceleration = 8.0f;
params.maxSpeed = 3.5f;
params.collisionQueryRange = params.radius * 12.0f;
params.pathOptimizationRange = params.radius * 30.0f;
params.separationWeight = 2.0f;
params.updateFlags = DT_CROWD_ANTICIPATE_TURNS | DT_CROWD_OBSTACLE_AVOIDANCE | DT_CROWD_SEPARATION;

int agent_id = crowd->addAgent(position, &params);
```

| 設定 | 意味 |
| --- | --- |
| `radius` / `height` | 大きさ（ナビメッシュのビルド時と、そろえる） |
| `maxSpeed` / `maxAcceleration` | 最高速度・加速度 |
| `collisionQueryRange` | 他のエージェントを探す範囲（半径の 8〜12 倍） |
| `pathOptimizationRange` | 経路を最適化する範囲（半径の 30 倍程度） |
| `separationWeight` | 離れる力の強さ |
| `updateFlags` | 使う機能のビット（旋回の予測・障害物の回避・分離・経路の最適化など） |
| `obstacleAvoidanceType` | 回避の品質（0〜3 のプリセット。大きいほど細かく、重い） |
| `queryFilterType` | 使うフィルタの番号（キャラの種類ごと） |

### 目標の設定と更新

```cpp
crowd->requestMoveTarget(agent_id, target_ref, target_pos);

crowd->update(delta_time, nullptr);

const dtCrowdAgent* agent = crowd->getAgent(agent_id);
position = agent->npos;
velocity = agent->vel;
```

| 関数 | 説明 |
| --- | --- |
| `requestMoveTarget` | 目標の位置（ポリゴンの参照 ＋ 座標）を設定 |
| `requestMoveVelocity` | 目標ではなく、速度を指定（操作・追従） |
| `resetMoveTarget` | 目標を取り消す |
| `update(dt, debug)` | 毎フレーム 1 回。全エージェントの位置を更新 |
| `getAgent(id)` | 現在の状態。`npos`（位置）・`vel`（速度）・`state`・`targetState` など |
| `removeAgent` | エージェントを削除 |

!!! note "表示との分担"
    DetourCrowd が計算するのは、ナビメッシュ上の位置と速度です。キャラのモデルをその位置に置き、向き・アニメーションは、自分で付けます（速度の向きから向きを決める、など）。物理エンジンとは別の仕組みなので、物理（Jolt など）のボディと併用するなら、どちらを主にするか決めます。

## 動的な障害物：DetourTileCache

**ナビメッシュは、作ったあとで形を変えられません**。ドアの開閉・置かれた箱・壊れる壁に対応するには、障害物を追加・削除して、影響するタイルだけを作り直す仕組みが必要です。それが DetourTileCache です。

| 点 | 説明 |
| --- | --- |
| タイル キャッシュは、圧縮した中間データを持つ | ビルド途中の状態（レイヤー）を圧縮して保存し、障害物の変更時にそこから素早く再構築する |
| 障害物の種類 | 円柱（`addObstacle`）・箱（`addBoxObstacle`）・回転する箱 |
| 反映は `update` で | 障害物の追加・削除はキューに入り、`dtTileCache::update` で数フレームにわけて反映される |
| 事前の準備 | ビルド時にタイル キャッシュ用のデータ（`dtTileCacheLayer`）を作る（Recast のLayers 方式の領域分割） |

```cpp
dtObstacleRef obstacle = 0;
tile_cache->addObstacle(position, radius, height, &obstacle);

tile_cache->update(delta_time, nav_mesh);

tile_cache->removeObstacle(obstacle);
```

| 使いどころ | 説明 |
| --- | --- |
| ドア・バリケード | 閉まったら障害物を追加、開いたら削除 |
| 建築ゲーム | 置いた建物の下を通れなくする |
| 壊れる地形 | 地形の変化に応じて、タイルを作り直す |

数が多いと重いのでナビメッシュを変える必要があるものだけを障害物にします。小さな動くものは、DetourCrowd の回避に任せます。

## オフメッシュ リンク

**ジャンプ・はしご・ワープ**など、歩いてはつながっていない 2 点をナビメッシュのリンクとして登録できます。

| 項目 | 説明 |
| --- | --- |
| 始点・終点・半径 | リンクの両端の位置と有効範囲 |
| 方向 | 一方向（飛び降りる）か、双方向（はしご） |
| エリア・フラグ | 通れる敵の種類を絞る（`ジャンプ可能` のフラグなど） |
| 経路探索での扱い | 普通のポリゴンと同じくグラフの辺として使われる |
| 移動の処理 | リンクを通る移動（ジャンプのアニメーション）は、自分で作る。`findStraightPath` の結果に、リンクの点（フラグ）が含まれる |

ナビメッシュのビルド時にリンクのデータを `dtNavMeshCreateParams` に渡します（`offMeshConVerts` など）。

## エリアと通行コスト

ポリゴンには**エリア ID**（0〜63）と、フラグ（ビット）を付けられます。

| 概念 | 用途 |
| --- | --- |
| エリア | 地面の種類（道・草・水・溶岩）。コストを設定して、通りにくさを変える |
| フラグ | 誰が通れるか（歩ける・泳げる・ドアを開けられる）。通れるか通れないかを絞る |
| 設定 | ビルド時に三角形ごとの `area` を設定（`rcMarkWalkableTriangles` の後にエリアのボリュームで上書きもできる）。実行時は `dtQueryFilter` で、コストとフラグを設定 |

例：水は通れるが遅い（コスト 5）、溶岩は通らない（除外）、道は速い（コスト 0.5 などの小さい値）。

## 注意点と設計

| 点 | 説明 |
| --- | --- |
| **エージェントの数の目安** | DetourCrowd は、数百〜千体程度まで。それ以上はグループ単位の移動など、別の仕組み |
| ナビメッシュと見た目のずれ | キャラの足が地面から浮く・めり込む。`getPolyHeight` で、高さを合わせる |
| 動く足場 | 動く床・エレベーターの上は、ナビメッシュでは扱いにくい。特別な処理を入れる |
| デバッグ描画 | `DebugUtils`（`duDebugDraw`）で、ナビメッシュ・経路・エージェントを描く。自作の描画クラスに実装して使う |
| スレッド | `dtCrowd::update` は、メインスレッド。ナビメッシュのビルドは、別スレッドでできる |

## よくあるミス

??? failure "エージェントの半径がナビメッシュのビルド時と違う"
    壁に刺さる・通れる所を通れない、になります。そろえます。

??? failure "`update` を呼び忘れて、エージェントが動かない"
    `crowd->update(dt, ...)` を毎フレーム呼びます。

??? failure "動く障害物を全部 TileCache の障害物にして重くなる"
    本当にナビメッシュを変えたいものだけにします。

??? failure "ナビメッシュのビルドがレイヤー方式でない"
    TileCache は、**Layers** 方式のデータが必要です。

??? failure "オフメッシュ リンクの移動処理を書かず、キャラが空中を歩く"
    リンクの点が来たら、ジャンプなどの専用の処理に切り替えます。

??? failure "物理エンジンと、DetourCrowd の両方が位置を動かす"
    どちらを主にするか決め、もう一方は追従にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>DetourCrowd</strong>：経路追従 ＋ 回避を多数でまとめて。追加 → 目標 → `update`
    - [x] 位置は`npos`。向きとアニメーションは自分で
    - [x] TileCache：動く障害物にタイル単位で追従。必要なものだけ
    - [x] オフメッシュ リンク：ジャンプ・はしご。移動処理は自作
    - [x] エリア（コスト）とフラグ（通れるか）で、キャラの種類ごとに通行を変える

## 関連ページ

- [Recast & Detour](index.md)
- [ナビメッシュとは](overview.md)
- [Recast：ナビメッシュを作る](build.md)
- [Detour：経路を探す](query.md)
- [Jolt Physics](../jolt/index.md)
