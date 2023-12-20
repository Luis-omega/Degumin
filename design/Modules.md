# Modules


We want to include the concept of package in the compiler, our 
way of doing it is by adding packages to the import/export system.


## Imports
We would borrow part of python import syntax and part of Haskell.

We also follow the Haskell approach of require to have the imports
at the top of the file (expect for comments and module statement)

```haskell
from packageName import Module.Directory.In.The.Package(
    Especific(Things)
    ) as QualifiedName hiding (something)
```

The list of imports can't be empty.

To refer to functions in the current package we can do like:

```haskell
from . import Module.Directory ...
```

or just 


```haskell
import Module.Directory ...
```

To import a module unqualified we can: 

```haskell
from package import unqualified Module.Name(Especific thing)
```
But we still mandate for the list of imports to be non empty. 

If even with this you want to import everything  you should use 
```haskell
from package importAllOf Module.Name as qualifiedName
```

We may (I still thinking on it), support a unqualified import of everything as:
```haskell
from package import unqualified all of Module.Name as qualifiedName
```

### Why make a unqualified import of everything this hard?

We want to discourage those kind of imports.

I frequently do code reviews on an online platform without access to a lsp or 
a way to search code except from those provided by the platform, in those cases
is very useful to have all the import explicit.

To alleviate this burden our aim is to provide a `LSP` with a good support for 
auto import at completion. This way people won't need to bother much 
with importing everything.


## Exports

For now I think that every type/term can be on one of  three categories 

- private, it won't scape the module in which is defined.
- package level, every module in the current package can see it
    including the test section, but no user of the package 
    can refer to it outside.
- public, all modules importing from the package can see them.

In the package and public level we still follows the privacy rules of
Haskell for types and functions. 

I'm still unsure about the syntax for them, we can follow Haskell
here with a top level declaration of exports, or we can follow 
Idris2 and use `public` and other keywords at the point we define things.
