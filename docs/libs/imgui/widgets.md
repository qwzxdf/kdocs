---
title: ImGui のウィジェット一覧
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のウィジェット一覧

ImGui の<strong>部品（ウィジェット）</strong>は、関数を 1 回呼ぶだけで、画面に出て、操作の結果が戻り値と、渡した変数に返ってきます（[即時モード](index.md)）。このページは、よく使う部品を、種類ごとに、使い方と戻り値で説明します。部品の「ラベル」が ID を兼ねることと、`Begin` と `End` の対応が、最初の落とし穴です。

!!! tip "ポイント"
    - 部品は<strong>「描く」と「入力を受け取る」を、1 回の関数呼び出し</strong>で行う。<strong>戻り値 ＝ 今フレームで、変更・クリックされたか</strong>。
    - 値はポインタ（`float*`、`bool*`）で渡す。ImGui が、その変数を直接書き換える。
    - ラベル（文字列）が、部品の ID。同じラベルが 2 つあると、同じ部品として扱われる（`##` で、見えない ID を付ける）。
    - `Begin...` が `true` を返したときだけ、`End...` を呼ぶもの（`BeginCombo`、`BeginTable` など）と、常に `End` を呼ぶもの（`Begin` / `End`）がある。
    - 数値の調整は、`Drag`（ドラッグで増減）が便利。範囲があるなら `Slider`。
    - `std::string` を `InputText` に渡すには、`imgui_stdlib.h`。

## 基本の考え方

```cpp
static float speed = 3.0f;
static bool godmode = false;

ImGui::Begin("デバッグ");

if (ImGui::Button("リセット")) {
  Reset();
}
ImGui::SliderFloat("速さ", &speed, 0.0f, 10.0f);
ImGui::Checkbox("無敵", &godmode);

ImGui::End();
```

| 点 | 説明 |
| --- | --- |
| **`ImGui::Button(...)`** | クリックされたフレームだけ `true` を返す |
| `ImGui::SliderFloat(..., &speed, ...)` | 変更されたフレームだけ `true`。`speed` が、直接書き換わる |
| `static` や、メンバ変数 | 値を、フレームをまたいで持つ必要がある（ローカル変数は、毎フレーム初期化される） |
| `Begin` / `End` | ウィンドウを作る。`End` は、`Begin` の戻り値に関係なく必ず呼ぶ |

<svg class="fig imgui" data-fig="imgui-gallery-basic" viewBox="0 0 780 340" role="img" aria-label="基本ウィジェットの見た目"><rect x="0" y="0" width="780" height="340" fill="#1b1b1f" rx="6"/><rect x="20.0" y="20.0" width="360.0" height="300.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="20.0" y="20.0" width="360.0" height="19.0" rx="0" fill="#294a7a" /><path d="M27,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="40.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Demo</text><text x="28.0" y="61.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Hello, ImGui!</text><rect x="28.0" y="70.0" width="48.0" height="19.0" rx="3" fill="#23456d" /><text x="36.0" y="84.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Save</text><rect x="28.0" y="93.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><path d="M32,102 l4,4 l7,-8" fill="none" stroke="#4296fa" stroke-width="2.2"/><text x="49.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Enable</text><circle cx="36" cy="125" r="8" fill="#1d2f49"/><text x="48.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >A</text><circle cx="76" cy="125" r="8" fill="#1d2f49"/><circle cx="76" cy="125" r="4" fill="#4296fa"/><text x="88.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >B</text><circle cx="116" cy="125" r="8" fill="#1d2f49"/><text x="128.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >C</text><rect x="28.0" y="139.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="139.2" y="141.0" width="10.0" height="15.0" rx="2" fill="#3d85e0" /><text x="118.5" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >5.50</text><text x="249.0" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >speed</text><rect x="28.0" y="162.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><text x="114.5" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >1.250</text><text x="249.0" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >pos</text><rect x="28.0" y="185.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><text x="32.0" y="199.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Player</text><text x="249.0" y="199.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >name</text><rect x="28.0" y="208.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="222.0" y="208.0" width="19.0" height="19.0" rx="3" fill="#23456d" /><path d="M227,215 l4.5,6 l4.5,-6 z" fill="#ffffff"/><text x="32.0" y="222.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Fast</text><text x="249.0" y="222.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >mode</text><rect x="28.0" y="231.0" width="19.0" height="19.0" rx="3" fill="#4296fa" stroke="#4b4b57"/><rect x="51.0" y="231.0" width="190.0" height="19.0" rx="3" fill="#1d2f49" /><text x="55.0" y="245.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >0.26 0.59 0.98</text><text x="249.0" y="245.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >color</text><rect x="28.0" y="254.0" width="220.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="28.0" y="254.0" width="136.4" height="19.0" rx="3" fill="#3d85e0" /><text x="127.2" y="268.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >62%</text><rect x="21.0" y="279.0" width="358.0" height="1.0" rx="0" fill="#5c5c6e" /><line x1="385" y1="56" x2="405" y2="56" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="60" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::Text("...")</text><line x1="385" y1="79" x2="405" y2="79" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="83" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::Button("Save")</text><line x1="385" y1="102" x2="405" y2="102" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="106" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::Checkbox("Enable", &amp;b)</text><line x1="385" y1="125" x2="405" y2="125" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="129" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::RadioButton("A", &amp;i, 0)</text><line x1="385" y1="148" x2="405" y2="148" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="152" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::SliderFloat("speed", &amp;f, 0, 10)</text><line x1="385" y1="171" x2="405" y2="171" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="175" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::DragFloat("pos", &amp;f, 0.01f)</text><line x1="385" y1="194" x2="405" y2="194" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="198" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::InputText("name", buf, size)</text><line x1="385" y1="217" x2="405" y2="217" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="221" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::Combo("mode", &amp;i, items, n)</text><line x1="385" y1="240" x2="405" y2="240" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="244" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::ColorEdit3("color", col)</text><line x1="385" y1="263" x2="405" y2="263" stroke="#9ec5ff" stroke-width="1"/><text x="412" y="267" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::ProgressBar(0.62f, size)</text></svg>

