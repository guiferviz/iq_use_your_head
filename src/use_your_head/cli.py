from use_your_head.dancing_links import Problem, DancingLinks
import time


class CLI:
    def __init__(self):
        pass

    def one_solution(self, problem_path: str):
        problem = Problem.from_yaml(problem_path)
        dlx = DancingLinks(problem.constraints, problem.candidates)
        for i in dlx.solutions():
            print(i)
            break

    def all_solutions(self, problem_path: str):
        problem = Problem.from_yaml(problem_path)
        dlx = DancingLinks(problem.constraints, problem.candidates)
        for i in dlx.solutions():
            print(i)

    def count_solutions(self, problem_path: str, report_interval: int = 1000):
        problem = Problem.from_yaml(problem_path)
        dlx = DancingLinks(problem.constraints, problem.candidates)
        count = 0
        start = time.time()
        for _ in dlx.solutions():
            count += 1
            if count % report_interval == 0:
                elapsed_time = time.time() - start
                print(
                    f"Solutions found: {count}, Time elapsed: {elapsed_time:.2f} seconds"
                )
        total_time = time.time() - start
        print(
            f"Total solutions found: {count}, Total time elapsed: {total_time:.2f} seconds"
        )
