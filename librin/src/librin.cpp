#include <mandarin/mandarin.hpp>

#include <cstdlib>
#include <iostream>
#include <cmath>


using std::vector;
using std::shared_ptr;
using std::make_shared;
using mandarin::support::Object;
using Value = shared_ptr<Object>;
using ArgList = const vector<Value>&;


namespace
{
    template <typename T, typename... Args>
    shared_ptr<Object> make_object(Args&&... args)
    {
        static_assert(std::is_base_of_v<Object, T>, "Type must be derived from mandarin::support::Object");
        return std::static_pointer_cast<Object>(
            std::make_shared<T>(std::forward<Args>(args)...)
        );
    }

    template <typename Class, typename Object>
    bool isinstance(const shared_ptr<Object>& object)
    {
        return object->_mndr_type_object()->_mndr_is_subclass(Class::_mndr_static_type_object());
    }

    template <typename Object>
    bool isinstance(const shared_ptr<Object>& object, const shared_ptr<mandarin::support::Type>& cls)
    {
        return object->_mndr_type_object()->_mndr_is_subclass(cls);
    }

    [[noreturn]] void error(const std::string& message)
    {
        std::cerr << "Fatal mandarin error: " << message << std::endl;
        abort();
    }
} // anonymous namespace


namespace mandarin::support
{

Object::Object()
{
    _mndr_setup_member_table();
}

Object::~Object()
{ }

void Object::_mndr_setup_member_table()
{ }

shared_ptr<Type> Object::_mndr_type_object()
{
    return make_shared<Type>("Object", nullptr);
}

shared_ptr<Type> Object::_mndr_static_type_object()
{
    return make_shared<Type>("Object", nullptr);
}

void Object::_mndr_maybe_call_method(const std::string& name, ArgList args)
{
    if (auto it = this->member_table.find(name); it != this->member_table.end()) {
        const auto& [k, v] = *it;
        if (!isinstance<Function>(v)) {
            error("Cannot call non-method member");
        }
        auto func = std::static_pointer_cast<Function>(v);
        func->_mndr_call(args);
    }
}

Value Object::_mndr_call_method(const std::string& name, ArgList args)
{
    if (auto it = this->member_table.find(name); it != this->member_table.end()) {
        const auto& [k, v] = *it;
        if (!isinstance<Function>(v)) {
            error("Cannot call non-method member");
        }
        auto func = std::static_pointer_cast<Function>(v);
        return func->_mndr_call(args);
    } else {
        error("Method " + name + " not found");
    }
}

Value Object::_mndr_unary_plus()
{
    return _mndr_call_method("__unary_plus__", {});
}

Value Object::_mndr_unary_minus()
{
    return _mndr_call_method("__unary_minus__", {});
}

Value Object::_mndr_unary_negate()
{
    return _mndr_call_method("__unary_negate__", {});
}

Value Object::_mndr_unary_compl()
{
    return _mndr_call_method("__unary_compl__", {});
}

Value Object::_mndr_binary_multiply(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__multiply__", {rhs});
}

Value Object::_mndr_binary_divide(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__divide__", {rhs});
}

Value Object::_mndr_binary_modulo(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__modulo__", {rhs});
}

Value Object::_mndr_binary_int_divide(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__int_divide__", {rhs});
}

Value Object::_mndr_binary_plus(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__add__", {rhs});
}

Value Object::_mndr_binary_minus(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__sub__", {rhs});
}

Value Object::_mndr_binary_incrange(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__incrange__", {rhs});
}

Value Object::_mndr_binary_range(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__range__", {rhs});
}

Value Object::_mndr_binary_equals(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__equals__", {rhs});
}

Value Object::_mndr_binary_less_equals(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__less_equals__", {rhs});
}

Value Object::_mndr_binary_greater_equals(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__greater_equals__", {rhs});
}

Value Object::_mndr_binary_not_equals(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__not_equals__", {rhs});
}

Value Object::_mndr_binary_less(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__less__", {rhs});
}

Value Object::_mndr_binary_greater(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__greater__", {rhs});
}

Value Object::_mndr_binary_logical_and(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__and__", {rhs});
}

Value Object::_mndr_binary_logical_or(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__or__", {rhs});
}

Value Object::_mndr_binary_logical_xor(const std::shared_ptr<Object>& rhs)
{
    return _mndr_call_method("__xor__", {rhs});
}

Value Object::_mndr_call(const std::vector<std::shared_ptr<Object>>& args)
{
    return _mndr_call_method("__call__", args);
}




Function::Function(
    const std::function<Value(ArgList)>& func,
    const vector<shared_ptr<Type>>& arg_types
):
    Object(),
    func(func),
    arg_types(arg_types)
{ }

void Function::_mndr_setup_member_table()
{
    member_table = {};
}

Value Function::_mndr_call(ArgList args)
{
    if (args.size() != arg_types.size()) {
        error("TypeError: arguments number mismatch (expected " + std::to_string(args.size()) + ")");
    }
    for (size_t i = 0; i < args.size(); ++i) {
        if (!isinstance(args[i], arg_types[i])) {
            error("TypeError: invalid argument type (expected " + arg_types[i]->name + ")");
        }
    }
    return func(args);
}

shared_ptr<Type> Function::_mndr_type_object()
{
    return make_shared<Type>("Function", Object::_mndr_static_type_object());
}

shared_ptr<Type> Function::_mndr_static_type_object()
{
    return make_shared<Type>("Function", Object::_mndr_static_type_object());
}



Type::Type(const std::string& name, const shared_ptr<Type>& parent):
    Object(),
    parent(parent),
    name(name)
{ }

void Type::_mndr_setup_member_table()
{
    member_table = {
        {
            "is_subclass",
            make_object<Function>(
                [this](ArgList args) { return this->mndr_is_subclass(args); },
                std::vector<shared_ptr<Type>>{Type::_mndr_static_type_object()}
            )
        },
        {
            "name",
            make_object<Function>(
                [this](ArgList args) { return this->mndr_name(args); },
                std::vector<shared_ptr<Type>>{}
            )
        },
    };
}

bool Type::_mndr_is_subclass(const shared_ptr<Type>& other)
{
    // XXX: STUB test for type equality
    if (name == other->name) {
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
    return make_object<mandarin::user::mndr_Bool>(_mndr_is_subclass(std::static_pointer_cast<Type>(args[0])));
}

Value Type::mndr_name(ArgList args)
{
    if (args.size() != 0) {
        error("TypeError: Type.name: invalid number of arguments (expected 0)");
    }
    return make_shared<mandarin::user::mndr_Str>(name);
}

shared_ptr<Type> Type::_mndr_type_object()
{
    return make_shared<Type>("Type", Object::_mndr_static_type_object());
}

shared_ptr<Type> Type::_mndr_static_type_object()
{
    return make_shared<Type>("Type", Object::_mndr_static_type_object());
}



shared_ptr<Object> value_of_true    = std::make_shared<mandarin::user::mndr_Bool>(true);
shared_ptr<Object> value_of_false   = std::make_shared<mandarin::user::mndr_Bool>(false);
shared_ptr<Object> value_of_none    = std::make_shared<mandarin::user::mndr_NoneType>();

} // namespace mandarin::support


namespace mandarin::user
{

using mandarin::support::Type;
using mandarin::support::Function;

void mndr_NoneType::_mndr_setup_member_table()
{
    member_table = {
        {
            "to_string",
            make_object<Function>(
                [this](ArgList args) { return this->mndr_to_string(args); },
                std::vector<shared_ptr<Type>>{}
            )
        },
    };
}


Value mndr_NoneType::mndr_to_string(ArgList args)
{
    return make_shared<mndr_Str>("none");
}

shared_ptr<Type> mndr_NoneType::_mndr_type_object()
{
    return make_shared<Type>("NoneType", Object::_mndr_static_type_object());
}

shared_ptr<Type> mndr_NoneType::_mndr_static_type_object()
{
    return make_shared<Type>("NoneType", Object::_mndr_static_type_object());
}



#define DEFUN(name, ...) \
    {   \
        #name, \
        make_object<Function>( \
            [this](ArgList args) {return this->mndr_##name(args);}, \
            std::vector<shared_ptr<Type>>{__VA_ARGS__} \
        ) \
    }

#define TO(Class) Class::_mndr_static_type_object()

#define CAST std::static_pointer_cast


mndr_Bool::mndr_Bool(bool v):
    Object(),
    raw_value(v)
{ }

void mndr_Bool::_mndr_setup_member_table()
{
    member_table = {
        DEFUN(__unary_negate__),
        DEFUN(to_string),
    };
}

Value mndr_Bool::mndr___unary_negate__(ArgList args)
{
    if (raw_value) {
        return mandarin::support::value_of_false;
    } else {
        return mandarin::support::value_of_true;
    }
}

Value mndr_Bool::mndr_to_string(ArgList args)
{
    if (raw_value) {
        return make_shared<mndr_Str>("true");
    } else {
        return make_shared<mndr_Str>("false");
    }
}

shared_ptr<Type> mndr_Bool::_mndr_type_object()
{
    return make_shared<Type>("Bool", TO(Object));
}

shared_ptr<Type> mndr_Bool::_mndr_static_type_object()
{
    return make_shared<Type>("Bool", TO(Object));
}



mndr_Int::mndr_Int(mandarin::support::IntegerType v):
    Object(),
    raw_value(v)
{ }

void mndr_Int::_mndr_setup_member_table()
{
    member_table = {
        DEFUN(__unary_plus__),
        DEFUN(__unary_minus__),
        DEFUN(__unary_compl__),
        DEFUN(__add__,                  TO(mndr_Int)),
        DEFUN(__sub__,                  TO(mndr_Int)),
        DEFUN(__multiply__,             TO(mndr_Int)),
        DEFUN(__divide__,               TO(mndr_Int)),
        DEFUN(__int_divide__,           TO(mndr_Int)),
        DEFUN(__modulo__,               TO(mndr_Int)),
        DEFUN(__incrange__,             TO(mndr_Int)),
        DEFUN(__range__,                TO(mndr_Int)),
        DEFUN(__less__,                 TO(mndr_Int)),
        DEFUN(__greater__,              TO(mndr_Int)),
        DEFUN(__less_equals__,          TO(mndr_Int)),
        DEFUN(__greater_equals__,       TO(mndr_Int)),
        DEFUN(__equals__,               TO(mndr_Int)),
        DEFUN(__not_equals__,           TO(mndr_Int)),
        DEFUN(__assign_plus__,          TO(mndr_Int)),
        DEFUN(__assign_minus__,         TO(mndr_Int)),
        DEFUN(__assign_multiply__,      TO(mndr_Int)),
        DEFUN(__assign_int_divide__,    TO(mndr_Int)),
        DEFUN(__assign_modulo__,        TO(mndr_Int)),
        DEFUN(to_string),
    };
}

Value mndr_Int::mndr___unary_plus__(ArgList args)
{
    return make_object<mndr_Int>(raw_value);
}

Value mndr_Int::mndr___unary_minus__(ArgList args)
{
    return make_object<mndr_Int>(-raw_value);
}

Value mndr_Int::mndr___unary_compl__(ArgList args)
{
    return make_object<mndr_Int>(~raw_value);
}

Value mndr_Int::mndr___add__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Int>(raw_value + other);
}

Value mndr_Int::mndr___sub__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Int>(raw_value - other);
}

Value mndr_Int::mndr___multiply__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Int>(raw_value * other);
}

