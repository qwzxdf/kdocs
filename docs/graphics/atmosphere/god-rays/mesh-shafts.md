---
title: Light Shaft Meshes
tags:
  - 描画
---

# Light Shaft Meshes

教会のステンドグラスから差す光、洞窟の天井の穴から落ちる光、窓から部屋に伸びる光の帯。位置が決まっている光の筋は画面全体で光を散乱させる計算をしなくても、半透明のメッシュ（光の柱）を置くだけで描けます。計算は数枚の板を塗るだけで済むので、あらゆる光の筋の方法の中で最も軽く、見た目はアーティストが完全に決められます。弱点は太陽が動いても板は動かず人が窓の前に立っても影が出ないことです。このページでは窓から差す光が床に作る形を幾何から数えフェードの式を導き太陽の向きに合わせて枠を押し出す頂点シェーダーで弱点の 1 つを解消します。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`vs_5_0` / `ps_5_0`）に通しましたが、描画した結果は確かめていません。

!!! tip "ポイント"
    - 床に落ちる光の長さは `窓の高さ ÷ tan(太陽の高さ)` で決まります。窓の下端が 0.9 m、上端が 2.9 m なら太陽の高さ 30° で床の長さは 3.46 m、60° で 1.15 m です。
    - 加算ブレンドの板は重なった数だけ明るくなります。箱型の柱で前面と背面を両方描くと明るさが 2 倍になります。
    - 固定メッシュは太陽の方位が 1 時間に 15° 回るので、届く距離 3 m の柱が 20 分で 26 cm ずれます。窓の枠を太陽の向きに押し出す頂点シェーダーならこのずれがありません。
    - 板の縁と床や壁との交差線をフェードで消します。向きのフェードは板の法線と視線のなす角が 66.4° を超えると薄くなります。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と読む順番）
    - [Blend State](../../translucency/blending-sorting/blend-state.md)（加算ブレンドの設定）
    - [Soft Particles](../../translucency/blending-sorting/soft-particles.md)（深度の差で薄くする考え方）

## 光の柱の形を数える {#geometry}

### 窓から床までの幾何 {#floor}

窓の面に対して真正面の方位から、太陽が高さ `E` で来るとします。窓の下端の高さを `y0`、上端を `y1` とすると光は下端から `y0 / tan E`、上端から `y1 / tan E` の水平距離で床に着きます。床に落ちる光の長さはその差です。

```text
長さ = (y1 − y0) / tan E
```

窓の幅 1.2 m、下端 0.9 m、上端 2.9 m（高さ 2.0 m）で数えました。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="窓から差す光の幾何"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">窓から差す光の幾何</text><text x="330" y="22" text-anchor="middle" style="font-size:13px;font-weight:700">横から見た図：窓から差す光（太陽の高さ 30°）</text><line x1="40" y1="260" x2="640" y2="260" stroke="#94a3b8" stroke-width="3"/><text x="620" y="278" text-anchor="end" style="font-size:12px;font-weight:400">床</text><line x1="40" y1="227.6" x2="40" y2="155.60000000000002" stroke="#4c8bf5" stroke-width="6"/><text x="44" y="148.39999999999998" text-anchor="start" style="font-size:12px;font-weight:400">窓（高さ 0.9〜2.9 m）</text><polygon points="40,155.60000000000002 220.8,260 96.1,260 40,227.6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><line x1="96.1" y1="270" x2="220.8" y2="270" stroke="#e5484d" stroke-width="3"/><text x="158.47227523771122" y="290" text-anchor="middle" style="font-size:12px;font-weight:400">床の光 1.56〜5.02 m（長さ 3.46 m）</text><text x="90.11844616523163" y="210" text-anchor="end" style="font-size:12px;font-weight:400">光線に沿った長さ 5.80 m</text></svg>

- 太陽の高さ 15°: 床は窓から 3.36〜10.82 m、長さ 7.46 m、面積 8.96 m²
- 30°: 1.56〜5.02 m、長さ 3.46 m、面積 4.16 m²
- 45°: 0.90〜2.90 m、長さ 2.00 m、面積 2.40 m²
- 60°: 0.52〜1.67 m、長さ 1.15 m、面積 1.39 m²
- 75°: 0.24〜0.78 m、長さ 0.54 m、面積 0.64 m²

