---
title: MSAA
tags:
  - 描画
---

# MSAA

<strong>MSAA（マルチサンプル アンチエイリアス）</strong>は、**三角形の縁だけを、1 画素に複数のサンプル点で判定して、滑らかにする**方式です。**ピクセル シェーダーは 1 画素につき 1 回だけ**走るので、**画素を全部 4 倍や 8 倍に増やす SSAA より、はるかに安い**のに**ジオメトリの縁のジャギーはしっかり消せます**。ただし、**シェーダー内のエイリアシングには効かず、ディファード レンダリングとは相性が悪い**という**弱点**があります。このページでは、**SSAA との違い・サンプル パターン・カバレッジとリゾルブ・DX11 の設定・弱点と対処**を説明します。

!!! tip "ポイント"
    - MSAA ＝ <strong>1 画素に複数のサンプル点（2・4・8）</strong>。<strong>三角形が各サンプルを覆うかを判定</strong>。
    - <strong>ピクセル シェーダーは 1 画素 1 回</strong>。<strong>覆ったサンプルすべてに同じ色を書く</strong>。
    - 縁の画素だけ<strong>サンプルごとに色が違う</strong>→ <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。
    - <strong>効く</strong>のは<strong>ジオメトリの縁</strong>。<strong>効かない</strong>のは<strong>シェーダー内・テクスチャ内</strong>のエイリアシング。
    - <strong>メモリと帯域が サンプル数 倍</strong>。<strong>ディファードの G バッファは特に重い</strong>。
    - <strong>VR・モバイル（タイルベース）</strong>では<strong>今も現役</strong>。

## SSAA との違い

<strong>SSAA（スーパー サンプリング）</strong>は、**画面全体を縦横 2 倍（面積 4 倍）で描いて縮小**する方式です。**最も高品質**ですが**ピクセル シェーダーも 4 倍回るので、非常に重い**です。

| 方式 | ピクセル シェーダー | メモリ | 縁 | シェーダー内 |
| --- | --- | --- | --- | --- |
| **SSAA 4x** | **4 倍** | **4 倍** | **滑らか** | **滑らか** |
| **MSAA 4x** | **1 倍** | <strong>4 倍（カラー・深度）</strong> | **滑らか** | **効かない** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="MSAA のサンプル">
<text x="20" y="26" class="fig-title">MSAA：縁をまたぐ画素だけ、サンプルごとに「覆っているか」を判定</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">1 サンプル（通常）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g fill="#334155"><rect x="80" y="80" width="80" height="80" opacity="0.6"/></g>
<circle cx="120" cy="120" r="4" fill="#fff"/>
<text x="0" y="182" style="font-size:12px">画素の中心だけで判定 → 全部か、ゼロ</text>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">4 サンプル（MSAA 4x）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g stroke="#94a3b8"><line x1="80" y1="0" x2="80" y2="160"/><line x1="0" y1="80" x2="160" y2="80"/></g>
<circle cx="50" cy="50" r="5" fill="#94a3b8"/><circle cx="110" cy="40" r="5" fill="#94a3b8"/><circle cx="40" cy="110" r="5" fill="#2563eb"/><circle cx="110" cy="115" r="5" fill="#2563eb"/>
<text x="0" y="182" style="font-size:12px">4 点のうち 2 点が内側 → 50 % の色</text>
</g>
<g font-size="13"><text x="520" y="100" style="font-weight:700">リゾルブ（解像）</text>
<text x="520" y="124">各画素のサンプルを平均して</text>
<text x="520" y="146">最終的な 1 画素の色にする</text></g>
</svg>

## 仕組み

| 手順 | 内容 |
| --- | --- |
| **① 各サンプルのカバレッジ** | **三角形が画素内の複数のサンプル点を、それぞれ覆うかを判定**（ラスタライザ） |
| **② ピクセル シェーダーは 1 回** | **画素ごとに 1 回、色を計算**（**画素の中心付近**） |
| **③ 覆ったサンプルに書く** | **その色を覆ったサンプルすべてに書く**（**深度はサンプルごとに別**） |
| **④ リゾルブ** | **各画素のサンプルを平均して、1 つの色に** |

**内側の画素**は**全サンプルが同じ色**なので、**平均しても変わりません**。**縁の画素**だけ、<strong>サンプルごとに色が違い（三角形の色と背景の色）</strong>、**平均すると中間色になり、滑らか**になります。

## サンプル パターン

**サンプル点の位置**は、**規則格子ではなく、回転した（ずらした）配置**が使われます。

| サンプル数 | 配置の特徴 |
| --- | --- |
| **2x** | **斜めに 2 点** |
| **4x** | <strong>回転した格子（RGSS）</strong>。**水平・垂直の縁で異なる段階を作れる** |
| **8x** | **さらに多様な位置** |

**規則格子**（**縦横にそろう**）だと**水平・垂直に近い縁でサンプルの高さが同じになり、段階が減ります**。**回転・ずらした配置**にすると**どの傾きの縁でも多くの段階**が**得られます**。

## DX11 での設定

