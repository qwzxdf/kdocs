---
title: Distant Shadows
tags:
  - 描画
---

# Distant Shadows

シャドウ マップはカメラの近くを細かく写すための道具です。遠くまで広げようとすると 1 テクセルが何十センチ、何メートルにもなり影がぼやけます。しかも遠くの物もシャドウ パスで描くので、コストが膨らみます。ところが遠景には山や大きな建物が谷に落とす長い影や地面を流れる雲の影のように、細部より「大きな影の形」が大事な影があります。大きな影はシャドウ マップ以外の安い方法で表せます。このページではカスケードが遠くで粗くなる様子を数字で見て、高さマップのレイマーチ、太陽側から走査する O(N) の方法、雲の影、距離フェードと焼いた影の合成を HLSL と C++ で説明します。

!!! tip "ポイント"
    - 4 つのカスケード（各 2048²、最大 2000 m）では最後のカスケードの 1 テクセルは約 2 m になる。この距離の影はシャドウ マップでは細部を出せない。
    - 高さマップのレイマーチは、歩幅が大きいと細い山の影を取りこぼす。幅 5 m の山では歩幅 20 m で影の約半分（48.6 %）を落とした。最大歩数で届く距離も見逃しの原因になる。
    - 太陽の水平方向に沿って、太陽側から走査すると 1 行を O(N) で解ける。レイマーチの 128 倍少ない作業で、格子上のレイマーチと完全に一致した。
    - 雲の影は雲の層の高さを `tan(太陽の仰角)` で割った分だけ地面で太陽の反対側にずれる。高さ 2000 m、仰角 15° なら約 7.5 km。
    - 近くは動的な影、遠くは焼いた影、境は `smoothstep` のフェードでつなぐ。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と読む順番）
    - [Cascaded Shadow Maps (CSM)](../cascaded.md)（近景のカスケードの仕組み）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文を読んで書いたものではありません。Dimitrov の "Cascaded Shadow Maps"（NVIDIA、2007）、Engel の同名の章（ShaderX5）、Wright の "Dynamic Occlusion with Signed Distance Fields"（2015）は、読んでいません。距離場の影の背景は Lumen の SIGGRAPH 2022 の発表（別ページで全部読みました）で、メッシュ距離場の作り方に触れた範囲だけを使います。

数字はこのページが書いた C++ で出しました。地形の断面、太陽の仰角、カスケードの分割は説明のための例です。HLSL は `fxc`（`ps_5_0` と `cs_5_0`）でコンパイルして確かめました。

## 遠くで何が起きるか {#problem}

カスケード シャドウ マップは視錐台を距離で区切り区切りごとに同じ解像度のシャドウ マップを使います。遠い区切りほど同じ解像度で広い範囲を覆うので、1 テクセルが大きくなります。

C++ で数えました。近い面 0.5 m、遠い面 2000 m、分割係数 λ = 0.5 の「practical split」で 4 つに分け、垂直画角 60°、縦横比 16:9、各 2048² とします。区間の遠い面の幅からテクセルの大きさを近似しました（回転や外接球の余裕は無視）。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="カスケードごとの 1 テクセルの大きさ(cm、各 2048²、最大 2000 m)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">カスケードごとの 1 テクセルの大きさ(cm、各 2048²、最大 2000 m)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">125</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">250</text><rect x="104.5" y="174.8" width="43.0" height="15.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="126.0" y="170.82" text-anchor="middle" font-size="10" fill="currentColor">25.3</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">0 (252 m)</text><rect x="239.5" y="159.0" width="43.0" height="31.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="261.0" y="154.98" text-anchor="middle" font-size="10" fill="currentColor">51.7</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">1 (516 m)</text><rect x="374.5" y="137.3" width="43.0" height="52.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="396.0" y="133.32" text-anchor="middle" font-size="10" fill="currentColor">87.8</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">2 (876 m)</text><rect x="509.5" y="69.7" width="43.0" height="120.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="531.0" y="65.69999999999999" text-anchor="middle" font-size="10" fill="currentColor">200.5</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">3 (2000 m)</text></svg>