実際の見た目と、それを出す関数です。関数の一覧は、[関数早見表](reference/widgets.md) にまとめています。

## テキスト

| 関数 | 用途 |
| --- | --- |
| **`Text(fmt, ...)`** | 文字を表示（`printf` 形式：`"%d"`、`"%.2f"`） |
| `TextColored(ImVec4, fmt, ...)` | 色付きの文字 |
| `TextDisabled(fmt, ...)` | 薄い色（無効に見える） |
| `TextWrapped(fmt, ...)` | ウィンドウの幅で、折り返す |
| `TextUnformatted(str)` | 書式なしで、そのまま表示（`%` を含む文字列に安全。速い） |
| `LabelText(label, fmt, ...)` | 左に値、右にラベル（読み取り専用の項目） |
| `BulletText(fmt, ...)` | 箇条書きの点付き |
| `SeparatorText("見出し")` | 見出し付きの区切り線（1.89 以降） |

```cpp
ImGui::Text("HP: %d / %d", hp, max_hp);
ImGui::TextColored(ImVec4(1, 0.3f, 0.3f, 1), "警告: 残りわずか");
ImGui::TextUnformatted(log_line.c_str());
```

!!! warning "ユーザーの文字列を、そのまま `Text` に渡さない"
    `ImGui::Text(user_string)` は、`%` を書式として解釈して、クラッシュします。`TextUnformatted`、または `Text("%s", str)` にします。

## ボタンと選択

| 関数 | 戻り値 | 用途 |
| --- | --- | --- |
| **`Button("ラベル", ImVec2(w, h))`** | クリックで `true` | 普通のボタン |
| `SmallButton("ラベル")` | 同上 | 小さなボタン（文章の中に入れる） |
| `Checkbox("ラベル", &flag)` | 変更で `true` | オン・オフ |
| `RadioButton("ラベル", &value, 番号)` | 選択で `true` | 複数の中から 1 つ（同じ `value` に、番号違いで並べる） |
| `Selectable("ラベル", selected)` | クリックで `true` | リストの項目（選択状態の見た目） |
| `ArrowButton("##id", ImGuiDir_Left)` | クリックで `true` | 矢印ボタン |

```cpp
static int mode = 0;
ImGui::RadioButton("移動", &mode, 0);
ImGui::SameLine();
ImGui::RadioButton("回転", &mode, 1);
ImGui::SameLine();
ImGui::RadioButton("拡大", &mode, 2);

for (int i = 0; i < items.size(); ++i) {
  if (ImGui::Selectable(items[i].name.c_str(), selected_index == i)) {
    selected_index = i;
  }
}
```

## 数値の入力

