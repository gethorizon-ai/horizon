from config import Config
import horizon_ai
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

horizon_ai.api_key = "83efb517-66cf-47e7-9318-707f9c13903e"
horizon_ai.openai_api_key = Config.HORIZON_OPENAI_API_KEY

test_job_listing = """QA Manager, BLANK,BLANK,Multiple Locations, WHAT MAKES US EPIC?  At the core of Epic’s success are talented, passionate people. Epic prides itself on creating a collaborative, welcoming, and creative environment. Whether it’s building award-winning games or crafting engine technology that enables others to make visually stunning interactive experiences, we’re always innovating.  Being Epic means being a part of a team that continually strives to do right by our community and users. We’re constantly innovating to raise the bar of engine and game development.  QA at Epic  What we do  The Online team at Epic Games is developing an innovative platform which provides tools and services with world-class features and scalability to developers and gamers. We’re making it easier and faster for developers to successfully launch, operate, and scale high-quality games. As a game developer ourselves, we understand how to tackle hard problems and are sharing the fruits of our labor with others in the development community.   Like what you hear? Come be a part of something Epic.  What you’ll do  Epic Games is looking for an experienced Technical QA Manager. This position will be responsible for the quality of multiple features supporting our Epic Online Services SDK. They will be leading a small, agile QA team embedded in our team of back-end and SDK engineers. If you're excited about working in a fast-paced environment and are highly motivated to ensure the best possible user experience, then we'd like to speak with you!  In this role, you will   * Working with product owners and developers to define acceptance criteria,    identify risks, and plan testing coverage for upcoming features/web releases   * Coordinating test efforts between geographically distributed teams, vendors    and agencies to deliver the highest quality product  * Managing test plans/test suites in a dynamic and fast-paced environment  * Managing compatibility testing efforts of the SDK across multiple platforms  * Analyzing and troubleshooting reported defects and internal issues  * Develop major testing initiatives using a combination of process, people, and    effective testing methodologies  * Ensuring that automation efforts are moving forward effectively and    efficiently  * Lead and grow a quality assurance team as both a people manager and a    tactical driver of success, with the ability to contribute to day-to-day    efforts as needed  What we’re looking for    * 7+ years of Software Quality Assurance experience  * Technical Background - not just a person leader; Able to contribute to    day-to-day testing/engineering efforts  * Experience working with and testing for multiple Platforms (Desktop, Mobile,    Consoles)  * Experience working with Unreal Engine or other Game Engines is preferred but    not required  * A deep understanding of defect reporting, version control, and configuration    management best practices, along with different testing phase best practices    and objectives (functional, system integration, UAT, performance)  * General experience with automation best practices and development tools; Unit    and Integration testing of APIs  * Solid understanding of testing APIs at both a client/sdk level and how they    interact with backend services  * Ability to prioritize and work independently, as well as in a team    environment  * Ability to thrive while working in a fast-paced working environment, with the    ability to juggle multiple projects  This position is open in multiple locations across North America and Europe including (but not limited to): Vancouver, Canada Toronto, Canada Boston, MA Salt Lake City, UT ...and many more.   ABOUT US  Epic Games spans across 19 countries with 55 studios and 4,500+ employees globally. For over 25 years, we’ve been making award-winning games and engine technology that empowers others to make visually stunning games and 3D content that bring environments to life like never before. Epic’s award-winning Unreal Engine technology not only provides game developers the ability to build high-fidelity, interactive experiences for PC, console, mobile, and VR, it is also a tool being embraced by content creators across a variety of industries such as media and entertainment, automotive, and architectural design. As we continue to build our Engine technology and develop remarkable games, we strive to build teams of world-class talent.   LIKE WHAT YOU HEAR? COME BE A PART OF SOMETHING EPIC!  Epic Games deeply values diverse teams and an inclusive work culture, and we are proud to be an Equal Opportunity employer. Learn more about our Equal Employment Opportunity (EEO) Policy here [https://www.epicgames.com/site/en-US/eeo-policy].

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
