---
title: Ground and Space Views
tags:
  - 描画
---

# Ground and Space Views

地面に立って見上げる空と宇宙から見下ろす惑星では、同じ大気でも見え方がまるで違います。地上では空が頭の上いっぱいに広がり地平線のあたりが白く霞みます。宇宙からは惑星が丸い円盤になりその縁に青い細い帯が光ります。ゲームでロケットや飛行機の上昇を描くならこの 2 つを 1 本につなぐ必要があります。このページでは視点の高さで何が変わるのかを幾何から数え宇宙から見るための積分をコードにし、地上用の方法とつなぐ高さを決めます。

数字は惑星の半径 6360 km、大気の上端 6460 km、レイリーのスケールハイト 8 km という一例の値で、C++ で数えました。HLSL は `fxc`（`ps_5_0`）でコンパイルして確かめたもので、描画した結果は確かめていません。

!!! tip "ポイント"
    - 視点が高くなるほど地平線は水平より下へ落ちます。高さ 1 km で 1.0°、10 km で 3.2°、100 km で 10.1° です。
    - 縁（リム）が青く光るのは、接線方向の視線が大気を長く通るからです。地表すれすれの接線は 2265 km で、真上の 100 km の 22.6 倍です。
    - 接線の高度が 10 km 上がるごとに通る空気の量は約半分になります。縁の帯が細いのはこのためです。
    - 地上用と宇宙用を切り替えるなら高度 50〜150 km（地平線の落ち込みでは約 7〜12°）をなめらかに混ぜます。

!!! info "このページを読む前に"
    - [Atmospheric Scattering](index.md)（このセクション全体の地図と、読む順番）
    - [Hillaire 2020: Four LUTs](hillaire.md)（地上用の LUT。この後ろで混ぜる相手）

## 視点の高さで変わるもの {#overview}

大気の見え方はカメラが大気の中にあるか外にあるかで、分かれます。

| カメラの位置 | 見え方 | 空の描き方 |
| --- | --- | --- |
| 地上（〜数 km） | 空が頭上に広がる | [Sky-View LUT](hillaire.md) |
| 飛行機（約 10 km） | 地平線が少し下がる | Sky-View LUT（高度が入力） |
| 宇宙（100 km 以上） | 惑星が球に見える | 画素ごとに直接積分 |

地上から見る空はカメラを中心にした全方向の色を LUT に描いておき画面では引くだけで済みます。空は滑らかに変わるので低解像度で足ります。宇宙から見ると画面の大半は黒（背景）で、惑星の円盤と縁の大気が一部を占めるだけです。カメラの周りの全方向を描く LUT は、ほとんど使われない方向に計算を使うことになり向きません。画素ごとに視線を大気に向けて直接積分するほうが合います。

<svg class="fig flow" viewBox="0 0 660 240" role="img" aria-label="高度ごとの描き方"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">高度ごとの描き方</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">高度ごとの描き方（境目は一例）</text><rect x="20" y="50" width="190" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="115.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">〜50 km：LUT</text><rect x="225" y="50" width="190" height="60" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="320.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">50〜150 km：混ぜる</text><rect x="430" y="50" width="210" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="535.0" y="80.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">150 km〜：宇宙ビュー</text><line x1="20" y1="150" x2="640" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="330" y="176" text-anchor="middle" style="font-size:12px;font-weight:400">カメラの高度</text><text x="20" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="217" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">50 km</text><text x="422" y="134" text-anchor="middle" style="font-size:11px;font-weight:400">150 km</text><text x="640" y="134" text-anchor="middle" style="font-size:11px;font-weight:400"></text><text x="115" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">地平線の落ち込み 〜7°</text><text x="320" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">7〜12°</text><text x="535" y="208" text-anchor="middle" style="font-size:12px;font-weight:400">12° 以上、円盤が見える</text></svg>

## 高さで変わる幾何 {#geometry}

### 地平線の落ち込み {#dip}