| 関数 | 操作 | 向く場面 |
| --- | --- | --- |
| **`SliderFloat("ラベル", &v, min, max, "%.2f")`** | つまみを動かす | 範囲がある値（0〜1、角度） |
| `SliderInt` / `SliderAngle` | 同上（整数／度で表示、ラジアンで保持） | 整数・角度 |
| `DragFloat("ラベル", &v, 速さ, min, max)` | ドラッグで増減（ダブルクリックで直接入力） | 範囲が広い・不明な値。調整に最も使う |
| `DragFloat3("ラベル", &v.x)` / `SliderFloat3` | 3 つまとめて | 位置・回転・拡大（`Vector3`） |
| `InputFloat` / `InputInt` | キーボードで入力（+/- ボタン） | 正確な値 |
| `InputFloat3("ラベル", &v.x)` | 3 つ | |

```cpp
ImGui::DragFloat3("位置", &transform.position.x, 0.1f);
ImGui::DragFloat3("回転", &euler.x, 1.0f, -180.0f, 180.0f);
ImGui::SliderFloat("FOV", &camera.fov, 30.0f, 120.0f, "%.0f 度");
```

| 点 | 説明 |
| --- | --- |
| 書式文字列（`"%.2f"`） | 表示の桁数・単位を決める |
| `ImGuiSliderFlags_Logarithmic` | 対数スケール（広い範囲の値に） |
| `&v.x` | `Vector3` の先頭（3 つの `float` が、連続して並んでいる前提） |
| ダブルクリック / Ctrl + クリック | スライダーに、直接数値を入力できる |

## 文字の入力

```cpp
static char name[64] = "";
ImGui::InputText("名前", name, sizeof(name));
```

| 関数 | 用途 |
| --- | --- |
| **`InputText(label, char* buf, size, flags)`** | **1 行の文字入力。バッファの大きさを渡す** |
| `InputTextMultiline(label, buf, size, ImVec2)` | 複数行 |
| `InputTextWithHint(label, hint, buf, size)` | 薄い説明文（ヒント）付き |

### std::string で使う

固定長の `char` 配列は不便です。`misc/cpp/imgui_stdlib.h`（ImGui に同梱）を include すれば、`std::string` を、そのまま渡せます。

```cpp
#include "misc/cpp/imgui_stdlib.h"

static std::string name;
ImGui::InputText("名前", &name);
```

| フラグ | 意味 |
| --- | --- |
| `ImGuiInputTextFlags_EnterReturnsTrue` | Enter を押したときだけ `true` を返す |
| `ImGuiInputTextFlags_ReadOnly` | 読み取り専用 |
| `ImGuiInputTextFlags_Password` | 入力を、`*` で隠す |
| `ImGuiInputTextFlags_CharsDecimal` | 数字だけを入力できる |

## 色

| 関数 | 用途 |
| --- | --- |
| **`ColorEdit3("ラベル", &color.x)`** | 色の編集（小さな色見本 + 数値。クリックでピッカー） |
| `ColorEdit4` | アルファ付き |
| `ColorPicker4("ラベル", &color.x)` | 大きな色のピッカーを、直接表示 |
| `ColorButton("##id", ImVec4)` | 色のボタン（押せる色見本） |

```cpp
ImGui::ColorEdit3("ライトの色", &light.color.x);
```

## リストとコンボボックス

### Combo

```cpp
static int current = 0;
const char* items[] = {"スライム", "ゴブリン", "ドラゴン"};
ImGui::Combo("敵の種類", &current, items, IM_ARRAYSIZE(items));
```

**項目を動的に作る**ときは、`BeginCombo` / `EndCombo`を使います。

```cpp
if (ImGui::BeginCombo("敵の種類", enemy_names[current].c_str())) {
  for (int i = 0; i < enemy_names.size(); ++i) {
    bool selected = (current == i);
    if (ImGui::Selectable(enemy_names[i].c_str(), selected)) current = i;
    if (selected) ImGui::SetItemDefaultFocus();
  }
  ImGui::EndCombo();
}
```

`Begin...` が `true` のときだけ、`End...` を呼びます。

### ListBox

```cpp
if (ImGui::BeginListBox("##list", ImVec2(-FLT_MIN, 8 * ImGui::GetTextLineHeightWithSpacing()))) {
  for (int i = 0; i < items.size(); ++i) {
    if (ImGui::Selectable(items[i].c_str(), i == selected)) selected = i;
  }
  ImGui::EndListBox();
}
```

