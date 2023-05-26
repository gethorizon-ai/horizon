import horizon_ai
from config import Config
import json

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Operations Manager, Change Management, Swedesboro, NJ, At HelloFresh, we want to change the way people eat forever by offering our customers high quality food and recipes for different meal occasions. Over the past 10 years, we've seen this mission spread around the world and beyond our wildest dreams. Now, we are a global food solutions group and the world's leading meal kit company, active in 18 countries across 3 continents. So, how did we do it? Our weekly boxes full of exciting recipes and fresh ingredients have blossomed into a community of customers looking for delicious, healthy and sustainable options. The HelloFresh Group now includes our core brand, HelloFresh, as well as: Green Chef, EveryPlate, Chefs Plate, Factor_, and Youfoodz.  Operations Change Manager  . Summary/Objective: The Operational Excellence (OpEX) team is constructing a foundational, scalable, and agile operations platform for HelloFresh that supports market share growth and enables best-in-class customer experience. As the Continuous Improvement Manager, OpEX, you support the OpEX team in deployment and standardization for benchmark performance across all Distribution Center processes. You will accelerate the implementation of technological advancements and contribute to the technical and process knowledge of the operational leaders across FC network. The Continuous Improvement Manager identifies opportunities in standards and execution and ensures appropriate root cause analysis improvement methodologies are implemented. You will support the overall OpEX strategy and measure the adoption of tools and techniques being leveraged to drive improvements and standardize processes throughout the value stream. You will work closely with local and network planning, launch teams, automation and engineering, and maintenance, reliability, and engineering (M&RE) teams to improve the critical input metrics for the DC by prioritizing and channeling resources to address gaps in these inputs. Essential Functions ·       Act as an expert in standard operating plans and processes across the DC ·       Train and keep alignment on best practices and benchmark standard practices ·       Support OpEX Product owners in creating and refining processes ·       Support the DC operations leaders in process deep dives and root cause analysis ·       On site support of continuous improvement and feedback mechanism for leaders in the DC network ·       Collect, consolidate, and perform initial prioritization of the flow of ideas escalated by DC Leaders ·       Network POC for all on site changes and adoptions of new technology and processes ·       Scope and create on site rollout for network products, and initiatives   Competencies ●      Leadership    ●      Time Management      ●      Respectful Coaching Techniques   ●      Thoroughness ●      Performance Management of team members ●      Detail Oriented and Results Driven ●      Conflict Resolution ●      Cross functional collaboration ●      Selection and Interviewing skills           Required Education and Experience ●      Bachelor’s degree or related management work experience. ●      At least 2 years of work experience in a production environment ●      Relevant knowledge of change management and continuous improvement methodologies Preferred Education and Experience ●      At least 3 years of work experience in a production environment, specifically targeted towards continuous improvement ●      Strong ability interpreting and communicating analytics and presenting to senior leaders   ABOUT HELLOFRESH  We believe that sharing a meal brings people of all identities, backgrounds, and cultures together. We are committed to celebrating all dimensions of diversity in the workplace equally and ensuring that everyone feels a sense of inclusion and belonging. We also aim to extend this commitment to the partners we work with and the communities we serve. We are constantly listening, learning, and evolving to deliver on these principles. We are proud of our collaborative culture. Our diverse employee population enables us to connect with our customers and turn their feedback into meaningful action - from developing new recipes to constantly improving our process of getting dinner to our customers’ homes. Our culture attracts top talent with shared values and forms the foundation for a great place to work!  At HelloFresh, we embrace diversity and inclusion. We are an equal opportunity employer and do not discriminate on the basis of an individual's race, national origin, color, gender, gender identity, gender expression, sexual orientation, religion, age, disability, marital status or any other protected characteristic under applicable law, whether actual or perceived. As part of the Company’s commitment to equal employment opportunity, we provide reasonable accommodations, up to the point of undue hardship, to candidates at any stage, including to individuals with disabilities.  We want to adapt our processes and create a safe space that welcomes everyone so please let us know how we can accommodate our process. In case you have any accessibility requirements you can share that with us in the application form.  To learn more about what it's like working inside HelloFresh, follow us on Instagram [https://www.instagram.com/insidehellofresh/] and LinkedIn [https://www.linkedin.com/company/hellofresh]

###"""
inputs = {"input_data": test_job_listing}
result = {}

title = json.loads(
    horizon_ai.deploy_task(task_id=215, inputs=inputs, log_deployment=True)
)["completion"]
result.update(title)

sub_role = json.loads(
    horizon_ai.deploy_task(task_id=216, inputs=inputs, log_deployment=True)
)["completion"]
result.update(sub_role)

tenure = json.loads(
    horizon_ai.deploy_task(task_id=216, inputs=inputs, log_deployment=True)
)["completion"]
result.update(tenure)

locations = json.loads(
    horizon_ai.deploy_task(task_id=224, inputs=inputs, log_deployment=True)
)["completion"]
result.update(locations)

pay_min = json.loads(
    horizon_ai.deploy_task(task_id=222, inputs=inputs, log_deployment=True)
)["completion"]
result.update(pay_min)

pay_max = json.loads(
    horizon_ai.deploy_task(task_id=223, inputs=inputs, log_deployment=True)
)["completion"]
result.update(pay_max)

responsibility = json.loads(
    horizon_ai.deploy_task(task_id=214, inputs=inputs, log_deployment=True)
)["completion"]
result.update(responsibility)

print(json.dumps(result, indent=4))
