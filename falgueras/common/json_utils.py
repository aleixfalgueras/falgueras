import json



def save_local_json(data: dict, output_filename: str = "response"):
    output_filename = output_filename if output_filename.endswith(".json") else f"{output_filename}.json"

    with open(output_filename, "w") as json_file:
        json.dump(data, json_file, indent=4)  # type: ignore


def load_local_json(filename: str) -> dict:
    filename = filename if filename.endswith(".json") else f"{filename}.json"

    try:
        with open(filename, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filename} does not exist.")
    except json.JSONDecodeError:
        raise ValueError(f"The file {filename} is not a valid JSON file.")