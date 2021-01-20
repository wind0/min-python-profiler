import time
import sys
import inspect
import functools
import logging

class TimerError(Exception):
    """Custom Timer Error used to report Timer failures"""


class Timer:
    
    def __init__(self, timing_func = time.perf_counter):
        self._timing_func = timing_func
        self.aggregated_timers = dict()

    def set_dict_default_values(self,called_name, calling_name):
        number_times_called = 0
        current_elapsed_time_sum = 0
        default_start_time = None
        self.aggregated_timers.setdefault((called_name,calling_name),(number_times_called,default_start_time,current_elapsed_time_sum))

    def measure(self):
        return self._timing_func()

    def start(self,called_name = None,calling_name = None):
        if called_name and calling_name:
            current_time = self.measure()
            self.set_dict_default_values(called_name,calling_name)
            current_value = self.aggregated_timers[(called_name,calling_name)]
            number_times_called = current_value[0]
            current_elapsed_time_sum = current_value[2]
            self.aggregated_timers[(called_name,calling_name)]=(number_times_called, current_time , current_elapsed_time_sum)
        else:
            raise TimerError(f"No function/parent function name given")

    def stop(self, called_name = None,calling_name = None):
        if called_name and calling_name:
            current_value = self.aggregated_timers[(called_name,calling_name)]
            number_times_called = current_value[0]
            current_start_time = current_value[1]
            elapsed_time_sum = current_value[2]
            elapsed_time = self.measure() - current_start_time
            self.aggregated_timers[(called_name,calling_name)]=(number_times_called+1,None, elapsed_time_sum+elapsed_time)
        else:
            raise TimerError(f"No function/parent function name given")

class WallTimer(Timer):
    
    def __init__(self):
        super().__init__(timing_func=time.perf_counter)
    
class CPUTimer(Timer):

    def __init__(self):
        super().__init__(timing_func=time.process_time_ns)

class Profiler:
    def __init__(self):
        self.wall_timer = WallTimer()
        self.cpu_timer = CPUTimer()

    def _profiler(self,frame,event,arg):
        if frame.f_back is None:
            return None
        if (event is "call"):
            function_name = frame.f_code.co_name
            caller_function_name = frame.f_back.f_code.co_name
            self.wall_timer.start(function_name, caller_function_name)
            self.cpu_timer.start(function_name, caller_function_name)
        
        if (event is "c_call"):
            function_name = arg.__name__
            caller_function_name = frame.f_code.co_name
            self.wall_timer.start(function_name, caller_function_name)
            self.cpu_timer.start(function_name, caller_function_name)

        if (event is "return"):
            function_name = frame.f_code.co_name
            caller_function_name = frame.f_back.f_code.co_name
            self.wall_timer.stop(function_name, caller_function_name)
            self.cpu_timer.stop(function_name, caller_function_name)

        if (event is "c_return"):
            function_name = arg.__name__
            caller_function_name = frame.f_code.co_name
            self.wall_timer.stop(function_name, caller_function_name)
            self.cpu_timer.stop(function_name, caller_function_name)

        if event is "c_exeption":
            pass
    
    def profiling_results_printing(self):
        wall_dict = self.wall_timer.aggregated_timers
        cpu_dict = self.cpu_timer.aggregated_timers
        results = [(k, cpu_dict[k][0], cpu_dict[k][2], wall_value[2]) for k, wall_value in wall_dict.items()]
        for (called, calling), times_called, cpu_time, wall_time in results:
            if times_called == 0:
                continue
            if calling is "wrapper_profiler":
                calling = "<module>"
            print(f"{calling}==>{called}//{times_called} {wall_time*1000:0.0f} {cpu_time}")

def profile(func):
    @functools.wraps(func)
    def wrapper_profiler(*args, **kwargs):
        profiler = Profiler()
        sys.setprofile(profiler._profiler)
        value = func(*args, **kwargs)
        sys.setprofile(None)
        profiler.profiling_results_printing()
        return value
    return wrapper_profiler
