# 外部ライブラリ

ゲームやツールを作るときに使う、**C++ の外部ライブラリ**の解説です。C++ の標準ライブラリ（STL）にはない機能（JSON、GUI、物理演算など）は、外部ライブラリを入れて使います。このカテゴリのページは、**最初に Visual Studio での入れ方**を書き、そのあとで使い方を説明します。ライブラリの入れ方の基本は [Visual Studio：外部ライブラリの入れ方](../vs/libraries.md) にまとめています。

## シリアライズ（保存・読み込み）

データをファイルや通信で扱える形に変えるライブラリです。概要は [シリアライズ](../engine/serialization/index.md) を先に読んでください。

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [nlohmann/json](serialization/nlohmann-json.md) | JSON（定番） | 一番書きやすい。読み書き両方 |
| [simdjson](serialization/simdjson.md) | JSON（速さ重視） | とても速く読む。読み込み専用 |
| [rapidyaml](serialization/rapidyaml.md) | YAML | 速い YAML。人が書くデータ向け |
| [cereal](serialization/cereal.md) | バイナリ（定番） | STL・スマートポインタに対応。バージョン管理あり |
| [zpp_bits](serialization/zpp-bits.md) | バイナリ（速さ重視） | 構造体のまま保存。とても速い |
| [yalantinglibs（struct_pack）](serialization/struct-pack.md) | バイナリ（速さ重視） | 型のチェックと互換フィールド |
| [cista](serialization/cista.md) | バイナリ（ゼロコピー） | 読み込みでコピーしない |

## GUI（ツール・デバッグ画面）

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [Dear ImGui](imgui/index.md) | 即時モード GUI | ゲームのデバッグ画面・エディタを数行で作る |
| [ImGuizmo](imgui/imguizmo.md) | 3D のギズモ | オブジェクトの移動・回転・拡大をマウスで操作する矢印 |
| [ImSequencer](imgui/imsequencer.md) | タイムライン | アニメーションやイベントの時間軸を編集する |
| [imgui-node-editor](imgui/node-editor.md) | ノード エディタ | ノードを線でつないで、グラフを編集する |

## ゲーム AI（ナビゲーション）

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [Recast & Detour](recast/index.md) | ナビメッシュの作成・経路探索・群衆 | 歩ける場所を自動で作り、経路を探す |

## スクリプト・他言語連携

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [sol2](sol2.md) | Lua の組み込み | ゲームを止めずに、挙動をスクリプトで変える |
| [pybind11](pybind11.md) | Python との連携 | C++ を Python から呼ぶ。ツールや自動テスト向け |

## 3D モデル

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [3D モデルの読み込みの選び方](model-loading.md) | 形式・ライブラリの比較 | glTF・FBX・OBJ と、どのライブラリを使うか |
| [fastgltf](fastgltf/index.md) | 3D モデル（glTF）の高速な読み込み | simdjson ベース。大きなアセット向き |
| [ufbx](ufbx/index.md) | FBX の読み込み | 2 ファイルを置くだけ。読み込み専用 |
| [FBX SDK](fbxsdk/index.md) | FBX の公式 SDK | 全機能・書き出し。導入とライセンスが重い |
| [tinygltf](tinygltf/index.md) | 3D モデル（glTF）の読み込み | 構造は「番号（インデックス）」でつながる。[構造](tinygltf/structure.md)・[取り出し方](tinygltf/reading.md) |

## 物理演算

| ライブラリ | 用途 | 一言で |
| --- | --- | --- |
| [Jolt Physics](jolt/index.md) | 3D 物理演算 | 剛体・衝突判定・キャラクター。ゲーム向けに作られた、速くて新しい物理エンジン |

!!! note "ページの状態"
    ページの先頭に **TODO** と書かれているものは、**構成だけ用意していて、内容はこれから書く**ものです。内容が深いライブラリ（Dear ImGui、Jolt Physics）は、複数のページに分けて少しずつ書いていきます。

## ライブラリの選び方（共通）

| 見ること | 理由 |
| --- | --- |
| **最後の更新はいつか** | 何年も更新されていないと、新しい C++ や Visual Studio でビルドできなくなる |
| **ライセンス** | MIT / Zlib / BSD / Apache 2.0 は、ゲームに入れて配布しやすい。GPL は、ソースの公開が必要になる |
| **vcpkg にあるか** | あると入れるのがとても楽 |
| **ヘッダだけか、ビルドが必要か** | ヘッダだけなら導入が簡単。ビルドが必要なら、CMake が絡む |
| **ドキュメントと例** | 少ないライブラリは、使い方を調べるのに苦労する |
| **コミュニティ** | 質問できる場所（GitHub の Issues、Discord）があるか |

## 関連ページ

- [Visual Studio：外部ライブラリの入れ方](../vs/libraries.md)
- [Visual Studio：よくあるエラー](../vs/errors.md)
- [シリアライズ（概要）](../engine/serialization/index.md)
