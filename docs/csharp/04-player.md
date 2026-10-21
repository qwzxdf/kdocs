---
title: 第 4 章 Player：エンジンを動かす実行側
tags:
  - C#連携
---

# 第 4 章 Player：エンジンを動かす実行側

この章では `Player` プロジェクトに <strong>Win32 のウィンドウ</strong>を作り `Engine` を動かします。エディタ（C#）を作る前に <strong>エンジンだけで、動く物を 1 つ作っておく</strong>ことが目的です。後でエディタ側がうまく動かないときに「エンジンが悪いのか連携が悪いのか」を、切り分けられます。

## この章のゴール

- Player がウィンドウを開き `Engine::Create` で、エンジンを作る。
- メッセージ ループの中で `Engine::Tick` を毎フレーム呼ぶ。
- ウィンドウの大きさを変えると、`Engine::Resize` が呼ばれる。
- <strong>色がなめらかに変わるウィンドウ</strong>が、画面に出る。

## Player の役割

| 役割 | 内容 |
| --- | --- |
| ウィンドウを持つ | OS のウィンドウは、Player（実行側）が作る。Engine は `HWND` を受け取るだけ |
| ループを回す | 「入力 → 更新・描画 → 繰り返し」のループは、Player の `main` にある |
| 時間を測る | 前のフレームからの経過秒（delta）を測って、`Tick` に渡す |

<strong>Engine がウィンドウを作らない</strong>ことが、重要です。エディタでは WPF が作る子ウィンドウの `HWND` を同じ `Engine::Create` に渡します。Player はその<strong>最も単純な利用者</strong>です。

## 手順 1：プロジェクトの設定

`Player` プロジェクトのプロパティを次のように設定します（構成「すべての構成」、プラットフォーム「x64」）。

| 場所 | 項目 | 値 |
| --- | --- | --- |
| 全般 | C++ 言語標準 | ISO C++23 プレビュー（`/std:c++latest`） |
| リンカー → システム | サブシステム | <strong>Windows (/SUBSYSTEM:WINDOWS)</strong> |
| C/C++ → 全般 | 追加のインクルード ディレクトリ | 第 2 章で、設定済み（Engine の `include`） |
| ビルド依存 | プロジェクト参照 | Engine（第 2 章で設定済み） |

`/SUBSYSTEM:WINDOWS` にすると黒いコンソールが出ません。その代わり入口の関数が `main` ではなく <strong>`wWinMain`</strong> になります。

## 手順 2：ソースを書く

`Player\src\main.cpp` を作ります（プロジェクトを右クリック →「追加 → 新しい項目 → C++ ファイル」）。

### ウィンドウ プロシージャ

