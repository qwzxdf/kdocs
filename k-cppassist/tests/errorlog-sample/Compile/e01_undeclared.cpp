// 未宣言・スペルミス・スコープ外
#include <iostream>
#include <vector>

int Sum(int a, int b) { return a + b; }

void Undeclared() {
  int total = Sum(1, 2);
  std::cout << totl << "\n";           // C2065: スペルミス
  std::cout << undefined_var << "\n";  // C2065: 宣言なし
  Summ(3, 4);                          // C3861: 関数が見つからない
  {
    int inner = 1;
  }
  inner = 2;                           // C2065: スコープ外
  std::vectr<int> v;                   // C2039: std に vectr はない
  strng s;                             // C2065: 型名のスペルミス
  (void)total;
}
