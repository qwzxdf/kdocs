---
title: デバッグ描画
tags:
  - 外部ライブラリ
  - 物理演算
---

# デバッグ描画

物理の**不具合の原因**（**見えない衝突の形がずれている・質量中心が違う・接触点が変**）は、**数値を見ても分かりにくい**です。**衝突の形・制約・速度を、画面に線で描く**（デバッグ描画）と、**一目で分かります**。Jolt には、<strong>デバッグ描画の仕組み（`DebugRenderer`）</strong>があり、**自分の描画（線の描画）につなぐ**だけで使えます。このページは、**有効にする方法**、**`DebugRendererSimple` の実装**、**物体・制約の描画**、**ImGui との組み合わせ**をまとめます。

!!! tip "ポイント"
    - デバッグ描画は <strong>`JPH_DEBUG_RENDERER` を定義してビルド</strong>したときだけ使える（<strong>ライブラリと自分のプロジェクトで、一致</strong>）。
    - <strong>`DebugRendererSimple`</strong> を継承して、<strong>線を描く関数（`DrawLine`）と、文字を描く関数（`DrawText3D`）</strong>を実装するだけで使える。
    - <strong>`physics_system.DrawBodies(settings, renderer)`</strong> で<strong>物体の形</strong>、<strong>`DrawConstraints(renderer)`</strong> で<strong>制約</strong>を描く。
    - <strong>線を溜めて、まとめて描く</strong>（<strong>1 本ずつ、描画命令を出さない</strong>）。
    - ImGui の<strong>`ImDrawList`</strong>で、<strong>3D の線を、画面上に描く</strong>方法が手軽（<strong>3D → 画面の座標変換が必要</strong>）。
    - <strong>製品版では、無効</strong>（<strong>`JPH_DEBUG_RENDERER` を定義しない</strong>）。

## 何が見えるか

| 描画するもの | 内容 | 使いどころ |
| --- | --- | --- |
| <strong>形（Shape）</strong> | **衝突の形**（ワイヤーフレーム・塗りつぶし） | **見た目と衝突の形が、ずれていないか** |
| <strong>境界ボックス（AABB）</strong> | **ブロードフェーズの、大まかな範囲** | **判定の範囲** |
| <strong>重心（Center of Mass）</strong> | **重心の位置と、軸** | **重心がずれていないか** |
| **速度** | **線速度・角速度の向き** | **動きの確認** |
| **制約** | **ヒンジの軸・接続点・制限の範囲** | **関節の設定の確認** |
| **接触点・法線** | **衝突した位置と向き** | **すり抜け・めり込みの調査** |
| **スリープ状態** | **休止中の物体を、色分け** | **休止が、効いているか** |

## 有効にする

**デバッグ描画は、ビルド時に、`JPH_DEBUG_RENDERER` を定義**したときだけ、使えます。

| 場所 | 設定 |
| --- | --- |
| **Jolt のライブラリ** | **`JPH_DEBUG_RENDERER` を定義して、ビルド**（vcpkg なら `debug-renderer` 機能） |
| **自分のプロジェクト** | **同じく、`JPH_DEBUG_RENDERER` を定義**（**食い違うと、クラッシュ**） |

（詳しくは、[ビルドと設定](build.md)）

## DebugRendererSimple を実装する

**`DebugRendererSimple`**は、<strong>「線と文字だけ、描ければよい」</strong>簡易版です。**これを継承して、自分の描画につなぎます**。

```cpp
#ifdef JPH_DEBUG_RENDERER

class MyDebugRenderer final : public DebugRendererSimple {
 public:
  MyDebugRenderer() { Initialize(); }

  void DrawLine(RVec3Arg from, RVec3Arg to, ColorArg color) override {
    lines_.push_back({ToVector3(from), ToVector3(to), ToColor(color)});
  }

  void DrawText3D(RVec3Arg position, const string_view& text, ColorArg color, float height) override {
    texts_.push_back({ToVector3(position), std::string(text), ToColor(color)});
  }

  void Flush(const Matrix& view, const Matrix& proj, Viewport viewport) {
    ImDrawList* draw = ImGui::GetBackgroundDrawList();
    for (const Line& line : lines_) {
      ImVec2 a;
      ImVec2 b;
      if (WorldToScreen(line.from, view, proj, viewport, a) && WorldToScreen(line.to, view, proj, viewport, b)) {
        draw->AddLine(a, b, line.color);
      }
    }
    lines_.clear();
    texts_.clear();
  }

 private:
  struct Line { Vector3 from; Vector3 to; ImU32 color; };
  struct Text { Vector3 position; std::string text; ImU32 color; };
  std::vector<Line> lines_;
  std::vector<Text> texts_;
};

#endif
```

