---
title: 岸辺と泡（フォーム）
tags:
  - 描画
---

# 岸辺と泡（フォーム）

<strong>水面の「白い泡」</strong>を、**どこに・どう出すか**です。**泡が出る場所は、大きく 3 つ**あります。**岸辺や水中の物の周り**（深度が浅い所）、**波頂**（波が折れる所）、**物がぶつかった跡**（航跡）です。このページでは、**深度差による岸辺の泡・ヤコビアンによる波頂の泡・泡テクスチャの動かし方・泡の合成**を説明します。

!!! tip "ポイント"
    - 泡 ＝ <strong>水面に足す白いマスク</strong>（0〜1）。<strong>マスクを作って、テクスチャで模様を付け、色に足す</strong>。
    - <strong>岸辺の泡</strong>：<strong>水深（水面と底の深度差）が浅いほど、泡が強い</strong>。
    - <strong>波頂の泡</strong>：<strong>ヤコビアンが小さい（負に近い）所</strong>＝<strong>波が折れる所</strong>。
    - <strong>泡テクスチャ</strong>は<strong>ノイズ状の模様</strong>。<strong>時間でスクロール</strong>させ、<strong>マスクで切り抜く</strong>。
    - <strong>泡は残る</strong>：<strong>出た泡はすぐには消えない</strong>。<strong>履歴（前のフレームの泡）を持つ</strong>と自然。
    - <strong>泡はアルベドを白く、粗さを高く</strong>（光沢を消す）。

## 泡のマスクを作る

**泡は、「0 なら泡なし、1 なら泡で真っ白」のマスク値**として扱います。**複数の原因（岸辺・波頂・航跡）のマスクを足し合わせ**、**最後にテクスチャで模様を付けます**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="泡のマスク">
<text x="20" y="24" class="fig-title">泡のマスク：原因ごとに作って、足して、模様を付ける</text>
<rect x="30" y="60" width="150" height="56" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/>
<text x="105" y="84" text-anchor="middle" style="font-size:13px">岸辺</text><text x="105" y="102" text-anchor="middle" style="font-size:11px">深度差が浅い</text>
<rect x="30" y="130" width="150" height="56" rx="6" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/>
<text x="105" y="154" text-anchor="middle" style="font-size:13px">波頂</text><text x="105" y="172" text-anchor="middle" style="font-size:11px">ヤコビアンが小さい</text>
<rect x="30" y="200" width="150" height="30" rx="6" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="105" y="220" text-anchor="middle" style="font-size:13px">航跡・衝突</text>
<line x1="180" y1="88" x2="290" y2="130" stroke="currentColor" stroke-opacity="0.6"/>
<line x1="180" y1="158" x2="290" y2="140" stroke="currentColor" stroke-opacity="0.6"/>
<line x1="180" y1="215" x2="290" y2="150" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="290" y="105" width="130" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="355" y="130" text-anchor="middle" style="font-size:13px">足して</text><text x="355" y="150" text-anchor="middle" style="font-size:13px">saturate</text>
<line x1="420" y1="135" x2="480" y2="135" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="480" y="105" width="130" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="545" y="130" text-anchor="middle" style="font-size:13px">泡テクスチャで</text><text x="545" y="150" text-anchor="middle" style="font-size:13px">模様を付ける</text>
<line x1="610" y1="135" x2="660" y2="135" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="660" y="105" width="90" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="705" y="140" text-anchor="middle" style="font-size:13px">色に足す</text>
</svg>

## 岸辺の泡：深度差

**水面と底の深度の差が小さい所は、水が浅い所**＝**岸辺や水中の物の周り**です。**浅いほど泡が強くなるマスク**を作ります。

```hlsl
float scene_depth = LinearizeDepth(depth_texture.Sample(point_clamp, screen_uv).r);
float surface_depth = LinearizeDepth(input.position.z);
float water_depth = max(scene_depth - surface_depth, 0.0);

float shore_mask = 1.0 - saturate(water_depth / foam_distance);
shore_mask = pow(shore_mask, foam_sharpness);
```

| 点 | 説明 |
| --- | --- |
| **`foam_distance`** | **泡が出る水深の範囲**（例：0.5 m）。**これより深いと 0** |
| **`pow(..., sharpness)`** | **端の鋭さ**。**大きいと岸のすぐそばだけ** |
| **水中の物にも出る** | **岩・杭・船の周りにも泡の輪**ができる（**深度差で自動的に**） |

### 波打ち際の動き

**岸辺の泡は波が寄せては引くように動く**と**自然**です。**水深に時間で揺れる値を足す**と**波打ち際が動きます**。

