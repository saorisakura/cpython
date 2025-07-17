import asyncio
import time

# 模拟一个耗时的 IO 操作
async def fetch_data(url):
    print(f"开始请求 {url}")
    # 使用 asyncio.sleep 模拟网络请求延迟
    await asyncio.sleep(2)  # 等待 2 秒
    print(f"{url} 数据已获取")
    return {"url": url, "data": "示例数据"}

# 模拟一个 CPU 密集型操作
async def process_data(task_id, data):
    print(f"开始处理任务 {task_id}")
    # 模拟一些处理工作
    await asyncio.sleep(1)  # 等待 1 秒
    print(f"任务 {task_id} 处理完成")
    return len(data["data"])

async def main():
    start_time = time.time()
    
    # 创建多个异步任务
    urls = ["https://api.example.com/data/1", "https://api.example.com/data/2", "https://api.example.com/data/3"]
    fetch_tasks = [fetch_data(url) for url in urls]
    
    # 并发执行所有获取数据的任务
    results = await asyncio.gather(*fetch_tasks)
    
    # 创建处理数据的任务
    process_tasks = [process_data(i, result) for i, result in enumerate(results)]
    
    # 并发执行所有处理数据的任务
    processed_results = await asyncio.gather(*process_tasks)
    
    print(f"所有任务处理完成，结果: {processed_results}")
    print(f"总耗时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())    
