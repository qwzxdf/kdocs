---
title: Combining with SSR
tags:
  - 描画
---

# Combining with SSR

<strong>プローブは安くて安定、SSR は細かく正確ですが、画面外が映らない</strong>ので、<strong>両者を組み合わせる</strong>のが現在の標準です。SSR が当たった所は SSR、外れた所はプローブ、という順で、重ねます。このページでは、使い分けと、長所・短所を説明します。

!!! tip "ポイント"
    - SSR の結果を優先し、信頼度が低い所は、プローブで埋める。
    - 境界は、信頼度でなめらかにブレンド。
    - プローブだけでも、最低限の反射が出るので、安全網になる。
    - プローブは、安い・安定・画面外も映る。ただし、視差のずれ・更新が課題。

## SSR と組み合わせる
<strong>プローブは遠くの粗い反射</strong>、<strong>SSR は近くの細かい映り込み</strong>が得意です。組み合わせるのが一般的です（[SSR Fallback and Compositing](../ssr-fallback.md)）。

それぞれが得意な範囲は、はっきり分かれています。遠景や粗い反射は<strong>プローブ</strong>、近くの細かい反射（足元や接地部）は <strong>SSR</strong>、平面（水面や鏡）は<strong>平面反射</strong>が向いています。

## 長所と短所
| 長所 | 短所 |
| --- | --- |
| 安い（キューブマップを引くだけ） | 位置が 1 点。視差・詳細なずれ |
| あらゆる形の面に使える | 動く物・変化するシーンを映せない（更新が必要） |
| 粗さに対応（ミップ） | 自己反射（そこにあるはずの物がプローブに写っている） |
| 画面外の景色も映る | 接地の細かい反射（足元の映り込み）が、出ない |


### 組み合わせの設計

SSR とプローブの合成は、<strong>信頼度</strong>で行います。SSR が当たりを見つけて、画面の端でも厚みも問題ないなら、信頼度は高く、SSR の色を使います。信頼度が下がるにつれて、プローブの色を混ぜていきます。プローブは常に計算しておき、`result = lerp(probe, ssr, confidence)` で合成します。こうすると、SSR が外れた画素でも、最低限の反射（プローブ）が常にあるので、画面が黒く抜けることがありません。プローブは SSR の失敗を隠す<strong>安全網</strong>の役目を担っています（[SSR Fallback and Compositing](../ssr-fallback.md)）。

### 組み合わせの設計

SSR とプローブの合成は、<strong>信頼度</strong>で行います。SSR が当たりを見つけて、画面の端でも厚みも問題ないなら、信頼度は高く、SSR の色を使います。信頼度が下がるにつれて、プローブの色を混ぜていきます。プローブは常に計算しておき、`result = lerp(probe, ssr, confidence)` で合成します。こうすると、SSR が外れた画素でも、最低限の反射（プローブ）が常にあるので、画面が黒く抜けることがありません。プローブは SSR の失敗を隠す<strong>安全網</strong>の役目を担っています（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## なぜ、組み合わせるのか

<strong>反射プローブ</strong>と、<strong>SSR</strong>（画面空間の、反射）は、得意・不得意が、正反対です。組み合わせると、互いの、弱点を、補えます。

| | 反射プローブ | SSR |
| --- | --- | --- |
| 画面の外の物 | ○（映る） | ×（画面に、無いので、映らない） |
| 動く物 | ×（ベイクなら、映らない） | ○（今のフレームの、画面から、拾う） |
| 近くの、細かい反射 | ×（解像度が、粗い、視差の、ずれ） | ○（正確、画面の、実際の、ジオメトリ） |
| 遠景 | ○ | △（遠いと、レイマーチが、長く、重い） |
| コスト | 小（テクスチャを、引くだけ） | 中〜大（画素ごとに、レイマーチ） |
| 画面の端 | ○ | ×（端で、反射が、欠ける） |

## 基本の、合成

<strong>SSR が、成功した、画素</strong>（<strong>レイが、画面内の、何かに、当たった</strong>）は、SSR の、結果を、使い、失敗した、画素（画面の外、見つからない）は、反射プローブで、補います。

