---
title: Rendering Depth
tags:
  - 描画
---

# Rendering Depth

光の行列ができたら次は光の位置から見た深度を描きます。色は要りません。書くのは深度バッファだけです。ピクセルシェーダーも付けないので、画面を描くパスよりずっと軽く済みます。軽いからといって手を抜くと影が欠ける影の端が崩れる、メモリが足りないといった問題が出ます。このページでは深度テクスチャの作り方、形式による精度とメモリの違いバイアスをハードウェアに任せるときの式、影を落とす物の絞り方を数字つきで説明します。

数字は C++ で数え直し HLSL は `fxc`（`vs_5_0` / `ps_5_0`）で、D3D11 のコードは `g++ -std=c++23 -fsyntax-only`（Windows のヘッダーつき）で通しました。描画した結果は確かめていません。バイアスの式は Microsoft Learn の「Depth Bias」（Direct3D 11）を読んで書いています。

!!! tip "ポイント"
    - 深度だけを描きピクセルシェーダーは付けません。アルファ テストの物だけ `clip` を行うピクセルシェーダーが要ります。
    - 2048² の `D32_FLOAT` は 16 MiB、`D16_UNORM` は 8 MiB です。4096² にすると 4 倍の 64 MiB と 32 MiB です。
    - 透視投影の光では near を 0.1 から 1.0 にすると、深度 1 刻みあたりの距離が約 10 分の 1 になります。
    - `DepthBias` は 24 ビットの深度で 1000 のとき深度に 5.96e-5 を足します。距離 100 m の正射影では約 6 mm です。

!!! info "このページを読む前に"
    - [Shadow Map Basics](index.md)（このセクション全体の地図と、読む順番）
    - [The Light Matrix](light-matrix.md)（この深度パスに渡す行列の作り方）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## このパスで起きること {#overview}

深度パスの仕事は光から見て各画素で最も近い面までの距離をテクスチャに残すことです。流れは短く頂点シェーダーが光の行列で頂点を変換し、ラスタライザーが三角形を塗り深度テストで手前が勝って、深度バッファに書き込まれます。

<svg class="fig flow" viewBox="0 0 660 210" role="img" aria-label="深度パスの流れ"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">深度パスの流れ</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">深度だけのパスで起きること</text><rect x="20" y="60" width="130" height="56" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="85.0" y="88.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">頂点シェーダー</text><text x="85" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">光の行列で変換</text><line x1="150" y1="88" x2="178" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="180" y="60" width="130" height="56" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="245.0" y="88.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ラスタライザー</text><text x="245" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">カリング・バイアス</text><line x1="310" y1="88" x2="338" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="340" y="60" width="130" height="56" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="405.0" y="88.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">深度テスト</text><text x="405" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">LESS で比べる</text><line x1="470" y1="88" x2="498" y2="88" stroke="currentColor" stroke-width="2" marker-end="url(#f1)"/><rect x="500" y="60" width="130" height="56" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="565.0" y="88.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">深度バッファ</text><text x="565" y="140" text-anchor="middle" style="font-size:11px;font-weight:400">だけに書く</text><text x="330" y="190" text-anchor="middle" style="font-size:12px;font-weight:400">ピクセル シェーダーなし・色の書き込みなし（アルファ テストの物だけ PS を付ける）</text></svg>

ピクセルシェーダーを付けない理由は色が要らないからです。ピクセルシェーダーがなければ、GPU は画素の色を計算せず深度の比較と書き込みだけを行います。「どれくらい速くなるか」は GPU によって違うので、このページでは数字を載せません。旧版には「多くの GPU が 2 倍以上」と書いてありましたが、出どころを確かめられなかったので、外しました。

## 深度テクスチャを作る {#create}

DirectX 11 では 1 枚のテクスチャを 2 通りに見ます。シャドウパスでは深度ステンシルビュー（DSV）として書き込みメインパスではシェーダーリソースビュー（SRV）として読み取ります。同じメモリを書く側の型と読む側の型で見せたいので、テクスチャそのものは `TYPELESS`（型なし）で作ります。

ここからコードを数行ずつ見ます。最初は入れ物です。

```cpp
#include <d3d11.h>

// ---- シャドウ マップの作成と、深度だけのパスの設定（Direct3D 11）----
// 例を短くするため、HRESULT の確認と解放は省く（実際のコードでは確認する）。

struct ShadowMap {
  ID3D11Texture2D* tex = nullptr;            // 深度テクスチャ本体（TYPELESS）
  ID3D11DepthStencilView* dsv = nullptr;     // 書き込み用の見え方
  ID3D11ShaderResourceView* srv = nullptr;   // 読み取り用の見え方
  ID3D11RasterizerState* rs = nullptr;       // シャドウ パス用のラスタライザー
  ID3D11DepthStencilState* ds = nullptr;     // 深度テストの状態
  UINT size = 0;                             // 一辺の画素数
};
```

`ShadowMap` にテクスチャと 2 つのビュー、ラスタライザーと深度の状態、大きさをまとめました。実際のコードでは `ComPtr` などのスマートポインターに替えて解放を自動にします。この例では短くするため生ポインターのままにし、`HRESULT` の確認も省いています。

次はテクスチャ本体です。