最初のカスケードは遠い端が約 252 m で、テクセルは約 25 cm です。次が 516 m で約 52 cm、その次が 876 m で約 88 cm、最後が 2000 m で約 2 m です。キャラクターの影や小さな物の影は 25 cm でも荒く見えます。最後の約 2 m では建物の細部は消えて、山や大きな建物の大まかな形しか残りません。

遠景の影に求められるのはおおまかに次の通りです。近景（数十 m）はキャラクターや物の細かい影。中景（数百 m）は建物や木の形が分かる程度の影。遠景（数百 m 以上）は山や大きな建物の大きな影で、細部は不要。超遠景（数 km）は地形の起伏が作る影（山の影が谷に落ちる）。この要求に合わせて方法を変えます。

## 方法 1: カスケードを遠くまで伸ばす {#extend}

最も単純なのは最後のカスケードを遠くまで広げることです。仕組みが統一され特別な処理がいりません。ただし、上の数字の通り遠いカスケードは約 2 m のテクセルで、ぼやけた影になります。しかも遠くの物もシャドウ パスで描くので、描画の範囲が広がってコストが高くなります。遠いカスケードの更新を数フレームに 1 回に間引くとコストは下がります（[Cascaded Shadow Maps (CSM)](../cascaded.md)）。

## 方法 2: 高さマップをレイマーチする {#march}

遠景の影の大半は地形が落とす影です。地形は高さマップで持てるので、点から太陽の向きへレイを進めレイより高い地形に当たったら影、とします。

```hlsl
// 遠景の影: ① 高さマップのレイマーチ ② 太陽側から走査して「影の高さ」を求める方法 ③ 雲の影 ④ 距離フェードと焼いた影の合成。
// 座標は左手系・Y-up（高さは y）。太陽の向きは「太陽へ向かう単位ベクトル」（L）。
// 「足した」と書いた値は、このページが説明のために決めたもの。

Texture2D<float> g_height : register(t0);          // 高さマップ（メートル）。1 テクセル = g_texel_m [m]
Texture2D<float> g_cloud : register(t1);           // 雲の密度（0 = 晴れ、1 = 厚い雲）
Texture2D<float> g_baked_shadow : register(t2);    // 焼いた遠景の影（0 = 影、1 = 光）
SamplerState g_linear_wrap : register(s0);
SamplerState g_linear_clamp : register(s1);

cbuffer DistantCB : register(b0) {
  float3 g_sun_dir;           // 太陽へ向かう単位ベクトル L
  float g_texel_m;            // 高さマップの 1 テクセルの大きさ [m]
  float2 g_map_origin;        // 高さマップの左下（ワールドの xz）[m]
  float2 g_map_size_texels;   // 高さマップの大きさ（テクセル）
  float g_step_m;             // レイマーチの 1 歩 [m]（足した値の例: 高さマップのテクセルと同じ）
  float g_cloud_height;       // 雲の層の高さ [m]
  float2 g_cloud_scale;       // ワールド [m] → 雲テクスチャの UV
  float2 g_wind;              // 風の速さ [m/s]
  float g_time;               // [s]
  float g_cloud_strength;     // 雲の影の濃さ（0〜1）
  float g_shadow_distance;    // シャドウ マップの最大距離 [m]
  float g_fade_range;         // フェードの幅 [m]
};

// ================= ① 高さマップのレイマーチ =================

float SampleHeightWorld(float2 xz) {
  float2 uv = (xz - g_map_origin) / (g_map_size_texels * g_texel_m);
  return g_height.SampleLevel(g_linear_clamp, uv, 0);
}

// 点 (xz, h) から太陽の向きへ進み、地形がレイより高ければ影。戻り値は 0（影）か 1（光）。
float TerrainShadowMarch(float2 xz, float h, int max_steps) {
  float2 dir_xz = g_sun_dir.xz;
  float horiz = length(dir_xz);
  if (horiz < 1e-4) return 1.0;                                 // 太陽が真上: 水平に進めない。影は出ない
  dir_xz /= horiz;
  float rise_per_m = g_sun_dir.y / horiz;                       // 水平 1 m あたりの上昇 [m]
  float2 p = xz;
  float ray_h = h + 0.5;                                        // 自分の面から離す（足した値: 0.5 m。自己影の防止）
  [loop] for (int i = 0; i < max_steps; ++i) {
    p += dir_xz * g_step_m;
    ray_h += rise_per_m * g_step_m;
    float2 uv = (p - g_map_origin) / (g_map_size_texels * g_texel_m);
    if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;             // マップの外に出たら、もう遮るものはない扱い
    if (SampleHeightWorld(p) > ray_h) return 0.0;               // 地形がレイより高い → 影
  }
  return 1.0;
}
```

