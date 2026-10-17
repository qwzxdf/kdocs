---
title: 波のジオメトリ
tags:
  - 描画
---

# 波のジオメトリ

**水面の形**（波）を、**どう作るか**です。**実際の海は無数の波が重なった結果**なので、**サイン波をいくつか重ねる**ところから出発し、**より自然な Gerstner 波**、**統計的に現実の海を再現する FFT 海面**へと発展します。このページでは、**サイン波の重ね合わせ・Gerstner 波（尖った波頂）・法線の計算・細かい凹凸の法線マップ・FFT 海面の考え方**を説明します。

!!! tip "ポイント"
    - 波 ＝ <strong>頂点シェーダーで、水面メッシュの頂点を動かす</strong>（<strong>高さ（と水平方向）を時間で変える</strong>）。
    - <strong>サイン波の重ね合わせ</strong>：<strong>方向・波長・振幅・速さが違う波を数本足す</strong>。<strong>単純だが波頂が丸い</strong>。
    - <strong>Gerstner 波</strong>：<strong>頂点を円運動させる</strong>（<strong>上下 ＋ 水平</strong>）。<strong>波頂が尖り、谷が広い、海らしい形</strong>になる。
    - <strong>法線は解析的に（微分で）求める</strong>。<strong>頂点数が少なくても滑らか</strong>。
    - <strong>細かい波は、法線マップを、2 枚以上、違う向きに流して重ねる</strong>。
    - <strong>FFT 海面</strong>：<strong>波のスペクトル（周波数ごとの強さ）</strong>から、<strong>逆 FFT で高さマップを作る</strong>。<strong>最もリアル・重い</strong>。

## 水面のメッシュ

**水面は平らな格子メッシュ**を**用意**し、**頂点シェーダーで波の高さを足します**。

| 方式 | 内容 |
| --- | --- |
| **平面の格子** | **XZ 平面に細かい格子**（例：256×256）。**カメラに近い所を細かく**（LOD・クリップマップ） |
| <strong>画面に追従する格子（Projected Grid）</strong> | **画面の画素に対応する、格子を水面へ投影**。**画面全体を均等な密度**で覆う |
| **カメラ中心のクリップマップ** | **カメラの周りに入れ子の格子**（近くは細かく、遠くは粗く）。**カメラに合わせて移動** |

**水面は広大**（地平線まで）なので**カメラの周りに格子を置き、カメラと一緒に動かして、波の座標はワールド座標で計算**します（**水面がカメラと一緒に動いて見えない**ため）。

## サイン波の重ね合わせ

**1 本のサイン波**は、**進行方向 `D`・波長 `λ`・振幅 `A`・速さ `s`** で決まります。

<div class="formula">h(x, z, t) = A · sin( ω · (D · (x, z)) + φ · t )　（ω = 2π/λ、φ = s · ω）</div>

| 記号 | 意味 |
| --- | --- |
| **A** | **振幅**（波の高さの半分） |
| **λ** | **波長**（波頭から次の波頭までの距離）。**ω = 2π / λ** が**波数** |
| **D** | **波の進む向き**（2D の単位ベクトル） |
| **s** | **波の速さ**。**φ = s · ω** |
| **t** | **時間** |

```hlsl
struct Wave {
  float2 direction;
  float amplitude;
  float wavelength;
  float speed;
};

float WaveHeight(float2 position, Wave wave, float time) {
  float frequency = 2.0 * 3.14159265 / wave.wavelength;
  float phase = wave.speed * frequency;
  return wave.amplitude * sin(dot(wave.direction, position) * frequency + time * phase);
}
```

**方向・波長・振幅を変えた波を、4〜8 本重ね**ると**ランダムな海面**に見えます。**波長を倍々に（大きい波から小さい波へ）、振幅を半分ずつ**と**減らす**のが**定番**です。

| 波 | 波長 | 振幅 | 向き |
| --- | --- | --- | --- |
| **1** | 長い（例：20 m） | 大 | 風向き |
| **2** | 中 | 中 | 少しずらす |
| **3** | 短い | 小 | さらにずらす |
| **4** | 非常に短い | 極小 | 別の向き |

**欠点**：**サイン波は波頂が丸く、谷も同じ形**で**海の「尖った波頂・広い谷」の形にならない**。

## Gerstner 波

**Gerstner 波**は、**水面の「粒子」を、円を描くように動かす**モデルです。**上下に動くだけでなく、水平方向にも動く**ので**波頂に向かって粒子が集まり、波頂が尖り、谷が広がります**。

<svg class="fig illust motion" data-fig="water-gerstner" viewBox="0 0 780 260" role="img" aria-label="Gerstner 波">
<text x="20" y="24" class="fig-title">Gerstner 波：粒子が円運動するので、波頂が尖り、谷が広くなる（上：サイン波、下：Gerstner 波）</text>
<line x1="40" y1="90" x2="740" y2="90" stroke="currentColor" stroke-opacity="0.2"/><line x1="40" y1="190" x2="740" y2="190" stroke="currentColor" stroke-opacity="0.2"/>
<text x="40" y="52" style="font-size:12px">サイン波（波頂が丸い）</text><text x="40" y="152" style="font-size:12px">Gerstner 波（波頂が尖る）</text>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points=""/>
</svg>

