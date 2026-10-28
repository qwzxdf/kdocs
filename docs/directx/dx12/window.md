---
title: Win32 Window and Message Loop (D3D12)
tags:
  - DirectX
---

# Win32 Window and Message Loop (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 は画像を作る API です。ウィンドウは作りません。画面に絵を出すには先に Windows のウィンドウ（`HWND`）を作って、メッセージ ループを回す必要があります。このページはそのための最小のコードです。

SDL や GLFW のようなウィンドウ ライブラリを使うならこのページは読み飛ばして構いません。ライブラリから `HWND` を取り出す方法だけあとの節で示します。

!!! tip "ポイント"
    - D3D12 に渡すのは、ウィンドウ ハンドル `HWND` と描画領域（クライアント領域）の大きさ。
    - メッセージ ループは `PeekMessage` で書く。メッセージがないときにフレームを描く。`GetMessage` は待ってしまう。
    - ウィンドウ全体の大きさと描画領域の大きさは違う。`AdjustWindowRect` で枠のぶんを足す。
    - `WM_SIZE`（大きさの変更）と `WM_DESTROY`（閉じる）は、必ず処理する。
    - ウィンドウの大きさが変わったときは、GPU の完了を待ってからバック バッファを作り直す。

!!! info "このページを読む前に"
    Win32 の知識はほとんど要りません。ここで作った `HWND` を[Swap Chain](swap-chain.md) に渡し、[Drawing a Triangle](triangle.md) の `Renderer::Init(hwnd)` で使います。

## ウィンドウ クラスを登録する

```cpp
#include <windows.h>

LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam);

HWND CreateGameWindow(HINSTANCE instance, int width, int height) {
  WNDCLASSEXW wc = {};
  wc.cbSize = sizeof(wc);
  wc.style = CS_HREDRAW | CS_VREDRAW;
  wc.lpfnWndProc = WindowProc;  // メッセージを受け取る関数
  wc.hInstance = instance;
  wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
  wc.lpszClassName = L"GameWindowClass";
  RegisterClassExW(&wc);
```

ウィンドウはまず**クラス**（ウィンドウの型紙）を登録して、そのクラスから作ります。`lpfnWndProc` はこのウィンドウ宛てのメッセージ（閉じる大きさの変更、キー入力など）を受け取る関数です。

## 描画領域の大きさを指定する

```cpp
  // 指定した大きさは「描画領域」の大きさ。タイトル バーや枠のぶんを足して、ウィンドウ全体の大きさにする。
  RECT rect = {0, 0, width, height};
  const DWORD style = WS_OVERLAPPEDWINDOW;
  AdjustWindowRect(&rect, style, FALSE);

  return CreateWindowExW(0, wc.lpszClassName, L"Game", style, CW_USEDEFAULT, CW_USEDEFAULT,
                         rect.right - rect.left, rect.bottom - rect.top,
                         nullptr, nullptr, instance, nullptr);
}
```

`CreateWindowExW` の幅と高さは枠を含んだウィンドウ全体の大きさです。1280×720 の描画領域が欲しいときにそのまま 1280×720 を渡すと、枠のぶんだけ描画領域が小さくなります。`AdjustWindowRect` が枠のぶんを足した大きさを計算してくれます。

## ウィンドウ プロシージャ

```cpp
LRESULT CALLBACK WindowProc(HWND hwnd, UINT message, WPARAM wparam, LPARAM lparam) {
  switch (message) {
    case WM_SIZE:
      // 大きさが変わった。最小化（SIZE_MINIMIZED）のときは何もしない。
      // lparam の下位 16 ビットが幅、上位 16 ビットが高さ。
      if (wparam != SIZE_MINIMIZED) {
        OnResize(LOWORD(lparam), HIWORD(lparam));  // バック バッファの作り直し（Swap Chain のページ）
      }
      return 0;
    case WM_DESTROY:
      PostQuitMessage(0);  // メッセージ ループを終わらせる
      return 0;
  }
  return DefWindowProcW(hwnd, message, wparam, lparam);  // それ以外は既定の処理に任せる
}
```

`WM_SIZE` ではバック バッファと深度バッファを作り直します。D3D12 では GPU がバッファを使っている間は作り直せないので、先に GPU の完了を待ちます（[Swap Chain](swap-chain.md#ウィンドウの大きさを変える)）。`WM_DESTROY` で `PostQuitMessage` を呼ぶとメッセージ ループに `WM_QUIT` が届いて、ループが終わります。処理しないメッセージは必ず `DefWindowProcW` に渡します。

## メッセージ ループ

```cpp
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int show) {
  HWND hwnd = CreateGameWindow(instance, 1280, 720);
  ShowWindow(hwnd, show);

  // ここで D3D12 を初期化する（Device and Factory のページ）

  MSG msg = {};
  while (msg.message != WM_QUIT) {
    if (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) {  // メッセージがあれば処理する
      TranslateMessage(&msg);
      DispatchMessageW(&msg);  // WindowProc が呼ばれる
    } else {
      UpdateGame();  // メッセージがなければ、1 フレーム進める
      RenderFrame();
    }
  }
  return static_cast<int>(msg.wParam);
}
```

`GetMessage` はメッセージが来るまで待つので、ゲームのループには使えません。`PeekMessage` はなければすぐ戻るのでメッセージがない間にゲームの更新と描画を回せます。フレームの速さは `Present` の垂直同期で決まります（[Swap Chain](swap-chain.md#present)）。

## クライアント領域の大きさを取り出す

```cpp
RECT client;
GetClientRect(hwnd, &client);  // 描画領域の大きさ。左上は (0, 0)
const UINT width = client.right - client.left;
const UINT height = client.bottom - client.top;
```

スワップ チェーンやビューポートの大きさには、ウィンドウ全体ではなくクライアント領域の大きさを使います。

## ウィンドウ ライブラリを使うとき

SDL の場合は `SDL_GetPointerProperty(SDL_GetWindowProperties(window), SDL_PROP_WINDOW_WIN32_HWND_POINTER, nullptr)` で `HWND` を取り出します。GLFW の場合は `GLFW_EXPOSE_NATIVE_WIN32` を定義して、`glfwGetWin32Window(window)` を呼びます。どちらも、`HWND` さえ取り出せれば以降の D3D12 のコードは同じです。

## よくあるミス

??? failure "描画領域が指定した大きさより小さい"
    `AdjustWindowRect` を通していません。ウィンドウ全体の大きさと描画領域の大きさを混同しています。

??? failure "ウィンドウを閉じても、プロセスが残る"
    `WM_DESTROY` で `PostQuitMessage` を呼んでいないかループの条件が `WM_QUIT` を見ていません。

??? failure "最小化すると `ResizeBuffers` が失敗する"
    最小化のとき `WM_SIZE` の幅と高さが 0 になります。`SIZE_MINIMIZED` のときは作り直しません。

??? failure "メッセージ ループが固まる"
    `GetMessage` で待っています。ゲームのループは `PeekMessage` で書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 の前に Win32 のウィンドウ（`HWND`）が要る
    - [x] クラスの登録、`AdjustWindowRect`、`CreateWindowExW`、`ShowWindow` の順に進む
    - [x] ループは `PeekMessage`。メッセージがなければ 1 フレーム描く
    - [x] `WM_SIZE` でバック バッファを作り直す。最小化のときは除く
    - [x] 大きさはクライアント領域（`GetClientRect`）で決める

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: ウィンドウの作成](https://learn.microsoft.com/ja-jp/windows/win32/learnwin32/creating-a-window)