球の上の高さ `h` の点から地平線を見ます。地平線の方向は視線が球にちょうど接する方向です。接点、視点、球の中心を結ぶと接点で直角の三角形ができます。斜辺は `R + h`、接点から中心への辺は `R` なので、視線が水平から下へ下がる角度 `θ` は、次のとおりです。

```text
cos θ = R / (R + h)
接点までの距離 d = sqrt((R + h)² − R²)
```

<svg class="fig flow" viewBox="0 0 660 380" role="img" aria-label="高さによる地平線の落ち込み"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">地平線の落ち込み</text><text x="330" y="22" text-anchor="middle" style="font-size:13px;font-weight:700">高さによる地平線の落ち込み（縮尺は誇張）</text><circle cx="330" cy="330" r="192" fill="rgba(76,139,245,0.18)" stroke="#4c8bf5" stroke-width="2"/><circle cx="330" cy="330" r="170" fill="rgba(148,163,184,0.25)" stroke="#94a3b8" stroke-width="2"/><circle cx="330" cy="150" r="5" fill="#2e9e5b"/><line x1="330" y1="150" x2="385.9" y2="169.4" stroke="#2e9e5b" stroke-width="2"/><line x1="330" y1="150" x2="480" y2="150" stroke="#2e9e5b" stroke-dasharray="4 3"/><text x="318" y="144" text-anchor="end" style="font-size:12px;font-weight:700">地上 1 km</text><circle cx="330" cy="90" r="5" fill="#e5aa28"/><line x1="330" y1="90" x2="450.0" y2="209.6" stroke="#e5aa28" stroke-width="2"/><line x1="330" y1="90" x2="480" y2="90" stroke="#e5aa28" stroke-dasharray="4 3"/><text x="318" y="84" text-anchor="end" style="font-size:12px;font-weight:700">高さ 400 km 相当</text><text x="330" y="338" text-anchor="middle" style="font-size:13px;font-weight:400">惑星</text><text x="180" y="144" text-anchor="start" style="font-size:12px;font-weight:400">大気</text><text x="530" y="110" text-anchor="start" style="font-size:11px;font-weight:400">破線: 水平</text><text x="530" y="126" text-anchor="start" style="font-size:11px;font-weight:400">実線: 地平線の方向</text><text x="530" y="142" text-anchor="start" style="font-size:11px;font-weight:400">落ち込み = acos(R / (R + h))</text></svg>

C++ で数えると高さ 2 m で 0.045°（接点まで 5 km）、1 km で 1.016°（113 km）、10 km で 3.211°（357 km）、100 km で 10.094°（1132 km）、400 km で 19.809°（2291 km）です。地上にいる間は地平線は水平とほとんど変わりません。飛行機の高度では 3° ほど下がり宇宙の高度で急に目立ち始めます。

### 惑星の円盤の大きさ {#disc}

惑星の円盤の半径は視点から `asin(R / (R + h))` の角度に見えます。高さ 400 km（国際宇宙ステーションに近い高さ）で 70.19°、直径で 140.4° です。縦の画角 60°、縦 1080 画素の画面では円盤は画面よりずっと大きく、約 2527 画素になります。静止軌道（高さ約 36000 km）まで離れて初めて、直径が 17.3°（311 画素）まで縮み円盤の全体が収まります。

この違いは描き方に響きます。低軌道では画面いっぱいに惑星の縁が弧として見え大気はその弧に沿った帯です。静止軌道では円盤全体と周りの細い輪が見えます。どちらも、視線が大気の球と交わるかどうかだけで決まるので、同じシェーダーで描けます。

### 縁で光が積もる理由 {#rim}

縁の青い帯は視線が大気を通る距離から説明できます。大気の殻の内側の半径を `Rb`、外側を `Rt` とします。球の中心から最短距離 `b` を通る直線が、殻の内側（半径 `Rt` の球の中）を通る長さは `2 × sqrt(Rt² − b²)` です。

- 地表から真上: 100 km
- 地表から水平（`b = Rb`）: 1132 km（片側）
- 宇宙から見た地表に接する視線: 2265 km（両側）

