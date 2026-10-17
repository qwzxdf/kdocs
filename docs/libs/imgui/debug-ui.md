---
title: ゲームでのデバッグ画面
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui でデバッグ画面を作る

ImGui の**一番の使いどころ**は、**ゲームの中の、デバッグ画面**です。**数値を、その場で変えて試す**、**フレーム時間をグラフで見る**、**ログを画面に出す**、**オブジェクトの中身を覗く**、**コマンドを打つ**——これらを、**数行のコード**で作れます。**再ビルドせずに調整できる**ので、**開発の速さが、大きく上がります**。このページは、**よく使うデバッグ画面の作り方**と、**製品版から外す方法**をまとめます。

!!! tip "ポイント"
    - デバッグ画面は<strong>「ゲームのデータへのポインタ」を、ImGui の部品に渡す</strong>だけで作れる（<strong>値を、その場で書き換えられる</strong>）。
    - <strong>フレーム時間</strong>は <strong>`PlotLines` ＋ リングバッファ</strong>。<strong>FPS だけでなく、ミリ秒</strong>で見る。
    - <strong>ログ ウィンドウ</strong>は、<strong>`BeginChild` ＋ 色分け ＋ `ImGuiTextFilter` ＋ 自動スクロール</strong>。
    - <strong>インスペクター</strong>（オブジェクトの中身の編集）は、<strong>コンポーネントごとに、編集用の関数</strong>を用意する。
    - <strong>調整した値は、ファイルに保存</strong>して、<strong>次回起動時に、読み込む</strong>。
    - <strong>製品版からは、`#ifdef` で、まるごと除外</strong>する。<strong>チート用の機能を、残さない</strong>。

## 基本：データにポインタを渡す

```cpp
void DrawDebugUi(Game& game) {
  if (ImGui::Begin("デバッグ")) {
    ImGui::SliderFloat("プレイヤーの速さ", &game.player.speed, 0.0f, 20.0f);
    ImGui::DragFloat("重力", &game.physics.gravity, 0.1f);
    ImGui::Checkbox("無敵", &game.player.godmode);
    if (ImGui::Button("敵を出す")) game.SpawnEnemy();
  }
  ImGui::End();
}
```

**`&game.player.speed`** を渡すだけで、**ゲームの値が、その場で変わります**。**ゲームの中で、遊びながら調整**できます。

## フレーム時間・FPS の表示

```cpp
class FrameStats {
 public:
  void Update(float dt) {
    times_[offset_] = dt * 1000.0f;
    offset_ = (offset_ + 1) % kCount;

    float sum = 0.0f;
    max_ = 0.0f;
    for (float t : times_) {
      sum += t;
      max_ = std::max(max_, t);
    }
    average_ = sum / kCount;
  }

  void Draw() {
    ImGui::Text("平均 %.2f ms（%.0f FPS）  最大 %.2f ms", average_, 1000.0f / average_, max_);
    ImGui::PlotLines("##frame", times_, kCount, offset_, nullptr, 0.0f, 33.0f, ImVec2(0, 60));
  }

 private:
  static constexpr int kCount = 120;
  float times_[kCount] = {};
  int offset_ = 0;
  float average_ = 0.0f;
  float max_ = 0.0f;
};
```

| 表示するもの | 理由 |
| --- | --- |
| <strong>平均のフレーム時間（ms）</strong> | **FPS より、足し算できる**（[フレーム時間の設計](../../optimize/frame-budget.md)） |
| **最大のフレーム時間** | **スパイク**（カクつき）の検出 |
| **折れ線グラフ**（**直近 120 フレーム**） | **スパイクが、見える** |

### システムごとの時間

**更新・物理・描画ごとの時間**を測って、**棒グラフや、表**で出すと、**どこが重いか**が、すぐ分かります。

```cpp
struct ScopedTimer {
  ScopedTimer(const char* name, TimeTable& table) : name_(name), table_(table), start_(Clock::now()) {}
  ~ScopedTimer() { table_[name_] = std::chrono::duration<float, std::milli>(Clock::now() - start_).count(); }
  ...
};

{ ScopedTimer t("物理", times); UpdatePhysics(dt); }
{ ScopedTimer t("AI", times); UpdateAi(dt); }

for (auto& [name, ms] : times) {
  ImGui::ProgressBar(ms / 16.6f, ImVec2(200, 0), "");
  ImGui::SameLine();
  ImGui::Text("%s: %.2f ms", name.c_str(), ms);
}
```

（本格的には、[プロファイラー](../../vs/profiler.md)や Tracy を使います）

## ログ ウィンドウ