```cpp
DXGI_SAMPLE_DESC sample_desc = {4, 0};

D3D11_TEXTURE2D_DESC color_desc = {};
color_desc.Width = width;
color_desc.Height = height;
color_desc.MipLevels = 1;
color_desc.ArraySize = 1;
color_desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
color_desc.SampleDesc = sample_desc;
color_desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&color_desc, nullptr, msaa_color.GetAddressOf());

context->ResolveSubresource(resolved.Get(), 0, msaa_color.Get(), 0, DXGI_FORMAT_R16G16B16A16_FLOAT);
```

| 点 | 説明 |
| --- | --- |
| **`SampleDesc = {4, 0}`** | **4x MSAA**。**カラーも深度も同じサンプル数** |
| **`ResolveSubresource`** | **ハードウェアがサンプルを平均して、1 サンプルの画像へ** |
| **HDR の注意** | **リゾルブは単純平均**なので、**明るい点が混ざって、トーンマップ後の見た目が悪化**することがある（**後述**） |

### HDR でのリゾルブの注意

<strong>HDR（値が 1 を超える）</strong>を**そのまま平均**すると**明るい点が支配的になり、トーンマップ後に縁がジャギーのまま見えます**。**対策**：

| 方法 | 内容 |
| --- | --- |
| **トーンマップしてから、リゾルブ** | **サンプルごとにトーンマップ（またはその近似）し、平均して戻す** |
| **カスタム リゾルブ** | **コンピュート シェーダーで、サンプルを読み、輝度で重み付けして平均**（**ファイアフライ対策と同様**） |

## 弱点

| 弱点 | 理由 | 対処 |
| --- | --- | --- |
| **シェーダー内のエイリアシングに効かない** | **シェーダーは 1 画素 1 回** | **TAA・スペキュラ AA** |
| **アルファ テストの縁に効かない** | **テクスチャのアルファ判定は、画素単位** | <strong>A2C（アルファ トゥ カバレッジ）</strong> |
| **ディファードで重い** | **G バッファがサンプル数 倍** | **フォワード系・MSAA を諦める** |
| **メモリと帯域が サンプル数 倍** | **深度・カラーのサンプルが増える** | **サンプル数を下げる・圧縮に頼る** |
| **ポストプロセスと相性が悪い** | **リゾルブ前のサンプルは、画面全体の加工に使いにくい** | **リゾルブしてから加工** |

### アルファ トゥ カバレッジ（A2C）

**葉・フェンスのアルファ テスト**の縁は、**MSAA で滑らかになりません**。**A2C** を**有効にする**と、**ピクセル シェーダーが出力したアルファを、カバレッジ マスクに変換**し、**サンプルごとに覆う・覆わないを決めます**。

```cpp
D3D11_BLEND_DESC blend = {};
blend.AlphaToCoverageEnable = TRUE;
```

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| <strong>フォワード ＋ MSAA（VR・モバイル）</strong> | <strong>タイルベース GPU は、MSAA がほぼ無料（タイル内で解決）</strong> |
| **MSAA ＋ TAA** | **縁は MSAA、残りは TAA で**（**重くなる**） |
| **A2C で葉・フェンス** | **アルファ テストの縁も滑らかに** |
| **HDR はトーンマップ後の見た目でリゾルブ** | **明るい点でジャギーが復活しないよう** |
| **スペキュラ AA を併用** | **シェーダー内のちらつきは、別に対策**（法線の分散を粗さに足す） |

## よくあるミス

??? failure "MSAA を有効にしたのに、スペキュラのちらつきが消えない"
    **MSAA はジオメトリの縁だけ**。**TAA・スペキュラ AA** を使う。

??? failure "HDR でリゾルブして、明るい縁がジャギーに見える"
    **トーンマップしてからリゾルブ**、または**重み付きリゾルブ**。

??? failure "ディファードで MSAA を有効にして、極端に重くなる"
    **G バッファが全サンプル分**。**フォワード系にするか、TAA に切り替える**。

??? failure "葉のアルファ テストの縁が、ジャギーのまま"
    <strong>A2C（`AlphaToCoverageEnable`）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MSAA ＝ <strong>1 画素に複数サンプル</strong>。<strong>縁だけサンプルごとに判定</strong>。<strong>シェーダーは 1 回</strong>
    - [x] <strong>ジオメトリの縁に効く</strong>が、<strong>シェーダー内には効かない</strong>
    - [x] <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。<strong>HDR ではリゾルブの順序に注意</strong>
    - [x] <strong>メモリ・帯域が サンプル数 倍</strong>。<strong>ディファードとは相性が悪い</strong>
    - [x] <strong>A2C</strong> で<strong>アルファ テストの縁</strong>も

## 参考

- Akeley, "RealityEngine Graphics"（SIGGRAPH 1993）
- Microsoft, "Multisampling Anti-Aliasing"（Microsoft Learn）
- Pettineo, "A Quick Overview of MSAA"（The Danger Zone）

## 関連ページ

- [アンチエイリアシング](index.md)
- [FXAA](fxaa.md)
- [TAA](taa.md)
- [比較と選び方](comparison.md)
- [ラスタライズ（MSAA）](../../../3d/render-flow/rasterize.md)
