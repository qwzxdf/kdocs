---
title: imgui-node-editor
tags:
  - 外部ライブラリ
  - GUI
---

# imgui-node-editor

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-14">C++14〜</span>
`#include <imgui_node_editor.h>`
</div>

**imgui-node-editor**（イムグイ・ノード・エディタ）は、[Dear ImGui](index.md) の上で動く**ノード エディタ**のライブラリです。四角い**ノード**（箱）を並べて、**ピン**（接続口）を**リンク**（線）でつなぐ、あの画面を作れます。Unreal Engine の Blueprint、Unity の Shader Graph、Blender のシェーダー ノードと同じ形式です。ゲームでは、**シェーダーやマテリアルの編集、ビジュアル スクリプト、会話・クエストの分岐、AI（ビヘイビア ツリー）の編集**などに使います。作者は thedmd（Michał Cichoń）です。

!!! tip "ポイント"
    - ノードエディタは <strong>「ノード」「ピン」「リンク」の 3 つ</strong>で成り立つ。それぞれに**一意な ID** を付けて渡す。
    - 描き方は、ImGui と同じ**即時モード**。毎フレーム、**`ed::Begin` → `ed::BeginNode` ... `ed::EndNode` → `ed::Link` → `ed::End`** と呼ぶ。
    - **データ（ノードの一覧、リンクの一覧）は自分で持つ**。ライブラリは**描画と、ユーザーの操作の通知**だけをする。
    - リンクを新しく作る・消す操作は、**`BeginCreate` / `BeginDelete`<strong> で受け取り、</strong>自分のデータに反映**する（`AcceptNewItem` で許可）。
    - ノードの位置などは、ライブラリが**設定ファイル（JSON）に自動で保存**する。

## 導入（Visual Studio）

imgui-node-editor は、**ソースを数ファイル、プロジェクトに追加する**のが一番確実です。先に [Dear ImGui の導入](install.md) を済ませておきます。

### 方法 1：ソースを入れる