```cpp
ShadowMap CreateShadowMap(ID3D11Device* device, UINT size) {
  ShadowMap sm;                                      // 返す入れ物
  sm.size = size;                                    // 大きさを覚える（ビューポートに使う）

  D3D11_TEXTURE2D_DESC desc = {};                    // 全メンバーを 0 で初期化
  desc.Width = size;                                 // 幅
  desc.Height = size;                                // 高さ
  desc.MipLevels = 1;                                // ミップは作らない
  desc.ArraySize = 1;                                // 1 枚
  desc.Format = DXGI_FORMAT_R32_TYPELESS;            // 型なし。ビューごとに D32_FLOAT と R32_FLOAT に見せる
  desc.SampleDesc.Count = 1;                         // MSAA なし
  desc.Usage = D3D11_USAGE_DEFAULT;                  // GPU が読み書きする
  desc.BindFlags = D3D11_BIND_DEPTH_STENCIL          // 書くとき: 深度バッファとして
                 | D3D11_BIND_SHADER_RESOURCE;       // 読むとき: テクスチャとして
  device->CreateTexture2D(&desc, nullptr, &sm.tex);  // 初期データは要らない
```

`Format` を `R32_TYPELESS` にするのが肝です。`D32_FLOAT` で作ると SRV を作れなくなります。`BindFlags` に `D3D11_BIND_DEPTH_STENCIL` と `D3D11_BIND_SHADER_RESOURCE` の両方を付けるのも忘れがちな点で、片方を忘れるとビューの作成が失敗します。ミップマップは作りません。シャドウマップの深度を平均すると、遮蔽の境目がありえない距離になってしまうからです。

続いて 2 つのビューです。

```cpp
  D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};            // 書き込み用ビュー
  dsv.Format = DXGI_FORMAT_D32_FLOAT;                // 深度として解釈する形式
  dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D; // 2D テクスチャ
  device->CreateDepthStencilView(sm.tex, &dsv, &sm.dsv);

  D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};          // 読み取り用ビュー
  srv.Format = DXGI_FORMAT_R32_FLOAT;                // シェーダーが float として読む形式
  srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D; // 2D テクスチャ
  srv.Texture2D.MipLevels = 1;                       // ミップは 1 段
  device->CreateShaderResourceView(sm.tex, &srv, &sm.srv);
```

DSV は `D32_FLOAT` として深度を書き SRV は `R32_FLOAT` として float を読みます。同じメモリを違う型名で見ているだけです。注意が 1 つあります。同じテクスチャを DSV として束ねたまま SRV としても読むことはできません。メインパスで読む前に `OMSetRenderTargets` で DSV を外します（後述の `EndShadowPass`）。

### 形式の選び方 {#formats}

`D32_FLOAT` 以外の形式を使うときは TYPELESS の形式、DSV の形式、SRV の形式をそろえて指定します。組み合わせは次のとおりです（Direct3D の形式名）。

| 精度 | テクスチャ | DSV | SRV |
| --- | --- | --- | --- |
| 32 ビット float | `R32_TYPELESS` | `D32_FLOAT` | `R32_FLOAT` |
| 24 ビット + ステンシル | `R24G8_TYPELESS` | `D24_UNORM_S8_UINT` | `R24_UNORM_X8_TYPELESS` |
| 16 ビット | `R16_TYPELESS` | `D16_UNORM` | `R16_UNORM` |

メモリは解像度の 2 乗に比例します。C++ で数えると次のとおりです。

- 512²: 32 ビット（と 24 ビット + ステンシル）は 1.0 MiB、16 ビットは 0.5 MiB
- 1024²: 4.0 MiB、2.0 MiB
- 2048²: 16.0 MiB、8.0 MiB
- 4096²: 64.0 MiB、32.0 MiB

カスケードを 4 枚、2048² で持てば 32 ビットで 64 MiB です。モバイルなど帯域が厳しい環境では 16 ビットにして半分にするのが定石です。ただし、その代わりに精度が落ちます。次の節で数えます。

## 深度の精度 {#precision}

### 正射影は一定の刻み {#ortho}

平行光源の影は正射影なので深度は線形です。光から見た奥行きの範囲が 100 m なら深度の 1 刻みは `100 m / 刻みの数` です。16 ビット（65536 刻み）で 1.526 mm、24 ビット（16777216 刻み）で 0.006 mm です。どの距離でも同じなのでバイアスが扱いやすくなります。

### 透視投影は近くで細かく遠くで粗い {#perspective}

