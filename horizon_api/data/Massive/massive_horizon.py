from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Sr. Design Validation Test Engineer, Newark, CA, Leading the future in luxury electric and mobility At Lucid, we set out to introduce the most captivating, luxury electric vehicles that elevate the human experience and transcend the perceived limitations of space, performance, and intelligence. Vehicles that are intuitive, liberating, and designed for the future of mobility.   We plan to lead in this new era of luxury electric by returning to the fundamentals of great design – where every decision we make is in service of the individual and environment. Because when you are no longer bound by convention, you are free to define your own experience.   Come work alongside some of the most accomplished minds in the industry. Beyond providing competitive salaries, we’re providing a community for innovators who want to make an immediate and significant impact. If you are driven to create a better, more sustainable future, then this is the right place for you.   We are currently seeking a Sr Design Validation Test Engineer for our Low Voltage team.  This position requires an experienced professional to work directly with the Infotainment Test & Validation team to accomplish DVP on time. Our ideal candidate exhibits a can-do attitude and approaches his or her work with vigor and determination. Candidates will be expected to demonstrate excellence in their respective fields, to possess the ability to learn quickly and to strive for perfection within a fast-paced environment. The Role: Report to the Test and Validation team and will be responsible for developing the test plan, component level test (DVT) and setting up, testing and reporting all the results to the infotainment and Controls teams. Qualifications: Collaborate with HW Design Engineers to develop and execute hardware verification test plans HW Design Validation and functional testingDesign, build and program test systems used in HW testing as well generate automated reports tracking test resultsUpload test setups, test plans and results into confluence and JIRACreate test sequences to verify performance and limitations of ECUsContribute with design team to resolve problems and develop corrective actionAnalyzes test results and test data to determine if design meets functional and performance specificationsResearch advanced measurement techniquesPrototyping EOLAt least 5 years of experience in HW testing (Automotive is a plus) Advantageous Skills and Experience: Extensive experience in testing of Digital and Analog/Mixed signal circuitsExperience with LV124 automotive test standards and executionExperience using RTStand LV124, spectrum analyzers, high-speed oscilloscopes, signal generators, arbitrary waveform generators.Ability to generate tests cases to validate product requirementsExperience designing and analyzing test procedures to minimize measurement errorKnowledge of industrial controls systems and their communications interfaces and protocols such as Ethernet/IPExperience with measurement automation tools and scripting languages such as, Python and LabVIEWFamiliarity and experience working with Gigabit Ethernet, WIFI, BT, FPD link, CAN, SPI, I2C, LIN, RS232Knowledge of EMC/EMI Education Requirements: Bachelor’s Degree in Electrical Engineering (MS preferred) Salary Range: The compensation range for this position is specific to the locations listed below and is the range Lucid reasonably and in good faith expects to pay for the position taking into account the wide variety of factors that are considered in making compensation decisions, including job-related knowledge; skillset; experience, education and training; certifications; and other relevant business and organizational factors. California (Bay Area) - $115,000 - $165,000 At Lucid, we don’t just welcome diversity - we celebrate it! Lucid Motors is proud to be an equal opportunity workplace. We are committed to equal employment opportunity regardless of race, color, national or ethnic origin, age, religion, disability, sexual orientation, gender, gender identity and expression, marital status, and any other characteristic protected under applicable State or Federal laws and regulations. Notice regarding COVID-19 protocols   At Lucid, we prioritize the health and wellbeing of our employees, families, and friends above all else. In response to the novel Coronavirus all new Lucid employees, whose job will be based in the United States may or may not be required to provide original documentation confirming status as having received the prescribed inoculation (doses). Vaccination requirements are dependent upon location and position, please refer to the job description for more details.   Individuals in positions requiring vaccinations may seek a medical and/or religious exemption from this requirement and may be granted such an accommodation after submitting a formal request to and the subsequent review and approval thereof by our dedicated Covid-19 Response team.   To all recruitment agencies: Lucid Motors does not accept agency resumes. Please do not forward resumes to our careers alias or other Lucid Motors employees. Lucid Motors is not responsible for any fees related to unsolicited resumes.

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
