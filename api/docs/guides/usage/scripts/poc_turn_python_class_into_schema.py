import copy
import json
import os
import re

# # Getting the current work directory (cwd)
this_dir = os.getcwd()
# # Add the folder you want to run through
SUB_DIRECTORY_TO_CHECK = "/api"

LIST_OF_DIRS = []
# r=root, d=directories, f = files
for r, d, f in os.walk(this_dir + SUB_DIRECTORY_TO_CHECK):
    for file in f:
        if file.endswith(".py"):
            LIST_OF_DIRS.append(os.path.join(r, file))

COLUMN_REGEX = r"[\s\w\d_-]{1,100}[:][ ][\w][\w\]\[= )(\"\']*"


DOMAIN = this_dir.split("/")[-1]
SENSITIVITY = "PUBLIC"

TAGS = {"generated": "True"}

OWNERS = [{"name": "test-user", "email": "test-user@test.com"}]

BASE_SCHEMA = {
    "metadata": {
        "domain": DOMAIN,
        "dataset": "",
        "sensitivity": SENSITIVITY,
        "tags": TAGS,
        "owners": OWNERS,
    },
    "columns": [],
}

BASE_COLUMN = {
    "name": "",
    "partition_index": "null",
    "data_type": "string",
    "allow_null": "true",
    "format": "null",
}


def get_file_lines(file_path: str):
    file = open(file_path)
    # store all the lines in the file as a list
    lines = file.readlines()
    file.close()
    return lines


def get_columns_with_data_types(classes_columns: dict, line: str, line_number: int):
    column = line.replace(" ", "").replace("\n", "")
    values_col = column.split(":")
    classes_columns[line_number] = {"col_name": values_col[0], "type": values_col[1]}


def get_classes(classes_columns: dict, line: str, line_number: int):
    new_class = line.strip("class ").strip(" ").split("(")[0]
    classes_columns[line_number] = {"class_name": new_class}


def create_base_object(file_path: str):
    lines = get_file_lines(file_path)
    classes_columns = {}
    for line in lines:
        if "class " in line:
            get_classes(classes_columns, line, lines.index(line))
        elif re.match(COLUMN_REGEX, line):
            get_columns_with_data_types(classes_columns, line, lines.index(line))
    return classes_columns


def generate_column(raw_column: dict):
    schema_column = BASE_COLUMN.copy()
    schema_column["name"] = raw_column["col_name"]
    return schema_column


def generate_columns(generated_schema: dict, base_object: dict, base_index: int):
    for second_index in base_object:
        if second_index <= base_index:
            continue
        if "class_name" in base_object[second_index]:
            break
        else:
            generated_schema["columns"].append(
                generate_column(base_object[second_index])
            )


def generate_schema(raw_object: dict):
    new_schema = copy.deepcopy(BASE_SCHEMA)
    new_schema["metadata"]["dataset"] = raw_object["class_name"]
    return new_schema


def generate_schemas(file_path: str):
    base_object = create_base_object(file_path)
    list_of_schemas = []
    for base_index in base_object:
        if "class_name" in base_object[base_index]:
            generated_schema = generate_schema(base_object[base_index])
            generate_columns(generated_schema, base_object, base_index)
            list_of_schemas.append(generated_schema.copy())
    return list_of_schemas


def write_schemas(file_path: str):
    schemas = generate_schemas(file_path)
    for schema in schemas:
        metadata = schema["metadata"]
        with open(f"{DOMAIN}_{metadata['dataset']}.json", "w") as schema_file:
            schema_file.write(json.dumps(schema))


for directory in LIST_OF_DIRS:
    write_schemas(directory)
