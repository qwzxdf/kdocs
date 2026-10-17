---
title: 地形の生成
tags:
  - 描画
---

# 地形の生成

**地形を手で全部作るのは大変**です。**ノイズから山や谷の基本形を作り、侵食で自然な形に仕上げる**のが**手続き的な地形生成**の**基本**です。このページでは、**ノイズ（値ノイズ・勾配ノイズ）・fBm（ノイズの重ね合わせ）・リッジ ノイズ・ドメイン ワーピング・水による侵食・川の作り方・生成と手作業の組み合わせ**を説明します。

!!! tip "ポイント"
    - 地形の形 ＝ <strong>ノイズを、周波数を倍々にしながら重ねる</strong>（<strong>fBm</strong>）。<strong>大きな起伏 ＋ 小さな起伏</strong>。
    - <strong>ノイズは「滑らかな乱数」</strong>。<strong>格子点にランダム値を置き、間を補間する</strong>。
    - <strong>リッジ ノイズ</strong>：<strong>絶対値を反転</strong>して、<strong>尾根（とがった山脈）</strong>を作る。
    - <strong>ドメイン ワーピング</strong>：<strong>座標をノイズでゆがめて</strong>から、<strong>ノイズを引く</strong>。<strong>自然で有機的な形</strong>。
    - <strong>侵食</strong>：<strong>水の流れで削って運んで積もらせる</strong>。<strong>谷・尾根・扇状地ができ、一気にリアル</strong>になる。
    - <strong>シード</strong>を<strong>固定</strong>すれば<strong>再現できる</strong>。

## ノイズとは

**ノイズ関数**は**位置を入れると滑らかに変化するランダムな値を返す**関数です。**同じ位置はいつも同じ値**（**決定的**）で、**近い位置は近い値**になります。

| ノイズ | 内容 |
| --- | --- |
| <strong>値ノイズ（Value noise）</strong> | **格子点にランダムな値**を置き、**間を補間**。**簡単だが格子の向きが目立つ** |
| <strong>勾配ノイズ（Perlin / Simplex）</strong> | <strong>格子点にランダムな勾配（向き）</strong>を置き、**その内積を補間**。**自然で滑らか** |
| <strong>ワーリー ノイズ（Worley / セル）</strong> | **ランダムな点からの距離**。**石・細胞・ひび割れのような模様** |

### 値ノイズ

**2D の値ノイズ**は、**位置の整数部が属する格子の 4 隅の値を、小数部で補間**します。

```hlsl
float Hash(int2 p) {
  uint h = uint(p.x) * 374761393u + uint(p.y) * 668265263u;
  h = (h ^ (h >> 13)) * 1274126177u;
  return float(h ^ (h >> 16)) / 4294967295.0;
}

float ValueNoise(float2 p) {
  int2 cell = int2(floor(p));
  float2 f = frac(p);
  float2 u = f * f * (3.0 - 2.0 * f);

  float a = Hash(cell);
  float b = Hash(cell + int2(1, 0));
  float c = Hash(cell + int2(0, 1));
  float d = Hash(cell + int2(1, 1));
  return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}
```

| 点 | 説明 |
| --- | --- |
| **`f·f·(3 − 2f)`** | **smoothstep で補間の重みを滑らかに**（**格子の境で傾きが連続**） |
| **ハッシュ関数** | **整数の格子座標から、再現性のある乱数** |
| **値の範囲** | **0〜1**。**使うときは −1〜1 に直すこともある** |

### 勾配ノイズ（Perlin）

**勾配ノイズ**は<strong>各格子点にランダムな単位ベクトル（勾配）</strong>を持ち、**点から位置までのベクトルとの内積**を**補間**します。**値ノイズより、向きの偏りが少なく**、**自然な見た目**です。

```hlsl
float2 GradientAt(int2 p) {
  float angle = Hash(p) * 6.2831853;
  return float2(cos(angle), sin(angle));
}

float PerlinNoise(float2 p) {
  int2 cell = int2(floor(p));
  float2 f = frac(p);
  float2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);

  float a = dot(GradientAt(cell), f);
  float b = dot(GradientAt(cell + int2(1, 0)), f - float2(1, 0));
  float c = dot(GradientAt(cell + int2(0, 1)), f - float2(0, 1));
  float d = dot(GradientAt(cell + int2(1, 1)), f - float2(1, 1));
  return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}
```

| 点 | 説明 |
| --- | --- |
| **補間の重み** | **`6f⁵ − 15f⁴ + 10f³`**（**改良版 Perlin。2 階微分も連続**）。**法線の見た目が滑らか** |
| **値の範囲** | **おおよそ −0.7〜0.7** |
| **Simplex ノイズ** | **正方格子でなく三角格子を使い、方向の偏りと計算量が少ない** |