宇宙から縁を見ると真上の 22.6 倍の距離を通ります。ただし、大気は上へ行くほど薄くなるので、距離だけでは足りません。密度を指数 `exp(−高さ / 8 km)` として視線に沿って積分した「柱密度」を数えます。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="縁の柱密度"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">接点の高度ごとの柱密度</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,82.1 111.7,160.1 153.3,201.9 236.7,236.2 403.3,248.9"/><circle cx="70.0" cy="82.1" r="4" fill="#4c8bf5"/><text x="78.0" y="76.06375" text-anchor="start" style="font-size:11px;font-weight:700">70.7</text><circle cx="111.7" cy="160.1" r="4" fill="#4c8bf5"/><text x="119.66666666666666" y="154.0825" text-anchor="start" style="font-size:11px;font-weight:700">37.9</text><circle cx="153.3" cy="201.9" r="4" fill="#4c8bf5"/><text x="161.33333333333331" y="195.85875" text-anchor="start" style="font-size:11px;font-weight:700">20.3</text><circle cx="236.7" cy="236.2" r="4" fill="#4c8bf5"/><text x="244.66666666666666" y="230.20125000000002" text-anchor="start" style="font-size:11px;font-weight:700">5.8</text><circle cx="403.3" cy="248.9" r="4" fill="#4c8bf5"/><text x="411.3333333333333" y="242.86" text-anchor="start" style="font-size:11px;font-weight:700">0.48</text><line x1="70" y1="247.625" x2="570" y2="247.625" stroke="#e5484d" stroke-dasharray="5 4"/><text x="564" y="241.625" text-anchor="end" style="font-size:12px;font-weight:400">真上（地表から）= 1</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="153.33333333333331" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="236.66666666666666" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">20</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30</text><text x="403.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">40</text><text x="486.6666666666667" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="206.5" text-anchor="end" style="font-size:11px;font-weight:400">20</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">40</text><text x="62" y="111.5" text-anchor="end" style="font-size:11px;font-weight:400">60</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">80</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">接点の高度（km）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">柱密度（真上を 1 とした倍率）</text></svg>

真上から見た柱密度を 1 とすると、地表に接する視線は 70.7 倍、高さ 5 km に接する視線は 37.9 倍、10 km で 20.3 倍、20 km で 5.8 倍、40 km で 0.48 倍、80 km で 0.003 倍です。接線の高度が 10 km 上がるごとに柱密度はおおよそ半分以下になります。縁の帯が細く惑星の縁のすぐ上に集まるのは、この急な減り方のためです。帯の外側（80 km より上）はほとんど光りません。

## 地上から：Sky-View LUT {#ground}

カメラが大気の中にあるなら空はカメラの周りの全方向に広がります。LUT に全方向の色を描き画面ではそれを引きます。作り方は [Hillaire 2020: Four LUTs](hillaire.md) にあるので、ここでは繰り返しません。この LUT はカメラの高さを入力に持つので、高度が上がると地平線の位置が下へ動き滑らかに変わっていきます。

地面の反射も空に効きます。地面が明るい（雪や砂）と地面で反射した光が大気で散乱され地平線の近くが明るくなります。これは多重散乱の一部で単散乱の積分だけでは出ません。地上の LUT がこれをどう扱うかは、上のページを見てください。

## 宇宙から：画素ごとの積分 {#space}

宇宙から見る場合は画面の画素ごとに視線を大気に向けて積分します。コードの全体をまず定数から見ます。

