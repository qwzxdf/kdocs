---
title: FBX SDK（Autodesk 公式）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# FBX SDK（Autodesk 公式）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
</div>

**FBX SDK**は、**FBX の開発元（Autodesk）が提供する、公式の C++ ライブラリ**です。**FBX の読み込み・書き出し・変換**が、**すべての機能**（アニメーション・スキン・カメラ・ライト・ツール固有の情報）で、**できます**。**正確さ・網羅性**では、**最も信頼できる**一方、**導入が重く、ライセンスの制約があり、閉じたライブラリ**（ソースが見られない）です。**ゲームの実行時に組み込む**より、**アセット変換ツール**で、使われることが多いです。

!!! tip "ポイント"
    - <strong>公式の SDK</strong>。<strong>読み込みも書き出しも、すべての FBX の機能</strong>に対応。
    - <strong>Autodesk のサイトから、インストーラーを入手</strong>して、<strong>ライセンスに同意</strong>して入れる（<strong>vcpkg の標準ポートはなし</strong>）。
    - <strong>ヘッダ ＋ ライブラリ（`.lib`）＋ DLL</strong>。<strong>ランタイム（`/MD`・`/MT`）に合う `.lib` を選ぶ</strong>。
    - 使い方は<strong>「マネージャー → インポーター → シーン」</strong>。<strong>`FbxManager` を、最後に `Destroy`</strong>。
    - <strong>座標系・単位の変換</strong>（<strong>`FbxAxisSystem`・`FbxSystemUnit`</strong>）と、<strong>三角形化（`FbxGeometryConverter`）</strong>が、定番の前処理。
    - <strong>ライセンス・配布の条件を、必ず確認</strong>。<strong>軽く使うなら ufbx</strong>。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | 入手・インストール・プロジェクトの設定・DLL・ライセンス |
| [FBX SDK の基本](quickstart.md) | 最小の読み込み、オブジェクトの管理（`Destroy`）、座標系・単位、シーンの構造 |
| [データの取り出し方](reading.md) | メッシュ・三角形化・法線・UV・マテリアル・スキン・アニメーション |

## 関連ページ

- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [ufbx](../ufbx/index.md)
- [tinygltf](../tinygltf/index.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
