from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Research Associate - Tissue Culture and Transformation, San Francisco Bay Area, Living Carbon is a public benefit corporation with a mission to responsibly rebalance the planet’s carbon cycle using the inherent power of plants. We believe that gigaton scale CO2 drawdown will only happen if solutions are both beneficial to the environment and profitable to landowners. We’ve developed photosynthesis-enhanced seedlings that capture carbon faster on underperforming and degraded land. In addition to improving carbon capture rates we are also working on extending the durability of nature based sequestration. We’re backed by some of the most prominent investors in Silicon Valley including Felicis Ventures, YCombinator, and Chris Sacca of LowerCarbon Capital.  If you believe that climate change is the defining global emergency of the century and want to join an ambitious project that’s working on a biological solution, we’d love to hear from you.     Your role:  We’re looking for someone who’s excited to be part of a mission-driven early-stage company. As our Research Associate - Tissue Culture and Transformation, you will play an essential role in our tissue culture and transformation production systems in woody species. You will be working closely with our scientists to assist in facilitation of pipeline development, while helping carry out other experiments to achieve company goals. A successful candidate will have experience with plant biotechnology lab experimental approaches, with knowledge of and experience in both plant tissue culture and transformation. You will also have the opportunity to contribute to the company’s strategic goals and think creatively about how to move quickly and solve problems.     Your responsibilities:   * Perform tissue culture and plant transformation experiments  * Manage, maintain, organize, and track production-level amounts of cultures  * Design and conduct research projects relating to plant tissue culture and    transformation pipeline development  * Execute protocols in a thorough, independent, and technical manner  * Maintain a detailed record of experimental data and analysis  * Perform vital functions of pipeline support, including media making  * Timely communicate and adapt to experimental workflows while developing new    skills  * Nurture the desire to work in an exciting and rapidly evolving work    environment  * Provide unique perspectives and collaborate to creatively solve problems as    they arise     Requirements and qualifications:   * BSc or MSc in plant biology, plant science, plant science, or related field    and experience working with plant biotechnology systems  * Extensive hands-on experience with plant tissue culture systems is required.    Previous experience with suspension cultures is preferred    * Demonstrated ability in plant transformation techniques  * Proven capacity to carry out multiple experiments simultaneously  * Fundamental knowledge of and subsequent application in plant tissue culture    and transformation techniques  * Ability to work within a team to efficiently tackle high-throughput    experiments  * Excellent organization, with strong oral and written communication skills              Living Carbon PBC offers competitive compensation, and generous healthcare, dental and vision insurance.  Living Carbon PBC is an equal opportunity employer.  We believe the best solutions to climate change are created by diverse teams. Living Carbon is focused on building a multicultural and inclusive team with strong representation from the many diverse communities disproportionately impacted by climate change. As a public benefit corporation, ensuring solutions to slow climate change are widely distributed to all peoples is critical to the success of our mission. 

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
