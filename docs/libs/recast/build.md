---
title: Recast：ナビメッシュを作る
tags:
  - 外部ライブラリ
  - AI
---

# Recast：ナビメッシュを作る

Recast は、**ワールドの三角形メッシュ**から、**歩ける場所を自動で見つけて、ナビメッシュにする**ライブラリです。工程は多いですが<strong>やっていることは、「空間を細かい箱（ボクセル）に分け、歩ける箱だけを残し、それを大きなポリゴンにまとめる」</strong>だけです。このページでは、工程の順番と各設定値の意味を説明します。

!!! tip "ポイント"
    - 工程は<strong>ボクセル化 → フィルタ → 領域分割 → 輪郭 → ポリゴン → 詳細メッシュ → Detour 用データ</strong>。
    - <strong>設定値（`rcConfig`）</strong>は、<strong>キャラクターの大きさ</strong>と<strong>ボクセルの細かさ</strong>で決める。
    - <strong>ボクセル（`cs`・`ch`）が細かいほど正確</strong>だが重く、メモリも増える。
    - 大きなマップは<strong>タイル</strong>に分けて作る（部分的に作り直せる）。
    - 作った結果は<strong>ファイルに保存</strong>する。

## 工程の全体

<div class="anim" data-type="graph" data-label="Recast のビルド工程">
n a 三角形メッシュ 0 0
n b ボクセル化 1 0 new
n c フィルタ 2 0
n d コンパクト_ハイトフィールド 3 0
n e 領域分割 4 0
n f 輪郭 5 0
n g ポリゴン 6 0
n h Detour用データ 7 0 new
l a b
l b c
l c d
l d e
l e f
l f g
l g h
</div>

| 工程 | 何をするか | 関数 |
| --- | --- | --- |
| **① ボクセル化** | 三角形を細かい箱の柱（ハイトフィールド）にする | `rcCreateHeightfield`・`rcRasterizeTriangles` |
| **② フィルタ** | 歩けない所（低すぎる天井・崖の縁）を除く | `rcFilter...` |
| **③ コンパクト化** | 歩ける空間だけを効率のよい形で持つ。キャラの半径分だけ縮める | `rcBuildCompactHeightfield`・`rcErodeWalkableArea` |
| **④ 領域分割** | 歩ける面をつながった領域に分ける | `rcBuildDistanceField`・`rcBuildRegions` |
| **⑤ 輪郭** | 領域の外周の線を作り、簡略化する | `rcBuildContours` |
| **⑥ ポリゴン** | 輪郭から、凸ポリゴンを作る | `rcBuildPolyMesh` |
| **⑦ 詳細メッシュ** | 高さの情報を足す（坂・階段のなめらかさ） | `rcBuildPolyMeshDetail` |
| **⑧ Detour 用データ** | ナビメッシュを実行時用のデータにする | `dtCreateNavMeshData` |

## 設定値（`rcConfig`）

```cpp
rcConfig config = {};
config.cs = 0.3f;
config.ch = 0.2f;
config.walkableSlopeAngle = 45.0f;
config.walkableHeight = static_cast<int>(ceilf(2.0f / config.ch));
config.walkableClimb = static_cast<int>(floorf(0.9f / config.ch));
config.walkableRadius = static_cast<int>(ceilf(0.6f / config.cs));
config.maxEdgeLen = static_cast<int>(12.0f / config.cs);
config.maxSimplificationError = 1.3f;
config.minRegionArea = rcSqr(8);
config.mergeRegionArea = rcSqr(20);
config.maxVertsPerPoly = 6;
config.detailSampleDist = 6.0f;
config.detailSampleMaxError = 1.0f;
rcVcopy(config.bmin, bounds_min);
rcVcopy(config.bmax, bounds_max);
rcCalcGridSize(config.bmin, config.bmax, config.cs, &config.width, &config.height);
```

| 設定 | 単位 | 意味 |
| --- | --- | --- |
| **`cs`**（セル サイズ） | ワールド単位 | **水平方向のボクセルの大きさ**。小さいほど正確（0.3 が一般的） |
| **`ch`**（セル高さ） | ワールド単位 | **垂直方向のボクセルの大きさ**。通常 `cs` の半分程度 |
| **`walkableSlopeAngle`** | 度 | **登れる坂の最大角度**。これより急な面は歩けない |
| **`walkableHeight`** | ボクセル数 | **キャラの高さ**（これより低い天井の下は通れない） |
| **`walkableClimb`** | ボクセル数 | **登れる段差の高さ** |
| **`walkableRadius`** | ボクセル数 | **キャラの半径**。壁からこの距離を空ける |
| **`maxEdgeLen`** | ボクセル数 | 輪郭の辺の最大の長さ。長すぎると細長いポリゴンになる |
| **`maxSimplificationError`** | ボクセル数 | 輪郭の簡略化の許容誤差。大きいほど、ポリゴンの辺が少なくなる |
| **`minRegionArea`** | ボクセル数（面積） | これより小さい領域は捨てる（小さな島を消す） |
| **`mergeRegionArea`** | ボクセル数（面積） | これより小さい領域は、隣と結合する |
| **`maxVertsPerPoly`** | 個 | 1 ポリゴンの最大頂点数（3〜6。6 が既定） |
| **`detailSampleDist`**・**`detailSampleMaxError`** | ワールド単位 | 詳細メッシュの細かさ（高さの再現） |
| **`bmin`・`bmax`** | ワールド座標 | ナビメッシュを作る範囲（メッシュの境界） |

