#include <mandarin/mandarin.hpp>

#include <cstlib>
#include <iostream>


using std::vector;
using std::shared_ptr;
using std::make_shared;
using mandarin::support::Object;
using Value = shared_ptr<Object>;
using ArgList = const vector<Value>&;


namespace mandarin::support
{

namespace
{
    template <typename Class, typename Object>
    bool isinstance(const shared_ptr<Object>& object)
    {
        return object->_mndr_type_object()->_mndr_is_subclass(Class::_mndr_static_type_object());
    }

    [[noreturn]] void error(const std::string& message)
    {
        std::cerr << "Fatal mandarin error: " << message << std::endl;
        abort();
    }
} // anonymous namespace



// Empty for now
GenericObject::GenericObject()
{ }

// Empty for now
GenericObject::~GenericObject()
{ }

shared_ptr<Type> GenericObject::_mndr_type_object()
{
    return make_shared<Type>("GenericObject", nullptr);
}

shared_ptr<Type> GenericObject::_mndr_static_type_object()
{
    return make_shared<Type>("GenericObject", nullptr);
}



Object::Object()
{
    _mndr_setup_member_table();
}

void Object::_mndr_setup_member_table()
{ }

shared_ptr<Type> Object::_mndr_type_object()
{
    return make_shared<Type>("Object", GenericObject::_mndr_static_type_object());
}

shared_ptr<Type> Object::_mndr_static_type_object()
{
    return make_shared<Type>("Object", GenericObject::_mndr_static_type_object());
}



Function::Function(
    const std::function<Value(Arglist)>& func,
    const vector<Type>& arg_types
):
    func(func),
    arg_types(arg_types),
    Object()
{ }

Function::_mndr_setup_member_table()
{
    member_table = {};
}

Value Function::_mndr_call(Arglist args)
{
    if (args.size() != arg_types.size()) {
        error("TypeError: arguments number mismatch (expected " + std::to_string(args.size()) + ")");
    }
    for (size_t i = 0; i < args.size(); ++i) {
        if (!isinstance(args[i], arg_types[i])) {
            error("TypeError: invalid argument type (expected " + arg_types[i]->name + ")");
        }
    }
}

shared_ptr<Type> Function::_mndr_type_object()
{
    return make_shared<Type>("Function", Object::_mndr_static_type_object());
}

shared_ptr<Type> Function::_mndr_static_type_object()
{
    return make_shared<Type>("Function", Object::_mndr_static_type_object());
}



Type::Type(const shared_ptr<Type>& parent):
    parent(parent)
{ }

void Type::_mndr_setup_member_table()
{
    member_table = {
        {
            "is_subclass",
            Function(
                [this](Arglist args) { return this->mndr_is_subclass(args); },
                {Type::_mndr_static_type_object()}
            )
        },
        {
            "name",
            Function(
                [this](Arglist args) { return this->mndr_name(args); },
                {}
            )
        },
    };
}

bool Type::_mndr_is_subclass(const shared_ptr<Type>& other)
{
    // XXX: STUB test for type equality
    if (name == other.name) {
        return true;
    }
    if (parent == nullptr) {
        return false;
    }

    return parent->_mndr_is_subclass(other);
}

Value Type::mndr_is_subclass(ArgList args)
{
    if (args.size() != 1) {
        error("TypeError: Type.is_subclass: invalid number of arguments (expected 1)");
    }
    if (!isinstance<Type>(args[0])) {
        error("TypeError: Type.is_subclass: expected an argument of type Type");
    }
    return _mndr_is_subclass(args[0]);
}

Value Type::mndr_name(ArgList args)
{
    if (args.size() != 0) {
        error("TypeError: Type.name: invalid number of arguments (expected 0)");
    }
    return make_shared<mndr_Str>(name);
}

shared_ptr<Type> Type::_mndr_type_object()
{
    return make_shared<Type>("Type", Object::_mndr_static_type_object());
}

shared_ptr<Type> Type::_mndr_static_type_object()
{
    return make_shared<Type>("Type", Object::_mndr_static_type_object());
}

} // namespace mandarin::support
