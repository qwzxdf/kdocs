---
title: 頂点の工程
tags:
  - 3Dゲーム
  - 描画
---

# 頂点の工程

**モデルの頂点は、最初「そのモデルだけの座標」で書かれています**。これを画面に描くには、世界の座標 → カメラから見た座標 → 画面に写す座標へと、順に変換します。この変換を行うのが頂点シェーダーです。このページでは、4 つの座標空間・変換行列の役割・頂点シェーダーの書き方・数値を使った具体例・頂点シェーダーが出力するものを説明します。

!!! tip "ポイント"
    - 頂点シェーダー ＝ <strong>頂点 1 個を受け取り、変換後の頂点 1 個を返す</strong>小さなプログラム。<strong>頂点の数だけ呼ばれる</strong>。
    - 座標はローカル → ワールド → ビュー → クリップの順に変換される。
    - 変換は行列の掛け算：`ワールド行列`・`ビュー行列`・`射影行列`。まとめて 1 つの行列（WVP）にして1 回の掛け算で済ませる。
    - 頂点シェーダーは最低限、`SV_POSITION`（クリップ空間の位置）を出力する。
    - 法線・UV・色などはそのまま通すか、変換して、ピクセル シェーダーへ渡す。
    - このサイトは左手系・Y 上・+Z 前方・行ベクトル（`v * M`）。

!!! info "このページを読む前に"
    - [描画の流れ（入門）](index.md)（このセクション全体の地図と、読む順番）
    - [行列](../../gamemath/matrices.md)（行列の基礎）
    - [座標系](../../gamemath/coordinate-systems.md)（このサイトの座標系の約束）

## 4 つの座標空間

**同じ点でも、「何を基準にするか」で座標の値が変わります**。基準ごとに名前が付いています。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="4 つの座標空間"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">頂点は 4 つの空間を旅する</text>
<g font-size="12">
<rect x="20" y="50" width="160" height="150" rx="8" fill="#4c8bf5" fill-opacity="0.15" stroke="#4c8bf5" stroke-width="2"/>
<text x="100" y="74" text-anchor="middle" style="font-weight:700">① ローカル空間</text>
<line x1="100" y1="170" x2="100" y2="100" stroke="currentColor"/><line x1="100" y1="170" x2="160" y2="170" stroke="currentColor"/>
<circle cx="125" cy="140" r="5" fill="#e5484d"/><text x="105" y="190" style="font-size:11px">モデルの原点が基準</text>
<rect x="210" y="50" width="160" height="150" rx="8" fill="#2ea043" fill-opacity="0.15" stroke="#2ea043" stroke-width="2"/>
<text x="290" y="74" text-anchor="middle" style="font-weight:700">② ワールド空間</text>
<line x1="230" y1="170" x2="230" y2="110" stroke="currentColor" stroke-opacity="0.5"/><line x1="230" y1="170" x2="350" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="290" y="115" width="30" height="30" fill="#4c8bf5" fill-opacity="0.3" stroke="#4c8bf5"/><circle cx="310" cy="125" r="5" fill="#e5484d"/><text x="230" y="190" style="font-size:11px">世界の原点が基準</text>
<rect x="400" y="50" width="160" height="150" rx="8" fill="#e5aa28" fill-opacity="0.18" stroke="#e5aa28" stroke-width="2"/>
<text x="480" y="74" text-anchor="middle" style="font-weight:700">③ ビュー空間</text>
<polygon points="480,175 440,110 520,110" fill="none" stroke="currentColor" stroke-opacity="0.5"/><circle cx="480" cy="175" r="4" fill="currentColor"/><circle cx="492" cy="135" r="5" fill="#e5484d"/><text x="410" y="190" style="font-size:11px">カメラが原点・前が +Z</text>
<rect x="590" y="50" width="170" height="150" rx="8" fill="#9664e6" fill-opacity="0.18" stroke="#9664e6" stroke-width="2"/>
<text x="675" y="74" text-anchor="middle" style="font-weight:700">④ クリップ空間</text>
<rect x="615" y="95" width="120" height="75" fill="none" stroke="currentColor" stroke-opacity="0.6"/><circle cx="690" cy="125" r="5" fill="#e5484d"/><text x="600" y="190" style="font-size:11px">画面に写す直前の箱</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="181" y1="125" x2="208" y2="125" marker-end="url(#rfa)"/><line x1="371" y1="125" x2="398" y2="125" marker-end="url(#rfa)"/><line x1="561" y1="125" x2="588" y2="125" marker-end="url(#rfa)"/></g>
<g font-size="12">
<text x="195" y="245" text-anchor="middle" style="font-weight:700">ワールド行列</text>
<text x="385" y="245" text-anchor="middle" style="font-weight:700">ビュー行列</text>
<text x="575" y="245" text-anchor="middle" style="font-weight:700">射影行列</text>
<text x="195" y="265" text-anchor="middle" style="font-size:11px">置く・回す・拡大</text>
<text x="385" y="265" text-anchor="middle" style="font-size:11px">カメラ基準に直す</text>
<text x="575" y="265" text-anchor="middle" style="font-size:11px">遠近感を付ける</text>
</g>
</svg>

