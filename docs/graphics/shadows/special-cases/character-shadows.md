---
title: Character Shadows and Color
tags:
  - 描画
---

# Character Shadows and Color

ゲームで最も長く画面に映るのは、キャラクターです。足元が浮いて見える顔に鼻や顎の汚い影が出る歩くたびに影の縁がちらつく、といった不具合は背景の小さな破綻よりはるかに目立ちます。そのため、キャラクターの影だけは環境全体とは別の設定で作ることが多くなります。このページではまず環境の影がキャラクターに対して粗すぎることを数字で確かめます。次に、キャラクター専用のシャドウマップ、柔らかい影を安く作るカプセル影、影の色と濃さの合成をコードつきで説明します。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。この手法の論文や公式文書は今回は読んでいません。カプセル影の式は幾何から自分で導いたものです。

!!! tip "ポイント"
    - 範囲 50 m のカスケード（2048²）の 1 画素は 24 mm で、高さ 0.2 m の顔に入る画素は約 8 個です。半径 2 m の専用マップなら 1 画素が 1.95 mm で、約 102 個です。
    - カプセル影の柔らかさは受ける点と遮蔽物の距離に比例します。光の見かけの半角が 3° なら 1 m 離れた点で縁のぼけ幅は 0.105 m です。
    - 影の中は真っ黒にせず環境光を残します。直接光だけに影を掛けます。
    - 専用マップの中心はテクセルの整数倍に丸めます。丸めないとキャラクターが動くたびに背景の影の縁が泳ぎます。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と読む順番）
    - [Aliasing and Stabilization](../shadow-map-basics/aliasing-stabilize.md)（テクセル スナップの考え方）

## 環境の影はキャラクターには粗い {#why}

カスケード シャドウマップはカメラの見える範囲を数枚に分けて覆います。1 枚が覆う範囲を `L` m、解像度を 2048 とすると、1 画素は `L / 2048` m です。顔の高さを 0.2 m として、顔に何画素入るかを数えると次のとおりです。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="顔に入る画素数"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">カスケードの範囲と顔の画素数</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,109.8 75.5,111.4 81.0,113.0 86.5,114.6 92.0,116.2 97.5,117.8 103.0,119.4 108.5,121.0 114.0,122.6 119.5,124.2 125.0,125.8 130.5,127.4 136.0,129.0 141.5,130.6 147.0,132.2 152.5,133.8 158.0,135.4 163.5,137.0 169.0,138.6 174.5,140.2 180.0,141.8 185.5,143.4 191.0,145.0 196.5,146.6 202.0,148.2 207.5,149.8 213.0,151.4 218.5,153.0 224.0,154.6 229.5,156.2 235.0,157.8 240.5,159.4 246.0,161.0 251.5,162.6 257.0,164.2 262.5,165.8 268.0,167.5 273.5,169.1 279.0,170.7 284.5,172.3 290.0,173.9 295.5,175.5 301.0,177.1 306.4,178.7 311.9,180.3 317.4,181.9 322.9,183.5 328.4,185.1 333.9,186.7 339.4,188.3 344.9,189.9 350.4,191.5 355.9,193.1 361.4,194.7 366.9,196.3 372.4,197.9 377.9,199.5 383.4,201.1 388.9,202.7 394.4,204.3 399.9,205.9 405.4,207.5 410.9,209.1 416.4,210.7 421.9,212.3 427.4,213.9 432.9,215.5 438.4,217.1 443.9,218.7 449.4,220.3 454.9,221.9 460.4,223.5 465.9,225.1 471.4,226.8 476.9,228.4 482.4,230.0 487.9,231.6 493.4,233.2 498.9,234.8 504.4,236.4 509.9,238.0 515.4,239.6 520.9,241.2 526.4,242.8 531.9,244.4 537.4,246.0"/><circle cx="135.4" cy="128.8" r="4" fill="#4c8bf5"/><text x="143.41201032390637" y="120.79178934903126" text-anchor="start" style="font-size:11px;font-weight:700">41.0</text><circle cx="287.3" cy="173.1" r="4" fill="#4c8bf5"/><text x="295.2939948380468" y="165.0598896236458" text-anchor="start" style="font-size:11px;font-weight:700">8.2</text><circle cx="418.1" cy="211.9" r="4" fill="#4c8bf5"/><text x="426.1180154858596" y="203.8695338825624" text-anchor="start" style="font-size:11px;font-weight:700">2.0</text><circle cx="504.6" cy="237.1" r="4" fill="#4c8bf5"/><text x="512.5879896760937" y="229.0724010984581" text-anchor="start" style="font-size:11px;font-weight:700">0.8</text><line x1="70" y1="104.26810027461451" x2="570" y2="104.26810027461451" stroke="#2e9e5b" stroke-dasharray="5 4"/><text x="564" y="98.26810027461451" text-anchor="end" style="font-size:12px;font-weight:400">専用マップ（半径 2 m、2048）は 102 画素</text><text x="135.41201032390637" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">10</text><text x="287.2939948380468" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">50</text><text x="418.1180154858596" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">200</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1000</text><text x="62" y="234.9347669412812" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="171.60143360794785" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="108.26810027461451" text-anchor="end" style="font-size:11px;font-weight:400">100</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">カスケードが覆う範囲（m、2048²）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">顔（高さ 0.2 m）に入る画素数（対数）</text></svg>