スポットライトや点光源は透視投影で、深度が非線形です。標準の深度（near で 0、far で 1）では距離 `z` の深度は `f/(f−n) × (1 − n/z)` で、近くに刻みが集まります。far が 100 m のときの深度 1 刻みあたりの距離は次のとおりです。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="透視投影の深度の刻み"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">透視投影の深度の刻み</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="80.0,249.9 84.9,249.9 89.8,249.8 94.7,249.6 99.6,249.5 104.5,249.3 109.4,249.1 114.3,248.9 119.2,248.6 124.1,248.3 129.0,248.0 133.9,247.6 138.8,247.3 143.7,246.8 148.6,246.4 153.5,246.0 158.4,245.5 163.3,244.9 168.2,244.4 173.1,243.8 178.0,243.2 182.9,242.6 187.8,241.9 192.7,241.2 197.6,240.5 202.5,239.8 207.4,239.0 212.3,238.2 217.2,237.4 222.1,236.5 227.0,235.7 231.9,234.7 236.8,233.8 241.7,232.8 246.6,231.8 251.5,230.8 256.4,229.8 261.3,228.7 266.2,227.6 271.1,226.4 276.0,225.3 280.9,224.1 285.8,222.8 290.7,221.6 295.6,220.3 300.5,219.0 305.4,217.7 310.3,216.3 315.2,214.9 320.1,213.5 325.0,212.0 329.9,210.6 334.8,209.1 339.7,207.5 344.6,206.0 349.5,204.4 354.4,202.7 359.3,201.1 364.2,199.4 369.1,197.7 374.0,196.0 378.9,194.2 383.8,192.4 388.7,190.6 393.6,188.7 398.5,186.9 403.4,185.0 408.3,183.0 413.2,181.1 418.1,179.1 423.0,177.0 427.9,175.0 432.8,172.9 437.7,170.8 442.6,168.7 447.5,166.5 452.4,164.3 457.3,162.1 462.2,159.8 467.1,157.5 472.0,155.2 476.9,152.9 481.8,150.5 486.7,148.1 491.6,145.7 496.5,143.2 501.4,140.8 506.3,138.2 511.2,135.7 516.1,133.1 521.0,130.5 525.9,127.9 530.8,125.3 535.7,122.6 540.6,119.8 545.5,117.1 550.4,114.3 555.3,111.5 560.2,108.7 565.1,105.8 570.0,102.9"/><text x="370.0" y="189.38591179685932" text-anchor="start" style="font-size:12px;font-weight:700">D16, near 0.1</text><polyline fill="none" stroke="#e5aa28" stroke-width="2.5" points="80.0,250.0 84.9,250.0 89.8,250.0 94.7,250.0 99.6,249.9 104.5,249.9 109.4,249.9 114.3,249.9 119.2,249.9 124.1,249.8 129.0,249.8 133.9,249.8 138.8,249.7 143.7,249.7 148.6,249.6 153.5,249.6 158.4,249.6 163.3,249.5 168.2,249.4 173.1,249.4 178.0,249.3 182.9,249.3 187.8,249.2 192.7,249.1 197.6,249.1 202.5,249.0 207.4,248.9 212.3,248.8 217.2,248.8 222.1,248.7 227.0,248.6 231.9,248.5 236.8,248.4 241.7,248.3 246.6,248.2 251.5,248.1 256.4,248.0 261.3,247.9 266.2,247.8 271.1,247.7 276.0,247.6 280.9,247.4 285.8,247.3 290.7,247.2 295.6,247.1 300.5,246.9 305.4,246.8 310.3,246.7 315.2,246.5 320.1,246.4 325.0,246.3 329.9,246.1 334.8,246.0 339.7,245.8 344.6,245.7 349.5,245.5 354.4,245.4 359.3,245.2 364.2,245.0 369.1,244.9 374.0,244.7 378.9,244.5 383.8,244.3 388.7,244.2 393.6,244.0 398.5,243.8 403.4,243.6 408.3,243.4 413.2,243.2 418.1,243.0 423.0,242.8 427.9,242.6 432.8,242.4 437.7,242.2 442.6,242.0 447.5,241.8 452.4,241.6 457.3,241.4 462.2,241.2 467.1,240.9 472.0,240.7 476.9,240.5 481.8,240.3 486.7,240.0 491.6,239.8 496.5,239.5 501.4,239.3 506.3,239.1 511.2,238.8 516.1,238.6 521.0,238.3 525.9,238.1 530.8,237.8 535.7,237.5 540.6,237.3 545.5,237.0 550.4,236.7 555.3,236.5 560.2,236.2 565.1,235.9 570.0,235.6"/><text x="370.0" y="236.82899234230268" text-anchor="start" style="font-size:12px;font-weight:700">D16, near 1.0</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="80.0,250.0 84.9,250.0 89.8,250.0 94.7,250.0 99.6,250.0 104.5,250.0 109.4,250.0 114.3,250.0 119.2,250.0 124.1,250.0 129.0,250.0 133.9,250.0 138.8,250.0 143.7,250.0 148.6,250.0 153.5,250.0 158.4,250.0 163.3,250.0 168.2,250.0 173.1,250.0 178.0,250.0 182.9,250.0 187.8,250.0 192.7,250.0 197.6,250.0 202.5,250.0 207.4,250.0 212.3,250.0 217.2,250.0 222.1,249.9 227.0,249.9 231.9,249.9 236.8,249.9 241.7,249.9 246.6,249.9 251.5,249.9 256.4,249.9 261.3,249.9 266.2,249.9 271.1,249.9 276.0,249.9 280.9,249.9 285.8,249.9 290.7,249.9 295.6,249.9 300.5,249.9 305.4,249.9 310.3,249.9 315.2,249.9 320.1,249.9 325.0,249.9 329.9,249.8 334.8,249.8 339.7,249.8 344.6,249.8 349.5,249.8 354.4,249.8 359.3,249.8 364.2,249.8 369.1,249.8 374.0,249.8 378.9,249.8 383.8,249.8 388.7,249.8 393.6,249.8 398.5,249.8 403.4,249.7 408.3,249.7 413.2,249.7 418.1,249.7 423.0,249.7 427.9,249.7 432.8,249.7 437.7,249.7 442.6,249.7 447.5,249.7 452.4,249.7 457.3,249.7 462.2,249.7 467.1,249.6 472.0,249.6 476.9,249.6 481.8,249.6 486.7,249.6 491.6,249.6 496.5,249.6 501.4,249.6 506.3,249.6 511.2,249.6 516.1,249.5 521.0,249.5 525.9,249.5 530.8,249.5 535.7,249.5 540.6,249.5 545.5,249.5 550.4,249.5 555.3,249.5 560.2,249.5 565.1,249.4 570.0,249.4"/><text x="370.0" y="241.79634868670345" text-anchor="start" style="font-size:12px;font-weight:700">D24, near 0.1</text><line x1="70" y1="249.05" x2="570" y2="249.05" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="564" y="243.05" text-anchor="end" style="font-size:12px;font-weight:400">1 cm</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">75</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">100</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">1.0</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">1.5</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">2.0</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">光からの距離 z（m）。far = 100 m</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">深度 1 刻みあたりの距離（m）</text></svg>

