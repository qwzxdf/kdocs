---
title: モーション ブラー
tags:
  - 描画
---

# モーション ブラー

**カメラのシャッターが開いている間に、物やカメラが動く**と**像が流れてブレます**。これが**モーション ブラー**です。<strong>ゲームは、1 フレームを「一瞬」</strong>で**描く**ので**動きがカクカク（ストロボのよう）に見えます**。**動いた方向にぼかす**ことで、**動きを滑らかに見せ**、**速度感**を**強調**します。このページでは、**速度バッファ・カメラ モーション ブラー・オブジェクト モーション ブラー・タイル最大速度を使った高速化・TAA との関係**を説明します。

!!! tip "ポイント"
    - モーション ブラー ＝ <strong>1 画素ごとの「速度（画面上の移動量）」</strong>に沿って、<strong>画像をぼかす</strong>。
    - <strong>速度バッファ</strong>：<strong>前フレームと現フレームの画面位置の差</strong>を<strong>画素ごとに保存</strong>（TAA と共用できる）。
    - <strong>カメラのブラー</strong>は<strong>深度と行列から計算</strong>、<strong>オブジェクトのブラー</strong>は<strong>描画時に速度を書く</strong>。
    - <strong>タイル最大速度</strong>で<strong>「この範囲で最も速い動き」</strong>を<strong>見積もり</strong>、<strong>サンプル範囲を決める</strong>。
    - <strong>前景の動く物は、背景にもにじむ</strong>。<strong>深度と速度で重みを付ける</strong>。
    - <strong>強さはシャッター角（シャッター速度）</strong>で<strong>調整</strong>（<strong>フレームレートで変わらないように</strong>）。

## 原理

**シャッターが開いている時間**（**露光時間**）を `T`、**1 フレームの時間**を `Δt` とすると、**1 画素が露光中に動く距離**は、**速度 × T** です。**その線分に沿って、画素の色を平均**すれば、**モーション ブラー**になります。

<div class="formula">ブラーの長さ = 速度（画素/フレーム） × (シャッター時間 / フレーム時間)</div>

| 概念 | 内容 |
| --- | --- |
| **シャッター角** | **フレーム時間のうち、シャッターが開いている割合**を**角度で表す**。**180 度**（半分）が**映画の標準** |
| **ブラーの強さ** | **シャッター角 / 360 × 速度** |
| **フレームレートに依存しない** | **速度を「画素/秒」で持ち**、**フレーム時間に比例**して**スケール**すると、**どのフレームレートでも、同じ見た目** |

## 速度バッファ

<strong>各画素の画面上の移動量（2D ベクトル）</strong>を、**バッファ**に**保存**します。

<div class="formula">velocity = 現フレームの画面位置 − 前フレームの画面位置</div>

### オブジェクトの速度（描画時に書く）

**頂点シェーダー**で**現フレームと前フレームのクリップ空間位置**を**計算**し、**ピクセル シェーダーで差を取り**ます。

```hlsl
struct VsOutput {
  float4 position : SV_Position;
  float4 current_clip : CURRENT_CLIP;
  float4 previous_clip : PREVIOUS_CLIP;
};

VsOutput VSMain(float3 position : POSITION) {
  VsOutput output;
  float4 world_current = mul(float4(position, 1.0), world);
  float4 world_previous = mul(float4(position, 1.0), previous_world);
  output.current_clip = mul(world_current, view_projection);
  output.previous_clip = mul(world_previous, previous_view_projection);
  output.position = output.current_clip;
  return output;
}

float2 PSVelocity(VsOutput input) : SV_Target {
  float2 current_ndc = input.current_clip.xy / input.current_clip.w;
  float2 previous_ndc = input.previous_clip.xy / input.previous_clip.w;
  return (current_ndc - previous_ndc) * float2(0.5, -0.5);
}
```

| 点 | 説明 |
| --- | --- |
| **`previous_world`** | **前フレームのワールド行列**を**保持**しておく（**動く物ごと**） |
| **`previous_view_projection`** | **前フレームのビュー射影行列** |
| **NDC の差** | **ジッター（TAA のサブピクセル ずらし）を、除いた**位置で**差を取る**（**ジッターが速度に混入しないように**） |
| **`* float2(0.5, -0.5)`** | **NDC の差（-1〜1）を、UV の差（0〜1、y 下向き）**に**変換** |
| **スキニング** | **前フレームのボーン行列で、頂点をスキニング**した位置も**必要** |

**速度バッファの書式**は、**`R16G16_FLOAT`**が**標準的**です。

### カメラの速度（深度から再構成）