```hlsl
// ---- 宇宙から見た大気（単散乱）。惑星の中心が原点。単位は km。左手系・Y 上。リニア空間 ----

cbuffer SpaceCB : register(b0) {
  float3 gCamPos;        // カメラの位置（惑星の中心から。km）
  float  gBottomR;       // 惑星の半径（km）。例: 6360
  float3 gSunDir;        // 太陽へ向かう単位ベクトル
  float  gTopR;          // 大気の上端の半径（km）。例: 6460
  float3 gSunIlluminance;// 太陽の放射照度（リニア RGB）。単位は見た目に合わせて決める
  float  gMieG;          // ミー散乱の非対称パラメータ g（例: 0.8）
  float3 gGroundAlbedo;  // 地面の反射率（リニア RGB）。単色の例
  uint   gSteps;         // 視線方向の分割数（例: 32）
  float3 gTopLeft;       // 画面の左上へ向かう視線（ワールド、正規化前）
  float  gPad0;          // 詰め物
  float3 gRight;         // 画面の右端 - 左端 の視線ベクトル
  float  gPad1;          // 詰め物
  float3 gDown;          // 画面の上端 → 下端 の視線ベクトル
  float  gPad2;          // 詰め物
};

// 大気の係数（1/km）。値は一例で、地球の大気に近い量を、公開されている資料から借りた概算。今回は原文で確かめていない。
static const float3 kRayleighScatter = float3(5.802, 13.558, 33.1) * 1e-3;   // レイリー散乱（RGB）。短波長ほど大きい
static const float  kMieScatter = 3.996e-3;                                    // ミー散乱（波長に依らない）
static const float  kMieExtinct = 4.44e-3;                                     // ミーの消散 = 散乱 + 吸収
static const float  kRayleighH = 8.0;                                          // レイリーの密度の高さ（km）
static const float  kMieH = 1.2;                                               // ミーの密度の高さ（km）
static const float  kPi = 3.14159265;                                          // 円周率
```

惑星の中心を原点にして単位は km に揃えます。こうするとカメラの高さは `length(gCamPos) − gBottomR` で出ます。`gTopLeft`、`gRight`、`gDown` は画面の四隅へ向かう視線ベクトルで、ピクセルの `uv` から視線を補間して作るために渡します。係数の値（`5.802, 13.558, 33.1` など）は公開されている資料にある地球の大気の値を借りた概算で、原文では今回確かめていません。短い波長ほど大きいので青の係数が一番大きくなります。

### 視線と球の交点 {#ray-sphere}

```hlsl
// 半直線 origin + t * dir と、中心が原点・半径 radius の球の交点。dir は単位ベクトル。
// 戻り値: (近い t, 遠い t)。交わらないとき (-1, -1)。
float2 RaySphere(float3 origin, float3 dir, float radius) {
  float b = dot(origin, dir);                       // origin を dir に射影した長さ
  float c = dot(origin, origin) - radius * radius;  // 球の内側なら負、外側なら正
  float disc = b * b - c;                           // 判別式の 1/4。負なら交わらない
  if (disc < 0.0) return float2(-1.0, -1.0);        // 外れ
  float s = sqrt(disc);                             // 半弦長
  return float2(-b - s, -b + s);                    // 近い方と遠い方
}
```

`RaySphere` は視線と球の連立式を解いて、2 つの交点までの距離を返します。`disc` が負なら交わりません。`origin` が球の中にあるときは `c < 0` で、近い方の `t` が負になり遠い方だけが前方の交点です。これを使って大気の上端の球と惑星の本体の球の 2 つの交点を調べます。

### 密度と位相関数 {#density}

```hlsl
// 高度 alt（km）での、レイリーとミーの密度（1 で地表の密度）。
float2 Density(float alt) {
  return float2(exp(-alt / kRayleighH), exp(-alt / kMieH));   // 指数で薄くなる
}

// 位相関数。cos_t は視線と太陽の方向の cos。
float RayleighPhase(float cos_t) { return 3.0 / (16.0 * kPi) * (1.0 + cos_t * cos_t); }   // 前後対称
float MiePhase(float cos_t, float g) {                                                    // Cornette-Shanks
  float k = 3.0 / (8.0 * kPi) * (1.0 - g * g) / (2.0 + g * g);   // 正規化の係数
  return k * (1.0 + cos_t * cos_t) / pow(max(1.0 + g * g - 2.0 * g * cos_t, 1e-4), 1.5);   // 前方へ偏る
}
```

`Density` はレイリーとミーを別々の高さ（8 km と 1.2 km）で減らします。位相関数は太陽の光がどの向きに散乱されやすいかを表します。レイリーは前後対称でミーは前方（太陽の方向）に強く偏ります。`MiePhase` の `pow` の底に `max(…, 1e-4)` を入れたのは、`g` が 1 に近く `cos_t` が 1 のとき底が 0 に近づくのを避けるためです。

