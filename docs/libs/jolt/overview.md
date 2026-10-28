---
title: 物理演算の全体像
tags:
  - 外部ライブラリ
  - 物理演算
---

# 物理演算の全体像

Jolt の部品（世界・物体・形・レイヤー・制約）が**どうつながっているか**の見取り図です。

!!! info "このページを読む前に"
    - [Jolt Physics](index.md)（このセクション全体の地図と、読む順番）


## 物理演算の全体像

物理エンジンは、ゲームの絵とは別に、**もう 1 つの小さな世界**を持っています。その世界には「重力で落ちる箱」や「壁にぶつかる球」だけがあり、見た目（メッシュやテクスチャ）は存在しません。ゲームは毎フレーム、この物理の世界を少し進め、結果の位置と向きを自分の描画用のオブジェクトに写します。

Jolt の用語は、この「別の世界」を作る部品に対応しています。まず全体の登場人物を表で確認し、そのあとで、それぞれの役割を文章で説明します。

| 用語 | 意味 |
| --- | --- |
| `PhysicsSystem` | 物理の世界。物体、制約、衝突の判定をまとめて持つ。`Update` で時間を進める |
| `Body` | 物体。位置、向き、速度、形を持つ |
| `BodyID` | 物体を指す番号（ポインタではない）。[ハンドル](../../engine/handle.md)と同じ考え方 |
| `BodyInterface` | 物体を作る・追加する・動かす窓口（`physics_system.GetBodyInterface()`） |
| `Shape` | 物体の形。`BoxShape`、`SphereShape`、`CapsuleShape`、`MeshShape` など |
| `EMotionType` | 動き方。`Static`（動かない地面）、`Kinematic`（プログラムで動かす）、`Dynamic`（物理で動く） |
| レイヤー | 何と何が衝突するかを決める分類（`ObjectLayer`、`BroadPhaseLayer`） |
| `JobSystem` | 物理の計算を複数のスレッドに分けて動かす仕組み |
| `TempAllocator` | 1 回の `Update` の間だけ使う一時メモリ（[アリーナ](../../stl/memory/pmr.md)） |
| 制約（Constraint） | 物体どうしをつなぐ（ヒンジ、バネ、固定など） |
| `CharacterVirtual` | キャラクターの移動専用の、軽い仕組み（剛体として扱わない） |

<svg class="fig flow" viewBox="0 0 376 280" role="img" aria-label="Jolt の世界の構造"><defs><marker id="fl19562" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Jolt の世界の構造</text><line x1="143.6" y1="125.0" x2="230.4" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl19562)"/><text x="187.0" y="100.0" text-anchor="middle" style="font-size:12px">物体を追加</text><line x1="157.0" y1="148.0" x2="215.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl19562)"/><text x="186.0" y="142.0" text-anchor="middle" style="font-size:12px">物体を追加</text><line x1="143.6" y1="171.0" x2="232.0" y2="209.7" stroke="currentColor" stroke-width="2" marker-end="url(#fl19562)"/><text x="187.8" y="184.3" text-anchor="middle" style="font-size:12px">CharacterVirtual</text><rect x="28.0" y="128.0" width="126" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">PhysicsSystem</text><rect x="229.0" y="44.0" width="108" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="283.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">地面 Static</text><rect x="218.0" y="128.0" width="130" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="283.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ボール Dynamic</text><rect x="235.0" y="212.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="283.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">プレイヤー</text></svg>



## Jolt が得意なこと・不得意なこと

| 得意 | 不得意・注意 |
| --- | --- |
| 大量の剛体（数千〜数万個）を**マルチスレッドで速く**動かす | 2D 専用ではない（2D は Box2D など。Jolt で 2D を表現するなら、Z 軸を固定する） |
| キャラクターの移動（階段、坂、動く床）の専用機能 | 初期設定（レイヤー、初期化）が長い。最初の壁になる |
| 決定的な（再現できる）シミュレーション（リプレイ、ネットワーク同期） | 流体、布などは標準では持たない（ソフトボディは対応） |
| 車両、ラグドール、ソフトボディ | ドキュメントは、英語（公式の Docs と、HelloWorld、Samples が情報源） |
| メモリが少なく、動きが安定している | |


## 物理を使うときの考え方

物理演算で失敗しやすいのは、API の使い方ではなく**設計の考え方**です。特に「物理の世界とゲームの世界を混ぜない」ことと、「固定のステップで進める」ことは、最初に決めておかないと、あとから直すのが大変です。以下に 4 つの基本方針を挙げます。

| 考え方 | 説明 |
| --- | --- |
| 物理の世界とゲームの世界は別のものとして持つ | ゲームのオブジェクト（エンティティ）は、`BodyID` を持つ。毎フレーム、物理の位置をゲームの Transform にコピーする |
| 固定のステップで更新する | 可変の `dt` を渡すと、結果が不安定になる。`dt` は 1/60 などで固定し、足りない時間は複数回 `Update` する（[ゲームループと固定タイムステップ](../../engine/game-loop.md)） |
| キャラクターは剛体にしない | プレイヤーの動きは、`CharacterVirtual`（[キャラクター](character.md)）で、ゲームに合う操作感を作る |
| 衝突の分類を先に決める | 「プレイヤーと弾は衝突する、弾どうしは衝突しない」など、レイヤーの設計を最初にする |

## 関連ページ

- [Jolt Physics（目次）](index.md)
- [世界の初期化と更新](system.md)
- [物体（Body）](bodies.md)

