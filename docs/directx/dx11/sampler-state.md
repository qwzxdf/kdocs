---
title: Sampler State
tags:
  - DirectX
---

# Sampler State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>サンプラー ステート</strong>は、テクスチャを、<strong>どう読むか</strong>の、設定です。uv が、テクセルの、ちょうど、真ん中に、当たらないとき、周りを、混ぜるのか（フィルタリング）、uv が、0〜1 の、外に、出たとき、どうするのか（アドレス モード）、ミップを、どう選ぶか。これらを、<strong>テクスチャの、データとは、別</strong>に、サンプラーで、決めます。同じテクスチャを、別のサンプラーで、別の読み方が、できます。

!!! tip "ポイント"
    - サンプラー ＝ 読み方の設定（フィルタ、アドレス、異方性、ミップ）。テクスチャとは、別。
    - 作成は `CreateSamplerState`、束縛は `PSSetSamplers`。HLSL では `SamplerState g_sampler : register(s0);`。
    - 普通の、テクスチャ貼りは、`ANISOTROPIC`（またはトライリニア）+ `WRAP`。
    - G バッファ、深度、LUT は、`POINT` または `LINEAR` + `CLAMP`。
    - シャドウ マップは、<strong>比較サンプラー</strong>（`COMPARISON_*`）で、ハードウェアが、PCF する。

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
| `Filter` | 拡大・縮小・ミップの、補間の方法（下の表） |
| `AddressU`・`V`・`W` | uv が、0〜1 の外に、出たときの、扱い |
| `MipLODBias` | ミップの選択に、足す、偏り（正でぼける、負でシャープ。TAA では、負にする） |
| `MaxAnisotropy` | 異方性フィルタの、倍率（`Filter` が `ANISOTROPIC` のとき） |
| `ComparisonFunc` | 比較サンプラーの、比較関数 |
| `BorderColor` | `BORDER` の、外側の色 |
| `MinLOD`・`MaxLOD` | 使える、ミップの範囲。`MaxLOD = D3D11_FLOAT32_MAX` で、全段 |

## フィルタリング

テクスチャを、拡大・縮小するとき、uv の、位置の、色を、どう求めるかです。

| `Filter` | 内容 | 見た目 | コスト |
| --- | --- | --- | --- |
| `MIN_MAG_MIP_POINT` | 最も近い、テクセル 1 つ | ブロック状（ドット絵、ID、データ） | 最小 |
| `MIN_MAG_LINEAR_MIP_POINT` | 隣の 4 テクセルを、補間（バイリニア）。ミップは、近い段 | なめらか、ミップの切り替えが、見える | 小 |
| `MIN_MAG_MIP_LINEAR` | バイリニア + ミップ間も、補間（トライリニア） | なめらか、継ぎ目なし | 中 |
| `ANISOTROPIC` | 斜めの面で、細長い範囲を、複数回、読む | 斜めの面でも、ぼけない | 大（倍率に比例） |

<strong>異方性フィルタリング</strong>は、地面のように、視線に、対して、斜めの面で、効きます。トライリニアだと、斜めの面は、遠くが、ぼやけますが、異方性（倍率 8〜16）は、遠くまで、くっきりします。

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

比較サンプラーは、`SamplerComparisonState` と、`SampleCmp` 系の関数で、使います（[PCF](../../graphics/shadows/pcf.md)）。

## アドレス モード

uv が、0〜1 の範囲の外に、出たときの、扱いです。

| `AddressU/V/W` | 内容 | 使いどころ |
| --- | --- | --- |
| `WRAP` | 繰り返す（0.2 と 1.2 が、同じ位置） | 床・壁のタイル |
| `MIRROR` | 反転しながら、繰り返す | 継ぎ目が、目立つ、タイル |
| `CLAMP` | 端の、テクセルを、引き伸ばす | G バッファ、ポスト プロセス、LUT（はみ出さない） |
| `BORDER` | 範囲外は、`BorderColor` | シャドウ マップの、範囲外 |
| `MIRROR_ONCE` | 1 回だけ、反転して、あとは、`CLAMP` | 特殊 |

## よく使う、サンプラーの、組み合わせ

| 名前 | `Filter` | アドレス | 用途 |
| --- | --- | --- | --- |
| `linear_wrap` | `MIN_MAG_MIP_LINEAR` | `WRAP` | 一般的な、テクスチャ貼り |
| `linear_clamp` | `MIN_MAG_MIP_LINEAR` | `CLAMP` | ポスト プロセス、LUT、プローブ |
| `point_clamp` | `MIN_MAG_MIP_POINT` | `CLAMP` | G バッファ、深度、ID（補間したくない） |
| `anisotropic_wrap` | `ANISOTROPIC` | `WRAP` | 地面・壁の、高品質な、貼り |
| `shadow_cmp` | `COMPARISON_MIN_MAG_LINEAR_MIP_POINT` | `BORDER`（1） | シャドウ マップ |

これらを、起動時に、作って、スロットを、固定（`s0`〜`s4`）に、すると、全パスで、同じ、サンプラーを、使い回せます。

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

サンプラーは、1 つのシェーダーに、最大 16 個（スロット 0〜15）まで、つなげます。

## サンプラーの、作成数の、上限

デバイスごとに、作れる、サンプラー ステートの数は、<strong>4096 個</strong>までで、同じ設定の、サンプラーを、複数回、作っても、同じ、オブジェクトが、返ります（キャッシュされる）。

## よくあるミス

??? failure "床の遠くが、ぼやける（または、ちらつく）"
    ミップが、無い、または、異方性が、1。ミップを、作り、`ANISOTROPIC`（倍率 8 以上）にする。

??? failure "画面端が、引き伸ばされて、見える（ポスト プロセス）"
    `WRAP` のまま、画面の外を、読んでいる。`CLAMP` にする。ただし、画面端の、ぼかしは、端の、色が、そのまま、伸びる。

??? failure "G バッファや、深度を、読んだ値が、ぼやける"
    `LINEAR` で、読んでいる。法線や、深度は、補間すると、境界で、別の面の値が、混ざる。`POINT`（または `Load`）で、読む。

??? failure "シャドウ マップの、比較が、常に、0 か 1（PCF が、効かない）"
    普通の、サンプラー（`Filter` が `COMPARISON_` でない）で、`SampleCmp` を、呼んでいる。比較サンプラーを、作る。

??? failure "サンプラーを、設定し忘れて、何も、読めない"
    `PSSetSamplers` を、呼んでいない。サンプラーの、スロットが、既定で、空（`nullptr`）の、サンプラーは、黒を、返す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サンプラー ＝ テクスチャの、読み方の設定（フィルタ・アドレス・異方性）
    - [x] `CreateSamplerState`、`PSSetSamplers`、HLSL の `register(s#)`
    - [x] 貼る絵は、`ANISOTROPIC` + `WRAP`。G バッファ・深度は、`POINT` + `CLAMP`
    - [x] シャドウ マップは、比較サンプラー（`COMPARISON_*`、`SampleCmp`）
    - [x] 共通のサンプラーを、起動時に、作って、スロットを、固定する

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Texture2D](texture2d.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [PCF](../../graphics/shadows/pcf.md)
- [Microsoft Learn: ID3D11Device::CreateSamplerState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createsamplerstate)
