---
title: Probe GI
tags:
  - 描画
---

# Probe GI

<strong>プローブ GI は、空間のあちこちに「プローブ」を置き、そこでの間接光を保存しておいて、物体のシェーディング時に補間して使う手法</strong>です。<strong>動く物体にも使え、軽い</strong>のが利点です。このセクションでは、原理・補間・SH の持ち方・置き方・動的更新・反射プローブとの違いを、1 つずつ別のページで説明します。

## 原理
<strong>プローブの位置 `p_i`</strong> で、<strong>全方向の入射光</strong>をキャプチャ（ベイク・または動的に計算）し、<strong>放射照度 E_i(n)</strong>をSH に投影して、係数として保存します。

| 手順 | 内容 |
| --- | --- |
| ① 配置 | シーンの空間にプローブを置く（手動・自動・格子） |
| <strong>② 計算（ベイク）</strong> | 各プローブで全方向のレイ（またはキューブマップのレンダリング）から、放射照度を SH に |
| ③ 実行時の補間 | 物体の位置に応じ、近くのプローブの SH を、重み付けして補間 |
| ④ 評価 | 補間した SH を物体の法線で評価して、間接拡散光 |

```hlsl
float3 sh[9] = InterpolateProbes(world_pos);
float3 irradiance = EvaluateSH9(world_normal, sh);
float3 indirect_diffuse = albedo * irradiance;
```

### 歴史と実際の姿

「空間の点に間接光を保存し、補間して使う」という発想は、Greger らの<strong>Irradiance Volume</strong>（1998）に遡ります。ゲームでの広い採用は、Valve の Source エンジンが使った<strong>アンビエント キューブ</strong>（6 方向の色で拡散光を表す方式）や、Sloan らの SH を使った Precomputed Radiance Transfer（2002）の流れから来ています。いまの Unity のライト プローブや、Unreal Engine の Volumetric Lightmap は、この系統です。

プローブの利点を一言で言えば、<strong>ライトマップの届かない部分を、小さなコストで埋められること</strong>です。ライトマップはメッシュの表面にしか貼れないので、キャラクターや乗り物のような動く物体には使えません。プローブなら、動く物体がどこにいても、その位置の周りの 8 個（あるいは四面体の 4 個）のプローブから間接光を補間できます。木の葉や草のように、ライトマップを作りにくい小さな物体にも、プローブはよく使われます。

代償は、<strong>低周波しか持てない</strong>ことです。プローブ 1 個が表すのは、その点の周りの滑らかな明るさだけです。床と壁の接触部分の細かい暗さ（接触影）は、プローブには入りません。これは AO や[コンタクト シャドウ](../../shadows/contact-shadows.md)で補います。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Interpolation Methods](interpolation.md) | 周囲のプローブから、値を求める |
| [Storing SH](sh-storage.md) | 係数の保存形式 |
| [Probe Placement](placement.md) | どこに、どの密度で置くか |
| [Dynamic Updates](dynamic-update.md) | 光や物の変化への追従 |
| [Comparison with Reflection Probes and Cost](compare.md) | 用途の違い・長所短所 |

## プローブで、光を、持つ

<strong>ライトマップ</strong>は、<strong>面に、光を、焼き込み</strong>ます。動く物（キャラクター、車）は、面ではなく、空間のあちこちを、動くので、ライトマップで、照らせません。空間の、点に、光の情報を、置いておき、動く物の位置で、その情報を、引く方法が、プローブ GI（ライト プローブ、放射照度ボリューム）です（Greger ら、1998）。

```text
        ●        ●        ●        ← プローブ（空間の点。そこに、周りの光を、保存）
   ●        ●        ●
        ●        ●        ●
            ◎ ← 動くキャラクター: 周りの、プローブから、光を、補間して、受ける
```

## プローブが、持つもの

各プローブは、<strong>その点に、あらゆる方向から、入ってくる光</strong>（<strong>放射照度</strong>）を、少数の数で、保存します。