near が 0.1 m の場合、16 ビットで距離 2 m では 0.6 mm、10 m では 15 mm、50 m では 384 mm、100 m では 1548 mm です。24 ビットなら 100 m でも 6 mm です。near を 1.0 m に上げると、16 ビットで 100 m が 151 mm、50 m が 38 mm になり約 10 分の 1 になります。

near を遠くに置くと精度が上がるのは、`n/z` の項が小さくなり刻みが遠くへ回るからです。光源の近くにある物の影を諦められる範囲で、near はできるだけ遠くに置きます。16 ビットで遠くの影を描くのは、near を遠くしても難しいので、透視投影のシャドウマップは 24 ビット以上にします。

## シャドウ パスを設定する {#state}

ここまでの形式を決めたらパスの状態を決めます。

```cpp
  D3D11_RASTERIZER_DESC rs = {};                     // ラスタライザー
  rs.FillMode = D3D11_FILL_SOLID;                    // 塗りつぶし
  rs.CullMode = D3D11_CULL_BACK;                     // 通常は裏面を捨てる。前面カリングにするなら D3D11_CULL_FRONT
  rs.FrontCounterClockwise = FALSE;                  // 時計回りが表（このサイトの約束）
  rs.DepthBias = 1000;                               // ハードウェア バイアス。24 ビット換算で 1000 * 2^-24（一例）
  rs.SlopeScaledDepthBias = 1.5f;                    // 斜めの面ほど大きくずらす係数（一例）
  rs.DepthBiasClamp = 0.0f;                          // 上限なし。斜めすぎる面で飛ぶなら正の値を入れる
  rs.DepthClipEnable = FALSE;                        // FALSE: near の手前の物も捨てずに深度を near に張りつける
  device->CreateRasterizerState(&rs, &sm.rs);

  D3D11_DEPTH_STENCIL_DESC ds = {};                  // 深度テスト
  ds.DepthEnable = TRUE;                             // 深度テストを使う
  ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;    // 書き込みも有効
  ds.DepthFunc = D3D11_COMPARISON_LESS;              // 手前（小さい値）が勝つ
  device->CreateDepthStencilState(&ds, &sm.ds);
  return sm;
```

状態の設定で重要な項目を 1 つずつ見ます。

### カリング {#cull}

`CullMode` を `D3D11_CULL_BACK` にすれば通常の描画と同じく裏面を捨てます。表面を捨てる（`D3D11_CULL_FRONT`）と光から遠い側の面の深度が残り物の厚みの分だけ影の判定に余裕ができるので、自己影が減ります。ただし、板のような薄い物では影が欠けます（[Front-Face Culling](../bias/front-face-culling.md)）。このサイトでは時計回りが表（`FrontCounterClockwise = FALSE`）です。光の行列を左手系で作っていれば、通常の描画と向きが一致します。

### ハードウェアのバイアス {#hw-bias}

`DepthBias` と `SlopeScaledDepthBias` で書き込む深度を押し出せます。深度バッファが UNORM（`D16_UNORM`、`D24_UNORM_S8_UINT`）のとき式は次のとおりです。

```text
Bias = DepthBias × r + SlopeScaledDepthBias × MaxDepthSlope
```

`r` は深度バッファの形式で表せる 0 より大きい最小の値で、24 ビットなら `2^−24 = 5.96e-8` です。`MaxDepthSlope` はその画素での深度の傾き（水平方向と垂直方向の大きいほう）です。float の深度（`D32_FLOAT`）では式の第 1 項が `DepthBias × 2^(exponent(その三角形の最大の z) − 23)` に変わります。

24 ビットの深度で `DepthBias` を変えると、深度に足される量は次のとおりです。奥行き 100 m の正射影では世界の距離に直すと同じ比で変わります。

