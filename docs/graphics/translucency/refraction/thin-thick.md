---
title: Thin and Thick Glass
tags:
  - 描画
---

# Thin and Thick Glass

窓ガラスの向こうの景色はほとんどそのままに見えます。ところが、ガラスの玉の向こうは上下左右が逆になり水を入れたコップは景色を大きくゆがめます。同じ「ガラス」でも光の曲がり方がまるで違います。全部を同じ重い屈折の計算で描くと窓ガラスに無駄な計算をかけることになり逆に窓ガラスの簡単な計算で玉を描くと、玉らしく見えません。このページでは板で屈折がほとんど相殺される理由を式で示し、球で光がどう曲がるかを数え薄いガラス、曇りガラス、厚いガラスを使い分けるコードを書きます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。屈折の式はスネルの法則から自分で導いたものです。Wyman の論文は今回読んでいないので、論文の手順の再現とは言えません。

!!! tip "ポイント"
    - 平行な板を通る光は向きが変わらず横にずれるだけです。6 mm の窓ガラスに 45° で入っても、ずれは 1.97 mm です。
    - 球では端を通る光ほど強く曲がります。屈折率 1.5 の球は近軸の焦点が中心から 1.5R ですが、端（高さ 0.9R）を通る光は 1.104R で光軸と交わります。
    - 厚みを前面と背面の深度の差で見積もると、高さ 0.7R を通る光では実際の弦より 19.3% 短くなります。
    - 球の 1 回の通過では出口で全反射は起きません。全反射が起きるのは形がもっと複雑なときです。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と読む順番）
    - [Screen-Space Refraction](screen-space.md)（画面空間のずらしで屈折を作る方法）

## 薄いガラスと厚いガラス {#overview}

ガラスの扱いは光がガラスの中でどれだけ曲がるかで決まります。平行な板の窓は屈折がほとんど目立たず向こうの景色がそのまま見えます。球や瓶、宝石のような曲面の塊は光が入口と出口で別々の向きの面を通るので、向きが大きく変わり像が拡大・縮小・反転します。

| 種類 | 例 | 屈折 | 表現 |
| --- | --- | --- | --- |
| 薄いガラス | 窓・ガラス戸 | ほぼ無視 | 透過 + 反射 |
| 厚いガラス | 瓶・水晶球・宝石 | 目立つ | 屈折 + 厚みの色 + 反射 |
| 曇りガラス | すりガラス | ぼやける | 粗さに応じたミップ |

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="モデルの選び方"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">モデルの選び方</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">ガラスの種類で、モデルを選ぶ</text><rect x="20" y="50" width="170" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="105.0" y="69.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">窓・ガラス板</text><line x1="190" y1="69" x2="220" y2="69" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="230" y="74" text-anchor="start" style="font-size:12px;font-weight:400">薄いガラス：ごく小さなずらし + 反射</text><rect x="20" y="100" width="170" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="105.0" y="119.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">曇りガラス</text><line x1="190" y1="119" x2="220" y2="119" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="230" y="124" text-anchor="start" style="font-size:12px;font-weight:400">粗さのミップで背景を読む</text><rect x="20" y="150" width="170" height="38" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="105.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">瓶・球・宝石</text><line x1="190" y1="169" x2="220" y2="169" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="230" y="174" text-anchor="start" style="font-size:12px;font-weight:400">厚いガラス：2 回屈折</text><rect x="20" y="200" width="170" height="38" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="105.0" y="219.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">凹んだ・複雑な形</text><line x1="190" y1="219" x2="220" y2="219" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="230" y="224" text-anchor="start" style="font-size:12px;font-weight:400">レイトレーシング・事前に焼く</text><rect x="20" y="250" width="170" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="105.0" y="269.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">コップ・ボトル</text><line x1="190" y1="269" x2="220" y2="269" stroke="currentColor" stroke-width="2" marker-end="url(#f3)"/><text x="230" y="274" text-anchor="start" style="font-size:12px;font-weight:400">薄い壁 + 中身を別の厚い塊として</text></svg>

