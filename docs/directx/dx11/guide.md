---
title: DirectX 11 Guide
tags:
  - DirectX
---

# DirectX 11 Guide

このセクションの各ページは、API の部品ごとに書いてあります。部品を読んでも、「どの順に作れば、何が見えるようになるのか」は分かりにくいものです。このページは、<strong>ウィンドウを出すところから、回る立方体を描くところまで</strong>を、7 つの段階に分けて順番に示します。各段階で「動いたら何が見えるか」が決まっているので、つまずいたときに、どの段階の問題か分かります。

!!! tip "ポイント"
    - 各段階には、「ゴール」（画面に何が出るか）がある。ゴールの絵が出たら、次へ進む
    - 動かなくなったら、前の段階のコードに戻せるように、段階ごとにコミットしておく
    - 最初から [デバッグ レイヤー](debug-layer.md) を有効にする。ほとんどの間違いは、出力ウィンドウのメッセージで分かる
    - 描画に失敗しても、画面は真っ黒になるだけでエラーが出ないことが多い。段階を飛ばさない

!!! info "このページを読む前に"
    - [DirectX 11](index.md)（このセクションの全体像）
    - [Git の基礎](../../vs/git.md)（段階ごとにコミットする）

## 7 つの段階 {#steps}

| 段階 | ゴール | 読むページ |
| --- | --- | --- |
| 1 | 空のウィンドウが出て、閉じられる | [Window](window.md) |
| 2 | デバイスとスワップ チェーンが作れる（まだ何も描かない） | [Device](device.md)、[DXGI](dxgi.md)、[Swap Chain](swap-chain.md) |
| 3 | 画面が単色で塗りつぶされる | [Render Target View (RTV)](render-target-view.md)、[Clear and Present](clear-present.md) |
| 4 | 三角形が出る | [Shaders and Compilation](shaders.md)、[Vertex Buffer](vertex-buffer.md)、[Input Layout](input-layout.md)、[Drawing a Triangle](triangle.md) |
| 5 | 三角形が回る | [Constant Buffer](constant-buffer.md)、[Map and Update](map-update.md) |
| 6 | 立方体が正しく描かれる | [Index Buffer](index-buffer.md)、[Depth Buffer](depth-stencil.md) |
| 7 | ウィンドウのサイズを変えても壊れない | [Resize](resize.md) |

## 段階 1：ウィンドウ {#step1}

ゴールは、空のウィンドウです。DirectX は関係なく、Win32 のウィンドウとメッセージ ループだけを書きます。ここで作った `HWND` を、段階 2 でスワップ チェーンに渡します。

確認することは、閉じるボタンでプロセスが終了することです。終了しない場合、メッセージ ループの終了条件か `WM_DESTROY` の `PostQuitMessage` が抜けています。

## 段階 2：デバイスとスワップ チェーン {#step2}

ゴールは、エラーなしで起動して終了することです。画面はまだ変わりません。

`D3D11CreateDevice` でデバイスとコンテキストを作り、DXGI のファクトリーから、ウィンドウに結びついたスワップ チェーンを作ります。デバッグ ビルドでは `D3D11_CREATE_DEVICE_DEBUG` を付けます。付けるとデバッグ レイヤーが有効になり、API の誤用を教えてくれます。

`HRESULT` を必ず確認します。`FAILED(hr)` なら、その場で止める習慣にしておくと、後の段階で原因を探す時間が減ります。

## 段階 3：画面を塗りつぶす {#step3}

ゴールは、単色（たとえば濃い青）のウィンドウです。

スワップ チェーンのバック バッファから RTV を作り、毎フレーム次の流れを実行します。

```cpp
const float clear_color[4] = {0.1f, 0.2f, 0.4f, 1.0f};
context->OMSetRenderTargets(1, rtv.GetAddressOf(), nullptr);  // 描き込み先を設定する
context->ClearRenderTargetView(rtv.Get(), clear_color);       // 単色で塗りつぶす
swap_chain->Present(1, 0);                                    // 画面に出す
```

`OMSetRenderTargets` は、描き込み先を決める命令です。これを呼ばないと、塗りつぶしても画面に反映されません。`Present(1, 0)` の第 1 引数 `1` は、垂直同期を待つ指定です。

色が変わらないときは、クリアの色の値が `0` と `1` の範囲か、`Present` を呼んでいるか、RTV を作ったバック バッファが現在のものかを疑います。

## 段階 4：三角形 {#step4}

ゴールは、頂点ごとに赤・緑・青の三角形が出ることです。作るものが一気に増えます。

1. 頂点シェーダーとピクセル シェーダー（HLSL）を書いて、コンパイルする
2. 頂点の型（位置と色）と、3 頂点の頂点バッファを作る
3. 入力レイアウトで、頂点バッファの中身とシェーダーの入力を結びつける
4. ビューポートとラスタライザー ステートを設定して `Draw(3, 0)`

