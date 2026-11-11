---
title: Anisotropic Filtering
tags:
  - 描画
---

# Anisotropic Filtering

地形を低い視点から見ると足元の地面はくっきりしているのに、数十メートル先から急にテクスチャが絵の具をこすったようにぼやけます。ミップマップが「縮小するときの平均」を縦と横で同じ量だけ取るので、斜めに寝た面では細くなる方向まで余計にぼけるからです。

<strong>異方性フィルタリングは縦と横で別々の量を平均して、斜めの面のぼけを防ぎます</strong>。地形はほぼ必須の設定です。このページではなぜぼけるのか楕円の足跡、何サンプル取るか HLSL での手書きの例、DirectX 11 の設定、効き方とコストを説明します。

!!! tip "ポイント"
    - 斜めの面では画面の 1 画素がテクスチャの上で細長い楕円になります。標準のミップは正方形しか扱えずぼけるかちらつきます。
    - 異方性フィルタは長軸に沿ってサンプルを並べて、短軸に合わせたミップで読みます。
    - サンプル数は `長軸 ÷ 短軸` の比で決まり `MaxAnisotropy`（最大 16）で頭打ちになります。
    - 低い視点の地形では比が 16 を超える場所が多く、上限が効きます。
    - サンプラー ステートの `Filter` と `MaxAnisotropy` を設定するだけです。ミップのないテクスチャでは効きません。