Value mndr_Int::mndr___divide__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Float>(double(raw_value) / double(other));
}

Value mndr_Int::mndr___int_divide__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Int>(raw_value / other);
}

Value mndr_Int::mndr___modulo__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Int>(raw_value % other);
}

Value mndr_Int::mndr___incrange__(ArgList args)
{
    error("Ranges are not yet implemented");
}

Value mndr_Int::mndr___range__(ArgList args)
{
    error("Ranges are not yet implemented");
}

Value mndr_Int::mndr___less__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value < other);
}

Value mndr_Int::mndr___greater__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value > other);
}

Value mndr_Int::mndr___less_equals__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value <= other);
}

Value mndr_Int::mndr___greater_equals__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value >= other);
}

Value mndr_Int::mndr___equals__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value == other);
}

Value mndr_Int::mndr___not_equals__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value != other);
}

Value mndr_Int::mndr___assign_plus__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    raw_value += other;
    return mandarin::support::value_of_none;
}

Value mndr_Int::mndr___assign_minus__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    raw_value -= other;
    return mandarin::support::value_of_none;
}

Value mndr_Int::mndr___assign_multiply__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    raw_value *= other;
    return mandarin::support::value_of_none;
}

Value mndr_Int::mndr___assign_int_divide__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    raw_value /= other;
    return mandarin::support::value_of_none;
}

