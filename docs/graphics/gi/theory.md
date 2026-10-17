---
title: GI の理論
tags:
  - 描画
---

# GI の理論

個々の手法に入る前に**間接光が数式として何なのか**を押さえます。**レンダリング方程式**から出発し、**間接光がなぜ再帰的で難しいのか**、**拡散反射の間接光がなぜ「粗く保存」できるのか**、<strong>球面調和関数（SH）</strong>、**モンテカルロ積分**を説明します。

!!! tip "ポイント"
    - <strong>レンダリング方程式</strong>：<strong>出る光 ＝ 自分が出す光 ＋ ∫（入る光 × BRDF × cosθ）</strong>。
    - <strong>入る光の中に別の面から出た光</strong>が含まれる → <strong>再帰</strong>。これが GI。
    - <strong>拡散面の間接光</strong>は、法線ごとの<strong>放射照度 E(n)</strong> に畳み込める。<strong>低周波</strong>。
    - <strong>放射照度は、SH 3 次（9 係数）で、ほぼ表せる</strong>（Ramamoorthi & Hanrahan）。
    - <strong>鏡面の間接光</strong>は<strong>高周波</strong>。<strong>反射の手法</strong>（プローブ・SSR）が担当。
    - <strong>モンテカルロ</strong>：<strong>ランダムな方向をサンプルして平均</strong>。<strong>ノイズ</strong>が出るので<strong>デノイズ</strong>や<strong>再利用</strong>が要る。

## レンダリング方程式

点 `p` から、方向 `ω_o` に出る光の量（放射輝度）は、次のとおりです。

<div class="formula">L_o(p, ω_o) = L_e(p, ω_o) + ∫ L_i(p, ω_i) · f(p, ω_i, ω_o) · (n·ω_i) dω_i</div>

| 記号 | 意味 |
| --- | --- |
| **L_o** | 点から、視線方向へ出ていく光 |
| **L_e** | 点自身が出す光（発光） |
| <strong>L_i(p, ω_i)</strong> | 方向 `ω_i` から入ってくる光 |
| **f** | BRDF（入る方向と出る方向の反射の割合） |
| **n·ω_i** | 入射角の余弦（斜めから来る光は、薄まる） |
| **∫ … dω_i** | 半球上の全方向の積分 |

**入ってくる光 `L_i(p, ω_i)`** は、**その方向にある別の面 `q` から出てきた光 `L_o(q, -ω_i)`** です。つまり、**右辺の中に同じ式（別の点で）が含まれる**＝**再帰**です。

| 入ってくる光の出どころ | 呼び方 |
| --- | --- |
| **光源から直接** | **直接光**（シャドウ マップ・ライトの計算で処理） |
| **別の面で、1 回反射してから** | **1 バウンスの間接光** |
| **2 回以上反射してから** | **多バウンスの間接光** |

**リアルタイムの GI**は、**ほとんどが 1〜数バウンス**を、**近似**したものです。**バウンス数が増えるほど、光は弱まる**ので、**1 バウンスが一番重要**です。

## 拡散と鏡面

**BRDF**を**拡散**と**鏡面**に分けると**間接光の性質がまったく違います**。

| 項目 | 拡散の間接光 | 鏡面の間接光 |
| --- | --- | --- |
| **BRDF** | ほぼ一定（ランバート：`albedo / π`） | **鋭いローブ**（粗さで広がる） |
| **視線への依存** | **なし** | **あり** |
| **周波数** | <strong>低い（なめらか）</strong> | <strong>高い（細かい）</strong> |
| **保存のしかた** | **粗い情報で十分**（プローブ・ライトマップ） | **細かい情報が要る**（[反射](../reflections/index.md)） |

<strong>このセクションは、主に「拡散の間接光」</strong>を扱い、**鏡面は、[反射](../reflections/index.md)のセクション**が担当します。

## 放射照度：拡散の間接光を畳み込む

**ランバート面**では、**出る光の量は視線方向に依存せず**、**入ってくる光を余弦で重みづけて積分した量**（**放射照度 E**）だけで決まります。

<div class="formula">E(n) = ∫ L_i(ω) · max(0, n·ω) dω　、　L_o = (albedo / π) · E(n)</div>

**E は法線 `n` だけの関数**です（位置 `p` は固定とする）。**あらゆる方向からの光を、「n を中心とした余弦」で畳み込んだ**ものなので、<strong>非常になめらか（低周波）</strong>です。**法線が少し変わっても、E はほとんど変わりません**。

