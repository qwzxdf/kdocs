---
title: Vegetation Lighting
tags:
  - 描画
---

# Vegetation Lighting

草や葉を地面や壁と同じ式で照らすとがっかりした絵になります。草原が砂粒のようにごちゃごちゃして見える太陽を背にした葉が真っ黒になる根元まで一様に明るくて地面から浮いて見える、といった症状です。原因は草が「薄い帯」であることです。法線が 1 本ごとにばらばらで、光は裏から表へ抜け根元は周りの草に挟まれています。このページでは法線を地形に寄せる効果、透過光、根元の暗さ影、スペキュラー、霧を数字で確かめながら 1 つのシェーダーにまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。HLSL は `fxc`（`ps_5_0`）に通しましたが、描画した結果は確かめていません。透過光の式は後で触れる GDC 2011 の発表の考え方を簡略にしたものと理解していますが、発表は今回読んでいません。

!!! tip "ポイント"
    - 草の法線を地形の法線へ寄せると、明るさのばらつきが小さくなります。法線を 3 割だけ残すと標準偏差は 0.279 から 0.087 に下がります。
    - 透過光はカメラが太陽の真反対にいるときに最大で、45° ずれると 4 分の 1 ほどに減ります。
    - 根元の AO は高さ `t` の関数で近似します。`t = 0` で 0.3、`t = 0.67` で 1.0 です。
    - 草は影を受けるだけにします。100 万本が影を落とすとカスケード 1 枚あたり 500 万三角形が増えます。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と読む順番）
    - [Grass Shape](grass-shape.md)（根元の色と帯の形）

## なぜ草のライティングは難しいか {#why}

草 1 本は薄い帯です。この帯に地面と同じライティングを行うと次の問題が出ます。

- **ごちゃごちゃして見える。** 帯 1 本ずつの法線がばらばらで、隣り合う草の明るさがまちまちになります。
- **逆光で真っ黒になる。** 帯の表が光源と反対を向いていると、`n·l` が 0 になります。実際の葉は光を通します。
- **影が重い。** 草 1 本ずつに影を落とさせると、数百万本の影が要ります。
- **草と地面が別物に見える。** 根元の色と明るさが地面とずれると、草が浮きます。

## ① 法線を地形に寄せる {#normal}

草原を 1 枚の面のように照らすときれいに見えます。そのために、草の法線を地形の法線へ寄せます。

### どれだけ効くか {#normal-effect}

草の 1 本ごとの法線を真上から 0〜60° の傾きランダムな方位とします（一例）。太陽の高さを 45° として、`n·l` のばらつきを 10 万本で数えました。寄せ方は `n = normalize(lerp(地形の法線, 草の法線, w))` で `w` は草の法線を残す割合です。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="法線の寄せ方とばらつき"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">法線の寄せ方とばらつき</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,250.0 120.0,232.3 220.0,194.9 370.0,136.0 570.0,73.3"/><circle cx="70.0" cy="250.0" r="4" fill="#4c8bf5"/><text x="78.0" y="242.0" text-anchor="start" style="font-size:11px;font-weight:700">0.000</text><circle cx="120.0" cy="232.3" r="4" fill="#4c8bf5"/><text x="128.0" y="224.26666666666665" text-anchor="start" style="font-size:11px;font-weight:700">0.028</text><circle cx="220.0" cy="194.9" r="4" fill="#4c8bf5"/><text x="228.0" y="186.9" text-anchor="start" style="font-size:11px;font-weight:700">0.087</text><circle cx="370.0" cy="136.0" r="4" fill="#4c8bf5"/><text x="378.0" y="128.0" text-anchor="start" style="font-size:11px;font-weight:700">0.180</text><circle cx="570.0" cy="73.3" r="4" fill="#4c8bf5"/><text x="578.0" y="65.29999999999998" text-anchor="start" style="font-size:11px;font-weight:700">0.279</text><text x="70" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0</text><text x="195.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.25</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.5</text><text x="445.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0.75</text><text x="570" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">1</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="190.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">0.1</text><text x="62" y="127.33333333333333" text-anchor="end" style="font-size:11px;font-weight:400">0.2</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">0.3</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">草の法線の残し方 w（0 = 地形の法線、1 = そのまま）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">明るさ n·l の標準偏差（草の傾き 0〜60°）</text></svg>

