import { Box, Container, Typography } from "@mui/material";
import HorizonAppBar from "../../components/HorizonAppBar";
import { useEffect, useState } from "react";
import { Auth } from "aws-amplify";

const initialState = {
    user: undefined,
    isLoggedIn: false,
    loading: true
};

function PrivacyPolicyPage() {
    const [state, setState] = useState(initialState);
    useEffect(() => {
        async function checkUser() {
            await Auth.currentAuthenticatedUser({
                bypassCache: false
            }).then(user => {
                setState({
                    ...initialState,
                    user: user,
                    isLoggedIn: true,
                    loading: false
                });
                console.log(user)
            }).catch(err => {
                console.log(err);
                setState({
                    ...initialState,
                    user: undefined,
                    isLoggedIn: false,
                    loading: false
                });
            });
        }
        checkUser();
    }, []);

    const signOut = async () => {
        try {
            await Auth.signOut({ global: true });
            setState({ ...initialState, loading: false });
        } catch (error) {
            console.log('error signing out: ', error);
        }
    }

    if (state.loading) {
        return (<div className="main-box">
            <HorizonAppBar />
            <p>Loading...</p>
        </div>)
    }
    return (
        <Box>
            <HorizonAppBar user={state.user} signOut={signOut} />
            <Box component="main" sx={{ flexGrow: 1, mt: 3 }}>
                <Container maxWidth="xl">
                    <Typography variant="h4" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Horizon AI Privacy Policy
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Horizon AI may collect some Personal Data from its Users.<br />
                        This document contains a section dedicated to Californian consumers and their privacy rights.<br />
                        This document can be printed for reference by using the print command in the settings of any browser.<br />
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Owner and Data Controller
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Please email the company for details.<br />
                        Owner contact email: team@gethorizon.ai
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Types of Data collected
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Among the types of Personal Data that Horizon AI collects, by itself or through third parties, there are: first name; last name; Usage Data; email address.<br />
                        Complete details on each type of Personal Data collected are provided in the dedicated sections of this privacy policy or by specific explanation texts displayed prior to the Data collection.
                        Personal Data may be freely provided by the User, or, in case of Usage Data, collected automatically when using Horizon AI.<br />
                        Unless specified otherwise, all Data requested by Horizon AI is mandatory and failure to provide this Data may make it impossible for Horizon AI to provide its services. In cases where Horizon AI specifically states that some Data is not mandatory, Users are free not to communicate this Data without consequences to the availability or the functioning of the Service.<br />
                        Users who are uncertain about which Personal Data is mandatory are welcome to contact the Owner.
                        Any use of Cookies - or of other tracking tools - by Horizon AI or by the owners of third-party services used by Horizon AI serves the purpose of providing the Service required by the User, in addition to any other purposes described in the present document and in the Cookie Policy, if available.<br />
                        Users are responsible for any third-party Personal Data obtained, published or shared through Horizon AI and confirm that they have the third party's consent to provide the Data to the Owner.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Mode and place of processing the Data
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Methods of processing
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner takes appropriate security measures to prevent unauthorized access, disclosure, modification, or unauthorized destruction of the Data.<br />
                        The Data processing is carried out using computers and/or IT enabled tools, following organizational procedures and modes strictly related to the purposes indicated. In addition to the Owner, in some cases, the Data may be accessible to certain types of persons in charge, involved with the operation of Horizon AI (administration, sales, marketing, legal, system administration) or external parties (such as third-party technical service providers, mail carriers, hosting providers, IT companies, communications agencies) appointed, if necessary, as Data Processors by the Owner. The updated list of these parties may be requested from the Owner at any time.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Legal basis of processing
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Owner may process Personal Data relating to Users if one of the following applies:<br />
                        - Users have given their consent for one or more specific purposes. Note: Under some legislations the Owner may be allowed to process Personal Data until the User objects to such processing (“opt-out”), without having to rely on consent or any other of the following legal bases. This, however, does not apply, whenever the processing of Personal Data is subject to European data protection law;<br />
                        - Provision of Data is necessary for the performance of an agreement with the User and/or for any pre-contractual obligations thereof;<br />
                        - Processing is necessary for compliance with a legal obligation to which the Owner is subject;<br />
                        - Processing is related to a task that is carried out in the public interest or in the exercise of official authority vested in the Owner;<br />
                        - Processing is necessary for the purposes of the legitimate interests pursued by the Owner or by a third party.<br />
                        In any case, the Owner will gladly help to clarify the specific legal basis that applies to the processing, and in particular whether the provision of Personal Data is a statutory or contractual requirement, or a requirement necessary to enter into a contract.<br />
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Place
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Data is processed at the Owner's operating offices and in any other places where the parties involved in the processing are located.<br />
                        Depending on the User's location, data transfers may involve transferring the User's Data to a country other than their own. To find out more about the place of processing of such transferred Data, Users can check the section containing details about the processing of Personal Data.<br />
                        Users are also entitled to learn about the legal basis of Data transfers to a country outside the European Union or to any international organization governed by public international law or set up by two or more countries, such as the UN, and about the security measures taken by the Owner to safeguard their Data.<br />
                        If any such transfer takes place, Users can find out more by checking the relevant sections of this document or inquire with the Owner using the information provided in the contact section.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Retention time
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Personal Data shall be processed and stored for as long as required by the purpose they have been collected for.<br />
                        Therefore:<br />
                        - Personal Data collected for purposes related to the performance of a contract between the Owner and the User shall be retained until such contract has been fully performed.<br />
                        - Personal Data collected for the purposes of the Owner’s legitimate interests shall be retained as long as needed to fulfill such purposes. Users may find specific information regarding the legitimate interests pursued by the Owner within the relevant sections of this document or by contacting the Owner.<br />
                        The Owner may be allowed to retain Personal Data for a longer period as it deems necessary, as long as such consent is not withdrawn. Furthermore, the Owner may be obliged to retain Personal Data for a longer period whenever required to do so for the performance of a legal obligation or upon order of an authority.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        The purposes of processing
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The Data concerning the User is collected to allow the Owner to provide its Service, comply with its legal obligations, respond to enforcement requests, protect its rights and interests (or those of its Users or third parties), detect any malicious or fraudulent activity, as well as the following: Contacting the User, Analytics, Interaction with external social networks and platforms, Interaction with data collection platforms and other third parties and SPAM protection.<br />
                        For specific information about the Personal Data used for each purpose, the User may refer to the section “Detailed information on the processing of Personal Data”.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Detailed information on the processing of Personal Data
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Personal Data is collected for the following purposes and using the following services:
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Analytics
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        The services contained in this section enable the Owner to monitor and analyze web traffic and can be used to keep track of User behavior. They include, but are not limited to, the following:
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Google Analytics (Google LLC)
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Google Analytics is a web analysis service provided by Google LLC (“Google”). Google utilizes the Data collected to track and examine the use of Horizon AI, to prepare reports on its activities and share them with other Google services.<br />
                        Google may use the Data collected to contextualize and personalize the ads of its own advertising network.
                        Personal Data processed: Cookies; Usage Data.<br />
                        Place of processing: United States - <a href="https://policies.google.com/privacy">Privacy Policy</a> - <a href="https://tools.google.com/dlpage/gaoptout?hl=en">Opt Out</a>.<br />
                        Category of personal data collected according to CCPA: internet information.<br />
                        This processing constitutes a sale based on the definition under the CCPA. In addition to the information in this clause, the User can find information regarding how to opt out of the sale in the section detailing the rights of Californian consumers.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Heap Analytics (Heap Inc.)
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Heap Analytics is an analytics service provided by Heap Inc., that allows the Owner to analyze revenue and Users' (commercial) activity on Horizon AI.<br />
                        Personal Data processed: financial information; Tracker; Usage Data.<br />
                        Place of processing: United States - <a href="https://heap.io/privacy">Privacy Policy</a>.<br />
                        Category of personal information collected according to CCPA: California Consumer Records Statute information.<br />
                        This processing constitutes a sale based on the definition under the CCPA. In addition to the information in this clause, the User can find information regarding how to opt out of the sale in the section detailing the rights of Californian consumers.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Displaying content from external platforms
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        This type of service allows you to view content hosted on external platforms directly from the pages of Horizon AI and interact with them.<br />
                        This type of service might still collect web traffic data for the pages where the service is installed, even when Users do not use it.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Contacting the User
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Contact form (Horizon AI)<br />
                        By filling in the contact form with their Data, the User authorizes Horizon AI to use these details to reply to requests for information, quotes or any other kind of request as indicated by the form’s header.
                        Personal Data processed: company name; first name; last name.
                        Category of personal data collected according to CCPA: identifiers; commercial information.<br />
                        This type of service allows interaction with social networks or other external platforms directly from the pages of Horizon AI.<br />
                        The interaction and information obtained through Horizon AI are always subject to the User’s privacy settings for each social network.<br />
                        This type of service might still collect traffic data for the pages where the service is installed, even when Users do not use it.<br />
                        It is recommended to log out from the respective services in order to make sure that the processed data on Horizon AI isn't being connected back to the User's profile.<br />
                        This type of service allows Users to interact with data collection platforms or other services directly from the pages of Horizon AI for the purpose of saving and reusing data.<br />
                        If one of these services is installed, it may collect browsing and Usage Data in the pages where it is installed, even if the Users do not actively use the service.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        SPAM protection
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        This type of service analyzes the traffic of Horizon AI, potentially containing Users' Personal Data, with the purpose of filtering it from parts of traffic, messages and content that are recognized as SPAM.<br />
                        Google reCAPTCHA (Google LLC)<br />
                        Google reCAPTCHA is a SPAM protection service provided by Google LLC.<br />
                        The use of reCAPTCHA is subject to the Google <a href="https://www.google.com/policies/privacy/">privacy policy</a> and <a href="https://www.google.com/intl/en/policies/terms/">terms of use</a>.<br />
                        Personal Data processed: Cookies; Usage Data.<br />
                        Place of processing: United States - <a href="https://policies.google.com/privacy">Privacy Policy</a>.<br />
                        Category of personal data collected according to CCPA: internet information.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        The rights of Users
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Users may exercise certain rights regarding their Data processed by the Owner.<br />
                        In particular, Users have the right to do the following:<br />
                        - Withdraw their consent at any time. Users have the right to withdraw consent where they have previously given their consent to the processing of their Personal Data.<br />
                        - Object to processing of their Data. Users have the right to object to the processing of their Data if the processing is carried out on a legal basis other than consent. Further details are provided in the dedicated section below.<br />
                        - Access their Data. Users have the right to learn if Data is being processed by the Owner, obtain disclosure regarding certain aspects of the processing and obtain a copy of the Data undergoing processing.<br />
                        - Verify and seek rectification. Users have the right to verify the accuracy of their Data and ask for it to be updated or corrected.<br />
                        - Restrict the processing of their Data. Users have the right, under certain circumstances, to restrict the processing of their Data. In this case, the Owner will not process their Data for any purpose other than storing it.<br />
                        - Have their Personal Data deleted or otherwise removed. Users have the right, under certain circumstances, to obtain the erasure of their Data from the Owner.<br />
                        - Receive their Data and have it transferred to another controller. Users have the right to receive their Data in a structured, commonly used and machine readable format and, if technically feasible, to have it transmitted to another controller without any hindrance. This provision is applicable provided that the Data is processed by automated means and that the processing is based on the User's consent, on a contract which the User is part of or on pre-contractual obligations thereof.<br />
                        - Lodge a complaint. Users have the right to bring a claim before their competent data protection authority.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Details about the right to object to processing
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        Where Personal Data is processed for a public interest, in the exercise of an official authority vested in the Owner or for the purposes of the legitimate interests pursued by the Owner, Users may object to such processing by providing a ground related to their particular situation to justify the objection.<br />
                        Users must know that, however, should their Personal Data be processed for direct marketing purposes, they can object to that processing at any time without providing any justification. To learn, whether the Owner is processing Personal Data for direct marketing purposes, Users may refer to the relevant sections of this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        How to exercise these rights
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        Any requests to exercise User rights can be directed to the Owner through the contact details provided in this document. These requests can be exercised free of charge and will be addressed by the Owner as early as possible and always within one month.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Cookie Policy
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        Horizon AI may use Trackers.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Additional information about Data collection and processing
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Legal action
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        The User's Personal Data may be used for legal purposes by the Owner in Court or in the stages leading to possible legal action arising from improper use of Horizon AI or the related Services.<br />
                        The User declares to be aware that the Owner may be required to reveal personal data upon request of public authorities.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Additional information about User's Personal Data
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        In addition to the information contained in this privacy policy, Horizon AI may provide the User with additional and contextual information concerning particular Services or the collection and processing of Personal Data upon request.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        System logs and maintenance
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        For operation and maintenance purposes, Horizon AI and any third-party services may collect files that record interaction with Horizon AI (System logs) use other Personal Data (such as the IP Address) for this purpose.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Information not contained in this policy
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        More details concerning the collection or processing of Personal Data may be requested from the Owner at any time. Please see the contact information at the beginning of this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        How “Do Not Track” requests are handled
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        Horizon AI does not support “Do Not Track” requests.<br />
                        To determine whether any of the third-party services it uses honor the “Do Not Track” requests, please read their privacy policies.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Changes to this privacy policy
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        The Owner reserves the right to make changes to this privacy policy at any time by notifying its Users on this page and possibly within Horizon AI and/or - as far as technically and legally feasible - sending a notice to Users via any contact information available to the Owner. It is strongly recommended to check this page often, referring to the date of the last modification listed at the bottom.<br />
                        Should the changes affect processing activities performed on the basis of the User's consent, the Owner shall collect new consent from the User, where required.
                    </Typography>
                    <Typography variant="h5" align="left" sx={{ mb: 2 }}>
                        Information for Californian consumers
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        This part of the document integrates with and supplements the information contained in the rest of the privacy policy and is provided by the business running Horizon AI and, if the case may be, its parent, subsidiaries and affiliates (for the purposes of this section referred to collectively as “we”, “us”, “our”).<br />
                        The provisions contained in this section apply to all Users who are consumers residing in the state of California, United States of America, according to "The California Consumer Privacy Act of 2018" (Users are referred to below, simply as “you”, “your”, “yours”), and, for such consumers, these provisions supersede any other possibly divergent or conflicting provisions contained in the privacy policy.<br />
                        This part of the document uses the term “personal information“ as it is defined in The California Consumer Privacy Act (CCPA).
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Categories of personal information collected, disclosed or sold
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        In this section we summarize the categories of personal information that we've collected, disclosed or sold and the purposes thereof. You can read about these activities in detail in the section titled “Detailed information on the processing of Personal Data” within this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Information we collect: the categories of personal information we collect
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        We have collected the following categories of personal information about you: identifiers, commercial information and internet information.<br />
                        We will not collect additional categories of personal information without notifying you.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        How we collect information: what are the sources of the personal information we collect?
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        We collect the above mentioned categories of personal information, either directly or indirectly, from you when you use Horizon AI.<br />
                        For example, you directly provide your personal information when you submit requests via any forms on Horizon AI. You also provide personal information indirectly when you navigate Horizon AI, as personal information about you is automatically observed and collected. Finally, we may collect your personal information from third parties that work with us in connection with the Service or with the functioning of Horizon AI and features thereof.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        How we use the information we collect: sharing and disclosing of your personal information with third parties for a business purpose
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        We may disclose the personal information we collect about you to a third party for business purposes. In this case, we enter a written agreement with such third party that requires the recipient to both keep the personal information confidential and not use it for any purpose(s) other than those necessary for the performance of the agreement.<br />
                        We may also disclose your personal information to third parties when you explicitly ask or authorize us to do so, in order to provide you with our Service.<br />
                        To find out more about the purposes of processing, please refer to the relevant section of this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Sale of your personal information
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        For our purposes, the word “sale” means any “selling, renting, releasing, disclosing, disseminating, making available, transferring or otherwise communicating orally, in writing, or by electronic means, a consumer's personal information by the business to another business or a third party, for monetary or other valuable consideration”.<br />
                        This means that, for example, a sale can happen whenever an application runs ads, or makes statistical analyses on the traffic or views, or simply because it uses tools such as social network plugins and the like.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Your right to opt out of the sale of personal information
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        You have the right to opt out of the sale of your personal information. This means that whenever you request us to stop selling your data, we will abide by your request.<br />
                        Such requests can be made freely, at any time, without submitting any verifiable request, simply by following the instructions below.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Instructions to opt out of the sale of personal information
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        If you'd like to know more, or exercise your right to opt out in regard to all the sales carried out by Horizon AI, both online and offline, you can contact us for further information using the contact details provided in this document.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        What are the purposes for which we use your personal information?
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        We may use your personal information to allow the operational functioning of Horizon AI and features thereof (“business purposes”). In such cases, your personal information will be processed in a fashion necessary and proportionate to the business purpose for which it was collected, and strictly within the limits of compatible operational purposes.<br />
                        We may also use your personal information for other reasons such as for commercial purposes (as indicated within the section “Detailed information on the processing of Personal Data” within this document), as well as for complying with the law and defending our rights before the competent authorities where our rights and interests are threatened or we suffer an actual damage.<br />
                        We will not use your personal information for different, unrelated, or incompatible purposes without notifying you.
                    </Typography>
                    <Typography variant="h6" align="left" sx={{ mb: 2 }}>
                        Your California privacy rights and how to exercise them
                    </Typography>
                    <Typography variant="body1" align="left" sx={{ mb: 2 }}>
                        The right to know and to portability<br />
                        You have the right to request that we disclose to you:<br />
                        - the categories and sources of the personal information that we collect about you, the purposes for which we use your information and with whom such information is shared;<br />
                        - in case of sale of personal information or disclosure for a business purpose, two separate lists where we disclose:<br />
                        - for sales, the personal information categories purchased by each category of recipient; and<br />
                        - for disclosures for a business purpose, the personal information categories obtained by each category of recipient.<br />
                        The disclosure described above will be limited to the personal information collected or used over the past 12 months.<br />
                        If we deliver our response electronically, the information enclosed will be "portable", i.e. delivered in an easily usable format to enable you to transmit the information to another entity without hindrance – provided that this is technically feasible.<br /><br />

                        The right to request the deletion of your personal information
                        You have the right to request that we delete any of your personal information, subject to exceptions set forth by the law (such as, including but not limited to, where the information is used to identify and repair errors on Horizon AI, to detect security incidents and protect against fraudulent or illegal activities, to exercise certain rights etc.).<br />
                        If no legal exception applies, as a result of exercising your right, we will delete your personal information and direct any of our service providers to do so.<br /><br />

                        How to exercise your rights<br />
                        To exercise the rights described above, you need to submit your verifiable request to us by contacting us via the details provided in this document.<br />
                        For us to respond to your request, it's necessary that we know who you are. Therefore, you can only exercise the above rights by making a verifiable request which must:<br />
                        - provide sufficient information that allows us to reasonably verify you are the person about whom we collected personal information or an authorized representative;<br />
                        - describe your request with sufficient detail that allows us to properly understand, evaluate, and respond to it.<br />
                        We will not respond to any request if we are unable to verify your identity and therefore confirm the personal information in our possession actually relates to you.<br />
                        If you cannot personally submit a verifiable request, you can authorize a person registered with the California Secretary of State to act on your behalf.<br />
                        If you are an adult, you can make a verifiable request on behalf of a minor under your parental authority.
                        You can submit a maximum number of 2 requests over a period of 12 months.<br /><br />

                        How and when we are expected to handle your request<br />
                        We will confirm receipt of your verifiable request within 10 days and provide information about how we will process your request.<br />
                        We will respond to your request within 45 days of its receipt. Should we need more time, we will explain to you the reasons why, and how much more time we need. In this regard, please note that we may take up to 90 days to fulfill your request.<br />
                        Our disclosure(s) will cover the preceding 12 month period.<br />
                        Should we deny your request, we will explain you the reasons behind our denial.<br />
                        We do not charge a fee to process or respond to your verifiable request unless such request is manifestly unfounded or excessive. In such cases, we may charge a reasonable fee, or refuse to act on the request. In either case, we will communicate our choices and explain the reasons behind it.
                    </Typography>
                </Container>
            </Box>
        </Box >
    );
}

export default PrivacyPolicyPage
