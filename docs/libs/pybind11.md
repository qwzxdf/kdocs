---
title: pybind11（C++ と Python の連携）
tags:
  - 外部ライブラリ
---

# pybind11（C++ と Python の連携）

ゲームを作っていると、周辺のツール（アセットの変換、データの集計、バランス調整のグラフ）は、Python で書くほうが圧倒的に楽です。ところが、ゲーム本体は C++ なので、「Python のツールから、ゲームのクラスや関数を呼びたい」「C++ のゲームの中から、Python のスクリプトを呼びたい」という場面が出てきます。

pybind11 は、<strong>C++ の関数やクラスを Python から使える形にし、逆に C++ から Python を呼ぶ</strong>ためのヘッダーのみのライブラリです。

!!! tip "ポイント"
    - 方向は 2 つある。C++ を Python のモジュールにする（拡張モジュール）と、C++ の中で Python を動かす（埋め込み）
    - 拡張モジュールは、DLL（拡張子 `.pyd`）として作る。Python から `import` で使える
    - `PYBIND11_MODULE` マクロの中に見せたい関数やクラスを並べる
    - 型変換は自動。`std::vector` や `std::string` は、Python のリストや文字列になる
    - Python のバージョンと、ビルドの設定（x64、Debug/Release）をそろえる

!!! info "このページを読む前に"
    - [外部ライブラリの入れ方](../vs/libraries.md)（vcpkg）
    - [sol2（Lua の組み込み）](sol2.md)（スクリプト言語を組み込む、似た考え方）

## 導入（Visual Studio） {#setup}

vcpkg で入れます。

```json
{
  "dependencies": ["pybind11"]
}
```

Python の開発用ファイル（ヘッダーと `.lib`）も必要です。Python のインストーラーで「Download debug binaries」などを含めておくか、vcpkg の `python3` を使います。インクルードとライブラリのパスは、プロジェクトの設定に追加します。

そのほかの方法は、公式のドキュメントを見てください。

## C++ を Python から使う（拡張モジュール） {#module}

```cpp
#include <pybind11/pybind11.h>

namespace py = pybind11;

int Add(int a, int b) { return a + b; }

struct Player {
  int hp = 100;
  void Heal(int amount) { hp += amount; }
};

// モジュール名 gamecore。Python から import gamecore で使える
PYBIND11_MODULE(gamecore, m) {
  m.doc() = "ゲームの C++ 機能";
  m.def("add", &Add, "2 つの整数を足す");

  py::class_<Player>(m, "Player")
      .def(py::init<>())                                // コンストラクター
      .def_readwrite("hp", &Player::hp)                 // メンバー変数
      .def("heal", &Player::Heal, py::arg("amount"));   // メンバー関数
}
```

```python
import gamecore

print(gamecore.add(2, 3))     # 5

p = gamecore.Player()
p.heal(20)
print(p.hp)                   # 120
```

プロジェクトは、DLL として作り、出力のファイル名の拡張子を `.pyd` にします。ファイル名は、モジュール名（`gamecore.pyd`）と一致させます。これを Python が探せる場所（スクリプトと同じフォルダー）に置くと、`import` で読み込めます。

`py::arg("amount")` は、Python 側でキーワード引数（`p.heal(amount=20)`）を使えるようにします。省略もできます。

## C++ から Python を使う（埋め込み） {#embed}

```cpp
#include <pybind11/embed.h>

namespace py = pybind11;

int main() {
  py::scoped_interpreter guard{};   // Python の実行環境を起動する（スコープを抜けると終了）

  py::exec("print('hello from python')");          // 文字列を実行する

  py::module_ math = py::module_::import("math");  // Python のモジュールを使う
  double r = math.attr("sqrt")(16.0).cast<double>();  // 4.0
}
```

`py::scoped_interpreter` は、Python のインタープリタを起動し、スコープを抜けると終了します。1 つのプロセスで、1 回だけ作ります。

`py::module_::import` で、Python のモジュールを読み込み、`attr("名前")` で関数や変数を取り出して呼びます。戻り値は Python のオブジェクトで、`cast<型>()` で C++ の型に変換します。

## 型の変換 {#types}

基本の型は、自動で変換されます。`std::vector` や `std::map` を変換するには、`pybind11/stl.h` を追加で取り込みます。

```cpp
#include <pybind11/stl.h>   // std::vector, std::map, std::string などの変換

std::vector<int> Double(const std::vector<int>& v) {
  std::vector<int> out;
  for (int x : v) out.push_back(x * 2);
  return out;
}
```

変換は<strong>コピー</strong>を伴います。大きな配列（頂点データなど）を毎回コピーすると遅いので、NumPy の配列とメモリを共有する `py::array_t` を使います。

## 使いどころ {#use}

ゲームの周辺ツールを Python で書く場合に便利です。

- アセットの変換、一括処理のツールから、ゲームの形式の読み書きを呼ぶ
- バランス調整の計算をゲームの本物のコードで実行して、Python でグラフにする
- 自動テストを Python で書く

ゲーム本体の中の組み込みスクリプトには、Python は大きすぎます。Lua のような軽いものが向きます。

## よくあるミス {#mistakes}

??? failure "`import` すると、モジュールが見つからない／ DLL の読み込みに失敗する"
    Python のバージョン、x64/x86、Debug/Release が合っていません。Debug ビルドの Python 用ライブラリ（`python3x_d.lib`）が要ることもあります。

??? failure "リストを渡すたびに、重くなる"
    `std::vector` の変換はコピーです。大きなデータは NumPy の配列で共有します。

??? failure "Python のオブジェクトをインタープリタの終了後に触って落ちる"
    `scoped_interpreter` のスコープの外で、Python のオブジェクトを解放しています。オブジェクトは、スコープの中で破棄します。

## これだけ覚える {#summary}

- 拡張モジュール（C++ を Python から）と埋め込み（C++ から Python を）の 2 方向
- `PYBIND11_MODULE` に、見せたい関数とクラスを並べる。出力は `.pyd`
- Python のバージョンとビルド設定をそろえる。大きなデータのコピーに注意

## 関連ページ

- [外部ライブラリ](index.md)
- [sol2（Lua の組み込み）](sol2.md)
- [よくあるエラー](../vs/errors.md)
