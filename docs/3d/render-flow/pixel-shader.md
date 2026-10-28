---
title: ピクセルの色
tags:
  - 3Dゲーム
  - 描画
---

# ピクセルの色

**ラスタライズで見つかったピクセルごとに、「どんな色にするか」を計算するのがピクセル シェーダー**です。描画の見た目（質感・光・影）のほとんどはここで決まります。呼ばれる回数が多い（画面のピクセル数 × 重なり）ため、最適化でもいちばん注目される工程です。このページでは、ピクセル シェーダーの入出力・テクスチャの貼り方（UV）・フィルタリングとミップマップ・基本のライティング（ランバート）・色空間（ガンマ）を説明します。

!!! tip "ポイント"
    - ピクセル シェーダー ＝ <strong>ピクセル 1 個の色を返す</strong>小さなプログラム。<strong>覆うピクセルの数だけ呼ばれる</strong>。
    - 入力は頂点シェーダーの出力を補間した値（UV・法線・位置）。出力は色（`SV_Target`）。
    - テクスチャはUV 座標で引く。(0, 0) が左上、(1, 1) が右下。
    - フィルタリング：近傍（ブロック状）・線形（なめらか）・異方性（斜めでもくっきり）。
    - ミップマップ ＝ 縮小版テクスチャの列。遠くの面でちらつきを防ぐ。
    - ライティングは法線と光の向きの内積（ランバート）が出発点。
    - 色の計算は線形空間で行い、出力時にガンマ補正する。

!!! info "このページを読む前に"
    - [描画の流れ（入門）](index.md)（このセクション全体の地図と、読む順番）
    - [行列](../../gamemath/matrices.md)（行列の基礎）
    - [座標系](../../gamemath/coordinate-systems.md)（このサイトの座標系の約束）

## 入力と出力

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="ピクセル シェーダーの入出力"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">ピクセル シェーダー：補間された値を受け取り、色を返す</text>
<g font-size="12">
<rect x="30" y="60" width="200" height="110" rx="8" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="130" y="82" text-anchor="middle" style="font-weight:700">入力（補間済み）</text>
<text x="46" y="106">・UV</text><text x="46" y="126">・ワールド法線</text><text x="46" y="146">・ワールド位置</text>
<rect x="310" y="60" width="160" height="110" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/>
<text x="390" y="100" text-anchor="middle" style="font-weight:700">ピクセル</text><text x="390" y="120" text-anchor="middle" style="font-weight:700">シェーダー</text>
<rect x="550" y="60" width="200" height="110" rx="8" fill="#2ea043" fill-opacity="0.15" stroke="#2ea043" stroke-width="2"/>
<text x="650" y="82" text-anchor="middle" style="font-weight:700">出力</text>
<text x="566" y="112">SV_Target：色 (R,G,B,A)</text><text x="566" y="136" style="font-size:11px">（SV_Depth で深度も変えられる）</text>
<rect x="30" y="185" width="440" height="26" rx="6" fill="#e5aa28" fill-opacity="0.18" stroke="#e5aa28"/>
<text x="250" y="203" text-anchor="middle">＋ テクスチャ・定数バッファ（光・材質）を読める</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="232" y1="115" x2="308" y2="115" marker-end="url(#rfa)"/><line x1="472" y1="115" x2="548" y2="115" marker-end="url(#rfa)"/></g>
</svg>

