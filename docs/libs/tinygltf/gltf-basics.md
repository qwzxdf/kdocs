---
title: glTF の基本と規約
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# glTF の基本と規約

glTF とは何か、ファイルの形、**座標系・規約**、拡張、ほかのライブラリとの比較をまとめます。

## glTF とは

| 項目 | 内容 |
| --- | --- |
| **正式名称** | GL Transmission Format |
| **作った所** | Khronos Group（OpenGL / Vulkan の団体）。**オープン**な規格 |
| **バージョン** | **2.0** が、現在の標準 |
| **特徴** | **軽量**。**PBR のマテリアル**（金属度・粗さ）に対応。ボーン・アニメーションも持てる |
| **向き** | **ゲーム・Web・アプリ**への、**配布・受け渡し** |
| **拡張子** | `.gltf`（JSON + 外部ファイル）、`.glb`（1 ファイルにまとめたバイナリ） |

## ファイルの形

| 形式 | 構成 | 特徴 |
| --- | --- | --- |
| **`.gltf`** | JSON ＋ `.bin`（バイナリ）＋ 画像（`.png` など） | ファイルが分かれる。**中身を、テキストエディターで見られる** |
| **`.glb`** | **すべてを 1 つにまとめたバイナリ** | 1 ファイルで、扱いやすい。**配布向き** |
| **埋め込み `.gltf`** | JSON の中に、データを `base64` で入れたもの | 1 ファイルだが、サイズが大きくなる |


## glTF の座標系・規約

| 項目 | glTF | このサイトの規約（左手系・DX11） |
| --- | --- | --- |
| **座標系** | **右手系** | **左手系**（Z を反転して取り込む） |
| **上方向** | **+Y** | +Y（同じ） |
| **前方向** | <strong>+Z が「正面向き」</strong>（モデルが、+Z を向いて作られる） | カメラの前は +Z。**Z を反転すると、モデルの正面は −Z（カメラの方）を向く**（[座標系](../../gamemath/coordinate-systems.md)） |
| **単位** | **メートル** | メートル（同じ） |
| **UV の原点** | **左上**（V は下向き） | **左上**（DirectX と同じ。**反転は不要**） |
| **三角形の表** | <strong>反時計回り（CCW）</strong> | <strong>時計回り（CW）</strong>（`FrontCounterClockwise = FALSE`）。**インデックスの 2 番目と 3 番目を入れ替える** |
| <strong>回転（クォータニオン）</strong> | **`(x, y, z, w)`** の順 | 同じ並びだが、**Z 反転に合わせて `(-x, -y, z, w)`** にする |
| **行列** | **列優先**（column-major）の 16 個 | 行ベクトル規約（行優先）。**転置と同じ並びなので、`memcpy` で読める**。ただし **Z 反転の変換（`S × M × S`）が必要** |

glTF は右手系、このサイトは左手系なので、**読み込み時に 1 回だけ、座標を変換**します（[座標系](../../gamemath/coordinate-systems.md)）。普通は **Z を反転**します。

## 左手系へ変換する {#to-left-handed}

| 変換するもの | やること |
| --- | --- |
| **頂点の位置・法線** | `(x, y, z)` → `(x, y, -z)` |
| **三角形のインデックス** | 三角形ごとに、**2 番目と 3 番目を入れ替える**（CCW → CW。そうしないと、裏表が逆になる） |
| <strong>ノードの移動（translation）</strong> | `(x, y, z)` → `(x, y, -z)` |
| <strong>ノードの回転（quaternion）</strong> | `(x, y, z, w)` → `(-x, -y, z, w)` |
| <strong>ノードの拡大（scale）</strong> | そのまま |
| **ノードの `matrix`** | `S × M × S`（`S` は Z を反転する行列）。要素のうち、**Z の行と列の、どちらか一方だけに関わるもの**の符号を反転 |
| **スキンの逆バインド行列** | `matrix` と同じく `S × M × S` |
| **アニメーション** | translation・rotation のキーを、上と同じ規則で変換 |

```cpp
Vector3 ToLeftHanded(const Vector3& p) {
  return Vector3(p.x, p.y, -p.z);
}

Quaternion ToLeftHanded(const Quaternion& q) {
  return Quaternion(-q.x, -q.y, q.z, q.w);
}

Matrix ToLeftHanded(const Matrix& m) {
  Matrix s = Matrix::CreateScale(1.0f, 1.0f, -1.0f);
  return s * m * s;
}

void FlipWinding(std::vector<uint32_t>& indices) {
  for (size_t i = 0; i + 2 < indices.size(); i += 3) {
    std::swap(indices[i + 1], indices[i + 2]);
  }
}
```

!!! tip "キャラクターの正面"
    glTF は、モデルの正面が **+Z** です。Z を反転すると、正面は **−Z**（カメラの方）を向きます。キャラクターを `kForward`（+Z）の向きに歩かせたいときは、読み込み後に **Y 軸まわりに 180 度**回して使います。ビューアーのように、カメラに正面を向けたいだけなら、そのままで構いません。

**変換は、アセットの変換ツール（ビルド時）で 1 回だけ**行うのがおすすめです（[ベイク](../../optimize/baking.md)）。実行時に毎回変換すると、無駄です。


## 拡張（extensions）

glTF は、**拡張**で機能を足せます。**未対応の拡張**は、`warning` に出ます。

| 拡張 | 内容 | tinygltf の対応 |
| --- | --- | --- |
| `KHR_materials_*` | クリアコート・透過・光沢などの、**マテリアルの追加機能** | **値は読める**（`extensions` に入る。解釈は自分で） |
| `KHR_texture_transform` | UV の移動・回転・拡大 | 値は読める。自分で適用 |
| `KHR_lights_punctual` | ライト | 読める |
| `KHR_draco_mesh_compression` | **Draco による、メッシュ圧縮** | **デコードしない**（別のライブラリが必要） |
| `EXT_meshopt_compression` | meshopt による圧縮 | デコードしない |
| `KHR_texture_basisu` | KTX2（Basis）のテクスチャ圧縮 | **画像として読めない**（別のライブラリが必要） |

**圧縮された glTF** は、tinygltf だけでは、頂点が取り出せません。**書き出しのときに、圧縮を使わない**設定にするのが、いちばん簡単です。


## ほかの選択肢

| ライブラリ | 特徴 |
| --- | --- |
| **tinygltf** | **ヘッダのみ・使いやすい**。構造がそのまま見える。**学習・小規模向き** |
| **fastgltf** | **速い**（simdjson 使用）。**C++17 以降**。**大きなデータ向き** |
| **cgltf** | **C 言語**の、単一ヘッダ。**軽い**。構造がポインタで辿れる |
| **Assimp** | **多くの形式**に対応（glTF・FBX・OBJ…）。**重い** |

**学習・普通のゲームなら、tinygltf**が、理解しやすいです。

## 関連ページ

- [tinygltf（目次）](index.md)
- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)

