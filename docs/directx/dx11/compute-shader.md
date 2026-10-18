---
title: Compute Shader
tags:
  - DirectX
---

# Compute Shader

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>計算シェーダー</strong>（Compute Shader、CS）は、描画パイプライン（頂点 → ラスタライズ → ピクセル）とは<strong>別に</strong>、GPU の、並列計算を、<strong>自由に使う</strong>ための、シェーダーです。ぼかし、ヒストグラム、パーティクルの、更新、カリング、プローブの更新など、「画面の、1 ピクセル」や「三角形」に、縛られない、処理を、書けます。ポスト プロセスの、多くと、GPU ドリブンな、処理は、計算シェーダーが、土台です。

!!! tip "ポイント"
    - 計算シェーダーは、<strong>スレッド グループ</strong>（`numthreads`）を、`Dispatch(x, y, z)` 個、起動する。合計のスレッド数 ＝ グループの数 × グループ内のスレッド数。
    - 入力は SRV、出力は UAV（書き込み）。`RWTexture2D`、`RWStructuredBuffer` など。
    - グループ内は、`groupshared` メモリで、スレッド同士が、データを、共有できる。
    - 画面の大きさが、グループの、倍数でないとき、<strong>範囲チェック</strong>が、必須。
    - 同じリソースを、UAV で書きながら、SRV で、読めない（束縛の衝突）。

## 最小の、計算シェーダー

```hlsl
// 画像を、グレースケールに、変換する。1 スレッド = 1 ピクセル。
Texture2D<float4> g_input : register(t0);
RWTexture2D<float4> g_output : register(u0);

[numthreads(8, 8, 1)]                                       // 1 グループ = 8×8×1 = 64 スレッド
void GrayscaleCS(uint3 id : SV_DispatchThreadID) {
  uint width, height;
  g_output.GetDimensions(width, height);
  if (id.x >= width || id.y >= height) return;              // 端の余り: 画像の外のスレッドは、何もしない

  float4 color = g_input.Load(int3(id.xy, 0));
  float gray = dot(color.rgb, float3(0.2126, 0.7152, 0.0722));
  g_output[id.xy] = float4(gray, gray, gray, color.a);
}
```

| 要素 | 内容 |
| --- | --- |
| `[numthreads(X, Y, Z)]` | 1 つのグループの、スレッド数。合計は、1024 以下（`cs_5_0`）。64 の倍数が、効率がよい |
| `SV_DispatchThreadID` | このスレッドの、全体での、通し番号（`(グループ番号 × グループの大きさ) + グループ内の番号`） |
| `SV_GroupID` | このスレッドが属する、グループの番号 |
| `SV_GroupThreadID` | グループ内の、スレッドの番号 |
| `SV_GroupIndex` | グループ内の、通し番号（1 次元） |

## ホスト側：作る・つなぐ・起動する

```cpp
// ① シェーダーを作る（cs_5_0 でコンパイル）。
auto cs_bytecode = CompileShader(L"grayscale.hlsl", "GrayscaleCS", "cs_5_0");
Microsoft::WRL::ComPtr<ID3D11ComputeShader> compute_shader;
device->CreateComputeShader(cs_bytecode->GetBufferPointer(), cs_bytecode->GetBufferSize(), nullptr, &compute_shader);
```

```cpp
// ② 出力のテクスチャ（UAV つき）を作る。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;                   // UAV は、_SRGB を指定できない
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
device->CreateTexture2D(&desc, nullptr, &output_texture);
device->CreateUnorderedAccessView(output_texture.Get(), nullptr, &output_uav);
device->CreateShaderResourceView(output_texture.Get(), nullptr, &output_srv);    // 後のパスで、読むなら
```