## 平行な板では屈折が相殺する {#plate}

### 導出 {#plate-math}

厚さ `t`、屈折率 `n` の平行な板に法線から角度 `θ` で光が入ります。入口でスネルの法則 `sin θ = n sin φ` で曲がり板の中を角度 `φ` で進みます。出口の面は入口の面と平行なので、中の光は出口で `φ` から `θ` に戻ります。出てきた光は入る前と同じ向きです。違うのは横にずれていることだけです。ずれの大きさは板の中を進む長さ `t / cos φ` に向きの差 `sin(θ − φ)` を掛けたものです。

```text
sin φ = sin θ / n
横ずれ = t × sin(θ − φ) / cos φ
```

### 数字 {#plate-numbers}

`n = 1.5` として窓ガラス（6 mm）と分厚い板（50 mm）の横ずれは、次のとおりです。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="平行な板の横ずれ"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">板の横ずれ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 81.2,249.7 92.5,249.5 103.7,249.2 114.9,248.9 126.2,248.7 137.4,248.4 148.7,248.1 159.9,247.8 171.1,247.5 182.4,247.2 193.6,246.9 204.8,246.6 216.1,246.3 227.3,245.9 238.5,245.6 249.8,245.2 261.0,244.8 272.2,244.5 283.5,244.0 294.7,243.6 306.0,243.2 317.2,242.7 328.4,242.3 339.7,241.8 350.9,241.2 362.1,240.7 373.4,240.1 384.6,239.6 395.8,238.9 407.1,238.3 418.3,237.7 429.6,237.0 440.8,236.3 452.0,235.6 463.3,234.8 474.5,234.1 485.7,233.3 497.0,232.6 508.2,231.8 519.4,231.0 530.7,230.2 541.9,229.4 553.1,228.7 564.4,227.9"/><text x="320.0" y="231.2395563512331" text-anchor="start" style="font-size:12px;font-weight:700">窓ガラス 6 mm</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 81.2,247.8 92.5,245.6 103.7,243.3 114.9,241.1 126.2,238.8 137.4,236.5 148.7,234.2 159.9,231.8 171.1,229.3 182.4,226.8 193.6,224.3 204.8,221.6 216.1,218.9 227.3,216.1 238.5,213.2 249.8,210.2 261.0,207.0 272.2,203.8 283.5,200.4 294.7,196.9 306.0,193.2 317.2,189.4 328.4,185.5 339.7,181.3 350.9,177.0 362.1,172.5 373.4,167.8 384.6,162.9 395.8,157.9 407.1,152.6 418.3,147.2 429.6,141.6 440.8,135.8 452.0,129.8 463.3,123.7 474.5,117.4 485.7,111.1 497.0,104.6 508.2,98.1 519.4,91.6 530.7,85.1 541.9,78.6 553.1,72.3 564.4,66.0"/><text x="320.0" y="166.99630292694235" text-anchor="start" style="font-size:12px;font-weight:700">分厚い板 50 mm</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="238.53932584269663" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="407.07865168539325" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">89°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="216.0" text-anchor="end" style="font-size:11px;font-weight:400">10</text><text x="62" y="178.0" text-anchor="end" style="font-size:11px;font-weight:400">20</text><text x="62" y="140.0" text-anchor="end" style="font-size:11px;font-weight:400">30</text><text x="62" y="102.0" text-anchor="end" style="font-size:11px;font-weight:400">40</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">50</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">入射角（法線から）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">横ずれ（mm、n = 1.5）</text></svg>

- 入射角 15°: 6 mm で 0.54 mm、50 mm で 4.48 mm
- 30°: 1.16 mm、9.69 mm
- 45°: 1.97 mm、16.46 mm
- 60°: 3.07 mm、25.62 mm
- 75°: 4.49 mm、37.40 mm
- 85°: 5.51 mm、45.94 mm

