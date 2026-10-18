---
title: Thin and Thick Glass
tags:
  - 描画
---

# Thin and Thick Glass

<strong>窓ガラスのような「薄いガラス」は、屈折でほとんどずれません</strong>が、<strong>ガラスの塊のような「厚いガラス」は、大きくずれます</strong>。両者で、モデルを使い分けると、無駄なく、自然に見えます。このページでは、使い分けの基準を説明します。

!!! tip "ポイント"
    - 薄いガラス：ほぼ透明 ＋ 反射。屈折はほぼ無視。
    - 厚いガラス：屈折 ＋ 厚みによる色。
    - 球体・瓶などは、前面と背面の 2 回の屈折。
    - 使い分けで、コストを抑える。

## 薄いガラスと厚いガラス
| 種類 | 例 | 屈折 | 表現 |
| --- | --- | --- | --- |
| <strong>薄いガラス（板）</strong> | 窓・ガラス戸 | ほぼ無視（入口と出口で相殺） | <strong>透過 ＋ 反射（フレネル）</strong> のみ |
| 厚いガラス・水 | 瓶・水槽・宝石 | 目立つ | 屈折 ＋ 厚みの色 ＋ 反射 |
| 曇りガラス | すりガラス | ぼやける | 背景を、ミップや大きなブラーで読む（粗さに応じて） |

<strong>窓ガラス</strong>は、<strong>屈折を省いて、単純な半透明</strong>にすれば十分です。

### 曇りガラス（粗い屈折）

<strong>粗い面ほど、背景がぼやけて見える</strong>ので、<strong>背景コピーのミップ（ブラー済み）</strong>を、<strong>粗さに応じて</strong>読みます。

```hlsl
float mip = roughness * kMaxMip;
float3 background = scene_color_mips.SampleLevel(linear_clamp, refract_uv, mip).rgb;
```

<strong>背景のコピーに、ミップ チェーンを作って</strong>おく（[ブルームのダウンサンプル](../../postprocess/bloom/index.md)と同様）。

### なぜ薄いガラスの屈折は無視できるのか

ガラス板に斜めから光が入ると、入口で曲がり、ガラス内を直進して、出口で逆向きに同じだけ曲がります。出た光は、入る前と平行で、ずれるだけです。そのずれは、板の厚みに比例し、薄い板ならわずかです。そのため、窓ガラスの向こうの景色は、ほぼそのまま見えます。厚いガラスや水では、ずれが大きく、曲面なら像が拡大・縮小・反転するので、屈折の表現が必要になります。

## 薄いガラスと、厚いガラス

屈折の、扱い方は、<strong>ガラスの、厚み</strong>で、大きく変わります。

| | 薄いガラス（窓、ガラス板、水面） | 厚いガラス（瓶、球、宝石、水晶） |
| --- | --- | --- |
| 光の、通り道 | 入口と出口が、平行（ほぼ同じ向きで、出る）。ほぼ、まっすぐ通る | 内部で、大きく、曲がる。出口の向きが、入口と、大きく違う |
| 見え方 | 向こうが、ほぼ、そのまま見える。わずかに、ずれる | 向こうが、大きく、歪む。上下左右が、逆転することも |
| 必要な、計算 | ごく小さな、ずらし（画面空間で、十分） | 入口の屈折 + 出口の屈折（2 回の屈折）。内部の反射 |
| 代表例 | 窓、コップの壁、ガラス板 | 水晶球、ガラス玉、ダイヤモンド、水の入った、コップ（全体） |

## 薄いガラス：1 回で、十分

薄い、平行な、ガラス板では、<strong>入射の屈折</strong>と、<strong>出射の屈折</strong>が、ちょうど、打ち消し合い、光は、元の向きのまま、少し、ずれて、出てきます。ずれは、厚みと、入射角で決まり、薄ければ、ごくわずかです。

```text
 空気 | ガラス | 空気
      ╲       ╲
       ╲___    ╲        入射の向きと、出射の向きは、同じ（平行）
            ╲    ╲___   ずれ（横ずれ）は、厚みに比例
```

このため、<strong>窓ガラス</strong>は、<strong>画面空間の屈折</strong>（[Screen-Space Refraction](screen-space.md)）で、十分です。ずらし量を、ごく小さくするか、ほぼ、ゼロに、します。フレネル反射と、表面の汚れ、厚みによる、わずかな色が、見た目の、主役です。

## 厚いガラス：屈折が、2 回

球や、瓶のような、<strong>厚い</strong>ガラスでは、光が、<strong>入口で、1 回曲がり</strong>、内部を通って、出口で、もう 1 回曲がります。

```text
 空気 | ガラス球                 | 空気
      ╲╲         ╲╲
       ╲╲ ←入口で屈折  ╲╲ ←出口で屈折
```

<strong>入口の、屈折ベクトル</strong>と、<strong>物体の、内部を、通った、出口の位置・法線</strong>が、必要です。

### 近似の方法

