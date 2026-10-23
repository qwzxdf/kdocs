---
title: Pre-Integrated Skin Shading
tags:
  - 描画
---

# Pre-Integrated Skin Shading

<strong>事前積分</strong>（pre-integrated）による肌のシェーディングは、SSS の効果を ライティングの段階で、LUT を 1 回引くだけで近似する方法です。画面空間のぼかしが不要で追加のレンダー ターゲットも要りません。モバイルや画面に多くのキャラクターが映るゲームで使われます。Penner と Borshukov が "Pre-Integrated Skin Shading"（GPU Pro 2、2011）で提案しました。このページでは「なぜ法線の向きと曲率だけで SSS が近似できるのか」から順に説明します。

!!! tip "ポイント"
    - SSS は光が当たる側から影の側へじんわり染み出す現象。N·L の変化が緩やかになる。
    - LUT の入力は<strong>N·L（光の向き）</strong>と<strong>曲率（表面の曲がり具合）</strong>。出力は RGB の拡散光。
    - 曲率が大きい（細い）部位ほど光が回り込んで、影側が明るくなる。
    - 法線マップの法線を色ごとにぼかす（赤は大きく、青は小さく）と肌の柔らかさが増す。
    - 安いが影の縁の赤みや薄い部位の透けは、別に処理。