| 表現 | 数 | 内容 |
| --- | --- | --- |
| 単色 | 3（RGB） | 向きなし。最低限 |
| アンビエント キューブ | 18（6 方向 × RGB） | 6 つの軸方向の、色（Valve、2006）。法線で、3 つを、混ぜる |
| SH L1 | 12（4 × RGB） | おおまかな向き |
| SH L2 | 27（9 × RGB） | 標準。放射照度は、ほぼ、十分（[Spherical Harmonics (SH)](../theory/spherical-harmonics.md)） |

<strong>27 個の数</strong>（SH L2）が、<strong>1 つのプローブの、データ</strong>で、数千個のプローブでも、数百 KB に、収まります。

## 動く物を、照らす

<strong>動く物</strong>の、<strong>位置</strong>から、周りの、プローブを、探し、補間して、その位置での、環境光を、得ます（[Interpolation Methods](interpolation.md)）。

```hlsl
// 物体の位置で、プローブを補間して、法線方向の、拡散の、間接光を求める。
float3 sh[9];
InterpolateProbes(world_position, sh);                              // 周りの、プローブの SH 係数を、補間
float3 irradiance = IrradianceFromSH9(sh, normal);                  // 法線方向の、放射照度
float3 indirect = albedo / 3.14159265 * irradiance;
```

<strong>補間した SH 係数</strong>から、<strong>法線ごとの、放射照度</strong>を、求めて、`albedo / π` を、掛けます。動く物は、どこへ行っても、周りの、光で、照らされます（日向と日陰の、境を、歩くと、なめらかに、暗くなる）。

## プローブの、種類

| 種類 | プローブの、値を、どう作るか | 光が、動的か |
| --- | --- | --- |
| ベイクしたプローブ | ライトマップと、同時に、事前計算（[Baking Workflow](../lightmaps/baking.md)） | 静的（光は、固定） |
| 動的に、更新する、プローブ | 実行時に、再計算（昼夜、動く光に対応）（[Dynamic Updates](dynamic-update.md)） | 動的 |
| DDGI | レイトレーシングで、毎フレーム、更新（[DDGI](../ddgi.md)） | 動的 |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 動く物を、照らせる（ライトマップは、面に、焼くので、不可能） |
| 長所 | メモリが、小さい（1 つ 27 個の数）。実行時の、コストも、小さい（補間 + SH 評価） |
| 長所 | 大きな、空間（オープン ワールド）にも、配置密度を、変えて、対応できる |
| 短所 | 低周波のみ（SH L2）。鋭い、影、光の、境目は、ぼやける |
| 短所 | 光漏れ（プローブが、壁の、向こう側の、光を、拾う）。配置と、補間の、工夫が、必要（[Probe Placement](placement.md)） |
| 短所 | ベイクした、プローブは、光が、固定。動的な、光には、対応できない |

## このセクションの、構成

| ページ | 内容 |
| --- | --- |
| [Probe Placement](placement.md) | プローブを、どこに、どれだけ、置くか |
| [Storing SH](sh-storage.md) | SH を、どう、テクスチャに、保存するか |
| [Interpolation Methods](interpolation.md) | 周りの、プローブを、どう、補間するか |
| [Dynamic Updates](dynamic-update.md) | 光が、変わったとき、プローブを、どう、更新するか |
| [Comparison with Reflection Probes and Cost](compare.md) | 反射プローブとの、違いと、コスト |

## これだけ覚える

!!! abstract "まとめ"
    - [x] プローブに間接光を保存し、補間して使う
    - [x] 動く物体にも使える

## 参考

- Greger, Shirley, Hubbard, Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications, Vol. 18, No. 2, 1998（放射照度ボリューム。プローブ GI の原点）
- Mitchell, McTaggart, Green, "Shading in Valve's Source Engine", SIGGRAPH 2006, Advanced Real-Time Rendering in 3D Graphics and Games（アンビエント キューブ）
- Tatarchuk, "Irradiance Volumes for Games", Game Developers Conference 2005
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001
- Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（アンビエント ダイスなど）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [GI](../index.md)
- [DDGI](../ddgi.md)
- [Lightmaps](../lightmaps/index.md)