太陽が低いほど光は長く伸び面積が大きくなります。太陽の高さが 15° なら 10 m 以上伸びますが、75° なら窓のすぐ下にしか落ちません。窓の上端から床までの光線に沿った長さは、高さ 30° で 5.80 m、60° で 3.35 m です。柱のメッシュの長さはこの値で作ります。

### 明るさの確認 {#energy}

床の明るさが物理的に合っているかを確かめます。窓を通る光の量は光線に垂直な断面積 `幅 × 高さ × cos E` に太陽の強さを掛けたものです。これを床の面積 `幅 × 長さ` で割ると、床の照度になります。数えた結果は太陽の高さ 30° で 0.500、60° で 0.866 でどちらも `sin E` と一致しました。つまり、柱の中の光は太陽の高さが高いほど床で強くなります。メッシュの強さを固定にすると、この変化が出ないので必要なら `sin E` を掛けます。

## 柱のシェーダー {#shader}

### 太陽の向きに追従する頂点シェーダー {#vs}

メッシュを手で置くと太陽が動いたときに合わなくなります。それを避けるため窓の枠の頂点を頂点シェーダーで太陽の向きに押し出します。定数と出力の宣言です。

```hlsl
// ---- 窓から差す光の柱（左手系・Y 上。リニア空間）。太陽の向きに追従して、窓の枠を床まで押し出す ----

cbuffer ShaftCB : register(b0) {
  float4x4 gViewProj;      // ビュー × 射影（行ベクトル）
  float3 gSunDir;          // 太陽へ向かう単位ベクトル。y > 0（太陽が地平線の上）
  float  gFloorY;          // 光が着く床の高さ（m）
  float3 gSunColor;        // 太陽の色（リニア）
  float  gIntensity;       // 柱全体の強さ
  float3 gCameraPos;       // カメラ位置（ワールド）
  float  gTime;            // 秒（ほこりの流れに使う）
  float  gNearStart;       // カメラからこの距離（m）以内で消え始める
  float  gNearRange;       // そこから何 m かけて見えるようになるか
  float  gDepthFade;       // 床や壁との交差を薄くする距離（m）
  float  gNearPlane;       // カメラの near（m）。深度の復元に使う
  float  gFarPlane;        // カメラの far（m）
  float3 gPad;             // 詰め物
};

Texture2D<float>  gSceneDepth : register(t0);   // 不透明物の深度（D32_FLOAT の読み取り、標準 Z）
Texture2D<float>  gDust       : register(t1);   // ほこりのノイズ（R のみ）
SamplerState gLinearWrap : register(s0);        // 線形・ラップ

struct ShaftVSOut {
  float4 pos   : SV_Position;   // クリップ空間の位置
  float2 uv    : TEXCOORD0;     // x: 幅方向 0〜1、y: 窓 0 → 床 1
  float3 world : TEXCOORD1;     // ワールド位置
  float  eye_z : TEXCOORD2;     // 視点空間の距離（m）
};
```

`gSunDir` は太陽へ向かう単位ベクトルなので、光は逆向き（`−gSunDir`）に進みます。窓の角から床までの長さ `t` は `(角の高さ − 床の高さ) / gSunDir.y` です。

```hlsl
// 窓の枠の頂点を、太陽の光の向きに押し出す。corner は窓の角の位置（ワールド）、end は 0（窓）か 1（床）。
// 光は -gSunDir の向きに進む。窓の角を通る光が床（y = gFloorY）に着くまでの長さ t を、平面との交点で求める。
ShaftVSOut ShaftVS(float3 corner : POSITION, float2 uv : TEXCOORD0) {
  ShaftVSOut o;                                            // 出力
  float t = max((corner.y - gFloorY) / max(gSunDir.y, 0.05), 0.0);   // 光線に沿った長さ（足した: 太陽が低すぎる所で打ち切る）
  float3 p = corner - gSunDir * (t * uv.y);                // uv.y = 0 で窓、1 で床
  float4 clip = mul(float4(p, 1.0), gViewProj);            // 行ベクトルの掛け順
  o.pos = clip;
  o.uv = uv;
  o.world = p;
  o.eye_z = clip.w;                                        // 射影の w が視点空間の z（左手系）
  return o;
}
```

