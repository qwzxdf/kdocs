---
title: 3D モデルの読み込みライブラリの選び方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# 3D モデルの読み込みライブラリの選び方

3D モデルの**ファイル形式**と、**それを読み込むライブラリ**は、**種類が多い**ので、**どれを選ぶか**で、迷います。このページは、**主な形式（glTF・FBX・OBJ）の違い**と、**ライブラリ（tinygltf・fastgltf・ufbx・FBX SDK・Assimp）の選び方**をまとめます。

!!! tip "ポイント"
    - <strong>ゲームの実行時に読む形式は、glTF が第一候補</strong>（<strong>公開仕様・軽い・PBR 対応</strong>）。
    - <strong>制作データ（ツールの出力）は、FBX が多い</strong>。<strong>ufbx で読む</strong>のが手軽（<strong>FBX SDK は、導入・ライセンスが重い</strong>）。
    - <strong>本番は、ビルド時に、ゲーム専用のバイナリに変換</strong>（<strong>ベイク</strong>）。<strong>読み込みライブラリは、変換ツールの中だけ</strong>に、置くのが理想。
    - <strong>学習・小規模なら tinygltf</strong>。<strong>大量・高速なら fastgltf</strong>。
    - <strong>多くの形式を、1 つの API で</strong>読みたいなら <strong>Assimp</strong>（重い）。

## 形式の比べ

| 形式 | 作った所 | 特徴 | 向く用途 |
| --- | --- | --- | --- |
| **glTF / glb** | Khronos | **公開仕様**・**軽量**・**PBR 標準**・骨・アニメ | **ゲーム・Web の、実行時** |
| **FBX** | Autodesk | **制作ツールの標準**・アニメに強い・**仕様は非公開**・複雑 | **制作パイプラインの入口** |
| **OBJ** | Wavefront | **単純なテキスト**・**メッシュと簡単なマテリアルのみ**（骨・アニメなし） | **学習・簡単な静的モデル** |
| **独自形式** | 自作 | **そのまま読める・最速** | **製品版**（ビルド時に変換） |

（glTF の詳細は [glTF の構造](tinygltf/structure.md)、FBX は [FBX と ufbx の基本](ufbx/quickstart.md)）

## ライブラリの比べ

| ライブラリ | 形式 | 導入 | 速さ | ライセンス | 特徴 |
| --- | --- | --- | --- | --- | --- |
| <strong>[tinygltf](tinygltf/index.md)</strong> | glTF | **ヘッダのみ・簡単** | 普通 | MIT | **読み書きできる**。構造が分かりやすい。**学習向き** |
| <strong>[fastgltf](fastgltf/index.md)</strong> | glTF | vcpkg・CMake | **速い** | MIT | **simdjson**。**型が厳密**。**大きなアセット向き** |
| <strong>[ufbx](ufbx/index.md)</strong> | FBX | **2 ファイル・簡単** | **速い** | MIT / PD | **読み込みのみ**。**依存なし** |
| <strong>[FBX SDK](fbxsdk/index.md)</strong> | FBX | **手動・重い** | 普通 | **Autodesk の条件** | **公式**。**書き出し・全機能**。**ツール向き** |
| **Assimp** | **多数**（FBX・glTF・OBJ ...） | vcpkg | 普通〜遅い | BSD | **万能だが、重い**。**変換の品質は、形式ごとに差** |
| **tinyobjloader** | OBJ | ヘッダのみ | 普通 | MIT | **OBJ 専用の、軽い読み込み** |

## 選び方

