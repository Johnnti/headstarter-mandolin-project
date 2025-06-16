import os
import read_pa

#adbulla
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_dir, "Input Data", "Adbulla", "PA.pdf")

text = read_pa.read_pa(file_path=file_path)
print(text)
