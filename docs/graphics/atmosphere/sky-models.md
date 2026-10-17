---
title: 空のモデル
tags:
  - 描画
---

# 空のモデル

**空の描画**は**画面の背景全体**を**埋めます**。**もっとも単純なのは、色のグラデーションを塗る**方法で、**もっとも正確なのは、大気の散乱を物理計算する**方法です。このページでは、**スカイドーム／スカイボックスの描き方・グラデーションによる空・解析的な空のモデル（Preetham・Hosek-Wilkie）・太陽と月と星・空をライティングに使う方法**を説明します。物理計算は[大気散乱](scattering.md)で扱います。

!!! tip "ポイント"
    - 空 ＝ <strong>視線の向きごとの色</strong>。<strong>最後に深度が最奥のピクセルに描く</strong>（<strong>他が描かれなかった所だけ</strong>）。
    - <strong>グラデーション</strong>：<strong>地平線と天頂の色を視線の仰角で補間</strong>。<strong>最も安い</strong>。
    - <strong>解析モデル</strong>（Preetham・Hosek-Wilkie）：<strong>太陽の高さと濁り（turbidity）から、数式で空の色</strong>が出る。<strong>時間変化も自然</strong>。
    - <strong>太陽</strong>は<strong>明るい円盤</strong>、<strong>周りに光のにじみ（コロナ）</strong>。<strong>HDR で非常に明るい</strong>。
    - <strong>空の色は環境光</strong>にもなる。<strong>キューブマップ／球面調和関数</strong>に<strong>焼いて</strong>使う。
    - <strong>昼夜の移り変わり</strong>は<strong>太陽の方向を動かす</strong>だけで<strong>連続的</strong>に表せる。

## 空の描き方

**空はワールドの一番遠くにある背景**です。**描き方は 2 通り**あります。

| 方式 | 内容 |
| --- | --- |
| **スカイボックス** | **キューブマップ（6 枚の絵）を貼った箱をカメラ中心に描く** |
| **全画面で計算** | **画面の各ピクセルから視線の向きを求め、その向きの色を計算する** |

**スカイボックスは絵が固定**ですが、**全画面計算は時刻や天気に応じて色を変えられます**。

### 視線の向きを求める

**ピクセルごとの視線の向きは、逆射影行列で作ります**。

```hlsl
float3 ViewDirection(float2 uv) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  float4 clip = float4(ndc, 1.0, 1.0);
  float4 world = mul(clip, inverse_view_projection);
  return normalize(world.xyz / world.w - camera_position);
}
```

| 点 | 説明 |
| --- | --- |
| **クリップ空間の Z = 1** | **最も遠い面**（リバース Z なら 0） |
| **`mul(行ベクトル, 行列)`** | **行ベクトル規約**（`v * M`） |
| **カメラ位置を引く** | **ワールド位置から方向へ** |

### 深度テストで最奥だけに描く

**空は他の物を描いた後で深度が最奥のピクセルだけ**を**塗ります**（**描画量が減る**）。

| 方法 | 内容 |
| --- | --- |
| **深度テスト** | **フル スクリーン三角形を、Z = 1（最奥）で描く**。**深度テストの比較を `LESS_EQUAL`** にする |
| **最後に描く** | **不透明の後、半透明の前**に描く（**早期 Z で物があるピクセルを省略**） |

## グラデーションの空

**もっとも簡単**なのは、**視線の仰角（上下の角度）で、地平線の色と天頂の色を混ぜる**方法です。

```hlsl
float3 GradientSky(float3 view_dir) {
  float elevation = saturate(view_dir.y);
  float t = pow(elevation, 0.5);
  float3 sky = lerp(horizon_color, zenith_color, t);

  float below = saturate(-view_dir.y * 4.0);
  return lerp(sky, ground_color, below);
}
```

| 点 | 説明 |
| --- | --- |
| **`pow(elevation, 0.5)`** | **地平線付近で色が急に変わる**（**天頂は広く青い**）。**空の見た目に近づく** |
| **地面の色** | <strong>地平線より下は、地面（暗い色）</strong>で**塞ぐ**（実際の地面が見えない場合） |
| **太陽の方向で色を寄せる** | **太陽のそばを明るく暖色にする**（下の「太陽」） |
| **時間帯のプリセット** | **朝・昼・夕・夜の色セットを補間** |