```cpp
// ③ つないで、起動する。
context->CSSetShader(compute_shader.Get(), nullptr, 0);
context->CSSetShaderResources(0, 1, input_srv.GetAddressOf());                    // t0: 入力
context->CSSetUnorderedAccessViews(0, 1, output_uav.GetAddressOf(), nullptr);     // u0: 出力

const UINT groups_x = (width + 7) / 8;                                            // 切り上げ
const UINT groups_y = (height + 7) / 8;
context->Dispatch(groups_x, groups_y, 1);

// ④ 後始末: UAV と SRV の束縛を外す（次のパスで、同じテクスチャを、読むため）。
ID3D11UnorderedAccessView* null_uav = nullptr;
context->CSSetUnorderedAccessViews(0, 1, &null_uav, nullptr);
ID3D11ShaderResourceView* null_srv = nullptr;
context->CSSetShaderResources(0, 1, &null_srv);
```

<strong>グループの数</strong>は、画面を、グループの、大きさで、割って、<strong>切り上げ</strong>ます（`(width + 7) / 8`）。切り捨てると、右端・下端が、処理されません。

### Dispatch の、グループ数の、計算

| 処理 | `numthreads` | `Dispatch` |
| --- | --- | --- |
| 画面全体（1 スレッド = 1 ピクセル） | `(8, 8, 1)` | `((w + 7) / 8, (h + 7) / 8, 1)` |
| 配列の要素ごと（パーティクル） | `(64, 1, 1)` | `((count + 63) / 64, 1, 1)` |
| 3D テクスチャ（froxel） | `(8, 8, 1)` + z 方向 | `(w / 8, h / 8, depth)` |
| 1 グループ ＝ 1 タイル（ヒストグラム、タイル最大） | `(16, 16, 1)` | `(w / 16, h / 16, 1)` |

最大のグループ数は、各次元で 65535 です。

## groupshared：グループ内の、共有メモリ

1 つのグループの、スレッド同士が、<strong>高速な、共有メモリ</strong>で、データを、やり取りできます。ぼかし（隣のピクセルを、何度も読む）や、リダクション（合計、最大）で、<strong>メモリ アクセスを、減らす</strong>ために、使います。

```hlsl
groupshared float4 s_tile[8 + 2][8 + 2];                    // 8×8 のグループと、その周り 1 ピクセルぶん

[numthreads(8, 8, 1)]
void BlurCS(uint3 id : SV_DispatchThreadID, uint3 local : SV_GroupThreadID) {
  // ① 各スレッドが、自分の位置を、共有メモリに、読み込む（周りの分は、端のスレッドが、追加で読む）
  s_tile[local.y + 1][local.x + 1] = g_input.Load(int3(id.xy, 0));
  // ...（端のスレッドは、周りの 1 ピクセルも読む）...

  GroupMemoryBarrierWithGroupSync();                        // ② 全スレッドの、書き込みが、終わるのを、待つ

  // ③ 共有メモリから、周りの値を、読む（高速）
  float4 sum = 0;
  for (int dy = -1; dy <= 1; ++dy)
    for (int dx = -1; dx <= 1; ++dx) sum += s_tile[local.y + 1 + dy][local.x + 1 + dx];
  g_output[id.xy] = sum / 9.0;
}
```

`GroupMemoryBarrierWithGroupSync()` は、<strong>グループ内の、全スレッドが、ここまで来るのを、待ち</strong>、共有メモリへの、書き込みを、他のスレッドに、見えるようにします。これを、忘れると、他のスレッドが、まだ、書いていない値を、読みます。共有メモリの、大きさは、1 グループあたり 32 KB までです。

## アトミック操作

複数のスレッドが、同じ場所に、同時に、書くときは、アトミック関数を、使います。

| 関数 | 内容 |
| --- | --- |
| `InterlockedAdd(dest, value)` | 足す |
| `InterlockedMin`・`InterlockedMax` | 最小・最大 |
| `InterlockedExchange` | 入れ替え |
| `InterlockedCompareExchange` | 比較して、入れ替え |
| `InterlockedOr`・`And`・`Xor` | ビット演算 |

