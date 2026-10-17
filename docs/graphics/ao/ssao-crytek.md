---
title: Crytek SSAO
tags:
  - 描画
---

# Crytek SSAO

**SSAO**（Screen-Space Ambient Occlusion）は、2007 年に Crytek が『Crysis』のエンジン（CryEngine 2）で実用化した、**画面の深度バッファだけで AO を近似する**方式です。それまでの AO は、モデルに焼き込むか、事前計算するものでした。**毎フレーム、ポストプロセスとして、動くシーンにも使える AO**を、初めて現実的なコストで出したのが、この方式です。以降のスクリーン空間 AO は、すべてこの発想の延長にあります。

このページでは、**原型である Crytek 方式**を、仕組みから順に説明します。深度バッファから位置を復元する方法、サンプルの取り方、そして**この方式の弱点**（平らな面が灰色になる）まで扱います。

!!! tip "ポイント"
    - 入力は<strong>深度バッファだけ</strong>（法線は不要）。<strong>ポストプロセス</strong>で全画面に 1 パス。
    - 各画素で<strong>周囲の球の中にランダムなサンプル点</strong>を置く。<strong>サンプル点を画面に投影</strong>して、<strong>その画素の深度と比べ</strong>、<strong>面の奥にあれば「遮られている」</strong>と数える。
    - AO ＝ <strong>遮られていないサンプルの割合</strong>。
    - <strong>球</strong>を使うので<strong>平らな面でも約半分が「遮られる」</strong>。<strong>面全体が灰色</strong>になるのが弱点（次の[半球 SSAO](ssao-hemisphere.md) で解決）。
    - サンプル数が少ない（16 程度）ので<strong>画素ごとにサンプルをランダムに回転</strong>し、<strong>ぼかしで消す</strong>。

## 発想

[理論](theory/index.md)のとおり、AO は「**点 p の周りの遮られていない方向の割合**」でした。本来は**シーンにレイを飛ばして**調べます。Crytek 方式は、<strong>レイを飛ばす代わりに、「p の近くの点が物体の内側にあるか」</strong>を調べます。

<svg class="fig illust" viewBox="0 0 774 300" role="img" aria-label="Crytek SSAO のサンプル">
<text x="20" y="24" class="fig-title">p の周りの球の中のサンプル点が、面の「奥」にあれば、遮られているとみなす</text>
<path d="M60,200 L330,200 L380,140 L700,140" fill="none" stroke="currentColor" stroke-width="4"/>
<polygon points="60,200 330,200 380,140 700,140 700,270 60,270" fill="rgba(150,150,150,0.25)"/>
<circle cx="260" cy="200" r="7" fill="currentColor"/><text x="244" y="224" style="font-size:12px">p</text>
<circle cx="260" cy="200" r="70" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>
<g fill="#2ea043"><circle cx="230" cy="150" r="5"/><circle cx="290" cy="165" r="5"/><circle cx="250" cy="135" r="5"/><circle cx="215" cy="175" r="5"/></g>
<g fill="#e5484d"><circle cx="215" cy="225" r="5"/><circle cx="285" cy="235" r="5"/><circle cx="250" cy="245" r="5"/><circle cx="300" cy="180" r="5"/></g>
<text x="400" y="80" style="font-weight:700">緑：面の手前（空が見える）</text>
<text x="400" y="104" style="font-weight:700;fill:#e5484d">赤：面の奥（遮られている）</text>
<text x="400" y="134" style="font-size:12px">平らな面では、球の下半分が、全部「奥」になる</text>
<text x="400" y="154" style="font-size:12px">→ 何も遮るものが無くても、約 50% が「遮られた」と数えられる</text>
<text x="20" y="290" style="font-size:12px">この「球の下半分」の問題が、Crytek 方式の最大の弱点</text>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 深度バッファから、ビュー空間の位置を復元する** | 画素 (u, v) の深度から、その画素の 3D 位置 p（ビュー空間）を求める |
| **② 球の中にサンプル点を N 個作る** | 半径 R の球の中のランダムなベクトル（あらかじめ用意） |
| **③ 画素ごとにサンプル ベクトルをランダムに回転する** | 同じ模様が繰り返されて、縞（バンディング）が出るのを防ぐ |
| **④ サンプル点 s = p + R·ベクトル を、画面に投影する** | s が画面のどの画素に映るかを求める |
| **⑤ その画素の深度を読む** | s の位置にある、**画面から見える面の深度** |
| **⑥ 比べる** | **面の深度が、s の深度より手前**（小さい）なら、**s は面の奥にある ＝ 遮られている** |
| **⑦ 割合を出す** | `AO = 1 − (遮られた数 / N)` |