- 1: 5.96e-8（0.006 mm）
- 100: 5.96e-6（0.596 mm）
- 1000: 5.96e-5（5.96 mm）
- 10000: 5.96e-4（59.6 mm）

float32 の深度の場合は同じ `DepthBias = 1` でも三角形の最大の `z` によって、押し出す量が変わります。`z` が 0.9 や 0.5 付近なら 5.96e-8、0.1 付近なら 7.45e-9、0.01 付近なら 9.31e-10 です。near に近い三角形では同じ設定で押し出しが小さくなる点に気をつけます。

`SlopeScaledDepthBias` の項は面が光に対して傾くほど大きくなります。正射影で奥行き 100 m、40 m 四方を 2048 画素で覆うなら 1 テクセルは 0.0195 m です。面が光に正対（0°）なら傾きは 0、30° で 1 テクセルあたり 11.3 mm、60° で 33.8 mm、80° で 110.8 mm、85° で 223.2 mm と急に増えます。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="傾きと深度の変化"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">傾きと深度の変化</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 75.0,249.7 80.0,249.5 85.0,249.2 90.0,249.0 95.0,248.7 100.0,248.5 105.0,248.2 110.0,247.9 115.0,247.7 120.0,247.4 125.0,247.1 130.0,246.9 135.0,246.6 140.0,246.3 145.0,246.1 150.0,245.8 155.0,245.5 160.0,245.2 165.0,245.0 170.0,244.7 175.0,244.4 180.0,244.1 185.0,243.8 190.0,243.5 195.0,243.2 200.0,242.9 205.0,242.6 210.0,242.3 215.0,242.0 220.0,241.7 225.0,241.3 230.0,241.0 235.0,240.7 240.0,240.3 245.0,240.0 250.0,239.6 255.0,239.3 260.0,238.9 265.0,238.5 270.0,238.1 275.0,237.7 280.0,237.3 285.0,236.9 290.0,236.5 295.0,236.1 300.0,235.6 305.0,235.2 310.0,234.7 315.0,234.2 320.0,233.7 325.0,233.2 330.0,232.7 335.0,232.1 340.0,231.6 345.0,231.0 350.0,230.4 355.0,229.7 360.0,229.1 365.0,228.4 370.0,227.7 375.0,227.0 380.0,226.2 385.0,225.4 390.0,224.5 395.0,223.6 400.0,222.7 405.0,221.7 410.0,220.7 415.0,219.6 420.0,218.4 425.0,217.2 430.0,215.9 435.0,214.5 440.0,213.0 445.0,211.4 450.0,209.7 455.0,207.9 460.0,205.9 465.0,203.7 470.0,201.3 475.0,198.7 480.0,195.9 485.0,192.7 490.0,189.2 495.0,185.2 500.0,180.8 505.0,175.7 510.0,169.9 515.0,163.1 520.0,155.1 525.0,145.5 530.0,133.9 535.0,119.4 540.0,100.9 545.0,76.4 550.0,60.0 555.0,60.0 560.0,60.0 565.0,60.0 570.0,60.0"/><circle cx="238.5" cy="240.4" r="4" fill="#4c8bf5"/><text x="230.53932584269663" y="232.41517857142858" text-anchor="end" style="font-size:11px;font-weight:700">11.3 mm</text><circle cx="407.1" cy="221.3" r="4" fill="#4c8bf5"/><text x="399.07865168539325" y="213.33035714285714" text-anchor="end" style="font-size:11px;font-weight:700">33.8 mm</text><circle cx="519.4" cy="156.0" r="4" fill="#4c8bf5"/><text x="511.43820224719093" y="148.01785714285714" text-anchor="end" style="font-size:11px;font-weight:700">110.8 mm</text><circle cx="547.5" cy="60.7" r="4" fill="#4c8bf5"/><text x="539.5280898876405" y="52.678571428571416" text-anchor="end" style="font-size:11px;font-weight:700">223.2 mm</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="238.53932584269663" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="407.07865168539325" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="547.5280898876405" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">85°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="211.58928571428572" text-anchor="end" style="font-size:11px;font-weight:400">50</text><text x="62" y="169.17857142857144" text-anchor="end" style="font-size:11px;font-weight:400">100</text><text x="62" y="126.76785714285714" text-anchor="end" style="font-size:11px;font-weight:400">150</text><text x="62" y="84.35714285714286" text-anchor="end" style="font-size:11px;font-weight:400">200</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">面が光の向きに対して傾いた角度（0° = 光に正対）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">1 テクセル進んだときの深度の変化（mm、正射影 100 m）</text></svg>

傾きが大きくなる面では `SlopeScaledDepthBias` の項が大きく効きます。入れすぎると影が物から浮いて離れて見えます（ピーターパン現象）。そこで `DepthBiasClamp` に上限を入れます。正の値を入れるとバイアスの大きさがその値で頭打ちになります。このページの例では上限なし（0）にしています。値の決め方はバイアスのページで扱います（[Front-Face Culling](../bias/front-face-culling.md) など）。

### 深度クリップ {#clip}

`DepthClipEnable` を `FALSE` にすると near の手前にある三角形が切り取られず深度が near に張り付いた状態で残ります。影を落とす物は光の視錐台の外側（光の near より手前）にあっても、視錐台の中に影を落とすことがあります。そういう物を捨てずに残すための設定です。far の外側も同じように張り付きます。