三角形が出ないときの確認順は、[Drawing a Triangle](triangle.md) の「面の向き」にあります。このサイトの規約は、反時計回りが表です。`FrontCounterClockwise = TRUE` を設定し忘れると、三角形が裏面と判断されて、消えます。

## 段階 5：回す {#step5}

ゴールは、三角形が Y 軸の周りを回ることです。

回転行列を作り、定数バッファでシェーダーに渡します。数学ライブラリは SimpleMath を使います。行ベクトル方式なので、行列の掛け順は、頂点に近いものから順に、左から右です。

```cpp
struct Constants {
  DirectX::SimpleMath::Matrix world_view_proj;
};

// 毎フレーム
auto world = Matrix::CreateRotationY(angle);                       // 回転
auto view = Matrix::CreateLookAt({0, 1.5f, 3}, {0, 0, 0}, Vector3::Up);
auto proj = Matrix::CreatePerspectiveFieldOfView(
    XMConvertToRadians(60.0f), aspect, 0.1f, 100.0f);
Constants c{world * view * proj};                                  // 左から右へ掛ける
context->UpdateSubresource(constant_buffer.Get(), 0, nullptr, &c, 0, 0);
```

`world * view * proj` は、頂点にワールド、ビュー、プロジェクションの順に掛かる並びです。HLSL 側は、`mul(float4(position, 1), world_view_proj)` と書きます。

SimpleMath の行列はメモリ上で行優先です。HLSL の `cbuffer` は既定で列優先なので、`row_major float4x4` と宣言して合わせます。合わせないと、図形が歪みます。

```hlsl
cbuffer Constants : register(b0) {
  row_major float4x4 world_view_proj;
};
```

## 段階 6：立方体と深度 {#step6}

ゴールは、立方体が、手前の面だけ見えて回ることです。三角形では、重なりを考えませんでしたが、立体では、奥の面が手前に描かれてしまう問題が出ます。深度バッファで解決します。

立方体は 8 頂点 36 インデックスで書けます。面の巻き順は、外から見て反時計回りにします。

```cpp
// 頂点は ±0.5 の 8 点。色は頂点ごとに変えておくと、向きが分かりやすい
const uint16_t indices[] = {
    4, 5, 6, 4, 6, 7,   // +Z
    0, 3, 2, 0, 2, 1,   // -Z
    1, 2, 6, 1, 6, 5,   // +X
    0, 4, 7, 0, 7, 3,   // -X
    3, 7, 6, 3, 6, 2,   // +Y
    0, 1, 5, 0, 5, 4,   // -Y
};
```

頂点の並びは、0 が (-,-,-)、1 が (+,-,-)、2 が (+,+,-)、3 が (-,+,-)、4 が (-,-,+)、5 が (+,-,+)、6 が (+,+,+)、7 が (-,+,+) です。インデックス バッファを作り、`IASetIndexBuffer` で束ねて `DrawIndexed(36, 0, 0)` で描きます。

深度バッファは、画面と同じ大きさの `DXGI_FORMAT_D32_FLOAT` のテクスチャと、それを指す DSV (Depth Stencil View) です。毎フレーム `ClearDepthStencilView` で 1.0 に戻し、`OMSetRenderTargets` の第 3 引数に DSV を渡します。

```cpp
context->ClearDepthStencilView(dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
context->OMSetRenderTargets(1, rtv.GetAddressOf(), dsv.Get());
```

深度バッファの `Clear` を忘れると、前のフレームの値が残り、物体が途中で消えます。DSV を `OMSetRenderTargets` に渡し忘れると、深度テストが働かず、奥の面が手前に出ます。

## 段階 7：リサイズ {#step7}

ゴールは、ウィンドウの縁をドラッグしても、画面が崩れず、図形が引き伸ばされないことです。

`WM_SIZE` で新しいサイズを受け取り、バック バッファを参照する RTV と、深度バッファを、いったん解放します。それから `ResizeBuffers` を呼び、RTV と深度バッファを作り直します。投影行列のアスペクト比も更新します。詳しくは [Resize](resize.md) にあります。

解放し忘れて `ResizeBuffers` を呼ぶと、バッファがまだ参照されているために失敗します。

## この先 {#next}

回る立方体が動いたら、ここまでの部品で、ほとんどの描画の基礎ができたことになります。次は、次のページから、必要なものを選びます。

- テクスチャを貼る：[Texture2D](texture2d.md)、[Shader Resource View (SRV)](shader-resource-view.md)、[Sampler State](sampler-state.md)
- 半透明：[Blend State](blend-state.md)
- 大量に描く：[Instancing and Draw Calls](instancing-draw.md)
- 複数の描画パス：[Pass Recipes](pass-recipes.md)

## これだけ覚える {#summary}

- 段階を飛ばさず、ゴールの絵が出てから次へ
- 最初から、デバッグ レイヤーを有効にして、`HRESULT` を確認する
- 規約は、右手系・Y-up・行ベクトル・反時計回りが表

## 関連ページ

- [DirectX 11](index.md)
- [Drawing a Triangle](triangle.md)
- [GPU デバッグの流れ](../../vs/gpu-debug.md)