**グラデーションは、安く・調整しやすい**ですが**太陽の位置で色が変わる**（夕焼けで太陽の側だけ赤い）**といった表現は、手作業になります**。

## 解析的な空のモデル

<strong>Preetham（1999）・Hosek-Wilkie（2012）</strong>は、**空の輝度分布を少数のパラメータの数式で近似**します。<strong>パラメータは太陽の高さ（天頂角）と、大気の濁り（turbidity）</strong>です。**実測・シミュレーションにフィットさせた式**なので、**手作業のグラデーションより自然**で、**時刻による移り変わりも連続**します。

### Preetham（Perez の式）

**Perez の式**で<strong>視線ごとの輝度（Y）と色度（x, y）</strong>を**求めます**。

<div class="formula">F(θ, γ) = (1 + A·e^(B / cos θ)) · (1 + C·e^(D·γ) + E·cos²γ)</div>

| 記号 | 意味 |
| --- | --- |
| **θ** | **視線の天頂角**（真上から何度か） |
| **γ** | **視線と太陽のなす角** |
| **A〜E** | **係数**。**turbidity から線形式で決まる** |

**最終的な空の輝度は、天頂の輝度に比をかけて出します**。

<div class="formula">Y = Y_zenith · F(θ, γ) / F(0, θ_sun)</div>

```hlsl
float Perez(float cos_theta, float gamma, float cos_gamma, PerezCoefficients coeff) {
  return (1.0 + coeff.A * exp(coeff.B / max(cos_theta, 0.01)))
       * (1.0 + coeff.C * exp(coeff.D * gamma) + coeff.E * cos_gamma * cos_gamma);
}
```

| 点 | 説明 |
| --- | --- |
| **`max(cos θ, 0.01)`** | **地平線で発散するのを防ぐ** |
| **xyY から RGB** | **色度 (x, y) と輝度 Y を、XYZ → sRGB（線形）に変換** |
| **露出を掛ける** | <strong>輝度が絶対値（cd/m²）</strong>なので**露出で合わせる** |

### Hosek-Wilkie

**Hosek-Wilkie** は **Preetham の改良版**で、**特に太陽が低いとき、地面の反射率（アルベド）を考慮したとき**に**精度が高い**です。<strong>係数テーブル（9 つのパラメータ × 3 色 × turbidity × albedo × 高さ）</strong>を**公開データとして持ち、式の形は Preetham に似ています**。

| 項目 | Preetham | Hosek-Wilkie |
| --- | --- | --- |
| **精度** | **太陽が低いと不正確** | **より正確** |
| **パラメータ** | **turbidity** | **turbidity ＋ 地面のアルベド** |
| **データ** | <strong>数式の係数のみ（少ない）</strong> | <strong>係数テーブルが必要（大きい）</strong> |
| **用途** | **軽量・手軽** | **品質重視** |

**どちらも空の見た目だけ**で<strong>大気の中を通る光（遠景の霞・光の筋）</strong>は**別に計算**する必要があります。**そこは[大気散乱](scattering.md)の担当**です。

## 太陽・月・星

**空の主役**は**太陽**です。

### 太陽の円盤

**太陽は視線と太陽の方向の角度が小さい所だけ、非常に明るい円盤**です。**実際の太陽の見た目の大きさは、約 0.53°**（**半径 約 0.265°**）です。

```hlsl
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  float cos_radius = cos(radians(0.265));
  float edge = smoothstep(cos_radius - 0.00002, cos_radius, cos_angle);
  return edge * sun_intensity;
}
```

| 点 | 説明 |
| --- | --- |
| **角度を内積で** | **`acos` を避け、`cos` の値で比べる** |
| **縁を少し滑らかに** | **ジャギーを防ぐ**（**TAA で滑らかになる**） |
| **HDR の強度** | **昼の太陽は空の 1 万倍以上明るい**。**ブルームが光る** |
| <strong>周りのにじみ（コロナ）</strong> | **指数関数的に減る光を足す**：`exp(-angle * k)` |
| **大きすぎる太陽は不自然** | **誇張しすぎない** |

### 夕焼けの色

**太陽が地平線に近づくと、光が大気を長く通る**ので、**青が散り尽くして、赤が残ります**。**太陽の色を高さに応じて変える**だけで、**夕焼けの雰囲気**が**出ます**。

```hlsl
float3 SunColor(float sun_height) {
  float t = saturate(sun_height * 4.0);
  return lerp(float3(1.0, 0.35, 0.1), float3(1.0, 0.95, 0.85), t);
}
```