`rise_per_m` は水平に 1 m 進むときの上昇量で、`太陽の y ÷ 水平成分の長さ` です。太陽が真上（水平成分が 0）なら水平に進めないので、影は出ないとして戻ります。始点は `h + 0.5`、つまり 0.5 m 浮かせます。これを省くと点自身の高さマップに当たって、自分自身が影になります。マップの外に出たらもう遮るものはないとして光を返します。

この方法は簡単ですが歩幅と最大歩数に注意が要ります。C++ で 1000 m の断面に幅 5 m と 20 m の山を置いて、細かい歩幅（0.05 m）の結果を基準に見逃した割合（基準では影なのに、光と判定した割合）を数えました。太陽の仰角は 15°、最大 128 歩です。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="レイマーチの見逃し(%)(歩幅ごと、最大 128 歩、仰角 15°)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">レイマーチの見逃し(%)(歩幅ごと、最大 128 歩、仰角 15°)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">27.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">55</text><rect x="68.0" y="172.8" width="43.0" height="17.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="89.5" y="168.8181818181818" text-anchor="middle" font-size="10" fill="currentColor">6.3</text><rect x="114.0" y="178.8" width="43.0" height="11.2" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="135.5" y="174.8181818181818" text-anchor="middle" font-size="10" fill="currentColor">4.1</text><text x="114.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">1 m</text><rect x="176.0" y="185.6" width="43.0" height="4.4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="197.5" y="181.63636363636363" text-anchor="middle" font-size="10" fill="currentColor">1.6</text><rect x="222.0" y="190.0" width="43.0" height="0.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="243.5" y="186.0" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="222.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">2 m</text><rect x="284.0" y="172.8" width="43.0" height="17.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.5" y="168.8181818181818" text-anchor="middle" font-size="10" fill="currentColor">6.3</text><rect x="330.0" y="187.8" width="43.0" height="2.2" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="351.5" y="183.8181818181818" text-anchor="middle" font-size="10" fill="currentColor">0.8</text><text x="330.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">5 m</text><rect x="392.0" y="134.9" width="43.0" height="55.1" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="413.5" y="130.9090909090909" text-anchor="middle" font-size="10" fill="currentColor">20.2</text><rect x="438.0" y="183.2" width="43.0" height="6.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="459.5" y="179.1818181818182" text-anchor="middle" font-size="10" fill="currentColor">2.5</text><text x="438.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">10 m</text><rect x="500.0" y="57.5" width="43.0" height="132.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="521.5" y="53.45454545454544" text-anchor="middle" font-size="10" fill="currentColor">48.6</text><rect x="546.0" y="165.2" width="43.0" height="24.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="567.5" y="161.1818181818182" text-anchor="middle" font-size="10" fill="currentColor">9.1</text><text x="546.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">20 m</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">山の幅 5 m</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">山の幅 20 m</text></svg>

