---
title: Combining with SSR
tags:
  - 描画
---

# Combining with SSR

**プローブは安くて安定、SSR は細かく正確ですが、画面外が映らない**ので、**両者を組み合わせる**のが**現在の標準**です。**SSR が当たった所は SSR、外れた所はプローブ**、という**順で、重ねます**。このページでは、**使い分けと、長所・短所**を説明します。

!!! tip "ポイント"
    - **SSR の結果を優先し、信頼度が低い所は、プローブで埋める**。
    - **境界は、信頼度でなめらかにブレンド**。
    - **プローブだけでも、最低限の反射が出る**ので、**安全網**になる。
    - **プローブは、安い・安定・画面外も映る。ただし、視差のずれ・更新が課題**。

## SSR と組み合わせる
**プローブは遠くの粗い反射**、**SSR は近くの細かい映り込み**が得意です。**組み合わせる**のが一般的です（[SSR Fallback and Compositing](../ssr-fallback.md)）。

それぞれが得意な範囲は、はっきり分かれています。遠景や粗い反射は<strong>プローブ</strong>、近くの細かい反射（足元や接地部）は <strong>SSR</strong>、平面（水面や鏡）は<strong>平面反射</strong>が向いています。

## 長所と短所
プローブの長所は、キューブマップを引くだけで安いこと、あらゆる形の面に使えること、粗さにミップで対応できること、画面外の景色も映せることです。短所は、位置が 1 点に固定されるため視差のずれが出ること、動く物や変化するシーンを映せない（更新が必要）こと、そこにあるはずの物がプローブに写り込んでしまう自己反射、そして接地部の細かい反射（足元の映り込み）が出ないことです。

### 組み合わせの設計

SSR とプローブの合成は、<strong>信頼度</strong>で行います。SSR が当たりを見つけて、画面の端でも厚みも問題ないなら、信頼度は高く、SSR の色を使います。信頼度が下がるにつれて、プローブの色を混ぜていきます。プローブは常に計算しておき、`result = lerp(probe, ssr, confidence)` で合成します。こうすると、SSR が外れた画素でも、最低限の反射（プローブ）が常にあるので、画面が黒く抜けることがありません。プローブは SSR の失敗を隠す<strong>安全網</strong>の役目を担っています（[SSR Fallback and Compositing](../ssr-fallback.md)）。

## よくあるミス

??? failure "SSR の外れた所が黒くなる"
    **プローブを、フォールバック**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **SSR ＋ プローブが、標準の組み合わせ**
    - [x] **信頼度で、なめらかに切り替える**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflection Probes](index.md)
- [フォールバック](../ssr-fallback.md)
- [反射の比較](../comparison.md)
