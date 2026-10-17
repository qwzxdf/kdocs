---
title: 距離フォグ
tags:
  - 描画
---

# 距離フォグ

**遠くの山は青白く霞んで見えます**（**空気遠近法**）。**絵画でも古くから使われる**奥行きの手がかりで、<strong>ゲームでは「距離フォグ」</strong>として**実装**します。**距離に応じて物の色を霞の色に近づける**だけの**単純な処理**ですが、**奥行き感・スケール感・雰囲気**を**大きく左右します**。このページでは、**フォグの式（線形・指数・指数の 2 乗）・高さフォグ・太陽方向のにじみ・空との色合わせ・物理に基づく空気遠近法**を説明します。

!!! tip "ポイント"
    - フォグ ＝ <strong>物の色を、距離に応じてフォグの色に混ぜる</strong>：<strong>`color = lerp(fog_color, color, T)`</strong>（<strong>T は透過率</strong>）。
    - <strong>指数フォグ</strong> <strong>T = exp(−density · distance)</strong> が<strong>物理的に自然</strong>（Beer の法則）。
    - <strong>高さフォグ</strong>：<strong>低い所ほど濃い</strong>（<strong>谷に溜まる霧</strong>）。<strong>高さで密度が指数的に減る</strong>。
    - <strong>フォグの色は、空の色に合わせる</strong>。<strong>太陽の方向は明るく暖かく</strong>。
    - <strong>HDR の途中で適用</strong>する（<strong>トーンマップの前</strong>）。
    - <strong>半透明の物</strong>にも<strong>フォグ</strong>を掛ける（<strong>掛けないと遠くで浮く</strong>）。

## なぜ必要か

**フォグがない**と**遠くの物が近くの物と同じコントラストで見え**、**平面的**で**スケール感が出ません**。**フォグ**は**遠い物ほど霞ませる**ことで、**奥行きを伝えます**。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="空気遠近法">
<text x="20" y="24" class="fig-title">フォグなし（上）とあり（下）：遠くほど空の色に近づく</text>
<polygon points="40,90 160,50 240,90 320,40 420,90 520,55 620,90 740,45 740,90" fill="#2d5a3d"/>
<polygon points="40,185 160,145 240,185 320,135 420,185 520,150 620,185 740,140 740,185" fill="#2d5a3d" opacity="0.9"/>
<polygon points="320,185 420,185 520,150 620,185 740,140 740,185" fill="#b8c9e0" opacity="0.65"/>
<polygon points="520,185 620,185 740,140 740,185" fill="#b8c9e0" opacity="0.4"/>
<text x="40" y="112" style="font-size:12px">全部同じ濃さ</text>
<text x="40" y="206" style="font-size:12px">遠いほど霞む</text>
</svg>

## フォグの式

**光は距離 d を進むと減衰して散乱光と入れ替わります**。**物の色 C は、フォグの色 F と混ざります**。

<div class="formula">C_final = C · T + F · (1 − T)　（T：透過率）</div>

| 種類 | 透過率 T | 特徴 |
| --- | --- | --- |
| **線形** | <strong>T = saturate((end − d) / (end − start))</strong> | **start までは影響なし、end で完全にフォグ**。**調整しやすいが物理的ではない** |
| **指数** | <strong>T = exp(−density · d)</strong> | **物理的に自然**。**遠くが徐々に霞む** |
| **指数の 2 乗** | <strong>T = exp(−(density · d)²)</strong> | **近くはほぼ透明である距離から急に霞む** |

```hlsl
float FogTransmittance(float distance_to_pixel) {
  return exp(-fog_density * distance_to_pixel);
}

float3 ApplyFog(float3 color, float distance_to_pixel) {
  float t = FogTransmittance(distance_to_pixel);
  return lerp(fog_color, color, t);
}
```

| 点 | 説明 |
| --- | --- |
| **距離はカメラからの直線距離** | **深度（Z）ではなく、位置の長さ**を使う（**画面の端でも同じ濃さ**）。**`length(world_position − camera_position)`** |
| **`density`** | **0.001〜0.02 /m** 程度。**視界 200〜2000 m** |
| **HDR で適用** | **トーンマップの前**に掛ける |
| **空にもフォグ** | **地平線付近の空の色をフォグの色と一致させる**（**山が空に溶ける**） |

### 深度から距離を求める

**フル スクリーン パスで、深度バッファから位置を再構築**して**距離**を**出します**。

```hlsl
float3 world_position = ReconstructWorldPosition(uv, depth);
float distance_to_pixel = length(world_position - camera_position);
```

## 高さフォグ

**谷や低地に霧が溜まる**表現です。**霧の密度が高さに対して指数的に減る**と**仮定します**。

<div class="formula">density(h) = density₀ · exp( −falloff · h )</div>

**視線に沿った光学的厚さは、密度を積分した値**です。**指数関数の積分は、解析的に求まる**ので**ステップを刻まず 1 回で計算できます**。

```hlsl
float HeightFogOpticalDepth(float3 camera_pos, float3 world_pos) {
  float3 delta = world_pos - camera_pos;
  float distance_to_pixel = length(delta);
  float height_difference = delta.y;

  float falloff = fog_height_falloff;
  float base = fog_density * exp(-falloff * (camera_pos.y - fog_base_height));
  float integral;
  if (abs(height_difference) > 0.0001) {
    integral = (1.0 - exp(-falloff * height_difference)) / (falloff * height_difference);
  } else {
    integral = 1.0;
  }
  return base * integral * distance_to_pixel;
}

float transmittance = exp(-HeightFogOpticalDepth(camera_position, world_position));
```

