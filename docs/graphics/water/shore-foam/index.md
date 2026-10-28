---
title: Shore Foam
tags:
  - 描画
---

# Shore Foam

<strong>水の泡は、岸辺・波頭・航跡に出て、水の動きを見せます</strong>。<strong>泡のマスクを作り、泡テクスチャで色を付けて、合成する</strong>のが基本の流れです。このセクションでは、マスクの作り方・岸辺の泡（深度差）・波頂の泡（ヤコビアン）・泡テクスチャ・泡を残す・航跡を 1 つずつ別のページで説明します。

## 泡のマスクを作る
<strong>泡は、「0 なら泡なし、1 なら泡で真っ白」のマスク値</strong>として扱います。<strong>複数の原因（岸辺・波頂・航跡）のマスクを足し合わせ</strong>、最後にテクスチャで模様を付けます。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="泡のマスク">
<text x="20" y="24" class="fig-title">泡のマスク：原因ごとに作って、足して、模様を付ける</text>
<rect x="30" y="60" width="150" height="56" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/>
<text x="105" y="84" text-anchor="middle" style="font-size:13px">岸辺</text><text x="105" y="102" text-anchor="middle" style="font-size:11px">深度差が浅い</text>
<rect x="30" y="130" width="150" height="56" rx="6" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/>
<text x="105" y="154" text-anchor="middle" style="font-size:13px">波頂</text><text x="105" y="172" text-anchor="middle" style="font-size:11px">ヤコビアンが小さい</text>
<rect x="30" y="200" width="150" height="30" rx="6" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="105" y="220" text-anchor="middle" style="font-size:13px">航跡・衝突</text>
<line x1="180" y1="88" x2="290" y2="130" stroke="currentColor" stroke-opacity="0.6"/>
<line x1="180" y1="158" x2="290" y2="140" stroke="currentColor" stroke-opacity="0.6"/>
<line x1="180" y1="215" x2="290" y2="150" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="290" y="105" width="130" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="355" y="130" text-anchor="middle" style="font-size:13px">足して</text><text x="355" y="150" text-anchor="middle" style="font-size:13px">saturate</text>
<line x1="420" y1="135" x2="480" y2="135" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="480" y="105" width="130" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="545" y="130" text-anchor="middle" style="font-size:13px">泡テクスチャで</text><text x="545" y="150" text-anchor="middle" style="font-size:13px">模様を付ける</text>
<line x1="610" y1="135" x2="660" y2="135" stroke="currentColor" stroke-opacity="0.6"/>
<rect x="660" y="105" width="90" height="60" rx="6" fill="none" stroke="currentColor"/>
<text x="705" y="140" text-anchor="middle" style="font-size:13px">色に足す</text>
</svg>

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Shore Foam: Depth Difference](shore-depth.md) | 深度差で作る |
| [Crest Foam: The Jacobian](crest-jacobian.md) | ヤコビアンで作る |
| [Foam Textures and Compositing](foam-texture.md) | 見た目の作り方 |
| [Persistent Foam](foam-history.md) | 履歴で、ゆっくり消す |
| [Wakes and Collisions](wake.md) | 船・物が作る泡 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 泡のマスク × テクスチャ
    - [x] 深度差とヤコビアンで、位置を決める

## 参考

- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）
- Jensen, Golias, "Deep-Water Animation and Rendering", Gamasutra, 2001（海の描画。泡、波頭）
- Vlachos, "Water Flow in Portal 2", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games（フロー マップと、2 位相の繰り返し）
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015

## 関連ページ

- [Water](../index.md)
- [Water Waves](../waves/index.md)
- [Water Interaction](../interaction/index.md)
