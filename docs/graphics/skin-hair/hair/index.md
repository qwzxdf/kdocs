---
title: Hair Overview
tags:
  - 描画
---

# Hair Overview

髪は、ゲームの描画で、肌と並んで難しい対象です。難しさは、髪の<strong>構造</strong>から来ます。人間の頭には、約 10 万本の髪の毛があります。1 本の太さは、約 0.05〜0.1 mm と、<strong>画面の 1 画素よりずっと細い</strong>のが普通です。しかも、各々が半透明で、互いに影を落とし合い、光を内部で屈折・反射させます。このページでは、髪の構造と、描画で解かなければならない 4 つの問題を整理し、後のページの全体像を示します。

## 髪の構造

髪の毛 1 本は、細い円柱で、内側から順に、3 つの層でできています。

中心の<strong>髄質</strong>（メデュラ）は、空洞に近い層で、光を散乱させます。その外側の<strong>皮質</strong>（コルテックス）が、髪の大部分を占め、<strong>メラニン色素</strong>を含みます。髪の色は、このメラニンの量と種類で決まります。黒髪はメラニンが多く、金髪は少なく、白髪はほぼありません。一番外側の<strong>キューティクル</strong>（毛小皮）は、魚のうろこのように重なった薄い膜で、髪の表面を覆います。キューティクルは、<strong>わずかに傾いて</strong>重なっており、これが髪の光り方に影響します（ハイライトが、髪の軸に対して少しずれる）。

この構造から、光は髪に当たると、3 つの経路に分かれます（Marschner のモデル）。

1. R（Reflection）：キューティクルの表面で反射する。白いハイライトを作る。
2. TT（Transmission-Transmission）：髪の内部を通り抜けて反対側へ出る。髪が光に透けるときの明るさを作る。
3. TRT（Transmission-Reflection-Transmission）：内部を通り、反対側の内面で反射し、また通って出てくる。色のついた 2 本目のハイライトを作る。

髪の見た目は、この 3 つの成分の組み合わせです（[Marschner Model](marschner.md)）。

## 描画の 4 つの課題

髪の描画は、4 つの問題が重なり合っています。

<strong>1. 形</strong>。10 万本のストランドを、すべてポリゴンで描くのは、重すぎます。そこで、髪の束を板（カード）で近似するか、本数を絞ってストランドで描くか、設計が必要です（[Hair Geometry](geometry.md)）。

<strong>2. 光り方</strong>。髪は細い円柱なので、ふつうの面の反射（法線に基づく）では、光り方を表せません。髪特有の「ハイライトが髪の軸に沿って<strong>帯状</strong>に流れる」「ハイライトが 2 本ある」といった特徴を再現する、専用のシェーディングが必要です（[Kajiya-Kay](kajiya-kay.md)、[Marschner Model](marschner.md)）。

<strong>3. 透明</strong>。髪の毛 1 本 1 本は、画素より細いので、<strong>画素の一部しか覆わず</strong>、半透明に見えます。しかも、何十本も重なります。これを正しい順序で合成するのは難しく、アルファ テスト・OIT・A2C など、方式の選択が必要です（[Hair Transparency](transparency.md)）。

<strong>4. 影</strong>。髪は、<strong>自分自身に影を落とし合います</strong>。髪の束の内側は暗く、外側は明るい。この自己影がないと、髪が平らでのっぺり見えます。ところが、髪は細くて半透明なので、通常のシャドウ マップでは、うまく影が付きません（[Hair Shadows](shadows.md)）。

さらに、これらに加えて、<strong>エイリアシング</strong>の問題があります。1 画素より細い髪を描くと、ちらつき・ジャギーが出やすくなります（[Hair Anti-Aliasing](anti-aliasing.md)）。

## 技術の選び方

髪のレンダリングは、予算で大きく 3 段階に分かれます。

最も軽いのは、<strong>カード</strong>（板ポリ）に、髪の束の絵を貼る方法です。ポリゴン数は 1 つのキャラクターで数千。シェーディングは、Kajiya-Kay の簡易版。アルファ テストで切り抜き、影は簡易、という構成です。ほとんどのゲームは、ここです。

中程度は、カードを使いつつ、シェーディングを Marschner 風に高品質にし、透明の扱いに A2C や TAA を使い、髪の影に Deep Opacity Maps を足す構成です。ハイエンドなコンソール向けの、現代的な標準です。

最も重いのは、<strong>ストランド</strong>（1 本ずつ）の描画です。数万〜十万本のストランドを、線として描きます。NVIDIA の HairWorks、AMD の TressFX、Unreal Engine の Groom などがあります。物理シミュレーションで動かし、Marschner 風のシェーディングと、ボリュームの影を併用します。品質は最高ですが、GPU への負荷が大きく、主人公など限られたキャラクターに使われます。

## よくあるミス

??? failure "髪が一枚の板に見える"
    カードを<strong>層状に重ねて</strong>厚みを出す。<strong>自己影</strong>を入れる。ハイライトを髪の流れに沿わせる。

??? failure "髪のハイライトが、ベタッとした 1 つの塊になる"
    <strong>ハイライトを 2 本</strong>に分け、<strong>ノイズでずらす</strong>。髪の流れに沿った帯にする。

??? failure "髪の端が、ジャギーとちらつきでうるさい"
    <strong>TAA</strong>と、<strong>ストランドの太さを画素以上に補正する</strong>工夫を入れる（[Hair Anti-Aliasing](anti-aliasing.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 髪は<strong>細い半透明の円柱</strong>。R・TT・TRT の 3 経路で光る
    - [x] 課題は<strong>形・光り方・透明・影</strong>。さらにエイリアシング
    - [x] カード（軽い）→ カード＋高品質シェーディング → ストランド（重い）
    - [x] 自己影が髪の立体感を作る

## 参考

- Marschner, Jensen, Cammarano, Worley, Hanrahan, "Light Scattering from Human Hair Fibers"（SIGGRAPH 2003）
- Ward, Bertails, Kim, Marschner, Cani, Lin, "A Survey on Hair Modeling: Styling, Simulation, and Rendering"（IEEE TVCG, 2007）
- Scheuermann, "Hair Rendering and Shading"（GDC 2004）

## 関連ページ

- [Skin and Hair](../index.md)
- [Hair Geometry](geometry.md)
- [Kajiya-Kay](kajiya-kay.md)
- [Marschner Model](marschner.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