```cpp
#include <windows.h>

#include <chrono>

#include "Engine/Engine.h"
#include "Engine/Log.h"

namespace {

mini::Engine* g_engine = nullptr;   // ウィンドウ プロシージャから使うので、グローバルに置く

LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam) {
  switch (message) {
    case WM_SIZE:
      if (g_engine && wparam != SIZE_MINIMIZED) {
        g_engine->Resize(LOWORD(lparam), HIWORD(lparam));
      }
      return 0;
    case WM_DESTROY:
      PostQuitMessage(0);
      return 0;
  }
  return DefWindowProcW(hwnd, message, wparam, lparam);
}

}  // namespace
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `HWND` | ウィンドウの<strong>ハンドル</strong>（識別番号のような物）。ウィンドウに関する関数はすべて、これを受け取る |
| ウィンドウ プロシージャ | ウィンドウに届く<strong>メッセージ</strong>（大きさが変わった、閉じられたキーが押された…）を受け取る関数。OS が呼ぶ |
| `LRESULT CALLBACK` | 戻り値の型と呼び出し規約。`CALLBACK` は `__stdcall`。必ずこの形で書く |
| `WM_SIZE` | 大きさが変わったときのメッセージ。`lparam` の下位 16 ビットが幅、上位 16 ビットが高さ |
| `LOWORD` / `HIWORD` | 32 ビット値の下位 / 上位 16 ビットを取り出すマクロ |
| `SIZE_MINIMIZED` | 最小化されたことを示す値。このとき、幅・高さは 0 なので `Resize` を呼ばない |
| `WM_DESTROY` | ウィンドウが壊されるときのメッセージ |
| `PostQuitMessage(0)` | メッセージ ループに「終了せよ」のメッセージ（`WM_QUIT`）を積む |
| `DefWindowProcW` | 自分で処理しないメッセージを既定の動作に任せる。必ず最後に呼ぶ |
| 名前空間の無名 `namespace { }` | このファイルの中だけで、使う名前（外部に見せない） |

### ウィンドウの作成

```cpp
HWND CreateMainWindow(HINSTANCE instance, int width, int height) {
  WNDCLASSEXW wc = {};
  wc.cbSize = sizeof(wc);
  wc.style = CS_HREDRAW | CS_VREDRAW;
  wc.lpfnWndProc = WindowProc;
  wc.hInstance = instance;
  wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  wc.lpszClassName = L"MiniEnginePlayer";
  RegisterClassExW(&wc);

  // クライアント領域（描く部分）が width x height になるように、外枠の大きさを計算する。
  RECT rect = {0, 0, width, height};
  AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);

  return CreateWindowExW(0, wc.lpszClassName, L"MiniEngine Player", WS_OVERLAPPEDWINDOW, CW_USEDEFAULT,
                         CW_USEDEFAULT, rect.right - rect.left, rect.bottom - rect.top, nullptr, nullptr, instance,
                         nullptr);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `WNDCLASSEXW` | ウィンドウの「種類」（クラス）の設定。末尾の `W` は Unicode（UTF-16）版 |
| `wc.lpfnWndProc` | このクラスのウィンドウに届くメッセージを処理する関数 |
| `RegisterClassExW` | 上の設定を OS に登録する |
| `AdjustWindowRect` | 枠やタイトル バーを含めた外側の大きさを計算する（ウィンドウの大きさ ≠ 描ける領域） |
| `WS_OVERLAPPEDWINDOW` | 普通のウィンドウの見た目（タイトル バー、枠、最大化ボタンなど） |
| `CreateWindowExW` | ウィンドウを作る。戻り値が `HWND` |

!!! note "A と W"
    Windows API には、`〜A`（ANSI）と `〜W`（UTF-16）の 2 種類があります。**常に W を使います**（[文字コード](../encoding/index.md)）。

### 入口：wWinMain

