---
title: Heightmap LOD (Mips)
tags:
  - 描画
---

# Heightmap LOD (Mips)

<strong>遠くの地形は高さマップも粗くてよく、ミップマップが使えます</strong>。LOD に応じて読むミップを選ぶと、テクスチャのちらつきと帯域を減らせます。このページでは高さマップのミップを説明します。

!!! tip "ポイント"
    - 高さマップにもミップを作る。
    - 頂点の LOD に合わせて、ミップを選ぶ。
    - ミップで高さの平均を取ると、山が低くなる。
    - 最大・最小のミップも用意すると、カリングに使える。

## 高さマップの LOD（ミップ）
<strong>メッシュだけでなく高さマップもミップを使います</strong>。遠くの頂点は粗いミップから読むとちらつかず、メモリ アクセスも減ります。

対応の要点です。ミップ レベルは LOD レベルに対応し、LOD が 1 下がるごとに、ミップを 1 上げます。高さのミップは平均でよいですが、最大値のミップもカリングに使えます。最小・最大の高さはノードの境界ボックスに使います。

<!-- fig:height-mip-bars:begin -->

<svg class="fig illust motion" data-fig="height-mip-bars" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-mip-bars" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">高さのミップ: 隣り合う高さを平均して、半分の大きさを作る。遠景は粗い層で、足りる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 次元の高さ 16 点。層 0(16 点)→ 層 1(8 点)→ 層 2(4 点)→ 層 3(2 点)。層が粗いほど、元の地形との差が増える</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="302.4" width="46.0" height="57.6" fill="#64748b" opacity="0.35"/>
<rect x="122.0" y="308.8" width="46.0" height="51.2" fill="#64748b" opacity="0.35"/>
<rect x="172.0" y="313.41" width="46.0" height="46.59" fill="#64748b" opacity="0.35"/>
<rect x="222.0" y="256.37" width="46.0" height="103.63" fill="#64748b" opacity="0.35"/>
<rect x="272.0" y="208.31" width="46.0" height="151.69" fill="#64748b" opacity="0.35"/>
<rect x="322.0" y="213.65" width="46.0" height="146.35" fill="#64748b" opacity="0.35"/>
<rect x="372.0" y="276.29" width="46.0" height="83.71" fill="#64748b" opacity="0.35"/>
<rect x="422.0" y="269.32" width="46.0" height="90.68" fill="#64748b" opacity="0.35"/>
<rect x="472.0" y="205.49" width="46.0" height="154.51" fill="#64748b" opacity="0.35"/>
<rect x="522.0" y="212.05" width="46.0" height="147.95" fill="#64748b" opacity="0.35"/>
<rect x="572.0" y="218.53" width="46.0" height="141.47" fill="#64748b" opacity="0.35"/>
<rect x="622.0" y="278.7" width="46.0" height="81.3" fill="#64748b" opacity="0.35"/>
<rect x="672.0" y="247.03" width="46.0" height="112.97" fill="#64748b" opacity="0.35"/>
<rect x="722.0" y="255.28" width="46.0" height="104.72" fill="#64748b" opacity="0.35"/>
<rect x="772.0" y="211.7" width="46.0" height="148.3" fill="#64748b" opacity="0.35"/>
<rect x="822.0" y="222.26" width="46.0" height="137.74" fill="#64748b" opacity="0.35"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">層 0(16 点): 元との差(平均)0.00 / 最大 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="305.6" width="96.0" height="54.4" fill="#2563eb" opacity="0.55"/>
<rect x="172.0" y="284.89" width="96.0" height="75.11" fill="#2563eb" opacity="0.55"/>
<rect x="272.0" y="210.98" width="96.0" height="149.02" fill="#2563eb" opacity="0.55"/>
<rect x="372.0" y="272.8" width="96.0" height="87.2" fill="#2563eb" opacity="0.55"/>
<rect x="472.0" y="208.77" width="96.0" height="151.23" fill="#2563eb" opacity="0.55"/>
<rect x="572.0" y="248.61" width="96.0" height="111.39" fill="#2563eb" opacity="0.55"/>
<rect x="672.0" y="251.15" width="96.0" height="108.85" fill="#2563eb" opacity="0.55"/>
<rect x="772.0" y="216.98" width="96.0" height="143.02" fill="#2563eb" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">層 1(8 点): 元との差(平均)0.28 / 最大 0.84</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="295.25" width="196.0" height="64.75" fill="#2ea043" opacity="0.55"/>
<rect x="272.0" y="241.89" width="196.0" height="118.11" fill="#2ea043" opacity="0.55"/>
<rect x="472.0" y="228.69" width="196.0" height="131.31" fill="#2ea043" opacity="0.55"/>
<rect x="672.0" y="234.07" width="196.0" height="125.93" fill="#2ea043" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">層 2(4 点): 元との差(平均)0.64 / 最大 1.39</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/><rect x="72.0" y="268.57" width="396.0" height="91.43" fill="#e5aa28" opacity="0.55"/>
<rect x="472.0" y="231.38" width="396.0" height="128.62" fill="#e5aa28" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">層 3(2 点): 元との差(平均)0.74 / 最大 1.67</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<line x1="70.0" y1="360.0" x2="870.0" y2="360.0" stroke="#94a3b8" stroke-width="2"/>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">点の数:</text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/></text>
<text x="40" y="458" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">元の地形との差(×0.01 m):</text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">64<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">74<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8594;0.8596;1.0000" values="0;0;1;1"/><rect x="440" y="410" width="490" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="456" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">層が 1 つ上がると、点は半分、差は増える(0.00 → 0.74)</text>
<text x="456" y="457" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">遠くは、画面で 1 画素が数 m ぶんなので、粗い層で、見た目が変わらない</text>
<text x="456" y="479" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">遠い頂点を、粗い層から読めば、テクスチャの読み込みが軽く、キャッシュにも優しい</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">高さを、隣と平均して、小さな高さマップを作る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">層を重ねるほど、粗く、小さく<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.8807;0.8809;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離に応じて、層を選ぶ(ミップ)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8807;0.8809;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:height-mip-bars:end -->