```cpp
class LogWindow {
 public:
  void Add(Level level, std::string text) {
    lines_.push_back({level, std::move(text)});
    if (lines_.size() > 2000) lines_.erase(lines_.begin(), lines_.begin() + 500);
    scroll_to_bottom_ = auto_scroll_;
  }

  void Draw() {
    if (!ImGui::Begin("ログ")) { ImGui::End(); return; }

    if (ImGui::Button("クリア")) lines_.clear();
    ImGui::SameLine();
    ImGui::Checkbox("自動スクロール", &auto_scroll_);
    ImGui::SameLine();
    filter_.Draw("フィルター");
    ImGui::Separator();

    ImGui::BeginChild("lines", ImVec2(0, 0), ImGuiChildFlags_None, ImGuiWindowFlags_HorizontalScrollbar);
    for (const Line& line : lines_) {
      if (!filter_.PassFilter(line.text.c_str())) continue;
      ImVec4 color = line.level == Level::kError ? ImVec4(1, 0.4f, 0.4f, 1)
                   : line.level == Level::kWarning ? ImVec4(1, 0.8f, 0.3f, 1)
                   : ImVec4(0.9f, 0.9f, 0.9f, 1);
      ImGui::PushStyleColor(ImGuiCol_Text, color);
      ImGui::TextUnformatted(line.text.c_str());
      ImGui::PopStyleColor();
    }
    if (scroll_to_bottom_) ImGui::SetScrollHereY(1.0f);
    scroll_to_bottom_ = false;
    ImGui::EndChild();
    ImGui::End();
  }

 private:
  struct Line { Level level; std::string text; };
  std::vector<Line> lines_;
  ImGuiTextFilter filter_;
  bool auto_scroll_ = true;
  bool scroll_to_bottom_ = false;
};
```

| 部分 | 説明 |
| --- | --- |
| **色分け** | **エラーは赤、警告は黄色**（`PushStyleColor(ImGuiCol_Text, ...)`） |
| **`ImGuiTextFilter`** | **文字列でフィルター**（`"敵,-弾"` のように、**含む・除く**の指定もできる） |
| **自動スクロール** | **新しい行が来たら、最下部**へ（`SetScrollHereY(1.0f)`） |
| **行数の上限** | **古い行を、捨てる**（メモリと描画の、肥大を防ぐ） |
| **大量のログ** | **`ImGuiListClipper`** で、**見える行だけ**を描く |

**ゲームのログ機能**（[ログとデバッグ支援](../../design/practice/logging-debug.md)）に、**このウィンドウを、出力先として登録**します。

## インスペクター（オブジェクトの中身を編集）

**選んだオブジェクトの、各コンポーネントの値を、画面で見て、直接書き換えます**。

```cpp
void InspectEntity(Entity& e) {
  ImGui::Text("ID: %u", e.id);
  ImGui::InputText("名前", &e.name);

  if (ImGui::CollapsingHeader("Transform", ImGuiTreeNodeFlags_DefaultOpen)) {
    ImGui::DragFloat3("位置", &e.transform.position.x, 0.1f);
    ImGui::DragFloat3("回転", &e.euler.x, 1.0f);
    ImGui::DragFloat3("拡大", &e.transform.scale.x, 0.01f);
  }

  if (e.health && ImGui::CollapsingHeader("Health")) {
    ImGui::DragInt("HP", &e.health->hp, 1, 0, e.health->max_hp);
    ImGui::DragInt("最大 HP", &e.health->max_hp);
  }
}
```

| 工夫 | 説明 |
| --- | --- |
| **コンポーネントごとに、編集関数** | **`InspectTransform`・`InspectHealth`** のように、**種類ごと**に分ける |
| **選択の管理** | **シーンのツリー**（`TreeNodeEx`）で選び、**`selected_entity`** を覚える |
| **削除・追加のボタン** | **コンポーネントの追加・削除**もできると、便利 |
| **ハンドルを使う** | **選んだオブジェクトが、消えたとき**に、**クラッシュしない**（[ハンドル](../../engine/handle.md)） |

### ECS・リフレクションとの連携

**コンポーネントの型が、たくさんある**と、**編集関数を、全部手で書く**のは大変です。**リフレクション**（**メンバの名前・型・オフセットの一覧**）があれば、**自動で、ImGui の部品を作れます**。

```cpp
for (const Field& f : Reflect<Health>::fields) {
  switch (f.type) {
    case FieldType::kInt: ImGui::DragInt(f.name, f.GetPtr<int>(&health)); break;
    case FieldType::kFloat: ImGui::DragFloat(f.name, f.GetPtr<float>(&health)); break;
    case FieldType::kBool: ImGui::Checkbox(f.name, f.GetPtr<bool>(&health)); break;
  }
}
```

