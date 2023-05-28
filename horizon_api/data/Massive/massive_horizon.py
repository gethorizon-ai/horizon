from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Principal Software Engineer, Developer Productivity, Edmonton, Clari’s Revenue platform gives forecasting accuracy and visibility from the sales rep to the board room on revenue performance - helping them spot revenue leak to answer if they will meet, beat, or miss their sales goals. With insights like this, no wonder leading companies worldwide, including Okta, Adobe, Workday, and Zoom use Clari to drive revenue accuracy and precision. We never get tired of our customers singing our praises because it fuels us to help them continue to achieve remarkable. The next generation of revenue excellence is here…are you ready to achieve remarkable with us?   Clari's Infrastructure organization builds systems and tools to enable engineering velocity in a reliable manner. We partner with engineering teams to establish standards, improve reliability and cost-efficiency. This is a great opportunity to make a massive impact on scaling cloud infrastructure to meet the high demand and rapid growth of both users and workload per user.    The Developer Experience team is responsible for providing tools that enable the engineering teams at Clari to build, test, publish and deploy code. You will be instrumental in architecting the next generation of services that make it easier for engineers to adopt cloud-native standards and streamline their workflows. Our teams are empowered and expected to help realize Clari's vision via active development and collaboration with our engineering partners.   As a Principal Engineer in Developer Productivity, you are passionate about improving the lives of your fellow engineers. You have a keen eye for the future while having a deep understanding of existing development workflows.You have experience building an internal developer platform incrementally and plan according to data-driven decision making. You are a leader and a role model, capable of alternating between being a humble student and a patient teacher, knowing when to switch hats as needed.    This is a work-from-home opportunity based in Alberta, Ontario or British Columbia provinces. Candidates must be a Canadian Permanent Resident or Citizen. We are unable to provide work authorization sponsorship at this time. Responsibilities Architect and design the next generation engineering experience - Internal Developer Portal, Self-Service Environment Provisioning, Continuous Delivery Pipelines, Remote Debugging and Distributed TracingWrite functional specifications and design documents for specific functions of Developer ProductivityCollaborate effectively with other engineers to solve the most complex technical problems. This involves mentoring, peer reviews, participating in technical design reviews, and complex issue troubleshooting Qualifications 10+ years of experience as a backend software developer, most of it with Java but you’ve also accrued a number of other languages as well, such as Go, C++, Python, Scala, Kotlin or others5+ years of experience implementing and managing CI/CD best practices and systems3+ years of experience developing, implementing, rolling out and evolving an Internal Development PlatformExperience setting technical direction and planning, and successfully executing on large projects spanning multiple teamsAbility to lead discussions about complex solution design tradeoffs, as well as the capacity to drive conflict resolutionExperience working in a remote-first or distributed environment Work-Life and Benefits @ Clari Team-bonding activities and company-wide eventsFlexible working hours and remote opportunitiesInternet, phone, and wellness reimbursementsPre-IPO stock options #BI-Remote #LI-Remote You’ll often hear our CEO talk about being remarkable. To Clari, remarkable means many things. We believe in providing interesting and meaningful work in a nurturing and inclusive environment. One that is free from discrimination for everyone without regard to race, color, religion, sex, sexual orientation, national origin, age, disability, gender identity, or veteran status. Efforts have to be recognized. Voices have to be heard. And work-life balance has to be baked into the very fiber of the company. We are honored to be recognized by Inc. Magazine and Bay Area News Group as a best place to work for several years running. We’d love to have you join us on our journey to remarkable! If you feel you don’t meet 100% of the qualifications outlined above, we want you to apply! Clari believes in hiring people, not just skills. If you are passionate about learning and excited about what we are doing, then we want to hear from you.  Clari focuses on culture add, not culture fit. One of our values is One with Customers, and we know we can serve them better when we involve as many different perspectives as possible. Our team is made stronger by what makes you unique, so we hope you’ll bring your whole self to the job.

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
