input_file = "2023.csv"
output_file = "filtered.csv"

with open(input_file, "r") as f:
    lines = f.readlines()

result = lines[1::4]

with open(output_file, "w") as f:
    f.writelines(result)

print("Fichier filtré créé :", output_file)