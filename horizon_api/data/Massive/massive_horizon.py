from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Customer Success Manager North America (based in the US), US, Our story so far...   Pigment’s mission is to enable people and businesses to make better decisions.   Founded in 2019 by Romain Niccoli (ex founder and CTO of Criteo) and Eléonore Crespo (Index Ventures and Google), Pigment is a fast-growing international scale-up that raised over $160M+ to become the central business planning solution powering Finance, HR, Sales, and Marketing decisions.   We serve fast-growing companies including Gong, Carta, BlaBlaCar, Ledger, Deliveroo, Brex, Melio, and Spendesk to name a few!   Pigment is remote friendly and has offices in Paris, London and NYC.   What we do   Pigment is a SaaS planning platform that enables any business to play with business data in a safe, fun and collaborative environment.   It is an intuitive platform, which anyone can use and understand, that allows leaders and teams to analyze all of their business data better and anticipate the impact of their decisions with unprecedented speed and flexibility.   Join a forward-thinking team (from Meta, Google, Criteo, Datadog and others) that likes to move fast, work smart and solve big challenges as a team on this exciting journey!   What you'll do Manage and maintain customers relationships, ensuring that all customers attain a high level of adoption and business value from using PigmentManage customer implementations of Pigment, ensuring that customers understand the platform's value and attain a high level of adoptionDevelop a trusted advisor relationship with customer executive sponsors to create passion and satisfaction for PigmentEstablish measurable goals and KPIs for your customer accounts and drive a plan to completionNavigate through multiple departments within an organisation to expand use cases and business value of PigmentDeliver awe-inspiring presentations and trainings, provide insightful practices and structure creative solutionLead the development of the Pigment community though thought leadership, events, and developing practicesDevelop deep product expertise and creativity to work closely with our product team on the product vision and roadmap Who you are Significant experience in account management, sales or professional services at a software/SaaS companyProven track record of building strong C-level executive relationships, a deep sense of empathy and dedicationExperience in preparing and delivering presentations targeted to a senior audienceAbility to explain technical solutions, establish goals, develop opportunities, and provide reporting/dashboards to identify trends and improve the customer experienceExperience deploying SaaS platforms across enterprise organizations and driving long-term engagementStrategic thinker who is comfortable in a fast-paced, always-on, highly ambiguous start-up environmentAbility to adapt to a rapidly changing product and respond strategically to customer needsExperience meeting multiple objectives in an entrepreneurial environment with little supervisionYou speak English fluentlyBA/BS degree required, MBA or other relevant advanced degree preferred What we offer Competitive packageEquityBrand new offices in the heart of Paris, London and New YorkRemote-friendly policyAnnual offsite Pigment is an equal opportunity employer. We believe diversity is a strength and fosters innovation. We are committed to enabling everyone to feel included and valued at the workplace.  All qualified applicants will receive consideration for employment without regard to age, color, family, gender identity, marital status, national origin, physical or mental disability,  sex (including pregnancy), sexual orientation, or any other characteristic protected by applicable laws.

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
