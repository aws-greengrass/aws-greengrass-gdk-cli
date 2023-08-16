# LIBRARY ERROR MESSAGES
JSON_LIBRARY_ERROR_MESSAGES = {
    "Expecting ',' delimiter": [
        "lack of a comma at the end of the line",
        "lack of a comma at the end of the above line",
        "unmatched brackets or quotes"
    ],
    "Expecting ':' delimiter": [
        "a missing colon between the key and the value"
    ],
    "Expecting property name enclosed in double quotes": [
        "the key is not enclosed in double quotes",
        "missing opening or closing quotes for key or value",
        "unexpected characters or tokens present",
        "trailing comma after the last key-value pair"
    ],
    "Expecting value": [
        "missing value for the key",
        "unexpected characters or tokens between the key and value",
        "unmatched quotes for value"
    ],
    "Invalid control character at": [
        "unmatched quotes in the JSON data",
        "improperly escaped characters"
    ],
    "Extra data": [
        "multiple JSON objects present",
        "extra brackets present"
    ]
}

YAML_LIBRARY_ERROR_MESSAGES = {
    "mapping values are not allowed here": [
        "missing colon in the line above",
        "missing mandatory space after the colon in the line above"
    ],
    "expected <block end>, but found": [
        "unexpected characters or tokens at the end of the line",
        "incorrect indentation",
        "missing closing quotes on the line above",
        "unmatched opening and closing quotes",
        "missing mandatory space after the character '-' in the line above"
    ],
    "could not find expected ':'": [
        "unexpected characters or tokens between the key and value",
        "missing mandatory space after the colon in the line above"
    ],
    "found unexpected end of stream": [
        "unmatched opening and closing quotes"
    ],
    "expected '<document start>', but found": [
        "unexpected characters or tokens at the start of the document"
    ],
    "expected alphabetic or numeric character": [
        "unexpected characters or tokens at the start of a string"
    ],
    "found undefined alias": [
        "missing definition of the alias",
        "misusing characters '*', or '&'"
    ],
    "expected chomping or indentation indicators, but found": [
        "unexpected characters or tokens present"
    ],
    "expected the node content, but found": [
        "unexpected characters or tokens present"
    ],
    "found character '@' that cannot start any token": [
        "having a token that starts with the character '@'"
    ]
}

