---
title: Volume-Based God Rays
tags:
  - 描画
---

# Volume-Based God Rays

<strong>ボリューメトリック フォグの froxel を使うと、ゴッド レイも自然に得られます</strong>。光の注入の段階でシャドウを参照するだけで、複数のライトにも対応します。このページではボリュームを使った方法を説明します。

!!! tip "ポイント"
    - froxel の光の注入で、影を参照するだけ。
    - 複数のライトで筋が出る。
    - フォグを使うなら、追加コストがほぼ無い。
    - 解像度が低いので、細い筋は出にくい。

!!! info "このページを読む前に"
    - [God Rays](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ボリュームを使う方法
<strong>ボリューメトリック フォグ</strong>（[Volumetric Fog](../volumetric-fog/index.md)）を使っていれば、光の筋は自動で出ます。froxel に太陽光とシャドウを注入しているため、影による筋が自然に現れます。別途レイマーチを用意する必要はありません。

| 状況 | おすすめ |
| --- | --- |
| ボリューメトリック フォグを使っている | それを使う（自動） |
| 光の筋だけ欲しい | シャドウ マップのレイマーチ |
| とにかく軽く | 放射ぼかし |
| 固定の窓の光 | メッシュの光の柱 |

### 仕組み

ボリューメトリック フォグは、カメラの視錐台を 3D のセル（froxel）に分けて、セルごとに「その位置の霧に各ライトの光がどれだけ届いているか」を計算します（[Volumetric Fog](../volumetric-fog/index.md)）。太陽の光を注入するとき各セルの位置でシャドウ マップを引き、日向なら光を入れ日陰なら入れません。この処理がそのまま光の筋を作ります。

視線方向にセルを積分する最後のパスで、日向のセルの光が積み上がり日陰のセルは何も足さないので、「影を作る物体の後ろは暗くそうでない所は明るい」筋が自然に出ます。放射ぼかしやレイマーチの専用処理は不要でしかも、太陽以外のライト（スポットライト、点光源）も同じ仕組みで筋を出せます。懐中電灯の光線が霧の中でくっきり見える表現が、これで追加コストなく得られます。

### 解像度の限界

froxel の解像度は画面の 160×90 程度の粗さのため、細い筋は出にくくなります。また、奥行き方向の分割（64 スライス前後）が粗いと、筋が距離に沿って階段状になります。この問題には時間蓄積（フレームごとに格子をずらして平均する）で見かけの解像度を上げる、シャドウ マップの参照を PCF のようにぼかす、などの対策があります。それでも足りない細かい筋が必要な場合は、その場所だけシャドウ マップのレイマーチを追加する構成もあります。

## ボリュームでゴッド レイを作る

<strong>ボリューム ライティング</strong>（froxel、[Froxels](../volumetric-fog/froxel.md)）はカメラの前方の空間を、3D グリッドに分割し各セルに光の散乱を事前に、計算しておきます。画素ごとのレイマーチ（[Shadow Map Raymarching](shadowmap-march.md)）を、セルごとの計算に置き換えるので、効率的です。ゴッド レイはこのボリュームの、副産物として自動で現れます。

## 考え方

<strong>カメラから見て奥行き方向に、分割されたセル</strong>（froxel、「フラスタム」+「ボクセル」）の、各セルで 光の散乱（太陽の光が、そのセルでカメラの方へ散る量）を、計算して 3D テクスチャに格納します。画面の各画素は視線に沿ってセルを順に足して、散乱光を合計します。

```text
3D テクスチャ（froxel）: 横 × 縦 × 奥行き（160 × 90 × 64 など）

カメラ ●─────→ 奥行き方向に、セルを、足していく（積分）
        [セル0][セル1][セル2]...[セル63]
```

## ボリュームを作る：光の注入

<strong>各セル</strong>に 太陽の光を注入します。セルの位置が影の中かをシャドウ マップで調べ光が、届くセルだけ散乱光を格納します。

```hlsl
// 計算シェーダー: 各セルに、太陽の光の、散乱を、書き込む。
[numthreads(8, 8, 4)]
void InjectLightCS(uint3 id : SV_DispatchThreadID) {
  float3 cell_world = FroxelToWorld(id);                         // セルの中心の、ワールド位置
  float density = SampleFogDensity(cell_world);                   // そのセルの、霧の密度

  // 太陽の光が、届いているか（シャドウ マップ）。1 = 届く、0 = 影。
  float shadow = SampleShadowMap(cell_world);

  // 視線の方向（カメラから、セルへ）と、太陽の、間の位相関数。
  float3 view_dir = normalize(cell_world - g_camera_position);
  float phase = HenyeyGreenstein(dot(view_dir, g_sun_dir), g_phase_g);

  // 散乱光 = 密度 × 光が届く割合 × 位相関数 × 太陽の光
  float3 scattering = g_sun_color * shadow * phase * density;
  g_froxel_scatter[id] = float4(scattering, density);              // 散乱光と、消散（密度）を、格納
}
```

シャドウ マップの読み込みは、セルごとに 1 回です。画素ごとステップごとのレイマーチ（[Shadow Map Raymarching](shadowmap-march.md)）より、はるかに少ない回数で済みます（160×90×64 = 約 92 万セル）。

## ボリュームを積分する

<strong>奥行き方向</strong>に 手前から奥へ、散乱光を累積しながら透過率を、更新します。

```hlsl
// 計算シェーダー: 各 (x, y) の列について、奥行き方向に、散乱光を、累積する。
[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  float3 accumulated = 0.0;
  float transmittance = 1.0;
  for (uint z = 0; z < kFroxelDepth; ++z) {
    float4 cell = g_froxel_scatter[uint3(id.xy, z)];              // xyz = 散乱光、w = 密度（消散）
    float step_len = SliceThickness(z);                           // このスライスの、厚み（メートル）
    float cell_transmittance = exp(-cell.w * step_len);           // このセルを、通る、透過率

    // 区間内の積分（解析的）: 散乱光 × (1 − 透過率) / 消散
    float3 integral = cell.xyz * (1.0 - cell_transmittance) / max(cell.w, 1e-5);
    accumulated += transmittance * integral;                       // ここまでの、透過率を、掛けて、足す
    transmittance *= cell_transmittance;

    g_froxel_integrated[uint3(id.xy, z)] = float4(accumulated, transmittance);   // 「カメラから、スライス z まで」の結果
  }
}
```

奥行き方向の累積を 各スライスに、保存しておくと画面の画素は自分の深度に、対応するスライスを 1 回読むだけで、カメラからその物体までの散乱光と、透過率を得られます。

## 画面に適用する

```hlsl
// 物体の色に、ボリューム ライティングを、適用する。
float3 ApplyVolumetric(float3 scene_color, float2 screen_uv, float distance_m) {
  float slice = DistanceToSlice(distance_m);
  float4 v = g_froxel_integrated.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
  return scene_color * v.a + v.rgb;                                // 物の色 × 透過率 + 散乱光
}
```

<strong>物体の色に透過率を掛け</strong>、散乱光を足す。霧の式と同じ形ですが散乱光に影と、光の筋が含まれている点が違います。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 画素ごとのレイマーチより、効率的（セルごとに 1 回） |
| 長所 | 霧の密度（場所で、変わる）、局所光（ランプ、ライトの散乱）も同じ仕組みで、扱える（[Light Injection](../volumetric-fog/injection.md)） |
| 長所 | 半透明の物にも同じ、ボリュームを引くだけで適用できる |
| 長所 | 時間方向のフィルタ（TAA）で品質を、上げられる（[Temporal Accumulation](../volumetric-fog/temporal.md)） |
| 短所 | 解像度が低い（画面の 1/8 程度）。細かい光の筋はぼやける |
| 短所 | 奥行き方向の分割による、縞（[Quality and Performance](../volumetric-fog/quality.md)） |
| 短所 | メモリ（3D テクスチャ数枚） |

## よくあるミス

??? failure "細い光の筋が、ぼやける"
    <strong>froxel の解像度を上げる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォグのボリュームに、影を入れるだけ

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [God Rays](index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