## なぜミップが要るのか

遠くの地形を粗い LOD で描くと頂点が、数百メートルおきにしかありません。その頂点が <strong>細かい高さマップの、1 点だけ</strong>を読むとどうなるでしょうか。

高さマップが 1 m ごとに値を持つなら、数百メートル間隔の頂点はその中の 1 点を、たまたま拾います。カメラが少し動いて頂点の位置が、1 m 動くと拾う値が変わります。山の頂上を拾ったり谷を拾ったりして地形が、ちらちら揺れます。 これはテクスチャの縮小で出る、エイリアシングと同じ現象です。

ミップマップは「大きい画像を、半分の大きさに平均して縮めたもの」を、積み重ねたものです（Williams、1983）。頂点の間隔に合ったミップを読めば、その頂点が受け持つ範囲の平均の高さが取れます。

## どのミップを読むか

頂点の間隔が高さマップのテクセルの何個分かで、ミップが決まります。

```text
テクセル数 = 頂点の間隔(m) ÷ 高さマップの 1 テクセルの大きさ(m)
ミップ = log2(テクセル数)
```

| LOD | 頂点の間隔 | 高さマップが 1 m / テクセルのとき | 読むミップ |
| --- | --- | --- | --- |
| 0 | 2 m | 2 テクセル | 1 |
| 1 | 4 m | 4 テクセル | 2 |
| 2 | 8 m | 8 テクセル | 3 |
| 3 | 16 m | 16 テクセル | 4 |

LOD が 1 つ上がるごとに、ミップも 1 つ上がります。これは CDLOD の場合、「レベル = ミップ + 定数」で済みます。

```hlsl
// LOD レベルから、読むミップを決める。
// level は、頂点を持つノードのレベル（0 が最も細かい）。
// base_mip は、レベル 0 の頂点の間隔に、合うミップ。
float HeightMip(float level, float base_mip) {
  return base_mip + level;
}

float SampleHeightLod(float2 world_xz, float level) {
  float2 uv = (world_xz - heightmap_origin) / heightmap_size;
  return g_height.SampleLevel(g_linear_clamp, uv, HeightMip(level, 0.0)) * height_scale + height_offset;
}
```

<strong>連続的な LOD（モーフィングつき）では、ミップも連続的に変える</strong>と切り替えのポップが、さらに目立たなくなります。トライリニア補間が 2 つのミップを自動で混ぜてくれるので `SampleLevel` に、小数のミップ レベルを渡します。

```hlsl
// モーフ係数 morph（0〜1）を使って、ミップを、レベルの間で連続的に動かす。
float mip = level + morph;
float h = g_height.SampleLevel(g_linear_clamp, uv, mip);
```

## 平均だと山が低くなる

ミップは平均で作るのが普通です。しかし、<strong>地形の山は平均すると低くなります</strong>。幅の細い尾根はまわりの谷と平均されて、削られます。