- `w = 1.0`（寄せない）: 平均 0.588、標準偏差 0.279
- `w = 0.6`: 平均 0.662、標準偏差 0.180
- `w = 0.3`: 平均 0.696、標準偏差 0.087
- `w = 0.1`: 平均 0.706、標準偏差 0.028
- `w = 0.0`（完全に寄せる）: 平均 0.707、標準偏差 0

寄せるほどばらつきが減り平均が地形の `n·l`（太陽の高さ 45° で 0.707）に近づきます。`w = 0.3` で標準偏差は寄せないときの約 3 分の 1 です。`w = 0` まで寄せると草原は完全に一様で、平板に見えます。見た目で `w = 0.2〜0.4` の範囲から選びます。

地形の法線に寄せれば斜面は暗く日向は明るいという地形の起伏が草にも出ます。真上に寄せれば草は常に上から照らされた様子になり地形の陰影は無視されます。どちらにするかは絵の方向性で決めます。

### コード {#normal-code}

最初に定数バッファです。

```hlsl
// ---- 草・葉のライティング（左手系・Y 上。リニア空間）----

cbuffer FoliageCB : register(b0) {
  float3 gSunDir;          // 光へ向かう単位ベクトル（ワールド）
  float  gNormalBlend;     // 草の法線を何割残すか 0〜1。0 で地形の法線そのもの。例: 0.3
  float3 gSunColor;        // 太陽の色 × 強さ（リニア）
  float  gTransDistort;    // 透過光で法線が光を曲げる量。例: 0.3
  float3 gSkyAmbient;      // 空の環境光（リニア）
  float  gTransPower;      // 透過光の山の鋭さ（指数）。例: 4
  float3 gGroundAmbient;   // 地面の照り返し（リニア）
  float  gRootAo;          // 根元の AO の最小値。例: 0.3
  float3 gCameraPos;       // カメラ位置（ワールド）
  float  gSpecFadeNear;    // スペキュラーを消し始める距離（m）。例: 20
  float3 gFogColor;        // 霧の色（リニア）
  float  gSpecFadeFar;     // スペキュラーが 0 になる距離（m）。例: 60
  float  gFogDensity;      // 指数霧の密度（1/m）。地形と同じ値を使う
  float3 gPad;             // 詰め物
};
```

続いて法線の寄せ方です。

```hlsl
// 草の法線を、地形の法線へ寄せる。height_t は根元 0、先端 1。
float3 GrassNormal(float3 blade_n, float3 terrain_n, float height_t) {
  float w = gNormalBlend * height_t;                  // 先端ほど帯の法線を残す（根元は地形そのもの）
  return normalize(lerp(terrain_n, blade_n, w));      // 寄せた法線
}
```

`height_t` は根元で 0、先端で 1 です。根元は地形の法線そのもので先端に向かって、帯の法線を `gNormalBlend` まで残します。根元を地形に合わせると草と地面の境目が目立たなくなります。

## ② 透過光 {#translucency}

葉は薄いので裏から当たった光の一部が透けて、表に出ます。太陽を背にして草を見ると明るく透けて見えるのは、このためです。

### 式 {#trans-formula}

簡単な近似は光の向きを法線で曲げ曲げた向きとカメラの向きの内積から求めるものです。

```text
h = normalize(l + n × distortion)
t = saturate(dot(v, −h))^p
透過光 = albedo × 光の色 × t × (1 − thickness)
```

`v` は葉からカメラへ向かう単位ベクトルです。`−h` は光が葉を抜けて進む向きなので、カメラがその先にいるほど（`v` と `−h` が同じ向きなほど）`t` が大きくなります。`distortion` は法線で光を曲げる量で葉の中の屈折と散乱の近似です。`p` は山の鋭さで大きいほど太陽の真反対だけが光ります。`thickness` は葉の厚さ（0 が薄い）で、テクスチャで与えます。

### 山の形 {#trans-lobe}

法線を真上、光を水平から 30°の高さとして、カメラを太陽の真反対（水平）から水平面で回したときの `t`（`p = 4`）を数えると、次のとおりです。

