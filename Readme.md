# folder_validator

Write rules and conventions for the files and folders in your system. Check your file system for consistency with just one command. Discover inconsistencies such as misspellings, incorrectly sorted or missing files and folders with just one command.

This is my first project with Python 3. As it became more and more useful, I wanted to share it on Github.

The source code is just a Python file in the `src` directory that does not use any dependencies other than Python 3 itself.

## Features

* Define rules in JSON for folders and files in `.folder_format` files.
* Rules are specific to folders or files.
* Rules can include other rules. These are evaluated recursively.
* A rule specifies the name or a regular expression.
* Rules can validate names of existing objects or specify that certain files or folders exist.
* Exceptions to the rules can be defined.
* Pretty output (example 1):

      python folder_validator.py
      Checking My Taxes ...

      1: Violation found on My Taxes
         -> Format file: examples/1_unexpected_file/taxes/.folder_format

         following items were unexpected:
          * examples/1_unexpected_file/ taxes/unexpected_file
         because they did not match any of these rules:
          -> folder: my_taxes_{number}(range 2017-2019)
          -> folder: my_taxes_2020

          following items were expected, but could not be found:
           * my_taxes_2020

  For the rule:

      {
          "description": "My Taxes",
          "items": [
                  {"type": "folder", "name":"my_taxes_{number}", "pattern": "multible", "range_min": 2017, "range_max": 2019},
                  {"type": "folder", "name":"my_taxes_2020", "required": true}
          ]
      }

# Usage

Create `.folder_format` files.
From there, the script will search all directories recursively.

Run:

      python folder_validator.py

## Examples

### Run examples

Just type:

      python folder_validator.py

### Simple example:

    {
        "description": "My Taxes",
        "items": [
                {"type": "folder", "name":"my_taxes_2020"},
                {"type": "file", "name":"overview.odt"}
        ]
    }

### Names can be regular expressions:

    {
        "description": "My Taxes",
        "items": [
                {"type": "folder", "name":"my_taxes_\\d\\d\\d\\d"},
                {"type": "file", "name":".odt"}
        ]
    }


### Require an item

* Requires that at least one item matches the rule.
* If a range-element is required, the requirement only applies to one of its variants (until now). However, required elements in a range-element apply to all occurrences of the parent range-element


    {
        "description": "My Taxes",
        "items": [
                {"type": "folder", "name":"my_taxes_2020", "required": true}
        ]
    }


### Range (does not work with `required` (yet)):

    {
        "description": "My Taxes",
        "items": [
                {
                  "type": "folder",
                  "name":"my_taxes_{number}",
                  "pattern": "multible",
                  "range_min": 2017,
                  "range_max": 2019
                },
        ]
    }


### Stacking rules (example 2):

    {
      "description": "My Taxes",
      "items": [
                    {
                            "type": "folder",
                            "name":"my_taxes_{number}",
                            "pattern": "multible",
                            "range_min": 2017,
                            "range_max": 2019,

                            "items": [
                                    {"type": "file", "name": "income tax.pdf", "required": true},
                                    {"type": "file", "name": "donations.xlsx"},
                                    {
                                            "type": "folder",
                                            "name": "other documents",

                                            "items": [
                                              { "type": "file", "name": ".pdf" }
                                            ]

                                    }

                            ]
                    }
            ]
    }

### Exclusions:

    {
        "description": "My Taxes",
        "items": [
                {
                  "type": "folder",
                  "name":"my_taxes_{number}",
                  "pattern": "multible",
                  "range_min": 2017,
                  "range_max": 2019
                },
                {
                  "type": "exclusion", "name": ".backup"
                }
        ]
    }
