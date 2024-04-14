from multiprocessing import Pool
import time

def function_test(fire: int, advance: float) -> int:
    for i in range(10**8):
        fire += advance
    return fire


lambda_range = range(10)
# Assume lambda_range and other necessary data are defined

if __name__ == "__main__":  # Required for multiprocessing to work properly
    
    start = time.time()
    # for i in lambda_range:
    #     print(function_test(i))
    
    with Pool() as pool:
        results = pool.starmap(function_test, [(lambda_value, 0.001) for lambda_value in lambda_range])
    
    print(results)
    
    end = time.time()
    print("Time taken: ", end - start, " seconds")