- 範囲 10 m: 画素 4.88 mm、顔に 41.0 画素
- 範囲 25 m: 12.21 mm、16.4 画素
- 範囲 50 m: 24.41 mm、8.2 画素
- 範囲 100 m: 48.83 mm、4.1 画素
- 範囲 200 m: 97.66 mm、2.0 画素
- 範囲 500 m: 244.14 mm、0.8 画素

範囲 50 m で顔が 8 画素しかありません。鼻や顎の自己影を描くには桁が足りません。しかもバイアスは画素の大きさに比例して大きくなります。粗い画素用のバイアスをそのままキャラクターに使うと薄い部分の影が欠けます。キャラクターの影に別の仕組みを使う理由は、これです。

## 専用のシャドウマップ {#dedicated}

キャラクターを囲む小さな範囲だけにシャドウマップを割り当てます。半径 `r` の正射影を `N` 画素で覆うと 1 画素は `2r / N` です。

- 半径 1 m: 1024 で 1.95 mm、2048 で 0.98 mm、4096 で 0.49 mm
- 半径 2 m: 1024 で 3.91 mm、2048 で 1.95 mm、4096 で 0.98 mm
- 半径 3 m: 1024 で 5.86 mm、2048 で 2.93 mm、4096 で 1.46 mm

半径 2 m、2048 の専用マップなら 1 画素が 1.95 mm で、顔に約 102 画素入ります。環境のカスケード（範囲 50 m で約 8 画素）の 12 倍以上です。メモリは 2048² の D32 で 16 MiB、1024² で 4 MiB です（[Rendering Depth](../shadow-map-basics/render-depth.md)）。主役の数体だけにして脇役には使わないのが現実的です。

### 範囲の組み方 {#fit}

光の向きに合わせた正射影でキャラクターの中心を原点に半径 `r` の立方体を覆うように作ります。

```cpp
// キャラクターの中心 c から、光の来る向きに radius だけ引いた位置を、光の位置にする。
// 範囲は ±radius、奥行きは 0〜2*radius の正射影（左手系）。
// 行列の組み立ては DirectXMath の XMMatrixLookAtLH / XMMatrixOrthographicOffCenterLH を使う。
float radius = 2.0f;
Matrix view = XMMatrixLookAtLH(center - light_dir * radius, center, up);
Matrix proj = XMMatrixOrthographicOffCenterLH(-radius, radius, -radius, radius, 0.0f, 2.0f * radius);
```

ここで `light_dir` は「光が進む向き」ではなく、光に向かう向き（太陽の方向）として書くと `center - light_dir * radius` が光の側になります。向きの取り違えはよくある間違いです。この断片は DirectXMath の関数名を使っておりこのページではコンパイルしていません。

### 中心の丸め {#snap}

専用マップの中心をキャラクターに追従させると、キャラクターが動くたびにマップの原点が連続的に動きます。マップの画素の格子が背景に対して、毎フレームずれます。そのため、地面など動かない物の影の縁が、画素の単位で泳ぎます（ちらつき）。中心をテクセルの整数倍に丸めると、格子と背景の関係が固定され泳ぎません。

```text
snapped = floor(center / texel) * texel
```

