---
title: Combining with SSR
tags:
  - 描画
---

# Combining with SSR

<strong>プローブは安くて安定、SSR は細かく正確ですが画面外が映らない</strong>ので、両者を組み合わせるのが現在の標準です。SSR が当たった所は SSR、外れた所はプローブ、という順で重ねます。このページでは使い分けと長所・短所を説明します。

!!! tip "ポイント"
    - SSR の結果を優先し、信頼度が低い所はプローブで埋める。
    - 境界は信頼度でなめらかにブレンド。
    - プローブだけでも、最低限の反射が出るので安全網になる。
    - プローブは安い・安定・画面外も映る。ただし、視差のずれ・更新が課題。

!!! info "このページを読む前に"
    - [Reflection Probes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## SSR と組み合わせる
<strong>プローブは遠くの粗い反射</strong>、SSR は近くの細かい映り込みが得意です。組み合わせるのが一般的です（[SSR Fallback and Compositing](../ssr-fallback.md)）。

それぞれが得意な範囲ははっきり分かれています。遠景や粗い反射はプローブ、近くの細かい反射（足元や接地部）は SSR、平面（水面や鏡）は平面反射が向いています。

## 長所と短所
| 長所 | 短所 |
| --- | --- |
| 安い（キューブマップを引くだけ） | 位置が 1 点。視差・詳細なずれ |
| あらゆる形の面に使える | 動く物・変化するシーンを映せない（更新が必要） |
| 粗さに対応（ミップ） | 自己反射（そこにあるはずの物がプローブに写っている） |
| 画面外の景色も映る | 接地の細かい反射（足元の映り込み）が出ない |


### 組み合わせの設計

SSR とプローブの合成は <strong>信頼度</strong>で行います。SSR が当たりを見つけて画面の端でも厚みも問題ないなら、信頼度は高く SSR の色を使います。信頼度が下がるにつれてプローブの色を混ぜていきます。プローブは常に計算しておき `result = lerp(probe, ssr, confidence)` で合成します。こうすると SSR が外れた画素でも、最低限の反射（プローブ）が常にあるので、画面が黒く抜けることがありません。プローブは SSR の失敗を隠す安全網の役目を担っています（[SSR Fallback and Compositing](../ssr-fallback.md)）。

### 組み合わせの設計

SSR とプローブの合成は 信頼度で行います。SSR が当たりを見つけて画面の端でも厚みも問題ないなら、信頼度は高く SSR の色を使います。信頼度が下がるにつれてプローブの色を混ぜていきます。プローブは常に計算しておき `result = lerp(probe, ssr, confidence)` で合成します。こうすると SSR が外れた画素でも、最低限の反射（プローブ）が常にあるので、画面が黒く抜けることがありません。プローブは SSR の失敗を隠す安全網の役目を担っています（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## なぜ組み合わせるのか

<strong>反射プローブ</strong>と SSR（画面空間の、反射）は得意・不得意が正反対です。組み合わせると互いの弱点を補えます。

| | 反射プローブ | SSR |
| --- | --- | --- |
| 画面の外の物 | ○（映る） | ×（画面に無いので映らない） |
| 動く物 | ×（ベイクなら、映らない） | ○（今のフレームの、画面から拾う） |
| 近くの細かい反射 | ×（解像度が粗い視差の、ずれ） | ○（正確、画面の実際のジオメトリ） |
| 遠景 | ○ | △（遠いと、レイマーチが長く重い） |
| コスト | 小（テクスチャを引くだけ） | 中〜大（画素ごとに、レイマーチ） |
| 画面の端 | ○ | ×（端で反射が欠ける） |

## 基本の合成

<strong>SSR が成功した画素</strong>（レイが画面内の何かに当たった）は、SSR の結果を使い失敗した、画素（画面の外、見つからない）は反射プローブで、補います。

```hlsl
// SSR の結果（rgb = 色、a = 信頼度 0〜1）と、反射プローブで、合成する。
float4 ssr = g_ssr_result.Load(int3(pixel, 0));                            // rgb: 反射色、a: SSR が、有効な割合
float3 probe = SampleProbes(world_pos, R, roughness, ...);                  // 反射プローブ（粗さに応じた、ぼかし、視差補正）

float3 reflection = lerp(probe, ssr.rgb, ssr.a);                            // SSR が、有効なら SSR、無効ならプローブ
```

`ssr.a`（信頼度）が 1 なら、SSR だけ 0 ならプローブだけです。途中の値でなめらかにつなぎます。

### 信頼度の決め方

SSR の信頼度を いくつかの、要素から計算します（[Color Lookup and Fading](../ssr-basics/color-fade.md)）。

```hlsl
// SSR の、信頼度: 画面の端、レイの長さ、反射方向、粗さ、で、徐々に、下げる。
float confidence = 1.0;
confidence *= 1.0 - saturate(max(abs(hit_uv.x * 2.0 - 1.0), abs(hit_uv.y * 2.0 - 1.0)) * 4.0 - 3.0);   // 画面の端で、フェード
confidence *= 1.0 - saturate(ray_length / g_max_ssr_distance);                                          // 遠いほど、弱く
confidence *= saturate(dot(R, -V) * 4.0 + 1.0);                                                          // カメラに向かう反射は、弱く（情報が欠ける）
confidence *= 1.0 - saturate((roughness - 0.6) / 0.4);                                                    // 粗いほど、弱く（プローブに任せる）
```

画面の端、遠い、カメラに向かう粗いという SSR の苦手な条件で、信頼度を下げプローブに切り替えます。

## 順序と重み付け

<strong>3 段階</strong>のフォールバックを考えます。

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

SSR が有効な部分は SSR、それ以外は局所プローブ、さらにプローブの範囲外は空（[Probe Operation](blending.md)）、と段階的にフォールバックします。

## 色のつながり

<strong>SSR とプローブ</strong>は 別の方法で、作られたので同じ物を映しても色や、明るさがわずかに違うことがあります。境目（信頼度が変わる所）で反射の色がずれて見える場合があります。

| 問題 | 対策 |
| --- | --- |
| 明るさのずれ | SSR の、露出（前フレームのトーン マッピング前の色）と、プローブの HDRを同じスケールで、扱う |
| 色のずれ | プローブの、撮影時のライティングが今のシーンと、違う（昼夜が変わった）。プローブを動的に更新、または時間帯で補間 |
| 境目が見える | 信頼度の、フェードを広く（急に切り替えない） |

## 描画の順序

| 順 | 内容 |
| --- | --- |
| 1 | 不透明な物を描く（G バッファ） |
| 2 | SSR（G バッファと、前フレームの色から） |
| 3 | 反射プローブと SSR を合成（ライティングの一部として） |
| 4 | 半透明、ポスト プロセス |

<strong>SSR は前フレームの色</strong>を使うことが多く（今フレームの、ライティングはまだ終わっていないため）、1 フレームの遅れがあります（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## よくあるミス

??? failure "SSR の外れた所が黒くなる"
    <strong>プローブをフォールバック</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR ＋ プローブが標準の組み合わせ
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