```hlsl
// ヒストグラム: 各ピクセルが、自分の、ビンを、1 つ増やす。
uint bin = LuminanceToBin(luminance);
InterlockedAdd(s_histogram[bin], 1);                        // groupshared（グループ内で、衝突を、減らす）
```

アトミックは、同じ場所への、書き込みが、直列に、なるので、衝突が、多いと、遅くなります。グループ内の、`groupshared` で、先に、数えてから、グローバルに、足すと、衝突が、減ります。

## 描画パイプラインとの、使い分け

| | 描画（ピクセル シェーダー） | 計算シェーダー |
| --- | --- | --- |
| 出力 | レンダー ターゲット（ROP が、ブレンド・深度） | UAV（任意の場所に、書く） |
| 範囲 | 三角形が、覆う、ピクセル | 自由（ディスパッチの範囲） |
| 共有メモリ | なし | `groupshared` |
| 向く | 3D を描く | ぼかし、リダクション、パーティクル、カリング |

## 注意点

| 注意 | 内容 |
| --- | --- |
| UAV の、フォーマット | `_SRGB` は、UAV に、指定できない。`R8G8B8A8_UNORM` で、作り、色空間は、自分で、変換する |
| 型つき UAV の、読み込み | 読み書きできるのは、`R32_FLOAT`、`R32_UINT`、`R32_SINT` のみ（それ以外は、書き込みだけ。環境の `CheckFeatureSupport` で、追加の、型の、対応を、確認する） |
| SRV と UAV の、同時束縛 | 同じリソースを、同時に、読み書きできない |
| スレッド数 | 1 グループ 64 の倍数（NVIDIA は 32 の倍数、AMD は 64 の倍数が効率的）。8×8 や 16×16 が、無難 |
| `cs_5_0` の、制約 | 1 グループ、最大 1024 スレッド、`groupshared` は 32 KB |

## よくあるミス

??? failure "画面の右端・下端が、処理されない、または、メモリ外に書く"
    `Dispatch` を、切り捨てで、計算した、または、範囲チェックが、無い。`(size + N − 1) / N` と、`if (id.x >= width) return;`。

??? failure "出力が、真っ黒、または、前の値のまま"
    UAV を、`CSSetUnorderedAccessViews` で、束ねていない。SRV と UAV に、同じリソースを、束ねている。`Dispatch` の、グループ数が 0。

??? failure "ぼかしの結果に、縞が出る（共有メモリ）"
    `GroupMemoryBarrierWithGroupSync` を、入れていない。または、バリアを、条件分岐（`if`）の中に、置いて、一部の、スレッドが、到達しない（デッドロック）。

??? failure "`CreateUnorderedAccessView` が、失敗する"
    テクスチャの `BindFlags` に、`UNORDERED_ACCESS` が、無い。`_SRGB` や、圧縮フォーマットを、指定している。

??? failure "別のパスで、結果を、読むと、古い値が、見える"
    UAV の束縛を、外していない。次の、パスで、SRV として、読む前に、UAV を、`nullptr` で、外す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算シェーダー ＝ 描画パイプラインと、別の、自由な、GPU 並列計算
    - [x] `[numthreads]` と `Dispatch`。グループ数は、切り上げ
    - [x] 入力は SRV、出力は UAV。範囲チェックを、入れる
    - [x] グループ内の共有は、`groupshared` + `GroupMemoryBarrierWithGroupSync`
    - [x] 衝突する書き込みは、アトミック。`groupshared` で、先にまとめる
    - [x] 使い終わったら、UAV の束縛を、外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Unordered Access View (UAV)](uav.md)
- [Structured and Raw Buffers](structured-buffer.md)
- [Shaders and Compilation](shaders.md)
- [D3D11 Pass Recipes](pass-recipes.md)
- [Microsoft Learn: Compute Shader Overview](https://learn.microsoft.com/ja-jp/windows/win32/direct3d11/direct3d-11-advanced-stages-compute-shader)
