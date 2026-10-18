---
title: Water Waves
tags:
  - 描画
---

# Water Waves

<strong>水面の波は、頂点を動かして形を作り、法線を計算して、光の当たり方を決めます</strong>。<strong>波の作り方には、サイン波の重ね合わせ・Gerstner 波・FFT などがあり、品質とコストが違います</strong>。このセクションでは、メッシュ・サイン波・Gerstner 波・法線・波の動かし方・FFT・浮力を、1 つずつ別のページで説明します。

## 水面のメッシュ
<strong>水面は平らな格子メッシュ</strong>を<strong>用意</strong>し、頂点シェーダーで波の高さを足します。

水面メッシュの作り方は 3 つあります。<strong>平面の格子</strong>は、XZ 平面に細かい格子（例：256×256）を置き、カメラに近い所を細かくします（LOD・クリップマップ）。<strong>画面に追従する格子（Projected Grid）</strong>は、画面の画素に対応する格子を水面へ投影する方法で、画面全体を均等な密度で覆えます。<strong>カメラ中心のクリップマップ</strong>は、カメラの周りに入れ子の格子を置き（近くは細かく、遠くは粗く）、カメラに合わせて移動します。

<strong>水面は広大</strong>（地平線まで）なので<strong>カメラの周りに格子を置き、カメラと一緒に動かして、波の座標はワールド座標で計算</strong>します（水面がカメラと一緒に動いて見えないため）。

## 波の作り方の全体像

水面の波は、物理的には「流体の運動」ですが、ゲームではそれをそのまま計算せず、<strong>波の形を数式で表して、頂点の高さを決める</strong>方法を使います。方式は、品質と手間の順に並べると、次のようになります。

最も簡単なのが、サイン波の重ね合わせです（[Summing Sine Waves](sine-waves.md)）。向きや波長の違う数本のサイン波を足し合わせるだけで、海のように見える面が作れます。ただし、サイン波は上下が対称で、現実の波のように尖った波頭と平らな谷を表せません。そこで、頂点を高さだけでなく水平方向にも動かして、波頭を尖らせるのが Gerstner 波です（[Gerstner Waves](gerstner.md)）。数本から十数本で済み、軽く、見た目も良いため、ゲームの水で最もよく使われます。さらに本格的な海を求めるなら、海洋学の統計モデルを使って、無数の周波数成分から波を合成する FFT 海面です（[FFT Ocean](fft-ocean.md)）。

どの方式でも、頂点の位置を動かすだけでは細かい凹凸が足りないので、法線は別に計算して、細かい法線マップを重ねます（[Computing Normals](normals.md)）。また、船や浮きを波に合わせて動かすには、同じ波の高さを CPU 側でも求める必要があります（[Floating Objects](floating.md)）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Summing Sine Waves](sine-waves.md) | 最も簡単な波 |
| [Gerstner Waves](gerstner.md) | 尖った波頭を作る |
| [Computing Normals](normals.md) | 解析的な法線・法線マップの重ね |
| [Wave Animation Tricks](animation-tricks.md) | 繰り返しを隠す・遠くを省く |
| [FFT Ocean](fft-ocean.md) | 周波数から波を合成する |
| [Floating Objects](floating.md) | 波の高さを CPU 側でも求める |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 波は、高さの関数を時間で動かす
    - [x] 法線を正しく出して、光を当てる

## 参考

- Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の、出発点）
- Fournier, Reeves, "A Simple Model of Ocean Waves", SIGGRAPH 1986（Gerstner 波を、CG に持ち込んだ論文）
- Horvath, "Empirical Directional Wave Spectra for Computer Graphics", Digital Production Symposium 2015（方向分布を含む、実測に基づくスペクトル）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015（船の浮力・抗力・水しぶき）

## 関連ページ

- [Water](../index.md)
- [Water Shading](../shading/index.md)
- [Shore Foam](../shore-foam/index.md)
