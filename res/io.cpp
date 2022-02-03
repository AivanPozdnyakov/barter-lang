#include <iostream>
#include <fstream>
using std::ofstream;

int main () {
  ofstream myfile;
  myfile.open ("example.txt");
  myfile << "Writing this to a file.\n";
  myfile << 1;
  myfile << false;
  myfile.close();
  return 0;
}