ここで `texel` は光の座標系での 1 画素の大きさです。実際の実装では光の空間の x と y の 2 軸に対して丸めます。C++ で 1.95 mm の画素に対し、キャラクターを 0.3 mm ずつ 1000 回（合計 0.3 m）動かすと、丸めた中心が動くのは 153 回（約 6.5 ステップに 1 回）でした。丸めた中心は画素の大きさの飛び飛びの値でしか動かないので、背景の影はキャラクターが動いても画素単位で固定されます。

ただし、丸めてもキャラクター自身の影はキャラクターに付いて動くので、そのままです。これで直るのは背景（受ける側）のちらつきです。

## カプセル影 {#capsule}

腕や脚を線分と半径で表したカプセルにして、解析的に影を求める方法があります。シャドウマップを使わないので、解像度に縛られず柔らかい影が安く出ます。変形するキャラクターにも向きます。ただし、形は大まかなカプセルの集まりなので、輪郭の細部は出ません。

### 導出 {#capsule-math}

受ける点を `p`、光に向かう単位ベクトルを `l`、光の見かけの半角を `α` とします。太陽のように大きさのある光は点 `p` から見ると、半角 `α` の円錐です。この円錐がカプセルにどれくらい隠されるかを見ます。

1. **最近点を探す。** 光線 `p + t·l` に最も近い線分上の点 `c` を求めます。線分を `a + s·(b − a)` と書くと光線との最近点の `s` は、2 直線の最近点の式から求まります（光線と線分が平行なら端点にします。足した処理です）。`s` は 0〜1 に収めます。
2. **球とみなす。** その点 `c` を中心とする、半径 `r` の球と考えます。
3. **円錐の半径を求める。** 光線に沿って `c` に最も近い位置までの距離を `t` とすると、そこでの円錐の半径は `w = t × tan α` です。
4. **重なりを見る。** 光線と `c` の距離を `d` とすると、`d ≤ r − w` なら円錐が球に完全に隠れ `d ≥ r + w` なら隠れません。その間は線形に変えます。

<svg class="fig flow" viewBox="0 0 660 350" role="img" aria-label="カプセル影の円錐"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">カプセル影の円錐</text><text x="330" y="22" text-anchor="middle" style="font-size:13px;font-weight:700">カプセル影：光の円錐と球の重なり</text><line x1="70" y1="260" x2="582.8" y2="173.8" stroke="#e5aa28" stroke-width="2" stroke-dasharray="6 4"/><line x1="70" y1="260" x2="522.4" y2="3.7" stroke="#e5aa28" stroke-width="2" stroke-dasharray="6 4"/><line x1="70" y1="260" x2="380" y2="150" stroke="#94a3b8" stroke-width="1.5"/><circle cx="380" cy="150" r="34" fill="rgba(76,139,245,0.25)" stroke="#4c8bf5" stroke-width="2"/><text x="380" y="154" text-anchor="middle" style="font-size:12px;font-weight:400">半径 r</text><circle cx="70" cy="260" r="5" fill="currentColor"/><text x="70" y="280" text-anchor="middle" style="font-size:12px;font-weight:400">受ける点 p</text><text x="320" y="90" text-anchor="start" style="font-size:12px;font-weight:400">円錐の半径 w = t × tan(半角)</text><text x="220" y="212" text-anchor="middle" style="font-size:12px;font-weight:400">t</text><text x="330" y="330" text-anchor="middle" style="font-size:12px;font-weight:400">中心と光線の距離 d が r − w 以下なら完全な影、r + w 以上なら日向。その間は線形</text></svg>

光の半角が 3°（`tan = 0.052`）のとき受ける点と遮蔽物の距離 `t` ごとの縁のぼけ幅 `2 t tan α` は次のとおりです。

- 0.1 m: 0.010 m
- 0.5 m: 0.052 m
- 1.0 m: 0.105 m
- 2.0 m: 0.210 m
- 5.0 m: 0.524 m

足元に近いほど影の縁は鋭く離れるほどぼけます。これは実際の影の見え方（接触硬化）と同じ向きです。シャドウマップの PCF はぼけ幅を固定の半径で決めるので、この性質が出ません。

