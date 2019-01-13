#   AUTHOR: Sibyl System
#     DATE: 2018-04-19
#     DESC: 线程池，用于执行计算密集型任务

import queue
import threading


class Task(threading.Thread):

    """ 任务  """

    def __init__(self, num, input_queue, output_queue, error_queue):
        super(Task, self).__init__()
        self.thread_name = "thread-%s" % num
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.error_queue = error_queue
        self.deamon = True

    def run(self):
        """run
        """
        while 1:
            try:
                func, args = self.input_queue.get(block=False)
            except queue.Empty:
                print("%s finished!" % self.thread_name)
                break
            try:
                result = func(*args)
            except Exception as exc:
                self.error_queue.put((args, str(exc)))
            else:
                self.output_queue.put(result)


class Pool(object):

    """ 线程池 """

    def __init__(self, size):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.tasks = [
            Task(i, self.input_queue, self.output_queue,
                 self.error_queue) for i in range(size)
        ]

    def add_task(self, func, args):
        """添加单个任务
        """
        if not isinstance(args, tuple):
            raise TypeError("args must be tuple type!")
        self.input_queue.put((func, args))

    def add_tasks(self, tasks):
        """批量添加任务
        """
        if not isinstance(tasks, list):
            raise TypeError("tasks must be list type!")
        for func, args in tasks:
            self.add_task(func, args)

    def get_results(self):
        """获取执行结果集
        """
        while not self.output_queue.empty():
            yield self.output_queue.get()

    def get_errors(self):
        """获取执行失败的结果集
        """
        while not self.error_queue.empty():
            func, args, error_info = self.error_queue.get()
            print("Error: func: %s, args : %s, error_info : %s" \
                % (func.func_name, args, error_info))

    def run(self):
        """执行
        """
        for task in self.tasks:
            task.start()
        for task in self.tasks:
            task.join()


def test(i, global_list):
    """test """
    result = i
    print(i)
    global_list[i] = i
    return result


def main():
    """ main """
    global_list = [0, 0, 0, 0, 0]
    pool = Pool(size=5)
    pool.add_tasks([(test, (i, global_list)) for i in range(5)])
    pool.run()
    print(global_list)


if __name__ == "__main__":
    main()