## ① 深度から位置を復元する

深度バッファの値（0〜1）から、<strong>カメラからの距離（ビュー空間の z）</strong>を求め、そこから **x・y** を逆算します。**プロジェクション行列の式を、逆に解く**だけです（[投影](../../3d/projection.md)）。

左手系・標準の Z（near → 0、far → 1）の場合、深度値 d から、ビュー空間の奥行き z は、次のとおりです。

<div class="formula">z = (near · far) / (far − d · (far − near))</div>

x・y は、**NDC 座標と視野角**から、次のように求めます。

<div class="formula">x = ndc_x · z · tan(fovY/2) · aspect　、　y = ndc_y · z · tan(fovY/2)</div>

```hlsl
float LinearizeDepth(float d) {
  return near_z * far_z / (far_z - d * (far_z - near_z));
}

float3 ViewPosition(float2 uv, float z) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  return float3(ndc * tan_half_fov * z, z);
}
```

| 変数 | 意味 |
| --- | --- |
| `tan_half_fov` | `float2(tan(fovY/2) * aspect, tan(fovY/2))` |
| `uv.y` の反転 | テクスチャの V は下向き、NDC の y は上向き |

!!! note "reverse-Z のとき"
    深度が 1 → 0 に反転している場合（[投影](../../3d/projection.md)）、`LinearizeDepth` の式が変わります。**自分の射影行列に合わせた式**を使います。

## ②③ サンプルの作り方

**球の中**に N 個（16 前後）のベクトルを用意します。**原点の近くに多く**置くと、**近い遮蔽ほど強く効く**ので、見た目が良くなります。

```cpp
std::vector<Vector3> MakeSphereKernel(int n, std::mt19937& rng) {
  std::uniform_real_distribution<float> unit(-1.0f, 1.0f);
  std::uniform_real_distribution<float> zero_one(0.0f, 1.0f);
  std::vector<Vector3> kernel;
  while (static_cast<int>(kernel.size()) < n) {
    Vector3 v(unit(rng), unit(rng), unit(rng));
    if (v.LengthSquared() > 1.0f || v.LengthSquared() < 1e-4f) continue;
    v.Normalize();
    float t = static_cast<float>(kernel.size()) / static_cast<float>(n);
    float scale = std::lerp(0.1f, 1.0f, t * t);
    kernel.push_back(v * scale * zero_one(rng));
  }
  return kernel;
}
```

| 点 | 説明 |
| --- | --- |
| **球の内側に一様** | 立方体からランダムに取り、球の外なら捨てる（棄却法）。長さは後で揃える |
| **原点に近いサンプルを多く** | `scale = lerp(0.1, 1.0, t²)` で、近いサンプルを増やす |
| **サンプル数** | 8〜16。少ないほど速いがノイズが増える |

サンプル ベクトルを**画素ごとにランダムに回転**します。**4×4 画素のランダム ベクトルのテクスチャ**（`float3`、0〜1 を −1〜1 にして使う）を、画面全体に**繰り返し貼り**ます。

```hlsl
float3 random_vec = noise_tex.Sample(wrap_sampler, uv * screen_size / 4.0).xyz * 2.0 - 1.0;
float3 ray = reflect(kernel[i].xyz, random_vec);
```

`reflect` で**ランダム ベクトルを軸にサンプルを鏡映**します。これで画素ごとにサンプルの向きが変わります。

## ④〜⑦ 判定とコード

```hlsl
float SSAO(float2 uv) {
  float z = LinearizeDepth(depth_tex.Sample(point_sampler, uv).r);
  float3 p = ViewPosition(uv, z);
  float3 random_vec = noise_tex.Sample(wrap_sampler, uv * screen_size / 4.0).xyz * 2.0 - 1.0;

  float occlusion = 0.0;
  for (int i = 0; i < kKernelSize; ++i) {
    float3 s = p + reflect(kernel[i].xyz, random_vec) * radius;

    float4 clip = mul(float4(s, 1.0), projection);
    float2 suv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;

    float scene_z = LinearizeDepth(depth_tex.SampleLevel(point_sampler, suv, 0).r);

    float range_check = saturate(radius / abs(z - scene_z));
    occlusion += (scene_z < s.z - bias ? 1.0 : 0.0) * range_check;
  }
  return 1.0 - occlusion / kKernelSize;
}
```