```cpp
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
  const int kWidth = 1280;
  const int kHeight = 720;
  HWND hwnd = CreateMainWindow(instance, kWidth, kHeight);
  if (!hwnd) return 1;

  // エンジンの作成。クライアント領域の大きさを、取り直して渡す。
  RECT client;
  GetClientRect(hwnd, &client);
  mini::EngineDesc desc;
  desc.window = reinterpret_cast<mini::NativeWindow>(hwnd);
  desc.width = static_cast<std::uint32_t>(client.right - client.left);
  desc.height = static_cast<std::uint32_t>(client.bottom - client.top);
  g_engine = mini::Engine::Create(desc);
  if (!g_engine) {
    MessageBoxW(hwnd, L"Engine の作成に失敗しました。出力ウィンドウのログを確認してください。", L"MiniEngine", MB_ICONERROR);
    return 1;
  }

  ShowWindow(hwnd, show);

  // メッセージ ループ：メッセージがあれば処理し、無ければ 1 フレーム進める。
  auto previous = std::chrono::steady_clock::now();
  MSG msg = {};
  while (msg.message != WM_QUIT) {
    if (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {
      TranslateMessage(&msg);
      DispatchMessageW(&msg);
      continue;
    }
    const auto now = std::chrono::steady_clock::now();
    const float delta = std::chrono::duration<float>(now - previous).count();
    previous = now;
    g_engine->Tick(delta);
  }

  mini::Engine::Destroy(g_engine);
  g_engine = nullptr;
  return static_cast<int>(msg.wParam);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `wWinMain` | `/SUBSYSTEM:WINDOWS` の Unicode 版の入口。`instance` はこのプログラムの識別、`show` は最初の表示方法 |
| `GetClientRect` | 描ける領域（枠を除く）の大きさを取る |
| `PeekMessageW` | メッセージが<strong>あれば取り出し、無くても待たず</strong>に戻る（`GetMessage` は来るまで待つので、ゲーム ループには向かない） |
| `PM_REMOVE` | 取り出したらキューから消す |
| `TranslateMessage` / `DispatchMessageW` | キー入力の変換とウィンドウ プロシージャへの配送 |
| `WM_QUIT` | `PostQuitMessage` が積む終了メッセージ。これが来たらループを抜ける |
| `std::chrono::steady_clock` | 巻き戻らない時計。経過時間の測定に使う |
| `std::chrono::duration<float>` | 秒を `float` で持つ時間の型。`.count()` で数値を取る |

## 手順 3：動かす

1. ソリューション エクスプローラーで、Player を右クリック →「スタートアップ プロジェクトに設定」。
2. 構成を <strong>Debug / x64</strong> にして `F5`。

<strong>色がなめらかに変わる 1280×720 のウィンドウ</strong>が出れば成功です。ウィンドウの縁をドラッグして、大きさを変えても色が出続ければ `Resize` も動いています。

## 動作確認のチェック

| 見る所 | 期待する結果 |
| --- | --- |
| ウィンドウの色 | 赤・緑・青のなめらかな変化 |
| 大きさを変える | 変えている間も色が出る。クラッシュしない |
| 最小化 → 戻す | 戻したあと描画が再開する |
| 閉じる | プロセスが正常に終了する |
| 出力ウィンドウ | 「Engine を作成しました（1280x720）」「Engine を破棄します（N フレーム）」 |

## よくあるミス

??? failure "`LNK2019`：`WinMain` が見つからない／`main` が見つからない"
    サブシステムと入口の関数が合っていない。`/SUBSYSTEM:WINDOWS` なら `wWinMain`、`/SUBSYSTEM:CONSOLE` なら `main`。

??? failure "起動した瞬間に `Engine.dll` が見つからないと言われる"
    出力先がそろっていない。第 1 章の `Directory.Build.props` ですべてのプロジェクトが、同じ `bin\x64\Debug\` に出力されているか確認する。

??? failure "`Engine::Create` が `nullptr` になる"
    出力ウィンドウ（デバッグ出力）に理由が出ている。多くは GPU が DX12 に非対応、またはデバッグ レイヤー用の「Graphics Tools」が、入っていない（Windows の「オプション機能」から追加）。

??? failure "ウィンドウが、真っ黒のまま"
    `Tick` が呼ばれていない（ループの `continue` を忘れて、メッセージ処理で止まっている）。または、`Present` の前のバリアが逆になっている。

??? failure "大きさを変えると、クラッシュする"
    `Resize` でバック バッファへの参照が残っている。第 3 章の `Renderer::Resize` が `Reset` をすべて呼んでいるか確認する。

## この章で作ったもの

- `Engine`（C++ DLL）：DX12 で、ウィンドウを塗る。
- `Player`（C++ EXE）：ウィンドウを作り `Engine` を動かす。

ここまでが <strong>エンジン側の土台</strong>です。ここから先は同じ `Engine` を <strong>C# のエディタから動かす</strong>ことになります。

## 次の章へ

第 2 部では C# と WPF を学びます。まず、C++ を知っている人向けに C# の基本を対応表つきで説明します。

!!! note "続く章"
    第 5 章以降は順に追加されます。