この設定のとき near の手前の物は、すべて同じ深度（near と同じ値）で書かれます。その上にある物同士の前後は判定できなくなります。影を落とすという目的にはそれで足ります。

## 描画の設定と HLSL {#draw}

次は影を落とす物を描く前の設定です。

```cpp
// 影を落とす物を描く前の設定。呼んだ後に DrawShadowCasters を呼ぶ。
void BeginShadowPass(ID3D11DeviceContext* ctx, const ShadowMap& sm, ID3D11VertexShader* vs) {
  ctx->OMSetRenderTargets(0, nullptr, sm.dsv);                           // 色は無し。深度だけに書く
  ctx->ClearDepthStencilView(sm.dsv, D3D11_CLEAR_DEPTH, 1.0f, 0);        // 1.0（最も遠い）で消す
  D3D11_VIEWPORT vp = {0.0f, 0.0f, static_cast<float>(sm.size), static_cast<float>(sm.size), 0.0f, 1.0f};
  ctx->RSSetViewports(1, &vp);                                           // 描く範囲をシャドウ マップ全体に
  ctx->RSSetState(sm.rs);                                                // カリングとバイアス
  ctx->OMSetDepthStencilState(sm.ds, 0);                                 // 深度テスト
  ctx->VSSetShader(vs, nullptr, 0);                                      // 頂点シェーダーだけ
  ctx->PSSetShader(nullptr, nullptr, 0);                                 // ピクセル シェーダーは無し
}
```

色のターゲットは 0 個（`nullptr`）で、深度ビューだけを渡します。消去は 1.0 で行います。ビューポートはシャドウマップ全体にします。ピクセルシェーダーは `nullptr` です。この呼び出しが漏れると前のパスのピクセルシェーダーが残って、不要な計算とレンダーターゲットの不一致の警告が出ます。

```cpp
// 描き終わった後。同じテクスチャを SRV と DSV で同時に束ねられないので、DSV を外してから読む。
void EndShadowPass(ID3D11DeviceContext* ctx) {
  ctx->OMSetRenderTargets(0, nullptr, nullptr);                          // 書き込み先を外す
}
```

描き終わった後、読み取る前に書き込み先を外します。Direct3D 11 は同じテクスチャが DSV と SRV の両方に束ねられていると、SRV の側を黙って `nullptr` にしてしまうので、影が全部消えるといった症状になります。

頂点シェーダーです。

```hlsl
// ---- 深度だけのシャドウ パス（左手系・行ベクトル）----

cbuffer LightCB : register(b0) {
  float4x4 gLightViewProj;   // 光のビュー × 射影
};
cbuffer ObjectCB : register(b1) {
  float4x4 gWorld;           // モデル → ワールド
};

// 頂点シェーダー: 変換するだけ。ピクセル シェーダーは付けない。
float4 ShadowVS(float3 position : POSITION) : SV_Position {
  float4 world = mul(float4(position, 1.0), gWorld);   // まずワールドへ
  return mul(world, gLightViewProj);                   // 次に光のクリップ空間へ（深度は SV_Position.z/w になる）
}
```

`mul(float4(position, 1.0), gWorld)` でモデルからワールドへ次に `gLightViewProj` で光のクリップ空間へ変換します。行ベクトルなので掛ける順が左から右です。深度は `SV_Position.z / w` としてラスタライザーが勝手に深度バッファへ書きます。ピクセルシェーダーに何も書く必要がありません。

アルファ テストの物（葉、金網）は穴が空いた形を影にも反映する必要があるので、ピクセルシェーダーで穴を捨てます。

```hlsl
// アルファ テストの物だけ、ピクセル シェーダーを付ける。
Texture2D<float4> gAlbedo : register(t0);              // 葉のテクスチャなど。a が穴の形
SamplerState gLinear : register(s0);

struct CutoutVSOut {
  float4 pos : SV_Position;   // クリップ空間の位置
  float2 uv  : TEXCOORD0;     // テクスチャ座標
};

CutoutVSOut ShadowCutoutVS(float3 position : POSITION, float2 uv : TEXCOORD0) {
  CutoutVSOut o;                                       // 出力
  o.pos = ShadowVS(position);                          // 位置は同じ
  o.uv = uv;                                           // UV を渡す
  return o;
}

void ShadowCutoutPS(CutoutVSOut i) {                   // 戻り値なし。深度は自動で書かれる
  float a = gAlbedo.Sample(gLinear, i.uv).a;           // 穴の形
  clip(a - 0.5);                                       // 0.5 未満の画素を捨てる（深度も書かれない）
}
```

`clip(a − 0.5)` は引数が負なら画素を捨てます。捨てた画素には深度が書かれません。ピクセルシェーダーを付けると、高速パス（深度のみ）が使えなくなる GPU があるので、アルファ テストの物だけを別のドローコールに分けます。詳しくは [Alpha-Tested Shadows](../special-cases/alpha-test-shadows.md) を参照してください。

## 描く物を絞る {#cull-casters}

シャドウパスはシーンをもう一度描くので、描画コストが増えます。その増え方は物の数と三角形の数に比例します。減らす方法は次のとおりです。

