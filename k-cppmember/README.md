# K-CppMember

Visual Studio 2022 / 2026 用の拡張です。宣言していない変数に代入したとき、キー 1 つで**型を付けて宣言**します。

メンバー関数の中で `stride_ = device->GetDescriptorHandleIncrementSize(type);` と書くと、Visual Studio は `E0020: 識別子 "stride_" が定義されていません` と赤い波線を出します。直すには、ヘッダーを開いて、`GetDescriptorHandleIncrementSize` の戻り値が何だったかを調べて（`UINT`）、`UINT stride_;` を書き足して、元のファイルに戻る、という手間がかかります。K-CppMember は、この往復を 1 回のキーにします。

## 使い方

| キー | コマンド | することと例 |
|---|---|---|
| Alt+W | メンバー変数として宣言する | クラスのヘッダー（`.h`）に `型 名前;` を足す |
| Alt+Q | ローカル変数に型を付ける | その場の `count = 0;` を `int count = 0;` にする |
| Alt+E | ゲッター・セッターを作る | `stride_` の `GetStride()` と `SetStride(...)` を、クラスの `public:` の末尾に足す |

どちらも、**その行のどこにカーソルがあっても**押せます。行頭の `名前 = 右辺;` の左辺が対象です（`this->名前 = ...;` は Alt+W だけ）。拡張機能 メニューからも実行できます。

```cpp
// Alloc.cpp
Alloc::Alloc(Dev* device, int type) {
    stride_ = device->GetStride(type);   // この行のどこでも Alt+W
}
```

```cpp
// Alloc.h(Alt+W のあと。private: の末尾に入る)
 private:
  int capacity_;
  unsigned int stride_;
```

Alt+W は、カーソルのある `Class::Func` の `Class` を宣言から探して、そのクラスの末尾に足します。`private:` が最後でなければ、末尾に `private:` を作ってから足します。ヘッダーはエディターで開いたままになり（保存はしません）、作業中のファイルへ戻ります。挿入は 1 回の編集なので、Undo も 1 回です。

## ゲッター・セッター（Alt+E）

メンバー変数の宣言行（`UINT stride_;`）にカーソルを置くか、`.cpp` の `stride_ = ...;` の行にカーソルを置いて押します。名前は `stride_` から末尾の `_` を外して、先頭を大文字にします（`cpu_start_` は `GetCpuStart` / `SetCpuStart`）。

```cpp
 public:
  Alloc(Dev* device, int type);

  unsigned int GetStride() const { return stride_; }

  void SetStride(unsigned int value) { stride_ = value; }
```

ゲッターの前と、ゲッターとセッターの間の空行は、設定（下の「設定」）で切り替えられます。同じ名前がすでにあるときは足しません。`public:` がなければ、クラスの先頭に作ります。

型によって、書き方を変えます。

| 型 | ゲッター | セッター |
|---|---|---|
| `int`・`float`・ポインター・`UINT` のような大文字の型・ヘッダーに `enum` の定義がある型 | 値 | 値 |
| `std::string`・`std::vector`・構造体など | `const T&` | `const T&` |
| `bool`（名前が `is_` / `has_` で始まる） | `IsVisible()` / `HasXxx()` | `SetVisible(...)` / `SetHasXxx(...)` |
| `ComPtr<T>` | `T*`（`.Get()`） | 作らない |
| `std::unique_ptr<T>` | `T*`（`.get()`） | 作らない |
| `std::shared_ptr<T>` | `T*`（`.get()`） | 値で受けて `std::move` |
| `std::weak_ptr<T>` | `std::shared_ptr<T>`（`.lock()`） | `const&` |
| `std::atomic<T>` | `T`（`.load()`） | `T`（`.store()`） |
| `const` メンバー・参照メンバー | 作る | 作らない |
| `std::mutex`・`std::thread` など | 作らずに断る | 作らずに断る |

配列と `static` のメンバーは対象外です。

## 設定

ツール → オプション → K-CppMember → 全般（Visual Studio 2026 では、設定画面の「K-CppMember」から、従来のダイアログへ進みます）にあります。

- **ゲッターとセッターの間に空行を入れる**（初期値は True）。True のときは、ゲッターの前（直前がメンバーの行のとき）とゲッターとセッターの間に、空行を 1 行入れます。
- **キー。** 3 つのコマンドのキーを、ここで変えられます。「Alt+Q」「Ctrl+Alt+M」のように書き、OK を押すと Visual Studio のキー割り当てに反映されます。空にするとキーを外します。開いたときは、今の割り当てが表示されます。

## 型の決め方

右辺から、次の順に決めます。

1. **式そのもの。** `0` は `int`、`1.0f` は `float`、`true` は `bool`、`"abc"` は `const char*`、`static_cast<T>(...)` は `T`、`std::make_unique<T>(...)` は `std::unique_ptr<T>`、`new T` は `T*`。
2. **Quick Info（ホバーの内容）。** 関数呼び出しなら、戻り値の型を取り出します。`virtual UINT __stdcall ID3D12Device::GetDescriptorHandleIncrementSize(...)` から `UINT` を取ります。変数や引数なら、その型を取ります。
3. **どちらでも決まらないとき。** Alt+W は、型の入力欄を出します。Alt+Q は `auto` を入れます。

`const` と参照は外して、値の型にそろえます（`const UINT&` は `UINT`）。ポインターの `const` は残します。

## 制限

- 行頭が `名前 = 右辺;` の形で、**1 行**に収まっているものだけ扱います。`int x = 0;` のように、すでに型があるものは対象外です。
- Alt+W は `Class::Func(` の形の定義の中でだけ働きます。字下げされていても、引数が複数行に分かれていても見つかりますが、クラスの中に書いた関数と、ラムダの中では使えません。
- ヘッダーは、ソリューションのフォルダーの下から探します。cpp と同じ名前の `.h` を先に見て、なければ `class Class {` を含む `.h` を探します。
- クラスが入れ子や、同じ名前が複数あるときは、最初に見つかったものに足します。
- 右辺に演算子が入る式（`a + b` など）は、Quick Info では決められないので、入力欄（Alt+W）か `auto`（Alt+Q）になります。
- Alt+W は、Visual Studio の「ウィンドウ」メニューのアクセスキーと重なります。効かない場合は、上の「設定」のキーで、別のキーに付け替えてください。
- 失敗したときは、ステータスバーに理由が出ます。詳しいログは `%LOCALAPPDATA%\K-CppMember\vsix.log` です。

## インストールとビルド

`bin\K-CppMember.vsix` をダブルクリックして、Visual Studio を再起動します。作るには、次を実行します。事前に、Visual Studio の「Visual Studio extension development」ワークロードが要ります。

```powershell
.\build.ps1
```