# Json Schema Keywords for Structural Validation:
# https://json-schema.org/draft/2020-12/json-schema-validation.html#name-a-vocabulary-for-structural
JSON_SCHEMA_VALIDATION_KEYWORDS = {
    "type": {
        "description": "Validates instance type",
        "causes": [
            "Instance type does not match the specified type."
        ],
        "fixes": [
            "Please check the instance type and ensure it matches the expected type."
        ]
    },
    "enum": {
        "description": "Validates against a set of allowed values",
        "causes": [
            "Instance value is not one of the allowed enum values."
        ],
        "fixes": [
            "Please make sure the instance value is one of the allowed enum values."
        ]
    },
    "const": {
        "description": "Validates against a constant value",
        "causes": [
            "Instance value is not equal to the specified constant."
        ],
        "fixes": [
            "Please ensure the instance value matches the specified constant."
        ]
    },
    "multipleOf": {
        "description": "Validates numeric instances for divisibility",
        "causes": [
            "Numeric instance is not divisible by the specified value."
        ],
        "fixes": [
            "Please check if the numeric instance is divisible by the specified value."
        ]
    },
    "maximum": {
        "description": "Validates numeric instances against an upper limit",
        "causes": [
            "Numeric instance is greater than the allowed maximum value."
        ],
        "fixes": [
            "Please ensure the numeric instance is less than or equal to the allowed maximum value."
        ]
    },
    "exclusiveMaximum": {
        "description": "Validates numeric instances against an exclusive upper limit",
        "causes": [
            "Numeric instance is greater than or equal to the allowed exclusive maximum value."
        ],
        "fixes": [
            "Please ensure the numeric instance is strictly less than the allowed exclusive maximum value."
        ]
    },
    "minimum": {
        "description": "Validates numeric instances against a lower limit",
        "causes": [
            "Numeric instance is less than the allowed minimum value."
        ],
        "fixes": [
            "Please ensure the numeric instance is greater than or equal to the allowed minimum value."
        ]
    },
    "exclusiveMinimum": {
        "description": "Validates numeric instances against an exclusive lower limit",
        "causes": [
            "Numeric instance is less than or equal to the allowed exclusive minimum value."
        ],
        "fixes": [
            "Please ensure the numeric instance is strictly greater than the allowed exclusive minimum value."
        ]
    },
    "maxLength": {
        "description": "Validates string instances against a maximum length",
        "causes": [
            "String instance length is greater than the allowed maximum length."
        ],
        "fixes": [
            "Please ensure the string instance length is less than or equal to the allowed maximum length."
        ]
    },
    "minLength": {
        "description": "Validates string instances against a minimum length",
        "causes": [
            "String instance length is less than the allowed minimum length."
        ],
        "fixes": [
            "Please ensure the string instance length is greater than or equal to the allowed minimum length."
        ]
    },
    "pattern": {
        "description": "Validates string instances against a regular expression pattern",
        "causes": [
            "String instance does not match the specified pattern."
        ],
        "fixes": [
            "Please check if the string instance matches the specified regular expression pattern."
        ]
    },
    "maxItems": {
        "description": "Validates array instances against a maximum number of items",
        "causes": [
            "Array instance size is greater than the allowed maximum number of items."
        ],
        "fixes": [
            "Please ensure the array instance size is less than or equal to the allowed maximum number of items."
        ]
    },
    "minItems": {
        "description": "Validates array instances against a minimum number of items",
        "causes": [
            "Array instance size is less than the allowed minimum number of items."
        ],
        "fixes": [
            "Please ensure the array instance size is greater than or equal to the allowed minimum number of items."
        ]
    },
    "uniqueItems": {
        "description": "Validates array instances for unique items",
        "causes": [
            "Array instance contains duplicate items."
        ],
        "fixes": [
            "Please ensure all elements in the array instance are unique."
        ]
    },
    "maxContains": {
        "description": "Validates array instances based on the maximum number of contained items",
        "causes": [
            "Array instance contains more items than the maximum allowed."
        ],
        "fixes": [
            "Please ensure the number of contained items in the array instance is less than or equal to the maximum "
            "allowed."
        ]
    },
    "minContains": {
        "description": "Validates array instances based on the minimum number of contained items",
        "causes": [
            "Array instance contains fewer items than the minimum required."
        ],
        "fixes": [
            "Please ensure the number of contained items in the array instance is greater than or equal to the "
            "minimum required."
        ]
    },
    "maxProperties": {
        "description": "Validates object instances against a maximum number of properties",
        "causes": [
            "Object instance has more properties than the maximum allowed."
        ],
        "fixes": [
            "Please ensure the number of properties in the object instance is less than or equal to the maximum "
            "allowed."
        ]
    },
    "minProperties": {
        "description": "Validates object instances against a minimum number of properties",
        "causes": [
            "Object instance has fewer properties than the minimum required."
        ],
        "fixes": [
            "Please ensure the number of properties in the object instance is greater than or equal to the minimum "
            "required."
        ]
    },
    "required": {
        "description": "Validates object instances for required properties",
        "causes": [
            "Object instance is missing one or more required properties.",
            "A required property might be misspelled."
        ],
        "fixes": [
            "Please ensure all required properties are present in the object instance.",
            "And double-check that the required property names are spelled correctly."
        ]
    },
    "dependentRequired": {
        "description": "Validates dependent required properties in object instances",
        "causes": [
            "Dependent property is missing when its requirement is dependent on another property."
        ],
        "fixes": [
            "Please ensure the dependent properties are present based on the presence of other properties."
        ]
    },
    "allOf": {
        "description": "Validates if instance satisfies all of the options",
        "causes": [
            "Instance does not satisfy all of the options."
        ],
        "fixes": [
            "Please ensure the instance satisfies all of the options."
        ]
    },
    "anyOf": {
        "description": "Validates if instance satisfies at least one of the options",
        "causes": [
            "Instance does not satisfy any of the options."
        ],
        "fixes": [
            "Please ensure the instance satisfies at least one of the options."
        ]
    },
    "oneOf": {
        "description": "Validates if instance satisfies exactly one of the options",
        "causes": [
            "Instance does not satisfy exactly one of the options."
        ],
        "fixes": [
            "Please ensure the instance satisfies exactly one of the options."
        ]
    },
    "not": {
        "description": "Validates if instance does not satisfy the options",
        "causes": [
            "Instance satisfies the options when it shouldn't."
        ],
        "fixes": [
            "Please ensure the instance does not satisfy the options."
        ]
    },
    "if": {
        "description": "Conditional validation based on another property",
        "causes": [
            "The 'if' condition is not met."
        ],
        "fixes": [
            "Please ensure the condition specified in 'if' is met."
        ]
    },
    "then": {
        "description": "Validation to apply if 'if' condition is met",
        "causes": [
            "The 'then' validation is not met."
        ],
        "fixes": [
            "Please ensure the 'then' validation is met when the 'if' condition is met."
        ]
    },
    "else": {
        "description": "Validation to apply if 'if' condition is not met",
        "causes": [
            "The 'else' validation is not met."
        ],
        "fixes": [
            "Please ensure the 'else' validation is met when the 'if' condition is not met."
        ]
    },
    "items": {
        "description": "Validates items in an array",
        "causes": [
            "Items in the array do not satisfy the validation."
        ],
        "fixes": [
            "Please ensure all items in the array satisfy the validation."
        ]
    },
    "additionalItems": {
        "description": "Validates additional items in an array",
        "causes": [
            "Additional items in the array do not satisfy the validation."
        ],
        "fixes": [
            "Please ensure additional items in the array satisfy the validation."
        ]
    },
    "contains": {
        "description": "Validates if array contains at least one valid item",
        "causes": [
            "Array does not contain a valid item."
        ],
        "fixes": [
            "Please ensure the array contains at least one valid item."
        ]
    },
    "propertyNames": {
        "description": "Validates property names in an object",
        "causes": [
            "Property names in the object do not satisfy the validation."
        ],
        "fixes": [
            "Please ensure all property names in the object satisfy the validation."
        ]
    },
    "properties": {
        "description": "Validates specific properties in an object",
        "causes": [
            "Properties in the object do not satisfy the validation."
        ],
        "fixes": [
            "Please ensure all specified properties in the object satisfy the validation."
        ]
    },
    "patternProperties": {
        "description": "Validates properties based on a regular expression pattern",
        "causes": [
            "Properties in the object do not match the specified pattern."
        ],
        "fixes": [
            "Please ensure all properties in the object match the specified pattern."
        ]
    },
    "additionalProperties": {
        "description": "Validates object instances for disallowed additional properties",
        "causes": [
            "Object instance contains additional properties when they are not allowed.",
            "An allowed property might be misspelled."
        ],
        "fixes": [
            "Please ensure that no additional properties are present in the object instance when they are not allowed.",
            "Double-check that the spelling of allowed property names is correct."
        ]
    }
}
