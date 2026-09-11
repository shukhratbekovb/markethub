from random import randint

from slugify import slugify

first_name = "Владислав"
last_name = "Tyo"

username = slugify(f"{first_name} {last_name}", separator="_")
print(username)

variants = [
    slugify(f"{last_name}", separator="_"),
    slugify(f"{first_name[0]} {last_name}", separator="_"),
    slugify(f"{first_name[0]} {last_name}{randint(1, 512)}", separator="_"),
    slugify(f"{first_name} {last_name}", separator="_"),
]
print(variants)