Value mndr_Int::mndr___assign_modulo__(ArgList args)
{
    auto other = CAST<mndr_Int>(args.at(0))->raw_value;
    raw_value %= other;
    return mandarin::support::value_of_none;
}

Value mndr_Int::mndr_to_string(ArgList args)
{
    return make_shared<mndr_Str>(std::to_string(raw_value));
}

shared_ptr<Type> mndr_Int::_mndr_type_object()
{
    return make_shared<Type>("Int", TO(Object));
}

shared_ptr<Type> mndr_Int::_mndr_static_type_object()
{
    return make_shared<Type>("Int", TO(Object));
}



mndr_Float::mndr_Float(double v):
    Object(),
    raw_value(v)
{ }

void mndr_Float::_mndr_setup_member_table()
{
    member_table = {
        DEFUN(__unary_plus__),
        DEFUN(__unary_minus__),
        DEFUN(__add__,                  TO(mndr_Float)),
        DEFUN(__sub__,                  TO(mndr_Float)),
        DEFUN(__multiply__,             TO(mndr_Float)),
        DEFUN(__divide__,               TO(mndr_Float)),
        DEFUN(__modulo__,               TO(mndr_Float)),
        DEFUN(__less__,                 TO(mndr_Float)),
        DEFUN(__greater__,              TO(mndr_Float)),
        DEFUN(__less_equals__,          TO(mndr_Float)),
        DEFUN(__greater_equals__,       TO(mndr_Float)),
        DEFUN(__equals__,               TO(mndr_Float)),
        DEFUN(__not_equals__,           TO(mndr_Float)),
        DEFUN(__assign_plus__,          TO(mndr_Float)),
        DEFUN(__assign_minus__,         TO(mndr_Float)),
        DEFUN(__assign_multiply__,      TO(mndr_Float)),
        DEFUN(__assign_divide__,        TO(mndr_Float)),
        DEFUN(__assign_modulo__,        TO(mndr_Float)),
        DEFUN(to_string),
    };
}