!!! note "ワールド単位とボクセル数"
    設定値には**ワールド単位（メートル）で指定するもの**と**ボクセルの個数で指定するもの**が混ざっています。キャラの大きさ（メートル）を決めてから、`cs`・`ch` で割って、ボクセル数に変換します。

### 設定の決め方

| 考え方 | 内容 |
| --- | --- |
| **① キャラの大きさを決める** | 半径（例：0.6 m）・高さ（例：2.0 m）・登れる段差（例：0.9 m）・登れる坂（例：45 度） |
| **② ボクセルの細かさを決める** | `cs` は半径の 1/2 〜 1/3 程度。細かいほど、狭い通路を正しく表せる |
| **③ ボクセル数に変換する** | `ceil(2.0 / ch)` など |
| **④ 結果を見て調整** | デバッグ描画でナビメッシュが壁や段差にどう合っているか確認する |

## コードの流れ

```cpp
rcContext context;

rcHeightfield* solid = rcAllocHeightfield();
rcCreateHeightfield(&context, *solid, config.width, config.height, config.bmin, config.bmax, config.cs, config.ch);

std::vector<unsigned char> triangle_areas(triangle_count, 0);
rcMarkWalkableTriangles(&context, config.walkableSlopeAngle, vertices, vertex_count, indices, triangle_count, triangle_areas.data());
rcRasterizeTriangles(&context, vertices, vertex_count, indices, triangle_areas.data(), triangle_count, *solid, config.walkableClimb);

rcFilterLowHangingWalkableObstacles(&context, config.walkableClimb, *solid);
rcFilterLedgeSpans(&context, config.walkableHeight, config.walkableClimb, *solid);
rcFilterWalkableLowHeightSpans(&context, config.walkableHeight, *solid);

rcCompactHeightfield* compact = rcAllocCompactHeightfield();
rcBuildCompactHeightfield(&context, config.walkableHeight, config.walkableClimb, *solid, *compact);
rcErodeWalkableArea(&context, config.walkableRadius, *compact);
rcBuildDistanceField(&context, *compact);
rcBuildRegions(&context, *compact, 0, config.minRegionArea, config.mergeRegionArea);

rcContourSet* contours = rcAllocContourSet();
rcBuildContours(&context, *compact, config.maxSimplificationError, config.maxEdgeLen, *contours);

rcPolyMesh* poly_mesh = rcAllocPolyMesh();
rcBuildPolyMesh(&context, *contours, config.maxVertsPerPoly, *poly_mesh);

rcPolyMeshDetail* detail_mesh = rcAllocPolyMeshDetail();
rcBuildPolyMeshDetail(&context, *poly_mesh, *compact, config.detailSampleDist, config.detailSampleMaxError, *detail_mesh);
```

| 点 | 説明 |
| --- | --- |
| **`rcContext`** | ログ・タイマー用の入れ物。**エラーや処理時間**を取れる |
| **`rcMarkWalkableTriangles`** | 傾斜から、**歩ける三角形に印**を付ける（`triangle_areas` に歩行可能なエリアの ID を入れる） |
| **`rcFilter...`** | 「低い障害物をまたぐ」「崖の縁を除く」「天井が低い所を除く」 |
| **`rcBuildRegions`** | 領域分割の方法は 3 種類（Watershed・Monotone・Layers）。一般的には Watershed |
| **メモリ確保** | `rcAlloc...` で確保したものは、`rcFree...` で解放する |

!!! note "関数のシグネチャはバージョンで違う"
    ボクセル化のあたりは、バージョンで関数名・引数が変わっています（`rcHeightfield` を参照で渡す形など）。**自分の `Recast.h` を開いて確認**してください。

## 領域分割の方式

| 方式 | 特徴 | 向く場面 |
| --- | --- | --- |
| **Watershed** | 距離場を使い、**きれいな領域**を作る。処理は重め | 一般的・品質重視 |
| **Monotone** | **速い**が細長いポリゴンになりやすい | 高速化したいとき |
| **Layers** | 階層ごとに分ける（**タイル キャッシュ**で使う） | 動的な障害物 |