幅 5 m の山では歩幅 1 m（届く距離 128 m）で 6.3 %、2 m（256 m）で 1.6 %、5 m（640 m）で 6.3 %、10 m（1280 m）で 20.2 %、20 m（2560 m）で 48.6 % です。歩幅が小さいと届く距離が足りず遠くの山の影を落とします（1 m）。歩幅が大きいと細い山の上を飛び越えます（10 m 以上）。**歩幅と最大歩数の積が届く距離で、歩幅が地形の細部の大きさを決める**ので、この 2 つのバランスを取る必要があります。幅 20 m の山は歩幅 2 m で 0 %、20 m でも 9.1 % で、広い山ほど歩幅に強くなります。誤判定のうち基準は光なのに影と判定した割合は、すべての設定で 0 % でした。

## 方法 3: 太陽側から走査する（O(N)）{#sweep}

太陽の水平方向が固定なら高さマップの 1 行をもっと安く解けます。太陽に近い側から遠い側へ走査し、「影の高さ」を持ち回ります。

手前の山が作る影の面は遠ざかるほど下がります。1 歩進むと `slope × step` だけ下がります（`slope = 太陽の y ÷ 水平成分`）。位置 `i` の影の高さは `shade_h(i) = max(h(i), shade_h(i−1) − slope × step)` で、`h(i) < shade_h(i−1) − slope × step` ならその点は影の中です。

```hlsl
// ================= ② 太陽側から走査する（O(N)）=================

// 1 本の走査線（太陽に近い側から遠い側へ）。「影の高さ」shade_h を持ち回る。
//   shade_h(i) = max(h(i), shade_h(i-1) - slope * step)  : 手前の山が作る影の面は、奥へ向かって slope で下がる。
//   h(i) < shade_h(i) なら、i は影の中。
// 1 スレッドが 1 本の走査線を担当する。走査線は、太陽の水平方向に沿った行（ここでは +x 方向に太陽がある行を、x を減らしながら走る）。
RWTexture2D<float> g_out_shadow : register(u0);                 // 0 = 影、1 = 光
Texture2D<float> g_height_load : register(t3);

[numthreads(64, 1, 1)]
void ShadowSweepCS(uint3 dtid : SV_DispatchThreadID) {
  uint row = dtid.x;
  if (row >= (uint)g_map_size_texels.y) return;
  float slope = g_sun_dir.y / max(abs(g_sun_dir.x), 1e-4);      // 太陽が +x 側にある行の例。水平 1 m あたりの上昇
  float step_m = g_texel_m;
  float shade_h = -1e9;                                          // 最初は何も遮らない
  int w = (int)g_map_size_texels.x;
  for (int x = w - 1; x >= 0; --x) {                            // 太陽側（+x）の端から、遠い側（−x）へ
    float h = g_height_load.Load(int3(x, row, 0));
    shade_h = shade_h - slope * step_m;                         // 影の面は 1 歩進むと slope × step 下がる
    if (h >= shade_h) { shade_h = h; g_out_shadow[uint2(x, row)] = 1.0; }   // 地形が影の面より高い → この点は光、影の面を更新
    else { g_out_shadow[uint2(x, row)] = 0.0; }                  // 影の面より低い → 影
  }
}
```

1 スレッドが 1 本の走査線を担当し、`x` を減らしながら走ります。地形が影の面より高ければその点は光で、影の面を更新します。低ければ影です。1 行 N テクセルの作業は N 回で、レイマーチ（128 歩）の 128 分の 1 です。

C++ で確かめました。1 m 格子の断面でこの走査の結果と「同じ格子の高さだけを使い歩幅 1 m で無制限に進めるレイマーチ」を比べると、1000 点中、差は 0 でした。連続な地形の細かい歩幅（0.05 m）との比較では、幅 5 m の山で 3 点、幅 20 m で 12 点が違いました。格子の離散化（1 m 刻み）の差です。

太陽の水平方向が変わるたびに走査し直す必要があります。向きに合わせて高さマップを回すか走査線を斜めに取る工夫が要ります。ここでは、太陽が +x 側にある行を例にしました。結果はテクスチャ（0 = 影、1 = 光）に保存して毎フレーム引けます。太陽は 1 日かけてゆっくり動くので、数フレーム、または数十秒に 1 回の更新で足ります。

## 方法 4: 事前に焼く・距離場 {#baked}