窓ガラスのずれは 45° でも約 2 mm です。向こうの景色が約 2 mm 動いて見えるだけなので、無視しても気づかれません。ずれは板の厚さに比例します。50 mm の水槽の壁のような厚い板なら 45° で 16 mm 動くので、気づかれ始めます。

薄いガラスでは屈折を省略して、フレネル反射、汚れ厚みによるわずかな色を主役にします。曲がった窓（曲面）は場所によって入口と出口の面が平行でなくなるので、この近似は正確には成り立ちません。それでもごく浅い曲がりなら小さなずらしで足ります。

## 薄いガラスのコード {#thin}

ここからコードを数行ずつ見ます。最初は定数と読む資源です。

```hlsl
// ---- 薄いガラス・厚いガラス・曇りガラス（左手系・Y 上。リニア空間）----

cbuffer GlassCB : register(b0) {
  float4x4 gViewProj;      // ビュー × 射影（行ベクトル）
  float3 gCameraPos;       // カメラ位置（ワールド）
  float  gIor;             // 屈折率 n。ガラス 1.5、水 1.33、ダイヤモンド 2.42
  float3 gTint;            // 吸収の色（リニア）。厚みで効く。白なら無色
  float  gAbsorb;          // 吸収の強さ（1/m）。厚み 1 m あたり
  float  gThinShift;       // 薄いガラスのずらし量（UV）。ごく小さい値。例: 0.002
  float  gMaxMip;          // 背景コピーの最大ミップ。例: 8
  float  gRoughness;       // 曇りガラスの粗さ 0〜1
  float  gPad;             // 詰め物
};

Texture2D<float4> gSceneCopy : register(t0);   // 不透明物を描いた後の画面のコピー（ミップつき）
Texture2D<float>  gBackDepth : register(t1);   // ガラスの背面のカメラからの距離（m、リニア）
Texture2D<float4> gBackNormal: register(t2);   // ガラスの背面の法線（ワールド。xyz は外向き）
SamplerState gLinear : register(s0);           // 線形・クランプ
```

`gSceneCopy` は不透明物を描いた後の画面のコピーで、ミップチェーンを持たせます（曇りガラスで使います）。`gBackDepth` と `gBackNormal` はガラスの背面を先に描いて残した距離と法線で、厚いガラスで使います。

反射の割合を求めるフレネルです。

```hlsl
// シュリック近似の反射率。cos_i は法線と視線の cos、n は屈折率。
float Fresnel(float cos_i, float n) {
  float f0 = pow((n - 1.0) / (n + 1.0), 2.0);          // 垂直入射の反射率。n = 1.5 で 0.04
  return f0 + (1.0 - f0) * pow(1.0 - saturate(cos_i), 5.0);   // 縁ほど反射が増える
}
```

シュリック近似の垂直入射の反射率 `F0 = ((n − 1) / (n + 1))²` は、ガラス（1.5）で 0.040、水（1.33）で 0.020、ダイヤモンド（2.42）で 0.172 です。ダイヤモンドは垂直に見ても 17% 反射するので、金属のように光ります。縁（`cos_i` が 0 に近い）ではどの物質も反射が 1 に近づきます。

窓ガラスのシェーダーです。

```hlsl
// ---- 薄いガラス：屈折はほぼ無視。ごく小さいずらし + 反射 + 色 ----
float3 ThinGlass(float3 world_pos, float3 n, float2 screen_uv, float3 env_color) {
  float3 v = normalize(gCameraPos - world_pos);               // 表面からカメラへ
  float2 uv = screen_uv + n.xy * gThinShift;                  // 法線の傾きで、ごく小さくずらす（足した近似）
  float3 behind = gSceneCopy.SampleLevel(gLinear, uv, 0).rgb;  // ガラスの向こう
  float fr = Fresnel(dot(n, v), gIor);                         // 反射の割合
  return lerp(behind, env_color, fr);                          // 透過 + 反射のみ
}
```

