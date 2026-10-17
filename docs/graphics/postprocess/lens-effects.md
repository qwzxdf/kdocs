---
title: レンズ効果
tags:
  - 描画
---

# レンズ効果

**実際のカメラ・レンズ・フィルム**には**理想的ではない性質**があります。**色収差・ビネット（周辺減光）・フィルム グレイン・レンズ フレア・ゴースト・ゴッド レイ**。これらは<strong>「欠点」</strong>ですが**映像に写実感・映画らしさ**を与えるので、**ポストプロセスで意図的に再現**します。**どれも軽いエフェクト**ですが**かけすぎると逆に安っぽく**なります。このページでは、**各効果の原理と実装**、**かけ方の注意**を説明します。

!!! tip "ポイント"
    - <strong>色収差</strong>：<strong>波長ごとの屈折率の違い</strong>で、<strong>画面の端で R・G・B がずれる</strong>。
    - <strong>ビネット</strong>：<strong>画面の周辺が暗くなる</strong>。<strong>視線の誘導・フレーミング</strong>。
    - <strong>フィルム グレイン</strong>：<strong>粒状のノイズ</strong>。<strong>暗部で目立つ</strong>。<strong>バンディングの隠蔽</strong>にも役立つ。
    - <strong>レンズ フレア・ゴースト</strong>：<strong>明るい光源のレンズ内の反射</strong>。<strong>画面の中心を挟んだ反対側</strong>に<strong>像が出る</strong>。
    - <strong>ゴッド レイ（光の筋）</strong>：<strong>遮蔽物の隙間から差す光の筋</strong>。<strong>画面空間の放射状ブラー</strong>で近似。
    - <strong>全て、控えめに</strong>。<strong>UI にはかけない</strong>。

## 色収差（Chromatic Aberration）

**レンズ（ガラス）の屈折率は光の波長で少し違う**ので、**赤・緑・青が少しずつ、違う位置に結像**します。**画面の中心では、ほぼ一致**し、**周辺でずれが大きく**なります。**白と黒の境界に赤や青の縁取り**が見えます。

### 実装

**R・G・B の 3 チャンネルを、画面中心からの距離に応じて、少しずつずらして、サンプル**します。

```hlsl
float3 ChromaticAberration(float2 uv, float intensity) {
  float2 center_offset = uv - 0.5;
  float distance_squared = dot(center_offset, center_offset);
  float2 shift = center_offset * distance_squared * intensity;

  float r = scene_color.SampleLevel(linear_clamp, uv + shift, 0).r;
  float g = scene_color.SampleLevel(linear_clamp, uv, 0).g;
  float b = scene_color.SampleLevel(linear_clamp, uv - shift, 0).b;
  return float3(r, g, b);
}
```

| 点 | 説明 |
| --- | --- |
| **`center_offset * distance_squared`** | **中心ではずれがほぼ 0<strong>、</strong>周辺で急に大きく<strong>（</strong>実際のレンズの収差**に近い） |
| **R と B を逆方向にずらす** | **緑を基準**に**赤は外へ青は内へ**（**符号を逆**にして、**縁取りの色の向きが変わる**） |
| **`intensity`** | **強さ**。**0.005〜0.02 程度**。**強すぎると画面が溶けて見える** |

**より正確**には**多数のサンプルを波長ごとにずらして、スペクトルの色**に**変換し積分**する、**高品質版**もあります。

## ビネット（周辺減光）

**レンズの設計・絞り・フィルターの影響で画面の周辺が中心より暗くなります**。**視線を中心に集める**効果もあります。

```hlsl
float Vignette(float2 uv, float intensity, float smoothness, float roundness) {
  float2 d = (uv - 0.5) * float2(roundness, 1.0) * 2.0;
  float distance_from_center = length(d);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0 - intensity, distance_from_center) * intensity;
}
```

| 点 | 説明 |
| --- | --- |
| **`length(d)`** | **画面中心からの距離**（**中心 0、角で約 1.4**） |
| **`smoothstep`** | **暗くなり始める距離と暗くなりきる距離の間を、滑らかに** |
| **`roundness`** | **アスペクト比の補正**。**円形・楕円形** |
| **乗算** | **`color *= Vignette(...)`<strong>。</strong>HDR の段階（トーンマップ前）**でも**後**でも**可** |

**物理的には、`cos⁴θ` の法則**（**周辺が角度の 4 乗に比例して暗くなる**）が、**自然なビネットの式**です。