```hlsl
float wave = sin(time * 1.5 + input.world_position.x * 0.3) * 0.5 + 0.5;
float animated_depth = water_depth + wave * 0.3;
float shore_mask = 1.0 - saturate(animated_depth / foam_distance);
```

**波が寄せる位相と引く位相で泡の線が前後します**。**位置（`world_position.x`）で位相をずらす**と**波が一斉に動かず、ばらけます**。

## 波頂の泡：ヤコビアン

**波が尖りすぎると頂が折れて砕けます**。**折れる所は水平変位の面積が潰れる所**で、<strong>ヤコビアン（変位の面積比）</strong>で**検出できます**。

<strong>水面の位置を `P = P₀ + D(P₀)`（`D` は水平変位）</strong>とすると**面積の変化率**は**次の行列式**です。

<div class="formula">J = (1 + ∂Dx/∂x)(1 + ∂Dz/∂z) − (∂Dx/∂z)(∂Dz/∂x)</div>

| 値 | 意味 |
| --- | --- |
| **J = 1** | **面積が変わらない**（平らな水面） |
| **J > 1** | **広がっている**（谷） |
| **J < 1** | **縮んでいる**（波頂に向かって粒子が集まる） |
| **J ≤ 0** | **折れている**（粒子が追い越した）。**泡が出る** |

**Gerstner 波なら、解析的に求まります**。

```hlsl
float3 GerstnerJacobian(float2 position, GerstnerWave wave, float time) {
  float k = 2.0 * 3.14159265 / wave.wavelength;
  float phase = k * dot(wave.direction, position) + time * wave.speed * k;
  float s = sin(phase) * wave.steepness;
  return float3(wave.direction.x * wave.direction.x * s,
                wave.direction.y * wave.direction.y * s,
                wave.direction.x * wave.direction.y * s);
}

float jacobian = 1.0;
float3 sum = float3(0, 0, 0);
for (int i = 0; i < kWaveCount; ++i) {
  sum += GerstnerJacobian(position, waves[i], time);
}
jacobian = (1.0 - sum.x) * (1.0 - sum.y) - sum.z * sum.z;

float crest_mask = saturate((foam_threshold - jacobian) / foam_softness);
```

| 点 | 説明 |
| --- | --- |
| **`foam_threshold`** | **この値より J が小さいと、泡**（例：0.7）。**1 より小さい値** |
| **`foam_softness`** | **泡が立ち上がる幅**（例：0.3） |
| **FFT 海面** | **ヤコビアンを変位マップから計算してテクスチャに出す**（[波のジオメトリ](waves.md)） |

**FFT では水平変位マップの差分**から**ヤコビアンを求め**、**別のテクスチャに書き出す**のが**定番**です。

## 泡テクスチャ

**マスクだけでは、べったりした白**になります。**泡の模様（粒の集まり）のテクスチャ**を**乗せます**。

```hlsl
float2 foam_uv1 = input.world_position.xz * 0.2 + time * float2(0.02, 0.01);
float2 foam_uv2 = input.world_position.xz * 0.47 - time * float2(0.015, 0.03);
float foam_pattern = foam_texture.Sample(linear_wrap, foam_uv1).r
                   * foam_texture.Sample(linear_wrap, foam_uv2).r;

float foam = saturate(mask * 2.0 - (1.0 - foam_pattern * 2.0));
```

| 点 | 説明 |
| --- | --- |
| **2 枚を掛ける** | **スケールの違う 2 枚を掛けて、繰り返しを隠す** |
| **`mask * 2 − (1 − pattern)`** | **マスクが強いほど、模様の隙間まで埋まる<strong>（</strong>マスクが弱いと模様の濃い所だけ残る<strong>）。</strong>端が自然に崩れる** |
| **ワールド座標の UV** | **水面が動いても泡が水面に貼りつく** |
| **ゆっくり流す** | **泡は水の流れに乗る** |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="マスクと模様の合成">
<text x="20" y="24" class="fig-title">マスクの強さで、模様の見え方が変わる</text>
<defs>
<pattern id="foamdots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="3" fill="#ffffff"/><circle cx="11" cy="9" r="2" fill="#ffffff"/></pattern>
</defs>
<rect x="40" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="290" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="540" y="50" width="200" height="120" fill="#4c8bf5" fill-opacity="0.35"/>
<rect x="40" y="50" width="200" height="120" fill="url(#foamdots)" opacity="0.18"/>
<rect x="290" y="50" width="200" height="120" fill="url(#foamdots)" opacity="0.6"/>
<rect x="540" y="50" width="200" height="120" fill="#ffffff" opacity="0.9"/>
<text x="140" y="190" text-anchor="middle" style="font-size:12px">マスク弱：模様の濃い所だけ</text>
<text x="390" y="190" text-anchor="middle" style="font-size:12px">マスク中：まだら</text>
<text x="640" y="190" text-anchor="middle" style="font-size:12px">マスク強：ほぼ真っ白</text>
</svg>