C++ の関数で脚（線分 (0, 0.1, 0)〜(0, 0.9, 0)、半径 0.12 m）を斜め 45° の光で照らして、地面の影を数えました。光の見える割合は地面の x が −1.2 m で 1.000、−1.0 m で 0.150、−0.8〜0.0 m で 0.000、0.3 m で 1.000 です。影は光と反対側（−x）に伸びて、先端（−1.0 m 付近）が柔らかく消えています。半角 3° は太陽の実際の見かけの大きさより大きい値で、柔らかい影を見せるための一例です。

### コード {#capsule-code}

まず、定数です。

```hlsl
// ---- キャラクターの影：カプセル影と、影の色の合成（左手系・Y 上。リニア空間）----

cbuffer CharacterCB : register(b0) {
  float3 gSunDir;          // 光へ向かう単位ベクトル（ワールド）
  float  gTanHalfAngle;    // 光の見かけの半角の tan。大きいほど柔らかい影。例: tan(3°) ≒ 0.052
  float3 gSunColor;        // 太陽の色 × 強さ（リニア）
  float  gShadowStrength;  // 影の濃さ 0〜1（1 で遮蔽を全部反映）
  float3 gSkyAmbient;      // 空の環境光の色（リニア）。影の中に残る青みの光
  float  gPad0;            // 詰め物
  float3 gGroundAmbient;   // 地面からの照り返しの色（リニア）。下向きの面に効く
  float  gPad1;            // 詰め物
};

static const int kMaxCapsules = 16;      // 1 キャラクターの骨のカプセルの上限（一例）

cbuffer CapsuleCB : register(b1) {
  float4 gCapA[kMaxCapsules];            // xyz: 線分の端点 a（ワールド）、w: 半径
  float4 gCapB[kMaxCapsules];            // xyz: 線分の端点 b、w: 未使用
  uint   gCapCount;                      // 使うカプセルの数
  float3 gPad2;                          // 詰め物
};
```

`gTanHalfAngle` が影の柔らかさを決めます。カプセルの端点は骨のワールド位置から毎フレーム作って、`gCapA`（端点 a と半径）と `gCapB`（端点 b）に詰めます。

1 本のカプセルの遮蔽です。

```hlsl
// 1 本のカプセルが、点 p から光の方向を遮る度合い（0: 遮らない、1: 完全に遮る）。
float CapsuleOcclusion(float3 p, float3 l, float3 a, float3 b, float radius) {
  float3 ab = b - a;                                       // 線分の向き
  float3 pa = a - p;                                       // p から端点 a へ
  float abab = dot(ab, ab);                                // |ab|²
  float abl = dot(ab, l);                                  // ab と l の内積
  float denom = abab - abl * abl;                          // 光線と線分が平行なら 0
  // 光線と線分の最近点のパラメーター s（0〜1）。平行のときは端点 a にする（足した）。
  float s = denom > 1e-6 ? (abl * dot(pa, l) - dot(pa, ab)) / denom : 0.0;
  s = saturate(s);                                         // 線分の外へ出ない
  float3 c = a + ab * s;                                   // 線分上の最近点。ここを球の中心とみなす
  float t = max(dot(c - p, l), 0.0);                       // 光線上で c に最も近い位置までの距離。後ろ側なら 0
  float d = length(c - (p + l * t));                       // 光線と中心の距離
  float w = t * gTanHalfAngle;                             // その距離での光の円錐の半径（遠いほど広い）
  // d が r - w 以下なら全部隠れ、r + w 以上なら隠れない。その間は線形に変える。
  float visible = saturate((d - (radius - w)) / max(2.0 * w, 1e-4));
  return 1.0 - visible;                                    // 遮る度合いに直す
}
```

`s` の式は 2 本の直線の最近点を解いたものです。`denom` が 0 に近いとき光線と線分は平行なので、端点にします。`t` が負になる場合（カプセルが `p` の光と反対側にある場合）は 0 に切ります。その場合は `d` が大きくなるので、遮らないという結果になります。最後に `saturate` で線形の補間を 0〜1 にします。

全部のカプセルを合わせます。

```hlsl
// 全カプセルの影。複数のカプセルの遮蔽を、最も強いものにする（足した: 掛け合わせると重なる所が濃くなりすぎる）。
float CapsuleShadow(float3 p) {
  float occ = 0.0;                                         // ここまでの最大の遮蔽
  for (uint i = 0; i < gCapCount; ++i) {
    occ = max(occ, CapsuleOcclusion(p, gSunDir, gCapA[i].xyz, gCapB[i].xyz, gCapA[i].w));   // 半径は w に入れてある
  }
  return 1.0 - occ;                                        // 光の見える割合
}
```