この性質のおかげで**間接光（拡散）は、粗い情報**（**少ない数値**）で、**保存できます**。

## 球面調和関数（SH）

**球面上の関数**（たとえば、**全方向の入射光 `L_i(ω)`**）を、**少数の係数**で近似する方法が、**球面調和関数**（Spherical Harmonics、SH）です。**球面上のフーリエ級数**のようなものです。

| 次数 | 係数の数 | 表せる細かさ |
| --- | --- | --- |
| <strong>0 次（L0）</strong> | 1 | **平均**（全方向で同じ明るさ） |
| <strong>1 次（L1）</strong> | 4 | **おおまかな向き**（明るい方向・暗い方向） |
| <strong>2 次（L2）</strong> | 9 | **放射照度なら、ほぼ十分** |
| <strong>3 次（L3）</strong> | 16 | より細かい |

**Ramamoorthi と Hanrahan**（2001）は、**余弦の畳み込み後の放射照度**が、<strong>SH の 2 次（9 係数）</strong>で、**誤差 約 1%**ほどに収まることを示しました。**1 つのプローブに、9 個（×RGB の 27 個）の数値**を持たせれば、**全方向の法線に対する間接光**が**引ける**ということです。

```hlsl
float3 EvaluateSH9(float3 n, float3 sh[9]) {
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  return c1 * sh[8] * (n.x * n.x - n.y * n.y) + c3 * sh[6] * n.z * n.z + c4 * sh[0] - c5 * sh[6] +
         2.0 * c1 * (sh[4] * n.x * n.y + sh[7] * n.x * n.z + sh[5] * n.y * n.z) +
         2.0 * c2 * (sh[3] * n.x + sh[1] * n.y + sh[2] * n.z);
}
```

| 点 | 説明 |
| --- | --- |
| **`sh[9]`** | **RGB 各チャンネルの、SH 係数**（**事前に余弦畳み込み済み**または、評価時に係数を掛ける） |
| **定数 `c1〜c5`** | **余弦の畳み込み**と、**SH 基底関数の正規化**をまとめた定数 |
| **評価** | **法線 `n` を入れる**と**その向きの放射照度**が出る。**数十の演算**で済む |

**実用**では、<strong>L1（4 係数）</strong>や、<strong>アンビエント キューブ（6 方向の色）</strong>など、**さらに軽い表現**もよく使われます。

## モンテカルロ積分

**半球の積分**を**ランダムな方向をサンプルして平均する**ことで、**近似**する方法です。

<div class="formula">E ≈ (1/N) · Σ  L_i(ω_k) · (n·ω_k) / pdf(ω_k)</div>

| 項 | 意味 |
| --- | --- |
| **N** | サンプル数 |
| **ω_k** | k 番目のランダムな方向 |
| <strong>pdf(ω_k)</strong> | その方向を選ぶ確率密度（サンプリングの偏りの補正） |

**余弦重み付きサンプリング**（`pdf = cosθ / π`）を使えば、**`(n·ω) / pdf = π`** と**定数**になり、**単純な平均**になります（[AO の理論](../ao/theory.md)と同じ）。

| 性質 | 内容 |
| --- | --- |
| **偏りがない** | サンプルを増やすと**真の値に収束** |
| **ノイズ** | **誤差は、`1/√N` で減る**（**4 倍のサンプルで誤差は半分**） |
| **リアルタイム** | **少ないサンプル（画素あたり 1 本）＋ デノイズ・時間蓄積**で補う |

**サンプルの方向をどう選ぶか**（重要度サンプリング・ブルー ノイズ）、**ノイズをどう消すか**（時間蓄積・空間フィルタ・ReSTIR）が、**レイトレ GI の中心**です。

## 手法を分ける 2 つの軸

### 軸 1：いつ計算するか

| 区分 | 内容 | 例 |
| --- | --- | --- |
| <strong>事前（ベイク）</strong> | **オフラインで計算**し、**結果を保存** | ライトマップ・ベイク済みプローブ |
| **準動的** | **静的なジオメトリ**に対し、**光だけ**動的に更新 | プローブの再ライティング・DDGI |
| **完全動的** | **ジオメトリも光も動く**。**毎フレーム計算** | SSGI・ボクセル GI・レイトレ GI |

### 軸 2：どこに情報を持つか