法線の `xy` に `gThinShift` を掛けて、背景を読む位置をごく小さくずらします。これは足した近似で物理的な屈折の式ではありません。ずらし量は 0.002（画面幅の 0.2%）程度にします。反射は環境の色（`env_color`）を `fr` の割合で混ぜます。透過 + 反射だけで窓ガラスは成り立ちます。

## 曇りガラス {#frosted}

すりガラスは表面の細かい凹凸で光がばらばらに曲がり背景がぼやけて見えます。粗い面ほどぼけが大きくなります。粗さに応じて背景のコピーのミップを読めば近似できます。

```hlsl
// ---- 曇りガラス：粗さに応じたミップで背景を読む ----
float3 FrostedGlass(float2 refract_uv) {
  float mip = gRoughness * gMaxMip;                            // 粗いほど深いミップ（ぼけが大きい）
  return gSceneCopy.SampleLevel(gLinear, refract_uv, mip).rgb; // ブラー済みの背景を読む
}
```

ミップはダウンサンプルで事前にぼかされているので、1 回の読み込みで大きなぼけが得られます（[ブルームのダウンサンプル](../../postprocess/bloom/index.md)と同じ考え方です）。ミップを使う方法の欠点はぼけの形が正方形に近くなることとミップ間の補間で段差が見えることです。気になる場合は複数回サンプルを混ぜます。

## 球で光はどう曲がるか {#sphere}

厚いガラスの代表は球です。光軸と平行な光を球に当てスネルの法則を 2 回使って、出た光が光軸と交わる位置を数えました（半径 `R = 1`、`n = 1.5`）。

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="球を通る光線"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ガラス球の屈折</text><text x="330" y="22" text-anchor="middle" style="font-size:13px;font-weight:700">ガラス球（n = 1.5）を通る平行光</text><circle cx="330" cy="150" r="100" fill="rgba(76,139,245,0.18)" stroke="#4c8bf5" stroke-width="2"/><polyline fill="none" stroke="#e5484d" stroke-width="2" points="140.0,60.0 286.4,60.0 428.6,133.4 521.3,263.7"/><polyline fill="none" stroke="#e5aa28" stroke-width="2" points="140.0,100.0 243.4,100.0 428.8,134.5 578.1,191.9"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2" points="140.0,130.0 232.0,130.0 429.8,143.4 588.3,165.0"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2" points="140.0,170.0 232.0,170.0 429.8,156.6 588.3,135.0"/><polyline fill="none" stroke="#e5aa28" stroke-width="2" points="140.0,200.0 243.4,200.0 428.8,165.5 578.1,108.1"/><polyline fill="none" stroke="#e5484d" stroke-width="2" points="140.0,240.0 286.4,240.0 428.6,166.6 521.3,36.3"/><circle cx="480.0" cy="150" r="4" fill="currentColor"/><text x="480.0" y="138" text-anchor="middle" style="font-size:12px;font-weight:400">近軸の焦点 1.5R</text><text x="330" y="290" text-anchor="middle" style="font-size:12px;font-weight:400">端を通る光ほど強く曲がり、焦点が手前（1.10R）にずれる。像は上下左右が逆になる</text></svg>

- 高さ 0.05R: 入射角 2.87°、屈折角 1.91°、光軸との交点は中心から 1.499R
- 0.30R: 17.46°、11.54°、1.462R
- 0.50R: 30.00°、19.47°、1.392R
- 0.70R: 44.43°、27.82°、1.278R
- 0.90R: 64.16°、36.87°、1.104R

中心に近い光（光軸のすぐ近く）は薄いレンズの公式 `f = nR / (2(n − 1))` が与える 1.5R の焦点に集まります。端を通る光ほど強く曲がり焦点が手前にずれます（球面収差）。ガラス玉の像が中心でははっきりしていて、縁でゆがむのはこのためです。

この計算から分かることがもう 1 つあります。球を 1 回通るとき出口での入射角は、入口の屈折角と同じです。屈折角は必ず臨界角より小さいので、球の出口で全反射は起きません。全反射が起きるのは入口と出口の面の向きが対称でない形（凹んだ形、宝石のカット）です。宝石の輝きは内部での全反射の繰り返しで生まれます。