**静止した背景**は、**カメラだけが動いている**ので、**深度と現フレーム・前フレームの行列**から**計算**できます。**描画時に速度を書かなくてもよい**ため、**動く物だけ書けば済みます**。

```hlsl
float2 CameraVelocity(float2 uv, float depth) {
  float4 clip = float4(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0, depth, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  world /= world.w;
  float4 previous_clip = mul(world, previous_view_projection);
  float2 previous_ndc = previous_clip.xy / previous_clip.w;
  return (clip.xy - previous_ndc) * float2(0.5, -0.5);
}
```

| 点 | 説明 |
| --- | --- |
| **`inverse_view_projection`** | **現フレームのビュー射影の逆行列**。**画素 → ワールド位置**を**復元** |
| **`previous_view_projection`** | **復元したワールド位置を、前フレームの画面へ投影** |
| **動く物体は別に速度を書く** | **動く物体の画素**は、**速度バッファ**に**書かれた値**を**優先**（**カメラの速度は、静的な背景用**） |

## ぼかしの実装

**画素の速度**に沿って、**元の画像を複数サンプルして平均**します。

```hlsl
float3 MotionBlur(float2 uv, float2 velocity_uv, int sample_count) {
  float3 sum = scene_color.SampleLevel(linear_sampler, uv, 0).rgb;
  [loop] for (int i = 1; i < sample_count; ++i) {
    float t = (float(i) / float(sample_count - 1)) - 0.5;
    float2 sample_uv = uv + velocity_uv * t;
    sum += scene_color.SampleLevel(linear_sampler, sample_uv, 0).rgb;
  }
  return sum / float(sample_count);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`t`（-0.5〜0.5）</strong> | <strong>速度ベクトルの両側（前後）</strong>に**サンプル**を**配置**（**中心を通る線分**） |
| **サンプル数** | **8〜16**。**速い動きは多く必要** |
| **`velocity_uv`** | **ブラーの強さ（シャッター角）を掛けた**、**UV での移動量** |

**単純な線形ブラー**は、**ブラーの端がはっきり見えます**。**画素ごとにジッターをかけた**サンプル位置（**IGN**）と**TAA**で**平滑化**すると**綺麗**になります。

## 前景・背景の問題

**速く動く物体**の**ブラー**は、**その物体の外側（背景）にもにじみ出る**べきです。**一方、動かない前景の物体が背景の動きのブラーで汚れてはいけません**。**単純に画素の速度で自分をぼかす**だけでは、**この両方が破綻**します。

| 状況 | 問題 |
| --- | --- |
| **速い物体の輪郭の外** | **背景の画素**は**速度 0**なので**ぼけず**、**物体の動きの尾が輪郭でぱっと切れる** |
| **静止した前景の物の縁** | **背景の速い動き**で**ぼかした色**が、**前景ににじみ出る** |

### 深度と速度による重み付け

**サンプルを集めるとき**、**そのサンプルが自分より手前か奥か**、**そのサンプルの速度が自分まで届くか**を**重みで考慮**します。

```hlsl
float SampleWeight(float center_depth, float sample_depth, float2 center_velocity_px,
                   float2 sample_velocity_px, float offset_length_px) {
  float depth_compare = saturate(0.5 + (sample_depth - center_depth) * kDepthScale);
  float center_reach = saturate(1.0 - offset_length_px / max(length(center_velocity_px), 1e-4));
  float sample_reach = saturate(1.0 - offset_length_px / max(length(sample_velocity_px), 1e-4));
  float front = (1.0 - depth_compare) * sample_reach;
  float back = depth_compare * center_reach;
  return front + back;
}
```

| 点 | 説明 |
| --- | --- |
| **`depth_compare`** | **サンプルが自分より手前（0 に近い）か、奥（1 に近い）か** |
| **`sample_reach`** | **手前のサンプルの速度が、自分の位置まで届くか**（**手前の動く物が自分にかぶさる**） |
| **`center_reach`** | **自分の速度が奥のサンプルまで届くか**（**自分の動きが奥の色を混ぜる**） |
| **考え方** | **手前の動く物のブラーは、背景にかぶさる**。**奥の物は自分（手前）の動きが及ぶ範囲だけ混ぜる** |

<strong>McGuire らの「A Reconstruction Filter for Plausible Motion Blur」</strong>（2012）が**基本**とする方法で**ゲーム各社の実装の元**になっています。

## タイル最大速度

**画素ごとに長い距離を多数サンプルする**のは**重い**です。**画面を小さなタイル（例：16×16）に分け**、**各タイルの最大の速度**を**求めておき**、**ぼかしの範囲をそのタイルの最大速度**に**制限**します（**速くない場所は、短い範囲で済む**）。

| 手順 | 内容 |
| --- | --- |
| **① TileMax** | <strong>各タイルの最大速度（長さが最大の速度ベクトル）</strong>を**求める**（**共有メモリで並列リダクション**） |
| **② NeighborMax** | **周囲 3×3 タイルの、最大速度**を**取り**、**隣のタイルから、流れ込む動き**も**考慮** |
| **③ ブラー** | **NeighborMax の方向・長さ**を**ぼかしの範囲・サンプル方向**に**使う**（**画素自身の速度が小さくても、周囲の速い物が通り過ぎる**） |

**速度が小さい（閾値以下）タイル**は**ぼかし自体をスキップ**できます。

## カメラ モーション ブラーとオブジェクト モーション ブラー

| 種類 | 内容 | 速度の取得 |
| --- | --- | --- |
| **カメラ** | **カメラの移動・回転**で**背景全体**が**流れる** | **深度と行列から計算** |
| **オブジェクト** | <strong>動く物体（キャラ・乗り物）</strong> | **描画時に速度バッファに書く** |
| **スキニング** | **キャラクターの手足** | **前フレームのボーン行列でスキニングして、速度を出す** |

**カメラ ブラーだけ**でも、**スピード感**が**大きく向上**し、**コストが安い**（速度バッファへの書き込みが不要）ため、**まず実装する**のに**向いて**います。

## TAA との関係

**TAA は速度バッファ（動きのベクトル）が必要**なので**モーション ブラーと速度バッファを共有できます**。

| 点 | 内容 |
| --- | --- |
| **順序** | **TAA の後にモーション ブラー**（または、**TAA の前**）。**エンジンによる** |
| **ジッター** | **TAA のジッター**を**速度に含めない**（**差を取るとき、ジッターを除いた位置**で） |
| **重複** | **TAA 自体が時間方向の平均**なので**モーション ブラーとは別物**だが、**見た目が混ざる** |

## 強さの設計

| パラメータ | 内容 |
| --- | --- |
| **シャッター角** | **180 度が標準**。**大きいほど、ブラーが強い** |
| **最大ブラー長** | <strong>画面の数%（例：画面高さの 3%）</strong>に**制限**（**極端な速度で画面が崩れない**） |
| **フレームレート補正** | **ブラーの強さを`Δt` に応じて調整**（**60 FPS と 30 FPS で、見た目を揃える**） |
| **一部の対象を除外** | **プレイヤーの武器・UI・遠景**など |

**モーション ブラーは、好き嫌いが分かれる**ので、**オプションで ON/OFF・強さを選べる**ようにするのが**一般的**です（**酔いの原因にもなる**）。

## よくあるミス

??? failure "TAA のジッターが速度に混入して、静止した物がブレる"
    **ジッターを除いた位置で、速度を計算**する。

??? failure "前フレームのワールド行列を保持しておらず、動く物のブラーが出ない"
    **オブジェクトごとに、`previous_world` を保存**する。

??? failure "背景の速度で、前景の止まった物の縁が汚れる"
    **深度と速度による重み付け**を行う。

??? failure "フレームレートによって、ブラーの強さが変わる"
    **速度を時間ベースで扱い**、**シャッター角**で**スケール**する。

??? failure "非常に速い動きで、サンプルが粗く、縞が出る"
    **サンプル数を増やす**・**ジッター ＋ TAA**・**最大ブラー長を制限**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] モーション ブラー ＝ <strong>画素ごとの速度に沿って、画像をぼかす</strong>。<strong>動きを滑らかに・速度感を強調</strong>
    - [x] <strong>速度バッファ</strong>（現フレームと前フレームの画面位置の差）。<strong>カメラは深度から計算</strong>、<strong>物体は描画時に書く</strong>
    - [x] <strong>前景・背景</strong>は<strong>深度と速度の重み付け</strong>で<strong>処理</strong>（McGuire）
    - [x] <strong>タイル最大速度（TileMax/NeighborMax）</strong>で<strong>サンプル範囲を決め</strong>、<strong>軽く</strong>する
    - [x] <strong>シャッター角</strong>で<strong>強さを調整</strong>。<strong>TAA とは速度バッファを共用</strong>（<strong>ジッターを除く</strong>）

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [ポストプロセス](index.md)
- [アンチエイリアシング（TAA）](antialiasing.md)
- [被写界深度](dof.md)
- [TAA・アップスケール](../../rendering/taa-upscaling.md)