複数のカプセルの遮蔽は最も強いものを採ります。掛け合わせると腕と胴が重なる所で、影が濃くなりすぎるからです。この選び方は見た目で決めたもので、物理的な根拠はありません。

## 影の色と濃さ {#color}

### 影は真っ黒ではない {#not-black}

影の中にも光は届きます。空の光と周囲の反射光です。直接光だけが影で遮られ環境光は残ります。

```hlsl
// 影の色を考えた合成。shadow は 1: 日向、0: 影。ao は 0〜1（1 = 遮蔽なし）。
float3 ShadeCharacter(float3 albedo, float3 n, float shadow, float ao) {
  float n_dot_l = saturate(dot(n, gSunDir));               // 太陽の当たり具合
  float visibility = lerp(1.0, shadow, gShadowStrength);   // 影の濃さを調整（0 なら影を無効）
  float3 direct = albedo * gSunColor * n_dot_l * visibility;   // 直接光だけが影で遮られる
  float up = n.y * 0.5 + 0.5;                              // 上向きなら 1、下向きなら 0
  float3 ambient = albedo * lerp(gGroundAmbient, gSkyAmbient, up) * ao;   // 環境光は影でも残る。AO で隙間を暗くする
  return direct + ambient;                                 // 影の中でも真っ黒にならない
}
```

`visibility` は `lerp(1, shadow, strength)` です。`strength` が 1 なら影を全部反映し、0 なら影を無効にします。シーンの雰囲気に合わせる調整値です。環境光は上向きの面には空の色（青みがかる）、下向きの面には地面の照り返しの色を使います。AO を掛けると体と地面の隙間などが自然に暗くなります（[AO](../../ao/index.md)）。

### 濃さと明るさの関係 {#strength}

太陽が環境光の 4 倍の明るさ（太陽 1.0、環境光 0.25、`n·l = 1`）のとき影の画素と日向の画素の明るさの比は、`strength` が 1.00 で 0.200、0.75 で 0.400、0.50 で 0.600 です。濃さを 0.75 にしただけで、影の中が日向の 4 割になります。キャラクターは周囲より影を少し薄くすると、顔が潰れず見やすくなります。

### 影の中のキャラクターが浮く {#float}

周りの地面の影の色とキャラクターの影の中の色が合わないとキャラクターが浮いて見えます。同じ環境光（空の色、地面の照り返し）で照らすのが基本です。

## 接地感 {#grounding}

足元が地面に付いて見えるかは影の品質で決まります。環境のシャドウマップは粗いので、複数の仕組みを重ねます。

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="キャラクターの影の層"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">キャラクターの影の層</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">キャラクターの影に重ねるもの（遠くから近くへ）</text><rect x="20" y="50" width="200" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120.0" y="69.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">カスケード</text><text x="240" y="74" text-anchor="start" style="font-size:12px;font-weight:400">環境全体の影・粗い</text><rect x="20" y="100" width="200" height="38" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="120.0" y="119.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">専用シャドウマップ</text><text x="240" y="124" text-anchor="start" style="font-size:12px;font-weight:400">主役の顔や服の鋭い自己影</text><rect x="20" y="150" width="200" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">カプセル影</text><text x="240" y="174" text-anchor="start" style="font-size:12px;font-weight:400">柔らかい大きな影・安い</text><rect x="20" y="200" width="200" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120.0" y="219.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">コンタクト シャドウ</text><text x="240" y="224" text-anchor="start" style="font-size:12px;font-weight:400">足元・接触の細かい影</text><rect x="20" y="250" width="200" height="38" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="120.0" y="269.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">AO・ブロブ</text><text x="240" y="274" text-anchor="start" style="font-size:12px;font-weight:400">隙間と接地の暗がり</text></svg>

- **ブロブ影。** 足元に丸い暗いテクスチャを貼ります。簡単でどんな環境でも安定します（[Blob and Planar Projected Shadows](blob-planar.md)）。
- **コンタクト シャドウ。** 画面空間で足元の短い距離だけレイマーチして、細かい接触の影を補います（[Contact Shadows](../contact-shadows.md)）。
- **AO。** 体と地面の隙間や脇の下の暗がりです。

