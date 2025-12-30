from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from typing import List, Tuple, Dict, Any
from ortools.sat.python import cp_model
import collections
from fastapi import APIRouter, Depends, HTTPException, status
# from app.scheduling_optimization_ortools.main import Employee_Scheduling_Problems
from app.scheduling_optimization_ortools.main_1 import Employee_Scheduling_Problems

router = APIRouter(prefix="/schedula", tags=["schedulas"])


# ----------------------------
# Input schema
# ----------------------------
class JobData(BaseModel):
    job_id: int
    tasks: List[Tuple[str, int]]  # (machine_code, duration)


class ScheduleRequest(BaseModel):
    jobs: List[JobData]


# ----------------------------
# API routes
# ----------------------------

@router.post("/", status_code=status.HTTP_201_CREATED)
def schedule_jobshop(request: ScheduleRequest):

    job_index_to_id = {i: job.job_id for i, job in enumerate(request.jobs)}

    # Lấy tất cả machine code
    machine_codes = list({
        task[0]
        for job in request.jobs
        for task in job.tasks
    })

    # Map string → index
    machine_to_index = {code: i for i, code in enumerate(machine_codes)}
    index_to_machine = {i: code for code, i in machine_to_index.items()}

    jobs_data = [
        [(machine_to_index[machine_code], duration)
         for machine_code, duration in job.tasks]
        for job in request.jobs
    ]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    horizon = sum(task[1] for job in jobs_data for task in job)

    model = cp_model.CpModel()

    task_type = collections.namedtuple("task_type", "start end interval")
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )

    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.new_int_var(0, horizon, "start" + suffix)
            end_var = model.new_int_var(0, horizon, "end" + suffix)
            interval_var = model.new_interval_var(
                start_var, duration, end_var, "interval" + suffix)
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    for machine in all_machines:
        model.add_no_overlap(machine_to_intervals[machine])

    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.add(all_tasks[job_id, task_id + 1].start >=
                      all_tasks[job_id, task_id].end)

    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(obj_var, [all_tasks[job_id, len(
        job) - 1].end for job_id, job in enumerate(jobs_data)])
    model.minimize(obj_var)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    result: Dict[str, Any] = {
        "status": solver.status_name(status),
        "objective": solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
        "machines": [],
        "statistics": {
            "conflicts": solver.num_conflicts,
            "branches": solver.num_branches,
            "wall_time_sec": solver.wall_time,
        },
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1],
                    )
                )

        for machine in all_machines:
            assigned_jobs[machine].sort(key=lambda t: t.start)
            machine_tasks = [
                {
                    "job": job_index_to_id[t.job],   # trả về job_id thật
                    "task_index": t.index,
                    "start": t.start,
                    "end": t.start + t.duration,
                    "duration": t.duration,
                }
                for t in assigned_jobs[machine]
            ]
            result["machines"].append({
                "machine_id": index_to_machine[machine],  # trả về string
                "tasks": machine_tasks,
            })
    else:
        result["error"] = "No feasible solution found."

    return result


class Employee_Scheduling_Problems_Request(BaseModel):
    payload: Any


@router.post("/schedula-for-employee", status_code=status.HTTP_201_CREATED)
def schedule_for_employee(request: Employee_Scheduling_Problems_Request):
    return Employee_Scheduling_Problems(request.payload)