- **影を落とさない物を外す。** 小さな物、遠くの物、影が目立たない物はシャドウパスに入れません。
- **光の視錐台でカリングする。** カメラの視錐台ではありません。光から見て影のテクスチャに入らない物は描きません。ただし、光の視錐台の外にある物でも視錐台の中へ影を落とすなら残す必要があります。カメラの見える範囲を光の向きに伸ばした領域（押し出した領域）の中の物が対象です。
- **LOD を粗くする。** 影は細部が見えないので、粗い LOD で十分です。
- **静的な物をキャッシュする。** 動かない物のシャドウマップを保存して、動く物だけを毎フレーム描き足します（[Shadows for Many Lights](../local-lights/many-lights.md)）。
- **更新を間引く。** 遠いカスケードは数フレームに 1 回だけ更新します（[CSM](../cascaded.md)）。

## よくあるミス {#mistakes}

??? failure "画面に映っている物だけを描いて、影が欠ける"
    原因はカリングの対象をカメラから見える物にしていることです。画面の外にある物も影を落とします。光から見える物（と光の視錐台に影を落とす物）を描きます。

??? failure "影が全部消える"
    原因は DSV を束ねたまま同じテクスチャを SRV として読もうとしていることです。読む前に `OMSetRenderTargets(0, nullptr, nullptr)` で DSV を外します。デバッグレイヤーを有効にすると、警告が出ます。

??? failure "DSV または SRV の作成に失敗する"
    原因はテクスチャを `D32_FLOAT` など型つきで作ったことか `BindFlags` の片方を忘れたことです。`R32_TYPELESS` で作り `D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE` を両方付けます。

??? failure "光の近くの物の影が欠ける"
    原因は `DepthClipEnable = TRUE` のまま光の near より手前の物が切り取られることです。`FALSE` にして深度を near に張り付けます。

??? failure "斜めの面で影が浮く（ピーターパン）"
    原因は `SlopeScaledDepthBias` が大きすぎて、斜めの面が押し出されすぎることです。`DepthBiasClamp` で上限を入れます。

??? failure "遠くの影だけ帯状の縞が出る"
    原因は 16 ビットの透視投影で、遠くの深度の刻みが粗いことです。50 m で 384 mm の刻みになります。24 ビット以上にするか near を遠くに置きます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 深度だけを描く。ピクセル シェーダーは付けない（アルファ テストの物だけ `clip`）
    - [x] テクスチャは `TYPELESS` で作り DSV と SRV で型を分ける。読む前に DSV を外す
    - [x] 2048² は 32 ビットで 16 MiB、16 ビットで 8 MiB
    - [x] 透視投影は near を遠くに置く（0.1 → 1.0 で刻みが約 1/10）
    - [x] ハードウェア バイアスは `DepthBias × r + Slope × MaxDepthSlope`。24 ビットの 1000 で 5.96e-5
    - [x] 影を落とす物は光から見える物と押し出した領域の物

## C++ で数えたもの {#numbers}

```cpp
#include <cmath>
#include <cstdio>
#include <cstring>
#include <initializer_list>

// 標準の透視投影（near で 0、far で 1）での、視点空間の距離 z（m）から深度 d へ。
double DepthOf(double z, double n, double f) { return f / (f - n) * (1.0 - n / z); }
// 深度 d から z へ（逆変換）。
double ZOf(double d, double n, double f) { return n * f / (f - d * (f - n)); }

int main() {
  // 1. 解像度と形式ごとのメモリ（MiB）。D32_FLOAT と D24S8 は 4 バイト、D16 は 2 バイト。
  std::printf("-- memory (MiB)\n");
  for (int size : {512, 1024, 2048, 4096}) {
    const double texels = static_cast<double>(size) * size;
    std::printf("%4d^2: D32 / D24S8 = %6.1f MiB, D16 = %6.1f MiB\n", size, texels * 4.0 / 1048576.0, texels * 2.0 / 1048576.0);
  }

  // 2. 正射影: 深度が線形なので、深度 1 刻みあたりの距離は一定 = (far - near) / 刻みの数。
  std::printf("-- orthographic: world step per depth step (range 100 m)\n");
  std::printf("D16: %.4f mm, D24: %.5f mm\n", 100.0 / 65536.0 * 1000.0, 100.0 / 16777216.0 * 1000.0);

  // 3. 透視投影: 深度 1 刻みあたりの距離（m）。n = 0.1 と 1.0、f = 100。
  std::printf("-- perspective: world step per depth step (f = 100 m)\n");
  for (double n : {0.1, 1.0}) {
    for (double z : {2.0, 10.0, 50.0, 100.0}) {
      const double d = DepthOf(z, n, 100.0);                                                   // その距離の深度
      const double s16 = ZOf(d + 1.0 / 65536.0, n, 100.0) - ZOf(d, n, 100.0);                  // D16 の 1 刻み
      const double s24 = ZOf(d + 1.0 / 16777216.0, n, 100.0) - ZOf(d, n, 100.0);              // D24 の 1 刻み
      std::printf("n=%.1f z=%5.0f m: D16 step = %9.4f m, D24 step = %10.6f m\n", n, z, s16, s24);
    }
  }

  // 4. ハードウェアバイアス（UNORM の場合）: Bias = DepthBias * r + Slope * MaxDepthSlope。r は 24 ビットなら 2^-24。
  std::printf("-- hardware bias (UNORM24, ortho range 100 m, 2048 px over 40 m)\n");
  const double r24 = 1.0 / 16777216.0;
  for (int bias : {1, 100, 1000, 10000}) {
    std::printf("DepthBias=%5d: depth +%.3e = %.4f mm in the world\n", bias, bias * r24, bias * r24 * 100.0 * 1000.0);
  }
  const double texel = 40.0 / 2048.0;                                            // 1 テクセルの大きさ（m）
  for (double deg : {0.0, 30.0, 60.0, 80.0, 85.0}) {
    const double slope = texel * std::tan(deg * 3.14159265358979 / 180.0) / 100.0;   // 1 テクセル進んだときの深度の変化
    std::printf("surface angle %2.0f deg: MaxDepthSlope = %.3e (= %.4f mm per texel)\n", deg, slope, slope * 100.0 * 1000.0);
  }

  // 5. float32 の深度でのバイアスの刻み: 2^(exponent(max z) - 23)。
  std::printf("-- float32 depth: bias unit = 2^(exponent - 23)\n");
  for (double z : {0.01, 0.1, 0.5, 0.9}) {
    int e;
    std::frexp(z, &e);                                         // z = m * 2^e, 0.5 <= m < 1
    std::printf("max z = %.2f: exponent(IEEE) = %d, unit = %.3e\n", z, e - 1, std::ldexp(1.0, e - 1 - 23));
  }
}
```

