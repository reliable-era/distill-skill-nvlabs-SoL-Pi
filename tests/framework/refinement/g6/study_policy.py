"""Supervisor GO budget preflight. Exact arithmetic;no credential/network access.
Keep the existing5pp/run in-flight reservation;0.25pp/run is a FORECAST,
not permission to relax that guard or a claim about actual future consumption.
"""
from fractions import Fraction
import math,time
RESET=1792353600
RATE=Fraction(1,400)  # Supervisor:0.25 percentage points/run.
RESERVE=Fraction(1,20)  # Existing preregistered minimum5 percentage points.
def weekly_threshold(now):return Fraction(9,10) if now<RESET else Fraction(7,10)
def capacity(utilization,threshold,reserve=RESERVE,rate=RATE):
    """Optimistic serial capacity:each last admission must be strictly below cap.
    Start+(n-1)*rate+reserve < threshold. Ignore retries/external use/shorter
    quotas/preparation time;parallel reservations/adaptive increases only hurt.
    """
    return max(0,math.ceil((Fraction(str(threshold))-Fraction(str(utilization))-reserve)/rate))
def forecast(utilization,remaining=300,now=None):
    now=time.time() if now is None else now;u=Fraction(str(utilization));before=now<RESET
    old=capacity(u,Fraction(9,10)) if before else 0
    new=capacity(0,Fraction(7,10))
    return dict(weekly_reset_epoch=RESET,before_reset=before,active_weekly_threshold=float(weekly_threshold(now)),latest_observed_weekly_utilization=float(u),remaining_native_cells=remaining,forecast_increment_per_run=float(RATE),forecast_increment_percentage_points_per_run=.25,remaining_forecast_increment=float(remaining*RATE),current_window_full_N_projection=float(u+remaining*RATE),current_window_full_N_fits=u+remaining*RATE<weekly_threshold(now),fresh_new_week_full_N_projection=float(remaining*RATE),fresh_new_week_full_N_fits=remaining*RATE<Fraction(7,10),fresh_zero_is_counterfactual_not_observed=True,existing_minimum_inflight_reservation=float(RESERVE),optimistic_current_week_capacity_with_existing_guard=old,optimistic_fresh_new_week_capacity_with_existing_guard=new,optimistic_two_window_capacity_with_existing_guard=old+new,remaining_N_fits_optimistic_current_plus_next_week=remaining<=old+new,admissions_allowed=remaining<=old+new,capacity_assumptions='optimistic serialization,no retries,no external use,no shorter/model-specific limit,no adaptive reservation increase,unlimited preparation time before reset;not a guarantee of capacity',more_weekly_windows_not_silently_assumed=True)
def concurrency_after_cells(completed,api_adverse_events):return 4 if completed>=20 and api_adverse_events==0 else 2
def notify_new_week_sixty(scope,utilization,observation_epoch):
    return 'seven_day' in scope and observation_epoch>=RESET and utilization>=.60