1. [GitHub の imgui-node-editor](https://github.com/thedmd/imgui-node-editor) を取得して、`third_party/imgui-node-editor/` に置く（`git clone` または ZIP）
2. 次のファイルを、ソリューション エクスプローラーで**プロジェクトに追加**

| ファイル | 内容 |
| --- | --- |
| `imgui_node_editor.cpp` | 本体 |
| `imgui_node_editor_api.cpp` | 公開する関数 |
| `imgui_canvas.cpp` | ズーム・移動できる画面 |
| `crude_json.cpp` | 設定ファイル用の JSON |
| `imgui_node_editor.h` / `imgui_node_editor_internal.h` / `imgui_node_editor_internal.inl` / `imgui_bezier_math.h` / `imgui_bezier_math.inl` / `imgui_extra_math.h` / `imgui_extra_math.inl` / `imgui_canvas.h` / `crude_json.h` | ヘッダ（フォルダーごと置けばよい） |

3. **追加のインクルード ディレクトリ** に `$(SolutionDir)third_party\imgui-node-editor` を追加する
4. ImGui の `imgui_internal.h` を使うので、ImGui のインクルード パスも通っていること

!!! warning "ImGui のバージョンとの組み合わせ"
    imgui-node-editor は、**ImGui の内部の仕組みを使っている**ので、新しすぎる ImGui だとビルドエラーになることがあります。`master` ブランチと、**同じころの ImGui**（リポジトリのタグ、`develop` ブランチなど）の組み合わせを使います。うまくいかないときは、ImGui のバージョンを 1 つ前に下げます。

### 方法 2：vcpkg

```powershell
vcpkg search imgui-node-editor
```

ポートがある場合は、`vcpkg install` で入れられます。ポートの有無・名前・バージョンは変わるので、必ず `vcpkg search` で確認します。見つからなければ、方法 1 を使います。

### 名前空間の別名

ライブラリの名前空間は `ax::NodeEditor` で長いので、**別名**を付けて使います（サンプルも同じ書き方です）。

```cpp
#include <imgui_node_editor.h>

namespace ed = ax::NodeEditor;  // 以降、ed:: と書ける
```

## 仕組み：ノード・ピン・リンク

<svg class="fig flow" viewBox="0 0 418 280" role="img" aria-label="ノード・ピン・リンク"><defs><marker id="fl88120" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ノード・ピン・リンク</text><line x1="107.0" y1="64.0" x2="311.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl88120)"/><text x="209.0" y="58.0" text-anchor="middle" style="font-size:12px">リンク</text><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">数値</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="314.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="352.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">足し算</text><circle cx="316.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="316.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="168.0" y="128.0" width="82" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="209.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">出力ピン</text><circle cx="170.0" cy="130.0" r="10" fill="#2ea043"/><text x="170.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="168.0" y="212.0" width="82" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="209.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">入力ピン</text><circle cx="170.0" cy="214.0" r="10" fill="#2ea043"/><text x="170.0" y="214.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text></svg>


| 用語 | 意味 | ID の型 |
| --- | --- | --- |
| **ノード**（Node） | 四角い箱。位置を持つ。中に、名前や設定を描く | `ed::NodeId` |
| **ピン**（Pin） | ノードの**接続口**。左側の**入力**と、右側の**出力** | `ed::PinId` |
| **リンク**（Link） | 2 つのピンをつなぐ**線** | `ed::LinkId` |

- 3 つの ID は**別々の型**ですが、中身は整数（ポインタ）です。**種類が違っても、同じ数字を使わない**ほうが安全です（たとえば、ノードは 1〜、ピンは 100〜、リンクは 1000〜、のように範囲を分ける）
- **自分のデータ**として、`std::vector<Node>`、`std::vector<Link>` のようなものを持ちます。ライブラリは**それを描くだけ**です

## 基本の使い方

2 つのノードを並べて、リンクでつなぐ最小の例です。

```cpp
#include <vector>

#include <imgui.h>
#include <imgui_node_editor.h>

namespace ed = ax::NodeEditor;

// ---- 自分のデータ ----
struct Pin {
  int id;
  bool is_input;
};

struct Node {
  int id;
  const char* name;
  std::vector<Pin> pins;
};

struct Link {
  int id;
  int from;  // 出力ピンの ID
  int to;    // 入力ピンの ID
};

struct Graph {
  std::vector<Node> nodes;
  std::vector<Link> links;
  int next_id = 1000;
};

class NodeEditorWindow {
 public:
  NodeEditorWindow() {
    ed::Config config;
    config.SettingsFile = "node_editor.json";  // ノードの位置などの保存先
    context_ = ed::CreateEditor(&config);

    graph_.nodes = {{1, "数値", {{11, false}}},
                    {2, "足し算", {{21, true}, {22, true}, {23, false}}}};
    graph_.links = {{100, 11, 21}};
  }

  ~NodeEditorWindow() { ed::DestroyEditor(context_); }

  void Draw() {
    ImGui::Begin("ノード エディタ");
    ed::SetCurrentEditor(context_);

    ed::Begin("エディタ", ImVec2(0.0f, 0.0f));  // 0, 0 で、ウィンドウいっぱいに

    // ① ノードとピン
    for (const Node& node : graph_.nodes) {
      ed::BeginNode(node.id);
      ImGui::TextUnformatted(node.name);
      for (const Pin& pin : node.pins) {
        ed::BeginPin(pin.id, pin.is_input ? ed::PinKind::Input : ed::PinKind::Output);
        ImGui::Text(pin.is_input ? "-> 入力 %d" : "出力 %d ->", pin.id);
        ed::EndPin();
      }
      ed::EndNode();
    }

    // ② リンク
    for (const Link& link : graph_.links) {
      ed::Link(link.id, link.from, link.to);
    }

    // ③ ユーザーの操作（リンクを作る・消す）
    HandleCreate();
    HandleDelete();

    ed::End();
    ed::SetCurrentEditor(nullptr);
    ImGui::End();
  }

 private:
  void HandleCreate() {
    if (ed::BeginCreate()) {
      ed::PinId from, to;
      if (ed::QueryNewLink(&from, &to)) {  // ピンから、別のピンまでドラッグした
        if (from && to && from != to) {
          if (ed::AcceptNewItem()) {  // マウスを離したとき true
            graph_.links.push_back({graph_.next_id++, static_cast<int>(from.Get()),
                                    static_cast<int>(to.Get())});
          }
        } else {
          ed::RejectNewItem();  // つなげない（赤く表示される）
        }
      }
    }
    ed::EndCreate();
  }

  void HandleDelete() {
    if (ed::BeginDelete()) {
      ed::LinkId link_id;
      while (ed::QueryDeletedLink(&link_id)) {
        if (ed::AcceptDeletedItem()) {
          std::erase_if(graph_.links, [&](const Link& l) {
            return l.id == static_cast<int>(link_id.Get());
          });
        }
      }
    }
    ed::EndDelete();
  }

  ed::EditorContext* context_ = nullptr;
  Graph graph_;
};
```

### 流れ

<svg class="fig flow" viewBox="0 0 809 112" role="img" aria-label="ノード エディタの 1 フレーム"><defs><marker id="fl82824" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ノード エディタの 1 フレーム</text><line x1="126.0" y1="64.0" x2="184.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl82824)"/><line x1="300.0" y1="64.0" x2="358.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl82824)"/><line x1="452.0" y1="64.0" x2="510.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl82824)"/><line x1="640.0" y1="64.0" x2="698.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl82824)"/><rect x="28.0" y="44.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="75.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ed::Begin</text><rect x="187.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="242.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ノードとピン</text><rect x="361.0" y="44.0" width="88" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="405.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ed::Link</text><rect x="513.0" y="44.0" width="124" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="575.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">操作の受け取り</text><rect x="701.0" y="44.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="741.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ed::End</text></svg>


## 関数・型の詳しい説明

### CreateEditor と DestroyEditor {#create_editor}

```cpp
EditorContext* CreateEditor(const Config* config = nullptr);
void DestroyEditor(EditorContext* ctx);
```

| 引数 | 意味 |
| --- | --- |
| `config` | 設定（保存先のファイル名など）。`nullptr` なら既定 |
| `ctx` | 破棄するエディタ |

- 戻り値: `CreateEditor` は、エディタを表す `EditorContext*`
- エディタ 1 つにつき、**1 回**作って、使い終わったら `DestroyEditor` で破棄します（クラスのコンストラクタ・デストラクタが向いています）

### Config {#config}

```cpp
struct Config {
  const char* SettingsFile;
  /* 保存・読み込みのコールバックなど */
};
```

| メンバ | 意味 |
| --- | --- |
| `SettingsFile` | **ノードの位置・画面のズームなど**を保存する JSON ファイルの名前。`nullptr` にすると保存しない（既定は `"NodeEditor.json"`） |
| `BeginSaveSession` など | ファイルではなく、**自分のデータに保存**したいときのコールバック（自作のプロジェクト ファイルに、位置を入れたいとき） |

- **エディタごとに別のファイル名**を付けます。同じ名前だと、位置が混ざります
- 位置の保存先は、<strong>実行ファイルの置き場所（カレント ディレクトリ）</strong>です

### SetCurrentEditor {#set_current_editor}

```cpp
void SetCurrentEditor(EditorContext* ctx);
```

| 引数 | 意味 |
| --- | --- |
| `ctx` | これから操作するエディタ（`nullptr` で解除） |

- 戻り値: なし
- 以降の `ed::` の関数は、ここで選んだエディタに対して働きます。**エディタを複数持つ**ときに、描く前に切り替えます。使い終わったら `nullptr` に戻します

### Begin と End {#begin_end}

```cpp
bool Begin(const char* id, const ImVec2& size = ImVec2(0, 0));
void End();
```

| 引数 | 意味 |
| --- | --- |
| `id` | エディタの ID（文字列） |
| `size` | 画面の大きさ。`(0, 0)` で、今のウィンドウの空きを全部使う |

- 戻り値: `Begin` は、描画してよいなら `true`
- **`ed::Begin` から `ed::End` の間**に、ノードとリンクを描きます。ImGui のウィンドウ（`ImGui::Begin`）の**中**で呼びます

### BeginNode と EndNode {#node}

```cpp
void BeginNode(NodeId id);
void EndNode();
```

| 引数 | 意味 |
| --- | --- |
| `id` | ノードの ID（`ed::NodeId`。整数からそのまま作れる） |

- 戻り値: なし
- **この間に、ImGui の関数**（`Text`、`Button`、`InputFloat`、`Image` など）で、ノードの中身を描きます。**普通の ImGui の部品が、そのままノードの中に置けます**
- ノードの大きさは、中身に合わせて自動で決まります
- 位置は、`SetNodePosition` で決めます（最初に 1 回）。それ以降は、ユーザーがドラッグして動かします

```cpp
ed::BeginNode(node.id);
ImGui::TextUnformatted("パラメータ");
ImGui::SetNextItemWidth(100.0f);
ImGui::DragFloat("値", &node.value, 0.1f);   // ノードの中に、ImGui の部品
ed::EndNode();
```

### BeginPin と EndPin {#pin}

```cpp
void BeginPin(PinId id, PinKind kind);
void EndPin();
enum class PinKind { Input, Output };
```

| 引数 | 意味 |
| --- | --- |
| `id` | ピンの ID（`ed::PinId`） |
| `kind` | `PinKind::Input`（入力：左側）か `PinKind::Output`（出力：右側） |

- 戻り値: なし
- **`BeginNode` と `EndNode` の間**で使います。この間に描いた ImGui の部品（文字や絵）の**範囲が、ピンの当たり判定**になります
- 入力ピンは左側、出力ピンは右側に置くのが普通です。`ImGui::SameLine()` で、ノードの中の左右に並べます
- 当たり判定の範囲を変えたいときは、**`PinRect`<strong>（当たり判定の矩形）と </strong>`PinPivotRect`**（リンクがつながる点）を使います

```cpp
ed::BeginPin(pin.id, ed::PinKind::Input);
ImGui::Text("-> %s", pin.name);
ed::EndPin();
ImGui::SameLine();            // 同じ行の右に、出力ピン
ed::BeginPin(out_id, ed::PinKind::Output);
ImGui::Text("%s ->", out_name);
ed::EndPin();
```

### Link {#link}

```cpp
bool Link(LinkId id, PinId startPinId, PinId endPinId,
          const ImVec4& color = ImVec4(1, 1, 1, 1), float thickness = 1.0f);
```

| 引数 | 意味 |
| --- | --- |
| `id` | リンクの ID（`ed::LinkId`） |
| `startPinId` | 始まりのピン（**出力ピン**） |
| `endPinId` | 終わりのピン（**入力ピン**） |
| `color` | 線の色 |
| `thickness` | 線の太さ |

- 戻り値: リンクが描かれたとき `true`
- 毎フレーム、**自分のリンクの一覧**から、すべてのリンクに対して呼びます。呼ばれなかったリンクは、画面から消えます
- 色を変えて、**データの型**（数値は緑、文字は赤、など）を区別するのがよく使われます

### BeginCreate と QueryNewLink {#create}

```cpp
bool BeginCreate(const ImVec4& color = ImVec4(1, 1, 1, 1), float thickness = 1.0f);
bool QueryNewLink(PinId* startId, PinId* endId);
bool AcceptNewItem();
void RejectNewItem();
void EndCreate();
```

| 関数 | 意味 |
| --- | --- |
| `BeginCreate()` | リンクを**作る操作**を受け付ける。ユーザーが、ピンからドラッグしているとき `true` |
| `QueryNewLink(&a, &b)` | 今ドラッグしているリンクの両端のピンを、`a`、`b` に入れる。つなげられそうなら `true` |
| `AcceptNewItem()` | **つないでよい**と答える。マウスを離した瞬間に `true` になる（このときに、自分のデータにリンクを追加する） |
| `RejectNewItem()` | **つなげない**と答える。線が赤くなる |
| `EndCreate()` | 受け付けを終える（`BeginCreate` が `false` でも**必ず**呼ぶ） |

- **つなげてよいかの判定**は、自分で行います。たとえば、
    - 同じノードの中のピンどうしはダメ
    - 出力どうし、入力どうしはダメ
    - 型が合わないものはダメ（数値の出力を、文字の入力につなげない）
    - 入力ピンには、リンクを 1 本までにする
- **`AcceptNewItem()` の中が `true` のときだけ**、リンクを追加します（ドラッグ中は `false`）

```cpp
if (ed::QueryNewLink(&from, &to)) {
  bool ok = from && to && from != to && IsCompatible(from, to);
  if (!ok) {
    ed::RejectNewItem();
  } else if (ed::AcceptNewItem()) {
    AddLink(from, to);
  }
}
```

!!! note "ピンから何もない所にドラッグしたとき"
    `QueryNewNode(&pin)` を使うと、**ピンから、何もない場所までドラッグして離した**ことを受け取れます（Blueprint の「引き出してノードを作る」メニュー）。`AcceptNewItem()` のあと、メニューを開いて、新しいノードを作ります。

<svg class="fig flow" viewBox="0 0 564 196" role="img" aria-label="リンクを作る操作（BeginCreate）"><defs><marker id="fl55422" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">リンクを作る操作（BeginCreate）</text><line x1="253.0" y1="148.0" x2="311.0" y2="148.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl55422)"/><text x="282.0" y="142.0" text-anchor="middle" style="font-size:12px">QueryNewLink</text><rect x="28.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">数値</text><rect x="460.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="498.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">足し算</text><rect x="168.0" y="128.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="209.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">出力ピン</text><rect x="314.0" y="128.0" width="82" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="355.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">入力ピン</text></svg>