臨界角は物質から空気へ出るときの `asin(1/n)` です。水（1.33）で 48.75°、ガラス（1.5）で 41.81°、ダイヤモンド（2.42）で 24.41° です。ダイヤモンドは臨界角が小さいので、内部で光が何度も全反射して外へ出にくく、強く輝きます。

## 厚いガラスの 2 回屈折 {#thick}

### 近似の考え方 {#thick-idea}

画面空間で厚いガラスを近似するには次の手順を使います。

1. ガラスの背面を先に描き距離と法線を保存します。
2. 前面の画素で入口の屈折ベクトル `T1 = refract(V, N_front, 1/n)` を求めます。
3. 前面と背面の距離の差から厚みを求め出口の位置を `P_out ≈ P_front + T1 × 厚み` と推定します。
4. 出口での背面の法線 `N_back` で、2 回目の屈折 `T2 = refract(T1, −N_back, n)` を求めます。
5. `T2` の向きでシーンを読みます。

この手順は Wyman の画像空間の近似と同じ流れです。ただし、元の論文は読んでいないので細部は同じとは限りません。このページのコードは自分で書いたものです。

### 厚みの見積もりのずれ {#thick-error}

手順 3 の厚みは前面と背面の距離の差です。これは視線に沿った弦の長さで、屈折した光線に沿った実際の弦より短くなります。球で数えると次のとおりです（`n = 1.5`）。

- 高さ 0.0R: 視線の弦 2.000R、実際 2.000R、ずれ 0%
- 0.3R: 1.908R、1.960R、ずれ 2.6%
- 0.5R: 1.732R、1.886R、ずれ 8.1%
- 0.7R: 1.428R、1.769R、ずれ 19.3%
- 0.9R: 0.872R、1.600R、ずれ 45.5%

球の中心付近では問題になりませんが、端に近づくほど出口の位置の見積もりが手前にずれます。縁の歪みは近似の精度が悪い所に出ます。厚みに補正を掛ける方法もありますが、このページでは扱いません。

### コード {#thick-code}

```hlsl
// ---- 厚いガラス：背面のデータを使った 2 回屈折の近似 ----
// 背面の深度と法線を、前面と同じ画素から読む（足した近似: 凸な形で、背面が画素ごとに 1 枚と仮定）。
float3 ThickGlass(float3 world_pos, float3 n_front, float2 screen_uv, float front_dist, float3 env_color) {
  float3 v = normalize(world_pos - gCameraPos);               // カメラから表面へ向かう視線
  float3 t1 = refract(v, n_front, 1.0 / gIor);                // 入口の屈折（空気 → ガラス）
  float back_dist = gBackDepth.SampleLevel(gLinear, screen_uv, 0);   // 背面までの距離
  float thickness = max(back_dist - front_dist, 0.0);         // 視線に沿った厚み（屈折後の弦より短い）
  float3 p_out = world_pos + t1 * thickness;                  // 出口の点を推定
  float3 n_back = normalize(gBackNormal.SampleLevel(gLinear, screen_uv, 0).xyz);   // 背面の法線（外向き）
  float3 t2 = refract(t1, -n_back, gIor);                     // 出口の屈折（ガラス → 空気）。法線は内向きにする
  bool tir = dot(t2, t2) < 1e-5;                              // ゼロ ベクトルなら全反射
  if (tir) t2 = reflect(t1, -n_back);                         // 全反射したら反射させる（内部反射の 1 回分の近似）
  float3 sample_pos = p_out + t2 * 2.0;                       // 出口から 2 m 先（一例）を画面に投影して読む
  float3 refracted = gSceneCopy.SampleLevel(gLinear, ProjectToUv(sample_pos), 0).rgb;   // 向こうの景色
  float3 absorb = exp(-gAbsorb * thickness * (1.0 - gTint));  // 厚みで色がつく（Beer-Lambert の簡略形）
  float fr = Fresnel(dot(n_front, -v), gIor);                 // 表面の反射
  return lerp(refracted * absorb, env_color, fr);             // 屈折 + 厚みの色 + 反射
}
```