## fBm（フラクショナル ブラウン運動）

**自然の地形は大きな山、小さな丘、岩、砂粒とどの縮尺でも起伏があります**（**自己相似**）。**ノイズを周波数を上げ、振幅を下げながら足し合わせる**と、**この性質を再現できます**。

<div class="formula">fBm(p) = Σ  gain^i · noise( p · lacunarity^i )　（i = 0 … オクターブ数 − 1）</div>

| パラメータ | 意味 |
| --- | --- |
| **オクターブ数** | **重ねる層の数**（普通 4〜8）。**多いほど細かい起伏** |
| <strong>lacunarity（周波数の倍率）</strong> | **層ごとに周波数を何倍にするか**（**通常 2.0**） |
| <strong>gain（振幅の倍率）</strong> | **層ごとに振幅を何倍にするか**（**通常 0.5**）。**小さいと滑らか、大きいとギザギザ** |

```hlsl
float Fbm(float2 p, int octaves, float lacunarity, float gain) {
  float sum = 0.0;
  float amplitude = 1.0;
  float max_amplitude = 0.0;
  for (int i = 0; i < octaves; ++i) {
    sum += amplitude * PerlinNoise(p);
    max_amplitude += amplitude;
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum / max_amplitude;
}
```

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="fBm">
<text x="20" y="24" class="fig-title">fBm：周波数を上げ、振幅を下げた層を足す</text>
<polyline fill="none" stroke="#4c8bf5" stroke-width="2" points="40,60 120,45 200,70 280,55 360,60 440,48 520,66 600,52 680,58 740,50"/>
<text x="40" y="38" style="font-size:12px">1 層目：大きな起伏</text>
<polyline fill="none" stroke="#2ea043" stroke-width="2" points="40,125 70,120 100,130 130,118 160,128 190,121 220,131 250,119 280,127 310,120 340,130 370,122 400,128 430,120 460,131 490,119 520,127 550,121 580,130 610,120 640,128 670,121 700,129 740,123"/>
<text x="40" y="106" style="font-size:12px">2 層目：細かく、小さい</text>
<polyline fill="none" stroke="currentColor" stroke-width="3" points="40,205 70,188 100,214 130,190 160,208 190,185 220,215 250,188 280,206 310,186 340,214 370,190 400,205 430,184 460,214 490,189 520,208 550,186 580,213 610,189 640,206 670,187 700,212 740,190"/>
<text x="40" y="170" style="font-size:12px">合計：大きな起伏の上に細かい起伏</text>
</svg>

| 点 | 説明 |
| --- | --- |
| **`max_amplitude` で割る** | **値の範囲を揃える**（0〜1 などに） |
| **層ごとに位置をずらす** | **各層で座標をずらす**と**格子の揃いが目立たない** |
| **高さの調整** | **fBm の結果にカーブ（べき乗など）を掛けて、平地と山の比率を調整** |

## リッジ ノイズ

**山脈の尾根**を作るには、**ノイズの絶対値を取って反転**します。**ゼロ付近が鋭い尾根**になります。

```hlsl
float RidgedFbm(float2 p, int octaves, float lacunarity, float gain) {
  float sum = 0.0;
  float amplitude = 0.5;
  float weight = 1.0;
  for (int i = 0; i < octaves; ++i) {
    float n = 1.0 - abs(PerlinNoise(p));
    n *= n;
    n *= weight;
    weight = saturate(n * 2.0);
    sum += n * amplitude;
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum;
}
```

| 点 | 説明 |
| --- | --- |
| **`1 − abs(noise)`** | **0 付近の線が尾根**になる |
| **`n *= n`** | **尾根を鋭くする** |
| **`weight`** | **低い所では細かい起伏を弱める**（**谷を滑らかに尾根をごつごつ**） |
| **使い分け** | **山地はリッジ、平原は通常の fBm**。**ノイズでブレンド** |

## ドメイン ワーピング

**ノイズの入力座標を別のノイズでゆがめる**と、**自然に曲がりくねった形**になります。

