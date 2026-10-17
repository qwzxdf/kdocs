---
title: エラー処理の方針
tags:
  - 設計
---

# エラー処理の方針

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

プログラムには、「ファイルが無い」「データが壊れている」「ありえない値が来た」など、うまくいかない場面が必ずあります。C++ にはエラーを伝える方法がいくつもあり（`assert`、戻り値、`std::optional`、`std::expected`、例外）、**どのエラーにどれを使うか**を決めておかないと、チームの中でバラバラになって扱いにくくなります。

!!! tip "ポイント"
    - **プログラマーのミス**（ありえない状態）は `assert` で開発中に止める。
    - **起こりうる失敗**（ファイルが無い、通信が切れた）は戻り値で伝える。理由が要らなければ `std::optional`、要るなら `std::expected`。
    - ゲームでは例外を切る（使わない）ことが多い。使うなら「本当に想定外」のときだけ。
    - エラーは**握りつぶさない**。少なくともログに出す。

## エラーの種類と使う道具

| エラーの種類 | 例 | 使う道具 |
| --- | --- | --- |
| プログラマーのミス（バグ） | 範囲外の添字、nullptr を渡した、ありえない enum の値 | `assert` |
| 起こりうる失敗（理由は 1 つ） | 検索で見つからない | `std::optional` |
| 起こりうる失敗（理由がいくつか） | ファイルが無い / 壊れている / バージョンが違う | `std::expected` |
| 回復できない失敗 | メモリ不足、GPU が初期化できない | ログを出して終了（または例外） |
| 状況を知らせたいだけ | 古い形式のデータを読み込んだ | ログ（警告） |

## 1. assert：バグを見つける

```cpp
#include <cassert>
#include <vector>

int GetTile(const std::vector<int>& tiles, int index) {
  assert(index >= 0 && index < static_cast<int>(tiles.size()) && "タイルの範囲外");
  return tiles[index];
}
```

- 条件が `false` なら、メッセージを出してその場で止まる（デバッガで止まった場所が分かる）
- **Release ビルド（`NDEBUG` 定義時）では消える**ので、速さに影響しない
- `assert` の中に「必要な処理」を書かない（Release で消えてしまう）

```cpp
assert(LoadTexture("a.png"));  // NG: Release では読み込み自体が消える

bool ok = LoadTexture("a.png");
assert(ok);  // OK
```

コンパイル時に分かる条件は `static_assert` で確かめます。

```cpp
static_assert(sizeof(SaveHeader) == 16, "セーブデータの形が変わった");
```

## 2. optional / expected：失敗を戻り値で返す

```cpp
#include <expected>
#include <optional>
#include <print>
#include <string>

enum class LoadError { kNotFound, kBroken, kOldVersion };

std::expected<int, LoadError> LoadSaveVersion(const std::string& file) {
  if (file.empty()) {
    return std::unexpected(LoadError::kNotFound);
  }
  if (file == "old.dat") {
    return std::unexpected(LoadError::kOldVersion);
  }
  return 3;
}

const char* ToText(LoadError e) {
  switch (e) {
    case LoadError::kNotFound:
      return "セーブがありません";
    case LoadError::kBroken:
      return "データが壊れています";
    case LoadError::kOldVersion:
      return "古いバージョンのデータです";
  }
  return "";
}

int main() {
  for (std::string f : {"save.dat", "", "old.dat"}) {
    if (auto v = LoadSaveVersion(f)) {
      std::println("バージョン {}", *v);
    } else {
      std::println("エラー: {}", ToText(v.error()));
    }
  }
}
```

```text title="実行結果"
バージョン 3
エラー: セーブがありません
エラー: 古いバージョンのデータです
```

- 呼んだ側は、戻り値を見ないと値を取り出せないので、エラー処理を忘れにくい
- 詳しくは [`std::optional`](../../stl/utilities/optional.md)、[`std::expected`](../../stl/utilities/expected.md)

## 3. 例外

```cpp
try {
  auto data = LoadLevel("stage1.json");
} catch (const std::exception& e) {
  Log("読み込み失敗: {}", e.what());
}
```

| 長所 | 短所 |
| --- | --- |
| 何段も上の呼び出し元まで一気に伝えられる | どこから飛んでくるか見えにくい |
| 戻り値を使わずに済む | 投げたときのコストが大きい。コードサイズも増える |
| 標準ライブラリの一部（`at`、`stoi`、filesystem）が使う | 家庭用ゲーム機などでは使えない（切る）ことが多い |

ゲームのプロジェクトでは**例外を使わない**（コンパイラの設定で無効にする）ことも多いです。その場合は、例外を投げる標準ライブラリの関数（`std::stoi` など）の代わりに、投げない版（`std::from_chars`、`std::error_code` を取る filesystem の関数）を使います。

## 4. ログ

エラーは、直せないとしても**記録**します。

| レベル | 使うとき |
| --- | --- |
| Error | 機能が動かなかった（テクスチャが読めず、代わりの画像を出した） |
| Warning | 動いたが、おかしいかもしれない（古い形式のデータ、想定より重い） |
| Info | 普通の記録（ステージ開始、セーブ完了） |
| Debug | 開発中だけ見たい詳しい情報 |

## 5. 失敗したときにどうするか

| 方針 | 例 |
| --- | --- |
| 代わりのもので続ける | テクスチャが無ければピンクの「見つかりません」画像を出す |
| ユーザーに知らせる | 「セーブデータが壊れています。新しく始めますか？」 |
| やり直す | 通信をもう一度試す |
| 安全に終了する | 初期化に失敗したらメッセージを出して終了 |

開発中は**早く・大きく失敗する**（assert で止める）、製品版は**なるべく続ける**（代わりのもの + ログ）のが一般的です。

## ゲームでの例

| 場面 | 方針 |
| --- | --- |
| 配列の範囲外、nullptr | assert |
| ID で敵を探して見つからない | optional |
| セーブデータの読み込み | expected（理由をユーザーに伝える） |
| 画像が見つからない | 代わりの画像 + Error ログ |
| 設定ファイルの値がおかしい | デフォルト値 + Warning ログ |

## よくある失敗

??? failure "エラーを握りつぶす"
    ```cpp
    try { Load(); } catch (...) {}  // 何も起きなかったことにする
    ```

    原因が分からないまま、後で別の場所がおかしくなります。最低でもログを出します。

??? failure "assert で起こりうる失敗をチェックする"
    「ファイルが無い」は普通に起こるので、assert（Release で消える）ではなく、戻り値で処理します。

??? failure "bool だけ返して理由が分からない"
    `bool Load()` が false を返しても、何が悪いのか分かりません。理由があるなら expected にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バグは assert、起こりうる失敗は optional / expected
    - [x] ゲームでは例外を使わないことが多い
    - [x] エラーは握りつぶさずログに出す

## 関連ページ

- [std::expected](../../stl/utilities/expected.md)
- [std::optional](../../stl/utilities/optional.md)
- [未定義動作](../../basics/ub.md)
