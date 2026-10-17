---
title: ガンマと HDR 出力
tags:
  - 描画
---

# ガンマと HDR 出力

**トーンマップの出力は、リニア（光の量に比例）の 0〜1**です。**ディスプレイに出す前に、sRGB の曲線（ガンマ ≒ 2.2）を掛ける**必要があり、**これを間違えると画面全体が暗く潰れたり、白っぽくなったり**します。**HDR ディスプレイでは、さらに別の出力**（HDR10・scRGB）になります。このページでは、**なぜガンマが要るか・sRGB 変換の位置・レンダー ターゲットの作り方・HDR ディスプレイへの出し方・UI の扱い**を説明します。

!!! tip "ポイント"
    - 光の計算は<strong>リニア空間</strong>。<strong>画像やディスプレイは、暗部を細かく持つガンマ空間</strong>。
    - <strong>sRGB 変換はトーンマップの後・最後</strong>。<strong>前にすると暗部が潰れる</strong>。
    - <strong>`_SRGB` 形式のレンダー ターゲット</strong>に<strong>書けば、ハードウェアが自動変換</strong>する。
    - <strong>テクスチャ（色）は `_SRGB` で読む</strong>。<strong>法線・粗さなどのデータは UNORM</strong>。
    - <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ・別の出力形式</strong>（PQ・Rec.2020）。
    - <strong>UI</strong>は<strong>ペーパー ホワイト</strong>を<strong>別に調整して合成</strong>する。

## なぜガンマがあるのか

**人間の目は暗い所の違いに敏感**で**明るい所の違いには鈍感**です。**8 ビット（256 段階）に、明るさを比例で割り当てると**、**暗部の段階が少なすぎて、縞（バンディング）が出ます**。**そこで暗部に多くの段階を割り当てる曲線**（**ガンマ**）を**かけて保存**します。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="ガンマ曲線">
<text x="20" y="26" class="fig-title">リニアと sRGB：同じ 8 ビットでも、暗部の段階が増える</text>
<line x1="80" y1="240" x2="420" y2="240" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="240" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,240 420,50"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,240 90,215 110,190 140,165 180,140 230,115 290,92 350,70 420,50"/>
<text x="425" y="56" style="font-size:12px">sRGB（ガンマ）</text><text x="425" y="240" style="font-size:12px;fill:#64748b">リニアの値 →</text>
<text x="40" y="150" style="font-size:12px">保存値</text>
<g font-size="13">
<text x="480" y="90" style="font-weight:700">リニア値 0.2 を保存すると</text>
<text x="480" y="114">・sRGB なら 約 0.48（0〜255 で 約 124）</text>
<text x="480" y="138">・暗部（0〜0.2）に 約 124 段階を使える</text>
<text x="480" y="172" style="font-weight:700">ガンマが無いと</text>
<text x="480" y="196">・暗部（0〜0.2）に 約 51 段階だけ → 縞が出る</text>
</g>
</svg>

| 空間 | 用途 |
| --- | --- |
| **リニア** | **光の計算・合成・ブルーム・トーンマップ**（**物理的に正しい足し算ができる**） |
| <strong>sRGB（ガンマ）</strong> | **保存・表示**（**画像ファイル・ディスプレイ**） |

## 変換の位置

| 段階 | 空間 |
| --- | --- |
| <strong>テクスチャの読み込み（色）</strong> | **sRGB → リニア**（`_SRGB` 形式で自動） |
| **ライティング・露出・ブルーム・トーンマップ** | **リニア** |
| **画面への出力** | **リニア → sRGB**（最後。`_SRGB` の RTV で自動） |

**ガンマ変換をトーンマップの前に入れる**と、**暗部が潰れて眠い絵**になります（**典型的な事故**）。

## sRGB の式

<div class="formula">
sRGB(c) = 12.92 · c　　（c ≦ 0.0031308）<br>
sRGB(c) = 1.055 · c^(1/2.4) − 0.055　　（それ以外）
</div>

```hlsl
float3 LinearToSRGB(float3 c) {
  float3 low = c * 12.92;
  float3 high = 1.055 * pow(max(c, 0.0), 1.0 / 2.4) - 0.055;
  return (c <= 0.0031308) ? low : high;
}

float3 SRGBToLinear(float3 c) {
  float3 low = c / 12.92;
  float3 high = pow((c + 0.055) / 1.055, 2.4);
  return (c <= 0.04045) ? low : high;
}
```

| 近似 | 内容 |
| --- | --- |
| **`pow(c, 1/2.2)`** | **よく使われる近似**。**暗部で少しずれる** |
| **正確な sRGB** | **上の区分式**。**ハードウェアの自動変換はこちら** |

## DX11 での設定

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;