### BeginDelete と QueryDeletedLink {#delete}

```cpp
bool BeginDelete();
bool QueryDeletedLink(LinkId* linkId, PinId* startId = nullptr, PinId* endId = nullptr);
bool QueryDeletedNode(NodeId* nodeId);
bool AcceptDeletedItem(bool deleteDependencies = true);
void RejectDeletedItem();
void EndDelete();
```

| 関数 | 意味 |
| --- | --- |
| `BeginDelete()` | **削除の操作**（Delete キー）を受け付ける |
| `QueryDeletedLink(&id)` | 削除されようとしているリンクを 1 つずつ取る（`while` で回す） |
| `QueryDeletedNode(&id)` | 削除されようとしているノードを取る |
| `AcceptDeletedItem()` | **削除してよい**。`true` のときに、自分のデータから消す |
| `RejectDeletedItem()` | 削除させない（固定のノードなど） |
| `EndDelete()` | 受け付けを終える（**必ず**呼ぶ） |

- ノードを削除すると、**つながっていたリンクも**まとめて削除対象になります（`deleteDependencies = true`）
- **自分のデータ（`std::vector`）から消すのを忘れる**と、次のフレームでまた描かれて、「消えない」ように見えます

<div class="anim" data-type="graph" data-label="リンクを消す操作（BeginDelete）">
n a 数値 0 0
n b 足し算 2 0
l a b hit リンク
# リンクを選んで、Delete キーを押す
---
n a 数値 0 0
n b 足し算 2 0
l a b gone QueryDeletedLink
# BeginDelete が true。消されようとしているリンクが分かる
---
n a 数値 0 0
n b 足し算 2 0
# AcceptDeletedItem のあと、自分のデータから消す。次のフレームで ed::Link が呼ばれないので、線が消える
</div>

