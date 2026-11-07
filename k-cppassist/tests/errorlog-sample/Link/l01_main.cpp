// リンクエラー(コンパイルは通る)
#include <iostream>

int Declared(int);                       // 定義がない: LNK2019
void NeverDefined();                     // LNK2019
extern int g_missing;                    // LNK2001: 未解決の外部シンボル
extern int g_dup;

struct Widget {
  void Draw();                           // 定義なし
  static int count;                      // 静的メンバーの定義なし
};

int main() {
  std::cout << Declared(1) << g_missing << g_dup << "\n";
  NeverDefined();
  Widget w;
  w.Draw();
  std::cout << Widget::count;
  return 0;
}
