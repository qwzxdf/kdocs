---
title: 3D モデルの読み込みライブラリの選び方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# 3D モデルの読み込みライブラリの選び方

3D モデルの**ファイル形式**と、それを読み込むライブラリは、種類が多いので、どれを選ぶかで、迷います。このページは、主な形式（glTF・FBX・OBJ）の違いと、ライブラリ（tinygltf・fastgltf・ufbx・FBX SDK・Assimp）の選び方をまとめます。

!!! tip "ポイント"
    - <strong>ゲームの実行時に読む形式は、glTF が第一候補</strong>（<strong>公開仕様・軽い・PBR 対応</strong>）。
    - 制作データ（ツールの出力）は、FBX が多い。ufbx で読むのが手軽（FBX SDK は、導入・ライセンスが重い）。
    - 本番は、ビルド時に、ゲーム専用のバイナリに変換（ベイク）。読み込みライブラリは、変換ツールの中だけに、置くのが理想。
    - 学習・小規模なら tinygltf。大量・高速なら fastgltf。
    - 多くの形式を、1 つの API で読みたいなら Assimp（重い）。

!!! info "このページを読む前に"
    - [libs/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [外部ライブラリの入れ方](../vs/libraries.md)（外部ライブラリの入れ方（vcpkg））

## 形式の比べ

形式の選び方は、「**誰が作って、どこで使うか**」で決まります。制作ツール（Blender や Maya）から出てくる形式と、ゲームが実行時に読む形式は、別のものにするのが普通です。制作用は情報が多くて柔軟ですが重く、実行用は軽くて読みやすいことが求められるからです。以下で 4 つの形式の特徴を比べます。

| 形式 | 作った所 | 特徴 | 向く用途 |
| --- | --- | --- | --- |
| glTF / glb | Khronos | 公開仕様・軽量・PBR 標準・ボーン・アニメ | ゲーム・Web の、実行時 |
| FBX | Autodesk | 制作ツールの標準・アニメに強い・仕様は非公開・複雑 | 制作パイプラインの入口 |
| OBJ | Wavefront | 単純なテキスト・メッシュと簡単なマテリアルのみ（ボーン・アニメなし） | 学習・簡単な静的モデル |
| 独自形式 | 自作 | そのまま読める・最速 | 製品版（ビルド時に変換） |

（glTF の詳細は [glTF の構造](tinygltf/structure.md)、FBX は [FBX と ufbx の基本](ufbx/quickstart.md)）

## ライブラリの比べ

形式が決まったら、読み込むライブラリを選びます。判断軸は、**導入の簡単さ・読み込みの速さ・ライセンス**の 3 つです。学習なら導入が簡単なもの、大量のモデルを扱うなら速いもの、商用で使うならライセンスを最優先で見ます。

| ライブラリ | 形式 | 導入 | 速さ | ライセンス | 特徴 |
| --- | --- | --- | --- | --- | --- |
| [tinygltf](tinygltf/index.md) | glTF | ヘッダのみ・簡単 | 普通 | MIT | 読み書きできる。構造が分かりやすい。学習向き |
| [fastgltf](fastgltf/index.md) | glTF | vcpkg・CMake | 速い | MIT | simdjson。型が厳密。大きなアセット向き |
| [ufbx](ufbx/index.md) | FBX | 2 ファイル・簡単 | 速い | MIT / PD | 読み込みのみ。依存なし |
| [FBX SDK](fbxsdk/index.md) | FBX | 手動・重い | 普通 | Autodesk の条件 | 公式。書き出し・全機能。ツール向き |
| Assimp | 多数（FBX・glTF・OBJ ...） | vcpkg | 普通〜遅い | BSD | 万能だが、重い。変換の品質は、形式ごとに差 |
| tinyobjloader | OBJ | ヘッダのみ | 普通 | MIT | OBJ 専用の、軽い読み込み |

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
| <strong>ゲームの実行時に、モデルを読む（新規）</strong> | glTF ＋ tinygltf / fastgltf |
| ロードを、とにかく速くしたい・大量のモデル | fastgltf、または独自形式に、ビルド時変換 |
| 制作側から FBX を受け取る（実行時に読む） | ufbx |
| FBX の書き出し・全機能（ツール） | FBX SDK（ライセンスを確認） |
| 多様な形式を、1 つの API で | Assimp（ツール・プロトタイプ） |
| 学習・まず動かす | tinygltf（簡単）。OBJ なら tinyobjloader |
| 製品版 | ビルド時に、独自のバイナリへ変換（[ベイク](../optimize/baking.md)） |

## 製品版の、定番の構成

**ゲームの実行ファイルに、FBX の読み込みを、入れない**構成が、よく使われます。

<svg class="fig flow" viewBox="0 0 1034 112" role="img" aria-label="アセット パイプライン：制作データを、ビルド時に、ゲーム専用の形式に変換する"><defs><marker id="fl43356" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アセット パイプライン：制作データを、ビルド時に、ゲーム専用の形式に変換する</text><line x1="231.0" y1="64.0" x2="289.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="260.0" y="58.0" text-anchor="middle" style="font-size:12px">ビルド時</text><line x1="569.0" y1="64.0" x2="627.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="598.0" y="58.0" text-anchor="middle" style="font-size:12px">出力</text><line x1="785.0" y1="64.0" x2="843.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="814.0" y="58.0" text-anchor="middle" style="font-size:12px">そのまま読む</text><rect x="28.0" y="44.0" width="200" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="128.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">制作データ （FBX・glTF）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="292.0" y="44.0" width="274" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="429.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ufbx・tinygltf など）</text><circle cx="294.0" cy="46.0" r="10" fill="#2ea043"/><text x="294.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="630.0" y="44.0" width="152" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="706.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム専用バイナリ</text><circle cx="632.0" cy="46.0" r="10" fill="#2ea043"/><text x="632.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="846.0" y="44.0" width="160" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="926.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム （読むだけ）</text><circle cx="848.0" cy="46.0" r="10" fill="#e5a828"/><text x="848.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 利点 | 説明 |
| --- | --- |
| ロードが、最速 | 解析なし・そのまま読める（[シリアライズでロードを速く](../optimize/serialization-speed.md)） |
| 実行ファイルが、軽い | FBX SDK・ufbx を、ゲームに含めない |
| ライセンスの問題を、避けられる | FBX SDK は、ツールだけ |
| 形式の違いを、吸収 | 入力が FBX でも glTF でも、出力は同じ |

（[ベイク](../optimize/baking.md)、[メッシュとテクスチャ](../3d/mesh-textures.md)）

## 共通の注意

| 注意 | 説明 |
| --- | --- |
| **座標系・単位** | 形式ごとに違う。読み込み時に、右手系・Y 上・メートルにそろえ、ルートに X 反転の行列を掛けて左手系にする（[座標系](../gamemath/coordinate-systems.md)） |
| UV の原点 | glTF は左上（DirectX と同じ）、FBX・OBJ は左下（`v = 1 - v`） |
| 巻き順 | どれも、反時計回りが表。このサイトは時計回りが表なので、左手系へ変換するとき、インデックスを入れ替える |
| 色空間 | ベースカラーは sRGB、法線・メタリック・ラフネスはリニア（[PBR](../3d/pbr.md)） |
| ボーンの重みの数 | 頂点あたり 4 つに制限（GPU スキニング） |
| テクスチャのパス | 相対パスにして、ゲームのフォルダーで探す |
| 読み込み後の解放 | ライブラリのデータは、ゲーム用にコピーして、解放 |

## 関連ページ

- [外部ライブラリ（目次）](index.md)
- [tinygltf](tinygltf/index.md)
- [fastgltf](fastgltf/index.md)
- [ufbx](ufbx/index.md)
- [FBX SDK](fbxsdk/index.md)
- [ベイク（事前計算）](../optimize/baking.md)
- [メッシュとテクスチャ](../3d/mesh-textures.md)
