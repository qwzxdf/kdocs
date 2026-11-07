// 存在しないヘッダー・名前空間
#include "no_such_header.h"              // C1083: 開けない
#include <nonexistent>                   // C1083
#include <iostream>

using namespace nosuchns;                // C2871: 名前空間がない

void Include() {
  std::cout << "hi";
  MissingType t;                         // C2065
  using Foo = std::missing_alias;        // C2039
}