`uv.y` が 0 の頂点は窓の位置に 1 の頂点は床に着く位置に動きます。`max(gSunDir.y, 0.05)` は足した処理で太陽が地平線に近いと `t` が無限大になるのを避けて打ち切ります。時刻に合わせて `gSunDir` を更新すれば、柱は自動で向きを変えます。固定メッシュの弱点だった「太陽が動くと合わない」は、この方法で解けます。

動かない固定メッシュではずれは次のとおりです。太陽の方位は 1 時間に 15° 回るので、窓から届く距離 `D` の先端は `D × tan(回った角度)` ずれます。

<svg class="fig flow" viewBox="0 0 700 300" role="img" aria-label="固定メッシュのずれ"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">固定メッシュのずれ</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,250.0 86.7,248.5 103.3,247.1 120.0,245.6 136.7,244.1 153.3,242.7 170.0,241.2 186.7,239.7 203.3,238.3 220.0,236.8 236.7,235.3 253.3,233.9 270.0,232.4 286.7,230.9 303.3,229.4 320.0,227.9 336.7,226.4 353.3,224.9 370.0,223.4 386.7,221.9 403.3,220.4 420.0,218.9 436.7,217.4 453.3,215.9 470.0,214.4 486.7,212.8 503.3,211.3 520.0,209.8 536.7,208.2 553.3,206.6 570.0,205.1"/><text x="574" y="209.07910597478235" text-anchor="start" style="font-size:11px;font-weight:700">届く距離 1.5 m</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 86.7,247.1 103.3,244.1 120.0,241.2 136.7,238.3 153.3,235.4 170.0,232.4 186.7,229.5 203.3,226.6 220.0,223.6 236.7,220.7 253.3,217.7 270.0,214.8 286.7,211.8 303.3,208.8 320.0,205.9 336.7,202.9 353.3,199.9 370.0,196.9 386.7,193.9 403.3,190.9 420.0,187.9 436.7,184.8 453.3,181.8 470.0,178.7 486.7,175.7 503.3,172.6 520.0,169.5 536.7,166.4 553.3,163.3 570.0,160.2"/><text x="574" y="164.15821194956473" text-anchor="start" style="font-size:11px;font-weight:700">届く距離 3.0 m</text><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,250.0 86.7,244.1 103.3,238.3 120.0,232.4 136.7,226.6 153.3,220.7 170.0,214.9 186.7,209.0 203.3,203.1 220.0,197.2 236.7,191.3 253.3,185.4 270.0,179.5 286.7,173.6 303.3,167.7 320.0,161.7 336.7,155.8 353.3,149.8 370.0,143.8 386.7,137.8 403.3,131.8 420.0,125.7 436.7,119.7 453.3,113.6 470.0,107.5 486.7,101.3 503.3,95.2 520.0,89.0 536.7,82.8 553.3,76.6 570.0,70.3"/><text x="574" y="74.31642389912946" text-anchor="start" style="font-size:11px;font-weight:700">届く距離 6.0 m</text><line x1="70" y1="227.64705882352942" x2="570" y2="227.64705882352942" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="74" y="221.64705882352942" text-anchor="start" style="font-size:11px;font-weight:400">20 cm</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">15</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">45</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="198.11764705882354" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="142.23529411764707" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="62" y="86.35294117647058" text-anchor="end" style="font-size:11px;font-weight:400">1.5</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">経過時間（分）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">固定メッシュの先端のずれ（m、方位 15°/時）</text></svg>

- 届く距離 1.5 m: 10 分で 0.07 m、30 分で 0.20 m、60 分で 0.40 m
- 3.0 m: 0.13 m、0.39 m、0.80 m
- 6.0 m: 0.26 m、0.79 m、1.61 m

届く距離が 3 m なら 20 分で 26 cm です。気づかれ始める量なので昼夜サイクルのあるゲームは、柱を太陽に追従させます。

### ピクセルシェーダー {#ps}

深度を復元する関数です。