```hlsl
Texture2D albedo_texture : register(t0);
SamplerState linear_sampler : register(s0);

cbuffer Lighting : register(b1) {
  float3 light_direction;
  float3 light_color;
  float3 ambient_color;
};

float4 PSMain(VSOutput input) : SV_Target {
  float3 albedo = albedo_texture.Sample(linear_sampler, input.uv).rgb;
  float3 normal = normalize(input.world_normal);
  float n_dot_l = saturate(dot(normal, -light_direction));
  float3 color = albedo * (ambient_color + light_color * n_dot_l);
  return float4(color, 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| **`: SV_Target`** | この関数の戻り値が描画先（レンダー ターゲット）に書く色 |
| `Sample` | テクスチャから色を引く。サンプラーでフィルタを指定 |
| `normalize` | 補間で長さが変わった法線を長さ 1 に戻す |
| `dot(法線, -光の向き)` | 面が光に正対するほど 1、横向きで 0 |
| `saturate` | 0〜1 に収める（裏向きの負の値を 0 に） |

## テクスチャと UV

**テクスチャ（画像）を 3D の面に貼る**には、面の各点が画像のどこに対応するかを決める必要があります。この対応がUV 座標です。頂点ごとに UV を持ち、ラスタライズで補間されて、ピクセルに届きます。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="UV マッピング"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">UV：テクスチャ上の位置を頂点ごとに指定する</text>
<g transform="translate(40,50)">
<rect x="0" y="0" width="180" height="180" fill="#8a8a8a" fill-opacity="0.15" stroke="currentColor"/>
<g stroke="currentColor" stroke-opacity="0.2"><line x1="90" y1="0" x2="90" y2="180"/><line x1="0" y1="90" x2="180" y2="90"/></g>
<rect x="0" y="0" width="90" height="90" fill="#e5484d" fill-opacity="0.3"/><rect x="90" y="90" width="90" height="90" fill="#4c8bf5" fill-opacity="0.3"/>
<polygon points="20,150 160,150 90,30" fill="none" stroke="#e5aa28" stroke-width="3"/>
<circle cx="20" cy="150" r="5" fill="#e5aa28"/><circle cx="160" cy="150" r="5" fill="#e5aa28"/><circle cx="90" cy="30" r="5" fill="#e5aa28"/>
<text x="-6" y="-6" style="font-size:11px">(0,0)</text><text x="140" y="-6" style="font-size:11px">(1,0)</text>
<text x="-6" y="198" style="font-size:11px">(0,1)</text><text x="140" y="198" style="font-size:11px">(1,1)</text>
<text x="90" y="220" text-anchor="middle" style="font-size:12px">テクスチャ（UV 空間）</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="240" y1="140" x2="340" y2="140" marker-end="url(#rfa)"/></g>
<text x="290" y="128" text-anchor="middle" style="font-size:12px">貼る</text>
<g transform="translate(380,50)">
<polygon points="20,150 160,150 90,30" fill="#8a8a8a" fill-opacity="0.15" stroke="#e5aa28" stroke-width="3"/>
<clipPath id="uvclip"><polygon points="20,150 160,150 90,30"/></clipPath>
<g clip-path="url(#uvclip)"><rect x="20" y="30" width="70" height="60" fill="#e5484d" fill-opacity="0.35"/><rect x="90" y="90" width="70" height="60" fill="#4c8bf5" fill-opacity="0.35"/></g>
<text x="90" y="190" text-anchor="middle" style="font-size:12px">三角形（3D の面）</text>
</g>
<g font-size="12">
<text x="570" y="90" style="font-weight:700">UV の約束</text>
<text x="570" y="114">U ＝ 横（0 → 1）</text><text x="570" y="136">V ＝ 縦（0 → 1）</text>
<text x="570" y="160" style="fill:#e5484d">(0, 0) ＝ 画像の左上</text><text x="570" y="182">(1, 1) ＝ 画像の右下</text>
<text x="570" y="212" style="font-size:11px">※ V の向きはツールにより逆。取り込み時に注意</text>
</g>
</svg>

UV が 0〜1 の外にはみ出したときの挙動は、サンプラーのアドレスモードで決まります。

| モード | 動作 | 使い道 |
| --- | --- | --- |
| WRAP（繰り返し） | 0〜1 を繰り返す | 地面・壁のタイル |
| CLAMP（端を伸ばす） | 端のピクセルが続く | 一枚絵・UI・スカイボックス |
| MIRROR（鏡） | 反転しながら繰り返す | つなぎ目を目立たなくしたいタイル |
| BORDER（枠の色） | 指定した色 | シャドウ マップの範囲外 |

## フィルタリング

**ピクセルの UV は、テクスチャの画素（テクセル）の中間になるのがふつう**です。どのテクセルを使うか（混ぜるか）を決めるのがフィルタリングです。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="フィルタリングの比較">
<text x="20" y="24" class="fig-title">近傍（Point）と線形（Bilinear）：テクセルの拡大</text>
<g transform="translate(40,50)">
<g><rect x="0" y="0" width="40" height="40" fill="#222"/><rect x="40" y="0" width="40" height="40" fill="#eee"/><rect x="0" y="40" width="40" height="40" fill="#eee"/><rect x="40" y="40" width="40" height="40" fill="#222"/></g>
<text x="40" y="104" text-anchor="middle" style="font-size:12px">元のテクスチャ（2×2）</text>
</g>
<g transform="translate(200,50)">
<g><rect x="0" y="0" width="80" height="80" fill="#222"/><rect x="80" y="0" width="80" height="80" fill="#eee"/><rect x="0" y="80" width="80" height="80" fill="#eee"/><rect x="80" y="80" width="80" height="80" fill="#222"/></g>
<text x="80" y="184" text-anchor="middle" style="font-size:12px">近傍：ブロック状</text>
</g>
<g transform="translate(400,50)">
<defs><linearGradient id="fl-h" x1="0" x2="1"><stop offset="0" stop-color="#222"/><stop offset="1" stop-color="#eee"/></linearGradient><linearGradient id="fl-h2" x1="0" x2="1"><stop offset="0" stop-color="#eee"/><stop offset="1" stop-color="#222"/></linearGradient></defs>
<rect x="0" y="0" width="160" height="80" fill="url(#fl-h)"/><rect x="0" y="80" width="160" height="80" fill="url(#fl-h2)"/>
<rect x="0" y="0" width="160" height="160" fill="none" stroke="currentColor" stroke-opacity="0.3"/>
<text x="80" y="184" text-anchor="middle" style="font-size:12px">線形：なめらかに混ざる</text>
</g>
<g font-size="12">
<text x="590" y="80" style="font-weight:700">近傍</text><text x="590" y="100">最も近い 1 テクセル</text><text x="590" y="120">ドット絵向き</text>
<text x="590" y="156" style="font-weight:700">線形</text><text x="590" y="176">周りの 4 テクセルを混ぜる</text><text x="590" y="196">ふつうの写真向き</text>
</g>
</svg>

| フィルタ | 内容 | 向く場面 |
| --- | --- | --- |
| 近傍（Point） | 最も近い 1 テクセル | ドット絵・データ用テクスチャ |
| 双線形（Bilinear） | 周りの 4 テクセルを混ぜる | 標準 |
| 三線形（Trilinear） | 双線形 ＋ ミップ レベル間も混ぜる | ミップの切り替えを滑らかに |
| 異方性（Anisotropic） | 斜めから見た面で縦に伸びた範囲を平均 | 床・道など、斜めに見る面（16x） |

## ミップマップ

**遠くの面はテクスチャが画面上で小さく表示される**ので、1 ピクセルが多数のテクセルをまたぎます。そのまま 1 点だけ引くと、小さな模様が飛び飛びに選ばれて、動くとちらつきます。あらかじめ半分・4 分の 1…と縮小した画像（ミップマップ）を用意し、ピクセルの大きさに合うサイズを使うのがミップマップです。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="ミップマップ">
<text x="20" y="24" class="fig-title">ミップマップ：縮小版を事前に作る（合計で元の約 1.33 倍のメモリ）</text>
<g stroke="currentColor" stroke-width="1.5">
<rect x="40" y="50" width="128" height="128" fill="#4c8bf5" fill-opacity="0.3"/><text x="104" y="198" text-anchor="middle" style="font-size:12px">レベル 0（512）</text>
<rect x="190" y="50" width="64" height="64" fill="#4c8bf5" fill-opacity="0.3"/><text x="222" y="134" text-anchor="middle" style="font-size:12px">レベル 1（256）</text>
<rect x="276" y="50" width="32" height="32" fill="#4c8bf5" fill-opacity="0.3"/><text x="292" y="102" text-anchor="middle" style="font-size:12px">レベル 2</text>
<rect x="330" y="50" width="16" height="16" fill="#4c8bf5" fill-opacity="0.3"/><text x="338" y="86" text-anchor="middle" style="font-size:12px">3</text>
<rect x="368" y="50" width="8" height="8" fill="#4c8bf5" fill-opacity="0.3"/>
</g>
<g font-size="12">
<text x="440" y="74" style="font-weight:700">ミップ レベルの選び方</text>
<text x="440" y="98">・隣のピクセルとの UV の差から、</text><text x="440" y="116">　1 ピクセルが何テクセルに当たるか調べる</text>
<text x="440" y="140">・近い面 → レベル 0（大きい画像）</text><text x="440" y="160">・遠い面 → 高いレベル（小さい画像）</text>
<text x="440" y="190" style="font-weight:700">効果：ちらつき（エイリアシング）の防止と、</text><text x="440" y="208" style="font-weight:700">　　　メモリ読み出しの削減（キャッシュに優しい）</text>
</g>
</svg>

ミップ レベルを選ぶために、GPU は隣のピクセルとの UV の差（微分）を使います。だから 2×2 のクワッドで処理するのです（[ラスタライズ](rasterize.md)）。分岐の中でテクスチャを引くと、クワッドの他のピクセルが分岐に入らず微分が壊れることがあるので、そのときは `SampleLevel`（ミップを自分で指定）や `SampleGrad` を使います。

## 基本のライティング：ランバート

<strong>物の明るさの基本は、「面が光にどれだけ正対しているか」</strong>です。法線（面の向き）と光の来る向きの内積で決まります（ランバートの余弦則）。

<div class="formula">明るさ = max( 0, N · L )　（N：法線、L：面から光源へ向かう向き）</div>

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="ランバート"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">法線と光の向きの角度が小さいほど明るい</text>
<g transform="translate(110,0)">
<line x1="0" y1="200" x2="200" y2="200" stroke="currentColor" stroke-width="3"/>
<line x1="100" y1="200" x2="100" y2="90" stroke="#2ea043" stroke-width="3" marker-end="url(#rfa)"/><text x="108" y="100" style="font-size:12px;fill:#2ea043">N</text>
<line x1="100" y1="200" x2="100" y2="70" stroke="#e5aa28" stroke-width="3" stroke-dasharray="6 4"/><text x="60" y="76" style="font-size:12px;fill:#e5aa28">L</text>
<text x="100" y="228" text-anchor="middle" style="font-size:12px">真上から：N·L = 1（明るい）</text>
</g>
<g transform="translate(400,0)">
<line x1="0" y1="200" x2="200" y2="200" stroke="currentColor" stroke-width="3"/>
<line x1="100" y1="200" x2="100" y2="90" stroke="#2ea043" stroke-width="3" marker-end="url(#rfa)"/><text x="108" y="100" style="font-size:12px;fill:#2ea043">N</text>
<line x1="100" y1="200" x2="170" y2="100" stroke="#e5aa28" stroke-width="3" stroke-dasharray="6 4"/><text x="174" y="100" style="font-size:12px;fill:#e5aa28">L</text>
<text x="100" y="228" text-anchor="middle" style="font-size:12px">斜め 45°：N·L ≈ 0.71</text>
</g>
<g transform="translate(640,0)">
<line x1="0" y1="200" x2="120" y2="200" stroke="currentColor" stroke-width="3"/>
<line x1="60" y1="200" x2="60" y2="90" stroke="#2ea043" stroke-width="3" marker-end="url(#rfa)"/>
<line x1="60" y1="200" x2="150" y2="196" stroke="#e5aa28" stroke-width="3" stroke-dasharray="6 4"/>
<text x="60" y="228" text-anchor="middle" style="font-size:12px">真横：N·L = 0（暗い）</text>
</g>
</svg>

| 項目 | 内容 |
| --- | --- |
| `N · L` | 同じ向きで 1、直角で 0、裏側は負 |
| `saturate` | 負を 0 に（裏側は光が当たらない） |
| アンビエント（環境光） | 全体に足す、底上げの明るさ（真っ暗を避ける） |
| ディフューズ色 | テクスチャの色（アルベド）× 明るさ |

光沢（スペキュラ）・物理ベース（PBR）・影・間接光…はこの上に積み重ねます（[法線とライティング](../lighting-normals.md)・[PBR](../pbr.md)）。

## 色空間：線形とガンマ

**画像ファイルの色（sRGB）は、人間の目に合わせて暗い所を細かく保存してあり**、計算に使う明るさ（線形）とは違います。正しく計算するには、線形に直してから計算し、出力時に sRGB に戻す必要があります。

| 段階 | 空間 |
| --- | --- |
| テクスチャの読み込み | sRGB フォーマット（`_SRGB`）で作ると、GPU が自動で線形に変換 |
| ライティングの計算 | 線形 |
| 画面への出力 | バックバッファを `_SRGB` で作ると、GPU が自動で sRGB に変換 |

これを怠ると全体が暗く（または白っぽく）なり、光の足し算が不自然になります（[色空間とガンマ](../../graphics/postprocess/index.md)）。

## ピクセル シェーダーが重い理由

<strong>ピクセル シェーダーが呼ばれる回数 ＝ 画面のピクセル数 × 重なり（オーバードロー）</strong>です。

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="ピクセル シェーダーの呼び出し回数">
<text x="20" y="24" class="fig-title">解像度が上がると、呼び出し回数が掛け算で増える</text>
<g font-size="12">
<rect x="40" y="60" width="100" height="56" fill="#4c8bf5" fill-opacity="0.3" stroke="#4c8bf5"/><text x="90" y="92" text-anchor="middle">720p</text><text x="90" y="140" text-anchor="middle">約 92 万</text>
<rect x="190" y="52" width="150" height="84" fill="#2ea043" fill-opacity="0.3" stroke="#2ea043"/><text x="265" y="98" text-anchor="middle">1080p</text><text x="265" y="160" text-anchor="middle">約 207 万</text>
<rect x="390" y="40" width="300" height="126" fill="#e5484d" fill-opacity="0.3" stroke="#e5484d"/><text x="540" y="108" text-anchor="middle">4K</text><text x="540" y="188" text-anchor="middle">約 830 万（1080p の 4 倍）</text>
</g>
</svg>

| 対策 | 内容 |
| --- | --- |
| 解像度を下げる／アップスケール | ピクセル数を減らす（[TAA・アップスケール](../../rendering/taa-upscaling.md)） |
| オーバードローを減らす | 手前から描いて、隠れたピクセルを省略（[オーバードロー](../../rendering/overdraw.md)） |
| シェーダーを軽く | テクスチャ読み込み・計算を減らす（[シェーダーのコスト](../../rendering/shader-cost.md)） |

## よくあるミス

??? failure "法線を正規化せず、ライティングが乱れる"
    **補間した法線は長さが 1 でない**。ピクセル シェーダーで `normalize`。

??? failure "全体が暗い／白っぽい（色空間の間違い）"
    テクスチャに `_SRGB` を使い、バックバッファも sRGB に。計算は線形。

??? failure "遠くでテクスチャがちらつく"
    ミップマップを作って有効にする。異方性フィルタも。

??? failure "テクスチャが上下逆さまに貼られる"
    V の向きがツールと違う。読み込み時に反転するか、UV を `1 - v`。

??? failure "分岐の中の `Sample` で、境目に線が出る"
    `SampleLevel`／`SampleGrad` を使う、または分岐の外で引く。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ピクセル シェーダー ＝ <strong>ピクセル 1 個の色を返す</strong>。覆うピクセルの数だけ呼ばれる
    - [x] UVでテクスチャを引く。フィルタ（近傍・線形・異方性）とミップマップで見た目が決まる
    - [x] ライティングの基本は`N · L`（ランバート）。法線は正規化
    - [x] 計算は線形空間、出力は sRGB
    - [x] 解像度 × 重なりが呼び出し回数。最適化の主戦場

## 参考

- Microsoft, "Pixel Shader Stage"（Microsoft Learn）
- Williams, "Pyramidal Parametrics"（SIGGRAPH 1983、ミップマップ）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 8）

## 関連ページ

- [描画の流れ（入門）](index.md)
- [ラスタライズ](rasterize.md)
- [深度・ブレンド](output-merger.md)
- [メッシュとテクスチャ](../mesh-textures.md)
- [法線とライティング](../lighting-normals.md)
