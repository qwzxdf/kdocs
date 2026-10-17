---
title: 早見表：ウィジェット
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：ウィジェット

<strong>画面に出る部品（ウィジェット）</strong>の関数を**種類ごと**に並べます。**戻り値が `bool` のものは、「操作された」ことを表します**。**値を編集する関数は、変数のポインタ**を渡します。

!!! tip "ポイント"
    - <strong>編集系（`Slider`・`Drag`・`Input`・`Checkbox`・`Combo`・`ColorEdit`）は、変数のポインタを受け取る</strong>。<strong>戻り値は「変わった瞬間だけ true」</strong>。
    - <strong>表示系（`Text`・`Image`・`ProgressBar`・`PlotLines`）は、値を見せるだけ</strong>。
    - <strong>ラベルは ID を兼ねる</strong>。<strong>`"名前##id"`</strong> で見た目と ID を分けられる。

## テキスト

| 関数 | 出るもの | 戻り値 | メモ |
| --- | --- | --- | --- |
| `Text(fmt, ...)` | **書式付きテキスト**（printf 形式） | `void` | **最もよく使う** |
| `TextUnformatted(text, end)` | **書式を解釈しない、生のテキスト** | `void` | **長い文字列・`%` を含むとき**。**速い** |
| `TextColored(col, fmt, ...)` | **色付きテキスト** | `void` | `col` は `ImVec4(r,g,b,a)` |
| `TextDisabled(fmt, ...)` | **灰色の（無効な）テキスト** | `void` | 補足説明に |
| `TextWrapped(fmt, ...)` | **折り返すテキスト** | `void` | ウィンドウ幅で折り返し |
| `LabelText(label, fmt, ...)` | <strong>「値  ラベル」の並び</strong>（入力欄風・編集不可） | `void` | 読み取り専用の値の表示 |
| `BulletText(fmt, ...)` | <strong>「・」付きテキスト</strong> | `void` | 箇条書き |
| `SeparatorText(label)` | **ラベル付きの区切り線** | `void` | 1.89 以降 |
| `TextLink(label)` / `TextLinkOpenURL(label, url)` | **リンク風のテキスト** | `bool` / `bool` | 1.91 以降 |
| `Bullet()` | <strong>「・」だけ</strong> | `void` | 後ろに別の部品を続ける |

```cpp
ImGui::Text("HP: %d / %d", hp, max_hp);
ImGui::TextColored(ImVec4(1.0f, 0.4f, 0.4f, 1.0f), "Warning");
ImGui::TextWrapped("%s", long_message.c_str());
```

## ボタン・選択

| 関数 | 出るもの | 戻り値 | メモ |
| --- | --- | --- | --- |
| `Button(label, size)` | **押しボタン** | **押された瞬間 true** | `size` 省略で文字に合わせる |
| `SmallButton(label)` | **小さなボタン**（行の高さに合わせる） | 押された | 文章の途中に置ける |
| `InvisibleButton(id, size)` | **見えないボタン**（領域だけ） | 押された | **独自描画の当たり判定** |
| `ArrowButton(id, dir)` | **矢印ボタン** | 押された | `ImGuiDir_Left/Right/Up/Down` |
| `Checkbox(label, &b)` | **チェックボックス** | **変わった** | `b` は `bool` |
| `CheckboxFlags(label, &flags, bit)` | **フラグ 1 ビットのチェック** | 変わった | ビット フラグの編集 |
| `RadioButton(label, active)` | **ラジオ ボタン**（1 個） | 押された | `active` が「選択中か」 |
| `RadioButton(label, &v, v_button)` | **ラジオ ボタン**（`int` で管理） | 押された | 選ぶと `v` に番号を書く |
| `Selectable(label, selected, flags, size)` | **選択できる行** | 押された | リスト・インスペクターに |
| `Selectable(label, &selected)` | 同上（`bool` を直接編集） | 変わった | |
| `ColorButton(id, col, flags, size)` | **色の見本ボタン** | 押された | |
| `ImageButton(id, tex, size)` | **画像のボタン** | 押された | 1.89 以降は `id` が必要 |

```cpp
if (ImGui::Button("Save")) Save();
ImGui::Checkbox("Show", &show);
ImGui::RadioButton("Easy", &level, 0);
ImGui::SameLine();
ImGui::RadioButton("Hard", &level, 1);
```

## 数値の編集：スライダー