<svg class="fig flow" viewBox="0 0 660 300" role="img" aria-label="透過光の山"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">透過光の山</text><line x1="70" y1="250" x2="570" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="250" x2="70" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="70.0,71.9 81.1,72.3 92.2,73.6 103.3,75.7 114.4,78.7 125.6,82.5 136.7,86.9 147.8,92.1 158.9,97.9 170.0,104.3 181.1,111.1 192.2,118.4 203.3,125.9 214.4,133.8 225.6,141.7 236.7,149.8 247.8,157.9 258.9,165.9 270.0,173.7 281.1,181.3 292.2,188.7 303.3,195.7 314.4,202.3 325.6,208.5 336.7,214.3 347.8,219.6 358.9,224.4 370.0,228.7 381.1,232.6 392.2,236.0 403.3,238.9 414.4,241.3 425.6,243.4 436.7,245.1 447.8,246.5 458.9,247.6 470.0,248.4 481.1,249.0 492.2,249.4 503.3,249.7 514.4,249.8 525.6,249.9 536.7,250.0 547.8,250.0 558.9,250.0 570.0,250.0"/><text x="180.0" y="163.69456795386088" text-anchor="start" style="font-size:12px;font-weight:700">歪み 0.0</text><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="70.0,157.8 81.1,158.0 92.2,158.7 103.3,159.8 114.4,161.3 125.6,163.3 136.7,165.6 147.8,168.3 158.9,171.3 170.0,174.6 181.1,178.1 192.2,181.9 203.3,185.8 214.4,189.8 225.6,194.0 236.7,198.1 247.8,202.3 258.9,206.4 270.0,210.5 281.1,214.5 292.2,218.3 303.3,221.9 314.4,225.3 325.6,228.5 336.7,231.5 347.8,234.3 358.9,236.8 370.0,239.0 381.1,241.0 392.2,242.7 403.3,244.2 414.4,245.5 425.6,246.6 436.7,247.5 447.8,248.2 458.9,248.7 470.0,249.2 481.1,249.5 492.2,249.7 503.3,249.8 514.4,249.9 525.6,250.0 536.7,250.0 547.8,250.0 558.9,250.0 570.0,250.0"/><text x="180.0" y="200.50647893683606" text-anchor="start" style="font-size:12px;font-weight:700">歪み 0.3</text><polyline fill="none" stroke="#2e9e5b" stroke-width="2.5" points="70.0,203.6 81.1,203.7 92.2,204.1 103.3,204.6 114.4,205.4 125.6,206.4 136.7,207.6 147.8,208.9 158.9,210.4 170.0,212.1 181.1,213.8 192.2,215.7 203.3,217.7 214.4,219.7 225.6,221.8 236.7,223.9 247.8,226.0 258.9,228.1 270.0,230.1 281.1,232.1 292.2,234.0 303.3,235.9 314.4,237.6 325.6,239.2 336.7,240.7 347.8,242.1 358.9,243.3 370.0,244.5 381.1,245.5 392.2,246.3 403.3,247.1 414.4,247.7 425.6,248.3 436.7,248.7 447.8,249.1 458.9,249.4 470.0,249.6 481.1,249.7 492.2,249.8 503.3,249.9 514.4,250.0 525.6,250.0 536.7,250.0 547.8,250.0 558.9,250.0 570.0,250.0"/><text x="180.0" y="220.13706995883507" text-anchor="start" style="font-size:12px;font-weight:700">歪み 0.6</text><text x="70.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">0°</text><text x="236.66666666666666" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">30°</text><text x="403.3333333333333" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">60°</text><text x="570.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">90°</text><text x="62" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="62" y="190.66666666666666" text-anchor="end" style="font-size:11px;font-weight:400">0.2</text><text x="62" y="127.33333333333333" text-anchor="end" style="font-size:11px;font-weight:400">0.4</text><text x="62" y="64.0" text-anchor="end" style="font-size:11px;font-weight:400">0.6</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">カメラの向きが、太陽の真反対からずれた角度（水平面）</text><text x="74" y="52" text-anchor="start" style="font-size:12px;font-weight:400">透過光の強さ t（指数 4）</text></svg>

- 歪み 0.0: 0° で 0.563、15° で 0.490、30° で 0.316、45° で 0.141、60° で 0.035、75° で 0.003
- 歪み 0.3: 0° で 0.291、15° で 0.253、30° で 0.164、45° で 0.073、60° で 0.018、75° で 0.001
- 歪み 0.6: 0° で 0.146、15° で 0.127、30° で 0.082、45° で 0.037、60° で 0.009、75° で 0.001

