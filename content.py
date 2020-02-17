
def preprocess(lines, flags):
    output = []
    skip_level = 0
    for line in lines:
        line = line.split("//")[0].strip() # Remove comment
        if line == "":
            continue
        if line[0] == "#":
            if line.startswith("#ifdef"):
                cond = line[7:].strip()
                if skip_level > 0 or cond not in flags:
                    skip_level += 1
            elif line.startswith("#else"):
                if skip_level == 0:
                    skip_level = 1
                elif skip_level == 1:
                    skip_level = 0
            elif line.startswith("#endif"):
                if skip_level > 0:
                    skip_level -= 1
            continue
        if skip_level == 0:
            output.append(line)
    return output

def get_id(name_id_mapping, name):
    try:
        # if the name of the node is known then return the location with the name_id_mapping list
        return name_id_mapping.index(name)
    except:
        # else add the name of the node to the list then return the location
        name_id_mapping.append(name)
        return len(name_id_mapping)-1

def read_content(flags):
    with open("map_content.txt", "r") as f:
        lines = f.readlines()

    lines = preprocess(lines, flags)
    # if you map to air, then unknown blocks will be ignored
    name_id_mapping = ["air"]
    # name_id_mapping = ["mcblock:unknown"]
    bd = {}         # bd is block data, and keeps a list of the node names in the block
    # iterate through all the lines in the map_content.txt file
    for line in lines:
        s = line.split("\t")
        if len(s) >= 2:
            r = s[1].split(" ")
            if len(r) == 0:
                print(line)
                raise ValueError("Malformed data")
            name = r[0]
            param2 = 0
            for i in range(1, len(r)):
                if r[i] != "":
                    param2 = int(r[i])
                    break
            t = s[0].split(" ")
            if len(t) == 2:
                for data in t[1].split(","):
                    try:
                        key = (int(t[0]), int(data))
                        if key not in bd:
                            bd[key] = (get_id(name_id_mapping, name),
                                       param2)
                    except ValueError as e:
                        # invalid literal for int() with base 10: ''
                        raise ValueError("map_content syntax error:"
                              " a space should"
                              " only be after '{}' if an int comes"
                              " next.".format(s[0]))
                        # raise e
            elif len(t) == 1:
                for data in range(16):
                    key = (int(t[0]), data)
                    if key not in bd:
                        bd[key] = (get_id(name_id_mapping, name), param2)

    #blocks_len = max([i[0] for i in bd.keys()])+1
    blocks_len = 4096
    blocks = [[(0, 0)]*16 for i in range(blocks_len)]
    for (id, data), value in bd.items():
        blocks[id][data] = value
    return name_id_mapping, blocks
