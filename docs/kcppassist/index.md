---
title: K-CppAssist
tags:
  - Visual Studio
---

# K-CppAssist

メンバー関数の中で `stride_ = device->GetDescriptorHandleIncrementSize(type);` と書くと、Visual Studio は `E0020: 識別子 "stride_" が定義されていません` と赤い波線を出します。直すには、ヘッダーを開いて、`GetDescriptorHandleIncrementSize` の戻り値が何だったかを調べて（`UINT`）、`UINT stride_;` を書き足して、元のファイルに戻る、という往復が要ります。ゲッターとセッターを作るときも、同じ往復をもう一度やります。

K-CppAssist は、この往復をキー 1 つにする Visual Studio 用の拡張です。右辺の式から型を決めて、クラスの宣言（`.h`）に変数を足します。ローカル変数なら、その場で型を付けます。

!!! info "このページを読む前に"
    拡張機能の入れ方や、C++23 の設定は [Visual Studio](../vs/index.md) にあります。K-CppAssist は、右辺の型をエディターのホバー（Quick Info）から読みます。ホバーが出ない環境では、リテラルなど式だけで決まる型に限られます。

## ダウンロード

<p><a class="md-button md-button--primary" href="K-CppAssist-0.7.1.vsix" download>K-CppAssist 0.7.1 をダウンロード（.vsix、約 55 KB）</a></p>

Visual Studio 2026（Community・Professional・Enterprise）で動きます。2022 にも入れられます。Windows の x64 が対象です。ダウンロードした `.vsix` をダブルクリックして、画面の指示に従ってインストールし、Visual Studio を再起動します。新しい版に更新するときも、同じ手順で上書きできます。アンインストールは、Visual Studio の「拡張機能の管理」から行います。

## 使い方

コマンドは 5 つで、キーだけで使います。キーは、設定で変えられます。拡張機能 メニューに出るのは「K-CppAssist の設定...」の 1 つで、クリックすると設定画面が開きます。

| キー | コマンド | することと例 |
|---|---|---|
| Alt+W | メンバー変数として宣言する | クラスのヘッダー（`.h`）に `型 名前;` を足す |
| Alt+Q | ローカル変数に型を付ける | その場の `count = 0;` を `int count = 0;` にする |
| Alt+E | ゲッター・セッターを作る | `stride_` の `GetStride()` と `SetStride(...)` を `public:` の末尾に足す |
| Alt+G | 宣言と定義の引数を合わせる | ヘッダーの宣言と cpp の定義の引数を、変えた側に合わせる。引数を変えると、エディターで開いている相手にも自動で写す |
| Alt+F | `#include` を足す | カーソルの識別子（`std::vector`、`ComPtr`、`Camera`）のヘッダーを探して `#include` を足す。設定を `Auto` にすると、入力中にも自動で足す |

どのコマンドも、<strong>カーソルが行のどこにあっても</strong>押せます。対象は、行頭の `名前 = 右辺;` の左辺です。

```cpp
// Alloc.cpp
Alloc::Alloc(Dev* device, int type) {
    stride_ = device->GetStride(type);   // この行のどこでも Alt+W
}
```

Alt+W を押すと、`Alloc` の宣言から、ヘッダーに次の 1 行が入ります。

```cpp
 private:
  int capacity_;
  unsigned int stride_;
```

`Class::Func` の `Class` を宣言から探して、そのクラスの `private:` の末尾に足します。`private:` が最後でなければ、末尾に `private:` を作ってから足します。ヘッダーはエディターで開いたままになり（保存はしません）、作業中のファイルへ戻ります。挿入は 1 回の編集なので、Undo も 1 回です。字下げされた定義や、引数が複数行に分かれた定義でも見つかります。

## 型の決め方

右辺から、次の順に決めます。

1. <strong>式そのもの。</strong> `0` は `int`、`1.0f` は `float`、`true` は `bool`、`"abc"` は `const char*`、`static_cast<T>(...)` は `T`、`std::make_unique<T>(...)` は `std::unique_ptr<T>`、`new T` は `T*` です。
2. <strong>Quick Info（ホバーの内容）。</strong> 関数呼び出しなら、戻り値の型を取り出します。`virtual UINT __stdcall ID3D12Device::GetDescriptorHandleIncrementSize(...)` から `UINT` を取ります。変数や引数なら、その型を取ります。
3. <strong>どちらでも決まらないとき。</strong> Alt+W は型の入力欄を出します。Alt+Q は `auto` を入れます。

右辺が `cond ? A : B` の形のときは、A と B を順に試して、最初に型が決まったほうを使います。`{}` と `nullptr` の枝は、型を持たないので飛ばします。