| 関数 | 意味 |
| --- | --- |
| **`Initialize()`** | **基底クラスの初期化**（コンストラクタで呼ぶ） |
| **`DrawLine(from, to, color)`** | **線を 1 本描く**（**形・制約・軸など、すべての描画が、これに集約される**） |
| **`DrawText3D(position, text, color, height)`** | **3D 空間の位置に、文字**（**質量・名前など**） |

**`DebugRendererSimple` は、三角形や面も、すべて線に変換**します（**ワイヤーフレーム**）。**塗りつぶしの描画**がしたければ、**`DebugRenderer`** を直接継承して、<strong>三角形の描画（`DrawTriangle`・`CreateTriangleBatch`）</strong>を実装します（**手間が増えます**）。

### 描画を呼ぶ

```cpp
#ifdef JPH_DEBUG_RENDERER
void DrawPhysicsDebug(PhysicsSystem& system, MyDebugRenderer& renderer) {
  BodyManager::DrawSettings settings;
  settings.mDrawShape = true;
  settings.mDrawShapeWireframe = true;
  settings.mDrawBoundingBox = false;
  settings.mDrawCenterOfMassTransform = true;
  settings.mDrawVelocity = false;

  system.DrawBodies(settings, &renderer);
  system.DrawConstraints(&renderer);
  system.DrawConstraintLimits(&renderer);
}
#endif
```

| 関数 | 描画するもの |
| --- | --- |
| **`DrawBodies(settings, renderer)`** | **物体**（形・境界ボックス・重心・速度） |
| **`DrawConstraints(renderer)`** | **制約の、接続点・軸** |
| **`DrawConstraintLimits(renderer)`** | **制約の、可動範囲** |
| `DrawConstraintReferenceFrame(renderer)` | **制約の、基準の座標系** |

### DrawSettings の主な項目

| 項目 | 意味 |
| --- | --- |
| **`mDrawShape`** | **形を描く** |
| **`mDrawShapeWireframe`** | **ワイヤーフレーム**で |
| `mDrawShapeColor` | 色の付け方（**物体の種類・休止状態・動き方**で、色分け） |
| **`mDrawBoundingBox`** | **AABB** |
| **`mDrawCenterOfMassTransform`** | **重心の座標軸** |
| **`mDrawVelocity`** | **速度のベクトル** |
| `mDrawMassAndInertia` | **質量と慣性** |
| `mDrawSleepStats` | **スリープまでの時間** |

## 3D の線を、画面に描く

**3D の線を、画面上の線に変換**するには、**ワールド → 画面の座標変換**（MVP とビューポート）が必要です。

```cpp
bool WorldToScreen(const Vector3& world, const Matrix& view, const Matrix& proj,
                   const Viewport& viewport, ImVec2& out) {
  Vector3 screen = viewport.Project(world, proj, view, Matrix::Identity);
  if (screen.z < 0.0f || screen.z > 1.0f) return false;
  out = ImVec2(screen.x, screen.y);
  return true;
}
```

| 点 | 説明 |
| --- | --- |
| **`Viewport::Project`**（SimpleMath） | **ワールド座標 → 画面のピクセル座標**（[SimpleMath](../../3d/simplemath.md)、[変換と MVP](../../3d/transforms-mvp.md)） |
| **`screen.z`** | **0〜1 の範囲外は、カメラの後ろ・遠すぎ**。**描かない** |
| **`ImDrawList::AddLine`** | **画面上に、線を描く**（[デバッグ画面](../imgui/debug-ui.md)） |

