---
title: 早見表：描画（ImDrawList）
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：描画（ImDrawList）

<strong>ImGui の部品は、最終的に「頂点とインデックスの列（描画リスト）」</strong>に変換されます。この描画リスト（`ImDrawList`）に、自分で線・四角・円・文字を足すことで独自のウィジェット・デバッグ表示・グラフを自由に作れます。座標は「画面の座標」で、`GetCursorScreenPos()` が基準です。

!!! tip "ポイント"
    - <strong>`ImGui::GetWindowDrawList()`</strong>（そのウィンドウの上）・<strong>`GetForegroundDrawList()`</strong>（全ウィンドウの手前）・`GetBackgroundDrawList()`（全ウィンドウの奥）。
    - 座標は画面の左上が原点。ウィンドウ内の位置は `GetCursorScreenPos()` を足す。
    - 色は `ImU32`（`IM_COL32(r, g, b, a)` か `ImGui::GetColorU32(...)`）。
    - 独自の部品を作るときは、`InvisibleButton` で当たり判定を取り、見た目だけを `ImDrawList` で描く。
    - 線の太さ・丸み・分割数は引数の末尾。

## 描画リストの取得

| 関数 | 描画先 |
| --- | --- |
| `ImGui::GetWindowDrawList()` | **現在のウィンドウの内側**（ウィンドウと一緒にクリップ・重なり順） |
| `ImGui::GetForegroundDrawList()` | すべてのウィンドウの手前（オーバーレイ・デバッグ表示） |
| `ImGui::GetBackgroundDrawList()` | すべてのウィンドウの奥（ゲーム画面の上にウィンドウの下） |

## 図形

**`dl` は `ImDrawList*`<strong> とします。</strong>座標は `ImVec2`**。

| 関数 | 描くもの | 主な引数 |
| --- | --- | --- |
| `dl->AddLine(p1, p2, col, thickness)` | 線 | 太さ（既定 1） |
| `dl->AddRect(min, max, col, rounding, flags, thickness)` | 四角の枠 | 角の丸み |
| `dl->AddRectFilled(min, max, col, rounding, flags)` | 塗りつぶした四角 | 角の丸み |
| `dl->AddRectFilledMultiColor(min, max, c_ul, c_ur, c_br, c_bl)` | 四隅の色が違う四角（グラデーション） | 4 色 |
| `dl->AddCircle(center, radius, col, segments, thickness)` | 円の枠 | 分割数（0 で自動） |
| `dl->AddCircleFilled(center, radius, col, segments)` | 塗りつぶした円 | |
| `dl->AddEllipse(center, radius, col, rot, segments, thickness)` | 楕円の枠 | 1.89 以降 |
| `dl->AddTriangle(p1, p2, p3, col, thickness)` | 三角形の枠 | |
| `dl->AddTriangleFilled(p1, p2, p3, col)` | 塗りつぶした三角形 | |
| `dl->AddQuad(p1, p2, p3, p4, col, thickness)` | 四角形（自由な 4 点） | |
| `dl->AddNgon(center, radius, col, num_segments, thickness)` | 正多角形 | 辺の数 |
| `dl->AddPolyline(points, n, col, flags, thickness)` | 折れ線 | `ImDrawFlags_Closed` で閉じる |
| `dl->AddConvexPolyFilled(points, n, col)` | 凸多角形の塗りつぶし | |
| `dl->AddBezierCubic(p1, p2, p3, p4, col, thickness)` | 3 次ベジェ曲線 | ノード エディタの配線 |
| `dl->AddBezierQuadratic(p1, p2, p3, col, thickness)` | 2 次ベジェ曲線 | |
| `dl->AddText(pos, col, text)` | 文字 | |
| `dl->AddText(font, size, pos, col, text)` | フォントと大きさ指定の文字 | |
| `dl->AddImage(tex, min, max, uv0, uv1, col)` | 画像 | |
| `dl->AddImageRounded(tex, min, max, uv0, uv1, col, rounding)` | 角丸の画像 | |

```cpp
ImDrawList* dl = ImGui::GetWindowDrawList();
ImVec2 p = ImGui::GetCursorScreenPos();

dl->AddRectFilled(p, ImVec2(p.x + 100, p.y + 20), IM_COL32(60, 120, 200, 255), 4.0f);
dl->AddLine(p, ImVec2(p.x + 100, p.y + 20), IM_COL32(255, 255, 255, 255), 2.0f);
dl->AddCircleFilled(ImVec2(p.x + 50, p.y + 10), 6.0f, IM_COL32(255, 80, 80, 255));
ImGui::Dummy(ImVec2(100, 20));
```

描いたら、`ImGui::Dummy(size)` などでその領域をカーソルを進めて確保します（進めないと次の部品が描画の上に重なります）。

## 角の丸み（ImDrawFlags）

