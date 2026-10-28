---
title: スタイルとテーマ
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のスタイルとテーマ

ImGui の見た目（色・角丸・余白・線の太さ）は、<strong>`ImGuiStyle`</strong>という構造体で決まります。標準のテーマ（ダーク・ライト・クラシック）を選ぶだけでも、項目を書き換えて自分のテーマを作れます。一部の部品だけ、一時的に変えたいときは`PushStyleColor` / `PushStyleVar`を使います。このページはテーマの選び方、色と大きさの変更、一時的な変更、保存、高 DPI への対応をまとめます。

!!! tip "ポイント"
    - <strong>標準のテーマは 3 つ</strong>：<strong>`StyleColorsDark`</strong>（既定）・`StyleColorsLight`・`StyleColorsClassic`。
    - `ImGui::GetStyle()` で `ImGuiStyle` を取得し、色（`Colors[ImGuiCol_*]`）と大きさ（`WindowRounding` など）を直接変える。
    - 一時的な変更は `PushStyleColor` / `PushStyleVar` と対応する `Pop`。個数をそろえる。
    - 色は `ImVec4(R, G, B, A)`（0〜1）。
    - 高 DPI は `style.ScaleAllSizes(scale)` とフォントの拡大。スケールは 1 回だけ。
    - テーマはコードかファイルに保存して、起動時に適用する。

!!! info "このページを読む前に"
    - [Dear ImGui](index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](install.md)（ImGui の入れ方）

## 標準のテーマ

```cpp
ImGui::StyleColorsDark();
ImGui::StyleColorsLight();
ImGui::StyleColorsClassic();
```

| テーマ | 見た目 |
| --- | --- |
| **`StyleColorsDark`** | 暗い背景（既定）。ゲーム・ツールによく使われる |
| `StyleColorsLight` | 明るい背景 |
| `StyleColorsClassic` | 昔ながらの青灰色 |

`ImGui::CreateContext()` の後、ループの前に 1 回呼びます。

<svg class="fig imgui" data-fig="imgui-style-colors" viewBox="0 0 780 260" role="img" aria-label="色の項目と画面上の場所"><rect x="0" y="0" width="780" height="260" fill="#1b1b1f" rx="6"/><rect x="20.0" y="20.0" width="340.0" height="210.0" rx="0" fill="#0f0f0f" stroke="#4b4b57" stroke-width="1" /><rect x="20.0" y="20.0" width="340.0" height="19.0" rx="0" fill="#294a7a" /><path d="M27,26 l5,0 l-2.5,7 z" fill="#ffffff"/><text x="40.0" y="34.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Style</text><text x="28.0" y="61.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Text  (ImGuiCol_Text)</text><rect x="28.0" y="70.0" width="64.0" height="19.0" rx="3" fill="#23456d" /><text x="36.0" y="84.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Button</text><rect x="28.0" y="93.0" width="17.0" height="17.0" rx="3" fill="#1d2f49" /><path d="M32,102 l4,4 l7,-8" fill="none" stroke="#4296fa" stroke-width="2.2"/><text x="49.0" y="107.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >CheckMark</text><rect x="28.0" y="116.0" width="200.0" height="19.0" rx="3" fill="#1d2f49" /><rect x="105.0" y="118.0" width="10.0" height="15.0" rx="2" fill="#3d85e0" /><text x="116.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >4.0</text><text x="236.0" y="130.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >SliderGrab</text><rect x="28.0" y="139.0" width="200.0" height="19.0" rx="3" fill="#1d2f49" /><text x="32.0" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >abc</text><text x="236.0" y="153.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >FrameBg</text><rect x="22.0" y="162.0" width="336.0" height="19.0" rx="0" fill="#24435f" /><path d="M30,168 l10,0 l-5,9 z" fill="#ffffff"/><text x="46.0" y="176.0" style="fill:#ffffff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >Header</text><text x="390.0" y="40.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_WindowBg … ウィンドウの背景</text><text x="390.0" y="62.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_TitleBgActive … タイトル バー</text><text x="390.0" y="84.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_Button / ButtonHovered / ButtonActive</text><text x="390.0" y="106.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_CheckMark … チェックの色</text><text x="390.0" y="128.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_SliderGrab … つまみ</text><text x="390.0" y="150.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_FrameBg … 入力欄・スライダーの下地</text><text x="390.0" y="172.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_Header … 折りたたみ・選択行</text><text x="390.0" y="194.0" style="fill:#9ec5ff;font-family:Consolas,'Courier New',monospace;font-size:13px;" >ImGuiCol_Border … 枠線</text></svg>

色の名前が画面のどこに対応するかの見取り図です。一覧は[フラグ早見表](reference/flags.md)の「色の名前」を参照してください。

## ImGuiStyle

```cpp
ImGuiStyle& style = ImGui::GetStyle();
style.WindowRounding = 6.0f;
style.FrameRounding = 4.0f;
style.FramePadding = ImVec2(8, 5);
style.ItemSpacing = ImVec2(8, 6);
```

### 主な項目（大きさ）