```hlsl
// 標準 Z の深度 d を、視点空間の距離（m）に戻す。
float LinearDepth(float d) {
  return gNearPlane * gFarPlane / (gFarPlane - d * (gFarPlane - gNearPlane));
}
```

標準の深度（near で 0、far で 1）を視点空間の距離（m）に戻します。リバース Z の場合は式が違います（[Application Mistakes](../../ao/artifacts/application-mistakes.md)）。

次が本体です。6 つの係数を掛け合わせます。

```hlsl
// 加算ブレンド用。ブレンドは One + One（色は事前に強さを掛けておく）。
float4 ShaftPS(ShaftVSOut i, float3 face_normal : TEXCOORD3) : SV_Target {
  // ① 幅方向の縁。中心で 1、端で 0。端をなめらかにして、板の輪郭を消す。
  float across = 1.0 - abs(i.uv.x * 2.0 - 1.0);
  across = smoothstep(0.0, 0.5, across);

  // ② 長さ方向の減衰。窓 1、床 0。拡散して弱まる様子。
  float along = 1.0 - i.uv.y;

  // ③ 視線との向き。板を真横から見る（縁が見える）と薄く。facing = |n·v|。
  float3 v = normalize(gCameraPos - i.world);              // 表面からカメラへ
  float facing = abs(dot(normalize(face_normal), v));
  float edge = smoothstep(0.0, 0.4, facing);               // 66° までは 1、90° で 0

  // ④ 深度フェード。床や壁と交わる所を薄くして、硬い線を消す。単位は m にそろえる。
  float2 uv_screen = i.pos.xy / float2(1280.0, 720.0);     // 例: 1280x720 の画面（実際は定数バッファから渡す）
  float scene_z = LinearDepth(gSceneDepth.SampleLevel(gLinearWrap, uv_screen, 0));   // 不透明物までの距離
  float depth_fade = saturate((scene_z - i.eye_z) / gDepthFade);

  // ⑤ カメラに近いとき消す。近いほど板だと分かるため。
  float near_fade = saturate((i.eye_z - gNearStart) / gNearRange);

  // ⑥ ほこりの揺らぎ。縦長にずらして、時間で流す。
  float dust = gDust.Sample(gLinearWrap, i.uv * float2(4.0, 1.0) + float2(gTime * 0.02, 0.0)).r;

  float alpha = across * along * edge * depth_fade * near_fade * (0.7 + 0.3 * dust) * gIntensity;
  return float4(gSunColor * alpha, 0.0);                   // 加算ブレンド。a は使わない
}
```

1. **幅方向の縁。** 柱の中心を 1、端を 0 にします。端をなめらかにして板の輪郭を消します。
2. **長さ方向の減衰。** 窓で 1、床で 0 です。光が拡散して弱まる様子を出します。
3. **視線との向き。** 板の法線と視線の内積の絶対値 `facing` を使います。`smoothstep(0, 0.4, facing)` なので角度が 66.4° までは 1 で、72° で 0.868、80° で 0.402、90° で 0 です。板を真横から見ると薄くなり縁が見えません。
4. **深度フェード。** 床や壁との交差の線を薄くします。`fade_distance` が 0.5 m なら深度の差が 0.1 m で 0.20、0.25 m で 0.50、0.5 m 以上で 1.00 です。
5. **カメラに近いとき消す。** 近づくほど板だと分かるからです。
6. **ほこりの揺らぎ。** ノイズを時間で流し `0.7 + 0.3 × ほこり` で濃さを揺らします。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="向きのフェード"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">向きのフェード</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,60.0 81.1,60.0 92.2,60.0 103.3,60.0 114.4,60.0 125.6,60.0 136.7,60.0 147.8,60.0 158.9,60.0 170.0,60.0 181.1,60.0 192.2,60.0 203.3,60.0 214.4,60.0 225.6,60.0 236.7,60.0 247.8,60.0 258.9,60.0 270.0,60.0 281.1,60.0 292.2,60.0 303.3,60.0 314.4,60.0 325.6,60.0 336.7,60.0 347.8,60.0 358.9,60.0 370.0,60.0 381.1,60.0 392.2,60.0 403.3,60.0 414.4,60.0 425.6,60.0 436.7,60.0 447.8,62.2 458.9,70.8 470.0,85.0 481.1,103.7 492.2,125.6 503.3,149.4 514.4,173.7 525.6,197.0 536.7,217.9 547.8,234.7 558.9,245.9 570.0,250.0"/><text x="345.0" y="88.5" text-anchor="start" style="font-size:12px;font-weight:700">facing のフェード</text><circle cx="470.0" cy="85.1" r="4" fill="#4c8bf5"/><text x="478.0" y="79.08000000000001" text-anchor="start" style="font-size:11px;font-weight:700">0.868</text><circle cx="514.4" cy="173.6" r="4" fill="#4c8bf5"/><text x="522.4444444444445" y="167.62" text-anchor="start" style="font-size:11px;font-weight:700">0.402</text><line x1="438.9" y1="250" x2="438.9" y2="60" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="434.8888888888889" y="74" text-anchor="end" style="font-size:11px;font-weight:400">66.4°</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="236.66666666666666" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="403.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><text x="62" y="254" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="159.0" text-anchor="end" style="font-size:11px;font-weight:400">0.5</text><text x="62" y="64" text-anchor="end" style="font-size:11px;font-weight:400">1</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">板の法線と視線のなす角（0° = 正面、90° = 真横）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">フェードの係数</text></svg>

