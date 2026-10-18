---
title: Skin and Hair
tags:
  - 描画
---

# Skin and Hair

ゲームの主役は、たいてい人間（またはそれに近いキャラクター）です。プレイヤーの目は、顔と髪に最初に向かいます。しかも人間は、人の顔を見慣れているので、**わずかな不自然さにも気づきます**。「不気味の谷」と呼ばれる現象です。肌がプラスチックのように硬く見える、髪が一枚の板に見える、目が死んだように見える。これらは、**光の物理を省略した結果**です。

肌も髪も、**光が表面で跳ね返るだけでなく、物の内部を通る**素材です。肌では、光が皮膚の中へ入り、散らばり、少し離れた場所から出てきます。髪では、光が 1 本の細い繊維の中を通り抜け、反対側から出てきます。これを無視して「表面の色にライトを当てるだけ」で描くと、どれだけテクスチャが高精細でも、のっぺりとしたマネキンになります。

このセクションでは、その二つの素材を、**原典の論文の考え方に沿って**順に説明します。

!!! tip "ポイント"
    - 肌は<strong>表面の反射（鏡面）</strong>と<strong>内部で散らばった光（次表面散乱：SSS）</strong>の合計。**SSS を省くと、肌がプラスチックになる**。
    - SSS のコストと品質のバランスは、**事前積分（軽い）→ 画面空間の分離ぼかし（標準）→ ガウス和（重い）**の順。
    - 耳や鼻のように薄い所は、**光が裏から透ける**。厚みを測って、別に処理する。
    - 髪は**細い円柱**。**Kajiya-Kay（軽い）**か**Marschner（本格的）**で光る。ハイライトは**2 本**（白と色付き）。
    - 髪の描画は**透明・影・エイリアシング**の三重苦。**ストランド（1 本ずつ）**か**カード（板）**かで、設計が大きく変わる。
    - 目は**角膜の屈折**で虹彩が見える。**湿った表面の反射**が「生きている目」を作る。

## このセクションの流れ

肌の側から順に読むのがお勧めです。まず[Skin Overview](skin/index.md)で、肌の層構造と、光の振る舞いを知ります。次に[次表面散乱の理論](skin/subsurface-theory.md)で、「なぜ内部を通る光を計算するのか」を数式で理解します。そのうえで、実装の道具である[拡散プロファイル](skin/diffusion-profile.md)、画面空間の[分離ぼかし](skin/screen-space-sss.md)、軽量な[事前積分](skin/pre-integrated.md)を比べます。さらに、耳のような薄い部分の[透過](skin/thin-translucency.md)、肌の[鏡面反射](skin/specular.md)、毛穴やしわの[微細なディテール](skin/micro-detail.md)、そして[目](skin/eyes.md)を扱います。

髪は、[Hair Overview](hair/index.md)から入ります。形の作り方（[カードとストランド](hair/geometry.md)）、光り方の式（[Kajiya-Kay](hair/kajiya-kay.md)、[Marschner](hair/marschner.md)）、透明の扱い（[Hair Transparency](hair/transparency.md)）、影（[Hair Shadows](hair/shadows.md)）、エイリアシング（[Hair Anti-Aliasing](hair/anti-aliasing.md)）の順です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Skin Overview](skin/index.md) | 肌の層構造・光の振る舞い・全体の組み立て |
| [Subsurface Scattering](skin/subsurface-theory.md) | BSSRDF・拡散近似・双極子モデル |
| [Diffusion Profiles](skin/diffusion-profile.md) | ガウス和・プロファイルの作り方 |
| [Separable SSS](skin/screen-space-sss.md) | 画面空間のぼかしで SSS を近似 |
| [Pre-Integrated Skin Shading](skin/pre-integrated.md) | 曲率と N·L から LUT を引く軽量な方法 |
| [Thin Translucency](skin/thin-translucency.md) | 耳・指・鼻の透け |
| [Skin Specular](skin/specular.md) | 皮脂の二重ローブ・Fresnel |
| [Skin Micro-Detail](skin/micro-detail.md) | 毛穴・しわ・血流 |
| [Eye Rendering](skin/eyes.md) | 角膜の屈折・虹彩・涙の膜 |
| [Hair Overview](hair/index.md) | 髪の構造と描画の課題 |
| [Hair Geometry](hair/geometry.md) | カードとストランド |
| [Kajiya-Kay](hair/kajiya-kay.md) | 軽量なハイライトの式 |
| [Marschner Model](hair/marschner.md) | R・TT・TRT の 3 つのローブ |
| [Hair Transparency](hair/transparency.md) | アルファ・OIT・ソート |
| [Hair Shadows](hair/shadows.md) | Deep Opacity Maps |
| [Hair Anti-Aliasing](hair/anti-aliasing.md) | 1 画素より細い髪の扱い |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 肌は<strong>表面反射 ＋ 内部散乱</strong>。<strong>内部散乱を省くとプラスチックになる</strong>
    - [x] 髪は<strong>細い円柱</strong>。<strong>2 本のハイライト</strong>と<strong>透け</strong>が命
    - [x] どちらも<strong>「安い近似」の階段</strong>があり、<strong>予算で選ぶ</strong>

## 関連ページ

- [描画](../index.md)
- [PBR](../../3d/pbr.md)
- [Shadows](../shadows/index.md)
- [Character Shadows and Color](../shadows/special-cases/character-shadows.md)
- [Cel Shading](../postprocess/stylized/cel-shading.md)
