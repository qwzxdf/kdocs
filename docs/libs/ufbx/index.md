---
title: ufbx（FBX の読み込み）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# ufbx（FBX の読み込み）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
</div>

**ufbx**（ユー エフ ビー エックス）は、**FBX ファイルを読み込む**、**単一のソースファイル**（`ufbx.c` と `ufbx.h`）のライブラリです。**FBX**は、**Autodesk の独自形式**で、**Maya・3ds Max・Blender・Unity・Unreal**などの、**ほぼすべての 3D ツールが書き出せる**ので、**ゲームの制作現場で、広く使われています**。公式の FBX SDK は、**使うのが大変**（導入・ライセンス）ですが、ufbx は、**ファイルを 2 つ置くだけ**で、<strong>許可の厳しいライセンス（MIT / パブリックドメイン）</strong>で使えます。

!!! tip "ポイント"
    - <strong>`ufbx.c` と `ufbx.h` の 2 ファイルを、プロジェクトに追加するだけ</strong>で使える（<strong>依存なし</strong>）。
    - <strong>読み込みのみ</strong>（FBX の書き出しは、できない）。<strong>ASCII 形式も、バイナリ形式も</strong>読める。
    - <strong>`ufbx_load_file` → `ufbx_scene*`</strong>。<strong>使い終わったら `ufbx_free_scene`</strong>。
    - <strong>データは、`ufbx_scene` の、リスト（`.data` と `.count`）</strong>。<strong>ノード・メッシュ・マテリアルが、ポインタでつながる</strong>（<strong>glTF のような番号参照ではない</strong>）。
    - <strong>座標系・単位を、読み込み時に変換</strong>できる（<strong>右手系・Y 上・メートル</strong>（そのあと、ルートの X 反転で左手系）に）。
    - <strong>C 言語のライブラリ</strong>（C++ から、普通に呼べる）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | 2 ファイルを置く・vcpkg・CMake |
| [FBX と ufbx の基本](quickstart.md) | FBX とは、最小の読み込み、座標系・単位の変換、シーンの構造 |
| [データの取り出し方](reading.md) | メッシュ・三角形化・マテリアル・ノード・スキン・アニメーション |

## 関連ページ

- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [FBX SDK](../fbxsdk/index.md)
- [tinygltf](../tinygltf/index.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
