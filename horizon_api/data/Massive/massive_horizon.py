from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Staff Engineer, Data (Remote), Vancouver, British Columbia, We are looking for a Staff Engineer to join our growing Engineering Team. You will work with key technical team members across the organization to ensure that BenchSci's technical infrastructure and codebase will support long-term growth. Reporting to the Director of Engineering, you will provide technical leadership across several functional areas within the team, lead complex projects, participate in roadmap and project planning, and contribute to BenchSci's data engineering and architecture initiatives. The Staff Engineer will help foster the development of other individual contributors, while also playing an important role in helping us scale as we continue to improve scientific discovery.   BenchSci is a remote-first organization. At this moment, we are welcoming applicants from Canada, the US and the UK for this position.  You Will: Collaborate with multiple teams working on key customer features and our own internal development projectsContribute to setting technical and architectural direction for our Data Engineering teams with a focus on expanding the scope of our products and our ability to make life scientists more effectiveDrive the architecture of BenchSci to help us handle data more securelyDecouple work done by teams to allow for more independent work and smaller feature releasesBe involved in all aspects of software development, working to create and maintain the most reliable, secure, performant and high throughput service for our customers by using the latest cloud technology (this can range from setting high-level technical direction down to implementation)Be an inspiring mentor to other engineersBe an advocate for us and its engineering team through several channels You Have: 8+ years of professional development experience, with 2+ years at the Staff levelExpertise in data management practices, including approaches to capturing provenance, versioning, and disaster recoveryExperience working with secure data, including compliance with regulations like HIPAA and GDPRExpertise with data processing engines such as Apache BeamExperience working with SaaS products in a fast-paced Agile environmentThe ability to lead the engineering team toward the decisions they make while minimizing frictionThe ability to translate business concerns into technical implementationsExperience with mentoring technical teamsExperience with big dataThe ability to communicate trade-offs in approaches to security, speed to ship, and performanceDomain expertise in either machine learning, distributed systems, data engineering, or cloud infrastructureThe ability to provide constructive feedback to other individual contributors while showing a sense of empathy, tact, thoughtfulness and respect Benefits and Perks:  An engaging remote-first culture  A great compensation package that includes BenchSci equity options 15 days vacation plus an additional day every year; plus company closures for 15 more days throughout the year Unlimited flex time for sick days, personal days, religious holidays Comprehensive health and dental benefits Emphasis on mental health with $2500 CAD* for Psychologist, Social Worker, or Psychotherapist services A $2000 CAD* Annual Learning & Development budget A $1000 CAD*  home office set-up budget A $2500 CAD*wellness, lifestyle and productivity spending account for employees   Generous parental leave benefits with a top-up plan or paid time off options *Benefits are tied to Canadian dollar amounts and would be converted to local currency for those in other countries. Moving to local currency allotments in the future. About BenchSci: BenchSci's vision is to help scientists bring novel medicine to patients 50% faster by 2025. We empower scientists to run more successful experiments with the world's most advanced, biomedical artificial intelligence software platform.  Backed by F-Prime, Inovia, Golden Ventures, and Google's AI fund, Gradient Ventures, we provide an indispensable tool for scientists that accelerates research at 16 top 20 pharmaceutical companies and over 4,300 leading academic centers. We're a certified Great Place to Work®, and top-ranked company on Glassdoor. Our Culture: BenchSci relentlessly builds on its strong foundation of culture. We put team members first, knowing that they're the organization's beating heart. We invest as much in our people as our products. Our culture fosters transparency, collaboration, and continuous learning.  We value each other's differences and always look for opportunities to embed equity into the fabric of our work. We foster diversity, autonomy, and personal growth, and provide resources to support motivated self-leaders in continuous improvement.  You will work with high-impact, highly skilled, and intelligent experts motivated to drive impact and fulfill a meaningful mission. We empower you to unleash your full potential, do your best work, and thrive. Here you will be challenged to stretch yourself to achieve the seemingly impossible.  Learn more about our culture. Diversity, Equity and Inclusion: We're committed to creating an inclusive environment where people from all backgrounds can thrive. We believe that improving diversity, equity and inclusion is our collective responsibility, and this belief guides our DEI journey.  Learn more about our DEI initiatives. Accessibility Accommodations: Should you require any accommodation, we will work with you to meet your needs. Please reach out to talent@benchsci.com. #LI-Remote

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