| 点 | 説明 |
| --- | --- |
| **解析解** | **視線の高さが変わる区間の積分を、閉じた式で**（**ステップ不要**） |
| **`base`** | **カメラの高さでの密度** |
| **高さ差が 0 に近い** | **0 除算を避けるため、積分の値を 1 に** |
| **`fog_base_height`** | **霧が最も濃い高さ**（**谷底・海面**） |
| **`falloff`** | **大きいほど、霧が薄い層に集中** |

**雲海・谷の霧・朝霧**の表現に**効果的**です。

## 太陽方向のにじみ

**太陽の方向を見ると霧が明るく・暖色に光ります**（**前方散乱**）。**フォグの色を視線と太陽の角度で変えます**。

```hlsl
float sun_amount = saturate(dot(view_dir, sun_dir));
float3 fog_color_dir = lerp(fog_color, sun_fog_color, pow(sun_amount, 8.0));
```

| 点 | 説明 |
| --- | --- |
| **`pow(.., 8)`** | **太陽のすぐ周りだけ** |
| **ミー散乱の位相関数** | **より正確には、Henyey-Greenstein**（[大気散乱](scattering.md)） |
| **夕方** | **太陽側が赤橙、反対側が青紫**になる |

## フォグの色を空に合わせる

**フォグの色が空と違う**と、<strong>遠景の山が「浮いて」</strong>見えます。

| 方法 | 内容 |
| --- | --- |
| **空の色を引いてくる** | **視線の向きの空の色**（スカイビュー LUT など）を**フォグの色に使う**（地平線付近の色） |
| **環境マップの低ミップ** | **環境マップの平均色／視線方向の粗いミップ**を引く |
| **手動設定** | **時間帯ごとに色を設定し補間** |

## 物理に基づく空気遠近法

**大気散乱**（[大気散乱](scattering.md)）の**LUT** を**使うと**、**距離フォグを物理的に決められます**。<strong>Hillaire 2020 の「空気遠近法 LUT」</strong> は、**カメラ前方の froxel ごとの「散乱光」と「透過率」を保持**します。

```hlsl
float4 aerial = aerial_perspective_lut.SampleLevel(linear_clamp, float3(uv, depth_slice), 0);
float3 inscattered = aerial.rgb;
float transmittance = aerial.a;
float3 final_color = scene_color * transmittance + inscattered;
```

| 点 | 説明 |
| --- | --- |
| **`inscattered`** | **視線上で散乱して、カメラに入る光**（**霞の明るさと色**） |
| **`transmittance`** | **物の光が残る割合** |
| **深度スライス** | **深度をスライス番号に変換**（**非線形**）して**サンプル** |
| **利点** | **昼・夕・夜で自動的に色が変わる**。**太陽の方向も反映** |

## 適用する場所

| 場所 | 内容 |
| --- | --- |
| **フル スクリーン パス** | **不透明描画後に深度から位置を再構築して一括適用**。**簡単** |
| **マテリアルのシェーダー内** | **各物体のピクセル シェーダーでフォグを適用**。**半透明にも自然に適用** |
| **半透明** | **半透明は深度バッファに無いので、物ごとにシェーダー内で適用**（**パーティクル、ガラス**） |
| **ポストプロセスの前** | **HDR の線形空間** |

**加算ブレンドの物**は、**フォグの色を足さず、透過率だけ掛けます**（**霞の中で光が薄まるだけ**）。**足すと遠くの加算パーティクルが白く浮きます**。

## 夜と閉所

| 状況 | 扱い |
| --- | --- |
| **夜** | **フォグの色を暗く**。**月明かりで少しだけ明るく** |
| **室内** | **フォグを薄くする／区画ごとに変える**（**ボリューム フォグ**） |
| **洞窟・屋内の区画** | **区画（ボリューム）ごとにフォグの設定**を持ち、**境で補間** |
| **ライトの周り** | **点光源の周りだけ霧が光る**（[ボリューメトリック フォグ](volumetric-fog.md)） |

## よくあるミス

??? failure "フォグを深度（Z）で計算し、画面の端で薄くなる"
    <strong>カメラからの直線距離（`length`）</strong>を使う。

??? failure "空の色とフォグの色が違って、山の境目が見える"
    **フォグの色を地平線の空の色に合わせる**。

??? failure "半透明のパーティクルだけ、フォグが掛からず浮く"
    **半透明の物にもシェーダー内で適用する**。

??? failure "加算ブレンドの物が、遠くで白く光る"
    **フォグの色を足さず、透過率だけ掛ける**。

??? failure "トーンマップの後にフォグを掛けて、色が崩れる"
    **HDR のうち（トーンマップの前）に適用**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォグ ＝ <strong>`lerp(fog_color, color, T)`</strong>。<strong>指数フォグ T = exp(−density · d)</strong> が<strong>自然</strong>
    - [x] <strong>距離は直線距離</strong>（<strong>Z ではない</strong>）
    - [x] <strong>高さフォグ</strong>は<strong>指数密度の積分が解析的に</strong>求まる
    - [x] <strong>フォグの色は空に合わせ</strong>、<strong>太陽方向は明るく</strong>
    - [x] <strong>半透明にも適用</strong>。<strong>加算の物は透過率だけ</strong>
    - [x] <strong>物理的には、空気遠近法 LUT</strong>（Hillaire 2020）

## 参考

- Wenzel, "Real-time Atmospheric Effects in Games"（GDC 2006）
- Quilez, "Better Fog"（iquilezles.org）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）

## 関連ページ

- [空と大気](index.md)
- [大気散乱](scattering.md)
- [ボリューメトリック フォグ](volumetric-fog.md)
- [空のモデル](sky-models.md)
