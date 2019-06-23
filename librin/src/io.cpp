#include <mandarin/mandarin.hpp>
#include <cstdlib>
#include <iostream>


namespace mandarin::user
{

using std::shared_ptr;
using mandarin::support::Object;
using std::vector;


shared_ptr<Object> mndr_print(const vector<shared_ptr<Object>>& args)
{
    if (args.size() != 1) {
        std::cerr << "Fatal mandarin error: print: wrong number of arguments (expected 1)" << std::endl;
        abort();
    }
    std::cout << mandarin::support::dynamic_cast_to<mndr_Str>(
        args[0]->_mndr_call_method("to_string", {})
    )->str << std::endl;
    
    return mandarin::support::value_of_none;
}

shared_ptr<Object> mndr_input(const vector<shared_ptr<Object>>& args)
{
    if (args.size() != 0) {
        std::cerr << "Fatal mandarin error: print: wrong number of arguments (expected 0)" << std::endl;
        abort();
    }
    std::string s;
    std::getline(std::cin, s);
    return std::static_pointer_cast<Object>(std::make_shared<mndr_Str>(s));
}

} // namespace mandarin::user
