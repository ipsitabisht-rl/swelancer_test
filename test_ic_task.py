import asyncio
import shlex
from swelancer import SWELancerTask, SwelancerInstance
from nanoeval_alcatraz.task_to_alcatraz_config import task_to_alcatraz_config
from alcatraz.clusters.local import LocalConfig
from nanoeval_alcatraz.alcatraz_computer_interface import AlcatrazComputerInterface

async def verify_ic_task_with_hardcoded_fix(issue_id: str, fix_script: str):
    # 1. Create the task (fill in required fields as needed)
    task = SWELancerTask(
        question_id=issue_id,
        price=250.0,
        variant="ic_swe",
        prompt=[{"role": "user", "content": "Fix the issue"}],
        acceptable_folders=["src/"],
        manager_data=None,
        manager_commit=None,
        attempt_id=0,
        retry_idx=0,
        instance=SwelancerInstance(repo="expensify")
    )

    # 2. Setup the environment
    alcatraz_env = task_to_alcatraz_config(task, LocalConfig(pull_from_registry=False))
    async with alcatraz_env.build() as cluster:
        computer = AlcatrazComputerInterface(cluster_value=cluster)
        try:
            await task.setup(computer)

            # 3. Apply your hardcoded fix (as a Python script)
            result = await computer.send_shell_command(f"python -c {shlex.quote(fix_script)}")
            print("Fix script output:", result.output.decode())

            # 4. Run the grader
            grade = await task.grade(computer)
            print("Score:", grade.score)
            print("Grader log:", grade.grader_log)
        finally:
            await computer.stop()

# Example hardcoded fix (replace with your actual fix logic)
fix_script = """
with open('src/components/ExpenseItem.js', 'r') as f:
    content = f.read()
# Insert the Hold option if missing
if 'Hold' not in content:
    content = content.replace('menuItems = [', 'menuItems = [\\n    { label: "Hold", action: handleHold },')
with open('src/components/ExpenseItem.js', 'w') as f:
    f.write(content)
print("Hardcoded fix applied.")
"""

# Run the verification
asyncio.run(verify_ic_task_with_hardcoded_fix("1", fix_script))