### SetNodePosition と GetNodePosition {#position}

```cpp
void SetNodePosition(NodeId nodeId, const ImVec2& editorPosition);
ImVec2 GetNodePosition(NodeId nodeId);
ImVec2 GetNodeSize(NodeId nodeId);
```

| 引数 | 意味 |
| --- | --- |
| `nodeId` | ノードの ID |
| `editorPosition` | エディタの座標での位置（画面の座標ではなく、ズームや移動の影響を受けない座標） |

- 戻り値: `Get...` は位置・大きさ
- **ノードを最初に置く位置**に `SetNodePosition` を使います（毎フレーム呼ぶと、ドラッグで動かせなくなります。**作ったフレームに 1 回だけ**）
- 位置は設定ファイルに保存されるので、2 回目以降の起動では、保存された位置が使われます

### NavigateToContent {#navigate}

```cpp
void NavigateToContent(float duration = -1.0f);
void NavigateToSelection(bool zoomIn = false, float duration = -1.0f);
```

| 引数 | 意味 |
| --- | --- |
| `duration` | 画面が動く時間（秒）。`-1` で既定、`0` ですぐ |
| `zoomIn` | 選択したものにズームするか |

- 戻り値: なし
- 画面を、**全部のノードが見えるように**移動・拡大します（「全体を表示」ボタン用）。起動直後に 1 回呼ぶと、ノードが画面外にあって見えない、を防げます

