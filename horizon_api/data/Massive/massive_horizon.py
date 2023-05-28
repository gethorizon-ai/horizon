from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Firmware Manual SQA Lead, Boston, MA, Biofourmis is a rapidly growing, global digital health company filled with committed, passionate professionals who care about augmenting personalized care and empowering people with complex chronic conditions to live better and healthier lives. We are pioneering an entirely new category of medicine by developing clinically validated, software-based therapeutics to provide improved outcomes for patients, smarter engagement & tracking tools for clinicians, and cost-effective solutions for payers. We are collectively devoted to a single-minded idea: powering personally predictive care.  Our dynamic growth has been marked by doubled headcount in the last 12 months via both expansion & acquisition, yielding a global footprint with offices in Boston, Singapore, Bangalore, and Zurich. We are backed by prominent international venture capital investment & have cultivated relationships with worldwide healthcare stakeholders over the last 5 years. Our talented team features numerous PhD’s in Data Science and Biostatistics, over 80 patents, prolific scientific publications, world-class systems, developers & engineers, and leaders in the clinical operations space.  Firmware Manual SQA Lead  As a Firmware Manual SQA Lead- you will report into Firmware SQA Manager and you will plan and execute manual testing to improve system level design, performance, working on and testing embedded medical devices, as well as testing cloud connectivity via LTE/NB-IoT.  In addition, you will assist in building a team to scale manual test operations.  Location   * This role will be based in Boston with a hybrid work arrangement.  Responsibilities   * Lead QA efforts throughout the software testing lifecycle to ensure    applications are comprehensively tested and ready for release.  * Provide QA direction to QA resources and provide performance management    feedback to QA management  * Represent QA in product design, development, and testing meetings  * Drive Defect Triage  * Coach and mentor junior QA peers to better understanding of QA principals and    methodologies  * Support and help establish QA best practices, efficiently find the root cause    of defects, and build creative test approaches  Qualifications   * Bachelor’s Degree in computer science or Equivalent (Masters preferred)  * 4-6 years of experience working as a QA Engineer  * 2+ years of experience testing embedded platform products  * 2+ years of leadership experience (small teams)  * Experience with communication protocols and interfaces such as TCP/IP, USB,    Bluetooth, Wi-Fi, LTE  * Experience with test management tools (Jama (preferred), Test Rail, XRAY,    Zephyr or similar)  * Experience working with Jira/Confluence  * Experience working in agile/DevOps environments  * Experience interacting with cross-organizational groups  * Ability to engage and motivate team members  * Exceptional creative problem-solving skills and attention to detail  * Solid Communication Skills  GOOD TO HAVE:   * CI/CD and Jenkins experience  * Experience with scripting languages (Python)  * Familiarity with Pytest automation framework  * Familiarity with REST API  * Familiarity with LTE/NB-IoT  * Experience working in Medical/Health Industry  * Familiarity with the principles of risk management and ISO 14971, as well as    other industry standards such as IEC 60601-1, and ISO 62366  * Experience developing in an IEC 62304-compliant environment is a major plus  * Experience using test equipment (Oscilloscope, Signal Generator, DMMs, PSU,    SMU, etc.)  * Familiarity with back-end / front-end cloud applications  * Familiarity with FreeRTOS or similar real time operating system for    microcontrollers 

###"""

inputs = {"input_data": test_job_listing}
result = {}


# Define a function to make the API call and update the result
def make_api_call(task_id):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=False)[
            "completion"
        ]
    )


# List of task IDs to parallelize
task_ids = {
    "title": 215,
    "sub_role": 245,
    "tenure": 244,
    "locations": 243,
    "pay_min": 222,
    "pay_max": 223,
    "responsibility": 214,
}

with ThreadPoolExecutor() as executor:
    # Submit tasks to the executor and store the future objects
    futures = [executor.submit(make_api_call, task_id) for task_id in task_ids.values()]

    # Retrieve the results as they complete
    for future, field, task_id in zip(
        as_completed(futures), task_ids.keys(), task_ids.values()
    ):
        try:
            # Get the result of the completed task
            task_result = future.result()
        except Exception as e:
            # If error occurs, set field to None
            task_result = {field: None}
            print(f"Error occurred while executing task {task_id}: {e}")
        result.update(task_result)

print(json.dumps(result, indent=4))
