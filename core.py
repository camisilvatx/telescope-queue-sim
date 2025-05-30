import random
import numpy as np

from config import IMAGING_OVERHEAD, SPECTROSCOPY_OVERHEAD
from config import SEEING_BINS
from utils import forecast_uncertainty
from config import MIN_SEEING, MAX_SEEING

from config import MAX_FORECAST_LOOKAHEAD, FORECAST_OBS_WINDOW

class ObservingProgram:
    def __init__(self, seeing_bin, obs_time, is_spectroscopy):
        self.delivered_seeing = None
        self.seeing_bin = seeing_bin
        self.obs_time = obs_time
        self.is_spectroscopy = is_spectroscopy
        self.overhead = SPECTROSCOPY_OVERHEAD if is_spectroscopy else IMAGING_OVERHEAD
        self.total_time = self.obs_time + self.overhead
        self.met_requirement = None
        self.completed = False

    def __repr__(self):
        obs_type = "Spectroscopy" if self.is_spectroscopy else "Imaging"
        return (f"{obs_type}, {self.total_time} min "
                f"(Obs: {self.obs_time} min, Overhead: {self.overhead} min), "
                f"Bin: {self.seeing_bin}")
        

class ObservingNight:
    def __init__(self, total_time=None, Logs=True, SeeingCurve=True, seeing_time_series=None):
        self.seeing_time_series = (
            seeing_time_series if seeing_time_series is not None
            else generate_seeing_time_series(total_time or 600)
        )
        self.total_time = total_time if total_time is not None else len(self.seeing_time_series)
        self.remaining_time = self.total_time
        self.current_time = 0
        self.last_exec_end = 0
        self.programs = self.generate_programs()
        self.log = []
        self.show_logs = Logs
        self.show_seeing = SeeingCurve

    def generate_programs(self):
        programs = []
        distribution = {"0-20%": 0.2, "20-50%": 0.3, "50-70%": 0.2, ">70%": 0.3}
        for bin_name, fraction in distribution.items():
            count = int(fraction * 20)
            for _ in range(count):
                t = random.randint(40, 120)
                programs.append(ObservingProgram(bin_name, t, random.choice([True, False])))
        random.shuffle(programs)
        return programs

    def get_seeing_bin_at_time(self, t):
        val = self.seeing_time_series[t]
        for name,(low,high) in SEEING_BINS.items():
            if low <= val < high:
                return name
        return ">70%"

    def select_program(self, bin, rem):
        priority = ["0-20%","20-50%","50-70%",">70%"]
        idx = priority.index(bin)
        for b in priority[idx:]:
            for p in self.programs:
                if p.seeing_bin==b and not p.completed and p.total_time<=rem:
                    return p
        return None

    def select_program_with_forecast(self, t, rem):
        # Define forecast window
        start = min(t + MAX_FORECAST_LOOKAHEAD - FORECAST_OBS_WINDOW, self.total_time)
        end = min(t + MAX_FORECAST_LOOKAHEAD, self.total_time)

        if end <= start:
            mean_fut_with_noise = self.seeing_time_series[min(t, self.total_time - 1)]
            uncertainty = 0
        else:
            # Apply noise to each point in the forecast window
            noisy_vals = []
            uncertainties = []
            for minute in range(start, end):
                minutes_ahead = minute - t
                sigma = forecast_uncertainty(minutes_ahead)
                true_val = self.seeing_time_series[minute]
                noisy_val = np.random.normal(true_val, sigma)
                clipped = np.clip(noisy_val, MIN_SEEING, MAX_SEEING)
                noisy_vals.append(clipped)
                uncertainties.append(sigma)

            mean_fut_with_noise = np.mean(noisy_vals)
            uncertainty = np.mean(uncertainties)

        # Determine seeing bins
        def bin_of(x):
            for n, (l, h) in SEEING_BINS.items():
                if l <= x < h:
                    return n
            return ">70%"

        cur = self.get_seeing_bin_at_time(t)
        fut = bin_of(mean_fut_with_noise)
        priority = ["0-20%", "20-50%", "50-70%", ">70%"]

        if mean_fut_with_noise < self.seeing_time_series[t]:
            idx = min(priority.index(cur), priority.index(fut))
        else:
            idx = max(priority.index(cur), priority.index(fut))

        for b in priority[idx:]:
            for p in self.programs:
                if p.seeing_bin == b and not p.completed and p.total_time <= rem:
                    return p, mean_fut_with_noise, uncertainty

        return None, mean_fut_with_noise, uncertainty

    
    def run_night(self, use_forecast=True):
        retries, max_ret = 0, 50
        self.forecast_means = []
        self.forecast_uncertainties = []

        while self.current_time < self.total_time and retries < max_ret:
            bin = self.get_seeing_bin_at_time(self.current_time)
            
            if use_forecast:
                prog, mean_forecast, uncertainty = self.select_program_with_forecast(
                    self.current_time, self.remaining_time
                )
            else:
                prog = self.select_program(bin, self.remaining_time)
                mean_forecast = None
                uncertainty = 0

            if prog and self.remaining_time >= prog.total_time:
                st = self.current_time

                # — compute delivered seeing and requirement
                prog.delivered_seeing = np.mean(
                    self.seeing_time_series[st : st + prog.obs_time]
                )
                prog.met_requirement = (
                    prog.delivered_seeing <= SEEING_BINS[prog.seeing_bin][1]
                )
                status = 'Pass' if prog.met_requirement else 'Fail'
                self.log.append(f"{st:03d}: Executing {prog}, MetReq:{status}")

                # — store one forecast per minute
                for _ in range(prog.total_time):
                    self.forecast_means.append(mean_forecast)
                    self.forecast_uncertainties.append(uncertainty)

                # — advance time
                self.current_time += prog.total_time
                self.remaining_time -= prog.total_time

                prog.completed = True
                self.last_exec_end = self.current_time
                retries = 0
            else:
                self.forecast_means.append(mean_forecast)
                self.forecast_uncertainties.append(uncertainty)
                retries += 1
                self.current_time += 1
                self.remaining_time -= 1
                self.log.append(f"{self.current_time:03d}: Retry no prog for {bin}")

        passed = sum(p.completed and p.met_requirement for p in self.programs)
        failed = sum(p.completed and not p.met_requirement for p in self.programs)
        unused = self.total_time - self.last_exec_end
        self.log.append(f"Night end Rem:{self.remaining_time} | Passed:{passed} Failed:{failed}")
        self.log.append(f"Unused since last obs:{unused} min")

        if self.show_logs:
            print(f"{'Time':<6} {'Act':<10} {'Type':<12} {'Dur':<4} {'Bin':<6} {'Met':<4}")
            print('-' * 50)
            for e in self.log:
                if 'Executing' in e:
                    t, rest = e.split(': Executing ')
                    detail, met = rest.split(', MetReq:')
                    typ = 'Spect' if 'Spect' in detail else 'Img'
                    dur = detail.split()[1]
                    bin = detail.split('Bin:')[-1]
                    print(f"{t:<6} Exec {typ:<12} {dur:<4} {bin:<6} {met:<4}")
                elif 'Retry' in e:
                    t, _ = e.split(': Retry')
                    print(f"{t:<6} Retry      -    -    -    -")
                elif 'Unused' in e:
                    print(e)
                else:
                    print(e)