### 太陽の光の届き方 {#sun}

```hlsl
// 点 p から太陽へ向かう光の透過率。惑星の影に入っていれば 0（足した: 影は硬い境目にした）。
float3 SunTransmittance(float3 p) {
  float2 hit = RaySphere(p, gSunDir, gBottomR);     // 太陽方向が惑星に当たるか
  if (hit.y > 0.0 && hit.x > 0.0) return 0.0;       // 惑星の向こう側 → 光が届かない
  float2 top = RaySphere(p, gSunDir, gTopR);        // 大気を抜けるまでの距離
  float len = top.y;                                // p は大気の中なので遠い方
  float2 od = 0.0;                                  // 光学的厚み（レイリー, ミー）
  const int kN = 8;                                 // 太陽方向の分割数（粗くてよい）
  for (int i = 0; i < kN; ++i) {
    float3 q = p + gSunDir * ((i + 0.5) / kN * len);          // 区間の中点
    od += Density(length(q) - gBottomR) * (len / kN);         // 密度 × 区間の長さ
  }
  return exp(-(kRayleighScatter * od.x + kMieExtinct * od.y));   // Beer-Lambert
}
```

点 `p` から太陽の方向へ伸ばした線が、惑星の本体に当たるならその点は影の中にあるので、光は 0 です。この判定は硬い境目になります。実際には太陽に大きさがあるので、影の縁はぼやけます（足した処理で、省いた）。当たらなければ大気の上端までの 8 点で光学的厚みを足し、Beer-Lambert の式 `exp(−厚み)` で光の減り方を返します。8 点は粗いですが太陽方向の透過率は滑らかに変わるので、ここは粗くても目立ちません。

### 本体 {#space-main}

```hlsl
float4 SpaceViewPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float3 dir = normalize(gTopLeft + gRight * uv.x + gDown * uv.y);   // 画素の視線（単位ベクトル）

  float2 top = RaySphere(gCamPos, dir, gTopR);       // 大気の上端との交点
  if (top.y < 0.0) return float4(0, 0, 0, 0);        // 大気に当たらない → 宇宙（背景を見せる）
  float t_enter = max(top.x, 0.0);                   // 入口。カメラがすでに中なら 0

  float2 ground = RaySphere(gCamPos, dir, gBottomR); // 惑星の本体との交点
  bool hit_ground = ground.x > 0.0;                  // 近い交点が前方にあれば、地面に当たる
  float t_exit = hit_ground ? ground.x : top.y;      // 地面まで、またはぬけるまで

  float len = t_exit - t_enter;                      // 積分する長さ
  float dt = len / gSteps;                           // 1 ステップの長さ
  float cos_t = dot(dir, gSunDir);                   // 視線と太陽の cos（位相関数用）
  float3 transmit = 1.0;                             // ここまでの透過率
  float3 lum = 0.0;                                  // 積分した輝度

  for (uint i = 0; i < gSteps; ++i) {
    float3 p = gCamPos + dir * (t_enter + (i + 0.5) * dt);   // 区間の中点
    float2 d = Density(length(p) - gBottomR);                // その高さの密度
    float3 ext = kRayleighScatter * d.x + kMieExtinct * d.y; // 消散係数
    float3 step_t = exp(-ext * dt);                          // この区間の透過率
    float3 scatter = kRayleighScatter * d.x * RayleighPhase(cos_t)
                   + kMieScatter * d.y * MiePhase(cos_t, gMieG);   // 太陽の方向へ散乱される量
    float3 s = SunTransmittance(p) * gSunIlluminance * scatter;    // 区間の光源項
    lum += transmit * (s - s * step_t) / max(ext, 1e-6);     // 区間内で光源項が一定として解析的に積分
    transmit *= step_t;                                      // 次へ進む
  }

  if (hit_ground) {                                          // 地面に当たったとき
    float3 hit_pos = gCamPos + dir * t_exit;                 // 当たった点
    float3 n = normalize(hit_pos);                           // 球なので法線は中心から外向き
    float n_dot_l = saturate(dot(n, gSunDir));               // 昼側だけ照らす
    float3 ground_light = gGroundAlbedo / kPi * gSunIlluminance * n_dot_l * SunTransmittance(hit_pos);   // ランバート
    lum += transmit * ground_light;                          // 大気の透過率を掛けて足す
  }
  return float4(lum, 1.0);                                   // 空気の層を通った輝度
}
```