## Detour 用のデータにする

```cpp
dtNavMeshCreateParams params = {};
params.verts = poly_mesh->verts;
params.vertCount = poly_mesh->nverts;
params.polys = poly_mesh->polys;
params.polyAreas = poly_mesh->areas;
params.polyFlags = poly_mesh->flags;
params.polyCount = poly_mesh->npolys;
params.nvp = poly_mesh->nvp;
params.detailMeshes = detail_mesh->meshes;
params.detailVerts = detail_mesh->verts;
params.detailVertsCount = detail_mesh->nverts;
params.detailTris = detail_mesh->tris;
params.detailTriCount = detail_mesh->ntris;
params.walkableHeight = 2.0f;
params.walkableRadius = 0.6f;
params.walkableClimb = 0.9f;
rcVcopy(params.bmin, poly_mesh->bmin);
rcVcopy(params.bmax, poly_mesh->bmax);
params.cs = config.cs;
params.ch = config.ch;
params.buildBvTree = true;

unsigned char* nav_data = nullptr;
int nav_data_size = 0;
dtCreateNavMeshData(&params, &nav_data, &nav_data_size);
```

| 点 | 説明 |
| --- | --- |
| **`polyFlags`** | **ポリゴンごとの通行の種類**のビット（歩く・泳ぐ・ドア）。**後でフィルタで絞る**（[Detour](query.md)） |
| **`polyAreas`** | **エリアの種類**（水・草・溶岩）。**通行コスト**を変えられる |
| **`walkableHeight` など** | ここは**ワールド単位**で渡す（`rcConfig` はボクセル数） |
| **`buildBvTree`** | 検索を速くするための木。`true` が一般的 |
| **戻り値のバッファ** | `dtFree` で解放する（`DT_TILE_FREE_DATA` で `dtNavMesh` に渡せば、まとめて解放される） |

## タイル

大きなマップを 1 つのナビメッシュで作ると、**ビルドが重く**、**一部を変更しただけでも全体を作り直す**ことになります。**マップをタイル（正方形）に分けて**作ります。

| 点 | 説明 |
| --- | --- |
| **`tileSize`** | 1 タイルの大きさ（ボクセル数。32〜128 が一般的） |
| **`borderSize`** | タイルの境界の余白（`walkableRadius + 3` 程度）。隣のタイルとつなぐため |
| **タイルごとにビルド** | 範囲 `bmin`・`bmax` をタイルごとに設定して、同じ工程を繰り返す |
| **利点** | 部分的な作り直し・並列ビルド・ストリーミング（必要なタイルだけ読み込む） |

## 保存と読み込み

ナビメッシュのデータ（`nav_data`）は、**そのままバイナリでファイルに保存**できます。

| 点 | 説明 |
| --- | --- |
| **保存する単位** | 1 タイルごとにヘッダ ＋ データ |
| **実行時** | ファイルを読み、`dtNavMesh::addTile` で追加する（[Detour](query.md)） |
| **バージョン管理** | データの形式を変えたら、**バージョン番号**を持たせて、古いファイルを弾く（[ベイク](../../optimize/baking.md)） |

## よくあるミス

??? failure "ナビメッシュが、壁にめり込んでいる・壁から離れすぎている"
    `walkableRadius` と、`cs` の細かさを確認します。細かいほど、壁に沿います。

??? failure "階段・坂が歩けない"
    `walkableClimb`（段差）と `walkableSlopeAngle`（坂）が小さすぎます。

??? failure "狭い通路が、つぶれて消える"
    `cs` が大きすぎます。キャラの半径に対して、細かくします。

??? failure "細長くて、歩きにくい形のポリゴンができる"
    `maxEdgeLen`・`maxSimplificationError` を小さくします。

??? failure "ボクセルを細かくしすぎて、ビルドが終わらない・メモリが足りない"
    マップが大きいなら、**タイル分割**します。

??? failure "ワールド単位とボクセル数を、取り違える"
    `rcConfig` の多くは、ボクセル数です。メートルを `cs`・`ch` で割ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 工程は<strong>ボクセル化 → フィルタ → 領域 → 輪郭 → ポリゴン → 詳細 → Detour 用</strong>
    - [x] 設定は<strong>キャラの大きさ（半径・高さ・段差・坂）</strong>と<strong>ボクセルの細かさ</strong>
    - [x] <strong>ワールド単位とボクセル数</strong>を取り違えない
    - [x] 大きなマップは<strong>タイル</strong>に分ける
    - [x] <strong>ビルド時に作って、ファイルに保存</strong>。実行時は読み込むだけ

## 関連ページ

- [Recast & Detour](index.md)
- [ナビメッシュとは](overview.md)
- [Detour：経路を探す](query.md)
- [群衆と動的な障害物](crowd.md)
- [ベイク](../../optimize/baking.md)