太陽の真反対から 45° ずれると、歪みが何であっても最大値の約 4 分の 1 まで下がります。歪みを大きくすると全体が弱まります。これは光の向きが法線の側（上）に曲がり水平にいるカメラから外れるためです。強さは `gSunColor` の側で調整します。

山の幅は `p` で変えます。`p` を大きくすると太陽の方向を見たときだけ光る狭い山になります。小さくすると広い範囲がぼんやり明るくなります。

### コード {#trans-code}

```hlsl
// 透過光。n は表側の法線、v は葉からカメラへ向かう単位ベクトル。thickness は 0（薄い）〜1（厚い）。
float3 Translucency(float3 n, float3 v, float3 albedo, float thickness) {
  float3 h = normalize(gSunDir + n * gTransDistort);  // 法線で曲げた光の向き（葉の中の屈折と散乱の近似）
  float t = pow(saturate(dot(v, -h)), gTransPower);   // 光が葉を抜けてカメラに向かうほど強い
  return albedo * gSunColor * t * (1.0 - thickness);  // 葉の色を通した光。厚い葉は透けない
}
```

`thickness` を引くので厚い葉は透けません。透けた光の色は `albedo` を掛けるので、緑や黄色になります。白い光は透けません。透過光は影の中では出ないので、呼び出し側で `shadow` を掛けます（後述の `ShadeGrass`）。

## ③ 根元の暗さ {#ao}

草の根元は周りの草に挟まれて暗いはずです。草 1 本ずつの AO は計算できないので、高さ `t` の関数で近似します。

```hlsl
// 根元を暗くする AO。height_t は 0〜1。1.5 倍して、高さの 2/3 で 1 になるようにした（一例）。
float RootAo(float height_t) {
  return lerp(gRootAo, 1.0, saturate(height_t * 1.5));
}
```

高さに 1.5 を掛けるのは、高さの 3 分の 2 で明るさが 1 に達するようにするためで、一例です。数えると `t = 0` で 0.300、0.2 で 0.510、0.4 で 0.720、0.6 で 0.930、0.67 以上で 1.000 です。根元の暗さ（`gRootAo`）は 0.2〜0.4 の範囲で、草の密度が高いほど暗くします。根元の色は地形のテクスチャの色に合わせます。

環境光は上向きの面には空の色（青みがかる）、下向きの面には地面の照り返しの色を使います。すると、草の裏側（下向き）に地面の色が自然に乗ります。

## ④ 影 {#shadow}

- **草が受ける影。** 木、建物、岩の影を草が受けます。普通のシャドウマップを引けば、影の中の草は暗くなります。
- **草が落とす影。** 落とさないことが多いです。理由は数字で分かります。5 三角形の帯が 10 万本なら 0.5M 三角形、100 万本なら 5.0M、300 万本なら 15.0M 三角形が、カスケード 1 枚ごとに増えます。
- **草の影の代わり。** 地面のテクスチャに暗い色を焼くか草が生えている場所で地形の色を少し暗くします。草の影の印象が出ます。
- **木の影。** 木の葉はアルファ テストで影を切り抜きます（[Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)）。

草の影を省くのは一般的な選択です。そのかわり地面のライティングに草の影の印象を足します。

## ⑤ スペキュラー {#specular}

草の光沢は葉の表面のワックス質や細い葉の向きから来ます。控えめに足します。粗さを高く（0.7〜0.9）すると、鋭いハイライトが出ません。GGX の法線分布 `D` の正面での値は `1 / (π α²)`、`α = roughness²` で粗さ 0.2 で 198.94、0.4 で 12.43、0.6 で 2.46、0.8 で 0.78、0.9 で 0.49 です。粗さ 0.2 の草はハイライトが 200 倍近く尖って、遠くでちらつきます。

遠くの草はスペキュラーを 0 にします。小さなハイライトはサブピクセルの大きさになってちらつくからです。距離に応じて消えるようにします。

## ⑥ すべてをまとめる {#all}

最後に、全部の項を足し合わせるシェーダーです。

