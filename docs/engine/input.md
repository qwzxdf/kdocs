---
title: 入力（キーボード・マウス・ゲームパッド）
tags:
  - ゲームエンジン
---

# 入力（キーボード・マウス・ゲームパッド）

「スペースキーでジャンプ」は、`WM_KEYDOWN` が来たら `Jump()` を呼ぶ、と書くと動きます。ところが、そのまま作ると、すぐに困ります。キーを押しっぱなしにすると、`Jump()` が連続で呼ばれる。ゲームパッドのスティックを倒したままでも動いてほしい。マウスで視点を回すとき、画面の端に行くと回せなくなる。ゲームループの途中でキーが押された瞬間に、更新の順番が崩れる。

ゲームの入力は、<strong>「このフレームの間に、ボタンがどうなっているか」を、毎フレーム 1 回、まとめて取得して保存する</strong>形にすると、扱いやすくなります。ここでは、そのしくみと、キーボード・マウス・ゲームパッドそれぞれの取り方を説明します。

!!! tip "ポイント"
    - 入力は毎フレームの先頭で 1 回だけ取り、そのフレームの間は固定して使う。途中で変わらない
    - ボタンの状態は、「押された瞬間」「押している間」「離された瞬間」の 3 つで持つ
    - ゲームの処理は、キーの名前（スペース）ではなく、アクションの名前（ジャンプ）で書く
    - ゲームパッドは XInput が手軽。スティックにはデッドゾーンが要る
    - マウスで視点を回すなら、Raw Input で移動量を直接取る

!!! info "このページを読む前に"
    - [ゲームループと固定タイムステップ](game-loop.md)（入力 → 更新 → 描画 の順）

## 押された瞬間と、押している間 {#state}

ボタンは、現在の状態（押されているか）だけを持つと、「押された瞬間」が分かりません。ジャンプは押した瞬間の 1 回だけ、歩きは押している間ずっと、と使い分けるので、1 フレーム前の状態も持ちます。

```cpp
#include <array>

// ボタン 1 つ分の状態。毎フレーム Update で更新する
struct Button {
  bool current = false;   // 今のフレームで押されているか
  bool previous = false;  // 前のフレームで押されていたか

  void Update(bool pressed) {
    previous = current;
    current = pressed;
  }

  bool IsHeld() const { return current; }                  // 押している間
  bool WasPressed() const { return current && !previous; } // 押された瞬間（1 フレームだけ true）
  bool WasReleased() const { return !current && previous; }// 離された瞬間（1 フレームだけ true）
};
```

`Update` を毎フレーム 1 回呼ぶと、`current` と `previous` が入れ替わります。押した最初のフレームだけ、`current` が `true` で `previous` が `false` になるので、`WasPressed` が 1 フレームだけ `true` を返します。

## キーボード {#keyboard}

Win32 のキー入力は、メッセージで受け取る方法と、状態を取りにいく方法があります。

メッセージ（`WM_KEYDOWN` / `WM_KEYUP`）は、イベントとして、すべての入力を取りこぼしません。ウィンドウ プロシージャの中で、キー状態の表に反映します。

```cpp
#include <windows.h>

#include <array>

// 全キーの現在の状態。ウィンドウ プロシージャが書き、フレームの先頭で読む
std::array<bool, 256> g_key_down{};

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam) {
  switch (msg) {
    case WM_KEYDOWN:
      g_key_down[wparam & 0xFF] = true;   // wparam が仮想キー コード（VK_SPACE など）
      return 0;
    case WM_KEYUP:
      g_key_down[wparam & 0xFF] = false;
      return 0;
    case WM_KILLFOCUS:
      g_key_down.fill(false);             // ウィンドウが非アクティブになったら全部離す
      return 0;
  }
  return DefWindowProc(hwnd, msg, wparam, lparam);
}
```

`wparam` は仮想キー コードで、スペースは `VK_SPACE`、文字キーは大文字の ASCII（`'W'` など）です。`WM_KILLFOCUS` で全部のキーを離しておかないと、Alt+Tab で別のウィンドウに移ったときに、キーが押されたままになるバグが出ます。

もう 1 つの方法は、毎フレーム `GetAsyncKeyState(VK_SPACE) & 0x8000` で状態を取りにいくことです。コードが短いのですが、ウィンドウが非アクティブでも反応する点に注意が要ります。ゲームのメインでは、メッセージ方式のほうが安全です。

文字入力（名前の入力など）は、`WM_CHAR` を使います。キー コードでは、シフトや日本語入力の状態が分かりません。

## マウス {#mouse}

カーソルの位置は `WM_MOUSEMOVE` で来ます。メニューの操作には、これで足ります。

3D ゲームで視点を回すときは、事情が違います。カーソルの位置は、画面の端で止まるため、それ以上回せなくなります。必要なのは位置ではなく<strong>動いた量</strong>なので、Raw Input を使います。