動かない遠景の影は事前に計算して、テクスチャに焼けます。地形や建物の影をライトマップに焼き込む方法（[Lightmaps](../../gi/lightmaps/index.md)）は、太陽が動かない場面に向きます。太陽が動くなら時間帯ごとに複数枚を焼いて補間する必要があります。上の方法 3 の結果をそのまま焼いた影として使うこともできます。

メッシュ距離場（各点から最も近い面までの距離）を使うと柔らかい影を遠くまで安く出せます（[Distance Field Shadows](../sdf-shadows.md)）。Lumen の発表によるとメッシュ距離場は、薄い壁を取りこぼさないよう実行時に膨らませて使います。

## 雲の影 {#cloud}

雲の影は地面を流れる大きくて柔らかい影です。雲の密度テクスチャを太陽の方向から地面に投影し、ライティングに掛けます。

```hlsl
// ================= ③ 雲の影 =================

// 点から太陽へ向かうレイが雲の層（高さ H）と交わる位置を、雲テクスチャの UV にする。
// 雲の層が高いほど、影は地面で太陽と反対側へずれる（ずれ = (H − y) / tan(太陽の仰角)）。
float CloudShadow(float3 world_pos) {
  float t = (g_cloud_height - world_pos.y) / max(g_sun_dir.y, 0.05);   // 太陽の仰角が低すぎる場合は打ち切る（足した値）
  float2 hit_xz = world_pos.xz + g_sun_dir.xz * t;               // 雲の層との交点（ワールド xz）
  float2 uv = hit_xz * g_cloud_scale + g_wind * g_time * g_cloud_scale;   // 風で雲が流れる
  float density = g_cloud.SampleLevel(g_linear_wrap, uv, 0);
  return lerp(1.0, 1.0 - density, g_cloud_strength);             // 1 = 影なし、小さいほど暗い
}
```

点から太陽へ向かうレイが高さ `H` の雲の層に当たる位置を求めます。`t = (H − y) / L.y` で `L` は太陽へ向かう単位ベクトルです。交点の xz をテクスチャの UV にして、雲の密度を引きます。**雲の層が高いほど影は地面で太陽の反対側にずれます。** ずれは `(H − y) / tan(仰角)` です。

C++ で数えました。高さ 2000 m の雲は仰角 60° で 1155 m、45° で 2000 m、30° で 3464 m、15° で 7464 m ずれます。仰角 5° では 22.9 km です。日の出と日没の近くではずれが極端に大きくなります。`max(g_sun_dir.y, 0.05)` で打ち切るのは仰角が低すぎるときの発散を避けるためで、このページが決めた値です。

風で流すには UV に `風の速さ × 時間` を足します。雲そのものを描く側（[Clouds](../../atmosphere/clouds/index.md)）と同じ風、同じスケールを使うと見える雲と影がそろいます。

## 距離フェードと合成 {#fade}

シャドウ マップの最大距離で影が突然消えると、境目が線として見えます。手前からなめらかに消します。

```hlsl
// ================= ④ 距離フェードと焼いた影の合成 =================

float DistantShadow(float3 world_pos, float view_depth, float dynamic_shadow) {
  // 動的なシャドウ マップの有効度。最大距離の手前 fade_range から、smoothstep で 1 → 0。
  float t = saturate((g_shadow_distance - view_depth) / g_fade_range);
  float dynamic_weight = t * t * (3.0 - 2.0 * t);
  // 焼いた影（静的な遠景）。マップの外は光。
  float2 uv = (world_pos.xz - g_map_origin) / (g_map_size_texels * g_texel_m);
  float baked = all(uv >= 0.0) && all(uv <= 1.0) ? g_baked_shadow.SampleLevel(g_linear_clamp, uv, 0) : 1.0;
  // 近くは動的な影、遠くは焼いた影。重なりのある範囲では、暗いほうを使う（二重に暗くならないよう min）。
  float combined = lerp(baked, min(dynamic_shadow, baked), dynamic_weight);
  return combined * CloudShadow(world_pos);
}
```

