---
title: Probe Placement
tags:
  - 描画
---

# Probe Placement

<strong>プローブは多いほど精密ですが、メモリとベイクの時間が増えます</strong>。格子状に置く方法と重要な所に手動で置く方法があります。このページでは置き方の方針と、密度の決め方を説明します。

!!! tip "ポイント"
    - 格子状に自動配置 ＋ 重要な所を手動で補う。
    - 光が変化する所（窓・影の境目）は密に。
    - 壁の中に置かない（無効なプローブは、補間から外す）。
    - 密度が低いと光がぼやけ、漏れる。

!!! info "このページを読む前に"
    - [Probe GI](index.md)（このセクション全体の地図と、読む順番）

## 置き方
<strong>プローブの配置</strong>は 品質に直結します。

| 指針 | 内容 |
| --- | --- |
| 光が変化する場所に密に | 明暗の境目・窓の近く・照明の近く |
| 動く物体が通る場所に置く | 通路・部屋・キャラが歩く範囲 |
| 壁の両側に置く | 壁の内側にプローブがあると、反対側の光が混ざる（ライト リーク） |
| 家具の中・壁の中は避ける | 幾何の内部のプローブは、黒（または不正な値）に |
| 高さ方向にも | 床・腰・頭の数段 |
| 自動配置 | 格子を自動生成し、幾何の内側のプローブを除外・補完 |


光が変化する場所には密に置きます。明暗の境目、窓の近く照明の近くです。逆に、変化の小さい広い場所は粗くてかまいません。動く物体が通る場所には必ず置きます。通路、部屋、キャラクターが歩き回る範囲です。壁の両側にそれぞれ置きます。壁の内側にプローブがあると反対側の光が混ざるライト リークが起きるからです。家具や壁の中のような幾何の内部のプローブは、黒や不正な値になるので避けます。高さ方向にも床・腰・頭の数段に置きます。

実際には、まず格子を自動生成して幾何の内側のプローブを除外あるいは補完し、そのうえで重要な場所に手動でプローブを足します。

光が変化する場所には密に置きます。明暗の境目、窓の近く照明の近くです。逆に、変化の小さい広い場所は粗くてかまいません。動く物体が通る場所には必ず置きます。通路、部屋、キャラクターが歩き回る範囲です。壁の両側にそれぞれ置きます。壁の内側にプローブがあると反対側の光が混ざるライト リークが起きるからです。家具や壁の中のような幾何の内部のプローブは、黒や不正な値になるので避けます。高さ方向にも床・腰・頭の数段に置きます。

実際には、まず格子を自動生成して幾何の内側のプローブを除外あるいは補完し、そのうえで重要な場所に手動でプローブを足します。

<!-- fig:probe-light-leak:begin -->

<svg class="fig illust motion" data-fig="probe-light-leak" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-light-leak" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ライト リーク:壁の向こうのプローブが混ざってしまう</text>
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
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">暗い部屋の中の点を壁へ近づける<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="386" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">左:壁の向こうの明るいプローブが混ざり、暗い部屋が明るくなる（漏れ）。右:壁越しは重み 0 → 暗いまま<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:probe-light-leak:end -->

### ライト リーク（壁越しの漏れ）

プローブ間の補間は 壁の存在を知らないので、壁の向こう側のプローブの光がこちら側に漏れることがあります。

| 対策 | 内容 |
| --- | --- |
| プローブの配置の工夫 | 壁の近くを密に・壁の両側にそれぞれ置く |
| 可視性の重み付け | 物体から、プローブが見えるかを判定し見えないプローブの重みを下げる（[DDGI](../ddgi.md)の方式） |
| ボリュームの分割（ゾーン） | 部屋ごとにプローブ グループを分ける |
| 法線バイアス | 物体の位置を法線方向に少しずらして、補間 |


### 適応的な配置

均一な格子は広い空き地では無駄が多く、複雑な室内では足りません。そこで、シーンの複雑さに応じて密度を変える方式があります。Unreal Engine の Volumetric Lightmap は、シーンの幾何の複雑さに応じて、八分木（ブリック）の細かさを変えます。重要な部分（建物の近くなど）は細かいブリック、何もない空は大きなブリックになります。メモリを保ちながら必要な場所に密度を集中できます。

### 適応的な配置

均一な格子は広い空き地では無駄が多く、複雑な室内では足りません。そこで、シーンの複雑さに応じて密度を変える方式があります。Unreal Engine の Volumetric Lightmap は、シーンの幾何の複雑さに応じて、八分木（ブリック）の細かさを変えます。重要な部分（建物の近くなど）は細かいブリック、何もない空は大きなブリックになります。メモリを保ちながら必要な場所に密度を集中できます。

## プローブをどこに置くか

プローブの <strong>数と位置</strong>が GI の品質を決めます。少ないと光がぼやけ多いとメモリと更新が重くなります。光が急に変わる所（壁のすぐ両側、窓の近く）に密に変化のゆるやかな所（広い、空き地）に疎に置くのが基本です。

## 配置の方法