```hlsl
// SSR の結果（rgb = 色、a = 信頼度 0〜1）と、反射プローブで、合成する。
float4 ssr = g_ssr_result.Load(int3(pixel, 0));                            // rgb: 反射色、a: SSR が、有効な割合
float3 probe = SampleProbes(world_pos, R, roughness, ...);                  // 反射プローブ（粗さに応じた、ぼかし、視差補正）

float3 reflection = lerp(probe, ssr.rgb, ssr.a);                            // SSR が、有効なら SSR、無効ならプローブ
```

<strong>`ssr.a`</strong>（<strong>信頼度</strong>）が、1 なら、SSR だけ、0 なら、プローブだけです。途中の、値で、なめらかに、つなぎます。

### 信頼度の、決め方

<strong>SSR の、信頼度</strong>を、<strong>いくつかの、要素</strong>から、計算します（[Color Lookup and Fading](../ssr-basics/color-fade.md)）。

```hlsl
// SSR の、信頼度: 画面の端、レイの長さ、反射方向、粗さ、で、徐々に、下げる。
float confidence = 1.0;
confidence *= 1.0 - saturate(max(abs(hit_uv.x * 2.0 - 1.0), abs(hit_uv.y * 2.0 - 1.0)) * 4.0 - 3.0);   // 画面の端で、フェード
confidence *= 1.0 - saturate(ray_length / g_max_ssr_distance);                                          // 遠いほど、弱く
confidence *= saturate(dot(R, -V) * 4.0 + 1.0);                                                          // カメラに、向かう反射は、弱く（情報が、欠ける）
confidence *= 1.0 - saturate((roughness - 0.6) / 0.4);                                                    // 粗いほど、弱く（プローブに、任せる）
```

<strong>画面の端</strong>、<strong>遠い</strong>、カメラに向かう、粗い、という、SSR の、苦手な、条件で、信頼度を、下げ、プローブに、切り替えます。

## 順序と、重み付け

<strong>3 段階</strong>の、フォールバックを、考えます。

```text
① SSR（画面内の、近距離。最も、正確）  → 信頼度 a1
② 反射プローブ（画面の外・遠景）          → 残り (1 − a1) の、うち、プローブの、重み a2
③ グローバルな、空のキューブマップ          → 残り
```

```hlsl
float3 result = ssr.rgb * ssr.a                                              // ① SSR
              + local_probe * (1.0 - ssr.a) * probe_weight                   // ② ローカル プローブ
              + sky * (1.0 - ssr.a) * (1.0 - probe_weight);                  // ③ 空
```

<strong>SSR が、有効な部分</strong>は、<strong>SSR</strong>、それ以外は、局所プローブ、さらに、プローブの、範囲外は、空（[Probe Operation](blending.md)）、と、段階的に、フォールバックします。

## 色の、つながり

<strong>SSR と、プローブ</strong>は、<strong>別の、方法で、作られた</strong>ので、同じ物を、映しても、色や、明るさが、わずかに、違うことが、あります。境目（信頼度が、変わる所）で、反射の色が、ずれて見える場合が、あります。

| 問題 | 対策 |
| --- | --- |
| 明るさの、ずれ | SSR の、露出（前フレームの、トーン マッピング前の、色）と、プローブの、HDRを、同じ、スケールで、扱う |
| 色の、ずれ | プローブの、撮影時の、ライティングが、今のシーンと、違う（昼夜が、変わった）。プローブを、動的に、更新、または、時間帯で、補間 |
| 境目が、見える | 信頼度の、フェードを、広く（急に、切り替えない） |

## 描画の、順序

| 順 | 内容 |
| --- | --- |
| 1 | 不透明な物を、描く（G バッファ） |
| 2 | SSR（G バッファと、前フレームの色から） |
| 3 | 反射プローブと、SSR を、合成（ライティングの、一部として） |
| 4 | 半透明、ポスト プロセス |

<strong>SSR は、前フレームの、色</strong>を、使うことが、多く（<strong>今フレームの、ライティングは、まだ、終わっていない</strong>ため）、1 フレームの、遅れが、あります（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## よくあるミス

??? failure "SSR の外れた所が黒くなる"
    <strong>プローブを、フォールバック</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR ＋ プローブが、標準の組み合わせ
    - [x] 信頼度で、なめらかに切り替える

## 参考

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- Valient, "Reflections and Volumetrics of Killzone Shadow Fall", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [Reflection Probes](index.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
- [Reflection Comparison](../comparison.md)
