from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Technical Project Manager, Weather, Boulder, CO, Spire Global is a space-to-cloud analytics company that owns and operates the largest multi-purpose constellation of satellites. Its proprietary data and algorithms provide the most advanced maritime, aviation, and weather tracking in the world. In addition to its constellation, Spire’s data infrastructure includes a global ground station network and 24/7 operations that provide real-time global coverage of every point on Earth.   The Role  The Technical Project Manager will be responsible for the technical project management and providing guidance, leadership, and project support to a team of engineers, scientists, product managers, and senior management. Responsibilities will include all aspects of project management from initial planning, through execution and monitoring, to project completion, including a focus on timely delivery, budgets, resource allocation, and scope management.  The successful candidate will work with a variety of stakeholders to ensure deliverables and milestones are met within scope and budget, preparing reports for Senior management regarding status of project.  This role will coordinate with other departments to ensure aspects of various projects are compatible with resources to fulfill customer or product development needs.  This role is based out of our Boulder, CO office (hybrid arrangement possible).   Responsibilities:   * Develop and manage comprehensive project plans to enable appropriate    execution and monitoring of progress  * Ensure that projects are delivered on-time, within scope, and within budget  * Assist in the definition of project scope, involving all relevant    stakeholders and ensuring technical feasibility  * Drive the development of project requirements, objectives, and associated    project documentation  * Interface with engineering disciplines to manage inter-team agreements and    deliveries.  * Maintain a strong understanding of the technical project details  * Work with functional managers across the globe to ensure resource    availability and allocation  * Manage changes to project scope, schedule, resources, and costs  * Measure project performance using appropriate tools and techniques  * Manage the relationship with product managers, customers, and all    stakeholders  * Perform risk management, actively working to disposition and manage project    risks  * Integrate, track, and drive deliverables across a variety of projects  * Use and continually develop leadership skills  * Perform other related duties as assigned   Basic Qualifications:   * 6+ years’ experience in Project Management  * Experience driving multiple projects simultaneously  * Bachelor's Degree in business, engineering, or applicable field of study or    equivalent work experience  Preferred Qualifications:   * Experience with resource, scope, and plan management  * Solid organizational skills including attention to detail and multitasking    skills  * Flexible and calm in the face of ambiguity  * Ability to filter and distill relevant information appropriate for audience  * Experience with Agile  * Self-motivated and proactive with demonstrated creative and critical thinking  * Exceptional communication and leadership skills with the ability to win the    confidence of highly skilled engineers and executive staff alike  * Sense of humor!  Spire is Global and our success draws upon the diverse viewpoints, skills, and experiences of our employees. We are proud to be an equal opportunity employer and are committed to equal employment opportunity regardless of race, color, ancestry, religion, sex, national origin, sexual orientation, age, marital status, disability, gender identity or veteran status.  Colorado Salary Range - $150,000-$155000  #LI-NV1

###"""

inputs = {"input_data": test_job_listing}
result = {}


# Define a function to make the API call and update the result
def make_api_call(task_id):
    return json.loads(
        horizon_ai.deploy_task(task_id=task_id, inputs=inputs, log_deployment=True)[
            "completion"
        ]
    )


# List of task IDs to parallelize
task_ids = [215, 216, 219, 224, 222, 223, 214]

with ThreadPoolExecutor() as executor:
    # Submit tasks to the executor and store the future objects
    futures = [executor.submit(make_api_call, task_id) for task_id in task_ids]

    # Retrieve the results as they complete
    for future, task_id in zip(as_completed(futures), task_ids):
        try:
            # Get the result of the completed task
            task_result = future.result()
            result.update(task_result)
        except Exception as e:
            print(f"Error occurred while executing task {task_id}: {e}")

print(json.dumps(result, indent=4))