`t` は最大距離の手前 `g_fade_range` から 1 → 0 に下がる値で、`smoothstep` にして境をなだらかにします。近くは動的な影、遠くは焼いた影を使います。重なる範囲では暗いほうを選び（`min`）、二重に暗くならないようにします。最後に雲の影を掛けます。フェードの幅は最後のカスケードの 1〜2 割が目安です。遠くの影が消えた分、遠景は少し明るく見えます。空気遠近法（[Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)）の霞で、見た目を整えます。

<svg class="fig flow" viewBox="0 0 660 114" role="img" aria-label="距離ごとの担当"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">距離ごとの担当</text><rect x="10" y="34" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="85.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">近景 〜250 m</text><text x="85.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">動的 CSM 0〜1</text><rect x="190" y="34" width="150" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="265.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">中景 〜900 m</text><text x="265.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">CSM 2〜3(間引く)</text><rect x="370" y="34" width="150" height="50" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="445.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">遠景 〜2 km</text><text x="445.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">高さマップ/焼いた影</text><rect x="550" y="34" width="150" height="50" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="625.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">それ以上</text><text x="625.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">影なし + 霞</text><line x1="160" y1="59.0" x2="190" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="340" y1="59.0" x2="370" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="520" y1="59.0" x2="550" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/></svg>

## 組み合わせ（実際の構成）{#combine}

遠景の影は距離で担当を分けます。近景は動的なシャドウ マップ（高解像度のカスケード 0〜1、毎フレーム）です。中景はカスケード 2〜3（更新を間引く）です。遠景は方法 3 の高さマップの影や焼いた影、距離場の影です。それより遠くは影をなくして霞で雰囲気を作ります。近くは動的に遠くは事前計算にして、境をフェードでつなぐのが大きなゲームでの定番の構成です。

## 数字を出した C++ {#experiment}

