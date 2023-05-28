from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Regional Sales Executive, Seattle, WA, YOUR IMPACT  We are looking for experienced regional sales executives with a proven track record of growth in the ediscovery/legal technology industry or Saas/Technology sales. This is a field sales position in major U.S. markets.    Your contribution will accelerate our DISCO growth across both law firms and corporate legal departments in the legal technology space.  You will have the best legal technology tools in your backpack to share with the market.    WHAT YOU'LL DO   * You will sell the DISCO ediscovery, Managed Review, and Case Builder    platforms with responsibility for driving new business logos and expanding    existing client revenue through direct and team selling regionally.   * You’ll create and nurture trusted, long-term relationships with clients that    result in substantial multi-year revenue growth.  * You will relentlessly provide complete and appropriate solutions for all    clients in order to increase top-line revenue growth, client acquisition    levels and overall profitability through sourcing referrals from clients and    prospects and quickly building a local network at the user level to drive    viral growth.  * You will analyze market and territory potential, track sales, and maintain    status reports that deliver upon client needs, issues, interests, competitive    activities, and potential for cross-functional product sales and services.   * You will also keep abreast of best practices and trends in assigned territory    and overall market.   WHO YOU ARE   * Minimum 5 years in a complex selling environment requiring multi-level,    multi-party support to develop and close deals  * Proven track record of success selling in Legal Technology and/or SaaS    environments selling to executive level contacts  * Demonstrated history of overachievement on annual quotas >$1M  * Consistently ranked as a top performer in previous sales roles  * An expert in executing sales fundamentals including prospecting, cold    calling, pipeline and Salesforce management to ensure accurate data capture    and pipeline views  * Innate belief in a metrics driven approach to building a book of business  * Experience working with and developing Sales Development Representatives    (SDRs) to source and nurture leads  * Subject matter expert in the business and practice of law, legal technology,    competitive landscape, and market trends highly preferred   * Solidified commitment to  understand DISCO’s distinct position and    differentiators and our commitment to transforming the manner in which our    clients work  * Adept at partnering and collaborating with colleagues in all departments in    order to exceed client expectations and to secure the resources required to    win  * Ability to adapt, shift, and change quickly while maintaining a high quality    of work and output  * Demonstrate strong interpersonal communication, organization, and are    self-motivated with an entrepreneurial spirit   EDUCATION:   * BA or BS required; JD or MBA a plus, but not required.   LOCATION & TRAVEL:   * DISCO is hiring in all major U.S. cities. Travel as required to clients    within your territory as well as industry events and conferences.  *Business travel to commence based on COVID-19 situation  Perks of DISCO:   * Open, inclusive, and fun environment  * Benefits, including medical, dental and vision insurance, as well as 401(k)   * Competitive salary plus RSUs  * Flexible PTO   * Opportunity to be a part of a company that is revolutionizing the legal    industry  * Growth opportunities throughout the company   ABOUT DISCO  DISCO provides a cloud-native, artificial intelligence-powered legal solution that simplifies ediscovery, legal document review and case management for enterprises, law firms, legal services providers and governments. Our scalable, integrated solution enables legal departments to easily collect, process and review enterprise data that is relevant or potentially relevant to legal matters.   Are you ready to help us fulfill our mission to use technology to strengthen the rule of law? Join us!   We are an equal opportunity employer and value diversity. We do not discriminate on the basis of race, religion, color, national origin, gender, sexual orientation, age, marital status, veteran status, or disability status.  Please note that DISCO has a mandatory COVID vaccination policy which requires all employees in the U.S. to be fully vaccinated, subject to applicable legal exemptions.   

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
