# Mandarin
A programming language intended to be simple and beautiful. Please don't ask
me why I have chosen this name, I'll only say it has nothing to do with the world's
most popular human language

***In development***

## Features
**Warning: The language is in development, these are only planned features**

- Mix of dynamic and static type system
- Functions as methods (e.g. function of type T can be called as `T.func()` instead of `func(T)`)
- Compiler/transpiler, not interpreter
- Easy to debug (compared to, say, C/C++)

## Code examples
**Warning: The language is in development, the syntax and API may change**

### Hello world
```
def main()
    print('Hello world!')
end
```

OR

```
def main()
    'Hello world!'.print()
end
```

### Are two 2D vectors orthogonal?
```
class Vector2D
    def new(x, y)
        self.x = x
        self.y = y
    end

    def dot_product(Vector2D other)
        return self.x * other.x + self.y * other.y
    end

    var x, y
end

def main()
    c1 = input('Enter X and Y coords of the first vector: ').split()
    c2 = input('Enter X and Y coords of the second vector: ').split()

    v1 = Vector2D(c1[0], c1[1])
    v2 = Vector2D(c2[0], c2[1])
    if v1.dot_product(v2) == 0
        print('Vectors are orthogonal')
    else
        print('Vectrs are not orthogonal')
    end
end
```

## License
Compiler code itself (all Python files) are licensed under GNU GPLv3 (see LICENSE file
and boilerplates in source files).

Tests for compiler and mandarin code examples (including ones in README.md)
are in public domain (see tests/UNLICENSE)