| 点 | 説明 |
| --- | --- |
| **`scene_z < s.z − bias`** | 画面から見える面（`scene_z`）が、サンプル点（`s.z`）より**手前**なら、s は面の奥 ＝ 遮られている |
| **`bias`** | 平らな面で自分自身を遮蔽物と判定する（**自己遮蔽**）のを防ぐ小さな値 |
| **`range_check`** | **p から遠く離れた面**（手前にある別の物）が、**p を遮っていると誤判定**するのを防ぐ。**深度の差が大きいほど、効きを弱める** |
| **`SampleLevel`** | ループの中でミップを選ぶ命令（勾配が使えないため） |
| **ポイント サンプル** | 深度は**補間せずに**読む（補間すると境界で嘘の深度ができる） |

## この方式の問題点

### 1. 平らな面が灰色になる

**球**を使うので**平らな面の上の点**でもサンプルの**約半分が面の下**に入り、「遮られた」と数えられます。何も遮るものが無いのに、**AO が 0.5 程度**になり、**全体が灰色**に見えます。

| 対処 | 説明 |
| --- | --- |
| **0.5 を差し引いて伸ばす** | `ao = saturate((ao − 0.5) × 2)` のように**平面の値を 1 に補正**する。簡易的な対処で**凸の面は補正しすぎ**になる |
| **半球に変える** | 法線を使い、**面の上側だけ**にサンプルを置く（[半球 SSAO](ssao-hemisphere.md)） |

### 2. 法線が無いので、角の向きを区別できない

法線が無いため、<strong>凸の角（外側）</strong>と<strong>凹の角（内側）</strong>を区別できません。<strong>凸の縁にも暗い輪郭（ハロー）</strong>が出やすくなります。

### 3. ハロー

**手前の物体の縁**に**背景が暗く**なる輪が出ます。深度の差が大きい境界で、**背景側の点が手前の物に遮られている**と判定されるためです。**`range_check`** で弱められますが、完全には消えません（[アーティファクト](artifacts/index.md)）。

### 4. ノイズとバンディング

サンプル数が少ないので、**ノイズ**か**縞模様**が出ます。**4×4 のランダム回転 ＋ 4×4 のぼかし**で消すのが定番ですが、**ぼかしが物体の境界をにじませる**ので、深度を考慮した**バイラテラル ブラー**が必要です（[フィルタ](filtering/index.md)）。

## 歴史的な位置づけ

| 項目 | 内容 |
| --- | --- |
| **登場** | 2007 年、CryEngine 2（『Crysis』）。SIGGRAPH 2007 の講演で公開 |
| **意義** | **事前計算なしで動的なシーンに AO** を付けられる。深度バッファだけ（G-Buffer に依存しない） |
| **後の影響** | 「深度から位置を復元し、近傍をサンプルする」発想が**以降のすべての SSAO 系**の基礎になった |
| **欠点の改善** | 半球（法線）・式の導出（Alchemy）・地平線（HBAO）・ミップ（SAO）・コサイン重み（GTAO） |

## よくあるミス

??? failure "球を使い、平らな面が灰色になる"
    法線を使って**半球**にします。または、0.5 を補正します。

??? failure "深度を線形補間して読み、境界で嘘の深度が出る"
    ポイント サンプリングで読みます。

??? failure "遠くの別の物体が、手前の面を暗くする"
    `range_check`（深度差による弱め）を入れます。

??? failure "同じランダム パターンを、全画素に使い、縞が出る"
    画素ごとにサンプルを回転します（4×4 のノイズ テクスチャ）。

??? failure "`bias` が小さすぎて、平らな面に縞が出る"
    `bias` を少し大きくします（0.01〜0.05 程度）。大きすぎると接地の暗さが消えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Crytek SSAO ＝ <strong>深度バッファだけで、球のサンプルを画面に投影し、面の奥にあれば遮られた、と数える</strong>
    - [x] <strong>深度から位置を復元</strong>（ビュー空間）。<strong>ポイント サンプリング</strong>で深度を読む
    - [x] <strong>範囲チェック</strong>と<strong>バイアス</strong>で、誤判定を減らす
    - [x] <strong>球のため、平らな面が灰色</strong>になるのが最大の弱点 → 半球にする
    - [x] <strong>ランダム回転＋ぼかし</strong>が前提

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007 Advanced Real-Time Rendering in 3D Graphics and Games）

## 関連ページ

- [環境光遮蔽（AO）](index.md)
- [AO の理論](theory/index.md)
- [半球 SSAO](ssao-hemisphere.md)
- [フィルタ](filtering/index.md)
- [アーティファクト](artifacts/index.md)
- [投影](../../3d/projection.md)