!!! info "このページを読む前に"
    - [Terrain Texturing](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:aniso-footprint:begin -->

<svg class="fig illust motion" data-fig="aniso-footprint" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-aniso-footprint" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">斜めから見ると、1 画素が地面の細長い楕円を覆う</text>
<rect x="90" y="35" width="600" height="300" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<ellipse cx="390" cy="185" rx="24" ry="24" fill="#e5aa28" opacity="0.8" stroke="#e5484d" stroke-width="3"><animate attributeName="ry" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1481;0.2222;0.3704;0.4444;0.5926;0.6667;1.0000" values="24;24;33.941;33.941;70.171;70.171;138.21;138.21"/></ellipse>
<text x="100" y="55" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">地面を真上から見た図（赤い楕円 = 1 画素が覆う範囲）</text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">視線の角度 0 度（真上）: 円。1 画素 = 正方形の領域<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">45 度: 縦に 1.4 倍<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">70 度: 2.9 倍。普通のミップは、長い方に合わせて、ぼやける<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">80 度: 5.8 倍。異方性フィルタリングは、細長い範囲を複数のサンプルで平均する<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:aniso-footprint:end -->

## なぜ斜めから見るとぼやけるのか {#why}

画面の 1 画素がテクスチャの上でどんな形の領域に当たるかを考えます。真上から見ると 1 画素はテクスチャの小さな正方形に当たります。斜めから見る地面では画面の 1 画素が、テクスチャの上で細長い楕円に当たります。奥へ向かう方向には少ない画素でたくさんのテクセルが詰まるからです。

```text
真上から               斜めから（遠い地面）
┌──┐                  ┌──────────────┐
│  │  正方形          └──────────────┘  → 奥行き方向に長い楕円
└──┘
```

標準のミップマップ（等方性フィルタ）は、正方形の領域しか平均できません。細長い領域に対してミップを選ぶ方法は 2 つあります。

- 短い方に合わせて選ぶと長い方向のテクセルを飛ばして読むので、ちらつきます（エイリアシング）。
- 長い方に合わせて選ぶと短い方向が必要以上に平均されて、ぼけます。標準のハードウェアはこちらを選びます。

## 楕円の足跡を計算する {#footprint}

画面の座標が 1 画素動くとテクスチャ座標（テクセル単位）がどれだけ動くかは、`ddx` と `ddy` で分かります。この 2 つのベクトルが足跡を表す平行四辺形の 2 辺です。ここから長軸と短軸の長さを求めます（Heckbert、1989 の整理に基づきます）。

```hlsl
Texture2D<float4> g_albedo : register(t0);
SamplerState g_linear_wrap : register(s0);   // 異方性なしの線形フィルタ（手書き版用）

cbuffer AnisoConstants : register(b0) {
  float2 g_texture_size;      // テクスチャの幅・高さ（テクセル数）。例: (2048, 2048)
  float g_max_aniso;          // 最大サンプル数。例: 16
  float _pad;
};

// 足跡の長軸・短軸。xy = 長軸の方向（テクセル単位の、1 画素ぶんのベクトル）、z = 長軸の長さ、w = 短軸の長さ
float4 FootprintAxes(float2 uv) {
  float2 dx = ddx(uv) * g_texture_size;         // 画面で右へ 1 画素 → テクセル単位の移動
  float2 dy = ddy(uv) * g_texture_size;         // 画面で下へ 1 画素

  float len_x = length(dx);
  float len_y = length(dy);
  // 辺の長い方を長軸の方向とする近似（厳密な楕円の主軸ではなく、平行四辺形の長辺）
  float2 major_dir = (len_x >= len_y) ? dx : dy;
  float major = max(len_x, len_y);
  // 短軸の長さ = 平行四辺形の面積 ÷ 長軸の長さ。面積は外積の絶対値
  float area = abs(dx.x * dy.y - dx.y * dy.x);
  float minor = area / max(major, 1e-6);
  return float4(major_dir, major, max(minor, 1e-6));   // 足した: 0 割りを避ける下限
}
```

短軸の長さを面積から求めているのが要点です。平行四辺形の面積は `dx` と `dy` の外積の大きさで、長辺を底辺と見ると高さが短軸（に近い量）になります。

## 何サンプル取るか {#samples}

長軸と短軸の比 `長軸 ÷ 短軸` が足跡の「細長さ」です。この比のぶんだけ長軸の方向にサンプルを並べます。比が 1 なら 1 サンプル、4 なら 4 サンプルです。上限は `MaxAnisotropy` で 16 が最大です。

ミップのレベルは短軸ではなく、長軸を `N` で割った長さに合わせます。サンプルを `N` 個に分けると、1 サンプルの担当範囲が `長軸 ÷ N` に縮むからです。`N` が比の通りならその長さが短軸と一致して、短軸に合わせた細かいミップになります。`N` が上限で頭打ちのときは `長軸 ÷ N` が短軸より大きいので、少しぼけます。

```hlsl
// 異方性フィルタの手書き版（仕組みの説明用。実際はサンプラー ステートに任せる）
float4 ManualAnisotropicPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 axes = FootprintAxes(uv);
  float2 major_dir = axes.xy;
  float major = axes.z;
  float minor = axes.w;

  // サンプル数 N: 比を切り上げて、上限で止める。奇数にしておくと中央のサンプルが残る
  float ratio = major / minor;
  float n = clamp(ceil(ratio), 1.0, g_max_aniso);

  // ミップ: 長軸を N で割った長さに合わせる（1 テクセルより小さいなら 0 番）
  float lod = max(log2(major / n), 0.0);

  // 長軸の方向（UV 空間）に、N 個を等間隔で並べる。-0.5 .. +0.5 の範囲に中心を合わせる
  float2 step_uv = (major_dir / g_texture_size) / n;   // 長軸全体を N 等分した UV の 1 歩
  float4 sum = 0;
  for (int i = 0; i < (int)n; ++i) {
    float offset = (i + 0.5) - n * 0.5;                // 中心が 0 になるように
    sum += g_albedo.SampleLevel(g_linear_wrap, uv + step_uv * offset, lod);
  }
  return sum / n;
}
```

ハードウェアの実装はこの手書き版と少し違います。トライリニアのサンプルの列で楕円を近似する点は同じですが、サンプルの重みや間隔（Feline など McCormack らの手法が知られています）は、GPU の世代や各社で違います。手書き版は仕組みを知るためのもので、ハードウェアと同じ見た目にはなりません。

## 比がどれだけ大きくなるか {#ratio}

低い視点の地形を例に数字で見積もります。カメラの高さを 1.7 m、地面を距離 `d` メートル先で見るとして比は、視線が地面と作る角度の逆の正弦に近くなります。`比 ≒ sqrt(d² + h²) / h`（`h` はカメラの高さ）です。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="カメラの高さ 1.7 m で地面を見たときの、距離ごとの足跡の長軸と短軸の比"><text x="14" y="22" class="fig-title">距離と足跡の細長さ（カメラの高さ 1.7 m）</text>
<line x1="60" y1="220" x2="690" y2="220" stroke="currentColor" stroke-width="1.5"/><line x1="60" y1="220" x2="60" y2="40" stroke="currentColor" stroke-width="1.5"/>
<line x1="60" y1="133" x2="690" y2="133" stroke="#e5484d" stroke-dasharray="6 4"/><text x="690" y="126" text-anchor="end" style="font-size:12px;fill:#e5484d;font-weight:600">上限 16x</text>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="90" y="193" width="70" height="27"/><rect x="200" y="167" width="70" height="53"/><rect x="310" y="82" width="70" height="138"/><rect x="420" y="40" width="70" height="180"/><rect x="530" y="40" width="70" height="180" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="125" y="186">約 3</text><text x="235" y="160">約 6</text><text x="345" y="76">約 16</text><text x="455" y="34">約 29</text><text x="565" y="34">約 59</text>
<text x="125" y="240">5 m</text><text x="235" y="240">10 m</text><text x="345" y="240">27 m</text><text x="455" y="240">50 m</text><text x="565" y="240">100 m</text></g>
<text x="360" y="262" text-anchor="middle" style="font-size:12px">27 m を超えると、16x では足りない（長軸方向が少しぼける）。縦軸は上を切っている</text></svg>

5 m で約 3、10 m で約 6、27 m で約 16（上限）、50 m で約 29、100 m で約 59 です。27 m より先は 16x でも足りなくて、長軸方向に少しぼけます。それでも異方性フィルタなしでは比の全部がぼけとして現れるので、16x でも大きな改善です。

## DirectX 11 での設定 {#d3d11}

サンプラー ステートの `Filter` を `D3D11_FILTER_ANISOTROPIC` にして、`MaxAnisotropy` を設定します。

```cpp
// （コンパイルしていない）
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_ANISOTROPIC;     // 縮小・拡大・ミップのすべてが異方性
desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP; // 地形は繰り返すのでラップ
desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
desc.MaxAnisotropy = 16;                    // 1〜16。大きいほど品質が高く重い
desc.MaxLOD = D3D11_FLOAT32_MAX;            // ミップをすべて使う
desc.ComparisonFunc = D3D11_COMPARISON_NEVER;

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&desc, &sampler);
context->PSSetSamplers(0, 1, sampler.GetAddressOf());
```

`Filter` は縮小、拡大、ミップ間の補間のすべてを異方性にします。`MaxAnisotropy` は最大サンプル数です。1 にすると異方性が働きません。2、4、8、16 の値が一般的です。ミップマップがあることが前提で、ミップのないテクスチャには効きません。

## コストと効き方 {#cost}

斜めの面でのテクスチャ読み込みのコストは、次のように増えます（トライリニアを 1 倍とした最悪の場合です）。

- 2x は少し改善して約 2 倍です。
- 4x は中程度の斜めまでくっきりして、約 4 倍です。
- 8x は低い視点でもほぼくっきりして、約 8 倍です。
- 16x はほぼ水平の面までくっきりして、約 16 倍です。

トライリニアは 1 サンプルで 8 テクセル（2 ミップ × 4 テクセル）を読むので、16x の最悪は 128 テクセルです。ただし、倍率は「斜めの面のテクスチャ読み込みだけ」のものです。真上を向いた面では増えません。ゲーム全体のフレーム時間はほかの処理が大半なので、そこまで増えません。近年の GPU では 16x でもコストが小さいことが多いです（実測は GPU とシーンで違います）。

足跡を目で確かめるには `CalculateLevelOfDetail` で、ミップの番号と比を画面に出します。

```hlsl
Texture2D<float4> g_debug_tex : register(t1);
SamplerState g_aniso_sampler : register(s1);   // MaxAnisotropy = 16 のサンプラー

float4 DebugAnisoPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  // 足跡の細長さ（1 で等方、大きいほど細長い）
  float4 axes = FootprintAxes(uv);
  float ratio = axes.z / axes.w;
  // ミップ番号（サンプラーの異方性を考慮した値）
  float mip = g_debug_tex.CalculateLevelOfDetail(g_aniso_sampler, uv);
  // 赤 = 比（16 で飽和）、緑 = ミップ番号（8 で飽和）
  return float4(saturate(ratio / 16.0), saturate(mip / 8.0), 0.0, 1.0);
}
```

地面の遠くが赤くなる（比が 16 を超える）場所は、`MaxAnisotropy` の上限に当たっています。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`ManualAnisotropicPS` と `DebugAnisoPS` をコンパイルして、エラーが出ないことを確かめました。比の数字は式からの手計算です。ハードウェアの異方性フィルタとの見た目の一致は確かめていません。

## 地形ではほぼ必須 {#terrain}

地形は視点が低く地面がほぼ水平に見えることが多い対象です。遠くの地面は画面の中でほぼ水平になって、比が大きくなります。異方性フィルタがないと中景から遠景で、地面のテクスチャがぼけた絵の具のように見えます。

注意点がいくつかあります。

- トライプラナーマッピングと併用すると、3 方向のそれぞれに効くので、コストは 3 倍になります（[Triplanar Mapping](triplanar.md)）。
- 法線マップにも効きます。ぼけるとスペキュラーが不自然になります。
- 頂点シェーダーでは使えません。異方性は画素の微分から決めるので、頂点では `SampleLevel` でミップを直接指定します。
- ユーザー設定で 1x から 16x まで切り替えられるようにしておきます。

## よくあるミス {#mistakes}

??? failure "遠くの地面がぼやけている"
    原因はサンプラーが異方性になっていないことです。`Filter = D3D11_FILTER_ANISOTROPIC` で `MaxAnisotropy` を 8〜16 にします。トライリニア（`D3D11_FILTER_MIN_MAG_MIP_LINEAR`）のままだと `MaxAnisotropy` を設定しても無視されます。

??? failure "異方性を 16x にしたのに、効いていない"
    原因はテクスチャにミップマップがないことです。異方性はミップを使うのでミップのないテクスチャには効きません。テクスチャを作るときに `MipLevels = 0` で全ミップを作るか `GenerateMips` を呼びます。

??? failure "頂点シェーダーで読んだテクスチャが、おかしな結果になる"
    原因は頂点シェーダーで `Sample` を使っていることです。頂点には画素の微分がありません。`SampleLevel` でミップ番号を指定します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 斜めの面は画素がテクスチャ上で細長い楕円になり標準のミップでぼけます。
    - [x] 異方性フィルタは、長軸に沿って比のぶんだけサンプルを並べます。上限は 16 です。
    - [x] 低い視点の地形では、27 m より先で 16x でも比が足りません。それでも大きな改善です。
    - [x] サンプラーを `D3D11_FILTER_ANISOTROPIC` にして、ミップのあるテクスチャで使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。HLSL の手書き版は仕組みを説明するために自分で書いたもので、ハードウェアの実装とは異なります。

- Heckbert, "Fundamentals of Texture Mapping and Image Warping", Master's thesis, UC Berkeley, 1989（楕円の足跡を使うフィルタリングの基礎）
- McCormack, Perry, Farkas, Jouppi, "Feline: Fast Elliptical Lines for Anisotropic Texture Mapping", SIGGRAPH 1999
- Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_ANISOTROPIC` と `MaxAnisotropy`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（テクスチャのフィルタリングの章）

## 関連ページ

- [Terrain Texturing](index.md)
- [メッシュとテクスチャ](../../../3d/mesh-textures.md)
