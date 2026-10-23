---
title: Sampler State
tags:
  - DirectX
---

# Sampler State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>サンプラー ステート</strong>はテクスチャを <strong>どう読むか</strong>の設定です。uv がテクセルのちょうど真ん中に当たらないとき周りを混ぜるのか（フィルタリング）、uv が 0〜1 の外に出たときどうするのか（アドレス モード）、ミップをどう選ぶか。これらを <strong>テクスチャのデータとは別</strong>にサンプラーで決めます。同じテクスチャを別のサンプラーで、別の読み方ができます。

!!! tip "ポイント"
    - サンプラー ＝ 読み方の設定（フィルタ、アドレス、異方性、ミップ）。テクスチャとは別。
    - 作成は `CreateSamplerState`、束縛は `PSSetSamplers`。HLSL では `SamplerState g_sampler : register(s0);`。
    - 普通のテクスチャ貼りは `ANISOTROPIC`（またはトライリニア）+ `WRAP`。
    - G バッファ、深度、LUT は `POINT` または `LINEAR` + `CLAMP`。
    - シャドウ マップは <strong>比較サンプラー</strong>（`COMPARISON_*`）でハードウェアが、PCF する。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## 作る

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_ANISOTROPIC;                     // 異方性フィルタリング
desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP;                 // uv が 0〜1 を超えたら、繰り返す
desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
desc.MipLODBias = 0.0f;
desc.MaxAnisotropy = 8;                                     // 異方性の、倍率（1〜16）
desc.ComparisonFunc = D3D11_COMPARISON_NEVER;               // 比較しない（普通のサンプラー）
desc.MinLOD = 0.0f;
desc.MaxLOD = D3D11_FLOAT32_MAX;                            // ミップの、全段を、使える

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&desc, &sampler);

context->PSSetSamplers(0, 1, sampler.GetAddressOf());       // スロット 0（HLSL の register(s0)）
```

| メンバー | 内容 |
| --- | --- |
| `Filter` | 拡大・縮小・ミップの補間の方法（下の表） |
| `AddressU`・`V`・`W` | uv が、0〜1 の外に出たときの扱い |
| `MipLODBias` | ミップの選択に足す偏り（正でぼける負でシャープ。TAA では負にする） |
| `MaxAnisotropy` | 異方性フィルタの倍率（`Filter` が `ANISOTROPIC` のとき） |
| `ComparisonFunc` | 比較サンプラーの比較関数 |
| `BorderColor` | `BORDER` の外側の色 |
| `MinLOD`・`MaxLOD` | 使えるミップの範囲。`MaxLOD = D3D11_FLOAT32_MAX` で全段 |

## フィルタリング

テクスチャを拡大・縮小するとき uv の位置の色をどう求めるかです。

| `Filter` | 内容 | 見た目 | コスト |
| --- | --- | --- | --- |
| `MIN_MAG_MIP_POINT` | 最も近いテクセル 1 つ | ブロック状（ドット絵、ID、データ） | 最小 |
| `MIN_MAG_LINEAR_MIP_POINT` | 隣の 4 テクセルを補間（バイリニア）。ミップは近い段 | なめらかミップの切り替えが見える | 小 |
| `MIN_MAG_MIP_LINEAR` | バイリニア + ミップ間も補間（トライリニア） | なめらか、継ぎ目なし | 中 |
| `ANISOTROPIC` | 斜めの面で細長い範囲を複数回、読む | 斜めの面でもぼけない | 大（倍率に比例） |

<strong>異方性フィルタリング</strong>は地面のように視線に対して、斜めの面で効きます。トライリニアだと斜めの面は遠くが、ぼやけますが異方性（倍率 8〜16）は、遠くまでくっきりします。

### 比較サンプラー（シャドウ マップ）

```cpp
// シャドウ マップ用: 読んだ深度と、参照値を、ハードウェアが、比較して、0 か 1 を返す。バイリニアなら、PCF になる。
D3D11_SAMPLER_DESC shadow = {};
shadow.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
shadow.AddressU = shadow.AddressV = shadow.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
shadow.BorderColor[0] = shadow.BorderColor[1] = shadow.BorderColor[2] = shadow.BorderColor[3] = 1.0f;   // 範囲外は、光が当たる
shadow.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
shadow.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&shadow, &shadow_sampler);
```

```hlsl
SamplerComparisonState g_shadow_sampler : register(s1);
Texture2D<float> g_shadow_map : register(t2);

