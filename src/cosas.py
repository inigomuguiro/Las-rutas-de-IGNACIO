# turn to dict the Coordenadas json
    for f in final:
        f["Coordenadas"] = json.loads(f["Coordenadas"].replace("'", '"')).get("coordinates")