| 空間 | 基準 | 何のため |
| --- | --- | --- |
| ローカル（モデル） | モデル自身の原点 | モデルを作るときの座標（足元が原点、など） |
| ワールド | 世界の原点 | すべての物を同じ座標で扱う（当たり判定・ライティング） |
| ビュー（カメラ） | カメラの位置が原点、前が +Z | カメラから見た位置を調べる |
| クリップ | 視錐台を箱に変形した空間 | 画面の外を切り落とし、遠近を付ける |

ローカルからワールドへ：モデルを世界に置く（位置・向き・大きさ）。ワールドからビューへ：カメラを原点に動かす（世界全体をカメラの逆に動かす）。ビューからクリップへ：遠近法（近い物は大きく、遠い物は小さく）を付ける。

## 3 つの行列

**空間から空間への移り変わりは、行列の掛け算で表します**。行ベクトル規約（このサイト）では、**`v * W * V * P` と左から右へ掛けます**。

| 行列 | 内容 | 持つのは |
| --- | --- | --- |
| ワールド行列 W | 拡大縮小 → 回転 → 平行移動（物ごとに違う） | 物ごと |
| ビュー行列 V | カメラの位置・向きの逆 | カメラ（フレームに 1 つ） |
| 射影行列 P | 視野角・縦横比・近い面・遠い面 | カメラ（めったに変えない） |

<div class="formula">v_clip = v_local × W × V × P　（行ベクトル。左から順に適用）</div>

3 つを事前に 1 つの行列にまとめて（WVP 行列）、頂点では 1 回だけ掛けるのが一般的です。

```cpp
Matrix world = Matrix::CreateScale(scale) * Matrix::CreateFromQuaternion(rotation) * Matrix::CreateTranslation(position);
Matrix wvp = world * view * projection;
```

詳しい行列の中身は[座標変換（MVP）](../transforms-mvp.md)と[射影](../projection.md)で扱います。

## 頂点シェーダーを書く

**頂点シェーダー**は、入力（頂点属性）を受け取り、出力を返す関数です。

