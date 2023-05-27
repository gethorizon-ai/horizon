from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """Sr. Manager, Product Design, Vancouver, BC, About Highspot Highspot helps sales teams improve customer conversations and achieve their revenue goals. From content optimization and performance analytics to in-context training, guided selling, and more, the Highspot platform delivers enterprise-ready features in a modern design that sales reps and marketers love. Using Highspot, marketing leaders have deep insights and analytics into the performance and influenced revenue of content, campaigns, and marketing assets.  What makes the solution special? It’s loved by sales reps globally, and is the #1 rated sales enablement platform on G2 Crowd.    We are committed to diversity as both a moral and business imperative.    Design at Highspot We are a robust centralized design team where all creative functions mingle and have purview across the entire company. Product designers, hyper-focused on delivering a world-class product that reps love, collaborate with visual designers that are always pushing our brand in innovative ways, challenging every pixel. Our digital media designers create compelling story-driven content using critical insights provided by our user experience researchers that allow us to experiment and push for quality over quantity. Our design operations folks remove barriers, enable us to all do our best work, and build connections within and without the team.    Together, we are a team that designs together, one that empowers and lifts each other up, and that fosters trust not only in ourselves but trust in our team. A culture of openness, honesty and the ability to provide and receive constructive feedback are important to us. Communication and collaboration are key.   We also believe that great teams are inclusive in their composition. Being surrounded by a diversity of backgrounds, experiences, and perspectives bring out the best in everyone and lead to higher-quality products and experiences.   About the Role  We are seeking a driven design “conductor” that has that perfect balance of skills to drive the project forward, manage the team to make it happen, and willingness to roll up their sleeves to get those last few pesky pixels into place. This person is experienced with shepherding designs from initial ideation, through rapid iteration, to pixel-perfect implementation. As a seasoned manager, they will have the opportunity to hire senior designers and craft a team of their own.   This candidate should have a passion for usability, an eye for visual consistency, and a knack for reducing the complex to the bare essentials. He or she is an effective diplomat with strong communication and organization skills who is willing to advocate for the design position in the face of senior balancing points from product management and engineering leadership. “World-class” is the bar and this candidate has the desire to take us there! What You'll Do Ability to manage a small team of senior designers to deliver strong work on tight schedulesExperience working across multiple projects at onceIdentify and prioritize usage scenarios through customer research and competitive analysisAnalyze user feedback and activity to develop personasCreate wireframes, storyboards, and screen flowsDesign functional prototypes to prove out interaction modelsStrong partnership with engineering and product management to drive shared vision and execution of product plansDeliver a UX vision, along with a plan for evolutionary, iterative updates, that actualize the larger vision over time Your Background Degree in human-computer interaction, interaction design, visual design, or equivalent work experience8+ years of experience designing world-class experiences2+ years as a manager of multiple designers or leading projectsExpert knowledge of user-centered design principlesDemonstrable fluency with Adobe CC, Sketch, Figma, or equivalent design toolSolid portfolio of work spanning multiple projectsExperience with UX for enterprise software products, channels, or marketplacesExperience or interest in creating style guides, pattern libraries, and other design solutions that drive design across large organizationsExperience working with agile development teams (agile/scrum/kanban)Willingness to roll up the sleeves and lead by example when requiredOutstanding interpersonal, written, and verbal communication skillsExcellent collaborative skills Benefits Section Comprehensive medical, dental, vision, disability, and life benefits Group Retirement Savings Plan (RRSP) and matching employer contributions (DPSP) with immediate vesting 3 Weeks of Paid Vacation Generous Holiday Schedule + 5 Days for Annual Holiday Week Recharge Fridays (company wide mental health days) Flexible work schedules Professional development opportunities through BetterUp and LinkedIn Learning Discounted ClassPass membership Access to Coaches and Therapists through Modern Health 2 Volunteer days per year Equal Opportunity Statement We are an equal opportunity employer and value diversity at our company. We do not discriminate on the basis of any grounds protected by applicable human rights legislation, which may include age, ancestry, citizenship, color, ethnicity, family status, gender identity or expression, genetic information, marital status, medical condition, national origin, physical or invisible disabilities, political belief, race, religion, or sexual orientation. Did you read the requirements as a checklist and not tick every box? Don't rule yourself out! If this role resonates with you, hit the ‘apply’ button."""

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
