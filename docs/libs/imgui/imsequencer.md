---
title: ImSequencer
tags:
  - 外部ライブラリ
  - GUI
---

# ImSequencer

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11〜</span>
`#include "ImSequencer.h"`
</div>

**ImSequencer**（イムシーケンサー）は、[ImGuizmo](imguizmo.md) と同じ作者のリポジトリに入っている、タイムライン（シーケンサー）を出す ImGui の部品です。動画編集ソフトや、Unity の Timeline のような、横軸が時間（フレーム）で、縦に項目が並び、それぞれの項目が「いつからいつまで」を帯で表す画面を作れます。アニメーションのクリップ、エフェクトの発生タイミング、カットシーンのイベントなどを、マウスで編集できます。使い方は、自分のデータを `SequencerInterface` という決まった窓口（インターフェース）でライブラリに見せる形です。

!!! tip "ポイント"
    - 自分の **データ（項目の一覧）を持つクラス**を作り、**`ImSequencer::SequencerInterface` を継承**して、決まった関数を実装する。
    - 毎フレーム、`ImSequencer::Sequencer(...)`<strong> を呼ぶ。現在のフレーム・開閉・選択・表示の先頭フレームは、</strong>自分の変数を渡して、ライブラリに更新してもらう。
    - 項目の「開始・終了フレーム」は、ポインタ（`int`）を渡す**ので、ライブラリがマウス操作で書き換える。
    - オプションのフラグで、追加・削除・フレームの移動・コピペのどれを許すかを決める。
    - 項目の中の絵（カーブなど）は、`CustomDraw` で自由に描ける。

## 導入（Visual Studio）

ImSequencer は、ImGuizmo のリポジトリに含まれています。[Dear ImGui の導入](install.md) を済ませてから、**ソースを 2 つ追加**します。

