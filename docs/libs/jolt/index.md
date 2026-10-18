---
title: Jolt Physics
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt Physics

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17〜</span>
`#include <Jolt/Jolt.h>`
</div>

**Jolt Physics**（ジョルト・フィジクス）は、**3D の物理演算（剛体、衝突判定、キャラクターの移動など）を行う C++ ライブラリ**です。オランダのゲーム会社 Guerrilla Games の開発者 Jorrit Rouwé が、**PlayStation 5 の「Horizon Forbidden West」のために作った**エンジンを、オープンソース（MIT ライセンス）として公開したものです。**マルチスレッドで速く**、<strong>同じ入力から同じ結果が出る（決定的）</strong>ことを重視していて、Godot（4.4 以降の選択肢）や Unity 以外の多くの新しいゲームでも採用されています。Bullet や PhysX と同じ種類のライブラリですが、<strong>新しくてモダンな C++</strong>で書かれていて、導入しやすいのが特徴です。

## ページ一覧

**読む順番**：導入 → 全体像 → 最小の流れ → 各機能。

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | ソースからのビルド・CMake・vcpkg での入れ方 |
| [物理演算の全体像](overview.md) | 世界・物体・形・レイヤー・制約の関係 |
| [最小の流れ](quickstart.md) | 初期化から、球が落ちるまでの骨組み |
| [ビルドと設定](build.md) | プリプロセッサの定義、Debug / Release、倍精度、決定性、vcpkg と CMake の違い |
| [世界の初期化と更新](system.md) | `PhysicsSystem::Init` の引数、`Update`、固定ステップ、サブステップ |
| [レイヤー](layers.md) | `ObjectLayer`、`BroadPhaseLayer`、衝突フィルターの書き方 |
| [物体（Body）](bodies.md) | 作成・追加・削除、力・速度、摩擦と反発、スリープ、センサー |
| [形（Shape）](shapes.md) | 箱・球・カプセル・凸包・メッシュ・複合形状、スケール、重心 |
| [クエリ（レイキャストなど）](queries.md) | レイキャスト、形状キャスト、重なり判定、衝突フィルター |
| [制約（Constraint）](constraints.md) | ヒンジ、バネ、固定、距離、モーター、ラグドール |
| [キャラクター](character.md) | `CharacterVirtual`、階段・坂・動く床、`Character`（剛体版） |
| [デバッグ描画](debug-renderer.md) | `DebugRenderer` を実装して、衝突の形を画面に出す |
| [ECS・ゲームとの連携](integration.md) | `BodyID` とエンティティ、位置の同期、イベント（接触リスナー） |
| [車両・ソフトボディ](vehicles.md) | 車両の物理、ソフトボディ |

## 関連ページ

- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [Visual Studio：CMake で使う](../../vs/cmake.md)
- [ゲームループと固定タイムステップ](../../engine/game-loop.md)
- [ハンドルと世代 ID](../../engine/handle.md)
- [ECS](../../design/patterns/ecs.md)
- [Dear ImGui（デバッグ画面）](../imgui/index.md)
- [JoltPhysics（GitHub）](https://github.com/jrouwe/JoltPhysics)
- [Jolt のドキュメント](https://jrouwe.github.io/JoltPhysics/)