```hlsl
cbuffer PerObject : register(b0) {
  float4x4 world;
  float4x4 view_projection;
};

struct VSInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};

struct VSOutput {
  float4 position : SV_POSITION;
  float3 world_position : TEXCOORD0;
  float3 world_normal : TEXCOORD1;
  float2 uv : TEXCOORD2;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  float4 world_position = mul(float4(input.position, 1.0), world);
  output.position = mul(world_position, view_projection);
  output.world_position = world_position.xyz;
  output.world_normal = mul(input.normal, (float3x3)world);
  output.uv = input.uv;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| `float4(position, 1.0)` | 位置は w = 1 で 4 要素に広げる（平行移動を行列で表すため）。向き（方向）なら w = 0 |
| `mul(行ベクトル, 行列)` | 左から掛ける（行ベクトル規約） |
| `SV_POSITION` | クリップ空間の位置。GPU が必ず必要とする出力 |
| 法線は `(float3x3)world` | 平行移動を無視して、回転・拡大だけ掛ける（位置と同じワールド行列で変換する。非一様な拡大では逆転置行列が必要） |
| UV はそのまま | ピクセルへ渡して、テクスチャを引くために使う |
| 出力のセマンティクス | ピクセル シェーダーが受け取る名前。`TEXCOORD0…` を自由に使う |

## 具体例：数値で追う

**頂点がどう変わるか**を数字で確認します。条件は次のとおりです。

| 設定 | 値 |
| --- | --- |
| カメラ | 原点にいて +Z を向く（ビュー行列は単位行列） |
| 射影 | 視野角 90°・縦横比 1・近い面 1・遠い面 100 |
| 画面 | 800×800 ピクセル |
| 頂点（ワールド） | (3, 1, 10)（右に 3・上に 1・前に 10） |

射影行列を通した結果（クリップ座標）は次のようになります。

<div class="formula">
x_clip = x / tan(45°) = 3　　y_clip = y / tan(45°) = 1<br>
w_clip = z = 10　　z_clip = z · (100/99) − (100/99) ≈ 9.09
</div>

クリップ座標 (3, 1, 9.09, 10) になります。この後 GPU が `w` で割る（[次のページ](clip-viewport.md)）と、(0.3, 0.1, 0.909) になり、画面上の位置が決まります。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="頂点の変換の数値例"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">頂点 (3, 1, 10) の旅</text>
<g font-size="13">
<rect x="20" y="50" width="170" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5"/>
<text x="105" y="76" text-anchor="middle" style="font-weight:700">ワールド座標</text><text x="105" y="100" text-anchor="middle">(3, 1, 10)</text>
<rect x="230" y="50" width="170" height="70" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="315" y="76" text-anchor="middle" style="font-weight:700">ビュー座標</text><text x="315" y="100" text-anchor="middle">(3, 1, 10)</text>
<rect x="440" y="50" width="320" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6"/>
<text x="600" y="76" text-anchor="middle" style="font-weight:700">クリップ座標</text><text x="600" y="100" text-anchor="middle">(3, 1, 9.09, w = 10)</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="192" y1="85" x2="228" y2="85" marker-end="url(#rfa)"/><line x1="402" y1="85" x2="438" y2="85" marker-end="url(#rfa)"/></g>
<text x="210" y="145" text-anchor="middle" style="font-size:11px">ビュー行列</text>
<text x="420" y="145" text-anchor="middle" style="font-size:11px">射影行列</text>
<text x="20" y="190" style="font-size:13px">ポイント：w に「奥行き（z）」が入る。遠い物ほど w が大きい → 後で割ると小さくなる</text>
<text x="20" y="214" style="font-size:13px">これが遠近法（遠い物ほど小さく見える）のしくみ</text>
</svg>

w に奥行きが入ることが遠近法の核心です。後の工程で x・y を w で割ると遠い物（w が大きい）ほど画面の中心に寄って小さく見えます。

<!-- fig:perspective-divide-move:begin -->

<svg class="fig illust motion" data-fig="perspective-divide-move" viewBox="0 0 780 410" role="img"><rect x="0" y="0" width="780" height="410" rx="14" fill="#ffffff"/>
<defs><marker id="arr-perspective-divide-move" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">透視除算:遠ざかるほど w が大きくなり、画面上で小さくなる</text>
<polygon points="150,330 40,60 260,60" fill="#e0f2fe" stroke="#38bdf8" stroke-width="1.5"/>
<circle cx="150" cy="330" r="7" fill="#e5484d"/>
<text x="164" y="346" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">カメラ</text>
<text x="40" y="52" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">視錐台（上から見た図）</text>
<rect x="130" y="290" width="40" height="14" fill="#e5aa28" stroke="#1f2937" stroke-width="1.5"><animate attributeName="y" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;0.0973;0.1184;0.1395;0.1605;0.1816;0.2027;0.2238;0.2449;0.2660;0.2871;0.3082;0.3293;0.3503;0.3714;0.3925;0.4136;0.4347;0.4558;0.4769;0.4980;0.5190;0.5401;0.5612;0.5823;0.6034;0.6245;0.6456;0.6667;1.0000" values="290;290;306;298;290;282;274;266;258;250;242;234;226;218;210;202;194;186;178;170;162;154;146;138;130;122;114;106;98;90;82;82"/></rect>
<rect x="440" y="70" width="260" height="260" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
<text x="440" y="62" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">画面</text>
<rect x="480.0" y="110.0" width="180" height="180" fill="#e5aa28" stroke="#1f2937" stroke-width="2"><animate attributeName="x" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0973;0.1184;0.1395;0.1605;0.1816;0.2027;0.2238;0.2449;0.2660;0.2871;0.3082;0.3293;0.3503;0.3714;0.3925;0.4136;0.4347;0.4558;0.4769;0.4980;0.5190;0.5401;0.5612;0.5823;0.6034;0.6245;0.6456;0.6667;1.0000" values="480;480;500;512.73;521.54;528;532.94;536.84;540;542.61;544.8;546.67;548.28;549.68;550.91;552;552.97;553.85;554.63;555.35;556;556.6;557.14;557.65;558.11;558.55;558.95;559.32;559.67;560;560"/><animate attributeName="y" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0973;0.1184;0.1395;0.1605;0.1816;0.2027;0.2238;0.2449;0.2660;0.2871;0.3082;0.3293;0.3503;0.3714;0.3925;0.4136;0.4347;0.4558;0.4769;0.4980;0.5190;0.5401;0.5612;0.5823;0.6034;0.6245;0.6456;0.6667;1.0000" values="110;110;130;142.73;151.54;158;162.94;166.84;170;172.61;174.8;176.67;178.28;179.68;180.91;182;182.97;183.85;184.63;185.35;186;186.6;187.14;187.65;188.11;188.55;188.95;189.32;189.67;190;190"/><animate attributeName="width" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0973;0.1184;0.1395;0.1605;0.1816;0.2027;0.2238;0.2449;0.2660;0.2871;0.3082;0.3293;0.3503;0.3714;0.3925;0.4136;0.4347;0.4558;0.4769;0.4980;0.5190;0.5401;0.5612;0.5823;0.6034;0.6245;0.6456;0.6667;1.0000" values="180;180;140;114.55;96.92;84;74.12;66.32;60;54.78;50.4;46.67;43.45;40.65;38.18;36;34.05;32.31;30.73;29.3;28;26.81;25.71;24.71;23.77;22.91;22.11;21.36;20.66;20;20"/><animate attributeName="height" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0973;0.1184;0.1395;0.1605;0.1816;0.2027;0.2238;0.2449;0.2660;0.2871;0.3082;0.3293;0.3503;0.3714;0.3925;0.4136;0.4347;0.4558;0.4769;0.4980;0.5190;0.5401;0.5612;0.5823;0.6034;0.6245;0.6456;0.6667;1.0000" values="180;180;140;114.55;96.92;84;74.12;66.32;60;54.78;50.4;46.67;43.45;40.65;38.18;36;34.05;32.31;30.73;29.3;28;26.81;25.71;24.71;23.77;22.91;22.11;21.36;20.66;20;20"/></rect>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 1  →  画面上の大きさ = 1 / 1 = 1.00 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;0.1496;0.1500;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 2  →  画面上の大きさ = 1 / 2 = 0.50 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1496;0.1500;0.2234;0.2238;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 3  →  画面上の大きさ = 1 / 3 = 0.33 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2234;0.2238;0.2972;0.2976;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 4  →  画面上の大きさ = 1 / 4 = 0.25 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2972;0.2976;0.4449;0.4452;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 6  →  画面上の大きさ = 1 / 6 = 0.17 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4449;0.4452;0.6663;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="20" y="384" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">w = 9  →  画面上の大きさ = 1 / 9 = 0.11 倍<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.6663;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="440" y="350" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">x / w, y / w で割るので、遠い物ほど小さい</text>
</svg>

<!-- fig:perspective-divide-move:end -->

## 頂点シェーダーでできること

**変換以外にも頂点シェーダーは自由に位置を変えられます**。

| 用途 | 内容 |
| --- | --- |
| スキニング | 骨の行列で頂点を動かす（[スキニング](../skinning-animation.md)） |
| 波・揺れ | 時間に応じて位置をずらす（水・草・旗） |
| ビルボード | 常にカメラを向く板 |
| インスタンシング | 同じモデルをインスタンスごとの行列で多数描く |
| ハイトマップ | テクスチャで頂点を持ち上げる（[地形](../../graphics/terrain/heightmap-mesh/index.md)） |
| アウトライン | 法線方向に膨らませた裏面で輪郭線 |

## 頂点シェーダーの出力

**頂点シェーダーが返したデータは、三角形の中で補間されて、ピクセル シェーダーへ渡ります**（[ラスタライズ](rasterize.md)）。

| 出力 | 使い道 |
| --- | --- |
| `SV_POSITION` | 必須。画面のどこに描くか |
| ワールド位置 | ライティング（光との距離） |
| ワールド法線 | ライティング（面の向き） |
| UV | テクスチャを引く |
| 頂点カラー | 頂点ごとの色 |
| 接線 | 法線マップ用 |

出力を増やすと頂点シェーダー → ピクセル シェーダーの間のデータ量が増えて重くなるので、必要なものだけにします。

## よくあるミス

??? failure "`mul(行列, ベクトル)` の順序を間違えて、物が消える／歪む"
    **行ベクトル規約**は `mul(ベクトル, 行列)`。掛け順も `W × V × P`。

??? failure "位置の w を 0 にして、平行移動が効かない"
    位置は w = 1、向きは w = 0。

??? failure "法線に平行移動が掛かって、ライティングがおかしい"
    法線は `(float3x3)world` など、平行移動を含まない 3×3 で変換する。非一様スケールは逆転置行列。

??? failure "行列を C++ から渡すとき、転置を忘れて崩れる"
    C++ の行列と HLSL の行列の並び（行優先・列優先）を揃える。SimpleMath は行優先なので、HLSL でも `row_major` か、そのまま（既定が列優先なので `#pragma pack_matrix(row_major)`）。

??? failure "頂点シェーダーでライティングを重く計算して遅い"
    頂点数が多いと頂点側の負荷が上がる。ピクセル単位で計算するほうが普通。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点シェーダー ＝ <strong>頂点 1 個を変換</strong>。頂点の数だけ呼ばれる
    - [x] ローカル → ワールド → ビュー → クリップ。行列（W・V・P）の掛け算
    - [x] `v * W * V * P`（行ベクトル、左手系）。位置は w = 1
    - [x] 出力の `SV_POSITION` は必須。法線・UV は補間してピクセルへ
    - [x] w に奥行きが入る：遠近法の核心

## 参考

- Microsoft, "Vertex Shader Stage"（Microsoft Learn）
- Microsoft, "Coordinate Systems"（Direct3D 9/11 Learn）
- Fabian Giesen, "A trip through the Graphics Pipeline 2011"（Part 3）

## 関連ページ

- [描画の流れ（入門）](index.md)
- [CPU から GPU へ](cpu-to-gpu.md)
- [クリップと画面への写し](clip-viewport.md)
- [座標変換（MVP）](../transforms-mvp.md)
- [射影](../projection.md)