**ImGui のバックグラウンド描画リスト**（`GetBackgroundDrawList`）に描けば、**ゲームの画面の上に、線が重なります**。<strong>専用の線描画（頂点バッファ・シェーダー）</strong>を作る方が、**本格的**で、**深度テスト**もできます（**ImGui の線は、深度テストなし**で、**手前の物の裏側も、見える**）。

## 性能

**物体が多いと、線が、数万本**になります。

| 工夫 | 説明 |
| --- | --- |
| **線を、まとめて描く** | **1 本ずつ描画命令を出さず**、**頂点を溜めて、1 回で描く** |
| **範囲を絞る** | **カメラの近くの物体だけ**を描く（`DrawBodies` の、**物体の範囲指定**） |
| **必要なときだけ** | **ボタンで、オン・オフ**（[デバッグ画面](../imgui/debug-ui.md)） |
| **ワイヤーフレームを、簡略に** | **形の分割数を、減らす** |

## 使い方のコツ

| 見たいもの | 設定 |
| --- | --- |
| **衝突の形が、見た目と合っているか** | **`mDrawShapeWireframe = true`** ＋ **見た目のメッシュを、半透明に** |
| **すり抜け・めり込み** | **形と、AABB を描いて**、**位置関係**を見る |
| **重心** | **`mDrawCenterOfMassTransform`** |
| **ヒンジの動き** | **`DrawConstraints` と `DrawConstraintLimits`** |
| **休止している物体** | **色分け**（休止中は暗い色）で、**スリープが効いているか** |
| **キャラクターの形** | **`CharacterVirtual` の形**も、描ける（**`character->GetShape()` を、手動で描画**） |

## 製品版

**デバッグ描画は、製品版では、無効**にします。

```cpp
#ifdef JPH_DEBUG_RENDERER
  DrawPhysicsDebug(system, renderer);
#endif
```

**`JPH_DEBUG_RENDERER` を定義しなければ**、**デバッグ描画のコードは、ライブラリに含まれません**（**サイズと速度の節約**）。**製品用のライブラリ（定義なし）と、開発用のライブラリ（定義あり）を、別に用意**します。

## よくあるミス

??? failure "`JPH_DEBUG_RENDERER` を、ライブラリだけに定義して、クラッシュ"
    **自分のプロジェクトにも、同じ定義**が必要です。

??? failure "`DrawBodies` を呼んでも、何も描かれない"
    **`DrawLine` の実装が、画面に出ていない**（**溜めるだけで、描いていない**）、**`DrawSettings` の `mDrawShape` が `false`**、**カメラの外**、が考えられます。

??? failure "デバッグ描画が、重くて、フレームが落ちる"
    **線を、まとめて描き**、**範囲を絞り**ます。

??? failure "デバッグの線が、手前の壁を透けて見えて、分かりにくい"
    **ImGui の描画は、深度テストなし**です。**専用の線描画で、深度テストを有効**にします。

??? failure "製品版にも、デバッグ描画が残っている"
    **`JPH_DEBUG_RENDERER` を、定義しない**ビルドにします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`JPH_DEBUG_RENDERER` を、ライブラリと自分のプロジェクトで、一致して定義</strong>
    - [x] <strong>`DebugRendererSimple` を継承して `DrawLine` / `DrawText3D` を実装</strong>（<strong>線を溜める</strong>）
    - [x] <strong>`DrawBodies(settings, renderer)`</strong> で物体、<strong>`DrawConstraints`</strong> で制約
    - [x] <strong>3D の線は、`Viewport::Project` で画面に変換</strong>して、<strong>ImGui の `ImDrawList` で描く</strong>
    - [x] <strong>線を、まとめて描く</strong>。<strong>製品版では、無効</strong>

## 関連ページ

- [Jolt Physics](index.md)
- [ビルドと設定](build.md)
- [ImGui でデバッグ画面](../imgui/debug-ui.md)
- [変換と MVP](../../3d/transforms-mvp.md)
- [SimpleMath](../../3d/simplemath.md)