<div class="formula">falloff = cos⁴(θ)　（θ：光軸からの角度）</div>

## フィルム グレイン

**フィルムの粒子**や**デジタル センサーのノイズ**に**相当**する、**細かいノイズ**です。**画像の質感**を**加え**、**グラデーションのバンディング**を**隠す**効果もあります。

```hlsl
float Hash(float2 p) {
  float3 p3 = frac(float3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return frac((p3.x + p3.y) * p3.z);
}

float3 FilmGrain(float3 color, float2 pixel, float time, float intensity) {
  float noise = Hash(pixel + frac(time) * 1000.0) - 0.5;
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float response = 1.0 - luma;
  return color + noise * intensity * response;
}
```

| 点 | 説明 |
| --- | --- |
| **`Hash`** | **画素座標から、擬似乱数**。**時間で変えて、毎フレーム違うノイズ** |
| **`response`** | **暗い所ほど、粒状が目立つ**（**実際のフィルム**に近い）。**明部では弱める** |
| <strong>加算（またはオーバーレイ）</strong> | **ノイズを色に足す** |
| **LDR（トーンマップ後）で** | **最終的な見た目の質感**を**加える**ので、**トーンマップ後**に**かける** |

**グレインは見える最小単位（1 画素）が大きすぎる**と**粗く**見えるので、**解像度に応じて、グレインの大きさを調整**します。

## レンズ フレア

**明るい光源**（太陽・ライト）が**視野に入る**と**レンズ内の複数の面で反射**した**光**が、<strong>ゴースト（光の像）・光芒（星形）・ハロー（輪）</strong>として**画面に現れます**。

| 要素 | 内容 |
| --- | --- |
| **ゴースト** | **光源の像が画面中心を挟んだ反対側に、複数の円**として**現れる** |
| **ハロー** | **光源を囲む輪**（**画面中心を中心**とした、**大きな輪**） |
| <strong>光芒（スターバースト）</strong> | **絞りの羽根による回折で、光源から伸びる筋**（**羽根の数に応じた本数**） |
| **ストリーク** | **アナモルフィック レンズの、横に伸びる光** |

### 画面空間のゴースト（Screen-Space Lens Flare）

**明るい部分を抽出**し、**画面中心を軸に反転した位置**をサンプルすることで、**ゴースト**を**生成**します。

```hlsl
float3 LensFlareGhosts(float2 uv, int ghost_count, float dispersal, float distortion) {
  float2 flipped_uv = 1.0 - uv;
  float2 ghost_vector = (0.5 - flipped_uv) * dispersal;

  float3 result = 0.0;
  [loop] for (int i = 0; i < ghost_count; ++i) {
    float2 offset = frac(flipped_uv + ghost_vector * float(i));
    float weight = length(0.5 - offset) / length(float2(0.5, 0.5));
    weight = pow(1.0 - weight, 10.0);
    result += bright_texture.SampleLevel(linear_clamp, offset, 0).rgb * weight;
  }
  return result;
}
```

| 点 | 説明 |
| --- | --- |
| **`flipped_uv = 1 - uv`** | **画面中心に対して、反転した位置** |
| **`ghost_vector`** | **反転位置から画面中心へ向かうベクトル**。**`dispersal` で間隔を調整** |
| **`weight`** | **画面の端（中心から遠い所）のゴーストを弱める**（**画面外にサンプルが飛ぶ**ため） |
| **入力 `bright_texture`** | **ブルームの明るい部分抽出**（**半解像度**） |

**ゴーストに色収差を加え**、**ハロー・ダートを合成**すると**リアル**になります。

### 光芒（スターバースト）

**絞りの羽根の形**の**テクスチャ**を、**光源の位置に重ねる**・**ブルームの後にダート テクスチャ**で**変調**する**方法**が**一般的**です。

## ゴッド レイ（光の筋）

**霧・煙の中**を**光が通る**と<strong>遮蔽物の隙間から差す光が、筋（光線）</strong>として**見えます**。**ボリューメトリック ライティング**（[空と大気・ボリューム](../index.md)）が**物理的な方法**ですが**画面空間の放射状ブラー**で**安く近似**できます。

### 放射状ブラー

**光源の画面上の位置**を**中心**に、**各画素から光源に向かって、サンプルを重ねて平均**します。**遮蔽物（暗い物）の隙間から、光の筋が放射状に伸びる**見た目です。