背面のデータを前面と同じ画素から読んでいます。足した近似で背面が画素ごとに 1 枚で、前面と背面が同じ画素に重なる凸な形を仮定しています。`refract` がゼロベクトルを返したときは全反射なので、`reflect` で代用します。球では起きませんが凸でない形では起きます。`exp(−gAbsorb × 厚み × (1 − gTint))` は厚いほど色がつく吸収です。`gTint` が白なら吸収はありません。

## 凹んだ形、複雑な形 {#concave}

背面を 1 層だけ使う近似は視線が入口と出口で 1 回ずつ通る凸な形が前提です。コップ、ドーナツ、複雑な彫像のように視線が複数回通る形ではうまくいきません。

- **凸（球、瓶、単純な宝石）。** 背面の法線を使う近似でよいです。
- **軽く凹む形。** 誤差を許容します。
- **強く凹む複雑な形。** レイトレーシングか事前に焼いたキューブマップを使います。
- **宝石。** 内部の複数回の反射が見た目の本質です。キューブマップに焼くか専用の方法を使います（[Dispersion](dispersion.md) と組み合わせます）。

## 実際のガラスは薄い壁の空洞 {#hollow}

ほとんどのゲームのガラス（コップ、瓶、窓）は薄い壁を持つ空洞です。

- **ガラスのコップ。** 薄い壁として扱います（小さなずらし + フレネル + 厚みによる色）。中の水は別に描きます。
- **ワインのボトル。** 壁は薄いですが中の液体が屈折を起こします。液体を別メッシュとして厚いガラスの近似で描きます。
- **魚の水槽。** 水が大きな塊なので水の体積として扱います（[Water](../../water/index.md)）。
- **氷の塊。** 厚く内部で散乱と屈折が起きます。厚みとぼかしで近似します（[Thickness and Color](thickness-color.md)）。

## よくあるミス {#mistakes}

??? failure "窓ガラスに強い屈折を付けて、景色が歪みすぎる"
    原因は薄い板を厚い塊のモデルで描いていることです。6 mm の窓ガラスのずれは 45° でも 2 mm 程度です。ずらし量を 0.002 程度のごく小さい値にします。

??? failure "ガラス玉の縁がぼやけて、にじむ"
    原因は厚みを前面と背面の深度の差で見積もったことによる出口の位置のずれです。高さ 0.9R では厚みが 45% 短くなります。縁だけ補正するか玉ならば解析的な球の式で解きます。

??? failure "凹んだ形の屈折が、ひび割れたように見える"
    原因は背面を 1 層しか持っていないことです。視線が複数回ガラスを通る形では背面の層が足りません。レイトレーシングかキューブマップに焼く方法に切り替えます。

??? failure "曇りガラスの段差が見える"
    原因はミップ間の補間で、ぼけの量が不連続に変わることです。3 線形（トライリニア）フィルタを使い粗さの変化をなめらかにします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 平行な板は向きが変わらず横にずれるだけ。横ずれ = `t sin(θ − φ) / cos φ`。6 mm の窓ガラスは 45° で 1.97 mm
    - [x] 窓は透過 + 反射。屈折は省く。曇りガラスは粗さのミップで読む
    - [x] 球は端ほど強く曲がる（1.5R の焦点が、端では 1.104R）。球の出口では全反射しない
    - [x] 厚みを深度の差で見積もると、高さ 0.7R で 19.3% 短い
    - [x] ダイヤモンドは垂直でも 17.2% 反射し、臨界角が 24.41° と小さいので内部で何度も全反射する

## C++ で数えたもの {#numbers}