| 項目 | 意味 |
| --- | --- |
| **`WindowPadding`** | ウィンドウの内側の余白 |
| `WindowRounding` | ウィンドウの角丸（0 で四角） |
| `WindowBorderSize` | ウィンドウの枠線の太さ（0 でなし） |
| `FramePadding` | 部品（ボタン・入力欄）の内側の余白 |
| `FrameRounding` | 部品の角丸 |
| `FrameBorderSize` | 部品の枠線の太さ |
| `ItemSpacing` | 部品と部品の間隔 |
| `ItemInnerSpacing` | 部品の中の要素間隔（ラベルとの間など） |
| `IndentSpacing` | 字下げ・ツリーの幅 |
| `ScrollbarSize` / `ScrollbarRounding` | スクロールバーの太さ・角丸 |
| `GrabMinSize` / `GrabRounding` | スライダーのつまみの大きさ・角丸 |
| `TabRounding` | タブの角丸 |
| `WindowTitleAlign` | タイトルの揃え（`ImVec2(0.5f, 0.5f)` で中央） |
| `Alpha` | 全体の透明度 |
| `AntiAliasedLines` / `AntiAliasedFill` | 線・塗りのぎざぎざ防止 |

### 色の変更

**色は `style.Colors[ImGuiCol_*]` の配列**に入っています。

```cpp
ImVec4* colors = style.Colors;
colors[ImGuiCol_WindowBg] = ImVec4(0.10f, 0.10f, 0.12f, 1.00f);
colors[ImGuiCol_Button] = ImVec4(0.20f, 0.40f, 0.70f, 1.00f);
colors[ImGuiCol_ButtonHovered] = ImVec4(0.30f, 0.50f, 0.80f, 1.00f);
colors[ImGuiCol_ButtonActive] = ImVec4(0.15f, 0.35f, 0.65f, 1.00f);
```

| 項目 | 意味 |
| --- | --- |
| `ImGuiCol_Text` | 文字の色 |
| `ImGuiCol_WindowBg` | ウィンドウの背景 |
| `ImGuiCol_ChildBg` / `PopupBg` | 子ウィンドウ・ポップアップの背景 |
| `ImGuiCol_Border` | 枠線 |
| `ImGuiCol_FrameBg`（`Hovered` / `Active`） | 入力欄・チェックボックスの背景 |
| `ImGuiCol_Button`（`Hovered` / `Active`） | ボタン（通常・ホバー・押下） |
| `ImGuiCol_Header`（`Hovered` / `Active`） | ヘッダ・選択項目・メニュー項目 |
| `ImGuiCol_TitleBg`（`Active` / `Collapsed`） | タイトルバー |
| `ImGuiCol_Tab`（`Hovered` / `Active`） | タブ |
| `ImGuiCol_SliderGrab`（`Active`） | スライダーのつまみ |
| `ImGuiCol_CheckMark` | チェックマーク |
| `ImGuiCol_ScrollbarBg` / `ScrollbarGrab` | スクロールバー |
| `ImGuiCol_PlotLines` / `PlotHistogram` | グラフ |

ボタンなどは「通常・ホバー・押下」の 3 色をセットで決めると、操作感が良くなります。

## 一時的な変更（Push / Pop）

**一部の部品だけ**、色や大きさを変えるには`Push` で積み `Pop` で戻します。

```cpp
ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.7f, 0.2f, 0.2f, 1.0f));
ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.8f, 0.3f, 0.3f, 1.0f));
if (ImGui::Button("削除")) Delete();
ImGui::PopStyleColor(2);

ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 12.0f);
ImGui::Button("丸いボタン");
ImGui::PopStyleVar();
```

| 関数 | 説明 |
| --- | --- |
| `PushStyleColor(idx, color)` / `PopStyleColor(count)` | 色を一時的に変える |
| `PushStyleVar(idx, 値)` / `PopStyleVar(count)` | 大きさ・余白を一時的に変える |
| `PushFont(font)` / `PopFont()` | フォントを一時的に変える（[フォント](fonts.md)） |

!!! warning "Push と Pop の個数をそろえる"
    `Push` した数と `Pop` する数が合わないとassert で止まります（または、以降の見た目が壊れます）。`PopStyleColor(2)` のように数を渡して、まとめて戻せます。

### 無効な部品の見た目

```cpp
ImGui::BeginDisabled(!can_attack);
ImGui::Button("攻撃");
ImGui::EndDisabled();
```

`BeginDisabled(true)` で囲んだ部品が薄くなり操作できなくなります（`Push` で色を変えるより簡単）。

## 自作のテーマ

**よく使う設定を 1 つの関数にまとめる**と使い回せます。