```cpp
// 遠景の影の数字を出す。
//   [1] カスケードの分割と、1 テクセルの大きさ（距離とともに粗くなる）
//   [2] 高さマップのレイマーチ: 歩幅と最大歩数による取りこぼし（基準は細かい歩幅の結果）
//   [3] 太陽側からの走査（O(N)）が、細かいレイマーチと一致するか
//   [4] 雲の影のずれ（雲の高さ ÷ tan 仰角）
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

constexpr double kPi = 3.14159265358979323846;

// 1 次元の断面の高さ [m]。2 つの山と、ゆるやかな起伏（一例）。
static double Height(double x, double w) {
  return 40.0 * std::exp(-std::pow((x - 300) / w, 2)) + 25.0 * std::exp(-std::pow((x - 700) / (2 * w), 2)) + 3.0 * std::sin(x * 0.02);
}

// 点 x から +x 側の太陽（仰角 elev）へのレイが、地形に遮られるか。歩幅 step [m]、最大 steps 歩。
static bool Shadowed(double x, double w, double elev, double step, int steps) {
  double slope = std::tan(elev), h0 = Height(x, w) + 0.5, px = x, ray = h0;
  for (int i = 0; i < steps; ++i) {
    px += step; ray += slope * step;
    if (Height(px, w) > ray) return true;
  }
  return false;
}

int main() {
  // ---- [1] カスケード ----
  std::printf("[1] 4 cascades, 2048^2 each, near 0.5 m, far 2000 m, split lambda 0.5, vertical fov 60 deg, 16:9\n");
  const double n = 0.5, f = 2000, lambda = 0.5, tan_h = std::tan(30 * kPi / 180) * 16 / 9;
  std::printf("cascade  far[m]   width at far plane[m]   texel[cm]\n");
  for (int i = 1; i <= 4; ++i) {
    double u = i / 4.0;
    double split = lambda * n * std::pow(f / n, u) + (1 - lambda) * (n + u * (f - n));   // practical split scheme
    double width = 2 * split * tan_h;                            // 区間の far 面の幅（近似。回転や球の外接は無視）
    std::printf("%d        %7.1f  %10.1f             %8.1f\n", i - 1, split, width, width / 2048 * 100);
  }

  // ---- [2] レイマーチの取りこぼし ----
  std::printf("\n[2] ridge march: sun elevation 15 deg toward +x, 1000 receivers (1 m apart); reference step 0.05 m, 8000 steps (400 m)\n");
  std::printf("ridge_w  step[m]  steps  range[m]   false light   false shadow\n");
  double elev = 15 * kPi / 180;
  for (double w : {5.0, 20.0}) {
    std::vector<char> ref(1000);
    for (int x = 0; x < 1000; ++x) ref[x] = Shadowed(x, w, elev, 0.05, 8000);
    for (double step : {1.0, 2.0, 5.0, 10.0, 20.0}) {
      for (int steps : {128}) {
        int fl = 0, fs = 0, nref = 0;
        for (int x = 0; x < 1000; ++x) {
          bool s = Shadowed(x, w, elev, step, steps);
          nref += ref[x];
          fl += (ref[x] && !s);
          fs += (!ref[x] && s);
        }
        std::printf("%5.0f    %5.0f    %4d   %7.0f    %5.1f %%       %5.1f %%   (shadowed in ref: %d)\n", w, step, steps, step * steps,
                    100.0 * fl / std::max(nref, 1), 100.0 * fs / std::max(1000 - nref, 1), nref);
      }
    }
  }

  // ---- [3] 走査との一致 ----
  std::printf("\n[3] sweep from the sun side vs fine march (step 0.05 m): grid of 1 m texels\n");
  for (double w : {5.0, 20.0}) {
    const int N = 1000;
    std::vector<double> h(N);
    for (int i = 0; i < N; ++i) h[i] = Height(i, w);
    std::vector<char> sweep(N);
    double slope = std::tan(elev), shade = -1e9;
    for (int i = N - 1; i >= 0; --i) {                           // HLSL の ShadowSweepCS と同じ漸化式
      shade -= slope * 1.0;
      if (h[i] >= shade) { shade = h[i]; sweep[i] = 0; } else sweep[i] = 1;   // 1 = 影
    }
    int mismatch = 0;
    for (int i = 0; i < N; ++i) {
      // 比較の基準: 同じ格子（1 m）の高さだけを使った細かい補間なしの march（歩幅 1 m）と、連続な地形の細かい march の 2 通り
      bool grid_march = false;
      double ray = h[i];
      for (int k = 1; i + k < N; ++k) { ray += slope; if (h[i + k] > ray) { grid_march = true; break; } }
      mismatch += (grid_march != (bool)sweep[i]);
    }
    int cont_mismatch = 0;
    for (int i = 0; i < N; ++i) cont_mismatch += (Shadowed(i, w, elev, 0.05, 20000) != (bool)sweep[i]);
    std::printf("ridge_w=%2.0f: sweep vs grid march (step 1 m, no limit): %d / %d differ; sweep vs continuous fine march: %d / %d differ\n", w, mismatch, N,
                cont_mismatch, N);
  }
  std::printf("work per row of N texels: sweep = N, march = N x steps (128) = %d x\n", 128);

  // ---- [4] 雲の影のずれ ----
  std::printf("\n[4] cloud shadow offset on the ground = (cloud height - ground height) / tan(elevation)\n");
  std::printf("elev[deg]  H=1000 m   H=2000 m   H=4000 m\n");
  for (double e : {60.0, 45.0, 30.0, 15.0, 10.0, 5.0}) {
    double t = std::tan(e * kPi / 180);
    std::printf("%5.0f     %8.0f   %8.0f   %8.0f\n", e, 1000 / t, 2000 / t, 4000 / t);
  }
  return 0;
}
```

```text title="実行結果"
[1] 4 cascades, 2048^2 each, near 0.5 m, far 2000 m, split lambda 0.5, vertical fov 60 deg, 16:9
cascade  far[m]   width at far plane[m]   texel[cm]
0          252.2       517.7                 25.3
1          515.9      1059.1                 51.7
2          875.8      1797.9                 87.8
3         2000.0      4105.6                200.5
```

