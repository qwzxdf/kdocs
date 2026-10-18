---
title: Specular and Dynamic Objects
tags:
  - 描画
---

# Specular and Dynamic Objects

<strong>ライトマップは、拡散の間接光だけ</strong>で、<strong>鏡面の反射は含みません</strong>。また、動く物体には、ライトマップが無いので、プローブで間接光を補います。このページでは、鏡面の扱いと、動く物体との併用を説明します。

!!! tip "ポイント"
    - 鏡面は別：反射プローブ・SSRで扱う。
    - 動く物体は、ライトマップを持たない。
    - 周囲のプローブ（SH）から、間接光を受け取る。
    - 静的な背景と、動く物体の明るさが、揃うように調整する。

## 鏡面は別

ライトマップが保存するのは、拡散の間接光だけです。鏡面反射（周りの景色の映り込み）は含みません。鏡面は視線に依存するので、1 つの値としてテクスチャに焼いておくことができないからです（[Diffuse and Specular](../theory/diffuse-specular.md)）。鏡面反射は、[反射プローブ](../../reflections/probes/index.md)や SSR が担当します。ライトマップだけを使うと、つるつるした面が周りを映さず、違和感が出ます。

## 動く物体との併用

ライトマップは、メッシュの表面（UV2）に焼き込むため、動く物体・キャラクターには使えません。動く物体は、位置が変わるたびに受ける間接光が変わるからです。そこで、空間の点に間接光を保存した[ライト プローブ](../probes/index.md)から、周囲の間接光を受け取ります。静的な背景はライトマップ、動く物はプローブ、というのが標準的な組み合わせです。

この組み合わせで大切なのは、<strong>両者の見た目を揃える</strong>ことです。ライトマップで照らされた壁の前を、プローブで照らされたキャラクターが歩くとき、明るさや色が大きく違うと、キャラクターだけが浮いて見えます。プローブは、ライトマップと同じベイクの結果（同じ光源、同じバウンス数）から作るので、基本的には揃いますが、プローブの置き方が粗いと、壁の近くで差が出ます。

限界もあります。動く物体が背景に落とす間接光（キャラクターの赤い服が壁をほんのり赤くする）は、ライトマップに反映されません。ライトマップは焼き込み済みで、動く物体の存在を知らないためです。また、動く物体が背景に作る接触の暗さは、AO で補います（[AO](../../ao/index.md)）。

## 動く物は、ライトマップで、照らせない

<strong>ライトマップ</strong>は、<strong>面に、焼き込む</strong>ので、動かない、面にしか、使えません。動く物（キャラクター、車、扉、壊れる物）は、ライトマップを、持たず、別の方法で、周りの光を、受ける必要が、あります。

| 物の種類 | ライティング |
| --- | --- |
| 静的な物（壁、床、建物） | ライトマップ（焼き込み） |
| 動的な物（キャラクター、車） | ライト プローブ（空間に、置いた、プローブから、補間）（[Probe GI](../probes/index.md)） |

## ライト プローブで、動く物を、照らす

<strong>ライトマップと、同時に、ベイク</strong>した、<strong>ライト プローブ</strong>（[Probe GI](../probes/index.md)）が、シーンの、あちこちに、環境光を、保存しています。動く物の、位置で、周りの、プローブを、補間して、環境光を、得ます（[Interpolation Methods](../probes/interpolation.md)）。

```hlsl
// 動的な物の、シェーダー: ライトマップの代わりに、ライト プローブから、環境光を得る。
float3 sh[9];
InterpolateProbes(input.world_position, sh);
float3 irradiance = IrradianceFromSH9(sh, N);
float3 indirect = albedo / 3.14159265 * irradiance;
float3 direct = ComputeDirectLights(input.world_position, N);               // 動的な、直接光（影つき）
return float4(direct + indirect, 1.0);
```

<strong>ライトマップと、同じ光を、ベイクした、プローブ</strong>なので、<strong>静的な、背景と、動く物の、光が、なじみます</strong>（キャラクターが、日向から、日陰へ、歩くと、自然に、暗くなる）。

## 動く物が、背景に、与える、影響

<strong>動く物</strong>は、<strong>周りの、光を、受ける</strong>だけでなく、周りに、影を、落とし、光を、反射します。ライトマップは、これを、反映できません。

| 影響 | 扱い |
| --- | --- |
| 動く物の、影（直接光の、影） | 実行時の、シャドウ マップ（[Shadows](../../shadows/index.md)）。ミックス ライト（直接光は、実行時）なら、自然に、出る |
| 動く物の、接地の、暗さ（AO） | AO（[AO](../../ao/index.md)）、ブロブ影（[Blob and Planar Projected Shadows](../../shadows/special-cases/blob-planar.md)）、コンタクト シャドウ（[Contact Shadows](../../shadows/contact-shadows.md)） |
| 動く物からの、反射光（間接光） | 反映されない（ライトマップは、静的）。SSGI、DDGI、動的な プローブで、近似 |

## 鏡面反射

<strong>ライトマップ</strong>は、<strong>拡散</strong>の、光しか、焼けません（[Diffuse and Specular](../theory/diffuse-specular.md)）。鏡面（つるつるの、面の、反射）は、別の方法が、必要です。

| 物 | 鏡面 |
| --- | --- |
| 静的な、つるつるの面（床、窓） | 反射プローブ（[Reflection Probes](../../reflections/probes/index.md)）、SSR、平面反射 |
| 動的な、金属の物（車、武器） | 反射プローブ（最も近い、1〜2 個を、ブレンド） |

<strong>ライトマップの、拡散</strong>に、<strong>反射プローブの、鏡面</strong>を、足す構成が、標準です（[Reflection Probes](../../reflections/probes/index.md)）。

## 静的と、動的の、見た目の、差を、小さくする

<strong>ライトマップ</strong>（<strong>高品質、焼き込み</strong>）と、プローブ（低周波、補間）の、品質の、差が、目立ちます。キャラクターが、静的な、壁の、前に、立つと、キャラクターの、陰影が、のっぺり、壁は、細かい影、と、浮いて見えます。

| 対策 | 内容 |
| --- | --- |
| プローブを、密に置く | 動く物が、通る、場所に、プローブを、増やす |
| キャラクターに、AO や、コンタクト シャドウを、足す | 接地の、暗さで、背景に、なじむ |
| 動的な、ライトで、キャラクターの、近くを、補う | キャラクターの、近くに、追従する、弱いライト（フィル ライト）を、置く |
| プローブの、SH を、L2 に（L1 でなく） | 向きの、表現が、細かくなる |

## よくあるミス

??? failure "動く物体だけ、背景と明るさが合わない"
    <strong>ライトプローブ</strong>を置いて、<strong>間接光を揃える</strong>。

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