```hlsl
float3 GodRays(float2 uv, float2 light_uv, int sample_count, float density, float decay,
               float weight, float exposure) {
  float2 delta = (uv - light_uv) * density / float(sample_count);
  float2 sample_uv = uv;
  float illumination_decay = 1.0;
  float3 result = 0.0;

  [loop] for (int i = 0; i < sample_count; ++i) {
    sample_uv -= delta;
    float3 sample_color = occlusion_texture.SampleLevel(linear_clamp, sample_uv, 0).rgb;
    result += sample_color * illumination_decay * weight;
    illumination_decay *= decay;
  }
  return result * exposure;
}
```

| 点 | 説明 |
| --- | --- |
| **`occlusion_texture`** | **光源（空）は明るく、遮蔽物は暗い**画像（**深度から作る**：**空の画素のみ光る**） |
| **`delta`** | **光源方向への、1 ステップの移動量** |
| **`decay`** | **サンプルごとの減衰**（**遠いサンプルほど弱く**） |
| **`density`・`weight`・`exposure`** | **筋の長さ・強さ・全体の明るさ** |
| **欠点** | **光源が画面外**だと**使えない**。**3D の筋ではなく、見かけだけ** |

## 適用の順序

| 効果 | 段階 | 理由 |
| --- | --- | --- |
| **レンズ フレア・ゴッド レイ・ダート** | <strong>HDR（ブルームと同時）</strong> | **光の物理**に近い。**明るい光源から出る** |
| **色収差** | **HDR または LDR** | **画像の空間的なずれ**。**ブルーム・DOF の後** |
| **ビネット** | **HDR または LDR** | **どちらでも可**。**HDR で行うとトーンマップの前の明るさに影響** |
| **フィルム グレイン** | <strong>LDR（最後）</strong> | **最終的な質感**。**UI の前** |

## かけすぎない

| 効果 | 注意 |
| --- | --- |
| **色収差** | **強いと画面が溶けて、不快**。**中心付近はほぼ 0** |
| **ビネット** | **強いと画面が暗くなり、視認性が下がる** |
| **グレイン** | **強いとノイズで見づらい**。**ゲームプレイ中は控えめ** |
| **レンズ フレア** | **画面が白っぽくなり、視認性が下がる** |
| **全般** | **オプションで、ON/OFF できる**ように（**アクセシビリティ・好み**） |

## よくあるミス

??? failure "色収差を、画面全体に一様にかけて、中心の文字までにじむ"
    **中心では 0**、**周辺ほど強く**（`distance_squared`）。

??? failure "グレインを、UI の後にかけて、文字がざらつく"
    **UI はポストプロセスの後に重ねる**。

??? failure "グレインを、毎フレーム同じパターンで、固定ノイズに見える"
    **時間で乱数のシードを変える**。

??? failure "ゴッド レイを、画面外の光源に使って、破綻"
    **光源が画面外のときは、フェードアウト**・**無効化**。

??? failure "ビネットを、UI にもかけて、UI の端が暗くなる"
    **UI は別のパス**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>色収差</strong>：<strong>R・G・B を画面中心からの距離に応じてずらす</strong>（<strong>周辺ほど強く</strong>）
    - [x] <strong>ビネット</strong>：<strong>周辺を暗く</strong>（<strong>`cos⁴θ`</strong> が<strong>物理的</strong>）。<strong>視線誘導</strong>
    - [x] <strong>グレイン</strong>：<strong>粒状のノイズ</strong>。<strong>暗部ほど目立つ</strong>。<strong>LDR で最後に</strong>
    - [x] <strong>レンズ フレア</strong>：<strong>画面中心を軸に反転した位置にゴースト</strong>。<strong>ゴッド レイ</strong>は<strong>放射状ブラーで近似</strong>
    - [x] <strong>控えめに</strong>。<strong>UI にはかけない</strong>。<strong>オプションで切れるように</strong>

## 参考

- Jimenez et al., "Physically Based Lens Flare Rendering"（Eurographics 2011 ポスター）
- Mitchell, "Volumetric Light Scattering as a Post-Process"（GPU Gems 3）
- Hullin et al., "Physically-Based Real-Time Lens Flare Rendering"（SIGGRAPH 2011）

## 関連ページ

- [ポストプロセス](index.md)
- [ブルーム](bloom.md)
- [カラー グレーディング](color-grading.md)
