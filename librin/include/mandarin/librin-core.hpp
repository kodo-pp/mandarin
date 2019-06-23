#ifndef LIBRIN_CORE_HPP_INCLUDED
#define LIBRIN_CORE_HPP_INCLUDED

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>
#include <functional>


namespace mandarin
{

namespace support
{
    using IntegerType = long;

    class Object;
    class Type;
    class Function;
}
namespace user
{
    class mndr_Str;
}
namespace support
{
    class Object
    {
    public:
        Object();
        Object(const Object& other) = delete;
        Object(Object&& other) = default;
        virtual ~Object();

        Object& operator=(const Object& other) = delete;
        Object& operator=(Object&& other) = default;

        virtual std::shared_ptr<Object> _mndr_unary_plus();
        virtual std::shared_ptr<Object> _mndr_unary_minus();
        virtual std::shared_ptr<Object> _mndr_unary_negate();
        virtual std::shared_ptr<Object> _mndr_unary_compl();

        virtual std::shared_ptr<Object> _mndr_binary_multiply       (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_divide         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_modulo         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_int_divide     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_plus           (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_minus          (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_incrange       (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_range          (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_equals         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_less_equals    (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_greater_equals (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_not_equals     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_less           (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_greater        (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_logical_and    (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_logical_or     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> _mndr_binary_logical_xor    (const std::shared_ptr<Object>& rhs);

        virtual std::shared_ptr<Object> _mndr_call(const std::vector<std::shared_ptr<Object>>& args);

        virtual std::shared_ptr<Type> _mndr_type_object();
        static std::shared_ptr<Type> _mndr_static_type_object();

        virtual void _mndr_setup_member_table();

        void _mndr_maybe_call_method(
            const std::string& name,
            const std::vector<std::shared_ptr<Object>>& args
        );

        std::shared_ptr<Object> _mndr_call_method(
            const std::string& name,
            const std::vector<std::shared_ptr<Object>>& args
        );


    protected:
        std::unordered_map<std::string, std::shared_ptr<Object>> member_table;
    };


    class Function : public Object
    {
    public:
        Function(
            const std::function<std::shared_ptr<Object>(const std::vector<std::shared_ptr<Object>>&)>& func,
            const std::vector<std::shared_ptr<Type>>& arg_types
        );

        void _mndr_setup_member_table() override;

        std::shared_ptr<Object> _mndr_call(const std::vector<std::shared_ptr<Object>>& args) override;

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();

        std::function<std::shared_ptr<Object>(const std::vector<std::shared_ptr<Object>>&)> func;
        std::vector<std::shared_ptr<Type>> arg_types;
    };


    class Type final : public Object
    {
    public:
        Type(const std::string& name, const std::shared_ptr<Type>& parent);

        void _mndr_setup_member_table() override;
        
        bool _mndr_is_subclass(const std::shared_ptr<Type>& other);
        std::shared_ptr<Object> mndr_is_subclass(const std::vector<std::shared_ptr<Object>>& args);
        std::shared_ptr<Object> mndr_name(const std::vector<std::shared_ptr<Object>>& args);

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();

        std::shared_ptr<Type> parent;
        std::string name;
    };

    
    namespace detail
    {
        template <typename T>
        struct remove_pointer
        {
            using type = T;
        };

        template <typename T>
        struct remove_pointer<std::shared_ptr<T>>
        {
            using type = T;
        };

        template <typename T>
        using remove_pointer_t = typename remove_pointer<T>::type;


        template <typename T>
        struct make_pointer
        {
            using type = std::shared_ptr<T>;
        };

        template <typename T>
        struct make_pointer<std::shared_ptr<T>>
        {
            using type = std::shared_ptr<T>;
        };

        template <typename T>
        using make_pointer_t = typename make_pointer<T>::type;
    } // namespace detail


    template <typename RawTo, typename From>
    detail::make_pointer_t<RawTo> cast_to(const std::shared_ptr<From>& x)
    {
        using To = detail::remove_pointer_t<RawTo>;
        return std::static_pointer_cast<To>(x);
    }


    template <typename RawTo, typename From>
    detail::make_pointer_t<RawTo> dynamic_cast_to(const std::shared_ptr<From>& x)
    {
        using To = detail::remove_pointer_t<RawTo>;
        auto ptr = x.get();
        bool convertible = x->_mndr_type_object()->_mndr_is_subclass(To::_mndr_static_type_object());
        if (!convertible) {
            // TODO: raise (mandarin) exception
            std::cerr << "Fatal mandarin error: invalid dynamic_cast_to" << std::endl;
            abort();
        }

        return std::static_pointer_cast<To>(x);
    }
} // namespace support


namespace user
{
    using mandarin::support::Type;
    class mndr_NoneType : public mandarin::support::Object
    {
        void _mndr_setup_member_table() override;
        std::shared_ptr<mandarin::support::Object> mndr_to_string(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();
    };

    class mndr_Bool : public mandarin::support::Object
    {
    public:
        mndr_Bool(bool v = false);
        void _mndr_setup_member_table() override;

        std::shared_ptr<mandarin::support::Object> mndr_new(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_negate__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr_to_string(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();

        bool raw_value;
    };

    class mndr_Int : public mandarin::support::Object
    {
    public:
        mndr_Int(mandarin::support::IntegerType v = 0);
        void _mndr_setup_member_table() override;

        std::shared_ptr<mandarin::support::Object> mndr_new(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_plus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_minus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_compl__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___add__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___sub__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___divide__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___int_divide__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___modulo__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___incrange__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___range__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___not_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_plus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_minus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_int_divide__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_modulo__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr_to_string(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();
        mandarin::support::IntegerType raw_value;
    };


    class mndr_Float : public mandarin::support::Object
    {
    public:
        mndr_Float(double v = 0.0);
        void _mndr_setup_member_table() override;

        std::shared_ptr<mandarin::support::Object> mndr_new(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_plus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___unary_minus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___add__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___sub__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___divide__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___modulo__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___not_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_plus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_minus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_divide__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_modulo__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr_to_string(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();
        double raw_value;
    };


    class mndr_Str : public mandarin::support::Object
    {
    public:
        mndr_Str(const std::string& s = "");
        void _mndr_setup_member_table() override;

        std::shared_ptr<mandarin::support::Object> mndr_new(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___add__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___less_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___greater_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___not_equals__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_plus__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr___assign_multiply__(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );
        std::shared_ptr<mandarin::support::Object> mndr_to_string(
            const std::vector<std::shared_ptr<mandarin::support::Object>>& args
        );

        std::shared_ptr<Type> _mndr_type_object() override;
        static std::shared_ptr<Type> _mndr_static_type_object();
        std::string str;
    };
} // namespace user


namespace support
{
    template <typename T>
    bool native_bool(const std::shared_ptr<T>& x)
    {
        if (!x->_mndr_type_object()->_mndr_is_subclass(mandarin::user::mndr_Bool::_mndr_static_type_object())) {
            // TODO(?): raise (mandarin) exception
            std::cerr << "Fatal mandarin error: invalid native_bool" << std::endl;
            abort();
        }
        return x->raw_value;
    }

    extern std::shared_ptr<mandarin::support::Object> value_of_none;
    extern std::shared_ptr<mandarin::support::Object> value_of_true;
    extern std::shared_ptr<mandarin::support::Object> value_of_false;

    template <typename T>
    std::shared_ptr<Object> construct(const std::vector<std::shared_ptr<Object>>& args)
    {
        auto obj = std::make_shared<Object>();
        obj->_mndr_maybe_call_method("new", args);
        return obj;
    }
}
} // namespace mandarin

#endif // LIBRIN_CORE_HPP_INCLUDED