### Suspend と Resume {#suspend}

```cpp
void Suspend();
void Resume();
```

- 戻り値: なし
- **ポップアップ（右クリック メニューなど）を出すとき**に使います。エディタは、ズームや移動の変換をかけた特殊な状態で描いているので、そのまま `ImGui::OpenPopup` / `BeginPopup` を使うと、**位置がずれたり、ズームで拡大されたり**します。`Suspend()` で変換を一時的に解除して、`Resume()` で戻します

```cpp
ed::Suspend();
if (ImGui::BeginPopup("コンテキスト メニュー")) {
  if (ImGui::MenuItem("ノードを追加")) { AddNode(); }
  ImGui::EndPopup();
}
ed::Resume();
```

### ShowNodeContextMenu など（右クリックの検出） {#context_menu data-toc-label="コンテキスト メニューの検出"}

```cpp
bool ShowNodeContextMenu(NodeId* nodeId);
bool ShowPinContextMenu(PinId* pinId);
bool ShowLinkContextMenu(LinkId* linkId);
bool ShowBackgroundContextMenu();
```

- 戻り値: **右クリックされたとき** `true`（クリックされたものの ID が引数に入る）
- `if (ed::ShowNodeContextMenu(&id)) { ImGui::OpenPopup("NodeMenu"); }` のように使い、ポップアップは `Suspend` / `Resume` で囲んで出します