<svg class="fig imgui" data-fig="imgui-gallery-containers" viewBox="0 0 780 380" role="img" aria-label="コンテナ系ウィジェットの見た目"><rect x="0" y="0" width="780" height="380" fill="#1b1b1f" rx="6"/><rect x="20.0" y="20.0" width="360.0" height="340.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="20.0" y="20.0" width="360.0" height="19.0" rx="0" fill="#294a7a" /><path d="M27,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="40.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Containers</text><rect x="21.0" y="39.0" width="358.0" height="19.0" rx="0" fill="#232329" /><text x="28.0" y="53.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >File</text><text x="74.0" y="53.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Edit</text><text x="120.0" y="53.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >View</text><rect x="28.0" y="66.0" width="60.0" height="19.0" rx="3" fill="#3369ad" /><text x="38.0" y="80.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Scene</text><rect x="90.0" y="66.0" width="68.0" height="19.0" rx="3" fill="#2e5994" /><text x="100.0" y="80.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Assets</text><rect x="160.0" y="66.0" width="44.0" height="19.0" rx="3" fill="#2e5994" /><text x="170.0" y="80.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Log</text><rect x="28.0" y="85.0" width="344.0" height="2.0" rx="0" fill="#3369ad" /><rect x="22.0" y="93.0" width="356.0" height="19.0" rx="0" fill="#24435f" /><path d="M30,99 l10,0 l-5,9 z" fill="#ffffff"/><text x="46.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Transform</text><rect x="44.0" y="116.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><text x="86.5" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >0.00  1.50  0.00</text><text x="265.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >position</text><rect x="44.0" y="139.0" width="213.0" height="19.0" rx="3" fill="#1d2f49" /><text x="86.5" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >0.00  0.00  0.00</text><text x="265.0" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >rotation</text><path d="M30,168 l10,0 l-5,9 z" fill="#ffffff"/><text x="46.0" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Hierarchy</text><rect x="22.0" y="185.0" width="356.0" height="19.0" rx="0" fill="#24435f" /><path d="M47,189 l0,10 l9,-5 z" fill="#ffffff"/><text x="62.0" y="199.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Player</text><path d="M47,212 l0,10 l9,-5 z" fill="#ffffff"/><text x="62.0" y="222.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Enemy</text><text x="28.0" y="245.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >item 0</text><rect x="26.0" y="252.0" width="348.0" height="19.0" rx="0" fill="#3a7bc4" /><text x="28.0" y="266.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >item 1</text><text x="28.0" y="287.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >item 2</text><rect x="28.0" y="294.0" width="260.0" height="19.0" rx="0" fill="#303033" /><text x="32.0" y="308.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Name</text><text x="152.0" y="308.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >HP</text><text x="222.0" y="308.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Lv</text><text x="32.0" y="327.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Slime</text><text x="152.0" y="327.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >12</text><text x="222.0" y="327.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >1</text><rect x="28.0" y="332.0" width="260.0" height="19.0" rx="0" fill="#3a7bc4" /><text x="32.0" y="346.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Goblin</text><text x="152.0" y="346.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >30</text><text x="222.0" y="346.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >3</text><text x="32.0" y="365.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Dragon</text><text x="152.0" y="365.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >999</text><text x="222.0" y="365.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >50</text><rect x="148.0" y="294.0" width="1.0" height="76.0" rx="0" fill="#3a3a44" /><rect x="218.0" y="294.0" width="1.0" height="76.0" rx="0" fill="#3a3a44" /><line x1="385" y1="75" x2="405" y2="75" stroke="#9ec5ff"/><text x="412" y="79" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::BeginTabBar / BeginTabItem</text><line x1="385" y1="102" x2="405" y2="102" stroke="#9ec5ff"/><text x="412" y="106" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::CollapsingHeader("Transform")</text><line x1="385" y1="171" x2="405" y2="171" stroke="#9ec5ff"/><text x="412" y="175" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::TreeNode / TreePop</text><line x1="385" y1="240" x2="405" y2="240" stroke="#9ec5ff"/><text x="412" y="244" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::Selectable("item", sel)</text><line x1="385" y1="303" x2="405" y2="303" stroke="#9ec5ff"/><text x="412" y="307" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::BeginTable / TableNextRow</text><line x1="385" y1="40" x2="405" y2="40" stroke="#9ec5ff"/><text x="412" y="44" style="fill:#9ec5ff;font-family:Consolas,monospace;font-size:12px;">ImGui::BeginMenuBar / BeginMenu</text></svg>

ツリー・タブ・テーブル・メニューの実際の見た目です。

## ツリーと折りたたみ

