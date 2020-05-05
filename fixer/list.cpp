#include<vector>
using namespace std;

template < class T, class Alloc = allocator<T> > class Python_List:private vector{
	void append (T&& val){this->push_back(val);}
};

int main(){
	return 0;
}