```hlsl
float WarpedFbm(float2 p) {
  float2 q = float2(Fbm(p, 4, 2.0, 0.5), Fbm(p + float2(5.2, 1.3), 4, 2.0, 0.5));
  float2 r = float2(Fbm(p + 4.0 * q + float2(1.7, 9.2), 4, 2.0, 0.5),
                    Fbm(p + 4.0 * q + float2(8.3, 2.8), 4, 2.0, 0.5));
  return Fbm(p + 4.0 * r, 4, 2.0, 0.5);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>ワープの強さ（4.0）</strong> | **大きいと渦のようにねじれる** |
| **層を重ねる** | **q → r → 最終**と**2 段**で**複雑に** |
| **コスト** | **fBm を何度も呼ぶ**ので**重い**。**生成時（ベイク）に使い、実行時には焼いたテクスチャを読む** |

## 地形の高さへの変換

**ノイズ値をそのまま高さにするのではなく、形を整えます**。

| 工夫 | 内容 |
| --- | --- |
| **べき乗** | **`pow(h, 2.0)`** で**平地を広く、山を急に** |
| **大陸の形** | **低周波のノイズで陸と海の分布**を作り、**山のノイズを陸にだけ掛ける** |
| <strong>高さの段差（テラス）</strong> | **`floor` で段にし、少し滑らかに** |
| **島の形** | **中心から離れるほど、高さを下げる**（**円のマスク**） |
| **バイオーム** | **高さ・湿度（別のノイズ）で、地面の種類を決める** |

## 侵食

**ノイズだけの地形は、「ふにゃふにゃ」して不自然**です。**本物の山は水の流れが削った谷と尾根の網目**があります。**水による侵食を模擬**すると**劇的にリアル**になります。

| 方式 | 内容 |
| --- | --- |
| <strong>熱侵食（Thermal）</strong> | **急すぎる斜面の土が崩れて下に積もる**（**安息角**）。**崖が緩やかな斜面と裾野になる** |
| <strong>水力侵食（Hydraulic）</strong> | **雨が降り、流れて、削り、運び、堆積**。**谷・尾根・扇状地ができる** |
| **粒子ベース** | **水滴を 1 つずつ、地形の上で転がす**。**簡単** |
| <strong>格子ベース（パイプ モデル）</strong> | **水の量・流れ・土砂を格子で計算**。**GPU 向き** |

### 粒子ベースの水力侵食

**水滴をランダムな位置に落とし**、**高さの勾配に沿って転がします**。**勢い（速さ）と水量で運べる土砂の量が決まり**、**多すぎれば堆積、少なければ削ります**。

```cpp
void ErodeDroplet(HeightMap& map, std::mt19937& rng, const ErosionParams& p) {
  float x = RandomRange(rng, 1.0f, map.width - 2.0f);
  float y = RandomRange(rng, 1.0f, map.height - 2.0f);
  float dir_x = 0.0f;
  float dir_y = 0.0f;
  float speed = p.initial_speed;
  float water = p.initial_water;
  float sediment = 0.0f;

  for (int step = 0; step < p.max_lifetime; ++step) {
    int ix = static_cast<int>(x);
    int iy = static_cast<int>(y);
    glm::vec2 gradient = map.GradientAt(x, y);
    float old_height = map.HeightAt(x, y);

    dir_x = dir_x * p.inertia - gradient.x * (1.0f - p.inertia);
    dir_y = dir_y * p.inertia - gradient.y * (1.0f - p.inertia);
    float length = std::sqrt(dir_x * dir_x + dir_y * dir_y);
    if (length < 1e-6f) break;
    dir_x /= length;
    dir_y /= length;

    x += dir_x;
    y += dir_y;
    if (x < 1 || x >= map.width - 2 || y < 1 || y >= map.height - 2) break;

    float new_height = map.HeightAt(x, y);
    float delta = new_height - old_height;

    float capacity = std::max(-delta * speed * water * p.capacity_factor, p.min_capacity);
    if (sediment > capacity || delta > 0.0f) {
      float deposit = delta > 0.0f ? std::min(delta, sediment)
                                   : (sediment - capacity) * p.deposit_rate;
      sediment -= deposit;
      map.Deposit(ix, iy, deposit);
    } else {
      float erode = std::min((capacity - sediment) * p.erode_rate, -delta);
      sediment += erode;
      map.Erode(ix, iy, erode);
    }

    speed = std::sqrt(std::max(speed * speed + delta * p.gravity, 0.0f));
    water *= 1.0f - p.evaporation;
  }
}
```

| パラメータ | 意味 |
| --- | --- |
| **inertia** | **慣性**。**大きいと真っ直ぐ、小さいと勾配に忠実** |
| **capacity_factor** | **水が運べる土砂の量の係数** |
| **erode_rate / deposit_rate** | **削る・積もらせる速さ** |
| **evaporation** | **蒸発**。**水が減ると運べる量が減る** |
| **max_lifetime** | **水滴が転がる最大の歩数**（30 程度） |
| **水滴の数** | **十万〜数百万**。**多いほど、谷がはっきり** |

**削った・積もらせた量は、周囲のセルに重みを付けて配る**（**半径 3 程度のブラシ**）と、**滑らかな谷**になります。

### 結果

| 変化 | 内容 |
| --- | --- |
| **谷の網目** | **水が集まる所に深い谷**ができ、**支流が合流する** |
| **尾根の鋭さ** | **谷に挟まれた尾根が鋭くなる** |
| **扇状地・堆積** | **谷の出口に土砂が平らに積もる** |
| **地面の種類のヒント** | **堆積した所は土、削れた所は岩**（**スプラット マップに使える**） |

## 川と湖

**侵食の結果から、川を取り出せます**。

| 方法 | 内容 |
| --- | --- |
| **流量マップ** | **各セルについて、上流から集まる水量を数える**（**高い所から低い所へ累積**）。**水量が多い所が川** |
| **スプライン化** | **川の経路を折れ線／スプラインに抽出**し、**水面メッシュを沿わせる** |
| **窪地の処理** | **行き止まり（窪み）は、湖にするか、堤を越えて流す** |
| **幅と深さ** | **水量に比例**して**川幅を広げる** |

**川の水面**は、[水](../water/index.md)の**フローマップ**（[水面のインタラクション](../water/interaction.md)）で**流れを表現**します。

## 生成のタイミング

| 方式 | 内容 |
| --- | --- |
| <strong>事前に作って焼く（オフライン）</strong> | **地形ツール**（World Machine・Gaea・Houdini）や**自作ツール**で**高さマップを生成**。**ゲームにはテクスチャとして出荷**。**品質が高い** |
| **ランタイム生成** | **ゲーム中にシードから生成**。**ノイズ関数は軽いのでチャンクごとに GPU／CPU で生成**。**無限の世界・ランダム ステージ向き** |
| **ハイブリッド** | **大きな形は手で描き、細かい起伏だけ、ノイズで足す** |

**ランタイム生成**では、**チャンクの境界で値が連続する**こと（**ワールド座標でノイズを引く**）、**侵食は隣のチャンクにも影響する**ため**難しい**ことに**注意**します。

## 配置の生成

**地形の上に何を置くかも、手続き的に決められます**。

| 要素 | 内容 |
| --- | --- |
| **植生** | **高さ・傾き・湿度・ノイズから密度を決める**（[草と木](vegetation.md)） |
| **岩** | **傾きが急な所／侵食で削れた所** |
| **道** | **2 点間の最小コスト経路（A\*）<strong>。</strong>傾きが緩い所を通る** |
| **集落** | **平らで水に近い所** |
| **ポアソン円盤サンプリング** | **点が近づきすぎない、自然な散らばり** |

## よくあるミス

??? failure "ノイズが格子状に見える"
    **値ノイズの格子の向きが目立つ**。**勾配ノイズに変える**か、**層ごとに回転・ずらす**。

??? failure "地形がのっぺりして、山に迫力がない"
    **オクターブを増やし、リッジ ノイズ・侵食を使う**。

??? failure "チャンクの境目で、段差ができる"
    **ノイズはチャンクのローカル座標でなく、ワールド座標で引く**。

??? failure "侵食の結果が、スパイク（針状）になる"
    **削る量に上限を付け**、**ブラシで周囲に配る**。**水滴の慣性を上げる**。

??? failure "実行ごとに地形が違って、再現できない"
    **シードを固定**し、**乱数の呼び出し順を揃える**（**並列生成はチャンクごとにシードを派生**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 地形の形 ＝ <strong>fBm</strong>（<strong>周波数を倍々・振幅を半分ずつ</strong>）。<strong>勾配ノイズが自然</strong>
    - [x] <strong>尾根はリッジ ノイズ</strong>、<strong>有機的な形はドメイン ワーピング</strong>
    - [x] <strong>侵食</strong>（<strong>水滴の転がり</strong>）で<strong>谷と尾根の網目</strong>ができ、<strong>リアル</strong>に
    - [x] <strong>侵食の結果</strong>は<strong>地面のテクスチャや川</strong>にも<strong>使える</strong>
    - [x] <strong>ノイズはワールド座標で引く</strong>。<strong>シードを固定</strong>する

## 参考

- Perlin, "An Image Synthesizer"（SIGGRAPH 1985）、"Improving Noise"（SIGGRAPH 2002）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）
- Lague, "Hydraulic Erosion"（粒子ベース侵食の実装解説）
- Quilez, "Domain Warping" ・ "fBm"（iquilezles.org）

## 関連ページ

- [地形](index.md)
- [高さマップとメッシュ](heightmap-mesh.md)
- [地形のテクスチャ](texturing.md)
- [草と木](vegetation.md)
- [水](../water/index.md)
