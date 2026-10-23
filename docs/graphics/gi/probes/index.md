---
title: Probe GI
tags:
  - 描画
---

# Probe GI

<strong>プローブ GI は空間のあちこちに「プローブ」を置き、そこでの間接光を保存しておいて、物体のシェーディング時に補間して使う手法</strong>です。動く物体にも使え軽いのが利点です。このセクションでは原理・補間・SH の持ち方・置き方・動的更新・反射プローブとの違いを、1 つずつ別のページで説明します。

## 原理
<strong>プローブの位置 `p_i`</strong> で 全方向の入射光をキャプチャ（ベイク・または動的に計算）し、放射照度 E_i(n)をSH に投影して、係数として保存します。

| 手順 | 内容 |
| --- | --- |
| ① 配置 | シーンの空間にプローブを置く（手動・自動・格子） |
| ② 計算（ベイク） | 各プローブで全方向のレイ（またはキューブマップのレンダリング）から、放射照度を SH に |
| ③ 実行時の補間 | 物体の位置に応じ、近くのプローブの SH を重み付けして補間 |
| ④ 評価 | 補間した SH を物体の法線で評価して、間接拡散光 |

```hlsl
float3 sh[9] = InterpolateProbes(world_pos);
float3 irradiance = EvaluateSH9(world_normal, sh);
float3 indirect_diffuse = albedo * irradiance;
```

### 歴史と実際の姿

「空間の点に間接光を保存し補間して使う」という発想は、Greger らのIrradiance Volume（1998）に遡ります。ゲームでの広い採用は Valve の Source エンジンが使ったアンビエント キューブ（6 方向の色で拡散光を表す方式）や、Sloan らの SH を使った Precomputed Radiance Transfer（2002）の流れから来ています。いまの Unity のライト プローブや、Unreal Engine の Volumetric Lightmap は、この系統です。

プローブの利点を一言で言えば、ライトマップの届かない部分を、小さなコストで埋められることです。ライトマップはメッシュの表面にしか貼れないので、キャラクターや乗り物のような動く物体には使えません。プローブなら動く物体がどこにいても、その位置の周りの 8 個（あるいは四面体の 4 個）のプローブから間接光を補間できます。木の葉や草のようにライトマップを作りにくい小さな物体にも、プローブはよく使われます。

代償は 低周波しか持てないことです。プローブ 1 個が表すのはその点の周りの滑らかな明るさだけです。床と壁の接触部分の細かい暗さ（接触影）は、プローブには入りません。これは AO や[コンタクト シャドウ](../../shadows/contact-shadows.md)で補います。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Interpolation Methods](interpolation.md) | 周囲のプローブから、値を求める |
| [Storing SH](sh-storage.md) | 係数の保存形式 |
| [Probe Placement](placement.md) | どこに、どの密度で置くか |
| [Dynamic Updates](dynamic-update.md) | 光や物の変化への追従 |
| [Comparison with Reflection Probes and Cost](compare.md) | 用途の違い・長所短所 |

## プローブで光を持つ

<strong>ライトマップ</strong>は 面に光を、焼き込みます。動く物（キャラクター、車）は面ではなく空間のあちこちを、動くのでライトマップで照らせません。空間の点に光の情報を置いておき、動く物の位置でその情報を引く方法が、プローブ GI（ライト プローブ、放射照度ボリューム）です（Greger ら、1998）。

```text
        ●        ●        ●        ← プローブ（空間の点。そこに、周りの光を、保存）
   ●        ●        ●
        ●        ●        ●
            ◎ ← 動くキャラクター: 周りの、プローブから、光を、補間して、受ける
```

## プローブが持つもの

各プローブは <strong>その点にあらゆる方向から、入ってくる光</strong>（放射照度）を、少数の数で保存します。

| 表現 | 数 | 内容 |
| --- | --- | --- |
| 単色 | 3（RGB） | 向きなし。最低限 |
| アンビエント キューブ | 18（6 方向 × RGB） | 6 つの軸方向の、色（Valve、2006）。法線で 3 つを混ぜる |
| SH L1 | 12（4 × RGB） | おおまかな向き |
| SH L2 | 27（9 × RGB） | 標準。放射照度はほぼ十分（[Spherical Harmonics (SH)](../theory/spherical-harmonics.md)） |

27 個の数（SH L2）が、1 つのプローブのデータで、数千個のプローブでも数百 KB に、収まります。

## 動く物を照らす

<strong>動く物</strong>の 位置から周りの、プローブを探し補間してその位置での、環境光を得ます（[Interpolation Methods](interpolation.md)）。

```hlsl
// 物体の位置で、プローブを補間して、法線方向の、拡散の、間接光を求める。
float3 sh[9];
InterpolateProbes(world_position, sh);                              // 周りの、プローブの SH 係数を、補間
float3 irradiance = IrradianceFromSH9(sh, normal);                  // 法線方向の、放射照度
float3 indirect = albedo / 3.14159265 * irradiance;
```

補間した SH 係数から、法線ごとの放射照度を求めて `albedo / π` を、掛けます。動く物はどこへ行っても周りの光で、照らされます（日向と日陰の境を歩くと、なめらかに暗くなる）。

## プローブの種類

| 種類 | プローブの値を、どう作るか | 光が動的か |
| --- | --- | --- |
| ベイクしたプローブ | ライトマップと同時に、事前計算（[Baking Workflow](../lightmaps/baking.md)） | 静的（光は、固定） |
| 動的に更新するプローブ | 実行時に、再計算（昼夜、動く光に対応）（[Dynamic Updates](dynamic-update.md)） | 動的 |
| DDGI | レイトレーシングで、毎フレーム、更新（[DDGI](../ddgi.md)） | 動的 |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 動く物を照らせる（ライトマップは面に、焼くので不可能） |
| 長所 | メモリが小さい（1 つ 27 個の数）。実行時のコストも小さい（補間 + SH 評価） |
| 長所 | 大きな空間（オープン ワールド）にも、配置密度を変えて対応できる |
| 短所 | 低周波のみ（SH L2）。鋭い影、光の境目はぼやける |
| 短所 | 光漏れ（プローブが壁の、向こう側の光を拾う）。配置と補間の工夫が必要（[Probe Placement](placement.md)） |
| 短所 | ベイクしたプローブは光が固定。動的な光には対応できない |

## このセクションの構成

| ページ | 内容 |
| --- | --- |
| [Probe Placement](placement.md) | プローブをどこに、どれだけ置くか |
| [Storing SH](sh-storage.md) | SH をどう、テクスチャに保存するか |
| [Interpolation Methods](interpolation.md) | 周りの、プローブをどう補間するか |
| [Dynamic Updates](dynamic-update.md) | 光が、変わったときプローブをどう更新するか |
| [Comparison with Reflection Probes and Cost](compare.md) | 反射プローブとの違いと、コスト |

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
