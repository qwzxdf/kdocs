---
title: Win32 Window and Message Loop
tags:
  - DirectX
---

# Win32 Window and Message Loop

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D11 は画像を作る API で、ウィンドウは作りません。画面に出すにはまず <strong>Win32 のウィンドウ</strong>（`HWND`）を作り、<strong>メッセージ ループ</strong>を回します。このページはそのための最小のコードです。

!!! tip "ポイント"
    - D3D11 に渡すのは、ウィンドウ ハンドル `HWND` と、描画領域（クライアント領域）の大きさ。
    - メッセージ ループは `PeekMessage` で、メッセージが無いときにフレームを描く（`GetMessage` は、待ってしまう）。
    - ウィンドウの大きさと、描画領域の大きさは違う。`AdjustWindowRect` で枠ぶんを足す。
    - `WM_SIZE`（大きさの変更）、`WM_DESTROY`（閉じる）は必ず処理する。
    - ウィンドウ ライブラリ（SDL、GLFW）を使うならこのページは、飛ばしてよい。`HWND` の取り出し方だけ見る。

## ウィンドウ クラスの登録

```cpp
#include <windows.h>

LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam);

HWND CreateGameWindow(HINSTANCE instance, int width, int height) {
  WNDCLASSEXW wc = {};
  wc.cbSize = sizeof(wc);
  wc.style = CS_HREDRAW | CS_VREDRAW;
  wc.lpfnWndProc = WindowProc;                         // メッセージを受け取る関数
  wc.hInstance = instance;
  wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  wc.lpszClassName = L"GameWindowClass";
  RegisterClassExW(&wc);
```

ウィンドウはまず <strong>クラス</strong>（ウィンドウの、型紙）を登録してそのクラスから、作ります。`lpfnWndProc` がこのウィンドウ宛てのメッセージ（閉じる、大きさ変更、キー入力など）を受け取る関数です。

## 描画領域の大きさを指定する

```cpp
  // 指定した大きさは「描画領域」の大きさ。タイトル バーや枠のぶんを、足して、ウィンドウ全体の大きさにする。
  RECT rect = {0, 0, width, height};
  const DWORD style = WS_OVERLAPPEDWINDOW;
  AdjustWindowRect(&rect, style, FALSE);

  return CreateWindowExW(0, wc.lpszClassName, L"Game", style, CW_USEDEFAULT, CW_USEDEFAULT,
                         rect.right - rect.left, rect.bottom - rect.top,
                         nullptr, nullptr, instance, nullptr);
}
```

`CreateWindowExW` の幅と高さは枠を含むウィンドウ全体の大きさです。1280×720 の描画領域が欲しいときに、そのまま 1280×720 を渡すと、枠のぶん描画領域が小さくなります。`AdjustWindowRect` が枠のぶんを足した大きさを、計算してくれます。

## ウィンドウ プロシージャ

```cpp
LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam) {
  switch (message) {
    case WM_SIZE:
      // 大きさが変わった。最小化（SIZE_MINIMIZED）のときは、何もしない。
      // lparam の下位 16 ビットが幅、上位 16 ビットが高さ。
      if (wparam != SIZE_MINIMIZED) {
        OnResize(LOWORD(lparam), HIWORD(lparam));            // バック バッファの作り直し（resize.md）
      }
      return 0;
    case WM_DESTROY:
      PostQuitMessage(0);                                    // メッセージ ループを、終わらせる
      return 0;
  }
  return DefWindowProcW(hwnd, message, wparam, lparam);      // それ以外は、既定の処理に任せる
}
```

`WM_SIZE` でバック バッファを作り直します（[Window Resize and Device Removal](resize.md)）。`WM_DESTROY` で `PostQuitMessage` を呼ぶとメッセージ ループに、`WM_QUIT` が届き終了します。処理しないメッセージは `DefWindowProcW` に必ず、渡します。

## メッセージ ループ

```cpp
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
  HWND hwnd = CreateGameWindow(instance, 1280, 720);
  ShowWindow(hwnd, show);

  // ここで D3D11 を初期化する（device.md、swap-chain.md）

  MSG msg = {};
  while (msg.message != WM_QUIT) {
    if (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {      // メッセージがあれば、処理する
      TranslateMessage(&msg);
      DispatchMessageW(&msg);                                // WindowProc が呼ばれる
    } else {
      UpdateGame();                                          // メッセージが無ければ、1 フレーム進める
      RenderFrame();
    }
  }
  return static_cast<int>(msg.wParam);
}
```

`GetMessage` はメッセージが来るまで待つので、ゲームのループには使えません。`PeekMessage` は無ければすぐ戻るのでメッセージが無い間に、ゲームの更新と描画を回せます。フレームの速さは `Present` の垂直同期（[Clear and Present](clear-present.md)）で、決まります。

## クライアント領域の大きさを、取り出す

```cpp
RECT client;
GetClientRect(hwnd, &client);                                // 描画領域の大きさ。左上は (0, 0)
const UINT width = client.right - client.left;
const UINT height = client.bottom - client.top;
```

スワップ チェーンやビューポートの、大きさには <strong>ウィンドウ全体ではなく、クライアント領域</strong>の大きさを、使います（[Swap Chain](swap-chain.md)）。

## ウィンドウ ライブラリを使うとき

| ライブラリ | `HWND` の取り出し |
| --- | --- |
| SDL | `SDL_GetPointerProperty(SDL_GetWindowProperties(window), SDL_PROP_WINDOW_WIN32_HWND_POINTER, nullptr)` |
| GLFW | `glfwGetWin32Window(window)`（`#define GLFW_EXPOSE_NATIVE_WIN32`） |

どちらも、`HWND` さえ取り出せれば以降の D3D11 のコードは、同じです。

## よくあるミス

??? failure "描画領域が、指定した大きさより小さい"
    `AdjustWindowRect` を通していない。ウィンドウ全体の大きさと描画領域の大きさを、混同している。

??? failure "ウィンドウを閉じても、プロセスが残る"
    `WM_DESTROY` で `PostQuitMessage` を呼んでいない。または、ループの条件が `WM_QUIT` を見ていない。

??? failure "最小化すると `ResizeBuffers` が、失敗する"
    最小化のとき `WM_SIZE` の幅と高さが 0 になる。`SIZE_MINIMIZED` のときは作り直さない。

??? failure "メッセージ ループが、固まる"
    `GetMessage` で待っている。ゲームのループは `PeekMessage` で書く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D11 の前に、Win32 のウィンドウ（`HWND`）が要る
    - [x] クラス登録 → `AdjustWindowRect` → `CreateWindowExW` → `ShowWindow`
    - [x] ループは `PeekMessage`。無ければ 1 フレーム描く
    - [x] `WM_SIZE` でバック バッファを作り直す。最小化は除く
    - [x] 大きさは、クライアント領域（`GetClientRect`）で決める

## 関連ページ

- [DirectX 11 Guide](index.md)
- [ID3D11Device and Device Context](device.md)
- [Swap Chain](swap-chain.md)
- [Window Resize and Device Removal](resize.md)
- [Microsoft Learn: Win32 ウィンドウの作成](https://learn.microsoft.com/ja-jp/windows/win32/learnwin32/creating-a-window)
