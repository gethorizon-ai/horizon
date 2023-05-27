from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Engineering Manager, Site Reliability Engineering (Remote), Vancouver, British Columbia, We are looking for an Engineering Manager to join our growing Core Services group. Reporting to the Director of Engineering, Core Services, you will manage the planning, delivery and mentoring of our SRE team and lead all development and operations that ensure the reliability of our web applications. You will work with both teams focused on feature delivery and other teams to ensure that we have the right tooling and capabilities to support the high reliability of our systems. You will be responsible for improvements to our incident response and postmortem process, operational reviews and incident trend analysis to guide the internal roadmap of the SRE team.   BenchSci is a remote-first organization. At this moment, we are welcoming applicants from Canada, the US and the UK for this position.  You Will: Lead software and system design initiatives by using cloud-native design patterns and injecting your cloud expertise into the entire development lifecycleUnderstand feature delivery teams' needs and engage the SRE team to help them improve the reliability of the services they support in production.Perform operational reviews with feature delivery and other teams to understand incident trends and hot spots and work with them on a plan to address them.Provide periodic incident trends analysis to identify systemic issues and devise projects on SRE and feature delivery team's roadmaps to address them.Manage our post-mortem process and track the completion SLA of the action items assigned to SRE and feature delivery teams.Scale the SRE function through the development of self-serve tooling in addition to headcount.Help improve our monitoring capabilities to help feature delivery teams identify production issues.Improve the observability of our systems to help identify causes of incidents faster.Provide SLA compliance dashboards to track contractual obligations.Improve our incident response and post-mortem process and related automation.Increase the quality and standard of the documentation of our systems, and work with application development teams to maintain that standard. You Have: 2+ years of experience working in a leadership capacity within a DevOps or an SRE domain.5+ years of experience working as a Site Reliability Engineer or DevOps Engineer, with a focus on observability and reliabilityExperience with observability and reliability tools and techniques in a cloud-native environmentExperience working in Python and JavaScript codebases.Experience with cloud reference architectures and developing specialized stacks on cloud servicesEagerness to share your own ideas, and openness to those of others Benefits and Perks:  An engaging remote-first culture  A great compensation package that includes BenchSci equity options 15 days vacation plus an additional day every year; plus company closures for 15 more days throughout the year Unlimited flex time for sick days, personal days, religious holidays Comprehensive health and dental benefits Emphasis on mental health with $2500 CAD* for Psychologist, Social Worker, or Psychotherapist services A $2000 CAD* Annual Learning & Development budget A $1000 CAD*  home office set-up budget A $2500 CAD*wellness, lifestyle and productivity spending account for employees   Generous parental leave benefits with a top-up plan or paid time off options *Benefits are tied to Canadian dollar amounts and would be converted to local currency for those in other countries. Moving to local currency allotments in the future. About BenchSci: BenchSci's vision is to help scientists bring novel medicine to patients 50% faster by 2025. We empower scientists to run more successful experiments with the world's most advanced, biomedical artificial intelligence software platform.  Backed by F-Prime, Inovia, Golden Ventures, and Google's AI fund, Gradient Ventures, we provide an indispensable tool for scientists that accelerates research at 16 top 20 pharmaceutical companies and over 4,300 leading academic centers. We're a certified Great Place to Work®, and top-ranked company on Glassdoor. Our Culture: BenchSci relentlessly builds on its strong foundation of culture. We put team members first, knowing that they're the organization's beating heart. We invest as much in our people as our products. Our culture fosters transparency, collaboration, and continuous learning.  We value each other's differences and always look for opportunities to embed equity into the fabric of our work. We foster diversity, autonomy, and personal growth, and provide resources to support motivated self-leaders in continuous improvement.  You will work with high-impact, highly skilled, and intelligent experts motivated to drive impact and fulfill a meaningful mission. We empower you to unleash your full potential, do your best work, and thrive. Here you will be challenged to stretch yourself to achieve the seemingly impossible.  Learn more about our culture. Diversity, Equity and Inclusion: We're committed to creating an inclusive environment where people from all backgrounds can thrive. We believe that improving diversity, equity and inclusion is our collective responsibility, and this belief guides our DEI journey.  Learn more about our DEI initiatives. Accessibility Accommodations: Should you require any accommodation, we will work with you to meet your needs. Please reach out to talent@benchsci.com. #LI-Remote

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
