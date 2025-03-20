import pandas as pd
import numpy as np
import os

# 生成CSV文件的目录
output_dir = "generated_csv_files"
os.makedirs(output_dir, exist_ok=True)

# 生成表头
column_headers = [f"Column_{i+1}" for i in range(20)]

# 生成随机数据
num_rows = 100  # 每个CSV文件的行数
num_columns = 20  # 每个CSV文件的列数

for i in range(1, 6):
    data = np.random.uniform(1, 100, (num_rows, num_columns))  # 生成 1-100 之间的随机浮点数
    df = pd.DataFrame(data, columns=column_headers)
    
    # 保存为CSV文件
    file_path = os.path.join(output_dir, f"file_{i}.csv")
    df.to_csv(file_path, index=False)

print(f"已成功生成 5 个 CSV 文件，存储在 {output_dir} 目录下。")