```hlsl
// 距離による霧。地形と同じ式と密度を使うこと（草だけ霧がずれると浮いて見える）。
float3 ApplyFog(float3 color, float distance) {
  float f = exp(-gFogDensity * distance);             // 指数霧の透過率
  return lerp(gFogColor, color, f);                   // 遠いほど霧の色へ
}

// 草のライティング全体。is_back_face は SV_IsFrontFace の否定。
float3 ShadeGrass(float3 albedo, float3 blade_n, float3 terrain_n, float height_t, float thickness,
                  float shadow, float3 world_pos, bool is_back_face) {
  float3 n = GrassNormal(blade_n, terrain_n, height_t);       // 寄せた法線
  if (is_back_face) n = -n;                                   // 帯の裏面は法線を反転する（足した: 両面を描く草のため）
  float3 to_cam = gCameraPos - world_pos;                     // 草からカメラへ
  float dist = length(to_cam);                                // カメラまでの距離
  float3 v = to_cam / max(dist, 1e-4);                        // 単位ベクトル

  float n_dot_l = saturate(dot(n, gSunDir));                  // 通常の拡散
  float3 diffuse = albedo * gSunColor * n_dot_l * shadow;     // 影は受ける側だけ使う
  float3 trans = Translucency(n, v, albedo, thickness) * shadow;   // 透過光も影の中では出ない

  float up = n.y * 0.5 + 0.5;                                 // 上向きなら 1
  float3 ambient = albedo * lerp(gGroundAmbient, gSkyAmbient, up) * RootAo(height_t);   // 環境光と根元の AO

  // スペキュラーは弱く、遠くでは消す（小さなハイライトは遠くでちらつく）。
  float3 h = normalize(gSunDir + v);                          // ハーフベクトル
  float spec_fade = 1.0 - saturate((dist - gSpecFadeNear) / (gSpecFadeFar - gSpecFadeNear));   // 距離で 1 → 0
  float3 spec = gSunColor * pow(saturate(dot(n, h)), 16.0) * 0.04 * spec_fade * shadow;        // 控えめなつや（一例の係数）

  return ApplyFog(diffuse + trans + ambient + spec, dist);    // 最後に霧をかける
}
```

<svg class="fig flow" viewBox="0 0 660 310" role="img" aria-label="草の色を作る項"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">草の色を作る項</text><text x="330" y="24" text-anchor="middle" style="font-size:13px;font-weight:700">草の色を作る項（足し合わせる）</text><rect x="20" y="50" width="150" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="95.0" y="69.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">拡散</text><text x="190" y="74" text-anchor="start" style="font-size:12px;font-weight:400">法線を地形に寄せる・影を受ける</text><rect x="20" y="100" width="150" height="38" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="95.0" y="119.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">透過光</text><text x="190" y="124" text-anchor="start" style="font-size:12px;font-weight:400">葉の裏から抜ける光・薄さで弱める</text><rect x="20" y="150" width="150" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="95.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">環境光</text><text x="190" y="174" text-anchor="start" style="font-size:12px;font-weight:400">上は空・下は照り返し・根元を AO で暗く</text><rect x="20" y="200" width="150" height="38" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="219.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">スペキュラー</text><text x="190" y="224" text-anchor="start" style="font-size:12px;font-weight:400">弱く・遠くでは消す</text><rect x="20" y="250" width="150" height="38" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="95.0" y="269.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">霧</text><text x="190" y="274" text-anchor="start" style="font-size:12px;font-weight:400">地形と同じ式で最後にかける</text></svg>

`is_back_face` は帯の裏面を描くとき（両面描画）に法線を反転するための引数です。足した処理でこれがないと裏面は法線が逆を向いて暗くなります。`ApplyFog` は地形と同じ式と密度を使います。草だけ霧がずれると遠くで草が地面から浮いて見えます（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）。

## 草と地形の境目を消す {#blend}

草のライティングは地形のライティングと連続している必要があります。

- **色。** 草の根元の色を地形のテクスチャの色に合わせます。
- **明るさ。** 根元で草の法線を地形の法線に近づけます。
- **影。** 同じシャドウマップを同じ精度で引きます。
- **霧。** 地形と同じ距離の霧をかけます。

## よくあるミス {#mistakes}

??? failure "逆光の葉が真っ黒になる"
    原因は透過光を足していないことです。`n·l` は光が当たらない面で 0 になるので、裏から照らされた葉は暗くなります。透過光を足します。

??? failure "草原がざらついて、ごちゃごちゃして見える"
    原因は草の法線をそのまま使っていることです。地形の法線へ寄せます。`w = 0.3` で明るさのばらつきが約 3 分の 1 になります。