```cpp
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

struct V2 { double x, y; };
double Dot(V2 a, V2 b) { return a.x * b.x + a.y * b.y; }

// 2 次元の屈折。d は進む向き（単位）、nrm は面の法線（単位。向きは問わない）、eta = n1 / n2。
// 全反射のときは k < 0 になるので、呼び出し側で避ける（この例では起きない）。
V2 Refract(V2 d, V2 nrm, double eta) {
  double c = Dot(d, nrm);                                           // d と法線の内積
  if (c > 0.0) { nrm = {-nrm.x, -nrm.y}; c = -c; }                  // 法線を d と反対向きにそろえる
  const double k = 1.0 - eta * eta * (1.0 - c * c);                  // 負なら全反射
  const double s = eta * c + std::sqrt(k);                           // 法線方向の成分
  return {eta * d.x - s * nrm.x, eta * d.y - s * nrm.y};
}

// 平行な板（厚さ t、屈折率 n）に角度 theta（法線から）で入った光の横ずれ。
// 屈折角 phi は sin(phi) = sin(theta) / n。ずれ = t * sin(theta - phi) / cos(phi)。
double PlateShift(double t, double n, double theta) {
  const double phi = std::asin(std::sin(theta) / n);        // 板の中での角度
  return t * std::sin(theta - phi) / std::cos(phi);         // 入口と出口で平行になった後の横ずれ
}

// シュリック近似の垂直反射率 F0 = ((n - 1) / (n + 1))^2。
double F0(double n) { return std::pow((n - 1.0) / (n + 1.0), 2.0); }

int main() {
  // 1. 板の横ずれ（mm）。窓ガラス 6 mm と、分厚い板 50 mm。n = 1.5。
  std::printf("-- lateral shift of a flat plate (n = 1.5)\n");
  for (double deg : {0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 85.0}) {
    const double th = deg / kDeg;
    std::printf("incidence %2.0f deg: 6 mm plate = %5.2f mm, 50 mm plate = %6.2f mm\n", deg, PlateShift(6.0, 1.5, th),
                PlateShift(50.0, 1.5, th));
  }

  // 2. 臨界角（全反射が起きる入射角）。物質から空気（n = 1）へ出るとき sin(c) = 1 / n。
  std::printf("-- critical angle to air\n");
  for (double nn : {1.33, 1.5, 2.42}) {
    std::printf("n = %.2f: critical = %5.2f deg, F0 = %.3f\n", nn, std::asin(1.0 / nn) * kDeg, F0(nn));
  }

  // 3. 球（半径 R = 1、n = 1.5）に光軸と平行な光を当てる。光軸から高さ b に入る光線を、
  //    屈折の式（ベクトル）で 2 回曲げて、光軸と交わる位置（球の中心から）を数える。
  std::printf("-- ray through a glass sphere (R = 1, n = 1.5)\n");
  const double n = 1.5;
  for (double b : {0.05, 0.3, 0.5, 0.7, 0.9}) {
    const V2 pin = {-std::sqrt(1.0 - b * b), b};                       // 入口の点。左側の表面
    const V2 d0 = {1.0, 0.0};                                          // 入射方向（+x）
    const V2 d1 = Refract(d0, pin, 1.0 / n);                           // 入口で曲がった向き（法線は中心から外向き）
    // 球の中を進んで、反対側の表面に当たる点を求める（球との交点のうち遠い方）。
    const double bq = Dot(pin, d1);
    const double tq = -bq + std::sqrt(bq * bq - (Dot(pin, pin) - 1.0));
    const V2 pout = {pin.x + d1.x * tq, pin.y + d1.y * tq};            // 出口の点
    const V2 d2 = Refract(d1, pout, n);                                // 出口で曲がった向き（空気側へ）
    const double xcross = pout.x - pout.y * d2.x / d2.y;               // y = 0 になる x
    std::printf("b = %.2f: theta_i = %5.2f, theta_r = %5.2f, crosses axis at x = %.3f R from the center\n", b,
                std::asin(b) * kDeg, std::asin(b / n) * kDeg, xcross);
  }
  std::printf("paraxial focal point from the center: n R / (2 (n - 1)) = %.3f R\n", n / (2.0 * (n - 1.0)));

  // 4. 厚みを「前面と背面の深度の差」で見積もる近似のずれ。
  //    視線に沿った弦の長さ = 2 R cos(theta_i)、屈折した光線に沿った実際の弦の長さ = 2 R cos(theta_r)。
  std::printf("-- chord length: along the view ray vs along the refracted ray (R = 1)\n");
  for (double b : {0.0, 0.3, 0.5, 0.7, 0.9}) {
    const double chord_view = 2.0 * std::cos(std::asin(b));            // 視線に沿った厚み
    const double chord_true = 2.0 * std::cos(std::asin(b / n));        // 屈折光線に沿った実際の厚み
    std::printf("b = %.1f: view chord = %.3f R, refracted chord = %.3f R, error = %.3f R (%.1f%%)\n", b, chord_view,
                chord_true, chord_true - chord_view, (chord_true - chord_view) / chord_true * 100.0);
  }
}
```