| ミップ | 尾根の高さ（隣は谷 0 m） |
| --- | --- |
| 0（元の高さ） | 100 m |
| 1（2×2 の平均） | 50 m |
| 2（4×4 の平均） | 25 m |

そうすると、遠くの山が近くで見たときより、低く見えます。カメラが近づくと山がせり上がって、地形が膨らむ現象が起きます。

対策は 2 つあります。

| 方法 | 内容 |
| --- | --- |
| 最大値のミップも作る | 縮めるとき、4 つのテクセルの最大値を取る。遠くの山を少し高く見積もる |
| 平均と最大の間で混ぜる | `lerp(average, maximum, 0.5)` のように、中間を取る |

```cpp
// 高さマップのミップを、平均ではなく、最大値で作る例（CPU 側）。
void BuildMaxMip(const std::vector<float>& src, int src_size, std::vector<float>& dst) {
  const int dst_size = src_size / 2;
  dst.resize(static_cast<size_t>(dst_size) * dst_size);
  for (int y = 0; y < dst_size; ++y) {
    for (int x = 0; x < dst_size; ++x) {
      const float a = src[(2 * y) * src_size + 2 * x];
      const float b = src[(2 * y) * src_size + 2 * x + 1];
      const float c = src[(2 * y + 1) * src_size + 2 * x];
      const float d = src[(2 * y + 1) * src_size + 2 * x + 1];
      dst[y * dst_size + x] = std::max(std::max(a, b), std::max(c, d));
    }
  }
}
```

最大値のミップは カリングにも使えます。四分木のノードの AABB の「最大の高さ」は、そのノードが覆う範囲の最大値のミップを、引けば求まります。

## 最小・最大のミップを AABB に使う

CDLOD ではノードごとの AABB が、必要です。高さの最小値と最大値を <strong>ミップ（最小と最大の 2 本）</strong>として持てば、四分木の各ノードの値がミップのテクセルに、1 対 1 で対応します。

| ノードのレベル | 対応するミップ | 内容 |
| --- | --- | --- |
| 葉 | ミップ k | 1 テクセル = 1 ノードの最小・最大 |
| 1 つ上 | ミップ k+1 | 1 テクセル = 4 ノードの最小・最大 |

```cpp
// 四分木のノードの AABB を、最小・最大ミップから作る。
Aabb NodeBounds(int level, int x, int z, const MinMaxMips& mips) {
  const int mip = level + mips.base_mip;
  const float min_y = mips.min[mip].At(x, z);
  const float max_y = mips.max[mip].At(x, z);
  const float size = node_size_at_level[level];
  return {{x * size, min_y, z * size}, {(x + 1) * size, max_y, (z + 1) * size}};
}
```

高さを編集したら その範囲のミップを作り直し、影響する四分木のノードの AABB を、更新します。

## DirectX 11 での、ミップの作り方

高さマップをテクスチャとして作るとき、`MipLevels` を 0 にするとすべてのミップの領域が確保されます。`GenerateMips` は <strong>平均</strong>のミップを作ります（最大値のミップは、自分で作ります）。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = size;
desc.Height = size;
desc.MipLevels = 0;                     // 0 = 全ミップ
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16_UNORM;    // 高さは 16 ビット（線形補間ができる）
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;  // GenerateMips に必要
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;

device->CreateTexture2D(&desc, nullptr, &height_texture);
// 0 番のミップに、高さを書き込んだあと
context->GenerateMips(height_srv.Get());
```

16 ビットの高さは 0〜65535 を `height_scale` で、メートルに直します。8 ビットだと山の高さが 256 段階しかなく、階段が見えます。

!!! note "頂点シェーダーで、ミップを選ぶ"
    頂点シェーダーでは画面の微分（`ddx`、`ddy`）が使えないので `Sample` ではミップが自動では選ばれません。必ず `SampleLevel` でミップを自分で指定します。 指定を忘れてミップ 0 だけを読むと、遠くの地形がちらつきます。

## よくあるミス

??? failure "遠くの山が、低く見える"
    <strong>最大値のミップ</strong>も併用する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] LOD に合わせて、ミップを選ぶ

## 参考

- Williams, "Pyramidal Parametrics", SIGGRAPH 1983（ミップマップの原典）
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009（CDLOD の原典。作者の公開サンプル `fstrugar/CDLOD` が GitHub にある）
- Losasso, Hoppe, "Geometry Clipmaps: Terrain Rendering Using Nested Regular Grids", ACM Transactions on Graphics (SIGGRAPH 2004)
- Microsoft Learn, "ID3D11DeviceContext::GenerateMips"

## 関連ページ

- [Terrain LOD](index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