3 つを組み合わせるとシャドウマップが粗くても、接地感が保てます。

## ちらつきと欠け {#flicker}

- **動くことによるちらつき。** 専用マップの中心を丸めます（前述）。アニメーションで細いパーツが動いて、影が点滅する場合は PCF を広げる（5×5 など）か TAA で平均します。
- **薄い物の欠け。** 髪、マント、細いアクセサリーは薄すぎて深度の差が出ず影が欠けます。影用に厚みを持たせたメッシュを使うか両面を描きます。

## 影を落とす・受ける物の制御 {#flags}

物ごとに影を落とす・受けるのフラグをアーティストが設定できると、調整が楽です。

- **影を落とさない物。** 小さなアクセサリー、銃の細部、眼球です。眼球の影が顔に落ちると不自然に見えます。
- **影を受けない物。** 目、歯、顔の一部です。光り方が不自然になるのを避けます。
- **自己影を弱める。** 顔では鼻の下や顎の影が強すぎると不自然です。顔だけバイアスを大きくするか濃さを下げます。

髪は細いのでシャドウマップでは点にしかなりません。髪専用の影の方法があります（[Hair Shadows](../../skin-hair/hair/shadows.md)、[Skin and Hair](../../skin-hair/index.md)）。

## よくあるミス {#mistakes}

??? failure "顔に鼻や顎の汚い影が出る"
    原因は環境のカスケードの粗いバイアスと画素の大きさのまま顔の自己影を計算していることです。顔だけ専用のバイアスを使い専用マップで描き顔の影の濃さを下げます。

??? failure "キャラクターを動かすと地面の影の縁が泳ぐ"
    原因は専用マップの中心が連続的に動き画素の格子が背景に対してずれることです。中心を `floor(center / texel) * texel` で丸めます。

??? failure "カプセル影が、体の後ろ側にも出る"
    原因は光線の後ろ側のカプセルを数えていることです。`t = max(dot(c − p, l), 0)` で後ろ側を 0 に切っています。この行を消すと光と反対側の物の影も出ます。

??? failure "複数のカプセルが重なる所だけ影が濃すぎる"
    原因は各カプセルの遮蔽を掛け合わせていることです。最大値を採ります。

??? failure "影の中が真っ黒で、キャラクターが浮く"
    原因は環境光が無いか弱すぎることです。空の色の環境光を足し周囲の地面と同じ環境光で照らします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 環境のカスケード（50 m、2048²）では顔に約 8 画素。専用マップ（半径 2 m、2048²）では約 102 画素
    - [x] 専用マップの中心は `floor(center / texel) * texel` で丸める。直るのは背景のちらつき
    - [x] カプセル影の縁のぼけ幅は `2 × 距離 × tan(半角)`。複数のカプセルは最大値を採る
    - [x] 影は直接光だけを遮る。環境光は残す。濃さは `lerp(1, shadow, strength)` で調整
    - [x] 接地感はブロブ影・コンタクト シャドウ・AO を重ねて作る

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>