## 泡を残す（履歴）

**実際の泡はできてから、しばらく水面に残って、ゆっくり消えます**。**ヤコビアンの泡は、波が折れた瞬間にしか出ない**ので、**そのままだと一瞬光って消えて見えます**。

| 方法 | 内容 |
| --- | --- |
| **泡の履歴テクスチャ** | **前のフレームの泡を持ち**、**今のマスクと `max` を取り**、**毎フレーム少し減衰**させる |
| **水の流れに乗せる** | **履歴を読む UV を流れの向きにずらす**（泡が流れる） |
| **カメラ追従** | **履歴テクスチャは、カメラ周りのワールド領域**に**対応させ**、**カメラが動いたらスクロール** |

```hlsl
float previous = foam_history.Sample(linear_clamp, history_uv).r;
float decayed = previous * exp(-decay_rate * delta_time);
float foam_now = max(decayed, crest_mask);
```

| 点 | 説明 |
| --- | --- |
| **`exp(−rate · dt)`** | **フレームレートに依らない減衰** |
| **`max`** | **新しい泡が出たら、そこは新しい値** |
| **複数のマスクをまとめて書く** | **岸辺・波頂・航跡を、1 枚の履歴に集める**と**扱いやすい** |

## 泡の合成

**泡は水面の色の上に白く乗せます**。**泡の部分は水中が見えず（不透明）、光沢も無く**なります。

```hlsl
float3 foam_color = float3(0.95, 0.97, 1.0) * (ambient + diffuse_light);
float3 color = lerp(water_color, foam_color, foam);

float roughness = lerp(water_roughness, 0.9, foam);
float transparency = 1.0 - foam;
```

| 点 | 説明 |
| --- | --- |
| **泡の色** | **白だが光に照らされた色**（**暗い所で光らない**ように、**ライティングを掛ける**） |
| **粗さを上げる** | **泡は荒れた面**。**水の鋭いスペキュラを消す** |
| **屈折を弱める** | **泡の下は見えない**。**水中の色（屈折）の寄与を減らす** |

## 航跡と衝突

**船や泳ぐキャラクターの後ろ**には**泡の筋**が**残ります**。

| 方法 | 内容 |
| --- | --- |
| **ブラシで泡の履歴に描く** | **物の位置に丸い点を描き込む**（[波紋と水面のインタラクション](interaction.md)） |
| **パーティクル** | **しぶきをパーティクルで出す** |
| **水中の物の深度** | **岸辺と同じ深度差で杭の周りに自動で輪が出る** |

## よくあるミス

??? failure "泡が、すべて同じ白さでのっぺりする"
    **マスクだけで色を決めず、テクスチャの模様でマスクを崩す**。

??? failure "泡が一瞬で消えて、ちらつく"
    **履歴テクスチャに溜めて、ゆっくり減衰させる**。

??? failure "泡が、夜でも光って見える"
    **泡の色にライティングを掛ける**。

??? failure "岸辺の泡が、画面の端で消える"
    **深度の読み取りが画面外になる**。**画面外はマスクを 0 にするか、別の方法**（高さマップ）を使う。

??? failure "泡の下の水中が、透けて見える"
    **泡が強いほど、屈折の色を減らす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 泡 ＝ <strong>マスク（0〜1）× 泡テクスチャ</strong>。<strong>白く、粗く、不透明に</strong>
    - [x] <strong>岸辺</strong>は<strong>水面と底の深度差が浅い所</strong>。<strong>岩や杭の周りにも自動で出る</strong>
    - [x] <strong>波頂</strong>は<strong>ヤコビアンが 1 より小さい（折れる）所</strong>
    - [x] <strong>履歴テクスチャ</strong>に溜めて<strong>ゆっくり消す</strong>と<strong>自然</strong>
    - [x] <strong>泡の色にもライティング</strong>を掛ける

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Jensen & Golias, "Deep-Water Animation and Rendering"（Gamasutra 2001）
- Fiorini et al., "Crest: Ocean System"（Unity のオープン ソース）

## 関連ページ

- [水](index.md)
- [波のジオメトリ](waves.md)
- [水のシェーディング](shading.md)
- [波紋と水面のインタラクション](interaction.md)