### 選択の取得と設定 {#selection}

```cpp
int GetSelectedNodes(NodeId* nodes, int size);
int GetSelectedLinks(LinkId* links, int size);
bool IsNodeSelected(NodeId nodeId);
void SelectNode(NodeId nodeId, bool append = false);
void ClearSelection();
```

| 関数 | 意味 |
| --- | --- |
| `GetSelectedNodes(buf, size)` | 選択中のノードの ID を `buf` に入れて、**個数**を返す |
| `IsNodeSelected(id)` | そのノードが選択されているか |
| `SelectNode(id, append)` | ノードを選択する。`append` が `true` なら、今の選択に**足す** |
| `ClearSelection()` | 選択を解除する |

- 選択したノードの**プロパティ**を、別のウィンドウ（インスペクター）に出す、という使い方が定番です

### スタイルの変更（PushStyleColor など） {#style}

```cpp
ed::Style& GetStyle();
void PushStyleColor(StyleColor colorIndex, const ImVec4& color);
void PushStyleVar(StyleVar varIndex, float value);
void PopStyleColor(int count = 1);
void PopStyleVar(int count = 1);
```

| 項目 | 意味 |
| --- | --- |
| `StyleColor_Bg` / `StyleColor_Grid` | 背景・グリッドの色 |
| `StyleColor_NodeBg` / `StyleColor_NodeBorder` | ノードの背景・枠の色 |
| `StyleColor_HovNodeBorder` / `SelNodeBorder` | マウスを重ねたとき・選択したときの枠の色 |
| `StyleColor_PinRect` / `PinRectBorder` | ピンの当たり判定の色 |
| `StyleVar_NodePadding` | ノードの中の余白 |
| `StyleVar_NodeRounding` | ノードの角の丸み |
| `StyleVar_NodeBorderWidth` | 枠の太さ |

- ノードの種類ごとに色を変えるときは、`BeginNode` の**前に** `PushStyleColor` し、`EndNode` の**後に** `PopStyleColor` します

### EditorContext の複数化 {#multiple}

- エディタを**複数**（マテリアル エディタ、ビヘイビア ツリー エディタなど）持つときは、`ed::CreateEditor` で、**別々の `EditorContext`** を作ります。描くときに `SetCurrentEditor` で切り替えます。`Config::SettingsFile` を、エディタごとに**別の名前**にします

## ノードを実際のゲームのデータにつなぐ

ノード エディタは、**見た目と操作だけ**で、**何を意味するか**は自分で決めます。ゲームでは、次の流れで使います。

```text
① 自分のデータ構造を決める
     Node { id, type, params, pins[] }   Link { id, from_pin, to_pin }
② ノードの種類ごとに、中身を描く関数を作る（ImGui の部品で）
③ ed:: の関数で、ノードとリンクを描く
④ ユーザーの操作（作る・消す・動かす）を受け取って、①のデータに反映する
⑤ ①のデータを保存（JSON など）・読み込み・実行する
```

