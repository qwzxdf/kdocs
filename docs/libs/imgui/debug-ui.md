---
title: ゲームでのデバッグ画面
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui でデバッグ画面を作る

ImGui の**一番の使いどころ**は、ゲームの中のデバッグ画面です。数値をその場で変えて試す、フレーム時間をグラフで見る、ログを画面に出す、オブジェクトの中身を覗く、コマンドを打つ——これらを、数行のコードで作れます。再ビルドせずに調整できるので、開発の速さが大きく上がります。このページはよく使うデバッグ画面の作り方と、製品版から外す方法をまとめます。

!!! tip "ポイント"
    - デバッグ画面は<strong>「ゲームのデータへのポインタ」を、ImGui の部品に渡す</strong>だけで作れる（<strong>値をその場で書き換えられる</strong>）。
    - フレーム時間は `PlotLines` ＋ リングバッファ。FPS だけでなく、ミリ秒で見る。
    - ログ ウィンドウは、`BeginChild` ＋ 色分け ＋ `ImGuiTextFilter` ＋ 自動スクロール。
    - インスペクター（オブジェクトの中身の編集）は、コンポーネントごとに編集用の関数を用意する。
    - 調整した値は、ファイルに保存して、次回起動時に読み込む。
    - 製品版からは、`#ifdef` でまるごと除外する。チート用の機能を残さない。

!!! info "このページを読む前に"
    - [Dear ImGui](index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](install.md)（ImGui の入れ方）

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

**`&game.player.speed`** を渡すだけで、ゲームの値がその場で変わります。ゲームの中で遊びながら調整できます。

<svg class="fig imgui" data-fig="imgui-debug-windows" viewBox="0 0 780 360" role="img" aria-label="デバッグ画面の例"><rect x="0" y="0" width="780" height="360" fill="#1b1b1f" rx="6"/><rect x="20.0" y="20.0" width="240.0" height="320.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="20.0" y="20.0" width="240.0" height="19.0" rx="0" fill="#294a7a" /><path d="M27,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="40.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Stats</text><text x="28.0" y="61.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >FPS: 60.1  (16.6 ms)</text><rect x="28.0" y="70.0" width="224.0" height="60.0" rx="3" fill="#1d2f49" /><polyline points="30.0,126.0 46.9,117.3 63.8,126.0 80.8,108.7 97.7,126.0 114.6,74.0 131.5,126.0 148.5,117.3 165.4,126.0 182.3,126.0 199.2,100.0 216.2,126.0 233.1,117.3 250.0,126.0" fill="none" stroke="#e0a030" stroke-width="1.5"/><text x="32.0" y="83.0" style="fill:#808080;font-family:Consolas,'Courier New',monospace;font-size:13px;" >frame ms</text><rect x="28.0" y="134.0" width="200.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="28.0" y="134.0" width="80.0" height="19.0" rx="3" fill="#3d85e0" /><text x="102.8" y="148.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >GPU 40%</text><rect x="28.0" y="157.0" width="200.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="28.0" y="157.0" width="140.0" height="19.0" rx="3" fill="#3d85e0" /><text x="102.8" y="171.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >CPU 70%</text><rect x="21.0" y="182.0" width="238.0" height="1.0" rx="0" fill="#5c5c6e" /><rect x="28.0" y="188.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><path d="M32,197 l4,4 l7,-8" fill="none" stroke="#4296fa" stroke-width="2.2"/><text x="49.0" y="202.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >VSync</text><rect x="28.0" y="211.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><text x="49.0" y="225.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Wireframe</text><rect x="28.0" y="234.0" width="138.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="68.4" y="236.0" width="10.0" height="15.0" rx="2" fill="#3d85e0" /><text x="81.0" y="248.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >1.00</text><text x="174.0" y="248.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Scale</text><rect x="280.0" y="20.0" width="240.0" height="320.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="280.0" y="20.0" width="240.0" height="19.0" rx="0" fill="#0a0a0a" /><path d="M287,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="300.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Log</text><text x="288.0" y="61.0" style="fill:#9fe0a0;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[12:00:01] Init OK</text><text x="288.0" y="84.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[12:00:02] Load level1</text><text x="288.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[12:00:05] Spawn enemy x3</text><text x="288.0" y="130.0" style="fill:#e8c060;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[12:00:07] HP low!</text><text x="288.0" y="153.0" style="fill:#f07070;font-family:Consolas,'Courier New',monospace;font-size:13px;" >[12:00:09] Save failed</text><rect x="540.0" y="20.0" width="220.0" height="320.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="540.0" y="20.0" width="220.0" height="19.0" rx="0" fill="#0a0a0a" /><path d="M547,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="560.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Inspector</text><text x="548.0" y="61.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Entity #42</text><rect x="548.0" y="70.0" width="126.0" height="19.0" rx="3" fill="#1d2f49" /><text x="552.0" y="84.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Goblin</text><text x="682.0" y="84.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >name</text><rect x="548.0" y="93.0" width="126.0" height="19.0" rx="3" fill="#1d2f49" /><text x="603.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >30</text><text x="682.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >hp</text><rect x="548.0" y="116.0" width="126.0" height="19.0" rx="3" fill="#1d2f49" /><text x="595.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >4.20</text><text x="682.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >pos x</text><rect x="548.0" y="139.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><path d="M552,148 l4,4 l7,-8" fill="none" stroke="#4296fa" stroke-width="2.2"/><text x="569.0" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >visible</text><rect x="548.0" y="162.0" width="126.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="655.0" y="162.0" width="19.0" height="19.0" rx="3" fill="#23456d" /><path d="M660,169 l4.5,6 l4.5,-6 z" fill="#ffffff"/><text x="552.0" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Patrol</text><text x="682.0" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ai</text><rect x="548.0" y="185.0" width="19.0" height="19.0" rx="3" fill="#4296fa" stroke="#4b4b57"/><rect x="571.0" y="185.0" width="103.0" height="19.0" rx="3" fill="#1d2f49" /><text x="575.0" y="199.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >0.26 0.59 0.98</text><text x="682.0" y="199.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >tint</text></svg>