```cpp
void ApplyMyTheme() {
  ImGui::StyleColorsDark();
  ImGuiStyle& style = ImGui::GetStyle();

  style.WindowRounding = 6.0f;
  style.FrameRounding = 4.0f;
  style.GrabRounding = 4.0f;
  style.ScrollbarRounding = 6.0f;
  style.WindowBorderSize = 0.0f;
  style.FrameBorderSize = 0.0f;
  style.WindowPadding = ImVec2(10, 10);
  style.FramePadding = ImVec2(8, 5);
  style.ItemSpacing = ImVec2(8, 6);

  ImVec4* c = style.Colors;
  c[ImGuiCol_WindowBg] = ImVec4(0.09f, 0.10f, 0.12f, 1.00f);
  c[ImGuiCol_FrameBg] = ImVec4(0.16f, 0.17f, 0.20f, 1.00f);
  c[ImGuiCol_Button] = ImVec4(0.20f, 0.45f, 0.75f, 1.00f);
  c[ImGuiCol_ButtonHovered] = ImVec4(0.28f, 0.55f, 0.85f, 1.00f);
  c[ImGuiCol_ButtonActive] = ImVec4(0.16f, 0.38f, 0.65f, 1.00f);
  c[ImGuiCol_Header] = ImVec4(0.20f, 0.45f, 0.75f, 0.55f);
}
```

### 色の調整のコツ

| コツ | 説明 |
| --- | --- |
| 基準の色を 1 つ決める | ボタン・ヘッダ・つまみなどをその色の明るさ違いにする |
| ホバーは少し明るく | 押下は、少し暗く |
| 文字と背景のコントラスト | 読めることが、最優先 |
| ImGui のスタイル エディタ | `ImGui::ShowStyleEditor()` を開くとリアルタイムで、全項目を調整できる |

```cpp
ImGui::ShowStyleEditor();
```

スタイル エディタで見た目を決めてから、数値をコードに写すのが一番簡単です。

### 保存と読み込み

| 方法 | 説明 |
| --- | --- |
| コードに書く | テーマ関数（上の例）。最もシンプル |
| JSON などのファイル | 色・大きさをファイルに保存して、起動時に読む。再ビルドなしで調整できる（[nlohmann/json](../serialization/nlohmann-json.md)） |
| `ShowStyleEditor` の「Export」 | 色の配列を C++ コードとして、出力できる |

## 高 DPI（ディスプレイの拡大率）への対応 {#dpi}

**高解像度のディスプレイ**ではImGui の部品が小さく見えます。

```cpp
float dpi_scale = GetDpiScaleForWindow(hwnd);

ImGuiStyle& style = ImGui::GetStyle();
style.ScaleAllSizes(dpi_scale);

io.Fonts->AddFontFromFileTTF("font.ttf", 16.0f * dpi_scale);
```

| 点 | 説明 |
| --- | --- |
| `style.ScaleAllSizes(scale)` | 余白・角丸・スクロールバーなどすべての大きさを `scale` 倍する |
| フォントも拡大して読み込む | `io.FontGlobalScale` で拡大すると、ぼやける。フォントの大きさを DPI に合わせて作る（[フォント](fonts.md)） |
| スケールは 1 回だけ | `ScaleAllSizes` を何度も呼ぶと掛け算が重なって、大きくなりすぎる |
| DPI の変化 | ウィンドウを別のモニターに動かしたとき、スタイルを元に戻して再度スケールする |

!!! note "スタイルを元に戻してから、スケールする"
    `ScaleAllSizes` は今の値に掛けるので、DPI が変わるたびに呼ぶと積み重なります。元のスタイルを保存しておきコピーして、スケールします。

```cpp
ImGuiStyle base_style;
ImGuiStyle& style = ImGui::GetStyle();
base_style = style;

void OnDpiChanged(float scale) {
  ImGui::GetStyle() = base_style;
  ImGui::GetStyle().ScaleAllSizes(scale);
}
```

## よくあるミス

??? failure "`Push` と `Pop` の数が合わず assert で止まる"
    **積んだ数だけ戻します**（`PopStyleColor(2)`）。

??? failure "`StyleColors...` を `Colors[...]` の変更の後に呼ぶ"
    標準テーマが変更を上書きします。テーマを選んでから個別に変更します。

??? failure "`ScaleAllSizes` を毎フレーム呼ぶ"
    大きさがどんどん大きくなります。1 回だけ。

??? failure "`io.FontGlobalScale` で拡大して、文字がぼやける"
    フォント自体を大きく読み込み直す（[フォント](fonts.md)）。

??? failure "背景が透けて見える（アルファ）"
    `ImGuiCol_WindowBg` の アルファ（4 つ目）が 1 未満です。

??? failure "色の値を 0〜255 で書いている"
    `ImVec4` は 0〜1 の `float` です。`IM_COL32` は 0〜255 の整数（`ImU32`）で、用途が別です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>標準テーマは `StyleColorsDark` / `Light` / `Classic`</strong>。最初に 1 回
    - [x] `ImGui::GetStyle()` で、色（`Colors[ImGuiCol_*]`）と大きさ（`WindowRounding` など）を変える
    - [x] 一時的な変更は `PushStyleColor` / `PushStyleVar`。個数をそろえて `Pop`
    - [x] `ShowStyleEditor()` で、見た目を調整して値をコードに写す
    - [x] 高 DPI は `ScaleAllSizes`（1 回だけ）＋ フォントを大きく

## 関連ページ

- [Dear ImGui](index.md)
- [日本語フォントとアイコン](fonts.md)
- [レイアウトとウィンドウ](layout.md)
- [ウィジェット一覧](widgets.md)