struct V3 { double x, y, z; };
V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
V3 operator-(V3 a, V3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
double Len(V3 a) { return std::sqrt(Dot(a, a)); }

// カプセル（線分 a-b、半径 r）がつくる柔らかい影。p は受ける点、l は光へ向かう単位ベクトル、
// tan_a は光の見かけの半角の tan。戻り値は光の見える割合（1: 日向、0: 完全な影）。
double CapsuleVisibility(V3 p, V3 l, V3 a, V3 b, double r, double tan_a) {
  // 1. 光線 p + t*l に最も近い、線分上の点を探す（線分を s in [0,1] で表す）。
  const V3 ab = b - a;                         // 線分の向き
  const V3 pa = a - p;                         // p から端点 a へ
  const double abab = Dot(ab, ab);             // |ab|^2
  const double abl = Dot(ab, l);               // ab と l の内積
  const double pal = Dot(pa, l);               // pa と l の内積
  const double paab = Dot(pa, ab);             // pa と ab の内積
  // 2 直線 (a + s*ab) と (p + t*l) の最近点: s は次の式。l は単位ベクトルなので l.l = 1。
  const double denom = abab - abl * abl;       // 2 本が平行なら 0
  double s = denom > 1e-9 ? (abl * pal - paab) / denom : 0.0;   // 平行のときは端点にする（足した）
  s = std::clamp(s, 0.0, 1.0);                 // 線分の外へ出ないように
  const V3 c = a + ab * s;                     // 線分上の最近点（球の中心とみなす）
  // 2. その点を、光線の向きから見た「球」として扱う。
  const double t = std::max(Dot(c - p, l), 0.0);   // 光線上で c に最も近い位置までの距離（後ろ側は 0）
  const V3 q = p + l * t;                      // 光線上の最近点
  const double d = Len(c - q);                 // 光線と中心の距離
  const double w = t * tan_a;                  // その距離での光の円錐の半径
  // 3. 球の半径 r と円錐の半径 w の重なり具合を、線形に近似する。
  //    d <= r - w: 完全に隠れる、d >= r + w: 隠れない、その間は線形。
  const double v = std::clamp((d - (r - w)) / std::max(2.0 * w, 1e-6), 0.0, 1.0);
  return v;
}

// キャラクターの影の範囲の中心を、テクセルの整数倍に丸める（足した: 範囲が動くたびに影がちらつくのを抑える）。
double SnapToTexel(double center, double texel) { return std::floor(center / texel) * texel; }

int main() {
  // 1. カスケードの 1 画素の大きさと、顔（高さ 0.2 m）に何画素入るか。
  std::printf("-- cascade texel size (2048 map) and texels across a 0.2 m face\n");
  for (double extent : {10.0, 25.0, 50.0, 100.0, 200.0, 500.0}) {
    const double texel_mm = extent / 2048.0 * 1000.0;
    std::printf("range %5.0f m: texel = %7.2f mm, face = %6.1f texels\n", extent, texel_mm, 200.0 / texel_mm);
  }

  // 2. キャラクター専用の範囲（半径 r の正射影）の 1 画素の大きさ。
  std::printf("-- character-only map: texel size by radius and resolution\n");
  for (double r : {1.0, 2.0, 3.0}) {
    for (int n : {1024, 2048, 4096}) {
      std::printf("radius %.0f m, %4d: texel = %5.2f mm, face = %5.1f texels\n", r, n, 2.0 * r / n * 1000.0,
                  200.0 / (2.0 * r / n * 1000.0));
    }
  }
  std::printf("memory: 2048^2 D32 = %.0f MiB, 1024^2 D32 = %.0f MiB\n", 2048.0 * 2048 * 4 / 1048576, 1024.0 * 1024 * 4 / 1048576);

  // 3. カプセルの影: 脚（線分 (0,0.1,0)-(0,0.9,0)、半径 0.12 m）を、斜め 45 度上の光で照らす。
  //    光の見かけの半角 3 度（太陽は約 0.27 度だが、柔らかい影にするため大きめにした一例）。
  std::printf("-- capsule shadow along the ground (light elevation 45 deg, half angle 3 deg)\n");
  const V3 a = {0.0, 0.1, 0.0}, b = {0.0, 0.9, 0.0};
  const double rr = 0.12;
  const double tan_a = std::tan(3.0 * 3.14159265358979 / 180.0);
  const V3 l = {std::sqrt(0.5), std::sqrt(0.5), 0.0};            // 光へ向かう方向（+X と +Y）
  for (double x : {-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.3}) {
    const double v = CapsuleVisibility({x, 0.0, 0.0}, l, a, b, rr, tan_a);
    std::printf("ground x = %5.2f m: visibility = %.3f\n", x, v);
  }
  // 影の端のぼけ幅: 受ける点と遮蔽物の距離 t で、円錐の直径は 2 t tan(a)。
  std::printf("-- penumbra width (full angle 6 deg)\n");
  for (double t : {0.1, 0.5, 1.0, 2.0, 5.0}) {
    std::printf("receiver-occluder distance %.1f m: width = %.3f m\n", t, 2.0 * t * tan_a);
  }

  // 4. 中心を丸める効果。キャラクターが 0.3 mm ずつ動くとき、丸めた中心が動く回数。
  std::printf("-- snapping the map center (texel = 1.95 mm)\n");
  const double texel = 4.0 / 2048.0;
  int jumps = 0;
  double prev = SnapToTexel(0.0, texel);
  for (int i = 1; i <= 1000; ++i) {                   // 0.3 mm * 1000 = 0.3 m 動かす
    const double snapped = SnapToTexel(i * 0.0003, texel);
    if (snapped != prev) ++jumps;
    prev = snapped;
  }
  std::printf("moved 0.3 m in 1000 steps of 0.3 mm: center jumps = %d times (every %.2f steps)\n", jumps, 1000.0 / jumps);

  // 5. 影の色: 直接光が遮られた画素で、環境光だけが残る明るさの比。
  std::printf("-- shadowed pixel brightness / lit pixel brightness\n");
  const double sun = 1.0, amb = 0.25;                              // 太陽と環境光の明るさの比の一例（n.l = 1）
  for (double strength : {1.0, 0.75, 0.5}) {
    const double shadow = 1.0 - strength;                          // shadow = lerp(1, 0, strength)
    std::printf("strength %.2f: shadowed / lit = %.3f\n", strength, (sun * shadow + amb) / (sun + amb));
  }
}
```

```text title="実行結果"
-- cascade texel size (2048 map) and texels across a 0.2 m face
range    10 m: texel =    4.88 mm, face =   41.0 texels
range    25 m: texel =   12.21 mm, face =   16.4 texels
range    50 m: texel =   24.41 mm, face =    8.2 texels
range   100 m: texel =   48.83 mm, face =    4.1 texels
range   200 m: texel =   97.66 mm, face =    2.0 texels
range   500 m: texel =  244.14 mm, face =    0.8 texels
-- character-only map: texel size by radius and resolution
radius 1 m, 1024: texel =  1.95 mm, face = 102.4 texels
radius 1 m, 2048: texel =  0.98 mm, face = 204.8 texels
radius 1 m, 4096: texel =  0.49 mm, face = 409.6 texels
radius 2 m, 1024: texel =  3.91 mm, face =  51.2 texels
radius 2 m, 2048: texel =  1.95 mm, face = 102.4 texels
radius 2 m, 4096: texel =  0.98 mm, face = 204.8 texels
radius 3 m, 1024: texel =  5.86 mm, face =  34.1 texels
radius 3 m, 2048: texel =  2.93 mm, face =  68.3 texels
radius 3 m, 4096: texel =  1.46 mm, face = 136.5 texels
memory: 2048^2 D32 = 16 MiB, 1024^2 D32 = 4 MiB
-- capsule shadow along the ground (light elevation 45 deg, half angle 3 deg)
ground x = -1.20 m: visibility = 1.000
ground x = -1.00 m: visibility = 0.150
ground x = -0.80 m: visibility = 0.000
ground x = -0.60 m: visibility = 0.000
ground x = -0.40 m: visibility = 0.000
ground x = -0.20 m: visibility = 0.000
ground x =  0.00 m: visibility = 0.000
ground x =  0.30 m: visibility = 1.000
-- penumbra width (full angle 6 deg)
receiver-occluder distance 0.1 m: width = 0.010 m
receiver-occluder distance 0.5 m: width = 0.052 m
receiver-occluder distance 1.0 m: width = 0.105 m
receiver-occluder distance 2.0 m: width = 0.210 m
receiver-occluder distance 5.0 m: width = 0.524 m
-- snapping the map center (texel = 1.95 mm)
moved 0.3 m in 1000 steps of 0.3 mm: center jumps = 153 times (every 6.54 steps)
-- shadowed pixel brightness / lit pixel brightness
strength 1.00: shadowed / lit = 0.200
strength 0.75: shadowed / lit = 0.400
strength 0.50: shadowed / lit = 0.600
```

## 参考資料 {#references}

このページの式と数字は幾何から導き C++ で確かめたものです。以下の資料の中身は**今回は読んでいません**。

- Michal Valient, "Stable Rendering of Cascaded Shadow Maps", ShaderX6, 2008
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Rouslan Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007

旧版にあった McGuire and Mara, "Efficient GPU Screen-Space Ray Tracing"（Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014）は、コンタクト シャドウのページの資料なので、ここでは外しました。

## 関連ページ {#related}

- [Special Cases](index.md)
- [Shadow Bias](../bias/index.md)
- [Contact Shadows](../contact-shadows.md)
- [Cel Shading](../../postprocess/stylized/cel-shading.md)
