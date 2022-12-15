import yaml

DATA_FOR_YAML = {
    'list_params': ['param_01', 'param_02'],
    'int_params': 1,
    'dict_params': {
        '\u060B': 2,
        '\u20AB': 3
    }
}

with open("file.yaml", "w") as f_o:
    yaml.dump(DATA_FOR_YAML, f_o, default_flow_style=False, allow_unicode=True)
with open("file.yaml") as f_o:
    few_data = yaml.load(f_o, Loader=yaml.SafeLoader)
    if DATA_FOR_YAML == few_data:
        print('OK')
