---
title: Probe Placement
tags:
  - 描画
---

# Probe Placement

<strong>プローブは、多いほど精密ですが、メモリとベイクの時間が増えます</strong>。<strong>格子状に置く方法と、重要な所に手動で置く方法</strong>があります。このページでは、置き方の方針と、密度の決め方を説明します。

!!! tip "ポイント"
    - 格子状に自動配置 ＋ 重要な所を手動で補う。
    - 光が変化する所（窓・影の境目）は密に。
    - 壁の中に置かない（無効なプローブは、補間から外す）。
    - 密度が低いと、光がぼやけ、漏れる。

## 置き方
<strong>プローブの配置</strong>は、<strong>品質</strong>に直結します。

| 指針 | 内容 |
| --- | --- |
| 光が変化する場所に密に | 明暗の境目・窓の近く・照明の近く |
| 動く物体が通る場所に置く | 通路・部屋・キャラが歩く範囲 |
| 壁の両側に置く | 壁の内側にプローブがあると、反対側の光が混ざる（ライト リーク） |
| 家具の中・壁の中は避ける | 幾何の内部のプローブは、<strong>黒（または不正な値）</strong>に |
| 高さ方向にも | 床・腰・頭の数段 |
| 自動配置 | 格子を自動生成し、幾何の内側のプローブを、除外・補完 |


光が変化する場所には<strong>密に</strong>置きます。明暗の境目、窓の近く、照明の近くです。逆に、変化の小さい広い場所は粗くてかまいません。動く物体が通る場所には、必ず置きます。通路、部屋、キャラクターが歩き回る範囲です。<strong>壁の両側</strong>にそれぞれ置きます。壁の内側にプローブがあると、反対側の光が混ざる<strong>ライト リーク</strong>が起きるからです。家具や壁の中のような幾何の内部のプローブは、黒や不正な値になるので避けます。高さ方向にも、床・腰・頭の数段に置きます。

実際には、まず<strong>格子を自動生成</strong>して、幾何の内側のプローブを除外あるいは補完し、そのうえで重要な場所に手動でプローブを足します。

光が変化する場所には<strong>密に</strong>置きます。明暗の境目、窓の近く、照明の近くです。逆に、変化の小さい広い場所は粗くてかまいません。動く物体が通る場所には、必ず置きます。通路、部屋、キャラクターが歩き回る範囲です。<strong>壁の両側</strong>にそれぞれ置きます。壁の内側にプローブがあると、反対側の光が混ざる<strong>ライト リーク</strong>が起きるからです。家具や壁の中のような幾何の内部のプローブは、黒や不正な値になるので避けます。高さ方向にも、床・腰・頭の数段に置きます。

実際には、まず<strong>格子を自動生成</strong>して、幾何の内側のプローブを除外あるいは補完し、そのうえで重要な場所に手動でプローブを足します。

<!-- fig:probe-light-leak:begin -->

<svg class="fig illust motion" data-fig="probe-light-leak" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-light-leak" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ライト リーク:壁の向こうのプローブが、混ざってしまう</text>
<text x="40" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">可視性なし（そのまま補間）</text>
<rect x="40" y="90" width="330" height="220" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="202" y="90" width="10" height="220" fill="#475569"/>
<text x="130" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗い部屋</text>
<text x="290" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るい部屋</text>
<rect x="40" y="90" width="162" height="220" fill="#0f172a" fill-opacity="0.22"/>
<circle cx="80" cy="150" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="80" cy="260" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="330" cy="150" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="330" cy="260" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="160" cy="200" r="9" fill="#ffffff" stroke="#1f2937" stroke-width="3"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="160;160;100;109;118;127;136;145;154;163;172;181;190;190"/></circle>
<rect x="130" y="330" width="150" height="30" fill="#888888" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="#888888;#888888;#8a8a8a;#8f8f8f;#949494;#989898;#9d9d9d;#a1a1a1;#a5a5a5;#a9a9a9;#adadad;#b1b1b1;#b4b4b4;#b4b4b4"/></rect>
<text x="205" y="352" text-anchor="start" style="font-size:1px;font-weight:700;fill:#ffffff">→</text>
<text x="60" y="352" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">結果:</text>
<text x="400" y="68" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">可視性あり（壁の向こうは除く）</text>
<rect x="400" y="90" width="330" height="220" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="562" y="90" width="10" height="220" fill="#475569"/>
<text x="490" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗い部屋</text>
<text x="650" y="108" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るい部屋</text>
<rect x="400" y="90" width="162" height="220" fill="#0f172a" fill-opacity="0.22"/>
<circle cx="440" cy="150" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="440" cy="260" r="11" fill="#5a5a5a" stroke="#1f2937" stroke-width="2"/>
<circle cx="690" cy="150" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="690" cy="260" r="11" fill="#f3f3f3" stroke="#1f2937" stroke-width="2"/>
<circle cx="520" cy="200" r="9" fill="#ffffff" stroke="#1f2937" stroke-width="3"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="520;520;460;469;478;487;496;505;514;523;532;541;550;550"/></circle>
<rect x="490" y="330" width="150" height="30" fill="#888888" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1440;0.2080;0.2720;0.3360;0.4000;0.4640;0.5280;0.5920;0.6560;0.7200;1.0000" values="#888888;#888888;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a;#5a5a5a"/></rect>
<text x="565" y="352" text-anchor="start" style="font-size:1px;font-weight:700;fill:#ffffff">→</text>
<text x="420" y="352" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">結果:</text>
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">暗い部屋の中の点を、壁へ近づける<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">左:壁の向こうの明るいプローブが混ざり、暗い部屋が明るくなる（漏れ）。右:壁越しは重み 0 → 暗いまま<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:probe-light-leak:end -->

