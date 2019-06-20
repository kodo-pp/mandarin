#ifndef MANDARIN_HPP_INCLUDED
#define MANDARIN_HPP_INCLUDED

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>


namespace mandarin
{

namespace support
{
    class GenericObject;
    class Object : public GenericObject;

    class GenericObject
    {
    public:
        GenericObject();
        GenericObject(const GenericObject& other) = delete;
        GenericObject(GenericObject&& other) = default;
        virtual ~GenericObject();

        GenericObject& operator=(const GenericObject& other) = delete;
        GenericObject& operator=(GenericObject&& other) = default;

        virtual std::shared_ptr<Object> mndr___new__();
        virtual std::shared_ptr<Object> mndr___del__();

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

        virtual std::shared_ptr<Object> mndr___unary_plus__();
        virtual std::shared_ptr<Object> mndr___unary_minus__();
        virtual std::shared_ptr<Object> mndr___unary_negate__();
        virtual std::shared_ptr<Object> mndr___unary_compl__();

        virtual std::shared_ptr<Object> mndr___multiply__       (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___divide__         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___modulo__         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___int_divide__     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___add__            (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___sub__            (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___incrange__       (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___range__          (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___equals__         (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___less_equals__    (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___greater_equals__ (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___not_equals__     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___less__           (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___greater__        (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___logical_and__    (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___logical_or__     (const std::shared_ptr<Object>& rhs);
        virtual std::shared_ptr<Object> mndr___logical_xor__    (const std::shared_ptr<Object>& rhs);

        virtual std::shared_ptr<Object> mndr___iterator__();
        virtual std::shared_ptr<Object> mndr___next__();
        virtual std::shared_ptr<Object> mndr___inplace_next__();
        virtual std::shared_ptr<Object> mndr___is_iteration_finished__();
        virtual std::shared_ptr<Object> mndr___element__();

        virtual std::shared_ptr<Object> _mndr_type_object();
    };


    class Function : public GenericObject
    {
    public:
        // Stopped here
    }


    class Object : public GenericObject
    {
    public:
        Object();

    private:
        std::unordered_map<std::string, Function> methods;
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
        using remove_pointer_t = remove_pointer<T>::type;


        template <typename T>
        struct make_pointer
        {
            using type = std::shared_ptr<T>;
        };

        template <typename T>
        struct make_pointer<std::shared_ptr<T>>
        {
            using type = std::shared_ptr;
        };

        template <typename T>
        using make_pointer_t = make_pointer<T>::type;
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
        bool convertible = x->_mndr_is_instance(To::_mndr_static_type_object());
        if (!convertible) {
            // TODO: raise (mandarin) exception
            std::cerr << "Fatal mandarin error: invalid dynamic_cast_to" << std::endl;
            abort();
        }
    }
} // namespace support


namespace user
{
    class mndr_NoneType : public mandarin::support::Object
    {};

    class mndr_Bool : public mandarin::support::Object
    {
    public:
        std::shared_ptr<mandarin::support::Object> _mndr_unary_negate() override;
    private:
        bool raw_value;
    };

    class mndr_Int : public mandarin::support::Object
    {
    private:
        int 
    };
} // namespace user


namespace support
{
    template <typename T>
    bool native_bool(const std::shared_ptr<T>& x)
    {
        if (!x->_mndr_is_instance(mandarin::user::mndr_Bool::_mndr_static_type_object())) {
            // TODO(?): raise (mandarin) exception
            std::cerr << "Fatal mandarin error: invalid native_bool" << std::endl;
            abort();
        }
    }
}
} // namespace mandarin

#endif // MANDARIN_HPP_INCLUDED