!!! info "このページを読む前に"
    - [Skin Overview](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 考え方

肌に光が当たると光が当たった側で入った光が、内部で広がって <strong>影の側にも染み出します</strong>。その結果、明暗の境（N·L が 0 の付近）が、通常のランバート反射のようにくっきり切れずなだらかに暗くなります。さらに、このなだらかさは 赤の方が大きいので、境が赤く染まります。

ここで注目するのはこの広がりが、表面がどれだけ曲がっているかによって変わることです。平らな面（曲率 0）では光が当たる範囲も影になる範囲も広いので、広がった光が影の側へ染み出す量は少なくなります（染み出す先も一様に当たっている）。逆に、細く丸い面（指や耳、鼻の頭のように曲率が大きい面）では光が当たっている領域のすぐ隣が影の領域なので、光が影へ染み出す効果が大きく見えます。

つまり、SSS による影の側の明るさは N·L（光に対する向き）と曲率（表面の曲がり具合）の 2 つで、おおむね決まります。この 2 つを入力にして結果の拡散光を返す表（LUT）をあらかじめ作っておけば、実行時は引くだけで済みます。

<!-- fig:preint-lut:begin -->

<svg class="fig illust motion" data-fig="preint-lut" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-preint-lut" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">事前積分スキン: 光 × 曲率 の表で、影の境目の赤いにじみを作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">球の影の境目(N·L が 0 の付近)で、赤は広くにじみ、青は鋭く切れる。その差を、表にあらかじめ焼き込む</text>
<rect x="30" y="96" width="500" height="190" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">① 表(横 = N·L、縦 = 曲率)</text>
<rect x="104.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#000000"/></rect>
<rect x="121.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#e5e7eb;#000000"/></rect>
<rect x="138.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#000000"/></rect>
<rect x="155.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0747" values="#e5e7eb;#000000"/></rect>
<rect x="172.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#000000"/></rect>
<rect x="189.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#000000"/></rect>
<rect x="206.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#000000"/></rect>
<rect x="223.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#e5e7eb;#010000"/></rect>
<rect x="240.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#020000"/></rect>
<rect x="257.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#040000"/></rect>
<rect x="274.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#0a0100"/></rect>
<rect x="291.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0960" values="#e5e7eb;#120501"/></rect>
<rect x="308.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#1e110d"/></rect>
<rect x="325.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1013" values="#e5e7eb;#2e2525"/></rect>
<rect x="342.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#423d3d"/></rect>
<rect x="359.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#575656"/></rect>
<rect x="376.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#6f6e6e"/></rect>
<rect x="393.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1120" values="#e5e7eb;#878686"/></rect>
<rect x="410.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="427.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1173" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="444.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#d0d0d0"/></rect>
<rect x="461.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1227" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="478.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="112" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1280" values="#e5e7eb;#ffffff"/></rect>
<rect x="104.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#000000"/></rect>
<rect x="121.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#000000"/></rect>
<rect x="138.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#000000"/></rect>
<rect x="155.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#010000"/></rect>
<rect x="172.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#020000"/></rect>
<rect x="189.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#040000"/></rect>
<rect x="206.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#070000"/></rect>
<rect x="223.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1031" values="#e5e7eb;#0b0000"/></rect>
<rect x="240.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#100100"/></rect>
<rect x="257.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1084" values="#e5e7eb;#170300"/></rect>
<rect x="274.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#200700"/></rect>
<rect x="291.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1138" values="#e5e7eb;#2a0f04"/></rect>
<rect x="308.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#361b10"/></rect>
<rect x="325.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1191" values="#e5e7eb;#452b25"/></rect>
<rect x="342.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#e5e7eb;#54403d"/></rect>
<rect x="359.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#665656"/></rect>
<rect x="376.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#e5e7eb;#796e6e"/></rect>
<rect x="393.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#e5e7eb;#8d8686"/></rect>
<rect x="410.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#e5e7eb;#a39f9f"/></rect>
<rect x="427.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1351" values="#e5e7eb;#bab7b7"/></rect>
<rect x="444.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#d1d0d0"/></rect>
<rect x="461.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1404" values="#e5e7eb;#e9e8e8"/></rect>
<rect x="478.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="152" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1458" values="#e5e7eb;#ffffff"/></rect>
<rect x="104.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#080000"/></rect>
<rect x="121.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1049" values="#e5e7eb;#0d0000"/></rect>
<rect x="138.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076" values="#e5e7eb;#120000"/></rect>
<rect x="155.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#180000"/></rect>
<rect x="172.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1129" values="#e5e7eb;#1f0100"/></rect>
<rect x="189.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#270200"/></rect>
<rect x="206.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1182" values="#e5e7eb;#2f0400"/></rect>
<rect x="223.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#370700"/></rect>
<rect x="240.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1236" values="#e5e7eb;#410b00"/></rect>
<rect x="257.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1262" values="#e5e7eb;#4b1101"/></rect>
<rect x="274.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#551904"/></rect>
<rect x="291.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1316" values="#e5e7eb;#61230b"/></rect>
<rect x="308.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1342" values="#e5e7eb;#6d2f17"/></rect>
<rect x="325.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1369" values="#e5e7eb;#793d29"/></rect>
<rect x="342.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1396" values="#e5e7eb;#874e3e"/></rect>
<rect x="359.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#956056"/></rect>
<rect x="376.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1449" values="#e5e7eb;#a3756e"/></rect>
<rect x="393.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1476" values="#e5e7eb;#b38a86"/></rect>
<rect x="410.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1502" values="#e5e7eb;#c2a19f"/></rect>
<rect x="427.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1529" values="#e5e7eb;#d3b8b7"/></rect>
<rect x="444.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1556" values="#e5e7eb;#e4d0d0"/></rect>
<rect x="461.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1582" values="#e5e7eb;#f6e8e8"/></rect>
<rect x="478.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1609" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="192" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1636" values="#e5e7eb;#ffffff"/></rect>
<rect x="104.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#600300"/></rect>
<rect x="121.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1227" values="#e5e7eb;#690600"/></rect>
<rect x="138.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#e5e7eb;#720a00"/></rect>
<rect x="155.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1280" values="#e5e7eb;#7a0e00"/></rect>
<rect x="172.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#e5e7eb;#831300"/></rect>
<rect x="189.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#8c1901"/></rect>
<rect x="206.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#e5e7eb;#952002"/></rect>
<rect x="223.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1387" values="#e5e7eb;#9d2803"/></rect>
<rect x="240.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#e5e7eb;#a63106"/></rect>
<rect x="257.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1440" values="#e5e7eb;#af3a0b"/></rect>
<rect x="274.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#b74412"/></rect>
<rect x="291.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1493" values="#e5e7eb;#c0501b"/></rect>
<rect x="308.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1520" values="#e5e7eb;#c85c28"/></rect>
<rect x="325.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1547" values="#e5e7eb;#d06937"/></rect>
<rect x="342.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1573" values="#e5e7eb;#d97748"/></rect>
<rect x="359.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#e1865c"/></rect>
<rect x="376.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1627" values="#e5e7eb;#e99571"/></rect>
<rect x="393.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1653" values="#e5e7eb;#f1a688"/></rect>
<rect x="410.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1680" values="#e5e7eb;#f9b79f"/></rect>
<rect x="427.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1707" values="#e5e7eb;#ffcab8"/></rect>
<rect x="444.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1733" values="#e5e7eb;#ffddd0"/></rect>
<rect x="461.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1760" values="#e5e7eb;#fff1e8"/></rect>
<rect x="478.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1787" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="232" width="17.3" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1813" values="#e5e7eb;#ffffff"/></rect>
<text x="98" y="138" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">曲率 0.25</text>
<text x="98" y="178" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">曲率 0.50</text>
<text x="98" y="218" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">曲率 1.00</text>
<text x="98" y="258" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">曲率 2.00</text>
<text x="104" y="282" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">← 影(−1)</text>
<text x="512" y="282" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">光が当たる(+1)→</text>
<rect x="560" y="96" width="370" height="190" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="560" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">② 影の境目付近の明るさ(曲率 1)</text>
<line x1="745.0" y1="112.0" x2="745.0" y2="262.0" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="745.0" y="276.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">N·L = 0(影の境目)</text>
<path d="M580.0,262.0 L585.59,262.0 L591.19,262.0 L596.78,262.0 L602.37,262.0 L607.97,262.0 L613.56,262.0 L619.15,262.0 L624.75,262.0 L630.34,262.0 L635.93,262.0 L641.53,262.0 L647.12,262.0 L652.71,262.0 L658.31,262.0 L663.9,262.0 L669.49,262.0 L675.08,262.0 L680.68,262.0 L686.27,262.0 L691.86,262.0 L697.46,262.0 L703.05,262.0 L708.64,262.0 L714.24,262.0 L719.83,262.0 L725.42,262.0 L731.02,262.0 L736.61,262.0 L742.2,262.0 L747.8,259.46 L753.39,254.37 L758.98,249.29 L764.58,244.2 L770.17,239.12 L775.76,234.03 L781.36,228.95 L786.95,223.86 L792.54,218.78 L798.14,213.69 L803.73,208.61 L809.32,203.53 L814.92,198.44 L820.51,193.36 L826.1,188.27 L831.69,183.19 L837.29,178.1 L842.88,173.02 L848.47,167.93 L854.07,162.85 L859.66,157.76 L865.25,152.68 L870.85,147.59 L876.44,142.51 L882.03,137.42 L887.63,132.34 L893.22,127.25 L898.81,122.17 L904.41,117.08 L910.0,112.0" fill="none" stroke="#64748b" stroke-width="3" stroke-dasharray="6 5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/></path>
<text x="700" y="130" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b" opacity="0">灰の破線 = ふつうの拡散(境目で急に 0)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/></text>
<path d="M580.0,259.18 L585.59,258.26 L591.19,257.28 L596.78,256.25 L602.37,255.17 L607.97,254.04 L613.56,252.86 L619.15,251.62 L624.75,250.33 L630.34,249.0 L635.93,247.6 L641.53,246.15 L647.12,244.65 L652.71,243.09 L658.31,241.48 L663.9,239.82 L669.49,238.1 L675.08,236.33 L680.68,234.5 L686.27,232.62 L691.86,230.68 L697.46,228.7 L703.05,226.65 L708.64,224.54 L714.24,222.37 L719.83,220.16 L725.42,217.88 L731.02,215.56 L736.61,213.18 L742.2,210.75 L747.8,208.25 L753.39,205.7 L758.98,203.08 L764.58,200.42 L770.17,197.7 L775.76,194.93 L781.36,192.11 L786.95,189.23 L792.54,186.29 L798.14,183.29 L803.73,180.23 L809.32,177.12 L814.92,173.96 L820.51,170.74 L826.1,167.47 L831.69,164.15 L837.29,160.77 L842.88,157.34 L848.47,153.85 L854.07,150.31 L859.66,146.72 L865.25,143.06 L870.85,139.36 L876.44,135.62 L882.03,131.8 L887.63,127.95 L893.22,124.04 L898.81,120.08 L904.41,116.07 L910.0,112.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;1.0000" values="0;0;1;1"/></path>
<path d="M580.0,262.0 L585.59,262.0 L591.19,262.0 L596.78,261.99 L602.37,261.98 L607.97,261.97 L613.56,261.95 L619.15,261.91 L624.75,261.85 L630.34,261.78 L635.93,261.68 L641.53,261.54 L647.12,261.36 L652.71,261.13 L658.31,260.84 L663.9,260.48 L669.49,260.04 L675.08,259.51 L680.68,258.88 L686.27,258.15 L691.86,257.29 L697.46,256.3 L703.05,255.17 L708.64,253.87 L714.24,252.41 L719.83,250.78 L725.42,248.98 L731.02,247.01 L736.61,244.86 L742.2,242.52 L747.8,239.97 L753.39,237.23 L758.98,234.3 L764.58,231.19 L770.17,227.9 L775.76,224.44 L781.36,220.82 L786.95,217.03 L792.54,213.08 L798.14,208.98 L803.73,204.76 L809.32,200.41 L814.92,195.95 L820.51,191.4 L826.1,186.75 L831.69,182.02 L837.29,177.23 L842.88,172.37 L848.47,167.47 L854.07,162.53 L859.66,157.54 L865.25,152.53 L870.85,147.5 L876.44,142.45 L882.03,137.39 L887.63,132.32 L893.22,127.25 L898.81,122.17 L904.41,117.08 L910.0,112.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2754;0.2756;1.0000" values="0;0;1;1"/></path>
<path d="M580.0,262.0 L585.59,262.0 L591.19,262.0 L596.78,262.0 L602.37,262.0 L607.97,262.0 L613.56,262.0 L619.15,262.0 L624.75,262.0 L630.34,262.0 L635.93,262.0 L641.53,262.0 L647.12,262.0 L652.71,262.0 L658.31,262.0 L663.9,262.0 L669.49,262.0 L675.08,261.99 L680.68,261.99 L686.27,261.97 L691.86,261.93 L697.46,261.86 L703.05,261.73 L708.64,261.5 L714.24,261.11 L719.83,260.52 L725.42,259.66 L731.02,258.46 L736.61,256.87 L742.2,254.84 L747.8,252.3 L753.39,249.24 L758.98,245.74 L764.58,241.86 L770.17,237.64 L775.76,233.15 L781.36,228.45 L786.95,223.6 L792.54,218.64 L798.14,213.63 L803.73,208.58 L809.32,203.51 L814.92,198.44 L820.51,193.35 L826.1,188.27 L831.69,183.19 L837.29,178.1 L842.88,173.02 L848.47,167.93 L854.07,162.85 L859.66,157.76 L865.25,152.68 L870.85,147.59 L876.44,142.51 L882.03,137.42 L887.63,132.34 L893.22,127.25 L898.81,122.17 L904.41,117.08 L910.0,112.0" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3287;0.3289;1.0000" values="0;0;1;1"/></path>
<circle cx="580.0" cy="259.18" r="5.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="580;580;585.59;591.19;596.78;602.37;607.97;613.56;619.15;624.75;630.34;635.93;641.53;647.12;652.71;658.31;663.9;669.49;675.08;680.68;686.27;691.86;697.46;703.05;708.64;714.24;719.83;725.42;731.02;736.61;742.2;747.8;753.39;758.98;764.58;770.17;775.76;781.36;786.95;792.54;798.14;803.73;809.32;814.92;820.51;826.1;831.69;837.29;842.88;848.47;854.07;859.66;865.25;870.85;876.44;882.03;887.63;893.22;898.81;904.41;910;910"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="259.18;259.18;258.26;257.28;256.25;255.17;254.04;252.86;251.62;250.33;249;247.6;246.15;244.65;243.09;241.48;239.82;238.1;236.33;234.5;232.62;230.68;228.7;226.65;224.54;222.37;220.16;217.88;215.56;213.18;210.75;208.25;205.7;203.08;200.42;197.7;194.93;192.11;189.23;186.29;183.29;180.23;177.12;173.96;170.74;167.47;164.15;160.77;157.34;153.85;150.31;146.72;143.06;139.36;135.62;131.8;127.95;124.04;120.08;116.07;112;112"/></circle>
<circle cx="580.0" cy="262.0" r="5.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="580;580;585.59;591.19;596.78;602.37;607.97;613.56;619.15;624.75;630.34;635.93;641.53;647.12;652.71;658.31;663.9;669.49;675.08;680.68;686.27;691.86;697.46;703.05;708.64;714.24;719.83;725.42;731.02;736.61;742.2;747.8;753.39;758.98;764.58;770.17;775.76;781.36;786.95;792.54;798.14;803.73;809.32;814.92;820.51;826.1;831.69;837.29;842.88;848.47;854.07;859.66;865.25;870.85;876.44;882.03;887.63;893.22;898.81;904.41;910;910"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="262;262;262;262;261.99;261.98;261.97;261.95;261.91;261.85;261.78;261.68;261.54;261.36;261.13;260.84;260.48;260.04;259.51;258.88;258.15;257.29;256.3;255.17;253.87;252.41;250.78;248.98;247.01;244.86;242.52;239.97;237.23;234.3;231.19;227.9;224.44;220.82;217.03;213.08;208.98;204.76;200.41;195.95;191.4;186.75;182.02;177.23;172.37;167.47;162.53;157.54;152.53;147.5;142.45;137.39;132.32;127.25;122.17;117.08;112;112"/></circle>
<circle cx="580.0" cy="262.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="580;580;585.59;591.19;596.78;602.37;607.97;613.56;619.15;624.75;630.34;635.93;641.53;647.12;652.71;658.31;663.9;669.49;675.08;680.68;686.27;691.86;697.46;703.05;708.64;714.24;719.83;725.42;731.02;736.61;742.2;747.8;753.39;758.98;764.58;770.17;775.76;781.36;786.95;792.54;798.14;803.73;809.32;814.92;820.51;826.1;831.69;837.29;842.88;848.47;854.07;859.66;865.25;870.85;876.44;882.03;887.63;893.22;898.81;904.41;910;910"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4000;0.4053;0.4105;0.4158;0.4211;0.4264;0.4316;0.4369;0.4422;0.4475;0.4527;0.4580;0.4633;0.4685;0.4738;0.4791;0.4844;0.4896;0.4949;0.5002;0.5055;0.5107;0.5160;0.5213;0.5266;0.5318;0.5371;0.5424;0.5476;0.5529;0.5582;0.5635;0.5687;0.5740;0.5793;0.5846;0.5898;0.5951;0.6004;0.6056;0.6109;0.6162;0.6215;0.6267;0.6320;0.6373;0.6426;0.6478;0.6531;0.6584;0.6637;0.6689;0.6742;0.6795;0.6847;0.6900;0.6953;0.7006;0.7058;0.7111;1.0000" values="262;262;262;262;262;262;262;262;262;262;262;262;262;262;262;262;262;262;261.99;261.99;261.97;261.93;261.86;261.73;261.5;261.11;260.52;259.66;258.46;256.87;254.84;252.3;249.24;245.74;241.86;237.64;233.15;228.45;223.6;218.64;213.63;208.58;203.51;198.44;193.35;188.27;183.19;178.1;173.02;167.93;162.85;157.76;152.68;147.59;142.51;137.42;132.34;127.25;122.17;117.08;112;112"/></circle>
<text x="40" y="322" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">球の影の境目(上 = ふつうの拡散、下 = 事前積分)</text>
<text x="40" y="354" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ふつうの拡散</text>
<rect x="150.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7467" values="#e5e7eb;#000000"/></rect>
<rect x="166.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7480" values="#e5e7eb;#000000"/></rect>
<rect x="182.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7493" values="#e5e7eb;#000000"/></rect>
<rect x="198.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7507" values="#e5e7eb;#000000"/></rect>
<rect x="214.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7520" values="#e5e7eb;#000000"/></rect>
<rect x="230.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7533" values="#e5e7eb;#000000"/></rect>
<rect x="246.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7547" values="#e5e7eb;#000000"/></rect>
<rect x="262.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7560" values="#e5e7eb;#000000"/></rect>
<rect x="278.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7573" values="#e5e7eb;#000000"/></rect>
<rect x="294.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7587" values="#e5e7eb;#000000"/></rect>
<rect x="310.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#e5e7eb;#000000"/></rect>
<rect x="326.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7613" values="#e5e7eb;#000000"/></rect>
<rect x="342.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7627" values="#e5e7eb;#000000"/></rect>
<rect x="358.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7640" values="#e5e7eb;#000000"/></rect>
<rect x="374.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7653" values="#e5e7eb;#000000"/></rect>
<rect x="390.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7667" values="#e5e7eb;#000000"/></rect>
<rect x="406.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7680" values="#e5e7eb;#000000"/></rect>
<rect x="422.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7693" values="#e5e7eb;#000000"/></rect>
<rect x="438.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7707" values="#e5e7eb;#000000"/></rect>
<rect x="454.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7720" values="#e5e7eb;#000000"/></rect>
<rect x="470.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7733" values="#e5e7eb;#000000"/></rect>
<rect x="486.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7747" values="#e5e7eb;#000000"/></rect>
<rect x="502.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7760" values="#e5e7eb;#000000"/></rect>
<rect x="518.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7773" values="#e5e7eb;#000000"/></rect>
<rect x="534.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7787" values="#e5e7eb;#050505"/></rect>
<rect x="550.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7800" values="#e5e7eb;#101010"/></rect>
<rect x="566.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7813" values="#e5e7eb;#1a1a1a"/></rect>
<rect x="582.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7827" values="#e5e7eb;#242424"/></rect>
<rect x="598.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7840" values="#e5e7eb;#2f2f2f"/></rect>
<rect x="614.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7853" values="#e5e7eb;#393939"/></rect>
<rect x="630.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7867" values="#e5e7eb;#444444"/></rect>
<rect x="646.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7880" values="#e5e7eb;#4e4e4e"/></rect>
<rect x="662.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7893" values="#e5e7eb;#595959"/></rect>
<rect x="678.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7907" values="#e5e7eb;#636363"/></rect>
<rect x="694.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7920" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="710.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7933" values="#e5e7eb;#787878"/></rect>
<rect x="726.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7947" values="#e5e7eb;#828282"/></rect>
<rect x="742.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7960" values="#e5e7eb;#8d8d8d"/></rect>
<rect x="758.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7973" values="#e5e7eb;#979797"/></rect>
<rect x="774.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7987" values="#e5e7eb;#a1a1a1"/></rect>
<rect x="790.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8000" values="#e5e7eb;#acacac"/></rect>
<rect x="806.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8013" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="822.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8027" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="838.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8040" values="#e5e7eb;#cbcbcb"/></rect>
<rect x="854.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8053" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="870.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8067" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="886.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8080" values="#e5e7eb;#eaeaea"/></rect>
<rect x="902.0" y="340.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8093" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="150" y="340" width="768.0" height="16.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="406" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">事前積分</text>
<rect x="150.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7467" values="#e5e7eb;#060000"/></rect>
<rect x="166.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7480" values="#e5e7eb;#080000"/></rect>
<rect x="182.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7493" values="#e5e7eb;#0b0000"/></rect>
<rect x="198.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7507" values="#e5e7eb;#0d0000"/></rect>
<rect x="214.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7520" values="#e5e7eb;#100000"/></rect>
<rect x="230.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7533" values="#e5e7eb;#120000"/></rect>
<rect x="246.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7547" values="#e5e7eb;#150000"/></rect>
<rect x="262.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7560" values="#e5e7eb;#180000"/></rect>
<rect x="278.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7573" values="#e5e7eb;#1c0100"/></rect>
<rect x="294.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7587" values="#e5e7eb;#1f0100"/></rect>
<rect x="310.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#e5e7eb;#220200"/></rect>
<rect x="326.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7613" values="#e5e7eb;#260200"/></rect>
<rect x="342.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7627" values="#e5e7eb;#2a0300"/></rect>
<rect x="358.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7640" values="#e5e7eb;#2e0400"/></rect>
<rect x="374.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7653" values="#e5e7eb;#320500"/></rect>
<rect x="390.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7667" values="#e5e7eb;#360700"/></rect>
<rect x="406.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7680" values="#e5e7eb;#3a0900"/></rect>
<rect x="422.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7693" values="#e5e7eb;#3f0c00"/></rect>
<rect x="438.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7707" values="#e5e7eb;#440e01"/></rect>
<rect x="454.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7720" values="#e5e7eb;#481102"/></rect>
<rect x="470.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7733" values="#e5e7eb;#4d1503"/></rect>
<rect x="486.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7747" values="#e5e7eb;#531905"/></rect>
<rect x="502.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7760" values="#e5e7eb;#581e08"/></rect>
<rect x="518.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7773" values="#e5e7eb;#5d230d"/></rect>
<rect x="534.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7787" values="#e5e7eb;#632912"/></rect>
<rect x="550.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7800" values="#e5e7eb;#692f19"/></rect>
<rect x="566.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7813" values="#e5e7eb;#6f3622"/></rect>
<rect x="582.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7827" values="#e5e7eb;#753d2b"/></rect>
<rect x="598.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7840" values="#e5e7eb;#7b4535"/></rect>
<rect x="614.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7853" values="#e5e7eb;#814d40"/></rect>
<rect x="630.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7867" values="#e5e7eb;#88564b"/></rect>
<rect x="646.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7880" values="#e5e7eb;#8f5f56"/></rect>
<rect x="662.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7893" values="#e5e7eb;#966861"/></rect>
<rect x="678.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7907" values="#e5e7eb;#9d726d"/></rect>
<rect x="694.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7920" values="#e5e7eb;#a47c78"/></rect>
<rect x="710.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7933" values="#e5e7eb;#ab8784"/></rect>
<rect x="726.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7947" values="#e5e7eb;#b2918f"/></rect>
<rect x="742.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7960" values="#e5e7eb;#ba9c9b"/></rect>
<rect x="758.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7973" values="#e5e7eb;#c2a7a6"/></rect>
<rect x="774.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7987" values="#e5e7eb;#cab2b2"/></rect>
<rect x="790.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8000" values="#e5e7eb;#d2bdbd"/></rect>
<rect x="806.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8013" values="#e5e7eb;#dac9c8"/></rect>
<rect x="822.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8027" values="#e5e7eb;#e2d4d4"/></rect>
<rect x="838.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8040" values="#e5e7eb;#ebdfdf"/></rect>
<rect x="854.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8053" values="#e5e7eb;#f4ebeb"/></rect>
<rect x="870.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8067" values="#e5e7eb;#faf6f6"/></rect>
<rect x="886.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8080" values="#e5e7eb;#fafafa"/></rect>
<rect x="902.0" y="392.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8093" values="#e5e7eb;#fafafa"/></rect>
<rect x="150" y="392" width="768.0" height="16.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8283;0.8284;1.0000" values="0;0;1;1"/><rect x="560" y="436" width="370" height="76" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="576" y="460" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">影の境目(N·L = -0.15)での色</text>
<text x="576" y="482" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">事前積分: R 0.28 / G 0.08 / B 0.01 → 赤く にじむ</text>
<text x="576" y="505" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">ふつうの拡散: R 0 / G 0 / B 0(真っ黒)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">肌の中で光が散らばるので、影の境目で赤い光が先に回り込む<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光の当たり方と曲率から、色を求める表(LUT)を、あらかじめ作る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2220;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">赤は広く、青は狭く(境目で鋭く)切れる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;0.3998;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">N·L を動かすと、境目の外でも、赤がまだ残っている<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;0.7465;0.7467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">球に当てると、ふつうの拡散は硬く切れて、事前積分は、赤い帯がにじむ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7465;0.7467;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:preint-lut:end -->

## LUT の作り方

LUT は次のように計算します。曲率は半径 r の球で表します（曲率 = 1/r）。球の表面の点 P を考え光の方向と法線のなす角 θ（N·L = cos θ）を決めます。点 P での拡散光は <strong>球の全表面に当たった光が、拡散プロファイル R_d で P に広がってきた量の合計</strong>です。

球上の各点 Q は光に対する角度が違いその点での直接光は、`max(0, cos(θ + x))`（x は P から Q までの角度）に比例します。P と Q の距離は `2r sin(x/2)` です。したがって P での拡散光は次の積分で表されます。

<div class="formula">D(θ, r) = ∫_{−π}^{π} max(0, cos(θ + x)) · R_d(2r sin(x/2)) dx　／　∫_{−π}^{π} R_d(2r sin(x/2)) dx</div>

分母は正規化でプロファイルの合計を 1 にします。この積分を θ（または N·L）と 1/r の組み合わせごとに、RGB の各チャンネルについて計算し、2 次元のテクスチャに書き込みます。横軸が N·L（−1〜1 を 0〜1 に変換）、縦軸が曲率です。各テクセルに RGB の拡散光の値が入ります。この計算はオフラインで行い 1 つの LUT をすべての肌に共通で使います（プロファイルは肌の種類で共通とします）。

## 曲率の求め方

実行時に必要な「曲率」は画素ごとに次のように求めます。<strong>法線の変化量</strong>と 位置の変化量の比です。

<div class="formula">曲率 = ‖Δn‖ / ‖Δp‖　（隣の画素との差を使う）</div>

法線が速く変わる場所（鼻の頭）は曲率が大きく、ほぼ変わらない場所（頬の平らな部分）は曲率が小さくなります。ピクセル シェーダーで `ddx` と `ddy` を使って求めます。

```hlsl
float curvature = saturate(length(fwidth(normal)) / length(fwidth(world_pos)) * kCurvatureScale);
```

画素単位の計算はノイズが出やすいので、頂点ごとに曲率を計算して頂点属性に持たせたり事前に曲率のテクスチャを焼いておいたりする方法もあります。

## 実行時の計算

LUT を引く部分は次のようになります。

```hlsl
float3 SkinDiffuse(float3 n, float3 l, float curvature, float3 albedo, float3 light_color) {
  float n_dot_l = dot(n, l);
  float2 lut_uv = float2(n_dot_l * 0.5 + 0.5, curvature);
  float3 diffuse = skin_lut.SampleLevel(linear_clamp, lut_uv, 0).rgb;
  return diffuse * albedo * light_color;
}
```

通常のランバートでは `saturate(n_dot_l)` を使いますが、ここでは負の N·L（影の側）まで LUT に含めます。LUT の値は N·L が 0 を下回っても 0 にならず赤の成分がゆっくり減衰します。これが影の縁の赤みを作ります。

## 法線の扱い：色ごとにぼかす

さらに、事前積分の論文には <strong>法線の扱い</strong>の工夫があります。肌の表面の細かい凹凸（毛穴、小じわ）は法線マップで表されます。ところが、SSS で光が広がると 細かい凹凸の陰影は、赤の光では弱く青の光では強く見えます（赤は広がるので、細部が平均されてなめらかになります）。

そこで、法線を色ごとに別々にぼかします。具体的にはジオメトリの法線（なめらか）と法線マップの法線（細かい）の 2 つを用意します。次に、チャンネルごとに 2 つの法線を混ぜる割合を変えます。青は法線マップの法線を多めに使い（細部が強く出る）、赤はジオメトリの法線を多めに使います（細部が弱く出る）。そして、各チャンネルで別々の法線を使って、LUT を引きます。

```hlsl
float3 n_geom = normalize(input.normal);
float3 n_map = ApplyNormalMap(n_geom, normal_map_sample);
float3 n_r = normalize(lerp(n_geom, n_map, 0.3));
float3 n_g = normalize(lerp(n_geom, n_map, 0.7));
float3 n_b = n_map;
float3 diffuse;
diffuse.r = skin_lut.SampleLevel(linear_clamp, float2(dot(n_r, l) * 0.5 + 0.5, curvature), 0).r;
diffuse.g = skin_lut.SampleLevel(linear_clamp, float2(dot(n_g, l) * 0.5 + 0.5, curvature), 0).g;
diffuse.b = skin_lut.SampleLevel(linear_clamp, float2(dot(n_b, l) * 0.5 + 0.5, curvature), 0).b;
```

この小さな工夫で毛穴の凹凸の陰影が、青ではくっきり赤ではぼんやり見える現実の肌の柔らかさに近づきます。

## 長所と限界

事前積分の長所は軽いことです。画素ごとに LUT を引くだけで、別のパスも追加のレンダー ターゲットも不要です。SSS のぼかしにある輪郭をまたぐにじみの問題もありません。ライトごとに独立して計算できるので、複数のライトにも素直に使えます。

限界もあります。まず、LUT が引くのは <strong>N·L の変化のなだらかさ</strong>だけです。影（シャドウ マップ）で隠れた領域の周りに染み出す効果や 影の縁の赤みは表せません。これは影がライティングの前に決まっていて、周りの画素の情報を参照しないためです。次に、薄い部位の透け（耳に光を当てると赤く透ける）は、別の処理が必要です（[Thin Translucency](thin-translucency.md)）。そして、曲率の推定が粗いと顔の表面でムラが出ることがあります。

そのため、現代のゲームでは事前積分と画面空間のぼかしを併用することもよくあります。事前積分で N·L のなだらかさを担当し、画面空間のぼかしで影の縁などの広い範囲の散乱を担当します。

## よくあるミス

??? failure "曲率をそのまま使って、顔の表面がまだら模様になる"
    画素ごとの `fwidth` はノイズが出る。<strong>頂点ごとに曲率を計算して補間する</strong>か 曲率のテクスチャを焼く。

??? failure "LUT のアドレスが端で折り返して、境が見える"
    LUT のサンプラーは clamp。LUT の端のテクセルを半テクセル内側から使う。

??? failure "影の縁に赤みが出ない"
    事前積分はシャドウ マップの影の縁には効かない。影の縁の赤みは 影の判定にぼかしを掛けるか画面空間の SSS を併用する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力は<strong>N·L</strong>と曲率。LUT を 1 回引くだけで、SSS のなだらかさが出る
    - [x] LUT は球の表面で拡散プロファイルを積分して、事前に作る
    - [x] 法線を色ごとにぼかすと肌の柔らかさが増す
    - [x] 軽いが影の縁の赤みと薄い部位の透けは別に処理する

## 参考

- Penner, Borshukov, "Pre-Integrated Skin Shading"（GPU Pro 2, 2011）
- Penner, "Pre-Integrated Skin Shading"（SIGGRAPH 2011 Advances in Real-Time Rendering in Games）
- d'Eon, Luebke, "Advanced Techniques for Realistic Real-Time Skin Rendering"（GPU Gems 3, 2007）

## 関連ページ

- [Skin Overview](index.md)
- [Subsurface Scattering](subsurface-theory.md)
- [Separable SSS](screen-space-sss.md)
- [Thin Translucency](thin-translucency.md)