ステップの流れは次のとおりです。

1. **範囲を決めます。** 視線と大気の上端の交点がなければ、背景（宇宙）が見えるだけなので、何も描きません。あれば入口 `t_enter` を決めます。カメラがすでに大気の中にあるなら入口は 0 です。
2. **出口を決めます。** 視線が惑星の本体に当たるなら当たる点までが積分の範囲です。当たらないなら大気を突き抜けます。
3. **区間を刻みます。** 範囲を `gSteps` 個に分け各区間の中点で密度を読みます。
4. **光源項を作ります。** 各点で太陽の光（影を含む透過率）に散乱の係数と位相関数を掛けます。
5. **解析的に積分します。** `lum += transmit * (s − s·step_t) / ext` は区間の中で光源項が一定として、積分を厳密に解いたものです。単純に `s × dt` を足すよりステップ数が少なくても安定します。
6. **地面に当たったら足します。** 地面の色をランバート反射と太陽の光の透過率、視線の透過率で足します。昼側では青い大気越しに地面や海が見え夜側では暗くなります。

地面の色が単色（アルベドの平均）では惑星らしく見えないので、本物の惑星は大陸と海を描いたテクスチャ（キューブマップ）で差し替えます。夜側に街の光を足すのも同じ場所です。

### 縁が自然に出ること {#rim-code}

このコードに縁のための特別な処理はありません。接線に近い視線は `t_exit − t_enter` が長く各ステップで通る空気も多いので、積分が自然に大きな値を返します。逆に、惑星の中心を通る視線は大気を 100 km 通るだけです。縁が明るく見えるのは距離と密度の積分が、そう答えるからです。

## 地上から宇宙へのつなぎ {#transition}

高度に応じて地上用の LUT と宇宙ビューを切り替えます。境目が目立たないようになめらかに混ぜます。

```hlsl
// 地上用 LUT と宇宙ビューの混ぜ具合。altitude は km。
// 重みの境目（50 km と 150 km）は一例。足した処理。
float SpaceBlend(float altitude) {
  return smoothstep(50.0, 150.0, altitude);          // 0: 地上用 LUT のみ、1: 宇宙ビューのみ
}
```

50 km と 150 km は一例です。地平線の落ち込みで言うと約 7.2° から 12.3° の範囲です。地上用の LUT はカメラの周りの全方向を貼るという前提なので、地平線が下がるにつれて LUT の下半分（地面）の面積が増えます。宇宙ビューの結果とは解像度の差による小さなずれがあります。混ぜる幅を広く取るとずれは目立たなくなります。

## よくあるミス {#mistakes}

??? failure "宇宙から見た惑星に大気の縁が出ない"
    原因は視線が大気の球と交わるかを調べず地面（惑星の本体）にだけ当てていることです。大気の上端の球との交点を先に求め視線が惑星に当たらなくても、大気を通った分を積分します。

??? failure "地面を通り抜けた先まで積分して、縁が白く飽和する"
    原因は視線が惑星の本体に当たるのに、大気の出口を上端の遠い交点にしていることです。当たるなら当たる点までで積分を止めます（`t_exit` を `ground.x` にする）。

??? failure "夜側にも大気が光る"
    原因は太陽方向の透過率に惑星の影の判定が入っていないことです。点から太陽へ伸ばした線が惑星に当たるかを調べて、当たるなら 0 にします。