最後は `float4(色 × alpha, 0)` を返して加算ブレンド（`One + One`）で足します。色はあらかじめ強さを掛けておきます。

## 加算ブレンドの落とし穴 {#additive}

加算ブレンドは描く順番に依存しないので、ソートが要らないのが利点です。一方、重なった数だけ明るくなります。1 面の寄与を 0.3 とすると、2 面で 0.60、3 面で 0.90、4 面で 1.20、6 面で 1.80 です。

箱型の柱で前面と背面の両方を描くと明るさが 2 倍になります。どちらか一方（背面だけまたはカリングで片面）だけを描くようにして、強さを `gIntensity` で調整します。また、複数の窓の柱が重なる所は足し算で白く飽和します。HDR のレンダーターゲットなら後段のトーンマッピングで丸められるので、極端には崩れません。

## 作り方のコツ {#tips}

- **形。** 窓の形をそのまま太陽の方向に押し出した錐台が基本です。太陽は平行光なので窓と同じ大きさの柱になるはずですが、少し先広がりにすると光の拡散が出ます。
- **ビルボード。** 柱を何枚かの平面で作る場合はカメラに向けて回すとどの角度から見ても板に見えません。ただし、枠の押し出し方式（前節）と併用はしません。
- **ほこり。** ノイズ テクスチャをゆっくり流します。速度の違う 2 枚を重ねると、より自然になります。
- **柱の中心を明るく縁を暗く。** 縁のフェードと長さ方向の減衰を合わせます。

## 長所と短所、使いどころ {#pros-cons}

長所は 3 つあります。計算が軽くモバイルでも使えます。アーティストが形、色、動きを完全に決められます。カメラや太陽の位置に依存せず常に同じ形で見えます（枠を押し出せば、太陽には追従します）。

短所は 3 つあります。動く物が光を遮っても筋が変わりません。近くで見ると板だと分かります。配置が手作業でレベルデザイナーが置くことになります。

固定の演出（教会の窓、洞窟の穴）に向きます。動く太陽で屋外全体を覆うには不向きです（[Volume-Based God Rays](volume.md) など）。

## よくあるミス {#mistakes}

??? failure "柱の縁が硬く、板に見える"
    原因は板の端の濃さが 0 になっていないことです。幅方向に `smoothstep` で縁を落とし真横から見たときも向きのフェードで薄くします。

??? failure "箱型の柱が、思った倍の明るさになる"
    原因は前面と背面の両方が加算されていることです。片面だけ描くようにカリングを設定します。

??? failure "床や壁の交差に光る線が出る"
    原因は板が床や壁に突き刺さる所で、アルファが切れずに残ることです。深度フェードを入れます。フェード距離は 0.5 m 程度から調整します。

