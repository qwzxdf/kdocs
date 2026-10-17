---
title: 物理演算の全体像
tags:
  - 外部ライブラリ
  - 物理演算
---

# 物理演算の全体像

Jolt の部品（世界・物体・形・レイヤー・制約）が、**どうつながっているか**の見取り図です。

## 物理演算の全体像

| 用語 | 意味 |
| --- | --- |
| `PhysicsSystem` | **物理の世界**。物体、制約、衝突の判定をまとめて持つ。`Update` で時間を進める |
| `Body` | **物体**。位置、向き、速度、形を持つ |
| `BodyID` | 物体を指す**番号**（ポインタではない）。[ハンドル](../../engine/handle.md)と同じ考え方 |
| `BodyInterface` | 物体を作る・追加する・動かす**窓口**（`physics_system.GetBodyInterface()`） |
| `Shape` | 物体の**形**。`BoxShape`、`SphereShape`、`CapsuleShape`、`MeshShape` など |
| `EMotionType` | **動き方**。`Static`（動かない地面）、`Kinematic`（プログラムで動かす）、`Dynamic`（物理で動く） |
| レイヤー | **何と何が衝突するか**を決める分類（`ObjectLayer`、`BroadPhaseLayer`） |
| `JobSystem` | 物理の計算を、複数のスレッドに分けて動かす仕組み |
| `TempAllocator` | 1 回の `Update` の間だけ使う**一時メモリ**（[アリーナ](../../stl/memory/pmr.md)） |
| 制約（Constraint） | 物体どうしをつなぐ（ヒンジ、バネ、固定など） |
| `CharacterVirtual` | **キャラクターの移動**専用の、軽い仕組み（剛体として扱わない） |

<div class="anim" data-type="graph" data-label="Jolt の世界の構造">
n sys PhysicsSystem 0 1 hit
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1
n chara プレイヤー 2 2
# 物理の世界（PhysicsSystem）がある
---
n sys PhysicsSystem 0 1
n floor 地面_Static 2 0 new
n ball ボール_Dynamic 2 1 new
n chara プレイヤー 2 2
l sys floor new 物体を追加
l sys ball new 物体を追加
# Body（物体）を追加していく。地面は動かない（Static）、ボールは物理で動く（Dynamic）
---
n sys PhysicsSystem 0 1
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1
n chara プレイヤー 2 2 new
l sys floor
l sys ball
l sys chara new CharacterVirtual
# プレイヤーは剛体にせず、キャラクター専用の仕組み（CharacterVirtual）で動かす
---
n sys PhysicsSystem 0 1 hit
n floor 地面_Static 2 0
n ball ボール_Dynamic 2 1 hit
n chara プレイヤー 2 2 hit
l sys floor
l sys ball hit Update
l sys chara hit Update
# Update(1/60 秒) で、時間が進む。物体が動き、衝突が解決される
</div>



## Jolt が得意なこと・不得意なこと

| 得意 | 不得意・注意 |
| --- | --- |
| 大量の剛体（数千〜数万個）を、**マルチスレッドで速く**動かす | **2D 専用ではない**（2D は Box2D など。Jolt で 2D を表現するなら、Z 軸を固定する） |
| **キャラクターの移動**（階段、坂、動く床）の専用機能 | 初期設定（レイヤー、初期化）が**長い**。最初の壁になる |
| 決定的な（再現できる）シミュレーション（リプレイ、ネットワーク同期） | 流体、布などは**標準では持たない**（ソフトボディは対応） |
| 車両、ラグドール、ソフトボディ | ドキュメントは、英語（公式の Docs と、HelloWorld、Samples が情報源） |
| メモリが少なく、動きが安定している | |


## 物理を使うときの考え方

| 考え方 | 説明 |
| --- | --- |
| 物理の世界と、**ゲームの世界は別**のものとして持つ | ゲームのオブジェクト（エンティティ）は、`BodyID` を**持つ**。毎フレーム、物理の位置を、ゲームの Transform に**コピー**する |
| **固定のステップ**で更新する | 可変の `dt` を渡すと、結果が不安定になる。`dt` は 1/60 などで固定し、足りない時間は複数回 `Update` する（[ゲームループと固定タイムステップ](../../engine/game-loop.md)） |
| **キャラクターは剛体にしない** | プレイヤーの動きは、`CharacterVirtual`（[キャラクター](character.md)）で、ゲームに合う操作感を作る |
| **衝突の分類を先に決める** | 「プレイヤーと弾は衝突する、弾どうしは衝突しない」など、レイヤーの設計を最初にする |

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)