| 関数 | 用途 |
| --- | --- |
| **`TreeNode("ラベル")` … `TreePop()`** | 開閉できる木（`true` のときだけ中身を出し、`TreePop` を呼ぶ） |
| `CollapsingHeader("ラベル")` | 大きな折りたたみ見出し（`TreePop` は不要） |
| `TreeNodeEx(label, flags)` | フラグ付き（`ImGuiTreeNodeFlags_DefaultOpen`、`Leaf`、`Selected`） |

```cpp
if (ImGui::TreeNode("Transform")) {
  ImGui::DragFloat3("位置", &t.position.x);
  ImGui::TreePop();
}

if (ImGui::CollapsingHeader("Physics", ImGuiTreeNodeFlags_DefaultOpen)) {
  ImGui::DragFloat("質量", &mass);
}
```

エンティティの階層表示（シーンのツリー）に、`TreeNodeEx` の `Leaf` / `OpenOnArrow` を、よく使います。

## テーブル {#table}

**表形式**の表示です。ソート・スクロール・列の幅の変更ができます。

```cpp
ImGuiTableFlags flags = ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg |
                        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY |
                        ImGuiTableFlags_Sortable;

if (ImGui::BeginTable("enemies", 3, flags, ImVec2(0, 200))) {
  ImGui::TableSetupScrollFreeze(0, 1);
  ImGui::TableSetupColumn("名前");
  ImGui::TableSetupColumn("HP", ImGuiTableColumnFlags_WidthFixed, 60.0f);
  ImGui::TableSetupColumn("位置");
  ImGui::TableHeadersRow();

  for (const Enemy& e : enemies) {
    ImGui::TableNextRow();
    ImGui::TableNextColumn();
    ImGui::TextUnformatted(e.name.c_str());
    ImGui::TableNextColumn();
    ImGui::Text("%d", e.hp);
    ImGui::TableNextColumn();
    ImGui::Text("%.1f, %.1f", e.x, e.y);
  }
  ImGui::EndTable();
}
```

| 関数 | 意味 |
| --- | --- |
| `BeginTable(id, 列数, フラグ, サイズ)` | 表を始める（`true` のときだけ中身を出し、`EndTable`） |
| `TableSetupColumn(名前, フラグ, 幅)` | 列の設定 |
| `TableHeadersRow()` | ヘッダ行を出す |
| `TableNextRow()` / `TableNextColumn()` | 次の行・次の列へ |
| `TableGetSortSpecs()` | ソートの指定を取得（クリックされた列と向き） |
| `ImGuiListClipper` | 大量の行で、見えている行だけを描く（高速化） |

!!! note "大量の行は、ListClipper"
    数千行を毎フレーム全部描くと、重いです。`ImGuiListClipper` で、見える範囲だけを描きます。

## プロット（グラフ）

```cpp
static float frame_times[120] = {};
static int offset = 0;
frame_times[offset] = ImGui::GetIO().DeltaTime * 1000.0f;
offset = (offset + 1) % IM_ARRAYSIZE(frame_times);

ImGui::PlotLines("フレーム時間(ms)", frame_times, IM_ARRAYSIZE(frame_times), offset,
                 nullptr, 0.0f, 33.0f, ImVec2(0, 80));
```

| 関数 | 用途 |
| --- | --- |
| `PlotLines` | 折れ線グラフ |
| `PlotHistogram` | 棒グラフ |
| `ProgressBar(fraction, ImVec2, overlay)` | 進行バー（HP・ロード進捗） |

リングバッファ（`offset`）で、新しい値を書き続ける使い方が、定番です（[フレーム時間の設計](../../optimize/frame-budget.md)）。本格的なグラフが必要なら、ImPlot などの拡張があります。

## メニュー・ポップアップ・ツールチップ

### メニュー {#menu}

```cpp
if (ImGui::BeginMainMenuBar()) {
  if (ImGui::BeginMenu("ファイル")) {
    if (ImGui::MenuItem("保存", "Ctrl+S")) Save();
    if (ImGui::MenuItem("終了")) quit = true;
    ImGui::EndMenu();
  }
  if (ImGui::BeginMenu("表示")) {
    ImGui::MenuItem("デバッグ", nullptr, &show_debug);
    ImGui::EndMenu();
  }
  ImGui::EndMainMenuBar();
}
```

**`MenuItem` の第 3 引数に `bool*` を渡すと、チェック付きの項目**になります。

### ポップアップ