??? failure "太陽が動くと光の柱が窓と合わなくなる"
    原因は柱のメッシュが固定されていることです。窓の枠を頂点シェーダーで太陽の向きに押し出します。

??? failure "リバース Z の環境で深度フェードが効かない"
    原因は標準の深度の式で復元していることです。リバース Z では `1 − d` にそろえてから復元します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 床の光の長さは `窓の高さ ÷ tan E`。30° で 3.46 m、60° で 1.15 m
    - [x] 窓の枠を `−gSunDir` の向きに床まで押し出せば、柱が太陽に追従する
    - [x] 加算ブレンドは重なった数だけ明るい。箱型は片面だけ描く
    - [x] 向き・深度・カメラ近傍の 3 つのフェードで、板の縁と交差線を消す
    - [x] 固定メッシュは届く距離 3 m で 20 分に 26 cm ずれる

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>

const double kPi = std::numbers::pi;       // 円周率
const double kDeg = 180.0 / kPi;           // ラジアン -> 度

double Smoothstep(double a, double b, double x) {            // HLSL の smoothstep と同じ
  const double t = std::clamp((x - a) / (b - a), 0.0, 1.0);
  return t * t * (3.0 - 2.0 * t);
}

int main() {
  // 1. 窓から差す光が床に作る範囲。窓は幅 1.2 m、下端の高さ 0.9 m、上端 2.9 m（高さ 2.0 m）。
  //    太陽は窓の面の真正面の方位から、高さ（仰角）E で来るとする。
  std::printf("-- window beam footprint on the floor (window 1.2 m wide, sill 0.9 m, top 2.9 m)\n");
  const double w = 1.2, y0 = 0.9, y1 = 2.9;
  for (double e_deg : {15.0, 30.0, 45.0, 60.0, 75.0}) {
    const double e = e_deg / kDeg;
    const double d0 = y0 / std::tan(e);                       // 下端の光が床に着く、窓からの水平距離
    const double d1 = y1 / std::tan(e);                       // 上端の光が床に着く距離
    const double len = d1 - d0;                               // 床の光の長さ
    const double area = w * len;                              // 床の面積
    const double beam_len = y1 / std::sin(e);   // 上端から床までの、光線に沿った長さ
    // エネルギーの確認: 窓を通る光の量 = 窓の面積 * cos(E)（光に垂直な断面）、床の照度 = その量 / 床の面積。
    const double flux = w * (y1 - y0) * std::cos(e);          // 光線に垂直な断面積 * 太陽の強さ 1
    const double irradiance = flux / area;                    // 床の照度（太陽の強さを 1 として）
    std::printf("E=%2.0f deg: floor from %5.2f to %5.2f m (length %5.2f m, area %5.2f m2), beam length from top %5.2f m, floor irradiance = %.3f (sin E = %.3f)\n",
                e_deg, d0, d1, len, area, beam_len, irradiance, std::sin(e));
  }

  // 2. 加算ブレンドで重ねたときの明るさ。1 枚の寄与を a とする。
  //    箱型の柱は前面と背面の 2 枚が描かれるので 2a。カリングで背面だけにすれば a。
  std::printf("-- additive overdraw (contribution a = 0.3 per surface)\n");
  for (int layers : {1, 2, 3, 4, 6}) {
    std::printf("%d surfaces: sum = %.2f\n", layers, 0.3 * layers);
  }

  // 3. 太陽が動いたとき、メッシュの先端が本来の位置からずれる量。
  //    太陽の方位は 1 時間に 15 度回る。窓から床までの水平距離が D のとき、先端は D * tan(15 度 * h) ずれる。
  std::printf("-- tip displacement of a fixed mesh as the sun moves (azimuth 15 deg/hour)\n");
  for (double d : {1.5, 3.0, 6.0}) {
    std::printf("shaft reach %.1f m:", d);
    for (double minutes : {10.0, 20.0, 30.0, 60.0}) {
      const double ang = 15.0 * minutes / 60.0 / kDeg;       // 回った角度
      std::printf("  %3.0f min: %.2f m", minutes, d * std::tan(ang));
    }
    std::printf("\n");
  }

  // 4. 視線との向きによるフェード: facing = |n.v| = cos(theta)、alpha = smoothstep(0, 0.4, facing)。
  std::printf("-- facing fade: angle between plane normal and view\n");
  for (double deg : {0.0, 30.0, 50.0, 60.0, 66.0, 72.0, 80.0, 90.0}) {
    const double facing = std::cos(deg / kDeg);
    std::printf("theta=%2.0f deg: facing = %.3f, fade = %.3f\n", deg, facing, Smoothstep(0.0, 0.4, facing));
  }
  std::printf("fade reaches 1.0 at theta = %.1f deg (facing = 0.4)\n", std::acos(0.4) * kDeg);

  // 5. 深度フェード: depth_fade = saturate((scene - pixel) / fade_distance)。fade_distance = 0.5 m。
  std::printf("-- depth fade (fade distance 0.5 m)\n");
  for (double gap : {0.0, 0.1, 0.25, 0.5, 1.0}) {
    std::printf("gap %.2f m: fade = %.2f\n", gap, std::clamp(gap / 0.5, 0.0, 1.0));
  }
}
```

```text title="実行結果"
-- window beam footprint on the floor (window 1.2 m wide, sill 0.9 m, top 2.9 m)
E=15 deg: floor from  3.36 to 10.82 m (length  7.46 m, area  8.96 m2), beam length from top 11.20 m, floor irradiance = 0.259 (sin E = 0.259)
E=30 deg: floor from  1.56 to  5.02 m (length  3.46 m, area  4.16 m2), beam length from top  5.80 m, floor irradiance = 0.500 (sin E = 0.500)
E=45 deg: floor from  0.90 to  2.90 m (length  2.00 m, area  2.40 m2), beam length from top  4.10 m, floor irradiance = 0.707 (sin E = 0.707)
E=60 deg: floor from  0.52 to  1.67 m (length  1.15 m, area  1.39 m2), beam length from top  3.35 m, floor irradiance = 0.866 (sin E = 0.866)
E=75 deg: floor from  0.24 to  0.78 m (length  0.54 m, area  0.64 m2), beam length from top  3.00 m, floor irradiance = 0.966 (sin E = 0.966)
-- additive overdraw (contribution a = 0.3 per surface)
1 surfaces: sum = 0.30
2 surfaces: sum = 0.60
3 surfaces: sum = 0.90
4 surfaces: sum = 1.20
6 surfaces: sum = 1.80
-- tip displacement of a fixed mesh as the sun moves (azimuth 15 deg/hour)
shaft reach 1.5 m:   10 min: 0.07 m   20 min: 0.13 m   30 min: 0.20 m   60 min: 0.40 m
shaft reach 3.0 m:   10 min: 0.13 m   20 min: 0.26 m   30 min: 0.39 m   60 min: 0.80 m
shaft reach 6.0 m:   10 min: 0.26 m   20 min: 0.52 m   30 min: 0.79 m   60 min: 1.61 m
-- facing fade: angle between plane normal and view
theta= 0 deg: facing = 1.000, fade = 1.000
theta=30 deg: facing = 0.866, fade = 1.000
theta=50 deg: facing = 0.643, fade = 1.000
theta=60 deg: facing = 0.500, fade = 1.000
theta=66 deg: facing = 0.407, fade = 1.000
theta=72 deg: facing = 0.309, fade = 0.868
theta=80 deg: facing = 0.174, fade = 0.402
theta=90 deg: facing = 0.000, fade = 0.000
fade reaches 1.0 at theta = 66.4 deg (facing = 0.4)
-- depth fade (fade distance 0.5 m)
gap 0.00 m: fade = 0.00
gap 0.10 m: fade = 0.20
gap 0.25 m: fade = 0.50
gap 0.50 m: fade = 1.00
gap 1.00 m: fade = 1.00
```

## 参考資料 {#references}

このページの式と数字は幾何から導き C++ で確かめたものです。以下の資料は**今回は読んでいません**。

- Kenny Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる光の筋。このページの対象ではなく比較のために挙げる）
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（加算ブレンド）

## 関連ページ {#related}

- [God Rays](index.md)
- [Blend State](../../translucency/blending-sorting/blend-state.md)
- [Soft Particles](../../translucency/blending-sorting/soft-particles.md)