Value mndr_Float::mndr___unary_plus__(ArgList args)
{
    return make_object<mndr_Float>(raw_value);
}

Value mndr_Float::mndr___unary_minus__(ArgList args)
{
    return make_object<mndr_Float>(-raw_value);
}

Value mndr_Float::mndr___add__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Float>(raw_value + other);
}

Value mndr_Float::mndr___sub__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Float>(raw_value - other);
}

Value mndr_Float::mndr___multiply__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Float>(raw_value * other);
}

Value mndr_Float::mndr___divide__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Float>(raw_value / other);
}

Value mndr_Float::mndr___modulo__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Float>(fmod(raw_value, other));
}

Value mndr_Float::mndr___less__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value < other);
}

Value mndr_Float::mndr___greater__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value > other);
}

Value mndr_Float::mndr___less_equals__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value <= other);
}

Value mndr_Float::mndr___greater_equals__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value >= other);
}

Value mndr_Float::mndr___equals__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value == other);
}

Value mndr_Float::mndr___not_equals__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    return make_object<mndr_Bool>(raw_value != other);
}

Value mndr_Float::mndr___assign_plus__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    raw_value += other;
    return mandarin::support::value_of_none;
}

Value mndr_Float::mndr___assign_minus__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    raw_value -= other;
    return mandarin::support::value_of_none;
}

