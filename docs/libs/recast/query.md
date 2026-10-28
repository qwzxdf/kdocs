---
title: Detour：経路を探す
tags:
  - 外部ライブラリ
  - AI
---

# Detour：経路を探す

Detour は、**作ったナビメッシュを読み込み、その上で経路探索や位置の問い合わせをする**ライブラリです。ゲームの実行時に使うのは、ほぼ Detour だけです。`dtNavMesh`（データ）と`dtNavMeshQuery`（問い合わせ）の 2 つを組み合わせて使います。このページでは、読み込みから、最寄りの点の検索・経路探索・直線化・レイキャストまでを説明します。

!!! tip "ポイント"
    - <strong>`dtNavMesh`</strong> ＝ ナビメッシュのデータ。<strong>`dtNavMeshQuery`</strong> ＝ 問い合わせ。クエリはスレッドごとに 1 つ。
    - 位置はポリゴンの参照（`dtPolyRef`）＋座標で表す。まず最寄りのポリゴンを探す。
    - 経路探索（`findPath`）の結果はポリゴンの列。`findStraightPath` で、歩く点の列にする。
    - `dtQueryFilter` で、通れるポリゴンの種類と、エリアごとのコストを決める。
    - ナビメッシュ上にない点は、そのまま使えない。補正する。
    - 経路は毎フレーム探さない。目標が変わったとき、または一定間隔で。

!!! info "このページを読む前に"
    - [Recast & Detour](index.md)（このセクション全体の地図と、読む順番）
    - [ナビメッシュとは](overview.md)（Recast & Detour の全体像）

## 読み込み

```cpp
dtNavMesh* nav_mesh = dtAllocNavMesh();
dtNavMeshParams params = {};
params.orig[0] = origin_x;
params.orig[1] = origin_y;
params.orig[2] = origin_z;
params.tileWidth = tile_size_in_world;
params.tileHeight = tile_size_in_world;
params.maxTiles = max_tiles;
params.maxPolys = max_polys_per_tile;
nav_mesh->init(&params);

nav_mesh->addTile(tile_data, tile_data_size, DT_TILE_FREE_DATA, 0, nullptr);

dtNavMeshQuery* query = dtAllocNavMeshQuery();
query->init(nav_mesh, 2048);
```

| 点 | 説明 |
| --- | --- |
| <strong>単一のナビメッシュ（タイルなし）</strong> | `nav_mesh->init(data, size, DT_TILE_FREE_DATA)` でもよい |
| タイル方式 | `init(&params)` のあとにタイルごとに `addTile` |
| `DT_TILE_FREE_DATA` | `dtNavMesh` がデータの解放を引き受ける（呼び出し側で解放しない） |
| `init(nav_mesh, maxNodes)` | クエリの探索で使うノード数の上限。大きいマップなら増やす（2048〜65535） |
| 解放 | `dtFreeNavMeshQuery(query)`・`dtFreeNavMesh(nav_mesh)` |

## 位置：ポリゴン参照

Detour では、**どのポリゴンの上にいるか**を `dtPolyRef`（ポリゴンの ID）で表します。ワールド座標だけでは、経路探索を始められません。

```cpp
dtQueryFilter filter;
filter.setIncludeFlags(0xffff);
filter.setExcludeFlags(0);

float half_extents[3] = {2.0f, 4.0f, 2.0f};
float nearest[3];
dtPolyRef start_ref = 0;
query->findNearestPoly(start_pos, half_extents, &filter, &start_ref, nearest);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `center` | `const float*` | 探す中心（ワールド座標 `float[3]`） |
| `halfExtents` | `const float*` | 探す範囲（箱の半分の大きさ）。高さ方向を大きめに |
| `filter` | `const dtQueryFilter*` | 通れるポリゴンの条件 |
| `nearestRef` | `dtPolyRef*` | 見つかったポリゴンの ID（見つからなければ 0） |
| `nearestPt` | `float*` | ナビメッシュ上の最寄りの点 |

| 点 | 説明 |
| --- | --- |
| 補正する | 敵の足元・クリックした位置は、ナビメッシュ上にぴったりとはない。範囲を指定して、最寄りを探す |
| 範囲が小さすぎると見つからない | 高さ方向（`halfExtents[1]`）を段差より大きく取る |
| 戻り値 | `dtStatus`。`dtStatusSucceed(status)` で成功を確認する |

## 経路探索

```cpp
std::array<dtPolyRef, 256> path;
int path_count = 0;
query->findPath(start_ref, end_ref, start_nearest, end_nearest, &filter,
                path.data(), &path_count, static_cast<int>(path.size()));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `startRef` / `endRef` | `dtPolyRef` | 開始・目標のポリゴン |
| `startPos` / `endPos` | `const float*` | 開始・目標の座標（ナビメッシュ上） |
| `filter` | `const dtQueryFilter*` | 通行の条件・コスト |
| `path` | `dtPolyRef*` | 結果の**ポリゴンの列** |
| `pathCount` | `int*` | 結果の個数 |
| `maxPath` | `int` | `path` の大きさ |

| 点 | 説明 |
| --- | --- |
| アルゴリズム | A*（ポリゴンのグラフ上） |
| 結果は不完全なことがある | 目標に届かない（行き止まり）場合は最も近い所までの経路が返る。`status` に `DT_PARTIAL_RESULT` が立つ |
| ポリゴンの列 | まだ歩く点ではない。次の `findStraightPath` で、点にする |
| 探索ノード数の上限 | クエリの `maxNodes` を超えると、途中で終わる |

## 直線化（ストリング プル）

