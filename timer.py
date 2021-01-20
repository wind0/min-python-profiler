import time

class TimerError(Exception):
    """Custom Timer Error used to report Timer failures"""


class Timer:
    
    def __init__(self, timing_func = time.perf_counter):
        self._start_time = None
        self._timing_func = timing_func

    def start(self):
        if self._start_time is not None:
            raise TimerError(f"Timer already running")
        self._start_time = self._timing_func()
    
    def stop(self):
        if self._start_time is None:
            raise TimerError(f"Timer not running")
        elapsed_time  =self._timing_func() - self._start_time
        self._start_time = None

        

        return elapsed_time

class WallTimer(Timer):
    aggregated_timers = dict()
    def __init__(self,called_name = None,calling_name = None):
        self.called_name = called_name
        self.calling_name = calling_name
        if self.called_name and self.calling_name:
            self.aggregated_timers.setdefault((called_name,calling_name),0)
        super().__init__(timing_func=time.perf_counter)
    
    def stop(self):
        elapsed_wall_time = super().stop()
        if self.called_name and self.calling_name:
            self.aggregated_timers[(self.called_name,self.calling_name)]+=elapsed_wall_time
        return elapsed_wall_time

class CPUTimer(Timer):
    aggregated_timers = dict()
    def __init__(self,called_name = None,calling_name = None):
        self.called_name = called_name
        self.calling_name = calling_name
        if self.called_name and self.calling_name:
            self.aggregated_timers.setdefault((called_name,calling_name),0)
        super().__init__(timing_func=time.process_time_ns)
    
    def stop(self):
        elapsed_cpu_time = super().stop()
        if self.called_name and self.calling_name:
            self.aggregated_timers[(self.called_name,self.calling_name)]+=elapsed_cpu_time
        return elapsed_cpu_time