D3D11_RENDER_TARGET_VIEW_DESC rtv_desc = {};
rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv_desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv_desc, rtv.GetAddressOf());
```

| 点 | 説明 |
| --- | --- |
| **スワップチェーンの形式は UNORM** | **FLIP モデルでは `_SRGB` のスワップチェーンが作れない**ので、**RTV だけを `_SRGB` にする** |
| **RTV を `_SRGB` に** | **シェーダーのリニアな出力を、ハードウェアが sRGB に変換して書く** |
| **シェーダーで `pow` しない** | **RTV が `_SRGB` なら、二重にガンマがかかり、白っぽくなる** |

### テクスチャの読み込み

| テクスチャ | 形式 | 理由 |
| --- | --- | --- |
| <strong>アルベド（色）</strong> | **`_SRGB`** | **画像が sRGB で保存されているので、読み込み時にリニアへ** |
| **法線マップ** | <strong>UNORM（リニア）</strong> | **データであって、色ではない** |
| **粗さ・金属度・AO** | **UNORM** | **同上** |
| **HDR テクスチャ** | **FLOAT** | **すでにリニア** |

## HDR ディスプレイへの出力

**HDR ディスプレイは、SDR より広い明るさ（数百〜数千ニト）と広い色域**を**出せます**。**SDR 用のトーンマップの結果をそのまま送る**と、**HDR の良さが活きません**。

| 項目 | 内容 |
| --- | --- |
| **色空間** | **Rec.2020**（広い色域） |
| **伝達関数** | <strong>PQ（ST.2084）</strong>：**絶対的な明るさ（ニト）を、10 ビットに効率よく入れる曲線** |
| **スワップチェーン形式** | <strong>`R10G10B10A2_UNORM`（HDR10）</strong>、または <strong>`R16G16B16A16_FLOAT`（scRGB）</strong> |
| **色空間の設定** | **`IDXGISwapChain3::SetColorSpace1`** で **`DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020`** |
| **トーンマップ** | **ディスプレイの最大輝度（ニト）に合わせた HDR 用の曲線**。**SDR 用とは別** |

```cpp
swap_chain->SetColorSpace1(DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020);
```

```hlsl
float3 LinearToPQ(float3 nits) {
  const float m1 = 0.1593017578125;
  const float m2 = 78.84375;
  const float c1 = 0.8359375;
  const float c2 = 18.8515625;
  const float c3 = 18.6875;
  float3 y = pow(nits / 10000.0, m1);
  return pow((c1 + c2 * y) / (1.0 + c3 * y), m2);
}
```

| 点 | 説明 |
| --- | --- |
| **`nits / 10000`** | **PQ は 10,000 ニトを 1 とする** |
| **最大輝度を取得** | **`IDXGIOutput6::GetDesc1`** で**ディスプレイの最大輝度**を**得て、曲線のロールオフに使う** |

### ペーパー ホワイトと UI

**HDR では、「白」の明るさに決まりがありません**。**UI の白をゲーム画面の最大輝度で出すと、まぶしすぎる**ので、**UI の白を「ペーパー ホワイト」（約 200〜300 ニト）に決め**、**ゲーム画面とは別に変換して合成**します。

| 要素 | 扱い |
| --- | --- |
| **ゲーム画面** | **HDR 用トーンマップ → PQ** |
| **UI** | **ペーパー ホワイトに合わせたニトに変換 → 合成** |
| **ユーザー設定** | **最大輝度・ペーパー ホワイトを調整できるように** |

## よくあるミス

??? failure "ガンマ変換を二重にして、全体が白っぽい"
    **RTV が `_SRGB` なら、シェーダーで `pow` しない**。

??? failure "ガンマ変換が無くて、全体が暗く潰れる"
    **リニアのまま UNORM に書いている**。**`_SRGB` の RTV にする**。

??? failure "法線マップを `_SRGB` で読んで、ライティングが崩れる"
    **データのテクスチャは UNORM**。

??? failure "SDR 用の曲線を HDR ディスプレイにそのまま出して、地味"
    **HDR 用のトーンマップ**と**PQ の出力**を使う。

??? failure "HDR で UI がまぶしすぎる"
    **ペーパー ホワイトを決めて、UI を別に変換**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>計算はリニア、保存・表示は sRGB</strong>。<strong>ガンマは最後</strong>
    - [x] <strong>RTV を `_SRGB`</strong> にすれば<strong>自動変換</strong>。<strong>シェーダーで `pow` しない</strong>
    - [x] <strong>色テクスチャは `_SRGB`、データは UNORM</strong>
    - [x] <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ ＋ PQ ＋ Rec.2020</strong>
    - [x] <strong>UI はペーパー ホワイト</strong>で<strong>別に合成</strong>

## 参考

- Microsoft, "DXGI Color Space"・"High Dynamic Range and Wide Color Gamut"（Microsoft Learn）
- SMPTE ST 2084, "High Dynamic Range Electro-Optical Transfer Function"
- IEC 61966-2-1, "sRGB"

## 関連ページ

- [トーンマッピングと露出](index.md)
- [露出](exposure.md)
- [カラー グレーディング](../color-grading/index.md)
- [画面に出す](../../../3d/render-flow/present.md)
