# K-CppMember

Visual Studio 2022 / 2026 用の拡張です。宣言していない変数に代入したとき、キー 1 つで**型を付けて宣言**します。

メンバー関数の中で `stride_ = device->GetDescriptorHandleIncrementSize(type);` と書くと、Visual Studio は `E0020: 識別子 "stride_" が定義されていません` と赤い波線を出します。直すには、ヘッダーを開いて、`GetDescriptorHandleIncrementSize` の戻り値が何だったかを調べて（`UINT`）、`UINT stride_;` を書き足して、元のファイルに戻る、という手間がかかります。K-CppMember は、この往復を 1 回のキーにします。

## 使い方

| キー | コマンド | することと例 |
|---|---|---|
| Alt+W | メンバー変数として宣言する | クラスのヘッダー（`.h`）に `型 名前;` を足す |
| Alt+Q | ローカル変数に型を付ける | その場の `count = 0;` を `int count = 0;` にする |

どちらも、**代入の左辺の変数にカーソルを置いて**押します。拡張機能 メニューからも実行できます。

```cpp
// Alloc.cpp
Alloc::Alloc(Dev* device, int type) {
    stride_ = device->GetStride(type);   // stride_ にカーソルを置いて Alt+W
}
```

```cpp
// Alloc.h(Alt+W のあと。private: の末尾に入る)
 private:
  int capacity_;
  unsigned int stride_;
```

Alt+W は、カーソルのある `Class::Func` の `Class` を宣言から探して、そのクラスの末尾に足します。`private:` が最後でなければ、末尾に `private:` を作ってから足します。ヘッダーはエディターで開いたままになり（保存はしません）、作業中のファイルへ戻ります。挿入は 1 回の編集なので、Undo も 1 回です。

## 型の決め方

右辺から、次の順に決めます。

1. **式そのもの。** `0` は `int`、`1.0f` は `float`、`true` は `bool`、`"abc"` は `const char*`、`static_cast<T>(...)` は `T`、`std::make_unique<T>(...)` は `std::unique_ptr<T>`、`new T` は `T*`。
2. **Quick Info（ホバーの内容）。** 関数呼び出しなら、戻り値の型を取り出します。`virtual UINT __stdcall ID3D12Device::GetDescriptorHandleIncrementSize(...)` から `UINT` を取ります。変数や引数なら、その型を取ります。
3. **どちらでも決まらないとき。** Alt+W は、型の入力欄を出します。Alt+Q は `auto` を入れます。

`const` と参照は外して、値の型にそろえます（`const UINT&` は `UINT`）。ポインターの `const` は残します。

## 制限

- `名前 = 右辺;` が **1 行**に収まっているものだけ扱います。
- Alt+W は `Class::Func(` の形の定義の中でだけ働きます（クラスの中に書いた関数や、ラムダの中では使えません）。
- ヘッダーは、ソリューションのフォルダーの下から探します。cpp と同じ名前の `.h` を先に見て、なければ `class Class {` を含む `.h` を探します。
- クラスが入れ子や、同じ名前が複数あるときは、最初に見つかったものに足します。
- 右辺に演算子が入る式（`a + b` など）は、Quick Info では決められないので、入力欄（Alt+W）か `auto`（Alt+Q）になります。
- Alt+W は、Visual Studio の「ウィンドウ」メニューのアクセスキーと重なります。効かない場合は、ツール → オプション → 環境 → キーボードで、別のキーに付け替えてください。
- 失敗したときは、ステータスバーに理由が出ます。詳しいログは `%LOCALAPPDATA%\K-CppMember\vsix.log` です。

## インストールとビルド

`bin\K-CppMember.vsix` をダブルクリックして、Visual Studio を再起動します。作るには、次を実行します。事前に、Visual Studio の「Visual Studio extension development」ワークロードが要ります。

```powershell
.\build.ps1
```