| 方法 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| 均等な格子 | 空間を一定の、間隔（2 m など）で格子状に | 簡単。補間も単純（トライリニア） | 無駄が多い（何もない空間にも置く）。壁の中にプローブが埋まる |
| 手動 | アーティストが重要な場所に置く | 少なく済む（必要な所だけ） | 手間。置き忘れ |
| 自動（ジオメトリに合わせる） | 床、壁、天井の近くに自動で配置 | 無駄が少ない | 実装が複雑 |
| 適応的（光の変化に応じて） | 光が急に変わる場所に自動で細かく置く | 品質と数の、バランスがよい | 複雑。事前計算が重い |

## 格子配置

<strong>最も単純でよく使われる</strong>方法です。空間を立方体の格子に分け格子の頂点にプローブを置きます。

```cpp
// 立方体の範囲に均等な間隔で、プローブを置く。
struct ProbeGrid {
  Vector3 origin;          // 格子の、最小の角（ワールド座標）
  Vector3 spacing;         // 各軸の、プローブの、間隔（メートル）
  int3 count;              // 各軸の、プローブの数
};

Vector3 ProbePosition(const ProbeGrid& g, int x, int y, int z) {
  return g.origin + Vector3(x * g.spacing.x, y * g.spacing.y, z * g.spacing.z);
}
// 例: 64 m × 16 m × 64 m の、場面を 4 m 間隔で → 17 × 5 × 17 = 1,445 個のプローブ。
```

間隔は 光の変化の細かさに、合わせます。部屋の中（光が場所で変わる）は、1〜2 m、屋外の広場は 4〜8 m が目安です。

### 格子の問題

| 問題 | 内容 |
| --- | --- |
| 壁の中に埋まる | 格子の頂点が壁・床の中にある。中のプローブは真っ暗（光が届かない）。補間で周りの明るいプローブに暗さが、混ざる |
| 壁の向こうの光が漏れる | 壁の両側で光がまったく違うのに 1 つの格子のセルに含まれると補間で混ざる |
| 無駄が多い | 地面の下、空中、何もない場所にもプローブを置く |

## 埋まったプローブへの対処

<strong>壁や床の中</strong>に 埋まった、プローブは使えないので検出して、無効にするまたは押し出して外に動かす。

```cpp
// プローブがジオメトリの内側にあるかを調べる（複数方向にレイを飛ばし、裏面に当たる割合）。
bool IsInsideGeometry(const Vector3& pos) {
  int back_hits = 0;
  for (const Vector3& dir : kSampleDirections) {                    // 球面上の、数十方向
    RayHit hit;
    if (Raycast(pos, dir, 100.0f, &hit) && hit.is_back_face) ++back_hits;   // 裏面に当たった = 物体の内側から、見ている
  }
  return back_hits > kSampleDirections.size() * 0.5f;               // 半分以上が裏面 → 内側
}

// 内側のプローブは、最も近い、表面の外へ押し出す（または、無効にする）。
```

プローブから全方向にレイを飛ばし、多くが物体の裏面（物の内側から、見た面）に当たるならそのプローブは、物体の中にあります。無効にするか表面の外へ押し出します。

## 光漏れを防ぐ

<strong>壁の両側</strong>で 光がまったく違うとき（室内と屋外）、プローブの補間が壁をまたぐと光が漏れます。

| 対策 | 内容 |
| --- | --- |
| 壁の両側にプローブを置く | 壁の、すぐ近くに両側から 1 つずつ。補間で混ざる範囲が狭い |
| 可視性による重み | 補間の重みを「そのプローブがその物の位置を見通せるか」で調整（壁の向こうの、プローブは重みを 0 に）（[Interpolation Methods](interpolation.md)） |
| ゾーン（部屋）で分ける | 部屋ごとに別の、プローブ セット。部屋の境目ではブレンド |
| 補間に法線を使う | 物の向いている側の、プローブを重視 |

## 密度の調整

<strong>光の変化が大きい場所</strong>ほど 密に置くと品質が上がります。

| 場所 | 間隔の目安 |
| --- | --- |
| 窓の近く光と影の境目 | 0.5〜1 m |
| 部屋の中 | 1〜2 m |
| 屋外、建物の周り | 2〜4 m |
| 広場、空き地 | 4〜8 m |
| 遠景 | 8 m 以上、または置かない |

### 階層構造（カスケード）

カメラの近くは 密に遠くは疎にプローブを入れ子（カスケード）に並べる方法です（[Geometry Clipmaps](../../terrain/lod/clipmap.md) と、似た発想）。

| カスケード | 範囲 | 間隔 |
| --- | --- | --- |
| 0 | 16 m | 0.5 m |
| 1 | 64 m | 2 m |
| 2 | 256 m | 8 m |

どの階層でもプローブの数は、同じ（たとえば 32×32×32）で、範囲が 2〜4 倍ずつ広がり、間隔も広がります。カメラの動きに合わせて窓が動く（円環バッファ）ので、カメラの周りが常に細かいです。

## ベイクのデータ

<strong>ベイクしたプローブ</strong>では 配置のデータ（位置、SH 係数）をファイルに保存します。ステージのデータと一緒に読み込みます。

```cpp
struct ProbeData {
  Vector3 position;
  float3 sh[9];            // SH L2（RGB × 9）
  float validity;          // 0 = 無効（壁の中）、1 = 有効
};
// 全プローブを配列で、ファイルに保存する。起動時に GPU のバッファに読み込む。
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
