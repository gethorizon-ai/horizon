from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Open Source Software Engineer - Container Ecosystems, New York, New York, USA; Boston, Massachusetts, USA, The opportunity:  Did you discover containers over the past few years, and have you been running them in production ever since? Did you dive into the Docker and Kubernetes code bases or follow the evolution of containers and the CRI with anticipation?  Datadog is building world-class container-monitoring solutions that allow correlation between traces, metrics and logs coming from applications, the containers they run in, and the orchestrators that schedule them. We are looking for a developer experienced with the container ecosystem that will help us push container monitoring to the next level. Come join us as you help to build amazing open-source software that will run on thousands of machines and make life easier for technical customers who care deeply about what you build.     You will:   * Build open-source software that monitors containers, their runtimes and other    components of the cloud-native ecosystem  * Participate and contribute to upstream open-source communities  * Do it in Go, Python, or any language that fits the particular task at hand  * Design and write features that solve new problems in the industry  * Have a significant impact on the product and the user experience of fellow    engineers who use the product     Requirements:   * You have been working with containers in production for at least a year  * You have significant systems programming experience in one or more languages  * You enjoy diving into new code bases, and can get down to low-level when    needed  * You want to work in a fast, high growth startup environment that respects its    engineers and customers  * You have a BS/MS/PhD in a scientific field or equivalent experience      Bonus points:   * You have mastered one or more container orchestrators such as Kubernetes,    Mesos, or Nomad  * You enjoy interacting with the upstream open-source communities, and can    drive technical conversations in the open  #LI-BP1  The reasonably estimated salary for this role at Datadog ranges from $130,000 - $300,000, plus a competitive equity package, and may include variable compensation. Actual compensation is based on factors such as the candidate's skills, qualifications, and experience. In addition, Datadog offers a wide range of best in class, comprehensive and inclusive employee benefits for this role including healthcare, dental, parental planning, and mental health benefits, a 401(k) plan and match, paid time off, fitness reimbursements, and a discounted employee stock purchase plan.  --------------------------------------------------------------------------------  About Datadog:   Datadog (NASDAQ: DDOG) is a global SaaS business, delivering a rare combination of growth and profitability. We are on a mission to break down silos and solve complexity in the cloud age by enabling digital transformation, cloud migration, and infrastructure monitoring of our customers’ entire technology stacks. Built by engineers, for engineers, Datadog is used by organizations of all sizes across a wide range of industries. Together, we champion professional development, diversity of thought, innovation, and work excellence to empower continuous growth. Join the pack and become part of a collaborative, pragmatic, and thoughtful people-first community where we solve tough problems, take smart risks, and celebrate one another. Learn more about #DatadogLife on Instagram [https://www.instagram.com/datadoghq/?hl=en], LinkedIn [https://www.linkedin.com/company/datadog/mycompany/?viewAsMember=true] and Datadog Learning Center. [https://learn.datadoghq.com/]  --------------------------------------------------------------------------------  Equal Opportunity at Datadog:  Datadog is an Affirmative Action [https://www.datadoghq.com/affirmative-action-statement] and Equal Opportunity Employer [https://www.eeoc.gov/sites/default/files/2022-10/EEOC_KnowYourRights_screen_reader_10_20.pdf] and is proud to offer equal employment opportunity to everyone regardless of race, color, ancestry, religion, sex, national origin, sexual orientation, age, citizenship, marital status, disability, gender identity, veteran status, and more. We also consider qualified applicants regardless of criminal histories, consistent with legal requirements.  Your Privacy:  Any information you submit to Datadog as part of your application will be processed in accordance with Datadog’s Applicant and Candidate Privacy Notice [https://www.datadoghq.com/legal/applicant-candidate-privacy/].

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
    for future, task_id in zip(as_completed(futures), task_ids.values()):
        try:
            # Get the result of the completed task
            task_result = future.result()
            result.update(task_result)
        except Exception as e:
            print(f"Error occurred while executing task {task_id}: {e}")

print(json.dumps(result, indent=4))