**正確には大気の透過率（光学的厚さ）から求めます**（[大気散乱](scattering.md)）。

### 月と星

| 要素 | 内容 |
| --- | --- |
| **月** | **太陽と同様に円盤**。**月の満ち欠けは、太陽の向きとの角度から、球の陰影で表す** |
| **星** | <strong>星空のキューブマップ（HDR）</strong>を**回して貼る**。**空が暗いほど見える**（**昼の明るさで消える**） |
| **夜空の明るさ** | **月明かり・星明かりを環境光に足す** |
| **またたき** | **星に時間でわずかな明滅** |

```hlsl
float3 stars = star_cubemap.Sample(linear_wrap, mul(view_dir, star_rotation)).rgb;
float night_factor = saturate(-sun_dir.y * 5.0);
float3 sky = day_sky + stars * night_factor;
```

## 空をライティングに使う

**空は大きな光源**でもあります。**地面や物は空から環境光を受けます**。

| 方法 | 内容 |
| --- | --- |
| **キューブマップに焼く** | **空を 6 面に描画し、ミップで粗さを作る**（**IBL**）。**空が変わったら更新** |
| <strong>球面調和関数（SH）</strong> | **空の色を SH（L2 の 9 係数）に投影**し、**拡散の環境光に使う**（[ライティング](../../3d/lighting-normals.md)） |
| **更新の頻度** | **時間変化はゆっくり**なので、**数秒に 1 回、数フレームかけて更新** |
| **太陽は直接光** | **太陽の寄与は環境マップから除き、平行光源として別に扱う**（**二重に数えない**） |

## 昼夜のサイクル

**時刻から太陽の方向を決める**と、**すべてが連動します**。

```cpp
float time_of_day = std::fmod(game_hours, 24.0f) / 24.0f;
float angle = time_of_day * 2.0f * 3.14159265f - 3.14159265f * 0.5f;
Vector3 sun_direction(std::cos(angle) * 0.3f, std::sin(angle), std::cos(angle) * 0.95f);
sun_direction.Normalize();
```

| 連動する物 | 内容 |
| --- | --- |
| **空の色** | **太陽の方向から自動で** |
| **太陽光の色と強さ** | **高さで赤く・弱く**。**地平線の下で 0** |
| **環境光** | **空から更新** |
| **影の向き** | **平行光源の向き** |
| **月と星** | **夜に現れる** |
| **フォグの色** | **空の色に合わせる**（[距離フォグ](aerial-fog.md)） |

## よくあるミス

??? failure "空が最前面に描かれて、手前の物が消える"
    **深度テストを使い、最奥のピクセルだけ描く**（Z = 1、`LESS_EQUAL`）。

??? failure "地平線で、空の色が急に変わる／1 本の線が見える"
    **`cos θ` の下限を設ける**。**地面の色との境をぼかす**。

??? failure "太陽が、環境光と平行光源の両方に入って、二重に明るい"
    **環境マップから太陽の円盤を除く**。

??? failure "太陽の位置を変えても、フォグや環境光が昼のまま"
    **空の更新とフォグ・環境光を連動**させる。

??? failure "夜になっても、空が真っ暗にならない（星が見えない）"
    **星の明るさを太陽の高さで調整**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空 ＝ <strong>視線の向きごとの色</strong>。<strong>最奥のピクセルだけ</strong>に描く
    - [x] <strong>グラデーション</strong>は<strong>最も安い</strong>。<strong>解析モデル（Preetham・Hosek）</strong>は<strong>太陽と濁りから自然な空</strong>
    - [x] <strong>太陽は角度 0.53° の円盤</strong>、<strong>HDR で非常に明るい</strong>。<strong>低いと赤い</strong>
    - [x] <strong>空は環境光でもある</strong>：<strong>キューブマップ／SH に焼く</strong>
    - [x] <strong>時刻 → 太陽の方向</strong>で<strong>すべてが連動</strong>

## 参考

- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight"（SIGGRAPH 1999）
- Hosek & Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance"（SIGGRAPH 2012）
- Perez et al., "An All-Weather Model for Sky Luminance Distribution"（1993）

## 関連ページ

- [空と大気](index.md)
- [大気散乱](scattering.md)
- [距離フォグ](aerial-fog.md)
- [ライティングと法線](../../3d/lighting-normals.md)