// shadow_uv.z（光から見た深度）と、シャドウ マップの値を比較。結果は 0〜1（PCF で、なめらか）。
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, shadow_uv.xy, shadow_uv.z);
```

比較サンプラーは `SamplerComparisonState` と `SampleCmp` 系の関数で、使います（[PCF](../../graphics/shadows/pcf.md)）。

## アドレス モード

uv が 0〜1 の範囲の外に出たときの扱いです。

| `AddressU/V/W` | 内容 | 使いどころ |
| --- | --- | --- |
| `WRAP` | 繰り返す（0.2 と 1.2 が、同じ位置） | 床・壁のタイル |
| `MIRROR` | 反転しながら繰り返す | 継ぎ目が目立つタイル |
| `CLAMP` | 端のテクセルを引き伸ばす | G バッファ、ポスト プロセス、LUT（はみ出さない） |
| `BORDER` | 範囲外は `BorderColor` | シャドウ マップの範囲外 |
| `MIRROR_ONCE` | 1 回だけ反転してあとは、`CLAMP` | 特殊 |

## よく使うサンプラーの組み合わせ

| 名前 | `Filter` | アドレス | 用途 |
| --- | --- | --- | --- |
| `linear_wrap` | `MIN_MAG_MIP_LINEAR` | `WRAP` | 一般的なテクスチャ貼り |
| `linear_clamp` | `MIN_MAG_MIP_LINEAR` | `CLAMP` | ポスト プロセス、LUT、プローブ |
| `point_clamp` | `MIN_MAG_MIP_POINT` | `CLAMP` | G バッファ、深度、ID（補間したくない） |
| `anisotropic_wrap` | `ANISOTROPIC` | `WRAP` | 地面・壁の高品質な貼り |
| `shadow_cmp` | `COMPARISON_MIN_MAG_LINEAR_MIP_POINT` | `BORDER`（1） | シャドウ マップ |

これらを起動時に作ってスロットを固定（`s0`〜`s4`）にすると全パスで同じサンプラーを使い回せます。

```hlsl
// 共通のサンプラーを、スロットで、固定する。
SamplerState g_linear_wrap : register(s0);
SamplerState g_linear_clamp : register(s1);
SamplerState g_point_clamp : register(s2);
SamplerState g_anisotropic_wrap : register(s3);
SamplerComparisonState g_shadow_cmp : register(s4);
```

## 束縛

```cpp
// 全パスで共通のサンプラーを、一度だけ、つなぐ（フレームの最初）。
ID3D11SamplerState* samplers[] = {linear_wrap.Get(), linear_clamp.Get(), point_clamp.Get(), anisotropic_wrap.Get(),
                                  shadow_cmp.Get()};
context->PSSetSamplers(0, 5, samplers);
context->CSSetSamplers(0, 5, samplers);                     // 計算シェーダーでも、使うなら
```

サンプラーは 1 つのシェーダーに最大 16 個（スロット 0〜15）まで、つなげます。

## サンプラーの作成数の上限

デバイスごとに作れるサンプラー ステートの数は、<strong>4096 個</strong>までで同じ設定のサンプラーを複数回、作っても同じオブジェクトが返ります（キャッシュされる）。

## よくあるミス

??? failure "床の遠くが、ぼやける（またはちらつく）"
    ミップが無いまたは異方性が 1。ミップを作り `ANISOTROPIC`（倍率 8 以上）にする。

??? failure "画面端が、引き伸ばされて見える（ポスト プロセス）"
    `WRAP` のまま画面の外を読んでいる。`CLAMP` にする。ただし、画面端のぼかしは端の色がそのまま伸びる。

??? failure "G バッファや深度を読んだ値がぼやける"
    `LINEAR` で読んでいる。法線や深度は補間すると境界で、別の面の値が混ざる。`POINT`（または `Load`）で読む。

??? failure "シャドウ マップの比較が常に 0 か 1（PCF が効かない）"
    普通のサンプラー（`Filter` が `COMPARISON_` でない）で `SampleCmp` を呼んでいる。比較サンプラーを作る。

??? failure "サンプラーを設定し忘れて何も読めない"
    `PSSetSamplers` を呼んでいない。サンプラーのスロットが既定で、空（`nullptr`）のサンプラーは黒を返す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サンプラー ＝ テクスチャの読み方の設定（フィルタ・アドレス・異方性）
    - [x] `CreateSamplerState`、`PSSetSamplers`、HLSL の `register(s#)`
    - [x] 貼る絵は `ANISOTROPIC` + `WRAP`。G バッファ・深度は `POINT` + `CLAMP`
    - [x] シャドウ マップは、比較サンプラー（`COMPARISON_*`、`SampleCmp`）
    - [x] 共通のサンプラーを起動時に作ってスロットを固定する

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Texture2D](texture2d.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [PCF](../../graphics/shadows/pcf.md)
- [Microsoft Learn: ID3D11Device::CreateSamplerState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createsamplerstate)