```cpp
// 起動時に 1 回、マウスの Raw Input を登録する
RAWINPUTDEVICE rid = {};
rid.usUsagePage = 0x01;  // 汎用デスクトップ
rid.usUsage = 0x02;      // マウス
rid.hwndTarget = hwnd;
RegisterRawInputDevices(&rid, 1, sizeof(rid));

// ウィンドウ プロシージャで WM_INPUT を受ける
case WM_INPUT: {
  RAWINPUT raw = {};
  UINT size = sizeof(raw);
  GetRawInputData(reinterpret_cast<HRAWINPUT>(lparam), RID_INPUT, &raw, &size,
                  sizeof(RAWINPUTHEADER));
  if (raw.header.dwType == RIM_TYPEMOUSE) {
    g_mouse_dx += raw.data.mouse.lLastX;  // 前回からの移動量（ピクセル相当）
    g_mouse_dy += raw.data.mouse.lLastY;
  }
  return 0;
}
```

`lLastX` と `lLastY` は、前回からの移動量です。1 フレームの間に複数回届くので、`+=` で足し、フレームの先頭で読んだら 0 に戻します。

視点を回している間は、`ShowCursor(FALSE)` でカーソルを隠し、`ClipCursor` でウィンドウの中に閉じ込めると、外にはみ出しません。メニューを開くときは解除します。

## ゲームパッド（XInput） {#gamepad}

Xbox コントローラー互換のゲームパッドは、XInput が手軽です。毎フレーム `XInputGetState` を呼ぶだけです。

```cpp
#include <windows.h>
#include <xinput.h>

#pragma comment(lib, "xinput.lib")

// コントローラー 0 番の状態を取る。つながっていなければ false
bool ReadPad(float* lx, float* ly, bool* a_button) {
  XINPUT_STATE state = {};
  if (XInputGetState(0, &state) != ERROR_SUCCESS) return false;

  const XINPUT_GAMEPAD& pad = state.Gamepad;
  *lx = pad.sThumbLX / 32768.0f;  // -1.0 〜 +1.0 に正規化する
  *ly = pad.sThumbLY / 32768.0f;
  *a_button = (pad.wButtons & XINPUT_GAMEPAD_A) != 0;
  return true;
}
```

`XInputGetState` の第 1 引数は、コントローラーの番号（0〜3）です。つながっていないと `ERROR_DEVICE_NOT_CONNECTED` が返ります。毎フレーム、接続の有無を確認します。

スティックの値は、`-32768` 〜 `32767` の整数です。32768 で割って、`-1` 〜 `1` に直します。

### デッドゾーン {#deadzone}

スティックは、手を離しても、ぴったり 0 に戻りません。わずかに値が残るので、キャラクターがゆっくり勝手に動きます。そこで、一定の範囲以下は 0 とみなす、デッドゾーンを設けます。XInput は目安として、`XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE`（7849）を用意しています。

```cpp
// 左スティックのデッドゾーン処理。範囲内は 0、外側は 0〜1 に引き伸ばす
float ApplyDeadZone(float x, float y, float dead = 7849.0f / 32768.0f) {
  const float length = std::sqrt(x * x + y * y);
  if (length < dead) return 0.0f;                          // デッドゾーンの中は反応なし
  const float scaled = (length - dead) / (1.0f - dead);    // デッドゾーンの外を 0〜1 に伸ばす
  return scaled / length;                                  // 方向のベクトルに掛ける係数
}
```

x と y を<strong>別々に</strong>デッドゾーン処理すると、斜めの動きが四角い形になります。長さで判定すると、円形になります。

## アクションにまとめる {#action}

キーの名前を、ゲームの処理に直接書くと、あとで困ります。キーの配置を変えられなくなりますし、ゲームパッドにも対応できません。そこで、<strong>「ジャンプ」「攻撃」といったアクション</strong>に名前を付けて、入力と結びつけます。

```cpp
enum class Action { kJump, kAttack, kMoveX, kMoveY };

// アクションに、キーとボタンを割り当てる（設定画面で変えられるようにしておく）
struct Binding {
  int keyboard_key;  // VK_SPACE など
  WORD pad_button;   // XINPUT_GAMEPAD_A など
};

// ゲームの処理は、アクションの名前だけを見る
if (input.WasPressed(Action::kJump)) {
  player.Jump();
}
```

入力の読み取りと、ゲームの処理の間に、この層を挟みます。移動の軸（`kMoveX`、`kMoveY`）は、キーボードなら `A`/`D` で -1/+1、ゲームパッドなら左スティックの値、と同じ名前でそろえると、ゲームの側は、どちらの入力か意識せずに済みます。

## よくあるミス {#mistakes}

??? failure "押した瞬間の処理が、何度も実行される"
    `IsHeld` を使っています。1 回だけにしたい処理は `WasPressed` で書きます。

??? failure "ウィンドウを切り替えたら、キャラクターが歩き続ける"
    `WM_KILLFOCUS` で、キー状態をすべてクリアしていません。

??? failure "ゲームパッドのキャラクターが、勝手に少しずつ動く"
    デッドゾーンがありません。

??? failure "更新の途中でキー状態が変わって、フレーム内で食い違う"
    入力はフレームの先頭で 1 回だけ取り、そのフレームの間は同じ値を使います。

## これだけ覚える {#summary}

- 入力は毎フレームの先頭で 1 回取り、「押された瞬間」「押している間」「離された瞬間」で持つ
- マウスの視点移動は Raw Input、ゲームパッドは XInput とデッドゾーン
- ゲームの処理は、キーの名前でなく、アクションの名前で書く

## 関連ページ

- [ゲームループと固定タイムステップ](game-loop.md)
- [シーン管理](scene.md)
- [Win32 Window and Message Loop](../directx/dx11/window.md)
