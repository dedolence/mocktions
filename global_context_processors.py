def global_variables(request):
    # access any variable from globals.py in templates as {{ VARIABLE_NAME }}
    global_dict = {}
    with open('globals.py', 'r') as global_file:
        for line in global_file:
            k, v = line.split(' = ')
            global_dict[k] = v
    return global_dict     