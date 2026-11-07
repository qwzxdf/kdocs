# Visual Studio の画像（docs/vs/img）の撮り方

画像は、すべて PNG の実寸。**1 回まとめて撮り、あとは撮り直さない。** 枠（赤い四角と丸数字）だけを直したいときは、`vs_mark.py` の `JOBS` を直して再実行する（原画は `tools/vs_raw`）。

## 手順

1. 撮影用のプロジェクトを `C:\vsshots` に作る（`Game`、`ErrC1083`、`ErrLnk`、`CMakeGame`。中身はこのファイルの下を参照）
2. `python tools/vs_shoot.py props menus dialogs includes debug errors misc extra cmake` で撮る（段階ごとに指定できる）
3. `python tools/vs_mark.py` で、切り出しと枠を付ける
4. 撮った所は、ユーザーが普段使う Visual Studio ではなく、実験的なインスタンス（`devenv /RootSuffix Exp`）。ユーザーの Visual Studio には触れない
5. 撮り終えたら `C:\vsshots` を消す

## 段階と画像

- props: props-general / debug / vcdirs / cpp-general / language / preprocessor / cmdline / linker-general / linker-input / linker-system / cpp-general-asan / config-dropdown
- menus: file-new-menu / file-open-menu / tools-menu / project-menu / build-menu / debug-menu / extensions-menu / view-other-windows
- dialogs: new-project / add-new-item / options-all / property-manager
- includes: props-cpp-standard / include-edit-menu / include-edit-dialog / include-macros
- debug: debug-break / debug-toolbar / debug-step / output-window / profiler-start（first-break、first-toolbar、debug-autos、debug-callstack は vs_mark.py が切り出す）
- errors: error-list-c1083 / error-list-lnk2019
- misc: options-text-editor / extensions-tabs
- extra: props-toolset-dropdown / config-manager
- cmake: cmake-folder / cmake-build-menu / cmake-build-output（cmake-preset-dropdown は vs_mark.py が切り出す）

撮っていない画像: `installer-workloads.jpg`、`installer-cpp-details.jpg`（Visual Studio Installer の画面。自動で撮れず、古い JPEG のまま）。

## テスト プロジェクト

- `Game`: `main.cpp` に `Enemy` と `std::vector` のコード（13 行目の `for` にブレークポイント）。v145、`/std:c++latest`、`/utf-8`
- `ErrC1083`: `#include "enemy.h"` だけ
- `ErrLnk`: 定義のない `Update()` を呼ぶ
- `CMakeGame`: `CMakeLists.txt`、`CMakePresets.json`（x64-debug / x64-release）、`main.cpp`
