from typing import Literal, NoReturn
import asyncio


async def task1() -> Literal["result1"]:
    await asyncio.sleep(1)
    return "result1"


async def task2() -> NoReturn:
    print("Task 2 started")
    await asyncio.sleep(2)
    msg = "An error occurred in task2"
    raise ValueError(msg)


async def task3() -> Literal["result3"]:
    print("Task 3 started")
    await asyncio.sleep(3)
    return "result3"


async def main() -> None:
    tasks = []
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(task3())
            t2 = tg.create_task(task2())
            t3 = tg.create_task(task1())
            tasks.append([t1, t2, t3])
        all_results = [t.result() for t in tasks]
        print(f"All results: {all_results}")
    except* Exception as e:
        print(f"Exception: {e.exceptions}")


asyncio.run(main())