| 使い方 | 実行のしかた |
| --- | --- |
| **マテリアル / シェーダー グラフ** | グラフをたどって、HLSL のコードを生成する |
| **ビジュアル スクリプト** | 出力ピンから入力ピンへ、実行の順番にたどる（データの流れ / 実行の流れ） |
| **会話・クエストの分岐** | ノード ＝ 台詞や条件、リンク ＝ 次の台詞。実行時はグラフをたどって会話を進める |
| <strong>ビヘイビア ツリー（AI）</strong> | ノード ＝ 行動、リンク ＝ 親子。保存して、ゲームで読む |

!!! tip "データは自分で保存する"
    ライブラリが保存する設定ファイル（JSON）は、**ノードの位置と画面の状態**だけです。**ノードの種類やパラメータ、リンク**は、自分のデータなので、[JSON](../serialization/nlohmann-json.md) や [cereal](../serialization/cereal.md) で自分で保存・読み込みします。ID の重複を避けるため、**読み込んだあとに、次に使う ID を最大値 + 1 にします**。

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| シェーダー・マテリアルを、ノードで作る | 出力のコードを生成する |
| 会話や、クエストの分岐を編集 | ノード ＝ イベント、リンク ＝ 遷移 |
| AI（ビヘイビア ツリー、ステートマシン）の編集 | [ステートマシン](../../design/patterns/state-machine.md) を、画面で組む |
| ビジュアル スクリプトで、ゲームの仕組みを作る | ゲームデザイナーが、コードを書かずに作れる |
| アニメーションのブレンド ツリー | 入力のアニメーションを、ノードで混ぜる |

## よくあるミス

??? failure "ID が重複して、ノードやピンが反応しない"
    ノード・ピン・リンクの ID は、**エディタの中で一意**である必要があります。ループ変数 `i` をそのまま ID にして、ノードのピンも `i` を使うと、ぶつかります。種類ごとに範囲を分けるか、1 つのカウンターから発番します。

??? failure "`SetNodePosition` を毎フレーム呼んで、ノードが動かせない"
    毎フレーム位置を上書きするので、ドラッグしても元に戻ります。**ノードを作ったフレームに 1 回だけ**呼びます。

??? failure "`Begin` / `End` や `BeginCreate` / `EndCreate` の対応がずれる"
    `BeginCreate()` や `BeginDelete()` が `false` でも、**`EndCreate()` / `EndDelete()` を必ず呼びます**。呼ばないと、アサートで止まります。

??? failure "リンクを消したのに、自分のデータから消していない"
    `AcceptDeletedItem()` が `true` のときに、**自分の `std::vector<Link>` からも消します**。消さないと、次のフレームで `ed::Link` が呼ばれて、また線が出ます。

??? failure "ポップアップがずれる・拡大される"
    ノード エディタの中で、直接 `ImGui::OpenPopup` / `BeginPopup` を使うと、ズームの影響を受けます。`ed::Suspend()` と `ed::Resume()` で囲みます。

??? failure "ImGui を更新したら、ビルドエラーになる"
    imgui-node-editor は、ImGui の内部に依存します。ImGui を新しくしたら、imgui-node-editor も、対応する新しいバージョンにします。両方を **Git のタグ（コミット）で固定**しておくと、突然壊れません。

## 類似

| 名前 | 違い |
| --- | --- |
| ImNodes（Nelarius） | もっと小さくて、使いやすい ImGui のノード エディタ。機能は少なめ |
| ImGuizmo の `GraphEditor` | ImGuizmo に入っている、簡単なグラフ エディタ |
| [ImSequencer](imsequencer.md) | 時間軸の編集 |
| Unreal Blueprint / Unity Shader Graph | 商用エンジンの、同じ種類の機能 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] ノード・ピン・リンクに、重ならない ID を付ける
    - [x] `ed::Begin` の中で、`BeginNode` / `BeginPin` と `ed::Link` を毎フレーム描く
    - [x] リンクの作成・削除は、`BeginCreate` / `BeginDelete` で受け取り、**自分のデータ**に反映する
    - [x] 位置の保存はライブラリ、**中身の保存は自分**
    - [x] ポップアップは `Suspend` / `Resume` で囲む

## 関連ページ

- [Dear ImGui](index.md)
- [ImGuizmo](imguizmo.md)
- [ImSequencer](imsequencer.md)
- [ステートマシン](../../design/patterns/state-machine.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [imgui-node-editor（GitHub）](https://github.com/thedmd/imgui-node-editor)
