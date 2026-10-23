---
title: FBX SDK の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# FBX SDK の導入（Visual Studio）

FBX SDK は**Autodesk のサイトから、インストーラーをダウンロード**して入れます（vcpkg などのパッケージ管理には、標準ではありません）。手動の設定（インクルード・ライブラリ・DLL）が必要です（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md#lib_dll)）。

## 入手とインストール

| 手順 | 内容 |
| --- | --- |
| **1. ダウンロード** | Autodesk の「FBX SDK」のページから、Visual Studio のバージョンに合う Windows 用のインストーラーを取得（Autodesk のアカウント・ライセンスへの同意が、必要な場合がある） |
| 2. インストール | インストーラーを実行。既定では `C:\Program Files\Autodesk\FBX\FBX SDK\<バージョン>\` に入る |
| 3. 中身を確認 | `include\`（ヘッダ）、`lib\`（ライブラリ）、`samples\`（サンプル） |

!!! warning "Autodesk のライセンスを確認する"
    FBX SDK は Autodesk のライセンス（製品に組み込んで、再配布する条件）に従います。ゲームの配布（DLL の同梱）が許される条件・表示すべき著作権を、必ず確認します。商用では特に重要です。ライセンスが厳しい・不安な場合は[ufbx](../ufbx/index.md)（MIT）やglTF への変換を、検討します。

## プロジェクトの設定

1. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）構成を **Debug**（または Release）、プラットフォームを x64 にする
2. C/C++ → 全般 → 追加のインクルード ディレクトリ に、SDK の `include` を追加する

    ```text
    C:\Program Files\Autodesk\FBX\FBX SDK\2020.3.7\include
    ```

3. リンカー → 全般 → 追加のライブラリ ディレクトリ に、構成とランタイムに合う `lib` フォルダーを追加する

    ```text
    C:\Program Files\Autodesk\FBX\FBX SDK\2020.3.7\lib\vs2022\x64\debug
    ```

4. リンカー → 入力 → 追加の依存ファイル に`libfbxsdk-md.lib`（または `-mt`）などを追加する
5. 実行ファイルの横に `libfbxsdk.dll` をコピーする（DLL 版を使う場合）

### ライブラリの種類（ランタイムに合わせる）

| ファイル | 意味 | 合うランタイム |
| --- | --- | --- |
| `libfbxsdk.lib` + `libfbxsdk.dll` | DLL 版（動的リンク） | `/MD` |
| `libfbxsdk-md.lib` | 静的ライブラリ（DLL なし） | `/MD` |
| `libfbxsdk-mt.lib` | 静的ライブラリ | `/MT` |

!!! warning "ランタイム ライブラリをそろえる"
    `/MD` のプロジェクトに `-mt` のライブラリをリンクすると、`LNK2038`（不一致）や実行時のクラッシュになります。ライブラリのビルド（`debug` / `release` のフォルダー）も構成に合わせます（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)）。

### プリプロセッサの定義

| 定義 | 意味 |
| --- | --- |
| `FBXSDK_SHARED` | DLL 版を使うときに定義（`libfbxsdk.lib` + DLL） |
| `NOMINMAX` | Windows の `min` / `max` マクロの衝突を避ける（[プリプロセッサマクロ](../../vs/preprocessor.md)） |

## 最小の確認

```cpp
#include <fbxsdk.h>

int main() {
  FbxManager* manager = FbxManager::Create();
  std::println("FBX SDK のバージョン: {}", FbxManager::GetVersion());
  manager->Destroy();
}
```

**これがビルド・実行できれば、導入は成功**です（DLL 版なら `libfbxsdk.dll` が、実行ファイルの横に必要）。

## よくあるミス

??? failure "`libfbxsdk.dll が見つかりません` で、起動できない"
    **DLL 版**では`libfbxsdk.dll` を実行ファイルの横にコピーします。

??? failure "`LNK2038`（ランタイムの不一致）"
    `/MD` と `/MT`、Debug と Release をそろえます。

??? failure "古い Visual Studio 用の SDK を使って、リンクできない"
    Visual Studio のバージョンに合う `lib\vsXXXX` を選びます。新しい VS にまだ対応していない場合もあります。

??? failure "`fbxsdk.h` が見つからない"
    追加のインクルード ディレクトリに`include` フォルダーを指定します。

## 関連ページ

- [FBX SDK（目次）](index.md)
- [FBX SDK の基本](quickstart.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
- [プリプロセッサマクロ](../../vs/preprocessor.md)