```cpp
if (ImGui::Button("削除")) ImGui::OpenPopup("確認");

if (ImGui::BeginPopupModal("確認", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
  ImGui::Text("本当に削除しますか？");
  if (ImGui::Button("はい")) { Delete(); ImGui::CloseCurrentPopup(); }
  ImGui::SameLine();
  if (ImGui::Button("いいえ")) ImGui::CloseCurrentPopup();
  ImGui::EndPopup();
}
```

| 関数 | 用途 |
| --- | --- |
| `OpenPopup(id)` | ポップアップを開く（1 回） |
| `BeginPopup(id)` | 普通のポップアップ（外をクリックで閉じる） |
| `BeginPopupModal(id)` | モーダル（閉じるまで、他を触れない） |
| `BeginPopupContextItem()` | 右クリックのメニュー |
| `CloseCurrentPopup()` | 閉じる |

### ツールチップ

```cpp
ImGui::Button("攻撃");
if (ImGui::IsItemHovered()) {
  ImGui::SetTooltip("敵に、%d のダメージを与える", damage);
}
```

直前の部品にマウスが乗ったときに、説明を出します（`IsItemHovered`）。

## ID と、ラベルの重複

部品の ID は、ラベル文字列から作られます。同じラベルが複数あると、同じ部品と扱われて、片方しか反応しません。

```cpp
for (Enemy& e : enemies) {
  if (ImGui::Button("削除")) Remove(e);
}
```

このコードは、1 つ目のボタンしか、反応しません。

| 方法 | 書き方 | 説明 |
| --- | --- | --- |
| `##` で、見えない ID を足す | `"削除##" + 番号` | `##` より後ろは、画面に出ないが、ID になる |
| `###` | `"表示名###固定ID"` | `###` の後ろだけが ID（表示名が変わっても、ID は同じ） |
| `PushID` / `PopID` | `ImGui::PushID(i); ...; ImGui::PopID();` | ID の、前置きを積む（ループに最適） |

```cpp
for (int i = 0; i < enemies.size(); ++i) {
  ImGui::PushID(i);
  if (ImGui::Button("削除")) Remove(i);
  ImGui::PopID();
}
```

## Begin / End の対応

| 組 | `End` を呼ぶ条件 |
| --- | --- |
| `Begin` / `End`（ウィンドウ） | `Begin` の戻り値に関係なく、必ず `End` |
| `BeginChild` / `EndChild` | 同様に、必ず `EndChild` |
| `BeginCombo`・`BeginListBox`・`BeginTable`・`BeginMenu`・`BeginPopup`・`BeginTabBar`・`TreeNode` | `true` のときだけ、対応する `End` / `Pop` |

対応が崩れると、assertで止まります（デバッグビルドで分かる）。

## よくあるミス

??? failure "同じラベルのボタンが複数あり、1 つしか反応しない"
    `PushID` か `##` で、ID を変えます。

??? failure "`BeginCombo` が `false` なのに `EndCombo` を呼ぶ"
    `true` のときだけ、`End` を呼びます。

??? failure "ローカル変数を、スライダーに渡して、値が戻る"
    毎フレーム、初期化されます。`static` かメンバ変数にします。

??? failure "`ImGui::Text(user_string)` でクラッシュする"
    `TextUnformatted` か、`Text("%s", ...)`。

??? failure "`DragFloat3(..., &v)` で、構造体が壊れる"
    `float` 3 つが連続している型（`&v.x`）にだけ使います。

??? failure "大量の行を、毎フレーム全部描いて遅い"
    `ImGuiListClipper` を使います。

??? failure "日本語のラベルが `?` になる"
    日本語フォントが必要です（[フォント](fonts.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 部品は関数 1 回で、描画と入力。戻り値 ＝ 変更・クリックされたか。値はポインタで渡す
    - [x] 調整は`DragFloat`、範囲があれば`SliderFloat`。`Vector3` は `DragFloat3(&v.x)`
    - [x] `std::string` は `imgui_stdlib.h`。ユーザー文字列は `TextUnformatted`
    - [x] `BeginXxx` が `true` のときだけ `EndXxx`（ただし、`Begin` / `End` ウィンドウは必ず）
    - [x] ラベルが ID。重複は `PushID` / `##`
    - [x] 大量の行は `ImGuiListClipper`

## 関連ページ

- [Dear ImGui](index.md)
- [レイアウトとウィンドウ](layout.md)
- [日本語フォントとアイコン](fonts.md)
- [ゲームでのデバッグ画面](debug-ui.md)
- [スタイルとテーマ](style.md)
- [ImGuizmo](imguizmo.md)
