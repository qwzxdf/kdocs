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
