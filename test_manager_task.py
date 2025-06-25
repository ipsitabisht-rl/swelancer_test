import asyncio
import pandas as pd
import ast
from dotenv.main import dotenv_values
from swelancer import SWELancerTask, SwelancerInstance
from alcatraz.clusters.local import LocalConfig
from nanoeval_alcatraz.task_to_alcatraz_config import task_to_alcatraz_config
from nanoeval_alcatraz.alcatraz_computer_interface import AlcatrazComputerInterface

async def main():
    # Load environment variables
    env_vars = dotenv_values(".env")
    SWEFL_ENV = {
        "PUSHER_APP_KEY": "test_key",
        "PUSHER_APP_SECRET": "test_secret", 
        "PUSHER_APP_ID": "1234567",
        "USE_WEB_PROXY": env_vars.get("USE_WEB_PROXY", "false"),
        "EXPENSIFY_URL": env_vars.get("EXPENSIFY_URL", "http://localhost"),
        "NEW_EXPENSIFY_URL": env_vars.get("NEW_EXPENSIFY_URL", "http://localhost"),
        "ISSUE_ID": "test_issue",
        "LC_ALL": "C.UTF-8",
        "EVAL_VARIANT": "swe_manager",
    }

    # Load tasks and select the first swe_manager task
    tasks = pd.read_csv("swelancer_tasks.csv")
    manager_task_row = tasks[tasks['variant'] == 'swe_manager'].iloc[0]
    task_data = manager_task_row.to_dict()
    task_data['prompt'] = ast.literal_eval(task_data['prompt'])
    task_data['acceptable_folders'] = ast.literal_eval(task_data['acceptable_folders'])
    if str(task_data['manager_data']) == 'nan': 
        task_data['manager_data'] = None
    else:
        task_data['manager_data'] = ast.literal_eval(task_data['manager_data'])
    if str(task_data['manager_commit']) == 'nan': 
        task_data['manager_commit'] = None
    del task_data['price_limit']
    del task_data['canary']

    task = SWELancerTask(
        **task_data, 
        attempt_id="0", 
        environment=SWEFL_ENV, 
        grade_every_step=False, 
        docker_image="swelancer:latest", 
        instance=SwelancerInstance(repo="expensify")
    )

    # Set up the environment
    alcatraz_env = task_to_alcatraz_config(task, LocalConfig(pull_from_registry=False))
    async with alcatraz_env.build() as cluster:
        computer = AlcatrazComputerInterface(cluster_value=cluster)
        await task.setup(computer)

        # --- HARDCODE YOUR MANAGER DECISION HERE ---
        # The grader expects a JSON file at /app/expensify/manager_decisions.json
        # with the format: {"selected_proposal_id": <int>}
        # We'll pick 0 for demonstration, but you can inspect task_data['manager_data'] for the correct one.
        await computer.send_shell_command("echo '{\"selected_proposal_id\": 3}' > /app/expensify/manager_decisions.json")

        # --- GRADE THE SUBMISSION ---
        grade = await task.grade(computer)
        print("Score:", grade.score)
        print("Grader log:", grade.grader_log)

if __name__ == "__main__":
    asyncio.run(main())