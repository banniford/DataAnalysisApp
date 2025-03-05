import pandas as pd

# 原始时间列
time_data = [
    '2024/9/18 15:29:57.0', '2024/9/18 15:29:57.2', '2024/9/18 15:29:57.4',
    '2024/9/18 15:29:57.6', '2024/9/18 15:29:57.8', '2024/9/18 15:29:58.0',
    '2024/9/18 15:29:58.2', '2024/9/18 15:29:58.4', '2024/9/18 15:29:58.6',
    '2024/9/18 15:29:58.8', '2024/9/18 15:29:59.0', '2024/9/18 15:29:59.2',
    '2024/9/18 15:294', '2024/9/18 15:29:59.6', '2024/9/18 15:29:59.8',
    '2024/9/18 15:30:00.0', '2024/9/18 15:30:00.2', '2024/9/18 15:30:00.4',
    '2024/9/18 15:30:00.7', '2024/9/18 15:30:00.8', '2024/9/18 15:30:01.0'
]

# 创建 DataFrame
df = pd.DataFrame({'Time [s]': time_data})

# 将时间列转换为 datetime 格式
df['Time [s]'] = pd.to_datetime(df['Time [s]'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')

# 检查是否有无法解析的时间格式
invalid_times = df[df['Time [s]'].isna()]
if not invalid_times.empty:
    print("以下时间格式不正确：")
    print(invalid_times)

# 计算时间差
df['Time Difference'] = df['Time [s]'].diff().dt.total_seconds()

# 检查时间差是否一致
expected_diff = df['Time Difference'].mode()[0]  # 获取最常见的时间差作为预期值
print(f"预期的时间差为: {expected_diff} 秒")

# 找出不符合预期时间差的时间点
non_uniform_times = df[df['Time Difference'] != expected_diff]
if not non_uniform_times.empty:
    print("以下时间点不符合等差项：")
    print(non_uniform_times)
else:
    print("所有时间点都符合等差项。")