### ライト リーク（壁越しの漏れ）

<strong>プローブ間の補間</strong>は、<strong>壁の存在を知らない</strong>ので、壁の向こう側のプローブの光が、こちら側に漏れることがあります。

| 対策 | 内容 |
| --- | --- |
| プローブの配置の工夫 | 壁の近くを密に・壁の両側にそれぞれ置く |
| 可視性の重み付け | 物体から、プローブが見えるかを判定し、見えないプローブの重みを下げる（[DDGI](../ddgi.md)の方式） |
| <strong>ボリュームの分割（ゾーン）</strong> | 部屋ごとにプローブ グループを分ける |
| 法線バイアス | 物体の位置を法線方向に少しずらして、補間 |


### 適応的な配置

均一な格子は、広い空き地では無駄が多く、複雑な室内では足りません。そこで、シーンの複雑さに応じて密度を変える方式があります。Unreal Engine の Volumetric Lightmap は、シーンの幾何の複雑さに応じて、八分木（ブリック）の細かさを変えます。重要な部分（建物の近くなど）は細かいブリック、何もない空は大きなブリックになります。メモリを保ちながら、必要な場所に密度を集中できます。

### 適応的な配置

均一な格子は、広い空き地では無駄が多く、複雑な室内では足りません。そこで、シーンの複雑さに応じて密度を変える方式があります。Unreal Engine の Volumetric Lightmap は、シーンの幾何の複雑さに応じて、八分木（ブリック）の細かさを変えます。重要な部分（建物の近くなど）は細かいブリック、何もない空は大きなブリックになります。メモリを保ちながら、必要な場所に密度を集中できます。

## プローブを、どこに、置くか

プローブの、<strong>数と、位置</strong>が、<strong>GI の品質</strong>を、決めます。少ないと、光が、ぼやけ、多いと、メモリと、更新が、重くなります。光が、急に変わる所（壁の、すぐ両側、窓の、近く）に、密に、変化の、ゆるやかな所（広い、空き地）に、疎に、置くのが、基本です。

## 配置の、方法

| 方法 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| 均等な、格子 | 空間を、一定の、間隔（2 m など）で、格子状に | 簡単。補間も、単純（トライリニア） | 無駄が、多い（何もない、空間にも、置く）。壁の、中に、プローブが、埋まる |
| 手動 | アーティストが、重要な、場所に、置く | 効率的（必要な、所だけ） | 手間。置き忘れ |
| 自動（ジオメトリに、合わせる） | 床、壁、天井の、近くに、自動で、配置 | 無駄が、少ない | 実装が、複雑 |
| 適応的（光の変化に、応じて） | 光が、急に変わる、場所に、自動で、細かく置く | 品質と、数の、バランスが、よい | 複雑。事前計算が、重い |

## 格子配置

<strong>最も、単純で、よく使われる</strong>方法です。<strong>空間を、立方体の、格子</strong>に、分け、格子の、頂点に、プローブを、置きます。

```cpp
// 立方体の範囲に、均等な間隔で、プローブを置く。
struct ProbeGrid {
  Vector3 origin;          // 格子の、最小の角（ワールド座標）
  Vector3 spacing;         // 各軸の、プローブの、間隔（メートル）
  int3 count;              // 各軸の、プローブの数
};

Vector3 ProbePosition(const ProbeGrid& g, int x, int y, int z) {
  return g.origin + Vector3(x * g.spacing.x, y * g.spacing.y, z * g.spacing.z);
}
// 例: 64 m × 16 m × 64 m の、場面を、4 m 間隔で → 17 × 5 × 17 = 1,445 個のプローブ。
```

<strong>間隔</strong>は、<strong>光の変化の、細かさ</strong>に、合わせます。部屋の中（光が、場所で、変わる）は、1〜2 m、屋外の、広場は、4〜8 m が、目安です。

### 格子の、問題