```text title="実行結果（続き）"
[2] ridge march: sun elevation 15 deg toward +x, 1000 receivers (1 m apart); reference step 0.05 m, 8000 steps (400 m)
ridge_w  step[m]  steps  range[m]   false light   false shadow
    5        1     128       128      6.3 %         0.0 %   (shadowed in ref: 253)
    5        2     128       256      1.6 %         0.0 %   (shadowed in ref: 253)
    5        5     128       640      6.3 %         0.0 %   (shadowed in ref: 253)
    5       10     128      1280     20.2 %         0.0 %   (shadowed in ref: 253)
    5       20     128      2560     48.6 %         0.0 %   (shadowed in ref: 253)
   20        1     128       128      4.1 %         0.0 %   (shadowed in ref: 241)
   20        2     128       256      0.0 %         0.0 %   (shadowed in ref: 241)
   20        5     128       640      0.8 %         0.0 %   (shadowed in ref: 241)
   20       10     128      1280      2.5 %         0.0 %   (shadowed in ref: 241)
   20       20     128      2560      9.1 %         0.0 %   (shadowed in ref: 241)
```

```text title="実行結果（続き）"
[3] sweep from the sun side vs fine march (step 0.05 m): grid of 1 m texels
ridge_w= 5: sweep vs grid march (step 1 m, no limit): 0 / 1000 differ; sweep vs continuous fine march: 3 / 1000 differ
ridge_w=20: sweep vs grid march (step 1 m, no limit): 0 / 1000 differ; sweep vs continuous fine march: 12 / 1000 differ
work per row of N texels: sweep = N, march = N x steps (128) = 128 x
```

```text title="実行結果（続き）"
[4] cloud shadow offset on the ground = (cloud height - ground height) / tan(elevation)
elev[deg]  H=1000 m   H=2000 m   H=4000 m
   60          577       1155       2309
   45         1000       2000       4000
   30         1732       3464       6928
   15         3732       7464      14928
   10         5671      11343      22685
    5        11430      22860      45720
```

## よくあるミス {#mistakes}

??? failure "シャドウ マップの最大距離で、影が急に消える"
    境目が線として見える。最大距離の手前から `smoothstep` でフェードさせる。

??? failure "高さマップのレイマーチで、細い山の影が抜ける"
    歩幅が山の幅より大きい。歩幅を地形の細部に合わせるか走査（方法 3）に変える。

??? failure "遠くの山の影が出ない"
    歩幅 × 最大歩数が、影の長さに届いていない。仰角が低いほど影は長い。届く距離を計算して決める。

??? failure "自分自身が影になる"
    レイの始点を面から離していない。高さを 0.5 m ほど持ち上げる（このページの値）。

??? failure "雲の影が、雲の見えている位置とずれる"
    雲の層の高さを使わずに真上から投影している。太陽の向きに沿って層の高さまで進めた位置で引く。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] シャドウ マップは、遠くで粗くなる（この例の最後のカスケードで約 2 m）。遠景は別の方法で補う。
    - [x] 地形の影は高さマップから。レイマーチは歩幅が大事。太陽側から走査すれば O(N)。
    - [x] 雲の影は層の高さを `tan(仰角)` で割った分、地面でずれる。
    - [x] 近くは動的、遠くは焼いた影。境は `smoothstep` のフェード。

## 参考 {#references}

- Rouslan Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007. 読んでいない。
- Wolfgang Engel, "Cascaded Shadow Maps", ShaderX5, 2006. 読んでいない。
- Daniel Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games. 読んでいない。
- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022. 全部読んだ。メッシュ距離場の作りと膨らませの背景として使った。
- このページの高さマップのレイマーチ、太陽側からの走査、雲の影の投影は説明のために書いたもの。数字はその断面と太陽の仰角の一例。

## 関連ページ {#related}

- [Special Cases](index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [Distance Field Shadows](../sdf-shadows.md)
- [Clouds](../../atmosphere/clouds/index.md)