**範囲が決まっている値**（音量 0〜1 など）に使います。**つまみをドラッグ**して編集します。

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `SliderFloat(label, &f, min, max, fmt, flags)` | **float のスライダー** | `fmt` で表示形式（`"%.2f"`） |
| `SliderFloat2/3/4(label, f[N], min, max)` | **float 2〜4 個**を並べたスライダー | 位置・色など |
| `SliderInt(label, &i, min, max)` | **int のスライダー** | |
| `SliderInt2/3/4(label, i[N], min, max)` | **int 2〜4 個** | |
| `SliderAngle(label, &rad, min_deg, max_deg)` | **角度**（内部はラジアン、表示は度） | **回転の編集** |
| `SliderScalar(label, type, p, min, max)` | **任意の型**（`ImGuiDataType_`） | `uint8_t`・`double` など |
| `SliderScalarN(label, type, p, n, min, max)` | **任意の型を N 個** | |
| `VSliderFloat(label, size, &f, min, max)` | **縦のスライダー** | ミキサーのフェーダー |
| `VSliderInt(label, size, &i, min, max)` | <strong>縦のスライダー（int）</strong> | |

```cpp
ImGui::SliderFloat("Volume", &volume, 0.0f, 1.0f);
ImGui::SliderFloat3("Position", &pos.x, -10.0f, 10.0f);
ImGui::SliderAngle("Rotation", &yaw);
```

**Ctrl＋クリックで数値を直接入力**できます。**`ImGuiSliderFlags_AlwaysClamp`** を付けないと、**直接入力した値は範囲外にもなれます**。

## 数値の編集：ドラッグ

**範囲が決まっていない値**や、**細かく調整したい値**に使います。**左右にドラッグ**して**少しずつ変える**部品です。

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `DragFloat(label, &f, speed, min, max, fmt)` | **float のドラッグ入力** | `speed`：1 ピクセルあたりの変化量 |
| `DragFloat2/3/4(label, f[N], speed, min, max)` | **float 2〜4 個** | **位置・スケールの編集の定番** |
| `DragFloatRange2(label, &lo, &hi, speed, min, max)` | <strong>範囲（最小〜最大）</strong> | |
| `DragInt(label, &i, speed, min, max)` | **int のドラッグ入力** | |
| `DragInt2/3/4(label, i[N], ...)` | **int 2〜4 個** | |
| `DragIntRange2(label, &lo, &hi, ...)` | **int の範囲** | |
| `DragScalar(label, type, p, speed, min, max)` | **任意の型** | |
| `DragScalarN(label, type, p, n, speed, min, max)` | **任意の型を N 個** | |

```cpp
ImGui::DragFloat3("Position", &pos.x, 0.05f);
ImGui::DragFloat("Speed", &speed, 0.1f, 0.0f, 100.0f);
ImGui::DragIntRange2("Level", &lo, &hi, 1.0f, 1, 99);
```

| 比べ方 | スライダー | ドラッグ |
| --- | --- | --- |
| **範囲** | **必須** | 省略可（無制限） |
| **用途** | 音量・割合・明るさ | 位置・スケール・パラメータ |
| **見た目** | つまみが動く | 数字だけ（左右にドラッグ） |

## 数値の編集：入力欄

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `InputFloat(label, &f, step, step_fast, fmt)` | **float の入力欄**（`+` `−` ボタン付き） | `step` が 0 でボタンなし |
| `InputFloat2/3/4(label, f[N])` | **float 2〜4 個** | |
| `InputInt(label, &i, step, step_fast)` | **int の入力欄** | |
| `InputInt2/3/4(label, i[N])` | **int 2〜4 個** | |
| `InputDouble(label, &d, step, step_fast, fmt)` | **double** | |
| `InputScalar(label, type, p, step, step_fast)` | **任意の型** | |
| `InputScalarN(label, type, p, n)` | **任意の型を N 個** | |

## 文字の入力

| 関数 | 出るもの | 戻り値 | メモ |
| --- | --- | --- | --- |
| `InputText(label, buf, size, flags)` | **1 行の文字入力** | 変わった | `buf`：`char` 配列 |
| `InputTextMultiline(label, buf, size, ImVec2, flags)` | **複数行の文字入力** | 変わった | |
| `InputTextWithHint(label, hint, buf, size, flags)` | **未入力のとき薄く出るヒント付き** | 変わった | 検索欄 |
| `InputText(label, std::string*, flags)` | **`std::string` を直接編集** | 変わった | `imgui_stdlib.h` が必要 |