**C++ には、標準のリフレクションがない**ので、**マクロや、コード生成、`nlohmann/json` 風のメンバ登録**で、**自前で作る**のが一般的です（[ECS](../../design/patterns/ecs.md)、[シリアライズ](../../engine/serialization/index.md)）。

## パラメータ調整と保存

**ImGui で、調整した値は、終了すると、消えます**。**ファイルに保存**して、**次回起動時に、読み込みます**。

```cpp
struct TuningParams {
  float player_speed = 5.0f;
  float gravity = -9.8f;
  float enemy_spawn_rate = 1.0f;
};

void DrawTuning(TuningParams& p) {
  ImGui::SliderFloat("プレイヤー速度", &p.player_speed, 0.0f, 20.0f);
  ImGui::SliderFloat("重力", &p.gravity, -30.0f, 0.0f);
  ImGui::SliderFloat("敵の出現率", &p.enemy_spawn_rate, 0.0f, 5.0f);

  if (ImGui::Button("保存")) SaveTuning("tuning.json", p);
  ImGui::SameLine();
  if (ImGui::Button("読み込み")) LoadTuning("tuning.json", p);
}
```

| 方法 | 説明 |
| --- | --- |
| **JSON で保存** | **人が読める**。**ゲームの設定ファイルとしても使える**（[nlohmann/json](../serialization/nlohmann-json.md)） |
| **ホットリロード** | **ファイルを、監視**して、**変更されたら、再読み込み**（エディタで編集 → ゲームが追従） |
| **調整値を、ゲームのデータに反映** | **気に入った値を、データファイルへ**（[ファクトリとデータ駆動](../../design/patterns/factory.md)） |

## デバッグ メニューと、機能の切り替え

**メインメニューバー**に、**デバッグ機能の、オン・オフ**を並べます。

```cpp
struct DebugFlags {
  bool show_stats = true;
  bool show_log = false;
  bool show_inspector = false;
  bool draw_colliders = false;
  bool draw_navmesh = false;
};

void DrawDebugMenu(DebugFlags& f) {
  if (ImGui::BeginMainMenuBar()) {
    if (ImGui::BeginMenu("デバッグ")) {
      ImGui::MenuItem("統計", nullptr, &f.show_stats);
      ImGui::MenuItem("ログ", nullptr, &f.show_log);
      ImGui::MenuItem("インスペクター", nullptr, &f.show_inspector);
      ImGui::Separator();
      ImGui::MenuItem("当たり判定を描く", nullptr, &f.draw_colliders);
      ImGui::MenuItem("ナビメッシュを描く", nullptr, &f.draw_navmesh);
      ImGui::EndMenu();
    }
    ImGui::EndMainMenuBar();
  }
}
```

