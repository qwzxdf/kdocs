---
title: Anisotropic Filtering
tags:
  - 描画
---

# Anisotropic Filtering

**地面を斜めから見ると、遠くのテクスチャがぼやけます**。**異方性フィルタリングは、縦と横で別々にフィルタして、ぼけを防ぎます**。このページでは、**異方性フィルタの効果**を説明します。

!!! tip "ポイント"
    - **斜めの面で、ぼけを防ぐ**。
    - **サンプル数（2x〜16x）で、品質とコストが変わる**。
    - **地形では、ほぼ必須**。
    - **設定で ON にするだけ**。

## 異方性フィルタリング
**斜めから見る地面**は、**テクスチャが縦に潰れる**ので、**ぼやけます**。<strong>異方性フィルタリング（16x など）</strong>を**有効**にすると**遠くの地面もくっきり**します。**地形ではほぼ必須**です。

<!-- fig:aniso-footprint:begin -->

<svg class="fig illust motion" data-fig="aniso-footprint" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aniso-footprint" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">斜めから見ると、1 画素が、地面の細長い楕円を覆う</text>
<rect x="90" y="35" width="600" height="300" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<ellipse cx="390" cy="185" rx="24" ry="24" fill="#e5aa28" opacity="0.8" stroke="#e5484d" stroke-width="3"><animate attributeName="ry" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1481;0.2222;0.3704;0.4444;0.5926;0.6667;1.0000" values="24;24;33.941;33.941;70.171;70.171;138.21;138.21"/></ellipse>
<text x="100" y="55" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地面を、真上から見た図（赤い楕円 = 1 画素が覆う範囲）</text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">視線の角度 0 度（真上）: 円。1 画素 = 正方形の領域<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">45 度: 縦に 1.4 倍<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">70 度: 2.9 倍。普通のミップは、長い方に合わせて、ぼやける<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">80 度: 5.8 倍。異方性フィルタリングは、細長い範囲を複数のサンプルで平均する<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aniso-footprint:end -->

## なぜ、斜めから見ると、ぼやけるのか

テクスチャの 1 画素（ピクセル）が、テクスチャの上では、**どんな形の領域に当たるか**を考えます。真上から見ると、画面の 1 画素は、テクスチャの小さな正方形に当たります。**斜めから見る地面では、画面の 1 画素が、テクスチャの上で、細長い楕円**に当たります。

```text
真上から               斜めから（遠い地面）
┌──┐                  ┌──────────────┐
│  │  正方形          └──────────────┘  → 横に細長い楕円
└──┘
```

標準のミップマップ（等方性フィルタ）は、**正方形の領域**しか、平均できません。そこで、細長い領域の、長い方に合わせて、ミップを選ぶと、**短い方向が、必要以上に、ぼける**のです。

| 選び方 | 結果 |
| --- | --- |
| 短い方に合わせる | 長い方向が、ちらつく（エイリアシング） |
| 長い方に合わせる（標準のミップ） | 短い方向が、ぼける |

## 異方性フィルタリングの考え方

異方性（anisotropic）フィルタリングは、**楕円の足跡**を、直接扱います。基礎は、Heckbert（1989）の整理です。

1. 画面の 1 画素が、テクスチャ上で作る楕円の、**長軸と短軸**を求める（画面の微分 `ddx`・`ddy` から）
2. **短軸に合わせた、細かいミップ**を選ぶ
3. 長軸の方向に、**複数のサンプルを並べて、平均する**

サンプルの数は、`長軸 ÷ 短軸` の比で決まり、最大で `MaxAnisotropy` 個になります。

| 比（長軸 ÷ 短軸） | 使うサンプル数 |
| --- | --- |
| 1（真上から） | 1 |
| 4 | 4 |
| 16 | 16（`MaxAnisotropy = 16` のとき） |
| 32（ほぼ水平） | 16（上限） |

実際のハードウェアは、楕円を、**複数のトライリニア サンプルの列**で、近似しています（Feline など、各社の実装は少しずつ違う）。サンプルの数が増えるので、**テクスチャの帯域と、時間が、増えます**。ただし、斜めの面だけが、増える形で、真上を向いた面では、増えません。

## DirectX 11 での設定

サンプラー ステートを作るときに、`Filter` を `D3D11_FILTER_ANISOTROPIC` にして、`MaxAnisotropy` を設定します。

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_ANISOTROPIC;     // 異方性フィルタリング
desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP; // 地形は、繰り返すのでラップ
desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
desc.MaxAnisotropy = 16;                    // 1〜16。大きいほど、品質が高く、重い
desc.MaxLOD = D3D11_FLOAT32_MAX;            // ミップを、すべて使う
desc.ComparisonFunc = D3D11_COMPARISON_NEVER;

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&desc, &sampler);
context->PSSetSamplers(0, 1, sampler.GetAddressOf());
```

| 設定 | 内容 |
| --- | --- |
| `Filter` | `D3D11_FILTER_ANISOTROPIC`（縮小・拡大・ミップの、すべてが、異方性） |
| `MaxAnisotropy` | 最大サンプル数。1 で、異方性なし。2、4、8、16 |
| ミップが、あること | 異方性フィルタは、ミップマップを、使う。ミップのないテクスチャでは、効かない |

## どのくらい効くか

| 設定 | 見た目 | コスト（斜めの面） |
| --- | --- | --- |
| トライリニア（異方性なし） | 遠くの地面が、ぼやける | 1 倍 |
| 2x | 少し改善 | 約 2 倍 |
| 4x | 中程度の斜めまで、くっきり | 約 4 倍 |
| 8x | 低い視点でも、ほぼ、くっきり | 約 8 倍 |
| 16x | ほぼ水平の面まで、くっきり | 約 16 倍 |

ただし、「斜めの面の、テクスチャ読み込みだけ」の倍率です。ゲーム全体のフレーム時間は、そこまで増えません（ほかの処理が、ほとんどのため）。**近年の GPU では、16x でも、コストは小さい**ことが多いです。

## 地形では、ほぼ必須

地形は、**視点が低く、地面が、ほぼ水平に見える**ことが多い対象です。遠くの地面は、画面の中で、ほぼ水平で、異方性の比が、非常に大きくなります。異方性フィルタリングがないと、**中景から遠景で、地面のテクスチャが、ぼけた絵の具のように見えます**。

### 注意点

| 項目 | 内容 |
| --- | --- |
| トライプラナーとの併用 | 3 方向の、それぞれに効く。コストは 3 倍になる（[Triplanar Mapping](triplanar.md)） |
| 法線マップ | 異方性は、法線マップにも効く。ぼけると、スペキュラーが、不自然になる |
| 頂点シェーダー | 頂点では、`SampleLevel` で、ミップを指定する（異方性は、画素の微分から決めるので、頂点では使えない） |
| 設定の入れ替え | ユーザー設定で、1x〜16x を、切り替えられるように、しておく |

## よくあるミス

??? failure "遠くの地面が、ぼやけている"
    **異方性フィルタリング（8x〜16x）**を有効にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **斜めの面のぼけを防ぐ**

## 参考

- Heckbert, "Fundamentals of Texture Mapping and Image Warping", Master's thesis, UC Berkeley, 1989（楕円の足跡を使うフィルタリングの基礎）
- McCormack, Perry, Farkas, Jouppi, "Feline: Fast Elliptical Lines for Anisotropic Texture Mapping", SIGGRAPH 1999
- Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_ANISOTROPIC` と `MaxAnisotropy`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（テクスチャのフィルタリングの章）

## 関連ページ

- [Terrain Texturing](index.md)
- [メッシュとテクスチャ](../../../3d/mesh-textures.md)