1. [ImGuizmo（GitHub）](https://github.com/CedricGuillemet/ImGuizmo) を取得して、`third_party/ImGuizmo/` に置く
2. ソリューション エクスプローラーで、プロジェクトに追加する

| ファイル | 内容 |
| --- | --- |
| `ImSequencer.h` / `ImSequencer.cpp` | タイムライン本体 |
| `ImCurveEdit.h` / `ImCurveEdit.cpp` | カーブ エディタ（項目の中に、カーブを描いて編集したいときだけ） |

3. 追加のインクルード ディレクトリ に `$(SolutionDir)third_party\ImGuizmo` を追加する
4. `imgui_internal.h` を使うので、ImGui のインクルード パスも通っていること

!!! note "vcpkg"
    `vcpkg install imguizmo:x64-windows` で入る ImGuizmo には、ImSequencer も含まれていることが多いです。`vcpkg search imguizmo` と、インストール先の `include` フォルダーを確認してください。

## 画面のしくみ

<div class="anim" data-type="graph" data-label="タイムライン：帯をドラッグして編集する">
n r1 走る 0 0
n r2 ジャンプ 2 1
n r3 爆発 1 2
# 横が時間（フレーム）。帯の左端が開始、右端が終了
---
n r1 走る 1 0 hit
n r2 ジャンプ 2 1
n r3 爆発 1 2
# 帯をドラッグすると、開始・終了フレームがまとめて動く（start / end の変数が書き換わる）
---
n r1 走る 1 0
n r2 ジャンプ 2 1 hit
n r3 爆発 3 2 hit
# ほかの項目も、同じように動かせる。現在のフレームの縦線は、目盛りをクリックして動かす
</div>


- 項目の**帯の端をドラッグ**すると、開始・終了フレームが変わる
- 帯の中をドラッグすると、帯ごと前後に動く
- 上の目盛りをクリックすると、現在のフレームが動く
- マウス ホイールで、時間軸がスクロールする

## 基本の使い方

最小の実装です。3 種類の項目（アニメーション、効果音、エフェクト）が並んだタイムラインを作ります。

```cpp
#include <string>
#include <vector>

#include "ImSequencer.h"
#include "imgui.h"

// 1 つの項目（時間軸の上の 1 本の帯）
struct Clip {
  int type;   // 項目の種類（0: アニメ、1: 効果音、2: エフェクト）
  int start;  // 開始フレーム
  int end;    // 終了フレーム
  bool expanded = false;
};

// ライブラリに自分のデータを見せる窓口
class MySequence : public ImSequencer::SequencerInterface {
 public:
  int GetFrameMin() const override { return frame_min_; }
  int GetFrameMax() const override { return frame_max_; }
  int GetItemCount() const override { return static_cast<int>(clips_.size()); }

  // index 番目の項目の情報を、ポインタで教える（start / end はマウスで書き換えられる）
  void Get(int index, int** start, int** end, int* type, unsigned int* color) override {
    Clip& clip = clips_[index];
    if (color) {
      *color = kColors[clip.type];
    }
    if (start) {
      *start = &clip.start;
    }
    if (end) {
      *end = &clip.end;
    }
    if (type) {
      *type = clip.type;
    }
  }

  void Add(int type) override { clips_.push_back({type, 0, 10}); }  // 「追加」で呼ばれる
  void Del(int index) override { clips_.erase(clips_.begin() + index); }
  void Duplicate(int index) override { clips_.push_back(clips_[index]); }

  size_t GetCustomHeight(int index) override {
    return clips_[index].expanded ? 300 : 0;  // 開いたときの追加の高さ
  }

  // 項目の種類
  int GetItemTypeCount() const override { return 3; }
  const char* GetItemTypeName(int type) const override { return kTypeNames[type]; }
  const char* GetItemLabel(int index) const override {
    static char label[64];
    snprintf(label, sizeof(label), "%s", kTypeNames[clips_[index].type]);
    return label;
  }

  int frame_min_ = 0;
  int frame_max_ = 100;
  std::vector<Clip> clips_;

 private:
  static constexpr const char* kTypeNames[3] = {"アニメーション", "効果音", "エフェクト"};
  static constexpr unsigned int kColors[3] = {0xFFAA8844, 0xFF44AA88, 0xFF8844AA};
};

// ---- 毎フレーム ----
void DrawTimeline(MySequence& sequence) {
  static int current_frame = 0;      // 現在のフレーム（縦線の位置）
  static bool expanded = true;       // タイムラインの開閉
  static int selected_entry = -1;    // 選択中の項目
  static int first_frame = 0;        // 表示の先頭フレーム（スクロール）

  ImGui::Begin("タイムライン");
  ImSequencer::Sequencer(&sequence, &current_frame, &expanded, &selected_entry,
                         &first_frame,
                         ImSequencer::SEQUENCER_EDIT_STARTEND |  // 端をドラッグできる
                             ImSequencer::SEQUENCER_ADD |        // 追加できる
                             ImSequencer::SEQUENCER_DEL |        // 削除できる
                             ImSequencer::SEQUENCER_CHANGE_FRAME);  // 現在のフレームを動かせる
  ImGui::End();
}
```

### 流れ

<svg class="fig flow" viewBox="0 0 570 172" role="img" aria-label="ImSequencer のデータの流れ"><defs><marker id="fl57298" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ImSequencer のデータの流れ</text><line x1="141.0" y1="124.0" x2="199.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57298)"/><text x="170.0" y="118.0" text-anchor="middle" style="font-size:12px">Get で見せる</text><line x1="370.0" y1="124.0" x2="428.0" y2="124.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl57298)"/><text x="399.0" y="118.0" text-anchor="middle" style="font-size:12px">毎フレーム</text><path d="M486.5,102.0 Q284.8,50.0 83.0,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl57298)"/><text x="284.8" y="64.0" text-anchor="middle" style="font-size:12px">直接書き換え</text><rect x="28.0" y="104.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">自分のデータ</text><rect x="202.0" y="104.0" width="165" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="284.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">SequencerInterface</text><rect x="431.0" y="104.0" width="111" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="486.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Sequencer()</text></svg>


## 関数・型の詳しい説明

### Sequencer {#sequencer}

```cpp
namespace ImSequencer {
bool Sequencer(SequencerInterface* sequencer, int* currentFrame, bool* expanded,
               int* selectedEntry, int* firstFrame, int sequenceOptions);
}
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `sequencer` | `SequencerInterface*` | 自分のデータを見せる `SequencerInterface` |
| `currentFrame` | `int*` | **現在のフレーム**の変数へのポインタ。マウスで動かすと書き換わる |
| `expanded` | `bool*` | タイムライン全体が開いているかの変数へのポインタ（折りたたみ用） |
| `selectedEntry` | `int*` | 選択中の項目の番号へのポインタ（選択がなければ `-1`） |
| `firstFrame` | `int*` | 画面左端のフレームへのポインタ（スクロール位置） |
| `sequenceOptions` | `int` | 許可する操作のフラグ（[オプション](#options)） |

- 戻り値: 今のフレームに、ユーザーが何かを操作したとき `true`
- `currentFrame`、`expanded`、`selectedEntry`、`firstFrame` は、自分で持っている変数（`static` やメンバ）を渡します。毎フレーム新しく作ると、状態が保持されません
- `ImGui::Begin` と `End` の間で呼びます

### SequencerInterface {#interface}

```cpp
struct SequencerInterface {
  virtual int GetFrameMin() const = 0;
  virtual int GetFrameMax() const = 0;
  virtual int GetItemCount() const = 0;

  virtual void BeginEdit(int /*index*/) {}
  virtual void EndEdit() {}
  virtual int GetItemTypeCount() const { return 0; }
  virtual const char* GetItemTypeName(int /*typeIndex*/) const { return ""; }
  virtual const char* GetItemLabel(int /*index*/) const { return ""; }
  virtual const char* GetCollapseFmt() const { return "%d Frames / %d entries"; }

  virtual void Get(int index, int** start, int** end, int* type, unsigned int* color) = 0;
  virtual void Add(int /*type*/) {}
  virtual void Del(int /*index*/) {}
  virtual void Duplicate(int /*index*/) {}
  virtual void Copy() {}
  virtual void Paste() {}

  virtual size_t GetCustomHeight(int /*index*/) { return 0; }
  virtual void DoubleClick(int /*index*/) {}
  virtual void CustomDraw(int index, ImDrawList* draw_list, const ImRect& rc,
                          const ImRect& legendRect, const ImRect& clippingRect,
                          const ImRect& legendClippingRect) {}
  virtual void CustomDrawCompact(int index, ImDrawList* draw_list, const ImRect& rc,
                                 const ImRect& clippingRect) {}
};
```

必ず実装する（`= 0`）のは、`GetFrameMin`、`GetFrameMax`、`GetItemCount`、`Get` の 4 つです。ほかは、必要なものだけ上書きします。

| 関数 | 何を返す・何をする |
| --- | --- |
| `GetFrameMin()` / `GetFrameMax()` | タイムライン全体の、最小・最大のフレーム |
| `GetItemCount()` | 項目の数 |
| `Get(index, &start, &end, &type, &color)` | `index` 番目の項目の、開始・終了フレームへのポインタ、種類、帯の色（`0xAABBGGRR`）を設定する |
| `GetItemTypeCount()` / `GetItemTypeName(type)` | 「追加」で選べる種類の数と、その名前 |
| `GetItemLabel(index)` | 左の一覧に出す、項目の名前 |
| `Add(type)` | 「追加」で、種類 `type` の項目を作る |
| `Del(index)` | 項目を削除する |
| `Duplicate(index)` | 項目を複製する |
| `Copy()` / `Paste()` | コピー・貼り付け（`SEQUENCER_COPYPASTE` が有効なとき） |
| `BeginEdit(index)` / `EndEdit()` | 帯をドラッグし始めたとき・終わったときに呼ばれる。アンドゥ用に、操作の前後の状態を保存するのに使う |
| `GetCustomHeight(index)` | その項目を開いたときの追加の高さ（ピクセル）。0 なら開かない |
| `DoubleClick(index)` | 項目をダブルクリックしたとき（項目を開く、など） |
| `CustomDraw(...)` | 開いた項目の中身を、自分で描く（カーブ、波形など） |
| `CustomDrawCompact(...)` | 閉じているときの帯の上に、小さな絵を描く（キーフレームの印など） |
| `GetCollapseFmt()` | タイムラインを折りたたんだときの表示の書式 |

!!! warning "Get の `color` の並び"
    色は `0xAABBGGRR`（赤と青が逆の ABGR）です。`0xFF0000FF` は赤になります。

### オプションのフラグ {#options}

```cpp
enum SEQUENCER_OPTIONS {
  SEQUENCER_EDIT_NONE = 0,
  SEQUENCER_EDIT_STARTEND = 1 << 1,
  SEQUENCER_CHANGE_FRAME = 1 << 3,
  SEQUENCER_ADD = 1 << 4,
  SEQUENCER_DEL = 1 << 5,
  SEQUENCER_COPYPASTE = 1 << 6,
  SEQUENCER_EDIT_ALL = SEQUENCER_EDIT_STARTEND | SEQUENCER_CHANGE_FRAME
};
```

| フラグ | 許可すること |
| --- | --- |
| `SEQUENCER_EDIT_NONE` | 何も編集できない（表示だけ） |
| `SEQUENCER_EDIT_STARTEND` | 帯の端と中をドラッグして、開始・終了フレームを変える |
| `SEQUENCER_CHANGE_FRAME` | 上の目盛りをクリック・ドラッグして、現在のフレームを動かす |
| `SEQUENCER_ADD` | 「＋」ボタンで、項目を追加できる |
| `SEQUENCER_DEL` | 「−」ボタンで、項目を削除できる（選択中の項目） |
| `SEQUENCER_COPYPASTE` | 「Copy」「Paste」のボタンを出す |
| `SEQUENCER_EDIT_ALL` | `EDIT_STARTEND` と `CHANGE_FRAME` |

`|` で組み合わせます。再生中は `SEQUENCER_EDIT_NONE`（または `CHANGE_FRAME` だけ）にして、編集を止める、といった切り替えができます。

### Get {#get}

```cpp
void Get(int index, int** start, int** end, int* type, unsigned int* color);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `index` | `int` | 項目の番号 |
| `start` | `int` | 開始フレームの変数のアドレス**を入れる （`nullptr` のときは入れなくてよい） |
| `end` | `int` | 終了フレームの変数のアドレス**を入れる |
| `type` | `int*` | 項目の種類の番号を入れる |
| `color` | `unsigned int*` | 帯の色を入れる |

- 戻り値: なし（引数に値を入れる）
- `start` / `end` はポインタのポインタです。`*start = &clip.start;` のように、自分のデータの変数のアドレスを渡します。ライブラリがそのアドレスを通して、直接書き換えます
- 引数が `nullptr` の場合があるので、`if (start) { ... }` と確認して書きます

### BeginEdit と EndEdit（アンドゥ） {#undo data-toc-label="BeginEdit / EndEdit"}

```cpp
virtual void BeginEdit(int index) {}
virtual void EndEdit() {}
```

- 帯のドラッグを始めたときに `BeginEdit(index)`、離したときに `EndEdit()` が呼ばれます
- ここで操作前と操作後の値を保存して、アンドゥ（元に戻す）の履歴に積みます（[コマンドパターン](../../design/patterns/command.md)）。ドラッグの途中の値を全部積むと、アンドゥが使いにくくなります

```cpp
void BeginEdit(int index) override {
  editing_ = index;
  before_ = clips_[index];  // 操作前の値を覚える
}
void EndEdit() override {
  if (editing_ >= 0 && (before_.start != clips_[editing_].start ||
                        before_.end != clips_[editing_].end)) {
    undo_stack_.push_back({editing_, before_, clips_[editing_]});  // 変わったときだけ積む
  }
  editing_ = -1;
}
```

### CustomDraw {#customdraw}

```cpp
virtual void CustomDraw(int index, ImDrawList* draw_list, const ImRect& rc,
                        const ImRect& legendRect, const ImRect& clippingRect,
                        const ImRect& legendClippingRect);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `index` | `int` | 項目の番号 |
| `draw_list` | `ImDrawList*` | 描画先 |
| `rc` | `const ImRect&` | 項目の描画領域（時間軸の部分） |
| `legendRect` | `const ImRect&` | 左の凡例の領域 |
| `clippingRect` | `const ImRect&` | 時間軸側の切り取り範囲（これより外には描かない） |
| `legendClippingRect` | `const ImRect&` | 凡例側の切り取り範囲 |

- 戻り値: なし
- `GetCustomHeight` が 0 でない項目を開いたときに、その中身を自分で描くために呼ばれます。カーブ エディタ（`ImCurveEdit`）を埋め込んで、イージングやパラメータの変化を編集する使い方が定番です
- `draw_list->PushClipRect(clippingRect.Min, clippingRect.Max, true);` で、描く範囲を制限してから描きます

### ImCurveEdit（カーブの編集） {#curveedit data-toc-label="ImCurveEdit"}

```cpp
namespace ImCurveEdit {
struct Delegate {
  virtual size_t GetCurveCount() = 0;
  virtual ImVec2* GetPoints(size_t curveIndex) = 0;
  virtual size_t GetPointCount(size_t curveIndex) = 0;
  virtual uint32_t GetCurveColor(size_t curveIndex) = 0;
  virtual int EditPoint(size_t curveIndex, int pointIndex, ImVec2 value) = 0;
  virtual void AddPoint(size_t curveIndex, ImVec2 value) = 0;
  /* ... */
};
int Edit(Delegate& delegate, const ImVec2& size, unsigned int id,
         const ImRect* clippingRect = nullptr, ImVector<ImRect>* selectedPoints = nullptr);
}
```

- カーブを描いて、マウスで点を動かして編集する部品です。`Delegate` を実装して、自分のカーブのデータ（点の配列）を見せます。`CustomDraw` の中で `ImCurveEdit::Edit(...)` を呼ぶと、項目の中にカーブ エディタが出ます
- 細かい使い方は、ImGuizmo のリポジトリの `example/main.cpp` の `RampEdit` が参考になります

## タイムラインとゲームをつなぐ

タイムラインの値を、**ゲームのアニメーションに反映**します。

```cpp
// 現在のフレームに合わせて、各項目を再生する
void ApplyTimeline(const MySequence& sequence, int current_frame) {
  for (const Clip& clip : sequence.clips_) {
    bool active = current_frame >= clip.start && current_frame < clip.end;
    if (active) {
      float t = static_cast<float>(current_frame - clip.start) / (clip.end - clip.start);
      PlayClip(clip.type, t);  // t は 0.0〜1.0 の進み具合
    }
  }
}
```

| 使い方 | 説明 |
| --- | --- |
| 再生 / 停止ボタン | 自分で `ImGui::Button` を置いて、再生中は毎フレーム `current_frame` を進める |
| スクラブ（頭出し） | 縦線をドラッグすると、`current_frame` が変わる。変わるたびに、その時点の状態を表示する |
| 保存と読み込み | `clips_` を [JSON](../serialization/nlohmann-json.md) などで保存する |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| カットシーン・演出の編集 | カメラ、キャラのアニメ、効果音、台詞のタイミングを、タイムラインで並べる |
| エフェクト（パーティクル）の発生タイミング | 帯の開始・終了で、発生・消滅を決める |
| ボスの行動パターン | 攻撃の予兆と判定の時間を、フレーム単位で調整する |
| アニメーションのイベント | 「このフレームで足音を出す」を、印として置く |

## よくあるミス

??? failure "`Get` で `start` / `end` に値のコピーを渡す"
    `*start = &local_variable;` のように、**一時的な変数のアドレス**を渡すと、関数を抜けたあとに無効になります。`std::vector<Clip>` の中の要素など、ずっと残るデータのアドレスを渡します。vector が再確保されると、アドレスが無効になるので、タイムラインを描いている最中に項目を追加・削除しません（`Add` / `Del` の中では、描画の後に反映する、などの工夫をします）。

??? failure "状態の変数を、毎フレーム作り直す"
    `int current_frame = 0;` を関数の中に書くと、毎フレーム 0 に戻って、縦線が動かせません。`static` やメンバ変数で持ちます。

??? failure "`GetFrameMax` が小さすぎて、帯が見えない"
    項目の `end` が `GetFrameMax()` より大きいと、はみ出して描かれません。範囲を広げるか、項目を範囲内に収めます。

??? failure "色の並びを間違える"
    色は `0xAABBGGRR`（ABGR）です。RGBA の感覚で書くと、赤と青が入れ替わります。

??? failure "Add / Del の最中に、項目の配列が壊れる"
    ライブラリは、項目の並びを使っている最中に `Add` / `Del` を呼ぶことがあります。描画が終わったあとにまとめて反映するか、`index` の範囲を毎回確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [ImGuizmo](imguizmo.md) | 同じリポジトリ。3D のギズモ |
| ImGui の `imgui_neo_sequencer` | 別の作者の、よりモダンな見た目のシーケンサー |
| Unity の Timeline / Unreal の Sequencer | 商用エンジンの、同じ種類の機能 |
| 自作 | ImGui の描画 API（`ImDrawList`）で自作もできる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `SequencerInterface` を継承して、自分のデータを見せる（`Get` で開始・終了のアドレスを渡す）
    - [x] 毎フレーム `ImSequencer::Sequencer(...)` を呼び、現在のフレームなどは**自分の変数**で持つ
    - [x] オプションのフラグで、編集できる範囲を決める
    - [x] アンドゥは `BeginEdit` / `EndEdit`、項目の中の絵は `CustomDraw`
    - [x] 色は `0xAABBGGRR`

## 関連ページ

- [Dear ImGui](index.md)
- [ImGuizmo](imguizmo.md)
- [imgui-node-editor](node-editor.md)
- [コマンドパターン（アンドゥ）](../../design/patterns/command.md)
- [ImGuizmo / ImSequencer（GitHub）](https://github.com/CedricGuillemet/ImGuizmo)