**`MenuItem` の `bool*`<strong>で、</strong>チェック付きの項目<strong>になります（[ウィジェット一覧](widgets.md#menu)）。</strong>デバッグ描画**（当たり判定・経路）の切り替えに、便利です。

## コンソール（コマンドの入力）

**ゲームの中で、コマンドを打つ**（`spawn enemy`、`god on`、`teleport 10 0 5`）コンソールです。

```cpp
class Console {
 public:
  void Draw() {
    if (!ImGui::Begin("コンソール")) { ImGui::End(); return; }

    ImGui::BeginChild("output", ImVec2(0, -ImGui::GetFrameHeightWithSpacing()));
    for (const std::string& line : output_) ImGui::TextUnformatted(line.c_str());
    if (scroll_) ImGui::SetScrollHereY(1.0f);
    scroll_ = false;
    ImGui::EndChild();

    ImGui::SetNextItemWidth(-FLT_MIN);
    if (ImGui::InputText("##input", &input_, ImGuiInputTextFlags_EnterReturnsTrue)) {
      Execute(input_);
      input_.clear();
      ImGui::SetKeyboardFocusHere(-1);
    }
    ImGui::End();
  }

  void Register(std::string name, std::function<void(std::span<std::string>)> fn) {
    commands_[name] = std::move(fn);
  }

 private:
  void Execute(const std::string& line);
  std::unordered_map<std::string, std::function<void(std::span<std::string>)>> commands_;
  std::vector<std::string> output_;
  std::string input_;
  bool scroll_ = false;
};
```

| 部分 | 説明 |
| --- | --- |
| **コマンドの登録** | **名前 → 関数**の表（`std::unordered_map`） |
| **Enter で実行** | **`EnterReturnsTrue`**。実行後に、**入力欄へ、フォーカスを戻す**（`SetKeyboardFocusHere(-1)`） |
| **履歴・補完** | **上キーで履歴**、**Tab で補完**も、実装できる |
| **ImGui の例** | **`imgui_demo.cpp` の `ExampleAppConsole`** が、**履歴・補完付きの実装例** |

## 3D のデバッグ描画

**ImGui のウィンドウ以外に**、**3D の画面に、線・箱・球を描く**（**デバッグ描画**）ことも、よくやります。

| 方法 | 説明 |
| --- | --- |
| **自作のデバッグ描画**（線の描画） | **3D の頂点を、画面座標に変換**し、**`ImGui::GetBackgroundDrawList()->AddLine(...)`** で描く（**ImGui の描画リストを、借りる**） |
| **`ImDrawList`** | **線・円・矩形・テキスト**を、**画面に直接描く**（ゲームの画面の上に重ねる） |

```cpp
ImDrawList* draw = ImGui::GetBackgroundDrawList();
ImVec2 p = WorldToScreen(enemy.position);
draw->AddCircle(p, 20.0f, IM_COL32(255, 80, 80, 255));
draw->AddText(ImVec2(p.x + 22, p.y - 8), IM_COL32_WHITE, enemy.name.c_str());
```

**敵の頭の上に、名前や HP を出す**といった、**画面上のラベル**に便利です（`WorldToScreen` は、[MVP](../../3d/transforms-mvp.md)の逆）。**物理の形の描画**は、[Jolt のデバッグ描画](../jolt/debug-renderer.md)にあります。

## 製品版から、外す

**デバッグ画面は、製品版に残さない**のが原則です（**チート・パフォーマンス・情報漏えい**）。

```cpp
#ifdef ENABLE_DEBUG_UI
  DrawDebugMenu(debug_flags);
  DrawStats();
  DrawInspector();
#endif
```

| 方法 | 説明 |
| --- | --- |
| **`#ifdef ENABLE_DEBUG_UI`** | **Debug・Profile 構成だけ**で、**定義する**（[プリプロセッサマクロ](../../vs/preprocessor.md)） |
| **ImGui 自体を、リンクしない** | **製品版は、ImGui のコードごと**、**ビルドから外す**（CMake の条件、プロジェクトの構成） |
| **隠しコマンドを、残さない** | **コンソール・チートコマンド**も、**製品版では、無効** |
| **`IMGUI_DISABLE_DEMO_WINDOWS`** | **デモの、ビルド除外**（サイズ削減） |

**ゲームのコードの中に、ImGui の呼び出しが、散らばる**と、**`#ifdef` だらけ**になります。**デバッグ UI を、1 か所**（`DebugUi` クラス）に、**まとめて**、**そこだけ**を、**構成で出し入れ**するのが、きれいです（[依存性の注入](../../design/patterns/dependency-injection.md)）。

## よくあるミス

??? failure "ローカル変数を、スライダーに渡して、値が戻る"
    **ゲーム側のデータへのポインタ**（`&game.player.speed`）を、渡します。

??? failure "デバッグ UI の変更が、ゲームに反映されない"
    **コピー**を渡している可能性があります。**元のデータへのポインタ**にします。

??? failure "選んだオブジェクトが消えて、インスペクターがクラッシュする"
    **ポインタでなく、ハンドル**で持ち、**毎フレーム、有効か確認**します。

??? failure "ログが、無限に溜まって、重くなる"
    **行数の上限**を設け、**`ListClipper`** で描きます。

??? failure "製品版に、デバッグ UI が残っている"
    **`#ifdef` で除外**し、**製品構成で、ImGui をリンクしない**ようにします。

??? failure "デバッグ UI の操作が、ゲームの入力と、取り合いになる"
    **`io.WantCaptureMouse` / `WantCaptureKeyboard`** が `true` のときは、**ゲームに渡さない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ゲームのデータへのポインタを、ImGui の部品に渡す</strong>だけで、<strong>その場で調整できる</strong>
    - [x] <strong>フレーム時間は `PlotLines` ＋ リングバッファ</strong>（<strong>ミリ秒・最大値</strong>も）
    - [x] <strong>ログは、色分け・フィルター・自動スクロール・行数上限</strong>
    - [x] <strong>インスペクターは、コンポーネントごとの編集関数</strong>（<strong>リフレクションで自動化</strong>も）。<strong>ハンドルで持つ</strong>
    - [x] <strong>調整値は、ファイルに保存</strong>。<strong>デバッグ描画は、`ImDrawList`</strong>
    - [x] <strong>製品版からは、`#ifdef` ＋ リンクしない</strong>。<strong>入力は `WantCapture...` で調停</strong>

## 関連ページ

- [Dear ImGui](index.md)
- [ウィジェット一覧](widgets.md)
- [レイアウトとウィンドウ](layout.md)
- [ログとデバッグ支援の設計](../../design/practice/logging-debug.md)
- [フレーム時間の設計](../../optimize/frame-budget.md)
- [Jolt のデバッグ描画](../jolt/debug-renderer.md)
- [ECS](../../design/patterns/ecs.md)