```cpp
char name[64] = "Player";
ImGui::InputText("Name", name, sizeof(name));
ImGui::InputTextWithHint("##search", "Search...", filter, sizeof(filter));
```

## コンボ・リスト

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `Combo(label, &index, items, count)` | **ドロップダウン**（配列から選ぶ） | 変わった | 不要 |
| `Combo(label, &index, "A\0B\0C\0")` | **ドロップダウン**（`\0` 区切りの文字列） | 変わった | 不要 |
| `Combo(label, &index, getter, data, count)` | **コールバックで項目を生成** | 変わった | 不要 |
| `BeginCombo(label, preview)` | **自分で中身を作るドロップダウン** | 開いている | **true のとき `EndCombo()`** |
| `ListBox(label, &index, items, count, height)` | **常に開いた一覧**（スクロール） | 変わった | 不要 |
| `BeginListBox(label, size)` | **自分で中身を作る一覧** | 開いている | **true のとき `EndListBox()`** |

```cpp
const char* items[] = {"Easy", "Normal", "Hard"};
ImGui::Combo("Level", &level, items, IM_ARRAYSIZE(items));

if (ImGui::BeginCombo("Item", names[current].c_str())) {
  for (int i = 0; i < count; ++i) {
    bool selected = (i == current);
    if (ImGui::Selectable(names[i].c_str(), selected)) current = i;
    if (selected) ImGui::SetItemDefaultFocus();
  }
  ImGui::EndCombo();
}
```

## 色

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `ColorEdit3(label, col[3], flags)` | <strong>色の編集（RGB）</strong>：見本 ＋ 数値 | クリックで**ピッカー** |
| `ColorEdit4(label, col[4], flags)` | <strong>色の編集（RGBA）</strong> | |
| `ColorPicker3(label, col[3], flags)` | <strong>大きな色の選択パネル（RGB）</strong> | **色相リング／四角** |
| `ColorPicker4(label, col[4], flags, ref_col)` | <strong>色の選択パネル（RGBA）</strong> | |
| `ColorButton(id, col, flags, size)` | **色の見本** | |
| `SetColorEditOptions(flags)` | **色編集の表示方式を全体で設定** | **HSV 表示など** |

```cpp
float color[4] = {1.0f, 0.5f, 0.2f, 1.0f};
ImGui::ColorEdit4("Tint", color, ImGuiColorEditFlags_AlphaBar);
```

## 進捗・プロット

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `ProgressBar(fraction, size, overlay)` | **進捗バー**（0〜1） | `overlay` で中の文字（`"62%"`） |
| `PlotLines(label, values, count, offset, overlay, min, max, size)` | **折れ線グラフ** | **フレーム時間** |
| `PlotLines(label, getter, data, count, ...)` | **コールバックで値を取る折れ線** | |
| `PlotHistogram(label, values, count, ...)` | **棒グラフ** | |

```cpp
ImGui::ProgressBar(loaded / total, ImVec2(-1, 0));
ImGui::PlotLines("Frame ms", frame_times, 120, offset, nullptr, 0.0f, 33.0f, ImVec2(0, 60));
```

**本格的なグラフは、ImGui 本体ではなく、別ライブラリ ImPlot**を使います。

## 画像

| 関数 | 出るもの | 備考 |
| --- | --- | --- |
| `Image(tex, size, uv0, uv1, tint, border)` | **画像** | `tex`：`ImTextureID`（DX11 は SRV） |
| `ImageButton(id, tex, size, uv0, uv1, bg, tint)` | **画像のボタン** | |

詳しくは[テクスチャと画像](../textures.md)を参照してください。

## まとめ：どの関数を選ぶか

| やりたいこと | 使う関数 |
| --- | --- |
| **文字を表示** | `Text` |
| **実行する** | `Button` |
| **ON / OFF** | `Checkbox` |
| **選択肢から 1 つ** | `Combo`（多いとき）・`RadioButton`（少ないとき） |
| **0〜1 の割合** | `SliderFloat` |
| **位置・スケール** | `DragFloat3` |
| **名前の入力** | `InputText` |
| **色** | `ColorEdit3 / 4` |
| **進捗** | `ProgressBar` |
| **グラフ** | `PlotLines` |

## 関連ページ

- [関数早見表](index.md)
- [コンテナ](containers.md)
- [ウィジェット一覧（解説）](../widgets.md)