統計（FPS・グラフ）・ログ・インスペクターの、典型的なデバッグ画面です。

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
| <strong>平均のフレーム時間（ms）</strong> | FPS より、足し算できる（[フレーム時間の設計](../../optimize/frame-budget.md)） |
| 最大のフレーム時間 | スパイク（カクつき）の検出 |
| 折れ線グラフ（直近 120 フレーム） | スパイクが見える |

### システムごとの時間

更新・物理・描画ごとの時間を測って、棒グラフや表で出すとどこが重いかがすぐ分かります。

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
| **色分け** | エラーは赤、警告は黄色（`PushStyleColor(ImGuiCol_Text, ...)`） |
| `ImGuiTextFilter` | 文字列でフィルター（`"敵,-弾"` のように、含む・除くの指定もできる） |
| 自動スクロール | 新しい行が来たら、最下部へ（`SetScrollHereY(1.0f)`） |
| 行数の上限 | 古い行を捨てる（メモリと描画の肥大を防ぐ） |
| 大量のログ | `ImGuiListClipper` で、見える行だけを描く |

ゲームのログ機能（[ログとデバッグ支援](../../design/practice/logging-debug.md)）に、このウィンドウを出力先として登録します。

## インスペクター（オブジェクトの中身を編集）

**選んだオブジェクトの各コンポーネントの値を、画面で見て、直接書き換えます**。

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
| コンポーネントごとに編集関数 | `InspectTransform`・`InspectHealth` のように、種類ごとに分ける |
| 選択の管理 | シーンのツリー（`TreeNodeEx`）で選び、`selected_entity` を覚える |
| 削除・追加のボタン | コンポーネントの追加・削除もできると便利 |
| ハンドルを使う | 選んだオブジェクトが消えたときにクラッシュしない（[ハンドル](../../engine/handle.md)） |

### ECS・リフレクションとの連携

コンポーネントの型がたくさんあると編集関数を全部手で書くのは大変です。リフレクション（メンバの名前・型・オフセットの一覧）があれば、自動で、ImGui の部品を作れます。

```cpp
for (const Field& f : Reflect<Health>::fields) {
  switch (f.type) {
    case FieldType::kInt: ImGui::DragInt(f.name, f.GetPtr<int>(&health)); break;
    case FieldType::kFloat: ImGui::DragFloat(f.name, f.GetPtr<float>(&health)); break;
    case FieldType::kBool: ImGui::Checkbox(f.name, f.GetPtr<bool>(&health)); break;
  }
}
```

C++ には標準のリフレクションがないので、マクロやコード生成、`nlohmann/json` 風のメンバ登録で、自前で作るのが一般的です（[ECS](../../design/patterns/ecs.md)、[シリアライズ](../../engine/serialization/index.md)）。

## パラメータ調整と保存

**ImGui で調整した値は終了すると消えます**。ファイルに保存して、次回起動時に読み込みます。

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
| JSON で保存 | 人が読める。ゲームの設定ファイルとしても使える（[nlohmann/json](../serialization/nlohmann-json.md)） |
| ホットリロード | ファイルを監視して、変更されたら、再読み込み（エディタで編集 → ゲームが追従） |
| 調整値をゲームのデータに反映 | 気に入った値をデータファイルへ（[ファクトリとデータ駆動](../../design/patterns/factory.md)） |

## デバッグ メニューと、機能の切り替え

**メインメニューバー**にデバッグ機能のオン・オフを並べます。

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

