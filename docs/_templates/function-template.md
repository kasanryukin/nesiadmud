---
layout: function
title: "Function Name"
function_name: "function_name"
module: "module_name"
function_type: "efun|eobj|sefun"
parameters: ["param1", "param2"]
returns: "return_type"
nav_order: 1
parent: "Module Name"
---

Brief description of what this function does.

## Detailed Description

More detailed explanation of the function's purpose, behavior, and usage patterns.

### Parameters Detail
```yaml
parameters_detail:
  - name: "param1"
    type: "string"
    optional: false
    description: "Description of the first parameter"
  - name: "param2"
    type: "int"
    optional: true
    description: "Description of the second parameter"
```

### Returns Detail
```yaml
returns_detail: "Detailed description of what the function returns"
```

### Examples
```yaml
examples:
  - title: "Basic Usage"
    description: "Simple example showing basic usage"
    code: |
      result = function_name("example", 42)
      print(result)
  - title: "Advanced Usage"
    description: "More complex example"
    code: |
      # More complex example here
      for item in items:
          result = function_name(item.name, item.value)
          if result:
              print(f"Success: {result}")
```

### See Also
```yaml
see_also:
  - title: "Related Function"
    url: "/reference/modules/related-function/"
  - title: "Core Concept"
    url: "/core-concepts/related-concept/"
```

### Notes
```yaml
notes: |
  Any additional notes, warnings, or important information about this function.
  
  - Performance considerations
  - Security implications
  - Version compatibility
```