| 方法 | 内容 | 精度 |
| --- | --- | --- |
| 背面の法線を、使う（Wyman、2005） | 1. 背面の、深度と、法線を、テクスチャに描く。2. 前面で、入口の屈折を計算し、背面までの距離を推定する。3. 出口の位置と、背面の法線で、2 回目の、屈折を計算する | 凸な形で、よく合う |
| 解析的な形 | 球、箱に対して、レイと、形の、交差を、数式で、解く | 完全（形が、単純なら） |
| レイトレーシング | 実際に、光線を、追跡する | 完全。重い |

Wyman（2005）の、<strong>画像空間の、近似</strong>は、次のとおりです。

1. 物体の、背面を、描いて、深度（視点からの、距離）と、法線を、テクスチャに、保存する
2. 前面の、画素で、入口の屈折ベクトル `T₁` を、`refract(V, N_front, 1/n)` で、求める
3. 物体の厚み `d`（前面と背面の、深度の差）から、出口の位置を、`P_out ≈ P_front + T₁ × d` と、推定する
4. 出口の位置の、背面の法線 `N_back` で、2 回目の屈折を、`T₂ = refract(T₁, −N_back, n)` で、求める
5. `T₂` の、方向に、シーンを、サンプルする（画面空間の、ずらし）

```hlsl
// 厚いガラスの、2 回屈折（Wyman 2005 の考え方）。
float3 V = normalize(input.world_position - g_camera_position);
float3 N_front = normalize(input.world_normal);

// ① 入口の屈折
float3 T1 = refract(V, N_front, 1.0 / g_ior);

// ② 背面までの距離（厚み）。背面の深度から。
float thickness = ThicknessFromBackDepth(input);

// ③ 出口の位置を、推定
float3 P_out = input.world_position + T1 * thickness;

// ④ 出口での、背面の法線で、2 回目の屈折
float3 N_back = FetchBackNormal(P_out);                       // 背面の法線テクスチャから
float3 T2 = refract(T1, -N_back, g_ior);
if (dot(T2, T2) < 1e-5) T2 = reflect(T1, -N_back);            // 全反射したら、反射させる（内部反射）

// ⑤ T2 の向きで、シーンを読む（出口の位置から、T2 の向きに、少し進んだ点を、画面に投影）
float3 sample_pos = P_out + T2 * g_refract_distance;
float2 uv = ProjectToScreenUV(sample_pos);
float3 refracted = g_scene_copy.Sample(g_linear_clamp, uv).rgb;
```

`refract` が、ゼロ ベクトルを返したときは、<strong>全反射</strong>です。<strong>反射の向き</strong>で、代用します（内部反射の、1 回分の、近似）。

## 凹んだ形、複雑な形

背面を、1 層だけ、使う近似は、<strong>凸な形</strong>（視線が、入口と出口で、1 回ずつ通る）を、前提にしています。<strong>凹んだ形</strong>（コップ、ドーナツ、複雑な彫像）では、視線が、複数回、通るので、うまくいきません。

| 形 | 対応 |
| --- | --- |
| 凸（球、瓶、宝石の、単純なカット） | 背面の法線を使う近似で、よい |
| 軽く、凹む | 近似の、誤差を、許容 |
| 強く、凹む、複雑 | レイトレーシング、または、事前に、焼いた、キューブマップ（物体の、内部の、屈折を、焼く） |
| 宝石（ダイヤモンド） | 内部の、複数回の反射が、見た目の本質。キューブマップに、焼く、または、専用の、トリック（[Dispersion](dispersion.md) と組み合わせる） |

## 厚みと、薄さの、中間

ほとんどの、ゲームの、ガラス（コップ、瓶、窓）は、<strong>薄い壁</strong>の、<strong>空洞</strong>です。

| 物 | 扱い |
| --- | --- |
| ガラスの、コップ | 薄い壁として、扱う（画面空間の、小さなずらし + フレネル + 厚みによる色）。中の、水は、別（水のシェーダー） |
| ワインの、ボトル | 壁は、薄いが、中の液体が、屈折を、起こす。液体を、別メッシュとして、厚いガラスの、近似で |
| 魚の、水槽 | 水が、大きな、塊。水の、体積として、扱う（[Water](../../water/index.md)） |
| 氷の、塊 | 厚い。内部の、散乱、屈折。厚みと、ぼかしで、近似（[Thickness and Color](thickness-color.md)） |

## よくあるミス

??? failure "窓ガラスに、強い屈折を付けて、景色が歪みすぎる"
    <strong>薄いガラスは、屈折を弱める</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 薄い → 屈折ほぼ無し、厚い → 屈折 ＋ 色

## 参考

- Wyman, "An Approximate Image-Space Approach for Interactive Refraction", ACM Transactions on Graphics (SIGGRAPH 2005)
- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、フレネルの式、分散）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）

## 関連ページ

- [Refraction](index.md)
- [Thickness and Color](thickness-color.md)