`const` と参照は外して、値の型にそろえます（`const UINT&` は `UINT`）。ポインターの `const` は残します。

## ゲッター・セッター

メンバー変数の宣言行（`UINT stride_;`）にカーソルを置くか、`.cpp` の `stride_ = ...;` の行にカーソルを置いて、Alt+E を押します。名前は `stride_` から末尾の `_` を外して、先頭を大文字にします（`cpu_start_` は `GetCpuStart` / `SetCpuStart`）。

```cpp
 public:
  Alloc(Dev* device, int type);

  unsigned int GetStride() const { return stride_; }

  void SetStride(unsigned int value) { stride_ = value; }
```

同じ名前がすでにあるときは足しません。`public:` がなければ、クラスの先頭に作ります。型によって、書き方を変えます。

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

`ComPtr` のゲッターが `T*` なのは、呼び出し側が毎回 `.Get()` を書かなくて済むようにするためです。セッターを作らないのは、DirectX のオブジェクトは、作った側が持ち主になる使い方が多いからです。配列と `static` のメンバーは対象外です。

## 設定

拡張機能 メニューの「K-CppAssist の設定...」から開けます（ツール → オプション → K-CppAssist → 全般と同じ画面です）。

- <strong>ゲッターとセッターの間に空行を入れる</strong>（初期値は True）。True のときは、ゲッターの前（直前がメンバーの行のとき）と、ゲッターとセッターの間に空行を 1 行入れます。
- <strong>キー。</strong> 3 つのコマンドのキーをここで変えられます。「Alt+Q」「Ctrl+Alt+M」のように書き、OK を押すと Visual Studio のキー割り当てに反映されます。空にするとキーを外します。開いたときは、今の割り当てが表示されます。

## 制限

- 行頭が `名前 = 右辺;` の形で、1 行に収まっているものだけ扱います。`int x = 0;` のように、すでに型があるものは対象外です。
- Alt+W は `Class::Func(` の形の定義の中でだけ働きます。クラスの中に書いた関数と、ラムダの中では使えません。
- ヘッダーは、ソリューションのフォルダーの下から探します。cpp と同じ名前の `.h` を先に見て、なければ `class Class {` を含む `.h` を探します。クラスが入れ子や、同じ名前が複数あるときは、最初に見つかったものに足します。
- 右辺に演算子が入る式（`a + b` など）は、Quick Info では決められないので、入力欄（Alt+W）か `auto`（Alt+Q）になります。
- Alt+W は、Visual Studio の「ウィンドウ」メニューのアクセスキーと重なります。効かないときは、設定のキーで別のキーに付け替えてください。
- 失敗したときは、ステータスバーに理由が出ます。詳しいログは `%LOCALAPPDATA%\K-CppAssist\vsix.log` です。

## ソースコードと更新履歴

ソースは [GitHub](https://github.com/qwzxdf/kdocs/tree/main/k-cppassist) にあります（MIT ライセンス）。

| 版 | 内容 |
| --- | --- |
| 0.7.1 | 引数の自動合わせで、相手が開いていなくても、開いて書き換えるようにした(書き換えたあとは、作業中のファイルへ戻る) |
| 0.7.0 | Alt+G で、ヘッダーの宣言と cpp の定義の引数を合わせられるようにした。引数を変えると、エディターで開いている相手の引数を自動で書き換える。`#include` のパスを、プロジェクトが実際に使っている基準(既存の `#include` から学ぶ)に合わせた |
| 0.6.0 | Alt+F で `#include` を足せるようにした。設定を `Auto` にすると、入力中に未定義の型を見つけて自動で足す（型の位置だけ・波線つきだけ・一意なヘッダーだけ。足した直後に消したら戻す） |
| 0.5.0 | 拡張機能 メニューを「K-CppAssist の設定...」の 1 つだけにした（3 つのコマンドは、キーだけで使う） |
| 0.4.1 | 名前を K-CppMember から K-CppAssist に変えた（機能をメンバー変数以外にも広げるため）。`cond ? A : B` の右辺で、型の決まる枝から型を取るようにした（`{}` や `nullptr` の枝は飛ばす） |
| 0.4.0 | 字下げされた定義と、引数が複数行の定義でも Alt+W が働くようにした。型ごとのゲッター・セッターに対応し、設定（空行・キー）を追加した |
| 0.3.0 | Alt+E でゲッター・セッター（`GetXxx` / `SetXxx`）を作れるようにした |
| 0.2.1 | カーソルが行のどこにあっても、行頭の代入を対象にした |
| 0.2.0 | Alt+W でヘッダーにメンバー変数を足し、Alt+Q でローカル変数に型を付けるようにした |
| 0.1.0 | 最初の版（右辺の Quick Info をログに出すだけ） |