**`MenuItem` の `bool*`で、チェック付きの項目になります（[ウィジェット一覧](widgets.md#menu)）。デバッグ描画**（当たり判定・経路）の切り替えに便利です。

## コンソール（コマンドの入力）

**ゲームの中でコマンドを打つ**（`spawn enemy`、`god on`、`teleport 10 0 5`）コンソールです。

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
| コマンドの登録 | 名前 → 関数の表（`std::unordered_map`） |
| Enter で実行 | `EnterReturnsTrue`。実行後に入力欄へフォーカスを戻す（`SetKeyboardFocusHere(-1)`） |
| 履歴・補完 | 上キーで履歴、Tab で補完も実装できる |
| ImGui の例 | `imgui_demo.cpp` の `ExampleAppConsole` が、履歴・補完付きの実装例 |

## 3D のデバッグ描画

**ImGui のウィンドウ以外に**、3D の画面に線・箱・球を描く（デバッグ描画）こともよくやります。

| 方法 | 説明 |
| --- | --- |
| 自作のデバッグ描画（線の描画） | 3D の頂点を画面座標に変換し、`ImGui::GetBackgroundDrawList()->AddLine(...)` で描く（ImGui の描画リストを、借りる） |
| `ImDrawList` | 線・円・矩形・テキストを画面に直接描く（ゲームの画面の上に重ねる） |

```cpp
ImDrawList* draw = ImGui::GetBackgroundDrawList();
ImVec2 p = WorldToScreen(enemy.position);
draw->AddCircle(p, 20.0f, IM_COL32(255, 80, 80, 255));
draw->AddText(ImVec2(p.x + 22, p.y - 8), IM_COL32_WHITE, enemy.name.c_str());
```

敵の頭の上に名前や HP を出すといった、画面上のラベルに便利です（`WorldToScreen` は、[MVP](../../3d/transforms-mvp.md)の逆）。物理の形の描画は、[Jolt のデバッグ描画](../jolt/debug-renderer.md)にあります。

## 製品版から、外す

**デバッグ画面は、製品版に残さない**のが原則です（チート・パフォーマンス・情報漏えい）。

```cpp
#ifdef ENABLE_DEBUG_UI
  DrawDebugMenu(debug_flags);
  DrawStats();
  DrawInspector();
#endif
```

| 方法 | 説明 |
| --- | --- |
| `#ifdef ENABLE_DEBUG_UI` | Debug・Profile 構成だけで、定義する（[プリプロセッサマクロ](../../vs/preprocessor.md)） |
| ImGui 自体をリンクしない | 製品版は、ImGui のコードごと、ビルドから外す（CMake の条件、プロジェクトの構成） |
| 隠しコマンドを残さない | コンソール・チートコマンドも製品版では無効 |
| `IMGUI_DISABLE_DEMO_WINDOWS` | デモのビルド除外（サイズ削減） |

ゲームのコードの中に、ImGui の呼び出しが、散らばると`#ifdef` だらけになります。デバッグ UI を、1 か所（`DebugUi` クラス）に、まとめて、そこだけを構成で出し入れするのが、きれいです（[依存性の注入](../../design/patterns/dependency-injection.md)）。

## よくあるミス

??? failure "ローカル変数を、スライダーに渡して、値が戻る"
    ゲーム側のデータへのポインタ（`&game.player.speed`）を、渡します。

??? failure "デバッグ UI の変更が、ゲームに反映されない"
    コピーを渡している可能性があります。元のデータへのポインタにします。

??? failure "選んだオブジェクトが消えて、インスペクターがクラッシュする"
    ポインタでなく、ハンドルで持ち、毎フレーム、有効か確認します。

??? failure "ログが、無限に溜まって、重くなる"
    行数の上限を設け、`ListClipper` で描きます。

??? failure "製品版に、デバッグ UI が残っている"
    `#ifdef` で除外し、製品構成で、ImGui をリンクしないようにします。

??? failure "デバッグ UI の操作が、ゲームの入力と取り合いになる"
    `io.WantCaptureMouse` / `WantCaptureKeyboard` が `true` のときは、ゲームに渡さない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ゲームのデータへのポインタを、ImGui の部品に渡すだけで、その場で調整できる
    - [x] フレーム時間は `PlotLines` ＋ リングバッファ（ミリ秒・最大値も）
    - [x] ログは、色分け・フィルター・自動スクロール・行数上限
    - [x] インスペクターは、コンポーネントごとの編集関数（リフレクションで自動化も）。ハンドルで持つ
    - [x] 調整値は、ファイルに保存。デバッグ描画は、`ImDrawList`
    - [x] 製品版からは、`#ifdef` ＋ リンクしない。入力は `WantCapture...` で調停

## 関連ページ

- [Dear ImGui](index.md)
- [ウィジェット一覧](widgets.md)
- [レイアウトとウィンドウ](layout.md)
- [ログとデバッグ支援の設計](../../design/practice/logging-debug.md)
- [フレーム時間の設計](../../optimize/frame-budget.md)
- [Jolt のデバッグ描画](../jolt/debug-renderer.md)
- [ECS](../../design/patterns/ecs.md)
