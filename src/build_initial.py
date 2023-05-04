import re

import yaml

# from copy import deepcopy

ids_filter = r'[-#\(\)\*\,\.\:\;\?\[\]\{\}\^_>0123456789abBcdDfghHijJKlMnNpPqQrsStTuUvVwWxyzZ]'
cog_filter = r'[\(\)\*？\{\}⇄↻☷⿰⿱⿳⿸0234ABcCgHNoXZ]'
shape_filter = r'[-#\(\)\*\,\.\:\;\?\[\]\^_\{\}>↔↷⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻012〢3〣456789abBcdDfghHijJKlMnNpPqQrsStTuUvVwWxyzZ]'


def _load(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def _dump(path: str, obj):
    with open(path, 'w', encoding="utf-8") as f:
        yaml.dump(obj, f, indent=4, allow_unicode=True)


def _sort(src: str) -> str:
    lst = list(set(list(src)))
    lst.sort()
    return "".join(lst)


def _sub(src: str, amb_dict: dict[str, str]) -> str:
    lst = list(re.sub(shape_filter, "", src))
    new_lst = []

    for char in lst:
        for key, val in amb_dict.items():
            char = re.sub(f"{key}", val, char)
        new_lst.append(char)

    return "".join(new_lst)


def _get_uni(src: str, uni_dict: dict[str, str]) -> str:
    for key, val in uni_dict.items():
        if src in key:
            return key + ": " + val
    return ""


def build_ids_dict() -> dict[str, list[str]]:
    ids_path = "data/ids_lv2.txt"
    ids_dict: dict[str, list[str]] = {}
    with open(ids_path, 'r', encoding='utf-8') as f_ids:
        line = f_ids.readline().strip()
        while line:
            char, idses = line.split('\t')[0], line.split('\t')[1:]
            list_single_ids = []
            for idses in idses:
                list_single_ids += idses.split(";")
            ids_dict[char] = [re.sub(ids_filter, "", i) for i in list_single_ids]
            line = f_ids.readline().strip()

    # dump yaml
    _dump("res_initial/built_ids.yaml", ids_dict)
    return ids_dict


def build_cognition_dict() -> dict[str, list[str]]:
    cog_path = "data/ies20220126.txt"
    cog_dict: dict[str, list[str]] = {}
    with open(cog_path, 'r', encoding="utf-8") as f_cog:
        line = f_cog.readline().strip()
        while line:
            str_character, str_cognition = line.split('\t')
            str_cognition = re.sub(cog_filter, "", str_cognition)
            if str_character in cog_dict.keys():
                cog_dict[str_character].append(str_cognition)
            else:
                cog_dict[str_character] = [str_cognition]
            line = f_cog.readline().strip()

    # dump yaml
    _dump("res_initial/built_cognition.yaml", cog_dict)
    return cog_dict


def build_reference_ass(ids_dict: dict[str, list[str]], cog_dict: dict[str, list[str]], uni_dict: dict[str, str], char_range: range):
    amb_dict = _load("data/ambiguous.yaml")

    # build initial ass dict
    original_ass_dict = {}
    for codepoint in char_range:
        char = chr(codepoint)
        if char not in ids_dict.keys():
            ids_dict[char] = [char]
        if char not in cog_dict.keys():
            cog_dict[char] = []

        for ids in ids_dict[char]:
            for cognition in cog_dict[char]:
                if (set(_sub(ids, amb_dict)).issubset(set(_sort(cognition))) or set(_sub(ids, amb_dict)) == set(char)) and re.sub(ids_filter, "", ids) != "":
                    original_ass_dict[char] = re.sub(ids_filter, "", ids)

    # # build recursive ass dict
    # while True:
    #     temp_ass_dict = deepcopy(original_ass_dict)
    #     for key, val in original_ass_dict.items():
    #         if val[0] == "=":
    #             original_ass_dict[key] = val
    #         else:
    #             new_val = []
    #             for index in range(len(val)):
    #                 if val[index] == "=":
    #                     continue
    #                 if val[index] in original_ass_dict.keys():
    #                     new_val += original_ass_dict[val[index]]
    #                 else:
    #                     new_val.append(val[index])
    #                 original_ass_dict[key] = new_val
    #     if temp_ass_dict == original_ass_dict:
    #         break

    for codepoint in char_range:
        if chr(codepoint) not in original_ass_dict.keys():
            original_ass_dict[chr(codepoint)] = [chr(codepoint)]

    _dump("res_initial/reference_ass.yaml", original_ass_dict)

    temp_path = "res_initial/reference.txt"
    with open(temp_path, "w", encoding="utf-8") as f_out:
        for codepoint in char_range:
            f_out.write(chr(codepoint) + "\t" + str(ids_dict[chr(codepoint)]) + "\t" + str(cog_dict[chr(codepoint)]) + "\t" + _get_uni(chr(codepoint), uni_dict) + "\t" + "".join(original_ass_dict[chr(codepoint)]) + "\n")
    return original_ass_dict


def main():
    ids_dict = build_ids_dict()
    # ids_dict = _load("res_initial/built_ids.yaml")
    cog_dict = build_cognition_dict()
    # cog_dict = _load("res_initial/built_cognition.yaml")
    uni_dict = _load("data/unification.yaml")
    ass_reference = build_reference_ass(ids_dict, cog_dict, uni_dict, range(0x20000, 0x2a000))


if __name__ == '__main__':
    main()