| 問題 | 内容 |
| --- | --- |
| 壁の、中に、埋まる | 格子の、頂点が、壁・床の、中に、ある。中の、プローブは、真っ暗（光が、届かない）。補間で、周りの、明るいプローブに、暗さが、混ざる |
| 壁の、向こうの光が、漏れる | 壁の、両側で、光が、まったく、違うのに、1 つの、格子の、セルに、含まれると、補間で、混ざる |
| 無駄が、多い | 地面の、下、空中、何もない場所にも、プローブを、置く |

## 埋まった、プローブへの、対処

<strong>壁や、床の中</strong>に、<strong>埋まった</strong>、プローブは、使えないので、検出して、無効にする、または、押し出して、外に動かす。

```cpp
// プローブが、ジオメトリの内側にあるかを、調べる（複数方向に、レイを飛ばし、裏面に、当たる割合）。
bool IsInsideGeometry(const Vector3& pos) {
  int back_hits = 0;
  for (const Vector3& dir : kSampleDirections) {                    // 球面上の、数十方向
    RayHit hit;
    if (Raycast(pos, dir, 100.0f, &hit) && hit.is_back_face) ++back_hits;   // 裏面に当たった = 物体の内側から、見ている
  }
  return back_hits > kSampleDirections.size() * 0.5f;               // 半分以上が、裏面 → 内側
}

// 内側のプローブは、最も近い、表面の外へ、押し出す（または、無効にする）。
```

<strong>プローブから、全方向に、レイを飛ばし</strong>、<strong>多くが、物体の、裏面</strong>（物の内側から、見た面）に、当たるなら、そのプローブは、物体の中に、あります。無効にするか、表面の外へ、押し出します。

## 光漏れを、防ぐ

<strong>壁の、両側</strong>で、<strong>光が、まったく違う</strong>とき（室内と、屋外）、プローブの、補間が、壁を、またぐと、光が、漏れます。

| 対策 | 内容 |
| --- | --- |
| 壁の、両側に、プローブを、置く | 壁の、すぐ近くに、両側から、1 つずつ。補間で、混ざる、範囲が、狭い |
| 可視性による、重み | 補間の、重みを、「そのプローブが、その物の位置を、見通せるか」で、調整（壁の、向こうの、プローブは、重みを 0 に）（[Interpolation Methods](interpolation.md)） |
| ゾーン（部屋）で、分ける | 部屋ごとに、別の、プローブ セット。部屋の、境目では、ブレンド |
| 補間に、法線を、使う | 物の向いている、側の、プローブを、重視 |

## 密度の、調整

<strong>光の変化が、大きい場所</strong>ほど、<strong>密に、置く</strong>と、品質が、上がります。

| 場所 | 間隔の、目安 |
| --- | --- |
| 窓の、近く、光と影の、境目 | 0.5〜1 m |
| 部屋の中 | 1〜2 m |
| 屋外、建物の、周り | 2〜4 m |
| 広場、空き地 | 4〜8 m |
| 遠景 | 8 m 以上、または、置かない |

### 階層構造（カスケード）

<strong>カメラの、近く</strong>は、<strong>密に</strong>、遠くは、疎に、プローブを、入れ子（カスケード）に、並べる方法です（[Geometry Clipmaps](../../terrain/lod/clipmap.md) と、似た発想）。

| カスケード | 範囲 | 間隔 |
| --- | --- | --- |
| 0 | 16 m | 0.5 m |
| 1 | 64 m | 2 m |
| 2 | 256 m | 8 m |

<strong>どの階層でも、プローブの数は、同じ</strong>（たとえば、32×32×32）で、<strong>範囲が、2〜4 倍ずつ、広がり</strong>、間隔も、広がります。カメラの、動きに、合わせて、窓が、動く（円環バッファ）ので、カメラの周りが、常に、細かいです。

## ベイクの、データ

<strong>ベイクした、プローブ</strong>では、<strong>配置のデータ</strong>（位置、SH 係数）を、ファイルに、保存します。ステージの、データと、一緒に、読み込みます。

```cpp
struct ProbeData {
  Vector3 position;
  float3 sh[9];            // SH L2（RGB × 9）
  float validity;          // 0 = 無効（壁の中）、1 = 有効
};
// 全プローブを、配列で、ファイルに保存する。起動時に、GPU のバッファに、読み込む。
```

## よくあるミス

??? failure "プローブが壁の中にあって、暗い・おかしな色になる"
    <strong>壁の中のプローブは無効にして、補間から外す</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 格子 ＋ 手動で補う
    - [x] 変化の大きい所を密に

## 参考

- Greger, Shirley, Hubbard, Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications, Vol. 18, No. 2, 1998（放射照度ボリューム。プローブ GI の原点）
- Tatarchuk, "Irradiance Volumes for Games", Game Developers Conference 2005
- Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（アンビエント ダイスなど）
- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [Probe GI](index.md)
- [Interpolation Methods](interpolation.md)
- [Dynamic Updates](dynamic-update.md)