Value mndr_Float::mndr___assign_multiply__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    raw_value *= other;
    return mandarin::support::value_of_none;
}

Value mndr_Float::mndr___assign_divide__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    raw_value /= other;
    return mandarin::support::value_of_none;
}

Value mndr_Float::mndr___assign_modulo__(ArgList args)
{
    auto other = CAST<mndr_Float>(args.at(0))->raw_value;
    raw_value = fmod(raw_value, other);
    return mandarin::support::value_of_none;
}

Value mndr_Float::mndr_to_string(ArgList args)
{
    return make_shared<mndr_Str>(std::to_string(raw_value));
}

shared_ptr<Type> mndr_Float::_mndr_type_object()
{
    return make_shared<Type>("Float", TO(Object));
}

shared_ptr<Type> mndr_Float::_mndr_static_type_object()
{
    return make_shared<Type>("Float", TO(Object));
}



mndr_Str::mndr_Str(const std::string& s):
    Object(),
    str(s)
{ }

void mndr_Str::_mndr_setup_member_table()
{
    member_table = {
        DEFUN(__add__,                  TO(mndr_Str)),
        DEFUN(__multiply__,             TO(mndr_Int)),
        DEFUN(__less__,                 TO(mndr_Str)),
        DEFUN(__greater__,              TO(mndr_Str)),
        DEFUN(__less_equals__,          TO(mndr_Str)),
        DEFUN(__greater_equals__,       TO(mndr_Str)),
        DEFUN(__equals__,               TO(mndr_Str)),
        DEFUN(__not_equals__,           TO(mndr_Str)),
        DEFUN(__assign_plus__,          TO(mndr_Str)),
        DEFUN(__assign_multiply__,      TO(mndr_Int)),
        DEFUN(to_string),
    };
}

Value mndr_Str::mndr___add__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Str>(str + other);
}

Value mndr_Str::mndr___multiply__(ArgList args)
{
    auto n = CAST<mndr_Int>(args.at(0))->raw_value;
    std::string s;
    for (decltype(n) i = 0; i < n; ++i) {
        s += str;
    }
    return make_object<mndr_Str>(s);
}

Value mndr_Str::mndr___less__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str < other);
}

Value mndr_Str::mndr___greater__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str > other);
}

Value mndr_Str::mndr___less_equals__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str <= other);
}

Value mndr_Str::mndr___greater_equals__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str >= other);
}

Value mndr_Str::mndr___equals__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str == other);
}

Value mndr_Str::mndr___not_equals__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    return make_object<mndr_Bool>(str != other);
}

Value mndr_Str::mndr___assign_plus__(ArgList args)
{
    const auto& other = CAST<mndr_Str>(args.at(0))->str;
    str += other;
    return mandarin::support::value_of_none;
}

Value mndr_Str::mndr___assign_multiply__(ArgList args)
{
    auto n = CAST<mndr_Int>(args.at(0))->raw_value;
    std::string s = str;
    for (decltype(n) i = 0; i < n - 1; ++i) {
        str += s;
    }
    return mandarin::support::value_of_none;
}

Value mndr_Str::mndr_to_string(ArgList args)
{
    return make_object<mndr_Str>(str);
}

shared_ptr<Type> mndr_Str::_mndr_type_object()
{
    return make_shared<Type>("Str", Object::_mndr_static_type_object());
}

shared_ptr<Type> mndr_Str::_mndr_static_type_object()
{
    return make_shared<Type>("Str", Object::_mndr_static_type_object());
}

} // namespace mandarin::user
