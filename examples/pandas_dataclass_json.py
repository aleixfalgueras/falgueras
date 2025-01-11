from dataclasses import dataclass, asdict

from pandas import DataFrame, json_normalize

""" Show relation between Pandas, dataclass, and jsons """


@dataclass(frozen=True)
class Person:
    name: str
    age: int


aleix = Person("aleix", 28)

# from dataclass to Pandas DataFrame (DataFrame constructor takes a list of dictionaries)
aleix_df = DataFrame([asdict(aleix)])  # type: ignore
print(aleix_df)

# from Pandas DataFrame to dataclass (explicit)
new_aleix = Person(name=aleix_df["name"].iloc[0], age=aleix_df["age"].iloc[0])
print(new_aleix)

# from Pandas DataFrame to dataclass (dynamic)
new_aleix_dynamic = Person(**aleix_df.iloc[0].to_dict())
print(new_aleix_dynamic)

print("###############################################")

# json_normalize example
jsons_with_deep = [{"name": "pepito",
                    "detail": {"age": 28, "high": 1.9}},
                   {"name": "jose",
                    "detail": {"age": 46, "high": 1.6}}]

persons_json_deep_df = DataFrame(jsons_with_deep)
print(persons_json_deep_df)

persons_json_deep_normalize_df = json_normalize(jsons_with_deep)
print(persons_json_deep_normalize_df)