ポリゴンの列から、**角で曲がる、実際に歩く点の列**を作ります。

```cpp
std::array<float, 256 * 3> straight_path;
std::array<unsigned char, 256> straight_flags;
std::array<dtPolyRef, 256> straight_refs;
int straight_count = 0;
query->findStraightPath(start_nearest, end_nearest, path.data(), path_count,
                        straight_path.data(), straight_flags.data(), straight_refs.data(),
                        &straight_count, 256);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `startPos` / `endPos` | `const float*` | 始点・終点 |
| `path` / `pathSize` | `const dtPolyRef*`, `int` | `findPath` の結果 |
| `straightPath` | `float*` | 結果の点の列（`xyz` × 個数） |
| `straightPathFlags` | `unsigned char*` | 各点の種類（開始・終了・オフメッシュ リンク） |
| `straightPathRefs` | `dtPolyRef*` | 各点が属するポリゴン |
| `straightPathCount` | `int*` | 結果の個数 |
| `maxStraightPath` | `int` | 配列の大きさ |

| 点 | 説明 |
| --- | --- |
| キャラはこの点を順にたどる | 各点へ向かって移動し、近づいたら次へ |
| オプション | 最後の引数（`options`）で、エリアの境界ごとに点を足すこともできる |
| 点の種類 | `DT_STRAIGHTPATH_OFFMESH_CONNECTION` が立つ点は、ジャンプ・はしごなど |

## 通行条件：`dtQueryFilter`

| 設定 | 説明 |
| --- | --- |
| **`setIncludeFlags` / `setExcludeFlags`** | ポリゴンのフラグで通れるものを絞る（例：飛べる敵は水の上も通れる） |
| `setAreaCost(area, cost)` | エリア（水・草・溶岩）ごとの通りにくさ。コストを大きくすると遠回りしてでも避ける |
| フィルタはキャラの種類ごとに作る | 人間・動物・飛行などでフィルタを使い分ける |

## そのほかの問い合わせ

| 関数 | 用途 |
| --- | --- |
| **`raycast`** | ナビメッシュ上で壁に当たるまで直進する。見通しの判定・動ける距離を調べる |
| `moveAlongSurface` | 壁にぶつかったら滑るように移動した結果を返す（キャラの移動の補正） |
| `findRandomPoint` | ナビメッシュ上のランダムな点（巡回・スポーン位置） |
| `findRandomPointAroundCircle` | ある点の周りのランダムな点（うろつく） |
| `getPolyHeight` | その点のナビメッシュの高さ（足元の高さに合わせる） |
| `closestPointOnPoly` | ポリゴン上の最も近い点 |
| `findDistanceToWall` | 最も近い壁までの距離 |
| `findPolysAroundCircle` | 円内のポリゴンの一覧（範囲の探索） |

## 使い方の流れ（敵が目標へ向かう）

| 手順 | 内容 |
| --- | --- |
| **① 位置を補正** | 自分と目標の位置を `findNearestPoly` でナビメッシュ上へ |
| ② 経路探索 | `findPath` でポリゴンの列 |
| ③ 直線化 | `findStraightPath` で、歩く点の列 |
| ④ 移動 | 次の点へ向かって歩く。近づいたら次の点へ |
| ⑤ 再探索 | 目標が動いたら、一定間隔（0.5 秒など）で、あるいは目標が遠く動いたときだけ |

## パフォーマンス

| 点 | 説明 |
| --- | --- |
| **毎フレームの探索を避ける** | 探索は 1 回数十マイクロ秒〜数ミリ秒。数百体が毎フレーム探すと重い |
| 分散する | 敵ごとに探索するフレームをずらす |
| 経路のキャッシュ | 目標が動かないなら、前の結果を使う |
| スライス探索 | `initSlicedFindPath` / `updateSlicedFindPath` で、数フレームにまたがって探索する（大きなマップ） |
| スレッド | クエリ（`dtNavMeshQuery`）はスレッドごとに別。`dtNavMesh` は読み取りだけなら共有できる |

## よくあるミス

??? failure "ナビメッシュ上にない座標をそのまま `findPath` に渡す"
    先に `findNearestPoly` で補正します。見つからないときは、範囲（`halfExtents`）を大きくします。

??? failure "`findNearestPoly` の高さの範囲が小さく、見つからない"
    高さ方向を大きくします（キャラの身長程度）。

??? failure "`findPath` の結果をそのままキャラの座標の列として使う"
    ポリゴンの列です。`findStraightPath` で点にします。

??? failure "到達できない目標に対し、`DT_PARTIAL_RESULT` を無視して動く"
    行き止まりの手前で止まります。ステータスを確認して、動作を決めます。

??? failure "複数のスレッドで、同じ `dtNavMeshQuery` を使う"
    スレッドごとにクエリを作ります。

??? failure "毎フレーム、全ての敵が経路探索をする"
    間隔を空けて、ずらします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`dtNavMesh`（データ）と `dtNavMeshQuery`（問い合わせ）</strong>。クエリはスレッドごと
    - [x] まず`findNearestPoly` で、ナビメッシュ上の位置に補正
    - [x] `findPath` → `findStraightPath` で、歩く点の列
    - [x] `dtQueryFilter` で、通行条件・エリアのコスト
    - [x] `raycast`・`moveAlongSurface`・`findRandomPoint` も便利
    - [x] 経路探索は間隔を空けて

## 関連ページ

- [Recast & Detour](index.md)
- [ナビメッシュとは](overview.md)
- [Recast：ナビメッシュを作る](build.md)
- [群衆と動的な障害物](crowd.md)
