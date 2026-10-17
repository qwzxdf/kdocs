# 外部ライブラリ

ゲームやツールを作るときに使う、**C++ の外部ライブラリ**の解説です。C++ の標準ライブラリ（STL）にはない機能（JSON、GUI、物理演算など）は、外部ライブラリを入れて使います。このカテゴリのページは、**最初に Visual Studio での入れ方**を書き、そのあとで使い方を説明します。ライブラリの入れ方の基本は [Visual Studio：外部ライブラリの入れ方](../vs/libraries.md) にまとめています。

!!! tip "ポイント"
    - 入れ方は、まず **vcpkg**（`vcpkg install ライブラリ名:x64-windows`）。ヘッダだけのものは、ファイルを置くだけでもよい。
    - ライブラリは**目的ごとに選ぶ**（JSON か、バイナリか、GUI か、物理か）。同じ目的のライブラリが複数あるときは、**速さ・書きやすさ・メンテナンスの状況**で選ぶ。
    - ライブラリのバージョンは**固定する**（vcpkg のマニフェスト、Git のタグ）。勝手に変わると、動かなくなる。
    - ライブラリのライセンス（MIT、Apache、GPL など）を確認する。配布するゲームに使えるかが決まる。

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
| [Dear ImGui](imgui/index.md) | 即時モード GUI | ゲームのデバッグ画面・エディタを、数行で作る |
| [ImGuizmo](imgui/imguizmo.md) | 3D のギズモ | オブジェクトの移動・回転・拡大をマウスで操作する矢印 |
| [ImSequencer](imgui/imsequencer.md) | タイムライン | アニメーションやイベントの時間軸を編集する |
| [imgui-node-editor](imgui/node-editor.md) | ノード エディタ | ノードを線でつないで、グラフを編集する |

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