**頂点の位置は元の位置 `P₀` を中心に、円運動**します。

<div class="formula">
x = x₀ + Σ ( Q · A · D.x · cos(ω · D·P₀ + φt) )<br>
z = z₀ + Σ ( Q · A · D.z · cos(ω · D·P₀ + φt) )<br>
y = Σ ( A · sin(ω · D·P₀ + φt) )
</div>

| 記号 | 意味 |
| --- | --- |
| **Q** | **波の尖り具合**（0 でサイン波、**大きいほど、波頂が尖る**）。**0〜1/(ω·A) の範囲** |
| **A** | **振幅** |
| **D** | **波の向き** |
| **ω・φ** | **波数・位相の速さ** |

```hlsl
struct GerstnerWave {
  float2 direction;
  float amplitude;
  float wavelength;
  float steepness;
  float speed;
};

float3 GerstnerOffset(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float q = wave.steepness / (k * wave.amplitude);
  float c = cos(phase);
  float s = sin(phase);
  return float3(q * wave.amplitude * wave.direction.x * c,
                wave.amplitude * s,
                q * wave.amplitude * wave.direction.y * c);
}

float3 displaced = float3(position.x, 0, position.y);
for (int i = 0; i < kWaveCount; ++i) {
  displaced += GerstnerOffset(position, waves[i], time);
}
```

| 点 | 説明 |
| --- | --- |
| **`q = steepness / (k·A)`** | **`steepness`（0〜1）が、尖りの度合い**。**複数の波を足すとき、合計が 1 を超えない**ようにする（**超えると波が自分と交差（ループ）して、破綻**） |
| **戻り値** | <strong>元の位置からのずれ（XYZ）</strong>。**頂点に足す** |
| **重ね合わせ** | **波ごとのずれを全て足す** |

**`steepness` の合計が 1 を超えない**ように**注意**します（**波頂がねじれて、メッシュが裏返る**）。

## 法線の計算

**波の法線**は**頂点位置の偏微分**から**求められます**。**Gerstner 波は、解析的な式**があります。

```hlsl
float3 GerstnerNormal(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float wa = k * wave.amplitude;
  float c = cos(phase);
  float s = sin(phase);
  return float3(-wave.direction.x * wa * c,
                1.0 - wave.steepness * wa * s,
                -wave.direction.y * wa * c);
}

float3 normal = float3(0, 1, 0);
for (int i = 0; i < kWaveCount; ++i) {
  float3 n = GerstnerNormal(position, waves[i], time);
  normal += float3(n.x, n.y - 1.0, n.z);
}
normal = normalize(normal);
```

| 点 | 説明 |
| --- | --- |
| **解析的な法線** | **頂点を動かした後の正しい法線**。**メッシュの三角形から再計算しない** |
| **ピクセル シェーダーで計算** | **頂点の法線を補間**するより、**ピクセル ごとに計算**すると**滑らか**（**頂点が粗くても波の凹凸が出る**） |
| **`y` 成分** | **水平を向く基準が `1`**。**各波で、1 からのずれを足す** |

**数値微分**（隣の点との高さの差）でも**法線は求められます**が、**解析式のほうが安く正確**です。

## 細かい凹凸：法線マップの重ね

**メッシュの頂点密度は限られる**ので、<strong>細かい波（さざ波）</strong>は、**法線マップ**で**表現**します。**2 枚以上の法線マップを、違う向き・速さで流して重ねる**と**周期性が目立たず、動きが生まれます**。

```hlsl
float2 uv1 = world_position.xz * 0.05 + time * float2(0.03, 0.01);
float2 uv2 = world_position.xz * 0.11 - time * float2(0.02, 0.04);
float3 n1 = normal_map.Sample(linear_wrap, uv1).xyz * 2.0 - 1.0;
float3 n2 = normal_map.Sample(linear_wrap, uv2).xyz * 2.0 - 1.0;
float3 detail = normalize(float3(n1.xy + n2.xy, n1.z * n2.z));
float3 final_normal = normalize(float3(wave_normal.xz + detail.xy * detail_strength, wave_normal.y).xzy);
```

| 点 | 説明 |
| --- | --- |
| **UV の拡大率を変える** | **大きさの違う 2 層**（**スケールが異なる**ので**繰り返しが見えない**） |
| **逆向きに流す** | **互いに違う方向へ動く**ので、**波が複雑に見える** |
| **法線の合成** | **XY を足し、Z は掛ける**（**Whiteout・Reoriented Normal Mapping** などの正確な合成法もある） |
| **ワールド座標の UV** | **カメラが動いても波が水面に貼りつく** |

## 波の動かし方の工夫

