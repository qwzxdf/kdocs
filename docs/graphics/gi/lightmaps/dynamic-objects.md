---
title: Specular and Dynamic Objects
tags:
  - 描画
---

# Specular and Dynamic Objects

<strong>ライトマップは拡散の間接光だけ</strong>で、鏡面の反射は含みません。また、動く物体にはライトマップが無いので、プローブで間接光を補います。このページでは鏡面の扱いと動く物体との併用を説明します。

!!! tip "ポイント"
    - 鏡面は別：反射プローブ・SSRで扱う。
    - 動く物体はライトマップを持たない。
    - 周囲のプローブ（SH）から、間接光を受け取る。
    - 静的な背景と動く物体の明るさが、揃うように調整する。

!!! info "このページを読む前に"
    - [Lightmaps](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 鏡面は別

ライトマップが保存するのは拡散の間接光だけです。鏡面反射（周りの景色の映り込み）は含みません。鏡面は視線に依存するので 1 つの値としてテクスチャに焼いておくことができないからです（[Diffuse and Specular](../theory/diffuse-specular.md)）。鏡面反射は[反射プローブ](../../reflections/probes/index.md)や SSR が担当します。ライトマップだけを使うとつるつるした面が周りを映さず、違和感が出ます。

## 動く物体との併用

ライトマップはメッシュの表面（UV2）に焼き込むため、動く物体・キャラクターには使えません。動く物体は位置が変わるたびに受ける間接光が変わるからです。そこで、空間の点に間接光を保存した[ライト プローブ](../probes/index.md)から、周囲の間接光を受け取ります。静的な背景はライトマップ、動く物はプローブ、というのが標準的な組み合わせです。

この組み合わせで大切なのは <strong>両者の見た目を揃える</strong>ことです。ライトマップで照らされた壁の前をプローブで照らされたキャラクターが歩くとき、明るさや色が大きく違うとキャラクターだけが浮いて見えます。プローブはライトマップと同じベイクの結果（同じ光源、同じバウンス数）から作るので、基本的には揃いますがプローブの置き方が粗いと、壁の近くで差が出ます。

限界もあります。動く物体が背景に落とす間接光（キャラクターの赤い服が壁をほんのり赤くする）は、ライトマップに反映されません。ライトマップは焼き込み済みで、動く物体の存在を知らないためです。また、動く物体が背景に作る接触の暗さは、AO で補います（[AO](../../ao/index.md)）。

## 動く物はライトマップで、照らせない

<strong>ライトマップ</strong>は 面に焼き込むので、動かない面にしか使えません。動く物（キャラクター、車、扉、壊れる物）はライトマップを持たず、別の方法で周りの光を受ける必要があります。

| 物の種類 | ライティング |
| --- | --- |
| 静的な物（壁、床、建物） | ライトマップ（焼き込み） |
| 動的な物（キャラクター、車） | ライト プローブ（空間に置いた、プローブから補間）（[Probe GI](../probes/index.md)） |

## ライト プローブで動く物を照らす

<strong>ライトマップと同時にベイク</strong>した、ライト プローブ（[Probe GI](../probes/index.md)）がシーンのあちこちに環境光を保存しています。動く物の位置で周りのプローブを補間して環境光を得ます（[Interpolation Methods](../probes/interpolation.md)）。

```hlsl
// 動的な物の、シェーダー: ライトマップの代わりに、ライト プローブから、環境光を得る。
float3 sh[9];
InterpolateProbes(input.world_position, sh);
float3 irradiance = IrradianceFromSH9(sh, N);
float3 indirect = albedo / 3.14159265 * irradiance;
float3 direct = ComputeDirectLights(input.world_position, N);               // 動的な、直接光（影つき）
return float4(direct + indirect, 1.0);
```

ライトマップと同じ光をベイクした、プローブなので 静的な背景と、動く物の光がなじみます（キャラクターが日向から日陰へ歩くと自然に暗くなる）。

## 動く物が背景に与える影響

<strong>動く物</strong>は 周りの光を受けるだけでなく周りに影を落とし光を反射します。ライトマップはこれを反映できません。

| 影響 | 扱い |
| --- | --- |
| 動く物の影（直接光の影） | 実行時の、シャドウ マップ（[Shadows](../../shadows/index.md)）。ミックス ライト（直接光は実行時）なら自然に出る |
| 動く物の接地の暗さ（AO） | AO（[AO](../../ao/index.md)）、ブロブ影（[Blob and Planar Projected Shadows](../../shadows/special-cases/blob-planar.md)）、コンタクト シャドウ（[Contact Shadows](../../shadows/contact-shadows.md)） |
| 動く物からの反射光（間接光） | 反映されない（ライトマップは、静的）。SSGI、DDGI、動的な プローブで近似 |

## 鏡面反射

<strong>ライトマップ</strong>は 拡散の光しか、焼けません（[Diffuse and Specular](../theory/diffuse-specular.md)）。鏡面（つるつるの面の反射）は、別の方法が必要です。

| 物 | 鏡面 |
| --- | --- |
| 静的なつるつるの面（床、窓） | 反射プローブ（[Reflection Probes](../../reflections/probes/index.md)）、SSR、平面反射 |
| 動的な金属の物（車、武器） | 反射プローブ（最も近い、1〜2 個をブレンド） |

ライトマップの拡散に 反射プローブの、鏡面を足す構成が標準です（[Reflection Probes](../../reflections/probes/index.md)）。

## 静的と動的の見た目の差を小さくする

<strong>ライトマップ</strong>（高品質、焼き込み）とプローブ（低周波、補間）の品質の差が目立ちます。キャラクターが静的な壁の前に立つと、キャラクターの陰影がのっぺり壁は、細かい影、と浮いて見えます。

| 対策 | 内容 |
| --- | --- |
| プローブを密に置く | 動く物が通る場所にプローブを増やす |
| キャラクターに AO やコンタクト シャドウを足す | 接地の暗さで背景になじむ |
| 動的なライトでキャラクターの近くを補う | キャラクターの近くに、追従する弱いライト（フィル ライト）を置く |
| プローブの SH を L2 に（L1 でなく） | 向きの表現が細かくなる |

## よくあるミス

??? failure "動く物体だけ、背景と明るさが合わない"
    <strong>ライトプローブ</strong>を置いて、間接光を揃える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 鏡面は反射の手法で、動く物体はプローブで

## 参考

- Greger, Shirley, Hubbard, Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications, Vol. 18, No. 2, 1998（放射照度ボリューム。プローブ GI の原点）
- Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（アンビエント ダイスなど）
- Mitchell, McTaggart, Green, "Shading in Valve's Source Engine", SIGGRAPH 2006, Advanced Real-Time Rendering in 3D Graphics and Games（アンビエント キューブ）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [Lightmaps](index.md)
- [Probe GI](../probes/index.md)
- [Reflections](../../reflections/index.md)