??? failure "地上と宇宙の境目で空の色が飛ぶ"
    原因は 2 つの方式で定数（散乱係数、太陽の放射照度）が違うことです。係数と単位を同じ値で共有します。混ぜる幅を狭くしすぎても飛びます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 地平線の落ち込みは `acos(R / (R + h))`。1 km で 1°、100 km で 10°
    - [x] 縁が光るのは、接線方向の視線が長くかつ空気が多いから。接線高度が 10 km 上がるごとに半分以下
    - [x] 宇宙からは画素ごとに積分する。大気の上端の球との交点が積分の入口、本体に当たるならそこが出口
    - [x] 影の判定は太陽方向に惑星があるか
    - [x] 切り替えは 50〜150 km で混ぜる（一例）

## C++ で数えたもの {#numbers}

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;     // 円周率
const double kDeg = 180.0 / kPi;         // ラジアン -> 度
const double kRb = 6360.0;               // 惑星の半径（km）。地球に近い一例
const double kRt = 6460.0;               // 大気の上端の半径（km）。厚さ 100 km の一例
const double kScaleH = 8.0;              // レイリー散乱の密度の高さ（スケールハイト、km）

// 地表から高度 h（km）の点が見る、地平線の「落ち込み」（水平から下へ何度か）。
// 地平線の方向は球に接するので、中心・視点・接点が直角三角形を作り、cos(dip) = R / (R + h)。
double HorizonDipDeg(double h) { return std::acos(kRb / (kRb + h)) * kDeg; }

// 接点までの距離（km）。三平方の定理: d^2 = (R+h)^2 - R^2。
double HorizonDistance(double h) { return std::sqrt((kRb + h) * (kRb + h) - kRb * kRb); }

// 惑星の見かけの半径（度）。視点から見て、惑星の円盤の中心から縁までの角度。
double PlanetAngularRadiusDeg(double h) { return std::asin(kRb / (kRb + h)) * kDeg; }

// 中心から最短距離 b（km）の直線が、大気の殻（半径 kRt の球の内側）を通る長さの半分。
double HalfChord(double b) { return std::sqrt(kRt * kRt - b * b); }

// 最接近距離 b の直線に沿って、レイリーの密度 exp(-(r-Rb)/H) を積分した「柱密度」（km 単位の等価な長さ）。
// 直線上の位置 s（最接近点が 0）で、中心からの距離 r = sqrt(b^2 + s^2)。
double ColumnDensity(double b) {
  const double half = HalfChord(b);               // 大気に入ってから最接近点までの長さ
  const int n = 200000;                           // 分割数（十分細かく）
  const double ds = half / n;                     // 1 区間の長さ
  double sum = 0.0;                               // 片側の積分値
  for (int i = 0; i < n; ++i) {
    const double s = (i + 0.5) * ds;              // 区間の中点
    const double r = std::sqrt(b * b + s * s);    // 中心からの距離
    sum += std::exp(-(r - kRb) / kScaleH) * ds;   // 密度 × 長さ
  }
  return 2.0 * sum;                               // 最接近点の前後を足す
}