??? failure "草の裏面が真っ黒になる"
    原因は両面描画の帯で、裏面の法線が反転していないことです。`SV_IsFrontFace` を使って裏面では法線を反転します。

??? failure "遠くの草がちらつく"
    原因はスペキュラーが遠くでも残っていることです。粗さが低いとハイライトが小さく、画素より細くなります。距離に応じて 0 にします。

??? failure "草だけ霧の色が違って浮く"
    原因は霧の式か密度が、地形とずれていることです。同じ関数を共有します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 草の法線を地形の法線へ寄せる。`w = 0.3` で明るさのばらつきが約 1/3
    - [x] 透過光は `pow(saturate(dot(v, −h)), p)`。太陽の真反対から 45° ずれると約 1/4
    - [x] 根元は高さで暗くする（`t = 0` で 0.3）。根元の色は地形に合わせる
    - [x] 草は影を受けるだけ。落とすと 100 万本で 500 万三角形が増える
    - [x] スペキュラーは弱く、遠くで消す。霧は地形と同じ式

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#include <numbers>
#include <random>

const double kPi = std::numbers::pi;           // 円周率
const double kDeg = 180.0 / kPi;               // ラジアン -> 度

struct V3 { double x, y, z; };
V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
V3 Normalize(V3 a) { const double l = std::sqrt(Dot(a, a)); return {a.x / l, a.y / l, a.z / l}; }

