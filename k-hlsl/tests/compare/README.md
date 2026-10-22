# Viasfora との比較テスト

K-HLSL の色付けが、Viasfora と同じかどうかを、Viasfora 自身の DLL を読み込んで確かめるテストです。Viasfora は VS にインストール済みで、HLSL を C++ として扱う設定（既定値）を前提にします。

| フォルダー | 内容 |
| --- | --- |
| `difftest/` | Viasfora の `CBraceScanner`（括弧）と `CStringScanner`（文字列のエスケープ・書式指定子）に、K-HLSL のレキサーと同じ入力を流して、結果を突き合わせる。実ファイルと、ランダムに作った入力 12 万件を使う |
| `colortest/` | Viasfora の書式クラス（制御フロー・可視性・エスケープ・書式指定子・Rainbow 括弧 1〜9・対応なし）を生成して、K-HLSL の書式クラスと、色・太字・不透明度・`Order` などを突き合わせる |

## 実行

Viasfora の DLL の場所は、VS のインストールごとに違います（`Common7\IDE\Extensions\<ランダムな名前>\Viasfora.Core.dll`）。各 `.csproj` の `HintPath` を、手元の場所に直してください。

```powershell
# 先に build.ps1 で K-HLSL をビルドしておく
msbuild tests\compare\difftest\difftest.csproj /restore /p:Configuration=Release
tests\compare\difftest\bin\Release\net472\difftest.exe <シェーダーのフォルダー> ...

msbuild tests\compare\colortest\colortest.csproj /restore /p:Configuration=Release
tests\compare\colortest\bin\Release\net472\colortest.exe
```

どちらも、不一致が 0 件なら終了コード 0 になります。

## 結果（K-HLSL 1.0.4 / Viasfora 4.6.225）

- `difftest`: 実ファイル 89 本、ランダム 120000 件、不一致 0 件
- `colortest`: 196 項目、不一致 0 件

## 再現していない物

- レインボー行（インデントの縦線）
- Ctrl キーで括弧のペアを強調する機能と、括弧のツールチップ
- 現在の行・列のハイライト（Viasfora 本体が、コンテンツ タイプによらず、そのまま効く）
