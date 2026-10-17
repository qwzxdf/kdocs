---
title: Color Lookup and Fading
tags:
  - 描画
---

# Color Lookup and Fading

**当たりが見つかったら、その画素の「前フレームまたは現フレームの色」を持ってきます**。**ただし、画面の端や、カメラに向かう反射は、信頼できないので、フェード（徐々に弱める）が必要**です。このページでは、**どの色を使うか・フェードの掛け方**を説明します。

!!! tip "ポイント"
    - **当たった画素の色**を、**反射色**として使う。
    - **前フレームの色を使うと、反射の中の反射も映る**（ただし、ずれに注意）。
    - **画面の端・カメラ向きの反射・粗い面は、フェードで弱める**。
    - **信頼度 ＝ 端からの距離 × 向き × 距離 × 粗さ**を**掛け合わせる**。
    - **フェードした分は、フォールバックで補う**。

## 色の取得
**当たった画素の色**を反射として使います。**どの画像から取るか**が重要です。

色の取得元は 3 つあります。<strong>今のフレームの、SSR を除いたシーン色</strong>は、最新の色を使えるのが利点ですが、SSR を適用する前の画像を残しておく必要があります（反射のパスの前の色を保存します）。<strong>前フレームの最終画像</strong>は、すでに反射やポストが乗っていて手軽ですが、1 フレーム遅れるので動く物体にずれが出ます。さらに、反射の中の反射が入る（二重になる）という副作用もあります。<strong>前フレームを動きベクトルで再投影</strong>する方法は、遅れを補正できますが、動きベクトルが必要です。

**多くの実装は前フレームの最終画像**（**ブルーム前**の HDR）を使い、**動きベクトルで再投影**します。

## フェード：信頼できない反射を弱める
SSR は**画面にあるものしか映せません**。**信頼できない反射**は、**フェード**して、**フォールバック**（[フォールバック](../ssr-fallback.md)）に任せます。

信頼度を下げる要因は、6 つあります。<strong>画面端</strong>は、当たりが端に近いほど弱めます（`edge_fade = saturate((0.5 − |uv − 0.5|) / margin)`）。<strong>レイの長さ</strong>は、遠いほど不確かなので弱めます。<strong>粗さ</strong>は、粗いほど弱めます（SSR はくっきりした反射が得意なので、粗い面はプローブに任せます）。<strong>向き</strong>は、反射がカメラの方へ戻る場合（`R·V` が負で大きい）に、画面に映っていない面を指すので弱めます。<strong>厚みの検証</strong>は、当たった場所の深度差が不自然なら弱めます。<strong>当たらなかった</strong>場合は信頼度 0 で、フォールバックだけを使います。

```hlsl
float SSRConfidence(float2 hit_uv, float ray_length, float roughness, float3 R_vs) {
  float2 d = abs(hit_uv - 0.5) * 2.0;
  float edge = 1.0 - smoothstep(0.8, 1.0, max(d.x, d.y));
  float distance_fade = 1.0 - saturate(ray_length / max_distance);
  float rough_fade = 1.0 - saturate(roughness / max_roughness);
  float facing = saturate(1.0 + R_vs.z * 4.0);
  return edge * distance_fade * rough_fade * facing;
}
```

### 信頼度の考え方

信頼度は、それぞれの要因を<strong>掛け算</strong>で合成します（上のコード）。どれか 1 つでも 0 に近ければ全体が 0 に近づき、その反射を使いません。信頼度は 0〜1 の連続値にしておくことが大切で、これは次のページ以降で扱うフォールバックとの合成に使います。`信頼度 × SSR の色 + (1 − 信頼度) × プローブの色` のように混ぜれば、SSR が効く場所から効かない場所へ、なめらかに移行します（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## よくあるミス

??? failure "画面の端で、反射が急に消える"
    **端からの距離で、フェード**を掛ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **当たった画素の色を持ってくる**
    - [x] **信頼できない所は、フェードで弱める**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [SSR Basics](index.md)
- [フォールバック](../ssr-fallback.md)
- [Cost and Roughness](cost-roughness.md)