int main() {
  std::printf("-- horizon dip, distance, planet angular radius (Rb = %.0f km)\n", kRb);
  for (double h : {0.002, 1.0, 10.0, 50.0, 100.0, 150.0, 400.0}) {
    std::printf("h=%8.3f km: dip = %6.3f deg, horizon distance = %7.1f km, planet radius seen = %6.2f deg\n", h,
                HorizonDipDeg(h), HorizonDistance(h), PlanetAngularRadiusDeg(h));
  }

  std::printf("-- planet disc size on screen (vertical fov 60 deg, 1080 px)\n");
  for (double h : {100.0, 400.0, 36000.0}) {
    const double diameter = 2.0 * PlanetAngularRadiusDeg(h);                 // 円盤の直径（度）
    std::printf("h=%7.0f km: disc diameter = %6.1f deg = %6.0f px (screen height 1080 px = 60 deg)\n", h, diameter,
                diameter / 60.0 * 1080.0);
  }

  std::printf("-- path length through the shell (Rb = %.0f, Rt = %.0f)\n", kRb, kRt);
  std::printf("straight up from the ground: %.0f km\n", kRt - kRb);
  std::printf("horizontal from the ground (b = Rb): %.0f km\n", HalfChord(kRb));
  std::printf("limb seen from space, tangent at the ground: %.0f km\n", 2.0 * HalfChord(kRb));
  std::printf("limb / vertical = %.1f\n", 2.0 * HalfChord(kRb) / (kRt - kRb));

  std::printf("-- Rayleigh column density along a straight line (km-equivalent, H = %.0f km)\n", kScaleH);
  const double vertical = kScaleH * (1.0 - std::exp(-(kRt - kRb) / kScaleH));   // 真上は解析解
  std::printf("vertical from the ground: %.3f (analytic)\n", vertical);
  for (double z : {0.0, 5.0, 10.0, 20.0, 40.0, 80.0}) {                        // 接点の高度
    const double c = ColumnDensity(kRb + z);
    std::printf("limb tangent at %4.0f km: column = %8.3f = %6.2f x vertical\n", z, c, c / vertical);
  }

  std::printf("-- transition by dip angle\n");
  for (double h : {20.0, 50.0, 100.0, 150.0}) {
    std::printf("h=%4.0f km: dip = %5.2f deg\n", h, HorizonDipDeg(h));
  }
}
```

```text title="実行結果"
-- horizon dip, distance, planet angular radius (Rb = 6360 km)
h=   0.002 km: dip =  0.045 deg, horizon distance =     5.0 km, planet radius seen =  89.95 deg
h=   1.000 km: dip =  1.016 deg, horizon distance =   112.8 km, planet radius seen =  88.98 deg
h=  10.000 km: dip =  3.211 deg, horizon distance =   356.8 km, planet radius seen =  86.79 deg
h=  50.000 km: dip =  7.161 deg, horizon distance =   799.1 km, planet radius seen =  82.84 deg
h= 100.000 km: dip = 10.094 deg, horizon distance =  1132.3 km, planet radius seen =  79.91 deg
h= 150.000 km: dip = 12.323 deg, horizon distance =  1389.4 km, planet radius seen =  77.68 deg
h= 400.000 km: dip = 19.809 deg, horizon distance =  2290.9 km, planet radius seen =  70.19 deg
-- planet disc size on screen (vertical fov 60 deg, 1080 px)
h=    100 km: disc diameter =  159.8 deg =   2877 px (screen height 1080 px = 60 deg)
h=    400 km: disc diameter =  140.4 deg =   2527 px (screen height 1080 px = 60 deg)
h=  36000 km: disc diameter =   17.3 deg =    311 px (screen height 1080 px = 60 deg)
-- path length through the shell (Rb = 6360, Rt = 6460)
straight up from the ground: 100 km
horizontal from the ground (b = Rb): 1132 km
limb seen from space, tangent at the ground: 2265 km
limb / vertical = 22.6
-- Rayleigh column density along a straight line (km-equivalent, H = 8 km)
vertical from the ground: 8.000 (analytic)
limb tangent at    0 km: column =  565.676 =  70.71 x vertical
limb tangent at    5 km: column =  302.903 =  37.86 x vertical
limb tangent at   10 km: column =  162.196 =  20.27 x vertical
limb tangent at   20 km: column =   46.506 =   5.81 x vertical
limb tangent at   40 km: column =    3.823 =   0.48 x vertical
limb tangent at   80 km: column =    0.025 =   0.00 x vertical
-- transition by dip angle
h=  20 km: dip =  4.54 deg
h=  50 km: dip =  7.16 deg
h= 100 km: dip = 10.09 deg
h= 150 km: dip = 12.32 deg
```

## 参考資料 {#references}

このページの式と数字は幾何から導いて C++ で確かめたものです。以下の資料の中身は**今回は読んでいません**。係数の値の出どころ（Hillaire の資料）も記憶に基づく概算で、原文では確かめていません。

- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Eric Bruneton, Fabrice Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Tomoyuki Nishita, Takao Sirai, Katsumi Tadamura, Eihachiro Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ {#related}

- [Atmospheric Scattering](index.md)
- [Bruneton Precomputed Scattering](bruneton.md)
- [Hillaire 2020: Four LUTs](hillaire.md)