| 保存先 | 内容 | 例 |
| --- | --- | --- |
| <strong>面（テクスチャ）</strong> | **オブジェクトの表面**の UV 上 | ライトマップ |
| **空間の点** | **3D 空間の格子・点** | プローブ・DDGI |
| **画面** | **今見えている画素**だけ | SSGI |
| **ボクセル** | **3D の格子**に**シーンの光・形** | ボクセル GI |
| <strong>世界（レイ）</strong> | **光線を飛ばして、その場で** | レイトレ GI |

**各手法はこの 2 軸のどこに位置するか**で、**長所・短所**がほぼ決まります。

<!-- fig:gi-color-bleeding:begin -->

<svg class="fig illust motion" data-fig="gi-color-bleeding" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gi-color-bleeding" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<linearGradient id="gi-bleed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a5f" stop-opacity="0.75"/>
<stop offset="1" stop-color="#ff5a5f" stop-opacity="0"/>
</linearGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">間接光:光が壁で跳ね返って、隣の面に色がにじむ</text>
<rect x="80" y="60" width="480" height="270" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<rect x="72" y="60" width="16" height="270" fill="#e5484d"/>
<text x="86" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤い壁</text>
<rect x="80" y="330" width="480" height="14" fill="#94a3b8"/>
<rect x="80" y="320" width="180" height="10" fill="url(#gi-bleed)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></rect>
<circle cx="330" cy="72" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="348" y="78" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光源</text>
<line x1="330" y1="84" x2="420" y2="328" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1739;1.0000" values="1;1;0;0"/></line>
<polygon points="420,328 411.36,319.67 421.16,316.06" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></polygon>
<rect x="386" y="320" width="68" height="10" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></rect>
<line x1="320" y1="82" x2="86" y2="190" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.3304;1.0000" values="1;1;0;0"/></line>
<polygon points="86,190 93.62,180.73 98.0,190.21" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="130" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3826;0.4522;1.0000" values="1;1;0;0"/></line>
<polygon points="130,328 121.74,319.29 131.69,316.12" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="210" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4174;0.4870;1.0000" values="1;1;0;0"/></line>
<polygon points="210,328 198.9,323.45 206.66,316.47" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="290" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4522;0.5217;1.0000" values="1;1;0;0"/></line>
<polygon points="290,328 278.13,326.27 283.97,317.62" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></polygon>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光源から出た光<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 床に当たる（直接光）→ 明るくなる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 赤い壁に当たる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 壁は赤い光だけを反射して、四方に跳ね返す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 壁の近くの床が、赤っぽくなる（色のにじみ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="80" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">間接光は、直接光が当たった面が「次の光源」になる。リアルタイムでは、プローブやボクセルで近似する。</text>
<text x="590" y="90" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">光の跳ね返り</text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">0 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（直接）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（壁へ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">2 回（壁 → 床）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gi-color-bleeding:end -->

## 間接光の見た目への効果

| 効果 | 内容 |
| --- | --- |
| **日陰の明るさ** | **真っ黒にならず**、**周囲から回り込む光**で**ほのかに明るい** |
| **カラー ブリーディング** | **色付きの面**の近くが**その色に染まる** |
| **接地感** | <strong>AO（環境光遮蔽）</strong>と合わせて、**物が地面になじむ** |
| **屋内の明るさ** | **窓からの光が部屋全体**を**拡散して照らす** |

## これだけ覚える

!!! abstract "まとめ"
    - [x] GI ＝ <strong>レンダリング方程式の「入ってくる光」に含まれる、別の面から跳ね返った光</strong>（再帰）
    - [x] <strong>拡散の間接光は低周波</strong>。<strong>放射照度 E(n)</strong> に畳み込めて、<strong>SH 9 係数</strong>でほぼ表せる
    - [x] <strong>鏡面の間接光は高周波</strong>で、<strong>反射の手法</strong>が担当
    - [x] <strong>モンテカルロ</strong>：<strong>ランダムな方向の平均</strong>。<strong>ノイズ</strong>を<strong>デノイズ・再利用</strong>で消す
    - [x] 手法は<strong>「いつ計算するか」×「どこに保存するか」</strong>で整理できる

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Green, "Spherical Harmonic Lighting: The Gritty Details"（GDC 2003）

## 関連ページ

- [間接光（GI）](index.md)
- [ライトマップ](lightmaps.md)
- [ライト プローブ](probes.md)
- [AO の理論](../ao/theory.md)
- [反射](../reflections/index.md)