<div class="anim" data-type="graph" data-label="3D モデルの読み込み：何を読むかで、選ぶライブラリが決まる">
n q 何を読む？ 0 1 hit
---
n q 何を読む？ 0 1
n g glTF 1 0 new
n f FBX 1 1 new
n o OBJ 1 2 new
l q g hit
l q f hit
l q o hit
---
n g glTF 1 0
n f FBX 1 1
n o OBJ 1 2
n tg 学習・小規模_tinygltf 2 -0.3 new
n fg 速さ重視_fastgltf 2 0.4 new
n uf 手軽_ufbx 2 1 new
n sdk 公式の機能_FBX_SDK 2 1.8 new
n ob tinyobjloader 2 2 new
l g tg hit
l g fg hit
l f uf hit
l f sdk hit
l o ob hit
</div>

| 状況 | 選ぶもの |
| --- | --- |
| <strong>ゲームの実行時に、モデルを読む（新規）</strong> | **glTF ＋ tinygltf / fastgltf** |
| **ロードを、とにかく速くしたい・大量のモデル** | **fastgltf**、または**独自形式に、ビルド時変換** |
| <strong>制作側から FBX を受け取る（実行時に読む）</strong> | **ufbx** |
| <strong>FBX の書き出し・全機能（ツール）</strong> | **FBX SDK**（ライセンスを確認） |
| **多様な形式を、1 つの API で** | **Assimp**（ツール・プロトタイプ） |
| **学習・まず動かす** | **tinygltf**（簡単）。**OBJ なら tinyobjloader** |
| **製品版** | **ビルド時に、独自のバイナリへ変換**（[ベイク](../optimize/baking.md)） |

## 製品版の、定番の構成

**ゲームの実行ファイルに、FBX の読み込みを、入れない**構成が、よく使われます。

<div class="anim" data-type="graph" data-label="アセット パイプライン：制作データを、ビルド時に、ゲーム専用の形式に変換する">
n src 制作データ_（FBX・glTF） 0 1 hit
---
n src 制作データ_（FBX・glTF） 0 1
n tool 変換ツール_（ufbx・tinygltf など） 1 1 new
n out ゲーム専用バイナリ 2 1 new
l src tool hit ビルド時
l tool out hit 出力
---
n out ゲーム専用バイナリ 2 1
n game ゲーム_（読むだけ） 3 1 new
l out game hit そのまま読む
</div>

| 利点 | 説明 |
| --- | --- |
| **ロードが、最速** | **解析なし・そのまま読める**（[シリアライズでロードを速く](../optimize/serialization-speed.md)） |
| **実行ファイルが、軽い** | **FBX SDK・ufbx を、ゲームに含めない** |
| **ライセンスの問題を、避けられる** | **FBX SDK は、ツールだけ** |
| **形式の違いを、吸収** | **入力が FBX でも glTF でも、出力は同じ** |

（[ベイク](../optimize/baking.md)、[メッシュとテクスチャ](../3d/mesh-textures.md)）

## 共通の注意

| 注意 | 説明 |
| --- | --- |
| **座標系・単位** | **形式ごとに違う**。**読み込み時に、自分の規約（右手系・Y 上・メートル）に変換**（[座標系](../3d/coordinate-systems.md)） |
| **UV の原点** | **glTF は左上**（DirectX と同じ）、**FBX・OBJ は左下**（`v = 1 - v`） |
| **巻き順** | **どれも、反時計回りが表**（`FrontCounterClockwise = TRUE`） |
| **色空間** | **ベースカラーは sRGB**、**法線・メタリック・ラフネスはリニア**（[PBR](../3d/pbr.md)） |
| **骨の重みの数** | **頂点あたり 4 つ**に制限（GPU スキニング） |
| **テクスチャのパス** | **相対パス**にして、**ゲームのフォルダー**で探す |
| **読み込み後の解放** | **ライブラリのデータは、ゲーム用にコピーして、解放** |

## 関連ページ

- [外部ライブラリ（目次）](index.md)
- [tinygltf](tinygltf/index.md)
- [fastgltf](fastgltf/index.md)
- [ufbx](ufbx/index.md)
- [FBX SDK](fbxsdk/index.md)
- [ベイク（事前計算）](../optimize/baking.md)
- [メッシュとテクスチャ](../3d/mesh-textures.md)
