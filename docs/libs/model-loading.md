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

<svg class="fig flow" viewBox="0 0 535 305" role="img" aria-label="3D モデルの読み込み：何を読むかで、選ぶライブラリが決まる"><defs><marker id="fl87718" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">3D モデルの読み込み：何を読むかで、選ぶライブラリが決まる</text><line x1="117.1" y1="150.2" x2="185.0" y2="112.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="127.0" y1="173.2" x2="185.0" y2="173.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="117.1" y1="196.2" x2="185.0" y2="234.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="267.0" y1="83.8" x2="325.0" y2="76.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="267.0" y1="96.4" x2="339.0" y2="109.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="267.0" y1="173.2" x2="368.5" y2="173.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="267.0" y1="187.6" x2="352.0" y2="217.4" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><line x1="267.0" y1="257.2" x2="351.5" y2="257.2" stroke="currentColor" stroke-width="2" marker-end="url(#fl87718)"/><rect x="28.0" y="153.2" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="76.0" y="173.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">何を読む？</text><circle cx="30.0" cy="155.2" r="10" fill="#4c8bf5"/><text x="30.0" y="155.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="188.0" y="69.2" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="226.0" y="89.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">glTF</text><circle cx="190.0" cy="71.2" r="10" fill="#2ea043"/><text x="190.0" y="71.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="188.0" y="153.2" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="226.0" y="173.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">FBX</text><circle cx="190.0" cy="155.2" r="10" fill="#2ea043"/><text x="190.0" y="155.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="188.0" y="237.2" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="226.0" y="257.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">OBJ</text><circle cx="190.0" cy="239.2" r="10" fill="#2ea043"/><text x="190.0" y="239.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="328.0" y="44.0" width="179" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="417.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">学習・小規模 tinygltf</text><circle cx="330.0" cy="46.0" r="10" fill="#e5a828"/><text x="330.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="342.0" y="102.8" width="151" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="417.5" y="122.8" text-anchor="middle" dominant-baseline="central" style="font-weight:600">速さ重視 fastgltf</text><circle cx="344.0" cy="104.8" r="10" fill="#e5a828"/><text x="344.0" y="104.8" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="371.5" y="153.2" width="92" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="417.5" y="173.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">手軽 ufbx</text><circle cx="373.5" cy="155.2" r="10" fill="#e5a828"/><text x="373.5" y="155.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="338.5" y="220.4" width="158" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="417.5" y="240.4" text-anchor="middle" dominant-baseline="central" style="font-weight:600">公式の機能 FBX SDK</text><circle cx="340.5" cy="222.4" r="10" fill="#e5a828"/><text x="340.5" y="222.4" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="354.5" y="237.2" width="126" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="417.5" y="257.2" text-anchor="middle" dominant-baseline="central" style="font-weight:600">tinyobjloader</text><circle cx="356.5" cy="239.2" r="10" fill="#e5a828"/><text x="356.5" y="239.2" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

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

<svg class="fig flow" viewBox="0 0 1034 112" role="img" aria-label="アセット パイプライン：制作データを、ビルド時に、ゲーム専用の形式に変換する"><defs><marker id="fl43356" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">アセット パイプライン：制作データを、ビルド時に、ゲーム専用の形式に変換する</text><line x1="231.0" y1="64.0" x2="289.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="260.0" y="58.0" text-anchor="middle" style="font-size:12px">ビルド時</text><line x1="569.0" y1="64.0" x2="627.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="598.0" y="58.0" text-anchor="middle" style="font-size:12px">出力</text><line x1="785.0" y1="64.0" x2="843.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl43356)"/><text x="814.0" y="58.0" text-anchor="middle" style="font-size:12px">そのまま読む</text><rect x="28.0" y="44.0" width="200" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="128.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">制作データ （FBX・glTF）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="292.0" y="44.0" width="274" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="429.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ufbx・tinygltf など）</text><circle cx="294.0" cy="46.0" r="10" fill="#2ea043"/><text x="294.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="630.0" y="44.0" width="152" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="706.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム専用バイナリ</text><circle cx="632.0" cy="46.0" r="10" fill="#2ea043"/><text x="632.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="846.0" y="44.0" width="160" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="926.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲーム （読むだけ）</text><circle cx="848.0" cy="46.0" r="10" fill="#e5a828"/><text x="848.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

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