int main() {
  // 1. 法線を地形の法線（真上とする）へ寄せたときの、明るさ n.l のばらつき。
  //    草 1 本の法線: 真上から 0〜60 度ランダムに傾け、方位もランダム（一例）。
  //    n = normalize(lerp(up, blade, w))。w = 1 は寄せない、w = 0 は完全に寄せる。太陽の高さ 45 度。
  std::printf("-- n.l spread of 100000 blades (light elevation 45 deg, blade tilt 0-60 deg)\n");
  std::mt19937 rng(12345);                                        // 乱数の種を固定する
  std::uniform_real_distribution<double> uni(0.0, 1.0);           // 0〜1 の一様乱数
  const V3 l = Normalize({std::cos(45.0 / kDeg), std::sin(45.0 / kDeg), 0.0});   // 光へ向かう向き
  const V3 up = {0.0, 1.0, 0.0};
  for (double w : {1.0, 0.6, 0.3, 0.1, 0.0}) {
    double sum = 0.0, sum2 = 0.0;
    const int n = 100000;
    for (int i = 0; i < n; ++i) {
      const double tilt = uni(rng) * 60.0 / kDeg;                // 傾き
      const double az = uni(rng) * 2.0 * kPi;                    // 方位
      const V3 blade = {std::sin(tilt) * std::cos(az), std::cos(tilt), std::sin(tilt) * std::sin(az)};
      const V3 nrm = Normalize(up * (1.0 - w) + blade * w);      // 寄せた法線
      const double v = std::max(Dot(nrm, l), 0.0);               // n.l
      sum += v;
      sum2 += v * v;
    }
    const double mean = sum / n;
    const double sd = std::sqrt(std::max(sum2 / n - mean * mean, 0.0));
    std::printf("blade weight %.1f: mean n.l = %.3f, std dev = %.3f\n", w, mean, sd);
  }

  // 2. 透過光の山。t = saturate(dot(v, -h))^p, h = normalize(l + n * distortion)。p = 4。
  //    葉の法線は真上、光は水平から 30 度の高さ。v は「葉からカメラへ向かう向き」。
  //    カメラが太陽の真反対（水平）にあるときを 0 度として、水平に回した角度ごとの t を数える。
  std::printf("-- translucency lobe by view angle from the anti-sun direction (light elevation 30 deg)\n");
  const V3 lt = Normalize({std::cos(30.0 / kDeg), std::sin(30.0 / kDeg), 0.0});   // 光へ向かう向き
  for (double dist : {0.0, 0.3, 0.6}) {
    std::printf("distortion %.1f:", dist);
    for (double ang : {0.0, 15.0, 30.0, 45.0, 60.0, 75.0}) {
      const V3 view = {-std::cos(ang / kDeg), 0.0, std::sin(ang / kDeg)};        // 水平面で回したカメラの向き
      const V3 h = Normalize(lt + up * dist);                                    // 法線で曲げた光の向き
      const double t = std::pow(std::clamp(-Dot(view, h), 0.0, 1.0), 4.0);      // 山の高さ
      std::printf("  %2.0f deg: %.3f", ang, t);
    }
    std::printf("\n");
  }

  // 3. 根元の暗さ（高さ t の関数）。ao = lerp(0.3, 1, saturate(1.5 t))。
  std::printf("-- height AO\n");
  for (double t : {0.0, 0.2, 0.4, 0.6, 0.67, 1.0}) {
    const double s = std::clamp(1.5 * t, 0.0, 1.0);
    std::printf("t=%.2f: ao = %.3f\n", t, 0.3 + (1.0 - 0.3) * s);
  }

  // 4. 影を落とす草の三角形の数。1 本 5 三角形（7 頂点の帯）。
  std::printf("-- grass shadow casting cost\n");
  for (double blades : {1e5, 1e6, 3e6}) {
    std::printf("%.0e blades x 5 triangles = %.1f M triangles per shadow cascade pass\n", blades, blades * 5.0 / 1e6);
  }

  // 5. スペキュラーの鋭さ（GGX の法線分布 D、正面）。alpha = roughness^2、D(0) = 1 / (pi alpha^2)。
  std::printf("-- GGX peak D (normal incidence)\n");
  for (double r : {0.2, 0.4, 0.6, 0.8, 0.9}) {
    const double a = r * r;
    std::printf("roughness %.1f: alpha = %.3f, D peak = %6.2f\n", r, a, 1.0 / (kPi * a * a));
  }
}
```

```text title="実行結果"
-- n.l spread of 100000 blades (light elevation 45 deg, blade tilt 0-60 deg)
blade weight 1.0: mean n.l = 0.588, std dev = 0.279
blade weight 0.6: mean n.l = 0.662, std dev = 0.180
blade weight 0.3: mean n.l = 0.696, std dev = 0.087
blade weight 0.1: mean n.l = 0.706, std dev = 0.028
blade weight 0.0: mean n.l = 0.707, std dev = 0.000
-- translucency lobe by view angle from the anti-sun direction (light elevation 30 deg)
distortion 0.0:   0 deg: 0.563  15 deg: 0.490  30 deg: 0.316  45 deg: 0.141  60 deg: 0.035  75 deg: 0.003
distortion 0.3:   0 deg: 0.291  15 deg: 0.253  30 deg: 0.164  45 deg: 0.073  60 deg: 0.018  75 deg: 0.001
distortion 0.6:   0 deg: 0.146  15 deg: 0.127  30 deg: 0.082  45 deg: 0.037  60 deg: 0.009  75 deg: 0.001
-- height AO
t=0.00: ao = 0.300
t=0.20: ao = 0.510
t=0.40: ao = 0.720
t=0.60: ao = 0.930
t=0.67: ao = 1.000
t=1.00: ao = 1.000
-- grass shadow casting cost
1e+05 blades x 5 triangles = 0.5 M triangles per shadow cascade pass
1e+06 blades x 5 triangles = 5.0 M triangles per shadow cascade pass
3e+06 blades x 5 triangles = 15.0 M triangles per shadow cascade pass
-- GGX peak D (normal incidence)
roughness 0.2: alpha = 0.040, D peak = 198.94
roughness 0.4: alpha = 0.160, D peak =  12.43
roughness 0.6: alpha = 0.360, D peak =   2.46
roughness 0.8: alpha = 0.640, D peak =   0.78
roughness 0.9: alpha = 0.810, D peak =   0.49
```

## 参考資料 {#references}

このページの式と数字は C++ で確かめたものです。以下の資料は**今回は読んでいません**。透過光の式がこれらの資料の式と同じかどうかは、確かめていません。

- Colin Barré-Brisebois, Marc Bouchard, "Approximating Translucency for a Fast, Cheap and Convincing Subsurface Scattering Look", Game Developers Conference 2011
- Tiago Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007
- Sucker Punch の発表（Wohllaib, "Procedural Grass in Ghost of Tsushima", GDC 2021）
- Kevin Boulanger, Sumanta Pattanaik, Kadi Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009
- Klaus Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004

## 関連ページ {#related}

- [Vegetation](index.md)
- [Grass Shape](grass-shape.md)
- [Alpha-Tested Shadows](../../shadows/special-cases/alpha-test-shadows.md)