```text title="実行結果"
-- memory (MiB)
 512^2: D32 / D24S8 =    1.0 MiB, D16 =    0.5 MiB
1024^2: D32 / D24S8 =    4.0 MiB, D16 =    2.0 MiB
2048^2: D32 / D24S8 =   16.0 MiB, D16 =    8.0 MiB
4096^2: D32 / D24S8 =   64.0 MiB, D16 =   32.0 MiB
-- orthographic: world step per depth step (range 100 m)
D16: 1.5259 mm, D24: 0.00596 mm
-- perspective: world step per depth step (f = 100 m)
n=0.1 z=    2 m: D16 step =    0.0006 m, D24 step =   0.000002 m
n=0.1 z=   10 m: D16 step =    0.0153 m, D24 step =   0.000060 m
n=0.1 z=   50 m: D16 step =    0.3840 m, D24 step =   0.001489 m
n=0.1 z=  100 m: D16 step =    1.5479 m, D24 step =   0.005955 m
n=1.0 z=    2 m: D16 step =    0.0001 m, D24 step =   0.000000 m
n=1.0 z=   10 m: D16 step =    0.0015 m, D24 step =   0.000006 m
n=1.0 z=   50 m: D16 step =    0.0378 m, D24 step =   0.000148 m
n=1.0 z=  100 m: D16 step =    0.1513 m, D24 step =   0.000590 m
-- hardware bias (UNORM24, ortho range 100 m, 2048 px over 40 m)
DepthBias=    1: depth +5.960e-08 = 0.0060 mm in the world
DepthBias=  100: depth +5.960e-06 = 0.5960 mm in the world
DepthBias= 1000: depth +5.960e-05 = 5.9605 mm in the world
DepthBias=10000: depth +5.960e-04 = 59.6046 mm in the world
surface angle  0 deg: MaxDepthSlope = 0.000e+00 (= 0.0000 mm per texel)
surface angle 30 deg: MaxDepthSlope = 1.128e-04 (= 11.2764 mm per texel)
surface angle 60 deg: MaxDepthSlope = 3.383e-04 (= 33.8291 mm per texel)
surface angle 80 deg: MaxDepthSlope = 1.108e-03 (= 110.7672 mm per texel)
surface angle 85 deg: MaxDepthSlope = 2.232e-03 (= 223.2432 mm per texel)
-- float32 depth: bias unit = 2^(exponent - 23)
max z = 0.01: exponent(IEEE) = -7, unit = 9.313e-10
max z = 0.10: exponent(IEEE) = -4, unit = 7.451e-09
max z = 0.50: exponent(IEEE) = -1, unit = 5.960e-08
max z = 0.90: exponent(IEEE) = -1, unit = 5.960e-08
```

## 参考資料 {#references}

- Microsoft Learn, "Depth Bias"（Direct3D 11 のグラフィックス プログラミング ガイド、出力マージャー）。バイアスの式（UNORM と float の場合、`DepthBiasClamp`）はこの文書を読んで書きました。
- Lance Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウマップの原典）。**今回は読んでいません。**
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps" と "D3D11_RASTERIZER_DESC"。**今回は読んでいません。**
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）。**今回は読んでいません。**

`DepthClipEnable = FALSE` の挙動、同じテクスチャを DSV と SRV に同時に束ねたときに SRV が外れる挙動、形式の組み合わせの表は公式文書で確かめていない一般的な知識です。

## 関連ページ {#related}

- [Shadow Map Basics](index.md)
- [The Light Matrix](light-matrix.md)
- [Comparison Samplers](comparison-sampler.md)
