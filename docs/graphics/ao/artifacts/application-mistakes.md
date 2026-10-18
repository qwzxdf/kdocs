---
title: Application Mistakes
tags:
  - 描画
---

# Application Mistakes

**AO そのものは正しくても、適用の仕方を間違えると、絵が不自然**になります。**直接光に掛けてしまう・スペキュラに掛けない・深度や座標を取り違える**などです。このページでは、**適用の間違いと、深度・座標の取り違え**を説明します。

!!! tip "ポイント"
    - **AO は、環境光（間接拡散）に掛ける**。**直接光には掛けない**。
    - **スペキュラには、スペキュラ遮蔽**。
    - **深度・座標の取り違え**：**ビュー空間とワールド空間・線形深度と非線形深度**。
    - **AO 単体を出して、確認**する。

## Misapplication (Visual Defects) {#適用の間違い見た目の不具合}

### Sunlit Areas Get Dark Too {#日向まで暗くなる}

AO は<strong>「環境光（空や周囲から来る間接光）がどれだけ遮られるか」</strong>を表す量です。太陽のような直接光が当たっている所を暗くする意味はありません。直接光の遮蔽は影（シャドウ マップ）の役目です。AO を最終色に掛けたり直接光に掛けたりすると、日向の隅まで暗くなり、「汚れた」絵になります。AO は<strong>間接拡散の項だけ</strong>に掛けます（[Usage and Misconceptions of AO](../theory/usage-misconceptions.md)）。

直接光の隅に暗さが欲しい場合は、[コンタクト シャドウ](../../shadows/contact-shadows.md)のように、直接光の遮蔽を専用に近似する手法を使います。

### Everything Looks Dull {#全体的にどんよりする}

強度や指数（`pow(ao, k)`）が強すぎる場合のほか、<strong>マルチ バウンスの補正</strong>がないことが原因です。実際の隅は、壁同士が光を反射し合うので、AO の値ほどは暗くなりません。単純に AO を掛けると暗すぎるため、アルベドに応じて明るさを戻す近似（GTAO の論文のマルチ バウンス近似）を入れます。

### Shadows Crush (Gamma) {#暗部が潰れるガンマ}

ガンマ空間（sRGB のまま）の色に AO を掛けると、掛け算の結果が物理的な意味を持たなくなり、暗部が潰れます。ライティングの掛け算は、必ず<strong>リニア空間</strong>で行います（[Gamma and HDR Output](../../postprocess/tonemapping/gamma-srgb.md)）。

### Specular Corners Glare {#鏡面反射の隅がまぶしい}

AO は拡散にだけ掛けると、隅の鏡面反射（環境マップの映り込み）が暗くならず、<strong>隙間なのに眩しい反射</strong>が出ます。鏡面にも、視線方向と粗さを考慮した<strong>スペキュラ遮蔽</strong>を掛けます（[GTAO](../gtao.md)）。

### Sky, Transparency, UI {#空半透明ui}

* <strong>空</strong>：深度が far の画素は、遮蔽の計算に入れず、AO = 1（遮蔽なし）にします。
* <strong>半透明</strong>：半透明の物は通常、深度に書かれません。深度に書くと背後が AO に影響し、書かないと AO が付きません。どちらかに割り切って、半透明は別扱いにします。
* <strong>UI やパーティクル</strong>：AO はライティングの段階で適用します。ポスト プロセスで画面全体に掛けると、UI まで暗くなります。

## Mixing Up Depth and Coordinates {#深度座標の取り違え}

AO が「完全に変」なとき、多くは<strong>空間の取り違え</strong>です。数式が合っていても、入力の空間が違えば結果は意味を失います。

* <strong>深度の線形化の式が、射影行列と合っていない</strong>。標準 Z と reverse-Z で式が違います。AO が斑模様になったら、まず線形深度を画面に出して、距離に比例して滑らかに変化しているか確認します。
* <strong>画面の y とビュー空間の y の向きが逆</strong>。画面は下向きが正、ビュー空間は上向きが正です。AO が上下反転して見えます。
* <strong>左手系・右手系の取り違え</strong>。法線をワールドからビューへ変換するとき、行列の掛け順や符号を間違えると、鏡像になります。
* <strong>`tan(fov/2)` とアスペクト比の取り違え</strong>。位置の復元で縦横のスケールを間違えると、画面の端で AO が歪みます。

デバッグでは、<strong>復元した位置を色で出し、実際のワールド座標と見比べる</strong>のが最短です。位置が正しければ、AO の式自体の誤りに絞れます。

## Common Mistakes {#よくあるミス}

??? failure "AO が画面全体を暗くして、重い絵になる"
    **環境光にだけ掛ける**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **AO は環境光にだけ掛ける**
    - [x] **深度・座標の空間をそろえる**

## References {#参考}

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## Related Pages {#関連ページ}

- [AO Artifacts](index.md)
- [Usage and Misconceptions of AO](../theory/usage-misconceptions.md)
- [PBR](../../../3d/pbr.md)