| フラグ | 丸くする角 |
| --- | --- |
| `ImDrawFlags_RoundCornersAll` | **全部**（`rounding > 0` の既定） |
| `ImDrawFlags_RoundCornersTop` | 上の 2 つ |
| `ImDrawFlags_RoundCornersBottom` | 下の 2 つ |
| `ImDrawFlags_RoundCornersLeft` / `Right` | 左 / 右の 2 つ |
| `ImDrawFlags_RoundCornersTopLeft` ほか | 1 つの角だけ |
| `ImDrawFlags_RoundCornersNone` | 丸めない |
| `ImDrawFlags_Closed` | 折れ線を閉じる |

## 色

| 関数・マクロ | 内容 |
| --- | --- |
| `IM_COL32(r, g, b, a)` | **0〜255 の 4 値から `ImU32`** |
| `IM_COL32_WHITE` / `IM_COL32_BLACK` / `IM_COL32_BLACK_TRANS` | 定数 |
| `ImGui::GetColorU32(ImGuiCol_Text)` | スタイルの色から `ImU32` |
| `ImGui::GetColorU32(ImVec4(r, g, b, a))` | 0〜1 の `ImVec4` から `ImU32` |
| `ImGui::ColorConvertFloat4ToU32(col)` | 同上 |
| `ImGui::ColorConvertRGBtoHSV(...)` / `ColorConvertHSVtoRGB(...)` | RGB ⇄ HSV 変換 |

`ImU32` の並びは、`0xAABBGGRR`（リトル エンディアンで、R が最下位）です。16 進で色を書くときは、R と B が入れ替わるので注意します。

## クリップ

| 関数 | 内容 |
| --- | --- |
| `dl->PushClipRect(min, max, intersect)` | **描画範囲を制限**（それ以外は描かない） |
| `dl->PushClipRectFullScreen()` | クリップを画面全体に |
| `dl->PopClipRect()` | クリップを戻す |
| `ImGui::PushClipRect(min, max, intersect)` / `PopClipRect()` | ImGui 側のクリップ（部品も対象） |

```cpp
dl->PushClipRect(p, ImVec2(p.x + 100, p.y + 20), true);
dl->AddText(p, IM_COL32_WHITE, "Very long text that must not overflow");
dl->PopClipRect();
```

## 独自のウィジェットを作る

**見た目は `ImDrawList`**、当たり判定は `InvisibleButton`、という分担が基本です。

```cpp
bool Knob(const char* label, float* value, float min, float max) {
  ImGui::PushID(label);
  ImVec2 pos = ImGui::GetCursorScreenPos();
  float radius = 20.0f;
  ImGui::InvisibleButton("##knob", ImVec2(radius * 2, radius * 2));
  bool changed = false;
  if (ImGui::IsItemActive()) {
    *value = std::clamp(*value - ImGui::GetIO().MouseDelta.y * (max - min) * 0.01f, min, max);
    changed = true;
  }
  float t = (*value - min) / (max - min);
  float angle = -2.35f + t * 4.7f;
  ImVec2 center(pos.x + radius, pos.y + radius);
  ImDrawList* dl = ImGui::GetWindowDrawList();
  dl->AddCircleFilled(center, radius, ImGui::GetColorU32(ImGuiCol_FrameBg), 32);
  dl->AddLine(center, ImVec2(center.x + std::cos(angle - 1.57f) * radius, center.y + std::sin(angle - 1.57f) * radius),
              ImGui::GetColorU32(ImGuiCol_SliderGrab), 3.0f);
  ImGui::PopID();
  return changed;
}
```

| 要素 | 役割 |
| --- | --- |
| `PushID(label)` | 同じ見た目の部品を複数並べても、ID が衝突しない |
| `InvisibleButton` | 当たり判定・ドラッグ判定・カーソル位置の確保 |
| `IsItemActive()` | ドラッグ中か |
| `GetIO().MouseDelta` | 前フレームからのマウス移動量 |
| `ImDrawList` | 見た目の描画 |

## 描画リストの内部

**描画リストは頂点・インデックス・描画コマンド**からできています。

| メンバー | 内容 |
| --- | --- |
| `VtxBuffer` | 頂点（`ImDrawVert`：位置・UV・色） |
| `IdxBuffer` | インデックス（三角形） |
| `CmdBuffer` | 描画コマンド（クリップ矩形・テクスチャ・インデックスの範囲） |

バックエンド（`ImGui_ImplDX11_RenderDrawData` など）が、これらを GPU に送り、コマンドごとに `DrawIndexed` します。1 フレームの描画が重いときは、`ImGui::ShowMetricsWindow` で、頂点数・コマンド数を確認します。

## 関連ページ

- [関数早見表](index.md)
- [状態と入力](state-io.md)
- [フラグ](flags.md)
- [imgui-node-editor（ベジェ配線）](../node-editor.md)
