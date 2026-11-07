// 構文エラー(波及して複数の行にエラーが出る)
#include <iostream>

struct Missing {
  int x
};                                       // C2143: ; がない

void NoSemicolon() {
  int a = 1
  int b = 2;                             // C2146
  std::cout << a + b << std::endl
}

void UnbalancedParen() {
  if (1 + (2 * 3) {                      // C2059 / C2143
    std::cout << "x";
  }
}

int LoopTypo() {
  for (int i = 0; i < 3; ++i {           // C2143
  }
  return 0;
}

void Stray() {
  int x = ;                              // C2059: 式がない
  else { }                               // C2181: if のない else
}