```text title="実行結果"
-- lateral shift of a flat plate (n = 1.5)
incidence  0 deg: 6 mm plate =  0.00 mm, 50 mm plate =   0.00 mm
incidence 15 deg: 6 mm plate =  0.54 mm, 50 mm plate =   4.48 mm
incidence 30 deg: 6 mm plate =  1.16 mm, 50 mm plate =   9.69 mm
incidence 45 deg: 6 mm plate =  1.97 mm, 50 mm plate =  16.46 mm
incidence 60 deg: 6 mm plate =  3.07 mm, 50 mm plate =  25.62 mm
incidence 75 deg: 6 mm plate =  4.49 mm, 50 mm plate =  37.40 mm
incidence 85 deg: 6 mm plate =  5.51 mm, 50 mm plate =  45.94 mm
-- critical angle to air
n = 1.33: critical = 48.75 deg, F0 = 0.020
n = 1.50: critical = 41.81 deg, F0 = 0.040
n = 2.42: critical = 24.41 deg, F0 = 0.172
-- ray through a glass sphere (R = 1, n = 1.5)
b = 0.05: theta_i =  2.87, theta_r =  1.91, crosses axis at x = 1.499 R from the center
b = 0.30: theta_i = 17.46, theta_r = 11.54, crosses axis at x = 1.462 R from the center
b = 0.50: theta_i = 30.00, theta_r = 19.47, crosses axis at x = 1.392 R from the center
b = 0.70: theta_i = 44.43, theta_r = 27.82, crosses axis at x = 1.278 R from the center
b = 0.90: theta_i = 64.16, theta_r = 36.87, crosses axis at x = 1.104 R from the center
paraxial focal point from the center: n R / (2 (n - 1)) = 1.500 R
-- chord length: along the view ray vs along the refracted ray (R = 1)
b = 0.0: view chord = 2.000 R, refracted chord = 2.000 R, error = 0.000 R (0.0%)
b = 0.3: view chord = 1.908 R, refracted chord = 1.960 R, error = 0.052 R (2.6%)
b = 0.5: view chord = 1.732 R, refracted chord = 1.886 R, error = 0.154 R (8.1%)
b = 0.7: view chord = 1.428 R, refracted chord = 1.769 R, error = 0.341 R (19.3%)
b = 0.9: view chord = 0.872 R, refracted chord = 1.600 R, error = 0.728 R (45.5%)
```

## 参考資料 {#references}

このページの式と数字はスネルの法則から導き C++ で確かめたものです。以下の資料は**今回は読んでいません**。

- Chris Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)
- Tiago Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Eugene Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、フレネルの式、分散）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）

薄いレンズの公式 `f = nR / (2(n − 1))` とダイヤモンドの屈折率 2.42 は、記憶に基づく値で上の資料では確かめていません。球の計算で近軸の焦点が 1.499R と 1.5R に一致することは、確かめました。

## 関連ページ {#related}

- [Refraction](index.md)
- [Thickness and Color](thickness-color.md)
- [Screen-Space Refraction](screen-space.md)