| 工夫 | 内容 |
| --- | --- |
| **距離で波の本数を減らす** | **遠くは細かい波を省略**（**LOD**）。**ちらつきの防止** |
| **風向き・強さのパラメータ** | **風の向きで波の向き**を**風の強さで振幅・波長**を**変える** |
| **波長から速さを決める** | **深い水の波は`速さ = √(g·λ / 2π)`**（**長い波ほど速い**）。**自然な分散** |
| **ランダム化** | **波ごとの向きを基準の向きの周りでばらす** |

<div class="formula">波の速さ c = √( g · λ / (2π) )　（g = 9.8 m/s²、λ = 波長）</div>

## FFT 海面

**FFT 海面**（Tessendorf、2001）は、**海の波を「周波数ごとの成分の重ね合わせ」として、統計的に生成**します。**非常にリアルな海**が作れるので、**映画や、AAA ゲームの海**に使われます。

| 手順 | 内容 |
| --- | --- |
| **① スペクトルの作成** | **風速・風向き・海の広さ**から、**波の周波数ごとの振幅**（**Phillips スペクトルなど**）を、**初期状態**として作る |
| **② 時間発展** | **各周波数成分の位相を時間で回す**（**分散関係**：<strong>ω = √(g·k)</strong>） |
| **③ 逆 FFT** | **周波数空間から、空間（高さ）のマップ**に**変換**（**GPU のコンピュート シェーダー**） |
| **④ 変位・法線・フォーム** | <strong>高さ・水平変位・法線・波の折れ（ヤコビアン）</strong> を**テクスチャ**に出す |
| **⑤ 水面メッシュで読む** | **頂点シェーダーで高さマップを読んでメッシュを動かす** |

| 利点 | 欠点 |
| --- | --- |
| **非常にリアル**（自然な、無限に近い多様性） | **コンピュート シェーダーと、複数のテクスチャ**が必要（**実装が複雑**） |
| **周期的だが複数のスケールを重ねて目立たなくできる** | **正方形のタイルが繰り返される**（**タイリング対策**が必要） |
| **波の折れ（フォーム）の位置も得られる** | **ゲームプレイとの連携**（**物を浮かせる**）は、**同じ計算を CPU 側でも**行うか、**読み戻す** |

**ヤコビアン**（**水平変位の面積の変化**）が**小さい（負）所は波が折れている**ので**フォーム（泡）を出す目印**になります（[岸辺と泡](shore-foam.md)）。

## 物を水に浮かせる

**ボートや浮き**を**波に合わせて動かす**には、**CPU 側でも同じ波の高さを計算**する必要があります。

| 方法 | 内容 |
| --- | --- |
| **同じ式を、CPU で計算** | **Gerstner 波**なら、**シェーダーと同じ式を C++ で実装**。**複数点をサンプルして、傾き・高さを決める** |
| **GPU から読み戻す** | **FFT の高さマップを、読み戻して**サンプル（**数フレーム遅れ**） |
| **簡易な近似** | **大きな波だけ**を CPU で計算し、**細かい波は無視** |

<strong>浮力（アルキメデスの原理）</strong>で、**水に浸かった体積に応じた力**を**与える**と、**物理的に浮く**動きになります。

## よくあるミス

??? failure "Gerstner 波の steepness の合計が 1 を超えて、メッシュがねじれる"
    **合計が 1 を超えない**ように**抑える**（波の本数で割る）。

??? failure "水面をワールド固定にして、カメラが遠ざかると端が見える"
    **水面メッシュをカメラと一緒に動かし**、**波の計算はワールド座標**で行う。

??? failure "法線を、頂点の補間だけで済ませて、波の凹凸がのっぺりする"
    **ピクセル シェーダーで、解析的な法線 ＋ 細かい法線マップ**を計算する。

??? failure "法線マップを 1 枚だけ流して、繰り返しが目立つ"
    **スケールと向きの違う 2 枚以上**を**重ねる**。

??? failure "遠くの細かい波が、ちらつく"
    **距離で細かい波・法線マップの強さをフェードアウト**する（**LOD**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波 ＝ <strong>頂点シェーダーで水面メッシュを動かす</strong>。<strong>サイン波の重ね合わせ</strong>が<strong>基本</strong>
    - [x] <strong>Gerstner 波</strong>は<strong>粒子の円運動</strong>で<strong>波頂が尖る</strong>。<strong>steepness の合計は 1 以下</strong>
    - [x] <strong>法線は解析的に</strong>求め、<strong>細かい凹凸は法線マップを 2 枚以上重ねて流す</strong>
    - [x] <strong>FFT 海面</strong>は<strong>周波数スペクトル → 逆 FFT</strong>。<strong>最もリアル・重い</strong>。<strong>ヤコビアンで波の折れ（泡）</strong>が分かる
    - [x] <strong>浮かせる物</strong>は、<strong>CPU でも同じ波を計算</strong>する

## 参考

- Finch, "Effective Water Simulation from Physical Models"（GPU Gems、Gerstner 波）
- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001、FFT 海面）
- Fiorini et al., "Crest: Ocean System"（Unity のオープン ソース）

## 関連ページ

- [水](index.md)
- [水のシェーディング](shading.md)
- [岸辺と泡](shore-foam.md)
- [地形のメッシュ](../terrain/index.md)
